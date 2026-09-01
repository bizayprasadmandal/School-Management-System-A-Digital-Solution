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


class PointOfSale(models.Model):
    """POS checkout with PIN/barcode/biometric."""

    class PaymentMethod(models.TextChoices):
        PIN = "pin", "PIN"
        BARCODE = "barcode", "Barcode"
        BIOMETRIC = "biometric", "Biometric"
        CARD = "card", "Card Swipe"
        CASH = "cash", "Cash"

    class TransactionType(models.TextChoices):
        MEAL = "meal", "Meal Purchase"
        SNACK = "snack", "Snack Purchase"
        DRINK = "drink", "Drink Purchase"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="pos_transactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pos_transactions")
    # Transaction details
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    # Menu reference
    menu = models.ForeignKey(
        MealMenu, on_delete=models.SET_NULL, null=True, blank=True, related_name="pos_transactions"
    )
    # Account
    balance_before = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Status
    is_successful = models.BooleanField(default=True)
    # Meal benefits
    meal_benefit_applied = models.BooleanField(default=False)
    benefit_type = models.CharField(
        max_length=20,
        choices=[("free", "Free"), ("reduced", "Reduced"), ("paid", "Paid")],
        default="paid",
    )
    # Notes
    notes = models.TextField(blank=True)
    transaction_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_pos"
        ordering = ["-transaction_time"]

    def __str__(self):
        return f"{self.user.full_name} - {self.get_transaction_type_display()} - ${self.amount}"


class PaymentTransaction(models.Model):
    """Online payment processing."""

    class PaymentMethod(models.TextChoices):
        CREDIT_CARD = "credit_card", "Credit Card"
        DEBIT_CARD = "debit_card", "Debit Card"
        ACH = "ach", "ACH Transfer"
        CHECK = "check", "Check"
        CASH = "cash", "Cash"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    class TransactionType(models.TextChoices):
        DEPOSIT = "deposit", "Account Deposit"
        MEAL_PURCHASE = "meal_purchase", "Meal Purchase"
        PLAN_PURCHASE = "plan_purchase", "Meal Plan Purchase"
        REFUND = "refund", "Refund"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="cafeteria_payments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cafeteria_payments")
    # Transaction details
    transaction_type = models.CharField(max_length=15, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PaymentMethod.choices)
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Payment info
    transaction_id = models.CharField(max_length=100, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    # Account impact
    account_balance_before = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    account_balance_after = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Reference
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
    booking = models.ForeignKey(MealBooking, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments")
    # Auto-replenish
    auto_replenish = models.BooleanField(default=False)
    replenish_threshold = models.DecimalField(
        max_digits=8, decimal_places=2, default=10, help_text="Auto-replenish when balance below this"
    )
    replenish_amount = models.DecimalField(max_digits=8, decimal_places=2, default=25)
    # Notes
    notes = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.full_name} - ${self.amount} ({self.get_status_display()})"


class FreeReducedLunch(models.Model):
    """Free/reduced lunch eligibility tracking."""

    class EligibilityType(models.TextChoices):
        FREE = "free", "Free Lunch"
        REDUCED = "reduced", "Reduced Lunch"
        PAID = "paid", "Paid"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        PENDING = "pending", "Pending Review"
        DENIED = "denied", "Denied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="free_reduced_lunch")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="meal_eligibility")
    # Eligibility
    eligibility_type = models.CharField(max_length=10, choices=EligibilityType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Application
    application_date = models.DateField()
    approval_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField()
    # Documentation
    application_number = models.CharField(max_length=50, blank=True)
    document_url = models.URLField(blank=True)
    # Household info
    household_size = models.PositiveSmallIntegerField(default=1)
    household_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Review
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_meal_eligibility"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_free_reduced"
        ordering = ["-application_date"]

    def __str__(self):
        return f"{self.student} - {self.get_eligibility_type_display()} ({self.get_status_display()})"

    @property
    def is_valid(self):
        from django.utils import timezone

        return self.status == self.Status.ACTIVE and self.expiry_date >= timezone.now().date()


class CafeteriaInventory(models.Model):
    """Real-time food inventory tracking."""

    class Category(models.TextChoices):
        PRODUCE = "produce", "Produce"
        DAIRY = "dairy", "Dairy"
        MEAT = "meat", "Meat/Poultry"
        GRAINS = "grains", "Grains"
        BEVERAGES = "beverages", "Beverages"
        FROZEN = "frozen", "Frozen"
        DRY_GOODS = "dry_goods", "Dry Goods"
        CONDIMENTS = "condiments", "Condiments"
        OTHER = "other", "Other"

    class Unit(models.TextChoices):
        KG = "kg", "Kilograms"
        GRAMS = "g", "Grams"
        LITERS = "l", "Liters"
        ML = "ml", "Milliliters"
        PIECES = "pcs", "Pieces"
        BOXES = "boxes", "Boxes"
        BAGS = "bags", "Bags"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="cafeteria_inventory")
    # Item info
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=15, choices=Category.choices)
    description = models.TextField(blank=True)
    # Stock
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=10, choices=Unit.choices)
    minimum_stock = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    # Cost
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Supplier
    supplier = models.ForeignKey(
        "VendorOrder", on_delete=models.SET_NULL, null=True, blank=True, related_name="supplied_items"
    )
    # Storage
    storage_location = models.CharField(max_length=100, blank=True)
    temperature_requirement = models.CharField(
        max_length=50, blank=True, help_text="e.g. Refrigerated, Frozen, Room Temp"
    )
    # Expiry
    expiry_date = models.DateField(null=True, blank=True)
    is_perishable = models.BooleanField(default=False)
    # Status
    is_active = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_inventory"
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.get_unit_display()})"

    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_stock


