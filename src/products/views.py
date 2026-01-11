from rest_framework import viewsets
from .models import Product, ProductVariant, ProductImage
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductImageSerializer


class ProductViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'

    def get_queryset(self):
        base_qs = Product.objects.select_related('category')
        if self.action == 'list':
            return base_qs.prefetch_related('tags', 'images')
        return base_qs.prefetch_related('tags', 'images', 'variants')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

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
