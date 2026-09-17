"""
Fees Service — Views for invoicing, payments, scholarships
"""

import csv
import io
import uuid
from datetime import timedelta
from decimal import Decimal

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
from services.students.models import AcademicYear

from .models import (
    AccountingEntry,
    AdvancePayment,
    BankReconciliation,
    BudgetLineItem,
    BudgetPlan,
    BulkInvoiceGeneration,
    CreditNote,
    DebitNote,
    ExpenseTracking,
    FeeAdjustment,
    FeeCategory,
    FeeCollectionDashboard,
    FeeConcession,
    FeeDiscount,
    FeeExemption,
    FeeInvoice,
    FeeStructure,
    FeeTemplate,
    FeeWaiver,
    FeeWaiverApproval,
    FinancialAudit,
    FinancialYear,
    InstallmentPayment,
    InstallmentPlan,
    InvoiceTemplate,
    LateFeeRule,
    ParentAccount,
    Payment,
    PaymentGatewayConfig,
    PaymentMethod,
    PaymentReconciliation,
    PaymentReminder,
    ReceiptTemplate,
    RefundRecord,
    RevenueReport,
    Scholarship,
    SiblingDiscount,
    StudentFinancialAccount,
    StudentLedger,
    TransactionLog,
)
from .serializers import (
    AccountingEntrySerializer,
    AdvancePaymentSerializer,
    BankReconciliationSerializer,
    BudgetLineItemSerializer,
    BudgetPlanSerializer,
    BulkInvoiceGenerationSerializer,
    CreditNoteSerializer,
    DebitNoteSerializer,
    ExpenseTrackingSerializer,
    FeeAdjustmentSerializer,
    FeeCategorySerializer,
    FeeCollectionDashboardSerializer,
    FeeConcessionSerializer,
    FeeDiscountSerializer,
    FeeExemptionSerializer,
    FeeInvoiceSerializer,
    FeeStructureSerializer,
    FeeTemplateSerializer,
    FeeWaiverApprovalSerializer,
    FeeWaiverSerializer,
    FinancialAuditSerializer,
    FinancialYearSerializer,
    InstallmentPaymentSerializer,
    InstallmentPlanSerializer,
    InvoiceTemplateSerializer,
    LateFeeRuleSerializer,
    ParentAccountSerializer,
    PaymentGatewayConfigSerializer,
    PaymentMethodSerializer,
    PaymentReconciliationSerializer,
    PaymentReminderSerializer,
    PaymentSerializer,
    ReceiptTemplateSerializer,
    RefundRecordSerializer,
    RevenueReportSerializer,
    ScholarshipSerializer,
    SiblingDiscountSerializer,
    StudentFinancialAccountSerializer,
    StudentLedgerSerializer,
    TransactionLogSerializer,
)

BRAND_COLOR = colors.HexColor("#4F46E5")


class FeeCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = FeeCategorySerializer

    def get_queryset(self):
        return FeeCategory.objects.filter(school=self.request.user.school).order_by("name")

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
        return (
            FeeStructure.objects.filter(school=self.request.user.school)
            .order_by("id")
            .select_related("grade", "fee_category", "academic_year")
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
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "student", "academic_year"]
    search_fields = [
        "invoice_number",
        "student__user__first_name",
        "student__user__last_name",
    ]
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
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "bulk_generate",
            "waive",
            "import_csv",
        ]:
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

    @action(detail=True, methods=["get"], url_path="invoice-pdf")
    def invoice_pdf(self, request, pk=None):
        """Generate and download a printable invoice PDF using InvoiceTemplate."""
        invoice = self.get_object()
        school = invoice.student.school
        student = invoice.student

        # Fetch the default invoice template for this school
        from .models import InvoiceTemplate

        template = (
            InvoiceTemplate.objects.filter(school=school, is_default=True, is_active=True).first()
            or InvoiceTemplate.objects.filter(school=school, is_active=True).first()
        )

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
        small_style = ParagraphStyle(
            "Small",
            parent=normal,
            fontSize=8,
            textColor=colors.grey,
        )

        elements = []

        # Header text from template
        if template and template.header_text:
            elements.append(Paragraph(template.header_text, small_style))
            elements.append(Spacer(1, 4))

        elements.append(Paragraph("FEE INVOICE", title_style))
        elements.append(Paragraph(f"{school.name} — {school.address}", normal))
        elements.append(HRFlowable(width="100%", thickness=1, color=BRAND_COLOR, spaceAfter=12))

        details = [
            ["Invoice No.", invoice.invoice_number],
            ["Student", student.user.full_name],
            ["Admission No.", student.admission_number],
            ["Grade", student.classroom.grade.name if student.classroom and student.classroom.grade else "—"],
            ["Due Date", invoice.due_date.strftime("%B %d, %Y") if invoice.due_date else "—"],
            ["Base Amount", f"Rs. {invoice.base_amount:,.2f}"],
            ["Discount", f"Rs. {invoice.discount_amount:,.2f}"],
            ["Late Fee", f"Rs. {invoice.late_fee:,.2f}"],
            ["Total Amount", f"Rs. {invoice.total_amount:,.2f}"],
            ["Paid Amount", f"Rs. {invoice.paid_amount:,.2f}"],
            ["Outstanding", f"Rs. {invoice.outstanding_amount:,.2f}"],
            ["Status", invoice.get_status_display()],
        ]
        detail_table = Table(details, colWidths=[5 * cm, 10 * cm])
        detail_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    (
                        "ROWBACKGROUNDS",
                        (0, 0),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f8fafc")],
                    ),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(detail_table)
        elements.append(Spacer(1, 1 * cm))

        # Terms and conditions from template
        if template and template.terms_and_conditions:
            elements.append(
                Paragraph(
                    "Terms & Conditions",
                    ParagraphStyle(
                        "TCHeader",
                        parent=normal,
                        fontSize=10,
                        fontName="Helvetica-Bold",
                        spaceAfter=4,
                    ),
                )
            )
            elements.append(Paragraph(template.terms_and_conditions, small_style))
            elements.append(Spacer(1, 0.5 * cm))

        # Footer text from template
        footer_text = (
            template.footer_text
            if template and template.footer_text
            else f"Generated by EduSphere SMS on {timezone.now().strftime('%B %d, %Y')}"
        )
        elements.append(Paragraph(footer_text, small_style))

        doc.build(elements)
        buffer.seek(0)

        response = FileResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
        return response

    @action(detail=False, methods=["get"], url_path="aging-report")
    def aging_report(self, request):
        """
        Generate an overdue invoice aging report with buckets:
        0-30 days, 31-60 days, 61-90 days, 90+ days.

        Query params:
            academic_year (optional) — filter by academic year ID
        """
        from django.db.models import DateField, ExpressionWrapper, F
        from django.db.models.functions import Greatest

        today = timezone.now().date()
        qs = FeeInvoice.objects.filter(
            student__school=request.user.school,
            status__in=["unpaid", "overdue", "partial"],
            due_date__lt=today,
        ).select_related("student__user", "student__classroom__grade")

        academic_year = request.query_params.get("academic_year")
        if academic_year:
            qs = qs.filter(academic_year_id=academic_year)

        # Annotate days overdue
        qs = qs.annotate(
            days_overdue_expr=Greatest(
                ExpressionWrapper(
                    today - F("due_date"),
                    output_field=DateField(),
                ),
                0,
            )
        )

        # Build aging buckets
        buckets = {
            "0-30": {"label": "0-30 days", "count": 0, "total": 0, "invoices": []},
            "31-60": {"label": "31-60 days", "count": 0, "total": 0, "invoices": []},
            "61-90": {"label": "61-90 days", "count": 0, "total": 0, "invoices": []},
            "90+": {"label": "90+ days", "count": 0, "total": 0, "invoices": []},
        }

        for inv in qs:
            days = inv.days_overdue_expr.days if inv.days_overdue_expr else 0
            outstanding = float(inv.total_amount - inv.paid_amount)
            student_name = inv.student.user.full_name

            invoice_data = {
                "id": str(inv.id),
                "invoice_number": inv.invoice_number,
                "student_name": student_name,
                "grade": (
                    inv.student.classroom.grade.name if inv.student.classroom and inv.student.classroom.grade else "—"
                ),
                "total_amount": float(inv.total_amount),
                "paid_amount": float(inv.paid_amount),
                "outstanding_amount": outstanding,
                "due_date": inv.due_date.isoformat(),
                "days_overdue": days,
                "status": inv.status,
            }

            if days <= 30:
                bucket_key = "0-30"
            elif days <= 60:
                bucket_key = "31-60"
            elif days <= 90:
                bucket_key = "61-90"
            else:
                bucket_key = "90+"

            buckets[bucket_key]["count"] += 1
            buckets[bucket_key]["total"] += outstanding
            buckets[bucket_key]["invoices"].append(invoice_data)

        # Summary
        total_overdue_count = sum(b["count"] for b in buckets.values())
        total_overdue_amount = sum(b["total"] for b in buckets.values())

        return Response(
            {
                "summary": {
                    "total_overdue_count": total_overdue_count,
                    "total_overdue_amount": total_overdue_amount,
                    "as_of_date": today.isoformat(),
                },
                "buckets": {
                    k: {
                        "label": v["label"],
                        "count": v["count"],
                        "total": v["total"],
                        "invoices": sorted(v["invoices"], key=lambda x: -x["days_overdue"]),
                    }
                    for k, v in buckets.items()
                },
            }
        )

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

        return Response(
            {
                "imported": imported,
                "invoice_numbers": invoice_numbers,
                "errors": errors[:20],
            }
        )

    @action(detail=False, methods=["post"], url_path="bulk-generate")
    def bulk_generate(self, request):
        """Generate invoices for all students in a grade for a fee structure."""
        from services.students.models import AcademicYear

        structure_id = request.data.get("fee_structure_id")
        academic_year_id = request.data.get("academic_year_id")

        if not structure_id or not academic_year_id:
            return Response(
                {"detail": "fee_structure_id and academic_year_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Tenant isolation: the fee structure AND the academic year must belong
        # to the caller's school, otherwise the queued task would generate
        # invoices against a foreign structure or a foreign academic year
        # (cross-tenant write on the money path).
        if not FeeStructure.objects.filter(id=structure_id, school=request.user.school).exists():
            raise PermissionDenied("Fee structure not found in your school.")
        if not AcademicYear.objects.filter(id=academic_year_id, school=request.user.school).exists():
            raise PermissionDenied("Academic year not found in your school.")

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

        # Tenant scoping — payments may only be recorded against invoices in the caller's school
        if invoice.student.school_id != request.user.school_id:
            return Response(
                {"detail": "Invoice does not belong to your school."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Overpayments are not allowed — cap the amount at the outstanding balance
        outstanding = invoice.total_amount - invoice.paid_amount
        if serializer.validated_data["amount"] > outstanding:
            return Response(
                {"detail": (f"Payment amount exceeds the outstanding balance of " f"{outstanding} on this invoice.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = serializer.save(collected_by=request.user)

        from .ledger import credit_invoice

        invoice = credit_invoice(invoice, payment.amount, payment=payment, user=request.user)

        # Dispatch receipt notification for successful cash/manual payments
        if payment.status == Payment.Status.SUCCESSFUL:
            from .tasks import send_payment_receipt_notification

            send_payment_receipt_notification.delay(str(payment.id))

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="receipt-pdf")
    def receipt_pdf(self, request, pk=None):
        """Generate and download a printable payment receipt PDF using ReceiptTemplate."""
        payment = self.get_object()
        school = payment.invoice.student.school
        student = payment.invoice.student
        invoice = payment.invoice

        # Fetch the default receipt template for this school
        from .models import ReceiptTemplate

        template = (
            ReceiptTemplate.objects.filter(school=school, is_default=True, is_active=True).first()
            or ReceiptTemplate.objects.filter(school=school, is_active=True).first()
        )

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
        small_style = ParagraphStyle(
            "Small",
            parent=normal,
            fontSize=8,
            textColor=colors.grey,
        )

        elements = []

        # Header text from template
        if template and template.header_text:
            elements.append(Paragraph(template.header_text, small_style))
            elements.append(Spacer(1, 4))

        elements.append(Paragraph("PAYMENT RECEIPT", title_style))
        elements.append(Paragraph(f"{school.name} — {school.address}", normal))
        elements.append(HRFlowable(width="100%", thickness=1, color=BRAND_COLOR, spaceAfter=12))

        details = [
            ["Receipt No.", payment.receipt_number],
            ["Invoice No.", invoice.invoice_number],
            ["Student", student.user.full_name],
            ["Admission No.", student.admission_number],
            ["Amount", f"Rs. {payment.amount:,.2f}"],
            ["Payment Method", payment.get_payment_method_display()],
            [
                "Date",
                (payment.paid_at.strftime("%B %d, %Y, %H:%M %p") if payment.paid_at else "—"),
            ],
            ["Status", "Paid"],
        ]
        detail_table = Table(details, colWidths=[5 * cm, 10 * cm])
        detail_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    (
                        "ROWBACKGROUNDS",
                        (0, 0),
                        (-1, -1),
                        [colors.white, colors.HexColor("#f8fafc")],
                    ),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(detail_table)
        elements.append(Spacer(1, 1 * cm))

        # Footer text from template
        footer_text = (
            template.footer_text
            if template and template.footer_text
            else f"Generated by EduSphere SMS on {timezone.now().strftime('%B %d, %Y')}"
        )
        elements.append(Paragraph(footer_text, small_style))

        doc.build(elements)
        buffer.seek(0)

        response = FileResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="receipt_{payment.receipt_number}.pdf"'
        return response

    @action(detail=False, methods=["post"], url_path="batch")
    def batch_create(self, request):
        """
        Create multiple payments at once for cash/bank collections.

        Accepts:
            payments: [
                {
                    "invoice": "<uuid>",
                    "amount": 5000.00,
                    "payment_method": "cash",
                    "notes": "optional"
                },
                ...
            ]

        Returns:
            { created: [...], errors: [...] }
        """
        payments_data = request.data.get("payments", [])
        if not payments_data:
            return Response(
                {"detail": "No payments provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created = []
        errors = []

        for idx, payment_data in enumerate(payments_data):
            invoice_id = payment_data.get("invoice")
            amount = payment_data.get("amount")
            payment_method = payment_data.get("payment_method", "cash")
            notes = payment_data.get("notes", "")

            if not invoice_id or not amount:
                errors.append({"index": idx, "error": "invoice and amount are required"})
                continue

            try:
                with transaction.atomic():
                    invoice = FeeInvoice.objects.select_for_update().get(id=invoice_id)

                    # Tenant check
                    if invoice.student.school_id != request.user.school_id:
                        errors.append({"index": idx, "invoice": invoice_id, "error": "Wrong school"})
                        continue

                    # Check outstanding
                    outstanding = invoice.total_amount - invoice.paid_amount
                    if Decimal(str(amount)) > outstanding:
                        errors.append(
                            {
                                "index": idx,
                                "invoice": invoice_id,
                                "error": f"Amount {amount} exceeds outstanding {outstanding}",
                            }
                        )
                        continue

                    payment = Payment.objects.create(
                        invoice=invoice,
                        amount=Decimal(str(amount)),
                        payment_method=payment_method,
                        status=Payment.Status.SUCCESSFUL,
                        paid_at=timezone.now(),
                        collected_by=request.user,
                        notes=notes,
                    )

                    from .ledger import credit_invoice

                    credit_invoice(invoice, payment.amount, payment=payment, user=request.user)

                    created.append(
                        {
                            "id": str(payment.id),
                            "receipt_number": payment.receipt_number,
                            "invoice_number": invoice.invoice_number,
                            "amount": str(payment.amount),
                        }
                    )

            except FeeInvoice.DoesNotExist:
                errors.append({"index": idx, "invoice": invoice_id, "error": "Invoice not found"})
            except Exception as e:
                errors.append({"index": idx, "invoice": invoice_id, "error": str(e)})

        # Dispatch receipt notifications for all successful payments
        if created:
            from .tasks import send_payment_receipt_notification

            for p in created:
                send_payment_receipt_notification.delay(p["id"])

        return Response(
            {"created": created, "errors": errors, "total_created": len(created), "total_errors": len(errors)},
            status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=["post"])
    def void(self, request, pk=None):
        """
        Void/cancel a pending payment. Only payments with status=pending can be voided.
        Successful payments cannot be voided — use refund instead.
        """
        payment = self.get_object()

        if payment.status != Payment.Status.PENDING:
            return Response(
                {
                    "detail": (
                        f"Cannot void a payment with status '{payment.status}'. " "Use refund for successful payments."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            locked = Payment.objects.select_for_update().get(pk=payment.pk)
            if locked.status != Payment.Status.PENDING:
                return Response(
                    {"detail": "Payment was modified by another request."},
                    status=status.HTTP_409_CONFLICT,
                )

            locked.status = Payment.Status.FAILED
            locked.notes = f"Voided by {request.user.full_name}: {request.data.get('reason', 'No reason provided')}"
            locked.save(update_fields=["status", "notes"])

            # Audit trail: record the void as a failed transaction so finance
            # has a permanent record of who voided what and why.
            TransactionLog.objects.get_or_create(
                transaction_id=f"VOID-{locked.id}",
                defaults={
                    "school_id": locked.invoice.student.school_id,
                    "student_id": locked.invoice.student_id,
                    "transaction_type": TransactionLog.TransactionType.OTHER,
                    "amount": locked.amount,
                    "payment_method": locked.payment_method,
                    "reference_number": locked.receipt_number,
                    "status": "failed",
                    "description": (
                        f"Payment {locked.receipt_number} voided by "
                        f"{request.user.full_name}: "
                        f"{request.data.get('reason', 'No reason provided')}"
                    ),
                    "metadata": {"payment_id": str(locked.id), "action": "void"},
                },
            )

        return Response({"detail": "Payment voided successfully.", "payment_id": str(payment.id)})


class ScholarshipViewSet(viewsets.ModelViewSet):
    serializer_class = ScholarshipSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "academic_year", "is_active"]

    def get_queryset(self):
        return (
            Scholarship.objects.filter(school=self.request.user.school)
            .order_by("name")
            .select_related("student__user", "academic_year", "approved_by")
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
            return Response(
                {"detail": "Only school administrators can update gateway settings."},
                status=403,
            )

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
                {
                    "id": "esewa",
                    "name": "eSewa",
                    "description": "eSewa wallet or connected bank accounts",
                    "icon": "🏦",
                }
            )
        return Response(gateways)


# =============================================================================
# Installment Plans ViewSets
# =============================================================================


class InstallmentPlanViewSet(viewsets.ModelViewSet):
    serializer_class = InstallmentPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    filterset_fields = ["student", "status", "invoice"]

    def get_queryset(self):
        return InstallmentPlan.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, approved_by=self.request.user)


class InstallmentPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = InstallmentPaymentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["installment_plan", "status"]

    def get_queryset(self):
        return InstallmentPayment.objects.filter(installment_plan__school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Sibling Discounts ViewSets
# =============================================================================


class SiblingDiscountViewSet(viewsets.ModelViewSet):
    serializer_class = SiblingDiscountSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["is_active", "discount_type"]

    def get_queryset(self):
        return SiblingDiscount.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Payment Reminders ViewSets
# =============================================================================


class PaymentReminderViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentReminderSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    filterset_fields = ["student", "reminder_type", "status", "invoice"]

    def get_queryset(self):
        return PaymentReminder.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Fee Concessions ViewSets
# =============================================================================


class FeeConcessionViewSet(viewsets.ModelViewSet):
    serializer_class = FeeConcessionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "name"]
    filterset_fields = ["student", "concession_type", "status", "academic_year"]

    def get_queryset(self):
        return FeeConcession.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Revenue Reports ViewSets
# =============================================================================


class RevenueReportViewSet(viewsets.ModelViewSet):
    serializer_class = RevenueReportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "summary"]
    filterset_fields = ["report_type", "status"]

    def get_queryset(self):
        return RevenueReport.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, generated_by=self.request.user)


# =============================================================================
# Fee Collection Dashboard ViewSets
# =============================================================================


class FeeCollectionDashboardViewSet(viewsets.ModelViewSet):
    serializer_class = FeeCollectionDashboardSerializer
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        return FeeCollectionDashboard.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=False, methods=["get"], url_path="realtime")
    def realtime(self, request):
        """
        Compute live fee collection stats for the current academic year.
        Returns real-time data without relying on the snapshot model.
        """
        from django.db.models import Count, Q, Sum
        from services.students.models import AcademicYear, Enrollment

        school = request.user.school
        academic_year = AcademicYear.objects.filter(school=school, is_current=True).first()

        if not academic_year:
            return Response(
                {
                    "error": "No current academic year set",
                    "total_expected": 0,
                    "total_collected": 0,
                    "total_outstanding": 0,
                    "collection_percentage": 0,
                    "total_invoices": 0,
                    "paid_invoices": 0,
                    "unpaid_invoices": 0,
                    "overdue_invoices": 0,
                    "partial_invoices": 0,
                    "total_students": 0,
                    "total_defaulters": 0,
                    "overdue_amount": 0,
                    "by_status": [],
                    "by_category": [],
                    "by_grade": [],
                    "by_payment_method": [],
                    "daily_collection": [],
                    "recent_payments": [],
                }
            )

        today = timezone.now().date()

        # Aggregate invoice stats
        invoice_stats = FeeInvoice.objects.filter(
            student__school=school,
            academic_year=academic_year,
        ).aggregate(
            total_expected=Sum("total_amount"),
            total_collected=Sum("paid_amount"),
            total_invoices=Count("id"),
            paid_invoices=Count("id", filter=Q(status="paid")),
            unpaid_invoices=Count("id", filter=Q(status="unpaid")),
            overdue_invoices=Count("id", filter=Q(status="overdue")),
            partial_invoices=Count("id", filter=Q(status="partial")),
        )

        total_expected = invoice_stats["total_expected"] or 0
        total_collected = invoice_stats["total_collected"] or 0
        total_outstanding = total_expected - total_collected

        # Count defaulters (students with any unpaid/overdue/partial invoice)
        defaulter_ids = (
            FeeInvoice.objects.filter(
                student__school=school,
                academic_year=academic_year,
                status__in=["unpaid", "overdue", "partial"],
            )
            .values_list("student_id", flat=True)
            .distinct()
        )
        total_defaulters = len(list(defaulter_ids))

        # Overdue amount
        overdue_amount = (
            FeeInvoice.objects.filter(
                student__school=school,
                academic_year=academic_year,
                status__in=["unpaid", "overdue", "partial"],
                due_date__lt=today,
            ).aggregate(total=Sum("total_amount"))["total"]
            or 0
        )

        # Stats by status
        by_status = list(
            FeeInvoice.objects.filter(
                student__school=school,
                academic_year=academic_year,
            )
            .values("status")
            .annotate(total=Sum("total_amount"), count=Count("id"))
            .order_by("status")
        )

        # Stats by category
        by_category = list(
            FeeInvoice.objects.filter(
                student__school=school,
                academic_year=academic_year,
            )
            .values("fee_structure__fee_category__name")
            .annotate(
                total=Sum("total_amount"),
                collected=Sum("paid_amount"),
                count=Count("id"),
            )
            .order_by("-total")
        )

        # Stats by grade
        by_grade = list(
            FeeInvoice.objects.filter(
                student__school=school,
                academic_year=academic_year,
            )
            .values("student__classroom__grade__name")
            .annotate(
                total=Sum("total_amount"),
                collected=Sum("paid_amount"),
                count=Count("id"),
            )
            .order_by("-total")
        )

        # Stats by payment method
        by_payment_method = list(
            Payment.objects.filter(
                invoice__student__school=school,
                invoice__academic_year=academic_year,
                status="successful",
            )
            .values("payment_method")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
        )

        # Last 30 days collection
        daily_collection = []
        for i in range(29, -1, -1):
            day = today - timedelta(days=i)
            day_total = (
                Payment.objects.filter(
                    invoice__student__school=school,
                    invoice__academic_year=academic_year,
                    status="successful",
                    paid_at__date=day,
                ).aggregate(total=Sum("amount"))["total"]
                or 0
            )
            daily_collection.append(
                {
                    "date": day.isoformat(),
                    "collected": float(day_total),
                }
            )

        # Recent payments
        recent_payments = list(
            Payment.objects.filter(
                invoice__student__school=school,
                status="successful",
            )
            .select_related("invoice__student__user")
            .order_by("-paid_at")[:10]
            .values(
                "id",
                "receipt_number",
                "amount",
                "payment_method",
                "status",
                "paid_at",
                "invoice__invoice_number",
                "invoice__student__user__first_name",
                "invoice__student__user__last_name",
            )
        )

        # Format recent payments
        for p in recent_payments:
            p["invoice_number"] = p.pop("invoice__invoice_number")
            first = p.pop("invoice__student__user__first_name", "")
            last = p.pop("invoice__student__user__last_name", "")
            p["student_name"] = f"{first} {last}".strip()
            p["id"] = str(p["id"])

        collection_pct = (total_collected / total_expected * 100) if total_expected > 0 else 0

        return Response(
            {
                "total_expected": float(total_expected),
                "total_collected": float(total_collected),
                "total_outstanding": float(total_outstanding),
                "collection_percentage": round(collection_pct, 2),
                "total_invoices": invoice_stats["total_invoices"],
                "paid_invoices": invoice_stats["paid_invoices"],
                "unpaid_invoices": invoice_stats["unpaid_invoices"],
                "overdue_invoices": invoice_stats["overdue_invoices"],
                "partial_invoices": invoice_stats["partial_invoices"],
                "total_students": Enrollment.objects.filter(
                    classroom__school=school,
                    academic_year=academic_year,
                    is_active=True,
                ).count(),
                "total_defaulters": total_defaulters,
                "overdue_amount": float(overdue_amount),
                "by_status": by_status,
                "by_category": [
                    {
                        "category": c["fee_structure__fee_category__name"] or "Unknown",
                        "total": float(c["total"] or 0),
                        "collected": float(c["collected"] or 0),
                        "count": c["count"],
                    }
                    for c in by_category
                ],
                "by_grade": [
                    {
                        "grade": g["student__classroom__grade__name"] or "Unknown",
                        "total": float(g["total"] or 0),
                        "collected": float(g["collected"] or 0),
                        "count": g["count"],
                    }
                    for g in by_grade
                ],
                "by_payment_method": [
                    {
                        "method": m["payment_method"],
                        "total": float(m["total"] or 0),
                        "count": m["count"],
                    }
                    for m in by_payment_method
                ],
                "daily_collection": daily_collection,
                "recent_payments": recent_payments,
            }
        )


# =============================================================================
# Fee Adjustments ViewSets
# =============================================================================


class FeeAdjustmentViewSet(viewsets.ModelViewSet):
    serializer_class = FeeAdjustmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "description",
    ]
    filterset_fields = ["student", "adjustment_type", "invoice"]

    def get_queryset(self):
        return FeeAdjustment.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


# =============================================================================
# Advance Payments ViewSets
# =============================================================================


class AdvancePaymentViewSet(viewsets.ModelViewSet):
    serializer_class = AdvancePaymentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    filterset_fields = ["student", "status"]

    def get_queryset(self):
        return AdvancePayment.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Fee Waivers ViewSets
# =============================================================================


class FeeWaiverViewSet(viewsets.ModelViewSet):
    serializer_class = FeeWaiverSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["student__user__first_name", "student__user__last_name", "reason"]
    filterset_fields = ["student", "waiver_type", "status", "academic_year"]

    def get_queryset(self):
        return FeeWaiver.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Student Ledger ViewSets
# =============================================================================


class StudentLedgerViewSet(viewsets.ModelViewSet):
    serializer_class = StudentLedgerSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "reference_number",
    ]
    filterset_fields = ["student", "transaction_type", "academic_year"]

    def get_queryset(self):
        user = self.request.user
        qs = StudentLedger.objects.filter(school=user.school)
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "parent":
            qs = qs.filter(student__guardians__user=user)
        return qs

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Fee Templates ViewSets
# =============================================================================


class FeeTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = FeeTemplateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "description"]
    filterset_fields = ["template_type", "recurrence", "is_active"]

    def get_queryset(self):
        return FeeTemplate.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


# =============================================================================
# Bulk Invoice Generation ViewSets
# =============================================================================


class BulkInvoiceGenerationViewSet(viewsets.ModelViewSet):
    serializer_class = BulkInvoiceGenerationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["batch_name", "description"]
    filterset_fields = ["status", "academic_year"]

    def get_queryset(self):
        return BulkInvoiceGeneration.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, initiated_by=self.request.user)


# =============================================================================
# Payment Reconciliation ViewSets
# =============================================================================


class PaymentReconciliationViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentReconciliationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["notes"]
    filterset_fields = ["reconciliation_type", "status"]

    def get_queryset(self):
        return PaymentReconciliation.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, initiated_by=self.request.user)


# ── Additional ViewSets (module expansion) ──


class PaymentGatewayConfigViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentGatewayConfigSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return PaymentGatewayConfig.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BudgetPlanViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return BudgetPlan.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=True, methods=["get"], url_path="variance")
    def variance(self, request, pk=None):
        """
        Budget-vs-actual variance report for one budget plan.

        Actuals per line item:
        - Line items linked to a fee category are computed from approved/paid
          ExpenseTracking rows in that category within the plan's academic
          year (pending expenses are not counted as spent).
        - Line items without a category use their stored ``actual_amount``.

        Variance = budgeted − actual (positive means under budget). The
        report is computed on read; nothing is persisted.
        """
        from django.db.models import Sum

        plan = self.get_object()
        year = plan.academic_year
        line_items = list(plan.line_items.select_related("category"))

        # Approved/paid expenses grouped by category within the academic year.
        expenses_by_category: dict[int, Decimal] = {}
        if year and year.start_date and year.end_date:
            expense_rows = (
                ExpenseTracking.objects.filter(
                    school=plan.school,
                    category__isnull=False,
                    expense_date__gte=year.start_date,
                    expense_date__lte=year.end_date,
                    status__in=["approved", "paid"],
                )
                .values("category_id")
                .annotate(total=Sum("amount"))
            )
            expenses_by_category = {row["category_id"]: row["total"] for row in expense_rows}

        line_reports = []
        total_budgeted = Decimal("0")
        total_actual = Decimal("0")
        over_budget_lines = 0

        for item in line_items:
            if item.category_id and item.category_id in expenses_by_category:
                actual = expenses_by_category[item.category_id]
                source = "expenses"
            else:
                actual = item.actual_amount
                source = "manual"
            budgeted = item.budgeted_amount
            variance = budgeted - actual
            utilization = float(actual / budgeted * 100) if budgeted > 0 else 0.0
            if variance < 0:
                over_budget_lines += 1

            total_budgeted += budgeted
            total_actual += actual
            line_reports.append(
                {
                    "id": str(item.id),
                    "description": item.description,
                    "category": item.category.name if item.category else None,
                    "budgeted_amount": str(budgeted),
                    "actual_amount": str(actual),
                    "variance": str(variance),
                    "utilization_pct": round(utilization, 1),
                    "over_budget": variance < 0,
                    "source": source,
                }
            )

        total_variance = total_budgeted - total_actual
        plan_utilization = float(total_actual / total_budgeted * 100) if total_budgeted > 0 else 0.0

        return Response(
            {
                "plan": {
                    "id": str(plan.id),
                    "title": plan.title,
                    "status": plan.status,
                    "academic_year": year.name if year else None,
                    "total_budget": str(plan.total_budget),
                    "allocated": str(sum(i.budgeted_amount for i in line_items)),
                    "spent": str(total_actual),
                    "remaining": str(plan.total_budget - total_actual),
                },
                "line_items": line_reports,
                "summary": {
                    "total_budgeted": str(total_budgeted),
                    "total_actual": str(total_actual),
                    "total_variance": str(total_variance),
                    "utilization_pct": round(plan_utilization, 1),
                    "line_count": len(line_reports),
                    "over_budget_lines": over_budget_lines,
                },
            }
        )


class BudgetLineItemViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetLineItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return BudgetLineItem.objects.filter(budget_plan__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class ExpenseTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ExpenseTracking.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RefundRecordViewSet(viewsets.ModelViewSet):
    serializer_class = RefundRecordSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return RefundRecord.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class LateFeeRuleViewSet(viewsets.ModelViewSet):
    serializer_class = LateFeeRuleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return LateFeeRule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class FeeDiscountViewSet(viewsets.ModelViewSet):
    serializer_class = FeeDiscountSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return FeeDiscount.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class FeeExemptionViewSet(viewsets.ModelViewSet):
    serializer_class = FeeExemptionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return FeeExemption.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InvoiceTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceTemplateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InvoiceTemplate.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ReceiptTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptTemplateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ReceiptTemplate.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AccountingEntryViewSet(viewsets.ModelViewSet):
    serializer_class = AccountingEntrySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["description", "account_name", "account_code", "reference_type", "reference_id"]
    filterset_fields = ["school", "entry_type", "account_code", "reference_type"]

    def get_queryset(self):
        return AccountingEntry.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=False, methods=["get"])
    def monthly_summary(self, request):
        """Debits vs credits for the current month, grouped by posting stream.

        Streams are derived from ``reference_type`` (payment, transport,
        hostel, cafeteria_pos, cafeteria_payment, cafeteria_refund,
        depreciation, purchase_order, ...) so every ledger writer shows up
        automatically. Returns per-stream totals for the current month, the
        same aggregates for the previous month (``prev_*``), plus the overall
        balances — so clients can show month-over-month deltas.
        """
        from datetime import timedelta

        from django.db.models import Count, Q, Sum
        from django.db.models.functions import Coalesce
        from django.utils import timezone

        today = timezone.localdate()
        month_start = today.replace(day=1)
        prev_start = (month_start - timedelta(days=1)).replace(day=1)
        prev_end = month_start - timedelta(days=1)
        base = self.get_queryset()

        def _aggregate(start, end):
            grouped = (
                base.filter(entry_date__gte=start, entry_date__lte=end)
                .values("reference_type")
                .annotate(
                    total_debits=Coalesce(
                        Sum("amount", filter=Q(entry_type=AccountingEntry.EntryType.DEBIT)),
                        Decimal("0"),
                    ),
                    total_credits=Coalesce(
                        Sum("amount", filter=Q(entry_type=AccountingEntry.EntryType.CREDIT)),
                        Decimal("0"),
                    ),
                    entry_count=Count("id"),
                )
                .order_by("reference_type")
            )
            return {row["reference_type"] or "unclassified": row for row in grouped}

        def _money(value):
            return str(Decimal(value).quantize(Decimal("0.01")))

        current = _aggregate(month_start, today)
        previous = _aggregate(prev_start, prev_end)

        rows = []
        for stream in sorted(set(current) | set(previous)):
            cur, prior = current.get(stream), previous.get(stream)
            rows.append(
                {
                    "stream": stream,
                    "total_debits": _money(cur["total_debits"]) if cur else "0.00",
                    "total_credits": _money(cur["total_credits"]) if cur else "0.00",
                    "entry_count": cur["entry_count"] if cur else 0,
                    "prev_debits": _money(prior["total_debits"]) if prior else "0.00",
                    "prev_credits": _money(prior["total_credits"]) if prior else "0.00",
                }
            )

        total_debits = sum((Decimal(r["total_debits"]) for r in rows), Decimal("0.00"))
        total_credits = sum((Decimal(r["total_credits"]) for r in rows), Decimal("0.00"))
        prev_total_debits = sum((Decimal(r["prev_debits"]) for r in rows), Decimal("0.00"))
        prev_total_credits = sum((Decimal(r["prev_credits"]) for r in rows), Decimal("0.00"))
        return Response(
            {
                "month": month_start.strftime("%Y-%m"),
                "prev_month": prev_start.strftime("%Y-%m"),
                "streams": rows,
                "total_debits": _money(total_debits),
                "total_credits": _money(total_credits),
                "net": _money(total_credits - total_debits),
                "prev_total_debits": _money(prev_total_debits),
                "prev_total_credits": _money(prev_total_credits),
                "prev_net": _money(prev_total_credits - prev_total_debits),
            }
        )

    @action(detail=False, methods=["get"])
    def monthly_trend(self, request):
        """Per-stream credits/debits for the trailing months (default 6).

        Powers the trend sparklines on the ledger summary card. Months are
        calendar months ending with the current one; a stream with no
        activity in a given month reports 0.00 so series stay aligned.
        """
        from datetime import timedelta

        from django.db.models import Q, Sum
        from django.db.models.functions import Coalesce, TruncMonth
        from django.utils import timezone

        try:
            months = min(max(int(request.query_params.get("months", "6")), 1), 12)
        except (TypeError, ValueError):
            months = 6

        today = timezone.localdate()
        start = today.replace(day=1)
        for _ in range(months - 1):
            start = (start - timedelta(days=1)).replace(day=1)

        labels = []
        cursor = start
        while cursor <= today:
            labels.append(cursor.strftime("%Y-%m"))
            cursor = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)

        def _money(value):
            return str(Decimal(value).quantize(Decimal("0.01")))

        buckets = (
            self.get_queryset()
            .filter(entry_date__gte=start, entry_date__lte=today)
            .annotate(bucket=TruncMonth("entry_date"))
            .values("reference_type", "bucket")
            .annotate(
                debits=Coalesce(
                    Sum("amount", filter=Q(entry_type=AccountingEntry.EntryType.DEBIT)),
                    Decimal("0"),
                ),
                credits=Coalesce(
                    Sum("amount", filter=Q(entry_type=AccountingEntry.EntryType.CREDIT)),
                    Decimal("0"),
                ),
            )
            .order_by("bucket")
        )

        series = {}
        for row in buckets:
            stream = row["reference_type"] or "unclassified"
            label = row["bucket"].strftime("%Y-%m")
            series.setdefault(stream, {})[label] = row

        streams = [
            {
                "stream": stream,
                "credits": [_money(points[label]["credits"]) if label in points else "0.00" for label in labels],
                "debits": [_money(points[label]["debits"]) if label in points else "0.00" for label in labels],
            }
            for stream, points in sorted(series.items())
        ]
        return Response({"months": labels, "streams": streams})


class FinancialAuditViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialAuditSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return FinancialAudit.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class StudentFinancialAccountViewSet(viewsets.ModelViewSet):
    serializer_class = StudentFinancialAccountSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return StudentFinancialAccount.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ParentAccountViewSet(viewsets.ModelViewSet):
    serializer_class = ParentAccountSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ParentAccount.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BankReconciliationViewSet(viewsets.ModelViewSet):
    serializer_class = BankReconciliationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return BankReconciliation.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class PaymentMethodViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentMethodSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return PaymentMethod.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TransactionLogViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionLogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["description", "reference_number", "transaction_id"]
    filterset_fields = ["school", "transaction_type", "status"]

    def get_queryset(self):
        return TransactionLog.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CreditNoteViewSet(viewsets.ModelViewSet):
    serializer_class = CreditNoteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CreditNote.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, issued_by=self.request.user)

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        """
        Apply an issued credit note to its invoice: reduces the invoice's
        total_amount (and therefore the outstanding balance) by the note
        amount and records the adjustment in the audit trail.

        Only draft/issued notes can be applied, and only once — applied and
        cancelled notes are rejected. The invoice may not go negative.
        """
        note = self.get_object()

        if note.status not in (CreditNote.Status.DRAFT, CreditNote.Status.ISSUED):
            return Response(
                {"detail": f"Cannot apply a note with status '{note.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not note.invoice_id:
            return Response(
                {"detail": "This credit note is not linked to an invoice."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            locked_note = CreditNote.objects.select_for_update().get(pk=note.pk)
            if locked_note.status not in (CreditNote.Status.DRAFT, CreditNote.Status.ISSUED):
                return Response(
                    {"detail": "Note was modified by another request."},
                    status=status.HTTP_409_CONFLICT,
                )

            invoice = FeeInvoice.objects.select_for_update().get(id=locked_note.invoice_id)
            new_total = invoice.total_amount - locked_note.amount
            if new_total < 0:
                return Response(
                    {
                        "detail": (
                            f"Credit of {locked_note.amount} would take invoice "
                            f"{invoice.invoice_number} below zero "
                            f"(current total {invoice.total_amount})."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            invoice.total_amount = new_total
            invoice.save(update_fields=["total_amount"])

            locked_note.status = CreditNote.Status.APPLIED
            locked_note.applied_date = timezone.now().date()
            locked_note.save(update_fields=["status", "applied_date"])

            TransactionLog.objects.get_or_create(
                transaction_id=f"CN-{locked_note.id}",
                defaults={
                    "school_id": locked_note.school_id,
                    "student_id": locked_note.student_id,
                    "transaction_type": TransactionLog.TransactionType.ADJUSTMENT,
                    "amount": locked_note.amount,
                    "reference_number": locked_note.note_number,
                    "description": (
                        f"Credit note {locked_note.note_number} applied to invoice "
                        f"{invoice.invoice_number}: {locked_note.reason}"
                    ),
                    "metadata": {
                        "invoice_id": str(invoice.id),
                        "note_id": str(locked_note.id),
                        "note_type": "credit",
                        "applied_by": request.user.full_name,
                    },
                },
            )

        return Response(
            {
                "detail": f"Credit note {locked_note.note_number} applied.",
                "invoice_total": str(invoice.total_amount),
                "invoice_outstanding": str(invoice.outstanding_amount),
            }
        )


class DebitNoteViewSet(viewsets.ModelViewSet):
    serializer_class = DebitNoteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return DebitNote.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, issued_by=self.request.user)

    @action(detail=True, methods=["post"])
    def apply(self, request, pk=None):
        """
        Apply an issued debit note to its invoice: increases the invoice's
        total_amount (e.g. for late penalties or missed charges) and records
        the adjustment in the audit trail.

        Only draft/issued notes can be applied, and only once.
        """
        note = self.get_object()

        if note.status not in (DebitNote.Status.DRAFT, DebitNote.Status.ISSUED):
            return Response(
                {"detail": f"Cannot apply a note with status '{note.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not note.invoice_id:
            return Response(
                {"detail": "This debit note is not linked to an invoice."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            locked_note = DebitNote.objects.select_for_update().get(pk=note.pk)
            if locked_note.status not in (DebitNote.Status.DRAFT, DebitNote.Status.ISSUED):
                return Response(
                    {"detail": "Note was modified by another request."},
                    status=status.HTTP_409_CONFLICT,
                )

            invoice = FeeInvoice.objects.select_for_update().get(id=locked_note.invoice_id)
            invoice.total_amount += locked_note.amount
            invoice.save(update_fields=["total_amount"])

            locked_note.status = DebitNote.Status.APPLIED
            locked_note.applied_date = timezone.now().date()
            locked_note.save(update_fields=["status", "applied_date"])

            TransactionLog.objects.get_or_create(
                transaction_id=f"DN-{locked_note.id}",
                defaults={
                    "school_id": locked_note.school_id,
                    "student_id": locked_note.student_id,
                    "transaction_type": TransactionLog.TransactionType.ADJUSTMENT,
                    "amount": locked_note.amount,
                    "reference_number": locked_note.note_number,
                    "description": (
                        f"Debit note {locked_note.note_number} applied to invoice "
                        f"{invoice.invoice_number}: {locked_note.reason}"
                    ),
                    "metadata": {
                        "invoice_id": str(invoice.id),
                        "note_id": str(locked_note.id),
                        "note_type": "debit",
                        "applied_by": request.user.full_name,
                    },
                },
            )

        return Response(
            {
                "detail": f"Debit note {locked_note.note_number} applied.",
                "invoice_total": str(invoice.total_amount),
                "invoice_outstanding": str(invoice.outstanding_amount),
            }
        )


class FinancialYearViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialYearSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return FinancialYear.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """
        Close out a financial year.

        Locks the year (no un-close), snapshots revenue/expense/refund
        totals into the record, and rolls each student's outstanding
        balance into a carry-forward StudentLedger entry so the new
        year starts from the right position. Idempotent in effect: a
        year already closed rejects re-closing with a clear error.

        The snapshot is written before the lock so the totals reflect
        the state at close-out time.
        """
        from django.db.models import F, Sum

        fy = self.get_object()

        if fy.is_closed:
            return Response(
                {"detail": f"Financial year '{fy.name}' is already closed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        school = fy.school

        with transaction.atomic():
            # Snapshot period totals.
            payments = Payment.objects.filter(
                invoice__student__school=school,
                status=Payment.Status.SUCCESSFUL,
                paid_at__date__gte=fy.start_date,
                paid_at__date__lte=fy.end_date,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

            expenses = ExpenseTracking.objects.filter(
                school=school,
                status="paid",
                expense_date__gte=fy.start_date,
                expense_date__lte=fy.end_date,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

            refunds = TransactionLog.objects.filter(
                school=school,
                transaction_type=TransactionLog.TransactionType.REFUND,
                created_at__date__gte=fy.start_date,
                created_at__date__lte=fy.end_date,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

            # Carry-forward: outstanding balance per student at year end.
            open_invoices = FeeInvoice.objects.filter(
                student__school=school,
                status__in=[FeeInvoice.Status.UNPAID, FeeInvoice.Status.PARTIAL, FeeInvoice.Status.OVERDUE],
            ).exclude(total_amount=F("paid_amount"))
            carryforward_by_student = {
                row["student_id"]: row["total"]
                for row in open_invoices.values("student_id").annotate(total=Sum("total_amount") - Sum("paid_amount"))
            }

            fy.notes = (
                (fy.notes + "\n" if fy.notes else "")
                + f"Closed by {request.user.full_name} on {timezone.now().date()}: "
                f"revenue {payments:,.2f}, expenses {expenses:,.2f}, refunds {refunds:,.2f}, "
                f"carry-forward for {len(carryforward_by_student)} student(s)."
            )
            fy.is_closed = True
            fy.closed_by = request.user
            fy.closed_date = timezone.now().date()
            fy.save(
                update_fields=[
                    "notes",
                    "is_closed",
                    "closed_by",
                    "closed_date",
                ]
            )

            # Roll forward: one ledger entry per student with a balance.
            # Idempotent on the reference (truncated FY + student ids to fit
            # varchar(50)): a re-close attempt is already blocked above, but
            # this also protects against race retries.
            current_year = AcademicYear.objects.filter(school=school, is_current=True).first()
            rolled = 0
            for student_id, amount in carryforward_by_student.items():
                if amount <= 0:
                    continue
                _, created = StudentLedger.objects.get_or_create(
                    school=school,
                    student_id=student_id,
                    academic_year=current_year,
                    transaction_type=StudentLedger.TransactionType.OTHER,
                    reference_number=f"FY-{str(fy.id)[:12]}-{str(student_id)[:12]}",
                    defaults={
                        "transaction_type": StudentLedger.TransactionType.OTHER,
                        "amount": amount,
                        "balance_after": amount,
                        "description": f"Carry-forward balance from financial year {fy.name}",
                        "transaction_date": fy.end_date,
                        "notes": f"Auto-generated by close-out of {fy.name}",
                    },
                )
                if created:
                    rolled += 1

        return Response(
            {
                "detail": f"Financial year '{fy.name}' closed.",
                "snapshot": {
                    "revenue": str(payments),
                    "expenses": str(expenses),
                    "refunds": str(refunds),
                    "net": str(payments - expenses),
                },
                "students_with_carryforward": len(carryforward_by_student),
                "carryforward_entries_created": rolled,
            }
        )


class FeeWaiverApprovalViewSet(viewsets.ModelViewSet):
    serializer_class = FeeWaiverApprovalSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return FeeWaiverApproval.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
