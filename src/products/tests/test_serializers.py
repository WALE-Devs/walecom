import pytest
from rest_framework import serializers
from products.models import Product, Category, Tag, ProductVariant, ProductImage, Attribute, AttributeValue
from products.serializers import ProductDetailSerializer, ProductVariantSerializer, ProductListSerializer

# All common fixtures (category, product)
# are now available from utils.test_helpers via conftest.py

@pytest.fixture
def api_request(db):
    """Creates a mock API request for serializer context."""
    from rest_framework.request import Request
    from rest_framework.test import APIRequestFactory
    factory = APIRequestFactory()
    request = factory.get('/')
    return request

@pytest.mark.django_db
class TestProductSerializers:
    def test_product_variant_serializer_create_with_attributes(self, product):
        data = {
            'name': 'Silver',
            'sku': 'PH-SILV',
            'price': 550.00,
            'stock': 5,
            'attributes': {'Color': 'Silver', 'Storage': '128GB'}
        }
        serializer = ProductVariantSerializer(data=data)
        assert serializer.is_valid()
        variant = serializer.save(product=product)
        
        assert variant.attribute_values.count() == 2
        assert Attribute.objects.filter(name='Color').exists()
        assert AttributeValue.objects.filter(value='Silver').exists()

    def test_product_variant_serializer_update_attributes(self, product):
        variant = ProductVariant.objects.create(product=product, name='Test', sku='T1', price=10, stock=1)
        attr = Attribute.objects.create(name='Size')
        val = AttributeValue.objects.create(attribute=attr, value='M')
        variant.attribute_values.add(val)
        
        data = {'attributes': {'Size': 'L'}}
        serializer = ProductVariantSerializer(variant, data=data, partial=True)
        assert serializer.is_valid()
        serializer.save()
        
        assert variant.attribute_values.count() == 1
        assert variant.attribute_values.first().value == 'L'

    def test_product_list_serializer_no_image(self, product):
        serializer = ProductListSerializer(product)
        assert serializer.data['image'] is None

    def test_product_detail_serializer_create_nested(self, category):
        data = {
            'name': 'Laptop',
            'description': 'A laptop',
            'base_sku': 'LAP',
            'category': category.id,
            'currency': 'USD',
            'default_price': 1000.00,
            'default_stock': 5,
            'tags': ['tech', 'portable'],
            'variants': [
                {'name': 'Pro', 'sku': 'LAP-PRO', 'price': 1200, 'stock': 2, 'attributes': {'RAM': '16GB'}}
            ]
        }
        serializer = ProductDetailSerializer(data=data)
        assert serializer.is_valid()
        product = serializer.save()
        
        assert product.tags.count() == 2
        # The signal creates a "Default" variant, and the serializer adds "Pro"
        assert product.variants.count() == 2
        assert product.variants.filter(name='Pro').exists()
        assert product.variants.filter(name='Default').exists()

    def test_product_detail_serializer_update_nested(self, product):
        data = {
            'tags': ['new-tag'],
            'variants': [
                {'name': 'Updated Variant', 'sku': 'UPD-V', 'price': 100, 'stock': 1}
            ]
        }
        serializer = ProductDetailSerializer(product, data=data, partial=True)
        assert serializer.is_valid()
        product = serializer.save()
        
        assert product.tags.count() == 1
        assert product.tags.first().name == 'new-tag'
        assert product.variants.count() == 1 # Replaces existing ones in this implementation
        assert product.variants.first().name == 'Updated Variant'

    def test_related_products_by_category(self, category, product):
        # Create another product in same category
        p2 = Product.objects.create(name='P2', slug='p2', category=category, base_sku='P2', default_price=10)
        
        serializer = ProductDetailSerializer(product)
        related = serializer.data['related_products']
        assert len(related) == 1
        assert related[0]['id'] == p2.id

    def test_related_products_by_tags(self, product):
        # Product without category
        product.category = None
        product.save()
        tag = Tag.objects.create(name='tag1')
        product.tags.add(tag)
        
        p2 = Product.objects.create(name='P2', slug='p2', base_sku='P2', default_price=10)
        p2.tags.add(tag)
        
        serializer = ProductDetailSerializer(product)
        related = serializer.data['related_products']
        assert len(related) == 1
        assert related[0]['name'] == 'P2'

    def test_related_products_none(self, product):
        product.category = None
        product.save()
        product.tags.clear()
        
        serializer = ProductDetailSerializer(product)
        assert serializer.data['related_products'] == []
