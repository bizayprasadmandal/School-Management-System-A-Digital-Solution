"""
Attendance Service — Daily and period-level attendance tracking
"""

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
