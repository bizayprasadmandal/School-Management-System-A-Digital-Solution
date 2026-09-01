"""Hostel / Accommodation Management — Hostels, rooms, allocations, fees, visitors."""

import uuid

from django.db import models
from services.auth.models import School, User


class Hostel(models.Model):
    """Hostel buildings (dormitories) on campus."""

    class Gender(models.TextChoices):
        MALE = "male", "Male Only"
        FEMALE = "female", "Female Only"
        COED = "coed", "Co-Educational"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        UNDER_MAINTENANCE = "under_maintenance", "Under Maintenance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="hostels")
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, default=Gender.MALE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    warden = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="warden_hostels",
    )
    assistant_warden = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assistant_warden_hostels",
    )
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    total_floors = models.PositiveSmallIntegerField(default=1)
    rules = models.TextField(blank=True)
    amenities = models.TextField(blank=True, help_text="Comma-separated list")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_hostels"
        unique_together = [("school", "name")]
        ordering = ["name"]

    @property
    def total_rooms(self):
        return self.rooms.count()

    @property
    def total_beds(self):
        from django.db.models import Sum

        return self.rooms.aggregate(total=Sum("capacity"))["total"] or 0

    @property
    def occupied_beds(self):
        return HostelAllocation.objects.filter(room__hostel=self, status=HostelAllocation.Status.ACTIVE).count()

    @property
    def available_beds(self):
        return self.total_beds - self.occupied_beds

    def __str__(self):
        return self.name


class HostelRoom(models.Model):
    """Rooms within a hostel."""

    class RoomType(models.TextChoices):
        SINGLE = "single", "Single"
        DOUBLE = "double", "Double"
        TRIPLE = "triple", "Triple"
        DORMITORY = "dormitory", "Dormitory (4+)"

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=20)
    floor = models.PositiveSmallIntegerField(default=1)
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.DOUBLE)
    capacity = models.PositiveSmallIntegerField(default=2)
    is_furnished = models.BooleanField(default=True)
    has_ac = models.BooleanField(default=False)
    has_attached_bathroom = models.BooleanField(default=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hostel_rooms"
        unique_together = [("hostel", "room_number")]
        ordering = ["hostel", "floor", "room_number"]

    @property
    def occupied_beds(self):
        return self.allocations.filter(status=HostelAllocation.Status.ACTIVE).count()

    @property
    def available_beds(self):
        return self.capacity - self.occupied_beds

    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"


class HostelAllocation(models.Model):
    """Student bed allocation within a hostel room."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CHECKED_OUT = "checked_out", "Checked Out"
        TRANSFERRED = "transferred", "Transferred"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="hostel_allocations",
    )
    room = models.ForeignKey(
        HostelRoom,
        on_delete=models.CASCADE,
        related_name="allocations",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    check_in_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    allocated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hostel_allocations_made",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_allocations"
        ordering = ["-check_in_date"]
        unique_together = [("student", "check_in_date")]

    def __str__(self):
        return f"{self.student} → {self.room}"


class HostelFee(models.Model):
    """Fee structure for hostel accommodation."""

    class BillingCycle(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        SEMI_ANNUAL = "semi_annual", "Semi-Annual"
        ANNUAL = "annual", "Annual"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="hostel_fees")
    name = models.CharField(max_length=100)
    hostel = models.ForeignKey(
        Hostel,
        on_delete=models.CASCADE,
        related_name="fee_structures",
    )
    room_type = models.CharField(
        max_length=20,
        choices=HostelRoom.RoomType.choices,
        blank=True,
        help_text="Leave blank to apply to all room types",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    billing_cycle = models.CharField(max_length=20, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    includes_meals = models.BooleanField(default=False)
    includes_laundry = models.BooleanField(default=False)
    includes_wifi = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hostel_fees"
        ordering = ["hostel", "name"]

    def __str__(self):
        return f"{self.hostel.name} - {self.name} (${self.amount})"


class HostelVisitor(models.Model):
    """Visitor log for hostel security tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="visitors")
    visitor_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    id_proof = models.CharField(max_length=100, blank=True, help_text="ID proof number")
    student_visited = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="hostel_visitors",
    )
    purpose = models.CharField(max_length=200, blank=True)
    in_time = models.DateTimeField()
    out_time = models.DateTimeField(null=True, blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    checked_in_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitor_checkins",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hostel_visitors"
        ordering = ["-in_time"]

    def __str__(self):
        return f"{self.visitor_name} → {self.student_visited}"


# =============================================================================
# Room Maintenance
# =============================================================================


class RoomMaintenance(models.Model):
    """Track room maintenance requests."""

    class MaintenanceType(models.TextChoices):
        PLUMBING = "plumbing", "Plumbing"
        ELECTRICAL = "electrical", "Electrical"
        FURNITURE = "furniture", "Furniture"
        CLEANING = "cleaning", "Cleaning"
        PAINTING = "painting", "Painting"
        GENERAL = "general", "General Maintenance"
        EMERGENCY = "emergency", "Emergency Repair"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        ON_HOLD = "on_hold", "On Hold"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name="maintenance_requests")
    # Request Details
    maintenance_type = models.CharField(max_length=15, choices=MaintenanceType.choices)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    # Reporting
    reported_by = models.ForeignKey("students.Student", on_delete=models.SET_NULL, null=True, blank=True)
    # Assignment
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="hostel_maintenance"
    )
    # Dates
    reported_date = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    # Cost
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Notes
    notes = models.TextField(blank=True)
    resolution_notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_maintenance"
        ordering = ["-reported_date"]

    def __str__(self):
        return f"{self.room} - {self.get_maintenance_type_display()} ({self.get_status_display()})"


