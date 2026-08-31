from django.contrib import admin

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


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "recurrence", "is_mandatory"]
    list_filter = ["school", "recurrence", "is_mandatory"]


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ["fee_category", "grade", "amount", "due_day", "academic_year", "is_active"]
    list_filter = ["academic_year", "grade", "is_active"]


@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "student", "total_amount", "paid_amount", "status", "due_date"]
    list_filter = ["status", "academic_year"]
    search_fields = ["invoice_number", "student__user__first_name", "student__admission_number"]
    readonly_fields = ["id", "invoice_number", "created_at", "updated_at"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["receipt_number", "invoice", "amount", "payment_method", "status", "paid_at"]
    list_filter = ["status", "payment_method"]
    search_fields = ["receipt_number"]
    readonly_fields = ["id", "receipt_number", "paid_at", "created_at"]


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ["name", "student", "discount_type", "discount_value", "is_active"]
    list_filter = ["discount_type", "is_active"]


@admin.register(PaymentGatewayConfig)
class PaymentGatewayConfigAdmin(admin.ModelAdmin):
    list_display = ["school", "stripe_enabled", "khalti_enabled", "esewa_enabled"]
    list_filter = ["stripe_enabled", "khalti_enabled", "esewa_enabled"]


# =============================================================================
# Installment Plans
# =============================================================================


class InstallmentPaymentInline(admin.TabularInline):
    model = InstallmentPayment
    extra = 0


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ["student", "total_amount", "number_of_installments", "installment_amount", "status", "start_date"]
    list_filter = ["status"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    inlines = [InstallmentPaymentInline]


@admin.register(InstallmentPayment)
class InstallmentPaymentAdmin(admin.ModelAdmin):
    list_display = ["installment_plan", "installment_number", "amount", "due_date", "paid_date", "status"]
    list_filter = ["status"]
    search_fields = ["installment_plan__student__user__first_name"]


# =============================================================================
# Sibling Discounts
# =============================================================================


@admin.register(SiblingDiscount)
class SiblingDiscountAdmin(admin.ModelAdmin):
    list_display = ["name", "discount_type", "discount_value", "min_siblings", "is_active", "priority"]
    list_filter = ["discount_type", "is_active"]
    search_fields = ["name"]


# =============================================================================
# Payment Reminders
# =============================================================================


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ["student", "invoice", "reminder_type", "status", "scheduled_date", "sent_at"]
    list_filter = ["reminder_type", "status"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    date_hierarchy = "scheduled_date"


# =============================================================================
# Fee Concessions
# =============================================================================


@admin.register(FeeConcession)
class FeeConcessionAdmin(admin.ModelAdmin):
    list_display = ["student", "concession_type", "name", "discount_type", "discount_value", "status"]
    list_filter = ["concession_type", "status", "discount_type"]
    search_fields = ["student__user__first_name", "student__user__last_name", "name"]
    date_hierarchy = "created_at"


# =============================================================================
# Revenue Reports
# =============================================================================


@admin.register(RevenueReport)
class RevenueReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "status", "period_start", "period_end", "total_collected"]
    list_filter = ["report_type", "status"]
    search_fields = ["title", "summary"]
    date_hierarchy = "created_at"


# =============================================================================
# Fee Collection Dashboard
# =============================================================================


@admin.register(FeeCollectionDashboard)
class FeeCollectionDashboardAdmin(admin.ModelAdmin):
    list_display = [
        "school",
        "total_expected",
        "total_collected",
        "total_outstanding",
        "collection_percentage",
        "last_updated",
    ]
    readonly_fields = ["last_updated", "created_at"]


# =============================================================================
# Fee Adjustments
# =============================================================================


@admin.register(FeeAdjustment)
class FeeAdjustmentAdmin(admin.ModelAdmin):
    list_display = ["student", "invoice", "adjustment_type", "amount", "adjustment_date"]
    list_filter = ["adjustment_type"]
    search_fields = ["student__user__first_name", "student__user__last_name", "description"]
    date_hierarchy = "adjustment_date"


# =============================================================================
# Advance Payments
# =============================================================================


@admin.register(AdvancePayment)
class AdvancePaymentAdmin(admin.ModelAdmin):
    list_display = ["student", "amount", "status", "payment_date", "applied_date"]
    list_filter = ["status"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    date_hierarchy = "payment_date"


# =============================================================================
# Fee Waivers
# =============================================================================


@admin.register(FeeWaiver)
class FeeWaiverAdmin(admin.ModelAdmin):
    list_display = ["student", "waiver_type", "amount", "status", "valid_from", "valid_until"]
    list_filter = ["waiver_type", "status"]
    search_fields = ["student__user__first_name", "student__user__last_name", "reason"]
    date_hierarchy = "created_at"


# =============================================================================
# Student Ledger
# =============================================================================


@admin.register(StudentLedger)
class StudentLedgerAdmin(admin.ModelAdmin):
    list_display = ["student", "transaction_type", "amount", "balance_after", "transaction_date", "reference_number"]
    list_filter = ["transaction_type", "academic_year"]
    search_fields = ["student__user__first_name", "student__user__last_name", "reference_number"]
    date_hierarchy = "transaction_date"


# =============================================================================
# Fee Templates
# =============================================================================


@admin.register(FeeTemplate)
class FeeTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "template_type", "default_amount", "recurrence", "is_mandatory", "is_active"]
    list_filter = ["template_type", "recurrence", "is_mandatory", "is_active"]
    search_fields = ["name", "description"]


# =============================================================================
# Bulk Invoice Generation
# =============================================================================


@admin.register(BulkInvoiceGeneration)
class BulkInvoiceGenerationAdmin(admin.ModelAdmin):
    list_display = [
        "batch_name",
        "status",
        "total_students",
        "total_invoices_generated",
        "total_amount",
        "initiated_at",
    ]
    list_filter = ["status"]
    search_fields = ["batch_name", "description"]
    date_hierarchy = "initiated_at"
    readonly_fields = ["initiated_at", "completed_at"]


# =============================================================================
# Payment Reconciliation
# =============================================================================


@admin.register(PaymentReconciliation)
class PaymentReconciliationAdmin(admin.ModelAdmin):
    list_display = [
        "school",
        "reconciliation_type",
        "status",
        "period_start",
        "period_end",
        "match_percentage",
        "discrepancy_count",
    ]
    list_filter = ["reconciliation_type", "status"]
    search_fields = ["notes"]
    date_hierarchy = "initiated_at"
    readonly_fields = ["initiated_at", "completed_at", "reviewed_at"]
