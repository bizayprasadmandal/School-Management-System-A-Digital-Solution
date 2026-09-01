"""
Counseling Service — Models for counseling appointments and student referrals.
"""

import uuid

from django.db import models
from django.utils import timezone
from services.auth.models import School, User
from services.students.models import Student


class CounselingAppointment(models.Model):
    """A scheduled counseling session between a counselor and a student."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    class AppointmentType(models.TextChoices):
        ACADEMIC = "academic", "Academic Counseling"
        CAREER = "career", "Career Guidance"
        PERSONAL = "personal", "Personal / Emotional"
        BEHAVIORAL = "behavioral", "Behavioral Intervention"
        COLLEGE = "college", "College Preparation"
        GROUP = "group", "Group Session"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_appointments")
    counselor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="counseling_appointments",
        limit_choices_to={"role": "counselor"},
        help_text="The counselor conducting the session",
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="counseling_appointments",
    )
    appointment_type = models.CharField(
        max_length=20,
        choices=AppointmentType.choices,
        default=AppointmentType.ACADEMIC,
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True,
    )
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=30, help_text="Duration in minutes")
    location = models.CharField(max_length=100, blank=True, help_text="Room or virtual meeting link")
    reason = models.TextField(blank=True, help_text="Reason for the appointment")
    notes = models.TextField(blank=True, help_text="Counselor's session notes (post-session)")
    follow_up_needed = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_appointments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counseling_appointments"
        ordering = ["-scheduled_date", "-scheduled_time"]
        indexes = [
            models.Index(fields=["school", "counselor", "status"]),
            models.Index(fields=["student", "status"]),
            models.Index(fields=["scheduled_date"]),
        ]
        verbose_name = "Counseling Appointment"
        verbose_name_plural = "Counseling Appointments"

    def __str__(self):
        return (
            f"{self.get_appointment_type_display()} — "
            f"{self.student.user.full_name} & {self.counselor.full_name} "
            f"({self.scheduled_date})"
        )


class StudentReferral(models.Model):
    """A referral from a teacher/admin to a counselor for student support."""

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Review"
        UNDER_REVIEW = "under_review", "Under Review"
        CONTACTED = "contacted", "Student Contacted"
        ACTIONED = "actioned", "Action Taken"
        CLOSED = "closed", "Closed"
        DECLINED = "declined", "Declined"

    class ReferralCategory(models.TextChoices):
        ACADEMIC = "academic", "Academic Concern"
        ATTENDANCE = "attendance", "Attendance Issue"
        BEHAVIOR = "behavior", "Behavioral Concern"
        EMOTIONAL = "emotional", "Emotional / Mental Health"
        FAMILY = "family", "Family / Home Issue"
        SOCIAL = "social", "Social / Peer Issue"
        SAFETY = "safety", "Safety Concern"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_referrals")
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="referrals",
    )
    referred_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="counseling_referrals_created",
        help_text="Teacher or admin who created the referral",
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="counseling_referrals_assigned",
        limit_choices_to={"role": "counselor"},
        help_text="Counselor assigned to handle this referral",
    )
    category = models.CharField(
        max_length=15,
        choices=ReferralCategory.choices,
        default=ReferralCategory.ACADEMIC,
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    reason = models.TextField(help_text="Reason for the referral")
    notes = models.TextField(blank=True, help_text="Additional notes and observations")
    intervention_plan = models.TextField(blank=True, help_text="Proposed intervention plan")
    outcome = models.TextField(blank=True, help_text="Outcome after action taken")
    action_taken_at = models.DateTimeField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    is_confidential = models.BooleanField(default=False, help_text="Restrict visibility to counselors and admins")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_referrals"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "status", "priority"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["student"]),
        ]
        verbose_name = "Student Referral"
        verbose_name_plural = "Student Referrals"

    def __str__(self):
        return (
            f"{self.get_category_display()} referral — " f"{self.student.user.full_name} ({self.get_status_display()})"
        )


class CounselorProfile(models.Model):
    """Extended counselor profile — additional professional information."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="counselor_profile")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counselor_profiles")
    specialties = models.TextField(
        blank=True, help_text="Areas of specialization, e.g. career counseling, academic advising, mental health"
    )
    certifications = models.TextField(blank=True, help_text="Professional certifications and licenses")
    office_hours = models.TextField(blank=True, help_text="Regular office hours and availability")
    bio = models.TextField(blank=True, help_text="Professional biography")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counselor_profiles"
        verbose_name = "Counselor Profile"
        verbose_name_plural = "Counselor Profiles"

    def __str__(self):
        return f"{self.user.full_name} — Counselor Profile"


# =============================================================================
# NEW MODELS: Counseling Sessions
# =============================================================================


class CounselingSession(models.Model):
    """Detailed session notes and documentation."""

    class SessionType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual Session"
        GROUP = "group", "Group Session"
        FAMILY = "family", "Family Session"
        CRISIS = "crisis", "Crisis Intervention"
        FOLLOW_UP = "follow_up", "Follow-up Session"
        ASSESSMENT = "assessment", "Assessment Session"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_sessions")
    appointment = models.ForeignKey(
        CounselingAppointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions"
    )
    counselor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="counselor_sessions", limit_choices_to={"role": "counselor"}
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="counseling_sessions")
    session_type = models.CharField(max_length=15, choices=SessionType.choices, default=SessionType.INDIVIDUAL)
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=30)
    # Content
    presenting_issue = models.TextField(blank=True, help_text="Primary issue discussed")
    session_summary = models.TextField(blank=True, help_text="Summary of session content")
    interventions_used = models.TextField(blank=True, help_text="Techniques or interventions applied")
    student_response = models.TextField(blank=True, help_text="Student's response to interventions")
    risk_assessment = models.TextField(blank=True, help_text="Current risk level and assessment")
    # Goals and Outcomes
    goals_addressed = models.TextField(blank=True, help_text="Goals addressed in this session")
    progress_notes = models.TextField(blank=True, help_text="Progress toward goals")
    # Follow-up
    follow_up_actions = models.TextField(blank=True, help_text="Next steps and action items")
    follow_up_date = models.DateField(null=True, blank=True)
    # Confidentiality
    is_confidential = models.BooleanField(default=True)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counseling_sessions"
        ordering = ["-session_date", "-start_time"]
        indexes = [
            models.Index(fields=["school", "counselor", "session_date"]),
            models.Index(fields=["student", "session_date"]),
        ]
        verbose_name = "Counseling Session"
        verbose_name_plural = "Counseling Sessions"

    def __str__(self):
        return f"{self.get_session_type_display()} — {self.student.user.full_name} ({self.session_date})"


class SessionAttachment(models.Model):
    """Attachments for counseling sessions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(CounselingSession, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="counseling/sessions/attachments/")
    file_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "session_attachments"

    def __str__(self):
        return f"{self.file_name} — {self.session}"


# =============================================================================
# NEW MODELS: Intervention Plans
# =============================================================================


class InterventionPlan(models.Model):
    """Track intervention plans and goals."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        DISCONTINUED = "discontinued", "Discontinued"

    class PlanType(models.TextChoices):
        ACADEMIC = "academic", "Academic Intervention"
        BEHAVIORAL = "behavioral", "Behavioral Intervention"
        SOCIAL_EMOTIONAL = "social_emotional", "Social-Emotional"
        MENTAL_HEALTH = "mental_health", "Mental Health"
        CRISIS = "crisis", "Crisis Intervention"
        CAREER = "career", "Career Planning"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="intervention_plans")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="counseling_intervention_plans")
    counselor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="counseling_managed_plans", limit_choices_to={"role": "counselor"}
    )
    plan_type = models.CharField(max_length=20, choices=PlanType.choices, default=PlanType.ACADEMIC)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    # Dates
    start_date = models.DateField()
    target_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    # Review
    review_frequency = models.CharField(max_length=20, blank=True, help_text="e.g., Weekly, Bi-weekly, Monthly")
    last_review_date = models.DateField(null=True, blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    # Referral
    referral = models.ForeignKey(
        StudentReferral, on_delete=models.SET_NULL, null=True, blank=True, related_name="intervention_plans"
    )
    # Outcomes
    outcome_summary = models.TextField(blank=True)
    is_effective = models.BooleanField(null=True, blank=True)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "intervention_plans"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "student", "status"]),
            models.Index(fields=["counselor", "status"]),
        ]
        verbose_name = "Intervention Plan"
        verbose_name_plural = "Intervention Plans"

    def __str__(self):
        return f"{self.title} — {self.student.user.full_name}"

    @property
    def completion_percentage(self):
        goals = self.goals.all()
        if not goals:
            return 0
        completed = goals.filter(is_completed=True).count()
        return round((completed / goals.count()) * 100, 2)


