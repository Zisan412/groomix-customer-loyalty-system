from decimal import Decimal

from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import User
from catalog.models import Category, Product
from credit.models import CreditFacility
from loyalty.models import LoyaltySettings, LoyaltyTransaction
from loyalty.services import available_points
from orders.models import Order
from payments.models import Payment


class OrderApiTests(APITestCase):
    def setUp(self):
        self.wholesaler = User.objects.create_user(
            username="partner", email="partner@example.com", password="Strong-test-password-2026",
            business_name="Partner Shop",
        )
        self.other_wholesaler = User.objects.create_user(
            username="other", email="other@example.com", password="Strong-test-password-2026",
        )
        self.admin = User.objects.create_superuser(
            username="factory", email="factory@example.com", password="Strong-test-password-2026",
        )
        self.category = Category.objects.create(name="Hair Care")
        self.product = Product.objects.create(
            category=self.category, sku="HC-101", name="Shampoo",
            selling_price="120.00", manufacturing_cost="84.00",
            units_per_box=24, stock_boxes=10,
        )
        self.client.force_authenticate(self.wholesaler)

    def create_order(self, payment_mode="ADVANCE", redeem_points=0, quantity=2):
        return self.client.post(
            "/api/orders/",
            {
                "items": [{"product": self.product.pk, "quantity_boxes": quantity}],
                "payment_mode": payment_mode,
                "redeem_points": redeem_points,
            },
            format="json",
        )

    def test_order_uses_server_price_and_snapshots_product(self):
        response = self.create_order()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Decimal(response.data["total"]), Decimal("240.00"))
        item = response.data["items"][0]
        self.assertEqual(Decimal(item["selling_price"]), Decimal("120.00"))
        self.product.selling_price = Decimal("200.00")
        self.product.save()
        self.assertEqual(Decimal(item["selling_price"]), Decimal("120.00"))

    def test_pending_order_cancel_does_not_reserve_stock(self):
        response = self.create_order()
        order_id = response.data["id"]
        cancelled = self.client.post(f"/api/orders/{order_id}/cancel/", {}, format="json")
        self.assertEqual(cancelled.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.reserved_boxes, 0)
        self.assertEqual(cancelled.data["status"], Order.Status.CANCELLED)

    def test_checkout_points_are_server_limited_and_restored_on_cancellation(self):
        LoyaltyTransaction.objects.create(
            user=self.wholesaler, kind=LoyaltyTransaction.Kind.EARNED, points=5000,
            description="Checkout test balance",
        )
        order_response = self.create_order(redeem_points=4000)
        self.assertEqual(order_response.status_code, 201)
        self.assertEqual(Decimal(order_response.data["points_discount"]), Decimal("40.00"))
        self.assertEqual(Decimal(order_response.data["total"]), Decimal("200.00"))
        self.assertEqual(available_points(self.wholesaler), 1000)

        rejected = self.create_order(redeem_points=5000)
        self.assertEqual(rejected.status_code, 400)
        self.client.post(f"/api/orders/{order_response.data['id']}/cancel/", {}, format="json")
        self.assertEqual(available_points(self.wholesaler), 5000)

    def test_approval_reserves_stock_and_cancellation_releases_it(self):
        order_id = self.create_order().data["id"]
        self.client.force_authenticate(self.admin)
        approved = self.client.post(f"/api/orders/{order_id}/approve/", {}, format="json")
        self.assertEqual(approved.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.reserved_boxes, 2)
        self.client.force_authenticate(self.wholesaler)
        cancelled = self.client.post(f"/api/orders/{order_id}/cancel/", {}, format="json")
        self.assertEqual(cancelled.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.reserved_boxes, 0)

    def test_wholesaler_cannot_read_another_users_order(self):
        order_id = self.create_order().data["id"]
        self.client.force_authenticate(self.other_wholesaler)
        response = self.client.get(f"/api/orders/{order_id}/")
        self.assertEqual(response.status_code, 404)

    def test_credit_request_needs_approved_facility_before_order_approval(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/credit/requests/",
            {
                "wholesaler": self.wholesaler.pk,
                "requested_limit": "1000.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_credit_order_tracks_partial_payments_and_awards_once_when_fully_paid(self):
        today = timezone.localdate()
        CreditFacility.objects.create(
            wholesaler=self.wholesaler,
            credit_limit="1000.00",
            outstanding_balance="0.00",
            payment_period_days=30,
            valid_from=today,
            valid_until=today + timezone.timedelta(days=60),
        )
        order_id = self.create_order(payment_mode="CREDIT").data["id"]
        self.client.force_authenticate(self.admin)
        self.client.post(f"/api/orders/{order_id}/approve/", {}, format="json")
        order = Order.objects.get(pk=order_id)
        self.assertEqual(order.status, Order.Status.APPROVED)
        self.assertEqual(order.wholesaler.credit_facility.outstanding_balance, Decimal("240.00"))

        self.client.force_authenticate(self.wholesaler)
        first = self.client.post(
            "/api/payments/",
            {"order": order_id, "amount": "100.00", "method": "Bank transfer"},
            format="json",
        )
        self.client.force_authenticate(self.admin)
        self.client.post(f"/api/payments/{first.data['id']}/verify/", {"verified": True}, format="json")
        self.client.post(
            f"/api/orders/{order_id}/set_status/",
            {"status": "PROCESSING"},
            format="json",
        )
        self.client.post(
            f"/api/orders/{order_id}/set_status/",
            {"status": "DISPATCHED"},
            format="json",
        )
        self.client.post(
            f"/api/orders/{order_id}/set_status/",
            {"status": "DELIVERED"},
            format="json",
        )
        self.assertFalse(LoyaltyTransaction.objects.filter(order_id=order_id, kind="EARNED").exists())

        self.client.force_authenticate(self.wholesaler)
        second = self.client.post(
            "/api/payments/",
            {"order": order_id, "amount": "140.00", "method": "Bank transfer"},
            format="json",
        )
        self.client.force_authenticate(self.admin)
        self.client.post(f"/api/payments/{second.data['id']}/verify/", {"verified": True}, format="json")
        settings = LoyaltySettings.current()
        self.assertEqual(settings.reward_budget_percent, Decimal("10.00"))
        awards = LoyaltyTransaction.objects.filter(order_id=order_id, kind="EARNED")
        self.assertEqual(awards.count(), 1)
        self.assertEqual(awards.first().points, 720)

    def test_advance_order_requires_full_payment_to_process_and_cannot_cancel_after_dispatch(self):
        order_id = self.create_order().data["id"]
        self.client.force_authenticate(self.admin)
        self.client.post(f"/api/orders/{order_id}/approve/", {}, format="json")
        processing = self.client.post(
            f"/api/orders/{order_id}/set_status/",
            {"status": "PROCESSING"},
            format="json",
        )
        self.assertEqual(processing.status_code, 400)
        self.client.force_authenticate(self.wholesaler)
        self.assertEqual(self.client.post(f"/api/orders/{order_id}/cancel/", {}, format="json").status_code, 200)
