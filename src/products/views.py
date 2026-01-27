from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from .models import Product, ProductVariant, ProductImage
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductImageSerializer
from .filters import ProductFilter


class ProductViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name']

    def get_queryset(self):
        base_qs = Product.objects.select_related('category')
        if self.action == 'list':
            return base_qs.prefetch_related('tags', 'images')
        return base_qs.prefetch_related('tags', 'images', 'variants')

    def get_permissions(self):
        """Public read, admin-only write."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

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
    queryset = ProductImage.objects.select_related('product').order_by('position')
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        """Public read, admin-only write."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
