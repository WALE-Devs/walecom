# import pytest
from products.models import Cart, ProductVariant
from django.test import TestCase
from django.contrib.auth.models import User


class CartTest(TestCase):

    fixtures = ["products/fixtures/products_init.json"]

    def test_cart(db):
        user = User.objects.create(username="probua")
        cart = Cart.objects.create_from_products(
            user=user,
            products=[
                {
                    "product_variant_id": ProductVariant.objects.get(id=1),
                    "quantity": 1
                },
                {
                    "product_variant_id": ProductVariant.objects.get(id=2),
                    "quantity": 2
                }
            ]
        )
        assert cart.user == user