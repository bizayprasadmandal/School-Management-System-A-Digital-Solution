"""Health / Clinic Management — Student health records, visits, immunizations, medications."""

import uuid

from django.db import models
from services.auth.models import School, User


class HealthRecord(models.Model):
    """Student health record with medical conditions and allergies."""

    class BloodType(models.TextChoices):
        A_POS = "A+", "A+"
        A_NEG = "A-", "A-"
        B_POS = "B+", "B+"
        B_NEG = "B-", "B-"
        AB_POS = "AB+", "AB+"
        AB_NEG = "AB-", "AB-"
        O_POS = "O+", "O+"
        O_NEG = "O-", "O-"
        UNKNOWN = "unknown", "Unknown"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_records")
    student = models.OneToOneField("students.Student", on_delete=models.CASCADE, related_name="health_record")
    blood_type = models.CharField(max_length=10, choices=BloodType.choices, default=BloodType.UNKNOWN)
    height_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    allergies = models.TextField(blank=True, help_text="Comma-separated list of allergies")
    chronic_conditions = models.TextField(blank=True)
    medications = models.TextField(blank=True, help_text="Regular medications")
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    doctor_name = models.CharField(max_length=150, blank=True)
    doctor_phone = models.CharField(max_length=20, blank=True)
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_records"

    def __str__(self):
        return f"Health: {self.student}"


class NurseVisit(models.Model):
    """Records of student visits to the school clinic/nurse."""

    class VisitType(models.TextChoices):
        SICK = "sick", "Sick Visit"
        INJURY = "injury", "Injury"
        MEDICATION = "medication", "Medication"
        CHECKUP = "checkup", "Routine Checkup"
        FOLLOWUP = "followup", "Follow-up"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        TREATED = "treated", "Treated"
        REFERRED = "referred", "Referred to Hospital"
        MEDICATION_GIVEN = "medication_given", "Medication Given"
        OBSERVATION = "observation", "Under Observation"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="nurse_visits")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="nurse_visits")
    visit_type = models.CharField(max_length=20, choices=VisitType.choices)
    visit_date = models.DateTimeField(auto_now_add=True)
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    medication_given = models.TextField(blank=True)
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TREATED)
    treated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="treatments")
    notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_visits"
        ordering = ["-visit_date"]

    def __str__(self):
        return f"{self.student} - {self.visit_date.date()} ({self.get_visit_type_display()})"


class Immunization(models.Model):
    """Student immunization/vaccination records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="immunizations")
    vaccine_name = models.CharField(max_length=100)
    dose_number = models.PositiveSmallIntegerField(default=1)
    date_administered = models.DateField()
    administered_by = models.CharField(max_length=150, blank=True)
    facility = models.CharField(max_length=150, blank=True)
    batch_number = models.CharField(max_length=50, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_immunizations"
        ordering = ["-date_administered"]

    def __str__(self):
        return f"{self.student} - {self.vaccine_name} (Dose {self.dose_number})"


class MedicationLog(models.Model):
    """Medication administration log."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="medication_logs")
    medication_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    route = models.CharField(max_length=50, blank=True, help_text="Oral, Topical, Injection, etc.")
    time_administered = models.DateTimeField()
    administered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="medication_admin"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_medication_logs"
        ordering = ["-time_administered"]

    def __str__(self):
        return f"{self.student} - {self.medication_name} ({self.dosage})"


# =============================================================================
# Health Forms & Waivers
# =============================================================================


class HealthForm(models.Model):
    """Digital health forms and waivers for students."""

    class FormType(models.TextChoices):
        HEALTH_HISTORY = "health_history", "Health History Form"
        IMMUNIZATION_RECORD = "immunization_record", "Immunization Record"
        MEDICATION_AUTHORIZATION = "medication_auth", "Medication Authorization"
        ALLERGY_ACTION_PLAN = "allergy_plan", "Allergy Action Plan"
        ASTHMA_ACTION_PLAN = "asthma_plan", "Asthma Action Plan"
        DIABETES_MANAGEMENT = "diabetes_mgmt", "Diabetes Management Plan"
        EMERGENCY_CONTACT = "emergency_contact", "Emergency Contact Form"
        PHYSICAL_EXAMINATION = "physical_exam", "Physical Examination Form"
        CONSENT_FORM = "consent", "Consent Form"
        WAIVER = "waiver", "Liability Waiver"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_forms")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    form_type = models.CharField(max_length=25, choices=FormType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Form content
    form_fields = models.JSONField(default=dict, help_text="JSON schema for form fields")
    instructions = models.TextField(blank=True)
    # Settings
    is_required = models.BooleanField(default=False, help_text="Required for enrollment?")
    due_date = models.DateField(null=True, blank=True)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_forms"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class HealthFormSubmission(models.Model):
    """Student/parent submission of health forms."""

    class SubmissionStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        NEEDS_REVISION = "needs_revision", "Needs Revision"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(HealthForm, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="health_form_submissions")
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=SubmissionStatus.choices, default=SubmissionStatus.SUBMITTED)
    # Form data
    form_data = models.JSONField(default=dict, help_text="Submitted form field values")
    # Documents
    attachments = models.JSONField(default=list, help_text="List of attachment URLs")
    # Review
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_health_forms"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    # Signature
    signature_data = models.TextField(blank=True, help_text="Digital signature data")
    signed_at = models.DateTimeField(null=True, blank=True)
    # Dates
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_form_submissions"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student} - {self.form.title}"


