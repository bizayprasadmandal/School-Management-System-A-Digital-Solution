"""Hostel / Accommodation Management — Hostels, rooms, allocations, fees, visitors."""

import uuid
from decimal import Decimal
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
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="warden_hostels",
    )
    assistant_warden = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
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
        return HostelAllocation.objects.filter(
            room__hostel=self, status=HostelAllocation.Status.ACTIVE
        ).count()

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
        "students.Student", on_delete=models.CASCADE, related_name="hostel_allocations",
    )
    room = models.ForeignKey(
        HostelRoom, on_delete=models.CASCADE, related_name="allocations",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    check_in_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    allocated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
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
        Hostel, on_delete=models.CASCADE, related_name="fee_structures",
    )
    room_type = models.CharField(
        max_length=20, choices=HostelRoom.RoomType.choices, blank=True,
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
        "students.Student", on_delete=models.CASCADE, related_name="hostel_visitors",
    )
    purpose = models.CharField(max_length=200, blank=True)
    in_time = models.DateTimeField()
    out_time = models.DateTimeField(null=True, blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    checked_in_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="visitor_checkins",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "hostel_visitors"
        ordering = ["-in_time"]

    def __str__(self):
        return f"{self.visitor_name} → {self.student_visited}"
