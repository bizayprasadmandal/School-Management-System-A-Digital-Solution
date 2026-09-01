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

    # Valid status transitions — enforced by update_status to prevent
    # impossible jumps (e.g. draft → enrolled) and ensure the pipeline
    # is followed in order.
    VALID_TRANSITIONS = {
        "draft": ["submitted", "cancelled"],
        "submitted": ["under_review", "rejected", "cancelled"],
        "under_review": ["shortlisted", "rejected", "waitlisted", "cancelled"],
        "shortlisted": ["accepted", "rejected", "cancelled"],
        "waitlisted": ["accepted", "rejected", "cancelled"],
        "accepted": ["enrolled", "cancelled"],
        "rejected": [],
        "enrolled": [],
        "cancelled": [],
    }

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


class EntranceAssessment(models.Model):
    """Entrance assessment linked to an application.

    Schools can define custom assessment criteria (written test, interview,
    portfolio review, etc.) and score each applicant against them.
    """

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    assessment_type = models.CharField(
        max_length=50,
        help_text="e.g. Written Test, Interview, Portfolio Review",
    )
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score out of 100",
    )
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        help_text="Maximum possible score",
    )
    notes = models.TextField(blank=True)
    assessor_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_assessments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.application.application_number} — {self.assessment_type}"

    @property
    def percentage(self):
        if self.score is not None and self.max_score:
            return round(float(self.score) / float(self.max_score) * 100, 1)
        return None


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


# =============================================================================
# Application Fees
# =============================================================================


class ApplicationFee(models.Model):
    """Application fee payment tracking."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        WAIVED = "waived", "Waived"
        REFUNDED = "refunded", "Refunded"
        FAILED = "failed", "Failed"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CARD = "card", "Credit/Debit Card"
        ONLINE = "online", "Online Gateway"
        MOBILE = "mobile", "Mobile Money"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="application_fees")
    # Fee Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    # Payment
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    receipt_number = models.CharField(max_length=50, blank=True)
    # Waiver
    waiver_reason = models.TextField(blank=True)
    waived_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Gateway
    gateway_response = models.JSONField(default=dict)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_fees"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Fee: {self.application.application_number} - {self.amount} ({self.get_status_display()})"


# =============================================================================
# Interview Schedule
# =============================================================================


class InterviewSchedule(models.Model):
    """Interview scheduling and tracking."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"
        RESCHEDULED = "rescheduled", "Rescheduled"

    class InterviewType(models.TextChoices):
        IN_PERSON = "in_person", "In-Person"
        VIDEO = "video", "Video Call"
        PHONE = "phone", "Phone Call"
        PANEL = "panel", "Panel Interview"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="interviews")
    # Interview Details
    interview_type = models.CharField(max_length=15, choices=InterviewType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    # Location/Meeting
    location = models.CharField(max_length=200, blank=True)
    meeting_link = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    # Interviewer
    interviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="admission_interviews"
    )
    panel_members = models.JSONField(default=list, help_text="List of panel member IDs")
    # Feedback
    feedback = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Rating out of 5")
    recommendation = models.CharField(max_length=50, blank=True)
    # Metadata
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_interviews"
        ordering = ["scheduled_date", "scheduled_time"]

    def __str__(self):
        return f"Interview: {self.application.application_number} - {self.scheduled_date}"


# =============================================================================
# Merit List
# =============================================================================


