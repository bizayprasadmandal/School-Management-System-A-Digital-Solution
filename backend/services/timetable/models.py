"""
Timetable Service — Period scheduling, room bookings, school events
"""

import uuid

from django.conf import settings
from django.db import models
from services.academics.models import Subject, TeacherAssignment
from services.auth.models import School, User
from services.students.models import AcademicYear, Classroom


class Period(models.Model):
    """Master period definition (e.g. Period 1: 08:00-08:45)."""

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="periods")
    name = models.CharField(max_length=50)  # "Period 1", "Lunch", "Break"
    period_number = models.PositiveSmallIntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)

    class Meta:
        db_table = "periods"
        ordering = ["period_number"]
        unique_together = [("school", "period_number")]

    def __str__(self):
        return f"{self.name} ({self.start_time}–{self.end_time})"


class TimetableSlot(models.Model):
    """A single cell in the class timetable grid."""

    DAYS_OF_WEEK = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
    ]

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="timetable_slots")
    assignment = models.ForeignKey(TeacherAssignment, on_delete=models.CASCADE, related_name="timetable_slots")
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    day_of_week = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    room = models.CharField(max_length=50, blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "timetable_slots"
        unique_together = [("classroom", "period", "day_of_week", "academic_year")]

    def __str__(self):
        day_name = dict(self.DAYS_OF_WEEK)[self.day_of_week]
        return f"{self.classroom} — {day_name} {self.period}"


class SchoolEvent(models.Model):
    """Calendar events — holidays, PTMs, sports days, etc."""

    class EventType(models.TextChoices):
        HOLIDAY = "holiday", "Public Holiday"
        EXAM = "exam", "Examination"
        SPORTS = "sports", "Sports Event"
        CULTURAL = "cultural", "Cultural Program"
        PTM = "ptm", "Parent-Teacher Meeting"
        TRIP = "trip", "Field Trip"
        OTHER = "other", "Other"

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=255, blank=True)
    is_school_wide = models.BooleanField(default=True)
    target_grades = models.ManyToManyField("students.Grade", blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "school_events"
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.title} ({self.start_date})"


class TeacherTimetable(models.Model):
    """Individual teacher schedule view — aggregated from timetable slots."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_timetables")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    slot = models.ForeignKey(TimetableSlot, on_delete=models.CASCADE, related_name="teacher_timetables")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    day_of_week = models.PositiveSmallIntegerField(choices=TimetableSlot.DAYS_OF_WEEK)
    total_hours_per_week = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "teacher_timetables"
        unique_together = [("teacher", "academic_year", "period", "day_of_week")]
        ordering = ["day_of_week", "period"]

    def __str__(self):
        day_name = dict(TimetableSlot.DAYS_OF_WEEK)[self.day_of_week]
        return f"{self.teacher} — {day_name} {self.period}"


class SubstituteTeacher(models.Model):
    """Substitute teacher assignments for absent teachers."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="substitute_teachers")
    original_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="timetable_substitute_absences"
    )
    substitute_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="timetable_substitute_assignments"
    )
    slot = models.ForeignKey(TimetableSlot, on_delete=models.CASCADE)
    date = models.DateField()
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="substitute_approvals"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "timetable_substitute_teachers"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.substitute_teacher} covering for {self.original_teacher} on {self.date}"


class ConflictDetection(models.Model):
    """Detect and track scheduling conflicts."""

    class ConflictType(models.TextChoices):
        TEACHER_DOUBLE_BOOK = "teacher_double_book", "Teacher Double Booking"
        ROOM_DOUBLE_BOOK = "room_double_book", "Room Double Booking"
        STUDENT_DOUBLE_BOOK = "student_double_book", "Student Double Booking"
        TEACHER_UNAVAILABLE = "teacher_unavailable", "Teacher Unavailable"
        ROOM_UNAVAILABLE = "room_unavailable", "Room Unavailable"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        RESOLVED = "resolved", "Resolved"
        IGNORED = "ignored", "Ignored"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="timetable_conflicts")
    conflict_type = models.CharField(max_length=25, choices=ConflictType.choices)
    slot1 = models.ForeignKey(TimetableSlot, on_delete=models.CASCADE, related_name="conflicts_as_slot1")
    slot2 = models.ForeignKey(TimetableSlot, on_delete=models.CASCADE, related_name="conflicts_as_slot2")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "timetable_conflicts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Conflict: {self.get_conflict_type_display()} ({self.status})"


