"""
Auth Service — Custom User model supporting multiple roles and multi-tenancy
"""

import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    SUPER_ADMIN = "super_admin", "Super Administrator"
    SCHOOL_ADMIN = "school_admin", "School Administrator"
    TEACHER = "teacher", "Teacher"
    STUDENT = "student", "Student"
    PARENT = "parent", "Parent / Guardian"
    ACCOUNTANT = "accountant", "Accountant"
    LIBRARIAN = "librarian", "Librarian"
    COUNSELOR = "counselor", "Counselor"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.SUPER_ADMIN)
        return self.create_user(email, password, **extra_fields)


class School(models.Model):
    """Multi-tenant: each school is an isolated tenant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    subdomain = models.CharField(max_length=63, unique=True)
    logo = models.ImageField(upload_to="schools/logos/", null=True, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    timezone = models.CharField(max_length=50, default="UTC")
    academic_year_start_month = models.PositiveSmallIntegerField(default=9)
    is_active = models.BooleanField(default=True)
    subscription_tier = models.CharField(
        max_length=20,
        choices=[("basic", "Basic"), ("standard", "Standard"), ("premium", "Premium")],
        default="standard",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "schools"

    def __str__(self):
        return f"{self.name} ({self.code})"


class User(AbstractBaseUser, PermissionsMixin):
    """Central user model — one account per person, role-scoped per school."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="users", null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="users/avatars/", null=True, blank=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, db_index=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    backup_code_failed_attempts = models.PositiveSmallIntegerField(default=0)
    backup_code_locked_until = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Notification preferences
    notify_email = models.BooleanField(default=True)
    notify_sms = models.BooleanField(default=False)
    notify_push = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "role"]

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["school", "role"]),
            models.Index(fields=["email", "is_active"]),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} <{self.email}> [{self.role}]"


class UserSession(models.Model):
    """Track active sessions for security auditing."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    refresh_token_jti = models.CharField(max_length=255, unique=True)
    device_info = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "user_sessions"

    def __str__(self):
        return f"Session for {self.user.email} ({self.ip_address})"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # SHA-256 hex digest of the plaintext reset token (same treatment as
    # TwoFactorBackupCode.hashed_code). The plaintext is only ever sent in the
    # reset email; it is never persisted. Tokens created before this hardening
    # stored the raw value and are unrecoverable.
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = "password_reset_tokens"

    def __str__(self):
        return f"Reset token for {self.user.email}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class EmailVerificationToken(models.Model):
    """Token for email verification — tied to a specific new email address."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verification_tokens")
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = "email_verification_tokens"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Verification for {self.email} — {'used' if self.used else 'pending'}"


class TwoFactorBackupCode(models.Model):
    """
    One-time backup codes for 2FA recovery.
    Each code is hashed with SHA-256 before storage.
    Users get a set of codes during 2FA setup; each can be used once
    to bypass TOTP verification during login.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="backup_codes")
    hashed_code = models.CharField(max_length=64, db_index=True)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "two_factor_backup_codes"
        indexes = [
            models.Index(fields=["user", "hashed_code"]),
        ]

    def __str__(self):
        status = "used" if self.used else "active"
        return f"Backup code for {self.user.email} ({status})"


class AuditLog(models.Model):
    """Immutable audit trail for all sensitive operations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]

    def __str__(self):
        actor = self.user.email if self.user_id else "system"
        return f"{self.action} on {self.resource_type} by {actor}"


class LoginHistory(models.Model):
    """Complete login tracking with IP, device, location."""

    class LoginType(models.TextChoices):
        PASSWORD = "password", "Password"
        TWO_FACTOR = "two_factor", "Two-Factor"
        OAUTH = "oauth", "OAuth"
        SSO = "sso", "SSO"
        MAGIC_LINK = "magic_link", "Magic Link"
        PASSKEY = "passkey", "Passkey"

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        BLOCKED = "blocked", "Blocked"
        PENDING_2FA = "pending_2fa", "Pending 2FA"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="login_history")
    email = models.EmailField()
    login_type = models.CharField(max_length=20, choices=LoginType.choices, default=LoginType.PASSWORD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUCCESS)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    location = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    failure_reason = models.CharField(max_length=200, blank=True)
    session_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_login_history"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["email", "created_at"]),
        ]

    def __str__(self):
        return f"{self.email} - {self.get_status_display()} ({self.created_at})"


