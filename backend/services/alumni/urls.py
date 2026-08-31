from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AlumniActivityFeedViewSet,
    AlumniAwardCategoryViewSet,
    AlumniAwardNominationViewSet,
    AlumniAwardViewSet,
    AlumniBadgeAwardViewSet,
    AlumniBadgeViewSet,
    AlumniCalendarEventViewSet,
    AlumniCalendarRSVPViewSet,
    AlumniCampaignDonationViewSet,
    AlumniCampaignViewSet,
    AlumniChapterMemberViewSet,
    AlumniChapterViewSet,
    AlumniConversationViewSet,
    AlumniDirectMessageViewSet,
    AlumniDirectoryFilterViewSet,
    AlumniDiscussionLikeViewSet,
    AlumniDiscussionReplyViewSet,
    AlumniDiscussionViewSet,
    AlumniDonationReceiptViewSet,
    AlumniDonationRecurringViewSet,
    AlumniDonationViewSet,
    AlumniEmailCampaignAnalyticsViewSet,
    AlumniEventRSVPViewSet,
    AlumniEventViewSet,
    AlumniGroupMemberViewSet,
    AlumniGroupPostViewSet,
    AlumniGroupViewSet,
    AlumniJobApplicationViewSet,
    AlumniJobPostingViewSet,
    AlumniMentorshipViewSet,
    AlumniNewsletterViewSet,
    AlumniPhotoAlbumViewSet,
    AlumniPhotoCommentViewSet,
    AlumniPhotoViewSet,
    AlumniPodcastEpisodeViewSet,
    AlumniPodcastSubscriptionViewSet,
    AlumniPollOptionViewSet,
    AlumniPollResponseViewSet,
    AlumniPollViewSet,
    AlumniProfileCompletenessViewSet,
    AlumniProfileViewSet,
    AlumniProfileViewViewSet,
    AlumniReferralViewSet,
    AlumniSuccessStoryViewSet,
    AlumniVerificationViewSet,
    AlumniVideoGalleryViewSet,
    AlumniVolunteerSignupViewSet,
    AlumniVolunteerViewSet,
)

app_name = "alumni_v1"
router = DefaultRouter()
# Profile & Verification
router.register(r"profiles", AlumniProfileViewSet, basename="alumni-profile")
router.register(r"verifications", AlumniVerificationViewSet, basename="alumni-verification")
# Events
router.register(r"events", AlumniEventViewSet, basename="alumni-event")
router.register(r"rsvps", AlumniEventRSVPViewSet, basename="alumni-rsvp")
# Donations
router.register(r"donations", AlumniDonationViewSet, basename="alumni-donation")
router.register(r"receipts", AlumniDonationReceiptViewSet, basename="alumni-receipt")
router.register(r"recurring-donations", AlumniDonationRecurringViewSet, basename="alumni-recurring-donation")
# Chapters
router.register(r"chapters", AlumniChapterViewSet, basename="alumni-chapter")
router.register(r"chapter-members", AlumniChapterMemberViewSet, basename="alumni-chapter-member")
# Mentorship
router.register(r"mentorships", AlumniMentorshipViewSet, basename="alumni-mentorship")
# Jobs
router.register(r"job-postings", AlumniJobPostingViewSet, basename="alumni-job-posting")
router.register(r"job-applications", AlumniJobApplicationViewSet, basename="alumni-job-application")
# Community
router.register(r"discussions", AlumniDiscussionViewSet, basename="alumni-discussion")
router.register(r"discussion-replies", AlumniDiscussionReplyViewSet, basename="alumni-discussion-reply")
router.register(r"discussion-likes", AlumniDiscussionLikeViewSet, basename="alumni-discussion-like")
# Newsletters & Campaigns
router.register(r"newsletters", AlumniNewsletterViewSet, basename="alumni-newsletter")
router.register(r"campaigns", AlumniCampaignViewSet, basename="alumni-campaign")
router.register(r"campaign-donations", AlumniCampaignDonationViewSet, basename="alumni-campaign-donation")
# Badges
router.register(r"badges", AlumniBadgeViewSet, basename="alumni-badge")
router.register(r"badge-awards", AlumniBadgeAwardViewSet, basename="alumni-badge-award")
# Activity Feed
router.register(r"activity-feed", AlumniActivityFeedViewSet, basename="alumni-activity-feed")
# Groups
router.register(r"groups", AlumniGroupViewSet, basename="alumni-group")
router.register(r"group-members", AlumniGroupMemberViewSet, basename="alumni-group-member")
router.register(r"group-posts", AlumniGroupPostViewSet, basename="alumni-group-post")
# Volunteer
router.register(r"volunteer-opportunities", AlumniVolunteerViewSet, basename="alumni-volunteer")
router.register(r"volunteer-signups", AlumniVolunteerSignupViewSet, basename="alumni-volunteer-signup")
# Polls
router.register(r"polls", AlumniPollViewSet, basename="alumni-poll")
router.register(r"poll-options", AlumniPollOptionViewSet, basename="alumni-poll-option")
router.register(r"poll-responses", AlumniPollResponseViewSet, basename="alumni-poll-response")
# Success Stories
router.register(r"success-stories", AlumniSuccessStoryViewSet, basename="alumni-success-story")
# Referrals
router.register(r"referrals", AlumniReferralViewSet, basename="alumni-referral")
# Messaging
router.register(r"messages", AlumniDirectMessageViewSet, basename="alumni-message")
router.register(r"conversations", AlumniConversationViewSet, basename="alumni-conversation")
# Calendar
router.register(r"calendar-events", AlumniCalendarEventViewSet, basename="alumni-calendar-event")
router.register(r"calendar-rsvps", AlumniCalendarRSVPViewSet, basename="alumni-calendar-rsvp")
# Photos
router.register(r"photo-albums", AlumniPhotoAlbumViewSet, basename="alumni-photo-album")
router.register(r"photos", AlumniPhotoViewSet, basename="alumni-photo")
router.register(r"photo-comments", AlumniPhotoCommentViewSet, basename="alumni-photo-comment")
# Videos
router.register(r"videos", AlumniVideoGalleryViewSet, basename="alumni-video")
# Directory
router.register(r"directory-filters", AlumniDirectoryFilterViewSet, basename="alumni-directory-filter")
router.register(r"profile-views", AlumniProfileViewViewSet, basename="alumni-profile-view")
router.register(r"profile-completeness", AlumniProfileCompletenessViewSet, basename="alumni-profile-completeness")
# Email Analytics
router.register(r"email-analytics", AlumniEmailCampaignAnalyticsViewSet, basename="alumni-email-analytics")
# Podcasts
router.register(r"podcast-episodes", AlumniPodcastEpisodeViewSet, basename="alumni-podcast-episode")
router.register(r"podcast-subscriptions", AlumniPodcastSubscriptionViewSet, basename="alumni-podcast-subscription")
# Awards
router.register(r"award-categories", AlumniAwardCategoryViewSet, basename="alumni-award-category")
router.register(r"awards", AlumniAwardViewSet, basename="alumni-award")
router.register(r"award-nominations", AlumniAwardNominationViewSet, basename="alumni-award-nomination")

urlpatterns = [path("", include(router.urls))]