class USDAComplianceReport(models.Model):
    """Automated reimbursement claims."""

    class ReportType(models.TextChoices):
        DAILY = "daily", "Daily Report"
        MONTHLY = "monthly", "Monthly Report"
        QUARTERLY = "quarterly", "Quarterly Report"
        ANNUAL = "annual", "Annual Report"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="usda_reports")
    # Report details
    report_type = models.CharField(max_length=15, choices=ReportType.choices)
    title = models.CharField(max_length=200)
    # Period
    start_date = models.DateField()
    end_date = models.DateField()
    # Meal counts
    total_meals_served = models.PositiveIntegerField(default=0)
    free_meals = models.PositiveIntegerField(default=0)
    reduced_meals = models.PositiveIntegerField(default=0)
    paid_meals = models.PositiveIntegerField(default=0)
    # Financial
    total_reimbursement = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    per_meal_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    # Submission
    submitted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="submitted_usda_reports"
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    # Approval
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_usda_reports"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    # Documents
    report_url = models.URLField(blank=True)
    supporting_docs = models.JSONField(default=list, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_usda_reports"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def reimbursement_per_day(self):
        days = (self.end_date - self.start_date).days + 1
        if days > 0:
            return round(self.total_reimbursement / days, 2)
        return 0


class PreOrderSystem(models.Model):
    """Parents order meals online in advance."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        FULFILLED = "fulfilled", "Fulfilled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="pre_orders")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pre_orders")
    menu = models.ForeignKey(MealMenu, on_delete=models.CASCADE, related_name="pre_orders")
    # Order details
    quantity = models.PositiveSmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    # Special instructions
    special_requests = models.TextField(blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Payment
    payment_status = models.CharField(
        max_length=15,
        choices=[("unpaid", "Unpaid"), ("paid", "Paid"), ("refunded", "Refunded")],
        default="unpaid",
    )
    transaction = models.ForeignKey(
        PaymentTransaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="pre_orders"
    )
    # Cutoff
    order_deadline = models.DateTimeField(help_text="Pre-order cutoff time")
    # Notes
    notes = models.TextField(blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_pre_orders"
        ordering = ["-ordered_at"]

    def __str__(self):
        return f"{self.user.full_name} - {self.menu} (x{self.quantity})"


class StudentAccount(models.Model):
    """Balance tracking, auto-replenish."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_accounts")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cafeteria_account")
    # Balance
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    low_balance_threshold = models.DecimalField(
        max_digits=8, decimal_places=2, default=10, help_text="Alert when balance below this"
    )
    # Auto-replenish
    auto_replenish_enabled = models.BooleanField(default=False)
    replenish_threshold = models.DecimalField(max_digits=8, decimal_places=2, default=10)
    replenish_amount = models.DecimalField(max_digits=8, decimal_places=2, default=25)
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Limits
    daily_spending_limit = models.DecimalField(
        max_digits=8, decimal_places=2, default=50, help_text="Maximum daily spending"
    )
    # Statistics
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deposited = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_accounts"

    def __str__(self):
        return f"{self.user.full_name} - Balance: ${self.balance}"

    @property
    def is_low_balance(self):
        return self.balance <= self.low_balance_threshold


