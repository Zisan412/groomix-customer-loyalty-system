from django.contrib import admin

from .models import CreditEntry, CreditFacility, CreditRequest


@admin.register(CreditRequest)
class CreditRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "wholesaler", "requested_limit", "status", "created_at")
    list_filter = ("status", "created_at")


@admin.register(CreditFacility)
class CreditFacilityAdmin(admin.ModelAdmin):
    list_display = ("wholesaler", "credit_limit", "outstanding_balance", "valid_until", "is_active")


@admin.register(CreditEntry)
class CreditEntryAdmin(admin.ModelAdmin):
    list_display = ("facility", "order", "kind", "amount", "created_at")
    list_filter = ("kind",)
