from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class RewardItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    points_cost = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    stock_quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["points_cost", "name"]

    @property
    def available_quantity(self):
        return self.stock_quantity - self.reserved_quantity

    def __str__(self):
        return self.name


class Redemption(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending approval"
        APPROVED = "APPROVED", "Approved"
        DISPATCHED = "DISPATCHED", "Dispatched"
        DELIVERED = "DELIVERED", "Delivered"
        REJECTED = "REJECTED", "Rejected"

    wholesaler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="redemptions")
    reward_item = models.ForeignKey(RewardItem, on_delete=models.PROTECT, related_name="redemptions")
    points_cost_snapshot = models.PositiveIntegerField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    shipping_address = models.TextField(blank=True)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
