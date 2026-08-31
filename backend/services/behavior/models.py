"""Behavior Management — Incidents, points, consequences, interventions, PBIS."""

import uuid

from django.db import models
from django.utils import timezone
from services.auth.models import School, User
from services.students.models import Student


class BehaviorCategory(models.Model):
    """Predefined behavior categories for consistent tracking."""

    class CategoryType(models.TextChoices):
        POSITIVE = "positive", "Positive"
        NEGATIVE = "negative", "Negative"
        NEUTRAL = "neutral", "Neutral"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_categories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category_type = models.CharField(max_length=10, choices=CategoryType.choices, default=CategoryType.POSITIVE)
    points_value = models.IntegerField(default=0, help_text="Points awarded/deducted (positive/negative)")
    is_active = models.BooleanField(default=True)
    requires_incident = models.BooleanField(default=False, help_text="Does this category require an incident report?")
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code for display")
    icon = models.CharField(max_length=50, blank=True, help_text="Icon identifier")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "behavior_categories"
        ordering = ["category_type", "name"]
        unique_together = [("school", "name")]

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Incident(models.Model):
    """Incident reporting and tracking."""

    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="incidents")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="incidents")
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reported_incidents")
    category = models.ForeignKey(
        BehaviorCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="incidents"
    )
    incident_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MEDIUM)
    description = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now, help_text="When the incident occurred")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    resolution = models.TextField(blank=True)
    # Notification settings
    parents_notified = models.BooleanField(default=False)
    parents_notified_at = models.DateTimeField(null=True, blank=True)
    # Follow-up
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "incidents"
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.incident_type} - {self.student} ({self.get_severity_display()})"


class Referral(models.Model):
    """Referrals to staff for behavior incidents."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIONED = "actioned", "Actioned"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="referrals")
    referred_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_referrals")
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_referrals")
    reason = models.TextField()
    action_taken = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "referrals"

    def __str__(self):
        return f"Referral: {self.incident} -> {self.referred_to}"


class BehaviorPoint(models.Model):
    """PBIS positive behavior points system."""

    class PointType(models.TextChoices):
        EARNED = "earned", "Earned"
        DEDUCTED = "deducted", "Deducted"
        ADJUSTED = "adjusted", "Adjusted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_points")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="behavior_points")
    category = models.ForeignKey(
        BehaviorCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="points"
    )
    points = models.IntegerField(help_text="Positive to award, negative to deduct")
    point_type = models.CharField(max_length=10, choices=PointType.choices, default=PointType.EARNED)
    reason = models.TextField()
    awarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="awarded_points")
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True, related_name="points")
    # Redemption
    is_redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "behavior_points"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "created_at"]),
            models.Index(fields=["school", "created_at"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.points} points ({self.get_point_type_display()})"


class BehaviorPointBalance(models.Model):
    """Current point balance for each student."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="point_balance")
    total_earned = models.PositiveIntegerField(default=0)
    total_deducted = models.PositiveIntegerField(default=0)
    current_balance = models.IntegerField(default=0)
    lifetime_earned = models.PositiveIntegerField(default=0)
    lifetime_deducted = models.PositiveIntegerField(default=0)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "behavior_point_balances"

    def __str__(self):
        return f"{self.student} - Balance: {self.current_balance}"

    def update_balance(self, points_change, point_type):
        """Update balance based on points earned/deducted."""
        if point_type == BehaviorPoint.PointType.EARNED:
            self.total_earned += abs(points_change)
            self.current_balance += abs(points_change)
            self.lifetime_earned += abs(points_change)
        elif point_type == BehaviorPoint.PointType.DEDUCTED:
            self.total_deducted += abs(points_change)
            self.current_balance -= abs(points_change)
            self.lifetime_deducted += abs(points_change)
        self.last_activity_at = timezone.now()
        self.save()


class BehaviorConsequence(models.Model):
    """Track consequences for negative behaviors."""

    class ConsequenceType(models.TextChoices):
        VERBAL_WARNING = "verbal_warning", "Verbal Warning"
        WRITTEN_WARNING = "written_warning", "Written Warning"
        DETENTION = "detention", "Detention"
        IN_SCHOOL_SUSPENSION = "in_school_suspension", "In-School Suspension"
        OUT_OF_SCHOOL_SUSPENSION = "out_of_school_suspension", "Out-of-School Suspension"
        EXPULSION = "expulsion", "Expulsion"
        COMMUNITY_SERVICE = "community_service", "Community Service"
        PARENT_MEETING = "parent_meeting", "Parent Meeting"
        LOSS_OF_PRIVILEGES = "loss_of_privileges", "Loss of Privileges"
        BEHAVIOR_CONTRACT = "behavior_contract", "Behavior Contract"
        COUNSELING = "counseling", "Counseling"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        APPEALED = "appealed", "Appealed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_consequences")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="consequences")
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="consequences")
    consequence_type = models.CharField(max_length=25, choices=ConsequenceType.choices)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Dates
    issued_date = models.DateField(default=timezone.now)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # Issued by
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="issued_consequences")
    # Details
    duration_hours = models.PositiveIntegerField(default=0, help_text="Duration in hours (for detention)")
    duration_days = models.PositiveIntegerField(default=0, help_text="Duration in days (for suspension)")
    location = models.CharField(max_length=100, blank=True)
    conditions = models.TextField(blank=True, help_text="Conditions for completion")
    notes = models.TextField(blank=True)
    # Parent notification
    parents_notified = models.BooleanField(default=False)
    parents_notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "behavior_consequences"
        ordering = ["-issued_date"]

    def __str__(self):
        return f"{self.student} - {self.get_consequence_type_display()} ({self.get_status_display()})"