class InterventionGoal(models.Model):
    """Individual goals within an intervention plan."""

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        ACHIEVED = "achieved", "Achieved"
        PARTIALLY_ACHIEVED = "partially_achieved", "Partially Achieved"
        NOT_ACHIEVED = "not_achieved", "Not Achieved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intervention_plan = models.ForeignKey(InterventionPlan, on_delete=models.CASCADE, related_name="goals")
    description = models.TextField()
    measurable_outcome = models.TextField(blank=True, help_text="How success will be measured")
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "intervention_goals"
        ordering = ["order"]

    def __str__(self):
        return f"{self.description[:50]} — {self.get_status_display()}"


# =============================================================================
# NEW MODELS: Mental Health Screening
# =============================================================================


class MentalHealthScreening(models.Model):
    """Mental health screening tools (PHQ-9, GAD-7, etc.)."""

    class ScreeningType(models.TextChoices):
        PHQ9 = "phq9", "PHQ-9 (Depression)"
        GAD7 = "gad7", "GAD-7 (Anxiety)"
        PSS10 = "pss10", "PSS-10 (Stress)"
        AUDIT = "audit", "AUDIT (Alcohol)"
        YRBS = "yrbs", "YRBS (Youth Risk)"
        SDQ = "sdq", "SDQ (Strengths & Difficulties)"
        CUSTOM = "custom", "Custom Screening"

    class RiskLevel(models.TextChoices):
        LOW = "low", "Low Risk"
        MODERATE = "moderate", "Moderate Risk"
        MODERATELY_SEVERE = "moderately_severe", "Moderately Severe"
        SEVERE = "severe", "Severe Risk"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="mental_health_screenings")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="mental_health_screenings")
    screening_type = models.CharField(max_length=15, choices=ScreeningType.choices)
    administered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    administered_date = models.DateField()
    # Results
    total_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW)
    interpretation = models.TextField(blank=True, help_text="Professional interpretation of results")
    # Recommendations
    recommendations = models.TextField(blank=True)
    referral_needed = models.BooleanField(default=False)
    referred_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="screening_referrals"
    )
    # Follow-up
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_completed = models.BooleanField(default=False)
    # Consent
    consent_obtained = models.BooleanField(default=False)
    consent_date = models.DateField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mental_health_screenings"
        ordering = ["-administered_date"]
        indexes = [
            models.Index(fields=["school", "student", "screening_type"]),
            models.Index(fields=["risk_level"]),
        ]
        verbose_name = "Mental Health Screening"
        verbose_name_plural = "Mental Health Screenings"

    def __str__(self):
        return f"{self.get_screening_type_display()} — {self.student.user.full_name} ({self.administered_date})"


class ScreeningResponse(models.Model):
    """Student responses to screening questions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    screening = models.ForeignKey(MentalHealthScreening, on_delete=models.CASCADE, related_name="responses")
    question_number = models.PositiveIntegerField()
    question_text = models.TextField()
    response_value = models.PositiveIntegerField(default=0)
    response_text = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "screening_responses"
        ordering = ["question_number"]

    def __str__(self):
        return f"Q{self.question_number}: {self.response_value}"


# =============================================================================
# NEW MODELS: Crisis Intervention
# =============================================================================


class CrisisIntervention(models.Model):
    """Crisis intervention tracking."""

    class SeverityLevel(models.TextChoices):
        LOW = "low", "Low"
        MODERATE = "moderate", "Moderate"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        STABILIZED = "stabilized", "Stabilized"
        FOLLOW_UP = "follow_up", "Follow-up Required"
        RESOLVED = "resolved", "Resolved"
        REFERRED = "referred", "Referred to External"

    class CrisisType(models.TextChoices):
        SUICIDAL_IDEATION = "suicidal_ideation", "Suicidal Ideation"
        SELF_HARM = "self_harm", "Self-Harm"
        VIOLENCE = "violence", "Violence Threat"
        SUBSTANCE_ABUSE = "substance_abuse", "Substance Abuse"
        TRAUMA = "trauma", "Trauma Event"
        MELTDOWN = "meltdown", "Emotional Meltdown"
        OTHER = "other", "Other Crisis"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="crisis_interventions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="crisis_interventions")
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reported_crises")
    crisis_type = models.CharField(max_length=20, choices=CrisisType.choices)
    severity_level = models.CharField(max_length=10, choices=SeverityLevel.choices, default=SeverityLevel.MODERATE)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Description
    description = models.TextField(help_text="Description of the crisis situation")
    immediate_actions = models.TextField(blank=True, help_text="Actions taken immediately")
    # Assessment
    risk_to_self = models.BooleanField(default=False)
    risk_to_others = models.BooleanField(default=False)
    risk_level_assessment = models.TextField(blank=True)
    # Response
    responding_counselor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="responded_crises"
    )
    response_time = models.DateTimeField(null=True, blank=True)
    intervention_provided = models.TextField(blank=True)
    # Follow-up
    follow_up_needed = models.BooleanField(default=True)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    # External referrals
    external_referral = models.BooleanField(default=False)
    external_agency = models.CharField(max_length=200, blank=True)
    external_contact = models.CharField(max_length=200, blank=True)
    # Parent notification
    parent_notified = models.BooleanField(default=False)
    parent_notified_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crisis_interventions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "severity_level", "status"]),
            models.Index(fields=["student", "status"]),
        ]
        verbose_name = "Crisis Intervention"
        verbose_name_plural = "Crisis Interventions"

    def __str__(self):
        return f"{self.get_crisis_type_display()} — {self.student.user.full_name} ({self.get_severity_level_display()})"


class CrisisFollowUp(models.Model):
    """Follow-up actions for crisis interventions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    crisis = models.ForeignKey(CrisisIntervention, on_delete=models.CASCADE, related_name="follow_ups")
    counselor = models.ForeignKey(User, on_delete=models.CASCADE)
    follow_up_date = models.DateField()
    notes = models.TextField()
    student_status = models.CharField(max_length=50, blank=True)
    actions_taken = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "crisis_follow_ups"
        ordering = ["-follow_up_date"]

    def __str__(self):
        return f"Follow-up for {self.crisis} ({self.follow_up_date})"


# =============================================================================
# NEW MODELS: Progress Tracking
# =============================================================================


