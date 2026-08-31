from django.contrib import admin

from .models import (
    BehaviorAcademicCorrelation,
    BehaviorAlert,
    BehaviorAnalytics,
    BehaviorAppeal,
    BehaviorAttendanceLink,
    BehaviorAutoEscalation,
    BehaviorBadge,
    BehaviorBadgeAward,
    BehaviorCategory,
    BehaviorConsequence,
    BehaviorContract,
    BehaviorDataVisualization,
    BehaviorEscalationLog,
    BehaviorEvidence,
    BehaviorGoal,
    BehaviorHouse,
    BehaviorHouseMember,
    BehaviorInterventionPlan,
    BehaviorLeaderboard,
    BehaviorMerit,
    BehaviorMTSS,
    BehaviorParentPortal,
    BehaviorPoint,
    BehaviorPointBalance,
    BehaviorPointsRedemption,
    BehaviorPolicyTemplate,
    BehaviorPredictiveAnalytics,
    BehaviorReportCard,
    BehaviorReward,
    BehaviorRubric,
    BehaviorRubricLevel,
    BehaviorSMSAlert,
    BehaviorStaffDashboard,
    BehaviorStreak,
    BehaviorStreakChallenge,
    BehaviorTrainingCompletion,
    BehaviorTrainingMaterial,
    DetentionTracking,
    DigitalHallPass,
    Incident,
    ParentNotification,
    Referral,
    SELCheckIn,
    SELCheckInResponse,
    SELSurvey,
    SELSurveyResponse,
    SuspensionTracking,
    TardyTracking,
    WitnessStatement,
)


@admin.register(BehaviorCategory)
class BehaviorCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category_type", "points_value", "is_active"]
    list_filter = ["category_type", "is_active"]
    search_fields = ["name"]


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ["student", "incident_type", "severity", "occurred_at", "reported_by", "status"]
    list_filter = ["status", "severity", "incident_type"]
    search_fields = ["student__user__full_name", "description"]


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ["incident", "referred_to", "referred_by", "status", "created_at"]
    list_filter = ["status"]


@admin.register(BehaviorPoint)
class BehaviorPointAdmin(admin.ModelAdmin):
    list_display = ["student", "points", "point_type", "reason", "awarded_by", "created_at"]
    list_filter = ["point_type", "category"]
    search_fields = ["student__user__full_name", "reason"]


@admin.register(BehaviorPointBalance)
class BehaviorPointBalanceAdmin(admin.ModelAdmin):
    list_display = ["student", "current_balance", "total_earned", "total_deducted", "last_activity_at"]
    search_fields = ["student__user__full_name"]


@admin.register(BehaviorConsequence)
class BehaviorConsequenceAdmin(admin.ModelAdmin):
    list_display = ["student", "consequence_type", "status", "issued_date", "issued_by"]
    list_filter = ["consequence_type", "status"]
    search_fields = ["student__user__full_name", "description"]


@admin.register(BehaviorMerit)
class BehaviorMeritAdmin(admin.ModelAdmin):
    list_display = ["student", "merit_type", "title", "points", "awarded_date"]
    list_filter = ["merit_type"]
    search_fields = ["student__user__full_name", "title"]


@admin.register(DetentionTracking)
class DetentionTrackingAdmin(admin.ModelAdmin):
    list_display = ["student", "detention_type", "scheduled_date", "start_time", "end_time", "status"]
    list_filter = ["detention_type", "status"]
    search_fields = ["student__user__full_name"]


@admin.register(SuspensionTracking)
class SuspensionTrackingAdmin(admin.ModelAdmin):
    list_display = ["student", "suspension_type", "start_date", "end_date", "status"]
    list_filter = ["suspension_type", "status"]
    search_fields = ["student__user__full_name"]


@admin.register(BehaviorContract)
class BehaviorContractAdmin(admin.ModelAdmin):
    list_display = ["student", "title", "status", "start_date", "end_date"]
    list_filter = ["status"]
    search_fields = ["student__user__full_name", "title"]


@admin.register(WitnessStatement)
class WitnessStatementAdmin(admin.ModelAdmin):
    list_display = ["incident", "witness_name", "witness_type", "statement_date"]
    list_filter = ["witness_type"]
    search_fields = ["witness_name", "statement"]


@admin.register(BehaviorEvidence)
class BehaviorEvidenceAdmin(admin.ModelAdmin):
    list_display = ["incident", "evidence_type", "title", "uploaded_by", "uploaded_at"]
    list_filter = ["evidence_type"]
    search_fields = ["title"]


