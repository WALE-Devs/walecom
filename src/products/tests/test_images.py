import os
import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from rest_framework.test import APIClient
from products.models import Product, ProductImage

from django.contrib.auth import get_user_model
User = get_user_model()

@pytest.mark.django_db
class TestProductImages:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(email='admin@example.com', password='password')
        self.client.force_authenticate(user=self.user)
        
        self.product = Product.objects.create(
            name="Test Product",
            description="Test",
            base_sku="TEST-IMG",
            default_price=10.00
        )
        self.url = reverse('productimage-list')

    def test_image_upload(self):
        # Create a small dummy image
        image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
        image_file = SimpleUploadedFile("test.gif", image_content, content_type="image/gif")
        
        response = self.client.post(self.url, {
            'product': self.product.id,
            'image': image_file,
            'position': 1
        }, format='multipart')
        
        assert response.status_code == 201
        data = response.json()
        assert 'image' in data
        # Django might append random chars, so we check if the base name is in the result
        assert 'test' in data['image']
        assert 'gif' in data['image']
        
        # Verify file exists on disk
        product_image = ProductImage.objects.get(id=data['id'])
        assert os.path.exists(product_image.image.path)

    @pytest.mark.django_db(transaction=True)
    def test_image_cleanup_on_delete(self):
        # 1. Create an image
        image_content = b'dummy_data'
        image_file = SimpleUploadedFile("delete_me.jpg", image_content, content_type="image/jpeg")
        product_image = ProductImage.objects.create(
            product=self.product,
            image=image_file,
            position=2
        )
        file_path = product_image.image.path
        assert os.path.exists(file_path)
        
        # 2. Delete the record
        product_image.delete()
        
        # 3. Verify file is gone (via django-cleanup)
        assert not os.path.exists(file_path)

    def test_product_detail_contains_images(self):
        # Create an image for the product
        ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile("detail.jpg", b"data", content_type="image/jpeg"),
            position=0
        )
        
        detail_url = reverse('product-detail', kwargs={'slug': self.product.slug})
        response = self.client.get(detail_url)
        
        assert response.status_code == 200
        data = response.json()
        assert 'images' in data
        assert len(data['images']) == 1
        assert 'main_image' in data
        # Check if the path contains our base filename
        assert 'detail' in data['main_image']
