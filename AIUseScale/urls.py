from rest_framework.routers import DefaultRouter
from .views import AIUserScaleViewSet, ScaleRecordViewSet

router = DefaultRouter()

router.register(r'aiusescale', AIUserScaleViewSet, basename='aiusescale')
router.register(r'scales', AIUserScaleViewSet, basename='scales')

router.register(r'scale-records', ScaleRecordViewSet, basename='scale-records')

urlpatterns = router.urls
