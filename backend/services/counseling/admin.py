"""
Counseling Service — Django Admin registrations.
"""

from django.contrib import admin
from .models import CounselingAppointment, StudentReferral


@admin.register(CounselingAppointment)
class CounselingAppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "student_name", "counselor_name", "appointment_type",
        "scheduled_date", "scheduled_time", "status",
    ]
    list_filter = ["status", "appointment_type", "scheduled_date"]
    search_fields = [
        "student__user__first_name", "student__user__last_name",
        "counselor__first_name", "counselor__last_name",
        "reason",
    ]
    date_hierarchy = "scheduled_date"
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-scheduled_date"]

    @admin.display(description="Student")
    def student_name(self, obj):
        return obj.student.user.full_name

    @admin.display(description="Counselor")
    def counselor_name(self, obj):
        return obj.counselor.full_name


@admin.register(StudentReferral)
class StudentReferralAdmin(admin.ModelAdmin):
    list_display = [
        "student_name", "category", "priority", "status",
        "assigned_to", "created_at",
    ]
    list_filter = ["status", "priority", "category"]
    search_fields = [
        "student__user__first_name", "student__user__last_name",
        "reason", "notes",
    ]
    readonly_fields = ["id", "created_at", "updated_at", "action_taken_at"]
    ordering = ["-created_at"]
    actions = ["mark_as_closed"]

    @admin.display(description="Student")
    def student_name(self, obj):
        return obj.student.user.full_name

    @admin.display(description="Mark selected referrals as closed")
    def mark_as_closed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status="closed", action_taken_at=timezone.now())
        self.message_user(request, f"{updated} referral(s) closed.")