class APIKey(models.Model):
    """API key management for integrations."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        REVOKED = "revoked", "Revoked"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="api_keys")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_keys")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    key_prefix = models.CharField(max_length=10, help_text="First 8 chars of the key for identification")
    key_hash = models.CharField(max_length=128, unique=True, help_text="SHA-256 hash of the API key")
    scopes = models.JSONField(default=list, blank=True, help_text="List of allowed scopes/permissions")
    rate_limit = models.PositiveIntegerField(default=1000, help_text="Requests per hour")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    last_used_ip = models.GenericIPAddressField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "auth_api_keys"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"


class DeviceManagement(models.Model):
    """Trusted device management."""

    class Status(models.TextChoices):
        TRUSTED = "trusted", "Trusted"
        PENDING = "pending", "Pending"
        BLOCKED = "blocked", "Blocked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    device_name = models.CharField(max_length=200)
    device_type = models.CharField(max_length=50, blank=True, help_text="e.g. Chrome on Windows")
    device_id = models.CharField(max_length=255, blank=True, help_text="Unique device identifier")
    fingerprint = models.CharField(max_length=255, blank=True, help_text="Browser/device fingerprint")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_active = models.BooleanField(default=True)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    trusted_at = models.DateTimeField(null=True, blank=True)
    blocked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "auth_devices"
        ordering = ["-last_seen"]

    def __str__(self):
        return f"{self.device_name} ({self.user.email})"


class PasswordPolicy(models.Model):
    """Password strength rules for a school."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name="password_policy")
    min_length = models.PositiveSmallIntegerField(default=8)
    max_length = models.PositiveSmallIntegerField(default=128)
    require_uppercase = models.BooleanField(default=True)
    require_lowercase = models.BooleanField(default=True)
    require_digit = models.BooleanField(default=True)
    require_special_char = models.BooleanField(default=True)
    special_chars = models.CharField(max_length=50, default="!@#$%^&*()_+-=[]{}|;':\",./<>?")
    prevent_REUSE = models.PositiveSmallIntegerField(
        default=5, help_text="Number of previous passwords to prevent reuse"
    )
    max_age_days = models.PositiveSmallIntegerField(default=90, help_text="Password expiry in days (0 = never)")
    lockout_attempts = models.PositiveSmallIntegerField(default=5)
    lockout_duration_minutes = models.PositiveSmallIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_password_policy"

    def __str__(self):
        return f"Password Policy for {self.school.name}"


class IPWhitelist(models.Model):
    """IP-based access control."""

    class AccessLevel(models.TextChoices):
        ADMIN = "admin", "Admin Only"
        STAFF = "staff", "Staff Only"
        ALL = "all", "All Users"
        API = "api", "API Access"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="ip_whitelist")
    ip_address = models.GenericIPAddressField()
    ip_range = models.CharField(max_length=50, blank=True, help_text="CIDR notation e.g. 192.168.1.0/24")
    description = models.CharField(max_length=200, blank=True)
    access_level = models.CharField(max_length=20, choices=AccessLevel.choices, default=AccessLevel.ALL)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_ip_whitelist"
        unique_together = [("school", "ip_address")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ip_address} ({self.get_access_level_display()})"


class OAuthProvider(models.Model):
    """OAuth/Social login providers."""

    class ProviderType(models.TextChoices):
        GOOGLE = "google", "Google"
        MICROSOFT = "microsoft", "Microsoft"
        GITHUB = "github", "GitHub"
        APPLE = "apple", "Apple"
        FACEBOOK = "facebook", "Facebook"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="oauth_providers")
    provider_type = models.CharField(max_length=20, choices=ProviderType.choices)
    name = models.CharField(max_length=100)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    redirect_uri = models.URLField(max_length=500)
    scopes = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_oauth_providers"
        unique_together = [("school", "provider_type")]

    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"


