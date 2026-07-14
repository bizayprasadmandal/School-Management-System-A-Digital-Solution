import uuid
from django.db import models
from services.auth.models import User, School
from services.students.models import Student


class ConferenceSlot(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="conference_slots")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conference_slots")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="conference_slots", null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    booked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="booked_slots")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conference_slots"
        ordering = ["date", "start_time"]
        unique_together = [("teacher", "date", "start_time")]

    def __str__(self):
        return f"{self.teacher.full_name} - {self.date} {self.start_time}-{self.end_time}"
