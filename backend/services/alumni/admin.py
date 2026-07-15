from django.contrib import admin
from .models import AlumniProfile, AlumniEvent, AlumniDonation, AlumniChapter

@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "graduation_year", "occupation", "employer", "city"]
    list_filter = ["graduation_year", "employment_status", "country"]
    search_fields = ["user__full_name", "user__email", "occupation", "employer"]
    readonly_fields = ["id", "created_at", "updated_at"]

@admin.register(AlumniEvent)
class AlumniEventAdmin(admin.ModelAdmin):
    list_display = ["title", "event_date", "location", "status"]
    list_filter = ["status"]; search_fields = ["title"]

@admin.register(AlumniDonation)
class AlumniDonationAdmin(admin.ModelAdmin):
    list_display = ["alumni", "amount", "fund_type", "donation_date", "is_recurring"]
    list_filter = ["fund_type", "is_recurring"]; search_fields = ["alumni__user__full_name"]

@admin.register(AlumniChapter)
class AlumniChapterAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "country", "president", "is_active"]
    list_filter = ["is_active", "country"]; search_fields = ["name", "city"]
