from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug')
    tags = filters.CharFilter(method='filter_by_tags')

    class Meta:
        model = Product
        fields = ['category', 'tags']

    def filter_by_tags(self, queryset, name, value):
        if not value:
            return queryset
        
        # Split by comma to support filtering by multiple tags in a single query parameter.
        # Strip whitespace to handle cases like "tag1, tag2" gracefully.
        tags = [tag.strip() for tag in value.split(',') if tag.strip()]
        
        # We apply filters sequentially to implement an AND logic:
        # the product must have ALL specified tags.
        for tag in tags:
            queryset = queryset.filter(tags__name=tag)
            
        # Due to the Many-to-Many relationship with tags, a product might appear multiple times 
        # in the result set after JOINing. distinct() ensures each product is returned only once.
        return queryset.distinct()