# =============================================================================
# Allergy Management
# =============================================================================


class AllergyManagement(models.Model):
    """Detailed allergy tracking for students."""

    class SeverityLevel(models.TextChoices):
        MILD = "mild", "Mild"
        MODERATE = "moderate", "Moderate"
        SEVERE = "severe", "Severe"
        LIFE_THREATENING = "life_threatening", "Life-Threatening"

    class AllergyType(models.TextChoices):
        FOOD = "food", "Food"
        MEDICATION = "medication", "Medication"
        ENVIRONMENTAL = "environmental", "Environmental"
        INSECT = "insect", "Insect"
        LATEX = "latex", "Latex"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="allergy_records")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="allergy_records")
    allergen_name = models.CharField(max_length=100)
    allergy_type = models.CharField(max_length=20, choices=AllergyType.choices)
    severity = models.CharField(max_length=20, choices=SeverityLevel.choices)
    # Symptoms & Treatment
    symptoms = models.TextField(blank=True, help_text="Common symptoms")
    reaction_description = models.TextField(blank=True)
    treatment_protocol = models.TextField(blank=True, help_text="What to do in case of reaction")
    # Medications
    emergency_medication = models.CharField(max_length=100, blank=True, help_text="e.g., EpiPen")
    medication_location = models.CharField(max_length=100, blank=True, help_text="Where emergency med is stored")
    # Documentation
    diagnosis_date = models.DateField(null=True, blank=True)
    diagnosed_by = models.CharField(max_length=150, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "allergy_records"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.allergen_name} ({self.get_severity_display()})"


# =============================================================================
# Chronic Condition Tracking
# =============================================================================


class ChronicConditionTracking(models.Model):
    """Track chronic conditions like diabetes, asthma, epilepsy."""

    class ConditionType(models.TextChoices):
        DIABETES = "diabetes", "Diabetes"
        ASTHMA = "asthma", "Asthma"
        EPILEPSY = "epilepsy", "Epilepsy"
        ALLERGIES = "allergies", "Severe Allergies"
        HEART_CONDITION = "heart", "Heart Condition"
        SICKLE_CELL = "sickle_cell", "Sickle Cell Disease"
        CYSTIC_FIBROSIS = "cystic_fibrosis", "Cystic Fibrosis"
        AUTISM = "autism", "Autism Spectrum"
        ADHD = "adhd", "ADHD"
        OTHER = "other", "Other"

    class SeverityLevel(models.TextChoices):
        MILD = "mild", "Mild"
        MODERATE = "moderate", "Moderate"
        SEVERE = "severe", "Severe"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="chronic_conditions")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="chronic_conditions")
    condition_type = models.CharField(max_length=25, choices=ConditionType.choices)
    condition_name = models.CharField(max_length=100)
    severity = models.CharField(max_length=15, choices=SeverityLevel.choices)
    diagnosed_date = models.DateField(null=True, blank=True)
    diagnosed_by = models.CharField(max_length=150, blank=True)
    # Management Plan
    management_plan = models.TextField(help_text="How to manage the condition at school")
    medication_schedule = models.TextField(blank=True, help_text="When and what medications to give")
    dietary_restrictions = models.TextField(blank=True)
    activity_restrictions = models.TextField(blank=True)
    # Emergency Protocol
    emergency_protocol = models.TextField(blank=True, help_text="What to do in emergency")
    emergency_medication = models.CharField(max_length=100, blank=True)
    emergency_med_location = models.CharField(max_length=100, blank=True)
    # Contacts
    specialist_name = models.CharField(max_length=150, blank=True)
    specialist_phone = models.CharField(max_length=20, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    last_review_date = models.DateField(null=True, blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "chronic_conditions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.condition_name}"


# =============================================================================
# Emergency Plans
# =============================================================================


class EmergencyPlan(models.Model):
    """Emergency protocols and procedures for the school."""

    class PlanType(models.TextChoices):
        MEDICAL_EMERGENCY = "medical", "Medical Emergency"
        ALLERGIC_REACTION = "allergic", "Allergic Reaction"
        SEIZURE = "seizure", "Seizure Protocol"
        DIABETIC_EMERGENCY = "diabetic", "Diabetic Emergency"
        ASTHMA_ATTACK = "asthma", "Asthma Attack"
        INJURY = "injury", "Injury Protocol"
        MENTAL_HEALTH_CRISIS = "mental_health", "Mental Health Crisis"
        GENERAL = "general", "General Emergency"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        UNDER_REVIEW = "under_review", "Under Review"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="emergency_plans")
    title = models.CharField(max_length=200)
    plan_type = models.CharField(max_length=20, choices=PlanType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Plan Content
    description = models.TextField()
    procedures = models.TextField(help_text="Step-by-step procedures")
    # Personnel
    responsible_staff = models.JSONField(default=list, help_text="List of staff responsible")
    contact_numbers = models.JSONField(default=dict, help_text="Emergency contact numbers")
    # Equipment
    required_equipment = models.TextField(blank=True, help_text="Equipment needed")
    equipment_location = models.CharField(max_length=200, blank=True)
    # Training
    last_training_date = models.DateField(null=True, blank=True)
    training_notes = models.TextField(blank=True)
    # Metadata
    effective_date = models.DateField()
    review_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "emergency_plans"
        ordering = ["-effective_date"]

    def __str__(self):
        return self.title


class EmergencyContact(models.Model):
    """Emergency contacts for students."""

    class Relationship(models.TextChoices):
        PARENT = "parent", "Parent"
        GUARDIAN = "guardian", "Guardian"
        GRANDPARENT = "grandparent", "Grandparent"
        SIBLING = "sibling", "Sibling"
        OTHER_FAMILY = "other_family", "Other Family"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="emergency_contacts")
    contact_name = models.CharField(max_length=150)
    relationship = models.CharField(max_length=20, choices=Relationship.choices)
    phone_primary = models.CharField(max_length=20)
    phone_secondary = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    can_pickup = models.BooleanField(default=False, help_text="Authorized for pickup?")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "emergency_contacts"
        ordering = ["-is_primary", "contact_name"]

    def __str__(self):
        return f"{self.student} - {self.contact_name} ({self.get_relationship_display()})"


# =============================================================================
# Health Screenings
# =============================================================================


class HealthScreening(models.Model):
    """Health screenings like vision, hearing, scoliosis."""

    class ScreeningType(models.TextChoices):
        VISION = "vision", "Vision Screening"
        HEARING = "hearing", "Hearing Screening"
        SCOLIOSIS = "scoliosis", "Scoliosis Screening"
        BMI = "bmi", "BMI Screening"
        DENTAL = "dental", "Dental Screening"
        BLOOD_PRESSURE = "bp", "Blood Pressure Screening"
        TB_TEST = "tb", "Tuberculosis Test"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        REFERRED = "referred", "Referred"
        FOLLOW_UP_NEEDED = "follow_up", "Follow-up Needed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_screenings")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="health_screenings")
    screening_type = models.CharField(max_length=20, choices=ScreeningType.choices)
    screening_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    # Results
    result_summary = models.TextField(blank=True)
    is_normal = models.BooleanField(null=True, blank=True)
    # Referral
    referral_needed = models.BooleanField(default=False)
    referral_notes = models.TextField(blank=True)
    referred_to = models.CharField(max_length=150, blank=True)
    # Personnel
    screened_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_screenings"
        ordering = ["-screening_date"]

    def __str__(self):
        return f"{self.student} - {self.get_screening_type_display()}"


