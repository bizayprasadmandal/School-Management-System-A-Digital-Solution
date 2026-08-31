from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .academic_year_views import AcademicYearViewSet
from .parent_profile import ParentProfileView

app_name = "students_v1"

router = DefaultRouter()

# Core
router.register(r"classrooms", views.ClassroomViewSet, basename="classroom")
router.register(r"grades", views.GradeViewSet, basename="grade")
router.register(r"academic-years", AcademicYearViewSet, basename="academic-year")
router.register(r"guardians", views.GuardianViewSet, basename="guardian")
# Contact & Medical
router.register(r"contacts", views.StudentContactViewSet, basename="student-contact")
router.register(r"medical-records", views.StudentMedicalRecordViewSet, basename="student-medical-record")
# Custom Fields
router.register(r"custom-fields", views.StudentCustomFieldViewSet, basename="student-custom-field")
router.register(r"custom-field-values", views.StudentCustomFieldValueViewSet, basename="student-custom-field-value")
# Photos & ID Cards
router.register(r"photos", views.StudentPhotoViewSet, basename="student-photo")
router.register(r"id-cards", views.StudentIDCardViewSet, basename="student-id-card")
# Status & Siblings
router.register(r"status-history", views.StudentStatusHistoryViewSet, basename="student-status-history")
router.register(r"siblings", views.SiblingTrackingViewSet, basename="sibling-tracking")
# Categories & Tags
router.register(r"categories", views.StudentCategoryViewSet, basename="student-category")
router.register(r"category-memberships", views.StudentCategoryMembershipViewSet, basename="student-category-membership")
router.register(r"tags", views.StudentTagViewSet, basename="student-tag")
router.register(r"tag-assignments", views.StudentTagAssignmentViewSet, basename="student-tag-assignment")
# Notes & Archive
router.register(r"notes", views.StudentNoteViewSet, basename="student-note")
router.register(r"archive", views.StudentArchiveViewSet, basename="student-archive")
# Social Media & Portfolio
router.register(r"social-media", views.StudentSocialMediaViewSet, basename="student-social-media")
router.register(r"portfolio", views.StudentPortfolioViewSet, basename="student-portfolio")
# Wellness
router.register(r"wellness", views.StudentWellnessViewSet, basename="student-wellness")
# Students (MUST be last as it's a catch-all)
router.register(r"", views.StudentViewSet, basename="student")

urlpatterns = [
    path("", include(router.urls)),
    path("parent-profile/", ParentProfileView.as_view(), name="parent_profile"),
]
