from django.contrib.auth.hashers import check_password
from rest_framework import permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializer import ManagedUserSerializer, UserSerializer

def success(data=None, msg="success", status=200):
    return Response({
        "user": data or {},
        "meta": {"status": status,
                 "message": msg}
    })

def fail(msg="bad request", status=400, data=None):
    return Response({
        "data": data or {},
        "meta": {"status": status,
                 "message": msg}
    })

class RegisterView(APIView):
    """
    POST /api/register
    body: { "username": "abcxyz", "password": "123456","role": "admin" }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = UserSerializer(data=request.data)
        if not ser.is_valid():
            return fail(msg="validation error", status=400, data=ser.errors)

        username = ser.validated_data["username"]
        if User.objects.filter(username=username).exists():
            return fail(msg="username already exists", status=400)

        user = ser.save()
        return success(
            data={"id": str(user.id), "username": user.username, "role": user.role},
            msg="registered",
            status=200,
        )

class LoginView(APIView):
    """
    POST /api/login
    body: { "username": "abcxyz", "password": "123456" }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = (request.data.get("password") or "")

        if not username or not password:
            return Response({"message": "username and password required"}, status=400)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"message": "username or password incorrect"}, status=401)

        if not check_password(password, user.password):
            return Response({"message": "username or password incorrect"}, status=401)

        user_profile = {
            "id": str(user.id),
            "username": user.username,
            "name": user.name or user.username,
            "role": user.role,
            "status": user.status,
        }

        if not user_profile["role"]:
            return Response({"message": "role missing, login failed"}, status=403)

        return Response({
            "token": None,
            "user": user_profile,
            "message": "login success"
        }, status=200)


class AdminUserListView(APIView):
    permission_classes = [permissions.AllowAny]

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
    permission_classes = [permissions.AllowAny]

    def put(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = ManagedUserSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        updated = serializer.save()
        data = ManagedUserSerializer(updated).data
        data["id"] = str(updated.id)
        data["name"] = data.get("name") or data.get("username")
        return Response(data, status=status.HTTP_200_OK)


class AdminUserStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        payload = request.data.get("data") or request.data
        new_status = (payload or {}).get("status")

        if new_status not in {User.STATUS_ACTIVE, User.STATUS_INACTIVE}:
            return Response(
                {"message": "invalid status", "allowed": [User.STATUS_ACTIVE, User.STATUS_INACTIVE]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.status = new_status
        user.save(update_fields=["status"])

        data = ManagedUserSerializer(user).data
        data["id"] = str(user.id)
        data["name"] = data.get("name") or data.get("username")
        return Response(data, status=status.HTTP_200_OK)
