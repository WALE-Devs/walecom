from django.db import models
from django.contrib.auth.models import User
from utils.slug_utils import unique_slugify


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    parent = models.ForeignKey('self', related_name='children', on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    base_sku = models.CharField(max_length=50)
    category = models.ForeignKey('Category', related_name='products', on_delete=models.PROTECT, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name='products', blank=True)
    currency = models.CharField(max_length=3, default="PEN")
    default_price = models.DecimalField(max_digits=10, decimal_places=2)
    default_stock = models.PositiveIntegerField(default=0, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self.name)
        super().save(*args, **kwargs)

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
    image = models.ImageField(upload_to='products/images/', blank=True, null=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']
        #unique_together = ('product', 'position')

    def __str__(self):
        return f"{self.product.name} - Image {self.position}"