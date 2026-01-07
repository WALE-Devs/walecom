from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    parent = models.ForeignKey('self', related_name='children', on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    base_sku = models.CharField(max_length=50)
    category = models.ForeignKey('Category', related_name='products', on_delete=models.PROTECT, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='products', blank=True)
    currency = models.CharField(max_length=3, default="PEN")
    default_price = models.DecimalField(max_digits=10, decimal_places=2)
    default_stock = models.PositiveIntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey('Product', related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    is_main = models.BooleanField(null = False, default=False)
    image = models.ImageField()


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
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()