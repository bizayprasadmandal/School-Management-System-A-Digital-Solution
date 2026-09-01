"""
Student Service — Core student information management models
"""

import uuid

from django.db import models, transaction
from services.auth.models import School, User


class AcademicYear(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_years")
    name = models.CharField(max_length=20)  # e.g. "2024-2025"
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        db_table = "academic_years"
        unique_together = [("school", "name")]

    def save(self, *args, **kwargs):
        if self.is_current:
            # Demote the previously current year(s) inside a lock so two
            # concurrent saves cannot interleave and leave multiple years
            # marked current.
            with transaction.atomic():
                locked = list(
                    AcademicYear.objects.select_for_update()
                    .filter(school=self.school, is_current=True)
                    .exclude(pk=self.pk)
                    .values_list("pk", flat=True)
                )
                if locked:
                    AcademicYear.objects.filter(pk__in=locked).update(is_current=False)
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
    name = models.CharField(max_length=20)  # e.g. "3A", "3B"
    capacity = models.PositiveSmallIntegerField(default=40)
    room_number = models.CharField(max_length=20, blank=True)
    class_teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="homeroom_class")
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

    def __str__(self):
        return f"{self.student} ← {self.guardian.full_name} ({self.relationship})"


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


class ParentProfile(models.Model):
    """Extended parent profile — self-service fields for parent/guardian users."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="parent_profile")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="parent_profiles")
    occupation = models.CharField(max_length=100, blank=True, help_text="Current occupation")
    alternate_phone = models.CharField(max_length=20, blank=True, help_text="Alternate contact number")
    address = models.TextField(blank=True, help_text="Residential address")
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True, help_text="Short personal biography")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "parent_profiles"
        verbose_name = "Parent Profile"
        verbose_name_plural = "Parent Profiles"

    def __str__(self):
        return f"{self.user.full_name} — Parent Profile"


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

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"


class StudentContact(models.Model):
    """Extended contact information for students."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="contact_info")
    # Contact details
    personal_phone = models.CharField(max_length=20, blank=True)
    personal_email = models.EmailField(blank=True)
    # Emergency contacts
    emergency_contact_1_name = models.CharField(max_length=150, blank=True)
    emergency_contact_1_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_1_relationship = models.CharField(max_length=50, blank=True)
    emergency_contact_2_name = models.CharField(max_length=150, blank=True)
    emergency_contact_2_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_2_relationship = models.CharField(max_length=50, blank=True)
    # Medical emergency
    medical_emergency_contact = models.CharField(max_length=150, blank=True)
    medical_emergency_phone = models.CharField(max_length=20, blank=True)
    # Doctor info
    doctor_name = models.CharField(max_length=150, blank=True)
    doctor_phone = models.CharField(max_length=20, blank=True)
    # Insurance
    insurance_provider = models.CharField(max_length=150, blank=True)
    insurance_policy_number = models.CharField(max_length=50, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_contacts"

    def __str__(self):
        return f"Contact Info — {self.student}"


class StudentMedicalRecord(models.Model):
    """Medical history and conditions for students."""

    class RecordType(models.TextChoices):
        ALLERGY = "allergy", "Allergy"
        CONDITION = "condition", "Medical Condition"
        MEDICATION = "medication", "Medication"
        IMMUNIZATION = "immunization", "Immunization"
        VISIT = "visit", "Medical Visit"
        OTHER = "other", "Other"

    class Severity(models.TextChoices):
        MILD = "mild", "Mild"
        MODERATE = "moderate", "Moderate"
        SEVERE = "severe", "Severe"
        LIFE_THREATENING = "life_threatening", "Life-Threatening"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="medical_records")
    # Record details
    record_type = models.CharField(max_length=15, choices=RecordType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=Severity.choices, blank=True)
    # Dates
    date_recorded = models.DateField(auto_now_add=True)
    date_of_visit = models.DateField(null=True, blank=True)
    # Doctor info
    doctor_name = models.CharField(max_length=150, blank=True)
    hospital_name = models.CharField(max_length=200, blank=True)
    # Treatment
    treatment_notes = models.TextField(blank=True)
    medication_details = models.TextField(blank=True)
    # Documents
    document_url = models.URLField(blank=True)
    # Status
    is_ongoing = models.BooleanField(default=False)
    resolved_date = models.DateField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_medical_records"
        ordering = ["-date_recorded"]

    def __str__(self):
        return f"{self.student} — {self.get_record_type_display()}: {self.title}"


