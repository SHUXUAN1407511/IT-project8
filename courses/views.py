from rest_framework import viewsets, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Course
from .serializer import CourseSerializer
from usersystem.permissions import ActiveUserPermission, RolePermission, resolve_active_user

class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [ActiveUserPermission, RolePermission]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'course_name', 'semester']
    ordering_fields = ['created_at', 'updated_at', 'code', 'course_name', 'semester']
    ordering = ['-created_at']
    role_permissions = {
        'list': ['admin', 'sc'],
        'retrieve': ['admin', 'sc'],
        'default': ['admin', 'sc'],
    }

    def get_queryset(self):
        qs = super().get_queryset()
        code = self.request.query_params.get('code')
        semester = self.request.query_params.get('semester')
        coordinator_id = self.request.query_params.get('coordinatorId')
        acting_user = resolve_active_user(self.request)

        if acting_user and getattr(acting_user, "role", None) == 'sc':
            qs = qs.filter(coordinator=acting_user)

        if code:
            qs = qs.filter(code=code)
        if semester:
            qs = qs.filter(semester=semester)
        if coordinator_id:
            qs = qs.filter(coordinator_id=coordinator_id)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'deleted successfully'}, status=status.HTTP_200_OK)