class AllergenManagement(models.Model):
    """Track and flag allergens."""

    class Severity(models.TextChoices):
        MILD = "mild", "Mild"
        MODERATE = "moderate", "Moderate"
        SEVERE = "severe", "Severe"
        LIFE_THREATENING = "life_threatening", "Life-Threatening"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="allergens")
    # Allergen info
    name = models.CharField(max_length=100, help_text="e.g. Peanuts, Milk, Gluten")
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MODERATE)
    # Common symptoms
    symptoms = models.TextField(blank=True, help_text="Common symptoms of reaction")
    # Treatment
    treatment_notes = models.TextField(blank=True, help_text="What to do in case of reaction")
    # Status
    is_active = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_allergens"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"


class MenuItemAllergen(models.Model):
    """Link menu items to allergens."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu = models.ForeignKey(MealMenu, on_delete=models.CASCADE, related_name="menu_allergens")
    allergen = models.ForeignKey(AllergenManagement, on_delete=models.CASCADE, related_name="menu_items")
    # Info
    contains = models.BooleanField(default=True, help_text="Does this menu item contain this allergen?")
    may_contain = models.BooleanField(default=False, help_text="May contain traces")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_menu_allergens"
        unique_together = [("menu", "allergen")]

    def __str__(self):
        return f"{self.menu} - {self.allergen}"


class NutritionTracking(models.Model):
    """Daily/weekly nutrition reports."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="nutrition_tracking")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="nutrition_tracking")
    # Date
    date = models.DateField()
    # Macros
    calories = models.PositiveIntegerField(default=0)
    protein = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Grams")
    carbohydrates = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Grams")
    fat = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Grams")
    fiber = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Grams")
    # Micros
    vitamins = models.JSONField(default=dict, blank=True)
    minerals = models.JSONField(default=dict, blank=True)
    # Meals
    meals = models.JSONField(default=list, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_nutrition"
        unique_together = [("user", "date")]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.full_name} - {self.date} ({self.calories} cal)"


class VendorManagement(models.Model):
    """Supplier management."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPENDED = "suspended", "Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="cafeteria_vendors")
    # Vendor info
    name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    # Products
    products_offered = models.JSONField(default=list, blank=True)
    # Terms
    payment_terms = models.CharField(max_length=100, blank=True)
    delivery_schedule = models.CharField(max_length=100, blank=True)
    minimum_order = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Performance
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_vendors"
        ordering = ["name"]

    def __str__(self):
        return self.name


class VendorOrder(models.Model):
    """Supplier ordering and tracking."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        CONFIRMED = "confirmed", "Confirmed"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="vendor_orders")
    vendor = models.ForeignKey(VendorManagement, on_delete=models.CASCADE, related_name="orders")
    # Order details
    order_number = models.CharField(max_length=50, blank=True)
    items = models.JSONField(default=list, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    # Dates
    order_date = models.DateField(auto_now_add=True)
    expected_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateField(null=True, blank=True)
    # Payment
    payment_status = models.CharField(
        max_length=15,
        choices=[("unpaid", "Unpaid"), ("paid", "Paid"), ("partial", "Partial")],
        default="unpaid",
    )
    # Created by
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_vendor_orders"
    )
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_vendor_orders"
        ordering = ["-order_date"]

    def __str__(self):
        return f"Order #{self.order_number or self.id} - {self.vendor.name}"


