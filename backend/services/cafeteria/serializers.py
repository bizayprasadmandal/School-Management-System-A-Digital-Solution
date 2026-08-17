"""Cafeteria serializers."""

from rest_framework import serializers

from .models import DietaryRestriction, MealBooking, MealMenu, MealPlan


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
