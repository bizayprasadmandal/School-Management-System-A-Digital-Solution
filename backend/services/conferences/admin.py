from django.contrib import admin

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


@admin.register(ConferenceSlot)
class ConferenceSlotAdmin(admin.ModelAdmin):
    list_display = ["teacher", "student", "date", "start_time", "end_time", "is_booked"]
    list_filter = ["is_booked", "date"]
    search_fields = ["teacher__full_name", "student__user__full_name"]


# =============================================================================
# Conference Types
# =============================================================================


@admin.register(ConferenceType)
class ConferenceTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "default_duration_minutes", "allow_virtual", "is_active"]
    list_filter = ["category", "allow_virtual", "is_active"]
    search_fields = ["name", "description"]


# =============================================================================
# Conference Bookings
# =============================================================================


@admin.register(ConferenceBooking)
class ConferenceBookingAdmin(admin.ModelAdmin):
    list_display = ["parent", "student", "teacher", "status", "is_virtual", "booked_at"]
    list_filter = ["status", "is_virtual"]
    search_fields = ["parent__first_name", "parent__last_name", "student__user__first_name"]
    date_hierarchy = "booked_at"


# =============================================================================
# Conference Reminders
# =============================================================================


@admin.register(ConferenceReminder)
class ConferenceReminderAdmin(admin.ModelAdmin):
    list_display = ["booking", "reminder_type", "status", "send_before_minutes", "sent_at"]
    list_filter = ["reminder_type", "status"]
    date_hierarchy = "created_at"


# =============================================================================
# Conference Notes
# =============================================================================


@admin.register(ConferenceNotes)
class ConferenceNotesAdmin(admin.ModelAdmin):
    list_display = ["booking", "note_type", "title", "has_action_items", "follow_up_needed", "created_at"]
    list_filter = ["note_type", "has_action_items", "follow_up_needed"]
    search_fields = ["title", "content"]
    date_hierarchy = "created_at"


# =============================================================================
# Follow-up Tracking
# =============================================================================


@admin.register(FollowUpTracking)
class FollowUpTrackingAdmin(admin.ModelAdmin):
    list_display = ["title", "booking", "priority", "status", "due_date", "assigned_to"]
    list_filter = ["priority", "status"]
    search_fields = ["title", "description"]
    date_hierarchy = "due_date"


# =============================================================================
# Conference Availability
# =============================================================================


@admin.register(ConferenceAvailability)
class ConferenceAvailabilityAdmin(admin.ModelAdmin):
    list_display = ["teacher", "day_of_week", "start_time", "end_time", "availability_type", "is_active"]
    list_filter = ["day_of_week", "availability_type", "is_active"]
    search_fields = ["teacher__first_name", "location"]


# =============================================================================
# Conference Reports
# =============================================================================


@admin.register(ConferenceReport)
class ConferenceReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "status", "period_start", "period_end", "total_conferences"]
    list_filter = ["report_type", "status"]
    search_fields = ["title", "summary"]
    date_hierarchy = "created_at"


# =============================================================================
# Conference Feedback
# =============================================================================


@admin.register(ConferenceFeedback)
class ConferenceFeedbackAdmin(admin.ModelAdmin):
    list_display = ["submitted_by", "booking", "feedback_for", "overall_rating", "submitted_at"]
    list_filter = ["feedback_for", "overall_rating"]
    search_fields = ["submitted_by__first_name", "positive_feedback"]
    date_hierarchy = "submitted_at"


# =============================================================================
# Conference History
# =============================================================================


@admin.register(ConferenceHistory)
class ConferenceHistoryAdmin(admin.ModelAdmin):
    list_display = ["teacher", "parent", "student", "conference_date", "was_virtual", "was_attended"]
    list_filter = ["was_virtual", "was_attended"]
    search_fields = ["teacher__first_name", "parent__first_name", "student__user__first_name"]
    date_hierarchy = "conference_date"


# =============================================================================
# Virtual Conference
# =============================================================================


@admin.register(VirtualConference)
class VirtualConferenceAdmin(admin.ModelAdmin):
    list_display = ["booking", "platform", "status", "participants_joined", "has_recording"]
    list_filter = ["platform", "status", "has_recording"]
    search_fields = ["meeting_id", "meeting_url"]


# =============================================================================
# Conference Templates
# =============================================================================


@admin.register(ConferenceTemplate)
class ConferenceTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "conference_type", "default_duration_minutes", "require_notes", "is_active"]
    list_filter = ["conference_type", "require_notes", "is_active"]
    search_fields = ["name", "description"]


# =============================================================================
# Waitlist Management
# =============================================================================


@admin.register(WaitlistManagement)
class WaitlistManagementAdmin(admin.ModelAdmin):
    list_display = ["parent", "student", "slot", "position", "status", "joined_at"]
    list_filter = ["status"]
    search_fields = ["parent__first_name", "student__user__first_name"]
    date_hierarchy = "joined_at"
