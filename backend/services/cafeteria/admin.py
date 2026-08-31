from django.contrib import admin

from .models import (
    AllergenManagement,
    CafeteriaInventory,
    DietaryRestriction,
    FreeReducedLunch,
    MealBooking,
    MealMenu,
    MealPlan,
    MenuItemAllergen,
    NutritionTracking,
    PaymentTransaction,
    PointOfSale,
    PreOrderSystem,
    ProductionPlanning,
    StudentAccount,
    USDAComplianceReport,
    VendorManagement,
    VendorOrder,
    WasteTracking,
)


@admin.register(MealMenu)
class MealMenuAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "meal_type", "price", "is_active"]
    list_filter = ["meal_type", "date", "is_active", "school"]
    search_fields = ["name", "items"]


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price_per_period", "period_days", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(MealBooking)
class MealBookingAdmin(admin.ModelAdmin):
    list_display = ["user", "menu", "meal_type", "status", "booking_date"]
    list_filter = ["meal_type", "status"]
    search_fields = ["user__full_name", "menu__name"]


@admin.register(DietaryRestriction)
class DietaryRestrictionAdmin(admin.ModelAdmin):
    list_display = ["user", "restriction_type", "severity"]
    list_filter = ["restriction_type"]
    search_fields = ["user__full_name", "restriction_type"]


@admin.register(PointOfSale)
class PointOfSaleAdmin(admin.ModelAdmin):
    list_display = ["user", "transaction_type", "amount", "payment_method", "benefit_type", "transaction_time"]
    list_filter = ["transaction_type", "payment_method", "benefit_type"]
    search_fields = ["user__full_name"]


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ["user", "transaction_type", "amount", "payment_method", "status", "created_at"]
    list_filter = ["transaction_type", "payment_method", "status"]
    search_fields = ["user__full_name", "transaction_id"]


@admin.register(FreeReducedLunch)
class FreeReducedLunchAdmin(admin.ModelAdmin):
    list_display = ["student", "eligibility_type", "status", "expiry_date"]
    list_filter = ["eligibility_type", "status"]
    search_fields = ["student__user__full_name"]


@admin.register(CafeteriaInventory)
class CafeteriaInventoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "quantity", "unit", "unit_cost", "expiry_date"]
    list_filter = ["category", "is_perishable", "is_active"]
    search_fields = ["name"]


@admin.register(USDAComplianceReport)
class USDAComplianceReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "start_date", "end_date", "status", "total_reimbursement"]
    list_filter = ["report_type", "status"]
    search_fields = ["title"]


@admin.register(PreOrderSystem)
class PreOrderSystemAdmin(admin.ModelAdmin):
    list_display = ["user", "menu", "quantity", "total_price", "status", "payment_status"]
    list_filter = ["status", "payment_status"]
    search_fields = ["user__full_name"]


@admin.register(StudentAccount)
class StudentAccountAdmin(admin.ModelAdmin):
    list_display = ["user", "balance", "status", "auto_replenish_enabled", "total_spent"]
    list_filter = ["status", "auto_replenish_enabled"]
    search_fields = ["user__full_name"]


@admin.register(AllergenManagement)
class AllergenManagementAdmin(admin.ModelAdmin):
    list_display = ["name", "severity", "is_active"]
    list_filter = ["severity", "is_active"]
    search_fields = ["name"]


@admin.register(MenuItemAllergen)
class MenuItemAllergenAdmin(admin.ModelAdmin):
    list_display = ["menu", "allergen", "contains", "may_contain"]
    search_fields = ["menu__name", "allergen__name"]


@admin.register(NutritionTracking)
class NutritionTrackingAdmin(admin.ModelAdmin):
    list_display = ["user", "date", "calories", "protein", "carbohydrates", "fat"]
    list_filter = ["date"]
    search_fields = ["user__full_name"]


@admin.register(VendorManagement)
class VendorManagementAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_name", "status", "rating", "total_orders"]
    list_filter = ["status"]
    search_fields = ["name", "contact_name"]


@admin.register(VendorOrder)
class VendorOrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "vendor", "total_amount", "status", "payment_status", "order_date"]
    list_filter = ["status", "payment_status"]
    search_fields = ["order_number", "vendor__name"]


@admin.register(ProductionPlanning)
class ProductionPlanningAdmin(admin.ModelAdmin):
    list_display = ["menu", "planned_quantity", "actual_quantity", "pre_order_count", "status"]
    list_filter = ["status"]
    search_fields = ["menu__name"]


@admin.register(WasteTracking)
class WasteTrackingAdmin(admin.ModelAdmin):
    list_display = ["item_name", "date", "waste_type", "quantity_wasted", "estimated_cost"]
    list_filter = ["waste_type", "date"]
    search_fields = ["item_name"]