@admin.register(BehaviorRubric)
class BehaviorRubricAdmin(admin.ModelAdmin):
    list_display = ["name", "min_score", "max_score", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(BehaviorRubricLevel)
class BehaviorRubricLevelAdmin(admin.ModelAdmin):
    list_display = ["rubric", "score", "label", "color"]
    search_fields = ["label"]


@admin.register(DigitalHallPass)
class DigitalHallPassAdmin(admin.ModelAdmin):
    list_display = ["student", "pass_type", "to_destination", "status", "issued_at"]
    list_filter = ["pass_type", "status"]
    search_fields = ["student__user__full_name", "to_destination"]


@admin.register(TardyTracking)
class TardyTrackingAdmin(admin.ModelAdmin):
    list_display = ["student", "tardy_type", "date", "scheduled_time", "arrival_time", "minutes_late"]
    list_filter = ["tardy_type", "status"]
    search_fields = ["student__user__full_name"]


@admin.register(BehaviorGoal)
class BehaviorGoalAdmin(admin.ModelAdmin):
    list_display = ["student", "goal_type", "title", "status", "start_date", "end_date"]
    list_filter = ["goal_type", "status"]
    search_fields = ["student__user__full_name", "title"]


@admin.register(BehaviorStreak)
class BehaviorStreakAdmin(admin.ModelAdmin):
    list_display = ["student", "streak_type", "current_streak", "longest_streak", "last_activity_at"]
    list_filter = ["streak_type"]
    search_fields = ["student__user__full_name"]


@admin.register(BehaviorAlert)
class BehaviorAlertAdmin(admin.ModelAdmin):
    list_display = ["student", "alert_type", "priority", "status", "created_at"]
    list_filter = ["alert_type", "priority", "status"]
    search_fields = ["student__user__full_name", "title"]


@admin.register(BehaviorAppeal)
class BehaviorAppealAdmin(admin.ModelAdmin):
    list_display = ["student", "appeal_type", "status", "decision", "submitted_at"]
    list_filter = ["appeal_type", "status", "decision"]
    search_fields = ["student__user__full_name", "reason"]


@admin.register(ParentNotification)
class ParentNotificationAdmin(admin.ModelAdmin):
    list_display = ["student", "notification_type", "delivery_method", "status", "created_at"]
    list_filter = ["notification_type", "delivery_method", "status"]
    search_fields = ["student__user__full_name", "subject"]


@admin.register(BehaviorAnalytics)
class BehaviorAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["report_type", "start_date", "end_date", "total_incidents", "generated_at"]
    list_filter = ["report_type"]


@admin.register(BehaviorReward)
class BehaviorRewardAdmin(admin.ModelAdmin):
    list_display = ["name", "reward_type", "points_cost", "stock_quantity", "total_redeemed", "is_active"]
    list_filter = ["reward_type", "availability", "is_active"]
    search_fields = ["name", "description"]


@admin.register(BehaviorPointsRedemption)
class BehaviorPointsRedemptionAdmin(admin.ModelAdmin):
    list_display = ["student", "reward", "points_spent", "status", "redeemed_at"]
    list_filter = ["status"]
    search_fields = ["student__user__full_name", "reward__name"]


@admin.register(BehaviorHouse)
class BehaviorHouseAdmin(admin.ModelAdmin):
    list_display = ["name", "total_points", "member_count", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(BehaviorHouseMember)
class BehaviorHouseMemberAdmin(admin.ModelAdmin):
    list_display = ["student", "house", "role", "is_active"]
    list_filter = ["role", "is_active"]
    search_fields = ["student__user__full_name", "house__name"]


@admin.register(BehaviorLeaderboard)
class BehaviorLeaderboardAdmin(admin.ModelAdmin):
    list_display = ["name", "leaderboard_type", "time_period", "total_entries", "is_published"]
    list_filter = ["leaderboard_type", "time_period", "is_published"]
    search_fields = ["name"]


@admin.register(BehaviorReportCard)
class BehaviorReportCardAdmin(admin.ModelAdmin):
    list_display = ["student", "report_period", "behavior_score", "status", "sent_to_parent"]
    list_filter = ["report_period", "status", "sent_to_parent"]
    search_fields = ["student__user__full_name"]


@admin.register(BehaviorInterventionPlan)
class BehaviorInterventionPlanAdmin(admin.ModelAdmin):
    list_display = ["student", "plan_type", "title", "status", "start_date"]
    list_filter = ["plan_type", "status"]
    search_fields = ["student__user__full_name", "title"]


@admin.register(BehaviorMTSS)
class BehaviorMTSSAdmin(admin.ModelAdmin):
    list_display = ["student", "tier_level", "status", "referral_date"]
    list_filter = ["tier_level", "status"]
    search_fields = ["student__user__full_name", "referral_reason"]


@admin.register(SELCheckIn)
class SELCheckInAdmin(admin.ModelAdmin):
    list_display = ["student", "mood", "energy_level", "stress_level", "needs_help", "check_in_date"]
    list_filter = ["mood", "needs_help"]
    search_fields = ["student__user__full_name"]


@admin.register(SELCheckInResponse)
class SELCheckInResponseAdmin(admin.ModelAdmin):
    list_display = ["check_in", "staff", "follow_up_required", "created_at"]
    list_filter = ["follow_up_required"]


@admin.register(BehaviorStaffDashboard)
class BehaviorStaffDashboardAdmin(admin.ModelAdmin):
    list_display = ["staff", "incidents_today", "points_given_today", "pending_alerts", "last_refreshed"]
    search_fields = ["staff__full_name"]


@admin.register(BehaviorBadge)
class BehaviorBadgeAdmin(admin.ModelAdmin):
    list_display = ["name", "badge_type", "points_required", "total_earned", "is_active"]
    list_filter = ["badge_type", "is_active"]
    search_fields = ["name"]


@admin.register(BehaviorBadgeAward)
class BehaviorBadgeAwardAdmin(admin.ModelAdmin):
    list_display = ["badge", "student", "awarded_at", "is_public"]
    list_filter = ["is_public"]
    search_fields = ["student__user__full_name", "badge__name"]


@admin.register(BehaviorSMSAlert)
class BehaviorSMSAlertAdmin(admin.ModelAdmin):
    list_display = ["student", "alert_type", "parent_phone", "status", "created_at"]
    list_filter = ["alert_type", "status"]
    search_fields = ["student__user__full_name", "parent_phone"]


@admin.register(BehaviorAutoEscalation)
class BehaviorAutoEscalationAdmin(admin.ModelAdmin):
    list_display = ["name", "trigger_type", "trigger_value", "escalation_action", "is_active", "times_triggered"]
    list_filter = ["trigger_type", "escalation_action", "is_active"]
    search_fields = ["name"]


@admin.register(BehaviorEscalationLog)
class BehaviorEscalationLogAdmin(admin.ModelAdmin):
    list_display = ["student", "escalation_rule", "triggered_at", "resolved"]
    list_filter = ["resolved"]
    search_fields = ["student__user__full_name"]


@admin.register(BehaviorAttendanceLink)
class BehaviorAttendanceLinkAdmin(admin.ModelAdmin):
    list_display = ["student", "link_type", "attendance_date", "points_adjusted"]
    list_filter = ["link_type"]
    search_fields = ["student__user__full_name"]


@admin.register(BehaviorAcademicCorrelation)
class BehaviorAcademicCorrelationAdmin(admin.ModelAdmin):
    list_display = ["student", "correlation_type", "behavior_score", "gpa", "correlation_strength"]
    list_filter = ["correlation_type", "correlation_strength"]
    search_fields = ["student__user__full_name"]


@admin.register(BehaviorDataVisualization)
class BehaviorDataVisualizationAdmin(admin.ModelAdmin):
    list_display = ["title", "chart_type", "is_public", "last_refreshed"]
    list_filter = ["chart_type", "is_public"]
    search_fields = ["title"]


@admin.register(BehaviorPredictiveAnalytics)
class BehaviorPredictiveAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["student", "prediction_type", "risk_level", "risk_score", "reviewed"]
    list_filter = ["prediction_type", "risk_level", "reviewed"]
    search_fields = ["student__user__full_name"]


@admin.register(SELSurvey)
class SELSurveyAdmin(admin.ModelAdmin):
    list_display = ["title", "survey_type", "status", "total_responses", "start_date", "end_date"]
    list_filter = ["survey_type", "status"]
    search_fields = ["title"]


@admin.register(SELSurveyResponse)
class SELSurveyResponseAdmin(admin.ModelAdmin):
    list_display = ["survey", "student", "overall_score", "needs_follow_up", "submitted_at"]
    list_filter = ["needs_follow_up"]
    search_fields = ["student__user__full_name"]


@admin.register(BehaviorTrainingMaterial)
class BehaviorTrainingMaterialAdmin(admin.ModelAdmin):
    list_display = ["title", "material_type", "audience", "is_required", "views_count", "completions_count"]
    list_filter = ["material_type", "audience", "is_required"]
    search_fields = ["title"]


@admin.register(BehaviorTrainingCompletion)
class BehaviorTrainingCompletionAdmin(admin.ModelAdmin):
    list_display = ["material", "staff", "status", "completed_at"]
    list_filter = ["status"]
    search_fields = ["staff__full_name"]


@admin.register(BehaviorPolicyTemplate)
class BehaviorPolicyTemplateAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "version", "is_template", "downloads_count"]
    list_filter = ["category", "is_template"]
    search_fields = ["title"]


@admin.register(BehaviorStreakChallenge)
class BehaviorStreakChallengeAdmin(admin.ModelAdmin):
    list_display = ["title", "challenge_type", "status", "target_streak", "total_participants", "total_completions"]
    list_filter = ["challenge_type", "status"]
    search_fields = ["title"]


@admin.register(BehaviorParentPortal)
class BehaviorParentPortalAdmin(admin.ModelAdmin):
    list_display = ["parent_user", "student", "access_level", "is_active", "last_login_at"]
    list_filter = ["access_level", "is_active"]
    search_fields = ["parent_user__full_name", "student__user__full_name"]
