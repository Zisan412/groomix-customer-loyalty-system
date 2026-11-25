from rest_framework import serializers

from accounts.models import User
from .models import LoyaltySettings, LoyaltyTransaction


class LoyaltySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltySettings
        fields = [
            "reward_budget_percent",
            "points_per_rupee",
            "minimum_redemption_points",
            "maximum_checkout_discount_percent",
            "points_expiry_months",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]

    def validate(self, attrs):
        budget = attrs.get("reward_budget_percent", getattr(self.instance, "reward_budget_percent", 0))
        discount = attrs.get(
            "maximum_checkout_discount_percent",
            getattr(self.instance, "maximum_checkout_discount_percent", 0),
        )
        if budget > 100:
            raise serializers.ValidationError({"reward_budget_percent": "Must not exceed 100%."})
        if discount > 100:
            raise serializers.ValidationError({"maximum_checkout_discount_percent": "Must not exceed 100%."})
        if attrs.get("points_per_rupee", getattr(self.instance, "points_per_rupee", 0)) < 1:
            raise serializers.ValidationError({"points_per_rupee": "Must be at least one."})
        if attrs.get("points_expiry_months", getattr(self.instance, "points_expiry_months", 0)) < 1:
            raise serializers.ValidationError({"points_expiry_months": "Must be at least one month."})
        return attrs


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyTransaction
        fields = ["id", "order", "redemption", "kind", "points", "description", "created_at", "expires_at", "reference"]


class LoyaltyAdjustmentSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role=User.Role.WHOLESALER))
    points = serializers.IntegerField(min_value=-100000000, max_value=100000000)
    description = serializers.CharField()

    def validate_points(self, value):
        if value == 0:
            raise serializers.ValidationError("Adjustment must change the points balance.")
        return value
