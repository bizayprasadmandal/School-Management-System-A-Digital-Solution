"""URL Configuration for fees."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AccountingEntryViewSet,
    AdvancePaymentViewSet,
    BankReconciliationViewSet,
    BudgetLineItemViewSet,
    BudgetPlanViewSet,
    BulkInvoiceGenerationViewSet,
    CreditNoteViewSet,
    DebitNoteViewSet,
    ExpenseTrackingViewSet,
    FeeAdjustmentViewSet,
    FeeCategoryViewSet,
    FeeCollectionDashboardViewSet,
    FeeConcessionViewSet,
    FeeDiscountViewSet,
    FeeExemptionViewSet,
    FeeInvoiceViewSet,
    FeeStructureViewSet,
    FeeTemplateViewSet,
    FeeWaiverApprovalViewSet,
    FeeWaiverViewSet,
    FinancialAuditViewSet,
    FinancialYearViewSet,
    InstallmentPaymentViewSet,
    InstallmentPlanViewSet,
    InvoiceTemplateViewSet,
    LateFeeRuleViewSet,
    ParentAccountViewSet,
    PaymentGatewayConfigViewSet,
    PaymentMethodViewSet,
    PaymentReconciliationViewSet,
    PaymentReminderViewSet,
    PaymentViewSet,
    ReceiptTemplateViewSet,
    RefundRecordViewSet,
    RevenueReportViewSet,
    ScholarshipViewSet,
    SiblingDiscountViewSet,
    StudentFinancialAccountViewSet,
    StudentLedgerViewSet,
    TransactionLogViewSet,
)

app_name = "fees_v1"

router = DefaultRouter()
router.register(r"fee-category", FeeCategoryViewSet, basename="fee-category")
router.register(r"fee-structure", FeeStructureViewSet, basename="fee-structure")
router.register(r"fee-invoice", FeeInvoiceViewSet, basename="fee-invoice")
router.register(r"payment", PaymentViewSet, basename="payment")
router.register(r"scholarship", ScholarshipViewSet, basename="scholarship")
router.register(r"payment-gateway-config", PaymentGatewayConfigViewSet, basename="payment-gateway-config")
router.register(r"installment-plan", InstallmentPlanViewSet, basename="installment-plan")
router.register(r"installment-payment", InstallmentPaymentViewSet, basename="installment-payment")
router.register(r"sibling-discount", SiblingDiscountViewSet, basename="sibling-discount")
router.register(r"payment-reminder", PaymentReminderViewSet, basename="payment-reminder")
router.register(r"fee-concession", FeeConcessionViewSet, basename="fee-concession")
router.register(r"revenue-report", RevenueReportViewSet, basename="revenue-report")
router.register(r"fee-collection-dashboard", FeeCollectionDashboardViewSet, basename="fee-collection-dashboard")
router.register(r"fee-adjustment", FeeAdjustmentViewSet, basename="fee-adjustment")
router.register(r"advance-payment", AdvancePaymentViewSet, basename="advance-payment")
router.register(r"fee-waiver", FeeWaiverViewSet, basename="fee-waiver")
router.register(r"student-ledger", StudentLedgerViewSet, basename="student-ledger")
router.register(r"fee-template", FeeTemplateViewSet, basename="fee-template")
router.register(r"bulk-invoice-generation", BulkInvoiceGenerationViewSet, basename="bulk-invoice-generation")
router.register(r"payment-reconciliation", PaymentReconciliationViewSet, basename="payment-reconciliation")
router.register(r"budget-plan", BudgetPlanViewSet, basename="budget-plan")
router.register(r"budget-line-item", BudgetLineItemViewSet, basename="budget-line-item")
router.register(r"expense-tracking", ExpenseTrackingViewSet, basename="expense-tracking")
router.register(r"refund-record", RefundRecordViewSet, basename="refund-record")
router.register(r"late-fee-rule", LateFeeRuleViewSet, basename="late-fee-rule")
router.register(r"fee-discount", FeeDiscountViewSet, basename="fee-discount")
router.register(r"fee-exemption", FeeExemptionViewSet, basename="fee-exemption")
router.register(r"invoice-template", InvoiceTemplateViewSet, basename="invoice-template")
router.register(r"receipt-template", ReceiptTemplateViewSet, basename="receipt-template")
router.register(r"accounting-entry", AccountingEntryViewSet, basename="accounting-entry")
router.register(r"financial-audit", FinancialAuditViewSet, basename="financial-audit")
router.register(r"student-financial-account", StudentFinancialAccountViewSet, basename="student-financial-account")
router.register(r"parent-account", ParentAccountViewSet, basename="parent-account")
router.register(r"bank-reconciliation", BankReconciliationViewSet, basename="bank-reconciliation")
router.register(r"payment-method", PaymentMethodViewSet, basename="payment-method")
router.register(r"transaction-log", TransactionLogViewSet, basename="transaction-log")
router.register(r"credit-note", CreditNoteViewSet, basename="credit-note")
router.register(r"debit-note", DebitNoteViewSet, basename="debit-note")
router.register(r"financial-year", FinancialYearViewSet, basename="financial-year")
router.register(r"fee-waiver-approval", FeeWaiverApprovalViewSet, basename="fee-waiver-approval")

urlpatterns = [
    path("", include(router.urls)),
]
