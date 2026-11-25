from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from accounts.permissions import IsFactoryAdmin, IsWholesaler, IsWholesalerOrAdmin
from credit.models import CreditEntry, CreditFacility
from loyalty.services import award_order_points
from orders.models import Order

from .models import Payment
from .serializers import PaymentSerializer, PaymentVerificationSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["reference", "order__id", "order__wholesaler__business_name"]
    ordering_fields = ["created_at", "amount", "status"]

    def get_queryset(self):
        queryset = Payment.objects.select_related("order", "order__wholesaler", "submitted_by")
        if not self.request.user.is_factory_admin:
            queryset = queryset.filter(order__wholesaler=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action == "verify":
            return [IsFactoryAdmin()]
        if self.action == "create":
            return [IsWholesaler()]
        return [IsWholesalerOrAdmin()]

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        if order.wholesaler_id != self.request.user.id:
            raise ValidationError({"order": "You can only submit payment for your own orders."})
        if order.status in {Order.Status.PENDING, Order.Status.CANCELLED}:
            raise ValidationError({"order": "Payment can only be recorded for an approved order."})
        amount = serializer.validated_data["amount"]
        remaining = max(order.total - order.paid_amount, Decimal("0.00"))
        pending = sum(
            Payment.objects.filter(order=order, kind=Payment.Kind.PAYMENT, status=Payment.Status.PENDING)
            .values_list("amount", flat=True),
            Decimal("0.00"),
        )
        if amount + pending > remaining:
            raise ValidationError({"amount": "Submitted payments cannot exceed the remaining order balance."})
        serializer.save(submitted_by=self.request.user, kind=Payment.Kind.PAYMENT)

    @action(detail=True, methods=["post"], permission_classes=[IsFactoryAdmin])
    def verify(self, request, pk=None):
        data = PaymentVerificationSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        values = data.validated_data
        with transaction.atomic():
            payment = Payment.objects.select_for_update().select_related("order").get(pk=pk)
            if payment.status != Payment.Status.PENDING:
                raise ValidationError({"detail": "This payment has already been reviewed."})
            if not values["verified"]:
                payment.status = Payment.Status.REJECTED
                payment.note = values.get("note", payment.note)
                payment.verified_at = timezone.now()
                payment.save(update_fields=["status", "note", "verified_at"])
                return Response(PaymentSerializer(payment).data)

            order = Order.objects.select_for_update().get(pk=payment.order_id)
            amount = values.get("verified_amount", payment.amount)
            if amount <= 0 or amount > payment.amount:
                raise ValidationError({"verified_amount": "Verified amount must be positive and no greater than the submitted amount."})
            if payment.kind == Payment.Kind.PAYMENT:
                remaining = max(order.total - order.paid_amount, Decimal("0.00"))
                if amount > remaining:
                    raise ValidationError({"verified_amount": "Verified amount exceeds the order's remaining balance."})
                order.paid_amount += amount
                if order.paid_amount >= order.total and order.status == Order.Status.APPROVED:
                    order.status = Order.Status.PAID
                order.save(update_fields=["paid_amount", "status"])
                if order.payment_mode == Order.PaymentMode.CREDIT:
                    facility = CreditFacility.objects.select_for_update().get(wholesaler=order.wholesaler)
                    reduction = min(facility.outstanding_balance, amount)
                    facility.outstanding_balance -= reduction
                    facility.save(update_fields=["outstanding_balance", "updated_at"])
                    CreditEntry.objects.create(
                        facility=facility,
                        order=order,
                        kind=CreditEntry.Kind.PAYMENT,
                        amount=-reduction,
                        note=f"Verified payment {payment.pk}",
                    )
            else:
                order.paid_amount = max(order.paid_amount - amount, Decimal("0.00"))
                order.save(update_fields=["paid_amount"])
            payment.status = Payment.Status.VERIFIED
            payment.verified_amount = amount
            payment.note = values.get("note", payment.note)
            payment.verified_at = timezone.now()
            payment.save(update_fields=["status", "verified_amount", "note", "verified_at"])
            award_order_points(order)
        return Response(PaymentSerializer(payment).data)
