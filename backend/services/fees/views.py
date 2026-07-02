"""
Fees Service — Views for invoicing, payments, scholarships
"""

from decimal import Decimal
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import FeeCategory, FeeStructure, FeeInvoice, Payment, Scholarship
from .serializers import (
    FeeCategorySerializer, FeeStructureSerializer,
    FeeInvoiceSerializer, PaymentSerializer, ScholarshipSerializer,
)
from core.permissions import IsSchoolMember, IsSchoolAdmin
from core.pagination import StandardResultsSetPagination


class FeeCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = FeeCategorySerializer

    def get_queryset(self):
        return FeeCategory.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class FeeStructureViewSet(viewsets.ModelViewSet):
    serializer_class = FeeStructureSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["grade", "academic_year", "fee_category", "is_active"]

    def get_queryset(self):
        return FeeStructure.objects.filter(
            school=self.request.user.school
        ).select_related("grade", "fee_category", "academic_year")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class FeeInvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = FeeInvoiceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "student", "academic_year"]
    search_fields = ["invoice_number", "student__user__first_name", "student__user__last_name"]
    ordering_fields = ["due_date", "total_amount", "status"]
    ordering = ["-due_date"]

    def get_queryset(self):
        user = self.request.user
        qs = FeeInvoice.objects.filter(
            student__school=user.school
        ).select_related("student__user", "academic_year", "fee_structure__fee_category")
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "parent":
            qs = qs.filter(student__guardians__user=user)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy",
                           "bulk_generate", "waive"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def waive(self, request, pk=None):
        invoice = self.get_object()
        reason = request.data.get("reason", "")
        invoice.status = FeeInvoice.Status.WAIVED
        invoice.notes = f"Waived by {request.user.full_name}: {reason}"
        invoice.save(update_fields=["status", "notes"])
        return Response({"detail": "Invoice waived."})

    @action(detail=False, methods=["post"], url_path="bulk-generate")
    def bulk_generate(self, request):
        """Generate invoices for all students in a grade for a fee structure."""
        structure_id = request.data.get("fee_structure_id")
        academic_year_id = request.data.get("academic_year_id")

        if not structure_id or not academic_year_id:
            return Response(
                {"detail": "fee_structure_id and academic_year_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from .tasks import generate_bulk_invoices
        task = generate_bulk_invoices.delay(structure_id, academic_year_id)
        return Response(
            {"detail": "Bulk invoice generation queued.", "task_id": task.id},
            status=status.HTTP_202_ACCEPTED,
        )


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "payment_method", "invoice"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.filter(
            invoice__student__school=user.school
        ).select_related("invoice__student__user")
        if user.role in ["student", "parent"]:
            if user.role == "student":
                qs = qs.filter(invoice__student__user=user)
            else:
                qs = qs.filter(invoice__student__guardians__user=user)
        return qs

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(collected_by=request.user)

        # Update invoice paid_amount and status
        invoice = payment.invoice
        invoice.paid_amount += payment.amount
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = FeeInvoice.Status.PAID
        elif invoice.paid_amount > 0:
            invoice.status = FeeInvoice.Status.PARTIAL
        invoice.save(update_fields=["paid_amount", "status"])

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ScholarshipViewSet(viewsets.ModelViewSet):
    serializer_class = ScholarshipSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "academic_year", "is_active"]

    def get_queryset(self):
        return Scholarship.objects.filter(
            school=self.request.user.school
        ).select_related("student__user", "academic_year", "approved_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            approved_by=self.request.user,
        )
