"""Alumni serializers."""

from rest_framework import serializers

from .models import (
    AlumniChapter,
    AlumniChapterMember,
    AlumniDiscussion,
    AlumniDiscussionLike,
    AlumniDiscussionReply,
    AlumniDonation,
    AlumniDonationReceipt,
    AlumniEvent,
    AlumniEventRSVP,
    AlumniJobApplication,
    AlumniJobPosting,
    AlumniMentorship,
    AlumniProfile,
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
            "is_newsletter_subscribed",
            "is_visible_to_public",
            "engagement_score",
            "last_activity_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "engagement_score", "last_activity_at"]


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
