"""
Fees Service — Serializers
"""

from rest_framework import serializers

from .models import (
    AdvancePayment,
    BulkInvoiceGeneration,
    FeeAdjustment,
    FeeCategory,
    FeeCollectionDashboard,
    FeeConcession,
    FeeInvoice,
    FeeStructure,
    FeeTemplate,
    FeeWaiver,
    InstallmentPayment,
    InstallmentPlan,
    Payment,
    PaymentGatewayConfig,
    PaymentReconciliation,
    PaymentReminder,
    RevenueReport,
    Scholarship,
    SiblingDiscount,
    StudentLedger,
)


class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = ["id", "name", "description", "is_mandatory", "is_recurring", "recurrence"]


class FeeStructureSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    category_name = serializers.CharField(source="fee_category.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model = FeeStructure
        fields = [
            "id",
            "grade",
            "grade_name",
            "fee_category",
            "category_name",
            "academic_year",
            "academic_year_name",
            "amount",
            "due_day",
            "late_fee_per_day",
            "is_active",
        ]


class FeeInvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    student_admission_number = serializers.CharField(source="student.admission_number", read_only=True)
    category_name = serializers.CharField(source="fee_structure.fee_category.name", read_only=True)
    outstanding_amount = serializers.ReadOnlyField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = FeeInvoice
        fields = [
            "id",
            "invoice_number",
            "student",
            "student_name",
            "student_admission_number",
            "academic_year",
            "fee_structure",
            "category_name",
            "due_date",
            "base_amount",
            "discount_amount",
            "late_fee",
            "total_amount",
            "paid_amount",
            "outstanding_amount",
            "status",
            "notes",
            "created_at",
            "is_overdue",
        ]
        read_only_fields = [
            "id",
            "invoice_number",
            "outstanding_amount",
            "created_at",
        ]

    def get_is_overdue(self, obj):
        from django.utils import timezone

        return obj.status in ["unpaid", "partial"] and obj.due_date < timezone.now().date()

    def create(self, validated_data):
        import uuid

        validated_data["invoice_number"] = f"INV-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="invoice.student.user.full_name", read_only=True)
    student_admission_number = serializers.CharField(source="invoice.student.admission_number", read_only=True)
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)
    collected_by_name = serializers.CharField(source="collected_by.full_name", read_only=True, default=None)

    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "invoice_number",
            "student_name",
            "student_admission_number",
            "amount",
            "payment_method",
            "status",
            "transaction_id",
            "gateway_response",
            "receipt_number",
            "paid_at",
            "collected_by_name",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "receipt_number", "status", "paid_at", "created_at"]

    def validate(self, attrs):
        """
        Tenant isolation + amount sanity on the write path.

        The invoice must belong to the caller's school (otherwise an admin of
        one school could credit another school's invoice by UUID), and the
        payment amount must not exceed the invoice's outstanding balance
        (prevents negative outstanding / silent overpayment absorption).
        """
        invoice = attrs.get("invoice")
        amount = attrs.get("amount")
        if invoice is not None:
            request = self.context.get("request")
            user = getattr(request, "user", None) if request else None
            school_id = getattr(user, "school_id", None)
            if school_id and invoice.student.school_id != school_id:
                raise serializers.ValidationError({"invoice": "Invoice not found in your school."})
            if amount is not None and amount > invoice.outstanding_amount:
                raise serializers.ValidationError({"amount": "Amount exceeds the invoice's outstanding balance."})
        return attrs

    def create(self, validated_data):
        import uuid

        from django.utils import timezone

        validated_data["receipt_number"] = f"RCP-{uuid.uuid4().hex[:8].upper()}"
        validated_data["status"] = "successful"
        validated_data["paid_at"] = timezone.now()
        validated_data["collected_by"] = self.context["request"].user
        return super().create(validated_data)


class ScholarshipSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True)

    class Meta:
        model = Scholarship
        fields = [
            "id",
            "student",
            "student_name",
            "academic_year",
            "name",
            "discount_type",
            "discount_value",
            "applies_to_categories",
            "reason",
            "approved_by",
            "approved_by_name",
            "is_active",
        ]
        read_only_fields = ["id", "approved_by"]


class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewayConfig
        fields = ["stripe_enabled", "khalti_enabled", "esewa_enabled"]


