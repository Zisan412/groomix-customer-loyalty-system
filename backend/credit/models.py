from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class CreditRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    wholesaler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="credit_requests")
    requested_limit = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("1.00"))])
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["wholesaler"],
                condition=models.Q(status="PENDING"),
                name="one_pending_credit_request_per_wholesaler",
            )
        ]


class CreditFacility(models.Model):
    wholesaler = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="credit_facility")
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    outstanding_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))])
    payment_period_days = models.PositiveIntegerField(default=30)
    valid_from = models.DateField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def available_credit(self):
        return max(self.credit_limit - self.outstanding_balance, 0)

    def __str__(self):
        return f"Credit facility for {self.wholesaler}"


class CreditEntry(models.Model):
    class Kind(models.TextChoices):
        CHARGE = "CHARGE", "Order charge"
        PAYMENT = "PAYMENT", "Payment"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"

    facility = models.ForeignKey(CreditFacility, on_delete=models.PROTECT, related_name="entries")
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, null=True, blank=True, related_name="credit_entries")
    kind = models.CharField(max_length=12, choices=Kind.choices)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
from decimal import Decimal

