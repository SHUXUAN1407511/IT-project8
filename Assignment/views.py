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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)
