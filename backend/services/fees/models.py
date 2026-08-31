"""
Fees Service — Fee structure, invoicing, payments, and receipts
"""

import uuid

from django.db import models
from services.auth.models import School, User
from services.students.models import AcademicYear, Grade, Student


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
    receipt_number = models.CharField(max_length=30, unique=True)
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
        return f"Installment {self.installment_number} - {self.student}"


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