class UserActivity(models.Model):
    """Detailed user activity logs."""

    class ActivityType(models.TextChoices):
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        PASSWORD_CHANGE = "password_change", "Password Change"
        PROFILE_UPDATE = "profile_update", "Profile Update"
        SETTINGS_CHANGE = "settings_change", "Settings Change"
        DATA_EXPORT = "data_export", "Data Export"
        DATA_IMPORT = "data_import", "Data Import"
        FILE_UPLOAD = "file_upload", "File Upload"
        FILE_DOWNLOAD = "file_download", "File Download"
        REPORT_VIEW = "report_view", "Report View"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=50, blank=True)
    resource_id = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_user_activities"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["activity_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()} ({self.created_at})"


class SessionPolicy(models.Model):
    """Session timeout and security settings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name="session_policy")
    session_timeout_minutes = models.PositiveIntegerField(default=480, help_text="8 hours default")
    absolute_timeout_hours = models.PositiveIntegerField(default=24)
    idle_timeout_minutes = models.PositiveIntegerField(default=30)
    max_concurrent_sessions = models.PositiveIntegerField(default=5)
    enforce_single_session = models.BooleanField(default=False)
    require_reauthentication = models.BooleanField(default=False)
    reauthentication_interval_minutes = models.PositiveIntegerField(default=60)
    remember_me_days = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_session_policy"

    def __str__(self):
        return f"Session Policy for {self.school.name}"


# =============================================================================
# NEW MODELS: Role & Permission Management
# =============================================================================


class Role(models.Model):
    """Dynamic role management."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # Hierarchical
    parent_role = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="child_roles"
    )
    level = models.PositiveIntegerField(default=0, help_text="Higher = more authority")
    # Status
    is_active = models.BooleanField(default=True)
    is_system_role = models.BooleanField(default=False, help_text="Cannot be deleted")
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_roles"
        unique_together = [("school", "name")]

    def __str__(self):
        return f"{self.name} ({self.school.name})"


class Permission(models.Model):
    """Granular permission definitions."""

    class PermissionType(models.TextChoices):
        MODULE = "module", "Module Access"
        ACTION = "action", "Action Permission"
        DATA = "data", "Data Permission"
        REPORT = "report", "Report Permission"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permission_type = models.CharField(max_length=10, choices=PermissionType.choices, default=PermissionType.MODULE)
    # Module
    module = models.CharField(max_length=50, blank=True, help_text="e.g., students, fees, attendance")
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_permissions"
        ordering = ["module", "name"]

    def __str__(self):
        return f"{self.name} ({self.codename})"


class RolePermission(models.Model):
    """Assign permissions to roles."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="role_permissions")
    # Scope
    granted = models.BooleanField(default=True)
    conditions = models.JSONField(default=dict, blank=True, help_text="Conditional permissions")
    # Metadata
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "auth_role_permissions"
        unique_together = [("role", "permission")]

    def __str__(self):
        return f"{self.role} - {self.permission}"


class UserRole(models.Model):
    """Assign roles to users."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")
    # Scope
    scope = models.JSONField(default=dict, blank=True, help_text="Role scope constraints")
    # Status
    is_active = models.BooleanField(default=True)
    # Dates
    assigned_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(null=True, blank=True)
    # Metadata
    assigned_by = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "auth_user_roles"
        unique_together = [("user", "role")]

    def __str__(self):
        return f"{self.user.full_name} - {self.role.name}"


# =============================================================================
# NEW MODELS: Security Settings
# =============================================================================