# =============================================================================
# Hostel Attendance
# =============================================================================


class HostelAttendance(models.Model):
    """Daily attendance/check-in tracking."""

    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        ON_LEAVE = "on_leave", "On Leave"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.CASCADE, related_name="attendance")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    # Check-in/out
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    # Location
    is_in_campus = models.BooleanField(default=True)
    # Recording
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hostel_attendance"
        ordering = ["-date"]
        unique_together = [("allocation", "date")]

    def __str__(self):
        return f"{self.allocation.student} - {self.date} ({self.get_status_display()})"


# =============================================================================
# Leave Management
# =============================================================================


class LeaveManagement(models.Model):
    """Student leave requests and approval."""

    class LeaveType(models.TextChoices):
        SICK = "sick", "Sick Leave"
        HOME = "home", "Home Leave"
        PERSONAL = "personal", "Personal Leave"
        EMERGENCY = "emergency", "Emergency Leave"
        ACADEMIC = "academic", "Academic Leave"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.CASCADE, related_name="leave_requests")
    # Leave Details
    leave_type = models.CharField(max_length=15, choices=LeaveType.choices)
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Dates
    from_date = models.DateField()
    to_date = models.DateField()
    total_days = models.PositiveSmallIntegerField()
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    # Parent Consent
    parent_notified = models.BooleanField(default=False)
    parent_consent = models.BooleanField(default=False)
    # Contact During Leave
    emergency_contact = models.CharField(max_length=150, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_leave_management"
        ordering = ["-from_date"]

    def __str__(self):
        return f"{self.allocation.student} - {self.get_leave_type_display()} ({self.from_date} to {self.to_date})"


# =============================================================================
# Mess Management
# =============================================================================


class MessManagement(models.Model):
    """Mess/meal planning and tracking."""

    class MealType(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast"
        LUNCH = "lunch", "Lunch"
        SNACK = "snack", "Snack"
        DINNER = "dinner", "Dinner"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="mess_menu")
    # Menu Details
    date = models.DateField()
    meal_type = models.CharField(max_length=10, choices=MealType.choices)
    menu_items = models.JSONField(default=list, help_text="List of menu items")
    description = models.TextField(blank=True)
    # Dietary
    is_vegetarian = models.BooleanField(default=True)
    is_vegan = models.BooleanField(default=False)
    is_halal = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    # Feedback
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Average rating out of 5")
    # Cost
    cost_per_meal = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_mess_management"
        ordering = ["-date", "meal_type"]
        unique_together = [("hostel", "date", "meal_type")]

    def __str__(self):
        return f"{self.hostel.name} - {self.date} {self.get_meal_type_display()}"


class MessAttendance(models.Model):
    """Track which students attended which meals."""

    class Status(models.TextChoices):
        ATTENDED = "attended", "Attended"
        ABSENT = "absent", "Absent"
        SKIPPED = "skipped", "Skipped"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mess_menu = models.ForeignKey(MessManagement, on_delete=models.CASCADE, related_name="attendance")
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.CASCADE, related_name="mess_attendance")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ATTENDED)
    # Metadata
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hostel_mess_attendance"
        unique_together = [("mess_menu", "allocation")]

    def __str__(self):
        return f"{self.allocation.student} - {self.mess_menu} ({self.get_status_display()})"


# =============================================================================
# Complaint Management
# =============================================================================


class ComplaintManagement(models.Model):
    """Student complaint tracking."""

    class ComplaintType(models.TextChoices):
        MAINTENANCE = "maintenance", "Maintenance"
        CLEANLINESS = "cleanliness", "Cleanliness"
        NOISE = "noise", "Noise"
        SECURITY = "security", "Security"
        FOOD = "food", "Food Quality"
        ROOMMATE = "roommate", "Roommate Issues"
        FACILITY = "facility", "Facility Issues"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        UNDER_REVIEW = "under_review", "Under Review"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"
        REJECTED = "rejected", "Rejected"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="complaints")
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.CASCADE, related_name="complaints")
    # Complaint Details
    complaint_type = models.CharField(max_length=15, choices=ComplaintType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    # Assignment
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="hostel_complaints"
    )
    # Resolution
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_complaints"
    )
    # Rating
    satisfaction_rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Rating out of 5")
    feedback = models.TextField(blank=True)
    # Anonymous
    is_anonymous = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_complaints"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