class MeritList(models.Model):
    """Merit list generation and ranking."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="merit_lists")
    intake = models.ForeignKey(EnrollmentIntake, on_delete=models.CASCADE, related_name="merit_lists")
    # List Details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Grade/Program
    grade = models.CharField(max_length=50, help_text="Grade or program this list is for")
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    # Statistics
    total_applicants = models.PositiveIntegerField(default=0)
    total_selected = models.PositiveIntegerField(default=0)
    total_waitlisted = models.PositiveIntegerField(default=0)
    # Publishing
    published_at = models.DateTimeField(null=True, blank=True)
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_merit_lists"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class MeritListEntry(models.Model):
    """Individual entries in merit list."""

    class Status(models.TextChoices):
        SELECTED = "selected", "Selected"
        WAITLISTED = "waitlisted", "Waitlisted"
        REJECTED = "rejected", "Rejected"
        DECLINED = "declined", "Declined by Applicant"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    merit_list = models.ForeignKey(MeritList, on_delete=models.CASCADE, related_name="entries")
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="merit_entries")
    # Ranking
    rank = models.PositiveIntegerField()
    total_score = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SELECTED)
    # Scores Breakdown
    academic_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    assessment_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    interview_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    extracurricular_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_merit_entries"
        ordering = ["rank"]
        unique_together = [("merit_list", "application")]

    def __str__(self):
        return f"Rank {self.rank}: {self.application.application_number}"


# =============================================================================
# Waitlist Management
# =============================================================================


class WaitlistManagement(models.Model):
    """Waitlist management and notifications."""

    class Status(models.TextChoices):
        WAITING = "waiting", "Waiting"
        OFFERED = "offered", "Offer Extended"
        ACCEPTED = "accepted", "Accepted Offer"
        DECLINED = "declined", "Declined Offer"
        EXPIRED = "expired", "Offer Expired"
        REMOVED = "removed", "Removed from Waitlist"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="waitlist")
    # Position
    position = models.PositiveIntegerField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.WAITING)
    # Offer Details
    offer_extended_at = models.DateTimeField(null=True, blank=True)
    offer_expires_at = models.DateTimeField(null=True, blank=True)
    offer_accepted_at = models.DateTimeField(null=True, blank=True)
    offer_declined_at = models.DateTimeField(null=True, blank=True)
    decline_reason = models.TextField(blank=True)
    # Notifications
    last_notified_at = models.DateTimeField(null=True, blank=True)
    notification_count = models.PositiveSmallIntegerField(default=0)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_waitlist"
        ordering = ["position"]

    def __str__(self):
        return f"Position {self.position}: {self.application.application_number}"


# =============================================================================
# Enrollment Confirmation
# =============================================================================


class EnrollmentConfirmation(models.Model):
    """Enrollment confirmation workflow."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        DECLINED = "declined", "Declined"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending Deposit"
        PAID = "paid", "Deposit Paid"
        WAIVED = "waived", "Deposit Waived"
        REFUNDED = "refunded", "Deposit Refunded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="enrollment_confirmation")
    # Confirmation Details
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Dates
    confirmation_sent_at = models.DateTimeField(null=True, blank=True)
    confirmation_deadline = models.DateField()
    confirmed_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    # Deposit
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=15, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    deposit_paid_at = models.DateTimeField(null=True, blank=True)
    deposit_transaction_id = models.CharField(max_length=100, blank=True)
    # Decline
    decline_reason = models.TextField(blank=True)
    # Documents
    enrollment_documents = models.JSONField(default=list, help_text="List of required enrollment documents")
    documents_completed = models.BooleanField(default=False)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_enrollment_confirmations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Confirmation: {self.application.application_number} ({self.get_status_display()})"


# =============================================================================
# Admissions Reports
# =============================================================================


class AdmissionsReport(models.Model):
    """Admissions analytics and reports."""

    class ReportType(models.TextChoices):
        SUMMARY = "summary", "Admissions Summary"
        PIPELINE = "pipeline", "Pipeline Analysis"
        CONVERSION = "conversion", "Conversion Rates"
        DEMOGRAPHIC = "demographic", "Demographic Report"
        FINANCIAL = "financial", "Financial Report"
        GRADE_WISE = "grade", "Grade-wise Report"
        SOURCE_WISE = "source", "Source Analysis"
        TIMELINE = "timeline", "Timeline Analysis"
        CUSTOM = "custom", "Custom Report"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATED = "generated", "Generated"
        SENT = "sent", "Sent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="admissions_reports")
    intake = models.ForeignKey(EnrollmentIntake, on_delete=models.CASCADE, null=True, blank=True)
    # Report Details
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=15, choices=ReportType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    # Report Period
    period_start = models.DateField()
    period_end = models.DateField()
    # Report Content
    summary = models.TextField(blank=True)
    findings = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)
    # Statistics
    total_applications = models.PositiveIntegerField(default=0)
    total_enrolled = models.PositiveIntegerField(default=0)
    total_rejected = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Breakdown
    by_status = models.JSONField(default=dict)
    by_grade = models.JSONField(default=dict)
    by_source = models.JSONField(default=dict)
    by_demographic = models.JSONField(default=dict)
    # Personnel
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admissions_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# =============================================================================
# Email Notifications
# =============================================================================


class AdmissionsEmailNotification(models.Model):
    """Automated email notifications."""

    class NotificationType(models.TextChoices):
        APPLICATION_RECEIVED = "received", "Application Received"
        APPLICATION_UNDER_REVIEW = "review", "Application Under Review"
        INTERVIEW_SCHEDULED = "interview", "Interview Scheduled"
        DOCUMENT_REQUEST = "document", "Document Request"
        DECISION_MADE = "decision", "Decision Made"
        ACCEPTANCE = "acceptance", "Acceptance Letter"
        REJECTION = "rejection", "Rejection Letter"
        WAITLIST = "waitlist", "Waitlist Notification"
        ENROLLMENT_DEADLINE = "enrollment", "Enrollment Deadline Reminder"
        FEE_REMINDER = "fee", "Fee Payment Reminder"
        WELCOME = "welcome", "Welcome to School"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        OPENED = "opened", "Opened"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="email_notifications")
    # Notification Details
    notification_type = models.CharField(max_length=15, choices=NotificationType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    # Recipient
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=150)
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admissions_email_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.application.application_number}"


