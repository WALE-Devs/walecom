from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductImageViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)


urlpatterns = router.urls