# =============================================================================
# Room Inspection
# =============================================================================


class RoomInspection(models.Model):
    """Room inspection and cleanliness checks."""

    class InspectionType(models.TextChoices):
        DAILY = "daily", "Daily Check"
        WEEKLY = "weekly", "Weekly Inspection"
        MONTHLY = "monthly", "Monthly Inspection"
        RANDOM = "random", "Random Check"
        CHECKOUT = "checkout", "Checkout Inspection"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Rating(models.IntegerChoices):
        POOR = 1, "Poor"
        FAIR = 2, "Fair"
        GOOD = 3, "Good"
        VERY_GOOD = 4, "Very Good"
        EXCELLENT = 5, "Excellent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name="inspections")
    # Inspection Details
    inspection_type = models.CharField(max_length=15, choices=InspectionType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    # Ratings
    cleanliness_rating = models.IntegerField(choices=Rating.choices, null=True, blank=True)
    orderliness_rating = models.IntegerField(choices=Rating.choices, null=True, blank=True)
    condition_rating = models.IntegerField(choices=Rating.choices, null=True, blank=True)
    # Inspector
    inspected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Issues Found
    issues_found = models.JSONField(default=list, help_text="List of issues found")
    has_issues = models.BooleanField(default=False)
    # Notes
    notes = models.TextField(blank=True)
    action_required = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_inspections"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.room} - {self.get_inspection_type_display()} ({self.scheduled_date})"


# =============================================================================
# Inventory Management
# =============================================================================


class InventoryManagement(models.Model):
    """Furniture and equipment tracking."""

    class ItemCategory(models.TextChoices):
        FURNITURE = "furniture", "Furniture"
        ELECTRONICS = "electronics", "Electronics"
        BEDDING = "bedding", "Bedding"
        FIXTURE = "fixture", "Fixtures"
        APPLIANCE = "appliance", "Appliances"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        NEEDS_REPAIR = "needs_repair", "Needs Repair"
        DAMAGED = "damaged", "Damaged"
        RETIRED = "retired", "Retired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="inventory")
    room = models.ForeignKey(HostelRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name="inventory")
    # Item Details
    item_name = models.CharField(max_length=100)
    item_category = models.CharField(max_length=15, choices=ItemCategory.choices)
    description = models.TextField(blank=True)
    # Tracking
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.GOOD)
    # Purchase Info
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    supplier = models.CharField(max_length=100, blank=True)
    # Condition
    last_inspected_date = models.DateField(null=True, blank=True)
    condition_notes = models.TextField(blank=True)
    # Metadata
    asset_tag = models.CharField(max_length=50, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_inventory"
        ordering = ["item_name"]

    def __str__(self):
        return f"{self.item_name} ({self.quantity})"


# =============================================================================
# Hostel Reports
# =============================================================================


class HostelReport(models.Model):
    """Hostel analytics and reports."""

    class ReportType(models.TextChoices):
        OCCUPANCY = "occupancy", "Occupancy Report"
        FINANCIAL = "financial", "Financial Report"
        MAINTENANCE = "maintenance", "Maintenance Report"
        DISCIPLINE = "discipline", "Discipline Report"
        ATTENDANCE = "attendance", "Attendance Report"
        MESS = "mess", "Mess Report"
        COMPLAINT = "complaint", "Complaint Report"
        GENERAL = "general", "General Report"
        CUSTOM = "custom", "Custom Report"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATED = "generated", "Generated"
        SENT = "sent", "Sent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="reports")
    # Report Details
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=15, choices=ReportType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    # Report Period
    period_start = models.DateField()
    period_end = models.DateField()
    # Report Content
    summary = models.TextField(blank=True)
    findings = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)
    # Statistics
    total_rooms = models.PositiveIntegerField(default=0)
    occupied_rooms = models.PositiveIntegerField(default=0)
    occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_complaints = models.PositiveIntegerField(default=0)
    resolved_complaints = models.PositiveIntegerField(default=0)
    total_maintenance = models.PositiveIntegerField(default=0)
    completed_maintenance = models.PositiveIntegerField(default=0)
    # Personnel
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hostel_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# =============================================================================
# Emergency Contacts
# =============================================================================