class ExamSchedule(models.Model):
    """Exam timetable management."""

    class ExamType(models.TextChoices):
        MIDTERM = "midterm", "Mid-Term"
        FINAL = "final", "Final"
        QUIZ = "quiz", "Quiz"
        PRACTICAL = "practical", "Practical"
        ORAL = "oral", "Oral"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="exam_schedules")
    title = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=20, choices=ExamType.choices, default=ExamType.MIDTERM)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    instructions = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "timetable_exam_schedules"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} ({self.get_exam_type_display()})"


class ExamScheduleEntry(models.Model):
    """Individual exam entries within an exam schedule."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="entries")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True)
    invigilator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timetable_invigilated_exams",
    )
    total_marks = models.PositiveIntegerField(default=100)
    passing_marks = models.PositiveIntegerField(default=33)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exam_schedule_entries"
        ordering = ["exam_date", "start_time"]
        unique_together = [("exam_schedule", "classroom", "subject")]

    def __str__(self):
        return f"{self.classroom} - {self.subject} ({self.exam_date})"


class AcademicCalendar(models.Model):
    """Year-long academic calendar management."""

    class CalendarType(models.TextChoices):
        TERM_START = "term_start", "Term Start"
        TERM_END = "term_end", "Term End"
        HOLIDAY = "holiday", "Holiday"
        VACATION = "vacation", "Vacation"
        EXAM_PERIOD = "exam_period", "Exam Period"
        REGISTRATION = "registration", "Registration"
        ORIENTATION = "orientation", "Orientation"
        GRADUATION = "graduation", "Graduation"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_calendar")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    calendar_type = models.CharField(max_length=20, choices=CalendarType.choices, default=CalendarType.OTHER)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    is_school_wide = models.BooleanField(default=True)
    target_grades = models.ManyToManyField("students.Grade", blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academic_calendar"
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.title} ({self.start_date})"


class RoomBooking(models.Model):
    """Room/venue booking system for classes, events, etc."""

    class BookingType(models.TextChoices):
        CLASS = "class", "Regular Class"
        EXAM = "exam", "Examination"
        EVENT = "event", "Event"
        MEETING = "meeting", "Meeting"
        TRAINING = "training", "Training"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="room_bookings")
    room_name = models.CharField(max_length=100)
    booking_type = models.CharField(max_length=20, choices=BookingType.choices, default=BookingType.CLASS)
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="room_bookings"
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    purpose = models.CharField(max_length=200, blank=True)
    attendees_count = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_room_bookings",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "room_bookings"
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.room_name} — {self.purpose} ({self.date})"


class TimetableTemplate(models.Model):
    """Reusable timetable templates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="timetable_templates")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    grade = models.ForeignKey("students.Grade", on_delete=models.SET_NULL, null=True, blank=True)
    periods_per_day = models.PositiveSmallIntegerField(default=8)
    working_days = models.CharField(
        max_length=50, default="0,1,2,3,4", help_text="Comma-separated day indices: 0=Mon,1=Tue,..."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "timetable_templates"
        ordering = ["name"]

    def __str__(self):
        return self.name


class TimetableTemplateSlot(models.Model):
    """Individual slots within a timetable template."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(TimetableTemplate, on_delete=models.CASCADE, related_name="slots")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    day_of_week = models.PositiveSmallIntegerField(choices=TimetableSlot.DAYS_OF_WEEK)
    room = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "timetable_template_slots"
        unique_together = [("template", "period", "day_of_week")]
        ordering = ["day_of_week", "period"]

    def __str__(self):
        day_name = dict(TimetableSlot.DAYS_OF_WEEK)[self.day_of_week]
        return f"{self.template.name} — {day_name} {self.period}"


class TeacherPreference(models.Model):
    """Faculty time preferences for timetable generation."""

    class PreferenceType(models.TextChoices):
        PREFERRED = "preferred", "Preferred"
        UNAVAILABLE = "unavailable", "Unavailable"
        PREFERRED_DAY = "preferred_day", "Preferred Day"
        PREFERRED_TIME = "preferred_time", "Preferred Time"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_preferences")
    preference_type = models.CharField(max_length=20, choices=PreferenceType.choices)
    day_of_week = models.PositiveSmallIntegerField(choices=TimetableSlot.DAYS_OF_WEEK, null=True, blank=True)
    period = models.ForeignKey(Period, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_to = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "teacher_preferences"
        ordering = ["teacher", "day_of_week"]

    def __str__(self):
        return f"{self.teacher} — {self.get_preference_type_display()}"


class TimetableApproval(models.Model):
    """Timetable approval workflow."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        PUBLISHED = "published", "Published"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="timetable_approvals")
    title = models.CharField(max_length=200)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    grade = models.ForeignKey("students.Grade", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="timetable_submissions"
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="timetable_approvals"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "timetable_approvals"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class TimetableChange(models.Model):
    """Track schedule change history."""

    class ChangeType(models.TextChoices):
        ROOM_CHANGE = "room_change", "Room Change"
        TIME_CHANGE = "time_change", "Time Change"
        TEACHER_CHANGE = "teacher_change", "Teacher Change"
        CANCELLATION = "cancellation", "Cancellation"
        RESCHEDULING = "rescheduling", "Rescheduling"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="timetable_changes")
    change_type = models.CharField(max_length=20, choices=ChangeType.choices)
    slot = models.ForeignKey(TimetableSlot, on_delete=models.CASCADE, related_name="changes")
    old_value = models.CharField(max_length=200, blank=True)
    new_value = models.CharField(max_length=200, blank=True)
    effective_date = models.DateField()
    reason = models.TextField(blank=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "timetable_changes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_change_type_display()} on {self.effective_date}"


class CoCurricularSchedule(models.Model):
    """Co-curricular activity scheduling."""

    class ActivityType(models.TextChoices):
        SPORTS = "sports", "Sports"
        ARTS = "arts", "Arts"
        MUSIC = "music", "Music"
        DRAMA = "drama", "Drama"
        DEBATE = "debate", "Debate"
        CLUB = "club", "Club"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="co_curricular_schedules")
    activity_name = models.CharField(max_length=200)
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices, default=ActivityType.OTHER)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="co_curricular_activities",
    )
    day_of_week = models.PositiveSmallIntegerField(choices=TimetableSlot.DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100, blank=True)
    max_participants = models.PositiveSmallIntegerField(default=0)
    target_grades = models.ManyToManyField("students.Grade", blank=True)
    is_mandatory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "co_curricular_schedules"
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.activity_name} ({self.get_activity_type_display()})"


