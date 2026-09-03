"""Django Admin registrations for auth."""

from django.contrib import admin

from .models import (
    APIKey,
    APIUsageLog,
    AuditLog,
    AuditReportSchedule,
    AuthWebhook,
    ComplianceRecord,
    ConsentRecord,
    DataDeletionRequest,
    DataExportRequest,
    DeviceManagement,
    DomainVerification,
    EmailVerificationToken,
    IPGeolocationCache,
    IPWhitelist,
    LoginAttempt,
    LoginHistory,
    MFAMethod,
    MFAVerification,
    OAuthProvider,
    OAuthToken,
    PasswordHistory,
    PasswordPolicy,
    PasswordResetToken,
    Permission,
    Role,
    RolePermission,
    School,
    SchoolFeatureFlag,
    SecurityNotificationPreference,
    SecurityPolicy,
    SessionPolicy,
    SessionToken,
    SSOConfiguration,
    TwoFactorBackupCode,
    UserActivity,
    UserRoleAssignment,
    UserSession,
    UserSessionHistory,
    UserTrustScore,
    WebhookDelivery,
)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(TwoFactorBackupCode)
class TwoFactorBackupCodeAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["id", "school"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(DeviceManagement)
class DeviceManagementAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "is_active", "created_at"]
    list_filter = ["is_active", "status"]
    search_fields = ["id"]


@admin.register(PasswordPolicy)
class PasswordPolicyAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(IPWhitelist)
class IPWhitelistAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(OAuthProvider)
class OAuthProviderAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(SessionPolicy)
class SessionPolicyAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(UserRoleAssignment)
class UserRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(SecurityPolicy)
class SecurityPolicyAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(SessionToken)
class SessionTokenAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(MFAMethod)
class MFAMethodAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(MFAVerification)
class MFAVerificationAdmin(admin.ModelAdmin):
    list_display = ["id", "status"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(OAuthToken)
class OAuthTokenAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(UserSessionHistory)
class UserSessionHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ComplianceRecord)
class ComplianceRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(PasswordHistory)
class PasswordHistoryAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(UserTrustScore)
class UserTrustScoreAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(SecurityNotificationPreference)
class SecurityNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(DataExportRequest)
class DataExportRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(DataDeletionRequest)
class DataDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(AuthWebhook)
class AuthWebhookAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    list_display = ["id", "status"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(SSOConfiguration)
class SSOConfigurationAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["name"]


@admin.register(DomainVerification)
class DomainVerificationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(IPGeolocationCache)
class IPGeolocationCacheAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(SchoolFeatureFlag)
class SchoolFeatureFlagAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(AuditReportSchedule)
class AuditReportScheduleAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]
