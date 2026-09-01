"""
Counseling Service — Django Admin registrations.
"""

from django.contrib import admin

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


@admin.register(CounselingAppointment)
class CounselingAppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "student_name",
        "counselor_name",
        "appointment_type",
        "scheduled_date",
        "scheduled_time",
        "status",
    ]
    list_filter = ["status", "appointment_type", "scheduled_date"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "counselor__first_name",
        "counselor__last_name",
        "reason",
    ]
    date_hierarchy = "scheduled_date"
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-scheduled_date"]

    @admin.display(description="Student")
    def student_name(self, obj):
        return obj.student.user.full_name

    @admin.display(description="Counselor")
    def counselor_name(self, obj):
        return obj.counselor.full_name


@admin.register(StudentReferral)
class StudentReferralAdmin(admin.ModelAdmin):
    list_display = [
        "student_name",
        "category",
        "priority",
        "status",
        "assigned_to",
        "created_at",
    ]
    list_filter = ["status", "priority", "category"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "reason",
        "notes",
    ]
    readonly_fields = ["id", "created_at", "updated_at", "action_taken_at"]
    ordering = ["-created_at"]
    actions = ["mark_as_closed"]

    @admin.display(description="Student")
    def student_name(self, obj):
        return obj.student.user.full_name

    @admin.display(description="Mark selected referrals as closed")
    def mark_as_closed(self, request, queryset):
        from django.utils import timezone

        updated = queryset.update(status="closed", action_taken_at=timezone.now())
        self.message_user(request, f"{updated} referral(s) closed.")


@admin.register(CounselorProfile)
class CounselorProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "specialties",
        "office_hours",
    ]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "specialties",
    ]


# =============================================================================
# Counseling Sessions
# =============================================================================


class SessionAttachmentInline(admin.TabularInline):
    model = SessionAttachment
    extra = 0


@admin.register(CounselingSession)
class CounselingSessionAdmin(admin.ModelAdmin):
    list_display = ["student", "counselor", "session_type", "session_date", "start_time", "duration_minutes"]
    list_filter = ["session_type", "is_confidential"]
    search_fields = ["student__user__first_name", "student__user__last_name", "presenting_issue"]
    date_hierarchy = "session_date"
    inlines = [SessionAttachmentInline]


# =============================================================================
# Intervention Plans
# =============================================================================


class InterventionGoalInline(admin.TabularInline):
    model = InterventionGoal
    extra = 0


@admin.register(InterventionPlan)
class InterventionPlanAdmin(admin.ModelAdmin):
    list_display = ["student", "counselor", "plan_type", "title", "status", "start_date", "completion_percentage"]
    list_filter = ["plan_type", "status"]
    search_fields = ["student__user__first_name", "title", "description"]
    inlines = [InterventionGoalInline]


@admin.register(InterventionGoal)
class InterventionGoalAdmin(admin.ModelAdmin):
    list_display = ["intervention_plan", "description", "status", "is_completed", "target_date"]
    list_filter = ["status", "is_completed"]
    search_fields = ["description"]


# =============================================================================
# Mental Health Screening
# =============================================================================


