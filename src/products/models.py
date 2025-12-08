from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    parent = models.ForeignKey('Category', related_name='children', on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


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
    category = models.ForeignKey('Category', related_name='products', on_delete=models.PROTECT)
    default_currency = models.CharField(max_length=3, default="PEN")
    default_price = models.DecimalField(max_digits=10, decimal_places=2)
    default_stock = models.PositiveIntegerField(default=0, blank=True, null=True)

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
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    attributes = models.ManyToManyField(AttributeValue, related_name='variants')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="PEN")
    stock = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new and not self.sku:  # Only replace if no SKU is specified
            # Ver si existe una variante default (sin SKU)
            default_variant = self.product.variants.filter(Q(sku__isnull=True) | Q(sku='')).first()
            if default_variant:
                # Sobrescribir solo la variante default (sin SKU)
                default_variant.price = self.price
                default_variant.currency = self.currency
                default_variant.stock = self.stock
                # Remove force_insert and force_update from kwargs for default variant
                save_kwargs = {k: v for k, v in kwargs.items() if k not in ['force_insert', 'force_update']}
                default_variant.save(*args, **save_kwargs)

                # Copiar la pk al self para que el código del cliente siga funcionando
                self.pk = default_variant.pk

                # Generar SKU si hay atributos
                if not default_variant.sku and default_variant.attributes.exists():
                    default_variant.sku = default_variant.product.generate_variant_sku(default_variant.attributes.all())
                    default_variant.save(update_fields=['sku'])
                return  # Terminar aquí para no crear nueva fila

        # Si no hay default_variant o se especificó SKU, comportamiento normal
        super().save(*args, **kwargs)

        # Generar SKU si no existe y hay atributos
        if not self.sku and self.attributes.exists():
            self.sku = self.product.generate_variant_sku(self.attributes.all())
            super().save(update_fields=['sku'])


# Señal para crear variante por defecto automáticamente
@receiver(post_save, sender=Product)
def create_default_variant(sender, instance, created, **kwargs):
    if created and not instance.variants.exists():
        ProductVariant.objects.create(
            product=instance,
            price=instance.default_price,
            currency=instance.default_currency,
            stock=instance.default_stock or 0,
        )


@receiver(m2m_changed, sender=ProductVariant.attributes.through)
def handle_attributes_change(sender, instance, action, pk_set, **kwargs):
    """Handle attributes change: generate SKU and replace existing attributes for new variants"""
    if action == 'post_add':
        # If this is a replacement operation (no existing SKU), replace all attributes
        if not instance.sku:
            # Get all current attributes and the newly added ones
            current_attrs = set(instance.attributes.all())
            new_attrs = AttributeValue.objects.filter(pk__in=pk_set)

            # Replace all attributes with the new ones only (complete replacement)
            instance.attributes.set(new_attrs)

            # Generate SKU if there are attributes
            if instance.attributes.exists():
                instance.sku = instance.product.generate_variant_sku(instance.attributes.all())
                instance.save(update_fields=['sku'])
        else:
            # Normal variant with existing SKU: just generate SKU if missing
            if not instance.sku and instance.attributes.exists():
                instance.sku = instance.product.generate_variant_sku(instance.attributes.all())
                instance.save(update_fields=['sku'])


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