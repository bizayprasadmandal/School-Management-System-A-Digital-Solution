from django.contrib import admin

from .models import (
    BehaviorAlert,
    BehaviorAnalytics,
    BehaviorAppeal,
    BehaviorCategory,
    BehaviorConsequence,
    BehaviorContract,
    BehaviorEvidence,
    BehaviorGoal,
    BehaviorMerit,
    BehaviorPoint,
    BehaviorPointBalance,
    BehaviorRubric,
    BehaviorRubricLevel,
    BehaviorStreak,
    DetentionTracking,
    DigitalHallPass,
    Incident,
    ParentNotification,
    Referral,
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