class ProductionPlanning(models.Model):
    """Kitchen production counts."""

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="production_plans")
    menu = models.ForeignKey(MealMenu, on_delete=models.CASCADE, related_name="production_plans")
    # Production details
    planned_quantity = models.PositiveIntegerField(default=0)
    actual_quantity = models.PositiveIntegerField(default=0)
    # Pre-orders count
    pre_order_count = models.PositiveIntegerField(default=0)
    expected_walk_in = models.PositiveIntegerField(default=0)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PLANNED)
    # Staff
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="production_plans"
    )
    # Timing
    prep_start_time = models.TimeField(null=True, blank=True)
    prep_end_time = models.TimeField(null=True, blank=True)
    serve_time = models.TimeField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_production"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.menu} - Planned: {self.planned_quantity}"

    @property
    def variance(self):
        return self.actual_quantity - self.planned_quantity


class WasteTracking(models.Model):
    """Monitor food waste."""

    class WasteType(models.TextChoices):
        PREP = "prep", "Prep Waste"
        PLATE = "plate", "Plate Waste"
        SPOILED = "spoiled", "Spoiled/Expired"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="waste_tracking")
    menu = models.ForeignKey(MealMenu, on_delete=models.SET_NULL, null=True, blank=True, related_name="waste_records")
    # Date
    date = models.DateField()
    # Waste details
    waste_type = models.CharField(max_length=10, choices=WasteType.choices)
    item_name = models.CharField(max_length=200)
    quantity_wasted = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=20, blank=True)
    # Cost
    estimated_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Reason
    reason = models.TextField(blank=True)
    # Prevention
    prevention_notes = models.TextField(blank=True)
    # Recorded by
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="recorded_waste"
    )
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_waste"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.item_name} - {self.quantity_wasted} ({self.get_waste_type_display()})"


# =============================================================================
# NEW MODELS: Online Ordering
# =============================================================================


