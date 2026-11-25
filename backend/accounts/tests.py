from rest_framework.test import APITestCase

from .models import User


class AccountApiTests(APITestCase):
    def test_registration_creates_wholesaler_but_never_admin(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "new@example.com",
                "password": "Strong-test-password-2026",
                "first_name": "New",
                "business_name": "New Shop",
                "role": "ADMIN",
                "is_superuser": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.role, User.Role.WHOLESALER)
        self.assertFalse(user.is_superuser)

    def test_email_login_and_profile(self):
        user = User.objects.create_user(
            username="partner@example.com",
            email="partner@example.com",
            password="Strong-test-password-2026",
            business_name="Partner Shop",
        )
        response = self.client.post(
            "/api/auth/login/",
            {"email": user.email, "password": "Strong-test-password-2026"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        profile = self.client.get("/api/auth/me/")
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.data["business_name"], "Partner Shop")

    def test_factory_admin_login_uses_superuser_account(self):
        admin = User.objects.create_superuser(
            username="factory",
            email="factory@example.com",
            password="Strong-test-password-2026",
        )
        response = self.client.post(
            "/api/auth/login/",
            {"email": admin.email, "password": "Strong-test-password-2026"},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["user"]["role"], User.Role.ADMIN)
