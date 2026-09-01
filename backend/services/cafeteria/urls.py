"""URL Configuration for cafeteria."""

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
router.register(r"meal-menu", MealMenuViewSet, basename="meal-menu")
router.register(r"meal-plan", MealPlanViewSet, basename="meal-plan")
router.register(r"meal-booking", MealBookingViewSet, basename="meal-booking")
router.register(r"dietary-restriction", DietaryRestrictionViewSet, basename="dietary-restriction")
router.register(r"point-of-sale", PointOfSaleViewSet, basename="point-of-sale")
router.register(r"payment-transaction", PaymentTransactionViewSet, basename="payment-transaction")
router.register(r"free-reduced-lunch", FreeReducedLunchViewSet, basename="free-reduced-lunch")
router.register(r"cafeteria-inventory", CafeteriaInventoryViewSet, basename="cafeteria-inventory")
router.register(r"u-s-d-a-compliance-report", USDAComplianceReportViewSet, basename="u-s-d-a-compliance-report")
router.register(r"pre-order-system", PreOrderSystemViewSet, basename="pre-order-system")
router.register(r"student-account", StudentAccountViewSet, basename="student-account")
router.register(r"allergen-management", AllergenManagementViewSet, basename="allergen-management")
router.register(r"menu-item-allergen", MenuItemAllergenViewSet, basename="menu-item-allergen")
router.register(r"nutrition-tracking", NutritionTrackingViewSet, basename="nutrition-tracking")
router.register(r"vendor-management", VendorManagementViewSet, basename="vendor-management")
router.register(r"vendor-order", VendorOrderViewSet, basename="vendor-order")
router.register(r"production-planning", ProductionPlanningViewSet, basename="production-planning")
router.register(r"waste-tracking", WasteTrackingViewSet, basename="waste-tracking")
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

urlpatterns = [
    path("", include(router.urls)),
]