class EmergencyContact(models.Model):
    """Emergency contact management."""

    class ContactType(models.TextChoices):
        WARDEN = "warden", "Hostel Warden"
        ASSISTANT_WARDEN = "assistant_warden", "Assistant Warden"
        SECURITY = "security", "Security"
        MEDICAL = "medical", "Medical"
        FIRE = "fire", "Fire Department"
        POLICE = "police", "Police"
        PARENT = "parent", "Parent/Guardian"
        SCHOOL = "school", "School Administration"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="emergency_contacts")
    # Contact Details
    contact_type = models.CharField(max_length=20, choices=ContactType.choices)
    name = models.CharField(max_length=150)
    phone_primary = models.CharField(max_length=20)
    phone_secondary = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    # Availability
    is_available_24x7 = models.BooleanField(default=False)
    available_hours = models.CharField(max_length=100, blank=True)
    # Location
    location = models.CharField(max_length=100, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_emergency_contacts"
        ordering = ["contact_type", "name"]

    def __str__(self):
        return f"{self.get_contact_type_display()}: {self.name}"


# =============================================================================
# Room Transfer
# =============================================================================


class RoomTransfer(models.Model):
    """Transfer between rooms/hostels."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.CASCADE, related_name="transfers")
    # Transfer Details
    from_room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name="transfers_from")
    to_room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name="transfers_to")
    # Reason
    reason = models.TextField()
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    # Dates
    requested_date = models.DateField(auto_now_add=True)
    transfer_date = models.DateField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_room_transfers"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Transfer: {self.allocation.student} from {self.from_room} to {self.to_room}"


# =============================================================================
# Checkout Process
# =============================================================================


class CheckoutProcess(models.Model):
    """Formal checkout workflow."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        ON_HOLD = "on_hold", "On Hold"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    allocation = models.OneToOneField(HostelAllocation, on_delete=models.CASCADE, related_name="checkout_process")
    # Checkout Details
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    checkout_date = models.DateField()
    # Inspection
    room_inspected = models.BooleanField(default=False)
    inspection_notes = models.TextField(blank=True)
    damage_detected = models.BooleanField(default=False)
    damage_description = models.TextField(blank=True)
    damage_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Items
    items_returned = models.JSONField(default=list, help_text="List of items returned")
    missing_items = models.JSONField(default=list, help_text="List of missing items")
    # Financial
    pending_dues = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    security_deposit_refund = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Keys
    keys_returned = models.BooleanField(default=False)
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_checkout_process"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Checkout: {self.allocation.student} ({self.get_status_display()})"


# =============================================================================
# Hostel Notifications
# =============================================================================


class HostelNotification(models.Model):
    """Automated notifications."""

    class NotificationType(models.TextChoices):
        GENERAL = "general", "General Announcement"
        EMERGENCY = "emergency", "Emergency"
        MAINTENANCE = "maintenance", "Maintenance Update"
        LEAVE = "leave", "Leave Status"
        COMPLAINT = "complaint", "Complaint Update"
        FEE = "fee", "Fee Reminder"
        EVENT = "event", "Hostel Event"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        READ = "read", "Read"
        FAILED = "failed", "Failed"

    class RecipientType(models.TextChoices):
        ALL = "all", "All Students"
        SPECIFIC = "specific", "Specific Students"
        WARDEN = "warden", "Warden Only"
        PARENT = "parent", "Parents"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="notifications")
    # Notification Details
    notification_type = models.CharField(max_length=15, choices=NotificationType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    # Recipients
    recipient_type = models.CharField(max_length=10, choices=RecipientType.choices, default=RecipientType.ALL)
    recipients = models.JSONField(default=list, help_text="List of recipient IDs")
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    read_count = models.PositiveIntegerField(default=0)
    # Priority
    is_priority = models.BooleanField(default=False)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hostel_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.title}"


# =============================================================================
# Hostel Feedback
# =============================================================================


class HostelFeedback(models.Model):
    """Student feedback on hostel."""

    class FeedbackType(models.TextChoices):
        ROOM = "room", "Room Quality"
        CLEANLINESS = "cleanliness", "Cleanliness"
        FOOD = "food", "Food Quality"
        SECURITY = "security", "Security"
        STAFF = "staff", "Staff Behavior"
        FACILITIES = "facilities", "Facilities"
        MAINTENANCE = "maintenance", "Maintenance"
        GENERAL = "general", "General Feedback"
        SUGGESTION = "suggestion", "Suggestion"
        COMPLAINT = "complaint", "Complaint"

    class Rating(models.IntegerChoices):
        VERY_POOR = 1, "Very Poor"
        POOR = 2, "Poor"
        AVERAGE = 3, "Average"
        GOOD = 4, "Good"
        EXCELLENT = 5, "Excellent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="feedbacks")
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.CASCADE, related_name="feedbacks")
    # Feedback Details
    feedback_type = models.CharField(max_length=15, choices=FeedbackType.choices)
    rating = models.IntegerField(choices=Rating.choices)
    # Content
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    # Suggestions
    suggestion = models.TextField(blank=True)
    # Anonymous
    is_anonymous = models.BooleanField(default=False)
    # Response
    response = models.TextField(blank=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hostel_feedbacks"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_feedback_type_display()} - {self.get_rating_display()}"


# =============================================================================
# NEW MODELS: Roommate Matching
# =============================================================================


class RoommatePreference(models.Model):
    """Student preferences for roommate matching."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField("students.Student", on_delete=models.CASCADE, related_name="roommate_preferences")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="roommate_preferences")
    # Sleep
    sleep_time = models.TimeField(null=True, blank=True)
    wake_time = models.TimeField(null=True, blank=True)
    is_light_sleeper = models.BooleanField(default=False)
    # Study
    study_habits = models.CharField(max_length=50, blank=True, help_text="e.g., Quiet, Background noise")
    prefers_study_at = models.CharField(max_length=50, blank=True)
    # Social
    visitor_frequency = models.CharField(max_length=50, blank=True, help_text="Never, Rarely, Sometimes, Often")
    is_social = models.BooleanField(default=True)
    # Habits
    smoking = models.BooleanField(default=False)
    snoring = models.BooleanField(default=False)
    neatness_level = models.CharField(max_length=20, blank=True, help_text="Very Neat, Average, Relaxed")
    temperature_preference = models.CharField(max_length=20, blank=True)
    # Requests
    roommate_request = models.ForeignKey(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="requested_by_roommate"
    )
    avoid_requests = models.ManyToManyField("students.Student", blank=True, related_name="avoided_by_roommate")
    # Notes
    additional_notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roommate_preferences"

    def __str__(self):
        return f"Roommate Preferences — {self.student}"


class RoommateAssignment(models.Model):
    """Roommate assignments within a room."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name="roommate_assignments")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="roommate_assignments")
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.SET_NULL, null=True, blank=True)
    match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Compatibility score 0-100")
    assigned_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "roommate_assignments"
        unique_together = [("room", "student")]

    def __str__(self):
        return f"{self.student} — Room {self.room.room_number} (Score: {self.match_score})"


