from rest_framework import serializers

from .models import Redemption, RewardItem


class RewardItemSerializer(serializers.ModelSerializer):
    available_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = RewardItem
        fields = [
            "id", "name", "description", "points_cost", "stock_quantity",
            "reserved_quantity", "available_quantity", "is_active", "created_at",
        ]
        read_only_fields = ["id", "reserved_quantity", "available_quantity", "created_at"]


class RedemptionSerializer(serializers.ModelSerializer):
    reward_name = serializers.CharField(source="reward_item.name", read_only=True)
    wholesaler_name = serializers.CharField(source="wholesaler.business_name", read_only=True)

    class Meta:
        model = Redemption
        fields = [
            "id", "wholesaler", "wholesaler_name", "reward_item", "reward_name",
            "points_cost_snapshot", "status", "shipping_address", "admin_note",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "wholesaler", "wholesaler_name", "points_cost_snapshot",
            "status", "admin_note", "created_at", "updated_at",
        ]
