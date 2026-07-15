"""Transportation Management — Vehicles, routes, student assignments, maintenance."""

import uuid
from django.db import models
from services.auth.models import School, User
from services.hr.models import Employee


class Vehicle(models.Model):
    """School vehicles (buses, vans) used for student transportation."""

    class VehicleType(models.TextChoices):
        BUS = "bus", "Bus"
        MINI_BUS = "mini_bus", "Mini Bus"
        VAN = "van", "Van"
        SUV = "suv", "SUV"
        SEDAN = "sedan", "Sedan"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        IN_MAINTENANCE = "in_maintenance", "In Maintenance"
        RETIRED = "retired", "Retired"
        OUT_OF_SERVICE = "out_of_service", "Out of Service"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="vehicles")
    plate_number = models.CharField(max_length=30, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices, default=VehicleType.BUS)
    model_name = models.CharField(max_length=100, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    capacity = models.PositiveSmallIntegerField(help_text="Maximum number of students")
    color = models.CharField(max_length=50, blank=True)
    chassis_number = models.CharField(max_length=50, blank=True)
    engine_number = models.CharField(max_length=50, blank=True)
    insurance_number = models.CharField(max_length=50, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    fitness_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_vehicles"
        ordering = ["plate_number"]

    def __str__(self):
        return f"{self.plate_number} ({self.get_vehicle_type_display()})"


class Driver(models.Model):
    """Drivers assigned to school vehicles — linked to Employee or standalone."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_LEAVE = "on_leave", "On Leave"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="drivers")
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="driver_records",
        help_text="Link to HR employee record if applicable",
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="driver_profiles",
    )
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_drivers"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Route(models.Model):
    """Bus routes with start/end points and assigned vehicle/driver."""

    class WeekDay(models.TextChoices):
        MONDAY = "monday", "Monday"
        TUESDAY = "tuesday", "Tuesday"
        WEDNESDAY = "wednesday", "Wednesday"
        THURSDAY = "thursday", "Thursday"
        FRIDAY = "friday", "Friday"
        SATURDAY = "saturday", "Saturday"
        SUNDAY = "sunday", "Sunday"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_routes")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_routes",
    )
    driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_routes",
    )
    origin = models.CharField(max_length=255, help_text="Starting point / depot")
    destination = models.CharField(max_length=255, help_text="School location")
    estimated_duration_minutes = models.PositiveSmallIntegerField(default=30)
    operating_days = models.CharField(
        max_length=100, blank=True,
        help_text="Comma-separated days: monday,tuesday,wednesday,thursday,friday",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_routes"
        unique_together = [("school", "name")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class RouteStop(models.Model):
    """Individual stops along a route with pickup/dropoff times and order."""

    class StopType(models.TextChoices):
        PICKUP = "pickup", "Pickup"
        DROPOFF = "dropoff", "Dropoff"
        BOTH = "both", "Both"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="stops",
    )
    name = models.CharField(max_length=200, help_text="e.g. Main Gate, City Center")
    address = models.CharField(max_length=255, blank=True)
    landmark = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    stop_order = models.PositiveSmallIntegerField(help_text="Order along the route (1 = first)")
    stop_type = models.CharField(max_length=20, choices=StopType.choices, default=StopType.BOTH)
    pickup_time = models.TimeField(null=True, blank=True, help_text="Estimated pickup time at this stop")
    dropoff_time = models.TimeField(null=True, blank=True, help_text="Estimated dropoff time at this stop")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_route_stops"
        ordering = ["route", "stop_order"]
        unique_together = [("route", "stop_order")]

    def __str__(self):
        return f"{self.name} (Stop #{self.stop_order})"


class StudentRoute(models.Model):
    """Many-to-many relationship assigning students to specific route stops."""

    class PickupDropoff(models.TextChoices):
        PICKUP = "pickup", "Pickup Only"
        DROPOFF = "dropoff", "Dropoff Only"
        BOTH = "both", "Both"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="student_assignments")
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="transport_assignments",
    )
    pickup_stop = models.ForeignKey(
        RouteStop, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="pickup_students",
    )
    dropoff_stop = models.ForeignKey(
        RouteStop, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="dropoff_students",
    )
    service_type = models.CharField(
        max_length=20, choices=PickupDropoff.choices, default=PickupDropoff.BOTH,
    )
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_student_assignments"
        unique_together = [("route", "student", "effective_from")]
        ordering = ["route", "student"]

    def __str__(self):
        return f"{self.student} on {self.route}"


class VehicleMaintenance(models.Model):
    """Maintenance and service records for vehicles."""

    class MaintenanceType(models.TextChoices):
        ROUTINE = "routine", "Routine Service"
        REPAIR = "repair", "Repair"
        INSPECTION = "inspection", "Inspection"
        TIRE = "tire", "Tire Change"
        ENGINE = "engine", "Engine Service"
        BODY = "body", "Body Work"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="maintenance_records",
    )
    maintenance_type = models.CharField(max_length=20, choices=MaintenanceType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    odometer_reading = models.PositiveIntegerField(null=True, blank=True, help_text="Odometer at service (km)")
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vendor_name = models.CharField(max_length=150, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="performed_maintenance",
    )
    next_service_date = models.DateField(null=True, blank=True)
    next_service_odometer = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_maintenance"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.get_maintenance_type_display()} ({self.scheduled_date})"
