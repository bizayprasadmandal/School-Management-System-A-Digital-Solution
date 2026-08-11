from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "gradebook_v1"
router = DefaultRouter()
router.register("exams", views.ExamViewSet, basename="exam")
router.register("grades", views.GradeViewSet, basename="grade")
router.register("proposals", views.GradeChangeProposalViewSet, basename="grade-change-proposal")
router.register("assessments", views.AssessmentViewSet, basename="assessment")
router.register("submissions", views.AssessmentSubmissionViewSet, basename="submission")
router.register("report-cards", views.ReportCardViewSet, basename="report-card")

urlpatterns = [path("", include(router.urls))]
