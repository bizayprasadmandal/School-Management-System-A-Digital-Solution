from django.contrib import admin
from .models import Incident, Referral


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ["student", "incident_type", "severity", "occurred_at", "reported_by", "status"]
    list_filter = ["status", "severity", "incident_type"]
    search_fields = ["student__user__full_name", "description"]


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ["incident", "referred_to", "referred_by", "status", "created_at"]
    list_filter = ["status"]
