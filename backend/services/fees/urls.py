from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "fees_v1"
router = DefaultRouter()
router.register("categories", views.FeeCategoryViewSet, basename="fee-category")
router.register("structures", views.FeeStructureViewSet, basename="fee-structure")
router.register("invoices", views.FeeInvoiceViewSet, basename="fee-invoice")
router.register("payments", views.PaymentViewSet, basename="payment")
router.register("scholarships", views.ScholarshipViewSet, basename="scholarship")

urlpatterns = [path("", include(router.urls))]
