"""
Infrastructure Service — Buildings, rooms, work orders, assets, utilities, safety, compliance.
"""

import uuid

from django.conf import settings
from django.db import models
from services.auth.models import School


class Building(models.Model):
    """School buildings / blocks."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        UNDER_MAINTENANCE = "under_maintenance", "Under Maintenance"
        CLOSED = "closed", "Closed"
        DEMOLISHED = "demolished", "Demolished"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="infra_buildings")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True, help_text="Building code / abbreviation")
    description = models.TextField(blank=True)
    floors = models.PositiveSmallIntegerField(default=1)
    year_built = models.PositiveSmallIntegerField(null=True, blank=True)
    total_area_sqft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_buildings"
        unique_together = [("school", "name")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Room(models.Model):
    """Individual rooms within buildings."""

    class RoomType(models.TextChoices):
        CLASSROOM = "classroom", "Classroom"
        LAB = "lab", "Laboratory"
        LIBRARY = "library", "Library"
        OFFICE = "office", "Office"
        GYM = "gym", "Gymnasium"
        AUDITORIUM = "auditorium", "Auditorium"
        CAFETERIA = "cafeteria", "Cafeteria"
        STORAGE = "storage", "Storage"
        RESTROOM = "restroom", "Restroom"
        NURSE = "nurse", "Nurse Room"
        COUNSELING = "counseling", "Counseling Room"
        CONFERENCE = "conference", "Conference Room"
        COMPUTER_LAB = "computer_lab", "Computer Lab"
        ART_ROOM = "art_room", "Art Room"
        MUSIC_ROOM = "music_room", "Music Room"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        OCCUPIED = "occupied", "Occupied"
        UNDER_MAINTENANCE = "under_maintenance", "Under Maintenance"
        RESERVED = "reserved", "Reserved"
        UNAVAILABLE = "unavailable", "Unavailable"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=20)
    floor = models.PositiveSmallIntegerField(default=0)
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.CLASSROOM)
    capacity = models.PositiveSmallIntegerField(default=0, help_text="Maximum occupancy")
    area_sqft = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    has_projector = models.BooleanField(default=False)
    has_smartboard = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False, help_text="Air conditioning")
    has_wifi = models.BooleanField(default=True)
    has_computers = models.BooleanField(default=False)
    computer_count = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_rooms"
        unique_together = [("building", "room_number")]
        ordering = ["building", "room_number"]

    def __str__(self):
        return f"{self.building.name} - {self.room_number}"


class RoomAllocation(models.Model):
    """Assign rooms to classes, teachers, or departments."""

    class AllocationType(models.TextChoices):
        CLASS = "class", "Class Room"
        TEACHER = "teacher", "Teacher Office"
        DEPARTMENT = "department", "Department"
        EVENT = "event", "Event"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="allocations")
    allocation_type = models.CharField(max_length=20, choices=AllocationType.choices)
    classroom = models.ForeignKey(
        "students.Classroom",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_room_allocations",
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_room_allocations",
    )
    department = models.CharField(max_length=100, blank=True)
    event_name = models.CharField(max_length=200, blank=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_room_allocations"
        ordering = ["room", "effective_from"]

    def __str__(self):
        return f"{self.room} — {self.get_allocation_type_display()}"


class WorkOrder(models.Model):
    """Maintenance work orders for facilities."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"
        EMERGENCY = "emergency", "Emergency"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Category(models.TextChoices):
        PLUMBING = "plumbing", "Plumbing"
        ELECTRICAL = "electrical", "Electrical"
        HVAC = "hvac", "HVAC / Climate"
        CARPENTRY = "carpentry", "Carpentry"
        PAINTING = "painting", "Painting"
        ROOFING = "roofing", "Roofing"
        GROUND = "ground", "Grounds / Landscaping"
        CLEANING = "cleaning", "Cleaning"
        SECURITY = "security", "Security System"
        IT = "it", "IT / Network"
        GENERAL = "general", "General"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="infra_work_orders")
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    building = models.ForeignKey(
        Building,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_orders",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_orders",
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reported_infra_work_orders",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_infra_work_orders",
    )
    external_vendor = models.CharField(max_length=150, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    scheduled_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    attachments = models.JSONField(default=list, blank=True, help_text="List of attachment URLs")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_work_orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"WO-{self.pk}: {self.title}"


class WorkOrderComment(models.Model):
    """Comments / updates on work orders."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField()
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "infra_work_order_comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on WO-{self.work_order_id}"


class PreventiveMaintenance(models.Model):
    """Scheduled preventive maintenance tasks."""

    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        SEMI_ANNUAL = "semi_annual", "Semi-Annual"
        ANNUAL = "annual", "Annual"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="infra_preventive_maintenance")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=WorkOrder.Category.choices, default=WorkOrder.Category.GENERAL)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.MONTHLY)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_preventive_maintenance_tasks",
    )
    last_completed = models.DateField(null=True, blank=True)
    next_due = models.DateField()
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_preventive_maintenance"
        ordering = ["next_due"]

    def __str__(self):
        return f"{self.title} ({self.get_frequency_display()})"


class Asset(models.Model):
    """School assets — equipment, furniture, IT devices."""

    class AssetType(models.TextChoices):
        FURNITURE = "furniture", "Furniture"
        ELECTRONICS = "electronics", "Electronics"
        IT_DEVICE = "it_device", "IT Device"
        PROJECTOR = "projector", "Projector / Display"
        NETWORK = "network", "Network Equipment"
        SAFETY = "safety", "Safety Equipment"
        SPORTS = "sports", "Sports Equipment"
        MUSICAL = "musical", "Musical Instrument"
        LAB = "lab", "Lab Equipment"
        OTHER = "other", "Other"

    class Condition(models.TextChoices):
        NEW = "new", "New"
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        POOR = "poor", "Poor"
        DAMAGED = "damaged", "Damaged"
        WRITTEN_OFF = "written_off", "Written Off"

    class Status(models.TextChoices):
        IN_STOCK = "in_stock", "In Stock"
        IN_USE = "in_use", "In Use"
        UNDER_REPAIR = "under_repair", "Under Repair"
        RETIRED = "retired", "Retired"
        DISPOSED = "disposed", "Disposed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="infra_assets")
    asset_tag = models.CharField(max_length=50, unique=True, help_text="Unique asset tag / barcode")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    asset_type = models.CharField(max_length=20, choices=AssetType.choices, default=AssetType.FURNITURE)
    condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.GOOD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_STOCK)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    warranty_expiry = models.DateField(null=True, blank=True)
    warranty_provider = models.CharField(max_length=150, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    model_name = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=150, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    qr_code = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_assets"
        ordering = ["asset_tag"]

    def __str__(self):
        return f"{self.asset_tag}: {self.name}"


class AssetAssignment(models.Model):
    """Track asset assignments to staff, rooms, or departments."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RETURNED = "returned", "Returned"
        LOST = "lost", "Lost"
        DAMAGED = "damaged", "Damaged"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="assignments")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_asset_assignments",
    )
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    assigned_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    condition_at_assignment = models.CharField(
        max_length=20, choices=Asset.Condition.choices, default=Asset.Condition.GOOD
    )
    condition_at_return = models.CharField(max_length=20, choices=Asset.Condition.choices, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_asset_assignments"
        ordering = ["-assigned_date"]

    def __str__(self):
        return f"{self.asset.asset_tag} → {self.assigned_to or self.room or self.department}"


class AssetLifecycle(models.Model):
    """Track complete asset lifecycle from purchase to disposal."""

    class Event(models.TextChoices):
        PURCHASED = "purchased", "Purchased"
        RECEIVED = "received", "Received"
        ASSIGNED = "assigned", "Assigned"
        MAINTENANCE = "maintenance", "Maintenance"
        REPAIRED = "repaired", "Repaired"
        TRANSFERRED = "transferred", "Transferred"
        INSPECTED = "inspected", "Inspected"
        WRITTEN_OFF = "written_off", "Written Off"
        DISPOSED = "disposed", "Disposed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="lifecycle_events")
    event = models.CharField(max_length=20, choices=Event.choices)
    event_date = models.DateField()
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_asset_lifecycle_events",
    )
    notes = models.TextField(blank=True)
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "infra_asset_lifecycle"
        ordering = ["-event_date"]

    def __str__(self):
        return f"{self.asset.asset_tag}: {self.get_event_display()} ({self.event_date})"


