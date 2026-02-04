import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from products.models import Product, Category, Tag


@pytest.mark.django_db
class TestProductFiltering:
    def setup_method(self):
        self.client = APIClient()

        # Create categories
        self.cat1 = Category.objects.create(name="Electronics", description="Desc")
        self.cat2 = Category.objects.create(name="Home", description="Desc")

        # Create tags
        self.tag_new = Tag.objects.create(name="new")
        self.tag_featured = Tag.objects.create(name="featured")
        self.tag_sale = Tag.objects.create(name="sale")

        # Create products
        self.p1 = Product.objects.create(
            name="Laptop",
            description="High performance",
            base_sku="LAPTOP1",
            category=self.cat1,
            default_price=1000.00,
        )
        self.p1.tags.add(self.tag_new, self.tag_featured)

        self.p2 = Product.objects.create(
            name="Phone",
            description="Smart phone",
            base_sku="PHONE1",
            category=self.cat1,
            default_price=500.00,
        )
        self.p2.tags.add(self.tag_new, self.tag_sale)

        self.p3 = Product.objects.create(
            name="Lamp",
            description="Bedside lamp",
            base_sku="LAMP1",
            category=self.cat2,
            default_price=30.00,
        )
        self.p3.tags.add(self.tag_featured)

        self.url = reverse("product-list")

    def test_filter_by_category(self):
        response = self.client.get(self.url, {"category": self.cat1.slug})
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert len(results) == 2
        names = [item["name"] for item in results]
        assert "Laptop" in names
        assert "Phone" in names
        assert "Lamp" not in names

    def test_filter_by_single_tag(self):
        response = self.client.get(self.url, {"tags": "new"})
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert len(results) == 2
        names = [item["name"] for item in results]
        assert "Laptop" in names
        assert "Phone" in names
        assert "Lamp" not in names

    def test_filter_by_multiple_tags_and(self):
        response = self.client.get(self.url, {"tags": "new,featured"})
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Laptop"

    def test_filter_by_combined_category_and_tags(self):
        # Category Home (cat2) + Tag featured -> Lamp
        response = self.client.get(
            self.url, {"category": self.cat2.slug, "tags": "featured"}
        )
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Lamp"

    def test_filter_nonexistent_category(self):
        response = self.client.get(self.url, {"category": "nonexistent"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 0

    def test_filter_nonexistent_tag(self):
        response = self.client.get(self.url, {"tags": "ghost"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 0

    def test_filter_by_tags_with_whitespace(self):
        # Testing "new, featured" with whitespace
        response = self.client.get(self.url, {"tags": "new, featured"})
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Laptop"

    def test_filter_by_tags_empty_string(self):
        # Empty tags string should be ignored by our filter method and return all products
        response = self.client.get(self.url, {"tags": ""})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3

    def test_filter_by_category_no_products(self):
        cat_empty = Category.objects.create(
            name="Empty", description="No products here"
        )
        response = self.client.get(self.url, {"category": cat_empty.slug})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 0

    def test_filter_by_multiple_tags_no_match(self):
        # sale (Phone) and featured (Laptop, Lamp) -> no product has both
        response = self.client.get(self.url, {"tags": "sale,featured"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 0

    def test_search_by_name(self):
        # Search for "Lap" should return "Laptop"
        response = self.client.get(self.url, {"search": "Lap"})
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Laptop"

        # Search for "ne" should return "Phone"
        response = self.client.get(self.url, {"search": "ne"})
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert len(results) == 1
        assert results[0]["name"] == "Phone"
