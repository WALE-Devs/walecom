import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
User = get_user_model()
from products.models import Product, ProductVariant, Category
from orders.models import Cart, CartProduct

# All common fixtures (api_client, user, authenticated_client, product, variant, category)
# are now available from utils.test_helpers via conftest.py

@pytest.mark.django_db
class TestCartAPI:
    def test_get_cart_creates_if_not_exists(self, authenticated_client, user):
        url = reverse('cart-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert Cart.objects.filter(user=user).exists()
        assert response.data['user'] == user.id
        assert response.data['total_price'] == 0

    def test_add_item_to_cart(self, authenticated_client, variant):
        url = reverse('cart-add-item')
        data = {'product_variant_id': variant.id, 'quantity': 2}
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['total_items'] == 2
        assert response.data['total_price'] == 200.00  # 2 * 100.00
        
        # Check database
        cart_item = CartProduct.objects.get(product_variant=variant)
        assert cart_item.quantity == 2

    def test_add_item_insufficient_stock(self, authenticated_client, variant):
        url = reverse('cart-add-item')
        data = {'product_variant_id': variant.id, 'quantity': 11} # Stock is 10
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Not enough stock" in response.data['error']

    def test_update_quantity(self, authenticated_client, variant):
        # First add
        cart = Cart.objects.create(user=User.objects.get(email='test@example.com'))
        cart_item = CartProduct.objects.create(cart=cart, product_variant=variant, quantity=1)
        
        url = reverse('cart-update-quantity')
        data = {'item_id': cart_item.id, 'quantity': 5}
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 5
        
        cart_item.refresh_from_db()
        assert cart_item.quantity == 5

    def test_remove_item(self, authenticated_client, variant):
        cart = Cart.objects.create(user=User.objects.get(email='test@example.com'))
        cart_item = CartProduct.objects.create(cart=cart, product_variant=variant, quantity=1)
        
        url = reverse('cart-remove-item')
        data = {'item_id': cart_item.id}
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 0
        assert not CartProduct.objects.filter(id=cart_item.id).exists()

    def test_clear_cart(self, authenticated_client, variant):
        cart = Cart.objects.create(user=User.objects.get(email='test@example.com'))
        CartProduct.objects.create(cart=cart, product_variant=variant, quantity=1)
        
        url = reverse('cart-clear')
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_items'] == 0
        assert cart.items.count() == 0
