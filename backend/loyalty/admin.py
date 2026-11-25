from django.contrib import admin

from .models import LoyaltySettings, LoyaltyTransaction


@admin.register(LoyaltySettings)
class LoyaltySettingsAdmin(admin.ModelAdmin):
    list_display = ("reward_budget_percent", "points_per_rupee", "minimum_redemption_points", "maximum_checkout_discount_percent", "points_expiry_months")


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "kind", "points", "order", "created_at", "expires_at")
    list_filter = ("kind", "created_at")
    search_fields = ("user__business_name", "reference")
