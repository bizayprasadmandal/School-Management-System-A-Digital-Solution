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


# =============================================================================
# NEW MODELS: Conference Waiting List
# =============================================================================


class ConferenceWaitingList(models.Model):
    """Waitlist for full conference slots."""

    class Status(models.TextChoices):
        WAITING = "waiting", "Waiting"
        CONTACTED = "contacted", "Contacted"
        SCHEDULED = "scheduled", "Scheduled"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="conference_waiting_lists")
    parent = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="conference_waiting_lists")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="conference_waiting_lists")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.WAITING)
    position = models.PositiveIntegerField(default=0)
    preferred_dates = models.JSONField(default=list, blank=True)
    preferred_times = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conference_waiting_lists"
        ordering = ["position"]

    def __str__(self):
        return f"#{self.position} {self.parent.full_name} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Recurring Conferences
# =============================================================================


class RecurringConference(models.Model):
    """Recurring conference schedules."""

    class Frequency(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-weekly"
        MONTHLY = "monthly", "Monthly"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        ENDED = "ended", "Ended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="recurring_conferences")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=10, choices=Frequency.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    day_of_week = models.CharField(max_length=10, blank=True)
    time_of_day = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    teacher = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="recurring_conferences_led")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    last_occurrence = models.DateField(null=True, blank=True)
    next_occurrence = models.DateField(null=True, blank=True)
    total_occurrences = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recurring_conferences"

    def __str__(self):
        return f"{self.title} ({self.get_frequency_display()})"


class RecurringConferenceParticipant(models.Model):
    """Participants in recurring conferences."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recurring_conference = models.ForeignKey(RecurringConference, on_delete=models.CASCADE, related_name="participants")
    user = models.ForeignKey(
        "auth_service.User", on_delete=models.CASCADE, related_name="recurring_conference_participations"
    )
    role = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recurring_conference_participants"
        unique_together = [("recurring_conference", "user")]

    def __str__(self):
        return f"{self.user.full_name} - {self.recurring_conference.title}"


# =============================================================================
# NEW MODELS: Conference Settings
# =============================================================================


class ConferenceSettings(models.Model):
    """School-wide conference settings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.OneToOneField("auth_service.School", on_delete=models.CASCADE, related_name="conference_settings")
    booking_window_days = models.PositiveIntegerField(default=30)
    cancellation_window_hours = models.PositiveIntegerField(default=24)
    buffer_between_minutes = models.PositiveIntegerField(default=5)
    max_conferences_per_day = models.PositiveIntegerField(default=20)
    send_confirmation_email = models.BooleanField(default=True)
    send_reminder_email = models.BooleanField(default=True)
    reminder_hours_before = models.PositiveIntegerField(default=24)
    collect_feedback = models.BooleanField(default=True)
    feedback_deadline_days = models.PositiveIntegerField(default=7)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conference_settings"

    def __str__(self):
        return f"Conference Settings - {self.school.name}"


# =============================================================================
# NEW MODELS: Conference Analytics
# =============================================================================


