"""Serializers for cafeteria."""

from rest_framework import serializers

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


class MealMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealMenu
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "meal_type",
            "name",
            "date",
            "items",
            "description",
            "calories",
            "is_vegetarian",
            "is_vegan",
            "is_gluten_free",
            "price",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MealPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlan
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "meals_included",
            "price_per_period",
            "period_days",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MealBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealBooking
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "user",
            "on_delete",
            "menu",
            "on_delete",
            "meal_plan",
            "on_delete",
            "booking_date",
            "meal_type",
            "status",
            "notes",
            "cancelled_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DietaryRestrictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietaryRestriction
        fields = ["id", "id", "user", "on_delete", "restriction_type", "severity", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class PointOfSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointOfSale
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "user",
            "on_delete",
            "transaction_type",
            "amount",
            "payment_method",
            "menu",
            "on_delete",
            "balance_before",
            "balance_after",
            "is_successful",
            "meal_benefit_applied",
            "benefit_type",
        ]
        read_only_fields = ["id"]


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "user",
            "on_delete",
            "transaction_type",
            "amount",
            "payment_method",
            "status",
            "transaction_id",
            "receipt_number",
            "account_balance_before",
            "account_balance_after",
            "meal_plan",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]


class FreeReducedLunchSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreeReducedLunch
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "eligibility_type",
            "status",
            "application_date",
            "approval_date",
            "expiry_date",
            "application_number",
            "document_url",
            "household_size",
            "household_income",
            "reviewed_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CafeteriaInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaInventory
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "category",
            "description",
            "quantity",
            "unit",
            "minimum_stock",
            "unit_cost",
            "total_value",
            "supplier",
            "on_delete",
            "storage_location",
            "temperature_requirement",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class USDAComplianceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = USDAComplianceReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "report_type",
            "title",
            "start_date",
            "end_date",
            "total_meals_served",
            "free_meals",
            "reduced_meals",
            "paid_meals",
            "total_reimbursement",
            "per_meal_rate",
            "status",
            "submitted_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PreOrderSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreOrderSystem
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "user",
            "on_delete",
            "menu",
            "on_delete",
            "quantity",
            "unit_price",
            "total_price",
            "special_requests",
            "status",
            "payment_status",
            "transaction",
            "on_delete",
        ]
        read_only_fields = ["id", "updated_at"]


class StudentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAccount
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "user",
            "on_delete",
            "balance",
            "low_balance_threshold",
            "auto_replenish_enabled",
            "replenish_threshold",
            "replenish_amount",
            "status",
            "daily_spending_limit",
            "total_spent",
            "total_deposited",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AllergenManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllergenManagement
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "severity",
            "symptoms",
            "treatment_notes",
            "is_active",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MenuItemAllergenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemAllergen
        fields = [
            "id",
            "id",
            "menu",
            "on_delete",
            "allergen",
            "on_delete",
            "contains",
            "may_contain",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class NutritionTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionTracking
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "user",
            "on_delete",
            "date",
            "calories",
            "protein",
            "carbohydrates",
            "fat",
            "fiber",
            "vitamins",
            "minerals",
            "meals",
            "notes",
        ]
        read_only_fields = ["id", "created_at"]


class VendorManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorManagement
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "contact_name",
            "email",
            "phone",
            "address",
            "products_offered",
            "payment_terms",
            "delivery_schedule",
            "minimum_order",
            "status",
            "rating",
            "total_orders",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VendorOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorOrder
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "vendor",
            "on_delete",
            "order_number",
            "items",
            "total_amount",
            "status",
            "order_date",
            "expected_delivery",
            "actual_delivery",
            "payment_status",
            "created_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductionPlanningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionPlanning
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "menu",
            "on_delete",
            "planned_quantity",
            "actual_quantity",
            "pre_order_count",
            "expected_walk_in",
            "status",
            "assigned_to",
            "on_delete",
            "prep_start_time",
            "prep_end_time",
            "serve_time",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WasteTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteTracking
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "menu",
            "on_delete",
            "date",
            "waste_type",
            "item_name",
            "quantity_wasted",
            "unit",
            "estimated_cost",
            "reason",
            "prevention_notes",
            "recorded_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]


class OnlineOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineOrder
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "status",
            "items",
            "total_amount",
            "pickup_time",
            "delivery_location",
            "delivery_required",
            "paid",
            "payment_method",
            "special_instructions",
            "ordered_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OnlineOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineOrderItem
        fields = [
            "id",
            "id",
            "order",
            "on_delete",
            "menu_item",
            "on_delete",
            "item_name",
            "quantity",
            "unit_price",
            "total_price",
            "special_requests",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MealDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = MealDelivery
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "status",
            "delivery_date",
            "delivery_time",
            "delivery_location",
            "class_group",
            "meals_ordered",
            "meals_delivered",
            "meals_returned",
            "delivered_by",
            "on_delete",
            "created_at",
            "completed_at",
        ]
        read_only_fields = ["id", "created_at"]


class CashRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashRegister
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "register_name",
            "location",
            "is_active",
            "is_open",
            "opening_amount",
            "opened_by",
            "on_delete",
            "opened_at",
            "closing_amount",
            "expected_amount",
            "variance",
            "closed_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DailySalesSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySalesSummary
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "date",
            "total_sales",
            "total_transactions",
            "total_items_sold",
            "avg_transaction_value",
            "cash_sales",
            "card_sales",
            "account_sales",
            "free_meal_sales",
            "breakfast_sales",
            "lunch_sales",
            "snack_sales",
        ]
        read_only_fields = ["id", "created_at"]


class FoodSafetyCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodSafetyCheck
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "check_type",
            "check_date",
            "status",
            "checked_by",
            "on_delete",
            "temperature_reading",
            "location",
            "findings",
            "corrective_actions",
            "compliance_notes",
            "photo",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class FoodSafetyIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodSafetyIncident
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "description",
            "severity",
            "status",
            "reported_by",
            "on_delete",
            "people_affected",
            "root_cause",
            "investigation_notes",
            "corrective_actions",
            "preventive_measures",
            "resolved_at",
        ]
        read_only_fields = ["id", "created_at"]


class CafeteriaStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaStaff
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "user",
            "on_delete",
            "role",
            "shift_start",
            "shift_end",
            "days_of_week",
            "is_active",
            "is_certified",
            "certification_expiry",
            "performance_rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CafeteriaFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaFeedback
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "staff_member",
            "on_delete",
            "feedback_type",
            "rating",
            "comment",
            "meal_rated",
            "on_delete",
            "date_of_experience",
            "response",
            "responded_by",
        ]
        read_only_fields = ["id", "created_at"]


class MealPreOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPreOrder
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "meal_date",
            "meal_type",
            "menu_items",
            "total_amount",
            "status",
            "paid",
            "paid_via",
            "pickup_time",
            "pickup_location",
            "collected_at",
        ]
        read_only_fields = ["id", "created_at"]


class NutritionAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionAnalysis
        fields = [
            "id",
            "id",
            "menu_item",
            "on_delete",
            "calories",
            "protein_g",
            "carbohydrates_g",
            "fat_g",
            "fiber_g",
            "sugar_g",
            "sodium_mg",
            "vitamin_a",
            "vitamin_c",
            "calcium",
            "iron",
            "health_score",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CafeteriaEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaEquipment
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "equipment_type",
            "asset_tag",
            "brand",
            "model_number",
            "status",
            "purchase_date",
            "purchase_cost",
            "warranty_expiry",
            "last_maintenance",
            "next_maintenance",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CafeteriaReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaReservation
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "requested_by",
            "on_delete",
            "reservation_type",
            "title",
            "description",
            "reservation_date",
            "start_time",
            "end_time",
            "expected_guests",
            "status",
            "approved_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CafeteriaAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaAlert
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "alert_type",
            "severity",
            "status",
            "title",
            "description",
            "acknowledged_by",
            "on_delete",
            "resolved_by",
            "on_delete",
            "resolution_notes",
            "resolved_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MealSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealSubscription
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "plan_type",
            "status",
            "meals_included",
            "meals_per_week",
            "price_per_meal",
            "total_price",
            "discount_percentage",
            "start_date",
            "end_date",
            "next_billing_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SubscriptionUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionUsage
        fields = [
            "id",
            "id",
            "subscription",
            "on_delete",
            "meal_date",
            "meal_type",
            "menu_item",
            "on_delete",
            "used",
            "skipped",
            "recorded_at",
        ]
        read_only_fields = ["id"]


class CafeteriaAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaAnalytics
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "date",
            "total_visitors",
            "unique_visitors",
            "avg_wait_time_minutes",
            "peak_hour",
            "total_meals_served",
            "meals_by_type",
            "top_items",
            "least_popular",
            "total_waste_kg",
            "waste_percentage",
            "total_revenue",
        ]
        read_only_fields = ["id", "created_at"]


class CafeteriaCapacitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaCapacity
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "seating_area",
            "total_seats",
            "available_seats",
            "meal_type",
            "time_slot_start",
            "time_slot_end",
            "is_full",
            "reservation_required",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MenuItemRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemRating
        fields = [
            "id",
            "id",
            "menu_item",
            "on_delete",
            "student",
            "on_delete",
            "rating",
            "review",
            "would_order_again",
            "date_rated",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CafeteriaHolidayScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaHolidaySchedule
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "date",
            "is_closed",
            "special_hours",
            "opening_time",
            "closing_time",
            "reason",
            "special_menu",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CafeteriaMonthlyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaMonthlyReport
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "month",
            "year",
            "total_revenue",
            "total_cost",
            "net_profit",
            "total_meals_served",
            "total_operational_days",
            "avg_daily_revenue",
            "avg_food_rating",
            "avg_service_rating",
            "total_complaints",
            "complaints_resolved",
        ]
        read_only_fields = ["id", "created_at"]


class CafeteriaInventoryAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaInventoryAlert
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "item",
            "on_delete",
            "alert_type",
            "status",
            "message",
            "current_quantity",
            "reorder_quantity",
            "acknowledged_by",
            "on_delete",
            "resolved_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
