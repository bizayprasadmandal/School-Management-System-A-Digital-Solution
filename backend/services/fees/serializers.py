"""Serializers for fees."""

from rest_framework import serializers

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


class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = ["id", "school", "name", "description", "is_mandatory", "is_recurring", "recurrence"]
        read_only_fields = ["id", "school"]


class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = [
            "id",
            "school",
            "academic_year",
            "grade",
            "fee_category",
            "amount",
            "due_day",
            "late_fee_per_day",
            "is_active",
        ]
        read_only_fields = ["id", "school"]


class FeeInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeInvoice
        fields = [
            "id",
            "id",
            "invoice_number",
            "student",
            "academic_year",
            "fee_structure",
            "due_date",
            "base_amount",
            "discount_amount",
            "late_fee",
            "total_amount",
            "paid_amount",
            "status",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "id",
            "invoice",
            "amount",
            "payment_method",
            "status",
            "transaction_id",
            "gateway_response",
            "receipt_number",
            "paid_at",
            "receipt_sent_at",
            "collected_by",
            "refunded_by",
        ]
        read_only_fields = ["id", "created_at"]


class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = [
            "id",
            "school",
            "student",
            "academic_year",
            "name",
            "discount_type",
            "discount_value",
            "applies_to_categories",
            "reason",
            "approved_by",
            "is_active",
        ]
        read_only_fields = ["id", "school", "approved_by"]


