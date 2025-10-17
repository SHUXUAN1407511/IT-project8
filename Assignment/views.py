from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from usersystem.models import User
from template.serializers import AssignmentTemplateSerializer
from .models import Assignment
from .serializer import AssignmentSerializer


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    /assignments/           list/create
    /assignments/{id}/      retrieve/update/delete

    支持的查询参数:
    - courseId: 课程 ID
    - keyword: 名称或描述关键字
    - type: 作业类型
    - status: aiDeclarationStatus
    - ordering: created_at/-created_at/due_date/-due_date/name/-name
    """

    serializer_class = AssignmentSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination
    ordering_fields = ["due_date", "created_at", "name"]
    ordering = ["-created_at"]

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
        username = params.get("username")

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

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None
            if user and user.role == "tutor":
                queryset = queryset.filter(tutors=user)

        if ordering:
            allowed = {"created_at", "due_date", "name"}
            order_field = ordering.lstrip("-")
            if order_field in allowed:
                queryset = queryset.order_by(ordering)

        return queryset.distinct()

    def _resolve_request_user(self, request):
        """
        Try to resolve the business user making the request.
        Supports multiple hints (authenticated user, headers, params, payload).
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

    def create(self, request, *args, **kwargs):
        user = self._resolve_request_user(request)
        if user and user.role == "tutor":
            return Response(
                {"message": "Tutors are not allowed to create assignments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="template", url_name="template")
    def retrieve_template(self, request, pk=None):
        assignment = self.get_object()
        template = getattr(assignment, "ai_template", None)
        if not template:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = AssignmentTemplateSerializer(template)
        return Response(serializer.data)

    @retrieve_template.mapping.post
    def save_template(self, request, pk=None):
        assignment = self.get_object()
        existing_template = getattr(assignment, "ai_template", None)
        publish = request.data.get("publish", False)
        updated_by = request.data.get("updatedBy")

        if not updated_by:
            user = getattr(request, "user", None)
            if getattr(user, "is_authenticated", False):
                updated_by = getattr(user, "name", None) or getattr(
                    user, "get_full_name", lambda: ""
                )()
                if not updated_by:
                    updated_by = getattr(user, "username", "") or str(user)

        serializer_data = request.data.copy()
        if isinstance(serializer_data, (list, tuple)):
            return Response(
                {"detail": "Invalid payload format."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer_data.pop("publish", None)

        if existing_template:
            serializer = AssignmentTemplateSerializer(
                existing_template, data=serializer_data, partial=True
            )
        else:
            serializer = AssignmentTemplateSerializer(data=serializer_data)

        serializer.is_valid(raise_exception=True)
        template = serializer.save(assignment=assignment) if not existing_template else serializer.save()

        # Update template publishing state
        now = timezone.now()
        if publish:
            template.is_published = True
            template.last_published_at = now
        else:
            template.is_published = False
        if updated_by:
            template.updated_by = str(updated_by)
        template.save()

        # Reflect template status on the assignment
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
        template = getattr(assignment, "ai_template", None)
        if not template:
            return Response(
                {"detail": "Template not found."}, status=status.HTTP_404_NOT_FOUND
            )

        template.is_published = True
        template.last_published_at = timezone.now()
        updated_by = request.data.get("updatedBy")
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
            return Response(
                {"detail": "Template not found."}, status=status.HTTP_404_NOT_FOUND
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
