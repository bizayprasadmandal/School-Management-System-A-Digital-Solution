"""
Attendance Service — Daily and period-level attendance tracking
"""

import uuid

from django.db import models
from services.academics.models import TeacherAssignment
from services.auth.models import User
from services.students.models import AcademicYear, Classroom, Student


class AttendanceRecord(models.Model):
    """Daily attendance per student per classroom."""

    class Status(models.TextChoices):
        PRESENT = "P", "Present"
        ABSENT = "A", "Absent"
        LATE = "L", "Late"
        EXCUSED = "E", "Excused Absence"
        HALF_DAY = "H", "Half Day"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="attendance_records")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.PRESENT)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="recorded_attendance")
    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_attendance"
    )
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    remarks = models.CharField(max_length=255, blank=True)
    notified_guardian = models.BooleanField(default=False)

    class Meta:
        db_table = "attendance_records"
        unique_together = [("student", "date")]
        indexes = [
            models.Index(fields=["classroom", "date"]),
            models.Index(fields=["student", "academic_year"]),
            models.Index(fields=["classroom", "academic_year", "date"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.date} [{self.status}]"


class PeriodAttendance(models.Model):
    """Subject/period-level attendance for finer tracking."""

    class Status(models.TextChoices):
        PRESENT = "P", "Present"
        ABSENT = "A", "Absent"
        LATE = "L", "Late"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="period_attendance")
    assignment = models.ForeignKey(TeacherAssignment, on_delete=models.CASCADE)
    date = models.DateField()
    period_number = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=1, choices=Status.choices, default=Status.PRESENT)
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="recorded_period_attendance"
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_period_attendance"
    )
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "period_attendance"
        unique_together = [("student", "assignment", "date", "period_number")]

    def __str__(self):
        return f"{self.student} — {self.assignment} [{self.date} P{self.period_number}]"


class AttendanceLeave(models.Model):
    """Leave requests from students/parents."""

    class LeaveType(models.TextChoices):
        SICK = "sick", "Sick Leave"
        FAMILY = "family", "Family Emergency"
        OFFICIAL = "official", "Official Duty"
        OTHER = "other", "Other"

    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="leaves")
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    supporting_document = models.FileField(upload_to="leaves/documents/", null=True, blank=True)
    status = models.CharField(max_length=10, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_leaves"
    )
    review_remarks = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "attendance_leaves"

    @property
    def total_days(self):
        return (self.to_date - self.from_date).days + 1

    def __str__(self):
        return f"{self.student} — {self.get_leave_type_display()} [{self.status}]"


class AttendanceChangeLog(models.Model):
    """Immutable audit trail for attendance changes."""

    class ChangeType(models.TextChoices):
        CREATE = "create", "Created"
        UPDATE = "update", "Updated"
        DELETE = "delete", "Deleted"
        BULK_IMPORT = "bulk_import", "Bulk Import"

    # Generic FK to either AttendanceRecord or PeriodAttendance
    attendance_type = models.CharField(
        max_length=20,
        choices=[("daily", "Daily Attendance"), ("period", "Period Attendance")],
    )
    attendance_id = models.PositiveIntegerField(help_text="ID of the attendance record")
    change_type = models.CharField(max_length=15, choices=ChangeType.choices)
    old_values = models.JSONField(null=True, blank=True, help_text="Previous field values")
    new_values = models.JSONField(null=True, blank=True, help_text="New field values")
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True, help_text="Reason for change")

    class Meta:
        db_table = "attendance_change_logs"
        indexes = [
            models.Index(fields=["attendance_type", "attendance_id"]),
            models.Index(fields=["changed_by"]),
            models.Index(fields=["-changed_at"]),
        ]
        ordering = ["-changed_at"]

    def __str__(self):
        return f"{self.change_type} {self.attendance_type}#{self.attendance_id} by {self.changed_by}"


