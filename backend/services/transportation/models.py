"""Transportation Management — Vehicles, routes, student assignments, maintenance."""

import uuid

from django.conf import settings
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
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="driver_records",
        help_text="Link to HR employee record if applicable",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_routes",
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_routes",
    )
    origin = models.CharField(max_length=255, help_text="Starting point / depot")
    destination = models.CharField(max_length=255, help_text="School location")
    estimated_duration_minutes = models.PositiveSmallIntegerField(default=30)
    operating_days = models.CharField(
        max_length=100,
        blank=True,
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
        Route,
        on_delete=models.CASCADE,
        related_name="stops",
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
        "students.Student",
        on_delete=models.CASCADE,
        related_name="transport_assignments",
    )
    pickup_stop = models.ForeignKey(
        RouteStop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pickup_students",
    )
    dropoff_stop = models.ForeignKey(
        RouteStop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dropoff_students",
    )
    service_type = models.CharField(
        max_length=20,
        choices=PickupDropoff.choices,
        default=PickupDropoff.BOTH,
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
        Vehicle,
        on_delete=models.CASCADE,
        related_name="maintenance_records",
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
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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


class TransportFee(models.Model):
    """Transportation fees for students."""

    class FeeType(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        TERM = "term", "Term"
        ANNUAL = "annual", "Annual"
        ONE_TIME = "one_time", "One-Time"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        WAIVED = "waived", "Waived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_fees")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="transport_fees")
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    fee_type = models.CharField(max_length=20, choices=FeeType.choices, default=FeeType.MONTHLY)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    academic_year = models.ForeignKey("students.AcademicYear", on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_fees"
        ordering = ["-due_date"]

    def __str__(self):
        return f"{self.student} - {self.get_fee_type_display()} ({self.amount})"


class VehicleInsurance(models.Model):
    """Vehicle insurance tracking."""

    class InsuranceType(models.TextChoices):
        COMPREHENSIVE = "comprehensive", "Comprehensive"
        THIRD_PARTY = "third_party", "Third Party"
        LIABILITY = "liability", "Liability"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        PENDING_RENEWAL = "pending_renewal", "Pending Renewal"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="insurance_records")
    insurance_type = models.CharField(max_length=20, choices=InsuranceType.choices, default=InsuranceType.COMPREHENSIVE)
    provider = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    document_url = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_vehicle_insurance"
        ordering = ["-end_date"]

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.provider} ({self.policy_number})"


class DailyTransportAttendance(models.Model):
    """Daily student attendance on transport."""

    class AttendanceType(models.TextChoices):
        PICKUP = "pickup", "Pickup"
        DROPOFF = "dropoff", "Dropoff"
        BOTH = "both", "Both"

    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        EXCUSED = "excused", "Excused"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_attendance")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="transport_attendance")
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    attendance_type = models.CharField(max_length=20, choices=AttendanceType.choices, default=AttendanceType.BOTH)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    pickup_time = models.TimeField(null=True, blank=True)
    dropoff_time = models.TimeField(null=True, blank=True)
    pickup_stop = models.ForeignKey(
        RouteStop, on_delete=models.SET_NULL, null=True, blank=True, related_name="pickup_attendance"
    )
    dropoff_stop = models.ForeignKey(
        RouteStop, on_delete=models.SET_NULL, null=True, blank=True, related_name="dropoff_attendance"
    )
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_daily_attendance"
        ordering = ["-date", "student"]
        unique_together = [("student", "route", "date", "attendance_type")]

    def __str__(self):
        return f"{self.student} - {self.date} ({self.get_status_display()})"


class TransportIncidentReport(models.Model):
    """Transport incident tracking."""

    class IncidentType(models.TextChoices):
        ACCIDENT = "accident", "Accident"
        BREAKDOWN = "breakdown", "Breakdown"
        MEDICAL = "medical", "Medical Emergency"
        BEHAVIORAL = "behavioral", "Behavioral"
        ROUTE_DELAY = "route_delay", "Route Delay"
        VEHICLE_DAMAGE = "vehicle_damage", "Vehicle Damage"
        WEATHER = "weather", "Weather Related"
        OTHER = "other", "Other"

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
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_incidents")
    incident_type = models.CharField(max_length=20, choices=IncidentType.choices)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.LOW)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REPORTED)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    incident_date = models.DateField()
    incident_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    students_involved = models.JSONField(default=list, blank=True)
    injuries_reported = models.BooleanField(default=False)
    injury_details = models.TextField(blank=True)
    witnesses = models.TextField(blank=True)
    police_report = models.BooleanField(default=False)
    police_report_number = models.CharField(max_length=50, blank=True)
    insurance_claim = models.BooleanField(default=False)
    insurance_claim_number = models.CharField(max_length=50, blank=True)
    corrective_actions = models.TextField(blank=True)
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transport_incidents_resolved",
    )
    resolved_date = models.DateField(null=True, blank=True)
    attachments = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_incidents"
        ordering = ["-incident_date"]

    def __str__(self):
        return f"{self.get_incident_type_display()} - {self.incident_date}"


