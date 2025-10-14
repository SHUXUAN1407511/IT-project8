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
    /api/courses/           GET / POST
    /api/courses/{id}/      GET / PUT/PATCH / DELETE

    search：
      - filter：?code=CS101&semester=2025S2
      - search：?search=tom（search in code/name/teacher）
      - ordering：?ordering=created_at|-created_at|code|name|semester|credits
      - paging：?page=1&page_size=20
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code", "name", "teacher"]
    ordering_fields = ["created_at", "updated_at", "code", "name", "semester", "credits"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        code = self.request.query_params.get("code")
        semester = self.request.query_params.get("semester")
        if code:
            qs = qs.filter(code=code)
        if semester:
            qs = qs.filter(semester=semester)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)