class ScreeningResult(models.Model):
    """Detailed screening results."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    screening = models.ForeignKey(HealthScreening, on_delete=models.CASCADE, related_name="results")
    metric_name = models.CharField(max_length=100)
    metric_value = models.CharField(max_length=100)
    normal_range = models.CharField(max_length=100, blank=True)
    is_abnormal = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "screening_results"

    def __str__(self):
        return f"{self.screening} - {self.metric_name}: {self.metric_value}"


# =============================================================================
# Medication Inventory & Prescriptions
# =============================================================================


class MedicationInventory(models.Model):
    """Track clinic medication stock."""

    class MedicationCategory(models.TextChoices):
        PAIN_RELIEVER = "pain", "Pain Relievers"
        ANTIHISTAMINE = "antihistamine", "Antihistamines"
        RESPIRATORY = "respiratory", "Respiratory"
        GASTROINTESTINAL = "gastro", "Gastrointestinal"
        TOPICAL = "topical", "Topical"
        EMERGENCY = "emergency", "Emergency Medications"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="medication_inventory")
    medication_name = models.CharField(max_length=100)
    generic_name = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=20, choices=MedicationCategory.choices)
    # Stock
    quantity_on_hand = models.PositiveIntegerField(default=0)
    unit_of_measure = models.CharField(max_length=20, default="tablets")
    reorder_threshold = models.PositiveIntegerField(default=10)
    # Storage
    storage_location = models.CharField(max_length=100)
    requires_refrigeration = models.BooleanField(default=False)
    # Expiry
    expiration_date = models.DateField()
    lot_number = models.CharField(max_length=50, blank=True)
    # Supplier
    supplier = models.CharField(max_length=100, blank=True)
    last_reorder_date = models.DateField(null=True, blank=True)
    # Status
    is_controlled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medication_inventory"
        ordering = ["medication_name"]

    def __str__(self):
        return f"{self.medication_name} ({self.quantity_on_hand} {self.unit_of_measure})"


class MedicationPrescription(models.Model):
    """Prescriptions for student medications."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="medication_prescriptions")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="medication_prescriptions")
    # Medication
    medication_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    route = models.CharField(max_length=50, blank=True)
    # Timing
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    times_per_day = models.PositiveSmallIntegerField(default=1)
    administration_times = models.JSONField(default=list, help_text='List of times e.g., ["08:00", "12:00"]')
    # Authorization
    prescribed_by = models.CharField(max_length=150)
    prescriber_phone = models.CharField(max_length=20, blank=True)
    parent_consent = models.BooleanField(default=False)
    consent_date = models.DateField(null=True, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medication_prescriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.medication_name} ({self.dosage})"


