from rest_framework.test import APITestCase

from accounts.models import User
from loyalty.models import LoyaltyTransaction
from rewards.models import Redemption, RewardItem


class RewardsStoreApiTests(APITestCase):
    def setUp(self):
        self.wholesaler = User.objects.create_user(
            username="partner", email="partner@example.com", password="Strong-test-password-2026"
        )
        self.admin = User.objects.create_superuser(
            username="factory", email="factory@example.com", password="Strong-test-password-2026"
        )
        self.item = RewardItem.objects.create(name="Travel pouch", points_cost=1000, stock_quantity=5)
        LoyaltyTransaction.objects.create(
            user=self.wholesaler, kind=LoyaltyTransaction.Kind.EARNED, points=2000,
            description="Test reward points",
        )

    def test_rejection_releases_stock_and_refunds_points(self):
        self.client.force_authenticate(self.wholesaler)
        response = self.client.post(
            "/api/rewards/redemptions/",
            {"reward_item": self.item.pk, "shipping_address": "Pune"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        redemption = Redemption.objects.get(pk=response.data["id"])
        self.item.refresh_from_db()
        self.assertEqual(self.item.reserved_quantity, 1)

        self.client.force_authenticate(self.admin)
        rejected = self.client.post(
            f"/api/rewards/redemptions/{redemption.pk}/reject/",
            {"admin_note": "Out of stock check"},
            format="json",
        )
        self.assertEqual(rejected.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.reserved_quantity, 0)
        self.assertEqual(self.item.stock_quantity, 5)
        self.assertEqual(
            sum(LoyaltyTransaction.objects.filter(user=self.wholesaler).values_list("points", flat=True)),
            2000,
        )

    def test_insufficient_points_cannot_redeem(self):
        self.item.points_cost = 3000
        self.item.save()
        self.client.force_authenticate(self.wholesaler)
        response = self.client.post(
            "/api/rewards/redemptions/", {"reward_item": self.item.pk}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Redemption.objects.count(), 0)
