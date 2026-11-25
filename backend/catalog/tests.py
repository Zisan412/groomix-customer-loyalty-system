from rest_framework.test import APITestCase

from accounts.models import User
from .models import Category, Product


class ProductApiTests(APITestCase):
    def setUp(self):
        self.wholesaler = User.objects.create_user(
            username="wholesaler", email="wholesaler@example.com", password="Strong-test-password-2026"
        )
        self.admin = User.objects.create_superuser(
            username="factory", email="factory@example.com", password="Strong-test-password-2026"
        )
        self.category = Category.objects.create(name="Hair Care")
        self.active_product = Product.objects.create(
            category=self.category, sku="HC-1", name="Shampoo", selling_price="120.00",
            manufacturing_cost="84.00", units_per_box=24, stock_boxes=10,
        )
        Product.objects.create(
            category=self.category, sku="HC-2", name="Hidden shampoo", selling_price="130.00",
            manufacturing_cost="90.00", units_per_box=24, stock_boxes=4, is_active=False,
        )

    def test_wholesaler_sees_active_products_and_box_pricing(self):
        self.client.force_authenticate(self.wholesaler)
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["units_per_box"], 24)

    def test_wholesaler_cannot_manage_catalog(self):
        self.client.force_authenticate(self.wholesaler)
        response = self.client.patch(
            f"/api/products/{self.active_product.pk}/",
            {"selling_price": "1.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_update_catalog(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            f"/api/products/{self.active_product.pk}/",
            {"selling_price": "125.00"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.active_product.refresh_from_db()
        self.assertEqual(str(self.active_product.selling_price), "125.00")