class ProgressTracking(models.Model):
    """Track student progress over time."""

    class Domain(models.TextChoices):
        ACADEMIC = "academic", "Academic"
        BEHAVIORAL = "behavioral", "Behavioral"
        SOCIAL = "social", "Social"
        EMOTIONAL = "emotional", "Emotional"
        ATTENDANCE = "attendance", "Attendance"
        CAREER = "career", "Career"
        OVERALL = "overall", "Overall"

    class Trend(models.TextChoices):
        IMPROVING = "improving", "Improving"
        STABLE = "stable", "Stable"
        DECLINING = "declining", "Declining"
        FLUCTUATING = "fluctuating", "Fluctuating"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="progress_tracking")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="progress_tracking")
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tracked_progress")
    domain = models.CharField(max_length=15, choices=Domain.choices, default=Domain.OVERALL)
    assessment_date = models.DateField()
    # Ratings (1-10 scale)
    current_rating = models.PositiveSmallIntegerField(default=5)
    previous_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    target_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    trend = models.CharField(max_length=15, choices=Trend.choices, default=Trend.STABLE)
    # Details
    observations = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    areas_for_growth = models.TextField(blank=True)
    interventions_applied = models.TextField(blank=True)
    # Source
    source = models.CharField(max_length=50, blank=True, help_text="e.g., Teacher feedback, Test scores, Self-report")
    # Related
    intervention_plan = models.ForeignKey(
        InterventionPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="progress_entries"
    )
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "progress_tracking"
        ordering = ["-assessment_date"]
        indexes = [
            models.Index(fields=["student", "domain", "assessment_date"]),
        ]
        verbose_name = "Progress Tracking"
        verbose_name_plural = "Progress Tracking"

    def __str__(self):
        return f"{self.get_domain_display()} — {self.student.user.full_name} ({self.assessment_date})"

    @property
    def rating_change(self):
        if self.previous_rating is None:
            return 0
        return self.current_rating - self.previous_rating


class ProgressMilestone(models.Model):
    """Milestones within progress tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    progress = models.ForeignKey(ProgressTracking, on_delete=models.CASCADE, related_name="milestones")
    description = models.CharField(max_length=200)
    target_date = models.DateField(null=True, blank=True)
    achieved = models.BooleanField(default=False)
    achieved_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "progress_milestones"
        ordering = ["target_date"]

    def __str__(self):
        return f"{self.description} — {'Achieved' if self.achieved else 'Pending'}"


# =============================================================================
# NEW MODELS: Parent Consent
# =============================================================================


class ParentConsent(models.Model):
    """Parent consent for counseling."""

    class ConsentType(models.TextChoices):
        GENERAL = "general", "General Counseling"
        MENTAL_HEALTH = "mental_health", "Mental Health Services"
        SCREENING = "screening", "Mental Health Screening"
        GROUP = "group", "Group Counseling"
        EXTERNAL_REFERRAL = "external_referral", "External Referral"
        CRISIS = "crisis", "Crisis Intervention"
        RECORDS_ACCESS = "records_access", "Records Access"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        GRANTED = "granted", "Granted"
        DENIED = "denied", "Denied"
        REVOKED = "revoked", "Revoked"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="parent_consents")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="parent_consents")
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="counseling_consents")
    consent_type = models.CharField(max_length=20, choices=ConsentType.choices, default=ConsentType.GENERAL)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Consent details
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    # Documentation
    consent_form = models.FileField(upload_to="counseling/consent_forms/", null=True, blank=True)
    signature = models.ImageField(upload_to="counseling/signatures/", null=True, blank=True)
    # Scope
    scope_description = models.TextField(blank=True, help_text="What the consent covers")
    restrictions = models.TextField(blank=True, help_text="Any restrictions on consent")
    # Withdrawal
    withdrawal_date = models.DateField(null=True, blank=True)
    withdrawal_reason = models.TextField(blank=True)
    # Metadata
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="recorded_consents")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "parent_consents"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "consent_type", "status"]),
        ]
        verbose_name = "Parent Consent"
        verbose_name_plural = "Parent Consents"

    def __str__(self):
        return f"{self.get_consent_type_display()} — {self.student.user.full_name} ({self.get_status_display()})"

    @property
    def is_valid(self):
        if self.status != self.Status.GRANTED:
            return False
        if self.expiry_date and timezone.now().date() > self.expiry_date:
            return False
        return True


# =============================================================================
# NEW MODELS: Group Sessions
# =============================================================================


class GroupSession(models.Model):
    """Group counseling sessions."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class GroupType(models.TextChoices):
        SOCIAL_SKILLS = "social_skills", "Social Skills"
        GRIEF = "grief", "Grief & Loss"
        ANGER_MANAGEMENT = "anger_management", "Anger Management"
        ANXIETY = "anxiety", "Anxiety Support"
        DEPRESSION = "depression", "Depression Support"
        BEHAVIORAL = "behavioral", "Behavioral Support"
        CAREER = "career", "Career Exploration"
        PEER_MEDIATION = "peer_mediation", "Peer Mediation"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="group_sessions")
    counselor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="led_group_sessions", limit_choices_to={"role": "counselor"}
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    group_type = models.CharField(max_length=20, choices=GroupType.choices, default=GroupType.OTHER)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    # Schedule
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    meeting_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    location = models.CharField(max_length=200, blank=True)
    recurrence = models.CharField(max_length=50, blank=True, help_text="e.g., Weekly, Bi-weekly")
    # Capacity
    max_participants = models.PositiveIntegerField(default=10)
    min_participants = models.PositiveIntegerField(default=3)
    current_participants = models.PositiveIntegerField(default=0)
    # Content
    goals = models.TextField(blank=True)
    curriculum = models.TextField(blank=True)
    materials_needed = models.TextField(blank=True)
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "group_sessions"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} ({self.get_group_type_display()})"

    @property
    def is_full(self):
        return self.current_participants >= self.max_participants

    @property
    def available_spots(self):
        return max(0, self.max_participants - self.current_participants)


class GroupSessionAttendance(models.Model):
    """Attendance tracking for group sessions."""

    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        EXCUSED = "excused", "Excused"
        LATE = "late", "Late"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_session = models.ForeignKey(GroupSession, on_delete=models.CASCADE, related_name="attendances")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="group_session_attendances")
    session_number = models.PositiveIntegerField(default=1)
    attended_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "group_session_attendances"
        unique_together = [("group_session", "student", "attended_date")]

    def __str__(self):
        return f"{self.student} — {self.group_session} ({self.attended_date})"


