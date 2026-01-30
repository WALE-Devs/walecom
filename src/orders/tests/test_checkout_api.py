import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from products.models import Product, ProductVariant, Category
from orders.models import Cart, CartProduct, Order, OrderProduct
from decimal import Decimal

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='buyer', password='password123')

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def product(db):
    cat = Category.objects.create(name="Cat", slug="cat")
    return Product.objects.create(
        name="Pro", 
        base_sku="PRO", 
        category=cat, 
        default_price=Decimal("100.00"),
        default_stock=10
    )

@pytest.fixture
def variant(product):
    # System signal creates a default variant.
    v = product.variants.first()
    v.stock = 10
    v.price = Decimal("100.00")
    v.save()
    return v

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
