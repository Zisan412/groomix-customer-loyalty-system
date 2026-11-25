from rest_framework import permissions, viewsets

from accounts.permissions import IsAdminOrReadOnly, IsFactoryAdmin
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        queryset = Category.objects.all()
        if not self.request.user.is_factory_admin:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsFactoryAdmin()]
        return [IsAdminOrReadOnly()]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    search_fields = ["name", "sku", "description", "category__name"]
    ordering_fields = ["name", "selling_price", "created_at"]

    def get_queryset(self):
        queryset = Product.objects.select_related("category").all()
        if not self.request.user.is_factory_admin:
            queryset = queryset.filter(is_active=True, category__is_active=True)
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsFactoryAdmin()]
        return [IsAdminOrReadOnly()]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])
