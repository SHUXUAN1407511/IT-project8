from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from common.responses import error_response
from usersystem.models import User
from usersystem.permissions import ActiveUserPermission, RolePermission, resolve_active_user
from notifications.services import send_notifications
from notifications.utils import user_display_name
from template.serializers import AssignmentTemplateSerializer
from .models import Assignment
from .serializer import AssignmentSerializer


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [ActiveUserPermission, RolePermission]
    pagination_class = DefaultPagination
    ordering_fields = ["due_date", "created_at", "name"]
    ordering = ["-created_at"]
    role_permissions = {
        "list": ["admin", "sc", "tutor"],
        "retrieve": ["admin", "sc", "tutor"],
        "retrieve_template": ["admin", "sc", "tutor"],
        "save_template": ["admin", "sc", "tutor"],
        "default": ["admin", "sc"],
    }

    def get_queryset(self):
        queryset = (
            Assignment.objects.select_related("course")
            .prefetch_related("tutors")
            .order_by("-created_at")
        )

        params = self.request.query_params
        course_id = params.get("courseId")
        keyword = params.get("keyword") or params.get("search")
        assignment_type = params.get("type")
        status_param = params.get("status")
        ordering = params.get("ordering")
        request_user = self._resolve_request_user(self.request)

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) | Q(description__icontains=keyword)
            )
        if assignment_type:
            queryset = queryset.filter(type__iexact=assignment_type)
        if status_param:
            queryset = queryset.filter(ai_declaration_status=status_param)

        if request_user:
            role = getattr(request_user, "role", None)
            if role == "tutor":
                queryset = queryset.filter(tutors=request_user)
            elif role == "sc":
                queryset = queryset.filter(course__coordinator=request_user)

        if ordering:
            allowed = {"created_at", "due_date", "name"}
            order_field = ordering.lstrip("-")
            if order_field in allowed:
                queryset = queryset.order_by(ordering)

        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        request_user = self._resolve_request_user(request)
        if request_user and getattr(request_user, "role", None) == "sc":
            queryset = list(queryset)
            queryset = [
                assignment
                for assignment in queryset
                if assignment.ai_declaration_status != Assignment.STATUS_PUBLISHED
                or self._can_user_edit_assignment(request_user, assignment)
            ]
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def _resolve_request_user(self, request):
        return resolve_active_user(request)

    def _resolve_assignment_coordinator(self, assignment):
        course = getattr(assignment, "course", None)
        if not course:
            return None
        coordinator = getattr(course, "coordinator", None)
        if coordinator and getattr(coordinator, "status", None) == User.STATUS_ACTIVE:
            return coordinator
        return None

    def _coordinator_identifiers(self, assignment):
        course = getattr(assignment, "course", None)
        if not course:
            return set()
        coordinator = self._resolve_assignment_coordinator(assignment)
        if not coordinator:
            return set()
        identifiers = {str(coordinator.pk)}
        username = getattr(coordinator, "username", "")
        if username:
            identifiers.add(username)
        return identifiers

    def _can_user_edit_assignment(self, user, assignment):
        if not user:
            return False
        if getattr(user, "status", None) != User.STATUS_ACTIVE:
            return False
        role = getattr(user, "role", None)
        if role == "admin":
            return True
        if role == "sc":
            identifiers = self._coordinator_identifiers(assignment)
            if not identifiers:
                return False
            return str(user.pk) in identifiers or getattr(user, "username", "") in identifiers
        if role == "tutor":
            return assignment.tutors.filter(pk=user.pk, status=User.STATUS_ACTIVE).exists()
        return False

    def _gather_template_recipients(self, assignment, actor=None):
        # Build a unique set of active users who should be notified about template changes.
        recipients = []
        seen_ids = set()
        tutors = list(assignment.tutors.filter(status=User.STATUS_ACTIVE))
        coordinator = self._resolve_assignment_coordinator(assignment)

        candidates = tutors[:]
        if coordinator:
            candidates.append(coordinator)
        if actor and getattr(actor, "pk", None):
            candidates.append(actor)

        for user in candidates:
            if not user:
                continue
            pk = getattr(user, "pk", None)
            if pk is not None and pk in seen_ids:
                continue
            if not self._can_user_edit_assignment(user, assignment):
                continue
            if pk is not None:
                seen_ids.add(pk)
            recipients.append(user)

        return recipients

    def _emit_template_publish_notification(self, assignment, actor, template, updated_by_hint=""):
        role = getattr(actor, "role", None)
        if role not in {"sc", "tutor"} and not updated_by_hint:
            return

        recipients = self._gather_template_recipients(assignment, actor)
        if not recipients:
            return

        actor_name = user_display_name(actor, default=updated_by_hint or "System")
        assignment_name = getattr(assignment, "name", "assignment")
        course = getattr(assignment, "course", None)
        course_code = getattr(course, "code", "")
        course_term = getattr(course, "semester", "")
        course_label = " ".join(part for part in [course_code, course_term] if part)

        if course_label:
            content = (
                f"{actor_name} published the AI declaration template for "
                f"{assignment_name} ({course_label})."
            )
        else:
            content = f"{actor_name} published the AI declaration template for {assignment_name}."

        published_at = getattr(template, "last_published_at", None)
        body = ""
        if published_at is not None:
            body = f"Published at {published_at.isoformat()}"

        send_notifications(
            recipients,
            title="Template published",
            content=content,
            body=body,
            related_type="assignment",
            related_id=str(getattr(assignment, "pk", "")),
        )

    def _notify_tutor_assignment(self, assignment, actor, new_tutors):
        if not new_tutors:
            return
        actor_name = user_display_name(actor, default="Coordinator")
        assignment_name = getattr(assignment, "name", "assignment")
        course = getattr(assignment, "course", None)
        course_code = getattr(course, "code", "")
        course_term = getattr(course, "semester", "")
        course_label = " ".join(part for part in [course_code, course_term] if part)

        if course_label:
            content = (
                f"{actor_name} added you to the AI declaration template for "
                f"{assignment_name} ({course_label})."
            )
        else:
            content = (
                f"{actor_name} added you to the AI declaration template for "
                f"{assignment_name}."
            )

        body = "You now have permission to review and edit this template."

        send_notifications(
            new_tutors,
            title="Template access granted",
            content=content,
            body=body,
            related_type="assignment",
            related_id=str(getattr(assignment, "pk", "")),
        )

    def create(self, request, *args, **kwargs):
        user = self._resolve_request_user(request)
        if user and user.role == "tutor":
            return error_response(
                "Tutors are not allowed to create assignments.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        assignment = serializer.save()
        acting_user = self._resolve_request_user(self.request)
        if getattr(acting_user, "role", None) not in {"admin", "sc"}:
            return
        new_tutors = list(
            assignment.tutors.filter(
                role="tutor",
                status=User.STATUS_ACTIVE,
            )
        )
        self._notify_tutor_assignment(assignment, acting_user, new_tutors)

    def perform_update(self, serializer):
        instance = serializer.instance
        before_ids = set(
            instance.tutors.values_list("pk", flat=True)
        )
        assignment = serializer.save()
        acting_user = self._resolve_request_user(self.request)
        if getattr(acting_user, "role", None) not in {"admin", "sc"}:
            return
        current_tutors = list(
            assignment.tutors.filter(
                role="tutor",
                status=User.STATUS_ACTIVE,
            )
        )
        new_tutors = [
            tutor for tutor in current_tutors if getattr(tutor, "pk", None) not in before_ids
        ]
        self._notify_tutor_assignment(assignment, acting_user, new_tutors)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="template", url_name="template")
    def retrieve_template(self, request, pk=None):
        assignment = self.get_object()
        acting_user = self._resolve_request_user(request)
        if not self._can_user_edit_assignment(acting_user, assignment):
            return error_response(
                "You do not have permission to view this template.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        template = getattr(assignment, "ai_template", None)
        if not template:
            return error_response(
                "Template not found.",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        serializer = AssignmentTemplateSerializer(template)
        return Response(serializer.data)

    @retrieve_template.mapping.post
    def save_template(self, request, pk=None):
        assignment = self.get_object()
        acting_user = self._resolve_request_user(request)
        existing_template = getattr(assignment, "ai_template", None)
        publish = request.data.get("publish", False)
        updated_by = request.data.get("updatedBy")

        if not acting_user:
            return error_response(
                "Authentication required.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not self._can_user_edit_assignment(acting_user, assignment):
            return error_response(
                "You do not have permission to modify this template.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if not updated_by:
            updated_by = user_display_name(acting_user)

        serializer_data = request.data.copy()
        if isinstance(serializer_data, (list, tuple)):
            return error_response(
                "Invalid payload format.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        serializer_data.pop("publish", None)
        serializer_data.pop("updatedById", None)

        if existing_template:
            serializer = AssignmentTemplateSerializer(
                existing_template, data=serializer_data, partial=True
            )
        else:
            serializer = AssignmentTemplateSerializer(data=serializer_data)

        serializer.is_valid(raise_exception=True)
        if existing_template:
            template = serializer.save()
        else:
            template = serializer.save(assignment=assignment)

        now = timezone.now()
        if publish:
            template.is_published = True
            template.last_published_at = now
        else:
            template.is_published = False
        if updated_by:
            template.updated_by = str(updated_by)
        template.save()

        has_rows = bool(getattr(template, "rows", []))
        assignment.has_template = has_rows
        assignment.template_updated_at = template.updated_at
        if publish:
            assignment.ai_declaration_status = Assignment.STATUS_PUBLISHED
        else:
            assignment.ai_declaration_status = (
                Assignment.STATUS_DRAFT if has_rows else Assignment.STATUS_MISSING
            )
        assignment.save()

        if publish:
            self._emit_template_publish_notification(
                assignment,
                acting_user,
                template,
                updated_by_hint=str(updated_by or template.updated_by or ""),
            )

        response_serializer = AssignmentTemplateSerializer(template)
        status_code = (
            status.HTTP_200_OK if existing_template else status.HTTP_201_CREATED
        )
        return Response(response_serializer.data, status=status_code)

    @action(
        detail=True,
        methods=["post"],
        url_path="template/publish",
        url_name="template-publish",
    )
    def publish_template(self, request, pk=None):
        assignment = self.get_object()
        acting_user = self._resolve_request_user(request)
        template = getattr(assignment, "ai_template", None)
        if not template:
            return error_response(
                "Template not found.", status_code=status.HTTP_404_NOT_FOUND
            )

        if not self._can_user_edit_assignment(acting_user, assignment):
            return error_response(
                "You do not have permission to publish this template.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        template.is_published = True
        template.last_published_at = timezone.now()
        updated_by = request.data.get("updatedBy")
        if not acting_user:
            return error_response(
                "Authentication required.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        if not updated_by:
            updated_by = user_display_name(acting_user)
        if updated_by:
            template.updated_by = str(updated_by)
        template.save()

        has_rows = bool(getattr(template, "rows", []))
        assignment.has_template = has_rows
        assignment.template_updated_at = template.updated_at
        assignment.ai_declaration_status = (
            Assignment.STATUS_PUBLISHED if has_rows else Assignment.STATUS_MISSING
        )
        assignment.save()

        self._emit_template_publish_notification(
            assignment,
            acting_user,
            template,
            updated_by_hint=str(updated_by or template.updated_by or ""),
        )

        serializer = AssignmentTemplateSerializer(template)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        url_path="template/unpublish",
        url_name="template-unpublish",
    )
    def unpublish_template(self, request, pk=None):
        assignment = self.get_object()
        template = getattr(assignment, "ai_template", None)
        if not template:
            return error_response(
                "Template not found.", status_code=status.HTTP_404_NOT_FOUND
            )

        acting_user = self._resolve_request_user(request)
        if not self._can_user_edit_assignment(acting_user, assignment):
            return error_response(
                "You do not have permission to unpublish this template.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        template.is_published = False
        updated_by = request.data.get("updatedBy")
        if updated_by:
            template.updated_by = str(updated_by)
        template.save()

        has_rows = bool(getattr(template, "rows", []))
        assignment.has_template = has_rows
        assignment.template_updated_at = template.updated_at
        assignment.ai_declaration_status = (
            Assignment.STATUS_DRAFT if has_rows else Assignment.STATUS_MISSING
        )
        assignment.save()

        serializer = AssignmentTemplateSerializer(template)
        return Response(serializer.data)
