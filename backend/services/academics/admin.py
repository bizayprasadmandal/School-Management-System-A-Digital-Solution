from django.contrib import admin
from .models import Subject, TeacherAssignment, TeacherProfile, LessonPlan

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "grade", "is_core", "max_marks", "is_active"]
    list_filter = ["grade__school", "is_core", "is_active"]
    search_fields = ["name", "code"]

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "employee_id", "department", "qualification", "joining_date", "is_active"]
    list_filter = ["school", "qualification", "department", "is_active"]
    search_fields = ["employee_id", "user__first_name", "user__last_name", "user__email"]

    def full_name(self, obj): return obj.user.full_name

@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = ["teacher", "subject", "classroom", "academic_year", "is_primary"]
    list_filter = ["academic_year", "is_primary"]

@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = ["title", "topic", "date", "duration_minutes", "status"]
    list_filter = ["status", "date"]
    search_fields = ["title", "topic"]