class BehaviorMerit(models.Model):
    """Track merits for positive behavior recognition."""

    class MeritType(models.TextChoices):
        ACADEMIC = "academic", "Academic Excellence"
        CITIZENSHIP = "citizenship", "Good Citizenship"
        LEADERSHIP = "leadership", "Leadership"
        SERVICE = "service", "Community Service"
        IMPROVEMENT = "improvement", "Behavior Improvement"
        ATTENDANCE = "attendance", "Perfect Attendance"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_merits")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="merits")
    merit_type = models.CharField(max_length=20, choices=MeritType.choices, default=MeritType.CITIZENSHIP)
    title = models.CharField(max_length=200)
    description = models.TextField()
    points = models.PositiveIntegerField(default=0)
    awarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="awarded_merits")
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True, related_name="merits")
    # Recognition
    is_public = models.BooleanField(default=True, help_text="Show on school announcements")
    certificate_generated = models.BooleanField(default=False)
    awarded_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "behavior_merits"
        ordering = ["-awarded_date"]

    def __str__(self):
        return f"{self.student} - {self.title} ({self.get_merit_type_display()})"


class DetentionTracking(models.Model):
    """Schedule and track detentions."""

    class DetentionType(models.TextChoices):
        LUNCH = "lunch", "Lunch Detention"
        AFTER_SCHOOL = "after_school", "After-School Detention"
        IN_SCHOOL = "in_school", "In-School Detention"
        SATURDAY = "saturday", "Saturday Detention"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        MISSED = "missed", "Missed"
        EXCUSED = "excused", "Excused"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="detentions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="detentions")
    detention_type = models.CharField(max_length=20, choices=DetentionType.choices, default=DetentionType.AFTER_SCHOOL)
    consequence = models.ForeignKey(
        BehaviorConsequence, on_delete=models.SET_NULL, null=True, blank=True, related_name="detentions"
    )
    # Schedule
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    supervisor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="supervised_detentions"
    )
    # Attendance
    attended = models.BooleanField(default=False)
    attended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    # Parent
    parents_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "detention_tracking"
        ordering = ["scheduled_date", "start_time"]

    def __str__(self):
        return f"{self.student} - {self.get_detention_type_display()} on {self.scheduled_date}"


class SuspensionTracking(models.Model):
    """Track suspensions with dates and conditions."""

    class SuspensionType(models.TextChoices):
        IN_SCHOOL = "in_school", "In-School Suspension"
        OUT_OF_SCHOOL = "out_of_school", "Out-of-School Suspension"
        EXPULSION = "expulsion", "Expulsion"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        APPEALED = "appealed", "Appealed"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="suspensions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="suspensions")
    suspension_type = models.CharField(
        max_length=20, choices=SuspensionType.choices, default=SuspensionType.OUT_OF_SCHOOL
    )
    consequence = models.ForeignKey(
        BehaviorConsequence, on_delete=models.SET_NULL, null=True, blank=True, related_name="suspensions"
    )
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="suspensions")
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Conditions for return
    conditions_for_return = models.TextField(blank=True)
    meeting_required = models.BooleanField(default=False)
    meeting_date = models.DateField(null=True, blank=True)
    meeting_notes = models.TextField(blank=True)
    # Issued by
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="issued_suspensions")
    # Parent
    parents_notified = models.BooleanField(default=False)
    parents_notified_at = models.DateTimeField(null=True, blank=True)
    parent_signature_required = models.BooleanField(default=False)
    parent_signature_obtained = models.BooleanField(default=False)
    # Academic
    make_up_work_required = models.BooleanField(default=False)
    make_up_work_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "suspension_tracking"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.student} - {self.get_suspension_type_display()} ({self.start_date} to {self.end_date})"

    @property
    def duration_days(self):
        """Calculate suspension duration in days."""
        return (self.end_date - self.start_date).days + 1


class BehaviorContract(models.Model):
    """Document behavior agreements between school, student, and parents."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        VIOLATED = "violated", "Violated"
        TERMINATED = "terminated", "Terminated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_contracts")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="behavior_contracts")
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True, related_name="contracts")
    # Contract details
    title = models.CharField(max_length=200)
    description = models.TextField()
    goals = models.TextField(help_text="Specific goals and expectations")
    consequences_for_violation = models.TextField()
    rewards_for_compliance = models.TextField(blank=True)
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    review_dates = models.JSONField(default=list, blank=True, help_text="List of review dates")
    # Signatures
    student_signed = models.BooleanField(default=False)
    student_signed_at = models.DateTimeField(null=True, blank=True)
    parent_signed = models.BooleanField(default=False)
    parent_signed_at = models.DateTimeField(null=True, blank=True)
    administrator_signed = models.BooleanField(default=False)
    administrator_signed_at = models.DateTimeField(null=True, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    progress_notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_contracts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "behavior_contracts"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.student} - {self.title} ({self.get_status_display()})"


class WitnessStatement(models.Model):
    """Record witness accounts for incidents."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="witness_statements")
    # Witness info
    witness_type = models.CharField(
        max_length=20,
        choices=[("student", "Student"), ("staff", "Staff"), ("parent", "Parent"), ("other", "Other")],
        default="student",
    )
    witness_name = models.CharField(max_length=150)
    witness_student = models.ForeignKey(
        Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="witness_statements"
    )
    witness_contact = models.CharField(max_length=100, blank=True)
    # Statement
    statement = models.TextField()
    statement_date = models.DateField(default=timezone.now)
    # Collected by
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="collected_statements")
    # Metadata
    is_confidential = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "witness_statements"
        ordering = ["created_at"]

    def __str__(self):
        return f"Witness: {self.witness_name} on {self.incident}"


