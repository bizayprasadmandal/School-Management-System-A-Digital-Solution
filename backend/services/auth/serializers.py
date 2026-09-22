"""Serializers for auth."""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
    User,
    UserActivity,
    UserRoleAssignment,
    UserSession,
    UserSessionHistory,
    UserTrustScore,
    WebhookDelivery,
)
from .utils import generate_secure_password


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = [
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
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = UserSession
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "refresh_token_jti",
            "device_info",
            "ip_address",
            "created_at",
            "last_used",
            "is_active",
        ]
        read_only_fields = ["id", "created_at", "refresh_token_jti"]


class PasswordResetTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordResetToken
        fields = ["id", "user", "token", "created_at", "expires_at", "used"]
        read_only_fields = ["id", "created_at"]


class EmailVerificationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerificationToken
        fields = ["id", "id", "user", "email", "token", "created_at", "expires_at", "used"]
        read_only_fields = ["id", "created_at"]


class TwoFactorBackupCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwoFactorBackupCode
        fields = ["id", "id", "user", "hashed_code", "used", "created_at"]
        read_only_fields = ["id", "created_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    school_name = serializers.CharField(source="school.name", read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "school",
            "school_name",
            "user",
            "user_name",
            "user_email",
            "action",
            "resource_type",
            "resource_id",
            "changes",
            "ip_address",
            "user_agent",
            "timestamp",
        ]
        read_only_fields = ["id", "school"]

    def get_user_name(self, obj):
        return obj.user.full_name if obj.user else None

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None


class LoginHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    login_type_display = serializers.CharField(source="get_login_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    def get_user_name(self, obj):
        return obj.user.full_name if obj.user else obj.email

    class Meta:
        model = LoginHistory
        fields = [
            "id",
            "user",
            "user_name",
            "email",
            "login_type",
            "login_type_display",
            "status",
            "status_display",
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
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = APIKey
        fields = [
            "id",
            "school",
            "user",
            "user_name",
            "user_email",
            "name",
            "description",
            "key_prefix",
            "key_hash",
            "scopes",
            "rate_limit",
            "status",
            "status_display",
            "expires_at",
            "last_used_at",
            "last_used_ip",
        ]
        read_only_fields = ["id", "key_prefix", "key_hash", "created_at"]

    def get_user_name(self, obj):
        return obj.user.full_name if obj.user else None

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None


class DeviceManagementSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    device_type_display = serializers.CharField(source="get_device_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = DeviceManagement
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "device_name",
            "device_type",
            "device_type_display",
            "device_id",
            "fingerprint",
            "ip_address",
            "location",
            "status",
            "status_display",
            "is_active",
            "last_seen",
            "created_at",
            "trusted_at",
            "blocked_at",
        ]
        read_only_fields = ["id", "created_at"]


class PasswordPolicySerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PasswordPolicy
        fields = [
            "id",
            "school",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class IPWhitelistSerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    access_level_display = serializers.CharField(source="get_access_level_display", read_only=True)

    class Meta:
        model = IPWhitelist
        fields = [
            "id",
            "school",
            "ip_address",
            "ip_range",
            "description",
            "access_level",
            "access_level_display",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class OAuthProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthProvider
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class UserActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    activity_type_display = serializers.CharField(source="get_activity_type_display", read_only=True)

    class Meta:
        model = UserActivity
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "activity_type",
            "activity_type_display",
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
    school = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SessionPolicy
        fields = [
            "id",
            "school",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class RoleSerializer(serializers.ModelSerializer):
    """School-scoped dynamic roles. `school` is set from the request user."""

    school = serializers.PrimaryKeyRelatedField(read_only=True)
    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "school",
            "name",
            "description",
            "parent_role",
            "level",
            "is_active",
            "is_system_role",
            "permission_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_system_role", "created_at", "updated_at", "school"]

    def get_permission_count(self, obj):
        return obj.role_permissions.count()


class PermissionSerializer(serializers.ModelSerializer):
    """Global permission catalog shared across schools."""

    permission_type_display = serializers.CharField(source="get_permission_type_display", read_only=True)

    class Meta:
        model = Permission
        fields = [
            "id",
            "name",
            "codename",
            "description",
            "permission_type",
            "permission_type_display",
            "module",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class RolePermissionSerializer(serializers.ModelSerializer):
    """Grant a catalog permission to a school role."""

    role_name = serializers.CharField(source="role.name", read_only=True)
    permission_name = serializers.CharField(source="permission.name", read_only=True)
    permission_codename = serializers.CharField(source="permission.codename", read_only=True)
    permission_module = serializers.CharField(source="permission.module", read_only=True)
    permission_type_display = serializers.CharField(source="permission.get_permission_type_display", read_only=True)
    granted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RolePermission
        fields = [
            "id",
            "role",
            "role_name",
            "permission",
            "permission_name",
            "permission_codename",
            "permission_module",
            "permission_type_display",
            "granted",
            "conditions",
            "granted_at",
            "granted_by",
            "granted_by_name",
        ]
        read_only_fields = ["id", "granted_at", "granted_by"]

    def get_granted_by_name(self, obj):
        return obj.granted_by.full_name if obj.granted_by else None


class UserRoleSerializer(serializers.ModelSerializer):
    """Assign a school role to a user of the same school."""

    user_name = serializers.SerializerMethodField()
    user_email = serializers.CharField(source="user.email", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    assigned_by_name = serializers.SerializerMethodField()

    class Meta:
        model = UserRoleAssignment
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "role",
            "role_name",
            "scope",
            "is_active",
            "assigned_date",
            "expiry_date",
            "assigned_by",
            "assigned_by_name",
        ]
        read_only_fields = ["id", "assigned_date", "assigned_by"]

    def get_user_name(self, obj):
        return obj.user.full_name if obj.user else None

    def get_assigned_by_name(self, obj):
        return obj.assigned_by.full_name if obj.assigned_by else None


class UserDirectorySerializer(serializers.ModelSerializer):
    """Lightweight school user record for role-assignment pickers."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name", "role", "is_active", "avatar"]
        read_only_fields = fields


class SecurityPolicySerializer(serializers.ModelSerializer):
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    policy_type_display = serializers.CharField(source="get_policy_type_display", read_only=True)

    class Meta:
        model = SecurityPolicy
        fields = [
            "id",
            "school",
            "name",
            "policy_type",
            "policy_type_display",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class LoginAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginAttempt
        fields = [
            "id",
            "school",
            "id",
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
        ]
        read_only_fields = ["id", "school"]


class SessionTokenSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    token_type_display = serializers.CharField(source="get_token_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = SessionToken
        fields = [
            "id",
            "user",
            "user_name",
            "user_email",
            "token_type",
            "token_type_display",
            "status",
            "status_display",
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
        read_only_fields = ["id", "created_at", "token_hash"]


class MFAMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = MFAMethod
        fields = [
            "id",
            "id",
            "user",
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
        fields = ["id", "id", "mfa_method", "status", "ip_address", "user_agent", "attempted_at"]
        read_only_fields = ["id"]


class OAuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuthToken
        fields = [
            "id",
            "id",
            "user",
            "provider",
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
    api_key_name = serializers.CharField(source="api_key.name", read_only=True)

    class Meta:
        model = APIUsageLog
        fields = [
            "id",
            "api_key",
            "api_key_name",
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
            "evidence_file",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class PasswordHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordHistory
        fields = ["id", "id", "user", "password_hash", "changed_at", "changed_by", "change_reason"]
        read_only_fields = ["id"]


class UserTrustScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTrustScore
        fields = [
            "id",
            "id",
            "user",
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
            "data_type",
            "status",
            "requested_at",
            "completed_at",
            "export_file",
            "file_size_bytes",
            "expires_at",
            "error_message",
            "processed_by",
        ]
        read_only_fields = ["id", "school"]


class DataDeletionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataDeletionRequest
        fields = [
            "id",
            "school",
            "id",
            "user",
            "status",
            "reason",
            "data_scope",
            "reviewed_by",
            "review_notes",
            "requested_at",
            "reviewed_at",
            "completed_at",
            "denial_reason",
        ]
        read_only_fields = ["id", "school"]


class AuthWebhookSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthWebhook
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class WebhookDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookDelivery
        fields = [
            "id",
            "id",
            "webhook",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class DomainVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainVerification
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class SchoolFeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolFeatureFlag
        fields = [
            "id",
            "school",
            "id",
            "feature_name",
            "category",
            "description",
            "is_enabled",
            "rollout_percentage",
            "conditions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "school"]


class AuditReportScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditReportSchedule
        fields = [
            "id",
            "school",
            "id",
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
        read_only_fields = ["id", "created_at", "updated_at", "school"]


def serialize_login_user(user):
    """Build the user payload shared by login and 2FA-login responses."""
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "role": user.role,
        "avatar": user.avatar.url if user.avatar else None,
        "email_verified": user.email_verified,
        "school": (
            {
                "id": str(user.school.id),
                "name": user.school.name,
                "code": user.school.code,
            }
            if user.school
            else None
        ),
        "notify_email": user.notify_email,
        "notify_sms": user.notify_sms,
        "notify_push": user.notify_push,
    }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extends JWT payload with user profile data."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = serialize_login_user(self.user)
        return data


class PlatformDashboardSerializer(serializers.Serializer):
    """Cross-school analytics for super admin platform dashboard."""

    total_schools = serializers.IntegerField()
    active_schools = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    schools_by_tier = serializers.DictField(child=serializers.IntegerField())
    recent_schools = SchoolSerializer(many=True)
    top_schools = serializers.ListField(child=serializers.DictField())


class SchoolAdminSerializer(serializers.ModelSerializer):
    """Serializer for creating/managing school admin users."""

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone", "role", "is_active", "password", "date_joined"]
        read_only_fields = ["id", "date_joined"]

    def validate_role(self, value):
        if value != "school_admin":
            raise serializers.ValidationError("Only school_admin role can be created here.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        generated = password is None
        if generated:
            password = generate_secure_password()
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        # Expose the one-time plaintext when the password was auto-generated so
        # the caller can share it with the new admin. A caller-supplied
        # password is never echoed back.
        if generated:
            user._generated_password = password
        return user


class SendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=False,
        help_text="Email to verify. Defaults to the authenticated user's email if omitted.",
    )

    def validate_email(self, value):
        user = self.context["request"].user
        if value and value.lower() != user.email:
            raise serializers.ValidationError("You can only verify your own email address.")
        return value or user.email

    def validate(self, attrs):
        # Runs even when `email` is omitted from the payload.
        user = self.context["request"].user
        if user.email_verified:
            raise serializers.ValidationError({"email": "Email is already verified."})
        return attrs


class ConfirmEmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, help_text="The verification token sent to your email.")


class UserProfileSerializer(serializers.ModelSerializer):
    backup_codes_remaining = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "role",
            "is_active",
            "email_verified",
            "two_factor_enabled",
            "backup_codes_remaining",
            "notify_email",
            "notify_sms",
            "notify_push",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "role", "is_active", "email_verified", "date_joined"]

    def get_backup_codes_remaining(self, obj):
        if not obj.two_factor_enabled:
            return None
        return obj.backup_codes.filter(used=False).count()