class OnlineOrder(models.Model):
    """Online food ordering system."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready for Pickup"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="online_orders")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="online_orders")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Items
    items = models.JSONField(default=list, help_text="List of ordered items")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Delivery
    pickup_time = models.TimeField(null=True, blank=True)
    delivery_location = models.CharField(max_length=200, blank=True)
    delivery_required = models.BooleanField(default=False)
    # Payment
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, blank=True)
    # Notes
    special_instructions = models.TextField(blank=True)
    # Metadata
    ordered_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_online_orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.student} ({self.get_status_display()})"


class OnlineOrderItem(models.Model):
    """Individual items in an online order."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(OnlineOrder, on_delete=models.CASCADE, related_name="order_items")
    menu_item = models.ForeignKey("MealMenu", on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_requests = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_online_order_items"

    def __str__(self):
        return f"{self.quantity}x {self.item_name}"


# =============================================================================
# NEW MODELS: Meal Delivery
# =============================================================================


class MealDelivery(models.Model):
    """Meal delivery to classrooms/desks."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_TRANSIT = "in_transit", "In Transit"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="meal_deliveries")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    # Schedule
    delivery_date = models.DateField()
    delivery_time = models.TimeField()
    delivery_location = models.CharField(max_length=200)
    class_group = models.CharField(max_length=50, blank=True)
    # Items
    meals_ordered = models.PositiveIntegerField(default=0)
    meals_delivered = models.PositiveIntegerField(default=0)
    meals_returned = models.PositiveIntegerField(default=0)
    # Personnel
    delivered_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "cafeteria_meal_deliveries"
        ordering = ["-delivery_date"]

    def __str__(self):
        return f"Delivery - {self.delivery_location} ({self.delivery_date})"


# =============================================================================
# NEW MODELS: Cash Register / POS
# =============================================================================


class CashRegister(models.Model):
    """Cash register management."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="cash_registers")
    register_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    is_open = models.BooleanField(default=False)
    # Opening
    opening_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    opened_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    # Closing
    closing_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expected_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    variance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    closed_by = models.ForeignKey(
        "auth_service.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="registers_closed"
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_cash_registers"

    def __str__(self):
        return f"{self.register_name} ({'Open' if self.is_open else 'Closed'})"


class DailySalesSummary(models.Model):
    """Daily sales summary."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="daily_sales_summaries")
    date = models.DateField()
    # Sales
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_transactions = models.PositiveIntegerField(default=0)
    total_items_sold = models.PositiveIntegerField(default=0)
    avg_transaction_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # By payment type
    cash_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    card_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    account_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    free_meal_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # By meal
    breakfast_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    lunch_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    snack_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    dinner_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Top items
    top_items = models.JSONField(default=list, blank=True)
    # Cost
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Metadata
    prepared_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_daily_sales_summaries"
        unique_together = [("school", "date")]
        ordering = ["-date"]

    def __str__(self):
        return f"Sales Summary - {self.date} (${self.total_sales})"


# =============================================================================
# NEW MODELS: Food Safety
# =============================================================================


class FoodSafetyCheck(models.Model):
    """Food safety and hygiene checks."""

    class CheckType(models.TextChoices):
        TEMPERATURE = "temperature", "Temperature Check"
        CLEANLINESS = "cleanliness", "Cleanliness"
        STORAGE = "storage", "Storage Check"
        PERSONAL_HYGIENE = "hygiene", "Personal Hygiene"
        EQUIPMENT = "equipment", "Equipment Check"
        WASTE = "waste", "Waste Management"

    class Status(models.TextChoices):
        PASS = "pass", "Pass"
        FAIL = "fail", "Fail"
        CONDITIONAL = "conditional", "Conditional"
        PENDING = "pending", "Pending Review"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="food_safety_checks")
    check_type = models.CharField(max_length=15, choices=CheckType.choices)
    check_date = models.DateField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Details
    checked_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True)
    temperature_reading = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    # Findings
    findings = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    compliance_notes = models.TextField(blank=True)
    # File
    photo = models.ImageField(upload_to="cafeteria/safety_checks/", null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_food_safety_checks"
        ordering = ["-check_date"]

    def __str__(self):
        return f"{self.get_check_type_display()} - {self.get_status_display()} ({self.check_date})"


class FoodSafetyIncident(models.Model):
    """Food safety incidents."""

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        REPORTED = "reported", "Reported"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="food_safety_incidents")
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.REPORTED)
    # People affected
    reported_by = models.ForeignKey(
        "auth_service.User", on_delete=models.SET_NULL, null=True, related_name="food_safety_incidents_reported"
    )
    people_affected = models.PositiveIntegerField(default=0)
    # Investigation
    root_cause = models.TextField(blank=True)
    investigation_notes = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    preventive_measures = models.TextField(blank=True)
    # Resolution
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        "auth_service.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="food_safety_incidents_resolved",
    )
    # Metadata
    incident_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_food_safety_incidents"
        ordering = ["-incident_date"]

    def __str__(self):
        return f"{self.title} ({self.get_severity_display()})"


# =============================================================================
# NEW MODELS: Cafeteria Staff
# =============================================================================


class CafeteriaStaff(models.Model):
    """Cafeteria staff management."""

    class Role(models.TextChoices):
        COOK = "cook", "Cook"
        ASSISTANT = "assistant", "Assistant"
        CASHIER = "cashier", "Cashier"
        MANAGER = "manager", "Manager"
        CLEANER = "cleaner", "Cleaner"
        DELIVERY = "delivery", "Delivery"
        SUPERVISOR = "supervisor", "Supervisor"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="cafeteria_staff")
    user = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="cafeteria_roles")
    role = models.CharField(max_length=15, choices=Role.choices)
    # Schedule
    shift_start = models.TimeField(null=True, blank=True)
    shift_end = models.TimeField(null=True, blank=True)
    days_of_week = models.JSONField(default=list, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    is_certified = models.BooleanField(default=False)
    certification_expiry = models.DateField(null=True, blank=True)
    # Performance
    performance_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_staff"
        unique_together = [("school", "user", "role")]

    def __str__(self):
        return f"{self.user.full_name} ({self.get_role_display()})"


# =============================================================================
# NEW MODELS: Customer Feedback
# =============================================================================


class CafeteriaFeedback(models.Model):
    """Customer feedback on food and service."""

    class FeedbackType(models.TextChoices):
        FOOD_QUALITY = "food", "Food Quality"
        SERVICE = "service", "Service"
        CLEANLINESS = "cleanliness", "Cleanliness"
        PRICE = "price", "Price/Value"
        WAIT_TIME = "wait", "Wait Time"
        GENERAL = "general", "General"

    class Rating(models.IntegerChoices):
        VERY_POOR = 1, "Very Poor"
        POOR = 2, "Poor"
        AVERAGE = 3, "Average"
        GOOD = 4, "Good"
        EXCELLENT = 5, "Excellent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="cafeteria_feedbacks")
    student = models.ForeignKey(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="cafeteria_feedbacks"
    )
    staff_member = models.ForeignKey(
        "auth_service.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cafeteria_feedback_received",
    )
    # Feedback
    feedback_type = models.CharField(max_length=15, choices=FeedbackType.choices)
    rating = models.IntegerField(choices=Rating.choices)
    comment = models.TextField(blank=True)
    # Specifics
    meal_rated = models.ForeignKey(
        "MealMenu", on_delete=models.SET_NULL, null=True, blank=True, related_name="feedbacks"
    )
    date_of_experience = models.DateField(null=True, blank=True)
    # Response
    response = models.TextField(blank=True)
    responded_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    # Anonymous
    is_anonymous = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_feedbacks"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_feedback_type_display()} - {self.get_rating_display()} ({self.created_at})"


# =============================================================================
# NEW MODELS: Meal Pre-order
# =============================================================================


class MealPreOrder(models.Model):
    """Pre-order system for meals."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready"
        COLLECTED = "collected", "Collected"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="meal_pre_orders")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="meal_pre_orders")
    # Order details
    meal_date = models.DateField()
    meal_type = models.CharField(
        max_length=10, choices=[("breakfast", "Breakfast"), ("lunch", "Lunch"), ("dinner", "Dinner")]
    )
    menu_items = models.JSONField(default=list)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Payment
    paid = models.BooleanField(default=False)
    paid_via = models.CharField(max_length=20, blank=True)
    # Pickup
    pickup_time = models.TimeField(null=True, blank=True)
    pickup_location = models.CharField(max_length=200, blank=True)
    collected_at = models.DateTimeField(null=True, blank=True)
    # Notes
    special_instructions = models.TextField(blank=True)
    # Metadata
    ordered_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_meal_pre_orders"
        ordering = ["-meal_date"]

    def __str__(self):
        return f"Pre-order - {self.student} ({self.meal_date})"


