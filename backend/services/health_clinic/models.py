"""Health / Clinic Management — Student health records, visits, immunizations, medications."""

import uuid
from django.db import models
from services.auth.models import School, User


class HealthRecord(models.Model):
    """Student health record with medical conditions and allergies."""

    class BloodType(models.TextChoices):
        A_POS = "A+", "A+"; A_NEG = "A-", "A-"; B_POS = "B+", "B+"; B_NEG = "B-", "B-"
        AB_POS = "AB+", "AB+"; AB_NEG = "AB-", "AB-"; O_POS = "O+", "O+"; O_NEG = "O-", "O-"; UNKNOWN = "unknown", "Unknown"

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
    administered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="medication_admin")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "health_medication_logs"
        ordering = ["-time_administered"]
    def __str__(self):
        return f"{self.student} - {self.medication_name} ({self.dosage})"