class TimetableReport(models.Model):
    """Timetable analytics and reports."""

    class ReportType(models.TextChoices):
        TEACHER_LOAD = "teacher_load", "Teacher Load Distribution"
        ROOM_UTILIZATION = "room_utilization", "Room Utilization"
        SUBJECT_DISTRIBUTION = "subject_distribution", "Subject Distribution"
        CONFLICT_SUMMARY = "conflict_summary", "Conflict Summary"
        GENERAL = "general", "General Report"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="timetable_reports")
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=25, choices=ReportType.choices, default=ReportType.GENERAL)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    data = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "timetable_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"


class SchoolClosure(models.Model):
    """School closure days."""

    class ClosureType(models.TextChoices):
        PUBLIC_HOLIDAY = "public_holiday", "Public Holiday"
        SCHOOL_HOLIDAY = "school_holiday", "School Holiday"
        WEATHER = "weather", "Weather Closure"
        EMERGENCY = "emergency", "Emergency Closure"
        MAINTENANCE = "maintenance", "Maintenance Day"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="school_closures")
    title = models.CharField(max_length=200)
    closure_type = models.CharField(max_length=20, choices=ClosureType.choices, default=ClosureType.OTHER)
    date = models.DateField()
    description = models.TextField(blank=True)
    affects_all = models.BooleanField(default=True)
    target_grades = models.ManyToManyField("students.Grade", blank=True)
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "school_closures"
        ordering = ["date"]

    def __str__(self):
        return f"{self.title} ({self.date})"


