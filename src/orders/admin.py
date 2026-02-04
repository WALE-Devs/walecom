from django.contrib import admin
from .models import Order, OrderProduct, Cart, CartProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ["price_at_purchase"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "total_price", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__username", "id"]
    inlines = [OrderProductInline]


admin.site.register(Cart)
admin.site.register(CartProduct)
