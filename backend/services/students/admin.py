from django.contrib import admin
from .models import Student, Guardian, StudentGuardian, Enrollment, Classroom, Grade, AcademicYear, Document

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "start_date", "end_date", "is_current"]
    list_filter = ["school", "is_current"]

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["name", "level", "school"]
    list_filter = ["school"]
    ordering = ["school", "level"]

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ["name", "grade", "capacity", "class_teacher", "academic_year"]
    list_filter = ["grade__school", "academic_year", "grade"]
    search_fields = ["name", "room_number"]

class StudentGuardianInline(admin.TabularInline):
    model = StudentGuardian
    extra = 1

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    readonly_fields = ["enrollment_date"]

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["admission_number", "full_name", "gender", "is_active", "admission_date"]
    list_filter = ["gender", "is_active", "school"]
    search_fields = ["admission_number", "user__first_name", "user__last_name", "user__email"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [StudentGuardianInline, EnrollmentInline]

    def full_name(self, obj): return obj.user.full_name
    full_name.short_description = "Full Name"

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "phone", "is_primary"]
    search_fields = ["first_name", "last_name", "email"]
