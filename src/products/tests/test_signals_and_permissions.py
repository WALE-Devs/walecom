import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from products.models import Product, ProductVariant

User = get_user_model()

# All common fixtures (api_client, admin_user, normal_user, category)
# are now available from utils.test_helpers via conftest.py


@pytest.mark.django_db
class TestProductPermissions:
    def test_product_permissions(self, api_client, admin_user, normal_user, category):
        url = reverse("product-list")
        data = {
            "name": "New",
            "description": "D",
            "base_sku": "SKU",
            "default_price": 10,
            "category": category.id,
        }

        # List Public - OK
        assert api_client.get(url).status_code == status.HTTP_200_OK

        # Create Public - Fail
        assert api_client.post(url, data).status_code == status.HTTP_401_UNAUTHORIZED

        # Create Normal User - Fail
        api_client.force_authenticate(user=normal_user)
        assert api_client.post(url, data).status_code == status.HTTP_403_FORBIDDEN

        # Create Admin - OK
        api_client.force_authenticate(user=admin_user)
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestProductSignals:
    def test_default_variant_created_on_product_create(self, category):
        # Trigger creation via Model
        p = Product.objects.create(
            name="Test Product", base_sku="TEST", default_price=10.00, category=category
        )
        # Signal should have created a variant
        assert ProductVariant.objects.filter(product=p).count() == 1
        variant = ProductVariant.objects.get(product=p)
        assert variant.name == "Default"
        assert variant.sku == "TEST-DEF"
        assert variant.price == 10.00

    def test_signal_does_not_create_if_variants_exist(self, category):
        # This is harder to test directly without mocking signals,
        # but we can verify that manual creation followed by save doesn't double-create.
        p = Product.objects.create(
            name="P", base_sku="B", default_price=10, category=category
        )
        # Variant already created by signal above.
        assert p.variants.count() == 1

        # If we save again, it shouldn't create another one
        p.save()
        assert p.variants.count() == 1