# =============================================================================
# SMS Notifications
# =============================================================================


class AdmissionsSMSNotification(models.Model):
    """SMS notifications to applicants."""

    class NotificationType(models.TextChoices):
        APPLICATION_RECEIVED = "received", "Application Received"
        INTERVIEW_REMINDER = "interview", "Interview Reminder"
        DECISION_MADE = "decision", "Decision Made"
        ENROLLMENT_DEADLINE = "enrollment", "Enrollment Deadline"
        FEE_REMINDER = "fee", "Fee Reminder"
        GENERAL = "general", "General Update"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="sms_notifications")
    # Notification Details
    notification_type = models.CharField(max_length=15, choices=NotificationType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Content
    message = models.TextField()
    # Recipient
    phone_number = models.CharField(max_length=20)
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admissions_sms_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.application.application_number}"


# =============================================================================
# Re-enrollment Management
# =============================================================================


class ReEnrollment(models.Model):
    """Re-enrollment for existing students."""

    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        STARTED = "started", "Started"
        COMPLETED = "completed", "Completed"
        DECLINED = "declined", "Declined"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="re_enrollments")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="re_enrollments")
    intake = models.ForeignKey(EnrollmentIntake, on_delete=models.CASCADE, related_name="re_enrollments")
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.INVITED)
    # Details
    current_grade = models.CharField(max_length=20)
    next_grade = models.CharField(max_length=20)
    # Dates
    invited_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # Decline
    decline_reason = models.TextField(blank=True)
    # Fee
    re_enrollment_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fee_paid = models.BooleanField(default=False)
    # Metadata
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_re_enrollments"
        ordering = ["-invited_at"]
        unique_together = [("student", "intake")]

    def __str__(self):
        return f"{self.student} - {self.next_grade} ({self.get_status_display()})"


# =============================================================================
# Admissions Pipeline
# =============================================================================


class AdmissionsPipeline(models.Model):
    """Visual pipeline/kanban view configuration."""

    class Stage(models.TextChoices):
        INQUIRY = "inquiry", "Inquiry"
        APPLICATION = "application", "Application Received"
        DOCUMENTATION = "documentation", "Documentation Complete"
        ASSESSMENT = "assessment", "Assessment Scheduled"
        INTERVIEW = "interview", "Interview Scheduled"
        REVIEW = "review", "Under Review"
        DECISION = "decision", "Decision Pending"
        ENROLLMENT = "enrollment", "Enrollment"
        ONBOARDED = "onboarded", "Onboarded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="admissions_pipelines")
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="pipeline")
    # Pipeline Details
    current_stage = models.CharField(max_length=15, choices=Stage.choices, default=Stage.INQUIRY)
    # Stage Dates
    inquiry_date = models.DateTimeField(null=True, blank=True)
    application_date = models.DateTimeField(null=True, blank=True)
    documentation_date = models.DateTimeField(null=True, blank=True)
    assessment_date = models.DateTimeField(null=True, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
    decision_date = models.DateTimeField(null=True, blank=True)
    enrollment_date = models.DateTimeField(null=True, blank=True)
    onboarded_date = models.DateTimeField(null=True, blank=True)
    # Assignment
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="pipeline_applications"
    )
    # Priority
    is_priority = models.BooleanField(default=False)
    is_hot_lead = models.BooleanField(default=False)
    # Source
    lead_source = models.CharField(max_length=50, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_pipeline"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.application.application_number} - {self.get_current_stage_display()}"


# =============================================================================
# Application Templates
# =============================================================================


class ApplicationTemplate(models.Model):
    """Reusable application templates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="application_templates")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # Template Settings
    intake = models.ForeignKey(EnrollmentIntake, on_delete=models.SET_NULL, null=True, blank=True)
    # Template Content
    required_fields = models.JSONField(default=list, help_text="List of required fields")
    optional_fields = models.JSONField(default=list, help_text="List of optional fields")
    required_documents = models.JSONField(default=list, help_text="List of required documents")
    # Fees
    application_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="USD")
    # Settings
    allow_late_applications = models.BooleanField(default=False)
    late_fee_deadline_days = models.PositiveSmallIntegerField(default=0)
    max_applications_per_student = models.PositiveSmallIntegerField(default=1)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_templates"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =============================================================================
# Bulk Application Import
# =============================================================================


class BulkApplicationImport(models.Model):
    """Import applications from CSV."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        PARTIAL = "partial", "Partially Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="bulk_applications")
    # Import Details
    batch_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Statistics
    total_rows = models.PositiveIntegerField(default=0)
    imported_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    # Errors
    errors = models.JSONField(default=list, help_text="List of import errors")
    error_file_url = models.URLField(blank=True)
    # Personnel
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Dates
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "admissions_bulk_imports"
        ordering = ["-initiated_at"]

    def __str__(self):
        return f"{self.batch_name} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Campus Visit Management
