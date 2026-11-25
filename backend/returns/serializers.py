from rest_framework import serializers

from .models import ReturnItem, ReturnRequest


class ReturnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnItem
        fields = ["id", "order_item", "quantity_boxes"]
        read_only_fields = ["id"]


class ReturnRequestSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, allow_empty=False)
    wholesaler_name = serializers.CharField(source="wholesaler.business_name", read_only=True)

    class Meta:
        model = ReturnRequest
        fields = [
            "id", "order", "wholesaler", "wholesaler_name", "reason",
            "status", "inspection_result", "refund_amount", "created_at",
            "reviewed_at", "items",
        ]
        read_only_fields = [
            "id", "wholesaler", "wholesaler_name", "status", "inspection_result",
            "refund_amount", "created_at", "reviewed_at",
        ]

    def create(self, validated_data):
        items = validated_data.pop("items")
        instance = ReturnRequest.objects.create(**validated_data)
        ReturnItem.objects.bulk_create([
            ReturnItem(return_request=instance, **item) for item in items
        ])
        return instance


class ReturnDecisionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=["approve", "reject"])
    note = serializers.CharField(required=False, allow_blank=True)


class ReturnInspectionSerializer(serializers.Serializer):
    result = serializers.CharField()
    restock = serializers.BooleanField(default=False)
