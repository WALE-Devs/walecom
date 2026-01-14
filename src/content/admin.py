from django.contrib import admin
from .models import Content, ContentBlock


class ContentBlockInline(admin.TabularInline):
    model = ContentBlock
    extra = 1
    fields = (
        'identifier',
        'title',
        'subtitle',
        'order',
        'is_active',
        'language',
    )


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'title', 'language', 'is_active', 'last_updated')
    list_filter = ('language', 'is_active')
    search_fields = ('title', 'identifier')
    inlines = [ContentBlockInline]


@admin.register(ContentBlock)
class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'title', 'content', 'order', 'language', 'is_active')
    list_filter = ('language', 'is_active')
    search_fields = ('title', 'identifier')