class WarrantyClaim(models.Model):
    """Track warranty claims for assets."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        RESOLVED = "resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="warranty_claims")
    claim_number = models.CharField(max_length=50, blank=True)
    issue_description = models.TextField()
    claim_date = models.DateField()
    warranty_provider = models.CharField(max_length=150, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(max_length=254, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    resolution_date = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    cost_covered = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost_customer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    attachments = models.JSONField(default=list, blank=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_warranty_claims",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_warranty_claims"
        ordering = ["-claim_date"]

    def __str__(self):
        return f"Claim {self.claim_number} for {self.asset.asset_tag}"


class SpaceReservation(models.Model):
    """Book rooms / spaces for events, meetings, etc."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    class Purpose(models.TextChoices):
        MEETING = "meeting", "Meeting"
        EVENT = "event", "Event"
        EXAM = "exam", "Examination"
        TRAINING = "training", "Training"
        INTERVIEW = "interview", "Interview"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="reservations")
    title = models.CharField(max_length=200)
    purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.MEETING)
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="space_reservations",
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    attendees_count = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requires_av = models.BooleanField(default=False, help_text="Requires audio/visual equipment")
    requires_refreshments = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_space_reservations",
    )
    approval_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_space_reservations"
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.room} — {self.title} ({self.date})"


