from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts.permissions import IsFactoryAdmin, IsWholesaler, IsWholesalerOrAdmin
from orders.models import Order

from .models import ReturnRequest
from .serializers import ReturnDecisionSerializer, ReturnInspectionSerializer, ReturnRequestSerializer
from .services import create_return_request, decide_return, inspect_return


class ReturnViewSet(viewsets.ModelViewSet):
    serializer_class = ReturnRequestSerializer
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["order__id", "wholesaler__business_name", "reason"]
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        queryset = ReturnRequest.objects.select_related("order", "wholesaler").prefetch_related("items__order_item")
        if not self.request.user.is_factory_admin:
            queryset = queryset.filter(wholesaler=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action in {"review", "inspect"}:
            return [IsFactoryAdmin()]
        if self.action == "create":
            return [IsWholesaler()]
        return [IsWholesalerOrAdmin()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.validated_data["order"]
        if order.wholesaler_id != request.user.id:
            raise ValidationError({"order": "You can only return items from your own orders."})
        return_request = create_return_request(
            user=request.user,
            order=order,
            reason=serializer.validated_data["reason"],
            items=serializer.validated_data["items"],
        )
        return Response(self.get_serializer(return_request).data, status=201)

    @action(detail=True, methods=["post"], permission_classes=[IsFactoryAdmin])
    def review(self, request, pk=None):
        data = ReturnDecisionSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        return_request = decide_return(
            self.get_object(),
            decision=data.validated_data["decision"],
            note=data.validated_data.get("note", ""),
        )
        return Response(self.get_serializer(return_request).data)

    @action(detail=True, methods=["post"], permission_classes=[IsFactoryAdmin])
    def inspect(self, request, pk=None):
        data = ReturnInspectionSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        return_request = inspect_return(
            self.get_object(),
            result=data.validated_data["result"],
            restock=data.validated_data["restock"],
        )
        return Response(self.get_serializer(return_request).data)
