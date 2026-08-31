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

urlpatterns = [path("", include(router.urls))]
