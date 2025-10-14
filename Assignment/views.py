# Assignment/views.py
from rest_framework import viewsets, permissions, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Assignment
from .serializer import AssignmentSerializer

class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class AssignmentViewSet(viewsets.ModelViewSet):
    """
    /api/assignments/  list/create
    /api/assignments/{id}/  update/delete
    allow：?search=keyword（subject / assignment_title）
         ?ordering=due_date|-due_date|created_at|-created_at
    """
    queryset = Assignment.objects.all().order_by("-created_at")
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = DefaultPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["subject", "assignment_title"]
    ordering_fields = ["due_date", "created_at", "assignment_title", "subject"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "deleted successfully"}, status=status.HTTP_200_OK)
