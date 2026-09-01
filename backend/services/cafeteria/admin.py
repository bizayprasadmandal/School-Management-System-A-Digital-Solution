"""Django Admin registrations for cafeteria."""

from django.contrib import admin

from .models import (
    AllergenManagement,
    CafeteriaAlert,
    CafeteriaAnalytics,
    CafeteriaCapacity,
    CafeteriaEquipment,
    CafeteriaFeedback,
    CafeteriaHolidaySchedule,
    CafeteriaInventory,
    CafeteriaInventoryAlert,
    CafeteriaMonthlyReport,
    CafeteriaReservation,
    CafeteriaStaff,
    CashRegister,
    DailySalesSummary,
    DietaryRestriction,
    FoodSafetyCheck,
    FoodSafetyIncident,
    FreeReducedLunch,
    MealBooking,
    MealDelivery,
    MealMenu,
    MealPlan,
    MealPreOrder,
    MealSubscription,
    MenuItemAllergen,
    MenuItemRating,
    NutritionAnalysis,
    NutritionTracking,
    OnlineOrder,
    OnlineOrderItem,
    PaymentTransaction,
    PointOfSale,
    PreOrderSystem,
    ProductionPlanning,
    StudentAccount,
    SubscriptionUsage,
    USDAComplianceReport,
    VendorManagement,
    VendorOrder,
    WasteTracking,
)


@admin.register(MealMenu)
class MealMenuAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(MealBooking)
class MealBookingAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(DietaryRestriction)
class DietaryRestrictionAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(PointOfSale)
class PointOfSaleAdmin(admin.ModelAdmin):
    list_display = ["id", "school"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(FreeReducedLunch)
class FreeReducedLunchAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(CafeteriaInventory)
class CafeteriaInventoryAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(USDAComplianceReport)
class USDAComplianceReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(PreOrderSystem)
class PreOrderSystemAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentAccount)
class StudentAccountAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(AllergenManagement)
class AllergenManagementAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(MenuItemAllergen)
class MenuItemAllergenAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(NutritionTracking)
class NutritionTrackingAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(VendorManagement)
class VendorManagementAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(VendorOrder)
class VendorOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(ProductionPlanning)
class ProductionPlanningAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(WasteTracking)
class WasteTrackingAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(OnlineOrder)
class OnlineOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(OnlineOrderItem)
class OnlineOrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(MealDelivery)
class MealDeliveryAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(DailySalesSummary)
class DailySalesSummaryAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(FoodSafetyCheck)
class FoodSafetyCheckAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(FoodSafetyIncident)
class FoodSafetyIncidentAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(CafeteriaStaff)
class CafeteriaStaffAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(CafeteriaFeedback)
class CafeteriaFeedbackAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(MealPreOrder)
class MealPreOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(NutritionAnalysis)
class NutritionAnalysisAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(CafeteriaEquipment)
class CafeteriaEquipmentAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(CafeteriaReservation)
class CafeteriaReservationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(CafeteriaAlert)
class CafeteriaAlertAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(MealSubscription)
class MealSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(SubscriptionUsage)
class SubscriptionUsageAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(CafeteriaAnalytics)
class CafeteriaAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(CafeteriaCapacity)
class CafeteriaCapacityAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(MenuItemRating)
class MenuItemRatingAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(CafeteriaHolidaySchedule)
class CafeteriaHolidayScheduleAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(CafeteriaMonthlyReport)
class CafeteriaMonthlyReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(CafeteriaInventoryAlert)
class CafeteriaInventoryAlertAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]
