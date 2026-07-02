"""
Academics Service — Subjects, curriculum, teacher assignments
"""

import uuid
from django.db import models
from services.auth.models import User, School
from services.students.models import Grade, Classroom, AcademicYear


class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="subjects")
    is_core = models.BooleanField(default=True)
    is_elective = models.BooleanField(default=False)
    max_marks = models.PositiveSmallIntegerField(default=100)
    pass_marks = models.PositiveSmallIntegerField(default=35)
    credit_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "subjects"
        unique_together = [("school", "code", "grade")]

    def __str__(self):
        return f"{self.name} ({self.code}) — Grade {self.grade.name}"


class TeacherAssignment(models.Model):
    """Maps a teacher to a subject-classroom combination."""
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignments")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="assignments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=True)

    class Meta:
        db_table = "teacher_assignments"
        unique_together = [("teacher", "subject", "classroom", "academic_year")]

    def __str__(self):
        return f"{self.teacher.full_name} → {self.subject.name} @ {self.classroom}"


class TeacherProfile(models.Model):
    """Extended teacher information."""

    class QualificationLevel(models.TextChoices):
        DIPLOMA = "diploma", "Diploma"
        BACHELOR = "bachelor", "Bachelor's Degree"
        MASTER = "master", "Master's Degree"
        PHD = "phd", "PhD"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="teachers")
    employee_id = models.CharField(max_length=30, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female"), ("O", "Other")])
    qualification = models.CharField(max_length=20, choices=QualificationLevel.choices)
    specialization = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField()
    experience_years = models.PositiveSmallIntegerField(default=0)
    department = models.CharField(max_length=100, blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    address = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "teacher_profiles"

    def __str__(self):
        return f"{self.user.full_name} ({self.employee_id})"


class LessonPlan(models.Model):
    assignment = models.ForeignKey(TeacherAssignment, on_delete=models.CASCADE, related_name="lesson_plans")
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    objectives = models.TextField()
    content = models.TextField()
    resources = models.TextField(blank=True)
    date = models.DateField()
    duration_minutes = models.PositiveSmallIntegerField(default=45)
    status = models.CharField(
        max_length=20,
        choices=[("draft", "Draft"), ("approved", "Approved"), ("completed", "Completed")],
        default="draft",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lesson_plans"

    def __str__(self):
        return f"{self.title} — {self.date}"