# =============================================================================
# Parent Notifications
# =============================================================================


class ParentNotification(models.Model):
    """Health-related notifications to parents."""

    class NotificationType(models.TextChoices):
        MEDICATION_GIVEN = "medication", "Medication Given"
        CLINIC_VISIT = "clinic", "Clinic Visit"
        FEVER = "fever", "Fever Detected"
        INJURY = "injury", "Injury Reported"
        ILLNESS = "illness", "Illness Detected"
        ALLERGY_REACTION = "allergy", "Allergy Reaction"
        HEALTH_SCREENING = "screening", "Health Screening Results"
        IMMUNIZATION_DUE = "immunization", "Immunization Due"
        HEALTH_FORM_DUE = "form", "Health Form Due"
        EMERGENCY = "emergency", "Emergency"
        OTHER = "other", "Other"

    class DeliveryMethod(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push Notification"
        IN_APP = "in_app", "In-App"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        READ = "read", "Read"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_notifications")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="health_notifications")
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    delivery_method = models.CharField(max_length=10, choices=DeliveryMethod.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    # Related objects
    nurse_visit = models.ForeignKey(NurseVisit, on_delete=models.SET_NULL, null=True, blank=True)
    medication_log = models.ForeignKey(MedicationLog, on_delete=models.SET_NULL, null=True, blank=True)
    # Dates
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.get_notification_type_display()}"


# =============================================================================
# Health Compliance
# =============================================================================


class HealthCompliance(models.Model):
    """Track immunization compliance and health requirements."""

    class ComplianceType(models.TextChoices):
        IMMUNIZATION = "immunization", "Immunization Compliance"
        PHYSICAL_EXAM = "physical", "Physical Examination"
        DENTAL_EXAM = "dental", "Dental Examination"
        TB_TEST = "tb", "TB Test"
        VISION_TEST = "vision", "Vision Test"
        HEARING_TEST = "hearing", "Hearing Test"
        HEALTH_FORM = "form", "Health Form"
        MEDICATION_AUTH = "med_auth", "Medication Authorization"
        OTHER = "other", "Other"

    class ComplianceStatus(models.TextChoices):
        COMPLIANT = "compliant", "Compliant"
        NON_COMPLIANT = "non_compliant", "Non-Compliant"
        PENDING = "pending", "Pending"
        EXEMPTED = "exempted", "Exempted"
        OVERDUE = "overdue", "Overdue"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_compliance")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="health_compliance")
    compliance_type = models.CharField(max_length=20, choices=ComplianceType.choices)
    status = models.CharField(max_length=15, choices=ComplianceStatus.choices, default=ComplianceStatus.PENDING)
    # Dates
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    # Details
    requirement = models.CharField(max_length=200, help_text="Specific requirement description")
    notes = models.TextField(blank=True)
    # Documentation
    document_url = models.URLField(blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_compliance"
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.student} - {self.get_compliance_type_display()}"


# =============================================================================
# Nurse Scheduling
# =============================================================================


class NurseSchedule(models.Model):
    """Nurse availability and scheduling."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    class ShiftType(models.TextChoices):
        MORNING = "morning", "Morning Shift"
        AFTERNOON = "afternoon", "Afternoon Shift"
        FULL_DAY = "full_day", "Full Day"
        ON_CALL = "on_call", "On Call"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nurse = models.ForeignKey(User, on_delete=models.CASCADE, related_name="nurse_schedule")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="nurse_schedule")
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    shift_type = models.CharField(max_length=10, choices=ShiftType.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    # Recurring
    is_recurring = models.BooleanField(default=True)
    effective_from = models.DateField()
    effective_until = models.DateField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "nurse_schedule"
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.nurse} - {self.get_day_of_week_display()} ({self.get_shift_type_display()})"


# =============================================================================
# Incident Reports
# =============================================================================


class IncidentReport(models.Model):
    """Document health incidents and accidents."""

    class IncidentType(models.TextChoices):
        INJURY = "injury", "Injury"
        ILLNESS = "illness", "Illness"
        ALLERGIC_REACTION = "allergy", "Allergic Reaction"
        SEIZURE = "seizure", "Seizure"
        FAINTING = "fainting", "Fainting"
        BREATHING = "breathing", "Breathing Difficulty"
        HEADACHE = "headache", "Severe Headache"
        BLOOD = "blood", "Blood/Bodily Fluid"
        OTHER = "other", "Other"

    class SeverityLevel(models.TextChoices):
        MINOR = "minor", "Minor"
        MODERATE = "moderate", "Moderate"
        SEVERE = "severe", "Severe"
        CRITICAL = "critical", "Critical"

    class ActionTaken(models.TextChoices):
        NONE = "none", "No Action Needed"
        FIRST_AID = "first_aid", "First Aid Given"
        MEDICATION = "medication", "Medication Given"
        REFERRAL = "referral", "Referred to Hospital"
        EMS = "ems", "EMS Called"
        PARENT_CONTACTED = "parent", "Parent Contacted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="incident_reports")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="incident_reports")
    incident_type = models.CharField(max_length=20, choices=IncidentType.choices)
    severity = models.CharField(max_length=10, choices=SeverityLevel.choices)
    # Incident Details
    incident_date = models.DateTimeField()
    location = models.CharField(max_length=100)
    description = models.TextField()
    # Actions
    action_taken = models.CharField(max_length=20, choices=ActionTaken.choices)
    action_details = models.TextField(blank=True)
    # Personnel
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    witnessed_by = models.JSONField(default=list, help_text="List of witnesses")
    # Follow-up
    parent_notified = models.BooleanField(default=False)
    parent_notified_at = models.DateTimeField(null=True, blank=True)
    follow_up_needed = models.BooleanField(default=False)
    follow_up_notes = models.TextField(blank=True)
    # Medical
    treatment_given = models.TextField(blank=True)
    hospital_name = models.CharField(max_length=150, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "incident_reports"
        ordering = ["-incident_date"]

    def __str__(self):
        return f"{self.student} - {self.get_incident_type_display()} ({self.incident_date.date()})"


# =============================================================================
# Medical Referrals
# =============================================================================


class MedicalReferral(models.Model):
    """Track referrals to external medical providers."""

    class ReferralReason(models.TextChoices):
        SPECIALIST = "specialist", "Specialist Consultation"
        HOSPITAL = "hospital", "Hospital Referral"
        TESTING = "testing", "Medical Testing"
        TREATMENT = "treatment", "Treatment Follow-up"
        EMERGENCY = "emergency", "Emergency Care"
        MENTAL_HEALTH = "mental_health", "Mental Health Service"
        DENTAL = "dental", "Dental Care"
        VISION = "vision", "Vision Care"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="medical_referrals")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="medical_referrals")
    referral_reason = models.CharField(max_length=20, choices=ReferralReason.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Provider
    provider_name = models.CharField(max_length=150)
    provider_phone = models.CharField(max_length=20, blank=True)
    provider_address = models.TextField(blank=True)
    # Details
    reason_for_referral = models.TextField()
    urgency = models.CharField(max_length=20, blank=True)
    # Dates
    referral_date = models.DateField()
    appointment_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    # Follow-up
    follow_up_needed = models.BooleanField(default=False)
    follow_up_notes = models.TextField(blank=True)
    # Personnel
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "medical_referrals"
        ordering = ["-referral_date"]

    def __str__(self):
        return f"{self.student} - {self.get_referral_reason_display()}"


# =============================================================================
# Health Reports & Analytics
# =============================================================================


class HealthReport(models.Model):
    """Health analytics and reports."""

    class ReportType(models.TextChoices):
        IMMUNIZATION_STATUS = "immunization", "Immunization Status Report"
        CLINIC_USAGE = "clinic", "Clinic Usage Report"
        MEDICATION_USAGE = "medication", "Medication Usage Report"
        ALLERGY_SUMMARY = "allergy", "Allergy Summary"
        INCIDENT_SUMMARY = "incident", "Incident Summary"
        SCREENING_RESULTS = "screening", "Screening Results Report"
        COMPLIANCE_STATUS = "compliance", "Compliance Status Report"
        CHRONIC_CONDITIONS = "chronic", "Chronic Conditions Report"
        GENERAL = "general", "General Health Report"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATED = "generated", "Generated"
        SENT = "sent", "Sent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_reports")
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=ReportType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    # Report Details
    period_start = models.DateField()
    period_end = models.DateField()
    summary = models.TextField(blank=True)
    findings = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)
    # Statistics
    total_students = models.PositiveIntegerField(default=0)
    total_visits = models.PositiveIntegerField(default=0)
    total_incidents = models.PositiveIntegerField(default=0)
    # Personnel
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# =============================================================================
# Critical Health Alerts
# =============================================================================


class HealthAlert(models.Model):
    """Critical health alerts (epi-pen, etc.)."""

    class AlertType(models.TextChoices):
        EPI_PEN = "epi_pen", "EpiPen Required"
        ASTHMA_INHALER = "inhaler", "Asthma Inhaler Required"
        DIABETIC_KIT = "diabetic", "Diabetic Kit Required"
        SEIZURE_MEDICATION = "seizure", "Seizure Medication Required"
        ALLERGY = "allergy", "Severe Allergy"
        OTHER = "other", "Other Critical Health Alert"

    class UrgencyLevel(models.TextChoices):
        IMMEDIATE = "immediate", "Immediate Action Required"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_alerts")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="health_alerts")
    alert_type = models.CharField(max_length=20, choices=AlertType.choices)
    urgency_level = models.CharField(max_length=15, choices=UrgencyLevel.choices, default=UrgencyLevel.IMMEDIATE)
    # Alert Details
    alert_message = models.TextField()
    emergency_instructions = models.TextField()
    # Location of Medication
    medication_name = models.CharField(max_length=100)
    medication_location = models.CharField(max_length=200)
    # Contact
    emergency_contact_name = models.CharField(max_length=150)
    emergency_contact_phone = models.CharField(max_length=20)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"ALERT: {self.student} - {self.get_alert_type_display()}"


# =============================================================================
# Health Education
# =============================================================================


class HealthEducation(models.Model):
    """Health education resources for students."""

    class ResourceType(models.TextChoices):
        DOCUMENT = "document", "Document"
        VIDEO = "video", "Video"
        LINK = "link", "External Link"
        HANDOUT = "handout", "Handout"
        PRESENTATION = "presentation", "Presentation"
        OTHER = "other", "Other"

    class TopicCategory(models.TextChoices):
        NUTRITION = "nutrition", "Nutrition"
        HYGIENE = "hygiene", "Personal Hygiene"
        MENTAL_HEALTH = "mental_health", "Mental Health"
        SUBSTANCE_ABUSE = "substance", "Substance Abuse Prevention"
        SEX_EDUCATION = "sex_ed", "Sex Education"
        FIRST_AID = "first_aid", "First Aid"
        EXERCISE = "exercise", "Physical Activity"
        SLEEP = "sleep", "Sleep Health"
        GENERAL = "general", "General Health"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_education")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=15, choices=ResourceType.choices)
    topic_category = models.CharField(max_length=15, choices=TopicCategory.choices)
    # Content
    content_url = models.URLField(blank=True)
    file_url = models.URLField(blank=True)
    content_text = models.TextField(blank=True)
    # Target
    target_grades = models.JSONField(default=list, help_text="List of grade levels")
    is_required = models.BooleanField(default=False)
    # Personnel
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_education"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# =============================================================================
# Telehealth Sessions
# =============================================================================


class TelehealthSession(models.Model):
    """Virtual health consultations."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    class SessionType(models.TextChoices):
        CONSULTATION = "consultation", "General Consultation"
        FOLLOW_UP = "follow_up", "Follow-up"
        MENTAL_HEALTH = "mental_health", "Mental Health"
        SPECIALIST = "specialist", "Specialist Consultation"
        EMERGENCY = "emergency", "Emergency"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="telehealth_sessions")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="telehealth_sessions")
    session_type = models.CharField(max_length=15, choices=SessionType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=30)
    # Meeting Details
    meeting_link = models.URLField(blank=True)
    meeting_id = models.CharField(max_length=100, blank=True)
    meeting_password = models.CharField(max_length=50, blank=True)
    # Participants
    healthcare_provider = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="telehealth_provided"
    )
    parent_present = models.BooleanField(default=False)
    nurse_present = models.BooleanField(default=False)
    # Outcome
    notes = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_needed = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "telehealth_sessions"
        ordering = ["-scheduled_date", "-scheduled_time"]

    def __str__(self):
        return f"{self.student} - {self.get_session_type_display()} ({self.scheduled_date})"


