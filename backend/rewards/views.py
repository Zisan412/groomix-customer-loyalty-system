from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsFactoryAdmin, IsWholesaler, IsWholesalerOrAdmin

from .models import Redemption, RewardItem
from .serializers import RedemptionSerializer, RewardItemSerializer
from .services import request_redemption, update_redemption


class RewardItemViewSet(viewsets.ModelViewSet):
    serializer_class = RewardItemSerializer
    search_fields = ["name", "description"]
    ordering_fields = ["name", "points_cost", "created_at"]

    def get_queryset(self):
        queryset = RewardItem.objects.all()
        if not self.request.user.is_factory_admin:
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_permissions(self):
        return [IsFactoryAdmin() if self.action in {"create", "update", "partial_update", "destroy"} else permissions.IsAuthenticated()]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class RedemptionViewSet(viewsets.ModelViewSet):
    serializer_class = RedemptionSerializer
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["wholesaler__business_name", "reward_item__name"]
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        queryset = Redemption.objects.select_related("wholesaler", "reward_item")
        if not self.request.user.is_factory_admin:
            queryset = queryset.filter(wholesaler=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action in {"approve", "reject", "dispatch", "deliver"}:
            return [IsFactoryAdmin()]
        if self.action == "create":
            return [IsWholesaler()]
        return [IsWholesalerOrAdmin()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        redemption = request_redemption(
            user=request.user,
            reward_item=serializer.validated_data["reward_item"],
            shipping_address=serializer.validated_data.get("shipping_address", ""),
        )
        return Response(self.get_serializer(redemption).data, status=201)

    def _transition(self, request, status_value):
        redemption = update_redemption(
            self.get_object(),
            status_value=status_value,
            admin_note=request.data.get("admin_note", ""),
        )
        return Response(self.get_serializer(redemption).data)

    @action(detail=True, methods=["post"], permission_classes=[IsFactoryAdmin])
    def approve(self, request, pk=None):
        return self._transition(request, Redemption.Status.APPROVED)

    @action(detail=True, methods=["post"], permission_classes=[IsFactoryAdmin])
    def reject(self, request, pk=None):
        return self._transition(request, Redemption.Status.REJECTED)

    @action(detail=True, methods=["post"], permission_classes=[IsFactoryAdmin], url_path="dispatch")
    def mark_dispatched(self, request, pk=None):
        return self._transition(request, Redemption.Status.DISPATCHED)

    @action(detail=True, methods=["post"], permission_classes=[IsFactoryAdmin])
    def deliver(self, request, pk=None):
        return self._transition(request, Redemption.Status.DELIVERED)
