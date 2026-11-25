from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from catalog.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        PAID = "PAID", "Paid"
        PROCESSING = "PROCESSING", "Processing"
        DISPATCHED = "DISPATCHED", "Dispatched"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    class PaymentMode(models.TextChoices):
        ADVANCE = "ADVANCE", "Advance payment"
        CREDIT = "CREDIT", "Credit / Pay Later"

    wholesaler = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_mode = models.CharField(max_length=10, choices=PaymentMode.choices, default=PaymentMode.ADVANCE)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    points_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    dispatched_at = models.DateTimeField(null=True, blank=True)
    credit_due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def payment_status(self):
        if self.paid_amount >= self.total:
            return "PAID"
        if self.paid_amount > 0:
            return "PARTIALLY_PAID"
        return "UNPAID"

    def __str__(self):
        return f"Order {self.pk} ({self.wholesaler})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    product_name = models.CharField(max_length=200)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    manufacturing_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])
    units_per_box = models.PositiveIntegerField()
    quantity_boxes = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    @property
    def line_total(self):
        return self.selling_price * self.quantity_boxes

    def __str__(self):
        return f"{self.product_name} x {self.quantity_boxes} boxes"