# =============================================================================


class CampusVisit(models.Model):
    """Campus tours and visit scheduling."""

    class VisitType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual Tour"
        GROUP = "group", "Group Tour"
        OPEN_HOUSE = "open_house", "Open House"
        SHADOW_DAY = "shadow", "Shadow Day"
        VIRTUAL = "virtual", "Virtual Tour"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="campus_visits")
    visitor_name = models.CharField(max_length=200)
    visitor_email = models.EmailField(blank=True)
    visitor_phone = models.CharField(max_length=30, blank=True)
    # Student
    prospective_student = models.ForeignKey(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="campus_visits"
    )
    # Visit details
    visit_type = models.CharField(max_length=15, choices=VisitType.choices, default=VisitType.INDIVIDUAL)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    # Tour
    tour_guide = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="campus_tours")
    group_size = models.PositiveIntegerField(default=1)
    # Follow-up
    interested_in_enrolling = models.BooleanField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    satisfaction_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "campus_visits"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.visitor_name} - {self.get_visit_type_display()} ({self.scheduled_date})"


class OpenHouseEvent(models.Model):
    """Open house events for admissions."""

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="open_house_events")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PLANNED)
    # Schedule
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200, blank=True)
    # Capacity
    max_attendees = models.PositiveIntegerField(default=100)
    current_attendees = models.PositiveIntegerField(default=0)
    # Registration
    registration_required = models.BooleanField(default=True)
    registration_deadline = models.DateField(null=True, blank=True)
    registration_url = models.URLField(blank=True)
    # Staff
    coordinator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    presenters = models.ManyToManyField(User, blank=True, related_name="open_house_presentations")
    # Content
    agenda = models.TextField(blank=True)
    materials = models.TextField(blank=True)
    # Post-event
    total_attended = models.PositiveIntegerField(default=0)
    applications_generated = models.PositiveIntegerField(default=0)
    avg_satisfaction = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "open_house_events"
        ordering = ["-event_date"]

    def __str__(self):
        return f"{self.title} ({self.event_date})"


class OpenHouseRegistration(models.Model):
    """Registration for open house events."""

    class Status(models.TextChoices):
        REGISTERED = "registered", "Registered"
        CONFIRMED = "confirmed", "Confirmed"
        ATTENDED = "attended", "Attended"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(OpenHouseEvent, on_delete=models.CASCADE, related_name="registrations")
    registrant_name = models.CharField(max_length=200)
    registrant_email = models.EmailField(blank=True)
    registrant_phone = models.CharField(max_length=30, blank=True)
    # Student info
    child_name = models.CharField(max_length=200, blank=True)
    child_dob = models.DateField(null=True, blank=True)
    current_grade = models.CharField(max_length=20, blank=True)
    current_school = models.CharField(max_length=200, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.REGISTERED)
    num_attendees = models.PositiveIntegerField(default=1)
    # Follow-up
    application_created = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    # Metadata
    registered_at = models.DateTimeField(auto_now_add=True)
    attended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "open_house_registrations"
        unique_together = [("event", "registrant_email")]

    def __str__(self):
        return f"{self.registrant_name} - {self.event.title}"


# =============================================================================
# NEW MODELS: Scholarship Management
# =============================================================================


