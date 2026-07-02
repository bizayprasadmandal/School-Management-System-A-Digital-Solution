from django.contrib import admin
from .models import FeeCategory, FeeStructure, FeeInvoice, Payment, Scholarship

@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "recurrence", "is_mandatory"]
    list_filter = ["school", "recurrence", "is_mandatory"]

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ["fee_category", "grade", "amount", "due_day", "academic_year", "is_active"]
    list_filter = ["academic_year", "grade", "is_active"]

@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "student", "total_amount", "paid_amount", "status", "due_date"]
    list_filter = ["status", "academic_year"]
    search_fields = ["invoice_number", "student__user__first_name", "student__admission_number"]
    readonly_fields = ["id", "invoice_number", "created_at", "updated_at"]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["receipt_number", "invoice", "amount", "payment_method", "status", "paid_at"]
    list_filter = ["status", "payment_method"]
    search_fields = ["receipt_number"]
    readonly_fields = ["id", "receipt_number", "paid_at", "created_at"]

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ["name", "student", "discount_type", "discount_value", "is_active"]
    list_filter = ["discount_type", "is_active"]
