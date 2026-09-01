"""URL Configuration for auth."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    APIKeyViewSet,
    APIUsageLogViewSet,
    AuditLogViewSet,
    AuditReportScheduleViewSet,
    AuthWebhookViewSet,
    ComplianceRecordViewSet,
    ConsentRecordViewSet,
    DataDeletionRequestViewSet,
    DataExportRequestViewSet,
    DeviceManagementViewSet,
    DomainVerificationViewSet,
    EmailVerificationTokenViewSet,
    IPGeolocationCacheViewSet,
    IPWhitelistViewSet,
    LoginAttemptViewSet,
    LoginHistoryViewSet,
    MFAMethodViewSet,
    MFAVerificationViewSet,
    OAuthProviderViewSet,
    OAuthTokenViewSet,
    PasswordHistoryViewSet,
    PasswordPolicyViewSet,
    PasswordResetTokenViewSet,
    PermissionViewSet,
    RolePermissionViewSet,
    RoleViewSet,
    SchoolFeatureFlagViewSet,
    SchoolViewSet,
    SecurityNotificationPreferenceViewSet,
    SecurityPolicyViewSet,
    SessionPolicyViewSet,
    SessionTokenViewSet,
    SSOConfigurationViewSet,
    TwoFactorBackupCodeViewSet,
    UserActivityViewSet,
    UserRoleViewSet,
    UserSessionHistoryViewSet,
    UserSessionViewSet,
    UserTrustScoreViewSet,
    WebhookDeliveryViewSet,
)

app_name = "auth_v1"

router = DefaultRouter()
router.register(r"school", SchoolViewSet, basename="school")
router.register(r"user-session", UserSessionViewSet, basename="user-session")
router.register(r"password-reset-token", PasswordResetTokenViewSet, basename="password-reset-token")
router.register(r"email-verification-token", EmailVerificationTokenViewSet, basename="email-verification-token")
router.register(r"two-factor-backup-code", TwoFactorBackupCodeViewSet, basename="two-factor-backup-code")
router.register(r"audit-log", AuditLogViewSet, basename="audit-log")
router.register(r"login-history", LoginHistoryViewSet, basename="login-history")
router.register(r"a-p-i-key", APIKeyViewSet, basename="a-p-i-key")
router.register(r"device-management", DeviceManagementViewSet, basename="device-management")
router.register(r"password-policy", PasswordPolicyViewSet, basename="password-policy")
router.register(r"i-p-whitelist", IPWhitelistViewSet, basename="i-p-whitelist")
router.register(r"o-auth-provider", OAuthProviderViewSet, basename="o-auth-provider")
router.register(r"user-activity", UserActivityViewSet, basename="user-activity")
router.register(r"session-policy", SessionPolicyViewSet, basename="session-policy")
router.register(r"role", RoleViewSet, basename="role")
router.register(r"permission", PermissionViewSet, basename="permission")
router.register(r"role-permission", RolePermissionViewSet, basename="role-permission")
router.register(r"user-role", UserRoleViewSet, basename="user-role")
router.register(r"security-policy", SecurityPolicyViewSet, basename="security-policy")
router.register(r"login-attempt", LoginAttemptViewSet, basename="login-attempt")
router.register(r"session-token", SessionTokenViewSet, basename="session-token")
router.register(r"m-f-a-method", MFAMethodViewSet, basename="m-f-a-method")
router.register(r"m-f-a-verification", MFAVerificationViewSet, basename="m-f-a-verification")
router.register(r"o-auth-token", OAuthTokenViewSet, basename="o-auth-token")
router.register(r"user-session-history", UserSessionHistoryViewSet, basename="user-session-history")
router.register(r"a-p-i-usage-log", APIUsageLogViewSet, basename="a-p-i-usage-log")
router.register(r"compliance-record", ComplianceRecordViewSet, basename="compliance-record")
router.register(r"password-history", PasswordHistoryViewSet, basename="password-history")
router.register(r"user-trust-score", UserTrustScoreViewSet, basename="user-trust-score")
router.register(
    r"security-notification-preference",
    SecurityNotificationPreferenceViewSet,
    basename="security-notification-preference",
)
router.register(r"data-export-request", DataExportRequestViewSet, basename="data-export-request")
router.register(r"data-deletion-request", DataDeletionRequestViewSet, basename="data-deletion-request")
router.register(r"auth-webhook", AuthWebhookViewSet, basename="auth-webhook")
router.register(r"webhook-delivery", WebhookDeliveryViewSet, basename="webhook-delivery")
router.register(r"s-s-o-configuration", SSOConfigurationViewSet, basename="s-s-o-configuration")
router.register(r"domain-verification", DomainVerificationViewSet, basename="domain-verification")
router.register(r"i-p-geolocation-cache", IPGeolocationCacheViewSet, basename="i-p-geolocation-cache")
router.register(r"consent-record", ConsentRecordViewSet, basename="consent-record")
router.register(r"school-feature-flag", SchoolFeatureFlagViewSet, basename="school-feature-flag")
router.register(r"audit-report-schedule", AuditReportScheduleViewSet, basename="audit-report-schedule")

urlpatterns = [
    path("", include(router.urls)),
]
