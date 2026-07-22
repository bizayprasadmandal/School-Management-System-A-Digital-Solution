"""
Counseling Service — Models for counseling appointments and student referrals.
"""

import uuid
from django.db import models
from django.utils import timezone
from services.auth.models import User, School
from services.students.models import Student


class CounselingAppointment(models.Model):
    """A scheduled counseling session between a counselor and a student."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    class AppointmentType(models.TextChoices):
        ACADEMIC = "academic", "Academic Counseling"
        CAREER = "career", "Career Guidance"
        PERSONAL = "personal", "Personal / Emotional"
        BEHAVIORAL = "behavioral", "Behavioral Intervention"
        COLLEGE = "college", "College Preparation"
        GROUP = "group", "Group Session"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_appointments")
    counselor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="counseling_appointments",
        limit_choices_to={"role": "counselor"},
        help_text="The counselor conducting the session",
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="counseling_appointments",
    )
    appointment_type = models.CharField(
        max_length=20, choices=AppointmentType.choices, default=AppointmentType.ACADEMIC,
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.SCHEDULED, db_index=True,
    )
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=30, help_text="Duration in minutes")
    location = models.CharField(max_length=100, blank=True, help_text="Room or virtual meeting link")
    reason = models.TextField(blank=True, help_text="Reason for the appointment")
    notes = models.TextField(blank=True, help_text="Counselor's session notes (post-session)")
    follow_up_needed = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="created_appointments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counseling_appointments"
        ordering = ["-scheduled_date", "-scheduled_time"]
        indexes = [
            models.Index(fields=["school", "counselor", "status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["scheduled_date"]),
        ]
        verbose_name = "Counseling Appointment"
        verbose_name_plural = "Counseling Appointments"

    def __str__(self):
        return (
            f"{self.get_appointment_type_display()} — "
            f"{self.student.user.full_name} & {self.counselor.full_name} "
            f"({self.scheduled_date})"
        )


class StudentReferral(models.Model):
    """A referral from a teacher/admin to a counselor for student support."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Review"
        UNDER_REVIEW = "under_review", "Under Review"
        CONTACTED = "contacted", "Student Contacted"
        ACTIONED = "actioned", "Action Taken"
        CLOSED = "closed", "Closed"
        DECLINED = "declined", "Declined"

    class ReferralCategory(models.TextChoices):
        ACADEMIC = "academic", "Academic Concern"
        ATTENDANCE = "attendance", "Attendance Issue"
        BEHAVIOR = "behavior", "Behavioral Concern"
        EMOTIONAL = "emotional", "Emotional / Mental Health"
        FAMILY = "family", "Family / Home Issue"
        SOCIAL = "social", "Social / Peer Issue"
        SAFETY = "safety", "Safety Concern"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_referrals")
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="referrals",
    )
    referred_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="counseling_referrals_created",
        help_text="Teacher or admin who created the referral",
    )
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="counseling_referrals_assigned",
        limit_choices_to={"role": "counselor"},
        help_text="Counselor assigned to handle this referral",
    )
    category = models.CharField(
        max_length=15, choices=ReferralCategory.choices, default=ReferralCategory.ACADEMIC,
    )
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.PENDING, db_index=True,
    )
    reason = models.TextField(help_text="Reason for the referral")
    notes = models.TextField(blank=True, help_text="Additional notes and observations")
    intervention_plan = models.TextField(blank=True, help_text="Proposed intervention plan")
    outcome = models.TextField(blank=True, help_text="Outcome after action taken")
    action_taken_at = models.DateTimeField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    is_confidential = models.BooleanField(default=False, help_text="Restrict visibility to counselors and admins")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_referrals"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "status", "priority"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["student"]),
        ]
        verbose_name = "Student Referral"
        verbose_name_plural = "Student Referrals"

    def __str__(self):
        return (
            f"{self.get_category_display()} referral — "
            f"{self.student.user.full_name} ({self.get_status_display()})"
        )