class BehaviorEvidence(models.Model):
    """Attach evidence (photos, documents) to incidents."""

    class EvidenceType(models.TextChoices):
        PHOTO = "photo", "Photo"
        VIDEO = "video", "Video"
        DOCUMENT = "document", "Document"
        AUDIO = "audio", "Audio"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name="evidence")
    evidence_type = models.CharField(max_length=10, choices=EvidenceType.choices, default=EvidenceType.DOCUMENT)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file_url = models.URLField(help_text="URL to uploaded file")
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    # Uploaded by
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="uploaded_evidence")
    # Metadata
    is_confidential = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "behavior_evidence"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.get_evidence_type_display()}: {self.title}"


class BehaviorRubric(models.Model):
    """Standardized scoring rubric for behavior evaluation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_rubrics")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # Scoring
    min_score = models.IntegerField(default=1)
    max_score = models.IntegerField(default=5)
    # Categories
    applies_to = models.JSONField(
        default=list, blank=True, help_text="List of behavior categories this rubric applies to"
    )
    # Settings
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_rubrics")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "behavior_rubrics"
        ordering = ["name"]

    def __str__(self):
        return self.name


class BehaviorRubricLevel(models.Model):
    """Individual levels within a rubric."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rubric = models.ForeignKey(BehaviorRubric, on_delete=models.CASCADE, related_name="levels")
    score = models.IntegerField()
    label = models.CharField(max_length=100)
    description = models.TextField()
    color = models.CharField(max_length=7, default="#007bff")

    class Meta:
        db_table = "behavior_rubric_levels"
        ordering = ["score"]
        unique_together = [("rubric", "score")]

    def __str__(self):
        return f"{self.rubric.name} - {self.score}: {self.label}"


