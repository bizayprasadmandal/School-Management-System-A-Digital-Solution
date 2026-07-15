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
    create_zoom_meeting = serializers.BooleanField(default=False, write_only=True, help_text="Auto-create a Zoom meeting for this slot")

    class Meta:
        model = ConferenceSlot
        fields = ["teacher", "student", "date", "start_time", "end_time", "notes", "create_zoom_meeting"]


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
    password = serializers.CharField(required=False, min_length=4, max_length=10, help_text="Optional 4-10 char meeting passcode")


class ZoomMeetingSerializer(serializers.Serializer):
    """Serialized Zoom meeting response."""
    id = serializers.CharField()
    topic = serializers.CharField()
    join_url = serializers.URLField()
    start_url = serializers.URLField()
    password = serializers.CharField(required=False, allow_blank=True)
    duration = serializers.IntegerField()
    start_time = serializers.DateTimeField()