class StudentCustomField(models.Model):
    """Flexible student attributes for custom data."""

    class FieldType(models.TextChoices):
        TEXT = "text", "Text"
        NUMBER = "number", "Number"
        DATE = "date", "Date"
        BOOLEAN = "boolean", "Yes/No"
        SELECT = "select", "Dropdown"
        MULTI_SELECT = "multi_select", "Multi-Select"
        URL = "url", "URL"
        EMAIL = "email", "Email"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_custom_fields")
    # Field definition
    name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=15, choices=FieldType.choices)
    description = models.TextField(blank=True)
    # Options for select fields
    options = models.JSONField(default=list, blank=True, help_text="Options for select/multi-select fields")
    # Settings
    is_required = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)
    # Status
    is_active = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_custom_fields"
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_field_type_display()})"


class StudentCustomFieldValue(models.Model):
    """Values for custom fields per student."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="custom_field_values")
    field = models.ForeignKey(StudentCustomField, on_delete=models.CASCADE, related_name="values")
    # Value storage
    text_value = models.TextField(blank=True)
    number_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    date_value = models.DateField(null=True, blank=True)
    boolean_value = models.BooleanField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_custom_field_values"
        unique_together = [("student", "field")]

    def __str__(self):
        return f"{self.student} — {self.field.name}"


class StudentPhoto(models.Model):
    """Multiple photos over time for students."""

    class PhotoType(models.TextChoices):
        PROFILE = "profile", "Profile Photo"
        ID_PHOTO = "id_photo", "ID Card Photo"
        CLASS_PHOTO = "class_photo", "Class Photo"
        EVENT = "event", "Event Photo"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="photos")
    # Photo details
    photo_type = models.CharField(max_length=15, choices=PhotoType.choices, default=PhotoType.PROFILE)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # File
    photo_url = models.URLField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    # Metadata
    taken_date = models.DateField(auto_now_add=True)
    photographer = models.CharField(max_length=150, blank=True)
    # Settings
    is_primary = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_photos"
        ordering = ["-taken_date"]

    def __str__(self):
        return f"{self.student} — {self.get_photo_type_display()}"


class StudentIDCard(models.Model):
    """ID card generation and management."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        LOST = "lost", "Lost"
        REPLACED = "replaced", "Replaced"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="id_cards")
    # Card details
    card_number = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=100, blank=True)
    rfid_number = models.CharField(max_length=50, blank=True)
    # Validity
    issue_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Photo
    photo_url = models.URLField(blank=True)
    # Access
    access_level = models.CharField(max_length=20, blank=True, help_text="e.g. Library, Cafeteria, Building")
    # Notes
    notes = models.TextField(blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_id_cards"
        ordering = ["-issue_date"]

    def __str__(self):
        return f"ID Card — {self.student} ({self.card_number})"

    @property
    def is_valid(self):
        from django.utils import timezone

        if self.status != self.Status.ACTIVE:
            return False
        if self.expiry_date:
            return self.expiry_date >= timezone.now().date()
        return True


class StudentStatusHistory(models.Model):
    """Track student status changes over time."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        GRADUATED = "graduated", "Graduated"
        WITHDRAWN = "withdrawn", "Withdrawn"
        SUSPENDED = "suspended", "Suspended"
        TRANSFERRED = "transferred", "Transferred"
        EXPULLED = "expelled", "Expelled"
        DECEASED = "deceased", "Deceased"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="status_history")
    # Status change
    status = models.CharField(max_length=15, choices=Status.choices)
    previous_status = models.CharField(max_length=15, choices=Status.choices, blank=True)
    # Dates
    effective_date = models.DateField()
    # Reason
    reason = models.TextField(blank=True)
    # Documentation
    document_url = models.URLField(blank=True)
    # Approved by
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_status_history"
        ordering = ["-effective_date"]

    def __str__(self):
        return f"{self.student} — {self.get_status_display()} ({self.effective_date})"


class SiblingTracking(models.Model):
    """Link siblings together."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="siblings")
    sibling = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="related_siblings")
    # Relationship
    relationship = models.CharField(
        max_length=20,
        choices=[("sibling", "Sibling"), ("twin", "Twin"), ("step_sibling", "Step-Sibling")],
        default="sibling",
    )
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_siblings"
        unique_together = [("student", "sibling")]

    def __str__(self):
        return f"{self.student} — {self.sibling} ({self.relationship})"