class DigitalHallPass(models.Model):
    """Track student movement with digital hall passes."""

    class PassType(models.TextChoices):
        BATHROOM = "bathroom", "Bathroom"
        NURSE = "nurse", "Nurse"
        COUNSELOR = "counselor", "Counselor"
        ADMINISTRATION = "administration", "Administration"
        LIBRARY = "library", "Library"
        OTHER_CLASS = "other_class", "Other Class"
        OFFICE = "office", "Office"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        EXPIRED = "expired", "Expired"
        DENIED = "denied", "Denied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="hall_passes")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="hall_passes")
    pass_type = models.CharField(max_length=20, choices=PassType.choices, default=PassType.BATHROOM)
    # Class info
    from_class = models.CharField(max_length=100, blank=True)
    to_destination = models.CharField(max_length=100)
    # Teacher approval
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_hall_passes"
    )
    # Timing
    issued_at = models.DateTimeField(auto_now_add=True)
    expected_return_at = models.DateTimeField(null=True, blank=True)
    actual_return_at = models.DateTimeField(null=True, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Escalation
    is_late = models.BooleanField(default=False)
    minutes_late = models.PositiveIntegerField(default=0)
    # Notes
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "digital_hall_passes"
        ordering = ["-issued_at"]
        indexes = [
            models.Index(fields=["student", "issued_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.get_pass_type_display()} ({self.get_status_display()})"


class TardyTracking(models.Model):
    """Track tardiness with patterns and interventions."""

    class TardyType(models.TextChoices):
        EXCUSED = "excused", "Excused"
        UNEXCUSED = "unexcused", "Unexcused"
        MEDICAL = "medical", "Medical"
        FAMILY = "family", "Family Emergency"
        TRANSPORTATION = "transportation", "Transportation"

    class Status(models.TextChoices):
        RECORDED = "recorded", "Recorded"
        EXCUSED = "excused", "Excused"
        APPEALED = "appealed", "Appealed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="tardies")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="tardies")
    tardy_type = models.CharField(max_length=20, choices=TardyType.choices, default=TardyType.UNEXCUSED)
    # Timing
    date = models.DateField()
    scheduled_time = models.TimeField(help_text="When class was supposed to start")
    arrival_time = models.TimeField(help_text="When student actually arrived")
    minutes_late = models.PositiveIntegerField(default=0)
    # Class info
    class_name = models.CharField(max_length=100, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="recorded_tardies")
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.RECORDED)
    reason = models.TextField(blank=True)
    parent_contacted = models.BooleanField(default=False)
    # Patterns
    is_part_of_pattern = models.BooleanField(default=False)
    pattern_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tardy_tracking"
        ordering = ["-date", "arrival_time"]
        indexes = [
            models.Index(fields=["student", "date"]),
            models.Index(fields=["tardy_type"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.get_tardy_type_display()} on {self.date}"


class BehaviorGoal(models.Model):
    """Set and track behavior goals for students."""

    class GoalType(models.TextChoices):
        REDUCE_INCIDENTS = "reduce_incidents", "Reduce Incidents"
        IMPROVE_ATTENDANCE = "improve_attendance", "Improve Attendance"
        EARN_POINTS = "earn_points", "Earn Behavior Points"
        COMPLETE_CONSEQUENCE = "complete_consequence", "Complete Consequence"
        CUSTOM = "custom", "Custom Goal"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACHIEVED = "achieved", "Achieved"
        MISSED = "missed", "Missed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_goals")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="behavior_goals")
    goal_type = models.CharField(max_length=20, choices=GoalType.choices, default=GoalType.CUSTOM)
    title = models.CharField(max_length=200)
    description = models.TextField()
    # Target
    target_value = models.IntegerField(default=0, help_text="Target number to achieve")
    current_value = models.IntegerField(default=0, help_text="Current progress")
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Support
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_goals")
    support_plan = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "behavior_goals"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.student} - {self.title} ({self.get_status_display()})"

    @property
    def progress_percentage(self):
        """Calculate progress percentage."""
        if self.target_value > 0:
            return min(100, int((self.current_value / self.target_value) * 100))
        return 0


class BehaviorStreak(models.Model):
    """Track consecutive good behavior streaks."""

    class StreakType(models.TextChoices):
        NO_INCIDENTS = "no_incidents", "No Incidents"
        PERFECT_ATTENDANCE = "perfect_attendance", "Perfect Attendance"
        ON_TIME = "on_time", "On Time"
        POINTS_EARNED = "points_earned", "Points Earned"
        CUSTOM = "custom", "Custom"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="behavior_streaks")
    streak_type = models.CharField(max_length=20, choices=StreakType.choices, default=StreakType.NO_INCIDENTS)
    # Streak data
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    streak_unit = models.CharField(max_length=20, default="days", help_text="days, weeks, months")
    # Dates
    streak_started_at = models.DateField()
    last_activity_at = models.DateField()
    # Milestones
    milestone_7 = models.BooleanField(default=False, help_text="7-day/week milestone achieved")
    milestone_30 = models.BooleanField(default=False, help_text="30-day/month milestone achieved")
    milestone_90 = models.BooleanField(default=False, help_text="90-day/quarter milestone achieved")
    milestone_180 = models.BooleanField(default=False, help_text="180-day/semester milestone achieved")
    milestone_365 = models.BooleanField(default=False, help_text="365-day/year milestone achieved")
    # Rewards
    reward_earned = models.BooleanField(default=False)
    reward_description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "behavior_streaks"
        unique_together = [("student", "streak_type")]
        ordering = ["-current_streak"]

    def __str__(self):
        return f"{self.student} - {self.get_streak_type_display()}: {self.current_streak} {self.streak_unit}"

    def increment_streak(self):
        """Increment the current streak."""
        self.current_streak += 1
        self.last_activity_at = timezone.now().date()
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        # Check milestones
        if self.current_streak >= 7:
            self.milestone_7 = True
        if self.current_streak >= 30:
            self.milestone_30 = True
        if self.current_streak >= 90:
            self.milestone_90 = True
        if self.current_streak >= 180:
            self.milestone_180 = True
        if self.current_streak >= 365:
            self.milestone_365 = True
        self.save()

    def break_streak(self):
        """Break the current streak."""
        self.current_streak = 0
        self.streak_started_at = timezone.now().date()
        self.save()


class BehaviorAlert(models.Model):
    """Real-time alerts for critical incidents."""

    class AlertType(models.TextChoices):
        CRITICAL_INCIDENT = "critical_incident", "Critical Incident"
        PATTERN_DETECTED = "pattern_detected", "Pattern Detected"
        ESCALATION = "escalation", "Escalation"
        ATTENDANCE = "attendance", "Attendance Alert"
        PARENT_CONTACT = "parent_contact", "Parent Contact Required"
        FOLLOW_UP = "follow_up", "Follow-Up Required"
        OTHER = "other", "Other"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_alerts")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="behavior_alerts")
    alert_type = models.CharField(max_length=20, choices=AlertType.choices, default=AlertType.OTHER)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    # Alert content
    title = models.CharField(max_length=200)
    message = models.TextField()
    # Related objects
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts")
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    acknowledged_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="acknowledged_alerts"
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    # Notification
    notification_sent = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "behavior_alerts"
        ordering = ["-priority", "-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["student", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_priority_display()}: {self.title}"


class BehaviorAppeal(models.Model):
    """Students can appeal incidents and consequences."""

    class AppealType(models.TextChoices):
        INCIDENT = "incident", "Incident Appeal"
        CONSEQUENCE = "consequence", "Consequence Appeal"
        SUSPENSION = "suspension", "Suspension Appeal"

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under Review"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        WITHDRAWN = "withdrawn", "Withdrawn"

    class Decision(models.TextChoices):
        UPHELD = "upheld", "Original Decision Upheld"
        MODIFIED = "modified", "Decision Modified"
        OVERTURNED = "overturned", "Decision Overturned"
        REDUCED = "reduced", "Penalty Reduced"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_appeals")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="behavior_appeals")
    appeal_type = models.CharField(max_length=20, choices=AppealType.choices, default=AppealType.INCIDENT)
    # Related objects
    incident = models.ForeignKey(Incident, on_delete=models.SET_NULL, null=True, blank=True, related_name="appeals")
    consequence = models.ForeignKey(
        BehaviorConsequence, on_delete=models.SET_NULL, null=True, blank=True, related_name="appeals"
    )
    suspension = models.ForeignKey(
        SuspensionTracking, on_delete=models.SET_NULL, null=True, blank=True, related_name="appeals"
    )
    # Appeal details
    reason = models.TextField(help_text="Reason for appeal")
    supporting_evidence = models.TextField(blank=True)
    requested_outcome = models.TextField(blank=True)
    # Review
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SUBMITTED)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_appeals"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    decision = models.CharField(max_length=15, choices=Decision.choices, null=True, blank=True)
    decision_notes = models.TextField(blank=True)
    # Parent involvement
    parent_notified = models.BooleanField(default=False)
    parent_statement = models.TextField(blank=True)
    # Dates
    submitted_at = models.DateTimeField(auto_now_add=True)
    hearing_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "behavior_appeals"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student} - {self.get_appeal_type_display()} ({self.get_status_display()})"


