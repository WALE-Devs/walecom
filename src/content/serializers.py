from rest_framework import serializers
from django.conf import settings
from .models import Content, ContentBlock


class ContentBlockSerializer(serializers.ModelSerializer):
    """Serializer for content sections (blocks) within a Content entry."""

    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ContentBlock
        fields = [
            'id',
            'content',
            'identifier',
            'title',
            'subtitle',
            'content_text',
            'items',
            'image_path',   # editable (stored in DB)
            'image_url',    # computed (absolute URL)
            'order',
            'is_active',
            'type',
            'language',
        ]

    def get_image_url(self, obj):
        """
        Builds an absolute URL for the image using MEDIA_URL and request context.
        Returns None if no image_path is set.
        """
        if not obj.image_path:
            return None

        request = self.context.get('request')
        relative_url = f"{settings.MEDIA_URL}{obj.image_path}"
        return request.build_absolute_uri(relative_url) if request else relative_url


class ContentSerializer(serializers.ModelSerializer):
    """Serializer for main content entries (About, FAQ, Contact, etc.)"""

    blocks = ContentBlockSerializer(many=True, read_only=True)

    class Meta:
        model = Content
        fields = [
            'id',
            'identifier',
            'title',
            'description',
            'language',
            'is_active',
            'last_updated',
            'blocks',
        ]