class GroupSessionMember(models.Model):
    """Members enrolled in a group session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_session = models.ForeignKey(GroupSession, on_delete=models.CASCADE, related_name="members")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="group_memberships")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "group_session_members"
        unique_together = [("group_session", "student")]

    def __str__(self):
        return f"{self.student} in {self.group_session}"


# =============================================================================
# NEW MODELS: Case Management
# =============================================================================


class CaseManagement(models.Model):
    """Comprehensive case management."""

    class CaseStatus(models.TextChoices):
        OPEN = "open", "Open"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        CLOSED = "closed", "Closed"
        REFERRED = "referred", "Referred"

    class CasePriority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_cases")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="counseling_cases")
    case_manager = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="managed_cases", limit_choices_to={"role": "counselor"}
    )
    case_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=CaseStatus.choices, default=CaseStatus.OPEN)
    priority = models.CharField(max_length=10, choices=CasePriority.choices, default=CasePriority.MEDIUM)
    # Description
    presenting_concerns = models.TextField(help_text="Primary concerns")
    background_information = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    risk_factors = models.TextField(blank=True)
    # Team
    team_members = models.ManyToManyField(User, blank=True, related_name="case_team_memberships")
    # Dates
    opened_date = models.DateField(auto_now_add=True)
    closed_date = models.DateField(null=True, blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    # Outcome
    outcome_summary = models.TextField(blank=True)
    is_successful = models.BooleanField(null=True, blank=True)
    # Referrals
    referral_source = models.CharField(max_length=100, blank=True)
    referrals_made = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "case_management"
        ordering = ["-opened_date"]
        indexes = [
            models.Index(fields=["school", "status", "priority"]),
            models.Index(fields=["case_manager", "status"]),
            models.Index(fields=["student", "status"]),
        ]
        verbose_name = "Case Management"
        verbose_name_plural = "Case Management"

    def __str__(self):
        return f"{self.case_number} — {self.title}"


class CaseNote(models.Model):
    """Notes within a case."""

    class NoteType(models.TextChoices):
        SESSION = "session", "Session Note"
        PHONE = "phone", "Phone Call"
        EMAIL = "email", "Email Communication"
        MEETING = "meeting", "Team Meeting"
        HOME_VISIT = "home_visit", "Home Visit"
        OBSERVATION = "observation", "Observation"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    case = models.ForeignKey(CaseManagement, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    note_type = models.CharField(max_length=15, choices=NoteType.choices, default=NoteType.OTHER)
    content = models.TextField()
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    is_confidential = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "case_notes"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.get_note_type_display()} — {self.case.case_number} ({self.date})"


# =============================================================================
# NEW MODELS: Counseling Outcomes
# =============================================================================


class CounselingOutcome(models.Model):
    """Track outcomes of counseling."""

    class OutcomeType(models.TextChoices):
        ACADEMIC = "academic", "Academic Outcome"
        BEHAVIORAL = "behavioral", "Behavioral Outcome"
        SOCIAL_EMOTIONAL = "social_emotional", "Social-Emotional Outcome"
        ATTENDANCE = "attendance", "Attendance Outcome"
        CAREER = "career", "Career Outcome"
        OVERALL = "overall", "Overall Outcome"

    class Rating(models.TextChoices):
        SIGNIFICANT_IMPROVEMENT = "significant_improvement", "Significant Improvement"
        MODERATE_IMPROVEMENT = "moderate_improvement", "Moderate Improvement"
        SLIGHT_IMPROVEMENT = "slight_improvement", "Slight Improvement"
        NO_CHANGE = "no_change", "No Change"
        DECLINE = "decline", "Decline"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_outcomes")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="counseling_outcomes")
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documented_outcomes")
    outcome_type = models.CharField(max_length=20, choices=OutcomeType.choices, default=OutcomeType.OVERALL)
    assessment_date = models.DateField()
    # Outcome
    rating = models.CharField(max_length=25, choices=Rating.choices, default=Rating.NO_CHANGE)
    description = models.TextField(help_text="Description of outcome")
    measurable_results = models.TextField(blank=True)
    # Sources
    data_sources = models.TextField(blank=True, help_text="Sources of outcome data")
    # Related
    intervention_plan = models.ForeignKey(
        InterventionPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="outcomes"
    )
    case = models.ForeignKey(CaseManagement, on_delete=models.SET_NULL, null=True, blank=True, related_name="outcomes")
    # Recommendations
    recommendations = models.TextField(blank=True)
    continuation_needed = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counseling_outcomes"
        ordering = ["-assessment_date"]

    def __str__(self):
        return f"{self.get_outcome_type_display()} — {self.student.user.full_name} ({self.get_rating_display()})"


# =============================================================================
# NEW MODELS: Counseling Reports
# =============================================================================


class CounselingReport(models.Model):
    """Reports and analytics."""

    class ReportType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual Student Report"
        GROUP = "group", "Group Report"
        DEPARTMENT = "department", "Department Report"
        SCHOOL = "school", "School-wide Report"
        PROGRAM = "program", "Program Evaluation"
        COMPLIANCE = "compliance", "Compliance Report"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        FINAL = "final", "Final"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_reports")
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=15, choices=ReportType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    # Period
    period_start = models.DateField()
    period_end = models.DateField()
    # Content
    summary = models.TextField(blank=True)
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    # Data
    total_students_served = models.PositiveIntegerField(default=0)
    total_sessions = models.PositiveIntegerField(default=0)
    total_referrals = models.PositiveIntegerField(default=0)
    report_data = models.JSONField(default=dict, blank=True)
    # File
    report_file = models.FileField(upload_to="counseling/reports/", null=True, blank=True)
    # Metadata
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counseling_reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"


# =============================================================================
# NEW MODELS: Counselor Availability
# =============================================================================


class CounselorAvailability(models.Model):
    """Counselor availability and scheduling."""

    class DayOfWeek(models.TextChoices):
        MONDAY = "monday", "Monday"
        TUESDAY = "tuesday", "Tuesday"
        WEDNESDAY = "wednesday", "Wednesday"
        THURSDAY = "thursday", "Thursday"
        FRIDAY = "friday", "Friday"
        SATURDAY = "saturday", "Saturday"
        SUNDAY = "sunday", "Sunday"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="availability_slots")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counselor_availability")
    day_of_week = models.CharField(max_length=10, choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    location = models.CharField(max_length=100, blank=True)
    session_type = models.CharField(max_length=50, blank=True, help_text="Type of sessions available")
    max_appointments = models.PositiveIntegerField(default=5)
    notes = models.TextField(blank=True)
    effective_from = models.DateField(null=True, blank=True)
    effective_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counselor_availability"
        ordering = ["day_of_week", "start_time"]
        verbose_name = "Counselor Availability"
        verbose_name_plural = "Counselor Availability"

    def __str__(self):
        return f"{self.counselor.full_name} — {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"

    @property
    def duration_hours(self):
        from datetime import datetime

        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        delta = end - start
        return delta.total_seconds() / 3600


class CounselorAbsence(models.Model):
    """Track counselor absences."""

    class AbsenceType(models.TextChoices):
        SICK = "sick", "Sick Leave"
        PERSONAL = "personal", "Personal Leave"
        PROFESSIONAL_DEVELOPMENT = "pd", "Professional Development"
        CONFERENCE = "conference", "Conference"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="counselor_absences")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counselor_absences")
    absence_type = models.CharField(max_length=20, choices=AbsenceType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    appointments_affected = models.PositiveIntegerField(default=0)
    students_notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "counselor_absences"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.counselor.full_name} — {self.get_absence_type_display()} ({self.start_date})"


# =============================================================================
# NEW MODELS: Counseling Feedback
# =============================================================================


class CounselingFeedback(models.Model):
    """Student/parent feedback on counseling."""

    class FeedbackType(models.TextChoices):
        STUDENT = "student", "Student Feedback"
        PARENT = "parent", "Parent Feedback"
        TEACHER = "teacher", "Teacher Feedback"

    class SatisfactionLevel(models.TextChoices):
        VERY_SATISFIED = "very_satisfied", "Very Satisfied"
        SATISFIED = "satisfied", "Satisfied"
        NEUTRAL = "neutral", "Neutral"
        DISSATISFIED = "dissatisfied", "Dissatisfied"
        VERY_DISSATISFIED = "very_dissatisfied", "Very Dissatisfied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_feedback")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="counseling_feedback")
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_feedback")
    feedback_type = models.CharField(max_length=10, choices=FeedbackType.choices, default=FeedbackType.STUDENT)
    # Ratings
    overall_satisfaction = models.CharField(max_length=20, choices=SatisfactionLevel.choices)
    helpfulness_rating = models.PositiveSmallIntegerField(default=5, help_text="Rating from 1-10")
    communication_rating = models.PositiveSmallIntegerField(default=5, help_text="Rating from 1-10")
    professionalism_rating = models.PositiveSmallIntegerField(default=5, help_text="Rating from 1-10")
    # Feedback
    what_went_well = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    additional_comments = models.TextField(blank=True)
    would_recommend = models.BooleanField(null=True, blank=True)
    # Related
    session = models.ForeignKey(
        CounselingSession, on_delete=models.SET_NULL, null=True, blank=True, related_name="feedback"
    )
    group_session = models.ForeignKey(
        GroupSession, on_delete=models.SET_NULL, null=True, blank=True, related_name="feedback"
    )
    # Anonymous option
    is_anonymous = models.BooleanField(default=False)
    # Metadata
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "counseling_feedback"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_feedback_type_display()} — {self.student.user.full_name}"

    @property
    def average_rating(self):
        ratings = [self.helpfulness_rating, self.communication_rating, self.professionalism_rating]
        return round(sum(ratings) / len(ratings), 2)


# =============================================================================
# NEW MODELS: Career Counseling
# =============================================================================


class CareerAssessment(models.Model):
    """Career assessment tools and results (e.g. Holland Code, MBTI)."""

    class AssessmentType(models.TextChoices):
        HOLLAND_CODE = "holland_code", "Holland Code (RIASEC)"
        MBTI = "mbti", "Myers-Briggs Type"
        CLIFTON_STRENGTHS = "clifton", "CliftonStrengths"
        STRONG_INTEREST = "strong", "Strong Interest Inventory"
        SKILLS_APTITUDE = "skills", "Skills & Aptitude Test"
        VALUES_INVENTORY = "values", "Values Inventory"
        CUSTOM = "custom", "Custom Assessment"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="career_assessments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="career_assessments")
    assessment_type = models.CharField(max_length=20, choices=AssessmentType.choices)
    administered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    administered_date = models.DateField()
    # Results
    result_summary = models.TextField(blank=True, help_text="Overall result summary")
    result_data = models.JSONField(default=dict, blank=True, help_text="Structured result data")
    recommended_careers = models.JSONField(default=list, blank=True, help_text="List of recommended careers")
    recommended_fields = models.JSONField(default=list, blank=True, help_text="Recommended study fields")
    # Recommendations
    recommendations = models.TextField(blank=True)
    counselor_notes = models.TextField(blank=True)
    # File
    report_file = models.FileField(upload_to="counseling/career_assessments/", null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "career_assessments"
        ordering = ["-administered_date"]
        indexes = [
            models.Index(fields=["school", "student"]),
        ]
        verbose_name = "Career Assessment"
        verbose_name_plural = "Career Assessments"

    def __str__(self):
        return f"{self.get_assessment_type_display()} — {self.student.user.full_name} ({self.administered_date})"


class CareerGoal(models.Model):
    """Student career goals and aspirations."""

    class GoalStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        ACHIEVED = "achieved", "Achieved"
        CHANGED = "changed", "Goal Changed"
        ABANDONED = "abandoned", "Abandoned"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="career_goals")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="career_goals")
    counselor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="guided_career_goals")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_field = models.CharField(max_length=100, blank=True, help_text="Target career field")
    target_university = models.CharField(max_length=200, blank=True)
    target_program = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=GoalStatus.choices, default=GoalStatus.ACTIVE)
    action_steps = models.TextField(blank=True)
    resources_needed = models.TextField(blank=True)
    timeline = models.TextField(blank=True)
    progress_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "career_goals"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} — {self.student.user.full_name}"


class CollegeApplication(models.Model):
    """Track college/university applications."""

    class Status(models.TextChoices):
        RESEARCHING = "researching", "Researching"
        PREPARING = "preparing", "Preparing"
        SUBMITTED = "submitted", "Submitted"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        WAITLISTED = "waitlisted", "Waitlisted"
        ENROLLED = "enrolled", "Enrolled"
        DECLINED = "declined", "Declined by Student"

    class DegreeType(models.TextChoices):
        BACHELORS = "bachelors", "Bachelor's Degree"
        MASTERS = "masters", "Master's Degree"
        ASSOCIATE = "associate", "Associate's Degree"
        DIPLOMA = "diploma", "Diploma/Certificate"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="college_applications")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="college_applications")
    counselor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="supervised_applications")
    university_name = models.CharField(max_length=200)
    program_name = models.CharField(max_length=200, blank=True)
    degree_type = models.CharField(max_length=15, choices=DegreeType.choices, default=DegreeType.BACHELORS)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.RESEARCHING)
    # Dates
    application_deadline = models.DateField(null=True, blank=True)
    application_submitted_date = models.DateField(null=True, blank=True)
    decision_date = models.DateField(null=True, blank=True)
    enrollment_deadline = models.DateField(null=True, blank=True)
    # Financial
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    scholarship_offered = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    financial_aid_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    # Requirements
    sat_score = models.PositiveIntegerField(null=True, blank=True)
    act_score = models.PositiveIntegerField(null=True, blank=True)
    gpa_required = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    essays_completed = models.BooleanField(default=False)
    letters_of_rec_sent = models.BooleanField(default=False)
    # Notes
    notes = models.TextField(blank=True)
    counselor_recommendation = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "college_applications"
        ordering = ["application_deadline"]
        indexes = [
            models.Index(fields=["student", "status"]),
        ]
        verbose_name = "College Application"
        verbose_name_plural = "College Applications"

    def __str__(self):
        return f"{self.university_name} — {self.student.user.full_name} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Workshop & Program Management
# =============================================================================


class CounselingWorkshop(models.Model):
    """Workshops and programs run by counseling department."""

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class WorkshopType(models.TextChoices):
        ORIENTATION = "orientation", "Student Orientation"
        PARENT_WORKSHOP = "parent", "Parent Workshop"
        STRESS_MANAGEMENT = "stress", "Stress Management"
        BULLYING_PREVENTION = "bullying", "Bullying Prevention"
        COLLEGE_PREP = "college_prep", "College Preparation"
        FINANCIAL_LITERACY = "financial", "Financial Literacy"
        MENTAL_HEALTH_AWARENESS = "mental_health", "Mental Health Awareness"
        CAREER_EXPLORATION = "career", "Career Exploration"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_workshops")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_workshops")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    workshop_type = models.CharField(max_length=20, choices=WorkshopType.choices, default=WorkshopType.OTHER)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PLANNED)
    # Schedule
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    # Capacity
    max_participants = models.PositiveIntegerField(default=30)
    current_participants = models.PositiveIntegerField(default=0)
    # Target audience
    target_grades = models.CharField(max_length=100, blank=True, help_text="Comma-separated grades")
    target_audience = models.CharField(max_length=50, blank=True, help_text="Students, Parents, Teachers")
    # Content
    objectives = models.TextField(blank=True)
    materials = models.TextField(blank=True)
    speaker_name = models.CharField(max_length=200, blank=True)
    speaker_org = models.CharField(max_length=200, blank=True)
    # Feedback
    avg_satisfaction = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    total_feedback_count = models.PositiveIntegerField(default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counseling_workshops"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} ({self.get_workshop_type_display()})"


class WorkshopRegistration(models.Model):
    """Registration for counseling workshops."""

    class Status(models.TextChoices):
        REGISTERED = "registered", "Registered"
        ATTENDED = "attended", "Attended"
        NO_SHOW = "no_show", "No Show"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workshop = models.ForeignKey(CounselingWorkshop, on_delete=models.CASCADE, related_name="registrations")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="workshop_registrations")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.REGISTERED)
    registered_at = models.DateTimeField(auto_now_add=True)
    attended_at = models.DateTimeField(null=True, blank=True)
    feedback_rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Rating 1-5")
    feedback_comments = models.TextField(blank=True)

    class Meta:
        db_table = "workshop_registrations"
        unique_together = [("workshop", "student")]

    def __str__(self):
        return f"{self.student} — {self.workshop}"


# =============================================================================
# NEW MODELS: Academic Advising
# =============================================================================


class AcademicAdvising(models.Model):
    """Academic advising records."""

    class AdvisingType(models.TextChoices):
        COURSE_SELECTION = "course_selection", "Course Selection"
        SCHEDULING = "scheduling", "Schedule Planning"
        ACADEMIC_STANDING = "standing", "Academic Standing Review"
        GRADUATION_REQUIREMENTS = "graduation", "Graduation Requirements"
        TRANSFER_CREDITS = "transfer", "Transfer Credit Review"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        FOLLOW_UP = "follow_up", "Follow-up Needed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_advising")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="counseling_academic_advising")
    advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="advised_students")
    advising_type = models.CharField(max_length=20, choices=AdvisingType.choices, default=AdvisingType.COURSE_SELECTION)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    # Content
    topics_discussed = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    courses_recommended = models.JSONField(default=list, blank=True)
    courses_to_drop = models.JSONField(default=list, blank=True)
    # Academic status
    current_gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    credits_earned = models.PositiveIntegerField(null=True, blank=True)
    credits_required = models.PositiveIntegerField(null=True, blank=True)
    standing = models.CharField(max_length=30, blank=True, help_text="Good, Academic Probation, etc.")
    # Follow-up
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academic_advising"
        ordering = ["-scheduled_date"]
        indexes = [
            models.Index(fields=["student", "advising_type"]),
        ]

    def __str__(self):
        return f"{self.get_advising_type_display()} — {self.student.user.full_name} ({self.scheduled_date})"


class CourseRecommendation(models.Model):
    """Course recommendations for students."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    advising = models.ForeignKey(AcademicAdvising, on_delete=models.CASCADE, related_name="course_recommendations")
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=200)
    semester = models.CharField(max_length=20, blank=True)
    priority = models.CharField(max_length=20, blank=True, help_text="Required, Recommended, Optional")
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "course_recommendations"

    def __str__(self):
        return f"{self.course_code} — {self.course_name}"


