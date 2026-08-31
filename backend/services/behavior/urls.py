from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "behavior_v1"
router = DefaultRouter()
# Core
router.register("categories", views.BehaviorCategoryViewSet, basename="behavior-category")
router.register("incidents", views.IncidentViewSet, basename="incident")
router.register("referrals", views.ReferralViewSet, basename="referral")
# PBIS Points
router.register("points", views.BehaviorPointViewSet, basename="behavior-point")
router.register("point-balances", views.BehaviorPointBalanceViewSet, basename="behavior-point-balance")
# Consequences
router.register("consequences", views.BehaviorConsequenceViewSet, basename="behavior-consequence")
router.register("merits", views.BehaviorMeritViewSet, basename="behavior-merit")
# Detention & Suspension
router.register("detentions", views.DetentionTrackingViewSet, basename="detention-tracking")
router.register("suspensions", views.SuspensionTrackingViewSet, basename="suspension-tracking")
# Contracts & Statements
router.register("contracts", views.BehaviorContractViewSet, basename="behavior-contract")
router.register("witness-statements", views.WitnessStatementViewSet, basename="witness-statement")
router.register("evidence", views.BehaviorEvidenceViewSet, basename="behavior-evidence")
# Rubrics
router.register("rubrics", views.BehaviorRubricViewSet, basename="behavior-rubric")
router.register("rubric-levels", views.BehaviorRubricLevelViewSet, basename="behavior-rubric-level")
# Hall Pass & Tardy
router.register("hall-passes", views.DigitalHallPassViewSet, basename="digital-hall-pass")
router.register("tardies", views.TardyTrackingViewSet, basename="tardy-tracking")
# Goals & Streaks
router.register("goals", views.BehaviorGoalViewSet, basename="behavior-goal")
router.register("streaks", views.BehaviorStreakViewSet, basename="behavior-streak")
# Alerts & Appeals
router.register("alerts", views.BehaviorAlertViewSet, basename="behavior-alert")
router.register("appeals", views.BehaviorAppealViewSet, basename="behavior-appeal")
# Notifications
router.register("parent-notifications", views.ParentNotificationViewSet, basename="parent-notification")
# Analytics
router.register("analytics", views.BehaviorAnalyticsViewSet, basename="behavior-analytics")
# Rewards & Redemption
router.register("rewards", views.BehaviorRewardViewSet, basename="behavior-reward")
router.register("redemptions", views.BehaviorPointsRedemptionViewSet, basename="behavior-redemption")
# Houses
router.register("houses", views.BehaviorHouseViewSet, basename="behavior-house")
router.register("house-members", views.BehaviorHouseMemberViewSet, basename="behavior-house-member")
# Leaderboards
router.register("leaderboards", views.BehaviorLeaderboardViewSet, basename="behavior-leaderboard")
# Report Cards
router.register("report-cards", views.BehaviorReportCardViewSet, basename="behavior-report-card")
# Intervention Plans
router.register("intervention-plans", views.BehaviorInterventionPlanViewSet, basename="behavior-intervention-plan")
# MTSS
router.register("mtss", views.BehaviorMTSSViewSet, basename="behavior-mtss")
# SEL
router.register("sel-checkins", views.SELCheckInViewSet, basename="sel-checkin")
router.register("sel-responses", views.SELCheckInResponseViewSet, basename="sel-response")
# Staff Dashboard
router.register("staff-dashboards", views.BehaviorStaffDashboardViewSet, basename="behavior-staff-dashboard")
# Gamification
router.register("badges", views.BehaviorBadgeViewSet, basename="behavior-badge")
router.register("badge-awards", views.BehaviorBadgeAwardViewSet, basename="behavior-badge-award")
# SMS Alerts
router.register("sms-alerts", views.BehaviorSMSAlertViewSet, basename="behavior-sms-alert")
# Auto-Escalation
router.register("auto-escalations", views.BehaviorAutoEscalationViewSet, basename="behavior-auto-escalation")
router.register("escalation-logs", views.BehaviorEscalationLogViewSet, basename="behavior-escalation-log")
# Attendance & Academic
router.register("attendance-links", views.BehaviorAttendanceLinkViewSet, basename="behavior-attendance-link")
router.register(
    "academic-correlations", views.BehaviorAcademicCorrelationViewSet, basename="behavior-academic-correlation"
)
# Data Visualization
router.register("data-visualizations", views.BehaviorDataVisualizationViewSet, basename="behavior-data-visualization")
# Predictive Analytics
router.register(
    "predictive-analytics", views.BehaviorPredictiveAnalyticsViewSet, basename="behavior-predictive-analytics"
)
# SEL Surveys
router.register("sel-surveys", views.SELSurveyViewSet, basename="sel-survey")
router.register("sel-survey-responses", views.SELSurveyResponseViewSet, basename="sel-survey-response")
# Training
router.register("training-materials", views.BehaviorTrainingMaterialViewSet, basename="behavior-training-material")
router.register(
    "training-completions", views.BehaviorTrainingCompletionViewSet, basename="behavior-training-completion"
)
# Policies
router.register("policy-templates", views.BehaviorPolicyTemplateViewSet, basename="behavior-policy-template")
# Streak Challenges
router.register("streak-challenges", views.BehaviorStreakChallengeViewSet, basename="behavior-streak-challenge")
# Parent Portal
router.register("parent-portals", views.BehaviorParentPortalViewSet, basename="behavior-parent-portal")

urlpatterns = [path("", include(router.urls))]
