from rest_framework import serializers
from django.conf import settings
from .models import Content, ContentBlock


class ContentBlockSerializer(serializers.ModelSerializer):
    """Serializer for content sections (blocks) within a Content entry."""

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
            'image',
            'order',
            'is_active',
            'type',
            'language',
        ]


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
