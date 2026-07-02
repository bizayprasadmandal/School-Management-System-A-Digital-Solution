"""
Gradebook Service — Exams, assessments, grades, report cards
"""

import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from services.auth.models import User, School
from services.students.models import Student, Classroom, AcademicYear
from services.academics.models import Subject, TeacherAssignment


class GradingScale(models.Model):
    """Configurable grading scale per school."""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="grading_scales")
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "grading_scales"


class GradingScaleEntry(models.Model):
    scale = models.ForeignKey(GradingScale, on_delete=models.CASCADE, related_name="entries")
    grade_letter = models.CharField(max_length=5)    # A+, A, B, etc.
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=1)  # GPA points
    description = models.CharField(max_length=50)    # Excellent, Good, etc.

    class Meta:
        db_table = "grading_scale_entries"
        ordering = ["-min_percentage"]


class ExamType(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="exam_types")
    name = models.CharField(max_length=100)          # Midterm, Final, Quiz, Assignment
    weightage = models.DecimalField(max_digits=5, decimal_places=2)  # % of total
    is_terminal = models.BooleanField(default=False)

    class Meta:
        db_table = "exam_types"


class Exam(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="exams")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exams"


class ExamSchedule(models.Model):
    """Date/time for a specific subject exam."""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="schedules")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100, blank=True)
    invigilator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="invigilated_exams"
    )
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    passing_marks = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = "exam_schedules"
        unique_together = [("exam", "subject", "classroom")]


class Grade(models.Model):
    """Individual student grade for a specific exam-subject."""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grades")
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="grades")
    marks_obtained = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    is_absent = models.BooleanField(default=False)
    remarks = models.CharField(max_length=255, blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exam_grades"
        unique_together = [("student", "exam_schedule")]

    @property
    def percentage(self):
        if self.marks_obtained is None or self.is_absent:
            return None
        max_marks = self.exam_schedule.max_marks
        if max_marks == 0:
            return Decimal("0")
        return (self.marks_obtained / max_marks) * 100

    @property
    def is_pass(self):
        if self.marks_obtained is None or self.is_absent:
            return False
        return self.marks_obtained >= self.exam_schedule.passing_marks


class Assessment(models.Model):
    """Continuous assessment — homework, quizzes, projects."""

    class AssessmentType(models.TextChoices):
        HOMEWORK = "homework", "Homework"
        QUIZ = "quiz", "Quiz"
        PROJECT = "project", "Project"
        CLASSWORK = "classwork", "Class Work"
        LAB = "lab", "Lab Work"

    assignment = models.ForeignKey(TeacherAssignment, on_delete=models.CASCADE, related_name="assessments")
    title = models.CharField(max_length=255)
    assessment_type = models.CharField(max_length=20, choices=AssessmentType.choices)
    due_date = models.DateField()
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    attachment = models.FileField(upload_to="assessments/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "assessments"


class AssessmentSubmission(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="assessment_submissions")
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    file = models.FileField(upload_to="submissions/", null=True, blank=True)
    remarks = models.TextField(blank=True)
    is_late = models.BooleanField(default=False)

    class Meta:
        db_table = "assessment_submissions"
        unique_together = [("assessment", "student")]


class ReportCard(models.Model):
    """Generated report card per student per exam."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        SENT = "sent", "Sent to Parents"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="report_cards")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="report_cards")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    obtained_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade_letter = models.CharField(max_length=5, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    rank_in_class = models.PositiveSmallIntegerField(null=True, blank=True)
    rank_in_grade = models.PositiveSmallIntegerField(null=True, blank=True)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_remarks = models.TextField(blank=True)
    principal_remarks = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    pdf_file = models.FileField(upload_to="report_cards/%Y/%m/", null=True, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "report_cards"
        unique_together = [("student", "exam")]