class VehicleInspection(models.Model):
    """Pre-trip safety inspections."""

    class InspectionType(models.TextChoices):
        PRE_TRIP = "pre_trip", "Pre-Trip"
        POST_TRIP = "post_trip", "Post-Trip"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        ANNUAL = "annual", "Annual"

    class Result(models.TextChoices):
        PASS = "pass", "Pass"
        FAIL = "fail", "Fail"
        NEEDS_REPAIR = "needs_repair", "Needs Repair"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="inspections")
    inspection_type = models.CharField(max_length=20, choices=InspectionType.choices, default=InspectionType.PRE_TRIP)
    inspection_date = models.DateField()
    inspector_name = models.CharField(max_length=150)
    result = models.CharField(max_length=20, choices=Result.choices, default=Result.PASS)
    odometer_reading = models.PositiveIntegerField(null=True, blank=True)
    exterior_check = models.BooleanField(default=True)
    interior_check = models.BooleanField(default=True)
    tires_check = models.BooleanField(default=True)
    lights_check = models.BooleanField(default=True)
    brakes_check = models.BooleanField(default=True)
    signals_check = models.BooleanField(default=True)
    emergency_equipment = models.BooleanField(default=True)
    first_aid_kit = models.BooleanField(default=True)
    fire_extinguisher = models.BooleanField(default=True)
    defects_found = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_inspections"
        ordering = ["-inspection_date"]

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.get_inspection_type_display()} ({self.inspection_date})"


class TripSchedule(models.Model):
    """Field trip scheduling."""

    class TripType(models.TextChoices):
        FIELD_TRIP = "field_trip", "Field Trip"
        SPORTS_EVENT = "sports_event", "Sports Event"
        CULTURAL_EVENT = "cultural_event", "Cultural Event"
        EXAMINATION = "examination", "Examination"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="trip_schedules")
    title = models.CharField(max_length=200)
    trip_type = models.CharField(max_length=20, choices=TripType.choices, default=TripType.FIELD_TRIP)
    destination = models.CharField(max_length=255)
    trip_date = models.DateField()
    departure_time = models.TimeField()
    return_time = models.TimeField(null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    expected_students = models.PositiveIntegerField(default=0)
    actual_students = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    purpose = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="trip_approvals"
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="trip_creations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_trip_schedules"
        ordering = ["-trip_date"]

    def __str__(self):
        return f"{self.title} ({self.trip_date})"


class FuelLog(models.Model):
    """Fuel tracking and costs."""

    class FuelType(models.TextChoices):
        DIESEL = "diesel", "Diesel"
        PETROL = "petrol", "Petrol"
        CNG = "cng", "CNG"
        ELECTRIC = "electric", "Electric"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="fuel_logs")
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices, default=FuelType.DIESEL)
    fill_date = models.DateField()
    odometer_reading = models.PositiveIntegerField()
    liters = models.DecimalField(max_digits=8, decimal_places=2)
    cost_per_liter = models.DecimalField(max_digits=8, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    station_name = models.CharField(max_length=200, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    filled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_fuel_logs"
        ordering = ["-fill_date"]

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.liters}L ({self.fill_date})"


class TransportNotification(models.Model):
    """Transport notifications to parents/students."""

    class NotificationType(models.TextChoices):
        DELAY = "delay", "Delay Alert"
        CANCELLATION = "cancellation", "Cancellation"
        ROUTE_CHANGE = "route_change", "Route Change"
        PICKUP_COMPLETE = "pickup_complete", "Pickup Complete"
        DROPOFF_COMPLETE = "dropoff_complete", "Dropoff Complete"
        INCIDENT = "incident", "Incident"
        FEE_REMINDER = "fee_reminder", "Fee Reminder"
        GENERAL = "general", "General"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_notifications")
    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices, default=NotificationType.GENERAL
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    recipients = models.JSONField(default=list, blank=True, help_text="List of recipient IDs or emails")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_notification_type_display()})"


