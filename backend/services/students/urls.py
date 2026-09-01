"""URL Configuration for students."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcademicYearViewSet,
    ClassroomViewSet,
    DocumentViewSet,
    EnrollmentViewSet,
    GradeViewSet,
    GuardianViewSet,
    ParentProfileViewSet,
    SiblingTrackingViewSet,
    StudentAcademicAdvisorViewSet,
    StudentAchievementViewSet,
    StudentActivityViewSet,
    StudentArchiveViewSet,
    StudentAwardViewSet,
    StudentCareerGuidanceViewSet,
    StudentCategoryMembershipViewSet,
    StudentCategoryViewSet,
    StudentClubViewSet,
    StudentContactViewSet,
    StudentCustomFieldValueViewSet,
    StudentCustomFieldViewSet,
    StudentDisciplineViewSet,
    StudentFeedbackViewSet,
    StudentFinancialAidViewSet,
    StudentGraduationViewSet,
    StudentGuardianViewSet,
    StudentIDActivityViewSet,
    StudentIDCardViewSet,
    StudentInternshipViewSet,
    StudentLearningStyleViewSet,
    StudentMealPlanViewSet,
    StudentMedicalRecordViewSet,
    StudentMentorViewSet,
    StudentNoteViewSet,
    StudentParentCommunicationViewSet,
    StudentParkingViewSet,
    StudentPhotoViewSet,
    StudentPortfolioViewSet,
    StudentScholarshipViewSet,
    StudentSocialMediaViewSet,
    StudentStatusHistoryViewSet,
    StudentTagAssignmentViewSet,
    StudentTagViewSet,
    StudentTransferViewSet,
    StudentTransportAssignmentViewSet,
    StudentTutoringViewSet,
    StudentViewSet,
    StudentVolunteerViewSet,
    StudentWellnessViewSet,
)

app_name = "students_v1"

router = DefaultRouter()
router.register(r"academic-year", AcademicYearViewSet, basename="academic-year")
router.register(r"grade", GradeViewSet, basename="grade")
router.register(r"classroom", ClassroomViewSet, basename="classroom")
router.register(r"student", StudentViewSet, basename="student")
router.register(r"guardian", GuardianViewSet, basename="guardian")
router.register(r"student-guardian", StudentGuardianViewSet, basename="student-guardian")
router.register(r"enrollment", EnrollmentViewSet, basename="enrollment")
router.register(r"parent-profile", ParentProfileViewSet, basename="parent-profile")
router.register(r"document", DocumentViewSet, basename="document")
router.register(r"student-contact", StudentContactViewSet, basename="student-contact")
router.register(r"student-medical-record", StudentMedicalRecordViewSet, basename="student-medical-record")
router.register(r"student-custom-field", StudentCustomFieldViewSet, basename="student-custom-field")
router.register(r"student-custom-field-value", StudentCustomFieldValueViewSet, basename="student-custom-field-value")
router.register(r"student-photo", StudentPhotoViewSet, basename="student-photo")
router.register(r"student-i-d-card", StudentIDCardViewSet, basename="student-i-d-card")
router.register(r"student-status-history", StudentStatusHistoryViewSet, basename="student-status-history")
router.register(r"sibling-tracking", SiblingTrackingViewSet, basename="sibling-tracking")
router.register(r"student-category", StudentCategoryViewSet, basename="student-category")
router.register(
    r"student-category-membership", StudentCategoryMembershipViewSet, basename="student-category-membership"
)
router.register(r"student-tag", StudentTagViewSet, basename="student-tag")
router.register(r"student-tag-assignment", StudentTagAssignmentViewSet, basename="student-tag-assignment")
router.register(r"student-note", StudentNoteViewSet, basename="student-note")
router.register(r"student-archive", StudentArchiveViewSet, basename="student-archive")
router.register(r"student-social-media", StudentSocialMediaViewSet, basename="student-social-media")
router.register(r"student-portfolio", StudentPortfolioViewSet, basename="student-portfolio")
router.register(r"student-wellness", StudentWellnessViewSet, basename="student-wellness")
router.register(r"student-learning-style", StudentLearningStyleViewSet, basename="student-learning-style")
router.register(r"student-achievement", StudentAchievementViewSet, basename="student-achievement")
router.register(r"student-club", StudentClubViewSet, basename="student-club")
router.register(r"student-activity", StudentActivityViewSet, basename="student-activity")
router.register(r"student-award", StudentAwardViewSet, basename="student-award")
router.register(r"student-discipline", StudentDisciplineViewSet, basename="student-discipline")
router.register(r"student-tutoring", StudentTutoringViewSet, basename="student-tutoring")
router.register(r"student-mentor", StudentMentorViewSet, basename="student-mentor")
router.register(r"student-career-guidance", StudentCareerGuidanceViewSet, basename="student-career-guidance")
router.register(
    r"student-parent-communication", StudentParentCommunicationViewSet, basename="student-parent-communication"
)
router.register(r"student-academic-advisor", StudentAcademicAdvisorViewSet, basename="student-academic-advisor")
router.register(r"student-transfer", StudentTransferViewSet, basename="student-transfer")
router.register(r"student-graduation", StudentGraduationViewSet, basename="student-graduation")
router.register(r"student-volunteer", StudentVolunteerViewSet, basename="student-volunteer")
router.register(r"student-internship", StudentInternshipViewSet, basename="student-internship")
router.register(r"student-scholarship", StudentScholarshipViewSet, basename="student-scholarship")
router.register(r"student-financial-aid", StudentFinancialAidViewSet, basename="student-financial-aid")
router.register(
    r"student-transport-assignment", StudentTransportAssignmentViewSet, basename="student-transport-assignment"
)
router.register(r"student-meal-plan", StudentMealPlanViewSet, basename="student-meal-plan")
router.register(r"student-parking", StudentParkingViewSet, basename="student-parking")
router.register(r"student-i-d-activity", StudentIDActivityViewSet, basename="student-i-d-activity")
router.register(r"student-feedback", StudentFeedbackViewSet, basename="student-feedback")

urlpatterns = [
    path("", include(router.urls)),
]
