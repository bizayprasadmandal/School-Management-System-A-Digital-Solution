from rest_framework import serializers

from .models import ConferenceSlot


class ConferenceSlotSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True, allow_null=True)

    class Meta:
        model = ConferenceSlot
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ConferenceSlotCreateUpdateSerializer(serializers.ModelSerializer):
    create_zoom_meeting = serializers.BooleanField(
        default=False, write_only=True, help_text="Auto-create a Zoom meeting for this slot"
    )

    class Meta:
        model = ConferenceSlot
        fields = [
            "teacher",
            "student",
            "date",
            "start_time",
            "end_time",
            "notes",
            "create_zoom_meeting",
        ]
        extra_kwargs = {
            "teacher": {
                "required": False,
                "help_text": "Defaults to the requesting user for teachers.",
            }
        }
        # The model's unique_together(teacher, date, start_time) auto-generates a
        # UniqueTogetherValidator that forces every tuple field to be required
        # (even with required=False). We disable it and re-implement the check
        # in validate() so teacher can default to the requesting user.
        validators = []

    def validate(self, attrs):
        teacher = attrs.get("teacher")
        if teacher is None:
            request = self.context.get("request")
            teacher = getattr(request, "user", None)
            if teacher is None or not teacher.is_authenticated:
                raise serializers.ValidationError({"teacher": "Teacher is required."})
            attrs["teacher"] = teacher

        qs = ConferenceSlot.objects.filter(
            teacher=teacher,
            date=attrs["date"],
            start_time=attrs["start_time"],
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A slot for this teacher, date, and start time already exists.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("create_zoom_meeting", None)
        return super().create(validated_data)


class ZoomSettingsSerializer(serializers.Serializer):
    """Validate Zoom OAuth credentials."""

    account_id = serializers.CharField(required=True, min_length=2)
    client_id = serializers.CharField(required=True, min_length=2)
    client_secret = serializers.CharField(required=True, min_length=2)


class ZoomConnectionStatusSerializer(serializers.Serializer):
    """Zoom connection status response."""

    status = serializers.CharField()
    detail = serializers.CharField()
    user = serializers.DictField(required=False, allow_null=True)


class CreateZoomMeetingSerializer(serializers.Serializer):
    """Create a Zoom meeting for a conference slot."""

    slot_id = serializers.UUIDField(required=True)
    topic = serializers.CharField(required=False, help_text="Meeting topic (defaults to conference slot label)")
    duration_minutes = serializers.IntegerField(default=30, min_value=5, max_value=240)
    password = serializers.CharField(
        required=False, min_length=4, max_length=10, help_text="Optional 4-10 char meeting passcode"
    )


class ZoomMeetingSerializer(serializers.Serializer):
    """Serialized Zoom meeting response."""

    id = serializers.CharField()
    topic = serializers.CharField()
    join_url = serializers.URLField()
    start_url = serializers.URLField()
    password = serializers.CharField(required=False, allow_blank=True)
    duration = serializers.IntegerField()
    start_time = serializers.DateTimeField()
