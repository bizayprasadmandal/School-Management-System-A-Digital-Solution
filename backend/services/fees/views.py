"""
Fees Service — Views for invoicing, payments, scholarships
"""

import io

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db import transaction
from django.http import FileResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FeeCategory, FeeInvoice, FeeStructure, Payment, PaymentGatewayConfig, Scholarship
from .serializers import (
    FeeCategorySerializer,
    FeeInvoiceSerializer,
    FeeStructureSerializer,
    PaymentGatewayConfigSerializer,
    PaymentSerializer,
    ScholarshipSerializer,
)

BRAND_COLOR = colors.HexColor("#4F46E5")


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
        return FeeStructure.objects.filter(school=self.request.user.school).select_related(
            "grade", "fee_category", "academic_year"
        )

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
        qs = FeeInvoice.objects.filter(student__school=user.school).select_related(
            "student__user", "academic_year", "fee_structure__fee_category"
        )
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "parent":
            qs = qs.filter(student__guardians__user=user)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "bulk_generate", "waive", "import_csv"]:
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

    @action(detail=False, methods=["post"], url_path="import-csv")
    def import_csv(self, request):
        """
        Bulk-import fee invoices from CSV data.
        Expected CSV columns (header row required):
        admission_number, fee_category_name, due_date (YYYY-MM-DD),
        amount, discount_amount (optional), notes (optional)
        The fee structure is resolved by (academic_year, grade, category)
        from the student's active enrollment; missing structures are
        reported as row errors instead of being created implicitly.
        """
        import csv
        import io
        import uuid

        from services.students.models import AcademicYear

        from .models import FeeStructure

        csv_text = request.data.get("csv_data", "")
        if not csv_text:
            return Response({"error": "csv_data field is required."}, status=400)

        school = request.user.school
        current_year = AcademicYear.objects.filter(school=school, is_current=True).first()
        if not current_year:
            return Response({"error": "No current academic year set."}, status=400)

        reader = csv.DictReader(io.StringIO(csv_text))
        imported = 0
        errors = []
        invoice_numbers = []

        for row_num, row in enumerate(reader, start=2):
            admission_number = row.get("admission_number", "").strip()
            category_name = row.get("fee_category_name", "").strip()
            due_date = row.get("due_date", "").strip()
            amount_raw = row.get("amount", "").strip()

            if not all([admission_number, category_name, due_date, amount_raw]):
                errors.append(f"Row {row_num}: admission_number, fee_category_name, due_date and amount are required")
                continue

            from services.students.models import Student

            student = Student.objects.filter(school=school, admission_number=admission_number).first()
            if not student:
                errors.append(f"Row {row_num}: student with admission '{admission_number}' not found")
                continue

            enrollment = student.enrollments.filter(is_active=True).first()
            if not enrollment:
                errors.append(f"Row {row_num}: student '{admission_number}' has no active enrollment")
                continue

            structure = FeeStructure.objects.filter(
                school=school,
                academic_year=current_year,
                grade=enrollment.classroom.grade,
                fee_category__name=category_name,
            ).first()
            if not structure:
                errors.append(
                    f"Row {row_num}: no fee structure for category '{category_name}' "
                    f"in the current academic year for grade {enrollment.classroom.grade}"
                )
                continue

            try:
                from decimal import Decimal, InvalidOperation

                amount = Decimal(amount_raw)
                discount = Decimal(row.get("discount_amount", "0").strip() or "0")
                invoice_number = f"IMP{uuid.uuid4().hex[:8].upper()}"
                FeeInvoice.objects.create(
                    invoice_number=invoice_number,
                    student=student,
                    academic_year=current_year,
                    fee_structure=structure,
                    due_date=due_date,
                    base_amount=amount,
                    discount_amount=discount,
                    total_amount=amount - discount,
                    status=FeeInvoice.Status.UNPAID,
                    notes=row.get("notes", "").strip(),
                    created_by=request.user,
                )
                imported += 1
                invoice_numbers.append(invoice_number)
            except (InvalidOperation, ValueError):
                # Unparseable amounts or dates become per-row errors, never a 500.
                errors.append(f"Row {row_num}: invalid amount or date in row")
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)[:100]}")

        return Response({"imported": imported, "invoice_numbers": invoice_numbers, "errors": errors[:20]})

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

        # Tenant isolation: the fee structure must belong to the caller's
        # school, otherwise the queued task would generate invoices against a
        # foreign structure.
        if not FeeStructure.objects.filter(id=structure_id, school=request.user.school).exists():
            raise PermissionDenied("Fee structure not found in your school.")

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
        qs = Payment.objects.filter(invoice__student__school=user.school).select_related(
            "invoice__student__user", "collected_by"
        )
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

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Lock the invoice row to prevent race conditions on concurrent payments
        invoice = FeeInvoice.objects.select_for_update().get(id=serializer.validated_data["invoice"].id)

        payment = serializer.save(collected_by=request.user)

        # Update invoice paid_amount and status
        invoice.paid_amount += payment.amount
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = FeeInvoice.Status.PAID
        elif invoice.paid_amount > 0:
            invoice.status = FeeInvoice.Status.PARTIAL
        invoice.save(update_fields=["paid_amount", "status"])

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="receipt-pdf")
    def receipt_pdf(self, request, pk=None):
        """Generate and download a printable payment receipt PDF."""
        payment = self.get_object()
        school = payment.invoice.student.school
        student = payment.invoice.student
        invoice = payment.invoice

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Title"],
            textColor=BRAND_COLOR,
            fontSize=18,
            spaceAfter=6,
        )
        normal = styles["Normal"]

        elements = []
        elements.append(Paragraph("PAYMENT RECEIPT", title_style))
        elements.append(Paragraph(f"{school.name} — {school.address}", normal))
        elements.append(HRFlowable(width="100%", thickness=1, color=BRAND_COLOR, spaceAfter=12))

        details = [
            ["Receipt No.", payment.receipt_number],
            ["Invoice No.", invoice.invoice_number],
            ["Student", student.user.full_name],
            ["Admission No.", student.admission_number],
            ["Amount", f"${payment.amount:,.2f}"],
            ["Payment Method", payment.get_payment_method_display()],
            ["Date", payment.paid_at.strftime("%B %d, %Y, %H:%M %p") if payment.paid_at else "—"],
            ["Status", "Paid"],
        ]
        detail_table = Table(details, colWidths=[5 * cm, 10 * cm])
        detail_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(detail_table)
        elements.append(Spacer(1, 1 * cm))
        elements.append(
            Paragraph(
                f"Generated by EduSphere SMS on {timezone.now().strftime('%B %d, %Y')}",
                ParagraphStyle("Footer", parent=normal, fontSize=8, textColor=colors.grey),
            )
        )

        doc.build(elements)
        buffer.seek(0)

        response = FileResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="receipt_{payment.receipt_number}.pdf"'
        return response