class StudentCategory(models.Model):
    """Custom student groups (honors, at-risk, etc.)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_categories")
    # Category info
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, blank=True, help_text="Hex color code")
    # Settings
    is_active = models.BooleanField(default=True)
    # Stats
    student_count = models.PositiveIntegerField(default=0)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class StudentCategoryMembership(models.Model):
    """Link students to categories."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="category_memberships")
    category = models.ForeignKey(StudentCategory, on_delete=models.CASCADE, related_name="members")
    # Dates
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_category_memberships"
        unique_together = [("student", "category")]

    def __str__(self):
        return f"{self.student} — {self.category}"


class StudentTag(models.Model):
    """Flexible labeling system for students."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_tags")
    # Tag info
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, blank=True)
    # Stats
    usage_count = models.PositiveIntegerField(default=0)
    # Status
    is_active = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_tags"
        ordering = ["name"]

    def __str__(self):
        return self.name


class StudentTagAssignment(models.Model):
    """Assign tags to students."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="tag_assignments")
    tag = models.ForeignKey(StudentTag, on_delete=models.CASCADE, related_name="assignments")
    # Assigned by
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_tag_assignments"
        unique_together = [("student", "tag")]

    def __str__(self):
        return f"{self.student} — {self.tag}"


class StudentNote(models.Model):
    """Internal notes about students."""

    class NoteType(models.TextChoices):
        GENERAL = "general", "General"
        ACADEMIC = "academic", "Academic"
        BEHAVIOR = "behavior", "Behavior"
        MEDICAL = "medical", "Medical"
        PASTORAL = "pastoral", "Pastoral"
        CONFIDENTIAL = "confidential", "Confidential"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_notes")
    # Note details
    note_type = models.CharField(max_length=15, choices=NoteType.choices, default=NoteType.GENERAL)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    # Author
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="student_notes")
    # Settings
    is_confidential = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_notes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} — {self.get_note_type_display()}"