# =============================================================================
# NEW MODELS: Key Management
# =============================================================================


class RoomKey(models.Model):
    """Key tracking for hostel rooms."""

    class Status(models.TextChoices):
        ASSIGNED = "assigned", "Assigned"
        RETURNED = "returned", "Returned"
        LOST = "lost", "Lost"
        REPLACED = "replaced", "Replaced"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name="keys")
    key_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ASSIGNED)
    # Assignment
    allocated_to = models.ForeignKey(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="hostel_keys"
    )
    issued_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    # Replacement
    replacement_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reported_lost_date = models.DateField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "room_keys"
        ordering = ["key_number"]

    def __str__(self):
        return f"Key {self.key_number} — Room {self.room.room_number} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Laundry Service
# =============================================================================


class LaundryService(models.Model):
    """Laundry service requests and tracking."""

    class Status(models.TextChoices):
        PICKUP_SCHEDULED = "pickup", "Pickup Scheduled"
        PICKED_UP = "picked_up", "Picked Up"
        IN_PROCESS = "in_process", "In Process"
        READY = "ready", "Ready for Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    class GarmentType(models.TextChoices):
        UNIFORM = "uniform", "Uniform"
        BEDDING = "bedding", "Bedding"
        PERSONAL = "personal", "Personal Clothes"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="laundry_services")
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.CASCADE, related_name="laundry_requests")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PICKUP_SCHEDULED)
    # Garment details
    garment_type = models.CharField(max_length=15, choices=GarmentType.choices, default=GarmentType.PERSONAL)
    quantity = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)
    # Schedule
    pickup_date = models.DateField()
    pickup_time = models.TimeField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_time = models.TimeField(null=True, blank=True)
    # Cost
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)
    # Special instructions
    special_instructions = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "laundry_services"
        ordering = ["-pickup_date"]

    def __str__(self):
        return f"Laundry — {self.allocation.student} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Common Area Booking
# =============================================================================


class CommonAreaBooking(models.Model):
    """Booking for common areas (study room, gym, TV room, etc.)."""

    class AreaType(models.TextChoices):
        STUDY_ROOM = "study", "Study Room"
        GYM = "gym", "Gym / Fitness"
        TV_ROOM = "tv", "TV Room"
        GAME_ROOM = "game", "Game Room"
        LIBRARY = "library", "Hostel Library"
        TERRACE = "terrace", "Terrace / Garden"
        MEETING_ROOM = "meeting", "Meeting Room"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        BOOKED = "booked", "Booked"
        ACTIVE = "active", "In Use"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="common_area_bookings")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="common_area_bookings")
    area_type = models.CharField(max_length=10, choices=AreaType.choices)
    area_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BOOKED)
    # Schedule
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    # Capacity
    group_size = models.PositiveIntegerField(default=1)
    additional_members = models.ManyToManyField(
        "students.Student", blank=True, related_name="common_area_bookings_guest"
    )
    # Purpose
    purpose = models.TextField(blank=True)
    # Rules
    rules_acknowledged = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "common_area_bookings"
        ordering = ["-booking_date", "-start_time"]

    def __str__(self):
        return f"{self.get_area_type_display()} — {self.student} ({self.booking_date})"


# =============================================================================
# NEW MODELS: Wellness Checks
# =============================================================================


