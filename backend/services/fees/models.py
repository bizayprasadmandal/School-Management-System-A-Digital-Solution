"""
Fees Service — Fee structure, invoicing, payments, and receipts
"""

import uuid
from django.db import models
from services.auth.models import User, School
from services.students.models import Student, AcademicYear, Grade


class FeeCategory(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_categories")
    name = models.CharField(max_length=100)         # Tuition, Transport, Hostel, etc.
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(default=True)
    is_recurring = models.BooleanField(default=True)
    recurrence = models.CharField(
        max_length=20,
        choices=[("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual"), ("one_time", "One Time")],
        default="monthly",
    )

    class Meta:
        db_table = "fee_categories"

    def __str__(self):
        return f"{self.name} ({self.school.code})"


class FeeStructure(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_structures")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_day = models.PositiveSmallIntegerField(default=10)   # day of month
    late_fee_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "fee_structures"
        unique_together = [("academic_year", "grade", "fee_category")]


class FeeInvoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        UNPAID = "unpaid", "Unpaid"
        PARTIAL = "partial", "Partially Paid"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        WAIVED = "waived", "Waived"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=30, unique=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="invoices")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    due_date = models.DateField()
    base_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    late_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.UNPAID)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_invoices"
        indexes = [models.Index(fields=["student", "status"]), models.Index(fields=["due_date", "status"])]

    @property
    def outstanding_amount(self):
        return self.total_amount - self.paid_amount

    def __str__(self):
        return f"INV-{self.invoice_number} | {self.student} | {self.total_amount}"


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CARD = "card", "Credit/Debit Card"
        CHEQUE = "cheque", "Cheque"
        ONLINE = "online", "Online Gateway"
        MOBILE = "mobile", "Mobile Money"
        KHALTI = "khalti", "Khalti"
        ESEWA = "esewa", "eSewa"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESSFUL = "successful", "Successful"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    transaction_id = models.CharField(max_length=255, blank=True)
    gateway_response = models.JSONField(default=dict)
    receipt_number = models.CharField(max_length=30, unique=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"

    def __str__(self):
        return f"PAY-{self.receipt_number} | {self.amount} [{self.status}]"


class Scholarship(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="scholarships")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="scholarships")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    discount_type = models.CharField(
        max_length=10, choices=[("percent", "Percentage"), ("fixed", "Fixed Amount")]
    )
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    applies_to_categories = models.ManyToManyField(FeeCategory, blank=True)
    reason = models.TextField()
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "scholarships"
