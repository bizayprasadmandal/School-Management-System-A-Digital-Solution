import uuid

from django.db import models
from services.auth.models import School, User
from services.students.models import Student


class ConferenceSlot(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="conference_slots")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conference_slots")
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="conference_slots", null=True, blank=True
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    booked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="booked_slots")
    notes = models.TextField(blank=True)

    # Zoom meeting integration
    zoom_meeting_id = models.CharField(max_length=64, blank=True, default="", help_text="Zoom meeting ID")
    zoom_join_url = models.URLField(blank=True, default="", help_text="Zoom join link for participants")
    zoom_start_url = models.URLField(blank=True, default="", help_text="Zoom start link for host")
    zoom_password = models.CharField(max_length=32, blank=True, default="", help_text="Zoom meeting password")
    is_zoom_created = models.BooleanField(
        default=False, help_text="Whether a Zoom meeting has been created for this slot"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conference_slots"
        ordering = ["date", "start_time"]
        unique_together = [("teacher", "date", "start_time")]

    def __str__(self):
        return f"{self.teacher.full_name} - {self.date} {self.start_time}-{self.end_time}"


# =============================================================================
# Conference Types
# =============================================================================


class ConferenceType(models.Model):
    """Different conference types (parent-teacher, student-led, etc.)."""

    class Category(models.TextChoices):
        PARENT_TEACHER = "ptc", "Parent-Teacher Conference"
        STUDENT_LED = "student_led", "Student-Led Conference"
        THREE_WAY = "three_way", "Three-Way Conference"
        IEP = "iep", "IEP Meeting"
        PLANNING = "planning", "Academic Planning"
        PROGRESS = "progress", "Progress Review"
        DISCIPLINE = "discipline", "Discipline Conference"
        ORIENTATION = "orientation", "Orientation"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="conference_types")
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=15, choices=Category.choices, default=Category.PARENT_TEACHER)
    description = models.TextField(blank=True)
    # Settings
    default_duration_minutes = models.PositiveSmallIntegerField(default=15)
    max_participants = models.PositiveSmallIntegerField(default=3)
    allow_virtual = models.BooleanField(default=True)
    allow_notes = models.BooleanField(default=True)
    require_student = models.BooleanField(default=False)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conference_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =============================================================================
# Conference Bookings
# =============================================================================


