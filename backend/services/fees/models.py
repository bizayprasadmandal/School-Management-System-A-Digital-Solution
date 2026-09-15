"""
Fees Service — Fee structure, invoicing, payments, and receipts
"""

import uuid

from django.db import models
from services.auth.models import School, User
from services.students.models import AcademicYear, Grade, Student, StudentCategory


class FeeCategory(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_categories")
    name = models.CharField(max_length=100)  # Tuition, Transport, Hostel, etc.
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
    due_day = models.PositiveSmallIntegerField(default=10)  # day of month
    late_fee_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "fee_structures"
        unique_together = [("academic_year", "grade", "fee_category")]

    def __str__(self):
        return f"{self.grade} — {self.fee_category.name} ({self.amount})"


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
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["student", "academic_year"]),
            models.Index(fields=["due_date", "status"]),
        ]

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
    transaction_id = models.CharField(max_length=255, blank=True, db_index=True)
    gateway_response = models.JSONField(default=dict)
    receipt_number = models.CharField(max_length=30, unique=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    receipt_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the payment receipt notification was sent (set once per successful payment)",
    )
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="collected_payments")
    refunded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="refunded_payments",
        help_text="Admin who initiated the refund",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        indexes = [
            models.Index(fields=["status", "paid_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RCPT-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"PAY-{self.receipt_number} | {self.amount} [{self.status}]"


class Scholarship(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="scholarships")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="scholarships")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    discount_type = models.CharField(max_length=10, choices=[("percent", "Percentage"), ("fixed", "Fixed Amount")])
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    applies_to_categories = models.ManyToManyField(FeeCategory, blank=True)
    reason = models.TextField()
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "scholarships"

    def __str__(self):
        return f"{self.name} — {self.student} ({self.discount_type})"


class PaymentGatewayConfig(models.Model):
    """
    Per-school configuration for which payment gateways are enabled.
    Only one config row per school.
    """

    school = models.OneToOneField(
        School,
        on_delete=models.CASCADE,
        related_name="payment_gateway_config",
        primary_key=True,
    )
    stripe_enabled = models.BooleanField(default=True, help_text="Enable Stripe (credit/debit card) payments")
    khalti_enabled = models.BooleanField(default=False, help_text="Enable Khalti wallet payments")
    esewa_enabled = models.BooleanField(default=False, help_text="Enable eSewa wallet payments")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_gateway_config"

    def __str__(self):
        enabled = []
        if self.stripe_enabled:
            enabled.append("Stripe")
        if self.khalti_enabled:
            enabled.append("Khalti")
        if self.esewa_enabled:
            enabled.append("eSewa")
        return f"{self.school.code}: {', '.join(enabled) or 'No gateways enabled'}"


# =============================================================================
# Installment Plans
# =============================================================================


class InstallmentPlan(models.Model):
    """Split fees into monthly installments."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        DEFAULTED = "defaulted", "Defaulted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="installment_plans")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="installment_plans")
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name="installment_plans")
    # Plan Details
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    number_of_installments = models.PositiveSmallIntegerField()
    installment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Settings
    late_fee_per_installment = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    grace_period_days = models.PositiveSmallIntegerField(default=0)
    # Metadata
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "installment_plans"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.number_of_installments} installments"


class InstallmentPayment(models.Model):
    """Individual installment payments."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        WAIVED = "waived", "Waived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    installment_plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name="payments")
    installment_number = models.PositiveSmallIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    late_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "installment_payments"
        ordering = ["installment_number"]
        unique_together = [("installment_plan", "installment_number")]

    def __str__(self):
        return f"Installment {self.installment_number} - {self.installment_plan.student}"


# =============================================================================
# Sibling Discounts
# =============================================================================


class SiblingDiscount(models.Model):
    """Auto-apply discounts for siblings."""

    class DiscountType(models.TextChoices):
        PERCENT = "percent", "Percentage"
        FIXED = "fixed", "Fixed Amount"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sibling_discounts")
    name = models.CharField(max_length=100)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    # Conditions
    min_siblings = models.PositiveSmallIntegerField(default=2, help_text="Minimum siblings required")
    applies_to_categories = models.ManyToManyField(FeeCategory, blank=True)
    # Status
    is_active = models.BooleanField(default=True)
    priority = models.PositiveSmallIntegerField(default=0, help_text="Higher priority applied first")
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sibling_discounts"
        ordering = ["-priority"]

    def __str__(self):
        return self.name


# =============================================================================
# Payment Reminders
# =============================================================================


class PaymentReminder(models.Model):
    """Automated payment reminders."""

    class ReminderType(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push Notification"
        IN_APP = "in_app", "In-App"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="payment_reminders")
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name="reminders")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="payment_reminders")
    # Reminder Details
    reminder_type = models.CharField(max_length=10, choices=ReminderType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_reminders"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.student} - {self.get_reminder_type_display()}"


# =============================================================================
# Fee Concessions
# =============================================================================


class FeeConcession(models.Model):
    """Concessions for eligible students."""

    class ConcessionType(models.TextChoices):
        SIBLING = "sibling", "Sibling Discount"
        STAFF_WARD = "staff_ward", "Staff Ward"
        MERIT = "merit", "Merit-Based"
        NEED_BASED = "need_based", "Need-Based"
        GOVERNMENT = "government", "Government Scheme"
        SPORTS = "sports", "Sports Achievement"
        CULTURAL = "cultural", "Cultural Achievement"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_concessions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_concessions")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    # Concession Details
    concession_type = models.CharField(max_length=15, choices=ConcessionType.choices)
    name = models.CharField(max_length=200)
    discount_type = models.CharField(max_length=10, choices=[("percent", "Percentage"), ("fixed", "Fixed Amount")])
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    # Conditions
    applies_to_categories = models.ManyToManyField(FeeCategory, blank=True)
    max_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True, help_text="Maximum concession amount"
    )
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    # Dates
    valid_from = models.DateField()
    valid_until = models.DateField()
    # Documentation
    supporting_documents = models.JSONField(default=list, help_text="List of document URLs")
    reason = models.TextField()
    notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_concessions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.student}"


