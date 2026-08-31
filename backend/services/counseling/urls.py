"""
Counseling Service — URL Configuration.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "counseling_v1"

router = DefaultRouter()
router.register(r"appointments", views.CounselingAppointmentViewSet, basename="appointment")
router.register(r"referrals", views.StudentReferralViewSet, basename="referral")
router.register(r"sessions", views.CounselingSessionViewSet, basename="session")
router.register(r"intervention-plans", views.InterventionPlanViewSet, basename="intervention-plan")
router.register(r"intervention-goals", views.InterventionGoalViewSet, basename="intervention-goal")
router.register(r"screenings", views.MentalHealthScreeningViewSet, basename="screening")
router.register(r"screening-responses", views.ScreeningResponseViewSet, basename="screening-response")
router.register(r"crisis", views.CrisisInterventionViewSet, basename="crisis")
router.register(r"crisis-followups", views.CrisisFollowUpViewSet, basename="crisis-followup")
router.register(r"progress", views.ProgressTrackingViewSet, basename="progress")
router.register(r"progress-milestones", views.ProgressMilestoneViewSet, basename="progress-milestone")
router.register(r"consent", views.ParentConsentViewSet, basename="consent")
router.register(r"group-sessions", views.GroupSessionViewSet, basename="group-session")
router.register(r"group-attendance", views.GroupSessionAttendanceViewSet, basename="group-attendance")
router.register(r"cases", views.CaseManagementViewSet, basename="case")
router.register(r"outcomes", views.CounselingOutcomeViewSet, basename="outcome")
router.register(r"reports", views.CounselingReportViewSet, basename="report")
router.register(r"availability", views.CounselorAvailabilityViewSet, basename="availability")
router.register(r"feedback", views.CounselingFeedbackViewSet, basename="feedback")

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/stats/", views.CounselorDashboardStatsView.as_view(), name="dashboard_stats"),
    path("profile/", views.CounselorProfileView.as_view(), name="counselor_profile"),
]