# =============================================================================
# NEW MODELS: Peer Mentoring
# =============================================================================


class PeerMentor(models.Model):
    """Student peer mentors."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        GRADUATED = "graduated", "Graduated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="peer_mentors")
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="peer_mentor_profile")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    training_completed = models.BooleanField(default=False)
    training_date = models.DateField(null=True, blank=True)
    specialties = models.TextField(blank=True)
    max_mentees = models.PositiveIntegerField(default=3)
    current_mentees = models.PositiveIntegerField(default=0)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="supervised_mentors")
    # Stats
    total_sessions = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "peer_mentors"
        verbose_name = "Peer Mentor"
        verbose_name_plural = "Peer Mentors"

    def __str__(self):
        return f"{self.student.user.full_name} — Peer Mentor"


class PeerMentoringSession(models.Model):
    """Individual peer mentoring sessions."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mentor = models.ForeignKey(PeerMentor, on_delete=models.CASCADE, related_name="sessions")
    mentee = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="peer_mentoring_sessions")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    session_date = models.DateField()
    session_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    location = models.CharField(max_length=200, blank=True)
    topics_covered = models.TextField(blank=True)
    mentor_notes = models.TextField(blank=True)
    mentee_feedback = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Rating 1-5")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "peer_mentoring_sessions"
        ordering = ["-session_date"]

    def __str__(self):
        return f"{self.mentor} → {self.mentee} ({self.session_date})"


