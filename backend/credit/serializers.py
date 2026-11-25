from decimal import Decimal

from rest_framework import serializers

from .models import CreditEntry, CreditFacility, CreditRequest


class CreditRequestSerializer(serializers.ModelSerializer):
    wholesaler_name = serializers.CharField(source="wholesaler.business_name", read_only=True)

    class Meta:
        model = CreditRequest
        fields = ["id", "wholesaler", "wholesaler_name", "requested_limit", "reason", "status", "admin_note", "created_at", "decided_at"]
        read_only_fields = ["id", "wholesaler", "wholesaler_name", "status", "admin_note", "created_at", "decided_at"]


class CreditDecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=["approve", "reject"])
    credit_limit = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0.00"), required=False)
    payment_period_days = serializers.IntegerField(min_value=1, required=False)
    valid_from = serializers.DateField(required=False)
    valid_until = serializers.DateField(required=False)
    admin_note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["decision"] == "approve":
            required = ["credit_limit", "payment_period_days", "valid_from", "valid_until"]
            missing = [field for field in required if field not in attrs]
            if missing:
                raise serializers.ValidationError({field: "This field is required for approval." for field in missing})
            if attrs["valid_until"] < attrs["valid_from"]:
                raise serializers.ValidationError({"valid_until": "Validity must end on or after the start date."})
        return attrs


class CreditFacilitySerializer(serializers.ModelSerializer):
    available_credit = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = CreditFacility
        fields = ["id", "credit_limit", "outstanding_balance", "available_credit", "payment_period_days", "valid_from", "valid_until", "is_active", "updated_at"]


class CreditEntrySerializer(serializers.ModelSerializer):
    wholesaler = serializers.CharField(source="facility.wholesaler.business_name", read_only=True)

    class Meta:
        model = CreditEntry
        fields = ["id", "wholesaler", "order", "kind", "amount", "note", "created_at"]
