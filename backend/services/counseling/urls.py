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
router.register(r"academic-advising", views.AcademicAdvisingViewSet, basename="academic_advising")
router.register(r"bullying-followups", views.BullyingFollowUpViewSet, basename="bullying_followups")
router.register(r"bullying-reports", views.BullyingReportViewSet, basename="bullying_reports")
router.register(r"career-assessments", views.CareerAssessmentViewSet, basename="career_assessments")
router.register(r"career-goals", views.CareerGoalViewSet, basename="career_goals")
router.register(r"case-notes", views.CaseNoteViewSet, basename="case_notes")
router.register(r"college-applications", views.CollegeApplicationViewSet, basename="college_applications")
router.register(r"contracts", views.CounselingContractViewSet, basename="contracts")
router.register(r"goal-tracking", views.CounselingGoalTrackingViewSet, basename="goal_tracking")
router.register(r"notifications", views.CounselingNotificationViewSet, basename="notifications")
router.register(r"session-logs", views.CounselingSessionLogViewSet, basename="session_logs")
router.register(r"surveys", views.CounselingSurveyViewSet, basename="surveys")
router.register(r"survey-responses", views.CounselingSurveyResponseViewSet, basename="survey_responses")
router.register(r"waitlist", views.CounselingWaitlistViewSet, basename="waitlist")
router.register(r"workshops", views.CounselingWorkshopViewSet, basename="workshops")
router.register(r"absences", views.CounselorAbsenceViewSet, basename="absences")
router.register(r"coverage", views.CounselorCoverageViewSet, basename="coverage")
router.register(r"counselor-profiles", views.CounselorProfileViewSet, basename="counselor_profiles")
router.register(r"course-recommendations", views.CourseRecommendationViewSet, basename="course_recommendations")
router.register(r"providers", views.ExternalReferralProviderViewSet, basename="providers")
router.register(r"group-members", views.GroupSessionMemberViewSet, basename="group_members")
router.register(r"peer-mentors", views.PeerMentorViewSet, basename="peer_mentors")
router.register(r"peer-mentoring-sessions", views.PeerMentoringSessionViewSet, basename="peer_mentoring_sessions")
router.register(r"referral-tracking", views.ReferralTrackingViewSet, basename="referral_tracking")
router.register(r"restorative-commitments", views.RestorativeCommitmentViewSet, basename="restorative_commitments")
router.register(r"restorative-sessions", views.RestorativeJusticeSessionViewSet, basename="restorative_sessions")
router.register(r"sel-assessments", views.SELAssessmentViewSet, basename="sel_assessments")
router.register(r"sel-goals", views.SELGoalViewSet, basename="sel_goals")
router.register(r"session-attachments", views.SessionAttachmentViewSet, basename="session_attachments")
router.register(
    r"special-education-referrals", views.SpecialEducationReferralViewSet, basename="special_education_referrals"
)
router.register(r"workshop-registrations", views.WorkshopRegistrationViewSet, basename="workshop_registrations")

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/stats/", views.CounselorDashboardStatsView.as_view(), name="dashboard_stats"),
    path("profile/", views.CounselorProfileView.as_view(), name="counselor_profile"),
]
