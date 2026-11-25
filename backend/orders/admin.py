from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "selling_price", "manufacturing_cost", "units_per_box")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "wholesaler", "status", "payment_mode", "total", "paid_amount", "created_at")
    list_filter = ("status", "payment_mode", "created_at")
    search_fields = ("wholesaler__business_name", "wholesaler__email")
    inlines = [OrderItemInline]
