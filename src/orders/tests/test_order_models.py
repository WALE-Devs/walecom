import pytest

from django.contrib.auth import get_user_model
from orders.models import Cart, Order, OrderProduct

User = get_user_model()

# All common fixtures (user, product, variant)
# are now available from utils.test_helpers via conftest.py


@pytest.mark.django_db
class TestOrderModels:
    def test_order_str(self, user):
        order = Order.objects.create(
            user=user, total_price=100, shipping_address="Addr", billing_address="Addr"
        )
        assert str(order) == f"Pedido {order.id} - {user.email}"

    def test_order_product_str(self, user, variant):
        order = Order.objects.create(
            user=user, total_price=100, shipping_address="Addr", billing_address="Addr"
        )
        op = OrderProduct.objects.create(
            order=order, product_variant=variant, quantity=2, price_at_purchase=500
        )
        assert str(op) == f"2 x {variant.product.name} (Default)"

    def test_cart_str(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        assert str(cart) == f"{user.email}'s cart "

    def test_cart_manager_create_from_products(self, user, variant):
        products_data = [{"product_variant_id": variant, "quantity": 3}]
        # Delete existing cart if any
        Cart.objects.filter(user=user).delete()

        cart = Cart.objects.create_from_products(user, products_data)
        assert Cart.objects.filter(user=user).count() == 1
        assert cart.items.count() == 1
        assert cart.items.first().quantity == 3
        assert cart.items.first().product_variant == variant
