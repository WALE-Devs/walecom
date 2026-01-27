from django.db import models
from django.contrib.auth.models import User
from products.models import Product, ProductVariant


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name='products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name= 'orders', on_delete=models.PROTECT)
    quantity = models.IntegerField()


class CartManager(models.Manager):
    def create_from_products(self, user, products):
        cart = Cart.objects.create(user=user)
        for product_data in products:
            CartProduct.objects.create(
                cart=cart,
                product_variant=product_data.get('product_variant_id'),
                quantity=product_data.get('quantity')
            )
        return cart


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)

    objects = CartManager()

    def __str__(self):
        return f"{self.user.username}'s cart "


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()