class AttendancePolicy(models.Model):
    """Configurable attendance policy per school."""

    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="attendance_policies")
    name = models.CharField(max_length=100, default="Default Policy")
    min_attendance_pct = models.DecimalField(max_digits=5, decimal_places=2, default=75.0)
    auto_fail_below = models.BooleanField(default=True)
    notify_parent_below_pct = models.DecimalField(max_digits=5, decimal_places=2, default=80.0)
    notify_admin_below_pct = models.DecimalField(max_digits=5, decimal_places=2, default=60.0)
    edit_window_days = models.PositiveIntegerField(default=7)
    reminder_time = models.TimeField(default="10:00", help_text="Time to remind teachers to record attendance")
    escalation_enabled = models.BooleanField(default=True)
    escalation_after_minutes = models.PositiveIntegerField(default=60, help_text="Minutes after reminder to escalate")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_policies"
        unique_together = [("school", "is_active")]

    def __str__(self):
        return f"{self.name} ({self.school})"


class Holiday(models.Model):
    """School holidays — no attendance recorded on these days."""

    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="holidays")
    name = models.CharField(max_length=200)
    date = models.DateField()
    holiday_type = models.CharField(
        max_length=20,
        choices=[
            ("public", "Public Holiday"),
            ("school", "School Holiday"),
            ("exam", "Exam Holiday"),
            ("vacation", "Vacation"),
        ],
        default="school",
    )
    description = models.TextField(blank=True)
    academic_year = models.ForeignKey("students.AcademicYear", on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "holidays"
        unique_together = [("school", "date")]
        ordering = ["date"]

    def __str__(self):
        return f"{self.name} — {self.date}"


class LeaveBalance(models.Model):
    """Track leave balance per student per academic year."""

    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="leave_balances")
    academic_year = models.ForeignKey("students.AcademicYear", on_delete=models.CASCADE)
    sick_leave_total = models.PositiveIntegerField(default=10)
    sick_leave_used = models.PositiveIntegerField(default=0)
    casual_leave_total = models.PositiveIntegerField(default=5)
    casual_leave_used = models.PositiveIntegerField(default=0)
    other_leave_total = models.PositiveIntegerField(default=5)
    other_leave_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leave_balances"
        unique_together = [("student", "academic_year")]

    @property
    def sick_leave_remaining(self):
        return self.sick_leave_total - self.sick_leave_used

    @property
    def casual_leave_remaining(self):
        return self.casual_leave_total - self.casual_leave_used

    @property
    def other_leave_remaining(self):
        return self.other_leave_total - self.other_leave_used

    @property
    def total_remaining(self):
        return self.sick_leave_remaining + self.casual_leave_remaining + self.other_leave_remaining

    def __str__(self):
        return f"{self.student} — Leave Balance ({self.academic_year})"


class LeaveApprovalLevel(models.Model):
    """Multi-level leave approval workflow."""

    leave = models.ForeignKey(AttendanceLeave, on_delete=models.CASCADE, related_name="approval_levels")
    level = models.PositiveIntegerField(help_text="Approval level (1=Teacher, 2=HOD, 3=Principal)")
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_approvals")
    status = models.CharField(
        max_length=15,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("skipped", "Skipped"),
        ],
        default="pending",
    )
    remarks = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "leave_approval_levels"
        ordering = ["level"]
        unique_together = [("leave", "level")]

    def __str__(self):
        return f"Leave #{self.leave_id} — Level {self.level} ({self.status})"


class QRCodeSession(models.Model):
    """QR code sessions for student check-in."""

    classroom = models.ForeignKey("students.Classroom", on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    period_number = models.PositiveSmallIntegerField(null=True, blank=True)
    qr_code = models.CharField(max_length=255, unique=True)
    secret_key = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "qr_code_sessions"

    def __str__(self):
        return f"QR Session — {self.classroom} ({self.date})"


class QRCodeCheckin(models.Model):
    """Student check-in via QR code."""

    session = models.ForeignKey(QRCodeSession, on_delete=models.CASCADE, related_name="checkins")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE)
    checked_in_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_info = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "qr_code_checkins"
        unique_together = [("session", "student")]

    def __str__(self):
        return f"{self.student} checked in to {self.session}"


