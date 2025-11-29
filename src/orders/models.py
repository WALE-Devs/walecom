from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):
    user = models.ForeignKey(User, related_name='orders', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name='products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name= 'orders', on_delete=models.PROTECT)
    quantity = models.IntegerField()