from uuid import UUID

from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, filters, status
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
from usersystem.permissions import ActiveUserPermission, RolePermission, resolve_active_user
from notifications.services import send_notifications
from notifications.utils import user_display_name
from Assignment.models import Assignment


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class AIUserScaleViewSet(viewsets.ModelViewSet):
    queryset = AIUserScale.objects.all()
    serializer_class = AIUserScaleSerializer
    permission_classes = [ActiveUserPermission, RolePermission]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "notes"]
    ordering_fields = ["created_at", "updated_at", "name", "level"]
    ordering = ["-updated_at"]
    role_permissions = {
        "list": ["admin", "sc"],
        "retrieve": ["admin", "sc"],
        "default": ["admin", "sc"],
    }

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
    queryset = ScaleRecord.objects.all().prefetch_related("versions__levels")
    serializer_class = ScaleRecordSerializer
    permission_classes = [ActiveUserPermission, RolePermission]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["updated_at", "created_at", "name"]
    ordering = ["-updated_at"]
    role_permissions = {
        "list": ["admin", "sc"],
        "retrieve": ["admin", "sc"],
        "default": ["admin", "sc"],
    }

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
        return resolve_active_user(request)

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
        serializer = SaveScaleVersionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        record_id = data["scaleId"]
        notes = data.get("notes")
        levels = data["levels"]
        acting_user = self._resolve_request_user(request)
        if not acting_user:
            raise PermissionDenied("Authentication required.")
        updated_by = data.get("updatedBy") or getattr(acting_user, "username", "system")

        try:
            record = ScaleRecord.objects.get(pk=record_id)
        except ScaleRecord.DoesNotExist:
            return Response({"detail": "ScaleRecord not found"}, status=status.HTTP_404_NOT_FOUND)

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

        owner_user = None
        if record.owner_type == ScaleRecord.OWNER_SC and record.owner_id:
            owner_lookup = Q(username=record.owner_id)
            try:
                owner_lookup |= Q(pk=int(record.owner_id))
            except (TypeError, ValueError):
                pass
            owner_user = (
                User.objects.filter(role="sc", status=User.STATUS_ACTIVE)
                .filter(owner_lookup)
                .first()
            )

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

        actor_for_notifications = acting_user or owner_user
        actor_name = user_display_name(actor_for_notifications, default=(updated_by or "system"))
        version_label = f"v{next_version_num}"
        response_payload = ScaleRecordSerializer(record).data

        if record.owner_type == ScaleRecord.OWNER_SYSTEM:
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
        elif record.owner_type == ScaleRecord.OWNER_SC:
            sc_identifiers = set()
            if record.owner_id:
                sc_identifiers.add(str(record.owner_id))
            if owner_user:
                sc_identifiers.add(str(getattr(owner_user, "pk", "")))
                username = getattr(owner_user, "username", "")
                if username:
                    sc_identifiers.add(username)
            if acting_user and getattr(acting_user, "role", None) == "sc":
                sc_identifiers.add(str(getattr(acting_user, "pk", "")))
                username = getattr(acting_user, "username", "")
                if username:
                    sc_identifiers.add(username)
            sc_identifiers = {value for value in sc_identifiers if value}

            pk_identifiers: set[int] = set()
            username_identifiers: set[str] = set()
            for value in sc_identifiers:
                try:
                    pk_identifiers.add(int(value))
                except (TypeError, ValueError):
                    if value:
                        username_identifiers.add(value)

            assignment_qs = Assignment.objects.filter(
                Q(course__coordinator__pk__in=pk_identifiers)
                | Q(course__coordinator__username__in=username_identifiers)
            ).prefetch_related("tutors")
            tutor_candidates = set()
            for assignment in assignment_qs:
                for tutor in assignment.tutors.all():
                    if getattr(tutor, "status", None) == User.STATUS_ACTIVE:
                        tutor_candidates.add(tutor.pk)

            recipients = []
            if tutor_candidates:
                recipients.extend(
                    User.objects.filter(
                        pk__in=tutor_candidates,
                        role="tutor",
                        status=User.STATUS_ACTIVE,
                    )
                )

            fallback_tutors = (
                User.objects.filter(
                    role="tutor",
                    status=User.STATUS_ACTIVE,
                )
                .filter(
                    Q(assignments__course__coordinator__pk__in=pk_identifiers)
                    | Q(assignments__course__coordinator__username__in=username_identifiers)
                )
                .distinct()
            )
            existing_ids = {getattr(user, "pk", None) for user in recipients}
            for tutor in fallback_tutors:
                pk = getattr(tutor, "pk", None)
                if pk is None or pk in existing_ids:
                    continue
                recipients.append(tutor)
                existing_ids.add(pk)

            if owner_user and getattr(owner_user, "status", None) == User.STATUS_ACTIVE:
                recipients.append(owner_user)
            title = "Coordinator AI use scale updated"
            content = (
                f"{actor_name} published {version_label} of their AI use scale "
                f"\"{record.name}\". Please review related templates."
            )
            send_notifications(
                recipients,
                title=title,
                content=content,
                body=notes or "",
                related_type="scale",
                related_id=str(record.id),
            )

        return Response(response_payload, status=status.HTTP_201_CREATED)
