from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import User
from catalog.models import Category, Product
from orders.models import Order, OrderItem
from loyalty.models import LoyaltyTransaction
from payments.models import Payment
from returns.models import ReturnRequest


class ReturnApiTests(APITestCase):
    def setUp(self):
        self.wholesaler = User.objects.create_user(
            username="partner", email="partner@example.com", password="Strong-test-password-2026"
        )
        category = Category.objects.create(name="Face Care")
        product = Product.objects.create(
            category=category, sku="FC-RTN", name="Face wash",
            selling_price="100.00", manufacturing_cost="60.00",
            units_per_box=12, stock_boxes=5,
        )
        self.order = Order.objects.create(
            wholesaler=self.wholesaler, status=Order.Status.DELIVERED,
            subtotal="100.00", total="100.00",
            delivered_at=timezone.now() - timedelta(days=8),
        )
        self.item = OrderItem.objects.create(
            order=self.order, product=product, product_name=product.name,
            selling_price=product.selling_price, manufacturing_cost=product.manufacturing_cost,
            units_per_box=product.units_per_box, quantity_boxes=1,
        )

    def test_return_request_outside_seven_day_window_is_rejected(self):
        self.client.force_authenticate(self.wholesaler)
        response = self.client.post(
            "/api/returns/",
            {
                "order": self.order.pk,
                "reason": "Package damaged",
                "items": [{"order_item": self.item.pk, "quantity_boxes": 1}],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ReturnRequest.objects.count(), 0)

    def test_partial_return_restock_refunds_and_reverses_attributable_points(self):
        self.order.subtotal = "200.00"
        self.order.total = "200.00"
        self.item.quantity_boxes = 2
        self.item.save()
        self.order.paid_amount = "200.00"
        self.order.delivered_at = timezone.now() - timedelta(days=1)
        self.order.save()
        self.client.force_authenticate(self.wholesaler)
        response = self.client.post(
            "/api/returns/",
            {
                "order": self.order.pk,
                "reason": "One box damaged",
                "items": [{"order_item": self.item.pk, "quantity_boxes": 1}],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        return_id = response.data["id"]
        self.client.force_authenticate(User.objects.create_superuser(
            username="factory", email="factory@example.com", password="Strong-test-password-2026"
        ))
        approved = self.client.post(
            f"/api/returns/{return_id}/review/",
            {"decision": "approve"},
            format="json",
        )
        self.assertEqual(approved.status_code, 200)
        inspected = self.client.post(
            f"/api/returns/{return_id}/inspect/",
            {"result": "One box accepted and restocked.", "restock": True},
            format="json",
        )
        self.assertEqual(inspected.status_code, 200)
        self.assertEqual(inspected.data["status"], ReturnRequest.Status.COMPLETED)
        self.assertEqual(inspected.data["refund_amount"], "100.00")
        self.assertEqual(
            LoyaltyTransaction.objects.filter(order=self.order, kind=LoyaltyTransaction.Kind.REVERSED).first().points,
            -400,
        )
        self.assertTrue(Payment.objects.filter(order=self.order, kind=Payment.Kind.REFUND).exists())
        self.item.product.refresh_from_db()
        self.assertEqual(self.item.product.stock_boxes, 6)
