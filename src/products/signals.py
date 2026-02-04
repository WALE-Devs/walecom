from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product, ProductVariant


@receiver(post_save, sender=Product)
def create_default_variant(sender, instance, created, **kwargs):
    if created and not instance.variants.exists():
        ProductVariant.objects.get_or_create(
            product=instance,
            name="Default",
            defaults={
                "sku": f"{instance.base_sku}-DEF",
                "price": instance.default_price,
                "stock": instance.default_stock or 0,
            },
        )