class ScholarshipViewSet(viewsets.ModelViewSet):
    serializer_class = ScholarshipSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "academic_year", "is_active"]

    def get_queryset(self):
        return Scholarship.objects.filter(school=self.request.user.school).select_related(
            "student__user", "academic_year", "approved_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            approved_by=self.request.user,
        )


class GatewayConfigView(viewsets.ViewSet):
    """
    View for managing which payment gateways are enabled for the school.

    GET  /fees/gateway-config/       — get current config
    POST /fees/gateway-config/       — update config (admin only)
    GET  /fees/gateway-config/enabled/  — public list of enabled gateways
    """

    def get_config(self, request):
        """Get or create the config for the user's school."""
        config, _ = PaymentGatewayConfig.objects.get_or_create(school=request.user.school)
        return config

    def list(self, request):
        """GET /fees/gateway-config/ — return current config."""
        config = self.get_config(request)
        serializer = PaymentGatewayConfigSerializer(config)
        return Response(serializer.data)

    def create(self, request):
        """PUT /fees/gateway-config/ — update config (admin only).

        Uses POST for simplicity (API tooling doesn't always support PUT with forms).
        Method name 'create' maps to POST via DefaultRouter.
        """
        if request.user.role not in ("school_admin", "super_admin"):
            return Response({"detail": "Only school administrators can update gateway settings."}, status=403)

        config = self.get_config(request)
        serializer = PaymentGatewayConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def enabled(self, request):
        """
        GET /fees/gateway-config/enabled/
        Public endpoint — returns list of enabled gateways for the user's school.
        Used by the frontend to show/hide gateway options in the payment picker.
        """
        config, _ = PaymentGatewayConfig.objects.get_or_create(school=request.user.school)
        gateways = []
        if config.stripe_enabled:
            gateways.append(
                {
                    "id": "stripe",
                    "name": "Credit / Debit Card",
                    "description": "Visa, Mastercard, Amex via Stripe",
                    "icon": "💳",
                }
            )
        if config.khalti_enabled:
            gateways.append(
                {
                    "id": "khalti",
                    "name": "Khalti",
                    "description": "Khalti wallet, Mobile Banking, or Cards",
                    "icon": "💰",
                }
            )
        if config.esewa_enabled:
            gateways.append(
                {"id": "esewa", "name": "eSewa", "description": "eSewa wallet or connected bank accounts", "icon": "🏦"}
            )
        return Response(gateways)
