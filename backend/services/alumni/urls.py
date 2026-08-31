from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AlumniChapterMemberViewSet,
    AlumniChapterViewSet,
    AlumniDiscussionLikeViewSet,
    AlumniDiscussionReplyViewSet,
    AlumniDiscussionViewSet,
    AlumniDonationReceiptViewSet,
    AlumniDonationViewSet,
    AlumniEventRSVPViewSet,
    AlumniEventViewSet,
    AlumniJobApplicationViewSet,
    AlumniJobPostingViewSet,
    AlumniMentorshipViewSet,
    AlumniProfileViewSet,
)

app_name = "alumni_v1"
router = DefaultRouter()
router.register(r"profiles", AlumniProfileViewSet, basename="alumni-profile")
router.register(r"events", AlumniEventViewSet, basename="alumni-event")
router.register(r"rsvps", AlumniEventRSVPViewSet, basename="alumni-rsvp")
router.register(r"donations", AlumniDonationViewSet, basename="alumni-donation")
router.register(r"receipts", AlumniDonationReceiptViewSet, basename="alumni-receipt")
router.register(r"chapters", AlumniChapterViewSet, basename="alumni-chapter")
router.register(r"chapter-members", AlumniChapterMemberViewSet, basename="alumni-chapter-member")
router.register(r"mentorships", AlumniMentorshipViewSet, basename="alumni-mentorship")
router.register(r"job-postings", AlumniJobPostingViewSet, basename="alumni-job-posting")
router.register(r"job-applications", AlumniJobApplicationViewSet, basename="alumni-job-application")
router.register(r"discussions", AlumniDiscussionViewSet, basename="alumni-discussion")
router.register(r"discussion-replies", AlumniDiscussionReplyViewSet, basename="alumni-discussion-reply")
router.register(r"discussion-likes", AlumniDiscussionLikeViewSet, basename="alumni-discussion-like")

urlpatterns = [path("", include(router.urls))]
