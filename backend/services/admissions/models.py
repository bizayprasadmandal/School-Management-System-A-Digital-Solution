"""Admissions / Enrollment — Applications, documents, reviews, intake management."""

import uuid

from django.db import models
from services.auth.models import School, User


class EnrollmentIntake(models.Model):
    """Academic intake periods for admissions (e.g., Fall 2026, Spring 2027)."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        UPCOMING = "upcoming", "Upcoming"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="enrollment_intakes")
    name = models.CharField(max_length=100, help_text="e.g. Fall 2026 Intake")
    academic_year = models.CharField(max_length=30, blank=True)
    application_start = models.DateField()
    application_end = models.DateField()
    enrollment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPCOMING)
    max_applications = models.PositiveSmallIntegerField(default=0, help_text="0 = unlimited")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admissions_intakes"
        unique_together = [("school", "name")]
        ordering = ["-application_start"]

    def __str__(self):
        return self.name


class Application(models.Model):
    """Student applications for admission."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under Review"
        SHORTLISTED = "shortlisted", "Shortlisted"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        WAITLISTED = "waitlisted", "Waitlisted"
        ENROLLED = "enrolled", "Enrolled"
        CANCELLED = "cancelled", "Cancelled"

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="applications")
    intake = models.ForeignKey(EnrollmentIntake, on_delete=models.CASCADE, related_name="applications")
    application_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)

    # Personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=Gender.choices)
    nationality = models.CharField(max_length=100, blank=True)

    # Contact
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)

    # Academic info
    previous_school = models.CharField(max_length=200, blank=True)
    previous_grade = models.CharField(max_length=20, blank=True)
    applying_for_grade = models.CharField(max_length=20)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    # Guardian info
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    guardian_email = models.EmailField(max_length=254, blank=True)
    guardian_relation = models.CharField(max_length=50, blank=True)

    # Metadata
    source = models.CharField(max_length=50, blank=True, help_text="How did they hear about us?")
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_applications"
    )
    review_notes = models.TextField(blank=True)

    # ── Admissions CRM pipeline (inquiry → tour → offer → enrolled) ────────
    tour_date = models.DateField(null=True, blank=True, help_text="Scheduled campus tour date")
    toured_at = models.DateTimeField(null=True, blank=True)
    offer_sent_at = models.DateTimeField(null=True, blank=True)
    offer_deadline = models.DateField(
        null=True,
        blank=True,
        help_text="Deadline for the family to accept the offer; after this date the offer expires.",
    )
    offer_accepted_at = models.DateTimeField(null=True, blank=True)
    linked_student = models.ForeignKey(
        "students.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admission_application",
        help_text="Student record created when this application is enrolled",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_applications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.application_number}: {self.first_name} {self.last_name}"


class ApplicationTimelineEvent(models.Model):
    """Immutable pipeline activity log for an application.

    Every stage move (created, submitted, tour scheduled/completed,
    offer sent/accepted, enrolled) and manual status change is recorded here,
    giving the admissions team a complete CRM-style timeline.
    """

    class Stage(models.TextChoices):
        CREATED = "created", "Application Created"
        SUBMITTED = "submitted", "Submitted"
        TOUR_SCHEDULED = "tour_scheduled", "Tour Scheduled"
        TOUR_COMPLETED = "tour_completed", "Tour Completed"
        OFFER_SENT = "offer_sent", "Offer Sent"
        OFFER_ACCEPTED = "offer_accepted", "Offer Accepted"
        ENROLLED = "enrolled", "Enrolled"
        STATUS_CHANGED = "status_changed", "Status Changed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="timeline")
    stage = models.CharField(max_length=30, choices=Stage.choices)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admissions_timeline"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.application.application_number} — {self.stage}"


class ApplicationDocument(models.Model):
    """Documents uploaded for an application."""

    class DocType(models.TextChoices):
        BIRTH_CERT = "birth_cert", "Birth Certificate"
        PASSPORT = "passport", "Passport"
        TRANSCRIPT = "transcript", "Academic Transcript"
        RECOMMENDATION = "recommendation", "Recommendation Letter"
        REPORT_CARD = "report_card", "Previous Report Card"
        MEDICAL = "medical", "Medical Records"
        PHOTO = "photo", "Passport Photo"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=30, choices=DocType.choices)
    file_url = models.URLField(max_length=500)
    file_name = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "admissions_documents"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.application.application_number} - {self.get_document_type_display()}"


class ApplicationReview(models.Model):
    """Review/score for an application by an admissions officer."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="admission_reviews")
    score = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Score out of 100")
    strengths = models.TextField(blank=True)
    weaknesses = models.TextField(blank=True)
    recommendation = models.CharField(max_length=50, blank=True, help_text="Strongly Recommend, Recommend, etc.")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admissions_reviews"
        unique_together = [("application", "reviewer")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.application} - {self.reviewer}"
