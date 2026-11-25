from rest_framework import serializers

from catalog.models import Product
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id", "product", "product_name", "selling_price", "manufacturing_cost",
            "units_per_box", "quantity_boxes", "line_total",
        ]
        read_only_fields = fields


class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment_status = serializers.CharField(read_only=True)
    wholesaler_name = serializers.CharField(source="wholesaler.business_name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "wholesaler", "wholesaler_name", "status", "payment_mode",
            "subtotal", "points_discount", "total", "paid_amount", "payment_status",
            "notes", "created_at", "approved_at", "dispatched_at", "delivered_at",
            "credit_due_date", "items",
        ]
        read_only_fields = fields


class RequestedOrderItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True))
    quantity_boxes = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    items = RequestedOrderItemSerializer(many=True, allow_empty=False)
    payment_mode = serializers.ChoiceField(choices=Order.PaymentMode.choices, default=Order.PaymentMode.ADVANCE)
    redeem_points = serializers.IntegerField(min_value=0, required=False, default=0)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_items(self, items):
        ids = [item["product"].pk for item in items]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Each product can appear only once; combine its box quantity.")
        return items
