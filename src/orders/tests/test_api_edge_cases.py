import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
User = get_user_model()
from products.models import Product, ProductVariant, Category
from orders.models import Cart, CartProduct

# All common fixtures (api_client, user, variant, category)
# are now available from utils.test_helpers via conftest.py

@pytest.mark.django_db
class TestOrderApiEdgeCases:
    def test_add_item_variant_not_found(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('cart-add-item')
        response = api_client.post(url, {'product_variant_id': 999, 'quantity': 1})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_add_item_insufficient_stock(self, api_client, user, variant):
        api_client.force_authenticate(user=user)
        url = reverse('cart-add-item')
        response = api_client.post(url, {'product_variant_id': variant.id, 'quantity': 15})  # Exceeds stock of 10
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_item_existing_increment(self, api_client, user, variant):
        api_client.force_authenticate(user=user)
        url = reverse('cart-add-item')
        api_client.post(url, {'product_variant_id': variant.id, 'quantity': 1})
        response = api_client.post(url, {'product_variant_id': variant.id, 'quantity': 1})
        assert response.status_code == status.HTTP_201_CREATED
        cart = Cart.objects.get(user=user)
        assert cart.items.first().quantity == 2

    def test_update_quantity_item_not_found(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('cart-update-quantity')
        response = api_client.post(url, {'item_id': 999, 'quantity': 5})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_quantity_to_zero_deletes(self, api_client, user, variant):
        api_client.force_authenticate(user=user)
        cart = Cart.objects.create(user=user)
        item = CartProduct.objects.create(cart=cart, product_variant=variant, quantity=1)
        url = reverse('cart-update-quantity')
        response = api_client.post(url, {'item_id': item.id, 'quantity': 0})
        assert response.status_code == status.HTTP_200_OK
        assert CartProduct.objects.count() == 0

    def test_update_quantity_insufficient_stock(self, api_client, user, variant):
        api_client.force_authenticate(user=user)
        cart = Cart.objects.create(user=user)
        item = CartProduct.objects.create(cart=cart, product_variant=variant, quantity=1)
        url = reverse('cart-update-quantity')
        response = api_client.post(url, {'item_id': item.id, 'quantity': 15})  # Exceeds stock of 10
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_item_not_found(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('cart-remove-item')
        response = api_client.post(url, {'item_id': 999})
        assert response.status_code == status.HTTP_404_NOT_FOUND
