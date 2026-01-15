from django.db import models


class Content(models.Model):
    """Represents a top-level content entry (e.g., About, FAQ, Contact, etc.)"""
    identifier = models.SlugField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=5, default='es')
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('identifier', 'language')
        ordering = ['identifier', 'language']

    def __str__(self):
        return f"{self.title} ({self.language})"


class ContentBlock(models.Model):
    """Represents a content block or section within a Content entry"""
    content = models.ForeignKey(Content, related_name='blocks', on_delete=models.CASCADE)
    identifier = models.SlugField(max_length=50)
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=200, blank=True)
    content_text = models.TextField(blank=True)
    items = models.JSONField(default=list, blank=True)
    image_path = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=5, default='es')

    class Meta:
        unique_together = ('content', 'identifier', 'language')
        ordering = ['order']

    def __str__(self):
        return f"{self.identifier or self.title or 'Block'} ({self.language})"
