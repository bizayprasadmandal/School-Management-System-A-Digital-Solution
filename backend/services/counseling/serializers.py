"""
Counseling Service — Serializers.
"""

from rest_framework import serializers

from .models import (
    AcademicAdvising,
    BullyingFollowUp,
    BullyingReport,
    CareerAssessment,
    CareerGoal,
    CaseManagement,
    CaseNote,
    CollegeApplication,
    CounselingAppointment,
    CounselingContract,
    CounselingFeedback,
    CounselingGoalTracking,
    CounselingNotification,
    CounselingOutcome,
    CounselingReport,
    CounselingSession,
    CounselingSessionLog,
    CounselingSurvey,
    CounselingSurveyResponse,
    CounselingWaitlist,
    CounselingWorkshop,
    CounselorAbsence,
    CounselorAvailability,
    CounselorCoverage,
    CounselorProfile,
    CourseRecommendation,
    CrisisFollowUp,
    CrisisIntervention,
    ExternalReferralProvider,
    GroupSession,
    GroupSessionAttendance,
    GroupSessionMember,
    InterventionGoal,
    InterventionPlan,
    MentalHealthScreening,
    ParentConsent,
    PeerMentor,
    PeerMentoringSession,
    ProgressMilestone,
    ProgressTracking,
    ReferralTracking,
    RestorativeCommitment,
    RestorativeJusticeSession,
    ScreeningResponse,
    SELAssessment,
    SELGoal,
    SessionAttachment,
    SpecialEducationReferral,
    StudentReferral,
    WorkshopRegistration,
)


