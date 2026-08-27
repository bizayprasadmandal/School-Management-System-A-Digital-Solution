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