class DentalRecord(models.Model):
    """Dental health records."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        FOLLOW_UP = "follow_up", "Follow-up Needed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="dental_records")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="dental_records")
    visit_date = models.DateField()
    dentist_name = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)
    examination_findings = models.TextField(blank=True)
    cavities_count = models.PositiveSmallIntegerField(default=0)
    gum_health = models.CharField(max_length=50, blank=True)
    treatment_provided = models.TextField(blank=True)
    prescriptions = models.TextField(blank=True)
    next_checkup_date = models.DateField(null=True, blank=True)
    xray_url = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_dental_records"
        ordering = ["-visit_date"]

    def __str__(self):
        return f"Dental: {self.student} ({self.visit_date})"


class VisionRecord(models.Model):
    """Vision screening records."""

    class Result(models.TextChoices):
        NORMAL = "normal", "Normal"
        NEEDS_CORRECTION = "needs_correction", "Needs Correction"
        REFERRED = "referred", "Referred to Specialist"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="vision_records")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="vision_records")
    screening_date = models.DateField()
    result = models.CharField(max_length=20, choices=Result.choices, default=Result.NORMAL)
    left_eye_vision = models.CharField(max_length=20, blank=True)
    right_eye_vision = models.CharField(max_length=20, blank=True)
    color_blindness = models.BooleanField(default=False)
    glasses_prescribed = models.BooleanField(default=False)
    prescription_details = models.TextField(blank=True)
    specialist_referral = models.BooleanField(default=False)
    referral_details = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_vision_records"
        ordering = ["-screening_date"]

    def __str__(self):
        return f"Vision: {self.student} ({self.screening_date})"


class GrowthChart(models.Model):
    """Growth tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="growth_charts")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="growth_charts")
    recorded_date = models.DateField()
    height_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    head_circumference_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure_systolic = models.PositiveSmallIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_growth_charts"
        ordering = ["-recorded_date"]

    def __str__(self):
        return f"Growth: {self.student} ({self.recorded_date})"