@admin.register(MentalHealthScreening)
class MentalHealthScreeningAdmin(admin.ModelAdmin):
    list_display = ["student", "screening_type", "total_score", "risk_level", "administered_date"]
    list_filter = ["screening_type", "risk_level"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    date_hierarchy = "administered_date"


@admin.register(ScreeningResponse)
class ScreeningResponseAdmin(admin.ModelAdmin):
    list_display = ["screening", "question_number", "response_value", "response_text"]
    list_filter = ["screening__screening_type"]


# =============================================================================
# Crisis Intervention
# =============================================================================


class CrisisFollowUpInline(admin.TabularInline):
    model = CrisisFollowUp
    extra = 0


@admin.register(CrisisIntervention)
class CrisisInterventionAdmin(admin.ModelAdmin):
    list_display = ["student", "crisis_type", "severity_level", "status", "parent_notified", "created_at"]
    list_filter = ["crisis_type", "severity_level", "status", "parent_notified"]
    search_fields = ["student__user__first_name", "description"]
    date_hierarchy = "created_at"
    inlines = [CrisisFollowUpInline]


@admin.register(CrisisFollowUp)
class CrisisFollowUpAdmin(admin.ModelAdmin):
    list_display = ["crisis", "counselor", "follow_up_date", "student_status"]
    date_hierarchy = "follow_up_date"


# =============================================================================
# Progress Tracking
# =============================================================================


class ProgressMilestoneInline(admin.TabularInline):
    model = ProgressMilestone
    extra = 0


@admin.register(ProgressTracking)
class ProgressTrackingAdmin(admin.ModelAdmin):
    list_display = ["student", "domain", "assessment_date", "current_rating", "trend"]
    list_filter = ["domain", "trend"]
    search_fields = ["student__user__first_name"]
    date_hierarchy = "assessment_date"
    inlines = [ProgressMilestoneInline]


@admin.register(ProgressMilestone)
class ProgressMilestoneAdmin(admin.ModelAdmin):
    list_display = ["progress", "description", "target_date", "achieved", "achieved_date"]
    list_filter = ["achieved"]


# =============================================================================
# Parent Consent
# =============================================================================


@admin.register(ParentConsent)
class ParentConsentAdmin(admin.ModelAdmin):
    list_display = ["student", "parent", "consent_type", "status", "consent_date", "expiry_date"]
    list_filter = ["consent_type", "status"]
    search_fields = ["student__user__first_name", "parent__first_name"]
    date_hierarchy = "created_at"


# =============================================================================
# Group Sessions
# =============================================================================


class GroupSessionMemberInline(admin.TabularInline):
    model = GroupSessionMember
    extra = 0


@admin.register(GroupSession)
class GroupSessionAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "counselor",
        "group_type",
        "status",
        "start_date",
        "current_participants",
        "max_participants",
    ]
    list_filter = ["group_type", "status"]
    search_fields = ["title", "description"]
    date_hierarchy = "start_date"
    inlines = [GroupSessionMemberInline]


@admin.register(GroupSessionAttendance)
class GroupSessionAttendanceAdmin(admin.ModelAdmin):
    list_display = ["group_session", "student", "attended_date", "status"]
    list_filter = ["status"]
    search_fields = ["student__user__first_name"]


@admin.register(GroupSessionMember)
class GroupSessionMemberAdmin(admin.ModelAdmin):
    list_display = ["group_session", "student", "is_active", "enrolled_at"]
    list_filter = ["is_active"]


# =============================================================================
# Case Management
# =============================================================================


class CaseNoteInline(admin.TabularInline):
    model = CaseNote
    extra = 0


@admin.register(CaseManagement)
class CaseManagementAdmin(admin.ModelAdmin):
    list_display = ["case_number", "title", "student", "case_manager", "status", "priority", "opened_date"]
    list_filter = ["status", "priority"]
    search_fields = ["case_number", "title", "student__user__first_name"]
    date_hierarchy = "opened_date"
    inlines = [CaseNoteInline]


@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    list_display = ["case", "author", "note_type", "date", "is_confidential"]
    list_filter = ["note_type", "is_confidential"]
    date_hierarchy = "date"


# =============================================================================
# Counseling Outcomes
# =============================================================================


@admin.register(CounselingOutcome)
class CounselingOutcomeAdmin(admin.ModelAdmin):
    list_display = ["student", "outcome_type", "assessment_date", "rating", "continuation_needed"]
    list_filter = ["outcome_type", "rating"]
    search_fields = ["student__user__first_name", "description"]
    date_hierarchy = "assessment_date"


# =============================================================================
# Counseling Reports
# =============================================================================


@admin.register(CounselingReport)
class CounselingReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "status", "period_start", "period_end", "generated_by"]
    list_filter = ["report_type", "status"]
    search_fields = ["title", "summary"]
    date_hierarchy = "created_at"


# =============================================================================
# Counselor Availability
# =============================================================================


@admin.register(CounselorAvailability)
class CounselorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ["counselor", "day_of_week", "start_time", "end_time", "is_available", "location"]
    list_filter = ["day_of_week", "is_available"]
    search_fields = ["counselor__first_name", "location"]


@admin.register(CounselorAbsence)
class CounselorAbsenceAdmin(admin.ModelAdmin):
    list_display = ["counselor", "absence_type", "start_date", "end_date", "appointments_affected"]
    list_filter = ["absence_type"]
    search_fields = ["counselor__first_name", "reason"]
    date_hierarchy = "start_date"


