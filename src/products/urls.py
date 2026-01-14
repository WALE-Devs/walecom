from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductImageViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-images', ProductImageViewSet, basename='productimage')

urlpatterns = router.urls