import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from products.models import Product, Category


@pytest.mark.django_db
class TestProductPagination:
    def setup_method(self):
        self.client = APIClient()
        self.category = Category.objects.create(
            name="Test Category", description="Test Description"
        )

        # Create 15 products to test pagination (default is 10)
        self.products = [
            Product.objects.create(
                name=f"Product {i}",
                description=f"Description {i}",
                base_sku=f"SKU-{i}",
                category=self.category,
                default_price=10.00,
            )
            for i in range(15)
        ]
        self.url = reverse("product-list")

    def test_default_pagination(self):
        """Test that default pagination returns 10 items."""
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert len(response.data["results"]) == 10
        assert response.data["count"] == 15
        assert response.data["next"] is not None
        assert response.data["previous"] is None

    def test_custom_page_size(self):
        """Test that custom page_size query parameter works."""
        response = self.client.get(self.url, {"page_size": 5})
        assert response.status_code == 200
        assert len(response.data["results"]) == 5
        assert response.data["count"] == 15

    def test_max_page_size(self):
        """Test that requesting more than max_page_size returns max_page_size (100)."""
        # Create more products to exceed the default 15
        for i in range(15, 110):
            Product.objects.create(
                name=f"Product {i}",
                description=f"Description {i}",
                base_sku=f"SKU-{i}",
                category=self.category,
                default_price=10.00,
            )

        response = self.client.get(self.url, {"page_size": 150})
        assert response.status_code == 200
        # Since max_page_size is 100, it should return 100 items even if 150 requested
        assert len(response.data["results"]) == 100
