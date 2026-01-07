from rest_framework import viewsets
from .models import Product, ProductVariant, ProductImage
from .serializers import ProductSerializer, ProductImageSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').prefetch_related('tags', 'images', 'variants')
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        product = serializer.save()
        if not product.variants.exists():
            ProductVariant.objects.create(
                product=product,
                name="Default",
                sku=f"{product.base_sku}-DEF",
                price=product.default_price,
                stock=product.default_stock or 0,
            )


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
