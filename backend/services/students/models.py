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
