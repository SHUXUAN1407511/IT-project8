
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet

app_name = "Assignment"

router = DefaultRouter()
router.register(r'assignments', AssignmentViewSet, basename='assignments')

urlpatterns = [
    path('', include(router.urls)),
]
