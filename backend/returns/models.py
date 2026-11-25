from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class ReturnRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        INSPECTED = "INSPECTED", "Inspected"
        COMPLETED = "COMPLETED", "Completed"

    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="returns")
    wholesaler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="returns")
    reason = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    inspection_result = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))])
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class ReturnItem(models.Model):
    return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name="items")
    order_item = models.ForeignKey("orders.OrderItem", on_delete=models.PROTECT, related_name="return_items")
    quantity_boxes = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["return_request", "order_item"], name="unique_order_item_per_return"),
        ]
from decimal import Decimal