class Scholarship(models.Model):
    """Scholarships offered during admissions."""

    class ScholarshipType(models.TextChoices):
        MERIT = "merit", "Merit-Based"
        NEED = "need", "Need-Based"
        ATHLETIC = "athletic", "Athletic"
        ARTS = "arts", "Arts & Culture"
        SIBLING = "sibling", "Sibling Discount"
        EMPLOYEE = "employee", "Employee"
        CUSTOM = "custom", "Custom"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="admission_scholarships")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scholarship_type = models.CharField(max_length=15, choices=ScholarshipType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Amount
    amount_type = models.CharField(max_length=20, blank=True, help_text="Fixed or Percentage")
    amount_fixed = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    amount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_recipients = models.PositiveIntegerField(null=True, blank=True)
    current_recipients = models.PositiveIntegerField(default=0)
    # Eligibility
    min_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    eligible_grades = models.CharField(max_length=100, blank=True)
    eligible_intakes = models.ManyToManyField("EnrollmentIntake", blank=True)
    renewal_eligible = models.BooleanField(default=False)
    renewal_criteria = models.TextField(blank=True)
    # Application
    application_required = models.BooleanField(default=True)
    deadline = models.DateField(null=True, blank=True)
    # Dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admissions_scholarships"

    def __str__(self):
        return f"{self.name} ({self.get_scholarship_type_display()})"


class ScholarshipApplication(models.Model):
    """Applications for scholarships."""

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "review", "Under Review"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        WAITLISTED = "waitlisted", "Waitlisted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name="applications")
    application = models.ForeignKey("Application", on_delete=models.CASCADE, related_name="scholarship_applications")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SUBMITTED)
    # Supporting docs
    essay = models.TextField(blank=True)
    recommendation_letter = models.FileField(upload_to="admissions/scholarships/letters/", null=True, blank=True)
    transcript = models.FileField(upload_to="admissions/scholarships/transcripts/", null=True, blank=True)
    # Financial info
    family_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    financial_need_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    # Merit info
    merit_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    gpa_at_application = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    # Decision
    decision_notes = models.TextField(blank=True)
    amount_awarded = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    decided_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scholarship_applications"
        unique_together = [("scholarship", "application")]

    def __str__(self):
        return f"{self.scholarship.name} - {self.application}"


# =============================================================================
# NEW MODELS: Admission Agreement & Policies
# =============================================================================


class AdmissionPolicy(models.Model):
    """School admission policies and criteria."""

    class PolicyType(models.TextChoices):
        AGE = "age", "Age Requirements"
        CAPACITY = "capacity", "Capacity Limits"
        PRIORITY = "priority", "Priority Criteria"
        RESIDENCE = "residence", "Residence Requirements"
        SIBLING = "sibling", "Sibling Priority"
        EMPLOYEE = "employee", "Employee Children"
        DISABILITY = "disability", "Disability Accommodation"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="admission_policies")
    name = models.CharField(max_length=200)
    policy_type = models.CharField(max_length=15, choices=PolicyType.choices)
    description = models.TextField()
    # Rules
    min_age_years = models.PositiveIntegerField(null=True, blank=True)
    max_age_years = models.PositiveIntegerField(null=True, blank=True)
    priority_weight = models.PositiveIntegerField(default=0, help_text="Higher = higher priority")
    # Capacity
    max_students_per_grade = models.PositiveIntegerField(null=True, blank=True)
    # Dates
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Document
    policy_document = models.FileField(upload_to="admissions/policies/", null=True, blank=True)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admission_policies"
        ordering = ["-priority_weight"]

    def __str__(self):
        return f"{self.name} ({self.get_policy_type_display()})"