class VitalSigns(models.Model):
    """Vital signs tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="vital_signs")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="vital_signs")
    recorded_date = models.DateField()
    recorded_time = models.TimeField(null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    heart_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    respiratory_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    blood_pressure_systolic = models.PositiveSmallIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveSmallIntegerField(null=True, blank=True)
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_glucose = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    pain_scale = models.PositiveSmallIntegerField(null=True, blank=True, help_text="0-10 scale")
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_vital_signs"
        ordering = ["-recorded_date", "-recorded_time"]

    def __str__(self):
        return f"Vitals: {self.student} ({self.recorded_date})"


class LabResult(models.Model):
    """Lab test results."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        REVIEWED = "reviewed", "Reviewed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="lab_results")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="lab_results")
    test_name = models.CharField(max_length=200)
    test_date = models.DateField()
    result_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    result_value = models.CharField(max_length=100, blank=True)
    normal_range = models.CharField(max_length=100, blank=True)
    is_abnormal = models.BooleanField(default=False)
    lab_name = models.CharField(max_length=200, blank=True)
    ordered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_lab_results"
    )
    document_url = models.URLField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_lab_results"
        ordering = ["-test_date"]

    def __str__(self):
        return f"Lab: {self.student} - {self.test_name} ({self.test_date})"


class MedicalHistory(models.Model):
    """Complete medical history."""

    class HistoryType(models.TextChoices):
        CONDITION = "condition", "Medical Condition"
        SURGERY = "surgery", "Surgery"
        HOSPITALIZATION = "hospitalization", "Hospitalization"
        INJURY = "injury", "Injury"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="medical_history_records")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="medical_history_records")
    history_type = models.CharField(max_length=20, choices=HistoryType.choices)
    condition_name = models.CharField(max_length=200)
    diagnosis_date = models.DateField(null=True, blank=True)
    treating_physician = models.CharField(max_length=200, blank=True)
    treatment = models.TextField(blank=True)
    outcome = models.TextField(blank=True)
    is_chronic = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    resolved_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_medical_history"
        ordering = ["-diagnosis_date"]

    def __str__(self):
        return f"{self.student} - {self.condition_name}"


