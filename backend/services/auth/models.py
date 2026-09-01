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