class SubstituteTeacher(models.Model):
    """Substitute teacher assignment when a teacher is absent."""

    original_teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="substitute_original")
    substitute_teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="substitute_assignments")
    date = models.DateField()
    period_number = models.PositiveSmallIntegerField(null=True, blank=True)
    classroom = models.ForeignKey("students.Classroom", on_delete=models.CASCADE)
    subject = models.ForeignKey("academics.Subject", on_delete=models.CASCADE, null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    is_auto_assigned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "substitute_teachers"
        unique_together = [("date", "period_number", "classroom")]

    def __str__(self):
        return f"{self.substitute_teacher} replacing {self.original_teacher} on {self.date}"


class AttendanceDataArchive(models.Model):
    """Archived attendance data for GDPR compliance and performance."""

    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE)
    academic_year = models.ForeignKey("students.AcademicYear", on_delete=models.CASCADE)
    archive_type = models.CharField(max_length=20, choices=[("daily", "Daily"), ("period", "Period")])
    data = models.JSONField(help_text="Archived attendance records")
    record_count = models.PositiveIntegerField(default=0)
    date_from = models.DateField()
    date_to = models.DateField()
    archived_at = models.DateTimeField(auto_now_add=True)
    is_purged = models.BooleanField(default=False, help_text="Original data has been purged")

    class Meta:
        db_table = "attendance_data_archives"
        indexes = [
            models.Index(fields=["school", "academic_year"]),
            models.Index(fields=["-archived_at"]),
        ]

    def __str__(self):
        return f"Archive {self.archive_type} — {self.school} ({self.date_from} to {self.date_to})"


class BiometricCheckin(models.Model):
    """Fingerprint or face recognition check-in."""

    class BiometricType(models.TextChoices):
        FINGERPRINT = "fingerprint", "Fingerprint"
        FACE = "face", "Face Recognition"
        IRIS = "iris", "Iris Scan"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        DENIED = "denied", "Access Denied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="biometric_checkins")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="biometric_checkins")
    # Biometric details
    biometric_type = models.CharField(max_length=15, choices=BiometricType.choices)
    device_id = models.CharField(max_length=100, blank=True, help_text="Biometric device identifier")
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUCCESS)
    confidence_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Recognition confidence (0-100)"
    )
    # Location
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    # Timestamp
    checkin_time = models.DateTimeField(auto_now_add=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance_biometric_checkins"
        ordering = ["-checkin_time"]

    def __str__(self):
        return f"{self.student} — {self.get_biometric_type_display()} ({self.get_status_display()})"


class RFIDCheckin(models.Model):
    """Tap card attendance."""

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        DENIED = "denied", "Access Denied"
        LOST = "lost", "Lost Card"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="rfid_checkins")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="rfid_checkins")
    # RFID details
    card_number = models.CharField(max_length=50)
    reader_id = models.CharField(max_length=100, blank=True, help_text="RFID reader device ID")
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUCCESS)
    # Location
    location = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    # Timestamp
    checkin_time = models.DateTimeField(auto_now_add=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance_rfid_checkins"
        ordering = ["-checkin_time"]

    def __str__(self):
        return f"{self.student} — RFID {self.card_number} ({self.get_status_display()})"


class GPSAttendance(models.Model):
    """Location-based attendance verification."""

    class Status(models.TextChoices):
        VERIFIED = "verified", "Verified"
        OUT_OF_RANGE = "out_of_range", "Out of Range"
        PENDING = "pending", "Pending Verification"
        DENIED = "denied", "Denied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="gps_attendance")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="gps_attendance")
    # Location details
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    accuracy_meters = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # Geofence
    geofence_name = models.CharField(max_length=100, blank=True)
    geofence_radius = models.PositiveIntegerField(default=100, help_text="Geofence radius in meters")
    distance_from_school = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Device info
    device_id = models.CharField(max_length=100, blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    # Timestamp
    checkin_time = models.DateTimeField(auto_now_add=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance_gps"
        ordering = ["-checkin_time"]

    def __str__(self):
        return f"{self.student} — GPS ({self.get_status_display()})"

    @property
    def is_within_school(self):
        return self.distance_from_school is not None and self.distance_from_school <= self.geofence_radius


class ParentNotification(models.Model):
    """Automated absence notifications to parents."""

    class NotificationType(models.TextChoices):
        ABSENCE = "absence", "Absence Alert"
        LATE = "late", "Late Arrival"
        EARLY_DEPARTURE = "early_departure", "Early Departure"
        CHRONIC = "chronic", "Chronic Absence"
        PATTERN = "pattern", "Attendance Pattern"
        OTHER = "other", "Other"

    class Channel(models.TextChoices):
        SMS = "sms", "SMS"
        EMAIL = "email", "Email"
        PUSH = "push", "Push Notification"
        ALL = "all", "All Channels"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"
        READ = "read", "Read"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="attendance_notifications")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="attendance_notifications")
    # Notification details
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.ALL)
    # Message
    title = models.CharField(max_length=200)
    message = models.TextField()
    # Recipient
    parent_email = models.EmailField(blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Delivery tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    # Reference
    attendance_record = models.ForeignKey(
        AttendanceRecord, on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications"
    )
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance_parent_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} — {self.get_notification_type_display()} ({self.get_status_display()})"


