from django.contrib import admin
from .models import MealMenu, MealPlan, MealBooking, DietaryRestriction

@admin.register(MealMenu)
class MealMenuAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "meal_type", "price", "is_active"]
    list_filter = ["meal_type", "date", "is_active", "school"]
    search_fields = ["name", "items"]

@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price_per_period", "period_days", "is_active"]
    list_filter = ["is_active"]; search_fields = ["name"]

@admin.register(MealBooking)
class MealBookingAdmin(admin.ModelAdmin):
    list_display = ["user", "menu", "meal_type", "status", "booking_date"]
    list_filter = ["meal_type", "status"]; search_fields = ["user__full_name", "menu__name"]

@admin.register(DietaryRestriction)
class DietaryRestrictionAdmin(admin.ModelAdmin):
    list_display = ["user", "restriction_type", "severity"]
    list_filter = ["restriction_type"]; search_fields = ["user__full_name", "restriction_type"]