class TransportReport(models.Model):
    """Transport analytics and reports."""

    class ReportType(models.TextChoices):
        ROUTE_SUMMARY = "route_summary", "Route Summary"
        VEHICLE_STATUS = "vehicle_status", "Vehicle Status"
        FUEL_CONSUMPTION = "fuel_consumption", "Fuel Consumption"
        INCIDENT_SUMMARY = "incident_summary", "Incident Summary"
        FEE_COLLECTION = "fee_collection", "Fee Collection"
        ATTENDANCE_SUMMARY = "attendance_summary", "Attendance Summary"
        MAINTENANCE_COST = "maintenance_cost", "Maintenance Cost"
        GENERAL = "general", "General Report"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transport_reports")
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=25, choices=ReportType.choices, default=ReportType.GENERAL)
    date_from = models.DateField()
    date_to = models.DateField()
    report_data = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"


class VehicleDocument(models.Model):
    """Vehicle document management."""

    class DocumentType(models.TextChoices):
        REGISTRATION = "registration", "Registration"
        INSURANCE = "insurance", "Insurance"
        PERMIT = "permit", "Permit"
        FITNESS = "fitness", "Fitness Certificate"
        POLLUTION = "pollution", "Pollution Certificate"
        TAX = "tax", "Tax Receipt"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    document_name = models.CharField(max_length=200)
    document_number = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    issued_by = models.CharField(max_length=200, blank=True)
    document_url = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_vehicle_documents"
        ordering = ["expiry_date"]

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.get_document_type_display()}"


# =============================================================================
# NEW MODELS: GPS Tracking
# =============================================================================