# =============================================================================
# NEW MODELS: Counseling Scheduling
# =============================================================================


class CounselingWaitlist(models.Model):
    """Waitlist for counseling appointments."""

    class Status(models.TextChoices):
        WAITING = "waiting", "Waiting"
        CONTACTED = "contacted", "Contacted"
        SCHEDULED = "scheduled", "Scheduled"
        EXPIRED = "expired", "Expired"
        REMOVED = "removed", "Removed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_waitlist")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="counseling_waitlist")
    preferred_counselor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField()
    priority = models.CharField(
        max_length=10, choices=StudentReferral.Priority.choices, default=StudentReferral.Priority.MEDIUM
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.WAITING)
    position = models.PositiveIntegerField(default=0)
    added_date = models.DateField(auto_now_add=True)
    contact_date = models.DateField(null=True, blank=True)
    scheduled_appointment = models.ForeignKey(CounselingAppointment, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "counseling_waitlist"
        ordering = ["position"]
        verbose_name = "Counseling Waitlist"
        verbose_name_plural = "Counseling Waitlist"

    def __str__(self):
        return f"#{self.position} {self.student.user.full_name} — {self.get_status_display()}"


class CounselingNotification(models.Model):
    """Notifications related to counseling services."""

    class NotificationType(models.TextChoices):
        APPOINTMENT_REMINDER = "appt_reminder", "Appointment Reminder"
        APPOINTMENT_CONFIRMED = "appt_confirmed", "Appointment Confirmed"
        APPOINTMENT_CANCELLED = "appt_cancelled", "Appointment Cancelled"
        FOLLOW_UP = "follow_up", "Follow-up Reminder"
        WORKSHOP_INVITE = "workshop", "Workshop Invitation"
        WAITLIST_UPDATE = "waitlist", "Waitlist Update"
        SCREENING_DUE = "screening", "Screening Due"
        CRISIS_ALERT = "crisis", "Crisis Alert"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_notifications")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="counseling_notifications")
    student = models.ForeignKey(
        Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="counseling_notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_via = models.CharField(max_length=50, blank=True, help_text="email, sms, push")
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "counseling_notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} — {self.title}"


# =============================================================================
# NEW MODELS: Counseling Contracts & Agreements
# =============================================================================


class CounselingContract(models.Model):
    """Confidentiality agreements and counseling contracts."""

    class ContractType(models.TextChoices):
        CONFIDENTIALITY = "confidentiality", "Confidentiality Agreement"
        SERVICE_AGREEMENT = "service", "Service Agreement"
        CONSENT_TREATMENT = "consent", "Consent for Treatment"
        INFORMATION_RELEASE = "release", "Information Release"
        SAFETY_PLAN = "safety", "Safety Plan"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Signature"
        SIGNED = "signed", "Signed"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_contracts")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="counseling_contracts")
    parent = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="counseling_parent_contracts"
    )
    counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="counseling_contracts")
    contract_type = models.CharField(max_length=20, choices=ContractType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Full contract/agreement text")
    # Signatures
    student_signed = models.BooleanField(default=False)
    student_signed_date = models.DateField(null=True, blank=True)
    parent_signed = models.BooleanField(default=False)
    parent_signed_date = models.DateField(null=True, blank=True)
    counselor_signed = models.BooleanField(default=False)
    counselor_signed_date = models.DateField(null=True, blank=True)
    # File
    document_file = models.FileField(upload_to="counseling/contracts/", null=True, blank=True)
    # Validity
    effective_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counseling_contracts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "contract_type"]),
        ]

    def __str__(self):
        return f"{self.get_contract_type_display()} — {self.student.user.full_name}"

    @property
    def is_fully_signed(self):
        return self.student_signed and self.counselor_signed

    @property
    def is_valid(self):
        if self.status != self.Status.SIGNED:
            return False
        if self.expiry_date and timezone.now().date() > self.expiry_date:
            return False
        return True


# =============================================================================
# NEW MODELS: Referral Network
# =============================================================================


class ExternalReferralProvider(models.Model):
    """External referral providers and agencies."""

    class ProviderType(models.TextChoices):
        THERAPIST = "therapist", "Therapist / Psychologist"
        PSYCHIATRIST = "psychiatrist", "Psychiatrist"
        SOCIAL_WORKER = "social_worker", "Social Worker"
        COMMUNITY = "community", "Community Agency"
        HOSPITAL = "hospital", "Hospital / Medical"
        EDUCATIONAL = "educational", "Educational Specialist"
        LEGAL = "legal", "Legal Services"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="external_referral_providers")
    name = models.CharField(max_length=200)
    provider_type = models.CharField(max_length=20, choices=ProviderType.choices)
    organization = models.CharField(max_length=200, blank=True)
    contact_person = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    specialties = models.TextField(blank=True)
    insurance_accepted = models.TextField(blank=True)
    referral_process = models.TextField(blank=True, help_text="How to make a referral")
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "external_referral_providers"
        verbose_name = "External Referral Provider"
        verbose_name_plural = "External Referral Providers"

    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"