class UtilityTracker(models.Model):
    """Track utility usage (electricity, water, gas) per building."""

    class UtilityType(models.TextChoices):
        ELECTRICITY = "electricity", "Electricity"
        WATER = "water", "Water"
        GAS = "gas", "Gas"
        INTERNET = "internet", "Internet"
        PHONE = "phone", "Phone"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="utility_records")
    utility_type = models.CharField(max_length=20, choices=UtilityType.choices)
    reading_date = models.DateField()
    reading_value = models.DecimalField(max_digits=12, decimal_places=2, help_text="Meter reading")
    units = models.CharField(max_length=20, blank=True, help_text="kWh, gallons, etc.")
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    previous_reading = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    consumption = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "infra_utility_records"
        ordering = ["-reading_date"]

    def __str__(self):
        return f"{self.building.name} — {self.get_utility_type_display()} ({self.reading_date})"


class SafetyInspection(models.Model):
    """Safety inspections and audits."""

    class InspectionType(models.TextChoices):
        FIRE = "fire", "Fire Safety"
        STRUCTURAL = "structural", "Structural"
        ELECTRICAL = "electrical", "Electrical Safety"
        PLUMBING = "plumbing", "Plumbing Safety"
        HVAC = "hvac", "HVAC Safety"
        ACCESSIBILITY = "accessibility", "Accessibility"
        ENVIRONMENTAL = "environmental", "Environmental"
        GENERAL = "general", "General Safety"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        PASSED = "passed", "Passed"
        FAILED = "failed", "Failed"
        FOLLOW_UP = "follow_up", "Follow-up Required"

    class Severity(models.TextChoices):
        NONE = "none", "None"
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="infra_safety_inspections")
    title = models.CharField(max_length=200)
    inspection_type = models.CharField(max_length=20, choices=InspectionType.choices, default=InspectionType.GENERAL)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    inspector_name = models.CharField(max_length=150, blank=True)
    inspector_organization = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    overall_severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.NONE)
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    next_inspection_date = models.DateField(null=True, blank=True)
    certificate_url = models.URLField(max_length=500, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    conducted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_safety_inspections_conducted",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_safety_inspections"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.title} ({self.get_inspection_type_display()})"