class ParentNotification(models.Model):
    """Notify parents of behavior incidents and consequences."""

    class NotificationType(models.TextChoices):
        INCIDENT = "incident", "Incident Report"
        CONSEQUENCE = "consequence", "Consequence Notice"
        SUSPENSION = "suspension", "Suspension Notice"
        MEETING = "meeting", "Meeting Request"
        GOAL_UPDATE = "goal_update", "Goal Update"
        POSITIVE = "positive", "Positive Report"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"

    class DeliveryMethod(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push Notification"
        PHONE = "phone", "Phone Call"
        LETTER = "letter", "Letter"
        IN_APP = "in_app", "In-App Notification"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="parent_notifications")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="parent_notifications")
    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices, default=NotificationType.OTHER
    )
    delivery_method = models.CharField(max_length=10, choices=DeliveryMethod.choices, default=DeliveryMethod.EMAIL)
    # Related objects
    incident = models.ForeignKey(
        Incident, on_delete=models.SET_NULL, null=True, blank=True, related_name="parent_notifications"
    )
    consequence = models.ForeignKey(
        BehaviorConsequence, on_delete=models.SET_NULL, null=True, blank=True, related_name="parent_notifications"
    )
    # Content
    subject = models.CharField(max_length=200)
    message = models.TextField()
    # Recipient
    parent_email = models.EmailField(blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    # Response
    parent_response = models.TextField(blank=True)
    response_received_at = models.DateTimeField(null=True, blank=True)
    # Sent by
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sent_parent_notifications")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "parent_notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "notification_type"]),
            models.Index(fields=["student", "created_at"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.get_notification_type_display()} ({self.get_status_display()})"


class BehaviorAnalytics(models.Model):
    """Aggregated behavior analytics and reports."""

    class ReportType(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        ANNUAL = "annual", "Annual"
        CUSTOM = "custom", "Custom"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_analytics")
    report_type = models.CharField(max_length=15, choices=ReportType.choices, default=ReportType.WEEKLY)
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    # Incident stats
    total_incidents = models.PositiveIntegerField(default=0)
    incidents_by_severity = models.JSONField(default=dict, blank=True)
    incidents_by_type = models.JSONField(default=dict, blank=True)
    incidents_by_grade = models.JSONField(default=dict, blank=True)
    incidents_by_day = models.JSONField(default=dict, blank=True)
    # Points stats
    total_points_awarded = models.IntegerField(default=0)
    total_points_deducted = models.IntegerField(default=0)
    average_points_per_student = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Consequence stats
    total_consequences = models.PositiveIntegerField(default=0)
    consequences_by_type = models.JSONField(default=dict, blank=True)
    # Attendance impact
    total_suspension_days = models.PositiveIntegerField(default=0)
    total_detention_hours = models.PositiveIntegerField(default=0)
    # Top students
    top_earners = models.JSONField(default=list, blank=True)
    students_needing_support = models.JSONField(default=list, blank=True)
    # Trends
    comparison_to_previous = models.JSONField(default=dict, blank=True, help_text="Comparison to previous period")
    # Report metadata
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="generated_analytics")
    generated_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "behavior_analytics"
        ordering = ["-generated_at"]

    def __str__(self):
        return f"{self.get_report_type_display()} Report: {self.start_date} to {self.end_date}"


class BehaviorReward(models.Model):
    """Catalog of rewards available for point redemption."""

    class RewardType(models.TextChoices):
        PHYSICAL = "physical", "Physical Item"
        PRIVILEGE = "privilege", "Privilege"
        EXPERIENCE = "experience", "Experience"
        CERTIFICATE = "certificate", "Certificate"
        DIGITAL = "digital", "Digital"
        OTHER = "other", "Other"

    class Availability(models.TextChoices):
        ALWAYS = "always", "Always Available"
        LIMITED = "limited", "Limited Stock"
        SEASONAL = "seasonal", "Seasonal"
        EVENT = "event", "Event Only"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_rewards")
    name = models.CharField(max_length=200)
    description = models.TextField()
    reward_type = models.CharField(max_length=15, choices=RewardType.choices, default=RewardType.PRIVILEGE)
    # Cost
    points_cost = models.PositiveIntegerField(help_text="Points required to redeem")
    # Availability
    availability = models.CharField(max_length=15, choices=Availability.choices, default=Availability.ALWAYS)
    stock_quantity = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    max_per_student = models.PositiveIntegerField(default=0, help_text="0 = unlimited per student")
    # Redemption stats
    total_redeemed = models.PositiveIntegerField(default=0)
    # Media
    image_url = models.URLField(blank=True)
    # Schedule
    available_from = models.DateField(null=True, blank=True)
    available_until = models.DateField(null=True, blank=True)
    # Settings
    requires_approval = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_rewards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "behavior_rewards"
        ordering = ["points_cost", "name"]

    def __str__(self):
        return f"{self.name} ({self.points_cost} points)"

    @property
    def is_available(self):
        """Check if reward is currently available."""
        if not self.is_active:
            return False
        if self.stock_quantity > 0 and self.total_redeemed >= self.stock_quantity:
            return False
        from django.utils import timezone as tz

        today = tz.now().date()
        if self.available_from and today < self.available_from:
            return False
        if self.available_until and today > self.available_until:
            return False
        return True


class BehaviorPointsRedemption(models.Model):
    """Track point redemption history."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        FULFILLED = "fulfilled", "Fulfilled"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="point_redemptions")
    reward = models.ForeignKey(BehaviorReward, on_delete=models.CASCADE, related_name="redemptions")
    points_spent = models.PositiveIntegerField(help_text="Points spent on this redemption")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Approval
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_redemptions"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    # Fulfillment
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    fulfilled_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="fulfilled_redemptions"
    )
    # Notes
    notes = models.TextField(blank=True)
    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "behavior_points_redemptions"
        ordering = ["-redeemed_at"]

    def __str__(self):
        return f"{self.student} redeemed {self.reward} for {self.points_spent} points"


class BehaviorHouse(models.Model):
    """House system for school-wide competitions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_houses")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code")
    mascot = models.CharField(max_length=100, blank=True)
    # Leadership
    captain = models.ForeignKey(
        Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="house_captain_of"
    )
    vice_captain = models.ForeignKey(
        Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="house_vice_captain_of"
    )
    faculty_advisor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="house_advised"
    )
    # Stats
    total_points = models.IntegerField(default=0)
    member_count = models.PositiveIntegerField(default=0)
    # Settings
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "behavior_houses"
        ordering = ["-total_points", "name"]

    def __str__(self):
        return f"{self.name} ({self.total_points} points)"