class SecurityPolicy(models.Model):
    """School-wide security policies."""

    class PolicyType(models.TextChoices):
        PASSWORD = "password", "Password Policy"
        SESSION = "session", "Session Policy"
        LOGIN = "login", "Login Policy"
        MFA = "mfa", "Multi-Factor Authentication"
        API = "api", "API Access Policy"
        IP = "ip", "IP Policy"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="security_policies")
    name = models.CharField(max_length=200)
    policy_type = models.CharField(max_length=10, choices=PolicyType.choices)
    description = models.TextField(blank=True)
    # Settings
    settings = models.JSONField(default=dict, help_text="Policy settings as JSON")
    # Password settings
    min_length = models.PositiveIntegerField(null=True, blank=True)
    require_uppercase = models.BooleanField(default=False)
    require_lowercase = models.BooleanField(default=False)
    require_numbers = models.BooleanField(default=False)
    require_special = models.BooleanField(default=False)
    max_age_days = models.PositiveIntegerField(null=True, blank=True)
    history_count = models.PositiveIntegerField(default=5, help_text="Remember last N passwords")
    # Session settings
    session_timeout_minutes = models.PositiveIntegerField(default=30)
    max_concurrent_sessions = models.PositiveIntegerField(default=5)
    # Login settings
    max_attempts = models.PositiveIntegerField(default=5)
    lockout_duration_minutes = models.PositiveIntegerField(default=30)
    # Status
    is_active = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_security_policies"

    def __str__(self):
        return f"{self.name} ({self.get_policy_type_display()})"


class LoginAttempt(models.Model):
    """Track all login attempts."""

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        LOCKED = "locked", "Account Locked"
        BLOCKED = "blocked", "IP Blocked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="login_attempts")
    username = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    # Attempt details
    status = models.CharField(max_length=10, choices=Status.choices)
    failure_reason = models.CharField(max_length=100, blank=True)
    # Technical
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    device_info = models.JSONField(default=dict, blank=True)
    # Location
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    # Timestamp
    attempted_at = models.DateTimeField(auto_now_add=True)
    # Related
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True, related_name="login_attempts")

    class Meta:
        db_table = "auth_login_attempts"
        ordering = ["-attempted_at"]
        indexes = [
            models.Index(fields=["username", "attempted_at"]),
            models.Index(fields=["ip_address", "attempted_at"]),
            models.Index(fields=["school", "status"]),
        ]

    def __str__(self):
        return f"Login {self.get_status_display()}: {self.username} ({self.attempted_at})"


# =============================================================================
# NEW MODELS: Session Management (Extended)
# =============================================================================


