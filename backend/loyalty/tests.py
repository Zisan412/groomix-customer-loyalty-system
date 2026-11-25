from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import User
from loyalty.models import LoyaltyTransaction
from loyalty.services import available_points


class LoyaltyApiTests(APITestCase):
    def setUp(self):
        self.wholesaler = User.objects.create_user(
            username="partner", email="partner@example.com", password="Strong-test-password-2026"
        )
        self.admin = User.objects.create_superuser(
            username="factory", email="factory@example.com", password="Strong-test-password-2026"
        )

    def test_expiring_earned_points_do_not_consume_newer_points(self):
        now = timezone.now()
        LoyaltyTransaction.objects.create(
            user=self.wholesaler, kind=LoyaltyTransaction.Kind.EARNED, points=1000,
            description="Old award", expires_at=now - timedelta(days=1),
        )
        LoyaltyTransaction.objects.create(
            user=self.wholesaler, kind=LoyaltyTransaction.Kind.EARNED, points=500,
            description="New award", expires_at=now + timedelta(days=30),
        )
        LoyaltyTransaction.objects.create(
            user=self.wholesaler, kind=LoyaltyTransaction.Kind.REDEEMED, points=-1200,
            description="Prior redemption",
        )
        self.assertEqual(available_points(self.wholesaler), 300)
        self.assertFalse(
            LoyaltyTransaction.objects.filter(
                user=self.wholesaler,
                kind=LoyaltyTransaction.Kind.EXPIRED,
                reference=f"expiry:{LoyaltyTransaction.objects.filter(description='Old award').first().pk}",
            ).exists()
        )

    def test_admin_can_create_audited_adjustment_only_for_wholesalers(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/loyalty/adjustments/",
            {"user": self.wholesaler.pk, "points": 250, "description": "Goodwill adjustment"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        transaction_record = LoyaltyTransaction.objects.get(pk=response.data["id"])
        self.assertEqual(transaction_record.created_by, self.admin)
        self.assertEqual(transaction_record.kind, LoyaltyTransaction.Kind.ADJUSTMENT)

        self.client.force_authenticate(self.wholesaler)
        denied = self.client.post(
            "/api/loyalty/adjustments/",
            {"user": self.wholesaler.pk, "points": 250, "description": "Not allowed"},
            format="json",
        )
        self.assertEqual(denied.status_code, 403)