class InfrastructureComplianceRecord(models.Model):
    """Compliance documentation and regulatory requirements."""

    class ComplianceType(models.TextChoices):
        FIRE_SAFETY = "fire_safety", "Fire Safety"
        BUILDING_CODE = "building_code", "Building Code"
        ACCESSIBILITY = "accessibility", "Accessibility (ADA)"
        ENVIRONMENTAL = "environmental", "Environmental"
        HEALTH = "health", "Health & Safety"
        DATA_PRIVACY = "data_privacy", "Data Privacy"
        EMPLOYMENT = "employment", "Employment Law"
        FOOD_SAFETY = "food_safety", "Food Safety"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        COMPLIANT = "compliant", "Compliant"
        NON_COMPLIANT = "non_compliant", "Non-Compliant"
        IN_PROGRESS = "in_progress", "In Progress"
        EXEMPT = "exempt", "Exempt"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="infra_compliance_records")
    title = models.CharField(max_length=200)
    compliance_type = models.CharField(max_length=20, choices=ComplianceType.choices, default=ComplianceType.OTHER)
    description = models.TextField(blank=True)
    regulation_reference = models.CharField(max_length=200, blank=True, help_text="e.g. OSHA 1910.22")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    last_audit_date = models.DateField(null=True, blank=True)
    next_audit_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, help_text="Certificate / license expiry")
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_compliance_records",
    )
    document_url = models.URLField(max_length=500, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_compliance_records"
        ordering = ["compliance_type", "title"]

    def __str__(self):
        return f"{self.title} ({self.get_compliance_type_display()})"


class VendorContract(models.Model):
    """Vendor / service provider contracts."""

    class ContractType(models.TextChoices):
        MAINTENANCE = "maintenance", "Maintenance"
        CLEANING = "cleaning", "Cleaning"
        SECURITY = "security", "Security"
        LANDSCAPING = "landscaping", "Landscaping"
        IT_SUPPORT = "it_support", "IT Support"
        HVAC = "hvac", "HVAC Service"
        PEST_CONTROL = "pest_control", "Pest Control"
        ELECTRICAL = "electrical", "Electrical"
        PLUMBING = "plumbing", "Plumbing"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        TERMINATED = "terminated", "Terminated"
        RENEWED = "renewed", "Renewed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="infra_vendor_contracts")
    vendor_name = models.CharField(max_length=200)
    contract_type = models.CharField(max_length=20, choices=ContractType.choices, default=ContractType.OTHER)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    contract_number = models.CharField(max_length=50, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    renewal_date = models.DateField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_frequency = models.CharField(max_length=20, blank=True, help_text="Monthly, Quarterly, Annual")
    contact_person = models.CharField(max_length=150, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(max_length=254, blank=True)
    sla_description = models.TextField(blank=True, help_text="Service Level Agreement details")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    attachments = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_vendor_contracts_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_vendor_contracts"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.vendor_name}: {self.title}"


class InfrastructureEmergencyPlan(models.Model):
    """Emergency response plans and protocols."""

    class PlanType(models.TextChoices):
        FIRE = "fire", "Fire Emergency"
        LOCKDOWN = "lockdown", "Lockdown"
        EVACUATION = "evacuation", "Evacuation"
        MEDICAL = "medical", "Medical Emergency"
        NATURAL_DISASTER = "natural_disaster", "Natural Disaster"
        CHEMICAL_SPILL = "chemical_spill", "Chemical Spill"
        POWER_OUTAGE = "power_outage", "Power Outage"
        ACTIVE_THREAT = "active_threat", "Active Threat"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="infra_emergency_plans")
    title = models.CharField(max_length=200)
    plan_type = models.CharField(max_length=20, choices=PlanType.choices, default=PlanType.OTHER)
    description = models.TextField()
    procedures = models.TextField(help_text="Step-by-step emergency procedures")
    assembly_points = models.TextField(blank=True, help_text="Designated assembly points")
    emergency_contacts = models.JSONField(default=list, blank=True, help_text="List of emergency contacts")
    last_drill_date = models.DateField(null=True, blank=True)
    next_drill_date = models.DateField(null=True, blank=True)
    last_review_date = models.DateField(null=True, blank=True)
    document_url = models.URLField(max_length=500, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_emergency_plans_reviewed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_emergency_plans"
        ordering = ["plan_type", "title"]

    def __str__(self):
        return f"{self.title} ({self.get_plan_type_display()})"


class InfrastructureReport(models.Model):
    """Infrastructure analytics and reports."""

    class ReportType(models.TextChoices):
        WORK_ORDER_SUMMARY = "work_order_summary", "Work Order Summary"
        ASSET_SUMMARY = "asset_summary", "Asset Summary"
        UTILIZATION = "utilization", "Room Utilization"
        UTILITY_USAGE = "utility_usage", "Utility Usage"
        SAFETY_COMPLIANCE = "safety_compliance", "Safety & Compliance"
        MAINTENANCE_COST = "maintenance_cost", "Maintenance Cost"
        ASSET_DEPRECIATION = "asset_depreciation", "Asset Depreciation"
        GENERAL = "general", "General Report"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="infra_reports")
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=25, choices=ReportType.choices, default=ReportType.GENERAL)
    description = models.TextField(blank=True)
    date_from = models.DateField()
    date_to = models.DateField()
    data = models.JSONField(default=dict, blank=True, help_text="Report data as JSON")
    summary = models.TextField(blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_reports",
    )
    file_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "infra_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"


# =============================================================================
# NEW MODELS: Energy Management
# =============================================================================


class EnergyMeter(models.Model):
    """Energy meters for buildings and rooms."""

    class MeterType(models.TextChoices):
        ELECTRIC = "electric", "Electric"
        WATER = "water", "Water"
        GAS = "gas", "Gas"
        SOLAR = "solar", "Solar"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="energy_meters")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="energy_meters")
    meter_number = models.CharField(max_length=50, unique=True)
    meter_type = models.CharField(max_length=10, choices=MeterType.choices)
    installation_date = models.DateField(null=True, blank=True)
    last_reading_date = models.DateField(null=True, blank=True)
    last_reading_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "energy_meters"

    def __str__(self):
        return f"{self.meter_number} ({self.get_meter_type_display()})"