class ReferralTracking(models.Model):
    """Track referrals made to external providers."""

    class Status(models.TextChoices):
        INITIATED = "initiated", "Referral Initiated"
        CONFIRMED = "confirmed", "Appointment Confirmed"
        ATTENDED = "attended", "Student Attended"
        ONGOING = "ongoing", "Ongoing Treatment"
        COMPLETED = "completed", "Treatment Completed"
        LOST_TO_FOLLOWUP = "lost", "Lost to Follow-up"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="referral_tracking")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="referral_tracking")
    provider = models.ForeignKey(ExternalReferralProvider, on_delete=models.CASCADE, related_name="referrals")
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
    referral_date = models.DateField()
    reason = models.TextField()
    urgency = models.CharField(
        max_length=10, choices=StudentReferral.Priority.choices, default=StudentReferral.Priority.MEDIUM
    )
    # Follow-up
    appointment_date = models.DateField(null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    outcome_notes = models.TextField(blank=True)
    # Parent
    parent_consent = models.BooleanField(default=False)
    parent_contacted = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "referral_tracking"
        ordering = ["-referral_date"]
        indexes = [
            models.Index(fields=["student", "status"]),
        ]

    def __str__(self):
        return f"{self.student.user.full_name} → {self.provider.name} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Bullying & Harassment
# =============================================================================


class BullyingReport(models.Model):
    """Bullying and harassment incident reports."""

    class ReportType(models.TextChoices):
        PHYSICAL = "physical", "Physical Bullying"
        VERBAL = "verbal", "Verbal Bullying"
        SOCIAL = "social", "Social / Relational Bullying"
        CYBERBULLYING = "cyber", "Cyberbullying"
        SEXUAL = "sexual", "Sexual Harassment"
        RACIAL = "racial", "Racial Harassment"
        DISCRIMINATION = "discrimination", "Discrimination"
        OTHER = "other", "Other"

    class SeverityLevel(models.TextChoices):
        LOW = "low", "Low"
        MODERATE = "moderate", "Moderate"
        HIGH = "high", "High"
        SEVERE = "severe", "Severe"

    class Status(models.TextChoices):
        REPORTED = "reported", "Reported"
        INVESTIGATING = "investigating", "Under Investigation"
        CONFIRMED = "confirmed", "Confirmed"
        UNFOUNDED = "unfounded", "Unfounded"
        RESOLVED = "resolved", "Resolved"
        ESCALATED = "escalated", "Escalated"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="bullying_reports")
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="bullying_reports_filed")
    victim = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="bullying_victim_reports")
    alleged_perpetrator = models.ForeignKey(
        Student, on_delete=models.SET_NULL, null=True, blank=True, related_name="bullying_alleged_reports"
    )
    report_type = models.CharField(max_length=15, choices=ReportType.choices)
    severity = models.CharField(max_length=10, choices=SeverityLevel.choices, default=SeverityLevel.MODERATE)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.REPORTED)
    # Description
    description = models.TextField(help_text="Description of bullying/harassment incident")
    location = models.CharField(max_length=200, blank=True)
    date_of_incident = models.DateField(null=True, blank=True)
    witnesses = models.TextField(blank=True)
    evidence = models.TextField(blank=True, help_text="Description of any evidence")
    # Investigation
    investigator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="bullying_investigations"
    )
    investigation_notes = models.TextField(blank=True)
    investigation_date = models.DateField(null=True, blank=True)
    # Resolution
    resolution = models.TextField(blank=True)
    actions_taken = models.TextField(blank=True)
    # Support
    victim_support_plan = models.TextField(blank=True)
    counselor_assigned = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="bullying_counseling_assignments"
    )
    # Parent notification
    victim_parent_notified = models.BooleanField(default=False)
    perpetrator_parent_notified = models.BooleanField(default=False)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bullying_reports"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "status", "severity"]),
            models.Index(fields=["victim", "status"]),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} — {self.victim.user.full_name} ({self.get_status_display()})"


class BullyingFollowUp(models.Model):
    """Follow-up actions for bullying reports."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(BullyingReport, on_delete=models.CASCADE, related_name="follow_ups")
    conducted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    follow_up_date = models.DateField()
    participant = models.CharField(max_length=100, help_text="Who was involved in follow-up")
    notes = models.TextField()
    outcome = models.TextField(blank=True)
    victim_status = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "bullying_follow_ups"
        ordering = ["-follow_up_date"]

    def __str__(self):
        return f"Follow-up: {self.report} ({self.follow_up_date})"


# =============================================================================
# NEW MODELS: Social-Emotional Learning (SEL)
# =============================================================================


class SELAssessment(models.Model):
    """Social-Emotional Learning assessment results."""

    class SELDomain(models.TextChoices):
        SELF_AWARENESS = "self_awareness", "Self-Awareness"
        SELF_MANAGEMENT = "self_management", "Self-Management"
        SOCIAL_AWARENESS = "social_awareness", "Social Awareness"
        RELATIONSHIP_SKILLS = "relationship", "Relationship Skills"
        RESPONSIBLE_DECISIONS = "decisions", "Responsible Decision-Making"
        OVERALL = "overall", "Overall SEL"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sel_assessments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="sel_assessments")
    assessor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    domain = models.CharField(max_length=20, choices=SELDomain.choices)
    assessment_date = models.DateField()
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    strength_areas = models.TextField(blank=True)
    growth_areas = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    intervention_suggested = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sel_assessments"
        ordering = ["-assessment_date"]
        indexes = [
            models.Index(fields=["student", "domain"]),
        ]

    def __str__(self):
        return f"{self.get_domain_display()} — {self.student.user.full_name} ({self.score}/{self.max_score})"

    @property
    def percentage_score(self):
        if self.max_score == 0:
            return 0
        return round((self.score / self.max_score) * 100, 2)


class SELGoal(models.Model):
    """SEL goals for students."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACHIEVED = "achieved", "Achieved"
        DISCONTINUED = "discontinued", "Discontinued"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="sel_goals")
    counselor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sel_goals_guided")
    domain = models.CharField(max_length=20, choices=SELAssessment.SELDomain.choices)
    goal_description = models.TextField()
    measurable_outcome = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    start_date = models.DateField()
    target_date = models.DateField(null=True, blank=True)
    achieved_date = models.DateField(null=True, blank=True)
    strategies = models.TextField(blank=True)
    progress_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sel_goals"
        ordering = ["-start_date"]

    def __str__(self):
        return f"SEL Goal — {self.student.user.full_name}: {self.goal_description[:50]}"


# =============================================================================
# NEW MODELS: Restorative Justice
# =============================================================================


class RestorativeJusticeSession(models.Model):
    """Restorative justice circles and conferences."""

    class SessionType(models.TextChoices):
        CIRCLE = "circle", "Restorative Circle"
        CONFERENCES = "conference", "Restorative Conference"
        MEDIATION = "mediation", "Peer Mediation"
        DIALOGUE = "dialogue", "Restorative Dialogue"

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class OutcomeType(models.TextChoices):
        RESOLUTION = "resolution", "Resolution Reached"
        PARTIAL = "partial", "Partial Resolution"
        NO_RESOLUTION = "no_resolution", "No Resolution"
        REFERRED = "referred", "Referred"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="restorative_sessions")
    facilitator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="restorative_facilitated_sessions"
    )
    session_type = models.CharField(max_length=15, choices=SessionType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    # Participants
    participants = models.ManyToManyField(Student, related_name="restorative_sessions")
    participant_count = models.PositiveIntegerField(default=0)
    # Content
    incident_description = models.TextField(blank=True)
    harm_caused = models.TextField(blank=True)
    needs_identified = models.TextField(blank=True)
    agreements = models.TextField(blank=True)
    # Outcome
    outcome = models.CharField(max_length=20, choices=OutcomeType.choices, blank=True)
    outcome_notes = models.TextField(blank=True)
    agreements_met = models.BooleanField(null=True, blank=True)
    # Follow-up
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    # Metadata
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="restorative_sessions_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "restorative_justice_sessions"
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.get_session_type_display()} — {self.scheduled_date}"


