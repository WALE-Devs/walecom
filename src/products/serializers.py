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


class ProductListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

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
            'image',
            'tags',
        ]

    def get_image(self, obj):
        request = self.context.get('request')
        image = obj.images.filter(is_main=True).first() or obj.images.filter(is_main=False).first()
        if not image:
            return None
        url = image.image.url
        return request.build_absolute_uri(url) if request else url


    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, required=False)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        write_only=True
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
        variants_data = validated_data.pop('variants', None)
        tags_data = validated_data.pop('tags', None)

        product = Product.objects.create(**validated_data)

        if tags_data is not None:
            tag_objects = [
                Tag.objects.get_or_create(name=name.strip().lower())[0]
                for name in tags_data
            ]
            product.tags.set(tag_objects)

        if variants_data is not None:
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
            tag_objects = [
                Tag.objects.get_or_create(name=name.strip().lower())[0]
                for name in tags_data
            ]
            instance.tags.set(tag_objects)

        # Update variants
        if variants_data is not None:
            instance.variants.all().delete()
            for variant_data in variants_data:
                ProductVariant.objects.create(product=instance, **variant_data)

        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tags'] = [tag.name for tag in instance.tags.all()]
        return data


