"""Django Admin registrations for conferences."""

from django.contrib import admin

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


@admin.register(ConferenceSlot)
class ConferenceSlotAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ConferenceType)
class ConferenceTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(ConferenceBooking)
class ConferenceBookingAdmin(admin.ModelAdmin):
    list_display = ["id", "status"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ConferenceReminder)
class ConferenceReminderAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ConferenceNotes)
class ConferenceNotesAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(FollowUpTracking)
class FollowUpTrackingAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ConferenceAvailability)
class ConferenceAvailabilityAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(ConferenceReport)
class ConferenceReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(ConferenceFeedback)
class ConferenceFeedbackAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ConferenceHistory)
class ConferenceHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "school"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(VirtualConference)
class VirtualConferenceAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ConferenceTemplate)
class ConferenceTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(WaitlistManagement)
class WaitlistManagementAdmin(admin.ModelAdmin):
    list_display = ["id", "status"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ConferenceWaitingList)
class ConferenceWaitingListAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(RecurringConference)
class RecurringConferenceAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(RecurringConferenceParticipant)
class RecurringConferenceParticipantAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(ConferenceSettings)
class ConferenceSettingsAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ConferenceAnalytics)
class ConferenceAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ConferenceBookingRule)
class ConferenceBookingRuleAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(ConferenceSystemNotification)
class ConferenceSystemNotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(ConferenceExport)
class ConferenceExportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(ConferenceLocation)
class ConferenceLocationAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(ConferenceBlockedSlot)
class ConferenceBlockedSlotAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ConferenceScheduleOverride)
class ConferenceScheduleOverrideAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ConferenceReminderSchedule)
class ConferenceReminderScheduleAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(ConferenceAccessibilityRequirement)
class ConferenceAccessibilityRequirementAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ConferenceNoteTemplate)
class ConferenceNoteTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(ConferenceApproval)
class ConferenceApprovalAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ConferenceResource)
class ConferenceResourceAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    list_filter = []
    search_fields = ["name"]


@admin.register(ConferenceSurvey)
class ConferenceSurveyAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(ConferenceSurveyResponse)
class ConferenceSurveyResponseAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ConferenceCalendarSync)
class ConferenceCalendarSyncAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ConferenceHistoryDetail)
class ConferenceHistoryDetailAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ConferenceTimeSlot)
class ConferenceTimeSlotAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(ConferenceFeedbackTemplate)
class ConferenceFeedbackTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(ConferenceFollowUp)
class ConferenceFollowUpAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ConferenceRoomBooking)
class ConferenceRoomBookingAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ConferenceTemplateSection)
class ConferenceTemplateSectionAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ConferenceNoShow)
class ConferenceNoShowAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ConferenceConferenceType)
class ConferenceConferenceTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]
