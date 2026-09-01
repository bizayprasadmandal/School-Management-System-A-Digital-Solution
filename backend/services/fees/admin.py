"""Django Admin registrations for fees."""

from django.contrib import admin

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


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "school"]
    list_filter = ["school"]
    search_fields = ["name"]


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(PaymentGatewayConfig)
class PaymentGatewayConfigAdmin(admin.ModelAdmin):
    list_display = ["id", "school"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(InstallmentPayment)
class InstallmentPaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(SiblingDiscount)
class SiblingDiscountAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(FeeConcession)
class FeeConcessionAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(RevenueReport)
class RevenueReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(FeeCollectionDashboard)
class FeeCollectionDashboardAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(FeeAdjustment)
class FeeAdjustmentAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(AdvancePayment)
class AdvancePaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(FeeWaiver)
class FeeWaiverAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentLedger)
class StudentLedgerAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(FeeTemplate)
class FeeTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(BulkInvoiceGeneration)
class BulkInvoiceGenerationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(PaymentReconciliation)
class PaymentReconciliationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(BudgetPlan)
class BudgetPlanAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(BudgetLineItem)
class BudgetLineItemAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ExpenseTracking)
class ExpenseTrackingAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(RefundRecord)
class RefundRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(LateFeeRule)
class LateFeeRuleAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(FeeDiscount)
class FeeDiscountAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(FeeExemption)
class FeeExemptionAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(InvoiceTemplate)
class InvoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(ReceiptTemplate)
class ReceiptTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(AccountingEntry)
class AccountingEntryAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(FinancialAudit)
class FinancialAuditAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentFinancialAccount)
class StudentFinancialAccountAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(ParentAccount)
class ParentAccountAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(BankReconciliation)
class BankReconciliationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(DebitNote)
class DebitNoteAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(FinancialYear)
class FinancialYearAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["name"]


@admin.register(FeeWaiverApproval)
class FeeWaiverApprovalAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]