# =============================================================================
# Revenue Reports
# =============================================================================


class RevenueReport(models.Model):
    """Financial insights and reports."""

    class ReportType(models.TextChoices):
        DAILY = "daily", "Daily Collection"
        WEEKLY = "weekly", "Weekly Collection"
        MONTHLY = "monthly", "Monthly Collection"
        QUARTERLY = "quarterly", "Quarterly Collection"
        ANNUAL = "annual", "Annual Collection"
        CATEGORY_WISE = "category", "Category-wise Report"
        GRADE_WISE = "grade", "Grade-wise Report"
        OUTSTANDING = "outstanding", "Outstanding Dues"
        DEFAULTERS = "defaulters", "Defaulters Report"
        SCHOLARSHIP = "scholarship", "Scholarship Report"
        REFUND = "refund", "Refund Report"
        CUSTOM = "custom", "Custom Report"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATED = "generated", "Generated"
        SENT = "sent", "Sent"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="revenue_reports")
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=15, choices=ReportType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    # Report Period
    period_start = models.DateField()
    period_end = models.DateField()
    # Report Content
    summary = models.TextField(blank=True)
    findings = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)
    # Financial Data
    total_collected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_outstanding = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_refunded = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_scholarships = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_concessions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Breakdown
    collection_by_category = models.JSONField(default=dict)
    collection_by_grade = models.JSONField(default=dict)
    collection_by_payment_method = models.JSONField(default=dict)
    # Personnel
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "revenue_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# =============================================================================
# Fee Collection Dashboard
# =============================================================================