class ConferenceBooking(models.Model):
    """Self-service booking for parents."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"
        NO_SHOW = "no_show", "No Show"
        RESCHEDULED = "rescheduled", "Rescheduled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slot = models.ForeignKey(ConferenceSlot, on_delete=models.CASCADE, related_name="bookings")
    booking_type = models.ForeignKey(ConferenceType, on_delete=models.SET_NULL, null=True, blank=True)
    # Participants
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conference_bookings")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="conference_bookings")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teacher_bookings")
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Virtual Meeting
    is_virtual = models.BooleanField(default=False)
    meeting_link = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)
    # Details
    reason = models.TextField(blank=True, help_text="Reason for conference")
    notes = models.TextField(blank=True)
    # Confirmation
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    # Metadata
    booked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conference_bookings"
        ordering = ["-booked_at"]
        indexes = [
            models.Index(fields=["parent", "status"]),
            models.Index(fields=["student", "status"]),
        ]

    def __str__(self):
        return f"{self.parent.full_name} - {self.student} ({self.get_status_display()})"


# =============================================================================
# Conference Reminders
# =============================================================================


class ConferenceReminder(models.Model):
    """Automated reminders before conferences."""

    class ReminderType(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push Notification"
        IN_APP = "in_app", "In-App"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(ConferenceBooking, on_delete=models.CASCADE, related_name="reminders")
    reminder_type = models.CharField(max_length=10, choices=ReminderType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    # Scheduling
    send_before_minutes = models.PositiveIntegerField(default=60, help_text="Minutes before conference")
    sent_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_reminders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reminder for {self.booking} ({self.get_reminder_type_display()})"


# =============================================================================
# Conference Notes
# =============================================================================


class ConferenceNotes(models.Model):
    """Notes and action items from conferences."""

    class NoteType(models.TextChoices):
        GENERAL = "general", "General Notes"
        ACADEMIC = "academic", "Academic Discussion"
        BEHAVIOR = "behavior", "Behavior Notes"
        ACTION_ITEMS = "action", "Action Items"
        FOLLOW_UP = "follow_up", "Follow-up Required"
        RECOMMENDATIONS = "recommendations", "Recommendations"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(ConferenceBooking, on_delete=models.CASCADE, related_name="conference_notes")
    note_type = models.CharField(max_length=15, choices=NoteType.choices, default=NoteType.GENERAL)
    # Content
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    # Action Items
    has_action_items = models.BooleanField(default=False)
    action_items = models.JSONField(default=list, help_text="List of action items")
    action_items_completed = models.BooleanField(default=False)
    # Follow-up
    follow_up_needed = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    # Personnel
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Visibility
    shared_with_parent = models.BooleanField(default=False)
    shared_with_student = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conference_notes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.booking} - {self.get_note_type_display()}"


# =============================================================================
# Follow-up Tracking
# =============================================================================


class FollowUpTracking(models.Model):
    """Track follow-up actions from conferences."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        OVERDUE = "overdue", "Overdue"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(ConferenceBooking, on_delete=models.CASCADE, related_name="follow_ups")
    # Details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Assignment
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="conference_follow_ups"
    )
    # Dates
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "follow_up_tracking"
        ordering = ["due_date", "-priority"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


# =============================================================================
# Conference Availability
# =============================================================================


class ConferenceAvailability(models.Model):
    """Teacher availability management."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    class AvailabilityType(models.TextChoices):
        AVAILABLE = "available", "Available"
        UNAVAILABLE = "unavailable", "Unavailable"
        TENTATIVE = "tentative", "Tentative"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conference_availability")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="conference_availability")
    # Schedule
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    availability_type = models.CharField(
        max_length=15, choices=AvailabilityType.choices, default=AvailabilityType.AVAILABLE
    )
    # Location
    location = models.CharField(max_length=100, blank=True)
    is_virtual_available = models.BooleanField(default=True)
    # Dates
    effective_from = models.DateField()
    effective_until = models.DateField(null=True, blank=True)
    # Status
    is_recurring = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conference_availability"
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.teacher.full_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


# =============================================================================
# Conference Reports
# =============================================================================


class ConferenceReport(models.Model):
    """Conference analytics and reports."""

    class ReportType(models.TextChoices):
        ATTENDANCE = "attendance", "Attendance Report"
        SUMMARY = "summary", "Conference Summary"
        TEACHER = "teacher", "Teacher-wise Report"
        GRADE = "grade", "Grade-wise Report"
        FOLLOW_UP = "follow_up", "Follow-up Report"
        FEEDBACK = "feedback", "Feedback Report"
        CUSTOM = "custom", "Custom Report"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATED = "generated", "Generated"
        SENT = "sent", "Sent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="conference_reports")
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
    total_conferences = models.PositiveIntegerField(default=0)
    total_attended = models.PositiveIntegerField(default=0)
    total_no_show = models.PositiveIntegerField(default=0)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Breakdown
    by_teacher = models.JSONField(default=dict)
    by_grade = models.JSONField(default=dict)
    by_type = models.JSONField(default=dict)
    # Personnel
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# =============================================================================
# Conference Feedback
# =============================================================================


class ConferenceFeedback(models.Model):
    """Parent/teacher feedback forms."""

    class FeedbackFor(models.TextChoices):
        TEACHER = "teacher", "Teacher"
        CONFERENCE = "conference", "Conference"
        SCHOOL = "school", "School"
        OTHER = "other", "Other"

    class Rating(models.IntegerChoices):
        POOR = 1, "Poor"
        FAIR = 2, "Fair"
        GOOD = 3, "Good"
        VERY_GOOD = 4, "Very Good"
        EXCELLENT = 5, "Excellent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(ConferenceBooking, on_delete=models.CASCADE, related_name="feedbacks")
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conference_feedbacks")
    # Feedback
    feedback_for = models.CharField(max_length=15, choices=FeedbackFor.choices)
    overall_rating = models.IntegerField(choices=Rating.choices)
    # Specific Ratings
    communication_rating = models.IntegerField(choices=Rating.choices, null=True, blank=True)
    preparedness_rating = models.IntegerField(choices=Rating.choices, null=True, blank=True)
    helpfulness_rating = models.IntegerField(choices=Rating.choices, null=True, blank=True)
    # Comments
    positive_feedback = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    additional_comments = models.TextField(blank=True)
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_feedbacks"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.submitted_by.full_name} - {self.get_feedback_for_display()} ({self.overall_rating}/5)"


# =============================================================================
# Conference History
# =============================================================================


class ConferenceHistory(models.Model):
    """Historical conference records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="conference_history")
    booking = models.ForeignKey(ConferenceBooking, on_delete=models.CASCADE, related_name="history")
    # Details
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="teaching_conferences")
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="parent_conferences")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_conferences")
    # Conference Info
    conference_date = models.DateField()
    conference_type = models.ForeignKey(ConferenceType, on_delete=models.SET_NULL, null=True, blank=True)
    was_virtual = models.BooleanField(default=False)
    duration_minutes = models.PositiveSmallIntegerField(default=15)
    # Outcome
    was_attended = models.BooleanField(default=True)
    had_notes = models.BooleanField(default=False)
    had_action_items = models.BooleanField(default=False)
    had_follow_up = models.BooleanField(default=False)
    # Summary
    summary = models.TextField(blank=True)
    # Metadata
    archived_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_history"
        ordering = ["-conference_date"]
        indexes = [
            models.Index(fields=["teacher", "conference_date"]),
            models.Index(fields=["parent", "conference_date"]),
            models.Index(fields=["student", "conference_date"]),
        ]

    def __str__(self):
        return f"{self.teacher.full_name} - {self.parent.full_name} ({self.conference_date})"


