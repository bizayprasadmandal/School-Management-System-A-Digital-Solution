from django.contrib import admin
from .models import EnrollmentIntake, Application, ApplicationDocument, ApplicationReview

class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument; extra = 1; fields = ["document_type", "file_name", "is_verified"]

class ApplicationReviewInline(admin.TabularInline):
    model = ApplicationReview; extra = 1; fields = ["reviewer", "score", "recommendation"]

@admin.register(EnrollmentIntake)
class EnrollmentIntakeAdmin(admin.ModelAdmin):
    list_display = ["name", "academic_year", "application_start", "application_end", "status"]
    list_filter = ["status", "school"]; search_fields = ["name"]

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["application_number", "first_name", "last_name", "applying_for_grade", "status", "submitted_at"]
    list_filter = ["status", "applying_for_grade"]; search_fields = ["first_name", "last_name", "email", "application_number"]
    inlines = [ApplicationDocumentInline, ApplicationReviewInline]; readonly_fields = ["id", "created_at", "updated_at"]

@admin.register(ApplicationDocument)
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ["application", "document_type", "file_name", "is_verified", "uploaded_at"]
    list_filter = ["document_type", "is_verified"]; search_fields = ["file_name"]

@admin.register(ApplicationReview)
class ApplicationReviewAdmin(admin.ModelAdmin):
    list_display = ["application", "reviewer", "score", "recommendation", "created_at"]
    list_filter = ["recommendation"]; search_fields = ["application__application_number"]