class FeeCollectionDashboard(models.Model):
    """Real-time collection dashboard data."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_dashboards")
    # Collection Stats
    total_expected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_collected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_outstanding = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    collection_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Category Breakdown
    collected_by_category = models.JSONField(default=dict)
    outstanding_by_category = models.JSONField(default=dict)
    # Grade Breakdown
    collected_by_grade = models.JSONField(default=dict)
    outstanding_by_grade = models.JSONField(default=dict)
    # Payment Method Breakdown
    collected_by_method = models.JSONField(default=dict)
    # Trends
    daily_collection = models.JSONField(default=list, help_text="Last 30 days collection")
    monthly_collection = models.JSONField(default=list, help_text="Last 12 months collection")
    # Defaulters
    total_defaulters = models.PositiveIntegerField(default=0)
    total_overdue_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fee_collection_dashboards"

    def __str__(self):
        return f"Dashboard: {self.school.code} - {self.last_updated}"


# =============================================================================
# Fee Adjustments
# =============================================================================


class FeeAdjustment(models.Model):
    """Adjust fees for specific students."""

    class AdjustmentType(models.TextChoices):
        DISCOUNT = "discount", "Discount"
        SURCHARGE = "surcharge", "Surcharge"
        WAIVER = "waiver", "Fee Waiver"
        PENALTY = "penalty", "Penalty"
        CREDIT = "credit", "Credit"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_adjustments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_adjustments")
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name="adjustments")
    # Adjustment Details
    adjustment_type = models.CharField(max_length=10, choices=AdjustmentType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="approved_fee_adjustments")
    approved_at = models.DateTimeField(null=True, blank=True)
    # Dates
    adjustment_date = models.DateField()
    # Metadata
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_fee_adjustments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fee_adjustments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.get_adjustment_type_display()} ({self.amount})"


# =============================================================================
# Advance Payments
# =============================================================================


class AdvancePayment(models.Model):
    """Record advance payments."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPLIED = "applied", "Applied"
        REFUNDED = "refunded", "Refunded"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="advance_payments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="advance_payments")
    # Payment Details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="advance_payments")
    # Application
    applied_to_invoice = models.ForeignKey(FeeInvoice, on_delete=models.SET_NULL, null=True, blank=True)
    applied_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Dates
    payment_date = models.DateField()
    applied_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "advance_payments"
        ordering = ["-payment_date"]

    def __str__(self):
        return f"{self.student} - {self.amount} ({self.get_status_display()})"


# =============================================================================
# Fee Waivers
# =============================================================================