class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewayConfig
        fields = ["id", "school", "stripe_enabled", "khalti_enabled", "esewa_enabled", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class InstallmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPlan
        fields = [
            "id",
            "school",
            "id",
            "student",
            "invoice",
            "total_amount",
            "number_of_installments",
            "installment_amount",
            "start_date",
            "end_date",
            "status",
            "late_fee_per_installment",
            "grace_period_days",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = [
            "id",
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


class SiblingDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiblingDiscount
        fields = [
            "id",
            "school",
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
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PaymentReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReminder
        fields = [
            "id",
            "school",
            "id",
            "invoice",
            "student",
            "reminder_type",
            "status",
            "subject",
            "message",
            "scheduled_date",
            "scheduled_time",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class FeeConcessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeConcession
        fields = [
            "id",
            "school",
            "id",
            "student",
            "academic_year",
            "concession_type",
            "name",
            "discount_type",
            "discount_value",
            "applies_to_categories",
            "max_amount",
            "status",
            "approved_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RevenueReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueReport
        fields = [
            "id",
            "school",
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
        ]
        read_only_fields = ["id", "created_at"]


class FeeCollectionDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCollectionDashboard
        fields = [
            "id",
            "school",
            "id",
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
        ]
        read_only_fields = ["id", "created_at"]


class FeeAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeAdjustment
        fields = [
            "id",
            "school",
            "id",
            "student",
            "invoice",
            "adjustment_type",
            "amount",
            "description",
            "approved_by",
            "approved_at",
            "adjustment_date",
            "notes",
        ]
        read_only_fields = ["id", "created_at"]


class AdvancePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancePayment
        fields = [
            "id",
            "school",
            "id",
            "student",
            "amount",
            "payment",
            "applied_to_invoice",
            "applied_amount",
            "status",
            "payment_date",
            "applied_date",
            "expiry_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FeeWaiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeWaiver
        fields = [
            "id",
            "school",
            "id",
            "student",
            "academic_year",
            "waiver_type",
            "amount",
            "applies_to_categories",
            "status",
            "approved_by",
            "approved_at",
            "rejection_reason",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentLedger
        fields = [
            "id",
            "school",
            "id",
            "student",
            "academic_year",
            "transaction_type",
            "amount",
            "balance_after",
            "invoice",
            "payment",
            "description",
        ]
        read_only_fields = ["id", "created_at"]


class FeeTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeTemplate
        fields = [
            "id",
            "school",
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
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BulkInvoiceGenerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkInvoiceGeneration
        fields = [
            "id",
            "school",
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
        ]
        read_only_fields = ["id"]


class PaymentReconciliationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentReconciliation
        fields = [
            "id",
            "school",
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
        ]
        read_only_fields = ["id"]


class BudgetPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetPlan
        fields = [
            "id",
            "school",
            "id",
            "academic_year",
            "title",
            "total_budget",
            "allocated",
            "spent",
            "status",
            "approved_by",
            "approved_date",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BudgetLineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetLineItem
        fields = [
            "id",
            "id",
            "budget_plan",
            "category",
            "description",
            "budgeted_amount",
            "actual_amount",
            "variance",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ExpenseTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseTracking
        fields = [
            "id",
            "school",
            "id",
            "expense_type",
            "description",
            "amount",
            "vendor",
            "invoice_number",
            "expense_date",
            "category",
            "approved_by",
            "status",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RefundRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundRecord
        fields = [
            "id",
            "school",
            "id",
            "student",
            "payment",
            "invoice",
            "amount",
            "reason",
            "status",
            "processed_date",
            "refund_method",
            "approved_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LateFeeRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LateFeeRule
        fields = [
            "id",
            "school",
            "id",
            "name",
            "days_after_due",
            "fee_amount",
            "fee_type",
            "percentage",
            "max_late_fee",
            "applies_to",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FeeDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeDiscount
        fields = [
            "id",
            "school",
            "id",
            "name",
            "discount_type",
            "value",
            "applies_to",
            "grade",
            "category",
            "start_date",
            "end_date",
            "is_active",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FeeExemptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeExemption
        fields = [
            "id",
            "school",
            "id",
            "student",
            "fee_structure",
            "reason",
            "exemption_type",
            "percentage",
            "approved_by",
            "approved_date",
            "valid_from",
            "valid_to",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InvoiceTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceTemplate
        fields = [
            "id",
            "school",
            "id",
            "name",
            "description",
            "header_text",
            "footer_text",
            "terms_and_conditions",
            "logo_url",
            "is_default",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReceiptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptTemplate
        fields = [
            "id",
            "school",
            "id",
            "name",
            "description",
            "header_text",
            "footer_text",
            "is_default",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AccountingEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountingEntry
        fields = [
            "id",
            "school",
            "id",
            "entry_type",
            "account_code",
            "account_name",
            "description",
            "amount",
            "reference_type",
            "reference_id",
            "entry_date",
            "created_by",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class FinancialAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialAudit
        fields = [
            "id",
            "school",
            "id",
            "audit_type",
            "title",
            "audit_period_start",
            "audit_period_end",
            "status",
            "auditor_name",
            "auditor_organization",
            "findings",
            "recommendations",
            "total_revenue",
            "total_expenses",
            "net_income",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StudentFinancialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFinancialAccount
        fields = [
            "id",
            "school",
            "id",
            "student",
            "account_type",
            "balance",
            "credit_limit",
            "total_paid",
            "total_outstanding",
            "last_payment_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ParentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentAccount
        fields = [
            "id",
            "school",
            "id",
            "parent",
            "balance",
            "total_paid",
            "total_outstanding",
            "payment_method",
            "auto_pay_enabled",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BankReconciliationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankReconciliation
        fields = [
            "id",
            "school",
            "id",
            "bank_statement_date",
            "statement_balance",
            "book_balance",
            "difference",
            "status",
            "matched_transactions",
            "unmatched_transactions",
            "adjustments",
            "reconciled_by",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            "id",
            "school",
            "id",
            "name",
            "method_type",
            "description",
            "processing_fee_percentage",
            "processing_fee_fixed",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TransactionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionLog
        fields = [
            "id",
            "school",
            "id",
            "transaction_type",
            "transaction_id",
            "student",
            "amount",
            "payment_method",
            "reference_number",
            "status",
            "description",
            "metadata",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CreditNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditNote
        fields = [
            "id",
            "school",
            "id",
            "note_number",
            "student",
            "invoice",
            "amount",
            "reason",
            "status",
            "issued_date",
            "applied_date",
            "issued_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DebitNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebitNote
        fields = [
            "id",
            "school",
            "id",
            "note_number",
            "student",
            "invoice",
            "amount",
            "reason",
            "status",
            "issued_date",
            "applied_date",
            "issued_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FinancialYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialYear
        fields = [
            "id",
            "school",
            "id",
            "name",
            "start_date",
            "end_date",
            "is_current",
            "is_closed",
            "closed_by",
            "closed_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FeeWaiverApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeWaiverApproval
        fields = [
            "id",
            "school",
            "id",
            "waiver",
            "approver",
            "status",
            "comments",
            "approved_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
