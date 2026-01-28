from rest_framework import serializers
from django.db.models import Prefetch
from django.conf import settings
from .models import Product, ProductImage, ProductVariant, Tag


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            'id',
            'product',
            'image',
            'position'
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
        """Returns the absolute URL of the main product image."""
        image = obj.images.order_by('position').first()
        if not image or not image.image:
            return None

        request = self.context.get('request')
        url = image.image.url
        return request.build_absolute_uri(url) if request else url

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]


class ProductDetailSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, required=False)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    related_products = serializers.SerializerMethodField()

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
            'main_image',
            'images',
            'variants',
            'related_products'
        ]
        read_only_fields = ['slug']

    def get_main_image(self, obj):
        """Returns the absolute URL of the main image."""
        image = obj.images.order_by('position').first()
        if not image or not image.image:
            return None

        request = self.context.get('request')
        url = image.image.url
        return request.build_absolute_uri(url) if request else url

    def get_related_products(self, obj):
        """
        Returns a list of products related by category or tags, optimized with Prefetch and only()
        """
        related_qs = Product.objects.exclude(id=obj.id)

        # Filter by category if exists else by tags
        if obj.category:
            related_qs = related_qs.filter(category=obj.category)
        elif obj.tags.exists():
            related_qs = related_qs.filter(tags__in=obj.tags.all()).distinct()
        else:
            return []

        # query w/only, prefetch, limit 4
        related_qs = related_qs.only(
            'id', 'name', 'slug', 'currency', 'default_price', 'base_sku'
        ).prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.only('image', 'position', 'product').order_by('position'),
            )
        )[:4]

        # Serialize manually
        request = self.context.get('request')
        result = []
        for p in related_qs:
            image = p.images.order_by('position').first()
            image_url = None
            if image and image.image:
                url = image.image.url
                image_url = request.build_absolute_uri(url) if request else url

            result.append({
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'price': str(p.default_price),
                'currency': p.currency,
                'image': image_url
            })

        return result


    def create(self, validated_data):
        variants_data = validated_data.pop('variants', None)
        tags_data = validated_data.pop('tags', None)

        product = Product.objects.create(**validated_data)

        # Handle tags
        if tags_data is not None:
            tag_objects = [
                Tag.objects.get_or_create(name=name.strip().lower())[0]
                for name in tags_data
            ]
            product.tags.set(tag_objects)

        # Handle variants
        if variants_data is not None:
            for variant_data in variants_data:
                ProductVariant.objects.create(product=product, **variant_data)

        return product

    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', None)
        tags_data = validated_data.pop('tags', None)

        # Update fields
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


