
from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from .models import AIUserScale
from .serializer import AIUserScaleSerializer

class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

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
