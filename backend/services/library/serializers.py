from rest_framework import serializers
from .models import Book, Checkout, LibrarianProfile


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class LibrarianProfileSerializer(serializers.ModelSerializer):
    """Full librarian profile — for admin view."""
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = LibrarianProfile
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class LibrarianSelfProfileSerializer(serializers.ModelSerializer):
    """Limited fields that librarians can edit themselves."""

    class Meta:
        model = LibrarianProfile
        fields = ["library_section", "qualification", "experience_years", "certifications", "bio"]


class CheckoutSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()

    class Meta:
        model = Checkout
        fields = "__all__"
        read_only_fields = ["id", "checked_out_at", "fine_amount", "fine_paid"]