# =============================================================================
# NEW MODELS: Bell Schedule
# =============================================================================


class BellSchedule(models.Model):
    """School bell/period timing configuration."""

    class DayType(models.TextChoices):
        REGULAR = "regular", "Regular Day"
        EARLY = "early", "Early Dismissal"
        LATE = "late", "Late Start"
        SPECIAL = "special", "Special Schedule"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="bell_schedules")
    name = models.CharField(max_length=200)
    day_type = models.CharField(max_length=10, choices=DayType.choices, default=DayType.REGULAR)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_until = models.DateField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bell_schedules"

    def __str__(self):
        return f"{self.name} ({self.get_day_type_display()})"


class BellScheduleEntry(models.Model):
    """Individual bell schedule entries."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bell_schedule = models.ForeignKey(BellSchedule, on_delete=models.CASCADE, related_name="entries")
    period = models.ForeignKey("Period", on_delete=models.CASCADE, related_name="bell_entries")
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False, help_text="Is this a break/lunch period?")
    break_name = models.CharField(max_length=50, blank=True, help_text="e.g., Morning Break, Lunch")
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "bell_schedule_entries"
        ordering = ["sort_order"]
        unique_together = [("bell_schedule", "period")]

    def __str__(self):
        return f"{self.period} - {self.start_time} to {self.end_time}"

    @property
    def duration_minutes(self):
        from datetime import datetime

        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        return int((end - start).total_seconds() / 60)


# =============================================================================
# NEW MODELS: Class Group / Section Management
# =============================================================================


class ClassGroup(models.Model):
    """Class groups / sections within a grade."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="class_groups")
    grade_level = models.CharField(max_length=50)
    section_name = models.CharField(max_length=50, help_text="e.g., A, B, Science, Arts")
    academic_year = models.CharField(max_length=10)
    # Capacity
    max_students = models.PositiveIntegerField(default=40)
    current_students = models.PositiveIntegerField(default=0)
    # Class teacher
    class_teacher = models.ForeignKey(
        "auth_service.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="class_groups_managed"
    )
    # Room
    homeroom = models.ForeignKey(
        "infrastructure.Room", on_delete=models.SET_NULL, null=True, blank=True, related_name="class_groups"
    )
    # Subjects
    subjects = models.JSONField(default=list, blank=True, help_text="List of subject codes")
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "class_groups"
        unique_together = [("school", "grade_level", "section_name", "academic_year")]
        ordering = ["grade_level", "section_name"]

    def __str__(self):
        return f"Grade {self.grade_level} - Section {self.section_name} ({self.academic_year})"


