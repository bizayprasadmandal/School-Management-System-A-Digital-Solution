from django.contrib import admin

from .models import (
    AlumniActivityFeed,
    AlumniAward,
    AlumniAwardCategory,
    AlumniAwardNomination,
    AlumniBadge,
    AlumniBadgeAward,
    AlumniCalendarEvent,
    AlumniCalendarRSVP,
    AlumniCampaign,
    AlumniCampaignDonation,
    AlumniChapter,
    AlumniChapterMember,
    AlumniConversation,
    AlumniDirectMessage,
    AlumniDirectoryFilter,
    AlumniDiscussion,
    AlumniDiscussionLike,
    AlumniDiscussionReply,
    AlumniDonation,
    AlumniDonationReceipt,
    AlumniDonationRecurring,
    AlumniEmailCampaignAnalytics,
    AlumniEvent,
    AlumniEventRSVP,
    AlumniGroup,
    AlumniGroupMember,
    AlumniGroupPost,
    AlumniJobApplication,
    AlumniJobPosting,
    AlumniMentorship,
    AlumniNewsletter,
    AlumniPhoto,
    AlumniPhotoAlbum,
    AlumniPhotoComment,
    AlumniPodcastEpisode,
    AlumniPodcastSubscription,
    AlumniPoll,
    AlumniPollOption,
    AlumniPollResponse,
    AlumniProfile,
    AlumniProfileCompleteness,
    AlumniProfileView,
    AlumniReferral,
    AlumniSuccessStory,
    AlumniVerification,
    AlumniVideoGallery,
    AlumniVolunteer,
    AlumniVolunteerSignup,
)


@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "graduation_year", "occupation", "employer", "city", "engagement_score"]
    list_filter = ["graduation_year", "employment_status", "country"]
    search_fields = ["user__full_name", "user__email", "occupation", "employer"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(AlumniVerification)
class AlumniVerificationAdmin(admin.ModelAdmin):
    list_display = ["alumni", "verification_method", "status", "verified_at"]
    list_filter = ["status", "verification_method"]
    search_fields = ["alumni__user__full_name"]


@admin.register(AlumniEvent)
class AlumniEventAdmin(admin.ModelAdmin):
    list_display = ["title", "event_date", "location", "status"]
    list_filter = ["status"]
    search_fields = ["title"]


@admin.register(AlumniEventRSVP)
class AlumniEventRSVPAdmin(admin.ModelAdmin):
    list_display = ["alumni", "event", "status", "registered_at"]
    list_filter = ["status"]
    search_fields = ["alumni__user__full_name", "event__title"]


@admin.register(AlumniDonation)
class AlumniDonationAdmin(admin.ModelAdmin):
    list_display = ["alumni", "amount", "fund_type", "donation_date", "is_recurring"]
    list_filter = ["fund_type", "is_recurring"]
    search_fields = ["alumni__user__full_name"]


@admin.register(AlumniDonationReceipt)
class AlumniDonationReceiptAdmin(admin.ModelAdmin):
    list_display = ["receipt_number", "donation", "tax_deductible_amount", "status"]
    list_filter = ["status"]
    search_fields = ["receipt_number"]


@admin.register(AlumniChapter)
class AlumniChapterAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "country", "president", "is_active"]
    list_filter = ["is_active", "country"]
    search_fields = ["name", "city"]


@admin.register(AlumniChapterMember)
class AlumniChapterMemberAdmin(admin.ModelAdmin):
    list_display = ["alumni", "chapter", "role", "is_active"]
    list_filter = ["role", "is_active"]
    search_fields = ["alumni__user__full_name", "chapter__name"]


@admin.register(AlumniMentorship)
class AlumniMentorshipAdmin(admin.ModelAdmin):
    list_display = ["mentor", "mentee", "focus_area", "status"]
    list_filter = ["status", "focus_area"]
    search_fields = ["mentor__user__full_name", "mentee__full_name"]


@admin.register(AlumniJobPosting)
class AlumniJobPostingAdmin(admin.ModelAdmin):
    list_display = ["title", "company", "job_type", "status", "created_at"]
    list_filter = ["status", "job_type", "experience_level"]
    search_fields = ["title", "company"]


@admin.register(AlumniJobApplication)
class AlumniJobApplicationAdmin(admin.ModelAdmin):
    list_display = ["applicant", "job", "status", "applied_at"]
    list_filter = ["status"]
    search_fields = ["applicant__full_name", "job__title"]


