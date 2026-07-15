"""Alumni serializers."""

from rest_framework import serializers
from .models import AlumniProfile, AlumniEvent, AlumniDonation, AlumniChapter


class AlumniProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    employment_status_display = serializers.CharField(source="get_employment_status_display", read_only=True)

    class Meta:
        model = AlumniProfile
        fields = ["id", "user", "user_name", "user_email", "graduation_year", "student_id", "occupation", "employer", "employment_status", "employment_status_display", "phone", "address", "city", "country", "linkedin_url", "facebook_url", "twitter_handle", "bio", "is_newsletter_subscribed", "is_visible_to_public", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AlumniEventSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    organizer_name = serializers.CharField(source="organizer.full_name", read_only=True, default=None)

    class Meta:
        model = AlumniEvent
        fields = ["id", "title", "description", "event_date", "end_date", "location", "venue", "max_attendees", "registration_deadline", "fee_amount", "status", "status_display", "organizer", "organizer_name", "cover_image_url", "created_at"]
        read_only_fields = ["id", "created_at"]


class AlumniDonationSerializer(serializers.ModelSerializer):
    alumni_name = serializers.CharField(source="alumni.user.full_name", read_only=True)
    fund_type_display = serializers.CharField(source="get_fund_type_display", read_only=True)

    class Meta:
        model = AlumniDonation
        fields = ["id", "alumni", "alumni_name", "amount", "fund_type", "fund_type_display", "payment_method", "transaction_id", "donation_date", "is_anonymous", "is_recurring", "message", "created_at"]
        read_only_fields = ["id", "donation_date", "created_at"]


class AlumniChapterSerializer(serializers.ModelSerializer):
    president_name = serializers.CharField(source="president.full_name", read_only=True, default=None)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = AlumniChapter
        fields = ["id", "name", "city", "country", "description", "president", "president_name", "is_active", "member_count", "created_at"]
        read_only_fields = ["id", "created_at"]
    def get_member_count(self, obj):
        return AlumniProfile.objects.filter(city__iexact=obj.city).count() if obj.city else 0