class AttendanceDashboard(models.Model):
    """Visual analytics dashboard data."""

    class DashboardType(models.TextChoices):
        SCHOOL = "school", "School-wide"
        GRADE = "grade", "Grade Level"
        CLASSROOM = "classroom", "Classroom"
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="attendance_dashboards")
    # Dashboard details
    dashboard_type = models.CharField(max_length=15, choices=DashboardType.choices)
    title = models.CharField(max_length=200)
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    # Metrics
    total_students = models.PositiveIntegerField(default=0)
    average_attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    present_count = models.PositiveIntegerField(default=0)
    absent_count = models.PositiveIntegerField(default=0)
    late_count = models.PositiveIntegerField(default=0)
    excused_count = models.PositiveIntegerField(default=0)
    # Trends
    attendance_trend = models.JSONField(default=list, blank=True)
    daily_breakdown = models.JSONField(default=dict, blank=True)
    # Alerts
    chronic_absence_count = models.PositiveIntegerField(default=0)
    at_risk_count = models.PositiveIntegerField(default=0)
    # Charts
    chart_data = models.JSONField(default=dict, blank=True)
    # Settings
    is_public = models.BooleanField(default=False)
    generated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_attendance_dashboards"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_dashboards"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_dashboard_type_display()})"


class ChronicAbsenceTracking(models.Model):
    """Flag students with >10% absence."""

    class SeverityLevel(models.TextChoices):
        WATCH = "watch", "Watch (5-10%)"
        WARNING = "warning", "Warning (10-15%)"
        CONCERN = "concern", "Concerning (15-20%)"
        CRITICAL = "critical", "Critical (>20%)"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        IMPROVING = "improving", "Improving"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="chronic_absence_tracking")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="chronic_absence_tracking")
    # Period
    academic_year = models.ForeignKey("students.AcademicYear", on_delete=models.CASCADE)
    term = models.ForeignKey("academics.AcademicTerm", on_delete=models.SET_NULL, null=True, blank=True)
    # Metrics
    total_days = models.PositiveIntegerField(default=0)
    days_present = models.PositiveIntegerField(default=0)
    days_absent = models.PositiveIntegerField(default=0)
    days_late = models.PositiveIntegerField(default=0)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    absence_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Severity
    severity_level = models.CharField(max_length=10, choices=SeverityLevel.choices)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Intervention
    intervention_plan = models.TextField(blank=True)
    intervention_start_date = models.DateField(null=True, blank=True)
    intervention_notes = models.TextField(blank=True)
    # Follow-up
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    # Assigned to
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="chronic_absence_cases"
    )
    # Notifications
    parent_notified = models.BooleanField(default=False)
    admin_notified = models.BooleanField(default=False)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_chronic_absence"
        unique_together = [("student", "academic_year")]
        ordering = ["-absence_percentage"]

    def __str__(self):
        return f"{self.student} — {self.attendance_percentage}% ({self.get_severity_level_display()})"

    def calculate_severity(self):
        """Calculate severity based on absence percentage."""
        if self.absence_percentage >= 20:
            self.severity_level = self.SeverityLevel.CRITICAL
        elif self.absence_percentage >= 15:
            self.severity_level = self.SeverityLevel.CONCERN
        elif self.absence_percentage >= 10:
            self.severity_level = self.SeverityLevel.WARNING
        elif self.absence_percentage >= 5:
            self.severity_level = self.SeverityLevel.WATCH
        return self.severity_level