class EnergyReading(models.Model):
    """Energy meter readings over time."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meter = models.ForeignKey(EnergyMeter, on_delete=models.CASCADE, related_name="readings")
    reading_date = models.DateField()
    reading_value = models.DecimalField(max_digits=12, decimal_places=2)
    units = models.CharField(max_length=20, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "energy_readings"
        ordering = ["-reading_date"]
        unique_together = [("meter", "reading_date")]

    def __str__(self):
        return f"{self.meter} - {self.reading_value} {self.units} ({self.reading_date})"


class EnergyAlert(models.Model):
    """Alerts for unusual energy consumption."""

    class AlertType(models.TextChoices):
        HIGH_CONSUMPTION = "high", "High Consumption"
        SPIKE = "spike", "Sudden Spike"
        LEAK = "leak", "Suspected Leak"
        METER_FAULT = "fault", "Meter Fault"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="energy_alerts")
    meter = models.ForeignKey(EnergyMeter, on_delete=models.SET_NULL, null=True, blank=True)
    alert_type = models.CharField(max_length=10, choices=AlertType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    description = models.TextField()
    threshold_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    acknowledged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "energy_alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.building.name} ({self.get_severity_display()})"


# =============================================================================
# NEW MODELS: CCTV / Access Control
# =============================================================================


class CCTVCamera(models.Model):
    """CCTV cameras on campus."""

    class Status(models.TextChoices):
        ONLINE = "online", "Online"
        OFFLINE = "offline", "Offline"
        MAINTENANCE = "maintenance", "Under Maintenance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="cctv_cameras")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="cctv_cameras")
    camera_name = models.CharField(max_length=100)
    camera_id = models.CharField(max_length=50, unique=True)
    location_description = models.CharField(max_length=200, blank=True)
    stream_url = models.URLField(blank=True)
    recording_enabled = models.BooleanField(default=True)
    storage_days = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ONLINE)
    installation_date = models.DateField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cctv_cameras"

    def __str__(self):
        return f"{self.camera_name} ({self.get_status_display()})"


class AccessControlPoint(models.Model):
    """Electronic access control points."""

    class AccessType(models.TextChoices):
        CARD = "card", "Card Reader"
        BIOMETRIC = "biometric", "Biometric"
        PIN = "pin", "PIN Pad"
        MANUAL = "manual", "Manual Lock"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DISABLED = "disabled", "Disabled"
        MAINTENANCE = "maintenance", "Under Maintenance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="access_control_points")
    room = models.ForeignKey(
        Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="access_control_points"
    )
    point_name = models.CharField(max_length=100)
    access_type = models.CharField(max_length=10, choices=AccessType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    access_start_time = models.TimeField(null=True, blank=True)
    access_end_time = models.TimeField(null=True, blank=True)
    restricted_access = models.BooleanField(default=False)
    allowed_roles = models.JSONField(default=list, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "access_control_points"

    def __str__(self):
        return f"{self.point_name} ({self.get_access_type_display()})"


# =============================================================================
# NEW MODELS: Pest Control
# =============================================================================


class PestControlInspection(models.Model):
    """Pest control inspection records."""

    class InspectionType(models.TextChoices):
        ROUTINE = "routine", "Routine"
        REQUESTED = "requested", "Requested"
        FOLLOW_UP = "follow_up", "Follow-up"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="pest_inspections")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    inspection_type = models.CharField(max_length=15, choices=InspectionType.choices, default=InspectionType.ROUTINE)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    inspector_name = models.CharField(max_length=200, blank=True)
    pests_found = models.TextField(blank=True)
    treatment_applied = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    treatment_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    report_file = models.FileField(upload_to="infrastructure/pest_control/", null=True, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pest_control_inspections"

    def __str__(self):
        return f"Pest Inspection - {self.building.name} ({self.scheduled_date})"


class PestTreatment(models.Model):
    """Pest treatment records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inspection = models.ForeignKey(
        PestControlInspection, on_delete=models.SET_NULL, null=True, blank=True, related_name="treatments"
    )
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="pest_treatments")
    treatment_date = models.DateField()
    treatment_type = models.CharField(max_length=100, blank=True)
    pest_target = models.CharField(max_length=100, blank=True)
    chemical_name = models.CharField(max_length=200, blank=True)
    safety_re_entry_hours = models.PositiveIntegerField(default=24)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pest_treatments"

    def __str__(self):
        return f"{self.pest_target} Treatment - {self.building.name} ({self.treatment_date})"


