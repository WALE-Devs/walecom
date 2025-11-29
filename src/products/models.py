from django.db import models


class Attribute(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=50)
    sku_code = models.CharField(max_length=10)

    class Meta:
        unique_together = ['attribute', 'value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    base_sku = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="PEN")
    category = models.ForeignKey('Category', related_name='products', on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def generate_variant_sku(self, attributes):
        """Genera SKU para variante combinando base_sku con códigos de atributos"""
        sku_parts = [self.base_sku]
        for attr_value in attributes.order_by('attribute__name'):
            sku_parts.append(attr_value.sku_code)
        return "-".join(sku_parts)


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    sku = models.CharField(max_length=50, unique=True, blank=True)
    attributes = models.ManyToManyField(AttributeValue, related_name='variants')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="PEN")
    stock = models.PositiveIntegerField()

    # def __str__(self):
    #     attrs = ", ".join([str(av) for av in self.attributes.all()])
    #     return f"{self.product.name} - {attrs}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Guarda primero para obtener un ID

        if is_new and not self.sku and self.attributes.exists():
            self.sku = self.product.generate_variant_sku(self.attributes.all())
            super().save(update_fields=['sku'])



class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    parent = models.ForeignKey('Category', related_name='children', on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