class RestorativeCommitment(models.Model):
    """Commitments/agreements from restorative justice sessions."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        OVERDUE = "overdue", "Overdue"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(RestorativeJusticeSession, on_delete=models.CASCADE, related_name="commitments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="restorative_commitments")
    commitment = models.TextField(help_text="What the student committed to")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateField(null=True, blank=True)
    completed_date = models.DateField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "restorative_commitments"
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.student.user.full_name}: {self.commitment[:50]}"


# =============================================================================
# NEW MODELS: Counseling Surveys
# =============================================================================


class CounselingSurvey(models.Model):
    """Surveys for counseling program evaluation."""

    class SurveyType(models.TextChoices):
        SATISFACTION = "satisfaction", "Satisfaction Survey"
        NEEDS_ASSESSMENT = "needs", "Needs Assessment"
        PROGRAM_EVALUATION = "evaluation", "Program Evaluation"
        ANONYMOUS_FEEDBACK = "anonymous", "Anonymous Feedback"
        PRE_POST = "pre_post", "Pre/Post Assessment"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"
        ANALYZED = "analyzed", "Analyzed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_surveys")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    survey_type = models.CharField(max_length=20, choices=SurveyType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    questions = models.JSONField(default=list, blank=True, help_text="List of survey questions")
    target_audience = models.CharField(max_length=50, blank=True, help_text="Students, Parents, Staff")
    is_anonymous = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    total_responses = models.PositiveIntegerField(default=0)
    results_data = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counseling_surveys"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_survey_type_display()})"


class CounselingSurveyResponse(models.Model):
    """Individual survey responses."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(CounselingSurvey, on_delete=models.CASCADE, related_name="responses")
    respondent_type = models.CharField(max_length=20, blank=True, help_text="student, parent, staff")
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="counseling_survey_responses"
    )
    answers = models.JSONField(default=dict, blank=True)
    overall_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "counseling_survey_responses"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Response to {self.survey} — {self.submitted_at}"


# =============================================================================
# NEW MODELS: Counseling Leave & Coverage
# =============================================================================


class CounselorCoverage(models.Model):
    """Coverage assignments when counselors are absent."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counselor_coverages")
    absent_counselor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="counselor_coverage_absences")
    covering_counselor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="counselor_coverage_assignments"
    )
    absence = models.ForeignKey(CounselorAbsence, on_delete=models.CASCADE, related_name="coverages")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    coverage_date = models.DateField()
    students_covered = models.ManyToManyField(Student, blank=True, related_name="coverage_sessions")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counselor_coverages"
        ordering = ["coverage_date"]

    def __str__(self):
        return (
            f"{self.covering_counselor.full_name} covering for {self.absent_counselor.full_name} ({self.coverage_date})"
        )


# =============================================================================
# NEW MODELS: Special Education Referral
# =============================================================================


class SpecialEducationReferral(models.Model):
    """Referrals for special education evaluation and IEP/504 plans."""

    class ReferralType(models.TextChoices):
        IEP = "iep", "IEP Evaluation"
        PLAN_504 = "504", "504 Plan"
        GIFTED = "gifted", "Gifted/Talented"
        LEARNING_DISABILITY = "ld", "Learning Disability"
        ADHD = "adhd", "ADHD Accommodation"
        AUTISM = "autism", "Autism Spectrum"
        EMOTIONAL = "emotional", "Emotional/Behavioral"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        INITIATED = "initiated", "Referral Initiated"
        EVALUATION_SCHEDULED = "eval_scheduled", "Evaluation Scheduled"
        UNDER_EVALUATION = "evaluating", "Under Evaluation"
        ELIGIBLE = "eligible", "Found Eligible"
        NOT_ELIGIBLE = "not_eligible", "Not Eligible"
        IEP_CREATED = "iep_created", "IEP/504 Created"
        IN_PROGRESS = "in_progress", "Active Plan"
        REVIEW = "review", "Under Review"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="spec_ed_referrals")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="spec_ed_referrals")
    referred_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="spec_ed_referrals_created"
    )
    referral_type = models.CharField(max_length=20, choices=ReferralType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED)
    reason = models.TextField(help_text="Reason for referral")
    supporting_data = models.TextField(blank=True)
    # Evaluation
    evaluator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    evaluation_date = models.DateField(null=True, blank=True)
    evaluation_results = models.TextField(blank=True)
    # Plan
    plan_type = models.CharField(max_length=20, blank=True, help_text="IEP, 504, etc.")
    plan_created_date = models.DateField(null=True, blank=True)
    plan_review_date = models.DateField(null=True, blank=True)
    # Parent
    parent_consent = models.BooleanField(default=False)
    parent_consent_date = models.DateField(null=True, blank=True)
    parent_notified = models.BooleanField(default=False)
    # Notes
    notes = models.TextField(blank=True)
    document = models.FileField(upload_to="counseling/spec_ed/", null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "special_education_referrals"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "referral_type"]),
            models.Index(fields=["school", "status"]),
        ]
        verbose_name = "Special Education Referral"
        verbose_name_plural = "Special Education Referrals"

    def __str__(self):
        return f"{self.get_referral_type_display()} — {self.student.user.full_name} ({self.get_status_display()})"


class CounselingGoalTracking(models.Model):
    """Long-term counseling goal tracking for students."""

    class Domain(models.TextChoices):
        ACADEMIC = "academic", "Academic"
        SOCIAL = "social", "Social Skills"
        EMOTIONAL = "emotional", "Emotional Regulation"
        BEHAVIORAL = "behavioral", "Behavioral"
        CAREER = "career", "Career Development"
        COLLEGE = "college", "College Readiness"
        WELLNESS = "wellness", "Overall Wellness"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACHIEVED = "achieved", "Achieved"
        PARTIALLY = "partial", "Partially Achieved"
        ONGOING = "ongoing", "Ongoing"
        DISCONTINUED = "discontinued", "Discontinued"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_goal_tracking")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="counseling_goal_tracking")
    counselor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    domain = models.CharField(max_length=15, choices=Domain.choices)
    goal = models.TextField(help_text="Goal description")
    measurable_criteria = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    priority = models.CharField(
        max_length=10, choices=StudentReferral.Priority.choices, default=StudentReferral.Priority.MEDIUM
    )
    start_date = models.DateField()
    target_date = models.DateField(null=True, blank=True)
    achieved_date = models.DateField(null=True, blank=True)
    progress_percentage = models.PositiveSmallIntegerField(default=0)
    progress_notes = models.TextField(blank=True)
    barriers = models.TextField(blank=True)
    support_strategies = models.TextField(blank=True)
    review_dates = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "counseling_goal_tracking"
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["student", "domain", "status"]),
        ]
        verbose_name = "Counseling Goal Tracking"
        verbose_name_plural = "Counseling Goal Tracking"

    def __str__(self):
        return f"{self.get_domain_display()} — {self.student.user.full_name}: {self.goal[:50]}"


class CounselingSessionLog(models.Model):
    """Audit log for counseling session access and modifications."""

    class ActionType(models.TextChoices):
        VIEWED = "viewed", "Record Viewed"
        CREATED = "created", "Record Created"
        EDITED = "edited", "Record Edited"
        SHARED = "shared", "Record Shared"
        EXPORTED = "exported", "Record Exported"
        DELETED = "deleted", "Record Deleted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="counseling_session_logs")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="counseling_audit_logs")
    action = models.CharField(max_length=15, choices=ActionType.choices)
    target_type = models.CharField(max_length=50, help_text="Model type affected")
    target_id = models.CharField(max_length=100, help_text="ID of the affected record")
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "counseling_session_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "action"]),
            models.Index(fields=["target_type", "target_id"]),
        ]
        verbose_name = "Counseling Session Log"
        verbose_name_plural = "Counseling Session Logs"

    def __str__(self):
        return f"{self.user.full_name} — {self.get_action_display()} {self.target_type} ({self.timestamp})"
