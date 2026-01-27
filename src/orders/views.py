from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartProduct
from .serializers import CartSerializer, CartItemSerializer
from products.models import ProductVariant

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # A user only has one cart (OneToOneField)
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def list(self, request, *args, **kwargs):
        """Returns the current user's cart."""
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Adds a product variant to the cart."""
        cart = self.get_object()
        variant_id = request.data.get('product_variant_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response({"error": "Product variant not found"}, status=status.HTTP_404_NOT_FOUND)

        if variant.stock < quantity:
            return Response({"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartProduct.objects.get_or_create(
            cart=cart, 
            product_variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """Updates the quantity of an item in the cart."""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity'))

        try:
            cart_item = CartProduct.objects.get(id=item_id, cart=cart)
        except CartProduct.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)

        if quantity <= 0:
            cart_item.delete()
        else:
            if cart_item.product_variant.stock < quantity:
                return Response({"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = quantity
            cart_item.save()

        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Removes an item from the cart."""
        cart = self.get_object()
        item_id = request.data.get('item_id')

        try:
            cart_item = CartProduct.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except CartProduct.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)

        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clears the cart."""
        cart = self.get_object()
        cart.items.all().delete()
        return Response(CartSerializer(cart).data)