# =============================================================================
# Virtual Conference
# =============================================================================


class VirtualConference(models.Model):
    """Virtual/hybrid conference support."""

    class Platform(models.TextChoices):
        ZOOM = "zoom", "Zoom"
        GOOGLE_MEET = "meet", "Google Meet"
        MS_TEAMS = "teams", "Microsoft Teams"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(ConferenceBooking, on_delete=models.CASCADE, related_name="virtual_details")
    # Platform
    platform = models.CharField(max_length=15, choices=Platform.choices, default=Platform.ZOOM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    # Meeting Details
    meeting_id = models.CharField(max_length=100)
    meeting_url = models.URLField()
    meeting_password = models.CharField(max_length=50, blank=True)
    host_url = models.URLField(blank=True)
    # Recording
    recording_url = models.URLField(blank=True)
    has_recording = models.BooleanField(default=False)
    # Participants
    participants_joined = models.PositiveSmallIntegerField(default=0)
    # Duration
    scheduled_duration = models.PositiveSmallIntegerField(default=15)
    actual_duration = models.PositiveSmallIntegerField(null=True, blank=True)
    # Technical
    had_technical_issues = models.BooleanField(default=False)
    technical_notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "virtual_conferences"

    def __str__(self):
        return f"Virtual: {self.booking} ({self.get_platform_display()})"


# =============================================================================
# Conference Templates
# =============================================================================


class ConferenceTemplate(models.Model):
    """Reusable conference templates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="conference_templates")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # Template Settings
    conference_type = models.ForeignKey(ConferenceType, on_delete=models.SET_NULL, null=True, blank=True)
    default_duration_minutes = models.PositiveSmallIntegerField(default=15)
    # Template Content
    agenda_items = models.JSONField(default=list, help_text="List of agenda items")
    discussion_topics = models.JSONField(default=list, help_text="Discussion topics")
    questions_to_ask = models.JSONField(default=list, help_text="Questions for parent/teacher")
    # Settings
    require_notes = models.BooleanField(default=True)
    require_feedback = models.BooleanField(default=False)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conference_templates"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =============================================================================
# Waitlist Management
# =============================================================================


class WaitlistManagement(models.Model):
    """Waitlist for full time slots."""

    class Status(models.TextChoices):
        WAITING = "waiting", "Waiting"
        OFFERED = "offered", "Slot Offered"
        BOOKED = "booked", "Booked"
        EXPIRED = "expired", "Offer Expired"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slot = models.ForeignKey(ConferenceSlot, on_delete=models.CASCADE, related_name="waitlist")
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conference_waitlist")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="conference_waitlist")
    # Position
    position = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.WAITING)
    # Offer
    offered_at = models.DateTimeField(null=True, blank=True)
    offer_expires_at = models.DateTimeField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "waitlist_management"
        ordering = ["position"]
        unique_together = [("slot", "parent")]

    def __str__(self):
        return f"{self.parent.full_name} - Position {self.position} for {self.slot}"
