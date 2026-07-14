from django.contrib import admin
from .models import ConferenceSlot


@admin.register(ConferenceSlot)
class ConferenceSlotAdmin(admin.ModelAdmin):
    list_display = ["teacher", "student", "date", "start_time", "end_time", "is_booked"]
    list_filter = ["is_booked", "date"]
    search_fields = ["teacher__full_name", "student__user__full_name"]
