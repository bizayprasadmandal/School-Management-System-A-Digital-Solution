"""Alumni serializers."""

from rest_framework import serializers

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


class AlumniProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    employment_status_display = serializers.CharField(source="get_employment_status_display", read_only=True)

    class Meta:
        model = AlumniProfile
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "graduation_year",
            "student_id",
            "occupation",
            "employer",
            "employment_status",
            "employment_status_display",
            "phone",
            "address",
            "city",
            "country",
            "linkedin_url",
            "facebook_url",
            "twitter_handle",
            "bio",
            "skills",
            "interests",
            "is_newsletter_subscribed",
            "is_visible_to_public",
            "engagement_score",
            "last_activity_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "engagement_score", "last_activity_at"]


class AlumniVerificationSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    verification_method_display = serializers.CharField(source="get_verification_method_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    verified_by_name = serializers.CharField(source="verified_by.full_name", read_only=True, default=None)

    class Meta:
        model = AlumniVerification
        fields = [
            "id",
            "alumni",
            "alumni_name",
            "verification_method",
            "verification_method_display",
            "status",
            "status_display",
            "document_url",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "rejection_reason",
            "expires_at",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "verified_at", "created_at"]


class AlumniEventSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    organizer_name = serializers.CharField(source="organizer.full_name", read_only=True, default=None)
    rsvp_count = serializers.SerializerMethodField()

    class Meta:
        model = AlumniEvent
        fields = [
            "id",
            "title",
            "description",
            "event_date",
            "end_date",
            "location",
            "venue",
            "max_attendees",
            "registration_deadline",
            "fee_amount",
            "status",
            "status_display",
            "organizer",
            "organizer_name",
            "cover_image_url",
            "rsvp_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_rsvp_count(self, obj):
        return obj.rsvps.exclude(status="cancelled").count() if hasattr(obj, "rsvps") else 0


class AlumniEventRSVPSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlumniEventRSVP
        fields = [
            "id",
            "event",
            "event_title",
            "alumni",
            "alumni_name",
            "status",
            "status_display",
            "registered_at",
            "checked_in_at",
            "check_in_code",
            "notes",
        ]
        read_only_fields = ["id", "registered_at", "checked_in_at", "check_in_code"]


class AlumniDonationSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    fund_type_display = serializers.CharField(source="get_fund_type_display", read_only=True)

    class Meta:
        model = AlumniDonation
        fields = [
            "id",
            "alumni",
            "alumni_name",
            "amount",
            "fund_type",
            "fund_type_display",
            "payment_method",
            "transaction_id",
            "donation_date",
            "is_anonymous",
            "is_recurring",
            "recurring_frequency",
            "message",
            "created_at",
        ]
        read_only_fields = ["id", "donation_date", "created_at"]


class AlumniDonationReceiptSerializer(serializers.ModelSerializer):
    donation_amount = serializers.DecimalField(
        source="donation.amount", max_digits=14, decimal_places=2, read_only=True
    )
    alumni_name = serializers.CharField(source="donation.alumni.user.full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlumniDonationReceipt
        fields = [
            "id",
            "donation",
            "donation_amount",
            "alumni_name",
            "receipt_number",
            "receipt_date",
            "tax_deductible_amount",
            "status",
            "status_display",
            "pdf_url",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "receipt_number", "receipt_date", "created_at"]


class AlumniChapterSerializer(serializers.ModelSerializer):
    president_name = serializers.CharField(source="president.full_name", read_only=True, default=None)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = AlumniChapter
        fields = [
            "id",
            "name",
            "city",
            "country",
            "description",
            "president",
            "president_name",
            "is_active",
            "member_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_member_count(self, obj):
        if hasattr(obj, "member_count") and obj.member_count is not None:
            return obj.member_count
        return obj.members.filter(is_active=True).count() if hasattr(obj, "members") else 0


class AlumniChapterMemberSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    chapter_name = serializers.CharField(source="chapter.name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = AlumniChapterMember
        fields = [
            "id",
            "chapter",
            "chapter_name",
            "alumni",
            "alumni_name",
            "role",
            "role_display",
            "joined_at",
            "is_active",
        ]
        read_only_fields = ["id", "joined_at"]


class AlumniMentorshipSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source="mentor.user.full_name", read_only=True)
    mentee_name = serializers.CharField(source="mentee.full_name", read_only=True)
    focus_area_display = serializers.CharField(source="get_focus_area_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlumniMentorship
        fields = [
            "id",
            "mentor",
            "mentor_name",
            "mentee",
            "mentee_name",
            "focus_area",
            "focus_area_display",
            "status",
            "status_display",
            "start_date",
            "end_date",
            "goals",
            "meeting_frequency",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AlumniJobPostingSerializer(serializers.ModelSerializer):
    posted_by_name = serializers.CharField(source="posted_by.user.full_name", read_only=True)
    job_type_display = serializers.CharField(source="get_job_type_display", read_only=True)
    experience_level_display = serializers.CharField(source="get_experience_level_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = AlumniJobPosting
        fields = [
            "id",
            "posted_by",
            "posted_by_name",
            "title",
            "company",
            "description",
            "location",
            "is_remote",
            "job_type",
            "job_type_display",
            "experience_level",
            "experience_level_display",
            "salary_min",
            "salary_max",
            "application_url",
            "application_email",
            "status",
            "status_display",
            "expires_at",
            "application_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_application_count(self, obj):
        return obj.applications.count() if hasattr(obj, "applications") else 0


class AlumniJobApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source="applicant.full_name", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(source="job.company", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlumniJobApplication
        fields = [
            "id",
            "job",
            "job_title",
            "company_name",
            "applicant",
            "applicant_name",
            "resume_url",
            "cover_letter",
            "status",
            "status_display",
            "applied_at",
            "notes",
        ]
        read_only_fields = ["id", "applied_at"]


class AlumniDiscussionSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.user.full_name", read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = AlumniDiscussion
        fields = [
            "id",
            "author",
            "author_name",
            "title",
            "content",
            "category",
            "category_display",
            "status",
            "status_display",
            "views_count",
            "likes_count",
            "is_anonymous",
            "reply_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "views_count", "likes_count", "created_at", "updated_at"]

    def get_reply_count(self, obj):
        return obj.replies.count() if hasattr(obj, "replies") else 0


class AlumniDiscussionReplySerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.user.full_name", read_only=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = AlumniDiscussionReply
        fields = [
            "id",
            "discussion",
            "author",
            "author_name",
            "content",
            "parent",
            "likes_count",
            "is_anonymous",
            "children_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "likes_count", "created_at", "updated_at"]

    def get_children_count(self, obj):
        return obj.children.count() if hasattr(obj, "children") else 0


class AlumniDiscussionLikeSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)

    class Meta:
        model = AlumniDiscussionLike
        fields = [
            "id",
            "alumni",
            "alumni_name",
            "target_type",
            "discussion",
            "reply",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AlumniNewsletterSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    open_rate = serializers.ReadOnlyField()
    click_rate = serializers.ReadOnlyField()

    class Meta:
        model = AlumniNewsletter
        fields = [
            "id",
            "title",
            "subject",
            "content",
            "plain_text",
            "status",
            "scheduled_at",
            "sent_at",
            "target_graduation_years",
            "target_cities",
            "total_sent",
            "total_opened",
            "total_clicked",
            "total_bounced",
            "total_unsubscribed",
            "open_rate",
            "click_rate",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "sent_at",
            "total_sent",
            "total_opened",
            "total_clicked",
            "total_bounced",
            "total_unsubscribed",
            "created_at",
            "updated_at",
        ]


class AlumniCampaignSerializer(serializers.ModelSerializer):
    campaign_type_display = serializers.CharField(source="get_campaign_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = AlumniCampaign
        fields = [
            "id",
            "title",
            "description",
            "campaign_type",
            "campaign_type_display",
            "status",
            "status_display",
            "goal_amount",
            "raised_amount",
            "donor_count",
            "progress_percentage",
            "is_active",
            "start_date",
            "end_date",
            "has_matching",
            "matching_multiplier",
            "matching_deadline",
            "cover_image_url",
            "video_url",
            "is_anonymous_allowed",
            "is_recurring_allowed",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "raised_amount", "donor_count", "created_at", "updated_at"]


class AlumniCampaignDonationSerializer(serializers.ModelSerializer):
    campaign_title = serializers.CharField(source="campaign.title", read_only=True)
    donation_amount = serializers.DecimalField(
        source="donation.amount", max_digits=14, decimal_places=2, read_only=True
    )

    class Meta:
        model = AlumniCampaignDonation
        fields = [
            "id",
            "campaign",
            "campaign_title",
            "donation",
            "donation_amount",
            "is_matching",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AlumniBadgeSerializer(serializers.ModelSerializer):
    badge_type_display = serializers.CharField(source="get_badge_type_display", read_only=True)

    class Meta:
        model = AlumniBadge
        fields = [
            "id",
            "name",
            "description",
            "badge_type",
            "badge_type_display",
            "icon_url",
            "color",
            "criteria_description",
            "criteria_value",
            "total_awarded",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "total_awarded", "created_at"]


class AlumniBadgeAwardSerializer(serializers.ModelSerializer):
    badge_name = serializers.CharField(source="badge.name", read_only=True)
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    awarded_by_name = serializers.CharField(source="awarded_by.full_name", read_only=True, default=None)

    class Meta:
        model = AlumniBadgeAward
        fields = [
            "id",
            "badge",
            "badge_name",
            "alumni",
            "alumni_name",
            "awarded_at",
            "awarded_by",
            "awarded_by_name",
            "reason",
            "is_public",
        ]
        read_only_fields = ["id", "awarded_at"]


class AlumniActivityFeedSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    activity_type_display = serializers.CharField(source="get_activity_type_display", read_only=True)

    class Meta:
        model = AlumniActivityFeed
        fields = [
            "id",
            "alumni",
            "alumni_name",
            "activity_type",
            "activity_type_display",
            "title",
            "description",
            "reference_id",
            "reference_model",
            "metadata",
            "is_visible",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AlumniGroupSerializer(serializers.ModelSerializer):
    admin_name = serializers.CharField(source="admin.user.full_name", read_only=True, default=None)
    group_type_display = serializers.CharField(source="get_group_type_display", read_only=True)

    class Meta:
        model = AlumniGroup
        fields = [
            "id",
            "name",
            "description",
            "group_type",
            "group_type_display",
            "admin",
            "admin_name",
            "is_private",
            "is_active",
            "max_members",
            "member_count",
            "cover_image_url",
            "logo_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "member_count", "created_at", "updated_at"]


class AlumniGroupMemberSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlumniGroupMember
        fields = [
            "id",
            "group",
            "group_name",
            "alumni",
            "alumni_name",
            "role",
            "role_display",
            "status",
            "status_display",
            "joined_at",
            "is_muted",
        ]
        read_only_fields = ["id", "joined_at"]


class AlumniGroupPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.user.full_name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)

    class Meta:
        model = AlumniGroupPost
        fields = [
            "id",
            "group",
            "group_name",
            "author",
            "author_name",
            "title",
            "content",
            "attachment_url",
            "likes_count",
            "comments_count",
            "is_pinned",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "likes_count", "comments_count", "created_at", "updated_at"]


class AlumniVolunteerSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    time_commitment_display = serializers.CharField(source="get_time_commitment_display", read_only=True)
    organizer_name = serializers.CharField(source="organizer.full_name", read_only=True, default=None)

    class Meta:
        model = AlumniVolunteer
        fields = [
            "id",
            "title",
            "description",
            "skills_required",
            "max_volunteers",
            "current_volunteers",
            "start_date",
            "end_date",
            "time_commitment",
            "time_commitment_display",
            "estimated_hours",
            "location",
            "is_remote",
            "status",
            "status_display",
            "organizer",
            "organizer_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "current_volunteers", "created_at", "updated_at"]


class AlumniVolunteerSignupSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    opportunity_title = serializers.CharField(source="opportunity.title", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlumniVolunteerSignup
        fields = [
            "id",
            "opportunity",
            "opportunity_title",
            "alumni",
            "alumni_name",
            "status",
            "status_display",
            "hours_logged",
            "feedback",
            "rating",
            "signed_up_at",
            "completed_at",
        ]
        read_only_fields = ["id", "signed_up_at"]


class AlumniPollSerializer(serializers.ModelSerializer):
    poll_type_display = serializers.CharField(source="get_poll_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = AlumniPoll
        fields = [
            "id",
            "title",
            "description",
            "poll_type",
            "poll_type_display",
            "status",
            "status_display",
            "is_anonymous",
            "allow_multiple_answers",
            "start_date",
            "end_date",
            "total_responses",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_responses", "created_at", "updated_at"]


class AlumniPollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniPollOption
        fields = [
            "id",
            "poll",
            "text",
            "vote_count",
            "order",
        ]
        read_only_fields = ["id", "vote_count"]


class AlumniPollResponseSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    option_text = serializers.CharField(source="option.text", read_only=True)

    class Meta:
        model = AlumniPollResponse
        fields = [
            "id",
            "poll",
            "alumni",
            "alumni_name",
            "option",
            "option_text",
            "text_response",
            "responded_at",
        ]
        read_only_fields = ["id", "responded_at"]


class AlumniSuccessStorySerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    story_type_display = serializers.CharField(source="get_story_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlumniSuccessStory
        fields = [
            "id",
            "alumni",
            "alumni_name",
            "title",
            "content",
            "story_type",
            "story_type_display",
            "status",
            "status_display",
            "cover_image_url",
            "video_url",
            "views_count",
            "likes_count",
            "slug",
            "meta_description",
            "featured",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "views_count", "likes_count", "published_at", "created_at", "updated_at"]


class AlumniReferralSerializer(serializers.ModelSerializer):
    referrer_name = serializers.CharField(source="referrer.user.full_name", read_only=True)
    referral_type_display = serializers.CharField(source="get_referral_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    job_title = serializers.CharField(source="job_posting.title", read_only=True, default=None)

    class Meta:
        model = AlumniReferral
        fields = [
            "id",
            "referrer",
            "referrer_name",
            "referred_name",
            "referred_email",
            "referred_phone",
            "referral_type",
            "referral_type_display",
            "status",
            "status_display",
            "notes",
            "job_posting",
            "job_title",
            "referred_at",
            "contacted_at",
            "converted_at",
            "reward_points",
            "reward_description",
        ]
        read_only_fields = ["id", "referred_at", "contacted_at", "converted_at"]


class AlumniDirectMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.user.full_name", read_only=True)
    receiver_name = serializers.CharField(source="receiver.user.full_name", read_only=True)
    message_type_display = serializers.CharField(source="get_message_type_display", read_only=True)

    class Meta:
        model = AlumniDirectMessage
        fields = [
            "id",
            "sender",
            "sender_name",
            "receiver",
            "receiver_name",
            "message_type",
            "message_type_display",
            "content",
            "attachment_url",
            "is_read",
            "read_at",
            "is_deleted_by_sender",
            "is_deleted_by_receiver",
            "created_at",
        ]
        read_only_fields = ["id", "read_at", "created_at"]


class AlumniConversationSerializer(serializers.ModelSerializer):
    participant1_name = serializers.CharField(source="participant1.user.full_name", read_only=True)
    participant2_name = serializers.CharField(source="participant2.user.full_name", read_only=True)
    last_message_content = serializers.CharField(source="last_message.content", read_only=True, default=None)

    class Meta:
        model = AlumniConversation
        fields = [
            "id",
            "participant1",
            "participant1_name",
            "participant2",
            "participant2_name",
            "last_message",
            "last_message_content",
            "last_message_at",
            "is_archived_by_p1",
            "is_archived_by_p2",
            "created_at",
        ]
        read_only_fields = ["id", "last_message_at", "created_at"]


class AlumniCalendarEventSerializer(serializers.ModelSerializer):
    event_type_display = serializers.CharField(source="get_event_type_display", read_only=True)
    recurrence_type_display = serializers.CharField(source="get_recurrence_type_display", read_only=True)
    organizer_name = serializers.CharField(source="organizer.full_name", read_only=True, default=None)
    ical_data = serializers.SerializerMethodField()

    class Meta:
        model = AlumniCalendarEvent
        fields = [
            "id",
            "title",
            "description",
            "event_type",
            "event_type_display",
            "start_datetime",
            "end_datetime",
            "all_day",
            "timezone",
            "recurrence_type",
            "recurrence_type_display",
            "recurrence_end_date",
            "location",
            "venue",
            "is_virtual",
            "virtual_link",
            "ical_uid",
            "google_event_id",
            "max_attendees",
            "requires_registration",
            "registration_deadline",
            "organizer",
            "organizer_name",
            "is_published",
            "ical_data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "ical_uid", "created_at", "updated_at"]

    def get_ical_data(self, obj):
        return obj.generate_ical() if obj.ical_uid else None


class AlumniCalendarRSVPSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    event_title = serializers.CharField(source="event.title", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlumniCalendarRSVP
        fields = [
            "id",
            "event",
            "event_title",
            "alumni",
            "alumni_name",
            "status",
            "status_display",
            "responded_at",
        ]
        read_only_fields = ["id", "responded_at"]


class AlumniPhotoAlbumSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.user.full_name", read_only=True, default=None)

    class Meta:
        model = AlumniPhotoAlbum
        fields = [
            "id",
            "title",
            "description",
            "event",
            "cover_photo_url",
            "photo_count",
            "is_public",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "photo_count", "created_at", "updated_at"]


class AlumniPhotoSerializer(serializers.ModelSerializer):
    album_title = serializers.CharField(source="album.title", read_only=True)
    uploaded_by_name = serializers.CharField(source="uploaded_by.user.full_name", read_only=True, default=None)

    class Meta:
        model = AlumniPhoto
        fields = [
            "id",
            "album",
            "album_title",
            "photo_url",
            "thumbnail_url",
            "caption",
            "uploaded_by",
            "uploaded_by_name",
            "likes_count",
            "comments_count",
            "is_featured",
            "uploaded_at",
        ]
        read_only_fields = ["id", "likes_count", "comments_count", "uploaded_at"]


class AlumniPhotoCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.user.full_name", read_only=True)

    class Meta:
        model = AlumniPhotoComment
        fields = [
            "id",
            "photo",
            "author",
            "author_name",
            "content",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AlumniVideoGallerySerializer(serializers.ModelSerializer):
    video_type_display = serializers.CharField(source="get_video_type_display", read_only=True)
    uploaded_by_name = serializers.CharField(source="uploaded_by.user.full_name", read_only=True, default=None)
    duration_formatted = serializers.ReadOnlyField()

    class Meta:
        model = AlumniVideoGallery
        fields = [
            "id",
            "title",
            "description",
            "video_type",
            "video_type_display",
            "video_url",
            "thumbnail_url",
            "duration_seconds",
            "duration_formatted",
            "view_count",
            "like_count",
            "event",
            "uploaded_by",
            "uploaded_by_name",
            "is_featured",
            "tags",
            "uploaded_at",
            "updated_at",
        ]
        read_only_fields = ["id", "view_count", "like_count", "uploaded_at", "updated_at"]


class AlumniDirectoryFilterSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)

    class Meta:
        model = AlumniDirectoryFilter
        fields = [
            "id",
            "alumni",
            "alumni_name",
            "name",
            "graduation_year_min",
            "graduation_year_max",
            "cities",
            "countries",
            "industries",
            "companies",
            "skills",
            "employment_status",
            "is_public",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AlumniProfileViewSerializer(serializers.ModelSerializer):
    viewer_name = serializers.CharField(source="viewer.user.full_name", read_only=True)
    viewed_name = serializers.CharField(source="viewed.user.full_name", read_only=True)

    class Meta:
        model = AlumniProfileView
        fields = [
            "id",
            "viewer",
            "viewer_name",
            "viewed",
            "viewed_name",
            "viewed_at",
        ]
        read_only_fields = ["id", "viewed_at"]


class AlumniProfileCompletenessSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)

    class Meta:
        model = AlumniProfileCompleteness
        fields = [
            "id",
            "alumni",
            "alumni_name",
            "has_photo",
            "has_bio",
            "has_occupation",
            "has_employer",
            "has_phone",
            "has_address",
            "has_linkedin",
            "has_skills",
            "has_interests",
            "has_graduation_year",
            "completion_percentage",
            "last_calculated_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "completion_percentage", "last_calculated_at", "created_at", "updated_at"]


class AlumniEmailCampaignAnalyticsSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    newsletter_title = serializers.CharField(source="newsletter.title", read_only=True)
    event_type_display = serializers.CharField(source="get_event_type_display", read_only=True)

    class Meta:
        model = AlumniEmailCampaignAnalytics
        fields = [
            "id",
            "newsletter",
            "newsletter_title",
            "alumni",
            "alumni_name",
            "event_type",
            "event_type_display",
            "ip_address",
            "user_agent",
            "link_url",
            "bounce_reason",
            "event_at",
        ]
        read_only_fields = ["id", "event_at"]


class AlumniDonationRecurringSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    frequency_display = serializers.CharField(source="get_frequency_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlumniDonationRecurring
        fields = [
            "id",
            "alumni",
            "alumni_name",
            "fund_type",
            "amount",
            "frequency",
            "frequency_display",
            "status",
            "status_display",
            "start_date",
            "next_payment_date",
            "last_payment_date",
            "end_date",
            "payment_method",
            "total_paid",
            "total_payments",
            "failed_payments",
            "is_anonymous",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_paid", "total_payments", "failed_payments", "created_at", "updated_at"]


class AlumniPodcastEpisodeSerializer(serializers.ModelSerializer):
    episode_type_display = serializers.CharField(source="get_episode_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    host_name = serializers.CharField(source="host.user.full_name", read_only=True)
    guest_names = serializers.SerializerMethodField()
    duration_formatted = serializers.ReadOnlyField()

    class Meta:
        model = AlumniPodcastEpisode
        fields = [
            "id",
            "title",
            "description",
            "episode_type",
            "episode_type_display",
            "status",
            "status_display",
            "audio_url",
            "thumbnail_url",
            "duration_seconds",
            "duration_formatted",
            "host",
            "host_name",
            "guests",
            "guest_names",
            "play_count",
            "like_count",
            "download_count",
            "episode_number",
            "season_number",
            "tags",
            "published_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "play_count",
            "like_count",
            "download_count",
            "published_at",
            "created_at",
            "updated_at",
        ]

    def get_guest_names(self, obj):
        return [g.user.full_name for g in obj.guests.all()]


class AlumniPodcastSubscriptionSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)

    class Meta:
        model = AlumniPodcastSubscription
        fields = [
            "id",
            "alumni",
            "alumni_name",
            "is_active",
            "subscribed_at",
        ]
        read_only_fields = ["id", "subscribed_at"]


class AlumniAwardCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AlumniAwardCategory
        fields = [
            "id",
            "name",
            "description",
            "icon_url",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AlumniAwardSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlumniAward
        fields = [
            "id",
            "category",
            "category_name",
            "title",
            "description",
            "year",
            "status",
            "status_display",
            "nominations_start",
            "nominations_end",
            "judging_end",
            "announcement_date",
            "ceremony_date",
            "max_nominations_per_person",
            "requires_nomination_statement",
            "total_nominations",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "total_nominations", "created_at", "updated_at"]


class AlumniAwardNominationSerializer(serializers.ModelSerializer):
    nominee_name = serializers.CharField(source="nominee.user.full_name", read_only=True)
    nominated_by_name = serializers.CharField(source="nominated_by.user.full_name", read_only=True)
    award_title = serializers.CharField(source="award.title", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = AlumniAwardNomination
        fields = [
            "id",
            "award",
            "award_title",
            "nominee",
            "nominee_name",
            "nominated_by",
            "nominated_by_name",
            "statement",
            "status",
            "status_display",
            "evidence_urls",
            "score",
            "judge_notes",
            "nominated_at",
            "reviewed_at",
        ]
        read_only_fields = ["id", "nominated_at", "reviewed_at"]
