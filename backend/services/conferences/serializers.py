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
            "on_delete",
            "teacher",
            "on_delete",
            "student",
            "on_delete",
            "date",
            "start_time",
            "end_time",
            "is_booked",
            "booked_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "booking_type",
            "on_delete",
            "parent",
            "on_delete",
            "student",
            "on_delete",
            "teacher",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "title",
            "description",
            "priority",
            "status",
            "assigned_to",
            "on_delete",
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
            "on_delete",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "submitted_by",
            "on_delete",
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
            "on_delete",
            "booking",
            "on_delete",
            "teacher",
            "on_delete",
            "parent",
            "on_delete",
            "student",
            "on_delete",
            "conference_date",
            "conference_type",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "name",
            "description",
            "conference_type",
            "on_delete",
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
            "on_delete",
            "parent",
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "parent",
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "title",
            "description",
            "frequency",
            "status",
            "day_of_week",
            "time_of_day",
            "duration_minutes",
            "teacher",
            "on_delete",
            "start_date",
            "end_date",
            "last_occurrence",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RecurringConferenceParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringConferenceParticipant
        fields = [
            "id",
            "id",
            "recurring_conference",
            "on_delete",
            "user",
            "on_delete",
            "role",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSettings
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "recipient",
            "on_delete",
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
            "on_delete",
            "export_type",
            "format",
            "status",
            "date_from",
            "date_to",
            "file",
            "record_count",
            "requested_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "teacher",
            "on_delete",
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
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "date",
            "override_type",
            "start_time",
            "end_time",
            "reason",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceReminderScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceReminderSchedule
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
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
        fields = [
            "id",
            "id",
            "booking",
            "on_delete",
            "requirement_type",
            "details",
            "language",
            "is_confirmed",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceNoteTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceNoteTemplate
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "sections",
            "is_active",
            "is_default",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceApproval
        fields = [
            "id",
            "id",
            "booking",
            "on_delete",
            "approver",
            "on_delete",
            "status",
            "comments",
            "decided_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceResource
        fields = [
            "id",
            "id",
            "booking",
            "on_delete",
            "resource_type",
            "name",
            "quantity",
            "is_reserved",
            "cost",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceSurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSurvey
        fields = ["id", "school", "id", "on_delete", "title", "questions", "status", "total_responses", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConferenceSurveyResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceSurveyResponse
        fields = [
            "id",
            "id",
            "survey",
            "on_delete",
            "respondent",
            "on_delete",
            "answers",
            "overall_rating",
            "comments",
            "submitted_at",
        ]
        read_only_fields = ["id"]


class ConferenceCalendarSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceCalendarSync
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
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
            "on_delete",
            "booking",
            "on_delete",
            "student",
            "on_delete",
            "conference_date",
            "conference_type",
            "topics_discussed",
            "outcome",
            "follow_up_needed",
            "recommendations",
            "recorded_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceTimeSlot
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "teacher",
            "on_delete",
            "date",
            "start_time",
            "end_time",
            "status",
            "booking",
            "on_delete",
            "location",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceFeedbackTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceFeedbackTemplate
        fields = ["id", "school", "id", "on_delete", "name", "questions", "target_audience", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConferenceFollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceFollowUp
        fields = [
            "id",
            "id",
            "booking",
            "on_delete",
            "assigned_to",
            "on_delete",
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
            "on_delete",
            "booking",
            "on_delete",
            "date",
            "start_time",
            "end_time",
            "status",
            "booked_by",
            "on_delete",
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
            "on_delete",
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
        fields = [
            "id",
            "id",
            "booking",
            "on_delete",
            "user",
            "on_delete",
            "rescheduled",
            "rescheduled_to",
            "on_delete",
            "reason",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ConferenceConferenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConferenceConferenceType
        fields = [
            "id",
            "id",
            "conference_type",
            "on_delete",
            "requires_parent_consent",
            "requires_student_consent",
            "auto_generate_notes",
            "default_location",
            "on_delete",
            "max_duration_minutes",
            "allow_virtual",
            "allow_walk_in",
            "fee",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