class AdmissionAgreement(models.Model):
    """Enrollment agreements and contracts."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="admission_agreements")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = models.TextField(help_text="Full agreement text")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    version = models.CharField(max_length=20, blank=True)
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    requires_parent_signature = models.BooleanField(default=True)
    requires_student_signature = models.BooleanField(default=False)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admission_agreements"

    def __str__(self):
        return f"{self.name} (v{self.version})"


class AgreementSignature(models.Model):
    """Signatures on admission agreements."""

    class SignerType(models.TextChoices):
        PARENT = "parent", "Parent/Guardian"
        STUDENT = "student", "Student"
        ADMIN = "admin", "Administrator"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agreement = models.ForeignKey(AdmissionAgreement, on_delete=models.CASCADE, related_name="signatures")
    application = models.ForeignKey("Application", on_delete=models.CASCADE, related_name="agreement_signatures")
    signer_type = models.CharField(max_length=10, choices=SignerType.choices)
    signer_name = models.CharField(max_length=200)
    signature = models.ImageField(upload_to="admissions/signatures/", null=True, blank=True)
    signed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "agreement_signatures"
        unique_together = [("agreement", "application", "signer_type")]

    def __str__(self):
        return f"{self.signer_name} - {self.agreement.name}"


# =============================================================================
# NEW MODELS: Admission Communication
# =============================================================================


class AdmissionCommunicationLog(models.Model):
    """Log of all communications during admissions."""

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PHONE = "phone", "Phone Call"
        IN_PERSON = "in_person", "In Person"
        MAIL = "mail", "Postal Mail"
        OTHER = "other", "Other"

    class Direction(models.TextChoices):
        INBOUND = "inbound", "Incoming"
        OUTBOUND = "outbound", "Outgoing"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="admission_comm_logs")
    application = models.ForeignKey("Application", on_delete=models.CASCADE, related_name="communication_logs")
    # Communication details
    channel = models.CharField(max_length=10, choices=Channel.choices)
    direction = models.CharField(max_length=10, choices=Direction.choices, default=Direction.OUTBOUND)
    subject = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    # Participants
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sent_to_name = models.CharField(max_length=200, blank=True)
    sent_to_email = models.EmailField(blank=True)
    # Tracking
    delivered = models.BooleanField(default=True)
    opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admission_communication_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_channel_display()} - {self.application} ({self.get_direction_display()})"


class AdmissionReminder(models.Model):
    """Automated reminders for admissions deadlines."""

    class ReminderType(models.TextChoices):
        DOCUMENT = "document", "Missing Documents"
        DEADLINE = "deadline", "Upcoming Deadline"
        PAYMENT = "payment", "Fee Payment"
        INTERVIEW = "interview", "Interview Scheduled"
        FOLLOW_UP = "follow_up", "Follow-up"
        CUSTOM = "custom", "Custom"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        SENT = "sent", "Sent"
        CANCELLED = "cancelled", "Cancelled"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="admission_reminders")
    application = models.ForeignKey("Application", on_delete=models.CASCADE, related_name="reminders")
    reminder_type = models.CharField(max_length=15, choices=ReminderType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    # Content
    subject = models.CharField(max_length=255)
    message = models.TextField()
    # Schedule
    scheduled_date = models.DateTimeField()
    sent_date = models.DateTimeField(null=True, blank=True)
    # Channel
    channel = models.CharField(
        max_length=10,
        choices=AdmissionCommunicationLog.Channel.choices,
        default=AdmissionCommunicationLog.Channel.EMAIL,
    )
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admission_reminders"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.get_reminder_type_display()} - {self.application}"


# =============================================================================
# NEW MODELS: Grade/Class Availability
# =============================================================================


class GradeLevelCapacity(models.Model):
    """Track capacity per grade level per intake."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intake = models.ForeignKey("EnrollmentIntake", on_delete=models.CASCADE, related_name="grade_capacities")
    grade_level = models.CharField(max_length=50)
    max_capacity = models.PositiveIntegerField()
    current_enrollment = models.PositiveIntegerField(default=0)
    waitlist_count = models.PositiveIntegerField(default=0)
    # Breakdown
    boys_count = models.PositiveIntegerField(default=0)
    girls_count = models.PositiveIntegerField(default=0)
    # Fees
    tuition_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Status
    is_accepting = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "grade_level_capacities"
        unique_together = [("intake", "grade_level")]

    def __str__(self):
        return f"{self.grade_level} - {self.intake} ({self.current_enrollment}/{self.max_capacity})"

    @property
    def available_spots(self):
        return max(0, self.max_capacity - self.current_enrollment)

    @property
    def capacity_percentage(self):
        if self.max_capacity == 0:
            return 0
        return round((self.current_enrollment / self.max_capacity) * 100, 2)


class AdmissionDecision(models.Model):
    """Formal admission decisions."""

    class Decision(models.TextChoices):
        ADMITTED = "admitted", "Admitted"
        REJECTED = "rejected", "Rejected"
        WAITLISTED = "waitlisted", "Waitlisted"
        DEFERRED = "deferred", "Deferred to Next Intake"
        CONDITIONAL = "conditional", "Conditional Admission"

    class DecisionReason(models.TextChoices):
        CAPACITY = "capacity", "Capacity Constraints"
        ACADEMIC = "academic", "Academic Performance"
        BEHAVIOR = "behavior", "Behavioral Concern"
        DOCUMENTS = "documents", "Incomplete Documents"
        ELIGIBILITY = "eligibility", "Not Eligible"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey("Application", on_delete=models.CASCADE, related_name="decisions")
    decision = models.CharField(max_length=15, choices=Decision.choices)
    decision_reason = models.CharField(max_length=15, choices=DecisionReason.choices, blank=True)
    # Details
    rationale = models.TextField(blank=True)
    conditions = models.TextField(blank=True, help_text="For conditional admission")
    # Grade placement
    recommended_grade = models.CharField(max_length=50, blank=True)
    recommended_class = models.CharField(max_length=50, blank=True)
    # Financial
    scholarship_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    financial_aid_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    # Decision maker
    decided_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)
    # Notification
    parent_notified = models.BooleanField(default=False)
    parent_notified_at = models.DateTimeField(null=True, blank=True)
    # Appeal
    appeal_deadline = models.DateField(null=True, blank=True)
    appeal_submitted = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admission_decisions"
        ordering = ["-decided_at"]

    def __str__(self):
        return f"{self.application} - {self.get_decision_display()}"