# =============================================================================
# NEW MODELS: Nutrition Analysis
# =============================================================================


class NutritionAnalysis(models.Model):
    """Nutritional analysis for menu items."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.OneToOneField("MealMenu", on_delete=models.CASCADE, related_name="nutrition_analysis")
    # Macros
    calories = models.PositiveIntegerField(default=0)
    protein_g = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    carbohydrates_g = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fat_g = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    fiber_g = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    sugar_g = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    sodium_mg = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Vitamins (optional)
    vitamin_a = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    vitamin_c = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    calcium = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    iron = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    # Ratings
    health_score = models.DecimalField(max_digits=3, decimal_places=1, default=5, help_text="1-10 scale")
    is_healthy_choice = models.BooleanField(default=True)
    # Metadata
    analyzed_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_nutrition_analysis"

    def __str__(self):
        return f"Nutrition: {self.menu_item} ({self.calories} cal)"


# =============================================================================
# NEW MODELS: Cafeteria Equipment
# =============================================================================


class CafeteriaEquipment(models.Model):
    """Cafeteria kitchen equipment tracking."""

    class EquipmentType(models.TextChoices):
        OVEN = "oven", "Oven"
        REFRIGERATOR = "fridge", "Refrigerator"
        FREEZER = "freezer", "Freezer"
        DISHWASHER = "dishwasher", "Dishwasher"
        MIXER = "mixer", "Mixer"
        FRYER = "fryer", "Fryer"
        STEAMER = "steamer", "Steamer"
        WARMER = "warmer", "Food Warmer"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        WORKING = "working", "Working"
        MAINTENANCE = "maintenance", "Under Maintenance"
        BROKEN = "broken", "Broken"
        RETIRED = "retired", "Retired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="cafeteria_equipment")
    name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=15, choices=EquipmentType.choices)
    asset_tag = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.WORKING)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_equipment"

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Cafeteria Reservation
# =============================================================================


class CafeteriaReservation(models.Model):
    """Reservation for cafeteria space (events, meetings)."""

    class ReservationType(models.TextChoices):
        EVENT = "event", "Event"
        MEETING = "meeting", "Meeting"
        CELEBRATION = "celebration", "Celebration"
        MEETING_LUNCH = "lunch_meeting", "Lunch Meeting"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="cafeteria_reservations")
    requested_by = models.ForeignKey(
        "auth_service.User", on_delete=models.CASCADE, related_name="cafeteria_reservations"
    )
    reservation_type = models.CharField(max_length=15, choices=ReservationType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Schedule
    reservation_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    # Capacity
    expected_guests = models.PositiveIntegerField(default=10)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    # Menu
    menu_items = models.JSONField(default=list, blank=True)
    special_requests = models.TextField(blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_reservations"
        ordering = ["-reservation_date"]

    def __str__(self):
        return f"{self.title} ({self.reservation_date})"


# =============================================================================
# NEW MODELS: Cafeteria Alerts
# =============================================================================


class CafeteriaAlert(models.Model):
    """Cafeteria system alerts."""

    class AlertType(models.TextChoices):
        LOW_INVENTORY = "inventory", "Low Inventory"
        EQUIPMENT_FAILURE = "equipment", "Equipment Failure"
        SAFETY_ISSUE = "safety", "Safety Issue"
        FOOD_WASTE = "waste", "High Food Waste"
        OVERBUDGET = "budget", "Over Budget"
        STAFF_SHORTAGE = "staff", "Staff Shortage"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="cafeteria_alerts")
    alert_type = models.CharField(max_length=15, choices=AlertType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    # Actions
    acknowledged_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    resolved_by = models.ForeignKey(
        "auth_service.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cafeteria_alert_resolutions",
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title}"


# =============================================================================
# NEW MODELS: Meal Subscription
# =============================================================================


class MealSubscription(models.Model):
    """Meal subscription plans for students."""

    class PlanType(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        YEARLY = "yearly", "Yearly"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="meal_subscriptions")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="meal_subscriptions")
    plan_type = models.CharField(max_length=15, choices=PlanType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Meals
    meals_included = models.JSONField(default=list, help_text="Which meals are included")
    meals_per_week = models.PositiveIntegerField(default=5)
    # Pricing
    price_per_meal = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    next_billing_date = models.DateField(null=True, blank=True)
    # Payment
    payment_method = models.CharField(max_length=20, blank=True)
    auto_renew = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_meal_subscriptions"

    def __str__(self):
        return f"{self.student} - {self.get_plan_type_display()} ({self.get_status_display()})"


class SubscriptionUsage(models.Model):
    """Track subscription meal usage."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(MealSubscription, on_delete=models.CASCADE, related_name="usage_records")
    meal_date = models.DateField()
    meal_type = models.CharField(max_length=10)
    menu_item = models.ForeignKey("MealMenu", on_delete=models.SET_NULL, null=True, blank=True)
    # Tracking
    used = models.BooleanField(default=True)
    skipped = models.BooleanField(default=False)
    # Metadata
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_subscription_usage"
        unique_together = [("subscription", "meal_date", "meal_type")]

    def __str__(self):
        return f"Usage: {self.subscription.student} ({self.meal_date})"