class AttendanceReport(models.Model):
    """Generate attendance reports."""

    class ReportType(models.TextChoices):
        DAILY = "daily", "Daily Report"
        WEEKLY = "weekly", "Weekly Report"
        MONTHLY = "monthly", "Monthly Report"
        TERM = "term", "Term Report"
        ANNUAL = "annual", "Annual Report"
        CUSTOM = "custom", "Custom Range"
        STUDENT = "student", "Student Report"
        CLASS = "class", "Class Report"
        CHRONIC = "chronic", "Chronic Absence Report"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATED = "generated", "Generated"
        SENT = "sent", "Sent"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="attendance_reports")
    # Report details
    report_type = models.CharField(max_length=15, choices=ReportType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    # Scope
    classroom = models.ForeignKey("students.Classroom", on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey("students.Student", on_delete=models.SET_NULL, null=True, blank=True)
    grade = models.ForeignKey("students.Grade", on_delete=models.SET_NULL, null=True, blank=True)
    # Metrics
    total_students = models.PositiveIntegerField(default=0)
    average_attendance = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    present_count = models.PositiveIntegerField(default=0)
    absent_count = models.PositiveIntegerField(default=0)
    late_count = models.PositiveIntegerField(default=0)
    excused_count = models.PositiveIntegerField(default=0)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    # File
    report_url = models.URLField(blank=True)
    file_size_mb = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Generated by
    generated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_attendance_reports"
    )
    # Sent to
    sent_to = models.JSONField(default=list, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"


class BulkAttendanceImport(models.Model):
    """Import attendance from CSV."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        PARTIAL = "partial", "Partial Success"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="bulk_attendance_imports")
    # Import details
    file_name = models.CharField(max_length=255)
    file_url = models.URLField(blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Results
    total_records = models.PositiveIntegerField(default=0)
    successful_records = models.PositiveIntegerField(default=0)
    failed_records = models.PositiveIntegerField(default=0)
    # Errors
    error_log = models.JSONField(default=list, blank=True)
    # Settings
    date_column = models.CharField(max_length=50, default="date")
    student_column = models.CharField(max_length=50, default="student_id")
    status_column = models.CharField(max_length=50, default="status")
    overwrite_existing = models.BooleanField(default=False)
    # Imported by
    imported_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="bulk_attendance_imports"
    )
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance_bulk_imports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Import {self.file_name} ({self.get_status_display()})"

    @property
    def success_rate(self):
        if self.total_records > 0:
            return round(self.successful_records / self.total_records * 100, 1)
        return 0


class AttendanceCorrectionWorkflow(models.Model):
    """Staff can correct attendance."""

    class CorrectionType(models.TextChoices):
        STATUS_CHANGE = "status_change", "Status Change"
        TIME_CHANGE = "time_change", "Time Change"
        ADD_RECORD = "add_record", "Add Record"
        DELETE_RECORD = "delete_record", "Delete Record"
        BULK_UPDATE = "bulk_update", "Bulk Update"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        AUTO_APPROVED = "auto_approved", "Auto-Approved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="attendance_corrections")
    # Correction details
    correction_type = models.CharField(max_length=15, choices=CorrectionType.choices)
    # Reference
    attendance_record = models.ForeignKey(
        AttendanceRecord, on_delete=models.SET_NULL, null=True, blank=True, related_name="corrections"
    )
    period_attendance = models.ForeignKey(
        PeriodAttendance, on_delete=models.SET_NULL, null=True, blank=True, related_name="corrections"
    )
    # Changes
    old_status = models.CharField(max_length=1, blank=True)
    new_status = models.CharField(max_length=1)
    old_time = models.DateTimeField(null=True, blank=True)
    new_time = models.DateTimeField(null=True, blank=True)
    # Reason
    reason = models.TextField()
    supporting_document = models.FileField(upload_to="attendance/corrections/", null=True, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Requested by
    requested_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="requested_attendance_corrections"
    )
    # Reviewed by
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_attendance_corrections"
    )
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_corrections"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_correction_type_display()} — {self.get_status_display()}"


class AttendanceHistoryView(models.Model):
    """Student attendance timeline."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="attendance_history")
    # Timeline data
    academic_year = models.ForeignKey("students.AcademicYear", on_delete=models.CASCADE)
    term = models.ForeignKey("academics.AcademicTerm", on_delete=models.SET_NULL, null=True, blank=True)
    # Summary
    total_days = models.PositiveIntegerField(default=0)
    days_present = models.PositiveIntegerField(default=0)
    days_absent = models.PositiveIntegerField(default=0)
    days_late = models.PositiveIntegerField(default=0)
    days_excused = models.PositiveIntegerField(default=0)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Timeline
    timeline_data = models.JSONField(default=list, blank=True, help_text="Daily attendance timeline")
    # Trends
    monthly_trend = models.JSONField(default=list, blank=True)
    weekday_trend = models.JSONField(default=dict, blank=True)
    # Streaks
    current_streak = models.PositiveIntegerField(default=0, help_text="Consecutive present days")
    longest_streak = models.PositiveIntegerField(default=0)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_history_views"
        unique_together = [("student", "academic_year")]
        ordering = ["-academic_year"]

    def __str__(self):
        return f"{self.student} — {self.academic_year} ({self.attendance_percentage}%)"


class AttendancePatterns(models.Model):
    """Detect patterns (Monday absences)."""

    class PatternType(models.TextChoices):
        WEEKDAY = "weekday", "Weekday Pattern"
        MONTHLY = "monthly", "Monthly Pattern"
        SEASONAL = "seasonal", "Seasonal Pattern"
        CONSECUTIVE = "consecutive", "Consecutive Absences"
        BEFORE_AFTER_BREAK = "before_after_break", "Before/After Break"

    class RiskLevel(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="attendance_patterns")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="attendance_patterns")
    academic_year = models.ForeignKey("students.AcademicYear", on_delete=models.CASCADE)
    # Pattern details
    pattern_type = models.CharField(max_length=20, choices=PatternType.choices)
    pattern_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Metrics
    frequency = models.PositiveIntegerField(default=0, help_text="Number of occurrences")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Risk
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices)
    # Details
    pattern_data = models.JSONField(default=dict, blank=True)
    affected_dates = models.JSONField(default=list, blank=True)
    # Intervention
    intervention_recommended = models.BooleanField(default=False)
    intervention_notes = models.TextField(blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendance_patterns"
        ordering = ["-percentage"]

    def __str__(self):
        return f"{self.student} — {self.pattern_name} ({self.get_risk_level_display()})"


class RealTimeDashboard(models.Model):
    """Live attendance monitoring."""

    class DashboardScope(models.TextChoices):
        SCHOOL = "school", "School-wide"
        GRADE = "grade", "Grade Level"
        CLASSROOM = "classroom", "Classroom"
        BUS = "bus", "Bus Route"
        DORMITORY = "dormitory", "Dormitory"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="realtime_dashboards")
    # Dashboard details
    scope = models.CharField(max_length=15, choices=DashboardScope.choices)
    scope_id = models.CharField(max_length=50, blank=True, help_text="ID of grade/classroom/bus")
    # Live metrics
    total_expected = models.PositiveIntegerField(default=0)
    total_present = models.PositiveIntegerField(default=0)
    total_absent = models.PositiveIntegerField(default=0)
    total_late = models.PositiveIntegerField(default=0)
    total_excused = models.PositiveIntegerField(default=0)
    total_early_departure = models.PositiveIntegerField(default=0)
    # Percentage
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Real-time data
    live_checkins = models.JSONField(default=list, blank=True)
    recent_alerts = models.JSONField(default=list, blank=True)
    # Refresh
    last_refreshed = models.DateTimeField(auto_now=True)
    refresh_interval_seconds = models.PositiveIntegerField(default=30)
    # Settings
    auto_refresh = models.BooleanField(default=True)
    show_names = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attendance_realtime_dashboards"
        ordering = ["-last_refreshed"]

    def __str__(self):
        return f"Real-Time Dashboard — {self.get_scope_display()} ({self.attendance_percentage}%)"

    def refresh_data(self):
        """Refresh live attendance data."""
        from django.utils import timezone

        # This would typically query live data
        # For now, just update the timestamp
        self.last_refreshed = timezone.now()
        self.save(update_fields=["last_refreshed"])
