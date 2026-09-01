"""Django Admin registrations for admissions."""

from django.contrib import admin

from .models import (
    AdmissionAgreement,
    AdmissionCommunicationLog,
    AdmissionDecision,
    AdmissionDocumentChecklist,
    AdmissionDocumentVerification,
    AdmissionFunnelSnapshot,
    AdmissionMarketingSource,
    AdmissionPolicy,
    AdmissionPredictionModel,
    AdmissionReminder,
    AdmissionsEmailNotification,
    AdmissionsPipeline,
    AdmissionsReport,
    AdmissionsSMSNotification,
    AdmissionTrendAnalysis,
    AgreementSignature,
    Application,
    ApplicationDocument,
    ApplicationFee,
    ApplicationReview,
    ApplicationTemplate,
    ApplicationTimelineEvent,
    BulkApplicationImport,
    CampusVisit,
    EnrollmentConfirmation,
    EnrollmentIntake,
    EntranceAssessment,
    GradeLevelCapacity,
    InterviewSchedule,
    MeritList,
    MeritListEntry,
    OpenHouseEvent,
    OpenHouseRegistration,
    ReEnrollment,
    Scholarship,
    ScholarshipApplication,
    SiblingGroup,
    SiblingRecord,
    TransferStudent,
    WaitlistManagement,
)


@admin.register(EnrollmentIntake)
class EnrollmentIntakeAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(ApplicationTimelineEvent)
class ApplicationTimelineEventAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(EntranceAssessment)
class EntranceAssessmentAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ApplicationReview)
class ApplicationReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ApplicationFee)
class ApplicationFeeAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(InterviewSchedule)
class InterviewScheduleAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(MeritList)
class MeritListAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(MeritListEntry)
class MeritListEntryAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(WaitlistManagement)
class WaitlistManagementAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(EnrollmentConfirmation)
class EnrollmentConfirmationAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(AdmissionsReport)
class AdmissionsReportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(AdmissionsEmailNotification)
class AdmissionsEmailNotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(AdmissionsSMSNotification)
class AdmissionsSMSNotificationAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(ReEnrollment)
class ReEnrollmentAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(AdmissionsPipeline)
class AdmissionsPipelineAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(ApplicationTemplate)
class ApplicationTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(BulkApplicationImport)
class BulkApplicationImportAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(CampusVisit)
class CampusVisitAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(OpenHouseEvent)
class OpenHouseEventAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(OpenHouseRegistration)
class OpenHouseRegistrationAdmin(admin.ModelAdmin):
    list_display = ["id", "status"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ["id", "status"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(AdmissionPolicy)
class AdmissionPolicyAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(AdmissionAgreement)
class AdmissionAgreementAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(AgreementSignature)
class AgreementSignatureAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(AdmissionCommunicationLog)
class AdmissionCommunicationLogAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(AdmissionReminder)
class AdmissionReminderAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(GradeLevelCapacity)
class GradeLevelCapacityAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(AdmissionDecision)
class AdmissionDecisionAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(TransferStudent)
class TransferStudentAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(SiblingGroup)
class SiblingGroupAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(SiblingRecord)
class SiblingRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(AdmissionFunnelSnapshot)
class AdmissionFunnelSnapshotAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(AdmissionDocumentChecklist)
class AdmissionDocumentChecklistAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(AdmissionDocumentVerification)
class AdmissionDocumentVerificationAdmin(admin.ModelAdmin):
    list_display = ["id", "status"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(AdmissionPredictionModel)
class AdmissionPredictionModelAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(AdmissionMarketingSource)
class AdmissionMarketingSourceAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(AdmissionTrendAnalysis)
class AdmissionTrendAnalysisAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]
