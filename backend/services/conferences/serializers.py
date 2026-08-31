from rest_framework import serializers

from .models import (
    ConferenceAvailability,
    ConferenceBooking,
    ConferenceFeedback,
    ConferenceHistory,
    ConferenceNotes,
    ConferenceReminder,
    ConferenceReport,
    ConferenceSlot,
    ConferenceTemplate,
    ConferenceType,
    FollowUpTracking,
    VirtualConference,
    WaitlistManagement,
)


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


# =============================================================================
# Conference Types Serializers
# =============================================================================


class ConferenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceType
        fields = [
            "id",
            "name",
            "category",
            "description",
            "default_duration_minutes",
            "max_participants",
            "allow_virtual",
            "allow_notes",
            "require_student",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Conference Bookings Serializers
# =============================================================================


class ConferenceBookingSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    slot_date = serializers.DateField(source="slot.date", read_only=True)
    slot_start = serializers.TimeField(source="slot.start_time", read_only=True)
    slot_end = serializers.TimeField(source="slot.end_time", read_only=True)

    class Meta:
        model = ConferenceBooking
        fields = [
            "id",
            "slot",
            "booking_type",
            "parent",
            "parent_name",
            "student",
            "student_name",
            "teacher",
            "teacher_name",
            "slot_date",
            "slot_start",
            "slot_end",
            "status",
            "is_virtual",
            "meeting_link",
            "meeting_id",
            "meeting_password",
            "reason",
            "notes",
            "confirmed_at",
            "cancelled_at",
            "cancellation_reason",
            "booked_at",
        ]
        read_only_fields = ["id", "booked_at", "confirmed_at", "cancelled_at"]


# =============================================================================
# Conference Reminders Serializers
# =============================================================================


class ConferenceReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceReminder
        fields = [
            "id",
            "booking",
            "reminder_type",
            "status",
            "subject",
            "message",
            "send_before_minutes",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["id", "sent_at", "created_at"]


# =============================================================================
# Conference Notes Serializers
# =============================================================================


class ConferenceNotesSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = ConferenceNotes
        fields = [
            "id",
            "booking",
            "note_type",
            "title",
            "content",
            "has_action_items",
            "action_items",
            "action_items_completed",
            "follow_up_needed",
            "follow_up_date",
            "follow_up_notes",
            "created_by",
            "created_by_name",
            "shared_with_parent",
            "shared_with_student",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Follow-up Tracking Serializers
# =============================================================================


class FollowUpTrackingSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default=None)

    class Meta:
        model = FollowUpTracking
        fields = [
            "id",
            "booking",
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
            "assigned_to_name",
            "due_date",
            "completed_date",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Conference Availability Serializers
# =============================================================================


class ConferenceAvailabilitySerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)

    class Meta:
        model = ConferenceAvailability
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "day_of_week",
            "start_time",
            "end_time",
            "availability_type",
            "location",
            "is_virtual_available",
            "effective_from",
            "effective_until",
            "is_recurring",
            "is_active",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Conference Reports Serializers
# =============================================================================


class ConferenceReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default=None)

    class Meta:
        model = ConferenceReport
        fields = [
            "id",
            "title",
            "report_type",
            "status",
            "period_start",
            "period_end",
            "summary",
            "findings",
            "recommendations",
            "total_conferences",
            "total_attended",
            "total_no_show",
            "attendance_rate",
            "by_teacher",
            "by_grade",
            "by_type",
            "generated_by",
            "generated_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Conference Feedback Serializers
# =============================================================================


class ConferenceFeedbackSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source="submitted_by.full_name", read_only=True)

    class Meta:
        model = ConferenceFeedback
        fields = [
            "id",
            "booking",
            "submitted_by",
            "submitted_by_name",
            "feedback_for",
            "overall_rating",
            "communication_rating",
            "preparedness_rating",
            "helpfulness_rating",
            "positive_feedback",
            "suggestions",
            "additional_comments",
            "submitted_at",
        ]
        read_only_fields = ["id", "submitted_at"]


# =============================================================================
# Conference History Serializers
# =============================================================================


class ConferenceHistorySerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    parent_name = serializers.CharField(source="parent.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    conference_type_name = serializers.CharField(source="conference_type.name", read_only=True, default=None)

    class Meta:
        model = ConferenceHistory
        fields = [
            "id",
            "booking",
            "teacher",
            "teacher_name",
            "parent",
            "parent_name",
            "student",
            "student_name",
            "conference_date",
            "conference_type",
            "conference_type_name",
            "was_virtual",
            "duration_minutes",
            "was_attended",
            "had_notes",
            "had_action_items",
            "had_follow_up",
            "summary",
            "archived_at",
        ]
        read_only_fields = ["id", "archived_at"]


# =============================================================================
# Virtual Conference Serializers
# =============================================================================


class VirtualConferenceSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="booking.parent.full_name", read_only=True)
    teacher_name = serializers.CharField(source="booking.teacher.full_name", read_only=True)

    class Meta:
        model = VirtualConference
        fields = [
            "id",
            "booking",
            "parent_name",
            "teacher_name",
            "platform",
            "status",
            "meeting_id",
            "meeting_url",
            "meeting_password",
            "host_url",
            "recording_url",
            "has_recording",
            "participants_joined",
            "scheduled_duration",
            "actual_duration",
            "had_technical_issues",
            "technical_notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Conference Templates Serializers
# =============================================================================


class ConferenceTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    conference_type_name = serializers.CharField(source="conference_type.name", read_only=True, default=None)

    class Meta:
        model = ConferenceTemplate
        fields = [
            "id",
            "name",
            "description",
            "conference_type",
            "conference_type_name",
            "default_duration_minutes",
            "agenda_items",
            "discussion_topics",
            "questions_to_ask",
            "require_notes",
            "require_feedback",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Waitlist Management Serializers
# =============================================================================


class WaitlistManagementSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.full_name", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    slot_date = serializers.DateField(source="slot.date", read_only=True)
    slot_teacher = serializers.CharField(source="slot.teacher.full_name", read_only=True)

    class Meta:
        model = WaitlistManagement
        fields = [
            "id",
            "slot",
            "slot_date",
            "slot_teacher",
            "parent",
            "parent_name",
            "student",
            "student_name",
            "position",
            "status",
            "offered_at",
            "offer_expires_at",
            "notes",
            "joined_at",
        ]
        read_only_fields = ["id", "joined_at"]