class StudentArchive(models.Model):
    """Historical student records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="archive")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_archives")
    # Academic info
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True)
    # Status
    status = models.CharField(
        max_length=15,
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("graduated", "Graduated"),
            ("withdrawn", "Withdrawn"),
            ("suspended", "Suspended"),
            ("transferred", "Transferred"),
        ],
    )
    # Performance
    final_grade = models.CharField(max_length=10, blank=True)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    rank_in_class = models.PositiveSmallIntegerField(null=True, blank=True)
    # Attendance
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Achievements
    achievements = models.JSONField(default=list, blank=True)
    # Documents
    report_card_url = models.URLField(blank=True)
    transcript_url = models.URLField(blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_archives"
        unique_together = [("student", "academic_year")]
        ordering = ["-academic_year"]

    def __str__(self):
        return f"{self.student} — {self.academic_year}"


class StudentSocialMedia(models.Model):
    """Social media profiles for students."""

    class Platform(models.TextChoices):
        FACEBOOK = "facebook", "Facebook"
        TWITTER = "twitter", "Twitter/X"
        INSTAGRAM = "instagram", "Instagram"
        LINKEDIN = "linkedin", "LinkedIn"
        YOUTUBE = "youtube", "YouTube"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="social_media")
    # Platform info
    platform = models.CharField(max_length=15, choices=Platform.choices)
    username = models.CharField(max_length=100, blank=True)
    profile_url = models.URLField(blank=True)
    # Status
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_social_media"
        unique_together = [("student", "platform")]

    def __str__(self):
        return f"{self.student} — {self.get_platform_display()}"


class StudentPortfolio(models.Model):
    """Work samples and achievements."""

    class PortfolioType(models.TextChoices):
        ACADEMIC = "academic", "Academic Work"
        CREATIVE = "creative", "Creative Work"
        PROJECT = "project", "Project"
        PRESENTATION = "presentation", "Presentation"
        CERTIFICATE = "certificate", "Certificate"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="portfolio")
    # Portfolio details
    portfolio_type = models.CharField(max_length=15, choices=PortfolioType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # File
    file_url = models.URLField(blank=True)
    thumbnail_url = models.URLField(blank=True)
    # Metadata
    subject = models.CharField(max_length=100, blank=True)
    date_completed = models.DateField(auto_now_add=True)
    grade_received = models.CharField(max_length=10, blank=True)
    # Settings
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_portfolio"
        ordering = ["-date_completed"]

    def __str__(self):
        return f"{self.student} — {self.title}"


class StudentWellness(models.Model):
    """Mental health tracking for students."""

    class WellnessType(models.TextChoices):
        CHECK_IN = "check_in", "Wellness Check-In"
        ASSESSMENT = "assessment", "Assessment"
        COUNSELING = "counseling", "Counseling Session"
        INCIDENT = "incident", "Incident Report"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        NORMAL = "normal", "Normal"
        ATTENTION = "attention", "Needs Attention"
        CONCERN = "concern", "Concerning"
        URGENT = "urgent", "Urgent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="wellness_records")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_wellness")
    # Wellness details
    wellness_type = models.CharField(max_length=15, choices=WellnessType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NORMAL)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # Mood/score
    mood_score = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-10 scale")
    stress_level = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-10 scale")
    # Counselor
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    # Confidential
    is_confidential = models.BooleanField(default=True)
    # Documents
    document_url = models.URLField(blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_wellness"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} — {self.get_wellness_type_display()} ({self.get_status_display()})"


class StudentLearningStyle(models.Model):
    """Learning style assessment for students."""

    class StyleType(models.TextChoices):
        VISUAL = "visual", "Visual"
        AUDITORY = "auditory", "Auditory"
        KINESTHETIC = "kinesthetic", "Kinesthetic"
        READING = "reading", "Reading/Writing"
        MULTIMODAL = "multimodal", "Multimodal"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="learning_styles")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_learning_styles")
    primary_style = models.CharField(max_length=20, choices=StyleType.choices)
    secondary_style = models.CharField(max_length=20, choices=StyleType.choices, blank=True)
    assessment_tool = models.CharField(max_length=100, blank=True)
    score_visual = models.PositiveSmallIntegerField(default=0)
    score_auditory = models.PositiveSmallIntegerField(default=0)
    score_kinesthetic = models.PositiveSmallIntegerField(default=0)
    score_reading = models.PositiveSmallIntegerField(default=0)
    recommendations = models.TextField(blank=True)
    assessed_date = models.DateField()
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_learning_styles"
        ordering = ["-assessed_date"]

    def __str__(self):
        return f"{self.student} - {self.get_primary_style_display()}"


class StudentAchievement(models.Model):
    """Academic achievements and honors."""

    class AchievementType(models.TextChoices):
        ACADEMIC = "academic", "Academic Honor"
        SPORTS = "sports", "Sports Achievement"
        ARTS = "arts", "Arts Achievement"
        LEADERSHIP = "leadership", "Leadership"
        SERVICE = "service", "Community Service"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="achievements")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_achievements")
    achievement_type = models.CharField(max_length=20, choices=AchievementType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_earned = models.DateField()
    awarded_by = models.CharField(max_length=200, blank=True)
    certificate_url = models.URLField(max_length=500, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_achievements"
        ordering = ["-date_earned"]

    def __str__(self):
        return f"{self.student} - {self.title}"


class StudentClub(models.Model):
    """Student club membership."""

    class Role(models.TextChoices):
        MEMBER = "member", "Member"
        PRESIDENT = "president", "President"
        VICE_PRESIDENT = "vice_president", "Vice President"
        SECRETARY = "secretary", "Secretary"
        TREASURER = "treasurer", "Treasurer"
        ADVISOR = "advisor", "Faculty Advisor"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="club_memberships")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_club_memberships")
    club_name = models.CharField(max_length=200)
    club_type = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    join_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    advisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_club_memberships"
        ordering = ["-join_date"]

    def __str__(self):
        return f"{self.student} - {self.club_name} ({self.get_role_display()})"


class StudentActivity(models.Model):
    """Extracurricular activities."""

    class ActivityType(models.TextChoices):
        SPORTS = "sports", "Sports"
        ARTS = "arts", "Arts"
        MUSIC = "music", "Music"
        DRAMA = "drama", "Drama"
        DEBATE = "debate", "Debate"
        SCIENCE = "science", "Science Club"
        CODING = "coding", "Coding Club"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="activities")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_activities")
    activity_name = models.CharField(max_length=200)
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    hours_per_week = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_activities"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.student} - {self.activity_name}"


class StudentAward(models.Model):
    """Awards and honors."""

    class AwardLevel(models.TextChoices):
        CLASSROOM = "classroom", "Classroom"
        SCHOOL = "school", "School"
        DISTRICT = "district", "District"
        STATE = "state", "State"
        NATIONAL = "national", "National"
        INTERNATIONAL = "international", "International"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="awards")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_awards")
    award_name = models.CharField(max_length=200)
    award_level = models.CharField(max_length=20, choices=AwardLevel.choices, default=AwardLevel.SCHOOL)
    category = models.CharField(max_length=100, blank=True)
    date_awarded = models.DateField()
    awarded_by = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    certificate_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_awards"
        ordering = ["-date_awarded"]

    def __str__(self):
        return f"{self.student} - {self.award_name}"


class StudentDiscipline(models.Model):
    """Discipline records."""

    class ActionType(models.TextChoices):
        WARNING = "warning", "Warning"
        DETENTION = "detention", "Detention"
        SUSPENSION = "suspension", "Suspension"
        EXPULSION = "expulsion", "Expulsion"
        COUNSELING = "counseling", "Counseling"
        COMMUNITY_SERVICE = "community_service", "Community Service"
        OTHER = "other", "Other"

    class Severity(models.TextChoices):
        MINOR = "minor", "Minor"
        MODERATE = "moderate", "Moderate"
        MAJOR = "major", "Major"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="discipline_records")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_discipline")
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MINOR)
    incident_date = models.DateField()
    description = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    witnesses = models.TextField(blank=True)
    action_taken = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    parent_notified = models.BooleanField(default=False)
    parent_notified_date = models.DateField(null=True, blank=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_discipline"
        ordering = ["-incident_date"]

    def __str__(self):
        return f"{self.student} - {self.get_action_type_display()} ({self.incident_date})"


class StudentTutoring(models.Model):
    """Tutoring sessions."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="tutoring_sessions")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_tutoring")
    subject = models.ForeignKey("academics.Subject", on_delete=models.SET_NULL, null=True, blank=True)
    tutor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tutoring_sessions")
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    topics_covered = models.TextField(blank=True)
    homework_assigned = models.TextField(blank=True)
    progress_notes = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-5 rating")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_tutoring"
        ordering = ["-session_date"]

    def __str__(self):
        return f"{self.student} - Tutoring ({self.session_date})"


