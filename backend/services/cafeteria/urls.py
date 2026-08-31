from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AllergenManagementViewSet,
    CafeteriaInventoryViewSet,
    DietaryRestrictionViewSet,
    FreeReducedLunchViewSet,
    MealBookingViewSet,
    MealMenuViewSet,
    MealPlanViewSet,
    MenuItemAllergenViewSet,
    NutritionTrackingViewSet,
    PaymentTransactionViewSet,
    PointOfSaleViewSet,
    PreOrderSystemViewSet,
    ProductionPlanningViewSet,
    StudentAccountViewSet,
    USDAComplianceReportViewSet,
    VendorManagementViewSet,
    VendorOrderViewSet,
    WasteTrackingViewSet,
)

app_name = "cafeteria_v1"
router = DefaultRouter()
# Core
router.register(r"menus", MealMenuViewSet, basename="meal-menu")
router.register(r"plans", MealPlanViewSet, basename="meal-plan")
router.register(r"bookings", MealBookingViewSet, basename="meal-booking")
router.register(r"dietary", DietaryRestrictionViewSet, basename="dietary")
# POS & Payments
router.register(r"pos", PointOfSaleViewSet, basename="point-of-sale")
router.register(r"payments", PaymentTransactionViewSet, basename="payment-transaction")
router.register(r"accounts", StudentAccountViewSet, basename="student-account")
# Free/Reduced Lunch
router.register(r"free-reduced", FreeReducedLunchViewSet, basename="free-reduced-lunch")
# Inventory & Vendors
router.register(r"inventory", CafeteriaInventoryViewSet, basename="cafeteria-inventory")
router.register(r"vendors", VendorManagementViewSet, basename="vendor-management")
router.register(r"vendor-orders", VendorOrderViewSet, basename="vendor-order")
# Allergens & Nutrition
router.register(r"allergens", AllergenManagementViewSet, basename="allergen-management")
router.register(r"menu-allergens", MenuItemAllergenViewSet, basename="menu-item-allergen")
router.register(r"nutrition", NutritionTrackingViewSet, basename="nutrition-tracking")
# Pre-Orders & Production
router.register(r"pre-orders", PreOrderSystemViewSet, basename="pre-order-system")
router.register(r"production", ProductionPlanningViewSet, basename="production-planning")
# Compliance & Waste
router.register(r"usda-reports", USDAComplianceReportViewSet, basename="usda-compliance-report")
router.register(r"waste", WasteTrackingViewSet, basename="waste-tracking")

urlpatterns = [path("", include(router.urls))]
