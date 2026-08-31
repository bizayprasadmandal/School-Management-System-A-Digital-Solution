"""Cafeteria serializers."""

from rest_framework import serializers

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


class MealMenuSerializer(serializers.ModelSerializer):
    meal_type_display = serializers.CharField(source="get_meal_type_display", read_only=True)
    booking_count = serializers.SerializerMethodField()

    class Meta:
        model = MealMenu
        fields = [
            "id",
            "meal_type",
            "meal_type_display",
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
            "booking_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_booking_count(self, obj):
        return getattr(obj, "booking_count", obj.bookings.count())


class MealPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlan
        fields = [
            "id",
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
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    meal_type_display = serializers.CharField(source="get_meal_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = MealBooking
        fields = [
            "id",
            "user",
            "user_name",
            "menu",
            "menu_name",
            "meal_plan",
            "booking_date",
            "meal_type",
            "meal_type_display",
            "status",
            "status_display",
            "notes",
            "cancelled_at",
            "created_at",
        ]
        read_only_fields = ["id", "booking_date", "created_at"]


class DietaryRestrictionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = DietaryRestriction
        fields = ["id", "user", "user_name", "restriction_type", "severity", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class PointOfSaleSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    transaction_type_display = serializers.CharField(source="get_transaction_type_display", read_only=True)
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)

    class Meta:
        model = PointOfSale
        fields = [
            "id",
            "user",
            "user_name",
            "transaction_type",
            "transaction_type_display",
            "amount",
            "payment_method",
            "payment_method_display",
            "menu",
            "balance_before",
            "balance_after",
            "is_successful",
            "meal_benefit_applied",
            "benefit_type",
            "notes",
            "transaction_time",
        ]
        read_only_fields = ["id", "transaction_time"]


class PaymentTransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    transaction_type_display = serializers.CharField(source="get_transaction_type_display", read_only=True)
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            "id",
            "user",
            "user_name",
            "transaction_type",
            "transaction_type_display",
            "amount",
            "payment_method",
            "payment_method_display",
            "status",
            "status_display",
            "transaction_id",
            "receipt_number",
            "account_balance_before",
            "account_balance_after",
            "meal_plan",
            "booking",
            "auto_replenish",
            "replenish_threshold",
            "replenish_amount",
            "notes",
            "processed_at",
            "created_at",
        ]
        read_only_fields = ["id", "processed_at", "created_at"]


class FreeReducedLunchSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    eligibility_type_display = serializers.CharField(source="get_eligibility_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default=None)
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = FreeReducedLunch
        fields = [
            "id",
            "student",
            "student_name",
            "eligibility_type",
            "eligibility_type_display",
            "status",
            "status_display",
            "application_date",
            "approval_date",
            "expiry_date",
            "is_valid",
            "application_number",
            "document_url",
            "household_size",
            "household_income",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reviewed_at", "created_at", "updated_at"]


class CafeteriaInventorySerializer(serializers.ModelSerializer):
    unit_display = serializers.CharField(source="get_unit_display", read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = CafeteriaInventory
        fields = [
            "id",
            "name",
            "category",
            "category_display",
            "description",
            "quantity",
            "unit",
            "unit_display",
            "minimum_stock",
            "is_low_stock",
            "unit_cost",
            "total_value",
            "storage_location",
            "temperature_requirement",
            "expiry_date",
            "is_perishable",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class USDAComplianceReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source="get_report_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    submitted_by_name = serializers.CharField(source="submitted_by.full_name", read_only=True, default=None)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)
    reimbursement_per_day = serializers.ReadOnlyField()

    class Meta:
        model = USDAComplianceReport
        fields = [
            "id",
            "report_type",
            "report_type_display",
            "title",
            "start_date",
            "end_date",
            "total_meals_served",
            "free_meals",
            "reduced_meals",
            "paid_meals",
            "total_reimbursement",
            "per_meal_rate",
            "reimbursement_per_day",
            "status",
            "status_display",
            "submitted_by",
            "submitted_by_name",
            "submitted_at",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejection_reason",
            "report_url",
            "supporting_docs",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "submitted_at", "approved_at", "created_at", "updated_at"]


class PreOrderSystemSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PreOrderSystem
        fields = [
            "id",
            "user",
            "user_name",
            "menu",
            "menu_name",
            "quantity",
            "unit_price",
            "total_price",
            "special_requests",
            "status",
            "status_display",
            "payment_status",
            "transaction",
            "order_deadline",
            "notes",
            "ordered_at",
            "updated_at",
        ]
        read_only_fields = ["id", "ordered_at", "updated_at"]


class StudentAccountSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    is_low_balance = serializers.ReadOnlyField()

    class Meta:
        model = StudentAccount
        fields = [
            "id",
            "user",
            "user_name",
            "balance",
            "is_low_balance",
            "low_balance_threshold",
            "auto_replenish_enabled",
            "replenish_threshold",
            "replenish_amount",
            "status",
            "status_display",
            "daily_spending_limit",
            "total_spent",
            "total_deposited",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_spent", "total_deposited", "created_at", "updated_at"]


class AllergenManagementSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)

    class Meta:
        model = AllergenManagement
        fields = [
            "id",
            "name",
            "description",
            "severity",
            "severity_display",
            "symptoms",
            "treatment_notes",
            "is_active",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MenuItemAllergenSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    allergen_name = serializers.CharField(source="allergen.name", read_only=True)

    class Meta:
        model = MenuItemAllergen
        fields = [
            "id",
            "menu",
            "menu_name",
            "allergen",
            "allergen_name",
            "contains",
            "may_contain",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class NutritionTrackingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = NutritionTracking
        fields = [
            "id",
            "user",
            "user_name",
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
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class VendorManagementSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = VendorManagement
        fields = [
            "id",
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
            "status_display",
            "rating",
            "total_orders",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_orders", "created_at", "updated_at"]


class VendorOrderSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = VendorOrder
        fields = [
            "id",
            "vendor",
            "vendor_name",
            "order_number",
            "items",
            "total_amount",
            "status",
            "status_display",
            "order_date",
            "expected_delivery",
            "actual_delivery",
            "payment_status",
            "created_by",
            "created_by_name",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "order_date", "created_at", "updated_at"]


class ProductionPlanningSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default=None)
    variance = serializers.ReadOnlyField()

    class Meta:
        model = ProductionPlanning
        fields = [
            "id",
            "menu",
            "menu_name",
            "planned_quantity",
            "actual_quantity",
            "variance",
            "pre_order_count",
            "expected_walk_in",
            "status",
            "status_display",
            "assigned_to",
            "assigned_to_name",
            "prep_start_time",
            "prep_end_time",
            "serve_time",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WasteTrackingSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source="menu.name", read_only=True, default=None)
    waste_type_display = serializers.CharField(source="get_waste_type_display", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.full_name", read_only=True, default=None)

    class Meta:
        model = WasteTracking
        fields = [
            "id",
            "menu",
            "menu_name",
            "date",
            "waste_type",
            "waste_type_display",
            "item_name",
            "quantity_wasted",
            "unit",
            "estimated_cost",
            "reason",
            "prevention_notes",
            "recorded_by",
            "recorded_by_name",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
