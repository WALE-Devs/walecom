from rest_framework import serializers
from products.models import ProductVariant
from products.serializers import ProductVariantSerializer
from .models import Cart, CartProduct, Order, OrderProduct

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


class OrderProductSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product_variant.product.name')
    variant_name = serializers.ReadOnlyField(source='product_variant.name')

    class Meta:
        model = OrderProduct
        fields = ['id', 'product_name', 'variant_name', 'quantity', 'price_at_purchase']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'total_price', 'shipping_address', 
            'billing_address', 'tracking_number', 'products', 
            'created_at', 'updated_at'
        ]


class CheckoutSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(required=True)
    billing_address = serializers.CharField(required=False)

    def validate(self, data):
        if not data.get('billing_address'):
            data['billing_address'] = data['shipping_address']
        return data
