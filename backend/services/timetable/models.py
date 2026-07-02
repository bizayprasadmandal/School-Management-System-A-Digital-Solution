"""
Timetable Service — Period scheduling, room bookings, school events
"""

from django.db import models
from services.auth.models import User, School
from services.students.models import Classroom, AcademicYear
from services.academics.models import Subject, TeacherAssignment


class Period(models.Model):
    """Master period definition (e.g. Period 1: 08:00-08:45)."""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="periods")
    name = models.CharField(max_length=50)          # "Period 1", "Lunch", "Break"
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
        (0, "Monday"), (1, "Tuesday"), (2, "Wednesday"),
        (3, "Thursday"), (4, "Friday"), (5, "Saturday"),
    ]

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="timetable_slots")
    assignment = models.ForeignKey(
        TeacherAssignment, on_delete=models.CASCADE, related_name="timetable_slots"
    )
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