# =============================================================================
# Counseling Feedback
# =============================================================================


@admin.register(CounselingFeedback)
class CounselingFeedbackAdmin(admin.ModelAdmin):
    list_display = ["student", "counselor", "feedback_type", "overall_satisfaction", "created_at"]
    list_filter = ["feedback_type", "overall_satisfaction"]
    search_fields = ["student__user__first_name", "counselor__first_name"]
    date_hierarchy = "created_at"


# =============================================================================
# Career Counseling
# =============================================================================


@admin.register(CareerAssessment)
class CareerAssessmentAdmin(admin.ModelAdmin):
    list_display = ["student", "assessment_type", "administered_date", "administered_by"]
    list_filter = ["assessment_type"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    date_hierarchy = "administered_date"


@admin.register(CareerGoal)
class CareerGoalAdmin(admin.ModelAdmin):
    list_display = ["student", "title", "target_field", "status"]
    list_filter = ["status"]
    search_fields = ["student__user__first_name", "title"]


@admin.register(CollegeApplication)
class CollegeApplicationAdmin(admin.ModelAdmin):
    list_display = ["student", "university_name", "program_name", "status", "application_deadline"]
    list_filter = ["status", "degree_type"]
    search_fields = ["student__user__first_name", "university_name"]
    date_hierarchy = "application_deadline"


# =============================================================================
# Workshop & Program Management
# =============================================================================


@admin.register(CounselingWorkshop)
class CounselingWorkshopAdmin(admin.ModelAdmin):
    list_display = ["title", "workshop_type", "status", "start_date", "current_participants", "max_participants"]
    list_filter = ["workshop_type", "status"]
    search_fields = ["title", "description"]
    date_hierarchy = "start_date"


@admin.register(WorkshopRegistration)
class WorkshopRegistrationAdmin(admin.ModelAdmin):
    list_display = ["workshop", "student", "status", "feedback_rating"]
    list_filter = ["status"]
    search_fields = ["student__user__first_name"]


# =============================================================================
# Academic Advising
# =============================================================================


@admin.register(AcademicAdvising)
class AcademicAdvisingAdmin(admin.ModelAdmin):
    list_display = ["student", "advisor", "advising_type", "status", "scheduled_date"]
    list_filter = ["advising_type", "status"]
    search_fields = ["student__user__first_name", "advisor__first_name"]
    date_hierarchy = "scheduled_date"


@admin.register(CourseRecommendation)
class CourseRecommendationAdmin(admin.ModelAdmin):
    list_display = ["advising", "course_code", "course_name", "priority"]
    search_fields = ["course_code", "course_name"]


# =============================================================================
# Peer Mentoring
# =============================================================================


@admin.register(PeerMentor)
class PeerMentorAdmin(admin.ModelAdmin):
    list_display = ["student", "status", "training_completed", "current_mentees", "max_mentees"]
    list_filter = ["status", "training_completed"]
    search_fields = ["student__user__first_name"]


@admin.register(PeerMentoringSession)
class PeerMentoringSessionAdmin(admin.ModelAdmin):
    list_display = ["mentor", "mentee", "session_date", "status", "rating"]
    list_filter = ["status"]
    date_hierarchy = "session_date"


# =============================================================================
# Scheduling & Waitlist
# =============================================================================


@admin.register(CounselingWaitlist)
class CounselingWaitlistAdmin(admin.ModelAdmin):
    list_display = ["student", "position", "priority", "status", "added_date"]
    list_filter = ["status", "priority"]
    search_fields = ["student__user__first_name"]
    ordering = ["position"]


@admin.register(CounselingNotification)
class CounselingNotificationAdmin(admin.ModelAdmin):
    list_display = ["recipient", "notification_type", "title", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read"]
    search_fields = ["recipient__first_name", "title"]
    date_hierarchy = "created_at"


# =============================================================================
# Contracts & Agreements
# =============================================================================


@admin.register(CounselingContract)
class CounselingContractAdmin(admin.ModelAdmin):
    list_display = ["student", "contract_type", "status", "effective_date", "expiry_date"]
    list_filter = ["contract_type", "status"]
    search_fields = ["student__user__first_name", "title"]


# =============================================================================
# External Referrals
# =============================================================================


@admin.register(ExternalReferralProvider)
class ExternalReferralProviderAdmin(admin.ModelAdmin):
    list_display = ["name", "provider_type", "organization", "phone", "is_active"]
    list_filter = ["provider_type", "is_active"]
    search_fields = ["name", "organization"]


@admin.register(ReferralTracking)
class ReferralTrackingAdmin(admin.ModelAdmin):
    list_display = ["student", "provider", "status", "referral_date", "urgency"]
    list_filter = ["status", "urgency"]
    search_fields = ["student__user__first_name"]
    date_hierarchy = "referral_date"


# =============================================================================
# Bullying & Harassment
# =============================================================================


@admin.register(BullyingReport)
class BullyingReportAdmin(admin.ModelAdmin):
    list_display = ["victim", "report_type", "severity", "status", "created_at"]
    list_filter = ["report_type", "severity", "status"]
    search_fields = ["victim__user__first_name", "description"]
    date_hierarchy = "created_at"


@admin.register(BullyingFollowUp)
class BullyingFollowUpAdmin(admin.ModelAdmin):
    list_display = ["report", "conducted_by", "follow_up_date"]
    date_hierarchy = "follow_up_date"


# =============================================================================
# SEL
# =============================================================================


@admin.register(SELAssessment)
class SELAssessmentAdmin(admin.ModelAdmin):
    list_display = ["student", "domain", "score", "max_score", "assessment_date"]
    list_filter = ["domain"]
    search_fields = ["student__user__first_name"]
    date_hierarchy = "assessment_date"


@admin.register(SELGoal)
class SELGoalAdmin(admin.ModelAdmin):
    list_display = ["student", "domain", "status", "start_date", "target_date"]
    list_filter = ["status", "domain"]
    search_fields = ["student__user__first_name"]


# =============================================================================
# Restorative Justice
# =============================================================================


@admin.register(RestorativeJusticeSession)
class RestorativeJusticeSessionAdmin(admin.ModelAdmin):
    list_display = ["session_type", "status", "scheduled_date", "participant_count"]
    list_filter = ["session_type", "status"]
    date_hierarchy = "scheduled_date"


@admin.register(RestorativeCommitment)
class RestorativeCommitmentAdmin(admin.ModelAdmin):
    list_display = ["student", "commitment", "status", "due_date"]
    list_filter = ["status"]
    search_fields = ["student__user__first_name"]


# =============================================================================
# Surveys
# =============================================================================


@admin.register(CounselingSurvey)
class CounselingSurveyAdmin(admin.ModelAdmin):
    list_display = ["title", "survey_type", "status", "total_responses", "start_date"]
    list_filter = ["survey_type", "status"]
    search_fields = ["title"]


@admin.register(CounselingSurveyResponse)
class CounselingSurveyResponseAdmin(admin.ModelAdmin):
    list_display = ["survey", "respondent_type", "overall_rating", "submitted_at"]
    list_filter = ["respondent_type"]
    date_hierarchy = "submitted_at"


# =============================================================================
# Coverage & Special Ed
# =============================================================================


@admin.register(CounselorCoverage)
class CounselorCoverageAdmin(admin.ModelAdmin):
    list_display = ["absent_counselor", "covering_counselor", "coverage_date", "status"]
    list_filter = ["status"]
    date_hierarchy = "coverage_date"


@admin.register(SpecialEducationReferral)
class SpecialEducationReferralAdmin(admin.ModelAdmin):
    list_display = ["student", "referral_type", "status", "parent_consent", "created_at"]
    list_filter = ["referral_type", "status"]
    search_fields = ["student__user__first_name"]
    date_hierarchy = "created_at"


@admin.register(CounselingGoalTracking)
class CounselingGoalTrackingAdmin(admin.ModelAdmin):
    list_display = ["student", "domain", "goal", "status", "progress_percentage"]
    list_filter = ["domain", "status"]
    search_fields = ["student__user__first_name", "goal"]


@admin.register(CounselingSessionLog)
class CounselingSessionLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "target_type", "target_id", "timestamp"]
    list_filter = ["action"]
    search_fields = ["user__first_name", "target_type"]
    date_hierarchy = "timestamp"
    readonly_fields = ["id", "user", "action", "target_type", "target_id", "description", "ip_address", "timestamp"]
    ordering = ["-timestamp"]
