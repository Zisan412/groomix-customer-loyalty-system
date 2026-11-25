from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "kind", "amount", "verified_amount", "status", "created_at")
    list_filter = ("kind", "status", "method")
    search_fields = ("reference", "order__id", "order__wholesaler__business_name")
