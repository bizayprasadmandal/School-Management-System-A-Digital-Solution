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
        read_only_fields = ["id", "school", "created_at", "updated_at"]

    def validate(self, attrs):
        # Duplicate (school, date, meal_type) would hit the DB unique
        # constraint → 500; surface a clean 400 instead.
        date = attrs.get("date")
        meal_type = attrs.get("meal_type")
        if date is not None and meal_type:
            user = self.context["request"].user
            if MealMenu.objects.filter(school_id=user.school_id, date=date, meal_type=meal_type).exists():
                raise serializers.ValidationError({"detail": f"A {meal_type} menu already exists for {date}."})
        return attrs


class MealPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealPlan
        fields = [
            "id",
            "school",
            "id",
            "name",
            "description",
            "meals_included",
            "price_per_period",
            "period_days",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "school", "created_at"]


class MealBookingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    meal_plan_name = serializers.CharField(source="meal_plan.name", read_only=True)

    class Meta:
        model = MealBooking
        fields = [
            "id",
            "school",
            "id",
            "user",
            "menu",
            "meal_plan",
            "booking_date",
            "meal_type",
            "status",
            "notes",
            "cancelled_at",
            "created_at",
            "user_name",
            "menu_name",
            "meal_plan_name",
        ]
        read_only_fields = ["id", "school", "booking_date", "created_at"]

    def validate(self, attrs):
        # A user can only hold one booking per menu (model unique_together) —
        # surface a clean 400 instead of an IntegrityError 500.
        user = attrs.get("user")
        menu = attrs.get("menu")
        if user is not None and menu is not None:
            if MealBooking.objects.filter(user=user, menu=menu).exists():
                raise serializers.ValidationError({"detail": "A booking already exists for this user and menu."})
        return attrs


class DietaryRestrictionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = DietaryRestriction
        fields = ["id", "id", "user", "restriction_type", "severity", "notes", "created_at", "user_name"]
        read_only_fields = ["id", "created_at"]


class PointOfSaleSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    transaction_type_display = serializers.CharField(source="get_transaction_type_display", read_only=True)
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)

    class Meta:
        model = PointOfSale
        fields = [
            "id",
            "school",
            "id",
            "user",
            "transaction_type",
            "amount",
            "payment_method",
            "menu",
            "balance_before",
            "balance_after",
            "is_successful",
            "meal_benefit_applied",
            "benefit_type",
            "user_name",
            "menu_name",
            "transaction_type_display",
            "payment_method_display",
        ]
        read_only_fields = ["id", "school"]


class PaymentTransactionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    meal_plan_name = serializers.CharField(source="meal_plan.name", read_only=True)
    transaction_type_display = serializers.CharField(source="get_transaction_type_display", read_only=True)
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            "id",
            "school",
            "id",
            "user",
            "transaction_type",
            "amount",
            "payment_method",
            "status",
            "transaction_id",
            "receipt_number",
            "account_balance_before",
            "account_balance_after",
            "meal_plan",
            "user_name",
            "meal_plan_name",
            "transaction_type_display",
            "payment_method_display",
            "status_display",
        ]
        read_only_fields = ["id", "school", "created_at"]


class FreeReducedLunchSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    eligibility_type_display = serializers.CharField(source="get_eligibility_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    def get_student_name(self, obj):
        student = getattr(obj, "student", None)
        if student and student.user_id:
            return student.user.get_full_name()
        return None

    class Meta:
        model = FreeReducedLunch
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
            "eligibility_type_display",
            "status_display",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CafeteriaInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaInventory
        fields = [
            "id",
            "school",
            "id",
            "name",
            "category",
            "description",
            "quantity",
            "unit",
            "minimum_stock",
            "unit_cost",
            "total_value",
            "supplier",
            "storage_location",
            "temperature_requirement",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class USDAComplianceReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source="get_report_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = USDAComplianceReport
        fields = [
            "id",
            "school",
            "id",
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
            "report_type_display",
            "status_display",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PreOrderSystemSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PreOrderSystem
        fields = [
            "id",
            "school",
            "id",
            "user",
            "menu",
            "quantity",
            "unit_price",
            "total_price",
            "special_requests",
            "status",
            "payment_status",
            "transaction",
            "user_name",
            "menu_name",
            "status_display",
        ]
        read_only_fields = ["id", "updated_at"]


class StudentAccountSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = StudentAccount
        fields = [
            "id",
            "school",
            "id",
            "user",
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
            "user_name",
            "status_display",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AllergenManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllergenManagement
        fields = [
            "id",
            "school",
            "id",
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
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    allergen_name = serializers.CharField(source="allergen.name", read_only=True)

    class Meta:
        model = MenuItemAllergen
        fields = [
            "id",
            "id",
            "menu",
            "allergen",
            "contains",
            "may_contain",
            "notes",
            "created_at",
            "menu_name",
            "allergen_name",
        ]
        read_only_fields = ["id", "created_at"]


class NutritionTrackingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = NutritionTracking
        fields = [
            "id",
            "school",
            "id",
            "user",
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
            "user_name",
        ]
        read_only_fields = ["id", "created_at"]


class VendorManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorManagement
        fields = [
            "id",
            "school",
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
            "rating",
            "total_orders",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VendorOrderSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_status_display = serializers.CharField(source="get_payment_status_display", read_only=True)

    class Meta:
        model = VendorOrder
        fields = [
            "id",
            "school",
            "id",
            "vendor",
            "order_number",
            "items",
            "total_amount",
            "status",
            "order_date",
            "expected_delivery",
            "actual_delivery",
            "payment_status",
            "created_by",
            "vendor_name",
            "status_display",
            "payment_status_display",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductionPlanningSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ProductionPlanning
        fields = [
            "id",
            "school",
            "id",
            "menu",
            "planned_quantity",
            "actual_quantity",
            "pre_order_count",
            "expected_walk_in",
            "status",
            "assigned_to",
            "prep_start_time",
            "prep_end_time",
            "serve_time",
            "menu_name",
            "status_display",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WasteTrackingSerializer(serializers.ModelSerializer):
    menu_name = serializers.CharField(source="menu.name", read_only=True)
    waste_type_display = serializers.CharField(source="get_waste_type_display", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = WasteTracking
        fields = [
            "id",
            "school",
            "id",
            "menu",
            "date",
            "waste_type",
            "item_name",
            "quantity_wasted",
            "unit",
            "estimated_cost",
            "reason",
            "prevention_notes",
            "recorded_by",
            "menu_name",
            "waste_type_display",
            "recorded_by_name",
        ]
        read_only_fields = ["id", "created_at"]


class OnlineOrderSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)

    def get_student_name(self, obj):
        student = getattr(obj, "student", None)
        if student and student.user_id:
            return student.user.get_full_name()
        return None

    class Meta:
        model = OnlineOrder
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
            "status_display",
            "payment_method_display",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OnlineOrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    order_status = serializers.CharField(source="order.status", read_only=True)

    class Meta:
        model = OnlineOrderItem
        fields = [
            "id",
            "id",
            "order",
            "menu_item",
            "item_name",
            "quantity",
            "unit_price",
            "total_price",
            "special_requests",
            "created_at",
            "menu_item_name",
            "order_status",
        ]
        read_only_fields = ["id", "created_at"]


class MealDeliverySerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    class_group_name = serializers.CharField(source="class_group.name", read_only=True)
    delivered_by_name = serializers.CharField(source="delivered_by.get_full_name", read_only=True)

    class Meta:
        model = MealDelivery
        fields = [
            "id",
            "school",
            "id",
            "status",
            "delivery_date",
            "delivery_time",
            "delivery_location",
            "class_group",
            "meals_ordered",
            "meals_delivered",
            "meals_returned",
            "delivered_by",
            "created_at",
            "completed_at",
            "status_display",
            "class_group_name",
            "delivered_by_name",
        ]
        read_only_fields = ["id", "created_at"]


class CashRegisterSerializer(serializers.ModelSerializer):
    opened_by_name = serializers.CharField(source="opened_by.get_full_name", read_only=True)
    closed_by_name = serializers.CharField(source="closed_by.get_full_name", read_only=True)

    class Meta:
        model = CashRegister
        fields = [
            "id",
            "school",
            "id",
            "register_name",
            "location",
            "is_active",
            "is_open",
            "opening_amount",
            "opened_by",
            "opened_at",
            "closing_amount",
            "expected_amount",
            "variance",
            "closed_by",
            "opened_by_name",
            "closed_by_name",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DailySalesSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySalesSummary
        fields = [
            "id",
            "school",
            "id",
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
    check_type_display = serializers.CharField(source="get_check_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    checked_by_name = serializers.CharField(source="checked_by.get_full_name", read_only=True)

    class Meta:
        model = FoodSafetyCheck
        fields = [
            "id",
            "school",
            "id",
            "check_type",
            "check_date",
            "status",
            "checked_by",
            "temperature_reading",
            "location",
            "findings",
            "corrective_actions",
            "compliance_notes",
            "photo",
            "created_at",
            "check_type_display",
            "status_display",
            "checked_by_name",
        ]
        read_only_fields = ["id", "created_at"]


class FoodSafetyIncidentSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.get_full_name", read_only=True)

    class Meta:
        model = FoodSafetyIncident
        fields = [
            "id",
            "school",
            "id",
            "title",
            "description",
            "severity",
            "status",
            "reported_by",
            "people_affected",
            "root_cause",
            "investigation_notes",
            "corrective_actions",
            "preventive_measures",
            "resolved_at",
            "severity_display",
            "status_display",
            "reported_by_name",
        ]
        read_only_fields = ["id", "created_at"]


class CafeteriaStaffSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = CafeteriaStaff
        fields = [
            "id",
            "school",
            "id",
            "user",
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
            "user_name",
            "role_display",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CafeteriaFeedbackSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    staff_member_name = serializers.CharField(source="staff_member.user.get_full_name", read_only=True)
    feedback_type_display = serializers.CharField(source="get_feedback_type_display", read_only=True)
    responded_by_name = serializers.CharField(source="responded_by.get_full_name", read_only=True)

    def get_student_name(self, obj):
        student = getattr(obj, "student", None)
        if student and student.user_id:
            return student.user.get_full_name()
        return None

    class Meta:
        model = CafeteriaFeedback
        fields = [
            "id",
            "school",
            "id",
            "student",
            "staff_member",
            "feedback_type",
            "rating",
            "comment",
            "meal_rated",
            "date_of_experience",
            "response",
            "responded_by",
            "student_name",
            "staff_member_name",
            "feedback_type_display",
            "responded_by_name",
        ]
        read_only_fields = ["id", "created_at"]


class MealPreOrderSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    def get_student_name(self, obj):
        student = getattr(obj, "student", None)
        if student and student.user_id:
            return student.user.get_full_name()
        return None

    class Meta:
        model = MealPreOrder
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
            "status_display",
        ]
        read_only_fields = ["id", "created_at"]


class NutritionAnalysisSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    analyzed_by_name = serializers.CharField(source="analyzed_by.get_full_name", read_only=True)

    class Meta:
        model = NutritionAnalysis
        fields = [
            "id",
            "id",
            "menu_item",
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
            "menu_item_name",
            "analyzed_by_name",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CafeteriaEquipmentSerializer(serializers.ModelSerializer):
    equipment_type_display = serializers.CharField(source="get_equipment_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = CafeteriaEquipment
        fields = [
            "id",
            "school",
            "id",
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
            "equipment_type_display",
            "status_display",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CafeteriaReservationSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source="requested_by.get_full_name", read_only=True)
    reservation_type_display = serializers.CharField(source="get_reservation_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)

    class Meta:
        model = CafeteriaReservation
        fields = [
            "id",
            "school",
            "id",
            "requested_by",
            "reservation_type",
            "title",
            "description",
            "reservation_date",
            "start_time",
            "end_time",
            "expected_guests",
            "status",
            "approved_by",
            "requested_by_name",
            "reservation_type_display",
            "status_display",
            "approved_by_name",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CafeteriaAlertSerializer(serializers.ModelSerializer):
    alert_type_display = serializers.CharField(source="get_alert_type_display", read_only=True)
    severity_display = serializers.CharField(source="get_severity_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    acknowledged_by_name = serializers.CharField(source="acknowledged_by.get_full_name", read_only=True)
    resolved_by_name = serializers.CharField(source="resolved_by.get_full_name", read_only=True)

    class Meta:
        model = CafeteriaAlert
        fields = [
            "id",
            "school",
            "id",
            "alert_type",
            "severity",
            "status",
            "title",
            "description",
            "acknowledged_by",
            "resolved_by",
            "resolution_notes",
            "resolved_at",
            "created_at",
            "alert_type_display",
            "severity_display",
            "status_display",
            "acknowledged_by_name",
            "resolved_by_name",
        ]
        read_only_fields = ["id", "created_at"]


class MealSubscriptionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    plan_type_display = serializers.CharField(source="get_plan_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    def get_student_name(self, obj):
        student = getattr(obj, "student", None)
        if student and student.user_id:
            return student.user.get_full_name()
        return None

    class Meta:
        model = MealSubscription
        fields = [
            "id",
            "school",
            "id",
            "student",
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
            "student_name",
            "plan_type_display",
            "status_display",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SubscriptionUsageSerializer(serializers.ModelSerializer):
    subscription_label = serializers.CharField(source="subscription.id", read_only=True)
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    meal_type_display = serializers.CharField(source="get_meal_type_display", read_only=True)

    class Meta:
        model = SubscriptionUsage
        fields = [
            "id",
            "id",
            "subscription",
            "meal_date",
            "meal_type",
            "menu_item",
            "used",
            "skipped",
            "recorded_at",
            "subscription_label",
            "menu_item_name",
            "meal_type_display",
        ]
        read_only_fields = ["id"]


class CafeteriaAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaAnalytics
        fields = [
            "id",
            "school",
            "id",
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
    meal_type_display = serializers.CharField(source="get_meal_type_display", read_only=True)

    class Meta:
        model = CafeteriaCapacity
        fields = [
            "id",
            "school",
            "id",
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
            "meal_type_display",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MenuItemRatingSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source="menu_item.name", read_only=True)
    student_name = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        student = getattr(obj, "student", None)
        if student and student.user_id:
            return student.user.get_full_name()
        return None

    class Meta:
        model = MenuItemRating
        fields = [
            "id",
            "id",
            "menu_item",
            "student",
            "rating",
            "review",
            "would_order_again",
            "date_rated",
            "created_at",
            "menu_item_name",
            "student_name",
        ]
        read_only_fields = ["id", "created_at"]


class CafeteriaHolidayScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CafeteriaHolidaySchedule
        fields = [
            "id",
            "school",
            "id",
            "date",
            "is_closed",
            "special_hours",
            "opening_time",
            "closing_time",
            "reason",
            "special_menu",
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
    item_name = serializers.CharField(source="item.name", read_only=True)
    alert_type_display = serializers.CharField(source="get_alert_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = CafeteriaInventoryAlert
        fields = [
            "id",
            "school",
            "id",
            "item",
            "alert_type",
            "status",
            "message",
            "current_quantity",
            "reorder_quantity",
            "acknowledged_by",
            "resolved_at",
            "created_at",
            "item_name",
            "alert_type_display",
            "status_display",
        ]
        read_only_fields = ["id", "created_at"]
