from django.contrib import admin

from .models import Redemption, RewardItem


@admin.register(RewardItem)
class RewardItemAdmin(admin.ModelAdmin):
    list_display = ("name", "points_cost", "stock_quantity", "reserved_quantity", "is_active")
    list_filter = ("is_active",)


@admin.register(Redemption)
class RedemptionAdmin(admin.ModelAdmin):
    list_display = ("id", "wholesaler", "reward_item", "points_cost_snapshot", "status", "created_at")
    list_filter = ("status", "created_at")
