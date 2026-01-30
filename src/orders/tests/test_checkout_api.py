import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
User = get_user_model()
from products.models import Product, ProductVariant, Category
from orders.models import Cart, CartProduct, Order, OrderProduct
from decimal import Decimal

# All common fixtures (api_client, user, product, variant, category)
# are now available from utils.test_helpers via conftest.py

@pytest.fixture
def auth_client(authenticated_client):
    """Alias for authenticated_client to match existing test naming."""
    return authenticated_client

@pytest.mark.django_db
class TestCheckoutFlow:
    def test_checkout_success(self, auth_client, user, variant):
        # 1. Add item to cart
        cart, _ = Cart.objects.get_or_create(user=user)
        CartProduct.objects.create(cart=cart, product_variant=variant, quantity=2)
        
        # 2. Perform checkout
        url = reverse('orders-checkout')
        data = {
            "shipping_address": "Calle Falsa 123, Lima",
            "billing_address": "Misma que envío"
        }
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Decimal(response.data['total_price']) == Decimal("200.00")
        assert response.data['status'] == 'PENDING'
        
        # 3. Verify Order in DB
        order = Order.objects.get(user=user)
        assert order.total_price == Decimal("200.00")
        assert order.products.count() == 1
        assert order.shipping_address == "Calle Falsa 123, Lima"
        
        # 4. Verify stock decrement
        variant.refresh_from_db()
        assert variant.stock == 8
        
        # 5. Verify cart is empty
        assert cart.items.count() == 0

    def test_checkout_insufficient_stock(self, auth_client, user, variant):
        cart, _ = Cart.objects.get_or_create(user=user)
        # Attempt to buy more than stock (stock is 10)
        CartProduct.objects.create(cart=cart, product_variant=variant, quantity=15)
        
        url = reverse('orders-checkout')
        data = {"shipping_address": "Address"}
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "insuficiente" in response.data['error']
        
        # Verify no order created
        assert not Order.objects.filter(user=user).exists()
        
        # Verify stock NOT decremented (transaction rollback)
        variant.refresh_from_db()
        assert variant.stock == 10

    def test_checkout_empty_cart(self, auth_client, user):
        url = reverse('orders-checkout')
        data = {"shipping_address": "Address"}
        response = auth_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "vacío" in response.data['error']

    def test_price_snapshot(self, auth_client, user, variant):
        cart, _ = Cart.objects.get_or_create(user=user)
        CartProduct.objects.create(cart=cart, product_variant=variant, quantity=1)
        
        # Checkout
        url = reverse('orders-checkout')
        auth_client.post(url, {"shipping_address": "Addr"})
        
        # Change variant price AFTER order
        variant.price = Decimal("150.00")
        variant.save()
        
        # Verify order price is still the same (SNAPSHOT)
        order_product = OrderProduct.objects.get(product_variant=variant)
        assert order_product.price_at_purchase == Decimal("100.00")