class VehicleGPSLog(models.Model):
    """GPS location logging for vehicles."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE, related_name="gps_logs")
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    speed_kmh = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    heading = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField()
    # Status
    ignition_on = models.BooleanField(default=True)
    battery_level = models.PositiveIntegerField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vehicle_gps_logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"GPS: {self.vehicle} at ({self.latitude}, {self.longitude})"


class GeofenceZone(models.Model):
    """Geofence zones for vehicle monitoring."""

    class ZoneType(models.TextChoices):
        SCHOOL = "school", "School Zone"
        BUS_STOP = "stop", "Bus Stop"
        RESTRICTED = "restricted", "Restricted Area"
        DANGER = "danger", "Danger Zone"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="geofence_zones")
    name = models.CharField(max_length=200)
    zone_type = models.CharField(max_length=15, choices=ZoneType.choices)
    # Coordinates (simplified polygon as center + radius)
    center_latitude = models.DecimalField(max_digits=10, decimal_places=7)
    center_longitude = models.DecimalField(max_digits=10, decimal_places=7)
    radius_meters = models.PositiveIntegerField(default=500)
    # Polygon coordinates for complex shapes
    polygon_coordinates = models.JSONField(default=list, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Alerts
    alert_on_entry = models.BooleanField(default=False)
    alert_on_exit = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "geofence_zones"

    def __str__(self):
        return f"{self.name} ({self.get_zone_type_display()})"


class GeofenceAlert(models.Model):
    """Alerts triggered by geofence violations."""

    class AlertType(models.TextChoices):
        ENTRY = "entry", "Zone Entry"
        EXIT = "exit", "Zone Exit"
        SPEED = "speed", "Speed Violation"
        DEVIATION = "deviation", "Route Deviation"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE, related_name="geofence_alerts")
    zone = models.ForeignKey(GeofenceZone, on_delete=models.SET_NULL, null=True, blank=True)
    gps_log = models.ForeignKey(VehicleGPSLog, on_delete=models.SET_NULL, null=True, blank=True)
    alert_type = models.CharField(max_length=15, choices=AlertType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    description = models.TextField()
    # Speed
    speed_recorded = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    speed_limit = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "geofence_alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.vehicle} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Bus Tracking
# =============================================================================


class BusTracking(models.Model):
    """Real-time bus tracking for parents/students."""

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        ON_ROUTE = "on_route", "On Route"
        AT_STOP = "at_stop", "At Stop"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE, related_name="tracking_sessions")
    route = models.ForeignKey("Route", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NOT_STARTED)
    # Schedule
    scheduled_start = models.TimeField()
    scheduled_end = models.TimeField()
    actual_start = models.TimeField(null=True, blank=True)
    actual_end = models.TimeField(null=True, blank=True)
    # Current location
    current_stop = models.ForeignKey("RouteStop", on_delete=models.SET_NULL, null=True, blank=True)
    next_stop = models.ForeignKey(
        "RouteStop", on_delete=models.SET_NULL, null=True, blank=True, related_name="next_stop_tracking"
    )
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    # Students
    total_students_expected = models.PositiveIntegerField(default=0)
    total_students_onboard = models.PositiveIntegerField(default=0)
    total_students_picked_up = models.PositiveIntegerField(default=0)
    total_students_dropped = models.PositiveIntegerField(default=0)
    # Metadata
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bus_tracking"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"Bus {self.vehicle.vehicle_number} - {self.get_status_display()} ({self.date})"


class StopETA(models.Model):
    """Estimated time of arrival at each stop."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tracking = models.ForeignKey(BusTracking, on_delete=models.CASCADE, related_name="stop_etas")
    stop = models.ForeignKey("RouteStop", on_delete=models.CASCADE, related_name="etas")
    scheduled_time = models.TimeField()
    estimated_time = models.DateTimeField(null=True, blank=True)
    actual_time = models.DateTimeField(null=True, blank=True)
    # Students
    students_expected = models.PositiveIntegerField(default=0)
    students_picked_up = models.PositiveIntegerField(default=0)
    students_dropped = models.PositiveIntegerField(default=0)
    # Delay
    delay_minutes = models.IntegerField(default=0)
    delay_reason = models.CharField(max_length=200, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stop_etas"
        ordering = ["scheduled_time"]

    def __str__(self):
        return f"ETA: {self.stop} - {self.scheduled_time}"


# =============================================================================
# NEW MODELS: Driver Management (Extended)
# =============================================================================


class DriverLicense(models.Model):
    """Driver license tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.OneToOneField("Driver", on_delete=models.CASCADE, related_name="license_info")
    license_number = models.CharField(max_length=50, unique=True)
    license_type = models.CharField(max_length=50, blank=True, help_text="Commercial, Regular, etc.")
    issue_date = models.DateField()
    expiry_date = models.DateField()
    issuing_authority = models.CharField(max_length=200, blank=True)
    # Endorsements
    endorsements = models.JSONField(default=list, blank=True)
    restrictions = models.JSONField(default=list, blank=True)
    # Document
    license_image = models.ImageField(upload_to="transportation/licenses/", null=True, blank=True)
    # Status
    is_valid = models.BooleanField(default=True)
    suspension_reason = models.TextField(blank=True)
    suspension_date = models.DateField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "driver_licenses"

    def __str__(self):
        return f"License: {self.driver} - {self.license_number}"

    @property
    def is_expired(self):
        from django.utils import timezone

        return timezone.now().date() > self.expiry_date


class DriverPerformance(models.Model):
    """Driver performance tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey("Driver", on_delete=models.CASCADE, related_name="performance_records")
    evaluation_date = models.DateField()
    evaluator = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True)
    # Ratings (1-5)
    safety_rating = models.PositiveSmallIntegerField(default=3)
    punctuality_rating = models.PositiveSmallIntegerField(default=3)
    vehicle_care_rating = models.PositiveSmallIntegerField(default=3)
    student_interaction_rating = models.PositiveSmallIntegerField(default=3)
    overall_rating = models.DecimalField(max_digits=3, decimal_places=2, default=3)
    # Metrics
    total_trips = models.PositiveIntegerField(default=0)
    accidents = models.PositiveIntegerField(default=0)
    complaints = models.PositiveIntegerField(default=0)
    compliments = models.PositiveIntegerField(default=0)
    on_time_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    # Notes
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "driver_performance"
        ordering = ["-evaluation_date"]

    def __str__(self):
        return f"Performance: {self.driver} ({self.evaluation_date})"


# =============================================================================
# NEW MODELS: Vehicle Tracking
# =============================================================================


