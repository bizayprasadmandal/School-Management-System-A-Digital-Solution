from django.contrib import admin

from .models import (
    AcademicYear,
    Classroom,
    Enrollment,
    Grade,
    Guardian,
    SiblingTracking,
    Student,
    StudentArchive,
    StudentCategory,
    StudentCategoryMembership,
    StudentContact,
    StudentCustomField,
    StudentCustomFieldValue,
    StudentGuardian,
    StudentIDCard,
    StudentMedicalRecord,
    StudentNote,
    StudentPhoto,
    StudentPortfolio,
    StudentSocialMedia,
    StudentStatusHistory,
    StudentTag,
    StudentTagAssignment,
    StudentWellness,
)


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

    def full_name(self, obj):
        return obj.user.full_name

    full_name.short_description = "Full Name"


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "phone", "is_primary"]
    search_fields = ["first_name", "last_name", "email"]


@admin.register(StudentContact)
class StudentContactAdmin(admin.ModelAdmin):
    list_display = ["student", "personal_phone", "personal_email", "created_at"]
    search_fields = ["student__user__full_name", "personal_email"]


@admin.register(StudentMedicalRecord)
class StudentMedicalRecordAdmin(admin.ModelAdmin):
    list_display = ["student", "record_type", "title", "severity", "is_ongoing"]
    list_filter = ["record_type", "severity", "is_ongoing"]
    search_fields = ["student__user__full_name", "title"]


@admin.register(StudentCustomField)
class StudentCustomFieldAdmin(admin.ModelAdmin):
    list_display = ["name", "field_type", "is_required", "is_active"]
    list_filter = ["field_type", "is_active"]


@admin.register(StudentCustomFieldValue)
class StudentCustomFieldValueAdmin(admin.ModelAdmin):
    list_display = ["student", "field", "text_value", "created_at"]
    search_fields = ["student__user__full_name", "field__name"]


@admin.register(StudentPhoto)
class StudentPhotoAdmin(admin.ModelAdmin):
    list_display = ["student", "photo_type", "taken_date", "is_primary"]
    list_filter = ["photo_type", "is_primary"]
    search_fields = ["student__user__full_name"]


@admin.register(StudentIDCard)
class StudentIDCardAdmin(admin.ModelAdmin):
    list_display = ["student", "card_number", "status", "issue_date", "expiry_date"]
    list_filter = ["status"]
    search_fields = ["student__user__full_name", "card_number"]


@admin.register(StudentStatusHistory)
class StudentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["student", "status", "previous_status", "effective_date"]
    list_filter = ["status"]
    search_fields = ["student__user__full_name"]


@admin.register(SiblingTracking)
class SiblingTrackingAdmin(admin.ModelAdmin):
    list_display = ["student", "sibling", "relationship"]
    list_filter = ["relationship"]


@admin.register(StudentCategory)
class StudentCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "student_count", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(StudentCategoryMembership)
class StudentCategoryMembershipAdmin(admin.ModelAdmin):
    list_display = ["student", "category", "start_date", "is_active"]
    list_filter = ["is_active"]


@admin.register(StudentTag)
class StudentTagAdmin(admin.ModelAdmin):
    list_display = ["name", "color", "usage_count", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(StudentTagAssignment)
class StudentTagAssignmentAdmin(admin.ModelAdmin):
    list_display = ["student", "tag", "assigned_by"]


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ["student", "note_type", "title", "author", "is_confidential"]
    list_filter = ["note_type", "is_confidential"]
    search_fields = ["student__user__full_name", "title"]


@admin.register(StudentArchive)
class StudentArchiveAdmin(admin.ModelAdmin):
    list_display = ["student", "academic_year", "grade", "status", "final_grade"]
    list_filter = ["status", "academic_year"]


@admin.register(StudentSocialMedia)
class StudentSocialMediaAdmin(admin.ModelAdmin):
    list_display = ["student", "platform", "username", "is_active"]
    list_filter = ["platform", "is_active"]


@admin.register(StudentPortfolio)
class StudentPortfolioAdmin(admin.ModelAdmin):
    list_display = ["student", "portfolio_type", "title", "date_completed"]
    list_filter = ["portfolio_type"]
    search_fields = ["student__user__full_name", "title"]


@admin.register(StudentWellness)
class StudentWellnessAdmin(admin.ModelAdmin):
    list_display = ["student", "wellness_type", "status", "mood_score", "follow_up_required"]
    list_filter = ["wellness_type", "status", "follow_up_required"]
    search_fields = ["student__user__full_name"]
