from rest_framework.routers import DefaultRouter
from .views import ContentViewSet, ContentBlockViewSet

router = DefaultRouter()
router.register(r'content', ContentViewSet)
router.register(r'content-blocks', ContentBlockViewSet)

urlpatterns = router.urls
