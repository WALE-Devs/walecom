from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from products.models import Category


class CategoryAPITests(APITestCase):
    def setUp(self):
        self.cat1 = Category.objects.create(
            name="Ropa", description="Prendas de vestir"
        )
        self.cat2 = Category.objects.create(
            name="Calzado", description="Zapatos y zapatillas"
        )
        self.list_url = reverse("category-list")

    def test_list_categories(self):
        """Test that we can list all categories."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that we have 2 categories
        self.assertEqual(len(response.data), 2)

        # Verify fields in the first item
        item = response.data[0]
        self.assertEqual(item["name"], self.cat1.name)
        self.assertEqual(item["slug"], self.cat1.slug)
        self.assertEqual(item["description"], self.cat1.description)

    def test_retrieve_category(self):
        """Test that we can retrieve a single category by slug."""
        url = reverse("category-detail", kwargs={"slug": self.cat1.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.cat1.name)

    def test_retrieve_non_existent_category(self):
        """Test that retrieving a non-existent category returns 404."""
        url = reverse("category-detail", kwargs={"slug": "non-existent"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_category_list_is_public(self):
        """Test that the category list is accessible without authentication."""
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
