from decimal import Decimal

from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    wholesaler = serializers.IntegerField(source="order.wholesaler_id", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "order", "wholesaler", "kind", "amount", "verified_amount",
            "status", "method", "reference", "note", "created_at", "verified_at",
        ]
        read_only_fields = ["id", "wholesaler", "kind", "verified_amount", "status", "created_at", "verified_at"]


class PaymentVerificationSerializer(serializers.Serializer):
    verified_amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal("0.00"), required=False)
    verified = serializers.BooleanField()
    note = serializers.CharField(required=False, allow_blank=True)
