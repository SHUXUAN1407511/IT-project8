from rest_framework.routers import DefaultRouter
from .views import AIUserScaleViewSet

router = DefaultRouter()
router.register(r'aiusescale', AIUserScaleViewSet, basename='aiusescale')  # 兼容老路径
router.register(r'scales', AIUserScaleViewSet, basename='scales')          # 新路径，建议前端改用

urlpatterns = router.urls
