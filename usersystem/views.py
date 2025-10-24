import hashlib
import logging
import secrets
from datetime import timedelta
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import BadHeaderError, send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from smtplib import SMTPException

from common.responses import error_response

from .models import PasswordResetToken, User
from .permissions import ActiveUserPermission, RolePermission, resolve_active_user
from .serializer import ManagedUserSerializer, SelfProfileSerializer, UserSerializer

logger = logging.getLogger(__name__)

def success(data=None, msg="success", code=status.HTTP_200_OK):
    payload = {"message": msg}
    if data is not None:
        payload["data"] = data
    return Response(payload, status=code)


def fail(msg="bad request", code=status.HTTP_400_BAD_REQUEST, data=None):
    detail = data or {}
    if not isinstance(detail, dict):
        detail = {"detail": detail}
    return error_response(msg, status_code=code, data=detail)


def issue_token(user: User) -> str:
    # Allocate a short-lived auth token while avoiding collisions.
    for _ in range(5):
        token = secrets.token_urlsafe(32)
        if not User.objects.filter(auth_token=token).exists():
            user.auth_token = token
            user.last_login_at = timezone.now()
            user.save(update_fields=["auth_token", "last_login_at"])
            return token
    raise RuntimeError("Failed to allocate authentication token.")


def hash_reset_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_reset_link(token: str) -> str:
    # Inject the token into the configured reset URL without dropping existing params.
    base_url = getattr(settings, "PASSWORD_RESET_URL", "") or ""
    if not base_url:
        return token
    parsed = urlparse(base_url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["token"] = token
    new_query = urlencode(query)
    updated = parsed._replace(query=new_query)
    return urlunparse(updated)


def dispatch_password_reset_email(user: User, raw_token: str) -> None:
    # Email the reset instructions; swallow missing email addresses gracefully.
    if not user.email:
        logger.info("Skipping password reset email because user has no email set.")
        return
    reset_link = build_reset_link(raw_token)
    subject = "Password reset instructions"
    message = (
        "We received a request to reset your password.\n\n"
        "If you initiated this, click the link below to choose a new password:\n"
        f"{reset_link}\n\n"
        "If you did not request a reset, you can ignore this email."
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except (SMTPException, BadHeaderError) as exc:
        logger.exception("Failed to send password reset email: user=%s", user.id, exc_info=exc)


def invalidate_user_tokens(user: User) -> None:
    # Mark any previous tokens as used so only the latest one stays active.
    PasswordResetToken.objects.filter(
        user=user,
        used_at__isnull=True,
    ).update(used_at=timezone.now())

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = UserSerializer(data=request.data)
        if not ser.is_valid():
            return fail(msg="validation error", code=status.HTTP_400_BAD_REQUEST, data=ser.errors)

        username = ser.validated_data["username"]
        if User.objects.filter(username=username).exists():
            return fail(msg="username already exists", code=400)

        user = ser.save()
        return success(
            data={"id": str(user.id), "username": user.username, "role": user.role},
            msg="registered",
            code=status.HTTP_201_CREATED,
        )

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = (request.data.get("password") or "")

        if not username or not password:
            return error_response(
                "username and password required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return error_response(
                "username or password incorrect",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_password(password, user.password):
            return error_response(
                "username or password incorrect",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if user.status != User.STATUS_ACTIVE:
            return error_response(
                "account disabled. Please contact an administrator.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user_profile = {
            "id": str(user.id),
            "username": user.username,
            "name": user.name or user.username,
            "role": user.role,
            "status": user.status,
            "email": user.email,
            "phone": user.phone,
            "organization": user.organization,
            "bio": user.bio,
        }

        if not user_profile["role"]:
            return error_response(
                "role missing, login failed",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        token = issue_token(user)

        return Response(
            {
                "token": token,
                "user": user_profile,
                "message": "login success",
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [ActiveUserPermission]

    def post(self, request):
        user = resolve_active_user(request)
        if user:
            user.auth_token = None
            user.save(update_fields=["auth_token"])
        return success(msg="logged out", code=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        username = (request.data.get("username") or "").strip()
        if not email and not username:
            return error_response(
                "email or username required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = None
        if email:
            user = (
                User.objects.filter(email__iexact=email, status=User.STATUS_ACTIVE)
                .order_by('id')
                .first()
            )
        if not user and username:
            user = (
                User.objects.filter(username=username, status=User.STATUS_ACTIVE)
                .order_by('id')
                .first()
            )

        if user:
            with transaction.atomic():
                invalidate_user_tokens(user)
                raw_token = secrets.token_urlsafe(48)
                token_hash = hash_reset_token(raw_token)
                expires_at = timezone.now() + timedelta(
                    minutes=getattr(settings, "PASSWORD_RESET_TOKEN_EXPIRY_MINUTES", 30)
                )
                PasswordResetToken.objects.create(
                    user=user,
                    token_hash=token_hash,
                    expires_at=expires_at,
                )
            try:
                dispatch_password_reset_email(user, raw_token)
            except (SMTPException, BadHeaderError) as exc:
                logger.warning(
                    "Password reset email dispatch failed for user=%s",
                    user.id,
                    exc_info=exc,
                )

        return success(
            msg="If an account matches the provided details, a reset email has been sent."
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = (request.data.get("token") or "").strip()
        new_password = (request.data.get("newPassword") or "").strip()
        if not token or not new_password:
            return error_response(
                "token and newPassword required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if len(new_password) < 6:
            return error_response(
                "new password must contain at least 6 characters",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        token_hash = hash_reset_token(token)
        reset_entry = (
            PasswordResetToken.objects.select_related("user")
            .filter(token_hash=token_hash)
            .first()
        )
        if (
            not reset_entry
            or reset_entry.used_at is not None
            or reset_entry.expires_at < timezone.now()
        ):
            return error_response(
                "invalid or expired token",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = reset_entry.user
        user.password = make_password(new_password)
        user.save(update_fields=["password"])

        reset_entry.mark_used()
        invalidate_user_tokens(user)
        return success(msg="password reset")


class AdminUserListView(APIView):
    permission_classes = [ActiveUserPermission, RolePermission]
    required_roles = ['admin', 'sc']

    def get(self, request):
        role = request.query_params.get("role")
        status_param = request.query_params.get("status")

        queryset = User.objects.all()
        if role:
            queryset = queryset.filter(role=role)
        if status_param:
            queryset = queryset.filter(status=status_param)

        serializer = ManagedUserSerializer(queryset, many=True)
        data = serializer.data
        for item in data:
            item["id"] = str(item["id"])
            item["name"] = item.get("name") or item.get("username")
            item["status"] = item.get("status") or User.STATUS_ACTIVE
        return Response(data, status=status.HTTP_200_OK)


class AdminUserDetailView(APIView):
    permission_classes = [ActiveUserPermission, RolePermission]
    required_roles = ['admin']

    def put(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = ManagedUserSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                "validation error",
                status_code=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors,
            )

        updated = serializer.save()
        data = ManagedUserSerializer(updated).data
        data["id"] = str(updated.id)
        data["name"] = data.get("name") or data.get("username")
        return Response(data, status=status.HTTP_200_OK)


class AdminUserStatusView(APIView):
    permission_classes = [ActiveUserPermission, RolePermission]
    required_roles = ['admin']

    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        payload = request.data.get("data") or request.data
        new_status = (payload or {}).get("status")

        if new_status not in {User.STATUS_ACTIVE, User.STATUS_INACTIVE}:
            return error_response(
                "invalid status",
                status_code=status.HTTP_400_BAD_REQUEST,
                data={"allowed": [User.STATUS_ACTIVE, User.STATUS_INACTIVE]},
            )

        user.status = new_status
        user.save(update_fields=["status"])

        data = ManagedUserSerializer(user).data
        data["id"] = str(user.id)
        data["name"] = data.get("name") or data.get("username")
        return Response(data, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    permission_classes = [ActiveUserPermission]

    def get(self, request):
        user = resolve_active_user(request)
        serializer = SelfProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        user = resolve_active_user(request)
        serializer = SelfProfileSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                "validation error",
                status_code=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors,
            )

        updated = serializer.save()
        response_serializer = SelfProfileSerializer(updated)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class CurrentUserPasswordView(APIView):
    permission_classes = [ActiveUserPermission]

    def post(self, request):
        user = resolve_active_user(request)
        current_password = (request.data.get("currentPassword") or "").strip()
        new_password = (request.data.get("newPassword") or "").strip()

        if not current_password or not new_password:
            return error_response(
                "current and new password required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if len(new_password) < 6:
            return error_response(
                "new password must contain at least 6 characters",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if not check_password(current_password, user.password):
            return error_response(
                "current password incorrect",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user.password = make_password(new_password)
        user.save(update_fields=["password"])

        return success(msg="password updated")