# =============================================================================
# NEW MODELS: Cafeteria Analytics
# =============================================================================


class CafeteriaAnalytics(models.Model):
    """Cafeteria performance analytics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="cafeteria_analytics")
    date = models.DateField()
    # Visitors
    total_visitors = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    avg_wait_time_minutes = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    peak_hour = models.TimeField(null=True, blank=True)
    # Meals
    total_meals_served = models.PositiveIntegerField(default=0)
    meals_by_type = models.JSONField(default=dict, blank=True)
    # Top items
    top_items = models.JSONField(default=list, blank=True)
    least_popular = models.JSONField(default=list, blank=True)
    # Waste
    total_waste_kg = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    waste_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Financial
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_analytics"
        unique_together = [("school", "date")]
        ordering = ["-date"]

    def __str__(self):
        return f"Cafeteria Analytics - {self.date}"


class CafeteriaCapacity(models.Model):
    """Cafeteria seating capacity management."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="cafeteria_capacities")
    seating_area = models.CharField(max_length=200)
    total_seats = models.PositiveIntegerField(default=0)
    available_seats = models.PositiveIntegerField(default=0)
    # Schedule
    meal_type = models.CharField(
        max_length=10, choices=[("breakfast", "Breakfast"), ("lunch", "Lunch"), ("dinner", "Dinner")]
    )
    time_slot_start = models.TimeField()
    time_slot_end = models.TimeField()
    # Status
    is_full = models.BooleanField(default=False)
    reservation_required = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cafeteria_capacities"

    def __str__(self):
        return f"{self.seating_area} ({self.available_seats}/{self.total_seats})"

    @property
    def occupancy_percentage(self):
        if self.total_seats == 0:
            return 0
        return round(((self.total_seats - self.available_seats) / self.total_seats) * 100, 2)


