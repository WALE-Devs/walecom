import pytest
from django.db import IntegrityError
from content.models import Content, ContentBlock


@pytest.mark.django_db
class TestContentModels:
    def test_content_creation(self):
        content = Content.objects.create(
            identifier="about-us",
            title="Sobre Nosotros",
            description="Información corporativa",
            language="es",
        )
        assert str(content) == "Sobre Nosotros (es)"
        assert content.identifier == "about-us"
        assert content.is_active is True

    def test_content_unique_together(self):
        Content.objects.create(identifier="test", title="Test ES", language="es")
        # Same identifier, different language - OK
        Content.objects.create(identifier="test", title="Test EN", language="en")

        # Same identifier, same language - Fail
        with pytest.raises(IntegrityError):
            Content.objects.create(identifier="test", title="Duplicate", language="es")

    def test_content_block_creation(self):
        content = Content.objects.create(
            identifier="home", title="Inicio", language="es"
        )
        block = ContentBlock.objects.create(
            content=content,
            identifier="hero-section",
            title="Bienvenidos",
            order=1,
            language="es",
        )
        assert str(block) == "hero-section (es)"
        assert block.content == content
        assert block.order == 1

    def test_content_block_unique_together(self):
        content = Content.objects.create(identifier="faq", title="FAQ", language="es")
        ContentBlock.objects.create(
            content=content, identifier="q1", title="Q1", language="es"
        )

        # Same content, same identifier, same language - Fail
        with pytest.raises(IntegrityError):
            ContentBlock.objects.create(
                content=content, identifier="q1", title="Q1 Duplicate", language="es"
            )

    def test_content_cascade_deletion(self):
        content = Content.objects.create(
            identifier="delete-me", title="Delete", language="es"
        )
        ContentBlock.objects.create(content=content, identifier="b1", language="es")

        assert ContentBlock.objects.filter(content=content).count() == 1
        content.delete()
        assert ContentBlock.objects.filter(identifier="b1").count() == 0
