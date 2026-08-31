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
    list_filter = ["category", "school", "is_active"]
    search_fields = ["title", "author", "isbn"]


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = [
        "book",
        "student",
        "checked_out_at",
        "due_date",
        "returned_at",
        "fine_amount",
    ]
    list_filter = ["fine_paid"]
    search_fields = [
        "student__user__first_name",
        "student__admission_number",
        "book__title",
    ]


@admin.register(LibrarianProfile)
class LibrarianProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "library_section",
        "qualification",
        "experience_years",
    ]
    list_filter = ["library_section"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "qualification",
    ]
