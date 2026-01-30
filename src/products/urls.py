from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductImageViewSet

router = DefaultRouter()
router.register(r'images', ProductImageViewSet, basename='productimage')
router.register(r'', ProductViewSet, basename='product')

urlpatterns = router.urls