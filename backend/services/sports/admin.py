from django.contrib import admin
from .models import Sport, Team, TeamMember, SportEvent, SportAchievement

class TeamMemberInline(admin.TabularInline): model = TeamMember; extra = 1; fields = ["student", "role", "status"]

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "is_active"]; list_filter = ["category", "is_active", "school"]; search_fields = ["name"]

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "sport", "gender", "coach", "is_active"]; list_filter = ["gender", "is_active"]; search_fields = ["name"]; inlines = [TeamMemberInline]

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["student", "team", "role", "status"]; list_filter = ["role", "status"]; search_fields = ["student__user__full_name"]

@admin.register(SportEvent)
class SportEventAdmin(admin.ModelAdmin):
    list_display = ["title", "sport", "event_date", "status"]; list_filter = ["status"]; search_fields = ["title", "opponent"]

@admin.register(SportAchievement)
class SportAchievementAdmin(admin.ModelAdmin):
    list_display = ["title", "student", "position", "level", "awarded_date"]; list_filter = ["level"]; search_fields = ["title"]
