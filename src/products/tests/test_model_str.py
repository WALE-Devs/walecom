import pytest
from products.models import Category, Tag, Attribute, AttributeValue, Product, ProductVariant, ProductImage

# All common fixtures (product, category)
# are now available from utils.test_helpers via conftest.py

@pytest.mark.django_db
class TestProductModelStr:
    def test_tag_str(self):
        tag = Tag.objects.create(name='tag1')
        assert str(tag) == 'tag1'

    def test_category_str(self):
        cat = Category.objects.create(name='cat1')
        assert str(cat) == 'cat1'

    def test_attribute_str(self):
        attr = Attribute.objects.create(name='color')
        assert str(attr) == 'color'

    def test_attribute_value_str(self):
        attr = Attribute.objects.create(name='color')
        av = AttributeValue.objects.create(attribute=attr, value='red')
        assert str(av) == 'color: red'

    def test_product_str(self, product):
        assert str(product) == 'Test Product'

    def test_variant_str(self, product):
        variant = ProductVariant.objects.create(product=product, name='Silver', sku='TEST-SILV', price=500, stock=10)
        assert str(variant) == 'Test Product - Silver'

    def test_image_str(self, product):
        img = ProductImage.objects.create(product=product, position=1)
        assert str(img) == 'Test Product - Image 1'