class VehicleConditionReport(models.Model):
    """Pre/post trip vehicle condition reports."""

    class ReportType(models.TextChoices):
        PRE_TRIP = "pre_trip", "Pre-Trip"
        POST_TRIP = "post_trip", "Post-Trip"
        SPOT_CHECK = "spot_check", "Spot Check"

    class Condition(models.TextChoices):
        EXCELLENT = "excellent", "Excellent"
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        POOR = "poor", "Poor"
        NOT_WORKING = "not_working", "Not Working"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE, related_name="condition_reports")
    driver = models.ForeignKey("Driver", on_delete=models.SET_NULL, null=True, blank=True)
    report_type = models.CharField(max_length=15, choices=ReportType.choices)
    report_date = models.DateField()
    # Checks
    tires_condition = models.CharField(max_length=15, choices=Condition.choices, default=Condition.GOOD)
    brakes_condition = models.CharField(max_length=15, choices=Condition.choices, default=Condition.GOOD)
    lights_condition = models.CharField(max_length=15, choices=Condition.choices, default=Condition.GOOD)
    mirrors_condition = models.CharField(max_length=15, choices=Condition.choices, default=Condition.GOOD)
    body_condition = models.CharField(max_length=15, choices=Condition.choices, default=Condition.GOOD)
    interior_condition = models.CharField(max_length=15, choices=Condition.choices, default=Condition.GOOD)
    fuel_level = models.PositiveIntegerField(default=100, help_text="Percentage")
    mileage = models.PositiveIntegerField(default=0)
    # Issues
    issues_found = models.TextField(blank=True)
    photos = models.ImageField(upload_to="transportation/condition_reports/", null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vehicle_condition_reports"
        ordering = ["-report_date"]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.vehicle} ({self.report_date})"


# =============================================================================
# NEW MODELS: Route Optimization
# =============================================================================


class RouteOptimization(models.Model):
    """Route optimization records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="route_optimizations")
    route = models.ForeignKey("Route", on_delete=models.SET_NULL, null=True, blank=True)
    optimization_date = models.DateField()
    # Before
    original_distance_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    original_time_minutes = models.PositiveIntegerField(default=0)
    original_fuel_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # After
    optimized_distance_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    optimized_time_minutes = models.PositiveIntegerField(default=0)
    optimized_fuel_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Savings
    distance_saved_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    time_saved_minutes = models.PositiveIntegerField(default=0)
    fuel_saved = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Metadata
    optimized_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "route_optimizations"
        ordering = ["-optimization_date"]

    def __str__(self):
        return f"Optimization - {self.route} ({self.optimization_date})"


# =============================================================================
# NEW MODELS: Transportation Reporting
# =============================================================================


class TransportationDailyReport(models.Model):
    """Daily transportation operations report."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="transport_daily_reports")
    date = models.DateField()
    # Operations
    total_vehicles_active = models.PositiveIntegerField(default=0)
    total_trips_completed = models.PositiveIntegerField(default=0)
    total_routes_served = models.PositiveIntegerField(default=0)
    # Students
    total_students_transport = models.PositiveIntegerField(default=0)
    avg_occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Fuel
    total_fuel_consumed = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_fuel_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Incidents
    total_incidents = models.PositiveIntegerField(default=0)
    total_delays = models.PositiveIntegerField(default=0)
    avg_delay_minutes = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Maintenance
    vehicles_maintained = models.PositiveIntegerField(default=0)
    vehicles_in_repair = models.PositiveIntegerField(default=0)
    # Cost
    total_operational_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Metadata
    generated_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transportation_daily_reports"
        unique_together = [("school", "date")]
        ordering = ["-date"]

    def __str__(self):
        return f"Transport Report - {self.date}"


# =============================================================================
# NEW MODELS: Parent Portal
# =============================================================================


