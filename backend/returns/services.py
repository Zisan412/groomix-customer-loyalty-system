from decimal import Decimal, ROUND_DOWN
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from credit.models import CreditEntry, CreditFacility
from loyalty.models import LoyaltySettings, LoyaltyTransaction
from orders.models import Order, OrderItem
from payments.models import Payment
from catalog.models import Product

from .models import ReturnItem, ReturnRequest


@transaction.atomic
def create_return_request(*, user, order, reason, items):
    order = Order.objects.select_for_update().get(pk=order.pk, wholesaler=user)
    if order.status != Order.Status.DELIVERED or not order.delivered_at:
        raise ValidationError({"order": "Returns are available only for delivered orders."})
    if timezone.now() > order.delivered_at + timedelta(days=7):
        raise ValidationError({"order": "The 7-day return window has passed."})

    requested = {}
    for item in items:
        order_item = item["order_item"]
        if order_item.order_id != order.id:
            raise ValidationError({"items": "Each returned item must belong to this order."})
        if order_item.pk in requested:
            raise ValidationError({"items": "Each order item can appear only once in a return request."})
        requested[order_item.pk] = requested.get(order_item.pk, 0) + item["quantity_boxes"]

    for order_item_id, quantity in requested.items():
        order_item = OrderItem.objects.select_for_update().get(pk=order_item_id)
        previously_requested = sum(
            ReturnItem.objects.filter(
                order_item=order_item,
            ).exclude(return_request__status=ReturnRequest.Status.REJECTED).values_list(
                "quantity_boxes", flat=True
            )
        )
        if previously_requested + quantity > order_item.quantity_boxes:
            raise ValidationError({"items": f"Return quantity exceeds the delivered quantity for {order_item.product_name}."})

    return_request = ReturnRequest.objects.create(
        order=order,
        wholesaler=user,
        reason=reason,
    )
    ReturnItem.objects.bulk_create([
        ReturnItem(return_request=return_request, **item) for item in items
    ])
    return return_request


@transaction.atomic
def decide_return(return_request, *, decision, note=""):
    request = ReturnRequest.objects.select_for_update().select_related("order", "wholesaler").get(pk=return_request.pk)
    if request.status != ReturnRequest.Status.PENDING:
        raise ValidationError({"detail": "This return request has already been reviewed."})
    request.status = (
        ReturnRequest.Status.APPROVED if decision == "approve" else ReturnRequest.Status.REJECTED
    )
    request.inspection_result = note
    request.reviewed_at = timezone.now()
    request.save(update_fields=["status", "inspection_result", "reviewed_at"])
    return request


@transaction.atomic
def inspect_return(return_request, *, result, restock):
    request = ReturnRequest.objects.select_for_update().select_related("order", "wholesaler").get(pk=return_request.pk)
    if request.status != ReturnRequest.Status.APPROVED:
        raise ValidationError({"detail": "Only approved return requests can be inspected."})

    order = Order.objects.select_for_update().get(pk=request.order_id)
    return_items = list(request.items.select_related("order_item", "order_item__product"))
    returned_subtotal = sum(
        (item.order_item.selling_price * item.quantity_boxes for item in return_items),
        Decimal("0.00"),
    )
    if order.subtotal:
        discount_share = (
            order.points_discount * returned_subtotal / order.subtotal
        ).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    else:
        discount_share = Decimal("0.00")
    return_value = max(returned_subtotal - discount_share, Decimal("0.00"))

    if restock:
        for item in return_items:
            product = Product.objects.select_for_update().get(pk=item.order_item.product_id)
            product.stock_boxes += item.quantity_boxes
            product.save(update_fields=["stock_boxes"])

    credit_applied = Decimal("0.00")
    if order.payment_mode == Order.PaymentMode.CREDIT and return_value:
        try:
            facility = CreditFacility.objects.select_for_update().get(wholesaler=request.wholesaler)
        except CreditFacility.DoesNotExist:
            facility = None
        if facility:
            unpaid_for_order = max(order.total - order.paid_amount, Decimal("0.00"))
            credit_applied = min(return_value, unpaid_for_order, facility.outstanding_balance)
            if credit_applied:
                facility.outstanding_balance -= credit_applied
                facility.save(update_fields=["outstanding_balance", "updated_at"])
                CreditEntry.objects.create(
                    facility=facility,
                    order=order,
                    kind=CreditEntry.Kind.ADJUSTMENT,
                    amount=-credit_applied,
                    note=f"Approved return {request.pk}",
                )

    cash_refund_due = max(return_value - credit_applied, Decimal("0.00"))
    already_refunded = sum(
        Payment.objects.filter(
            order=order, kind=Payment.Kind.REFUND, status=Payment.Status.PENDING
        ).values_list("amount", flat=True),
        Decimal("0.00"),
    )
    refundable = min(
        cash_refund_due,
        max(order.paid_amount - already_refunded, Decimal("0.00")),
    )
    if refundable:
        Payment.objects.create(
            order=order,
            submitted_by=request.wholesaler,
            kind=Payment.Kind.REFUND,
            amount=refundable,
            status=Payment.Status.PENDING,
            method="Manual refund",
            reference=f"return:{request.pk}:refund",
            note=f"Refund request for return {request.pk}; verify after payment is issued.",
        )

    earned = LoyaltyTransaction.objects.filter(
        order=order, kind=LoyaltyTransaction.Kind.EARNED
    ).first()
    if earned and earned.points > 0:
        total_profit = sum(
            (
                max(line.selling_price - line.manufacturing_cost, Decimal("0.00"))
                * line.quantity_boxes
                for line in order.items.all()
            ),
            Decimal("0.00"),
        )
        returned_profit = sum(
            (
                max(item.order_item.selling_price - item.order_item.manufacturing_cost, Decimal("0.00"))
                * item.quantity_boxes
                for item in return_items
            ),
            Decimal("0.00"),
        )
        if total_profit:
            reversal_points = int(
                (Decimal(earned.points) * returned_profit / total_profit).to_integral_value(
                    rounding=ROUND_DOWN
                )
            )
            if reversal_points:
                LoyaltyTransaction.objects.create(
                    user=request.wholesaler,
                    order=order,
                    kind=LoyaltyTransaction.Kind.REVERSED,
                    points=-reversal_points,
                    description=f"Points reversed for return {request.pk}",
                    reference=f"return:{request.pk}:points",
                )

    order.subtotal = max(order.subtotal - returned_subtotal, Decimal("0.00"))
    order.points_discount = max(order.points_discount - discount_share, Decimal("0.00"))
    order.total = max(order.total - return_value, Decimal("0.00"))
    order.save(update_fields=["subtotal", "points_discount", "total"])
    request.status = ReturnRequest.Status.COMPLETED
    request.inspection_result = result
    request.refund_amount = refundable
    request.reviewed_at = timezone.now()
    request.save(update_fields=["status", "inspection_result", "refund_amount", "reviewed_at"])
    return request