# =============================================================================
# NEW MODELS: Waste Management
# =============================================================================


class WasteCollectionSchedule(models.Model):
    """Waste collection schedules."""

    class WasteType(models.TextChoices):
        GENERAL = "general", "General Waste"
        RECYCLABLE = "recyclable", "Recyclable"
        ORGANIC = "organic", "Organic"
        HAZARDOUS = "hazardous", "Hazardous"
        E_WASTE = "e_waste", "Electronic Waste"

    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="waste_schedules")
    waste_type = models.CharField(max_length=15, choices=WasteType.choices)
    frequency = models.CharField(max_length=10, choices=Frequency.choices)
    collection_day = models.CharField(max_length=10, blank=True)
    collection_time = models.TimeField(null=True, blank=True)
    vendor_name = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "waste_collection_schedules"

    def __str__(self):
        return f"{self.get_waste_type_display()} - {self.building.name}"


class GreenInitiative(models.Model):
    """Green/sustainability initiatives."""

    class InitiativeType(models.TextChoices):
        SOLAR = "solar", "Solar Energy"
        RAINWATER = "rainwater", "Rainwater Harvesting"
        WASTE_REDUCTION = "waste", "Waste Reduction"
        TREE_PLANTATION = "tree", "Tree Plantation"
        ENERGY_AUDIT = "audit", "Energy Audit"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PROPOSED = "proposed", "Proposed"
        APPROVED = "approved", "Approved"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="green_initiatives")
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    initiative_type = models.CharField(max_length=20, choices=InitiativeType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PROPOSED)
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estimated_savings = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    carbon_reduction_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    target_end_date = models.DateField(null=True, blank=True)
    proposed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "green_initiatives"

    def __str__(self):
        return f"{self.title} ({self.get_initiative_type_display()})"