class ParentTransportAccess(models.Model):
    """Parent access to transport tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="parent_transport_access")
    parent = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="transport_access")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="parent_transport_access")
    # Settings
    tracking_enabled = models.BooleanField(default=True)
    notifications_enabled = models.BooleanField(default=True)
    email_alerts = models.BooleanField(default=True)
    sms_alerts = models.BooleanField(default=False)
    # Alert preferences
    alert_pickup = models.BooleanField(default=True)
    alert_dropoff = models.BooleanField(default=True)
    alert_delay = models.BooleanField(default=True)
    alert_incident = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "parent_transport_access"
        unique_together = [("parent", "student")]

    def __str__(self):
        return f"Transport Access: {self.parent} for {self.student}"


# =============================================================================
# NEW MODELS: Transport Compliance
# =============================================================================


class TransportComplianceRecord(models.Model):
    """Compliance records for transportation."""

    class ComplianceType(models.TextChoices):
        VEHICLE_REGISTRATION = "reg", "Vehicle Registration"
        INSURANCE = "insurance", "Insurance"
        SAFETY_INSPECTION = "safety", "Safety Inspection"
        DRIVER_LICENSE = "license", "Driver License"
        EMERGENCY_EQUIPMENT = "emergency", "Emergency Equipment"
        ENVIRONMENTAL = "env", "Environmental"

    class Status(models.TextChoices):
        COMPLIANT = "compliant", "Compliant"
        EXPIRING = "expiring", "Expiring Soon"
        EXPIRED = "expired", "Expired"
        NON_COMPLIANT = "non_compliant", "Non-Compliant"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="transport_compliance")
    compliance_type = models.CharField(max_length=15, choices=ComplianceType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.COMPLIANT)
    # Reference
    vehicle = models.ForeignKey("Vehicle", on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey("Driver", on_delete=models.SET_NULL, null=True, blank=True)
    # Details
    document_number = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    issued_by = models.CharField(max_length=200, blank=True)
    # Document
    document_file = models.FileField(upload_to="transportation/compliance/", null=True, blank=True)
    # Alerts
    alert_days_before = models.PositiveIntegerField(default=30, help_text="Days before expiry to alert")
    last_alert_sent = models.DateField(null=True, blank=True)
    # Metadata
    verified_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_compliance_records"
        ordering = ["expiry_date"]

    def __str__(self):
        return f"{self.get_compliance_type_display()} - {self.get_status_display()}"


# =============================================================================
# NEW MODELS: Student Transport
# =============================================================================


class StudentTransportProfile(models.Model):
    """Student transport profile and preferences."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField("students.Student", on_delete=models.CASCADE, related_name="transport_profile")
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="student_transport_profiles"
    )
    # Route
    assigned_route = models.ForeignKey("Route", on_delete=models.SET_NULL, null=True, blank=True)
    assigned_stop = models.ForeignKey("RouteStop", on_delete=models.SET_NULL, null=True, blank=True)
    # Schedule
    needs_morning = models.BooleanField(default=True)
    needs_evening = models.BooleanField(default=True)
    # Special needs
    has_disability = models.BooleanField(default=False)
    disability_notes = models.TextField(blank=True)
    needs_wheelchair = models.BooleanField(default=False)
    needs_escort = models.BooleanField(default=False)
    # Emergency
    emergency_pickup_person = models.CharField(max_length=200, blank=True)
    emergency_pickup_phone = models.CharField(max_length=30, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_transport_profiles"

    def __str__(self):
        return f"Transport: {self.student}"


# =============================================================================
# NEW MODELS: Transport Alert
# =============================================================================


class TransportAlert(models.Model):
    """Transport system alerts."""

    class AlertType(models.TextChoices):
        DELAY = "delay", "Route Delay"
        CANCELLATION = "cancel", "Route Cancellation"
        BREAKDOWN = "breakdown", "Vehicle Breakdown"
        ACCIDENT = "accident", "Accident"
        WEATHER = "weather", "Weather Advisory"
        ROUTE_CHANGE = "route_change", "Route Change"
        MAINTENANCE = "maintenance", "Scheduled Maintenance"

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="transport_alerts")
    vehicle = models.ForeignKey("Vehicle", on_delete=models.SET_NULL, null=True, blank=True)
    route = models.ForeignKey("Route", on_delete=models.SET_NULL, null=True, blank=True)
    alert_type = models.CharField(max_length=15, choices=AlertType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    # Impact
    affected_students = models.PositiveIntegerField(default=0)
    affected_routes = models.JSONField(default=list, blank=True)
    estimated_delay_minutes = models.PositiveIntegerField(null=True, blank=True)
    # Actions
    acknowledged_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    resolved_by = models.ForeignKey(
        "auth_service.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transport_alert_resolutions",
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    # Notification
    parents_notified = models.BooleanField(default=False)
    staff_notified = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title}"


# =============================================================================
# NEW MODELS: Vehicle Pool
# =============================================================================


class VehiclePool(models.Model):
    """Vehicle pool for shared/ad-hoc use."""

    class PoolType(models.TextChoices):
        FIELD_TRIP = "field_trip", "Field Trip"
        STAFF = "staff", "Staff Use"
        EMERGENCY = "emergency", "Emergency"
        MAINTENANCE_REPLACEMENT = "replacement", "Maintenance Replacement"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BOOKED = "booked", "Booked"
        IN_USE = "in_use", "In Use"
        MAINTENANCE = "maintenance", "Under Maintenance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="vehicle_pools")
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE, related_name="pool_bookings")
    pool_type = models.CharField(max_length=15, choices=PoolType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.AVAILABLE)
    # Booking
    booked_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    purpose = models.CharField(max_length=200, blank=True)
    destination = models.CharField(max_length=300, blank=True)
    # Schedule
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    # Passengers
    expected_passengers = models.PositiveIntegerField(default=0)
    actual_passengers = models.PositiveIntegerField(default=0)
    # Approval
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        "auth_service.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicle_pool_approvals"
    )
    # Mileage
    start_mileage = models.PositiveIntegerField(default=0)
    end_mileage = models.PositiveIntegerField(default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vehicle_pool_bookings"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.vehicle} - {self.purpose} ({self.start_date})"


class TransportSchedule(models.Model):
    """Weekly transport schedule template."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="transport_schedules")
    route = models.ForeignKey("Route", on_delete=models.CASCADE, related_name="schedules")
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
        ],
    )
    # Times
    pickup_start = models.TimeField()
    pickup_end = models.TimeField()
    dropoff_start = models.TimeField(null=True, blank=True)
    dropoff_end = models.TimeField(null=True, blank=True)
    # Vehicle
    vehicle = models.ForeignKey("Vehicle", on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey("Driver", on_delete=models.SET_NULL, null=True, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_schedules"
        unique_together = [("route", "day_of_week")]

    def __str__(self):
        return f"{self.route} - {self.day_of_week.title()}"


class TransportFeeStructure(models.Model):
    """Transport fee structures."""

    class FeeType(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        ANNUAL = "annual", "Annual"
        PER_TRIP = "per_trip", "Per Trip"
        ONE_TIME = "one_time", "One Time"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="transport_fee_structures")
    name = models.CharField(max_length=200)
    fee_type = models.CharField(max_length=15, choices=FeeType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Eligibility
    route = models.ForeignKey("Route", on_delete=models.SET_NULL, null=True, blank=True)
    min_distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    max_distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    # Discounts
    sibling_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    early_bird_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Status
    is_active = models.BooleanField(default=True)
    academic_year = models.CharField(max_length=10)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_fee_structures"

    def __str__(self):
        return f"{self.name} - ${self.amount} ({self.get_fee_type_display()})"


class TransportIncident(models.Model):
    """Detailed transport incident records."""

    class IncidentType(models.TextChoices):
        ACCIDENT = "accident", "Accident"
        BREAKDOWN = "breakdown", "Breakdown"
        DELAY = "delay", "Major Delay"
        MEDICAL = "medical", "Medical Emergency"
        BEHAVIORAL = "behavioral", "Student Behavioral Issue"
        WEATHER = "weather", "Weather Related"
        OTHER = "other", "Other"

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
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="transport_detailed_incidents"
    )
    vehicle = models.ForeignKey("Vehicle", on_delete=models.SET_NULL, null=True, blank=True)
    route = models.ForeignKey("Route", on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey("Driver", on_delete=models.SET_NULL, null=True, blank=True)
    incident_type = models.CharField(max_length=15, choices=IncidentType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.REPORTED)
    # Details
    description = models.TextField()
    location = models.CharField(max_length=300, blank=True)
    incident_date = models.DateField()
    incident_time = models.TimeField(null=True, blank=True)
    # People involved
    reported_by = models.ForeignKey(
        "auth_service.User", on_delete=models.SET_NULL, null=True, related_name="transport_incidents_reported"
    )
    students_involved = models.ManyToManyField("students.Student", blank=True, related_name="transport_incidents")
    witnesses = models.TextField(blank=True)
    # Injuries
    injuries_reported = models.BooleanField(default=False)
    injury_details = models.TextField(blank=True)
    first_aid_administered = models.BooleanField(default=False)
    # Investigation
    investigation_notes = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)
    # Resolution
    corrective_actions = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        "auth_service.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transport_incidents_resolved_detail",
    )
    # Insurance
    insurance_claim_filed = models.BooleanField(default=False)
    claim_number = models.CharField(max_length=50, blank=True)
    # Photos
    photos = models.ImageField(upload_to="transportation/incidents/", null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_incidents_detail"
        ordering = ["-incident_date"]

    def __str__(self):
        return f"{self.get_incident_type_display()} - {self.get_severity_display()} ({self.incident_date})"


class TransportBudget(models.Model):
    """Annual transport budget."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="transport_budgets")
    academic_year = models.CharField(max_length=10)
    # Budget categories
    fuel_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    maintenance_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    salary_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_vehicle_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    miscellaneous_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Actual spending
    fuel_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    maintenance_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    salary_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_vehicle_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    miscellaneous_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Revenue
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Metadata
    approved_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_budgets"
        unique_together = [("school", "academic_year")]

    def __str__(self):
        return f"Transport Budget {self.academic_year}"

    @property
    def remaining_budget(self):
        return self.total_budget - self.total_spent

    @property
    def budget_utilization(self):
        if self.total_budget == 0:
            return 0
        return round((self.total_spent / self.total_budget) * 100, 2)


class TransportAuditLog(models.Model):
    """Audit log for transport operations."""

    class ActionType(models.TextChoices):
        VEHICLE_ADDED = "vehicle_add", "Vehicle Added"
        VEHICLE_UPDATED = "vehicle_update", "Vehicle Updated"
        ROUTE_CREATED = "route_create", "Route Created"
        ROUTE_MODIFIED = "route_modify", "Route Modified"
        DRIVER_ASSIGNED = "driver_assign", "Driver Assigned"
        MAINTENANCE_SCHEDULED = "maint_schedule", "Maintenance Scheduled"
        FEE_COLLECTED = "fee_collect", "Fee Collected"
        INCIDENT_REPORTED = "incident", "Incident Reported"
        ALERT_SENT = "alert", "Alert Sent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="transport_audit_logs")
    user = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    target_model = models.CharField(max_length=50, blank=True)
    target_id = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_audit_logs"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.get_action_type_display()} by {self.user} ({self.timestamp})"


class TransportMonthlyReport(models.Model):
    """Monthly transport performance report."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="transport_monthly_reports"
    )
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    # Operations
    total_operational_days = models.PositiveIntegerField(default=0)
    total_trips = models.PositiveIntegerField(default=0)
    total_routes_active = models.PositiveIntegerField(default=0)
    # Vehicles
    vehicles_active = models.PositiveIntegerField(default=0)
    vehicles_maintained = models.PositiveIntegerField(default=0)
    avg_fleet_age_years = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    # Students
    total_students_served = models.PositiveIntegerField(default=0)
    avg_daily_riders = models.PositiveIntegerField(default=0)
    # Fuel
    total_fuel_liters = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_fuel_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_fuel_efficiency = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Incidents
    total_incidents = models.PositiveIntegerField(default=0)
    total_accidents = models.PositiveIntegerField(default=0)
    total_delays = models.PositiveIntegerField(default=0)
    on_time_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    # Financial
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit_loss = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Satisfaction
    avg_parent_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_complaints = models.PositiveIntegerField(default=0)
    complaints_resolved = models.PositiveIntegerField(default=0)
    # Summary
    highlights = models.TextField(blank=True)
    issues = models.TextField(blank=True)
    next_month_plans = models.TextField(blank=True)
    # Metadata
    generated_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transport_monthly_reports"
        unique_together = [("school", "month", "year")]

    def __str__(self):
        return f"Transport Report - {self.month}/{self.year}"


class TransportEmergencyContact(models.Model):
    """Emergency contacts for transport."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="transport_emergency_contacts"
    )
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30)
    alternate_phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    organization = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    priority_order = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_emergency_contacts"
        ordering = ["priority_order", "-is_primary"]

    def __str__(self):
        return f"{self.name} ({self.role})"