class ConferenceAnalytics(models.Model):
    """Conference analytics and metrics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="conference_analytics")
    date = models.DateField()
    total_scheduled = models.PositiveIntegerField(default=0)
    total_completed = models.PositiveIntegerField(default=0)
    total_no_show = models.PositiveIntegerField(default=0)
    total_cancelled = models.PositiveIntegerField(default=0)
    total_parents = models.PositiveIntegerField(default=0)
    total_teachers = models.PositiveIntegerField(default=0)
    parent_participation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_duration_minutes = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_satisfaction_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    by_type_breakdown = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_analytics"
        unique_together = [("school", "date")]

    def __str__(self):
        return f"Analytics - {self.date}"


# =============================================================================
# NEW MODELS: Conference Booking Rules
# =============================================================================


class ConferenceBookingRule(models.Model):
    """Rules for conference booking."""

    class RuleType(models.TextChoices):
        TIME_SLOT = "time_slot", "Time Slot Restriction"
        GRADE_RESTRICTION = "grade", "Grade Restriction"
        TEACHER_LIMIT = "teacher_limit", "Teacher Booking Limit"
        PARENT_LIMIT = "parent_limit", "Parent Booking Limit"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="conference_booking_rules")
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=15, choices=RuleType.choices)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_booking_rules"
        ordering = ["-priority"]

    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


# =============================================================================
# NEW MODELS: Conference Notifications
# =============================================================================


class ConferenceSystemNotification(models.Model):
    """Conference-specific notifications."""

    class NotificationType(models.TextChoices):
        BOOKING_CONFIRMED = "booking_confirmed", "Booking Confirmed"
        BOOKING_REMINDER = "booking_reminder", "Booking Reminder"
        BOOKING_CANCELLED = "booking_cancelled", "Booking Cancellation"
        WAITLIST_AVAILABLE = "waitlist_available", "Waitlist Spot Available"
        FEEDBACK_REQUEST = "feedback_request", "Feedback Request"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="conference_system_notifications"
    )
    recipient = models.ForeignKey(
        "auth_service.User", on_delete=models.CASCADE, related_name="conference_sys_notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    channel = models.CharField(max_length=10, default="email")
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_system_notifications"

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.recipient.full_name}"


# =============================================================================
# NEW MODELS: Conference Export
# =============================================================================


class ConferenceExport(models.Model):
    """Conference data exports."""

    class ExportType(models.TextChoices):
        SCHEDULE = "schedule", "Schedule Export"
        ATTENDANCE = "attendance", "Attendance Report"
        FEEDBACK = "feedback", "Feedback Summary"
        ALL = "all", "All Data"

    class Format(models.TextChoices):
        CSV = "csv", "CSV"
        PDF = "pdf", "PDF"
        EXCEL = "excel", "Excel"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="conference_exports")
    export_type = models.CharField(max_length=15, choices=ExportType.choices)
    format = models.CharField(max_length=10, choices=Format.choices, default=Format.CSV)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to="conferences/exports/", null=True, blank=True)
    record_count = models.PositiveIntegerField(default=0)
    requested_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "conference_exports"

    def __str__(self):
        return f"{self.get_export_type_display()} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Conference Locations
# =============================================================================


class ConferenceLocation(models.Model):
    """Conference locations/venues."""

    class LocationType(models.TextChoices):
        IN_PERSON = "in_person", "In-Person"
        VIRTUAL = "virtual", "Virtual"
        HYBRID = "hybrid", "Hybrid"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="conference_locations")
    name = models.CharField(max_length=200)
    location_type = models.CharField(max_length=10, choices=LocationType.choices)
    building = models.CharField(max_length=200, blank=True)
    room = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField(default=10)
    virtual_link = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_locations"

    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()})"


# =============================================================================
# NEW MODELS: Conference Blocked Slots
# =============================================================================


class ConferenceBlockedSlot(models.Model):
    """Blocked time slots for conferences."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="conference_blocked_slots")
    teacher = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="conference_blocked_slots")
    title = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_blocked_slots"

    def __str__(self):
        return f"Blocked: {self.teacher.full_name} ({self.date})"


# =============================================================================
# NEW MODELS: Conference Schedule Override
# =============================================================================


class ConferenceScheduleOverride(models.Model):
    """Override default conference schedule."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="conference_schedule_overrides"
    )
    date = models.DateField()
    override_type = models.CharField(
        max_length=20,
        choices=[("early_close", "Early Closure"), ("late_open", "Late Opening"), ("no_conferences", "No Conferences")],
    )
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_schedule_overrides"
        unique_together = [("school", "date")]

    def __str__(self):
        return f"Override - {self.date} ({self.override_type})"


# =============================================================================
# NEW MODELS: Conference Reminder Schedule
# =============================================================================


class ConferenceReminderSchedule(models.Model):
    """Custom reminder schedules."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="conference_reminder_schedules"
    )
    name = models.CharField(max_length=200)
    hours_before = models.PositiveIntegerField()
    channel = models.CharField(max_length=10, choices=[("email", "Email"), ("sms", "SMS"), ("push", "Push")])
    message_template = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_reminder_schedules"

    def __str__(self):
        return f"{self.name} ({self.hours_before}h before)"