class FeeWaiver(models.Model):
    """Waive fees for special cases."""

    class WaiverType(models.TextChoices):
        FULL = "full", "Full Waiver"
        PARTIAL = "partial", "Partial Waiver"
        CATEGORY = "category", "Category Waiver"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        APPLIED = "applied", "Applied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_waivers")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_waivers")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    # Waiver Details
    waiver_type = models.CharField(max_length=10, choices=WaiverType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Amount to waive")
    applies_to_categories = models.ManyToManyField(FeeCategory, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    # Dates
    valid_from = models.DateField()
    valid_until = models.DateField()
    # Documentation
    reason = models.TextField(help_text="Reason for waiver")
    supporting_documents = models.JSONField(default=list)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_waivers"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.get_waiver_type_display()} ({self.amount})"


# =============================================================================
# Student Ledger
# =============================================================================


class StudentLedger(models.Model):
    """Complete financial ledger per student."""

    class TransactionType(models.TextChoices):
        INVOICE = "invoice", "Invoice Generated"
        PAYMENT = "payment", "Payment Received"
        ADJUSTMENT = "adjustment", "Fee Adjustment"
        SCHOLARSHIP = "scholarship", "Scholarship Applied"
        CONCESSION = "concession", "Concession Applied"
        WAIVER = "waiver", "Fee Waiver"
        REFUND = "refund", "Refund"
        LATE_FEE = "late_fee", "Late Fee"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_ledgers")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student_ledgers")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    # Transaction Details
    transaction_type = models.CharField(max_length=15, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    # Reference
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.SET_NULL, null=True, blank=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    # Dates
    transaction_date = models.DateField()
    # Metadata
    reference_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "student_ledgers"
        ordering = ["-transaction_date", "-created_at"]
        indexes = [
            models.Index(fields=["student", "academic_year", "transaction_date"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.get_transaction_type_display()} ({self.amount})"


# =============================================================================
# Fee Templates
# =============================================================================


class FeeTemplate(models.Model):
    """Reusable fee templates."""

    class TemplateType(models.TextChoices):
        TUITION = "tuition", "Tuition Fee"
        TRANSPORT = "transport", "Transport Fee"
        HOSTEL = "hostel", "Hostel Fee"
        LAB = "lab", "Lab Fee"
        LIBRARY = "library", "Library Fee"
        SPORTS = "sports", "Sports Fee"
        EXAMINATION = "exam", "Examination Fee"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_templates")
    name = models.CharField(max_length=100)
    template_type = models.CharField(max_length=15, choices=TemplateType.choices)
    description = models.TextField(blank=True)
    # Template Details
    default_amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_recurring = models.BooleanField(default=True)
    recurrence = models.CharField(
        max_length=20,
        choices=[("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual"), ("one_time", "One Time")],
        default="monthly",
    )
    # Settings
    is_mandatory = models.BooleanField(default=True)
    late_fee_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_templates"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =============================================================================
# Bulk Invoice Generation
# =============================================================================


class BulkInvoiceGeneration(models.Model):
    """Generate invoices in bulk."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        PARTIAL = "partial", "Partially Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="bulk_invoices")
    # Batch Details
    batch_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Filters
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    grades = models.ManyToManyField(Grade, blank=True)
    fee_categories = models.ManyToManyField(FeeCategory, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Statistics
    total_students = models.PositiveIntegerField(default=0)
    total_invoices_generated = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    errors = models.JSONField(default=list, help_text="List of errors")
    # Personnel
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Dates
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "bulk_invoice_generations"
        ordering = ["-initiated_at"]

    def __str__(self):
        return f"{self.batch_name} ({self.get_status_display()})"


# =============================================================================
# Payment Reconciliation
# =============================================================================


class PaymentReconciliation(models.Model):
    """Auto-reconcile payments."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        DISCREPANCIES = "discrepancies", "Has Discrepancies"

    class ReconciliationType(models.TextChoices):
        DAILY = "daily", "Daily Reconciliation"
        WEEKLY = "weekly", "Weekly Reconciliation"
        MONTHLY = "monthly", "Monthly Reconciliation"
        MANUAL = "manual", "Manual Reconciliation"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="payment_reconciliations")
    # Reconciliation Details
    reconciliation_type = models.CharField(max_length=10, choices=ReconciliationType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Period
    period_start = models.DateField()
    period_end = models.DateField()
    # Results
    total_expected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_matched = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_unmatched = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    match_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    # Discrepancies
    discrepancies = models.JSONField(default=list, help_text="List of discrepancies found")
    discrepancy_count = models.PositiveIntegerField(default=0)
    # Personnel
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_reconciliations"
    )
    # Dates
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    notes = models.TextField(blank=True)
    report_url = models.URLField(blank=True)

    class Meta:
        db_table = "payment_reconciliations"
        ordering = ["-initiated_at"]

    def __str__(self):
        return f"Reconciliation: {self.period_start} - {self.period_end} ({self.get_status_display()})"


class BudgetPlan(models.Model):
    """Budget planning and forecasting."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="budget_plans")
    academic_year = models.ForeignKey("students.AcademicYear", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    total_budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    allocated = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    spent = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_budget_plans"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.academic_year})"


class BudgetLineItem(models.Model):
    """Individual budget line items."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    budget_plan = models.ForeignKey(BudgetPlan, on_delete=models.CASCADE, related_name="line_items")
    category = models.ForeignKey(FeeCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=200)
    budgeted_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    variance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fee_budget_line_items"
        ordering = ["budget_plan", "description"]

    def __str__(self):
        return f"{self.description} - {self.budgeted_amount}"


class ExpenseTracking(models.Model):
    """Expense tracking."""

    class ExpenseType(models.TextChoices):
        SALARY = "salary", "Salary"
        UTILITY = "utility", "Utility"
        MAINTENANCE = "maintenance", "Maintenance"
        SUPPLIES = "supplies", "Supplies"
        TRANSPORT = "transport", "Transport"
        EVENT = "event", "Event"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="expenses")
    expense_type = models.CharField(max_length=20, choices=ExpenseType.choices)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    vendor = models.CharField(max_length=200, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    expense_date = models.DateField()
    category = models.ForeignKey(FeeCategory, on_delete=models.SET_NULL, null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=[("pending", "Pending"), ("approved", "Approved"), ("paid", "Paid")], default="pending"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_expenses"
        ordering = ["-expense_date"]

    def __str__(self):
        return f"{self.description} - {self.amount}"


class RefundRecord(models.Model):
    """Refund tracking."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        PROCESSED = "processed", "Processed"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="refunds")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="fee_refunds")
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    processed_date = models.DateField(null=True, blank=True)
    refund_method = models.CharField(max_length=50, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_refunds"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Refund: {self.student} - {self.amount}"


class LateFeeRule(models.Model):
    """Late fee automation rules."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="late_fee_rules")
    name = models.CharField(max_length=100)
    days_after_due = models.PositiveSmallIntegerField(help_text="Days after due date to apply late fee")
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_type = models.CharField(
        max_length=20, choices=[("fixed", "Fixed"), ("percentage", "Percentage")], default="fixed"
    )
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="Percentage of invoice amount"
    )
    max_late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    applies_to = models.CharField(
        max_length=20, choices=[("all", "All Students"), ("specific", "Specific Categories")], default="all"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_late_fee_rules"
        ordering = ["days_after_due"]

    def __str__(self):
        return f"{self.name} - {self.days_after_due} days"


class FeeDiscount(models.Model):
    """Fee discounts."""

    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FIXED = "fixed", "Fixed Amount"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_discounts")
    name = models.CharField(max_length=200)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    applies_to = models.CharField(
        max_length=20, choices=[("all", "All Students"), ("category", "Student Category"), ("grade", "Grade Level")]
    )
    grade = models.ForeignKey("students.Grade", on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(StudentCategory, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_discounts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.value}"


class FeeExemption(models.Model):
    """Fee exemptions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_exemptions")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="fee_exemptions")
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField()
    exemption_type = models.CharField(
        max_length=20, choices=[("full", "Full Exemption"), ("partial", "Partial Exemption")], default="full"
    )
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    documents = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_exemptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Exemption: {self.student} - {self.get_exemption_type_display()}"


class InvoiceTemplate(models.Model):
    """Reusable invoice templates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="invoice_templates")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    header_text = models.TextField(blank=True)
    footer_text = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    logo_url = models.URLField(max_length=500, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_invoice_templates"
        ordering = ["-is_default", "name"]

    def __str__(self):
        return self.name


class ReceiptTemplate(models.Model):
    """Reusable receipt templates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="receipt_templates")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    header_text = models.TextField(blank=True)
    footer_text = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_receipt_templates"
        ordering = ["-is_default", "name"]

    def __str__(self):
        return self.name


class AccountingEntry(models.Model):
    """Accounting entries."""

    class EntryType(models.TextChoices):
        DEBIT = "debit", "Debit"
        CREDIT = "credit", "Credit"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="accounting_entries")
    entry_type = models.CharField(max_length=20, choices=EntryType.choices)
    account_code = models.CharField(max_length=50)
    account_name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.CharField(max_length=255, blank=True)
    entry_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fee_accounting_entries"
        ordering = ["-entry_date"]

    def __str__(self):
        return f"{self.get_entry_type_display()}: {self.account_name} - {self.amount}"


class FinancialAudit(models.Model):
    """Financial audit trails."""

    class AuditType(models.TextChoices):
        INTERNAL = "internal", "Internal Audit"
        EXTERNAL = "external", "External Audit"
        TAX = "tax", "Tax Audit"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        FINDINGS = "findings", "Findings Reported"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="financial_audits")
    audit_type = models.CharField(max_length=20, choices=AuditType.choices)
    title = models.CharField(max_length=200)
    audit_period_start = models.DateField()
    audit_period_end = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    auditor_name = models.CharField(max_length=200, blank=True)
    auditor_organization = models.CharField(max_length=200, blank=True)
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_income = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discrepancies = models.JSONField(default=list, blank=True)
    report_url = models.URLField(max_length=500, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_financial_audits"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_audit_type_display()})"


class StudentFinancialAccount(models.Model):
    """Student financial accounts."""

    class AccountType(models.TextChoices):
        REGULAR = "regular", "Regular"
        SCHOLARSHIP = "scholarship", "Scholarship"
        FINANCIAL_AID = "financial_aid", "Financial Aid"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="student_financial_accounts")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_financial_accounts")
    account_type = models.CharField(max_length=20, choices=AccountType.choices, default=AccountType.REGULAR)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_outstanding = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    last_payment_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_student_accounts"
        unique_together = [("student", "school")]

    def __str__(self):
        return f"{self.student} - Balance: {self.balance}"


class ParentAccount(models.Model):
    """Parent financial accounts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey("students.ParentProfile", on_delete=models.CASCADE, related_name="parent_accounts")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="parent_accounts")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_outstanding = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, blank=True)
    auto_pay_enabled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_parent_accounts"
        unique_together = [("parent", "school")]

    def __str__(self):
        return f"Parent Account - Balance: {self.balance}"


class BankReconciliation(models.Model):
    """Bank reconciliation records."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        MATCHED = "matched", "Matched"
        UNMATCHED = "unmatched", "Unmatched"
        ADJUSTED = "adjusted", "Adjusted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="bank_reconciliations")
    bank_statement_date = models.DateField()
    statement_balance = models.DecimalField(max_digits=12, decimal_places=2)
    book_balance = models.DecimalField(max_digits=12, decimal_places=2)
    difference = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    matched_transactions = models.JSONField(default=list, blank=True)
    unmatched_transactions = models.JSONField(default=list, blank=True)
    adjustments = models.JSONField(default=list, blank=True)
    reconciled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_bank_reconciliations"
        ordering = ["-bank_statement_date"]

    def __str__(self):
        return f"Bank Reconciliation - {self.bank_statement_date}"


class PaymentMethod(models.Model):
    """Payment methods configuration."""

    class MethodType(models.TextChoices):
        CASH = "cash", "Cash"
        CHEQUE = "cheque", "Cheque"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        ONLINE = "online", "Online Payment"
        CARD = "card", "Card Payment"
        MOBILE = "mobile", "Mobile Payment"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="payment_methods")
    name = models.CharField(max_length=100)
    method_type = models.CharField(max_length=20, choices=MethodType.choices)
    description = models.TextField(blank=True)
    processing_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    processing_fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_payment_methods"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_method_type_display()})"


class TransactionLog(models.Model):
    """Transaction logs."""

    class TransactionType(models.TextChoices):
        PAYMENT = "payment", "Payment"
        REFUND = "refund", "Refund"
        ADJUSTMENT = "adjustment", "Adjustment"
        LATE_FEE = "late_fee", "Late Fee"
        WAIVER = "waiver", "Waiver"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transaction_logs")
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    transaction_id = models.CharField(max_length=100, unique=True)
    student = models.ForeignKey("students.Student", on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20, choices=[("success", "Success"), ("failed", "Failed"), ("pending", "Pending")], default="success"
    )
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fee_transaction_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.transaction_id} - {self.get_transaction_type_display()} ({self.amount})"


class CreditNote(models.Model):
    """Credit notes."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        APPLIED = "applied", "Applied"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="credit_notes")
    note_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="credit_notes")
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    issued_date = models.DateField()
    applied_date = models.DateField(null=True, blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_credit_notes"
        ordering = ["-issued_date"]

    def __str__(self):
        return f"Credit Note {self.note_number} - {self.amount}"


class DebitNote(models.Model):
    """Debit notes."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        APPLIED = "applied", "Applied"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="debit_notes")
    note_number = models.CharField(max_length=50, unique=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="debit_notes")
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    issued_date = models.DateField()
    applied_date = models.DateField(null=True, blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_debit_notes"
        ordering = ["-issued_date"]

    def __str__(self):
        return f"Debit Note {self.note_number} - {self.amount}"


class FinancialYear(models.Model):
    """Financial year settings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="financial_years")
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False)
    closed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    closed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_financial_years"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"


class FeeWaiverApproval(models.Model):
    """Fee waiver approval workflow."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="fee_waiver_approvals")
    waiver = models.ForeignKey(FeeWaiver, on_delete=models.CASCADE, related_name="approvals")
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="waiver_approvals")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    comments = models.TextField(blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fee_waiver_approvals"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Waiver Approval - {self.approver} ({self.get_status_display()})"
