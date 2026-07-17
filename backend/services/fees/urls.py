from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import stripe_views
from . import nepali_views

app_name = "fees_v1"
router = DefaultRouter()
router.register("categories", views.FeeCategoryViewSet, basename="fee-category")
router.register("structures", views.FeeStructureViewSet, basename="fee-structure")
router.register("invoices", views.FeeInvoiceViewSet, basename="fee-invoice")
router.register("payments", views.PaymentViewSet, basename="payment")
router.register("scholarships", views.ScholarshipViewSet, basename="scholarship")

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
    path("gateway-config/", views.GatewayConfigView.as_view({
        "get": "list",
        "post": "create",
    }), name="gateway-config"),
    path("gateway-config/enabled/", views.GatewayConfigView.as_view({
        "get": "enabled",
    }), name="gateway-config-enabled"),
]
