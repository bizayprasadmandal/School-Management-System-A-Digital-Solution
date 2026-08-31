from django.contrib import admin

from .models import (
    AdmissionsEmailNotification,
    AdmissionsPipeline,
    AdmissionsReport,
    AdmissionsSMSNotification,
    Application,
    ApplicationDocument,
    ApplicationFee,
    ApplicationReview,
    ApplicationTemplate,
    BulkApplicationImport,
    EnrollmentConfirmation,
    EnrollmentIntake,
    InterviewSchedule,
    MeritList,
    MeritListEntry,
    ReEnrollment,
    WaitlistManagement,
)


class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 1
    fields = ["document_type", "file_name", "is_verified"]


class ApplicationReviewInline(admin.TabularInline):
    model = ApplicationReview
    extra = 1
    fields = ["reviewer", "score", "recommendation"]


@admin.register(EnrollmentIntake)
class EnrollmentIntakeAdmin(admin.ModelAdmin):
    list_display = ["name", "academic_year", "application_start", "application_end", "status"]
    list_filter = ["status", "school"]
    search_fields = ["name"]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["application_number", "first_name", "last_name", "applying_for_grade", "status", "submitted_at"]
    list_filter = ["status", "applying_for_grade"]
    search_fields = ["first_name", "last_name", "email", "application_number"]
    inlines = [ApplicationDocumentInline, ApplicationReviewInline]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ["application", "document_type", "file_name", "is_verified", "uploaded_at"]
    list_filter = ["document_type", "is_verified"]
    search_fields = ["file_name"]


@admin.register(ApplicationReview)
class ApplicationReviewAdmin(admin.ModelAdmin):
    list_display = ["application", "reviewer", "score", "recommendation", "created_at"]
    list_filter = ["recommendation"]
    search_fields = ["application__application_number"]


# =============================================================================
# Application Fees
# =============================================================================


@admin.register(ApplicationFee)
class ApplicationFeeAdmin(admin.ModelAdmin):
    list_display = ["application", "amount", "status", "payment_method", "payment_date"]
    list_filter = ["status", "payment_method"]
    search_fields = ["application__application_number", "transaction_id"]
    date_hierarchy = "created_at"


# =============================================================================
# Interview Schedule
# =============================================================================


@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = ["application", "interview_type", "status", "scheduled_date", "scheduled_time", "interviewer"]
    list_filter = ["interview_type", "status"]
    search_fields = ["application__application_number"]
    date_hierarchy = "scheduled_date"


# =============================================================================
# Merit List
# =============================================================================


class MeritListEntryInline(admin.TabularInline):
    model = MeritListEntry
    extra = 0


@admin.register(MeritList)
class MeritListAdmin(admin.ModelAdmin):
    list_display = ["name", "grade", "status", "total_applicants", "total_selected", "published_at"]
    list_filter = ["status", "grade"]
    search_fields = ["name", "description"]
    inlines = [MeritListEntryInline]


@admin.register(MeritListEntry)
class MeritListEntryAdmin(admin.ModelAdmin):
    list_display = ["merit_list", "application", "rank", "total_score", "status"]
    list_filter = ["status"]
    search_fields = ["application__application_number"]
    ordering = ["rank"]


# =============================================================================
# Waitlist Management
# =============================================================================


@admin.register(WaitlistManagement)
class WaitlistManagementAdmin(admin.ModelAdmin):
    list_display = ["application", "position", "status", "offer_extended_at", "offer_expires_at"]
    list_filter = ["status"]
    search_fields = ["application__application_number"]
    ordering = ["position"]


# =============================================================================
# Enrollment Confirmation
# =============================================================================


@admin.register(EnrollmentConfirmation)
class EnrollmentConfirmationAdmin(admin.ModelAdmin):
    list_display = ["application", "status", "deposit_amount", "payment_status", "confirmation_deadline"]
    list_filter = ["status", "payment_status"]
    search_fields = ["application__application_number"]
    date_hierarchy = "created_at"


# =============================================================================
# Admissions Reports
# =============================================================================


@admin.register(AdmissionsReport)
class AdmissionsReportAdmin(admin.ModelAdmin):
    list_display = ["title", "report_type", "status", "period_start", "period_end", "total_applications"]
    list_filter = ["report_type", "status"]
    search_fields = ["title", "summary"]
    date_hierarchy = "created_at"


# =============================================================================
# Email Notifications
# =============================================================================


@admin.register(AdmissionsEmailNotification)
class AdmissionsEmailNotificationAdmin(admin.ModelAdmin):
    list_display = ["application", "notification_type", "status", "recipient_email", "sent_at"]
    list_filter = ["notification_type", "status"]
    search_fields = ["application__application_number", "recipient_email"]
    date_hierarchy = "created_at"


# =============================================================================
# SMS Notifications
# =============================================================================


@admin.register(AdmissionsSMSNotification)
class AdmissionsSMSNotificationAdmin(admin.ModelAdmin):
    list_display = ["application", "notification_type", "status", "phone_number", "sent_at"]
    list_filter = ["notification_type", "status"]
    search_fields = ["application__application_number", "phone_number"]
    date_hierarchy = "created_at"


# =============================================================================
# Re-enrollment Management
# =============================================================================


@admin.register(ReEnrollment)
class ReEnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "current_grade", "next_grade", "status", "deadline", "fee_paid"]
    list_filter = ["status", "fee_paid"]
    search_fields = ["student__user__first_name", "student__user__last_name"]
    date_hierarchy = "invited_at"


# =============================================================================
# Admissions Pipeline
# =============================================================================


@admin.register(AdmissionsPipeline)
class AdmissionsPipelineAdmin(admin.ModelAdmin):
    list_display = ["application", "current_stage", "is_priority", "is_hot_lead", "assigned_to", "lead_source"]
    list_filter = ["current_stage", "is_priority", "is_hot_lead"]
    search_fields = ["application__application_number", "lead_source"]
    date_hierarchy = "created_at"


# =============================================================================
# Application Templates
# =============================================================================


@admin.register(ApplicationTemplate)
class ApplicationTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "application_fee", "currency", "allow_late_applications", "is_active"]
    list_filter = ["is_active", "allow_late_applications"]
    search_fields = ["name", "description"]


# =============================================================================
# Bulk Application Import
# =============================================================================


@admin.register(BulkApplicationImport)
class BulkApplicationImportAdmin(admin.ModelAdmin):
    list_display = ["batch_name", "status", "total_rows", "imported_count", "failed_count", "initiated_at"]
    list_filter = ["status"]
    search_fields = ["batch_name", "description"]
    date_hierarchy = "initiated_at"
