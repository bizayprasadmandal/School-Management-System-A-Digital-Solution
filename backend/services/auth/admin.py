"""
Auth Service — Django Admin registrations with custom displays
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    APIKey,
    AuditLog,
    DeviceManagement,
    EmailVerificationToken,
    IPWhitelist,
    LoginHistory,
    OAuthProvider,
    PasswordPolicy,
    School,
    SessionPolicy,
    TwoFactorBackupCode,
    User,
    UserActivity,
)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "subdomain", "subscription_tier", "is_active", "created_at"]
    list_filter = ["subscription_tier", "is_active"]
    search_fields = ["name", "code", "subdomain", "email"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        ("Identity", {"fields": ("id", "name", "code", "subdomain", "logo")}),
        ("Contact", {"fields": ("address", "phone", "email", "website")}),
        ("Settings", {"fields": ("timezone", "academic_year_start_month", "subscription_tier", "is_active")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "full_name", "role", "school", "is_active", "date_joined"]
    list_filter = ["role", "is_active", "email_verified", "school"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]
    readonly_fields = ["id", "last_login_ip", "date_joined", "updated_at"]
    fieldsets = (
        ("Credentials", {"fields": ("id", "email", "password")}),
        ("Profile", {"fields": ("first_name", "last_name", "phone", "avatar")}),
        ("Role & School", {"fields": ("role", "school")}),
        ("Status", {"fields": ("is_active", "is_staff", "is_superuser", "email_verified", "two_factor_enabled")}),
        ("Notifications", {"fields": ("notify_email", "notify_sms", "notify_push")}),
        ("Meta", {"fields": ("last_login_ip", "date_joined", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "role", "school", "password1", "password2"),
            },
        ),
    )

    def full_name(self, obj):
        return obj.full_name

    full_name.short_description = "Name"


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ["email", "user", "created_at", "expires_at", "used"]
    list_filter = ["used"]
    search_fields = ["email", "user__email"]
    readonly_fields = ["id", "token", "created_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False


@admin.register(TwoFactorBackupCode)
class TwoFactorBackupCodeAdmin(admin.ModelAdmin):
    list_display = ["user", "hashed_code_short", "used", "created_at"]
    list_filter = ["used"]
    search_fields = ["user__email"]
    readonly_fields = ["id", "hashed_code", "created_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def hashed_code_short(self, obj):
        return f"{obj.hashed_code[:12]}..."

    hashed_code_short.short_description = "Code (hashed)"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "user", "action", "resource_type", "resource_id", "ip_address"]
    list_filter = ["action", "resource_type"]
    search_fields = ["user__email", "resource_id", "ip_address"]
    readonly_fields = [f.name for f in AuditLog._meta.get_fields()]
    ordering = ["-timestamp"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ["email", "login_type", "status", "ip_address", "created_at"]
    list_filter = ["login_type", "status"]
    search_fields = ["email", "ip_address"]
    readonly_fields = ["id", "created_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "key_prefix", "user", "status", "last_used_at", "usage_count"]
    list_filter = ["status"]
    search_fields = ["name", "user__email"]
    readonly_fields = ["id", "key_hash", "last_used_at", "last_used_ip", "usage_count", "created_at"]


@admin.register(DeviceManagement)
class DeviceManagementAdmin(admin.ModelAdmin):
    list_display = ["device_name", "user", "status", "last_seen", "is_active"]
    list_filter = ["status", "is_active"]
    search_fields = ["device_name", "user__email"]
    readonly_fields = ["id", "last_seen", "created_at"]


@admin.register(PasswordPolicy)
class PasswordPolicyAdmin(admin.ModelAdmin):
    list_display = ["school", "min_length", "require_uppercase", "require_digit", "lockout_attempts"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(IPWhitelist)
class IPWhitelistAdmin(admin.ModelAdmin):
    list_display = ["ip_address", "school", "access_level", "is_active"]
    list_filter = ["access_level", "is_active"]
    search_fields = ["ip_address", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(OAuthProvider)
class OAuthProviderAdmin(admin.ModelAdmin):
    list_display = ["name", "provider_type", "school", "is_active"]
    list_filter = ["provider_type", "is_active"]
    search_fields = ["name"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ["user", "activity_type", "resource_type", "created_at"]
    list_filter = ["activity_type"]
    search_fields = ["user__email", "description"]
    readonly_fields = ["id", "created_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SessionPolicy)
class SessionPolicyAdmin(admin.ModelAdmin):
    list_display = ["school", "session_timeout_minutes", "max_concurrent_sessions", "is_active"]
    readonly_fields = ["id", "created_at", "updated_at"]
