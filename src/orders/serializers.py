from rest_framework import serializers
from products.models import ProductVariant
from products.serializers import ProductVariantSerializer
from .models import Cart, CartProduct

class CartItemSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantSerializer(read_only=True)
    product_variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source='product_variant',
        write_only=True
    )
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartProduct
        fields = ['id', 'product_variant', 'product_variant_id', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return obj.product_variant.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'total_items']
        read_only_fields = ['user']

    def get_total_price(self, obj):
        return sum(item.product_variant.price * item.quantity for item in obj.items.all())

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())
