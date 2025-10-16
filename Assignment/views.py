from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from usersystem.models import User
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