# =============================================================================
# NEW MODELS: Transfer Student
# =============================================================================


class TransferStudent(models.Model):
    """Transfer student specific information."""

    class TransferStatus(models.TextChoices):
        REQUESTED = "requested", "Transfer Requested"
        DOCUMENTS_PENDING = "docs_pending", "Documents Pending"
        UNDER_REVIEW = "review", "Under Review"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        ENROLLED = "enrolled", "Enrolled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.OneToOneField("Application", on_delete=models.CASCADE, related_name="transfer_details")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transfer_students")
    # Previous school
    previous_school_name = models.CharField(max_length=200)
    previous_school_address = models.TextField(blank=True)
    previous_school_phone = models.CharField(max_length=30, blank=True)
    previous_school_email = models.EmailField(blank=True)
    previous_school_type = models.CharField(max_length=50, blank=True)
    # Duration
    years_attended = models.PositiveIntegerField(null=True, blank=True)
    last_grade_completed = models.CharField(max_length=50, blank=True)
    graduation_date = models.DateField(null=True, blank=True)
    # Academic
    previous_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    class_rank = models.CharField(max_length=50, blank=True)
    class_size = models.PositiveIntegerField(null=True, blank=True)
    # Credits
    credits_earned = models.PositiveIntegerField(null=True, blank=True)
    credits_required = models.PositiveIntegerField(null=True, blank=True)
    transferable_credits = models.PositiveIntegerField(null=True, blank=True)
    # Documents
    transcript_received = models.BooleanField(default=False)
    withdrawal_form_received = models.BooleanField(default=False)
    recommendation_letters_received = models.BooleanField(default=False)
    # Behavioral
    behavioral_issues = models.BooleanField(default=False)
    behavioral_notes = models.TextField(blank=True)
    # Status
    status = models.CharField(max_length=20, choices=TransferStatus.choices, default=TransferStatus.REQUESTED)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transfer_students"

    def __str__(self):
        return f"Transfer: {self.previous_school_name} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Sibling Registration
# =============================================================================


class SiblingGroup(models.Model):
    """Track sibling groups for admissions priority."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sibling_groups")
    family_name = models.CharField(max_length=200)
    # Parent/Guardian
    parent_name = models.CharField(max_length=200)
    parent_email = models.EmailField(blank=True)
    parent_phone = models.CharField(max_length=30, blank=True)
    # Siblings
    total_siblings = models.PositiveIntegerField(default=1)
    currently_enrolled = models.PositiveIntegerField(default=0)
    # Priority
    sibling_priority = models.BooleanField(default=True, help_text="Gets sibling priority in admissions")
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sibling_groups"

    def __str__(self):
        return f"{self.family_name} ({self.total_siblings} siblings)"


class SiblingRecord(models.Model):
    """Individual sibling records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sibling_group = models.ForeignKey(SiblingGroup, on_delete=models.CASCADE, related_name="members")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="sibling_records")
    application = models.ForeignKey(
        "Application", on_delete=models.SET_NULL, null=True, blank=True, related_name="sibling_records"
    )
    is_currently_enrolled = models.BooleanField(default=True)
    grade_level = models.CharField(max_length=50, blank=True)
    enrollment_date = models.DateField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sibling_records"
        unique_together = [("sibling_group", "student")]

    def __str__(self):
        return f"{self.student} - {self.sibling_group.family_name}"


# =============================================================================
# NEW MODELS: Admission Analytics
# =============================================================================