class ClassGroupEnrollment(models.Model):
    """Student enrollment in class groups."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="class_group_enrollments")
    enrolled_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "class_group_enrollments"
        unique_together = [("class_group", "student")]

    def __str__(self):
        return f"{self.student} in {self.class_group}"


# =============================================================================
# NEW MODELS: Subject-Teacher Assignment
# =============================================================================


class SubjectTeacherAssignment(models.Model):
    """Assign teachers to subjects for specific classes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="subject_teacher_assignments"
    )
    teacher = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="subject_assignments")
    subject = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=20, blank=True)
    # Class assignment
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name="subject_assignments")
    # Schedule
    periods_per_week = models.PositiveIntegerField(default=3)
    academic_year = models.CharField(max_length=10)
    semester = models.CharField(max_length=10, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subject_teacher_assignments"
        unique_together = [("teacher", "subject", "class_group", "academic_year")]

    def __str__(self):
        return f"{self.teacher} - {self.subject} ({self.class_group})"


# =============================================================================
# NEW MODELS: Lesson Plans
# =============================================================================


class LessonPlan(models.Model):
    """Teacher lesson plans linked to timetable slots."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"
        DELIVERED = "delivered", "Delivered"
        REVISION = "revision", "Needs Revision"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="lesson_plans")
    teacher = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="lesson_plans")
    # Class
    class_group = models.ForeignKey(ClassGroup, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=100)
    # Schedule
    plan_date = models.DateField()
    period = models.ForeignKey("Period", on_delete=models.SET_NULL, null=True, blank=True)
    timetable_slot = models.ForeignKey("TimetableSlot", on_delete=models.SET_NULL, null=True, blank=True)
    # Content
    topic = models.CharField(max_length=200)
    learning_objectives = models.TextField(blank=True)
    content_outline = models.TextField(blank=True)
    teaching_methods = models.TextField(blank=True)
    resources_needed = models.TextField(blank=True)
    materials = models.TextField(blank=True)
    # Assessment
    formative_assessment = models.TextField(blank=True)
    homework = models.TextField(blank=True)
    # Differentiation
    differentiation_strategies = models.TextField(blank=True)
    special_needs_accommodations = models.TextField(blank=True)
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    approved_by = models.ForeignKey(
        "auth_service.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_lesson_plans"
    )
    # Reflection
    post_lesson_notes = models.TextField(blank=True)
    what_worked_well = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "timetable_lesson_plans"
        ordering = ["-plan_date"]

    def __str__(self):
        return f"{self.topic} - {self.class_group or self.subject} ({self.plan_date})"


# =============================================================================
# NEW MODELS: Exam Room Allocation
# =============================================================================


class ExamRoomAllocation(models.Model):
    """Room allocation for examinations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="exam_room_allocations")
    exam_schedule = models.ForeignKey("ExamSchedule", on_delete=models.CASCADE, related_name="room_allocations")
    room = models.ForeignKey("infrastructure.Room", on_delete=models.CASCADE, related_name="exam_allocations")
    # Capacity
    seating_capacity = models.PositiveIntegerField(default=30)
    students_allocated = models.PositiveIntegerField(default=0)
    # Staff
    invigilator = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    co_invigilator = models.ForeignKey(
        "auth_service.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="co_invigilated_exams"
    )
    # Setup
    seating_arrangement = models.CharField(max_length=50, blank=True, help_text="Rows, Clusters, Individual, etc.")
    equipment_needed = models.TextField(blank=True)
    special_instructions = models.TextField(blank=True)
    # Status
    is_ready = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exam_room_allocations"
        unique_together = [("exam_schedule", "room")]

    def __str__(self):
        return f"Room {self.room} - {self.exam_schedule} ({self.students_allocated}/{self.seating_capacity})"


# =============================================================================
# NEW MODELS: Seating Arrangement
# =============================================================================


