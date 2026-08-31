from rest_framework import serializers

from .models import (
    BarcodeTracking,
    Book,
    BookCategory,
    BookRecommendation,
    BookReservation,
    BookReview,
    Checkout,
    DigitalResource,
    EventRegistration,
    FineManagement,
    FinePayment,
    InterLibraryLoan,
    InventoryAuditItem,
    InventoryManagement,
    LibrarianProfile,
    LibraryAnalytics,
    LibraryEvent,
    LibraryNotification,
    ReadingList,
    ReadingListItem,
)


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ["id", "school", "created_at"]

    def create(self, validated_data):
        # New books start fully available.
        total = validated_data.get("total_copies", validated_data.get("available_copies", 1))
        validated_data.setdefault("available_copies", total)
        return super().create(validated_data)


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
        read_only_fields = ["id", "checked_out_by", "checked_out_at", "fine_amount", "fine_paid"]

    def validate_book(self, value):
        # Checkouts must stay within the tenant — the book has to belong to the
        # same school as the librarian.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Book not found in your school.")
        return value

    def validate_student(self, value):
        # Checkouts must stay within the tenant — the student has to belong to
        # the same school as the librarian.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value

    def validate(self, attrs):
        book = attrs.get("book")
        if book and book.available_copies <= 0:
            raise serializers.ValidationError("No copies of this book are currently available.")
        return attrs


# =============================================================================
# Book Categories Serializers
# =============================================================================