class BehaviorHouseMember(models.Model):
    """Students assigned to houses."""

    class Role(models.TextChoices):
        CAPTAIN = "captain", "Captain"
        VICE_CAPTAIN = "vice_captain", "Vice Captain"
        MEMBER = "member", "Member"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    house = models.ForeignKey(BehaviorHouse, on_delete=models.CASCADE, related_name="members")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="house_memberships")
    role = models.CharField(max_length=15, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "behavior_house_members"
        unique_together = [("house", "student")]
        ordering = ["role", "-joined_at"]

    def __str__(self):
        return f"{self.student} in {self.house} ({self.get_role_display()})"


class BehaviorLeaderboard(models.Model):
    """School-wide/house leaderboards."""

    class LeaderboardType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        CLASS = "class", "Class"
        HOUSE = "house", "House"
        GRADE = "grade", "Grade"
        OVERALL = "overall", "Overall"

    class TimePeriod(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        SEMESTER = "semester", "Semester"
        ANNUAL = "annual", "Annual"
        ALL_TIME = "all_time", "All Time"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_leaderboards")
    name = models.CharField(max_length=200)
    leaderboard_type = models.CharField(
        max_length=15, choices=LeaderboardType.choices, default=LeaderboardType.INDIVIDUAL
    )
    time_period = models.CharField(max_length=15, choices=TimePeriod.choices, default=TimePeriod.MONTHLY)
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    # Data
    leaderboard_data = models.JSONField(default=list, blank=True, help_text="List of ranked entries")
    # Settings
    is_published = models.BooleanField(default=False)
    show_on_dashboard = models.BooleanField(default=True)
    # Stats
    total_entries = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_leaderboards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "behavior_leaderboards"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_leaderboard_type_display()})"

    def generate_leaderboard(self):
        """Generate leaderboard data based on type and period."""
        from django.db.models import Sum

        entries = []
        if self.leaderboard_type == self.LeaderboardType.INDIVIDUAL:
            students = (
                BehaviorPoint.objects.filter(
                    created_at__date__gte=self.start_date,
                    created_at__date__lte=self.end_date,
                    point_type=BehaviorPoint.PointType.EARNED,
                )
                .values("student__id", "student__user__first_name", "student__user__last_name")
                .annotate(total_points=Sum("points"))
                .order_by("-total_points")[:50]
            )
            for i, s in enumerate(students, 1):
                entries.append(
                    {
                        "rank": i,
                        "student_id": s["student__id"],
                        "name": f"{s['student__user__first_name']} {s['student__user__last_name']}",
                        "points": s["total_points"],
                    }
                )
        elif self.leaderboard_type == self.LeaderboardType.HOUSE:
            houses = BehaviorHouse.objects.filter(is_active=True).order_by("-total_points")
            for i, h in enumerate(houses, 1):
                entries.append(
                    {
                        "rank": i,
                        "house_id": str(h.id),
                        "name": h.name,
                        "points": h.total_points,
                        "color": h.color,
                    }
                )
        self.leaderboard_data = entries
        self.total_entries = len(entries)
        self.save(update_fields=["leaderboard_data", "total_entries"])
        return entries


