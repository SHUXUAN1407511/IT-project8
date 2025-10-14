from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet

app_name = "courses"

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='courses')

urlpatterns = [
    path('', include(router.urls)),
]
