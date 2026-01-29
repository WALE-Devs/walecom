from rest_framework import serializers
from django.db.models import Prefetch
from django.conf import settings
from .models import Product, ProductImage, ProductVariant, Tag, Attribute, AttributeValue


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
    attributes = serializers.DictField(child=serializers.CharField(), write_only=True, required=False)
    attribute_values_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'name',
            'sku',
            'price',
            'stock',
            'attributes',
            'attribute_values_display'
        ]

    def get_attribute_values_display(self, obj):
        return {av.attribute.name: av.value for av in obj.attribute_values.all()}

    def create(self, validated_data):
        attributes_data = validated_data.pop('attributes', {})
        variant = super().create(validated_data)
        self._handle_attributes(variant, attributes_data)
        return variant

    def update(self, instance, validated_data):
        attributes_data = validated_data.pop('attributes', None)
        variant = super().update(instance, validated_data)
        if attributes_data is not None:
            variant.attribute_values.clear()
            self._handle_attributes(variant, attributes_data)
        return variant

    def _handle_attributes(self, variant, attributes_data):
        for attr_name, attr_value in attributes_data.items():
            attribute, _ = Attribute.objects.get_or_create(name=attr_name)
            value_obj, _ = AttributeValue.objects.get_or_create(attribute=attribute, value=attr_value)
            variant.attribute_values.add(value_obj)


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
            for v_data in variants_data:
                v_serializer = ProductVariantSerializer(data=v_data)
                v_serializer.is_valid(raise_exception=True)
                v_serializer.save(product=product)

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
            for v_data in variants_data:
                v_serializer = ProductVariantSerializer(data=v_data)
                v_serializer.is_valid(raise_exception=True)
                v_serializer.save(product=instance)

        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tags'] = [tag.name for tag in instance.tags.all()]
        return data