class MenuItemRating(models.Model):
    """Individual ratings for menu items."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey("MealMenu", on_delete=models.CASCADE, related_name="item_ratings")
    student = models.ForeignKey("students.Student", on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(help_text="1-5 stars")
    review = models.TextField(blank=True)
    would_order_again = models.BooleanField(null=True, blank=True)
    date_rated = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_menu_item_ratings"
        ordering = ["-date_rated"]

    def __str__(self):
        return f"{self.menu_item} - {self.rating}/5 ({self.date_rated})"


class CafeteriaHolidaySchedule(models.Model):
    """Holiday schedule for cafeteria operations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="cafeteria_holiday_schedules"
    )
    date = models.DateField()
    is_closed = models.BooleanField(default=True)
    special_hours = models.BooleanField(default=False)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=200, blank=True)
    # Menu
    special_menu = models.ForeignKey("MealMenu", on_delete=models.SET_NULL, null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_holiday_schedules"
        unique_together = [("school", "date")]

    def __str__(self):
        status = "Closed" if self.is_closed else "Open"
        return f"Cafeteria {status} ({self.date})"


class CafeteriaMonthlyReport(models.Model):
    """Monthly cafeteria performance reports."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="cafeteria_monthly_reports"
    )
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    # Financial
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Operations
    total_meals_served = models.PositiveIntegerField(default=0)
    total_operational_days = models.PositiveIntegerField(default=0)
    avg_daily_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Quality
    avg_food_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    avg_service_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_complaints = models.PositiveIntegerField(default=0)
    complaints_resolved = models.PositiveIntegerField(default=0)
    # Waste
    total_waste_kg = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    waste_reduction_goal = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waste_reduction_actual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # Highlights
    highlights = models.TextField(blank=True)
    improvements_needed = models.TextField(blank=True)
    next_month_goals = models.TextField(blank=True)
    # Metadata
    generated_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_monthly_reports"
        unique_together = [("school", "month", "year")]

    def __str__(self):
        return f"Cafeteria Report - {self.month}/{self.year}"


class CafeteriaInventoryAlert(models.Model):
    """Inventory alerts for cafeteria."""

    class AlertType(models.TextChoices):
        LOW_STOCK = "low_stock", "Low Stock"
        EXPIRING = "expiring", "Expiring Soon"
        OUT_OF_STOCK = "out_of_stock", "Out of Stock"
        PRICE_CHANGE = "price", "Price Change"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="cafeteria_inventory_alerts"
    )
    item = models.ForeignKey("CafeteriaInventory", on_delete=models.CASCADE, related_name="alerts")
    alert_type = models.CharField(max_length=15, choices=AlertType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    message = models.TextField()
    current_quantity = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    reorder_quantity = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Actions
    acknowledged_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cafeteria_inventory_alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.item} ({self.get_status_display()})"
