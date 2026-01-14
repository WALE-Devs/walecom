from rest_framework import serializers
from .models import Content, ContentBlock


class ContentBlockSerializer(serializers.ModelSerializer):
    """Serializer for sections (blocks) inside a Content entry"""

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
            'type',
            'language',
            'is_active',
        ]


class ContentSerializer(serializers.ModelSerializer):
    """Serializer for top-level content entries (About, FAQ, etc.)"""
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
