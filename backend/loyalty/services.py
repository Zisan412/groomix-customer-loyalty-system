import calendar
from decimal import Decimal, ROUND_DOWN

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import User
from .models import LoyaltySettings, LoyaltyTransaction


def _ledger_balance(user):
    lots, debt = _point_lots(user)
    remaining = sum(
        lot["remaining"]
        for lot in lots
        if lot["expires_at"] is None or lot["expires_at"] > timezone.now()
    )
    return max(remaining - debt, 0)


def _point_lots(user):
    entries = list(
        LoyaltyTransaction.objects.filter(user=user).order_by("created_at", "pk")
    )
    lots = []
    debt = 0
    for entry in entries:
        if entry.points > 0:
            credit = entry.points
            paid_debt = min(debt, credit)
            debt -= paid_debt
            lots.append({
                "id": entry.pk,
                "kind": entry.kind,
                "remaining": credit - paid_debt,
                "expires_at": entry.expires_at,
            })
        elif entry.kind == LoyaltyTransaction.Kind.EXPIRED and entry.reference.startswith("expiry:"):
            earning_id = int(entry.reference.split(":", 1)[1])
            source = next((lot for lot in lots if lot["id"] == earning_id), None)
            if source:
                source["remaining"] = max(source["remaining"] + entry.points, 0)
        else:
            to_consume = abs(entry.points)
            for lot in lots:
                consumed = min(lot["remaining"], to_consume)
                lot["remaining"] -= consumed
                to_consume -= consumed
                if to_consume == 0:
                    break
            debt += to_consume
    return lots, debt


def expire_due_points(user):
    now = timezone.now()
    with transaction.atomic():
        User.objects.select_for_update().get(pk=user.pk)
        list(LoyaltyTransaction.objects.filter(user=user).select_for_update().values_list("pk", flat=True))
        lots, _ = _point_lots(user)
        for lot in lots:
            if (
                lot["kind"] == LoyaltyTransaction.Kind.EARNED
                and lot["expires_at"] is not None
                and lot["expires_at"] <= now
                and lot["remaining"] > 0
            ):
                reference = f"expiry:{lot['id']}"
                expiring_points = lot["remaining"]
                LoyaltyTransaction.objects.create(
                    user=user,
                    kind=LoyaltyTransaction.Kind.EXPIRED,
                    points=-expiring_points,
                    description=f"Expired points from earning #{lot['id']}",
                    reference=reference,
                )


def available_points(user):
    expire_due_points(user)
    return _ledger_balance(user)


def redeem_checkout_points(user, order, requested_points):
    if not requested_points:
        return Decimal("0.00")
    settings = LoyaltySettings.current()
    if requested_points < settings.minimum_redemption_points:
        raise ValidationError({
            "redeem_points": f"At least {settings.minimum_redemption_points} points are required."
        })
    current_balance = available_points(user)
    if requested_points > current_balance:
        raise ValidationError({"redeem_points": "You do not have enough available points."})

    rupee_value = (Decimal(requested_points) / Decimal(settings.points_per_rupee)).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )
    max_discount = (order.subtotal * settings.maximum_checkout_discount_percent / Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )
    if rupee_value > max_discount:
        raise ValidationError({
            "redeem_points": "Requested points exceed the configured checkout discount limit."
        })
    if rupee_value >= order.subtotal:
        raise ValidationError({"redeem_points": "Points cannot reduce an order total to zero."})

    order.points_discount = rupee_value
    order.total = order.subtotal - rupee_value
    order.save(update_fields=["points_discount", "total"])
    LoyaltyTransaction.objects.create(
        user=user,
        order=order,
        kind=LoyaltyTransaction.Kind.REDEEMED,
        points=-requested_points,
        description=f"Checkout discount for order {order.pk}",
        reference=f"order:{order.pk}:checkout",
    )
    return rupee_value


def award_order_points(order):
    if order.status != order.Status.DELIVERED or order.paid_amount < order.total:
        return None
    if order.status == order.Status.CANCELLED:
        return None

    existing = LoyaltyTransaction.objects.filter(
        order=order, kind=LoyaltyTransaction.Kind.EARNED
    ).first()
    if existing:
        return existing

    rules = LoyaltySettings.current()
    gross_profit = sum(
        (
            max(item.selling_price - item.manufacturing_cost, Decimal("0.00"))
            * item.quantity_boxes
            for item in order.items.all()
        ),
        Decimal("0.00"),
    )
    eligible_profit = max(gross_profit - order.points_discount, Decimal("0.00"))
    reward_budget = eligible_profit * rules.reward_budget_percent / Decimal("100")
    points = int((reward_budget * rules.points_per_rupee).to_integral_value(rounding=ROUND_DOWN))
    if points <= 0:
        return None

    expires_at = add_months(timezone.now(), rules.points_expiry_months)
    try:
        with transaction.atomic():
            return LoyaltyTransaction.objects.create(
                user=order.wholesaler,
                order=order,
                kind=LoyaltyTransaction.Kind.EARNED,
                points=points,
                description=f"Points earned from delivered order {order.pk}",
                expires_at=expires_at,
                reference=f"order:{order.pk}:earned",
            )
    except IntegrityError:
        return LoyaltyTransaction.objects.filter(order=order, kind=LoyaltyTransaction.Kind.EARNED).first()


def add_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)