class BehaviorReportCard(models.Model):
    """Periodic behavior summaries for parents."""

    class ReportPeriod(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        SEMESTER = "semester", "Semester"
        ANNUAL = "annual", "Annual"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATING = "generating", "Generating"
        COMPLETED = "completed", "Completed"
        SENT = "sent", "Sent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_report_cards")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="behavior_report_cards")
    report_period = models.CharField(max_length=15, choices=ReportPeriod.choices, default=ReportPeriod.MONTHLY)
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    # Stats
    total_incidents = models.PositiveIntegerField(default=0)
    total_merits = models.PositiveIntegerField(default=0)
    total_points_earned = models.IntegerField(default=0)
    total_points_deducted = models.IntegerField(default=0)
    net_points = models.IntegerField(default=0)
    total_detentions = models.PositiveIntegerField(default=0)
    total_suspensions = models.PositiveIntegerField(default=0)
    total_tardies = models.PositiveIntegerField(default=0)
    # Behavior scores
    behavior_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    behavior_trend = models.CharField(
        max_length=10,
        choices=[("improving", "Improving"), ("stable", "Stable"), ("declining", "Declining")],
        default="stable",
    )
    # Highlights
    strengths = models.JSONField(default=list, blank=True, help_text="List of strengths observed")
    areas_for_growth = models.JSONField(default=list, blank=True, help_text="Areas needing improvement")
    teacher_comments = models.TextField(blank=True)
    admin_comments = models.TextField(blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    generated_at = models.DateTimeField(null=True, blank=True)
    sent_to_parent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    # Generated by
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="generated_report_cards")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "behavior_report_cards"
        ordering = ["-start_date"]
        unique_together = [("student", "report_period", "start_date")]

    def __str__(self):
        return f"{self.student} - {self.get_report_period_display()} ({self.start_date} to {self.end_date})"

    def generate_report(self):
        """Generate report card data."""
        from django.db.models import Sum

        # Incidents
        incidents = Incident.objects.filter(
            student=self.student,
            occurred_at__date__gte=self.start_date,
            occurred_at__date__lte=self.end_date,
        )
        self.total_incidents = incidents.count()
        # Points
        points = BehaviorPoint.objects.filter(
            student=self.student,
            created_at__date__gte=self.start_date,
            created_at__date__lte=self.end_date,
        )
        self.total_points_earned = (
            points.filter(point_type=BehaviorPoint.PointType.EARNED).aggregate(total=Sum("points"))["total"] or 0
        )
        self.total_points_deducted = (
            points.filter(point_type=BehaviorPoint.PointType.DEDUCTED).aggregate(total=Sum("points"))["total"] or 0
        )
        self.net_points = self.total_points_earned - abs(self.total_points_deducted)
        # Merits
        self.total_merits = BehaviorMerit.objects.filter(
            student=self.student,
            awarded_date__gte=self.start_date,
            awarded_date__lte=self.end_date,
        ).count()
        # Detentions & Suspensions
        self.total_detentions = DetentionTracking.objects.filter(
            student=self.student,
            scheduled_date__gte=self.start_date,
            scheduled_date__lte=self.end_date,
        ).count()
        self.total_suspensions = SuspensionTracking.objects.filter(
            student=self.student,
            start_date__gte=self.start_date,
            start_date__lte=self.end_date,
        ).count()
        # Tardies
        self.total_tardies = TardyTracking.objects.filter(
            student=self.student,
            date__gte=self.start_date,
            date__lte=self.end_date,
        ).count()
        # Calculate behavior score (0-100)
        score = 100
        score -= self.total_incidents * 5
        score += self.total_merits * 2
        score += min(20, self.total_points_earned // 10)
        score -= self.total_detentions * 10
        score -= self.total_suspensions * 25
        score -= self.total_tardies * 2
        self.behavior_score = max(0, min(100, score))
        self.status = BehaviorReportCard.Status.COMPLETED
        self.generated_at = timezone.now()
        self.save()
        return self.behavior_score


class BehaviorInterventionPlan(models.Model):
    """Document behavior intervention plans (BIP) and functional behavior assessments (FBA)."""

    class PlanType(models.TextChoices):
        BIP = "bip", "Behavior Intervention Plan"
        FBA = "fba", "Functional Behavior Assessment"
        SAFETY_PLAN = "safety_plan", "Safety Plan"
        BEHAVIOR_SUPPORT = "behavior_support", "Behavior Support Plan"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        UNDER_REVIEW = "under_review", "Under Review"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    class ReviewFrequency(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_intervention_plans")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="intervention_plans")
    plan_type = models.CharField(max_length=20, choices=PlanType.choices, default=PlanType.BIP)
    # Plan details
    title = models.CharField(max_length=200)
    description = models.TextField()
    # FBA specific
    target_behavior = models.TextField(blank=True, help_text="Observable behavior to be changed")
    antecedents = models.TextField(blank=True, help_text="What happens before the behavior")
    behaviors = models.TextField(blank=True, help_text="The behavior itself")
    consequences = models.TextField(blank=True, help_text="What happens after the behavior")
    function_of_behavior = models.TextField(blank=True, help_text="Why the behavior occurs")
    # BIP specific
    prevention_strategies = models.TextField(blank=True)
    teaching_strategies = models.TextField(blank=True)
    reinforcement_strategies = models.TextField(blank=True)
    crisis_plan = models.TextField(blank=True)
    # Team
    team_members = models.JSONField(default=list, blank=True, help_text="List of team member names/roles")
    case_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_intervention_plans"
    )
    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    review_frequency = models.CharField(max_length=15, choices=ReviewFrequency.choices, default=ReviewFrequency.MONTHLY)
    next_review_date = models.DateField(null=True, blank=True)
    # Progress
    goals_met = models.JSONField(default=list, blank=True, help_text="List of achieved goals")
    goals_remaining = models.JSONField(default=list, blank=True, help_text="List of remaining goals")
    progress_notes = models.TextField(blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    # Signatures
    parent_signature_required = models.BooleanField(default=True)
    parent_signed = models.BooleanField(default=False)
    parent_signed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_intervention_plans"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "behavior_intervention_plans"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.student} - {self.get_plan_type_display()}: {self.title}"


class BehaviorMTSS(models.Model):
    """Multi-tiered support system (MTSS) tracking."""

    class TierLevel(models.TextChoices):
        TIER_1 = "tier_1", "Tier 1 - Universal"
        TIER_2 = "tier_2", "Tier 2 - Targeted"
        TIER_3 = "tier_3", "Tier 3 - Intensive"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        MONITORING = "monitoring", "Monitoring"
        PROGRESSING = "progressing", "Progressing"
        REFERRAL = "referral", "Referral"
        EXITED = "exited", "Exited"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_mtss")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="mtss_records")
    tier_level = models.CharField(max_length=10, choices=TierLevel.choices, default=TierLevel.TIER_1)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Reason
    referral_reason = models.TextField()
    referral_date = models.DateField(default=timezone.now)
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="mtss_referrals")
    # Interventions
    interventions = models.JSONField(default=list, blank=True, help_text="List of interventions applied")
    supports = models.JSONField(default=list, blank=True, help_text="List of supports provided")
    # Progress
    goals = models.JSONField(default=list, blank=True)
    progress_data = models.JSONField(default=list, blank=True, help_text="Data points tracking progress")
    baseline_date = models.DateField(null=True, blank=True)
    baseline_notes = models.TextField(blank=True)
    # Dates
    start_date = models.DateField(default=timezone.now)
    review_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # Team
    case_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="mtss_case_managed"
    )
    team_members = models.JSONField(default=list, blank=True)
    # Outcome
    outcome_notes = models.TextField(blank=True)
    outcome_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "behavior_mtss"
        ordering = ["-referral_date"]

    def __str__(self):
        return f"{self.student} - {self.get_tier_level_display()} ({self.get_status_display()})"


