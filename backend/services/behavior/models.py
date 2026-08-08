import uuid

from django.db import models
from django.utils import timezone
from services.auth.models import School, User
from services.students.models import Student


class Incident(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="incidents")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="incidents")
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reported_incidents")
    incident_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    description = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now, help_text="When the incident occurred; defaults to now.")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    resolution = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "incidents"
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.incident_type} - {self.student} ({self.get_severity_display()})"


class Referral(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="referrals")
    referred_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_referrals")
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_referrals")
    reason = models.TextField()
    action_taken = models.TextField(blank=True)
    status = models.CharField(
        max_length=15,
        choices=[("pending", "Pending"), ("actioned", "Actioned"), ("closed", "Closed")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "referrals"

    def __str__(self):
        return f"Referral: {self.incident} -> {self.referred_to}"