class StudentMentor(models.Model):
    """Mentorship programs."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        PAUSED = "paused", "Paused"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="mentorships")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_mentorships")
    mentor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    program_name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    goals = models.TextField(blank=True)
    meeting_frequency = models.CharField(max_length=50, blank=True)
    progress_notes = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_mentorships"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.student} - {self.program_name}"


class StudentCareerGuidance(models.Model):
    """Career counseling records."""

    class InterestType(models.TextChoices):
        STEM = "stem", "STEM"
        BUSINESS = "business", "Business"
        ARTS = "arts", "Arts & Humanities"
        HEALTHCARE = "healthcare", "Healthcare"
        EDUCATION = "education", "Education"
        LAW = "law", "Law"
        ENGINEERING = "engineering", "Engineering"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="career_guidance")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_career_guidance")
    career_interest = models.CharField(max_length=20, choices=InterestType.choices)
    career_goals = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    areas_for_development = models.TextField(blank=True)
    recommended_courses = models.TextField(blank=True)
    recommended_activities = models.TextField(blank=True)
    college_preferences = models.TextField(blank=True)
    scholarship_eligibility = models.BooleanField(default=False)
    guidance_date = models.DateField()
    guided_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_career_guidance"
        ordering = ["-guidance_date"]

    def __str__(self):
        return f"{self.student} - {self.get_career_interest_display()}"


class StudentParentCommunication(models.Model):
    """Parent-teacher communication records."""

    class CommType(models.TextChoices):
        MEETING = "meeting", "Meeting"
        PHONE_CALL = "phone_call", "Phone Call"
        EMAIL = "email", "Email"
        NOTE = "note", "Written Note"
        CONFERENCE = "conference", "Conference"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="parent_communications")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_parent_communications")
    communication_type = models.CharField(max_length=20, choices=CommType.choices)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    communication_date = models.DateField()
    parent_name = models.CharField(max_length=200, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    parent_email = models.EmailField(blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    is_confidential = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_parent_communications"
        ordering = ["-communication_date"]

    def __str__(self):
        return f"{self.student} - {self.get_communication_type_display()} ({self.communication_date})"


class StudentAcademicAdvisor(models.Model):
    """Academic advising records."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        PENDING = "pending", "Pending"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="academic_advising")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_academic_advising")
    advisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    advising_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    academic_goals = models.TextField(blank=True)
    course_recommendations = models.TextField(blank=True)
    academic_concerns = models.TextField(blank=True)
    action_items = models.TextField(blank=True)
    next_advising_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_academic_advising"
        ordering = ["-advising_date"]

    def __str__(self):
        return f"{self.student} - Academic Advising ({self.advising_date})"