class FamilyMedicalHistory(models.Model):
    """Family medical history."""

    class Relationship(models.TextChoices):
        MOTHER = "mother", "Mother"
        FATHER = "father", "Father"
        SIBLING = "sibling", "Sibling"
        GRANDPARENT = "grandparent", "Grandparent"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="family_medical_history_records"
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="family_medical_history_records")
    relationship = models.CharField(max_length=20, choices=Relationship.choices)
    condition_name = models.CharField(max_length=200)
    age_at_diagnosis = models.PositiveSmallIntegerField(null=True, blank=True)
    is_hereditary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_family_medical_history"
        ordering = ["relationship", "condition_name"]

    def __str__(self):
        return f"{self.student} - {self.get_relationship_display()} - {self.condition_name}"


class HealthInsuranceRecord(models.Model):
    """Insurance records."""

    class InsuranceType(models.TextChoices):
        HEALTH = "health", "Health Insurance"
        DENTAL = "dental", "Dental Insurance"
        VISION = "vision", "Vision Insurance"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="health_insurance_records")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_insurance_records")
    insurance_type = models.CharField(max_length=20, choices=InsuranceType.choices, default=InsuranceType.HEALTH)
    provider_name = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=100)
    group_number = models.CharField(max_length=100, blank=True)
    subscriber_name = models.CharField(max_length=200, blank=True)
    subscriber_relationship = models.CharField(max_length=50, blank=True)
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    copay_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    deductible = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_insurance_records"
        ordering = ["-effective_date"]

    def __str__(self):
        return f"Insurance: {self.student} - {self.provider_name}"


class VaccinationSchedule(models.Model):
    """Vaccination schedules."""

    class Status(models.TextChoices):
        DUE = "due", "Due"
        COMPLETED = "completed", "Completed"
        OVERDUE = "overdue", "Overdue"
        EXEMPTED = "exempted", "Exempted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="vaccination_schedule_records"
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="vaccination_schedule_records")
    vaccine_name = models.CharField(max_length=200)
    dose_number = models.PositiveSmallIntegerField(default=1)
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DUE)
    administered_by = models.CharField(max_length=200, blank=True)
    batch_number = models.CharField(max_length=50, blank=True)
    site_of_administration = models.CharField(max_length=50, blank=True)
    reactions = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_vaccination_schedule"
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.student} - {self.vaccine_name} (Dose {self.dose_number})"


class HealthAssessment(models.Model):
    """Health assessments."""

    class AssessmentType(models.TextChoices):
        ANNUAL = "annual", "Annual Physical"
        SPORTS = "sports", "Sports Physical"
        PRE_ENROLLMENT = "pre_enrollment", "Pre-Enrollment"
        FOLLOW_UP = "follow_up", "Follow-up"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="health_assessments")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_assessments")
    assessment_type = models.CharField(max_length=20, choices=AssessmentType.choices)
    assessment_date = models.DateField()
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    general_health = models.CharField(max_length=50, blank=True)
    immunizations_current = models.BooleanField(default=True)
    allergies_checked = models.BooleanField(default=True)
    medications_checked = models.BooleanField(default=True)
    vision_screened = models.BooleanField(default=False)
    hearing_screened = models.BooleanField(default=False)
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    follow_up_needed = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    document_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_assessments"
        ordering = ["-assessment_date"]

    def __str__(self):
        return f"Assessment: {self.student} - {self.get_assessment_type_display()}"