class SELCheckIn(models.Model):
    """Social-emotional learning check-ins for students."""

    class Mood(models.TextChoices):
        GREAT = "great", "Great"
        GOOD = "good", "Good"
        OKAY = "okay", "Okay"
        SAD = "sad", "Sad"
        ANGRY = "angry", "Angry"
        ANXIOUS = "anxious", "Anxious"
        SICK = "sick", "Sick"

    class CheckInFrequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        AS_NEEDED = "as_needed", "As Needed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sel_checkins")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="sel_checkins")
    # Check-in data
    mood = models.CharField(max_length=10, choices=Mood.choices)
    energy_level = models.PositiveSmallIntegerField(default=5, help_text="1-10 scale")
    stress_level = models.PositiveSmallIntegerField(default=5, help_text="1-10 scale")
    # Optional details
    how_are_you_feeling = models.TextField(blank=True, help_text="Why do you feel this way?")
    anything_else = models.TextField(blank=True)
    needs_help = models.BooleanField(default=False)
    help_type = models.CharField(max_length=100, blank=True, help_text="What kind of help?")
    # Wellness indicators
    sleep_quality = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-10 scale")
    ate_breakfast = models.BooleanField(null=True, blank=True)
    # Response
    staff_response = models.TextField(blank=True)
    responded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sel_responses"
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    follow_up_needed = models.BooleanField(default=False)
    follow_up_completed = models.BooleanField(default=False)
    # Metadata
    check_in_date = models.DateField(default=timezone.now)
    check_in_time = models.TimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sel_checkins"
        ordering = ["-check_in_date", "-check_in_time"]
        indexes = [
            models.Index(fields=["student", "check_in_date"]),
            models.Index(fields=["mood"]),
        ]

    def __str__(self):
        return f"{self.student} - {self.get_mood_display()} on {self.check_in_date}"


class SELCheckInResponse(models.Model):
    """Staff responses to SEL check-ins."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    check_in = models.ForeignKey(SELCheckIn, on_delete=models.CASCADE, related_name="staff_responses")
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sel_checkin_responses")
    response = models.TextField()
    action_taken = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sel_checkin_responses"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.staff} responded to {self.check_in}"


class BehaviorStaffDashboard(models.Model):
    """Teacher-specific behavior dashboard data."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="behavior_staff_dashboards")
    staff = models.OneToOneField(User, on_delete=models.CASCADE, related_name="behavior_dashboard")
    # Today's stats
    incidents_today = models.PositiveIntegerField(default=0)
    points_given_today = models.IntegerField(default=0)
    referrals_received_today = models.PositiveIntegerField(default=0)
    hall_passes_active = models.PositiveIntegerField(default=0)
    # This week
    incidents_this_week = models.PositiveIntegerField(default=0)
    points_given_this_week = models.IntegerField(default=0)
    # Class stats
    class_points_data = models.JSONField(default=list, blank=True, help_text="Points by class period")
    top_students = models.JSONField(default=list, blank=True)
    students_needing_attention = models.JSONField(default=list, blank=True)
    # Alerts
    pending_alerts = models.PositiveIntegerField(default=0)
    pending_referrals = models.PositiveIntegerField(default=0)
    # Quick actions
    recent_actions = models.JSONField(default=list, blank=True, help_text="Recent behavior actions taken")
    # Settings
    favorite_quick_actions = models.JSONField(default=list, blank=True)
    # Timestamps
    last_refreshed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "behavior_staff_dashboards"

    def __str__(self):
        return f"Dashboard for {self.staff.full_name}"

    def refresh_data(self):
        """Refresh dashboard data."""
        from datetime import date, timedelta

        from django.db.models import Sum

        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        # Today's stats
        self.incidents_today = Incident.objects.filter(reported_by=self.staff, occurred_at__date=today).count()
        self.points_given_today = (
            BehaviorPoint.objects.filter(awarded_by=self.staff, created_at__date=today).aggregate(total=Sum("points"))[
                "total"
            ]
            or 0
        )
        self.referrals_received_today = Referral.objects.filter(referred_to=self.staff, created_at__date=today).count()
        self.hall_passes_active = DigitalHallPass.objects.filter(
            approved_by=self.staff, status=DigitalHallPass.Status.ACTIVE
        ).count()
        # This week
        self.incidents_this_week = Incident.objects.filter(
            reported_by=self.staff, occurred_at__date__gte=week_start
        ).count()
        self.points_given_this_week = (
            BehaviorPoint.objects.filter(awarded_by=self.staff, created_at__date__gte=week_start).aggregate(
                total=Sum("points")
            )["total"]
            or 0
        )
        # Pending items
        self.pending_alerts = BehaviorAlert.objects.filter(status=BehaviorAlert.Status.ACTIVE).count()
        self.pending_referrals = Referral.objects.filter(referred_to=self.staff, status="pending").count()
        self.save()
        return self
