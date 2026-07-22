"""
Counseling Service — URL Configuration.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "counseling_v1"

router = DefaultRouter()
router.register(r"appointments", views.CounselingAppointmentViewSet, basename="appointment")
router.register(r"referrals", views.StudentReferralViewSet, basename="referral")

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/stats/", views.CounselorDashboardStatsView.as_view(), name="dashboard_stats"),
]
