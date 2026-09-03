"""Serializers for conferences."""

from rest_framework import serializers

from .models import (
    ConferenceAccessibilityRequirement,
    ConferenceAnalytics,
    ConferenceApproval,
    ConferenceAvailability,
    ConferenceBlockedSlot,
    ConferenceBooking,
    ConferenceBookingRule,
    ConferenceCalendarSync,
    ConferenceConferenceType,
    ConferenceExport,
    ConferenceFeedback,
    ConferenceFeedbackTemplate,
    ConferenceFollowUp,
    ConferenceHistory,
    ConferenceHistoryDetail,
    ConferenceLocation,
    ConferenceNoShow,
    ConferenceNotes,
    ConferenceNoteTemplate,
    ConferenceReminder,
    ConferenceReminderSchedule,
    ConferenceReport,
    ConferenceResource,
    ConferenceRoomBooking,
    ConferenceScheduleOverride,
    ConferenceSettings,
    ConferenceSlot,
    ConferenceSurvey,
    ConferenceSurveyResponse,
    ConferenceSystemNotification,
    ConferenceTemplate,
    ConferenceTemplateSection,
    ConferenceTimeSlot,
    ConferenceType,
    ConferenceWaitingList,
    FollowUpTracking,
    RecurringConference,
    RecurringConferenceParticipant,
    VirtualConference,
    WaitlistManagement,
)


class ConferenceSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSlot
        fields = [
            "id",
            "school",
            "teacher",
            "student",
            "date",
            "start_time",
            "end_time",
            "is_booked",
            "booked_by",
            "notes",
            "zoom_meeting_id",
            "zoom_join_url",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConferenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceType
        fields = [
            "id",
            "school",
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
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConferenceBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceBooking
        fields = [
            "id",
            "id",
            "slot",
            "booking_type",
            "parent",
            "student",
            "teacher",
            "status",
            "is_virtual",
            "meeting_link",
            "meeting_id",
        ]
        read_only_fields = ["id", "updated_at"]


class ConferenceReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceReminder
        fields = [
            "id",
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
        read_only_fields = ["id", "created_at"]


class ConferenceNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceNotes
        fields = [
            "id",
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
            "shared_with_parent",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FollowUpTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpTracking
        fields = [
            "id",
            "id",
            "booking",
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
            "due_date",
            "completed_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConferenceAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceAvailability
        fields = [
            "id",
            "school",
            "id",
            "teacher",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConferenceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceReport
        fields = [
            "id",
            "school",
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
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceFeedback
        fields = [
            "id",
            "id",
            "booking",
            "submitted_by",
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
        read_only_fields = ["id"]


class ConferenceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceHistory
        fields = [
            "id",
            "school",
            "id",
            "booking",
            "teacher",
            "parent",
            "student",
            "conference_date",
            "conference_type",
            "was_virtual",
        ]
        read_only_fields = ["id"]


class VirtualConferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualConference
        fields = [
            "id",
            "id",
            "booking",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConferenceTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceTemplate
        fields = [
            "id",
            "school",
            "id",
            "name",
            "description",
            "conference_type",
            "default_duration_minutes",
            "agenda_items",
            "discussion_topics",
            "questions_to_ask",
            "require_notes",
            "require_feedback",
            "is_active",
            "created_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WaitlistManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistManagement
        fields = [
            "id",
            "id",
            "slot",
            "parent",
            "student",
            "position",
            "status",
            "offered_at",
            "offer_expires_at",
            "notes",
            "joined_at",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class ConferenceWaitingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceWaitingList
        fields = [
            "id",
            "school",
            "id",
            "parent",
            "student",
            "status",
            "position",
            "preferred_dates",
            "preferred_times",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RecurringConferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringConference
        fields = [
            "id",
            "school",
            "id",
            "title",
            "description",
            "frequency",
            "status",
            "day_of_week",
            "time_of_day",
            "duration_minutes",
            "teacher",
            "start_date",
            "end_date",
            "last_occurrence",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RecurringConferenceParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringConferenceParticipant
        fields = ["id", "id", "recurring_conference", "user", "role", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConferenceSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSettings
        fields = [
            "id",
            "school",
            "id",
            "booking_window_days",
            "cancellation_window_hours",
            "buffer_between_minutes",
            "max_conferences_per_day",
            "send_confirmation_email",
            "send_reminder_email",
            "reminder_hours_before",
            "collect_feedback",
            "feedback_deadline_days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConferenceAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceAnalytics
        fields = [
            "id",
            "school",
            "id",
            "date",
            "total_scheduled",
            "total_completed",
            "total_no_show",
            "total_cancelled",
            "total_parents",
            "total_teachers",
            "parent_participation_rate",
            "avg_duration_minutes",
            "avg_satisfaction_rating",
            "by_type_breakdown",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceBookingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceBookingRule
        fields = [
            "id",
            "school",
            "id",
            "name",
            "rule_type",
            "description",
            "parameters",
            "is_active",
            "priority",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceSystemNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSystemNotification
        fields = [
            "id",
            "school",
            "id",
            "recipient",
            "notification_type",
            "status",
            "subject",
            "message",
            "channel",
            "sent_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceExport
        fields = [
            "id",
            "school",
            "id",
            "export_type",
            "format",
            "status",
            "date_from",
            "date_to",
            "file",
            "record_count",
            "requested_by",
            "requested_at",
            "completed_at",
        ]
        read_only_fields = ["id"]


class ConferenceLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceLocation
        fields = [
            "id",
            "school",
            "id",
            "name",
            "location_type",
            "building",
            "room",
            "capacity",
            "virtual_link",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceBlockedSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceBlockedSlot
        fields = [
            "id",
            "school",
            "id",
            "teacher",
            "title",
            "date",
            "start_time",
            "end_time",
            "reason",
            "is_recurring",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceScheduleOverrideSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceScheduleOverride
        fields = ["id", "school", "id", "date", "override_type", "start_time", "end_time", "reason", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConferenceReminderScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceReminderSchedule
        fields = [
            "id",
            "school",
            "id",
            "name",
            "hours_before",
            "channel",
            "message_template",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceAccessibilityRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceAccessibilityRequirement
        fields = ["id", "id", "booking", "requirement_type", "details", "language", "is_confirmed", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConferenceNoteTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceNoteTemplate
        fields = ["id", "school", "id", "name", "description", "sections", "is_active", "is_default", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConferenceApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceApproval
        fields = ["id", "id", "booking", "approver", "status", "comments", "decided_at", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConferenceResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceResource
        fields = ["id", "id", "booking", "resource_type", "name", "quantity", "is_reserved", "cost", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConferenceSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSurvey
        fields = ["id", "school", "id", "title", "questions", "status", "total_responses", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConferenceSurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSurveyResponse
        fields = ["id", "id", "survey", "respondent", "answers", "overall_rating", "comments", "submitted_at"]
        read_only_fields = ["id"]


class ConferenceCalendarSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceCalendarSync
        fields = [
            "id",
            "id",
            "user",
            "calendar_type",
            "status",
            "calendar_id",
            "ical_url",
            "auto_sync",
            "last_synced_at",
            "last_error",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConferenceHistoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceHistoryDetail
        fields = [
            "id",
            "school",
            "id",
            "booking",
            "student",
            "conference_date",
            "conference_type",
            "topics_discussed",
            "outcome",
            "follow_up_needed",
            "recommendations",
            "recorded_by",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceTimeSlot
        fields = [
            "id",
            "school",
            "id",
            "teacher",
            "date",
            "start_time",
            "end_time",
            "status",
            "booking",
            "location",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceFeedbackTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceFeedbackTemplate
        fields = ["id", "school", "id", "name", "questions", "target_audience", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConferenceFollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceFollowUp
        fields = [
            "id",
            "id",
            "booking",
            "assigned_to",
            "action_required",
            "due_date",
            "status",
            "notes",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ConferenceRoomBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceRoomBooking
        fields = [
            "id",
            "id",
            "location",
            "booking",
            "date",
            "start_time",
            "end_time",
            "status",
            "booked_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceTemplateSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceTemplateSection
        fields = [
            "id",
            "id",
            "template",
            "title",
            "description",
            "sort_order",
            "is_required",
            "suggested_questions",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceNoShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceNoShow
        fields = ["id", "id", "booking", "user", "rescheduled", "rescheduled_to", "reason", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConferenceConferenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceConferenceType
        fields = [
            "id",
            "id",
            "conference_type",
            "requires_parent_consent",
            "requires_student_consent",
            "auto_generate_notes",
            "default_location",
            "max_duration_minutes",
            "allow_virtual",
            "allow_walk_in",
            "fee",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ── Serializers restored from original module (expansion regression fix) ──


class ConferenceSlotCreateUpdateSerializer(serializers.ModelSerializer):
    create_zoom_meeting = serializers.BooleanField(
        default=False, write_only=True, help_text="Auto-create a Zoom meeting for this slot"
    )

    class Meta:
        model = ConferenceSlot
        fields = ["teacher", "student", "date", "start_time", "end_time", "notes", "create_zoom_meeting"]
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