class CounselingAppointmentSerializer(serializers.ModelSerializer):
    """Full appointment details — used for GET and detail views."""

    counselor_name = serializers.CharField(source="counselor.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    student_grade = serializers.SerializerMethodField()
    student_class = serializers.SerializerMethodField()

    def get_student_grade(self, obj):
        enrollment = obj.student.enrollments.filter(is_active=True).first()
        if enrollment and enrollment.classroom and enrollment.classroom.grade:
            return enrollment.classroom.grade.name
        return None

    def get_student_class(self, obj):
        enrollment = obj.student.enrollments.filter(is_active=True).first()
        if enrollment and enrollment.classroom:
            return enrollment.classroom.name
        return None

    class Meta:
        model = CounselingAppointment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class CounselingAppointmentCreateUpdateSerializer(serializers.ModelSerializer):
    """Appointment creation/update — write-only fields excluded."""

    send_reminder = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = CounselingAppointment
        fields = [
            "counselor",
            "student",
            "appointment_type",
            "status",
            "scheduled_date",
            "scheduled_time",
            "duration_minutes",
            "location",
            "reason",
            "notes",
            "follow_up_needed",
            "follow_up_date",
            "send_reminder",
        ]

    def create(self, validated_data):
        # send_reminder is a write-only flag, not a model field — pop it so the
        # model is only created with real columns.
        validated_data.pop("send_reminder", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("send_reminder", None)
        return super().update(instance, validated_data)


class StudentReferralSerializer(serializers.ModelSerializer):
    """Full referral details with computed display names."""

    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    student_grade = serializers.SerializerMethodField()
    student_class = serializers.SerializerMethodField()
    referred_by_name = serializers.CharField(source="referred_by.full_name", read_only=True, allow_null=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, allow_null=True)

    def get_student_grade(self, obj):
        enrollment = obj.student.enrollments.filter(is_active=True).first()
        if enrollment and enrollment.classroom and enrollment.classroom.grade:
            return enrollment.classroom.grade.name
        return None

    def get_student_class(self, obj):
        enrollment = obj.student.enrollments.filter(is_active=True).first()
        if enrollment and enrollment.classroom:
            return enrollment.classroom.name
        return None

    class Meta:
        model = StudentReferral
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "action_taken_at"]


class StudentReferralCreateUpdateSerializer(serializers.ModelSerializer):
    """Referral creation/update — sensitive computed fields excluded."""

    notify_counselor = serializers.BooleanField(default=True, write_only=True)

    class Meta:
        model = StudentReferral
        fields = [
            "student",
            "assigned_to",
            "category",
            "priority",
            "status",
            "reason",
            "notes",
            "intervention_plan",
            "outcome",
            "follow_up_date",
            "is_confidential",
            "notify_counselor",
        ]

    def validate_reason(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Reason must be at least 10 characters.")
        return value

    def create(self, validated_data):
        # notify_counselor is a write-only flag, not a model field — pop it so
        # the model is only created with real columns.
        validated_data.pop("notify_counselor", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("notify_counselor", None)
        return super().update(instance, validated_data)


class CounselorProfileSerializer(serializers.ModelSerializer):
    """Full counselor profile — used for GET responses."""

    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = CounselorProfile
        fields = [
            "id",
            "user",
            "full_name",
            "email",
            "specialties",
            "certifications",
            "office_hours",
            "bio",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CounselorSelfProfileSerializer(serializers.ModelSerializer):
    """Serializer for counselors to update their own profile."""

    class Meta:
        model = CounselorProfile
        fields = ["specialties", "certifications", "office_hours", "bio"]


# =============================================================================
# Counseling Sessions Serializers
# =============================================================================


class SessionAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True)

    class Meta:
        model = SessionAttachment
        fields = ["id", "session", "file", "file_name", "description", "uploaded_by", "uploaded_by_name", "created_at"]
        read_only_fields = ["id", "created_at"]


class CounselingSessionSerializer(serializers.ModelSerializer):
    counselor_name = serializers.CharField(source="counselor.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    attachments = SessionAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = CounselingSession
        fields = [
            "id",
            "appointment",
            "counselor",
            "counselor_name",
            "student",
            "student_name",
            "session_type",
            "session_date",
            "start_time",
            "end_time",
            "duration_minutes",
            "presenting_issue",
            "session_summary",
            "interventions_used",
            "student_response",
            "risk_assessment",
            "goals_addressed",
            "progress_notes",
            "follow_up_actions",
            "follow_up_date",
            "is_confidential",
            "attachments",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Intervention Plan Serializers
# =============================================================================


class InterventionGoalSerializer(serializers.ModelSerializer):
    plan_title = serializers.CharField(source="intervention_plan.title", read_only=True)

    class Meta:
        model = InterventionGoal
        fields = [
            "id",
            "intervention_plan",
            "description",
            "measurable_outcome",
            "target_date",
            "status",
            "is_completed",
            "completion_date",
            "notes",
            "order",
            "created_at",
            "plan_title",
        ]
        read_only_fields = ["id", "created_at"]


class InterventionPlanSerializer(serializers.ModelSerializer):
    goals = InterventionGoalSerializer(many=True, read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    counselor_name = serializers.CharField(source="counselor.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = InterventionPlan
        fields = [
            "id",
            "student",
            "student_name",
            "counselor",
            "counselor_name",
            "plan_type",
            "title",
            "description",
            "status",
            "start_date",
            "target_end_date",
            "actual_end_date",
            "review_frequency",
            "last_review_date",
            "next_review_date",
            "referral",
            "outcome_summary",
            "is_effective",
            "completion_percentage",
            "goals",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Mental Health Screening Serializers
# =============================================================================


class ScreeningResponseSerializer(serializers.ModelSerializer):
    screening_title = serializers.CharField(source="screening.screening_type", read_only=True)

    class Meta:
        model = ScreeningResponse
        fields = [
            "id",
            "screening",
            "question_number",
            "question_text",
            "response_value",
            "response_text",
            "created_at",
            "screening_title",
        ]
        read_only_fields = ["id", "created_at"]


class MentalHealthScreeningSerializer(serializers.ModelSerializer):
    responses = ScreeningResponseSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    administered_by_name = serializers.CharField(source="administered_by.full_name", read_only=True, default=None)

    class Meta:
        model = MentalHealthScreening
        fields = [
            "id",
            "student",
            "student_name",
            "screening_type",
            "administered_by",
            "administered_by_name",
            "administered_date",
            "total_score",
            "risk_level",
            "interpretation",
            "recommendations",
            "referral_needed",
            "referred_to",
            "follow_up_date",
            "follow_up_completed",
            "consent_obtained",
            "consent_date",
            "responses",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Crisis Intervention Serializers
# =============================================================================


class CrisisFollowUpSerializer(serializers.ModelSerializer):
    counselor_name = serializers.CharField(source="counselor.full_name", read_only=True)

    class Meta:
        model = CrisisFollowUp
        fields = [
            "id",
            "crisis",
            "counselor",
            "counselor_name",
            "follow_up_date",
            "notes",
            "student_status",
            "actions_taken",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CrisisInterventionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.full_name", read_only=True, default=None)
    responding_counselor_name = serializers.CharField(
        source="responding_counselor.full_name", read_only=True, default=None
    )
    follow_ups = CrisisFollowUpSerializer(many=True, read_only=True)

    class Meta:
        model = CrisisIntervention
        fields = [
            "id",
            "student",
            "student_name",
            "reported_by",
            "reported_by_name",
            "crisis_type",
            "severity_level",
            "status",
            "description",
            "immediate_actions",
            "risk_to_self",
            "risk_to_others",
            "risk_level_assessment",
            "responding_counselor",
            "responding_counselor_name",
            "response_time",
            "intervention_provided",
            "follow_up_needed",
            "follow_up_date",
            "follow_up_notes",
            "external_referral",
            "external_agency",
            "external_contact",
            "parent_notified",
            "parent_notified_at",
            "follow_ups",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Progress Tracking Serializers
# =============================================================================


class ProgressMilestoneSerializer(serializers.ModelSerializer):
    progress_domain = serializers.CharField(source="progress.domain", read_only=True)

    class Meta:
        model = ProgressMilestone
        fields = [
            "id",
            "progress",
            "description",
            "target_date",
            "achieved",
            "achieved_date",
            "notes",
            "created_at",
            "progress_domain",
        ]
        read_only_fields = ["id", "created_at"]


class ProgressTrackingSerializer(serializers.ModelSerializer):
    milestones = ProgressMilestoneSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    counselor_name = serializers.CharField(source="counselor.full_name", read_only=True)
    rating_change = serializers.ReadOnlyField()

    class Meta:
        model = ProgressTracking
        fields = [
            "id",
            "student",
            "student_name",
            "counselor",
            "counselor_name",
            "domain",
            "assessment_date",
            "current_rating",
            "previous_rating",
            "target_rating",
            "trend",
            "observations",
            "strengths",
            "areas_for_growth",
            "interventions_applied",
            "source",
            "intervention_plan",
            "rating_change",
            "milestones",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Parent Consent Serializers
# =============================================================================


class ParentConsentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    parent_name = serializers.CharField(source="parent.full_name", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.full_name", read_only=True, default=None)
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = ParentConsent
        fields = [
            "id",
            "student",
            "student_name",
            "parent",
            "parent_name",
            "consent_type",
            "status",
            "consent_given",
            "consent_date",
            "expiry_date",
            "scope_description",
            "restrictions",
            "withdrawal_date",
            "withdrawal_reason",
            "is_valid",
            "recorded_by",
            "recorded_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Group Session Serializers
# =============================================================================


class GroupSessionMemberSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = GroupSessionMember
        fields = ["id", "group_session", "student", "student_name", "enrolled_at", "is_active", "notes"]
        read_only_fields = ["id", "enrolled_at"]


class GroupSessionAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = GroupSessionAttendance
        fields = [
            "id",
            "group_session",
            "student",
            "student_name",
            "session_number",
            "attended_date",
            "status",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class GroupSessionSerializer(serializers.ModelSerializer):
    counselor_name = serializers.CharField(source="counselor.full_name", read_only=True)
    members = GroupSessionMemberSerializer(many=True, read_only=True)
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()

    class Meta:
        model = GroupSession
        fields = [
            "id",
            "counselor",
            "counselor_name",
            "title",
            "description",
            "group_type",
            "status",
            "start_date",
            "end_date",
            "meeting_time",
            "duration_minutes",
            "location",
            "recurrence",
            "max_participants",
            "min_participants",
            "current_participants",
            "goals",
            "curriculum",
            "materials_needed",
            "is_full",
            "available_spots",
            "members",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Case Management Serializers
# =============================================================================


class CaseNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)

    class Meta:
        model = CaseNote
        fields = [
            "id",
            "case",
            "author",
            "author_name",
            "note_type",
            "content",
            "date",
            "time",
            "is_confidential",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CaseManagementSerializer(serializers.ModelSerializer):
    notes = CaseNoteSerializer(many=True, read_only=True)
    case_manager_name = serializers.CharField(source="case_manager.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = CaseManagement
        fields = [
            "id",
            "case_number",
            "student",
            "student_name",
            "case_manager",
            "case_manager_name",
            "title",
            "status",
            "priority",
            "presenting_concerns",
            "background_information",
            "strengths",
            "risk_factors",
            "team_members",
            "opened_date",
            "closed_date",
            "next_review_date",
            "outcome_summary",
            "is_successful",
            "referral_source",
            "referrals_made",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "case_number", "opened_date", "created_at"]


# =============================================================================
# Counseling Outcomes Serializers
# =============================================================================


class CounselingOutcomeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    counselor_name = serializers.CharField(source="counselor.full_name", read_only=True)

    class Meta:
        model = CounselingOutcome
        fields = [
            "id",
            "student",
            "student_name",
            "counselor",
            "counselor_name",
            "outcome_type",
            "assessment_date",
            "rating",
            "description",
            "measurable_results",
            "data_sources",
            "intervention_plan",
            "case",
            "recommendations",
            "continuation_needed",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Counseling Reports Serializers
# =============================================================================


class CounselingReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default=None)

    class Meta:
        model = CounselingReport
        fields = [
            "id",
            "title",
            "report_type",
            "status",
            "period_start",
            "period_end",
            "summary",
            "findings",
            "recommendations",
            "total_students_served",
            "total_sessions",
            "total_referrals",
            "report_data",
            "generated_by",
            "generated_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Counselor Availability Serializers
# =============================================================================


class CounselorAbsenceSerializer(serializers.ModelSerializer):
    counselor_name = serializers.CharField(source="counselor.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = CounselorAbsence
        fields = [
            "id",
            "counselor",
            "counselor_name",
            "absence_type",
            "start_date",
            "end_date",
            "reason",
            "approved_by",
            "approved_by_name",
            "appointments_affected",
            "students_notified",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CounselorAvailabilitySerializer(serializers.ModelSerializer):
    counselor_name = serializers.CharField(source="counselor.full_name", read_only=True)
    duration_hours = serializers.ReadOnlyField()

    class Meta:
        model = CounselorAvailability
        fields = [
            "id",
            "counselor",
            "counselor_name",
            "day_of_week",
            "start_time",
            "end_time",
            "is_available",
            "location",
            "session_type",
            "max_appointments",
            "notes",
            "effective_from",
            "effective_until",
            "duration_hours",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Counseling Feedback Serializers
# =============================================================================


class CounselingFeedbackSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    counselor_name = serializers.CharField(source="counselor.full_name", read_only=True)
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = CounselingFeedback
        fields = [
            "id",
            "student",
            "student_name",
            "counselor",
            "counselor_name",
            "feedback_type",
            "overall_satisfaction",
            "helpfulness_rating",
            "communication_rating",
            "professionalism_rating",
            "what_went_well",
            "areas_for_improvement",
            "additional_comments",
            "would_recommend",
            "session",
            "group_session",
            "is_anonymous",
            "average_rating",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Academic Advising Serializers
# =============================================================================


class CourseRecommendationSerializer(serializers.ModelSerializer):
    advising_type = serializers.CharField(source="advising.advising_type", read_only=True)
    advising_student = serializers.CharField(source="advising.student.user.full_name", read_only=True)

    class Meta:
        model = CourseRecommendation
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "advising_type",
        ]


class AcademicAdvisingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    advisor_name = serializers.CharField(source="advisor.full_name", read_only=True)

    class Meta:
        model = AcademicAdvising
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Career Counseling Serializers
# =============================================================================


class CareerGoalSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = CareerGoal
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CareerAssessmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = CareerAssessment
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CollegeApplicationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = CollegeApplication
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Peer Mentoring Serializers
# =============================================================================


class PeerMentorSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = PeerMentor
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class PeerMentoringSessionSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source="mentor.student.user.full_name", read_only=True)
    mentee_name = serializers.CharField(source="mentee.user.full_name", read_only=True)

    class Meta:
        model = PeerMentoringSession
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Workshop & Program Serializers
# =============================================================================


class WorkshopRegistrationSerializer(serializers.ModelSerializer):
    workshop_title = serializers.CharField(source="workshop.title", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = WorkshopRegistration
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CounselingWorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounselingWorkshop
        fields = "__all__"
        read_only_fields = ["id", "created_at", "school"]


# =============================================================================
# Scheduling & Waitlist Serializers
# =============================================================================


class CounselingWaitlistSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = CounselingWaitlist
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CounselingNotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source="recipient.full_name", read_only=True)

    class Meta:
        model = CounselingNotification
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Contracts & Agreements Serializers
# =============================================================================


class CounselingContractSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = CounselingContract
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =============================================================================
# External Referral Serializers
# =============================================================================


class ExternalReferralProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalReferralProvider
        fields = "__all__"
        read_only_fields = ["id", "created_at", "school"]


class ReferralTrackingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    provider_name = serializers.CharField(source="provider.name", read_only=True)

    class Meta:
        model = ReferralTracking
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Bullying & Harassment Serializers
# =============================================================================


class BullyingFollowUpSerializer(serializers.ModelSerializer):
    report_type = serializers.CharField(source="report.report_type", read_only=True)

    class Meta:
        model = BullyingFollowUp
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "report_type",
        ]


class BullyingReportSerializer(serializers.ModelSerializer):
    victim_name = serializers.CharField(source="victim.user.full_name", read_only=True)

    class Meta:
        model = BullyingReport
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =============================================================================
# SEL Serializers
# =============================================================================


class SELAssessmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = SELAssessment
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SELGoalSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = SELGoal
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Restorative Justice Serializers
# =============================================================================


class RestorativeCommitmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = RestorativeCommitment
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class RestorativeJusticeSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestorativeJusticeSession
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Surveys Serializers
# =============================================================================


class CounselingSurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CounselingSurveyResponse
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CounselingSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = CounselingSurvey
        fields = "__all__"
        read_only_fields = ["id", "created_at", "school"]


# =============================================================================
# Coverage & Special Ed Serializers
# =============================================================================


class CounselorCoverageSerializer(serializers.ModelSerializer):
    absent_counselor_name = serializers.CharField(source="absent_counselor.full_name", read_only=True)
    covering_counselor_name = serializers.CharField(source="covering_counselor.full_name", read_only=True)

    class Meta:
        model = CounselorCoverage
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "absent_counselor_name",
            "covering_counselor_name",
        ]


class SpecialEducationReferralSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = SpecialEducationReferral
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Goal Tracking & Session Log Serializers
# =============================================================================


class CounselingGoalTrackingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = CounselingGoalTracking
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CounselingSessionLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = CounselingSessionLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