@admin.register(AlumniDiscussion)
class AlumniDiscussionAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "category", "status", "views_count"]
    list_filter = ["status", "category"]
    search_fields = ["title", "content"]


@admin.register(AlumniDiscussionReply)
class AlumniDiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ["discussion", "author", "created_at"]
    search_fields = ["content"]


@admin.register(AlumniDiscussionLike)
class AlumniDiscussionLikeAdmin(admin.ModelAdmin):
    list_display = ["alumni", "target_type", "created_at"]
    list_filter = ["target_type"]


@admin.register(AlumniNewsletter)
class AlumniNewsletterAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "total_sent", "total_opened", "created_at"]
    list_filter = ["status"]
    search_fields = ["title", "subject"]


@admin.register(AlumniCampaign)
class AlumniCampaignAdmin(admin.ModelAdmin):
    list_display = ["title", "campaign_type", "status", "goal_amount", "raised_amount", "progress_percentage"]
    list_filter = ["status", "campaign_type"]
    search_fields = ["title", "description"]


@admin.register(AlumniCampaignDonation)
class AlumniCampaignDonationAdmin(admin.ModelAdmin):
    list_display = ["campaign", "donation", "is_matching"]
    list_filter = ["is_matching"]


@admin.register(AlumniBadge)
class AlumniBadgeAdmin(admin.ModelAdmin):
    list_display = ["name", "badge_type", "total_awarded", "is_active"]
    list_filter = ["badge_type", "is_active"]
    search_fields = ["name"]


@admin.register(AlumniBadgeAward)
class AlumniBadgeAwardAdmin(admin.ModelAdmin):
    list_display = ["badge", "alumni", "awarded_at", "is_public"]
    list_filter = ["is_public"]
    search_fields = ["badge__name", "alumni__user__full_name"]


@admin.register(AlumniActivityFeed)
class AlumniActivityFeedAdmin(admin.ModelAdmin):
    list_display = ["alumni", "activity_type", "title", "created_at"]
    list_filter = ["activity_type"]
    search_fields = ["title"]


@admin.register(AlumniGroup)
class AlumniGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "group_type", "member_count", "is_active"]
    list_filter = ["group_type", "is_active"]
    search_fields = ["name"]


@admin.register(AlumniGroupMember)
class AlumniGroupMemberAdmin(admin.ModelAdmin):
    list_display = ["alumni", "group", "role", "status"]
    list_filter = ["role", "status"]
    search_fields = ["alumni__user__full_name", "group__name"]


@admin.register(AlumniGroupPost)
class AlumniGroupPostAdmin(admin.ModelAdmin):
    list_display = ["group", "author", "title", "is_pinned", "created_at"]
    list_filter = ["is_pinned"]
    search_fields = ["title", "content"]


@admin.register(AlumniVolunteer)
class AlumniVolunteerAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "time_commitment", "current_volunteers"]
    list_filter = ["status", "time_commitment"]
    search_fields = ["title"]


@admin.register(AlumniVolunteerSignup)
class AlumniVolunteerSignupAdmin(admin.ModelAdmin):
    list_display = ["alumni", "opportunity", "status", "hours_logged"]
    list_filter = ["status"]
    search_fields = ["alumni__user__full_name", "opportunity__title"]


@admin.register(AlumniPoll)
class AlumniPollAdmin(admin.ModelAdmin):
    list_display = ["title", "poll_type", "status", "total_responses"]
    list_filter = ["poll_type", "status"]
    search_fields = ["title"]


@admin.register(AlumniPollOption)
class AlumniPollOptionAdmin(admin.ModelAdmin):
    list_display = ["poll", "text", "vote_count"]
    search_fields = ["text"]


@admin.register(AlumniPollResponse)
class AlumniPollResponseAdmin(admin.ModelAdmin):
    list_display = ["poll", "alumni", "option", "responded_at"]
    search_fields = ["alumni__user__full_name"]


@admin.register(AlumniSuccessStory)
class AlumniSuccessStoryAdmin(admin.ModelAdmin):
    list_display = ["title", "alumni", "story_type", "status", "featured"]
    list_filter = ["status", "story_type", "featured"]
    search_fields = ["title", "content"]


@admin.register(AlumniReferral)
class AlumniReferralAdmin(admin.ModelAdmin):
    list_display = ["referrer", "referred_name", "referral_type", "status", "referred_at"]
    list_filter = ["referral_type", "status"]
    search_fields = ["referred_name", "referred_email"]


