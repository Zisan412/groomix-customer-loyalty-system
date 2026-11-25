import uuid

from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import IsFactoryAdmin, IsWholesaler, IsWholesalerOrAdmin
from .models import LoyaltySettings, LoyaltyTransaction
from .serializers import LoyaltyAdjustmentSerializer, LoyaltySettingsSerializer, LoyaltyTransactionSerializer
from .services import available_points


class LoyaltySettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = LoyaltySettingsSerializer

    def get_permissions(self):
        return [IsFactoryAdmin() if self.request.method in {"PUT", "PATCH"} else permissions.IsAuthenticated()]

    def get_object(self):
        return LoyaltySettings.current()


class MyLoyaltyView(generics.ListAPIView):
    serializer_class = LoyaltyTransactionSerializer
    permission_classes = [IsWholesaler]

    def get_queryset(self):
        available_points(self.request.user)
        return LoyaltyTransaction.objects.filter(user=self.request.user).select_related("order", "redemption")

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {
            "available_points": available_points(request.user),
            "transactions": response.data,
        }
        return response


class LoyaltyTransactionViewSet(generics.ListAPIView):
    serializer_class = LoyaltyTransactionSerializer

    def get_permissions(self):
        return [IsWholesalerOrAdmin()]

    def get_queryset(self):
        queryset = LoyaltyTransaction.objects.select_related("user", "order", "redemption")
        if not self.request.user.is_factory_admin:
            queryset = queryset.filter(user=self.request.user)
        wholesaler_id = self.request.query_params.get("wholesaler")
        if wholesaler_id and self.request.user.is_factory_admin:
            queryset = queryset.filter(user_id=wholesaler_id)
        return queryset


class LoyaltyAdjustmentView(APIView):
    permission_classes = [IsFactoryAdmin]

    def post(self, request):
        serializer = LoyaltyAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        with transaction.atomic():
            user = User.objects.select_for_update().get(pk=values["user"].pk)
            transaction_record = LoyaltyTransaction.objects.create(
                user=user,
                created_by=request.user,
                kind=LoyaltyTransaction.Kind.ADJUSTMENT,
                points=values["points"],
                description=values["description"],
                reference=f"admin-adjustment:{uuid.uuid4()}",
            )
        return Response(
            LoyaltyTransactionSerializer(transaction_record).data,
            status=status.HTTP_201_CREATED,
        )
