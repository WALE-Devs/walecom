from rest_framework.routers import DefaultRouter
from .views import ContentViewSet, ContentBlockViewSet

router = DefaultRouter()
router.register(r"blocks", ContentBlockViewSet, basename="contentblock")
router.register(r"", ContentViewSet, basename="content")

urlpatterns = router.urls
