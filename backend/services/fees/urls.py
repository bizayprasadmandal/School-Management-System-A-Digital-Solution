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
