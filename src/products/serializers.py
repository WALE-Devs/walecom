from rest_framework import serializers
from .models import Product, ProductImage, ProductVariant, Tag


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'is_main']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price', 'stock']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, required=False)
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects.all())

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'base_sku',
            'category',
            'currency',
            'default_price',
            'default_stock',
            'tags',
            'images',
            'variants'
        ]

    def create(self, validated_data):
        # Get variants if exist
        variants_data = validated_data.pop('variants', [])

        # Create product
        product = Product.objects.create(**validated_data)

        # Create asociated variants
        for variant_data in variants_data:
            ProductVariant.objects.create(product=product, **variant_data)

        return product
