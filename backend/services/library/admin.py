"""
Library Service — Admin registration for all models.
"""

from django.contrib import admin

from .models import Book, Checkout, LibrarianProfile


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "isbn",
        "category",
        "total_copies",
        "available_copies",
        "school",
    ]
    list_filter = ["category", "school"]
    search_fields = ["title", "author", "isbn"]


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = [
        "book",
        "student",
        "checked_out_at",
        "due_date",
        "returned_at",
        "is_overdue",
    ]
    list_filter = ["due_date"]
    search_fields = [
        "student__user__first_name",
        "student__admission_number",
        "book__title",
    ]


@admin.register(LibrarianProfile)
class LibrarianProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "employee_id",
        "department",
        "is_active",
    ]
    list_filter = ["is_active", "department"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "employee_id",
    ]