class WellnessCheck(models.Model):
    """Resident wellness checks by hostel staff."""

    class CheckType(models.TextChoices):
        ROUTINE = "routine", "Routine Check"
        FOLLOW_UP = "follow_up", "Follow-up Check"
        WELFARE = "welfare", "Welfare Check"
        MEDICAL = "medical", "Medical Check"
        MENTAL = "mental", "Mental Health Check"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        ISSUE_FOUND = "issue", "Issue Found"
        ESCALATED = "escalated", "Escalated"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="wellness_checks")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="wellness_checks")
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.SET_NULL, null=True, blank=True)
    checked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    check_type = models.CharField(max_length=10, choices=CheckType.choices, default=CheckType.ROUTINE)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    check_date = models.DateField()
    # Findings
    physical_wellbeing = models.CharField(max_length=20, blank=True, help_text="Good, Fair, Concern")
    emotional_state = models.CharField(max_length=20, blank=True, help_text="Stable, Anxious, Distressed")
    room_condition = models.CharField(max_length=20, blank=True)
    concerns_noted = models.TextField(blank=True)
    # Actions
    action_taken = models.TextField(blank=True)
    referred_to = models.CharField(max_length=200, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    # Parent notification
    parent_notified = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "wellness_checks"
        ordering = ["-check_date"]
        indexes = [
            models.Index(fields=["student", "check_type"]),
        ]

    def __str__(self):
        return f"{self.get_check_type_display()} — {self.student} ({self.check_date})"


# =============================================================================
# NEW MODELS: Visitor Management
# =============================================================================


class VisitorPass(models.Model):
    """Visitor passes for hostel guests."""

    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        CHECKED_IN = "checked_in", "Checked In"
        CHECKED_OUT = "checked_out", "Checked Out"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="visitor_passes")
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="visitor_passes")
    resident = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="visitor_passes")
    # Visitor info
    visitor_name = models.CharField(max_length=200)
    visitor_phone = models.CharField(max_length=30, blank=True)
    visitor_id_number = models.CharField(max_length=50, blank=True)
    relationship = models.CharField(max_length=50, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.REQUESTED)
    # Schedule
    visit_date = models.DateField()
    expected_arrival = models.TimeField()
    expected_departure = models.TimeField()
    actual_arrival = models.TimeField(null=True, blank=True)
    actual_departure = models.TimeField(null=True, blank=True)
    # Purpose
    purpose = models.CharField(max_length=200, blank=True)
    # Approval
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="visitor_pass_approvals"
    )
    approval_notes = models.TextField(blank=True)
    # Room access
    room_visited = models.ForeignKey(HostelRoom, on_delete=models.SET_NULL, null=True, blank=True)
    # ID verification
    id_verified = models.BooleanField(default=False)
    id_verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="visitor_id_verifications"
    )
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "visitor_passes"
        ordering = ["-visit_date"]

    def __str__(self):
        return f"Visitor: {self.visitor_name} → {self.resident} ({self.visit_date})"


# =============================================================================
# NEW MODELS: Roommate Matching (Extended)
# =============================================================================


class RoommateMatchRequest(models.Model):
    """Explicit roommate match requests between students."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="roommate_match_requests_sent"
    )
    requested = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="roommate_match_requests_received"
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    message = models.TextField(blank=True)
    response_message = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roommate_match_requests"
        unique_together = [("requester", "requested")]

    def __str__(self):
        return f"{self.requester} → {self.requested} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Mess Menu & Diet
# =============================================================================


class MessMenuPlan(models.Model):
    """Weekly/monthly mess menu planning."""

    class MealType(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast"
        LUNCH = "lunch", "Lunch"
        SNACK = "snack", "Snack"
        DINNER = "dinner", "Dinner"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="mess_menu_plans")
    meal_type = models.CharField(max_length=10, choices=MealType.choices)
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        ],
    )
    week_number = models.PositiveIntegerField(default=1, help_text="Week number for rotation")
    # Menu items
    main_course = models.TextField(blank=True)
    side_dish = models.TextField(blank=True)
    bread_rice = models.TextField(blank=True)
    dessert = models.TextField(blank=True)
    beverage = models.TextField(blank=True)
    # Dietary
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    calories = models.PositiveIntegerField(null=True, blank=True)
    # Cost
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Rating
    avg_student_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mess_menu_plans"
        ordering = ["week_number", "day_of_week", "meal_type"]

    def __str__(self):
        return f"{self.get_meal_type_display()} — {self.day_of_week.title()} (Week {self.week_number})"


class MessDietaryRequest(models.Model):
    """Student dietary requirement requests."""

    class DietType(models.TextChoices):
        VEGETARIAN = "vegetarian", "Vegetarian"
        VEGAN = "vegan", "Vegan"
        GLUTEN_FREE = "gluten_free", "Gluten Free"
        DIABETIC = "diabetic", "Diabetic Friendly"
        LOW_SODIUM = "low_sodium", "Low Sodium"
        HALAL = "halal", "Halal"
        KOSHER = "kosher", "Kosher"
        ALLERGY = "allergy", "Allergy Specific"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="mess_dietary_requests")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="mess_dietary_requests")
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.SET_NULL, null=True, blank=True)
    diet_type = models.CharField(max_length=15, choices=DietType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    medical_reason = models.TextField(blank=True)
    doctor_note = models.FileField(upload_to="hostel/dietary_notes/", null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mess_dietary_requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_diet_type_display()} — {self.student} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Hostel Inventory Tracking
# =============================================================================


class HostelAsset(models.Model):
    """Fixed assets in hostel rooms and common areas."""

    class AssetCondition(models.TextChoices):
        NEW = "new", "New"
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        POOR = "poor", "Poor"
        DAMAGED = "damaged", "Damaged"
        RETIRED = "retired", "Retired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(HostelRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name="assets")
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="assets")
    asset_name = models.CharField(max_length=200)
    asset_tag = models.CharField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True)
    condition = models.CharField(max_length=10, choices=AssetCondition.choices, default=AssetCondition.GOOD)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    last_inspected = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_assets"
        ordering = ["asset_name"]

    def __str__(self):
        return f"{self.asset_name} — Room {self.room.room_number if self.room else 'N/A'}"


class HostelAssetTransfer(models.Model):
    """Asset transfers between rooms."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(HostelAsset, on_delete=models.CASCADE, related_name="transfers")
    from_room = models.ForeignKey(
        HostelRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name="assets_sent"
    )
    to_room = models.ForeignKey(
        HostelRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name="assets_received"
    )
    transferred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    transfer_date = models.DateField(auto_now_add=True)
    reason = models.TextField(blank=True)
    condition_at_transfer = models.CharField(max_length=10, choices=HostelAsset.AssetCondition.choices)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "hostel_asset_transfers"
        ordering = ["-transfer_date"]

    def __str__(self):
        return f"Transfer: {self.asset} ({self.from_room} → {self.to_room})"