class StudentTransfer(models.Model):
    """Transfer records."""

    class TransferType(models.TextChoices):
        INCOMING = "incoming", "Incoming"
        OUTGOING = "outgoing", "Outgoing"
        INTERNAL = "internal", "Internal Transfer"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_transfers")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_transfers")
    transfer_type = models.CharField(max_length=20, choices=TransferType.choices)
    from_school = models.CharField(max_length=200, blank=True)
    to_school = models.CharField(max_length=200, blank=True)
    from_classroom = models.ForeignKey(
        Classroom, on_delete=models.SET_NULL, null=True, blank=True, related_name="transfers_from"
    )
    to_classroom = models.ForeignKey(
        Classroom, on_delete=models.SET_NULL, null=True, blank=True, related_name="transfers_to"
    )
    transfer_date = models.DateField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    documents = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_transfers"
        ordering = ["-transfer_date"]

    def __str__(self):
        return f"{self.student} - {self.get_transfer_type_display()} ({self.transfer_date})"


class StudentGraduation(models.Model):
    """Graduation tracking."""

    class Status(models.TextChoices):
        ON_TRACK = "on_track", "On Track"
        AT_RISK = "at_risk", "At Risk"
        GRADUATED = "graduated", "Graduated"
        NOT_GRADUATED = "not_graduated", "Not Graduated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="graduation_records")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_graduation")
    expected_graduation_year = models.PositiveSmallIntegerField()
    actual_graduation_year = models.PositiveSmallIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ON_TRACK)
    credits_earned = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    credits_required = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    class_rank = models.PositiveIntegerField(null=True, blank=True)
    diploma_type = models.CharField(max_length=100, blank=True)
    honors = models.CharField(max_length=100, blank=True)
    college_acceptance = models.TextField(blank=True)
    scholarship_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_graduation"
        ordering = ["-expected_graduation_year"]

    def __str__(self):
        return f"{self.student} - Graduation {self.expected_graduation_year}"


