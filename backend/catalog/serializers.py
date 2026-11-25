from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    available_boxes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "sku", "name", "description", "category", "category_name",
            "selling_price", "manufacturing_cost", "units_per_box", "stock_boxes",
            "reserved_boxes", "available_boxes", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "reserved_boxes", "available_boxes", "created_at", "updated_at"]

    def validate(self, attrs):
        stock = attrs.get("stock_boxes", getattr(self.instance, "stock_boxes", 0))
        reserved = getattr(self.instance, "reserved_boxes", 0)
        if stock < reserved:
            raise serializers.ValidationError({"stock_boxes": "Stock cannot be lower than boxes already reserved."})
        return attrs
