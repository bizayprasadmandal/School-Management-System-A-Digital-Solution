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
