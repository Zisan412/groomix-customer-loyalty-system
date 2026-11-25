from django.db import transaction
from django.utils import timezone
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsFactoryAdmin, IsWholesaler, IsWholesalerOrAdmin
from .models import CreditEntry, CreditFacility, CreditRequest
from .serializers import CreditDecisionSerializer, CreditEntrySerializer, CreditFacilitySerializer, CreditRequestSerializer


class CreditRequestViewSet(viewsets.ModelViewSet):
    serializer_class = CreditRequestSerializer
    http_method_names = ["get", "post", "head", "options"]
    search_fields = ["wholesaler__business_name", "wholesaler__email"]
    ordering_fields = ["created_at", "requested_limit"]

    def get_queryset(self):
        queryset = CreditRequest.objects.select_related("wholesaler")
        if self.request.user.is_factory_admin:
            return queryset
        return queryset.filter(wholesaler=self.request.user)

    def get_permissions(self):
        if self.action == "decide":
            return [IsFactoryAdmin()]
        if self.action == "create":
            return [IsWholesaler()]
        return [IsWholesalerOrAdmin()]

    def perform_create(self, serializer):
        if CreditRequest.objects.filter(wholesaler=self.request.user, status=CreditRequest.Status.PENDING).exists():
            raise ValidationError({"detail": "You already have a pending credit request."})
        serializer.save(wholesaler=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsFactoryAdmin])
    def decide(self, request, pk=None):
        decision_data = CreditDecisionSerializer(data=request.data)
        decision_data.is_valid(raise_exception=True)
        values = decision_data.validated_data
        with transaction.atomic():
            credit_request = CreditRequest.objects.select_for_update().get(pk=pk)
            if credit_request.status != CreditRequest.Status.PENDING:
                raise ValidationError({"detail": "This request has already been decided."})
            credit_request.admin_note = values.get("admin_note", "")
            credit_request.decided_at = timezone.now()
            if values["decision"] == "reject":
                credit_request.status = CreditRequest.Status.REJECTED
            else:
                credit_request.status = CreditRequest.Status.APPROVED
                facility = CreditFacility.objects.select_for_update().filter(
                    wholesaler=credit_request.wholesaler
                ).first()
                if facility and values["credit_limit"] < facility.outstanding_balance:
                    raise ValidationError({
                        "credit_limit": "The limit cannot be lower than the current outstanding balance."
                    })
                if facility:
                    facility.credit_limit = values["credit_limit"]
                    facility.payment_period_days = values["payment_period_days"]
                    facility.valid_from = values["valid_from"]
                    facility.valid_until = values["valid_until"]
                    facility.is_active = True
                    facility.save()
                else:
                    CreditFacility.objects.create(
                        wholesaler=credit_request.wholesaler,
                        credit_limit=values["credit_limit"],
                        payment_period_days=values["payment_period_days"],
                        valid_from=values["valid_from"],
                        valid_until=values["valid_until"],
                    )
            credit_request.save(update_fields=["admin_note", "decided_at", "status"])
        return Response(self.get_serializer(credit_request).data)


class MyCreditFacilityView(generics.RetrieveAPIView):
    serializer_class = CreditFacilitySerializer
    permission_classes = [IsAuthenticated, IsWholesaler]

    def get_object(self):
        try:
            return self.request.user.credit_facility
        except CreditFacility.DoesNotExist as exc:
            raise ValidationError({"detail": "No approved credit facility is available."}) from exc


class CreditEntryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CreditEntrySerializer
    search_fields = ["facility__wholesaler__business_name", "order__id", "note"]
    ordering_fields = ["created_at", "amount"]

    def get_permissions(self):
        return [IsWholesalerOrAdmin()]

    def get_queryset(self):
        queryset = CreditEntry.objects.select_related("facility__wholesaler", "order")
        if not self.request.user.is_factory_admin:
            queryset = queryset.filter(facility__wholesaler=self.request.user)
        return queryset
