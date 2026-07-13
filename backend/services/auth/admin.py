"""
Auth Service — Django Admin registrations with custom displays
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, School, AuditLog, UserSession, PasswordResetToken, EmailVerificationToken, TwoFactorBackupCode


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
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "school", "password1", "password2"),
        }),
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

    def has_add_permission(self, request): return False


@admin.register(TwoFactorBackupCode)
class TwoFactorBackupCodeAdmin(admin.ModelAdmin):
    list_display = ["user", "hashed_code_short", "used", "created_at"]
    list_filter = ["used"]
    search_fields = ["user__email"]
    readonly_fields = ["id", "hashed_code", "created_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False

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

    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
