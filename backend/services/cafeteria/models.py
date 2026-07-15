"""Cafeteria / Meal Management — Menus, meal plans, bookings, dietary tracking."""

import uuid
from django.db import models
from services.auth.models import School, User


class MealMenu(models.Model):
    """Daily meal menus for the cafeteria."""

    class MealType(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast"
        LUNCH = "lunch", "Lunch"
        DINNER = "dinner", "Dinner"
        SNACK = "snack", "Snack"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="meal_menus")
    meal_type = models.CharField(max_length=20, choices=MealType.choices)
    name = models.CharField(max_length=200, help_text="Menu name, e.g. Monday Lunch")
    date = models.DateField()
    items = models.TextField(blank=True, help_text="Comma-separated list of food items")
    description = models.TextField(blank=True)
    calories = models.PositiveSmallIntegerField(null=True, blank=True)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_menus"
        unique_together = [("school", "date", "meal_type")]
        ordering = ["-date", "meal_type"]
    def __str__(self):
        return f"{self.date} - {self.get_meal_type_display()}: {self.name}"


class MealPlan(models.Model):
    """Meal plans/ subscriptions for students or staff."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="meal_plans")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    meals_included = models.CharField(max_length=100, blank=True, help_text="e.g. breakfast,lunch,dinner")
    price_per_period = models.DecimalField(max_digits=10, decimal_places=2)
    period_days = models.PositiveSmallIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_plans"
        ordering = ["name"]
    def __str__(self):
        return f"{self.name} - ${self.price_per_period}/{self.period_days}days"


class MealBooking(models.Model):
    """Student/staff meal bookings against a meal plan or ad-hoc."""

    class Status(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        ATTENDED = "attended", "Attended"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="meal_bookings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_bookings")
    menu = models.ForeignKey(MealMenu, on_delete=models.CASCADE, related_name="bookings")
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    booking_date = models.DateField(auto_now_add=True)
    meal_type = models.CharField(max_length=20, choices=MealMenu.MealType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    notes = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_bookings"
        unique_together = [("user", "menu")]
        ordering = ["-booking_date"]
    def __str__(self):
        return f"{self.user.full_name} - {self.menu}"


class DietaryRestriction(models.Model):
    """Dietary restrictions/preferences for students/staff."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dietary_restrictions")
    restriction_type = models.CharField(max_length=100, help_text="e.g. Vegetarian, Vegan, Gluten-Free, Nut Allergy")
    severity = models.CharField(max_length=50, blank=True, help_text="e.g. Allergy, Preference, Medical")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_dietary"
        unique_together = [("user", "restriction_type")]
        ordering = ["user", "restriction_type"]
    def __str__(self):
        return f"{self.user.full_name} - {self.restriction_type}"
