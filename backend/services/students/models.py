"""
Student Service — Core student information management models
"""

import uuid
from django.db import models
from services.auth.models import User, School


class AcademicYear(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_years")
    name = models.CharField(max_length=20)          # e.g. "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        db_table = "academic_years"
        unique_together = [("school", "name")]

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(school=self.school, is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.school.code} — {self.name}"


class Grade(models.Model):
    """Grade / Year level (e.g. Grade 1, Form 3, Year 10)."""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="grades")
    name = models.CharField(max_length=50)
    level = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        db_table = "grades"
        ordering = ["level"]
        unique_together = [("school", "level")]

    def __str__(self):
        return f"{self.school.code} — {self.name}"


class Classroom(models.Model):
    """A section/stream within a grade."""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="classrooms")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="classrooms")
    name = models.CharField(max_length=20)           # e.g. "3A", "3B"
    capacity = models.PositiveSmallIntegerField(default=40)
    room_number = models.CharField(max_length=20, blank=True)
    class_teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="homeroom_class"
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    class Meta:
        db_table = "classrooms"
        unique_together = [("grade", "name", "academic_year")]

    def __str__(self):
        return f"{self.grade.name} {self.name}"

    @property
    def student_count(self):
        return self.enrollments.filter(is_active=True).count()


class Student(models.Model):
    """Core student profile — immutable personal record."""

    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    class BloodGroup(models.TextChoices):
        A_POS = "A+", "A+"
        A_NEG = "A-", "A-"
        B_POS = "B+", "B+"
        B_NEG = "B-", "B-"
        AB_POS = "AB+", "AB+"
        AB_NEG = "AB-", "AB-"
        O_POS = "O+", "O+"
        O_NEG = "O-", "O-"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="students")
    admission_number = models.CharField(max_length=30, unique=True, db_index=True)
    roll_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=Gender.choices)
    blood_group = models.CharField(max_length=3, choices=BloodGroup.choices, blank=True)
    nationality = models.CharField(max_length=50, default="")
    religion = models.CharField(max_length=50, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="")
    postal_code = models.CharField(max_length=20, blank=True)
    admission_date = models.DateField()
    photo = models.ImageField(upload_to="students/photos/", null=True, blank=True)
    medical_conditions = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    previous_school = models.CharField(max_length=255, blank=True)
    transfer_certificate = models.FileField(upload_to="students/documents/", null=True, blank=True)
    bio = models.TextField(blank=True, help_text="Short personal biography")
    interests = models.TextField(blank=True, help_text="Hobbies, extracurricular interests")
    learning_goals = models.TextField(blank=True, help_text="Academic goals and aspirations")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "students"
        indexes = [
            models.Index(fields=["school", "is_active"]),
            models.Index(fields=["admission_number"]),
        ]

    def __str__(self):
        return f"{self.user.full_name} ({self.admission_number})"

    @property
    def age(self):
        from django.utils import timezone
        today = timezone.now().date()
        return (today - self.date_of_birth).days // 365


class Guardian(models.Model):
    """Parent/guardian linked to one or more students."""

    class Relationship(models.TextChoices):
        FATHER = "father", "Father"
        MOTHER = "mother", "Mother"
        GUARDIAN = "guardian", "Legal Guardian"
        SIBLING = "sibling", "Sibling"
        OTHER = "other", "Other"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="guardian_profile", null=True, blank=True)
    students = models.ManyToManyField(Student, through="StudentGuardian", related_name="guardians")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "guardians"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class StudentGuardian(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    guardian = models.ForeignKey(Guardian, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=20, choices=Guardian.Relationship.choices)
    is_primary_contact = models.BooleanField(default=False)
    has_pickup_permission = models.BooleanField(default=True)
    portal_access = models.BooleanField(default=True)

    class Meta:
        db_table = "student_guardians"
        unique_together = [("student", "guardian")]


class Enrollment(models.Model):
    """Tracks student-classroom assignments per academic year."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        TRANSFERRED = "transferred", "Transferred"
        GRADUATED = "graduated", "Graduated"
        WITHDRAWN = "withdrawn", "Withdrawn"
        SUSPENDED = "suspended", "Suspended"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    enrollment_date = models.DateField(auto_now_add=True)
    promoted_from = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="promoted_to"
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "enrollments"
        unique_together = [("student", "academic_year")]
        indexes = [models.Index(fields=["classroom", "is_active"])]

    def __str__(self):
        return f"{self.student} → {self.classroom} ({self.academic_year})"


class Document(models.Model):
    """Student document vault — certificates, ID cards, etc."""

    class DocumentType(models.TextChoices):
        BIRTH_CERT = "birth_cert", "Birth Certificate"
        ID_CARD = "id_card", "National ID"
        TRANSFER_CERT = "transfer_cert", "Transfer Certificate"
        MEDICAL = "medical", "Medical Record"
        REPORT_CARD = "report_card", "Report Card"
        OTHER = "other", "Other"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="students/documents/%Y/%m/")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "student_documents"