class VehicleAssignmentLog(models.Model):
    """Log of vehicle assignments."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey("Vehicle", on_delete=models.CASCADE, related_name="assignment_logs")
    route = models.ForeignKey("Route", on_delete=models.SET_NULL, null=True, blank=True)
    driver = models.ForeignKey("Driver", on_delete=models.SET_NULL, null=True, blank=True)
    assignment_date = models.DateField()
    assignment_type = models.CharField(
        max_length=20,
        choices=[
            ("route", "Route Assignment"),
            ("trip", "Trip Assignment"),
            ("pool", "Pool Assignment"),
            ("maintenance", "Maintenance"),
        ],
    )
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    purpose = models.CharField(max_length=200, blank=True)
    assigned_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vehicle_assignment_logs"
        ordering = ["-assignment_date", "-created_at"]

    def __str__(self):
        return f"{self.vehicle} - {self.assignment_type} ({self.assignment_date})"


class TransportDriverSchedule(models.Model):
    """Driver work schedule management."""

    class ShiftType(models.TextChoices):
        MORNING = "morning", "Morning Shift"
        AFTERNOON = "afternoon", "Afternoon Shift"
        FULL_DAY = "full_day", "Full Day"
        OVERTIME = "overtime", "Overtime"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey("Driver", on_delete=models.CASCADE, related_name="driver_schedules")
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="driver_schedules")
    date = models.DateField()
    shift_type = models.CharField(max_length=15, choices=ShiftType.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    # Routes
    routes_assigned = models.JSONField(default=list, blank=True)
    total_distance_km = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Hours
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Status
    is_available = models.BooleanField(default=True)
    is_on_leave = models.BooleanField(default=False)
    leave_type = models.CharField(max_length=50, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transport_driver_schedules"
        unique_together = [("driver", "date")]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.driver} - {self.get_shift_type_display()} ({self.date})"