class HealthRiskAssessment(models.Model):
    """Health risk assessments."""

    class RiskLevel(models.TextChoices):
        LOW = "low", "Low Risk"
        MODERATE = "moderate", "Moderate Risk"
        HIGH = "high", "High Risk"
        CRITICAL = "critical", "Critical Risk"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="health_risk_assessments")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_risk_assessments")
    assessment_date = models.DateField()
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW)
    risk_factors = models.JSONField(default=list, blank=True)
    chronic_conditions = models.TextField(blank=True)
    family_history_risks = models.TextField(blank=True)
    lifestyle_factors = models.TextField(blank=True)
    environmental_factors = models.TextField(blank=True)
    mitigation_plan = models.TextField(blank=True)
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_risk_assessments"
        ordering = ["-assessment_date"]

    def __str__(self):
        return f"Risk: {self.student} - {self.get_risk_level_display()}"


class MentalHealthRecord(models.Model):
    """Mental health records."""

    class SessionType(models.TextChoices):
        COUNSELING = "counseling", "Counseling"
        THERAPY = "therapy", "Therapy"
        ASSESSMENT = "assessment", "Assessment"
        CRISIS = "crisis", "Crisis Intervention"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="mental_health_records")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="mental_health_records")
    session_type = models.CharField(max_length=20, choices=SessionType.choices)
    session_date = models.DateField()
    provider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    presenting_issue = models.TextField(blank=True)
    assessment_findings = models.TextField(blank=True)
    diagnosis = models.CharField(max_length=200, blank=True)
    treatment_plan = models.TextField(blank=True)
    interventions = models.TextField(blank=True)
    progress_notes = models.TextField(blank=True)
    risk_level = models.CharField(
        max_length=20, choices=HealthRiskAssessment.RiskLevel.choices, default=HealthRiskAssessment.RiskLevel.LOW
    )
    follow_up_needed = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    is_confidential = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_mental_health_records"
        ordering = ["-session_date"]

    def __str__(self):
        return f"Mental Health: {self.student} ({self.session_date})"


class HealthEducationMaterial(models.Model):
    """Health education resources."""

    class MaterialType(models.TextChoices):
        BROCHURE = "brochure", "Brochure"
        VIDEO = "video", "Video"
        ARTICLE = "article", "Article"
        POSTER = "poster", "Poster"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_education_materials")
    title = models.CharField(max_length=200)
    material_type = models.CharField(max_length=20, choices=MaterialType.choices)
    topic = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    file_url = models.URLField(max_length=500, blank=True)
    target_audience = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_education_materials"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_material_type_display()})"


class HealthCampaign(models.Model):
    """Health campaigns."""

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_campaigns")
    name = models.CharField(max_length=200)
    description = models.TextField()
    campaign_type = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    target_audience = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    participants_count = models.PositiveIntegerField(default=0)
    materials = models.ManyToManyField(HealthEducationMaterial, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_campaigns"
        ordering = ["-start_date"]

    def __str__(self):
        return self.name


class HealthSurvey(models.Model):
    """Health surveys."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_surveys")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    questions = models.JSONField(default=list, blank=True)
    target_audience = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_anonymous = models.BooleanField(default=True)
    response_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_surveys"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class MedicalEquipment(models.Model):
    """Medical equipment tracking."""

    class Status(models.TextChoices):
        OPERATIONAL = "operational", "Operational"
        MAINTENANCE = "maintenance", "Under Maintenance"
        RETIRED = "retired", "Retired"
        OUT_OF_SERVICE = "out_of_service", "Out of Service"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="medical_equipment")
    name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=100, blank=True)
    model_name = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPERATIONAL)
    location = models.CharField(max_length=200, blank=True)
    last_calibration_date = models.DateField(null=True, blank=True)
    next_calibration_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_medical_equipment"
        ordering = ["name"]

    def __str__(self):
        return self.name


class EquipmentMaintenance(models.Model):
    """Equipment maintenance records."""

    class MaintenanceType(models.TextChoices):
        CALIBRATION = "calibration", "Calibration"
        REPAIR = "repair", "Repair"
        PREVENTIVE = "preventive", "Preventive"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(MedicalEquipment, on_delete=models.CASCADE, related_name="maintenance_records")
    maintenance_type = models.CharField(max_length=20, choices=MaintenanceType.choices)
    maintenance_date = models.DateField()
    next_due_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    performed_by = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_equipment_maintenance"
        ordering = ["-maintenance_date"]

    def __str__(self):
        return f"Maintenance: {self.equipment.name} ({self.maintenance_date})"


class HealthStaffTraining(models.Model):
    """Health staff training records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_staff_training")
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="health_training")
    training_name = models.CharField(max_length=200)
    training_type = models.CharField(max_length=100, blank=True)
    provider = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    hours = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    certificate_url = models.URLField(max_length=500, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_staff_training"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.staff_member.full_name} - {self.training_name}"


class HealthAudit(models.Model):
    """Health audits."""

    class AuditType(models.TextChoices):
        COMPLIANCE = "compliance", "Compliance"
        QUALITY = "quality", "Quality"
        SAFETY = "safety", "Safety"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="health_audits")
    audit_type = models.CharField(max_length=20, choices=AuditType.choices)
    title = models.CharField(max_length=200)
    audit_date = models.DateField()
    auditor = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    report_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "health_audits"
        ordering = ["-audit_date"]

    def __str__(self):
        return f"Audit: {self.title} ({self.audit_date})"
