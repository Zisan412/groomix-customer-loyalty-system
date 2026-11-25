from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Payment(models.Model):
    class Kind(models.TextChoices):
        PAYMENT = "PAYMENT", "Payment"
        REFUND = "REFUND", "Refund"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending verification"
        VERIFIED = "VERIFIED", "Verified"
        REJECTED = "REJECTED", "Rejected"

    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="payments")
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="submitted_payments")
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.PAYMENT)
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    verified_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    method = models.CharField(max_length=40, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["reference"], condition=~models.Q(reference=""), name="unique_nonempty_payment_reference"),
        ]

    def __str__(self):
        return f"{self.kind} {self.amount} for order {self.order_id}"