class SeatingArrangement(models.Model):
    """Seating arrangements for exams."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_allocation = models.ForeignKey(
        ExamRoomAllocation, on_delete=models.CASCADE, related_name="seating_arrangements"
    )
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="exam_seatings")
    seat_number = models.CharField(max_length=10)
    row = models.PositiveIntegerField(default=0)
    column = models.PositiveIntegerField(default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "seating_arrangements"
        unique_together = [("room_allocation", "seat_number")]

    def __str__(self):
        return f"Seat {self.seat_number} - {self.student}"


# =============================================================================
# NEW MODELS: Exam Attendance
# =============================================================================


class ExamAttendance(models.Model):
    """Track student attendance for exams."""

    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        EXCUSED = "excused", "Excused"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam_entry = models.ForeignKey("ExamScheduleEntry", on_delete=models.CASCADE, related_name="attendances")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="exam_attendances")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    # Timing
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    minutes_late = models.PositiveIntegerField(default=0)
    # Seating
    seating = models.ForeignKey(SeatingArrangement, on_delete=models.SET_NULL, null=True, blank=True)
    # Notes
    invigilator_notes = models.TextField(blank=True)
    # Metadata
    recorded_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exam_attendances"
        unique_together = [("exam_entry", "student")]

    def __str__(self):
        return f"{self.student} - {self.exam_entry} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Academic Session Planning
# =============================================================================


class AcademicSession(models.Model):
    """Academic sessions/semesters."""

    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="academic_sessions")
    name = models.CharField(max_length=200, help_text="e.g., Fall 2026, Spring 2027")
    academic_year = models.CharField(max_length=10)
    semester = models.PositiveIntegerField(help_text="1, 2, 3, etc.")
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    # Enrollment
    enrollment_start = models.DateField(null=True, blank=True)
    enrollment_end = models.DateField(null=True, blank=True)
    # Exams
    exam_start_date = models.DateField(null=True, blank=True)
    exam_end_date = models.DateField(null=True, blank=True)
    results_date = models.DateField(null=True, blank=True)
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UPCOMING)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academic_sessions"
        ordering = ["-academic_year", "-semester"]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Substitute Schedule
# =============================================================================


class SubstituteSchedule(models.Model):
    """Detailed substitute teacher scheduling."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="substitute_schedules")
    substitute_teacher = models.ForeignKey(
        "auth_service.User", on_delete=models.CASCADE, related_name="substitute_schedules"
    )
    original_teacher = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="substituted_for")
    # Schedule
    date = models.DateField()
    timetable_slot = models.ForeignKey("TimetableSlot", on_delete=models.SET_NULL, null=True, blank=True)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=100, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    # Lesson plan
    lesson_plan = models.ForeignKey(LessonPlan, on_delete=models.SET_NULL, null=True, blank=True)
    instructions = models.TextField(blank=True)
    # Attendance
    class_covered = models.BooleanField(default=True)
    # Metadata
    assigned_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "substitute_schedules"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.substitute_teacher} for {self.original_teacher} ({self.date})"


# =============================================================================
# NEW MODELS: Room Utilization
# =============================================================================


