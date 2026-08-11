"""Admissions serializers."""

from rest_framework import serializers

from .models import Application, ApplicationDocument, ApplicationReview, ApplicationTimelineEvent, EnrollmentIntake


class ApplicationTimelineSerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source="get_stage_display", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default="")

    class Meta:
        model = ApplicationTimelineEvent
        fields = [
            "id",
            "stage",
            "stage_display",
            "note",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = fields


class EnrollmentIntakeSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = EnrollmentIntake
        fields = [
            "id",
            "name",
            "academic_year",
            "application_start",
            "application_end",
            "enrollment_date",
            "status",
            "status_display",
            "max_applications",
            "description",
            "application_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_application_count(self, obj):
        return obj.applications.count()


class ApplicationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = [
            "id",
            "application",
            "document_type",
            "file_url",
            "file_name",
            "uploaded_at",
            "is_verified",
            "notes",
        ]
        read_only_fields = ["id", "uploaded_at"]


class ApplicationReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source="reviewer.full_name", read_only=True)

    class Meta:
        model = ApplicationReview
        fields = [
            "id",
            "application",
            "reviewer",
            "reviewer_name",
            "score",
            "strengths",
            "weaknesses",
            "recommendation",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "reviewer", "created_at"]


class ApplicationSerializer(serializers.ModelSerializer):
    intake_name = serializers.CharField(source="intake.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    full_name = serializers.SerializerMethodField()
    documents = ApplicationDocumentSerializer(many=True, read_only=True)
    reviews = ApplicationReviewSerializer(many=True, read_only=True)
    timeline = ApplicationTimelineSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "intake",
            "intake_name",
            "application_number",
            "status",
            "status_display",
            "first_name",
            "last_name",
            "middle_name",
            "full_name",
            "date_of_birth",
            "gender",
            "nationality",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "postal_code",
            "previous_school",
            "previous_grade",
            "applying_for_grade",
            "gpa",
            "guardian_name",
            "guardian_phone",
            "guardian_email",
            "guardian_relation",
            "source",
            "submitted_at",
            "reviewed_by",
            "review_notes",
            "tour_date",
            "toured_at",
            "offer_sent_at",
            "offer_accepted_at",
            "linked_student",
            "documents",
            "reviews",
            "timeline",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "application_number", "created_at", "updated_at"]

    def get_full_name(self, obj):
        parts = [obj.first_name, obj.middle_name, obj.last_name]
        return " ".join(p for p in parts if p)


class ApplicationListSerializer(serializers.ModelSerializer):
    """Lightweight list serializer without nested docs/reviews."""

    intake_name = serializers.CharField(source="intake.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "intake",
            "intake_name",
            "application_number",
            "status",
            "status_display",
            "full_name",
            "email",
            "phone",
            "applying_for_grade",
            "previous_school",
            "submitted_at",
            "created_at",
        ]
        read_only_fields = ["id", "application_number", "created_at"]

    def get_full_name(self, obj):
        parts = [obj.first_name, obj.middle_name, obj.last_name]
        return " ".join(p for p in parts if p)
