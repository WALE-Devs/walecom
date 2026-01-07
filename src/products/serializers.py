from rest_framework import serializers
from .models import Product, ProductImage, ProductVariant


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'price', 'currency', 'stock']



class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)


    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'base_sku',
            'category',
            'default_currency',
            'default_price',
            'default_stock',
            'images',
            'variants'
        ]