class BookCategorySerializer(serializers.ModelSerializer):
    subcategories_count = serializers.SerializerMethodField()

    class Meta:
        model = BookCategory
        fields = [
            "id",
            "name",
            "description",
            "parent_category",
            "dewey_code",
            "is_active",
            "created_at",
            "subcategories_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_subcategories_count(self, obj):
        return obj.subcategories.count()


# =============================================================================
# Book Reservations Serializers
# =============================================================================


class BookReservationSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    is_expired = serializers.ReadOnlyField()

    class Meta:
        model = BookReservation
        fields = [
            "id",
            "book",
            "book_title",
            "student",
            "student_name",
            "status",
            "reserved_at",
            "expires_at",
            "notified",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "reserved_at", "created_at"]


# =============================================================================
# Reading Lists Serializers
# =============================================================================


class ReadingListItemSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_author = serializers.CharField(source="book.author", read_only=True)

    class Meta:
        model = ReadingListItem
        fields = [
            "id",
            "reading_list",
            "book",
            "book_title",
            "book_author",
            "order",
            "is_required",
            "notes",
            "added_at",
        ]
        read_only_fields = ["id", "added_at"]


class ReadingListSerializer(serializers.ModelSerializer):
    items = ReadingListItemSerializer(many=True, read_only=True)
    book_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = ReadingList
        fields = [
            "id",
            "name",
            "description",
            "created_by",
            "created_by_name",
            "grade",
            "subject",
            "status",
            "is_mandatory",
            "start_date",
            "end_date",
            "book_count",
            "items",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_book_count(self, obj):
        return obj.book_count


# =============================================================================
# Digital Resources Serializers
# =============================================================================


class DigitalResourceSerializer(serializers.ModelSerializer):
    is_available = serializers.ReadOnlyField()
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)

    class Meta:
        model = DigitalResource
        fields = [
            "id",
            "title",
            "author",
            "resource_type",
            "description",
            "url",
            "category",
            "category_name",
            "isbn",
            "publisher",
            "publication_date",
            "duration_minutes",
            "page_count",
            "file_size_mb",
            "language",
            "max_concurrent_users",
            "current_users",
            "is_available",
            "access_count",
            "created_at",
        ]
        read_only_fields = ["id", "access_count", "created_at"]


# =============================================================================
# Inventory Management Serializers
# =============================================================================


class InventoryAuditItemSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    discrepancy = serializers.ReadOnlyField()

    class Meta:
        model = InventoryAuditItem
        fields = [
            "id",
            "audit",
            "book",
            "book_title",
            "expected_copies",
            "found_copies",
            "condition",
            "shelf_location",
            "notes",
            "discrepancy",
            "checked_at",
        ]
        read_only_fields = ["id", "checked_at"]


class InventoryManagementSerializer(serializers.ModelSerializer):
    items = InventoryAuditItemSerializer(many=True, read_only=True)
    accuracy_percentage = serializers.ReadOnlyField()
    conducted_by_name = serializers.CharField(source="conducted_by.full_name", read_only=True, default=None)

    class Meta:
        model = InventoryManagement
        fields = [
            "id",
            "name",
            "audit_type",
            "status",
            "scheduled_date",
            "completed_date",
            "conducted_by",
            "conducted_by_name",
            "total_books_expected",
            "total_books_found",
            "total_missing",
            "total_damaged",
            "accuracy_percentage",
            "notes",
            "items",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Barcode Tracking Serializers
# =============================================================================


class BarcodeTrackingSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = BarcodeTracking
        fields = [
            "id",
            "book",
            "book_title",
            "tracking_type",
            "barcode_value",
            "status",
            "copy_number",
            "assigned_at",
            "last_scanned_at",
            "created_at",
        ]
        read_only_fields = ["id", "assigned_at", "created_at"]


# =============================================================================
# Fine Management Serializers
# =============================================================================


class FinePaymentSerializer(serializers.ModelSerializer):
    received_by_name = serializers.CharField(source="received_by.full_name", read_only=True, default=None)

    class Meta:
        model = FinePayment
        fields = [
            "id",
            "fine",
            "amount",
            "payment_method",
            "received_by",
            "received_by_name",
            "reference_number",
            "notes",
            "paid_at",
        ]
        read_only_fields = ["id", "paid_at"]


class FineManagementSerializer(serializers.ModelSerializer):
    outstanding_amount = serializers.ReadOnlyField()
    payments = FinePaymentSerializer(many=True, read_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = FineManagement
        fields = [
            "id",
            "student",
            "student_name",
            "book",
            "book_title",
            "fine_type",
            "amount",
            "amount_paid",
            "status",
            "days_overdue",
            "reason",
            "issued_by",
            "waived_by",
            "waive_reason",
            "outstanding_amount",
            "payments",
            "issued_at",
            "due_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Library Analytics Serializers
# =============================================================================


class LibraryAnalyticsSerializer(serializers.ModelSerializer):
    turnover_rate = serializers.ReadOnlyField()
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default=None)

    class Meta:
        model = LibraryAnalytics
        fields = [
            "id",
            "report_type",
            "period_start",
            "period_end",
            "total_checkouts",
            "total_returns",
            "total_renewals",
            "total_reservations",
            "total_books",
            "new_books_added",
            "books_lost",
            "books_damaged",
            "active_users",
            "new_users",
            "popular_books",
            "total_fines",
            "fines_collected",
            "digital_resource_access",
            "turnover_rate",
            "generated_by",
            "generated_by_name",
            "generated_at",
            "report_data",
        ]
        read_only_fields = ["id", "generated_at"]


# =============================================================================
# Library Events Serializers
# =============================================================================


class EventRegistrationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = EventRegistration
        fields = ["id", "event", "student", "student_name", "status", "registered_at", "attended_at", "notes"]
        read_only_fields = ["id", "registered_at"]


class LibraryEventSerializer(serializers.ModelSerializer):
    registrations = EventRegistrationSerializer(many=True, read_only=True)
    organizer_name = serializers.CharField(source="organizer.full_name", read_only=True, default=None)
    is_full = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()

    class Meta:
        model = LibraryEvent
        fields = [
            "id",
            "name",
            "description",
            "event_type",
            "status",
            "location",
            "start_date",
            "end_date",
            "max_participants",
            "current_participants",
            "organizer",
            "organizer_name",
            "is_mandatory",
            "grade",
            "is_full",
            "available_spots",
            "registrations",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Book Reviews Serializers
# =============================================================================


class BookReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = BookReview
        fields = [
            "id",
            "book",
            "book_title",
            "student",
            "student_name",
            "rating",
            "title",
            "review_text",
            "is_anonymous",
            "is_approved",
            "helpful_count",
            "created_at",
        ]
        read_only_fields = ["id", "helpful_count", "created_at"]


# =============================================================================
# Inter-Library Loans Serializers
# =============================================================================


class InterLibraryLoanSerializer(serializers.ModelSerializer):
    requesting_student_name = serializers.CharField(source="requesting_student.user.full_name", read_only=True)
    processed_by_name = serializers.CharField(source="processed_by.full_name", read_only=True, default=None)

    class Meta:
        model = InterLibraryLoan
        fields = [
            "id",
            "requesting_student",
            "requesting_student_name",
            "book_title",
            "book_author",
            "isbn",
            "lending_library",
            "lending_library_contact",
            "status",
            "requested_date",
            "expected_arrival",
            "actual_arrival",
            "due_date",
            "returned_date",
            "notes",
            "processed_by",
            "processed_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Book Recommendations Serializers
# =============================================================================


class BookRecommendationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_author = serializers.CharField(source="book.author", read_only=True)

    class Meta:
        model = BookRecommendation
        fields = [
            "id",
            "student",
            "student_name",
            "book",
            "book_title",
            "book_author",
            "recommendation_type",
            "score",
            "reason",
            "is_dismissed",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Library Notifications Serializers
# =============================================================================


class LibraryNotificationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True, default=None)

    class Meta:
        model = LibraryNotification
        fields = [
            "id",
            "student",
            "student_name",
            "notification_type",
            "channel",
            "title",
            "message",
            "book",
            "book_title",
            "checkout",
            "event",
            "is_read",
            "sent_at",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