class SessionToken(models.Model):
    """JWT/session token tracking."""

    class TokenType(models.TextChoices):
        ACCESS = "access", "Access Token"
        REFRESH = "refresh", "Refresh Token"
        RESET = "reset", "Password Reset"
        VERIFICATION = "verify", "Email Verification"
        API = "api", "API Token"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"
        BLACKLISTED = "blacklisted", "Blacklisted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="session_tokens")
    token_type = models.CharField(max_length=10, choices=TokenType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Token
    token_hash = models.CharField(max_length=255, unique=True)
    # Validity
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    last_used_at = models.DateTimeField(null=True, blank=True)
    # Device
    device_info = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    # Revocation
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.CharField(max_length=200, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_session_tokens"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "token_type", "status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.get_token_type_display()} - {self.user.full_name} ({self.get_status_display()})"

    @property
    def is_expired(self):
        from django.utils import timezone

        return timezone.now() > self.expires_at


# =============================================================================
# NEW MODELS: Multi-Factor Authentication
# =============================================================================


class MFAMethod(models.Model):
    """MFA methods configured per user."""

    class MethodType(models.TextChoices):
        TOTP = "totp", "Authenticator App (TOTP)"
        SMS = "sms", "SMS Code"
        EMAIL = "email", "Email Code"
        HARDWARE_KEY = "hardware", "Hardware Key (FIDO2)"
        BACKUP_CODES = "backup", "Backup Codes"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PENDING = "pending", "Pending Setup"
        DISABLED = "disabled", "Disabled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="mfa_methods")
    method_type = models.CharField(max_length=10, choices=MethodType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # TOTP
    totp_secret = models.CharField(max_length=255, blank=True)
    # SMS/Email
    phone_number = models.CharField(max_length=30, blank=True)
    email_address = models.EmailField(blank=True)
    # Hardware key
    hardware_key_id = models.CharField(max_length=255, blank=True)
    public_key = models.TextField(blank=True)
    # Backup codes
    backup_codes = models.JSONField(default=list, blank=True)
    # Verification
    last_used_at = models.DateTimeField(null=True, blank=True)
    use_count = models.PositiveIntegerField(default=0)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_mfa_methods"
        unique_together = [("user", "method_type")]

    def __str__(self):
        return f"{self.get_method_type_display()} - {self.user.full_name} ({self.get_status_display()})"


class MFAVerification(models.Model):
    """MFA verification attempts."""

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mfa_method = models.ForeignKey(MFAMethod, on_delete=models.CASCADE, related_name="verifications")
    status = models.CharField(max_length=10, choices=Status.choices)
    # Technical
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    # Timestamp
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_mfa_verifications"
        ordering = ["-attempted_at"]

    def __str__(self):
        return f"MFA {self.get_status_display()} - {self.mfa_method.user.full_name}"


# =============================================================================
# NEW MODELS: OAuth / Social Login
# =============================================================================


class OAuthToken(models.Model):
    """OAuth tokens for social login integrations."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="oauth_tokens")
    provider = models.ForeignKey(OAuthProvider, on_delete=models.CASCADE, related_name="tokens")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Tokens
    access_token = models.TextField(blank=True)
    refresh_token = models.TextField(blank=True)
    token_type = models.CharField(max_length=50, default="Bearer")
    # Provider user
    provider_user_id = models.CharField(max_length=255)
    provider_username = models.CharField(max_length=200, blank=True)
    provider_email = models.EmailField(blank=True)
    # Validity
    expires_at = models.DateTimeField(null=True, blank=True)
    scopes = models.JSONField(default=list, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_oauth_tokens"
        unique_together = [("user", "provider")]

    def __str__(self):
        return f"{self.provider} - {self.user.full_name}"


# =============================================================================
# NEW MODELS: Activity Tracking (Extended)
# =============================================================================


class UserSessionHistory(models.Model):
    """Extended session history tracking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="session_history")
    # Session details
    session_id = models.CharField(max_length=255, unique=True)
    # Device
    device_type = models.CharField(max_length=50, blank=True, help_text="Desktop, Mobile, Tablet")
    device_name = models.CharField(max_length=200, blank=True)
    os = models.CharField(max_length=100, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    # Location
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    # Timing
    login_at = models.DateTimeField()
    last_active_at = models.DateTimeField()
    logout_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    # Status
    is_current = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_session_history"
        ordering = ["-login_at"]
        indexes = [
            models.Index(fields=["user", "is_current"]),
        ]

    def __str__(self):
        return f"Session: {self.user.full_name} ({self.device_type}) - {self.login_at}"


# =============================================================================
# NEW MODELS: API Management (Extended)
# =============================================================================


class APIUsageLog(models.Model):
    """API usage tracking and rate limiting."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE, related_name="usage_logs")
    # Request details
    endpoint = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    status_code = models.PositiveIntegerField()
    response_time_ms = models.PositiveIntegerField(default=0)
    # Size
    request_size_bytes = models.PositiveIntegerField(default=0)
    response_size_bytes = models.PositiveIntegerField(default=0)
    # Technical
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    # Error
    error_message = models.TextField(blank=True)
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_api_usage_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["api_key", "timestamp"]),
            models.Index(fields=["endpoint", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code} ({self.timestamp})"


# =============================================================================
# NEW MODELS: Compliance & Audit
# =============================================================================


class ComplianceRecord(models.Model):
    """Compliance tracking for security and privacy."""

    class ComplianceType(models.TextChoices):
        GDPR = "gdpr", "GDPR Compliance"
        FERPA = "ferpa", "FERPA Compliance"
        HIPAA = "hipaa", "HIPAA Compliance"
        SOC2 = "soc2", "SOC 2 Compliance"
        ISO27001 = "iso27001", "ISO 27001"
        CUSTOM = "custom", "Custom Policy"

    class Status(models.TextChoices):
        COMPLIANT = "compliant", "Compliant"
        NON_COMPLIANT = "non_compliant", "Non-Compliant"
        IN_PROGRESS = "in_progress", "In Progress"
        EXEMPT = "exempt", "Exempt"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="auth_compliance_records")
    compliance_type = models.CharField(max_length=15, choices=ComplianceType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.IN_PROGRESS)
    # Details
    requirement = models.TextField(help_text="What needs to be compliant")
    current_state = models.TextField(blank=True)
    gap_analysis = models.TextField(blank=True)
    remediation_plan = models.TextField(blank=True)
    # Dates
    assessment_date = models.DateField()
    next_assessment_date = models.DateField(null=True, blank=True)
    last_compliant_date = models.DateField(null=True, blank=True)
    # Responsible
    responsible_person = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    # Document
    evidence_file = models.FileField(upload_to="auth/compliance/", null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_compliance_records"
        ordering = ["-assessment_date"]

    def __str__(self):
        return f"{self.get_compliance_type_display()} - {self.get_status_display()} ({self.assessment_date})"


# =============================================================================
# NEW MODELS: Password History
# =============================================================================


class PasswordHistory(models.Model):
    """Track password changes for enforcement."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="password_history")
    password_hash = models.CharField(max_length=255)
    changed_at = models.DateTimeField(auto_now_add=True)
    # Metadata
    changed_by = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, blank=True, related_name="password_changes_made"
    )
    change_reason = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = "auth_password_history"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"Password change: {self.user.full_name} ({self.changed_at})"


# =============================================================================
# NEW MODELS: Trust & Risk Scoring
# =============================================================================


class UserTrustScore(models.Model):
    """User trust/risk scoring for adaptive security."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="trust_score")
    # Score
    trust_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=50, help_text="0-100 (100 = fully trusted)"
    )
    risk_level = models.CharField(max_length=20, blank=True, help_text="Low, Medium, High, Critical")
    # Factors
    account_age_days = models.PositiveIntegerField(default=0)
    successful_logins = models.PositiveIntegerField(default=0)
    failed_logins = models.PositiveIntegerField(default=0)
    suspicious_activities = models.PositiveIntegerField(default=0)
    devices_used = models.PositiveIntegerField(default=0)
    locations_used = models.PositiveIntegerField(default=0)
    # MFA
    mfa_enabled = models.BooleanField(default=False)
    mfa_methods_count = models.PositiveIntegerField(default=0)
    # Last activity
    last_login = models.DateTimeField(null=True, blank=True)
    last_password_change = models.DateTimeField(null=True, blank=True)
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_user_trust_scores"

    def __str__(self):
        return f"Trust Score: {self.user.full_name} ({self.trust_score})"


# =============================================================================
# NEW MODELS: Notification Preferences
# =============================================================================


class SecurityNotificationPreference(models.Model):
    """Security notification preferences per user."""

    class NotificationType(models.TextChoices):
        LOGIN = "login", "New Login"
        PASSWORD_CHANGE = "password", "Password Changed"
        MFA_CHANGE = "mfa", "MFA Changed"
        API_KEY = "api_key", "API Key Used"
        SUSPICIOUS = "suspicious", "Suspicious Activity"
        DEVICE = "device", "New Device"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="security_notification_prefs")
    notification_type = models.CharField(max_length=15, choices=NotificationType.choices)
    # Channels
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_security_notification_prefs"
        unique_together = [("user", "notification_type")]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.full_name}"


# =============================================================================
# NEW MODELS: Data Export / Privacy
# =============================================================================


class DataExportRequest(models.Model):
    """GDPR/privacy data export requests."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    class DataType(models.TextChoices):
        ALL = "all", "All Data"
        PROFILE = "profile", "Profile Data"
        ACTIVITY = "activity", "Activity Logs"
        ACADEMIC = "academic", "Academic Records"
        FINANCIAL = "financial", "Financial Data"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="data_export_requests")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="data_export_requests")
    data_type = models.CharField(max_length=15, choices=DataType.choices, default=DataType.ALL)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Processing
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # Output
    export_file = models.FileField(upload_to="auth/data_exports/", null=True, blank=True)
    file_size_bytes = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Download link expiry")
    # Error
    error_message = models.TextField(blank=True)
    # Metadata
    processed_by = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "auth_data_export_requests"
        ordering = ["-requested_at"]

    def __str__(self):
        return f"Data Export: {self.user.full_name} ({self.get_status_display()})"


