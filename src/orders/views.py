from decimal import Decimal

from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartProduct, Order, OrderProduct
from .serializers import (
    CartSerializer,
    OrderSerializer,
    CheckoutSerializer,
)
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

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """Adds a product variant to the cart."""
        cart = self.get_object()
        variant_id = request.data.get("product_variant_id")
        quantity = int(request.data.get("quantity", 1))

        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response(
                {"error": "Product variant not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if variant.stock < quantity:
            return Response(
                {"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = CartProduct.objects.get_or_create(
            cart=cart, product_variant=variant, defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def update_quantity(self, request):
        """Updates the quantity of an item in the cart."""
        cart = self.get_object()
        item_id = request.data.get("item_id")
        quantity = int(request.data.get("quantity"))

        try:
            cart_item = CartProduct.objects.get(id=item_id, cart=cart)
        except CartProduct.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND
            )

        if quantity <= 0:
            cart_item.delete()
        else:
            if cart_item.product_variant.stock < quantity:
                return Response(
                    {"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = quantity
            cart_item.save()

        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        """Removes an item from the cart."""
        cart = self.get_object()
        item_id = request.data.get("item_id")

        try:
            cart_item = CartProduct.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except CartProduct.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["post"])
    def clear(self, request):
        """Clears the cart."""
        cart = self.get_object()
        cart.items.all().delete()
        return Response(CartSerializer(cart).data)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "products__product_variant__product"
        )

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """
        Converts the current user's cart into an Order.
        Expects: shipping_address (and optional billing_address)
        """
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.select_related("product_variant").all()

        if not cart_items:
            return Response(
                {"error": "El carrito está vacío"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # 1. Total and stock check
                total_price = Decimal("0.00")
                for item in cart_items:
                    if item.product_variant.stock < item.quantity:
                        raise ValueError(
                            f"Stock insuficiente para {item.product_variant.product.name}"
                        )
                    total_price += item.product_variant.price * item.quantity

                # 2. Create Order
                order = Order.objects.create(
                    user=request.user,
                    status="PENDING",
                    total_price=total_price,
                    shipping_address=serializer.validated_data["shipping_address"],
                    billing_address=serializer.validated_data["billing_address"],
                )

                # 3. Create items, snap prices and decrement stock
                for item in cart_items:
                    OrderProduct.objects.create(
                        order=order,
                        product_variant=item.product_variant,
                        quantity=item.quantity,
                        price_at_purchase=item.product_variant.price,
                    )
                    # Decrement stock
                    variant = item.product_variant
                    variant.stock -= item.quantity
                    variant.save()

                # 4. Clear Cart
                cart.items.all().delete()

                return Response(
                    OrderSerializer(order).context.update({"request": request})
                    or OrderSerializer(order).data,
                    status=status.HTTP_201_CREATED,
                )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(
                {"error": "Error al procesar el pedido"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
