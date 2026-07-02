from django.contrib import admin
from .models import Announcement, DirectMessage, Notification, NotificationTemplate

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ["title", "priority", "audience", "is_draft", "view_count", "created_at"]
    list_filter = ["priority", "audience", "is_draft", "school"]
    search_fields = ["title", "content"]
    readonly_fields = ["view_count", "created_at"]

@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "recipient", "status", "sent_at"]
    list_filter = ["status"]
    search_fields = ["sender__email", "recipient__email"]
    readonly_fields = ["id", "sent_at", "delivered_at", "read_at"]

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "channel", "status", "created_at"]
    list_filter = ["channel", "status"]
    search_fields = ["user__email", "title"]

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "event_type", "school", "is_active"]
    list_filter = ["is_active", "school"]