@admin.register(AlumniDirectMessage)
class AlumniDirectMessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "receiver", "message_type", "is_read", "created_at"]
    list_filter = ["message_type", "is_read"]
    search_fields = ["sender__user__full_name", "receiver__user__full_name", "content"]


@admin.register(AlumniConversation)
class AlumniConversationAdmin(admin.ModelAdmin):
    list_display = ["participant1", "participant2", "last_message_at"]
    search_fields = ["participant1__user__full_name", "participant2__user__full_name"]


@admin.register(AlumniCalendarEvent)
class AlumniCalendarEventAdmin(admin.ModelAdmin):
    list_display = ["title", "event_type", "start_datetime", "end_datetime", "is_virtual"]
    list_filter = ["event_type", "is_virtual", "recurrence_type"]
    search_fields = ["title", "location"]


@admin.register(AlumniCalendarRSVP)
class AlumniCalendarRSVPAdmin(admin.ModelAdmin):
    list_display = ["alumni", "event", "status", "responded_at"]
    list_filter = ["status"]
    search_fields = ["alumni__user__full_name", "event__title"]


@admin.register(AlumniPhotoAlbum)
class AlumniPhotoAlbumAdmin(admin.ModelAdmin):
    list_display = ["title", "photo_count", "is_public", "created_at"]
    list_filter = ["is_public"]
    search_fields = ["title"]


@admin.register(AlumniPhoto)
class AlumniPhotoAdmin(admin.ModelAdmin):
    list_display = ["album", "caption", "likes_count", "is_featured", "uploaded_at"]
    list_filter = ["is_featured"]
    search_fields = ["caption"]


@admin.register(AlumniPhotoComment)
class AlumniPhotoCommentAdmin(admin.ModelAdmin):
    list_display = ["photo", "author", "created_at"]
    search_fields = ["content"]


@admin.register(AlumniVideoGallery)
class AlumniVideoGalleryAdmin(admin.ModelAdmin):
    list_display = ["title", "video_type", "view_count", "is_featured", "uploaded_at"]
    list_filter = ["video_type", "is_featured"]
    search_fields = ["title", "description"]


@admin.register(AlumniDirectoryFilter)
class AlumniDirectoryFilterAdmin(admin.ModelAdmin):
    list_display = ["alumni", "name", "is_public", "created_at"]
    list_filter = ["is_public"]
    search_fields = ["name"]


@admin.register(AlumniProfileView)
class AlumniProfileViewAdmin(admin.ModelAdmin):
    list_display = ["viewer", "viewed", "viewed_at"]
    search_fields = ["viewer__user__full_name", "viewed__user__full_name"]


@admin.register(AlumniProfileCompleteness)
class AlumniProfileCompletenessAdmin(admin.ModelAdmin):
    list_display = ["alumni", "completion_percentage", "last_calculated_at"]
    search_fields = ["alumni__user__full_name"]


@admin.register(AlumniEmailCampaignAnalytics)
class AlumniEmailCampaignAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["newsletter", "alumni", "event_type", "event_at"]
    list_filter = ["event_type"]
    search_fields = ["alumni__user__full_name", "newsletter__title"]


@admin.register(AlumniDonationRecurring)
class AlumniDonationRecurringAdmin(admin.ModelAdmin):
    list_display = ["alumni", "amount", "frequency", "status", "next_payment_date"]
    list_filter = ["status", "frequency"]
    search_fields = ["alumni__user__full_name"]


@admin.register(AlumniPodcastEpisode)
class AlumniPodcastEpisodeAdmin(admin.ModelAdmin):
    list_display = ["title", "episode_type", "status", "play_count", "published_at"]
    list_filter = ["episode_type", "status"]
    search_fields = ["title", "description"]


@admin.register(AlumniPodcastSubscription)
class AlumniPodcastSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["alumni", "is_active", "subscribed_at"]
    list_filter = ["is_active"]


@admin.register(AlumniAwardCategory)
class AlumniAwardCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(AlumniAward)
class AlumniAwardAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "year", "status", "total_nominations"]
    list_filter = ["status", "year"]
    search_fields = ["title", "description"]


@admin.register(AlumniAwardNomination)
class AlumniAwardNominationAdmin(admin.ModelAdmin):
    list_display = ["nominee", "award", "nominated_by", "status", "nominated_at"]
    list_filter = ["status"]
    search_fields = ["nominee__user__full_name", "nominated_by__user__full_name"]