class WaterUsageRecord(models.Model):
    """Water usage tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="water_usage_records")
    record_date = models.DateField()
    usage_gallons = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    leak_detected = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "water_usage_records"
        unique_together = [("building", "record_date")]

    def __str__(self):
        return f"Water - {self.building.name} ({self.usage_gallons} gal)"


class VendorPerformance(models.Model):
    """Vendor performance records."""

    class ServiceType(models.TextChoices):
        CLEANING = "cleaning", "Cleaning"
        ELECTRICAL = "electrical", "Electrical"
        PLUMBING = "plumbing", "Plumbing"
        HVAC = "hvac", "HVAC"
        PEST_CONTROL = "pest", "Pest Control"
        OTHER = "other", "Other"

    class Rating(models.IntegerChoices):
        VERY_POOR = 1, "Very Poor"
        POOR = 2, "Poor"
        AVERAGE = 3, "Average"
        GOOD = 4, "Good"
        EXCELLENT = 5, "Excellent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor_contract = models.ForeignKey(VendorContract, on_delete=models.CASCADE, related_name="performance_records")
    service_type = models.CharField(max_length=15, choices=ServiceType.choices)
    evaluation_date = models.DateField()
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    quality_rating = models.IntegerField(choices=Rating.choices, default=Rating.AVERAGE)
    timeliness_rating = models.IntegerField(choices=Rating.choices, default=Rating.AVERAGE)
    communication_rating = models.IntegerField(choices=Rating.choices, default=Rating.AVERAGE)
    value_rating = models.IntegerField(choices=Rating.choices, default=Rating.AVERAGE)
    comments = models.TextField(blank=True)
    would_rehire = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vendor_performance_records"

    def __str__(self):
        return f"{self.vendor_contract.vendor_name} ({self.evaluation_date})"


class BuildingInspection(models.Model):
    """Building safety inspections."""

    class InspectionType(models.TextChoices):
        FIRE_SAFETY = "fire", "Fire Safety"
        STRUCTURAL = "structural", "Structural"
        ELECTRICAL = "electrical", "Electrical Safety"
        PLUMBING = "plumbing", "Plumbing"
        ACCESSIBILITY = "accessibility", "Accessibility"
        GENERAL = "general", "General"

    class Result(models.TextChoices):
        PASS = "pass", "Pass"
        CONDITIONAL = "conditional", "Conditional"
        FAIL = "fail", "Fail"
        PENDING = "pending", "Pending"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="building_inspections")
    inspection_type = models.CharField(max_length=15, choices=InspectionType.choices)
    inspection_date = models.DateField()
    inspector_name = models.CharField(max_length=200, blank=True)
    result = models.CharField(max_length=15, choices=Result.choices, default=Result.PENDING)
    findings = models.TextField(blank=True)
    violations = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    corrective_actions = models.TextField(blank=True)
    report_file = models.FileField(upload_to="infrastructure/building_inspections/", null=True, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "building_inspections"

    def __str__(self):
        return f"{self.get_inspection_type_display()} - {self.building.name} ({self.inspection_date})"


class InfrastructureAlert(models.Model):
    """Infrastructure alerts."""

    class AlertType(models.TextChoices):
        POWER_OUTAGE = "power", "Power Outage"
        WATER_LEAK = "water", "Water Leak"
        HVAC_FAILURE = "hvac", "HVAC Failure"
        STRUCTURAL = "structural", "Structural Issue"
        FLOODING = "flooding", "Flooding"
        FIRE = "fire", "Fire"
        GAS_LEAK = "gas", "Gas Leak"
        OTHER = "other", "Other"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="infrastructure_alerts")
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    alert_type = models.CharField(max_length=15, choices=AlertType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_alert_assignments",
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "infrastructure_alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title}"


class FloorPlan(models.Model):
    """Floor plans for buildings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="floor_plans")
    floor_number = models.IntegerField(default=0)
    floor_name = models.CharField(max_length=100, blank=True)
    plan_file = models.FileField(upload_to="infrastructure/floor_plans/")
    total_rooms = models.PositiveIntegerField(default=0)
    total_area_sqft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    is_current = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "floor_plans"
        unique_together = [("building", "floor_number")]

    def __str__(self):
        return f"Floor {self.floor_number} - {self.building.name}"


