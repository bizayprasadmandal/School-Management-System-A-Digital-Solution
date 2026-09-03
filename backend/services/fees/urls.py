from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import nepali_views, stripe_views, views

app_name = "fees_v1"
router = DefaultRouter()
router.register("categories", views.FeeCategoryViewSet, basename="fee-category")
router.register("structures", views.FeeStructureViewSet, basename="fee-structure")
router.register("invoices", views.FeeInvoiceViewSet, basename="fee-invoice")
router.register("payments", views.PaymentViewSet, basename="payment")
router.register("scholarships", views.ScholarshipViewSet, basename="scholarship")
router.register("installment-plans", views.InstallmentPlanViewSet, basename="installment-plan")
router.register("installment-payments", views.InstallmentPaymentViewSet, basename="installment-payment")
router.register("sibling-discounts", views.SiblingDiscountViewSet, basename="sibling-discount")
router.register("payment-reminders", views.PaymentReminderViewSet, basename="payment-reminder")
router.register("concessions", views.FeeConcessionViewSet, basename="fee-concession")
router.register("revenue-reports", views.RevenueReportViewSet, basename="revenue-report")
router.register("dashboard", views.FeeCollectionDashboardViewSet, basename="fee-dashboard")
router.register("adjustments", views.FeeAdjustmentViewSet, basename="fee-adjustment")
router.register("advance-payments", views.AdvancePaymentViewSet, basename="advance-payment")
router.register("waivers", views.FeeWaiverViewSet, basename="fee-waiver")
router.register("ledger", views.StudentLedgerViewSet, basename="student-ledger")
router.register("templates", views.FeeTemplateViewSet, basename="fee-template")
router.register("bulk-invoices", views.BulkInvoiceGenerationViewSet, basename="bulk-invoice")
router.register("reconciliation", views.PaymentReconciliationViewSet, basename="payment-reconciliation")


# ── Additional registrations (module expansion) ──
router.register(r"payment-gateway-config", views.PaymentGatewayConfigViewSet, basename="payment-gateway-config")
router.register(r"budget-plan", views.BudgetPlanViewSet, basename="budget-plan")
router.register(r"budget-line-item", views.BudgetLineItemViewSet, basename="budget-line-item")
router.register(r"expense-tracking", views.ExpenseTrackingViewSet, basename="expense-tracking")
router.register(r"refund-record", views.RefundRecordViewSet, basename="refund-record")
router.register(r"late-fee-rule", views.LateFeeRuleViewSet, basename="late-fee-rule")
router.register(r"fee-discount", views.FeeDiscountViewSet, basename="fee-discount")
router.register(r"fee-exemption", views.FeeExemptionViewSet, basename="fee-exemption")
router.register(r"invoice-template", views.InvoiceTemplateViewSet, basename="invoice-template")
router.register(r"receipt-template", views.ReceiptTemplateViewSet, basename="receipt-template")
router.register(r"accounting-entry", views.AccountingEntryViewSet, basename="accounting-entry")
router.register(r"financial-audit", views.FinancialAuditViewSet, basename="financial-audit")
router.register(
    r"student-financial-account", views.StudentFinancialAccountViewSet, basename="student-financial-account"
)
router.register(r"parent-account", views.ParentAccountViewSet, basename="parent-account")
router.register(r"bank-reconciliation", views.BankReconciliationViewSet, basename="bank-reconciliation")
router.register(r"payment-method", views.PaymentMethodViewSet, basename="payment-method")
router.register(r"transaction-log", views.TransactionLogViewSet, basename="transaction-log")
router.register(r"credit-note", views.CreditNoteViewSet, basename="credit-note")
router.register(r"debit-note", views.DebitNoteViewSet, basename="debit-note")
router.register(r"financial-year", views.FinancialYearViewSet, basename="financial-year")
router.register(r"fee-waiver-approval", views.FeeWaiverApprovalViewSet, basename="fee-waiver-approval")

urlpatterns = [
    path("", include(router.urls)),
    # Stripe payment integration
    path("stripe/create-payment-intent/", stripe_views.create_payment_intent, name="stripe-create-payment-intent"),
    path("stripe/refund/", stripe_views.refund_payment, name="stripe-refund"),
    path("stripe/webhook/", stripe_views.stripe_webhook, name="stripe-webhook"),
    # Nepali payment gateways
    path("nepali/initiate/", nepali_views.initiate_payment, name="nepali-initiate"),
    path("nepali/verify/", nepali_views.verify_payment, name="nepali-verify"),
    path("nepali/refund/", nepali_views.refund_nepali_payment, name="nepali-refund"),
    # Payment gateway configuration (per-school enable/disable)
    path(
        "gateway-config/",
        views.GatewayConfigView.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="gateway-config",
    ),
    path(
        "gateway-config/enabled/",
        views.GatewayConfigView.as_view(
            {
                "get": "enabled",
            }
        ),
        name="gateway-config-enabled",
    ),
]