# =============================================================================
# NEW MODELS: Conference Accessibility
# =============================================================================


class ConferenceAccessibilityRequirement(models.Model):
    """Accessibility requirements for conferences."""

    class RequirementType(models.TextChoices):
        INTERPRETER = "interpreter", "Sign Language Interpreter"
        TRANSLATOR = "translator", "Language Translator"
        WHEELCHAIR = "wheelchair", "Wheelchair Access"
        LARGE_PRINT = "large_print", "Large Print Materials"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        "ConferenceBooking", on_delete=models.CASCADE, related_name="accessibility_requirements"
    )
    requirement_type = models.CharField(max_length=15, choices=RequirementType.choices)
    details = models.TextField(blank=True)
    language = models.CharField(max_length=50, blank=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_accessibility_requirements"

    def __str__(self):
        return f"{self.get_requirement_type_display()} - {self.booking}"


# =============================================================================
# NEW MODELS: Conference Note Templates
# =============================================================================


class ConferenceNoteTemplate(models.Model):
    """Note templates for conferences."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="conference_note_templates"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sections = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_note_templates"

    def __str__(self):
        return self.name


# =============================================================================
# NEW MODELS: Conference Approval
# =============================================================================


class ConferenceApproval(models.Model):
    """Approval workflow for conferences."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey("ConferenceBooking", on_delete=models.CASCADE, related_name="approvals")
    approver = models.ForeignKey(
        "auth_service.User", on_delete=models.CASCADE, related_name="conference_approvals_made"
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    comments = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_approvals"
        unique_together = [("booking", "approver")]

    def __str__(self):
        return f"Approval - {self.booking} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Conference Resources
# =============================================================================


class ConferenceResource(models.Model):
    """Resources needed for conferences."""

    class ResourceType(models.TextChoices):
        ROOM = "room", "Meeting Room"
        EQUIPMENT = "equipment", "Equipment"
        DOCUMENT = "document", "Document"
        TRANSLATOR = "translator", "Translator"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey("ConferenceBooking", on_delete=models.CASCADE, related_name="resources")
    resource_type = models.CharField(max_length=15, choices=ResourceType.choices)
    name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    is_reserved = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_resources"

    def __str__(self):
        return f"{self.get_resource_type_display()} - {self.name}"


# =============================================================================
# NEW MODELS: Conference Survey
# =============================================================================


class ConferenceSurvey(models.Model):
    """Conference satisfaction surveys."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="conference_surveys")
    title = models.CharField(max_length=200)
    questions = models.JSONField(default=list)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    total_responses = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_surveys"

    def __str__(self):
        return self.title


class ConferenceSurveyResponse(models.Model):
    """Survey responses."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(ConferenceSurvey, on_delete=models.CASCADE, related_name="responses")
    respondent = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    answers = models.JSONField(default=dict)
    overall_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_survey_responses"

    def __str__(self):
        return f"Response - {self.survey} ({self.submitted_at})"


# =============================================================================
# NEW MODELS: Conference Calendar Sync
# =============================================================================


class ConferenceCalendarSync(models.Model):
    """Calendar sync for conferences."""

    class CalendarType(models.TextChoices):
        GOOGLE = "google", "Google Calendar"
        OUTLOOK = "outlook", "Outlook Calendar"
        ICS = "ics", "iCal Feed"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ERROR = "error", "Sync Error"
        DISABLED = "disabled", "Disabled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="conference_calendar_syncs")
    calendar_type = models.CharField(max_length=10, choices=CalendarType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    calendar_id = models.CharField(max_length=255, blank=True)
    ical_url = models.URLField(max_length=500, blank=True)
    auto_sync = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conference_calendar_syncs"
        unique_together = [("user", "calendar_type")]

    def __str__(self):
        return f"{self.get_calendar_type_display()} - {self.user.full_name}"


# =============================================================================
# NEW MODELS: Conference History Extended
# =============================================================================


class ConferenceHistoryDetail(models.Model):
    """Detailed conference history."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="conference_history_details"
    )
    booking = models.ForeignKey("ConferenceBooking", on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="conference_history_details")
    conference_date = models.DateField()
    conference_type = models.CharField(max_length=50, blank=True)
    topics_discussed = models.JSONField(default=list, blank=True)
    outcome = models.TextField(blank=True)
    follow_up_needed = models.BooleanField(default=False)
    recommendations = models.TextField(blank=True)
    recorded_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_history_details"
        ordering = ["-conference_date"]

    def __str__(self):
        return f"{self.student} - {self.conference_date}"


class ConferenceTimeSlot(models.Model):
    """Available time slots for booking."""

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        BOOKED = "booked", "Booked"
        BLOCKED = "blocked", "Blocked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="conference_time_slots")
    teacher = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="conference_time_slots")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.AVAILABLE)
    booking = models.ForeignKey("ConferenceBooking", on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(ConferenceLocation, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_time_slots"
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.teacher.full_name} - {self.date} {self.start_time}-{self.end_time}"


class ConferenceFeedbackTemplate(models.Model):
    """Templates for conference feedback questions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="conference_feedback_templates"
    )
    name = models.CharField(max_length=200)
    questions = models.JSONField(default=list)
    target_audience = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_feedback_templates"

    def __str__(self):
        return self.name


class ConferenceFollowUp(models.Model):
    """Follow-up actions after conferences."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey("ConferenceBooking", on_delete=models.CASCADE, related_name="conference_follow_ups")
    assigned_to = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    action_required = models.TextField()
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conference_follow_ups"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Follow-up: {self.action_required[:50]} ({self.get_status_display()})"


class ConferenceRoomBooking(models.Model):
    """Room booking for conferences."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.ForeignKey(ConferenceLocation, on_delete=models.CASCADE, related_name="room_bookings")
    booking = models.ForeignKey("ConferenceBooking", on_delete=models.CASCADE, related_name="room_bookings")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    booked_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_room_bookings"
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return f"{self.location.name} - {self.date} {self.start_time}-{self.end_time}"


class ConferenceTemplateSection(models.Model):
    """Sections within a conference template."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(ConferenceTemplate, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    suggested_questions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_template_sections"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.title} ({self.template.name})"


class ConferenceNoShow(models.Model):
    """Track no-shows for rescheduling."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey("ConferenceBooking", on_delete=models.CASCADE, related_name="no_shows")
    user = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="conference_no_shows")
    rescheduled = models.BooleanField(default=False)
    rescheduled_to = models.ForeignKey(
        "ConferenceBooking", on_delete=models.SET_NULL, null=True, blank=True, related_name="rescheduled_from"
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_no_shows"

    def __str__(self):
        return f"No-show: {self.user.full_name} ({self.booking})"


class ConferenceConferenceType(models.Model):
    """Extended conference type settings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conference_type = models.OneToOneField(ConferenceType, on_delete=models.CASCADE, related_name="extended_settings")
    requires_parent_consent = models.BooleanField(default=False)
    requires_student_consent = models.BooleanField(default=False)
    auto_generate_notes = models.BooleanField(default=False)
    default_location = models.ForeignKey(ConferenceLocation, on_delete=models.SET_NULL, null=True, blank=True)
    max_duration_minutes = models.PositiveIntegerField(default=60)
    allow_virtual = models.BooleanField(default=True)
    allow_walk_in = models.BooleanField(default=False)
    fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conference_type_extended_settings"

    def __str__(self):
        return f"Extended: {self.conference_type.name}"
