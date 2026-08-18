"""Public admissions serializers — used by unauthenticated endpoints."""

from rest_framework import serializers

from .models import Application, EnrollmentIntake


class PublicIntakeSerializer(serializers.ModelSerializer):
    """Read-only intake info for the public apply page."""

    status_display = serializers.CharField(source="get_status_display", read_only=True)

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
            "description",
        ]
        read_only_fields = fields


class PublicApplicationSubmitSerializer(serializers.ModelSerializer):
    """Writable serializer for the public application form."""

    class Meta:
        model = Application
        fields = [
            "intake",
            "first_name",
            "last_name",
            "middle_name",
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
        ]

    def validate_intake(self, intake):
        """Only allow applications to open intakes within the application window."""
        from django.utils import timezone

        today = timezone.now().date()
        if intake.status != "open":
            raise serializers.ValidationError("This intake is not currently accepting applications.")
        if today < intake.application_start:
            raise serializers.ValidationError("Application period has not started yet.")
        if today > intake.application_end:
            raise serializers.ValidationError("Application period has ended.")
        if intake.max_applications and intake.applications.count() >= intake.max_applications:
            raise serializers.ValidationError("This intake has reached its maximum capacity.")
        return intake

    def create(self, validated_data):
        import uuid

        from django.utils import timezone as dj_timezone

        from .models import ApplicationTimelineEvent

        # Set school from intake BEFORE first save (school is NOT NULL)
        intake = validated_data["intake"]
        validated_data["school"] = intake.school
        validated_data["application_number"] = f"APP-{dj_timezone.localdate():%Y%m}-{str(uuid.uuid4())[:6].upper()}"
        validated_data["status"] = Application.Status.SUBMITTED
        validated_data["submitted_at"] = dj_timezone.now()
        app = super().create(validated_data)

        # Create timeline event
        ApplicationTimelineEvent.objects.create(
            application=app,
            stage=ApplicationTimelineEvent.Stage.SUBMITTED,
            note="Application submitted via public portal",
        )

        return app


class PublicApplicationStatusSerializer(serializers.ModelSerializer):
    """Read-only serializer for public status checking."""

    intake_name = serializers.CharField(source="intake.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    timeline = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "application_number",
            "status",
            "status_display",
            "first_name",
            "last_name",
            "intake_name",
            "applying_for_grade",
            "submitted_at",
            "offer_deadline",
            "timeline",
        ]
        read_only_fields = fields

    def get_timeline(self, obj):
        from .serializers import ApplicationTimelineSerializer

        return ApplicationTimelineSerializer(obj.timeline.all(), many=True).data
