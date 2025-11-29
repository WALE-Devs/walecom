from django.contrib import admin
from .models import Product, Category, Attribute, AttributeValue, ProductVariant


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 3


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ['sku', 'attributes', 'price', 'stock']


class AttributeAdmin(admin.ModelAdmin):
    model = Attribute
    search_fields = ['name']
    inlines = [AttributeValueInline]

    def get_list_display(self, request):
        return ['name']


class AttributeValueAdmin(admin.ModelAdmin):
    model = AttributeValue
    search_fields = ['value', 'attribute__name']
    list_filter = ['attribute']

    def get_list_display(self, request):
        return ['attribute', 'value', 'sku_code']


class ProductAdmin(admin.ModelAdmin):
    model = Product
    search_fields = ['name']
    inlines = [ProductVariantInline]

    def get_list_display(self, request):
        fields = [field.name for field in self.model._meta.fields if field.name != 'id']
        return fields + ['get_variants_count']

    def get_variants_count(self, obj):
        return obj.variants.count()
    get_variants_count.short_description = 'Variants'


class CategoryAdmin(admin.ModelAdmin):
    model = Category

    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields if field.name != 'id']


class ProductVariantAdmin(admin.ModelAdmin):
    model = ProductVariant
    search_fields = ['sku', 'product__name']
    list_filter = ['product']
    filter_horizontal = ['attributes']

    def get_list_display(self, request):
        return ['product', 'sku', 'get_attributes', 'price', 'stock']

    def get_attributes(self, obj):
        return " / ".join([f"{av.attribute.name}:{av.value}" for av in obj.attributes.all()])
    get_attributes.short_description = 'Attributes'


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeValue, AttributeValueAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)