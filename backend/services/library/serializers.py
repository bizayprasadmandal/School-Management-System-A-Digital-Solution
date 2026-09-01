"""Serializers for library."""

from rest_framework import serializers

from .models import (
    AcquisitionRequest,
    BarcodeTracking,
    Book,
    BookCategory,
    BookClub,
    BookClubMembership,
    BookConditionLog,
    BookCopy,
    BookDonation,
    BookPurchase,
    BookRecommendation,
    BookRepair,
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
    LibraryCard,
    LibraryEvent,
    LibraryFeedback,
    LibraryNotification,
    ReadingChallenge,
    ReadingChallengeProgress,
    ReadingList,
    ReadingListItem,
    StudentReadingLog,
)


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id",
            "school",
            "on_delete",
            "title",
            "author",
            "isbn",
            "publisher",
            "category",
            "shelf_location",
            "total_copies",
            "available_copies",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        fields = [
            "id",
            "book",
            "on_delete",
            "student",
            "on_delete",
            "checked_out_by",
            "on_delete",
            "checked_out_at",
            "due_date",
            "returned_at",
            "fine_amount",
            "fine_paid",
            "notes",
        ]
        read_only_fields = ["id"]


class LibrarianProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibrarianProfile
        fields = [
            "id",
            "school",
            "id",
            "user",
            "on_delete",
            "on_delete",
            "library_section",
            "qualification",
            "experience_years",
            "certifications",
            "bio",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "parent_category",
            "on_delete",
            "dewey_code",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BookReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookReservation
        fields = [
            "id",
            "id",
            "book",
            "on_delete",
            "student",
            "on_delete",
            "status",
            "reserved_at",
            "expires_at",
            "notified",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReadingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingList
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "created_by",
            "on_delete",
            "grade",
            "on_delete",
            "subject",
            "on_delete",
            "status",
            "is_mandatory",
            "start_date",
            "end_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReadingListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingListItem
        fields = [
            "id",
            "id",
            "reading_list",
            "on_delete",
            "book",
            "on_delete",
            "order",
            "is_required",
            "notes",
            "added_at",
        ]
        read_only_fields = ["id"]


class DigitalResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalResource
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "title",
            "author",
            "resource_type",
            "description",
            "url",
            "file",
            "category",
            "on_delete",
            "isbn",
            "publisher",
            "publication_date",
            "duration_minutes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InventoryManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryManagement
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "audit_type",
            "status",
            "scheduled_date",
            "completed_date",
            "conducted_by",
            "on_delete",
            "total_books_expected",
            "total_books_found",
            "total_missing",
            "total_damaged",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InventoryAuditItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAuditItem
        fields = [
            "id",
            "id",
            "audit",
            "on_delete",
            "book",
            "on_delete",
            "expected_copies",
            "found_copies",
            "condition",
            "shelf_location",
            "notes",
            "checked_at",
        ]
        read_only_fields = ["id"]


class BarcodeTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BarcodeTracking
        fields = [
            "id",
            "id",
            "book",
            "on_delete",
            "tracking_type",
            "barcode_value",
            "status",
            "copy_number",
            "assigned_at",
            "last_scanned_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class FineManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FineManagement
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "checkout",
            "on_delete",
            "book",
            "on_delete",
            "fine_type",
            "amount",
            "amount_paid",
            "status",
            "days_overdue",
            "reason",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FinePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinePayment
        fields = [
            "id",
            "id",
            "fine",
            "on_delete",
            "amount",
            "payment_method",
            "received_by",
            "on_delete",
            "reference_number",
            "notes",
            "paid_at",
        ]
        read_only_fields = ["id"]


class LibraryAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryAnalytics
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
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
        ]
        read_only_fields = ["id"]


class LibraryEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryEvent
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
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
            "on_delete",
            "is_mandatory",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = [
            "id",
            "id",
            "event",
            "on_delete",
            "student",
            "on_delete",
            "status",
            "registered_at",
            "attended_at",
            "notes",
        ]
        read_only_fields = ["id"]


class BookReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookReview
        fields = [
            "id",
            "id",
            "book",
            "on_delete",
            "student",
            "on_delete",
            "rating",
            "title",
            "review_text",
            "is_anonymous",
            "is_approved",
            "helpful_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InterLibraryLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterLibraryLoan
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "requesting_student",
            "on_delete",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BookRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookRecommendation
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "book",
            "on_delete",
            "recommendation_type",
            "score",
            "reason",
            "is_dismissed",
            "is_read",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class LibraryNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryNotification
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "notification_type",
            "channel",
            "title",
            "message",
            "book",
            "on_delete",
            "checkout",
            "on_delete",
            "event",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]


class BookCopySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCopy
        fields = [
            "id",
            "school",
            "id",
            "book",
            "on_delete",
            "on_delete",
            "copy_number",
            "barcode",
            "condition",
            "location",
            "shelf_number",
            "is_available",
            "is_reference_only",
            "purchase_date",
            "purchase_price",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BookConditionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookConditionLog
        fields = [
            "id",
            "id",
            "book_copy",
            "on_delete",
            "previous_condition",
            "new_condition",
            "reason",
            "reported_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BookRepairSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookRepair
        fields = [
            "id",
            "school",
            "id",
            "book_copy",
            "on_delete",
            "on_delete",
            "issue",
            "description",
            "status",
            "cost",
            "vendor",
            "scheduled_date",
            "completed_date",
            "reported_by",
            "on_delete",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BookDonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookDonation
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "donor_name",
            "donor_email",
            "donor_phone",
            "book_title",
            "author",
            "isbn",
            "quantity",
            "condition",
            "status",
            "received_date",
            "received_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at"]


class BookPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookPurchase
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "book",
            "on_delete",
            "title",
            "author",
            "isbn",
            "quantity",
            "unit_price",
            "total_cost",
            "vendor",
            "order_date",
            "expected_date",
            "received_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LibraryCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryCard
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "card_number",
            "issue_date",
            "expiry_date",
            "status",
            "max_checkouts",
            "current_checkouts",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AcquisitionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcquisitionRequest
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "requested_by",
            "on_delete",
            "title",
            "author",
            "isbn",
            "publisher",
            "quantity",
            "estimated_cost",
            "reason",
            "priority",
            "status",
            "approved_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BookClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookClub
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "advisor",
            "on_delete",
            "meeting_day",
            "meeting_time",
            "meeting_location",
            "max_members",
            "current_book",
            "on_delete",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BookClubMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookClubMembership
        fields = [
            "id",
            "id",
            "book_club",
            "on_delete",
            "student",
            "on_delete",
            "role",
            "join_date",
            "end_date",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentReadingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentReadingLog
        fields = [
            "id",
            "school",
            "id",
            "student",
            "on_delete",
            "on_delete",
            "book",
            "on_delete",
            "book_title",
            "author",
            "pages_read",
            "total_pages",
            "start_date",
            "end_date",
            "rating",
            "review",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReadingChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingChallenge
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "description",
            "start_date",
            "end_date",
            "goal_books",
            "goal_pages",
            "status",
            "prize",
            "participants_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReadingChallengeProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingChallengeProgress
        fields = [
            "id",
            "id",
            "challenge",
            "on_delete",
            "student",
            "on_delete",
            "books_read",
            "pages_read",
            "is_completed",
            "completed_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LibraryFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryFeedback
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "student",
            "on_delete",
            "feedback_type",
            "rating",
            "comments",
            "suggestions",
            "is_anonymous",
            "response",
            "responded_by",
            "on_delete",
            "responded_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