# =============================================================================
# NEW MODELS: Hostel Events & Activities
# =============================================================================


class HostelEvent(models.Model):
    """Events and activities organized within the hostel."""

    class EventType(models.TextChoices):
        ORIENTATION = "orientation", "Resident Orientation"
        SOCIAL = "social", "Social Event"
        CLEANLINESS = "cleanliness", "Cleanliness Drive"
        SAFETY = "safety", "Safety Drill"
        CULTURAL = "cultural", "Cultural Event"
        SPORTS = "sports", "Sports Event"
        WORKSHOP = "workshop", "Workshop"
        CELEBRATION = "celebration", "Celebration"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="events")
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=15, choices=EventType.choices, default=EventType.SOCIAL)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PLANNED)
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    max_participants = models.PositiveIntegerField(default=50)
    current_participants = models.PositiveIntegerField(default=0)
    # Feedback
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_feedback = models.PositiveIntegerField(default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_events"
        ordering = ["-event_date"]

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()}) — {self.event_date}"


class HostelEventParticipant(models.Model):
    """Participants in hostel events."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(HostelEvent, on_delete=models.CASCADE, related_name="participants")
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="hostel_event_participations"
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    feedback_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback_comment = models.TextField(blank=True)

    class Meta:
        db_table = "hostel_event_participants"
        unique_together = [("event", "student")]

    def __str__(self):
        return f"{self.student} — {self.event}"


# =============================================================================
# NEW MODELS: Emergency Protocol
# =============================================================================


class HostelEmergencyProtocol(models.Model):
    """Emergency protocols and procedures for the hostel."""

    class EmergencyType(models.TextChoices):
        FIRE = "fire", "Fire Emergency"
        MEDICAL = "medical", "Medical Emergency"
        NATURAL_DISASTER = "natural", "Natural Disaster"
        LOCKDOWN = "lockdown", "Lockdown"
        EVACUATION = "evacuation", "Evacuation"
        POWER_OUTAGE = "power", "Power Outage"
        OTHER = "other", "Other Emergency"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="emergency_protocols")
    emergency_type = models.CharField(max_length=15, choices=EmergencyType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField()
    procedures = models.TextField(help_text="Step-by-step emergency procedures")
    contacts = models.TextField(help_text="Emergency contacts and numbers")
    assembly_point = models.CharField(max_length=200, blank=True)
    last_drill_date = models.DateField(null=True, blank=True)
    next_drill_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    document = models.FileField(upload_to="hostel/emergency_docs/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_emergency_protocols"
        ordering = ["emergency_type"]

    def __str__(self):
        return f"{self.get_emergency_type_display()} — {self.title}"


class HostelEmergencyDrill(models.Model):
    """Emergency drill records."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class EvaluationResult(models.TextChoices):
        EXCELLENT = "excellent", "Excellent"
        GOOD = "good", "Good"
        SATISFACTORY = "satisfactory", "Satisfactory"
        NEEDS_IMPROVEMENT = "needs_improvement", "Needs Improvement"
        POOR = "poor", "Poor"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="emergency_drills")
    protocol = models.ForeignKey(HostelEmergencyProtocol, on_delete=models.SET_NULL, null=True, blank=True)
    conducted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    drill_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    # Results
    participants_count = models.PositiveIntegerField(default=0)
    evaluation = models.CharField(max_length=20, choices=EvaluationResult.choices, blank=True)
    evacuation_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    issues_identified = models.TextField(blank=True)
    improvements_needed = models.TextField(blank=True)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_emergency_drills"
        ordering = ["-drill_date"]

    def __str__(self):
        return f"Drill — {self.hostel.name} ({self.drill_date})"


