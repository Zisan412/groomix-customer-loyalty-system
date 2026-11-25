from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import User
from catalog.models import Product
from credit.models import CreditEntry, CreditFacility
from loyalty.models import LoyaltyTransaction
from loyalty.services import redeem_checkout_points
from payments.models import Payment

from .models import Order, OrderItem


@transaction.atomic
def create_order(*, user, items, payment_mode, redeem_points=0, notes=""):
    User.objects.select_for_update().get(pk=user.pk)
    products = {
        product.pk: product
        for product in Product.objects.select_for_update()
        .select_related("category")
        .filter(pk__in=[item["product"].pk for item in items], is_active=True, category__is_active=True)
    }
    if len(products) != len(items):
        raise ValidationError({"items": "One or more products are unavailable."})

    subtotal = Decimal("0.00")
    for requested in items:
        product = products[requested["product"].pk]
        quantity = requested["quantity_boxes"]
        if product.available_boxes < quantity:
            raise ValidationError({"items": f"Not enough stock available for {product.name}."})
        subtotal += product.selling_price * quantity

    order = Order.objects.create(
        wholesaler=user,
        payment_mode=payment_mode,
        subtotal=subtotal,
        total=subtotal,
        notes=notes,
    )
    OrderItem.objects.bulk_create([
        OrderItem(
            order=order,
            product=products[item["product"].pk],
            product_name=products[item["product"].pk].name,
            selling_price=products[item["product"].pk].selling_price,
            manufacturing_cost=products[item["product"].pk].manufacturing_cost,
            units_per_box=products[item["product"].pk].units_per_box,
            quantity_boxes=item["quantity_boxes"],
        )
        for item in items
    ])
    if redeem_points:
        redeem_checkout_points(user, order, redeem_points)
    return order


@transaction.atomic
def approve_order(order):
    order = Order.objects.select_for_update().select_related("wholesaler").get(pk=order.pk)
    if order.status != Order.Status.PENDING:
        raise ValidationError({"detail": "Only pending orders can be approved."})

    product_quantities = {}
    for item in order.items.all():
        product_quantities[item.product_id] = product_quantities.get(item.product_id, 0) + item.quantity_boxes
    products = {
        product.pk: product
        for product in Product.objects.select_for_update().filter(pk__in=product_quantities)
    }
    for product_id, quantity in product_quantities.items():
        product = products[product_id]
        if not product.is_active or product.available_boxes < quantity:
            raise ValidationError({"detail": f"Insufficient stock to approve {product.name}."})

    if order.payment_mode == Order.PaymentMode.CREDIT:
        try:
            facility = CreditFacility.objects.select_for_update().get(
                wholesaler=order.wholesaler, is_active=True
            )
        except CreditFacility.DoesNotExist as exc:
            raise ValidationError({"detail": "No active credit facility is available."}) from exc
        today = timezone.localdate()
        if not facility.valid_from <= today <= facility.valid_until:
            raise ValidationError({"detail": "The credit facility is outside its validity period."})
        if facility.available_credit < order.total:
            raise ValidationError({"detail": "The order exceeds available credit."})
        facility.outstanding_balance += order.total
        facility.save(update_fields=["outstanding_balance", "updated_at"])
        order.credit_due_date = timezone.localdate() + timezone.timedelta(days=facility.payment_period_days)
        order.save(update_fields=["credit_due_date"])
        CreditEntry.objects.create(
            facility=facility,
            order=order,
            kind=CreditEntry.Kind.CHARGE,
            amount=order.total,
            note=f"Approved order {order.pk}",
        )

    for product_id, quantity in product_quantities.items():
        product = products[product_id]
        product.reserved_boxes += quantity
        product.save(update_fields=["reserved_boxes"])
    order.status = Order.Status.APPROVED
    order.approved_at = timezone.now()
    order.save(update_fields=["status", "approved_at"])
    return order


@transaction.atomic
def cancel_order(order, *, actor):
    order = Order.objects.select_for_update().select_related("wholesaler").get(pk=order.pk)
    if order.status in {Order.Status.DISPATCHED, Order.Status.DELIVERED}:
        raise ValidationError({"detail": "Dispatched orders cannot be cancelled. Submit a return request."})
    if order.status == Order.Status.CANCELLED:
        raise ValidationError({"detail": "This order is already closed."})

    if order.status != Order.Status.PENDING:
        for item in order.items.all():
            product = Product.objects.select_for_update().get(pk=item.product_id)
            product.reserved_boxes -= item.quantity_boxes
            product.save(update_fields=["reserved_boxes"])
        if order.payment_mode == Order.PaymentMode.CREDIT:
            try:
                facility = CreditFacility.objects.select_for_update().get(wholesaler=order.wholesaler)
            except CreditFacility.DoesNotExist:
                facility = None
            if facility:
                charge = sum(
                    (
                        entry.amount
                        for entry in CreditEntry.objects.filter(
                            facility=facility,
                            order=order,
                            kind=CreditEntry.Kind.CHARGE,
                        )
                    ),
                    Decimal("0.00"),
                )
                if charge:
                    adjustment = min(facility.outstanding_balance, charge)
                    facility.outstanding_balance -= adjustment
                    facility.save(update_fields=["outstanding_balance", "updated_at"])
                    CreditEntry.objects.create(
                        facility=facility,
                        order=order,
                        kind=CreditEntry.Kind.ADJUSTMENT,
                        amount=-adjustment,
                        note=f"Cancelled order {order.pk}",
                    )

    redeemed = LoyaltyTransaction.objects.filter(
        order=order, kind=LoyaltyTransaction.Kind.REDEEMED
    ).first()
    if redeemed and not LoyaltyTransaction.objects.filter(
        order=order, kind=LoyaltyTransaction.Kind.REFUNDED
    ).exists():
        LoyaltyTransaction.objects.create(
            user=order.wholesaler,
            order=order,
            kind=LoyaltyTransaction.Kind.REFUNDED,
            points=-redeemed.points,
            description=f"Checkout points refunded for cancelled order {order.pk}",
            reference=f"order:{order.pk}:cancel-points",
        )
    if order.paid_amount > 0 and not Payment.objects.filter(
        order=order, kind=Payment.Kind.REFUND, reference=f"order:{order.pk}:cancel-refund"
    ).exists():
        Payment.objects.create(
            order=order,
            submitted_by=actor,
            kind=Payment.Kind.REFUND,
            amount=order.paid_amount,
            status=Payment.Status.PENDING,
            method="Manual refund",
            reference=f"order:{order.pk}:cancel-refund",
            note="Refund pending admin verification after cancellation.",
        )
    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])
    return order
