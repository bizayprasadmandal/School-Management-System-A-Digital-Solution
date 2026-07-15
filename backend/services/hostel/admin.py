"""Hostel / Accommodation Management — Django Admin registrations."""

from django.contrib import admin
from .models import Hostel, HostelRoom, HostelAllocation, HostelFee, HostelVisitor


class HostelRoomInline(admin.TabularInline):
    model = HostelRoom
    extra = 1
    fields = ["room_number", "floor", "room_type", "capacity", "monthly_fee", "is_active"]


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "gender", "status", "warden", "total_floors"]
    list_filter = ["gender", "status", "school"]
    search_fields = ["name", "code", "address"]
    inlines = [HostelRoomInline]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(HostelRoom)
class HostelRoomAdmin(admin.ModelAdmin):
    list_display = ["room_number", "hostel", "floor", "room_type", "capacity", "is_active"]
    list_filter = ["room_type", "is_active", "has_ac", "is_furnished"]
    search_fields = ["room_number", "hostel__name"]
    readonly_fields = ["id", "created_at"]


@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):
    list_display = ["student", "room", "status", "check_in_date", "check_out_date", "is_paid"]
    list_filter = ["status", "is_paid"]
    search_fields = ["student__user__full_name", "room__room_number"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(HostelFee)
class HostelFeeAdmin(admin.ModelAdmin):
    list_display = ["name", "hostel", "amount", "billing_cycle", "is_active"]
    list_filter = ["billing_cycle", "is_active"]
    search_fields = ["name", "hostel__name"]
    readonly_fields = ["id", "created_at"]


@admin.register(HostelVisitor)
class HostelVisitorAdmin(admin.ModelAdmin):
    list_display = ["visitor_name", "student_visited", "hostel", "in_time", "out_time"]
    list_filter = ["hostel"]
    search_fields = ["visitor_name", "phone"]
    readonly_fields = ["id", "created_at"]