# =============================================================================
# Installment Plans Serializers
# =============================================================================


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = [
            "id",
            "installment_plan",
            "installment_number",
            "amount",
            "due_date",
            "paid_date",
            "status",
            "late_fee",
            "payment",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InstallmentPlanSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    payments = InstallmentPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = InstallmentPlan
        fields = [
            "id",
            "student",
            "student_name",
            "invoice",
            "total_amount",
            "number_of_installments",
            "installment_amount",
            "start_date",
            "end_date",
            "status",
            "late_fee_per_installment",
            "grace_period_days",
            "notes",
            "payments",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Sibling Discounts Serializers
# =============================================================================


class SiblingDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiblingDiscount
        fields = [
            "id",
            "name",
            "discount_type",
            "discount_value",
            "min_siblings",
            "applies_to_categories",
            "is_active",
            "priority",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Payment Reminders Serializers
# =============================================================================


class PaymentReminderSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)

    class Meta:
        model = PaymentReminder
        fields = [
            "id",
            "student",
            "student_name",
            "invoice",
            "invoice_number",
            "reminder_type",
            "status",
            "subject",
            "message",
            "scheduled_date",
            "scheduled_time",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["id", "sent_at", "created_at"]


# =============================================================================
# Fee Concessions Serializers
# =============================================================================


class FeeConcessionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = FeeConcession
        fields = [
            "id",
            "student",
            "student_name",
            "concession_type",
            "name",
            "discount_type",
            "discount_value",
            "applies_to_categories",
            "max_amount",
            "status",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejection_reason",
            "valid_from",
            "valid_until",
            "supporting_documents",
            "reason",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "approved_by", "approved_at", "created_at"]


# =============================================================================
# Revenue Reports Serializers
# =============================================================================


class RevenueReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default=None)

    class Meta:
        model = RevenueReport
        fields = [
            "id",
            "title",
            "report_type",
            "status",
            "period_start",
            "period_end",
            "summary",
            "findings",
            "recommendations",
            "total_collected",
            "total_outstanding",
            "total_refunded",
            "total_scholarships",
            "total_concessions",
            "collection_by_category",
            "collection_by_grade",
            "collection_by_payment_method",
            "generated_by",
            "generated_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Fee Collection Dashboard Serializers
# =============================================================================


class FeeCollectionDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCollectionDashboard
        fields = [
            "id",
            "school",
            "total_expected",
            "total_collected",
            "total_outstanding",
            "collection_percentage",
            "collected_by_category",
            "outstanding_by_category",
            "collected_by_grade",
            "outstanding_by_grade",
            "collected_by_method",
            "daily_collection",
            "monthly_collection",
            "total_defaulters",
            "total_overdue_amount",
            "last_updated",
            "created_at",
        ]
        read_only_fields = ["id", "last_updated", "created_at"]


# =============================================================================
# Fee Adjustments Serializers
# =============================================================================


class FeeAdjustmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = FeeAdjustment
        fields = [
            "id",
            "student",
            "student_name",
            "invoice",
            "adjustment_type",
            "amount",
            "description",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "adjustment_date",
            "notes",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "approved_by", "approved_at", "created_at"]


# =============================================================================
# Advance Payments Serializers
# =============================================================================


class AdvancePaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = AdvancePayment
        fields = [
            "id",
            "student",
            "student_name",
            "amount",
            "payment",
            "applied_to_invoice",
            "applied_amount",
            "status",
            "payment_date",
            "applied_date",
            "expiry_date",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Fee Waivers Serializers
# =============================================================================


class FeeWaiverSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = FeeWaiver
        fields = [
            "id",
            "student",
            "student_name",
            "waiver_type",
            "amount",
            "applies_to_categories",
            "status",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejection_reason",
            "valid_from",
            "valid_until",
            "reason",
            "supporting_documents",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "approved_by", "approved_at", "created_at"]


# =============================================================================
# Student Ledger Serializers
# =============================================================================


class StudentLedgerSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = StudentLedger
        fields = [
            "id",
            "student",
            "student_name",
            "transaction_type",
            "amount",
            "balance_after",
            "invoice",
            "payment",
            "description",
            "transaction_date",
            "reference_number",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Fee Templates Serializers
# =============================================================================


class FeeTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = FeeTemplate
        fields = [
            "id",
            "name",
            "template_type",
            "description",
            "default_amount",
            "is_recurring",
            "recurrence",
            "is_mandatory",
            "late_fee_per_day",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Bulk Invoice Generation Serializers
# =============================================================================


class BulkInvoiceGenerationSerializer(serializers.ModelSerializer):
    initiated_by_name = serializers.CharField(source="initiated_by.full_name", read_only=True, default=None)

    class Meta:
        model = BulkInvoiceGeneration
        fields = [
            "id",
            "batch_name",
            "description",
            "academic_year",
            "grades",
            "fee_categories",
            "status",
            "total_students",
            "total_invoices_generated",
            "total_amount",
            "errors",
            "initiated_by",
            "initiated_by_name",
            "initiated_at",
            "completed_at",
            "notes",
        ]
        read_only_fields = ["id", "initiated_at", "completed_at"]


# =============================================================================
# Payment Reconciliation Serializers
# =============================================================================


class PaymentReconciliationSerializer(serializers.ModelSerializer):
    initiated_by_name = serializers.CharField(source="initiated_by.full_name", read_only=True, default=None)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default=None)

    class Meta:
        model = PaymentReconciliation
        fields = [
            "id",
            "reconciliation_type",
            "status",
            "period_start",
            "period_end",
            "total_expected",
            "total_matched",
            "total_unmatched",
            "match_percentage",
            "discrepancies",
            "discrepancy_count",
            "initiated_by",
            "initiated_by_name",
            "reviewed_by",
            "reviewed_by_name",
            "initiated_at",
            "completed_at",
            "reviewed_at",
            "notes",
            "report_url",
        ]
        read_only_fields = ["id", "initiated_at", "completed_at", "reviewed_at"]