class AdmissionFunnelSnapshot(models.Model):
    """Daily/weekly snapshots of the admissions funnel."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intake = models.ForeignKey("EnrollmentIntake", on_delete=models.CASCADE, related_name="funnel_snapshots")
    snapshot_date = models.DateField()
    # Funnel stages
    inquiries = models.PositiveIntegerField(default=0)
    campus_visits = models.PositiveIntegerField(default=0)
    applications_started = models.PositiveIntegerField(default=0)
    applications_submitted = models.PositiveIntegerField(default=0)
    documents_complete = models.PositiveIntegerField(default=0)
    under_review = models.PositiveIntegerField(default=0)
    interviews_scheduled = models.PositiveIntegerField(default=0)
    interviews_completed = models.PositiveIntegerField(default=0)
    decisions_made = models.PositiveIntegerField(default=0)
    admitted = models.PositiveIntegerField(default=0)
    enrolled = models.PositiveIntegerField(default=0)
    # Conversion rates
    application_to_enrollment_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    inquiry_to_application_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Demographics
    male_count = models.PositiveIntegerField(default=0)
    female_count = models.PositiveIntegerField(default=0)
    # Source
    source_breakdown = models.JSONField(default=dict, blank=True, help_text="Applications by source")
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admission_funnel_snapshots"
        ordering = ["-snapshot_date"]
        unique_together = [("intake", "snapshot_date")]

    def __str__(self):
        return f"Funnel - {self.intake} ({self.snapshot_date})"


# =============================================================================
# NEW MODELS: Admission Document Checklist
# =============================================================================


class AdmissionDocumentChecklist(models.Model):
    """Required documents per intake/grade level."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intake = models.ForeignKey("EnrollmentIntake", on_delete=models.CASCADE, related_name="document_checklists")
    grade_level = models.CharField(max_length=50, blank=True)
    document_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    accepted_formats = models.CharField(max_length=100, blank=True, help_text="PDF, JPG, PNG, etc.")
    max_file_size_mb = models.PositiveIntegerField(default=5)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admission_document_checklists"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.document_name} ({'Required' if self.is_mandatory else 'Optional'})"


class AdmissionDocumentVerification(models.Model):
    """Verification status for each submitted document."""

    class VerificationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey("Application", on_delete=models.CASCADE, related_name="document_verifications")
    checklist_item = models.ForeignKey(
        AdmissionDocumentChecklist, on_delete=models.CASCADE, related_name="verifications"
    )
    status = models.CharField(max_length=15, choices=VerificationStatus.choices, default=VerificationStatus.PENDING)
    # Document
    file = models.FileField(upload_to="admissions/verification/")
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    # Verification
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admission_document_verifications"
        unique_together = [("application", "checklist_item")]

    def __str__(self):
        return f"{self.checklist_item.document_name} - {self.application} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Admission Analytics (Additional)
# =============================================================================


class AdmissionPredictionModel(models.Model):
    """Predictive analytics for admissions."""

    class PredictionType(models.TextChoices):
        ENROLLMENT = "enrollment", "Enrollment Prediction"
        YIELD = "yield", "Yield Rate"
        DEPOSIT = "deposit", "Deposit Prediction"
        RETENTION = "retention", "Retention Risk"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intake = models.ForeignKey("EnrollmentIntake", on_delete=models.CASCADE, related_name="predictions")
    prediction_type = models.CharField(max_length=15, choices=PredictionType.choices)
    prediction_date = models.DateField()
    # Results
    predicted_value = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    factors = models.JSONField(default=dict, blank=True)
    # Metadata
    model_version = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admission_prediction_models"

    def __str__(self):
        return f"{self.get_prediction_type_display()} - {self.intake} ({self.predicted_value})"


class AdmissionMarketingSource(models.Model):
    """Track marketing sources for admissions."""

    class SourceType(models.TextChoices):
        WEBSITE = "website", "Website"
        SOCIAL_MEDIA = "social", "Social Media"
        REFERRAL = "referral", "Referral"
        ADVERTISEMENT = "ad", "Advertisement"
        EVENT = "event", "Event"
        AGENT = "agent", "Agent/Broker"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="admission_marketing_sources")
    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=15, choices=SourceType.choices)
    # Tracking
    total_inquiries = models.PositiveIntegerField(default=0)
    total_applications = models.PositiveIntegerField(default=0)
    total_enrolled = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Cost
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cost_per_enrollment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admission_marketing_sources"

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class AdmissionTrendAnalysis(models.Model):
    """Historical admission trend data."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="admission_trends")
    academic_year = models.CharField(max_length=10)
    intake = models.ForeignKey("EnrollmentIntake", on_delete=models.SET_NULL, null=True, blank=True)
    # Applications
    total_applications = models.PositiveIntegerField(default=0)
    applications_male = models.PositiveIntegerField(default=0)
    applications_female = models.PositiveIntegerField(default=0)
    # Enrollment
    total_enrolled = models.PositiveIntegerField(default=0)
    enrollment_male = models.PositiveIntegerField(default=0)
    enrollment_female = models.PositiveIntegerField(default=0)
    # Yield
    yield_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Financial
    total_tuition_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_scholarships_awarded = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    # By grade
    grade_breakdown = models.JSONField(default=dict, blank=True)
    # By source
    source_breakdown = models.JSONField(default=dict, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admission_trend_analysis"
        unique_together = [("school", "academic_year", "intake")]

    def __str__(self):
        return f"Admission Trends - {self.academic_year}"
