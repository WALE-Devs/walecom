from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('PAID', 'Pagado'),
        ('SHIPPED', 'Enviado'),
        ('DELIVERED', 'Entregado'),
        ('CANCELLED', 'Cancelado'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    billing_address = models.TextField()
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.user.username}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name='products', on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, related_name='order_items', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product_variant.product.name} ({self.product_variant.name})"


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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    objects = CartManager()

    def __str__(self):
        return f"{self.user.username}'s cart "


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()