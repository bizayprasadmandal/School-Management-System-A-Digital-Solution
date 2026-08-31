"""
Academics Service — Subjects, curriculum, teacher assignments, student-subject enrollment,
curriculum standards mapping.
"""

import uuid

from django.db import models
from services.auth.models import School, User
from services.students.models import AcademicYear, Classroom, Grade, Student


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
    bio = models.TextField(blank=True, help_text="Professional bio / biography")
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


class StudentSubjectEnrollment(models.Model):
    """Tracks which students are enrolled in which subjects per academic year.

    This is independent of classroom enrollment — a student may take subjects
    from different streams or have elective choices that differ from their
    classroom peers.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DROPPED = "dropped", "Dropped"
        TRANSFERRED = "transferred", "Transferred"
        COMPLETED = "completed", "Completed"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="subject_enrollments")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="student_enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="subject_enrollments")
    enrolled_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_subject_enrollments"
        unique_together = [("student", "subject", "academic_year")]
        indexes = [
            models.Index(fields=["student", "academic_year"]),
            models.Index(fields=["subject", "academic_year"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["-enrolled_date"]

    def __str__(self):
        return f"{self.student} → {self.subject} ({self.academic_year})"

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE


class CurriculumStandard(models.Model):
    """A curriculum standard (e.g., Common Core, NGSS, CBSE, NCERT).

    Schools import or define the standards framework they follow,
    then map individual standards to subjects for tracking and
    accreditation reporting.
    """

    class Framework(models.TextChoices):
        COMMON_CORE = "common_core", "Common Core State Standards"
        NGSS = "ngss", "Next Generation Science Standards"
        CBSE = "cbse", "CBSE Curriculum"
        NCERT = "ncert", "NCERT Curriculum"
        NATIONAL_UK = "national_uk", "National Curriculum (UK)"
        IB = "ib", "International Baccalaureate"
        CUSTOM = "custom", "Custom / School-Defined"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="curriculum_standards")
    framework = models.CharField(max_length=20, choices=Framework.choices, default=Framework.CUSTOM)
    code = models.CharField(
        max_length=50,
        help_text="Unique standard code, e.g. CCSS.MATH.8.EE.1",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    grade = models.ForeignKey(
        Grade, on_delete=models.CASCADE, related_name="curriculum_standards", null=True, blank=True
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="curriculum_standards", null=True, blank=True
    )
    domain = models.CharField(
        max_length=100,
        blank=True,
        help_text="High-level domain, e.g. Algebra, Geometry, Life Science",
    )
    cluster = models.CharField(
        max_length=100,
        blank=True,
        help_text="Sub-domain cluster within the domain",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "curriculum_standards"
        unique_together = [("school", "code")]
        ordering = ["grade", "code"]
        indexes = [
            models.Index(fields=["school", "framework"]),
            models.Index(fields=["school", "grade"]),
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"


class SubjectStandardMapping(models.Model):
    """Maps a subject to one or more curriculum standards.

    Tracks which standards a subject covers and to what extent,
    useful for accreditation and curriculum review.
    """

    class CoverageLevel(models.TextChoices):
        FULL = "full", "Fully Covered"
        PARTIAL = "partial", "Partially Covered"
        INTRODUCED = "introduced", "Introduced"
        NOT_COVERED = "not_covered", "Not Covered"

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="standard_mappings")
    standard = models.ForeignKey(CurriculumStandard, on_delete=models.CASCADE, related_name="subject_mappings")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="standard_mappings")
    coverage_level = models.CharField(max_length=15, choices=CoverageLevel.choices, default=CoverageLevel.PARTIAL)
    notes = models.TextField(blank=True)
    mapped_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="standard_mappings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subject_standard_mappings"
        unique_together = [("subject", "standard", "academic_year")]
        ordering = ["subject", "standard__code"]
        indexes = [
            models.Index(fields=["subject", "academic_year"]),
            models.Index(fields=["standard", "academic_year"]),
        ]

    def __str__(self):
        return f"{self.subject} ↔ {self.standard.code} ({self.get_coverage_level_display()})"
