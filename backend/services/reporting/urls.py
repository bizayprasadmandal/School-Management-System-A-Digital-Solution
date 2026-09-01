from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "reporting_v1"
router = DefaultRouter()
router.register("", views.ReportingViewSet, basename="reporting")
router.register("templates", views.ReportTemplateViewSet, basename="report-template")
router.register("academic-performance", views.AcademicPerformanceReportViewSet, basename="academic-performance")
router.register("teacher-performance", views.TeacherPerformanceReportViewSet, basename="teacher-performance")
router.register("grade-trends", views.GradeTrendReportViewSet, basename="grade-trend")
router.register("scheduled", views.ScheduledReportViewSet, basename="scheduled-report")
router.register("year-over-year", views.YearOverYearReportViewSet, basename="year-over-year")
router.register("department", views.DepartmentReportViewSet, basename="department-report")
router.register("compliance", views.ComplianceReportViewSet, basename="compliance-report")
router.register("shares", views.ReportShareViewSet, basename="report-share")
router.register("student-progress", views.StudentProgressTrackingViewSet, basename="student-progress")

urlpatterns = [path("", include(router.urls))]
