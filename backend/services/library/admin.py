from django.contrib import admin
from .models import Book, Checkout


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "isbn", "category", "total_copies", "available_copies", "school"]
    list_filter = ["category"]
    search_fields = ["title", "author", "isbn"]


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    list_display = ["book", "student", "checked_out_at", "due_date", "returned_at", "is_overdue"]
    list_filter = ["due_date"]
