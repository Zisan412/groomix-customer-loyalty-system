from rest_framework.test import APITestCase

from accounts.models import User
from catalog.models import Category, Product
from orders.models import Order
from payments.models import Payment


class PaymentApiTests(APITestCase):
    def setUp(self):
        self.wholesaler = User.objects.create_user(
            username="partner", email="partner@example.com", password="Strong-test-password-2026"
        )
        self.admin = User.objects.create_superuser(
            username="factory", email="factory@example.com", password="Strong-test-password-2026"
        )
        category = Category.objects.create(name="Face Care")
        product = Product.objects.create(
            category=category, sku="FC-1", name="Face wash", selling_price="100.00",
            manufacturing_cost="60.00", units_per_box=12, stock_boxes=10,
        )
        self.order = Order.objects.create(
            wholesaler=self.wholesaler, status=Order.Status.APPROVED,
            subtotal="100.00", total="100.00",
        )
        from orders.models import OrderItem
        OrderItem.objects.create(
            order=self.order, product=product, product_name=product.name,
            selling_price=product.selling_price, manufacturing_cost=product.manufacturing_cost,
            units_per_box=product.units_per_box, quantity_boxes=1,
        )

    def test_payment_submission_does_not_change_paid_amount_until_admin_verifies(self):
        self.client.force_authenticate(self.wholesaler)
        response = self.client.post(
            "/api/payments/",
            {"order": self.order.pk, "amount": "40.00", "method": "UPI", "status": "VERIFIED"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], Payment.Status.PENDING)
        self.order.refresh_from_db()
        self.assertEqual(str(self.order.paid_amount), "0.00")

    def test_wholesaler_cannot_verify_payment_and_admin_verification_updates_due(self):
        payment = Payment.objects.create(
            order=self.order, submitted_by=self.wholesaler, amount="40.00", method="UPI"
        )
        self.client.force_authenticate(self.wholesaler)
        denied = self.client.post(
            f"/api/payments/{payment.pk}/verify/", {"verified": True}, format="json"
        )
        self.assertEqual(denied.status_code, 403)
        self.client.force_authenticate(self.admin)
        verified = self.client.post(
            f"/api/payments/{payment.pk}/verify/",
            {"verified": True, "verified_amount": "35.00"},
            format="json",
        )
        self.assertEqual(verified.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(str(self.order.paid_amount), "35.00")
