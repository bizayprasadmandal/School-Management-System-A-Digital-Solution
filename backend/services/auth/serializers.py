"""Serializers for auth."""

from rest_framework import serializers

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
    UserRole,
    UserSession,
    UserSessionHistory,
    UserTrustScore,
    WebhookDelivery,
)


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
            "id",
            "id",
            "name",
            "code",
            "subdomain",
            "logo",
            "address",
            "phone",
            "email",
            "website",
            "timezone",
            "academic_year_start_month",
            "is_active",
            "subscription_tier",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "refresh_token_jti",
            "device_info",
            "ip_address",
            "created_at",
            "last_used",
            "is_active",
        ]
        read_only_fields = ["id", "created_at"]


class PasswordResetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordResetToken
        fields = ["id", "user", "on_delete", "token", "created_at", "expires_at", "used"]
        read_only_fields = ["id", "created_at"]


class EmailVerificationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerificationToken
        fields = ["id", "id", "user", "on_delete", "email", "token", "created_at", "expires_at", "used"]
        read_only_fields = ["id", "created_at"]


class TwoFactorBackupCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwoFactorBackupCode
        fields = ["id", "id", "user", "on_delete", "hashed_code", "used", "created_at"]
        read_only_fields = ["id", "created_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "user",
            "on_delete",
            "action",
            "resource_type",
            "resource_id",
            "changes",
            "ip_address",
            "user_agent",
            "timestamp",
        ]
        read_only_fields = ["id"]


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "email",
            "login_type",
            "status",
            "ip_address",
            "user_agent",
            "device_info",
            "location",
            "country",
            "city",
            "failure_reason",
            "session_id",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "user",
            "on_delete",
            "name",
            "description",
            "key_prefix",
            "key_hash",
            "scopes",
            "rate_limit",
            "status",
            "expires_at",
            "last_used_at",
            "last_used_ip",
        ]
        read_only_fields = ["id", "created_at"]


class DeviceManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceManagement
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "device_name",
            "device_type",
            "device_id",
            "fingerprint",
            "ip_address",
            "location",
            "status",
            "is_active",
            "last_seen",
            "created_at",
            "trusted_at",
            "blocked_at",
        ]
        read_only_fields = ["id", "created_at"]


class PasswordPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordPolicy
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "min_length",
            "max_length",
            "require_uppercase",
            "require_lowercase",
            "require_digit",
            "require_special_char",
            "special_chars",
            "prevent_REUSE",
            "max_age_days",
            "lockout_attempts",
            "lockout_duration_minutes",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class IPWhitelistSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPWhitelist
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "ip_address",
            "ip_range",
            "description",
            "access_level",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OAuthProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthProvider
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "provider_type",
            "name",
            "client_id",
            "client_secret",
            "redirect_uri",
            "scopes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "activity_type",
            "description",
            "resource_type",
            "resource_id",
            "ip_address",
            "user_agent",
            "metadata",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SessionPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionPolicy
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "session_timeout_minutes",
            "absolute_timeout_hours",
            "idle_timeout_minutes",
            "max_concurrent_sessions",
            "enforce_single_session",
            "require_reauthentication",
            "reauthentication_interval_minutes",
            "remember_me_days",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "parent_role",
            "on_delete",
            "level",
            "is_active",
            "is_system_role",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "id", "name", "codename", "description", "permission_type", "module", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = [
            "id",
            "id",
            "role",
            "on_delete",
            "permission",
            "on_delete",
            "granted",
            "conditions",
            "granted_at",
            "granted_by",
            "on_delete",
        ]
        read_only_fields = ["id"]


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "role",
            "on_delete",
            "scope",
            "is_active",
            "assigned_date",
            "expiry_date",
            "assigned_by",
            "on_delete",
        ]
        read_only_fields = ["id"]


class SecurityPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityPolicy
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "policy_type",
            "description",
            "settings",
            "min_length",
            "require_uppercase",
            "require_lowercase",
            "require_numbers",
            "require_special",
            "max_age_days",
            "history_count",
            "session_timeout_minutes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginAttempt
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "username",
            "email",
            "status",
            "failure_reason",
            "ip_address",
            "user_agent",
            "device_info",
            "city",
            "country",
            "attempted_at",
            "user",
            "on_delete",
        ]
        read_only_fields = ["id"]


class SessionTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionToken
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "token_type",
            "status",
            "token_hash",
            "issued_at",
            "expires_at",
            "last_used_at",
            "device_info",
            "ip_address",
            "revoked_at",
            "revocation_reason",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class MFAMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = MFAMethod
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "method_type",
            "status",
            "totp_secret",
            "phone_number",
            "email_address",
            "hardware_key_id",
            "public_key",
            "backup_codes",
            "last_used_at",
            "use_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MFAVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MFAVerification
        fields = ["id", "id", "mfa_method", "on_delete", "status", "ip_address", "user_agent", "attempted_at"]
        read_only_fields = ["id"]


class OAuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthToken
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "provider",
            "on_delete",
            "status",
            "access_token",
            "refresh_token",
            "token_type",
            "provider_user_id",
            "provider_username",
            "provider_email",
            "expires_at",
            "scopes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserSessionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSessionHistory
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "session_id",
            "device_type",
            "device_name",
            "os",
            "browser",
            "ip_address",
            "city",
            "country",
            "login_at",
            "last_active_at",
            "logout_at",
            "duration_minutes",
        ]
        read_only_fields = ["id", "created_at"]


class APIUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIUsageLog
        fields = [
            "id",
            "id",
            "api_key",
            "on_delete",
            "endpoint",
            "method",
            "status_code",
            "response_time_ms",
            "request_size_bytes",
            "response_size_bytes",
            "ip_address",
            "user_agent",
            "error_message",
            "timestamp",
        ]
        read_only_fields = ["id"]


class ComplianceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceRecord
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "compliance_type",
            "status",
            "requirement",
            "current_state",
            "gap_analysis",
            "remediation_plan",
            "assessment_date",
            "next_assessment_date",
            "last_compliant_date",
            "responsible_person",
            "on_delete",
            "evidence_file",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PasswordHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordHistory
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "password_hash",
            "changed_at",
            "changed_by",
            "on_delete",
            "change_reason",
        ]
        read_only_fields = ["id"]


class UserTrustScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTrustScore
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "trust_score",
            "risk_level",
            "account_age_days",
            "successful_logins",
            "failed_logins",
            "suspicious_activities",
            "devices_used",
            "locations_used",
            "mfa_enabled",
            "mfa_methods_count",
            "last_login",
            "last_password_change",
        ]
        read_only_fields = ["id", "created_at"]


class SecurityNotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityNotificationPreference
        fields = [
            "id",
            "id",
            "user",
            "on_delete",
            "notification_type",
            "email_enabled",
            "sms_enabled",
            "push_enabled",
            "in_app_enabled",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DataExportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataExportRequest
        fields = [
            "id",
            "school",
            "id",
            "user",
            "on_delete",
            "on_delete",
            "data_type",
            "status",
            "requested_at",
            "completed_at",
            "export_file",
            "file_size_bytes",
            "expires_at",
            "error_message",
            "processed_by",
            "on_delete",
        ]
        read_only_fields = ["id"]


class DataDeletionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDeletionRequest
        fields = [
            "id",
            "school",
            "id",
            "user",
            "on_delete",
            "on_delete",
            "status",
            "reason",
            "data_scope",
            "reviewed_by",
            "on_delete",
            "review_notes",
            "requested_at",
            "reviewed_at",
            "completed_at",
            "denial_reason",
        ]
        read_only_fields = ["id"]


class AuthWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthWebhook
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "url",
            "secret",
            "event_type",
            "status",
            "headers",
            "max_retries",
            "retry_interval_seconds",
            "total_deliveries",
            "successful_deliveries",
            "failed_deliveries",
            "last_triggered_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WebhookDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookDelivery
        fields = [
            "id",
            "id",
            "webhook",
            "on_delete",
            "payload",
            "headers",
            "status",
            "response_status_code",
            "response_body",
            "error_message",
            "attempt_number",
            "max_attempts",
            "next_retry_at",
            "sent_at",
            "completed_at",
            "response_time_ms",
        ]
        read_only_fields = ["id"]


class SSOConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSOConfiguration
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "provider",
            "status",
            "entity_id",
            "sso_url",
            "slo_url",
            "x509_cert",
            "client_id",
            "client_secret",
            "discovery_url",
            "attribute_mapping",
            "is_default",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DomainVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainVerification
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "domain",
            "status",
            "verification_token",
            "verification_method",
            "txt_record_name",
            "txt_record_value",
            "verified_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class IPGeolocationCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPGeolocationCache
        fields = [
            "id",
            "id",
            "ip_address",
            "country",
            "region",
            "city",
            "latitude",
            "longitude",
            "timezone",
            "isp",
            "is_vpn",
            "is_proxy",
            "fetched_at",
            "expires_at",
        ]
        read_only_fields = ["id"]


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = [
            "id",
            "school",
            "id",
            "user",
            "on_delete",
            "on_delete",
            "consent_type",
            "status",
            "policy_version",
            "policy_url",
            "consented_at",
            "withdrawn_at",
            "ip_address",
            "user_agent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SchoolFeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolFeatureFlag
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "feature_name",
            "category",
            "description",
            "is_enabled",
            "rollout_percentage",
            "conditions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AuditReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditReportSchedule
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "report_type",
            "frequency",
            "day_of_week",
            "day_of_month",
            "time_of_day",
            "recipients",
            "email_delivery",
            "is_active",
            "last_generated",
            "next_generation",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
