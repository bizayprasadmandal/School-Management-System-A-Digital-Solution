from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AllergenManagementViewSet,
    CafeteriaAlertViewSet,
    CafeteriaAnalyticsViewSet,
    CafeteriaCapacityViewSet,
    CafeteriaEquipmentViewSet,
    CafeteriaFeedbackViewSet,
    CafeteriaHolidayScheduleViewSet,
    CafeteriaInventoryAlertViewSet,
    CafeteriaInventoryViewSet,
    CafeteriaMonthlyReportViewSet,
    CafeteriaReservationViewSet,
    CafeteriaStaffViewSet,
    CashRegisterViewSet,
    DailySalesSummaryViewSet,
    DietaryRestrictionViewSet,
    FoodSafetyCheckViewSet,
    FoodSafetyIncidentViewSet,
    FreeReducedLunchViewSet,
    MealBookingViewSet,
    MealDeliveryViewSet,
    MealMenuViewSet,
    MealPlanViewSet,
    MealPreOrderViewSet,
    MealSubscriptionViewSet,
    MenuItemAllergenViewSet,
    MenuItemRatingViewSet,
    NutritionAnalysisViewSet,
    NutritionTrackingViewSet,
    OnlineOrderItemViewSet,
    OnlineOrderViewSet,
    PaymentTransactionViewSet,
    PointOfSaleViewSet,
    PreOrderSystemViewSet,
    ProductionPlanningViewSet,
    StudentAccountViewSet,
    SubscriptionUsageViewSet,
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


# ── Additional registrations (module expansion) ──
router.register(r"online-order", OnlineOrderViewSet, basename="online-order")
router.register(r"online-order-item", OnlineOrderItemViewSet, basename="online-order-item")
router.register(r"meal-delivery", MealDeliveryViewSet, basename="meal-delivery")
router.register(r"cash-register", CashRegisterViewSet, basename="cash-register")
router.register(r"daily-sales-summary", DailySalesSummaryViewSet, basename="daily-sales-summary")
router.register(r"food-safety-check", FoodSafetyCheckViewSet, basename="food-safety-check")
router.register(r"food-safety-incident", FoodSafetyIncidentViewSet, basename="food-safety-incident")
router.register(r"cafeteria-staff", CafeteriaStaffViewSet, basename="cafeteria-staff")
router.register(r"cafeteria-feedback", CafeteriaFeedbackViewSet, basename="cafeteria-feedback")
router.register(r"meal-pre-order", MealPreOrderViewSet, basename="meal-pre-order")
router.register(r"nutrition-analysis", NutritionAnalysisViewSet, basename="nutrition-analysis")
router.register(r"cafeteria-equipment", CafeteriaEquipmentViewSet, basename="cafeteria-equipment")
router.register(r"cafeteria-reservation", CafeteriaReservationViewSet, basename="cafeteria-reservation")
router.register(r"cafeteria-alert", CafeteriaAlertViewSet, basename="cafeteria-alert")
router.register(r"meal-subscription", MealSubscriptionViewSet, basename="meal-subscription")
router.register(r"subscription-usage", SubscriptionUsageViewSet, basename="subscription-usage")
router.register(r"cafeteria-analytics", CafeteriaAnalyticsViewSet, basename="cafeteria-analytics")
router.register(r"cafeteria-capacity", CafeteriaCapacityViewSet, basename="cafeteria-capacity")
router.register(r"menu-item-rating", MenuItemRatingViewSet, basename="menu-item-rating")
router.register(r"cafeteria-holiday-schedule", CafeteriaHolidayScheduleViewSet, basename="cafeteria-holiday-schedule")
router.register(r"cafeteria-monthly-report", CafeteriaMonthlyReportViewSet, basename="cafeteria-monthly-report")
router.register(r"cafeteria-inventory-alert", CafeteriaInventoryAlertViewSet, basename="cafeteria-inventory-alert")

urlpatterns = [path("", include(router.urls))]
