from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import User
from .models import CreditFacility, CreditRequest


class CreditApiTests(APITestCase):
    def setUp(self):
        self.wholesaler = User.objects.create_user(
            username="partner", email="partner@example.com", password="Strong-test-password-2026"
        )
        self.admin = User.objects.create_superuser(
            username="factory", email="factory@example.com", password="Strong-test-password-2026"
        )

    def test_credit_request_approval_creates_facility_with_separate_validity(self):
        self.client.force_authenticate(self.wholesaler)
        response = self.client.post(
            "/api/credit/requests/",
            {"requested_limit": "25000.00", "reason": "Growing our shop"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.client.force_authenticate(self.admin)
        today = timezone.localdate()
        decision = self.client.post(
            f"/api/credit/requests/{response.data['id']}/decide/",
            {
                "decision": "approve",
                "credit_limit": "20000.00",
                "payment_period_days": 30,
                "valid_from": today.isoformat(),
                "valid_until": (today + timedelta(days=90)).isoformat(),
            },
            format="json",
        )
        self.assertEqual(decision.status_code, 200)
        facility = CreditFacility.objects.get(wholesaler=self.wholesaler)
        self.assertEqual(str(facility.credit_limit), "20000.00")
        self.assertEqual(facility.payment_period_days, 30)
        self.assertEqual(decision.data["status"], CreditRequest.Status.APPROVED)

    def test_wholesaler_can_only_read_own_credit_requests(self):
        other = User.objects.create_user(
            username="other", email="other@example.com", password="Strong-test-password-2026"
        )
        CreditRequest.objects.create(wholesaler=other, requested_limit="1000.00")
        self.client.force_authenticate(self.wholesaler)
        response = self.client.get("/api/credit/requests/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
