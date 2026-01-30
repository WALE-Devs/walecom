import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
User = get_user_model()
from products.models import Product, Category, ProductVariant

# All common fixtures (api_client, admin_user, category)
# are now available from utils.test_helpers via conftest.py

@pytest.mark.django_db
class TestViewSetExtra:
    def test_product_create_no_variants_trigger_perform_create(self, api_client, admin_user, category):
        """Covers products/views.py line 38: creation of default variant in view."""
        api_client.force_authenticate(user=admin_user)
        url = reverse('product-list')
        data = {
            'name': 'No Variant Prod',
            'description': 'D',
            'base_sku': 'NOVAR',
            'default_price': 100,
            'category': category.id
        }
        # We need to make sure the signal doesn't run or we check the logic in ViewSet.
        # Actually, if signal runs, perform_create check `if not product.variants.exists()` will be false.
        # To test the ViewSet logic specifically, we could temporarily disable signals, 
        # but let's see if we can just trigger it.
        
        with patch('products.signals.create_default_variant') as mocked_signal:
            response = api_client.post(url, data)
            assert response.status_code == status.HTTP_201_CREATED
            product = Product.objects.get(name='No Variant Prod')
            # The ViewSet should have created it because the signal was mocked
            assert product.variants.count() == 1
            assert product.variants.first().name == "Default"

    def test_checkout_general_exception(self, api_client, admin_user, category):
        """Covers orders/views.py line 159: general exception handling."""
        from orders.models import Cart, CartProduct
        api_client.force_authenticate(user=admin_user)
        p = Product.objects.create(name='P', base_sku='B', default_price=10, category=category)
        v = ProductVariant.objects.get(product=p)
        v.stock = 10
        v.save()
        cart = Cart.objects.create(user=admin_user)
        CartProduct.objects.create(cart=cart, product_variant=v, quantity=1)
        
        url = reverse('orders-checkout')
        data = {'shipping_address': 'Some place'}
        
        # Mock Order.objects.create to raise a general Exception
        with patch('orders.views.Order.objects.create', side_effect=Exception("Boom")):
            response = api_client.post(url, data)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.data['error'] == "Error al procesar el pedido"

    def test_product_image_viewset_list(self, api_client, category):
        """Covers products/views.py line 54 (AllowAny retrieval)."""
        p = Product.objects.create(name='P', base_sku='B', default_price=10, category=category)
        from products.models import ProductImage
        ProductImage.objects.create(product=p, position=1)
        
        url = reverse('productimage-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
