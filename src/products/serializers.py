from rest_framework import serializers
from .models import Product, ProductImage, ProductVariant, Tag


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            'id',
            'product',
            'image',
            'is_main'
        ]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'name',
            'sku',
            'price',
            'stock'
        ]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True, required=False)
    variants = ProductVariantSerializer(many=True, required=False)
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        required=False,
        allow_empty=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'base_sku',
            'category',
            'currency',
            'default_price',
            'default_stock',
            'tags',
            'images',
            'variants'
        ]
        read_only_fields = ['slug']

    def create(self, validated_data):
        # Get variants if exist
        variants_data = validated_data.pop('variants', [])
        tags_data = validated_data.pop('tags', [])

        # Create product
        product = Product.objects.create(**validated_data)

        # Tags set
        if tags_data:
            # Tags creation
            tag_objects = [Tag.objects.get_or_create(name=name)[0] for name in tags_data]
            product.tags.set(tag_objects)


        # Create variants
        for variant_data in variants_data:
            ProductVariant.objects.create(product=product, **variant_data)

        return product

    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', None)
        tags_data = validated_data.pop('tags', None)

        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update tags
        if tags_data is not None:
            # Tags creation
            tag_objects = [Tag.objects.get_or_create(name=name)[0] for name in tags_data]
            instance.tags.set(tag_objects)

        # Update variants
        if variants_data is not None:
            instance.variants.all().delete()
            for variant_data in variants_data:
                ProductVariant.objects.create(product=instance, **variant_data)

        return instance