# =============================================================================
# NEW MODELS: Hostel Fee Tracking
# =============================================================================


class HostelFeePayment(models.Model):
    """Individual fee payment records for hostel residents."""

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        BANK_TRANSFER = "bank", "Bank Transfer"
        ONLINE = "online", "Online Payment"
        CHEQUE = "cheque", "Cheque"
        SCHOLARSHIP = "scholarship", "Scholarship/Discount"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        PARTIAL = "partial", "Partially Paid"
        OVERDUE = "overdue", "Overdue"
        WAIVED = "waived", "Waived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="hostel_fee_payments")
    allocation = models.ForeignKey(HostelAllocation, on_delete=models.CASCADE, related_name="fee_payments")
    hostel_fee = models.ForeignKey(HostelFee, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Amount
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Payment details
    payment_method = models.CharField(max_length=15, choices=PaymentMethod.choices, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    # Period
    billing_period = models.CharField(max_length=50, blank=True, help_text="e.g., Jan 2026")
    due_date = models.DateField()
    # Notes
    notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_fee_payments"
        ordering = ["-due_date"]
        indexes = [
            models.Index(fields=["allocation", "status"]),
        ]

    def __str__(self):
        return f"{self.allocation.student} — {self.billing_period} ({self.get_status_display()})"

    @property
    def balance(self):
        return self.amount_due - self.amount_paid + self.late_fee - self.discount

    @property
    def is_fully_paid(self):
        return self.balance <= 0


class HostelInspectionSchedule(models.Model):
    """Scheduled room inspection rotations."""

    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="inspection_schedules")
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    frequency = models.CharField(max_length=15, choices=Frequency.choices, default=Frequency.WEEKLY)
    day_of_week = models.CharField(max_length=10, blank=True)
    time_of_day = models.TimeField(null=True, blank=True)
    rooms_to_inspect = models.CharField(max_length=200, blank=True, help_text="All, Floor 1, Specific rooms, etc.")
    checklist_items = models.JSONField(default=list, blank=True, help_text="Checklist items for inspection")
    is_active = models.BooleanField(default=True)
    last_inspection_date = models.DateField(null=True, blank=True)
    next_inspection_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hostel_inspection_schedules"

    def __str__(self):
        return f"{self.hostel.name} — {self.get_frequency_display()} Inspection"


class MessFeedback(models.Model):
    """Feedback on mess food quality."""

    class MealType(models.TextChoices):
        BREAKFAST = "breakfast", "Breakfast"
        LUNCH = "lunch", "Lunch"
        DINNER = "dinner", "Dinner"
        SNACK = "snack", "Snack"

    class Rating(models.IntegerChoices):
        VERY_POOR = 1, "Very Poor"
        POOR = 2, "Poor"
        AVERAGE = 3, "Average"
        GOOD = 4, "Good"
        EXCELLENT = 5, "Excellent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="mess_feedbacks")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="mess_feedbacks")
    meal_type = models.CharField(max_length=10, choices=MealType.choices)
    rating = models.IntegerField(choices=Rating.choices)
    food_quality = models.IntegerField(choices=Rating.choices, default=Rating.AVERAGE)
    portion_size = models.CharField(max_length=20, blank=True, help_text="Too Small, Just Right, Too Large")
    hygiene_rating = models.IntegerField(choices=Rating.choices, default=Rating.AVERAGE)
    # Comments
    liked_items = models.TextField(blank=True, help_text="What did you like?")
    disliked_items = models.TextField(blank=True, help_text="What could be improved?")
    suggestions = models.TextField(blank=True)
    # Date
    meal_date = models.DateField()
    # Metadata
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mess_feedbacks"
        ordering = ["-meal_date"]

    def __str__(self):
        return f"{self.student} — {self.get_meal_type_display()} ({self.get_rating_display()})"


class HostelAttendanceAlert(models.Model):
    """Auto-generated alerts for attendance anomalies."""

    class AlertType(models.TextChoices):
        MISSING = "missing", "Missing Check-in"
        NO_SHOW = "no_show", "No-show for Roll Call"
        LATE = "late", "Late Return"
        UNAUTHORIZED_ABSENCE = "unauthorized", "Unauthorized Absence"
        LEAVE_VIOLATION = "leave_violation", "Leave Policy Violation"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"
        ESCALATED = "escalated", "Escalated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="hostel_attendance_alerts")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="hostel_attendance_alerts")
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="attendance_alerts")
    alert_type = models.CharField(max_length=20, choices=AlertType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Details
    alert_date = models.DateField()
    description = models.TextField()
    related_attendance = models.ForeignKey(HostelAttendance, on_delete=models.SET_NULL, null=True, blank=True)
    # Actions
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="hostel_alert_resolutions"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    # Parent
    parent_notified = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hostel_attendance_alerts"
        ordering = ["-alert_date"]
        indexes = [
            models.Index(fields=["student", "alert_type"]),
            models.Index(fields=["school", "status", "severity"]),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()} — {self.student} ({self.get_severity_display()})"
