from django.db import transaction
from rest_framework.exceptions import ValidationError

from accounts.models import User
from loyalty.models import LoyaltyTransaction
from loyalty.services import available_points

from .models import Redemption, RewardItem


@transaction.atomic
def request_redemption(*, user, reward_item, shipping_address=""):
    User.objects.select_for_update().get(pk=user.pk)
    item = RewardItem.objects.select_for_update().get(pk=reward_item.pk)
    if not item.is_active or item.available_quantity < 1:
        raise ValidationError({"reward_item": "This reward is not currently available."})
    if available_points(user) < item.points_cost:
        raise ValidationError({"detail": "You do not have enough available points."})

    item.reserved_quantity += 1
    item.save(update_fields=["reserved_quantity"])
    redemption = Redemption.objects.create(
        wholesaler=user,
        reward_item=item,
        points_cost_snapshot=item.points_cost,
        shipping_address=shipping_address,
    )
    LoyaltyTransaction.objects.create(
        user=user,
        redemption=redemption,
        kind=LoyaltyTransaction.Kind.REDEEMED,
        points=-item.points_cost,
        description=f"Reward redemption: {item.name}",
        reference=f"redemption:{redemption.pk}:redeemed",
    )
    return redemption


@transaction.atomic
def update_redemption(redemption, *, status_value, admin_note=""):
    redemption = Redemption.objects.select_for_update().select_related("reward_item", "wholesaler").get(pk=redemption.pk)
    allowed = {
        Redemption.Status.PENDING: {Redemption.Status.APPROVED, Redemption.Status.REJECTED},
        Redemption.Status.APPROVED: {Redemption.Status.DISPATCHED},
        Redemption.Status.DISPATCHED: {Redemption.Status.DELIVERED},
    }
    if status_value not in allowed.get(redemption.status, set()):
        raise ValidationError({"status": "This rewards redemption cannot move to the requested status."})

    item = RewardItem.objects.select_for_update().get(pk=redemption.reward_item_id)
    if status_value == Redemption.Status.REJECTED:
        item.reserved_quantity -= 1
        item.save(update_fields=["reserved_quantity"])
        LoyaltyTransaction.objects.create(
            user=redemption.wholesaler,
            redemption=redemption,
            kind=LoyaltyTransaction.Kind.REFUNDED,
            points=redemption.points_cost_snapshot,
            description=f"Points refunded for rejected redemption {redemption.pk}",
            reference=f"redemption:{redemption.pk}:refund",
        )
    elif status_value == Redemption.Status.DISPATCHED:
        item.reserved_quantity -= 1
        item.stock_quantity -= 1
        item.save(update_fields=["reserved_quantity", "stock_quantity"])

    redemption.status = status_value
    redemption.admin_note = admin_note
    redemption.save(update_fields=["status", "admin_note", "updated_at"])
    return redemption