class RoomEquipment(models.Model):
    """Equipment installed in rooms."""

    class EquipmentType(models.TextChoices):
        PROJECTOR = "projector", "Projector"
        WHITEBOARD = "whiteboard", "Whiteboard"
        COMPUTER = "computer", "Computer"
        AC = "ac", "Air Conditioning"
        SMARTBOARD = "smartboard", "Smart Board"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        WORKING = "working", "Working"
        MAINTENANCE = "maintenance", "Under Maintenance"
        BROKEN = "broken", "Broken"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="equipment")
    equipment_type = models.CharField(max_length=15, choices=EquipmentType.choices)
    name = models.CharField(max_length=200)
    asset_tag = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.WORKING)
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "room_equipment"

    def __str__(self):
        return f"{self.name} - {self.room.room_number} ({self.get_status_display()})"


class ParkingLot(models.Model):
    """Parking lot management."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="parking_lots")
    name = models.CharField(max_length=200)
    total_spots = models.PositiveIntegerField(default=0)
    available_spots = models.PositiveIntegerField(default=0)
    is_covered = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "parking_lots"

    def __str__(self):
        return f"{self.name} ({self.available_spots}/{self.total_spots})"


class ParkingAssignment(models.Model):
    """Parking spot assignments."""

    class SpotType(models.TextChoices):
        REGULAR = "regular", "Regular"
        RESERVED = "reserved", "Reserved"
        HANDICAP = "handicap", "Handicap"
        VISITOR = "visitor", "Visitor"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name="assignments")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    spot_number = models.CharField(max_length=20)
    spot_type = models.CharField(max_length=10, choices=SpotType.choices, default=SpotType.REGULAR)
    vehicle_plate = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "parking_assignments"
        unique_together = [("parking_lot", "spot_number")]

    def __str__(self):
        return f"Spot {self.spot_number} - {self.parking_lot.name}"


class LightingSchedule(models.Model):
    """Lighting schedules."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="lighting_schedules")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    zone_name = models.CharField(max_length=200, blank=True)
    day_of_week = models.CharField(max_length=10, blank=True)
    on_time = models.TimeField()
    off_time = models.TimeField()
    brightness_level = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lighting_schedules"

    def __str__(self):
        return f"{self.zone_name or self.building.name} - {self.on_time} to {self.off_time}"


class MaintenanceCostTracking(models.Model):
    """Track maintenance costs."""

    class CostCategory(models.TextChoices):
        ELECTRICAL = "electrical", "Electrical"
        PLUMBING = "plumbing", "Plumbing"
        HVAC = "hvac", "HVAC"
        ROOFING = "roofing", "Roofing"
        PAINTING = "painting", "Painting"
        LANDSCAPING = "landscaping", "Landscaping"
        CLEANING = "cleaning", "Cleaning"
        GENERAL = "general", "General"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="maintenance_cost_tracking")
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name="cost_tracking"
    )
    cost_category = models.CharField(max_length=15, choices=CostCategory.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    vendor = models.CharField(max_length=200, blank=True)
    cost_date = models.DateField()
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "maintenance_cost_tracking"

    def __str__(self):
        return f"{self.get_cost_category_display()} - {self.amount} ({self.cost_date})"


class InfrastructureMaintenanceRequest(models.Model):
    """Maintenance requests submitted by staff."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        EMERGENCY = "emergency", "Emergency"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="infra_maintenance_requests")
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="infra_requests_created"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="infra_requests_assigned",
    )
    estimated_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateField(null=True, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    satisfaction_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "infra_maintenance_requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"