class RoomUtilization(models.Model):
    """Track room usage and utilization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey("infrastructure.Room", on_delete=models.CASCADE, related_name="utilization_records")
    date = models.DateField()
    # Usage stats
    total_hours_available = models.DecimalField(max_digits=5, decimal_places=2, default=8)
    total_hours_used = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    utilization_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Breakdown
    teaching_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    exam_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    meeting_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    event_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Conflicts
    conflicts_detected = models.PositiveIntegerField(default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "room_utilization"
        unique_together = [("room", "date")]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.room} - {self.utilization_percentage}% ({self.date})"


# =============================================================================
# NEW MODELS: Timetable Validation
# =============================================================================


class TimetableValidationRule(models.Model):
    """Rules for validating timetable generation."""

    class RuleType(models.TextChoices):
        TEACHER_LOAD = "teacher_load", "Teacher Load Limit"
        ROOM_CAPACITY = "room_capacity", "Room Capacity"
        SUBJECT_SPACING = "spacing", "Subject Spacing"
        CONSECUTIVE = "consecutive", "Consecutive Period Limit"
        BREAK_REQUIRED = "break", "Break Required"
        GRADE_CONFLICT = "grade_conflict", "Grade Conflict"
        TEACHER_CONFLICT = "teacher_conflict", "Teacher Conflict"
        CUSTOM = "custom", "Custom Rule"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="timetable_validation_rules"
    )
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=20, choices=RuleType.choices)
    description = models.TextField(blank=True)
    # Rule parameters
    max_value = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum allowed value")
    min_value = models.PositiveIntegerField(null=True, blank=True, help_text="Minimum required value")
    parameters = models.JSONField(default=dict, blank=True)
    # Severity
    is_hard_constraint = models.BooleanField(default=True, help_text="Hard = cannot violate, Soft = warning only")
    priority = models.PositiveIntegerField(default=0)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "timetable_validation_rules"
        ordering = ["-priority"]

    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


class TimetableValidationError(models.Model):
    """Validation errors in generated timetables."""

    class Severity(models.TextChoices):
        ERROR = "error", "Error (Must Fix)"
        WARNING = "warning", "Warning"
        INFO = "info", "Info"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(TimetableValidationRule, on_delete=models.CASCADE, related_name="errors")
    timetable_slot = models.ForeignKey(
        "TimetableSlot", on_delete=models.SET_NULL, null=True, blank=True, related_name="validation_errors"
    )
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.ERROR)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "timetable_validation_errors"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_severity_display()}: {self.message[:80]}"


# =============================================================================
# NEW MODELS: Resource Booking
# =============================================================================


class TimetableResource(models.Model):
    """Resources that can be booked (projectors, labs, etc.)."""

    class ResourceType(models.TextChoices):
        PROJECTOR = "projector", "Projector"
        LAB = "lab", "Laboratory"
        COMPUTER = "computer", "Computer Lab"
        LIBRARY = "library", "Library Room"
        AUDITORIUM = "auditorium", "Auditorium"
        SPORTS = "sports", "Sports Facility"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="timetable_resources")
    name = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=15, choices=ResourceType.choices)
    room = models.ForeignKey(
        "infrastructure.Room", on_delete=models.SET_NULL, null=True, blank=True, related_name="timetable_resources"
    )
    # Capacity
    capacity = models.PositiveIntegerField(default=1)
    # Availability
    is_available = models.BooleanField(default=True)
    # Cost
    hourly_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "timetable_resources"

    def __str__(self):
        return f"{self.name} ({self.get_resource_type_display()})"


class TimetableResourceBooking(models.Model):
    """Resource booking records."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resource = models.ForeignKey(TimetableResource, on_delete=models.CASCADE, related_name="bookings")
    booked_by = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="resource_bookings")
    class_group = models.ForeignKey(ClassGroup, on_delete=models.SET_NULL, null=True, blank=True)
    # Schedule
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    # Purpose
    purpose = models.CharField(max_length=200, blank=True)
    event = models.ForeignKey(
        "SchoolEvent", on_delete=models.SET_NULL, null=True, blank=True, related_name="resource_bookings"
    )
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    # Cost
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "timetable_resource_bookings"
        ordering = ["-booking_date", "-start_time"]

    def __str__(self):
        return f"{self.resource} - {self.booked_by} ({self.booking_date})"


# =============================================================================
# NEW MODELS: Timetable Analytics
# =============================================================================


