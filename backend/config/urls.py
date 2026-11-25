from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import LoginView, LogoutView, MeView, RegisterView
from catalog.views import CategoryViewSet, ProductViewSet
from credit.views import CreditEntryViewSet, CreditRequestViewSet, MyCreditFacilityView
from loyalty.views import LoyaltyAdjustmentView, LoyaltySettingsView, LoyaltyTransactionViewSet, MyLoyaltyView
from orders.views import OrderViewSet
from payments.views import PaymentViewSet
from returns.views import ReturnViewSet
from rewards.views import RedemptionViewSet, RewardItemViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("orders", OrderViewSet, basename="order")
router.register("payments", PaymentViewSet, basename="payment")
router.register("credit/requests", CreditRequestViewSet, basename="credit-request")
router.register("credit/entries", CreditEntryViewSet, basename="credit-entry")
router.register("rewards/items", RewardItemViewSet, basename="reward-item")
router.register("rewards/redemptions", RedemptionViewSet, basename="redemption")
router.register("returns", ReturnViewSet, basename="return")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/me/", MeView.as_view(), name="me"),
    path("api/credit/me/", MyCreditFacilityView.as_view(), name="my-credit"),
    path("api/loyalty/settings/", LoyaltySettingsView.as_view(), name="loyalty-settings"),
    path("api/loyalty/me/", MyLoyaltyView.as_view(), name="my-loyalty"),
    path("api/loyalty/adjustments/", LoyaltyAdjustmentView.as_view(), name="loyalty-adjustments"),
    path("api/loyalty/transactions/", LoyaltyTransactionViewSet.as_view(), name="loyalty-transactions"),
    path("api/", include(router.urls)),
]
