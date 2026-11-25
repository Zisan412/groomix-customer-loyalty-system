from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class LoyaltySettings(models.Model):
    reward_budget_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10, validators=[MinValueValidator(Decimal("0.00"))])
    points_per_rupee = models.PositiveIntegerField(default=100)
    minimum_redemption_points = models.PositiveIntegerField(default=1000)
    maximum_checkout_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=20, validators=[MinValueValidator(Decimal("0.00"))])
    points_expiry_months = models.PositiveIntegerField(default=12)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def current(cls):
        settings_obj, _ = cls.objects.get_or_create(pk=1)
        return settings_obj

    def __str__(self):
        return "Groomix loyalty settings"


class LoyaltyTransaction(models.Model):
    class Kind(models.TextChoices):
        EARNED = "EARNED", "Earned"
        REDEEMED = "REDEEMED", "Redeemed"
        EXPIRED = "EXPIRED", "Expired"
        REFUNDED = "REFUNDED", "Refunded"
        REVERSED = "REVERSED", "Reversed"
        ADJUSTMENT = "ADJUSTMENT", "Admin adjustment"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="loyalty_transactions")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="created_loyalty_transactions",
    )
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, null=True, blank=True, related_name="loyalty_transactions")
    redemption = models.ForeignKey("rewards.Redemption", on_delete=models.PROTECT, null=True, blank=True, related_name="loyalty_transactions")
    kind = models.CharField(max_length=12, choices=Kind.choices)
    points = models.IntegerField()
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    reference = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                condition=models.Q(kind="EARNED"),
                name="one_loyalty_award_per_order",
            ),
            models.UniqueConstraint(
                fields=["reference"],
                condition=~models.Q(reference=""),
                name="unique_loyalty_reference",
            ),
        ]