class TimetableAnalytics(models.Model):
    """Timetable generation analytics and metrics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="timetable_analytics")
    academic_year = models.CharField(max_length=10)
    semester = models.CharField(max_length=10, blank=True)
    generation_date = models.DateField()
    total_classes = models.PositiveIntegerField(default=0)
    total_slots = models.PositiveIntegerField(default=0)
    total_teachers = models.PositiveIntegerField(default=0)
    total_rooms = models.PositiveIntegerField(default=0)
    conflicts_found = models.PositiveIntegerField(default=0)
    conflicts_resolved = models.PositiveIntegerField(default=0)
    validation_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_teacher_load = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_teacher_load = models.PositiveIntegerField(default=0)
    avg_room_utilization = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    generation_time_seconds = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    generated_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "timetable_analytics"

    def __str__(self):
        return f"Analytics - {self.academic_year} ({self.generation_date})"


class TimetableChangeRequest(models.Model):
    """Requests for timetable changes."""

    class RequestType(models.TextChoices):
        SWAP = "swap", "Period Swap"
        ROOM_CHANGE = "room", "Room Change"
        TIME_CHANGE = "time", "Time Change"
        TEACHER_CHANGE = "teacher", "Teacher Change"
        CANCELLATION = "cancel", "Class Cancellation"
        EXTRA_CLASS = "extra", "Extra Class"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        IMPLEMENTED = "implemented", "Implemented"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="timetable_change_requests"
    )
    requested_by = models.ForeignKey(
        "auth_service.User", on_delete=models.CASCADE, related_name="timetable_change_requests"
    )
    request_type = models.CharField(max_length=10, choices=RequestType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    description = models.TextField()
    original_slot = models.ForeignKey(
        "TimetableSlot", on_delete=models.SET_NULL, null=True, blank=True, related_name="change_requests_from"
    )
    requested_slot = models.ForeignKey(
        "TimetableSlot", on_delete=models.SET_NULL, null=True, blank=True, related_name="change_requests_to"
    )
    approved_by = models.ForeignKey(
        "auth_service.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="timetable_change_approvals"
    )
    approval_notes = models.TextField(blank=True)
    implemented_at = models.DateTimeField(null=True, blank=True)
    is_urgent = models.BooleanField(default=False)
    effective_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "timetable_change_requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.get_status_display()}"


class DailySchedule(models.Model):
    """Daily schedule view for quick reference."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="daily_schedules")
    date = models.DateField()
    day_of_week = models.CharField(max_length=10)
    total_classes_scheduled = models.PositiveIntegerField(default=0)
    total_classes_conducted = models.PositiveIntegerField(default=0)
    total_classes_cancelled = models.PositiveIntegerField(default=0)
    total_substitutes = models.PositiveIntegerField(default=0)
    is_holiday = models.BooleanField(default=False)
    holiday_name = models.CharField(max_length=200, blank=True)
    is_special_schedule = models.BooleanField(default=False)
    special_schedule_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "daily_schedules"
        unique_together = [("school", "date")]
        ordering = ["-date"]

    def __str__(self):
        return f"Schedule - {self.date} ({self.day_of_week})"


class TeacherWorkload(models.Model):
    """Teacher workload tracking per week/semester."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="teacher_workloads")
    teacher = models.ForeignKey("auth_service.User", on_delete=models.CASCADE, related_name="teacher_workloads")
    academic_year = models.CharField(max_length=10)
    semester = models.CharField(max_length=10, blank=True)
    total_periods_per_week = models.PositiveIntegerField(default=0)
    total_classes = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    subjects_taught = models.JSONField(default=list, blank=True)
    classes_taught = models.JSONField(default=list, blank=True)
    max_periods_per_week = models.PositiveIntegerField(default=30)
    workload_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    duty_hours_per_week = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "teacher_workloads"
        unique_together = [("teacher", "academic_year", "semester")]

    def __str__(self):
        return f"{self.teacher} - {self.total_periods_per_week} periods ({self.workload_percentage}%)"


class ClassSchedule(models.Model):
    """Weekly class schedule for a specific class group."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE, related_name="class_schedules")
    academic_year = models.CharField(max_length=10)
    total_weekly_periods = models.PositiveIntegerField(default=0)
    subjects_scheduled = models.JSONField(default=list, blank=True)
    is_finalized = models.BooleanField(default=False)
    finalized_at = models.DateTimeField(null=True, blank=True)
    finalized_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "class_schedules"
        unique_together = [("class_group", "academic_year")]

    def __str__(self):
        return f"Schedule - {self.class_group} ({self.academic_year})"


class TimetableVersion(models.Model):
    """Version control for timetables."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="timetable_versions")
    academic_year = models.CharField(max_length=10)
    semester = models.CharField(max_length=10, blank=True)
    version_number = models.PositiveIntegerField(default=1)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # Snapshot
    timetable_data = models.JSONField(default=dict, help_text="Full timetable snapshot as JSON")
    # Status
    is_current = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    # Changes
    changes_from_previous = models.TextField(blank=True)
    # Metadata
    created_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "timetable_versions"
        ordering = ["-version_number"]

    def __str__(self):
        return f"{self.academic_year} v{self.version_number} ({'Current' if self.is_current else 'Draft'})"
