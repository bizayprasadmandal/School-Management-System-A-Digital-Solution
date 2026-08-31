"""
Counseling Service — Django Admin registrations.
"""

from django.contrib import admin

from .models import (
    CaseManagement,
    CaseNote,
    CounselingAppointment,
    CounselingFeedback,
    CounselingOutcome,
    CounselingReport,
    CounselingSession,
    CounselorAbsence,
    CounselorAvailability,
    CounselorProfile,
    CrisisFollowUp,
    CrisisIntervention,
    GroupSession,
    GroupSessionAttendance,
    GroupSessionMember,
    InterventionGoal,
    InterventionPlan,
    MentalHealthScreening,
    ParentConsent,
    ProgressMilestone,
    ProgressTracking,
    ScreeningResponse,
    SessionAttachment,
    StudentReferral,
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