class StudentVolunteer(models.Model):
    """Volunteer hours tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="volunteer_hours")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_volunteer")
    organization = models.CharField(max_length=200)
    activity = models.CharField(max_length=200)
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    date_performed = models.DateField()
    supervisor_name = models.CharField(max_length=200, blank=True)
    supervisor_phone = models.CharField(max_length=20, blank=True)
    supervisor_email = models.EmailField(blank=True)
    certificate_url = models.URLField(max_length=500, blank=True)
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_volunteer_hours"
        ordering = ["-date_performed"]

    def __str__(self):
        return f"{self.student} - {self.organization} ({self.hours} hrs)"


class StudentInternship(models.Model):
    """Internship tracking."""

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="internships")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_internships")
    company_name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    department = models.CharField(max_length=100, blank=True)
    supervisor_name = models.CharField(max_length=200, blank=True)
    supervisor_email = models.EmailField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    hours_per_week = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    stipend_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    skills_gained = models.TextField(blank=True)
    evaluation = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-5 rating")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_internships"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.student} - {self.company_name} ({self.position})"


class StudentScholarship(models.Model):
    """Scholarship tracking."""

    class Status(models.TextChoices):
        APPLIED = "applied", "Applied"
        PENDING = "pending", "Pending"
        AWARDED = "awarded", "Awarded"
        DECLINED = "declined", "Declined"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_scholarships")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_scholarships")
    scholarship_name = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    scholarship_type = models.CharField(max_length=100, blank=True)
    application_date = models.DateField()
    deadline_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)
    award_date = models.DateField(null=True, blank=True)
    renewal_required = models.BooleanField(default=False)
    renewal_date = models.DateField(null=True, blank=True)
    gpa_requirement = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    documents = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_scholarships"
        ordering = ["-application_date"]

    def __str__(self):
        return f"{self.student} - {self.scholarship_name}"


class StudentFinancialAid(models.Model):
    """Financial aid records."""

    class AidType(models.TextChoices):
        GRANT = "grant", "Grant"
        LOAN = "loan", "Loan"
        WORK_STUDY = "work_study", "Work-Study"
        WAIVER = "waiver", "Fee Waiver"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        APPLIED = "applied", "Applied"
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        DISBURSED = "disbursed", "Disbursed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="financial_aid")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_financial_aid")
    aid_type = models.CharField(max_length=20, choices=AidType.choices)
    aid_name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.CharField(max_length=200, blank=True)
    application_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)
    disbursement_date = models.DateField(null=True, blank=True)
    renewal_required = models.BooleanField(default=False)
    academic_requirement = models.TextField(blank=True)
    documents = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_financial_aid"
        ordering = ["-application_date"]

    def __str__(self):
        return f"{self.student} - {self.aid_name} ({self.get_aid_type_display()})"


class StudentTransportAssignment(models.Model):
    """Student transportation assignment."""

    class ServiceType(models.TextChoices):
        PICKUP = "pickup", "Pickup Only"
        DROPOFF = "dropoff", "Dropoff Only"
        BOTH = "both", "Both"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_transport_assignments")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_transport")
    route = models.ForeignKey("transportation.Route", on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey("transportation.Vehicle", on_delete=models.SET_NULL, null=True, blank=True)
    service_type = models.CharField(max_length=20, choices=ServiceType.choices, default=ServiceType.BOTH)
    pickup_address = models.TextField(blank=True)
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_transport_assignments"
        ordering = ["-effective_from"]

    def __str__(self):
        return f"{self.student} - Transport ({self.get_service_type_display()})"


class StudentMealPlan(models.Model):
    """Meal plan tracking."""

    class PlanType(models.TextChoices):
        FULL = "full", "Full Board"
        LUNCH = "lunch", "Lunch Only"
        BREAKFAST = "breakfast", "Breakfast Only"
        PARTIAL = "partial", "Partial"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="meal_plans")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_meal_plans")
    plan_type = models.CharField(max_length=20, choices=PlanType.choices)
    plan_name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    meals_per_day = models.PositiveSmallIntegerField(default=3)
    total_meals = models.PositiveIntegerField(default=0)
    meals_consumed = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dietary_restrictions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_meal_plans"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.student} - {self.plan_name}"


class StudentParking(models.Model):
    """Parking permit tracking."""

    class PermitType(models.TextChoices):
        STUDENT = "student", "Student"
        STAFF = "staff", "Staff"
        VISITOR = "visitor", "Visitor"
        HANDICAP = "handicap", "Handicap"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        SUSPENDED = "suspended", "Suspended"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="parking_permits")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_parking")
    permit_number = models.CharField(max_length=50, unique=True)
    permit_type = models.CharField(max_length=20, choices=PermitType.choices, default=PermitType.STUDENT)
    vehicle_make = models.CharField(max_length=100, blank=True)
    vehicle_model = models.CharField(max_length=100, blank=True)
    vehicle_color = models.CharField(max_length=50, blank=True)
    license_plate = models.CharField(max_length=20)
    parking_zone = models.CharField(max_length=50, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_parking_permits"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.permit_number} - {self.student}"


class StudentIDActivity(models.Model):
    """ID card usage tracking."""

    class ActivityType(models.TextChoices):
        ENTRY = "entry", "Building Entry"
        EXIT = "exit", "Building Exit"
        LIBRARY = "library", "Library"
        CAFETERIA = "cafeteria", "Cafeteria"
        LAB = "lab", "Lab Access"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="id_activities")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_id_activities")
    id_card = models.ForeignKey("StudentIDCard", on_delete=models.SET_NULL, null=True, blank=True)
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    location = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    device = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "student_id_activities"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.student} - {self.get_activity_type_display()} ({self.timestamp})"


class StudentFeedback(models.Model):
    """Student feedback surveys."""

    class FeedbackType(models.TextChoices):
        COURSE = "course", "Course Feedback"
        TEACHER = "teacher", "Teacher Feedback"
        FACILITY = "facility", "Facility Feedback"
        SERVICE = "service", "Service Feedback"
        GENERAL = "general", "General Feedback"

    class Rating(models.IntegerChoices):
        VERY_POOR = 1, "Very Poor"
        POOR = 2, "Poor"
        NEUTRAL = 3, "Neutral"
        GOOD = 4, "Good"
        EXCELLENT = 5, "Excellent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="feedback")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_feedback")
    feedback_type = models.CharField(max_length=20, choices=FeedbackType.choices)
    subject = models.CharField(max_length=200)
    rating = models.IntegerField(choices=Rating.choices)
    comments = models.TextField(blank=True)
    suggestions = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    response = models.TextField(blank=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    feedback_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_feedback"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.get_feedback_type_display()} ({self.get_rating_display()})"
