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
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
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
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

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