class DataDeletionRequest(models.Model):
    """GDPR/privacy data deletion requests."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWING = "reviewing", "Under Review"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        DENIED = "denied", "Denied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="data_deletion_requests")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="data_deletion_requests")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Details
    reason = models.TextField(blank=True)
    data_scope = models.TextField(help_text="What data to delete")
    # Review
    reviewed_by = models.ForeignKey("User", on_delete=models.SET_NULL, null=True, blank=True)
    review_notes = models.TextField(blank=True)
    # Processing
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    denial_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "auth_data_deletion_requests"
        ordering = ["-requested_at"]

    def __str__(self):
        return f"Deletion Request: {self.user.full_name} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Webhook Management
# =============================================================================


class AuthWebhook(models.Model):
    """Webhooks for auth events."""

    class EventType(models.TextChoices):
        LOGIN = "login", "User Login"
        LOGOUT = "logout", "User Logout"
        PASSWORD_CHANGE = "password", "Password Change"
        MFA_SETUP = "mfa_setup", "MFA Setup"
        USER_CREATED = "user_create", "User Created"
        USER_DEACTIVATED = "user_deactivate", "User Deactivated"
        ROLE_CHANGED = "role", "Role Changed"
        SUSPICIOUS = "suspicious", "Suspicious Activity"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        DISABLED = "disabled", "Disabled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="auth_webhooks")
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=500)
    secret = models.CharField(max_length=255, blank=True)
    event_type = models.CharField(max_length=15, choices=EventType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Headers
    headers = models.JSONField(default=dict, blank=True)
    # Retry
    max_retries = models.PositiveIntegerField(default=3)
    retry_interval_seconds = models.PositiveIntegerField(default=60)
    # Stats
    total_deliveries = models.PositiveIntegerField(default=0)
    successful_deliveries = models.PositiveIntegerField(default=0)
    failed_deliveries = models.PositiveIntegerField(default=0)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_webhooks"

    def __str__(self):
        return f"{self.name} ({self.get_event_type_display()})"


class WebhookDelivery(models.Model):
    """Webhook delivery attempts."""

    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        RETRYING = "retrying", "Retrying"
        PENDING = "pending", "Pending"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    webhook = models.ForeignKey(AuthWebhook, on_delete=models.CASCADE, related_name="deliveries")
    # Request
    payload = models.JSONField(default=dict)
    headers = models.JSONField(default=dict)
    # Response
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    response_status_code = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    # Retry
    attempt_number = models.PositiveIntegerField(default=1)
    max_attempts = models.PositiveIntegerField(default=3)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    # Timing
    sent_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    response_time_ms = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "auth_webhook_deliveries"
        ordering = ["-sent_at"]

    def __str__(self):
        return f"Webhook {self.get_status_display()} - {self.webhook.name} ({self.sent_at})"


class SSOConfiguration(models.Model):
    """Single Sign-On configuration."""

    class Provider(models.TextChoices):
        SAML = "saml", "SAML 2.0"
        OIDC = "oidc", "OpenID Connect"
        CAS = "cas", "CAS"
        AZURE_AD = "azure", "Azure AD"
        GOOGLE = "google", "Google Workspace"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        CONFIGURING = "configuring", "Configuring"
        DISABLED = "disabled", "Disabled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sso_configurations")
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=10, choices=Provider.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.CONFIGURING)
    # SAML
    entity_id = models.CharField(max_length=500, blank=True)
    sso_url = models.URLField(max_length=500, blank=True)
    slo_url = models.URLField(max_length=500, blank=True)
    x509_cert = models.TextField(blank=True)
    # OIDC
    client_id = models.CharField(max_length=255, blank=True)
    client_secret = models.CharField(max_length=255, blank=True)
    discovery_url = models.URLField(max_length=500, blank=True)
    # Mapping
    attribute_mapping = models.JSONField(default=dict, blank=True)
    # Status
    is_default = models.BooleanField(default=False)
    auto_provision_users = models.BooleanField(default=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_sso_configurations"

    def __str__(self):
        return f"{self.name} ({self.get_provider_display()})"


class DomainVerification(models.Model):
    """Email domain verification for school."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="domain_verifications")
    domain = models.CharField(max_length=200, unique=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Verification
    verification_token = models.CharField(max_length=255, blank=True)
    verification_method = models.CharField(max_length=20, blank=True, help_text="DNS, HTML, Email")
    # DNS records
    txt_record_name = models.CharField(max_length=200, blank=True)
    txt_record_value = models.CharField(max_length=255, blank=True)
    # Status
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_domain_verifications"

    def __str__(self):
        return f"{self.domain} ({self.get_status_display()})"


class IPGeolocationCache(models.Model):
    """Cache IP geolocation data."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField(unique=True)
    country = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    isp = models.CharField(max_length=200, blank=True)
    is_vpn = models.BooleanField(default=False)
    is_proxy = models.BooleanField(default=False)
    # Metadata
    fetched_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "auth_ip_geolocation_cache"

    def __str__(self):
        return f"{self.ip_address} - {self.city}, {self.country}"


class ConsentRecord(models.Model):
    """Track user consent for privacy/terms."""

    class ConsentType(models.TextChoices):
        TERMS = "terms", "Terms of Service"
        PRIVACY = "privacy", "Privacy Policy"
        COOKIE = "cookie", "Cookie Consent"
        DATA_PROCESSING = "data", "Data Processing"
        MARKETING = "marketing", "Marketing Communications"

    class Status(models.TextChoices):
        GRANTED = "granted", "Granted"
        DENIED = "denied", "Denied"
        WITHDRAWN = "withdrawn", "Withdrawn"
        PENDING = "pending", "Pending"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="consent_records")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="consent_records")
    consent_type = models.CharField(max_length=15, choices=ConsentType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Version
    policy_version = models.CharField(max_length=50, blank=True)
    policy_url = models.URLField(blank=True)
    # Consent
    consented_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    # Technical
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_consent_records"
        unique_together = [("user", "consent_type", "policy_version")]

    def __str__(self):
        return f"{self.get_consent_type_display()} - {self.user.full_name} ({self.get_status_display()})"


class SchoolFeatureFlag(models.Model):
    """Feature flags for schools."""

    class FeatureCategory(models.TextChoices):
        AUTH = "auth", "Authentication"
        ENROLLMENT = "enrollment", "Enrollment"
        BILLING = "billing", "Billing"
        REPORTING = "reporting", "Reporting"
        INTEGRATION = "integration", "Integration"
        UI = "ui", "User Interface"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="feature_flags")
    feature_name = models.CharField(max_length=100)
    category = models.CharField(max_length=15, choices=FeatureCategory.choices)
    description = models.TextField(blank=True)
    # Status
    is_enabled = models.BooleanField(default=False)
    # Rollout
    rollout_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    # Conditions
    conditions = models.JSONField(default=dict, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_feature_flags"
        unique_together = [("school", "feature_name")]

    def __str__(self):
        return f"{self.feature_name} - {'Enabled' if self.is_enabled else 'Disabled'} ({self.school.name})"


class AuditReportSchedule(models.Model):
    """Scheduled audit report generation."""

    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"

    class ReportType(models.TextChoices):
        LOGIN_SUMMARY = "login", "Login Summary"
        SECURITY_EVENTS = "security", "Security Events"
        API_USAGE = "api", "API Usage"
        USER_ACTIVITY = "activity", "User Activity"
        COMPLIANCE = "compliance", "Compliance"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="audit_report_schedules")
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=15, choices=ReportType.choices)
    frequency = models.CharField(max_length=15, choices=Frequency.choices)
    # Schedule
    day_of_week = models.CharField(max_length=10, blank=True)
    day_of_month = models.PositiveIntegerField(null=True, blank=True)
    time_of_day = models.TimeField()
    # Delivery
    recipients = models.ManyToManyField("User", blank=True, related_name="audit_report_subscriptions")
    email_delivery = models.BooleanField(default=True)
    # Status
    is_active = models.BooleanField(default=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    next_generation = models.DateTimeField(null=True, blank=True)
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "auth_audit_report_schedules"

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"
