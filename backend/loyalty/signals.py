from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import Order

from .services import award_order_points


@receiver(post_save, sender=Order)
def award_points_when_order_delivered(sender, instance, **kwargs):
    if (
        instance.status == Order.Status.DELIVERED
        and Decimal(instance.paid_amount) >= Decimal(instance.total)
    ):
        award_order_points(instance)
