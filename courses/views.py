from rest_framework import viewsets, permissions, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Course
from .serializer import CourseSerializer

class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class CourseViewSet(viewsets.ModelViewSet):
    """
    /courses/           GET / POST
    /courses/{id}/      GET / PUT/PATCH / DELETE

    支持：
    - 搜索：?search=xxx（在 code / Course_name / semester 上）
    - 排序：?ordering=created_at|-created_at|code|Course_name|semester
    - 过滤：?code=CS101&semester=2025S1
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'Course_name', 'semester']
    ordering_fields = ['created_at', 'updated_at', 'code', 'Course_name', 'semester']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        code = self.request.query_params.get('code')
        semester = self.request.query_params.get('semester')
        if code:
            qs = qs.filter(code=code)
        if semester:
            qs = qs.filter(semester=semester)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'deleted successfully'}, status=status.HTTP_200_OK)
