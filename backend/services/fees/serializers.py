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
        fields = ["id", "school", "on_delete", "name", "description", "is_mandatory", "is_recurring", "recurrence"]
        read_only_fields = ["id"]


class FeeStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeStructure
        fields = [
            "id",
            "school",
            "on_delete",
            "academic_year",
            "on_delete",
            "grade",
            "on_delete",
            "fee_category",
            "on_delete",
            "amount",
            "due_day",
            "late_fee_per_day",
            "is_active",
        ]
        read_only_fields = ["id"]


class FeeInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeInvoice
        fields = [
            "id",
            "id",
            "invoice_number",
            "student",
            "on_delete",
            "academic_year",
            "on_delete",
            "fee_structure",
            "on_delete",
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
            "on_delete",
            "amount",
            "payment_method",
            "status",
            "transaction_id",
            "gateway_response",
            "receipt_number",
            "paid_at",
            "receipt_sent_at",
            "collected_by",
            "on_delete",
            "refunded_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]


class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = [
            "id",
            "school",
            "on_delete",
            "student",
            "on_delete",
            "academic_year",
            "on_delete",
            "name",
            "discount_type",
            "discount_value",
            "applies_to_categories",
            "reason",
            "approved_by",
            "on_delete",
            "is_active",
        ]
        read_only_fields = ["id"]


class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewayConfig
        fields = ["id", "school", "on_delete", "stripe_enabled", "khalti_enabled", "esewa_enabled", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class InstallmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPlan
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "invoice",
            "on_delete",
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
            "on_delete",
            "installment_number",
            "amount",
            "due_date",
            "paid_date",
            "status",
            "late_fee",
            "payment",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "invoice",
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "academic_year",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "invoice",
            "on_delete",
            "adjustment_type",
            "amount",
            "description",
            "approved_by",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "amount",
            "payment",
            "on_delete",
            "applied_to_invoice",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "academic_year",
            "on_delete",
            "waiver_type",
            "amount",
            "applies_to_categories",
            "status",
            "approved_by",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "academic_year",
            "on_delete",
            "transaction_type",
            "amount",
            "balance_after",
            "invoice",
            "on_delete",
            "payment",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "batch_name",
            "description",
            "academic_year",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
        ]
        read_only_fields = ["id"]


class BudgetPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetPlan
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "academic_year",
            "on_delete",
            "title",
            "total_budget",
            "allocated",
            "spent",
            "status",
            "approved_by",
            "on_delete",
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
            "on_delete",
            "category",
            "on_delete",
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
            "on_delete",
            "expense_type",
            "description",
            "amount",
            "vendor",
            "invoice_number",
            "expense_date",
            "category",
            "on_delete",
            "approved_by",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "payment",
            "on_delete",
            "invoice",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "name",
            "discount_type",
            "value",
            "applies_to",
            "grade",
            "on_delete",
            "category",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "fee_structure",
            "on_delete",
            "reason",
            "exemption_type",
            "percentage",
            "approved_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "entry_type",
            "account_code",
            "account_name",
            "description",
            "amount",
            "reference_type",
            "reference_id",
            "entry_date",
            "created_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "on_delete",
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
            "on_delete",
            "on_delete",
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
            "on_delete",
            "bank_statement_date",
            "statement_balance",
            "book_balance",
            "difference",
            "status",
            "matched_transactions",
            "unmatched_transactions",
            "adjustments",
            "reconciled_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "transaction_type",
            "transaction_id",
            "student",
            "on_delete",
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
            "on_delete",
            "note_number",
            "student",
            "on_delete",
            "invoice",
            "on_delete",
            "amount",
            "reason",
            "status",
            "issued_date",
            "applied_date",
            "issued_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DebitNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebitNote
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "note_number",
            "student",
            "on_delete",
            "invoice",
            "on_delete",
            "amount",
            "reason",
            "status",
            "issued_date",
            "applied_date",
            "issued_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FinancialYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialYear
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "start_date",
            "end_date",
            "is_current",
            "is_closed",
            "closed_by",
            "on_delete",
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
            "on_delete",
            "waiver",
            "on_delete",
            "approver",
            "on_delete",
            "status",
            "comments",
            "approved_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
