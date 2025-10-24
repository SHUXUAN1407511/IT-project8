from uuid import UUID

from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import AIUserScale, ScaleRecord, ScaleVersion, ScaleLevel
from .serializer import (
    AIUserScaleSerializer,
    ScaleRecordSerializer,
    SaveScaleVersionRequestSerializer,
)
from usersystem.models import User
from notifications.services import send_notifications
from notifications.utils import user_display_name


# -------------------------
# 公共分页器
# -------------------------
class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# -------------------------
# 旧接口：/scales/（兼容 /aiusescale/）
# -------------------------
class AIUserScaleViewSet(viewsets.ModelViewSet):
    queryset = AIUserScale.objects.all()
    serializer_class = AIUserScaleSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "notes"]
    ordering_fields = ["created_at", "updated_at", "name", "level"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        username = self.request.query_params.get("username")
        if username:
            qs = qs.filter(username=username)
        return qs

    def list(self, request, *args, **kwargs):
        no_page = request.query_params.get("nopage") in ("1", "true", "True")
        if request.query_params.get("page_size") == "0":
            no_page = True

        queryset = self.filter_queryset(self.get_queryset())
        if no_page or self.pagination_class is None:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)


class ScaleRecordViewSet(viewsets.ModelViewSet):
    """
    - GET /scale-records/?ownerType=&ownerId=&isPublic=1
    - POST /scale-records/
    - PUT/PATCH /scale-records/:id/
    - DELETE /scale-records/:id/
    - POST /scale-records/save_version   (SaveScaleVersionRequest)
    """
    queryset = ScaleRecord.objects.all().prefetch_related("versions__levels")
    serializer_class = ScaleRecordSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["updated_at", "created_at", "name"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        owner_type = self.request.query_params.get("ownerType")
        owner_id = self.request.query_params.get("ownerId")
        is_public = self.request.query_params.get("isPublic")
        if owner_type:
            qs = qs.filter(owner_type=owner_type)
        if owner_id:
            qs = qs.filter(owner_id=owner_id)
        if is_public in ("1", "true", "True"):
            qs = qs.filter(is_public=True)

        acting_user = self._resolve_request_user(self.request)
        if acting_user and getattr(acting_user, "role", None) == "sc":
            owner_key = self._owner_key_for(acting_user)
            if owner_type == ScaleRecord.OWNER_SC and not owner_id:
                qs = qs.filter(owner_id=owner_key)
            elif not owner_type and not owner_id:
                qs = qs.filter(
                    Q(owner_type=ScaleRecord.OWNER_SYSTEM)
                    | Q(owner_type=ScaleRecord.OWNER_SC, owner_id=owner_key)
                )

        return qs

    def list(self, request, *args, **kwargs):
        no_page = request.query_params.get("nopage") in ("1", "true", "True")
        if request.query_params.get("page_size") == "0":
            no_page = True

        queryset = self.filter_queryset(self.get_queryset())
        if no_page or self.pagination_class is None:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def _resolve_request_user(self, request):
        """
        Try to resolve the business user making the request.
        Mirrors the assignment viewset logic so that front-end hints keep working.
        """
        django_user = getattr(request, "user", None)
        if getattr(django_user, "is_authenticated", False):
            if hasattr(django_user, "role"):
                return django_user
            username = getattr(django_user, "username", None)
            if username:
                try:
                    return User.objects.get(username=username)
                except User.DoesNotExist:
                    pass

        candidate_ids = [
            request.headers.get("X-User-Id"),
            request.headers.get("X_USER_ID"),
            request.headers.get("X-USER-ID"),
            request.query_params.get("userId"),
            getattr(request.data, "get", lambda _key, _default=None: _default)("userId"),
        ]
        for candidate in candidate_ids:
            if not candidate:
                continue
            try:
                return User.objects.get(pk=candidate)
            except (User.DoesNotExist, ValueError, TypeError):
                continue

        candidate_usernames = [
            request.headers.get("X-User-Username"),
            request.headers.get("X-User-Name"),
            request.headers.get("X_USER_NAME"),
            request.headers.get("X-USERNAME"),
            request.query_params.get("username"),
            getattr(request.data, "get", lambda _key, _default=None: _default)("username"),
        ]
        for candidate in candidate_usernames:
            if not candidate:
                continue
            try:
                return User.objects.get(username=candidate)
            except User.DoesNotExist:
                continue

        return None

    def _owner_key_for(self, user):
        username = getattr(user, "username", None)
        if username:
            return username
        return str(getattr(user, "pk", ""))

    def _resolve_record_by_alias(self, alias: str, acting_user):
        normalized = (alias or "").strip().lower()
        if not normalized:
            return None

        if normalized == "system_default":
            return (
                ScaleRecord.objects.filter(owner_type=ScaleRecord.OWNER_SYSTEM)
                .order_by("-updated_at")
                .first()
            )

        if (
            normalized in {"sc_personal", "personal", "owner_default"}
            and acting_user
            and getattr(acting_user, "role", None) == "sc"
        ):
            owner_key = self._owner_key_for(acting_user)
            return (
                ScaleRecord.objects.filter(
                    owner_type=ScaleRecord.OWNER_SC,
                    owner_id=owner_key,
                )
                .order_by("-updated_at")
                .first()
            )

        return None

    def _assert_can_modify_record(self, record: ScaleRecord, user):
        if not user:
            return
        role = getattr(user, "role", None)
        if role == "admin":
            return
        if role == "sc":
            owner_key = self._owner_key_for(user)
            if record.owner_type == ScaleRecord.OWNER_SYSTEM:
                raise PermissionDenied("SC users cannot modify the default scale.")
            if record.owner_type == ScaleRecord.OWNER_SC and record.owner_id != owner_key:
                raise PermissionDenied("You can only modify your own scale.")
        else:
            raise PermissionDenied("You do not have permission to modify this scale.")

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self._resolve_request_user(request)
        self._assert_can_modify_record(instance, user)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self._resolve_request_user(request)
        self._assert_can_modify_record(instance, user)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self._resolve_request_user(request)
        self._assert_can_modify_record(instance, user)
        return super().destroy(request, *args, **kwargs)

    @action(methods=["get"], detail=False, url_path="sc-view")
    def sc_view(self, request, *args, **kwargs):
        """
        Returns data grouped for SC dashboard usage:
        - defaultRecords: all system-owned scales (admin maintained)
        - personalRecord: the caller's private copy, if it exists
        """
        user = self._resolve_request_user(request)
        if not user or getattr(user, "role", None) != "sc":
            raise PermissionDenied("Only SC users can access this view.")

        owner_key = self._owner_key_for(user)

        default_qs = (
            ScaleRecord.objects.filter(owner_type=ScaleRecord.OWNER_SYSTEM)
            .prefetch_related("versions__levels")
            .order_by("-updated_at")
        )
        personal = (
            ScaleRecord.objects.filter(
                owner_type=ScaleRecord.OWNER_SC,
                owner_id=owner_key,
            )
            .prefetch_related("versions__levels")
            .order_by("-updated_at")
            .first()
        )

        default_payload = ScaleRecordSerializer(default_qs, many=True).data
        personal_payload = ScaleRecordSerializer(personal).data if personal else None

        return Response(
            {
                "defaultRecords": default_payload,
                "personalRecord": personal_payload,
            }
        )

    @action(methods=["post"], detail=False, url_path="save_version")
    def save_version(self, request, *args, **kwargs):
        """
        SaveScaleVersionRequest：
        {
          "scaleId": "uuid",
          "levels": [{ id,label,title?,description?,aiUsage?,instructions?,acknowledgement? }, ...],
          "notes": "optional",
          "updatedBy": "optional string"
        }
        """
        serializer = SaveScaleVersionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        record_id = data["scaleId"]
        notes = data.get("notes")
        levels = data["levels"]
        updated_by = data.get("updatedBy") or (
            getattr(getattr(request, "user", None), "username", None) or "system"
        )

        try:
            record = ScaleRecord.objects.get(pk=record_id)
        except ScaleRecord.DoesNotExist:
            return Response({"detail": "ScaleRecord not found"}, status=status.HTTP_404_NOT_FOUND)

        acting_user = self._resolve_request_user(request)
        if not acting_user and updated_by and updated_by != "system":
            try:
                acting_user = User.objects.get(username=updated_by)
            except User.DoesNotExist:
                acting_user = None
        if acting_user and not data.get("updatedBy"):
            updated_by = getattr(acting_user, "username", updated_by)

        record_owner = record.owner_type

        if acting_user and getattr(acting_user, "role", None) == "sc":
            owner_key = self._owner_key_for(acting_user)
            if record_owner == ScaleRecord.OWNER_SYSTEM:
                record, _created = ScaleRecord.objects.get_or_create(
                    owner_type=ScaleRecord.OWNER_SC,
                    owner_id=owner_key,
                    defaults={
                        "name": record.name,
                        "is_public": False,
                    },
                )
            elif record_owner == ScaleRecord.OWNER_SC and record.owner_id != owner_key:
                raise PermissionDenied("You can only save versions of your own scale.")
        elif acting_user and getattr(acting_user, "role", None) != "admin":
            raise PermissionDenied("You do not have permission to modify this scale.")

        with transaction.atomic():
            last = record.versions.order_by("-version").first()
            next_version_num = (last.version + 1) if last else 1

            version = ScaleVersion.objects.create(
                record=record,
                version=next_version_num,
                updated_by=updated_by,
                notes=notes,
            )

            bulk_levels = []
            for idx, lv in enumerate(levels):
                bulk_levels.append(
                    ScaleLevel(
                        version=version,
                        position=idx,
                        level_code=lv["level_code"],
                        label=lv["label"],
                        title=lv.get("title") or None,
                        description=lv.get("description") or "",
                        ai_usage=lv.get("aiUsage") or "",
                        instructions=lv.get("instructions") or None,
                        acknowledgement=lv.get("acknowledgement") or None,
                    )
                )
            ScaleLevel.objects.bulk_create(bulk_levels)

        actor_name = user_display_name(acting_user, default=(updated_by or "system"))
        version_label = f"v{next_version_num}"
        response_payload = ScaleRecordSerializer(record).data

        if (
            acting_user
            and getattr(acting_user, "role", None) == "admin"
            and record.owner_type == ScaleRecord.OWNER_SYSTEM
        ):
            recipients = User.objects.filter(
                role__in=["admin", "sc"],
                status=User.STATUS_ACTIVE,
            )
            title = "System AI use scale updated"
            content = (
                f"{actor_name} published {version_label} of the system AI use scale "
                f"\"{record.name}\"."
            )
            send_notifications(
                recipients,
                title=title,
                content=content,
                body=notes or "",
                related_type="scale",
                related_id=str(record.id),
            )
        elif (
            acting_user
            and getattr(acting_user, "role", None) == "sc"
            and record.owner_type == ScaleRecord.OWNER_SC
        ):
            sc_identifiers = {
                value
                for value in [
                    str(getattr(acting_user, "pk", "")),
                    getattr(acting_user, "username", ""),
                ]
                if value
            }
            tutors = (
                User.objects.filter(
                    role="tutor",
                    status=User.STATUS_ACTIVE,
                    assignments__course__coordinator__in=sc_identifiers,
                )
                .distinct()
            )
            title = "Coordinator AI use scale updated"
            content = (
                f"{actor_name} published {version_label} of their AI use scale "
                f"\"{record.name}\". Please review related templates."
            )
            send_notifications(
                tutors,
                title=title,
                content=content,
                body=notes or "",
                related_type="scale",
                related_id=str(record.id),
            )

        return Response(response_payload, status=status.HTTP_201_CREATED)
