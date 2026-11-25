from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts.permissions import IsFactoryAdmin, IsWholesaler, IsWholesalerOrAdmin
from catalog.models import Product
from loyalty.services import award_order_points

from .models import Order
from .serializers import OrderCreateSerializer, OrderReadSerializer
from .services import approve_order, cancel_order, create_order


class OrderViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["id", "wholesaler__business_name"]
    ordering_fields = ["created_at", "total", "status"]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related("items__product").select_related("wholesaler")
        if not self.request.user.is_factory_admin:
            queryset = queryset.filter(wholesaler=self.request.user)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter.upper())
        return queryset

    def get_permissions(self):
        if self.action in {"approve", "reject", "set_status"}:
            return [IsFactoryAdmin()]
        if self.action == "create":
            return [IsWholesaler()]
        return [IsWholesalerOrAdmin()]

    def get_serializer_class(self):
        return OrderCreateSerializer if self.action == "create" else OrderReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order(user=request.user, **serializer.validated_data)
        return Response(OrderReadSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[IsFactoryAdmin])
    def approve(self, request, pk=None):
        order = approve_order(self.get_object())
        return Response(OrderReadSerializer(order).data)

    @action(detail=True, methods=["post"], permission_classes=[IsFactoryAdmin])
    def reject(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.Status.PENDING:
            raise ValidationError({"detail": "Only pending orders can be rejected."})
        order = cancel_order(order, actor=request.user)
        return Response(OrderReadSerializer(order).data)

    @action(detail=True, methods=["post"], permission_classes=[IsFactoryAdmin])
    def set_status(self, request, pk=None):
        requested = request.data.get("status", "").upper()
        transitions = {
            Order.Status.APPROVED: {Order.Status.PAID, Order.Status.PROCESSING},
            Order.Status.PAID: {Order.Status.PROCESSING},
            Order.Status.PROCESSING: {Order.Status.DISPATCHED},
            Order.Status.DISPATCHED: {Order.Status.DELIVERED},
        }
        order = self.get_object()
        if requested not in Order.Status.values:
            raise ValidationError({"status": "Choose a valid order status."})
        if requested not in transitions.get(order.status, set()):
            raise ValidationError({"status": f"Cannot move an order from {order.get_status_display()} to {requested}."})
        if requested == Order.Status.PAID and order.paid_amount < order.total:
            raise ValidationError({"status": "An order can only be marked paid after full payment verification."})
        if requested == Order.Status.PROCESSING and order.payment_mode == Order.PaymentMode.ADVANCE and order.paid_amount < order.total:
            raise ValidationError({"status": "Advance-payment orders must be fully paid before processing."})
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order.pk)
            if requested == Order.Status.DISPATCHED:
                for item in order.items.all():
                    product = Product.objects.select_for_update().get(pk=item.product_id)
                    product.stock_boxes -= item.quantity_boxes
                    product.reserved_boxes -= item.quantity_boxes
                    product.save(update_fields=["stock_boxes", "reserved_boxes"])
                order.dispatched_at = timezone.now()
            if requested == Order.Status.DELIVERED:
                order.delivered_at = timezone.now()
            order.status = requested
            update_fields = ["status"]
            if requested == Order.Status.DISPATCHED:
                update_fields.append("dispatched_at")
            if requested == Order.Status.DELIVERED:
                update_fields.append("delivered_at")
            order.save(update_fields=update_fields)
            if requested == Order.Status.DELIVERED:
                award_order_points(order)
        return Response(OrderReadSerializer(order).data)

    @action(detail=True, methods=["post"], permission_classes=[IsWholesaler])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.wholesaler_id != request.user.id:
            raise ValidationError({"detail": "You can only cancel your own orders."})
        order = cancel_order(order, actor=request.user)
        return Response(OrderReadSerializer(order).data)
