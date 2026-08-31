"""
Library Service — Admin registration for all models.
"""

from django.contrib import admin

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


# =============================================================================
# Book Categories
# =============================================================================


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "dewey_code", "parent_category", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "dewey_code"]


# =============================================================================
# Book Reservations
# =============================================================================


@admin.register(BookReservation)
class BookReservationAdmin(admin.ModelAdmin):
    list_display = ["book", "student", "status", "reserved_at", "expires_at", "notified"]
    list_filter = ["status", "notified"]
    search_fields = ["student__admission_number", "book__title"]
    date_hierarchy = "reserved_at"


# =============================================================================
# Reading Lists
# =============================================================================


class ReadingListItemInline(admin.TabularInline):
    model = ReadingListItem
    extra = 0


@admin.register(ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by", "grade", "status", "is_mandatory", "created_at"]
    list_filter = ["status", "is_mandatory"]
    search_fields = ["name", "description"]
    inlines = [ReadingListItemInline]


@admin.register(ReadingListItem)
class ReadingListItemAdmin(admin.ModelAdmin):
    list_display = ["reading_list", "book", "order", "is_required"]
    list_filter = ["is_required"]
    search_fields = ["book__title"]


# =============================================================================
# Digital Resources
# =============================================================================


@admin.register(DigitalResource)
class DigitalResourceAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "resource_type", "language", "access_count", "is_active"]
    list_filter = ["resource_type", "language", "is_active"]
    search_fields = ["title", "author", "isbn"]


# =============================================================================
# Inventory Management
# =============================================================================


class InventoryAuditItemInline(admin.TabularInline):
    model = InventoryAuditItem
    extra = 0


@admin.register(InventoryManagement)
class InventoryManagementAdmin(admin.ModelAdmin):
    list_display = ["name", "audit_type", "status", "scheduled_date", "completed_date", "accuracy_percentage"]
    list_filter = ["audit_type", "status"]
    search_fields = ["name", "notes"]
    date_hierarchy = "scheduled_date"
    inlines = [InventoryAuditItemInline]


@admin.register(InventoryAuditItem)
class InventoryAuditItemAdmin(admin.ModelAdmin):
    list_display = ["audit", "book", "expected_copies", "found_copies", "condition", "discrepancy"]
    list_filter = ["condition"]
    search_fields = ["book__title"]


# =============================================================================
# Barcode Tracking
# =============================================================================


@admin.register(BarcodeTracking)
class BarcodeTrackingAdmin(admin.ModelAdmin):
    list_display = ["barcode_value", "book", "tracking_type", "status", "copy_number", "last_scanned_at"]
    list_filter = ["tracking_type", "status"]
    search_fields = ["barcode_value", "book__title"]


# =============================================================================
# Fine Management
# =============================================================================


class FinePaymentInline(admin.TabularInline):
    model = FinePayment
    extra = 0


@admin.register(FineManagement)
class FineManagementAdmin(admin.ModelAdmin):
    list_display = ["student", "book", "fine_type", "amount", "amount_paid", "status", "issued_at"]
    list_filter = ["fine_type", "status"]
    search_fields = ["student__admission_number", "book__title"]
    date_hierarchy = "issued_at"
    inlines = [FinePaymentInline]


@admin.register(FinePayment)
class FinePaymentAdmin(admin.ModelAdmin):
    list_display = ["fine", "amount", "payment_method", "received_by", "paid_at"]
    list_filter = ["payment_method"]
    date_hierarchy = "paid_at"


# =============================================================================
# Library Analytics
# =============================================================================


@admin.register(LibraryAnalytics)
class LibraryAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["report_type", "period_start", "period_end", "total_checkouts", "active_users", "generated_at"]
    list_filter = ["report_type"]
    date_hierarchy = "period_start"


# =============================================================================
# Library Events
# =============================================================================


class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0


@admin.register(LibraryEvent)
class LibraryEventAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "event_type",
        "status",
        "start_date",
        "end_date",
        "current_participants",
        "max_participants",
    ]
    list_filter = ["event_type", "status"]
    search_fields = ["name", "description"]
    date_hierarchy = "start_date"
    inlines = [EventRegistrationInline]


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ["event", "student", "status", "registered_at", "attended_at"]
    list_filter = ["status"]
    search_fields = ["student__admission_number", "event__name"]


# =============================================================================
# Book Reviews
# =============================================================================


@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ["book", "student", "rating", "title", "is_approved", "helpful_count", "created_at"]
    list_filter = ["rating", "is_approved"]
    search_fields = ["book__title", "student__admission_number"]
    date_hierarchy = "created_at"


# =============================================================================
# Inter-Library Loans
# =============================================================================


@admin.register(InterLibraryLoan)
class InterLibraryLoanAdmin(admin.ModelAdmin):
    list_display = ["book_title", "requesting_student", "lending_library", "status", "requested_date", "due_date"]
    list_filter = ["status"]
    search_fields = ["book_title", "requesting_student__admission_number", "lending_library"]
    date_hierarchy = "requested_date"


# =============================================================================
# Book Recommendations
# =============================================================================


@admin.register(BookRecommendation)
class BookRecommendationAdmin(admin.ModelAdmin):
    list_display = ["student", "book", "recommendation_type", "score", "is_dismissed", "created_at"]
    list_filter = ["recommendation_type", "is_dismissed"]
    search_fields = ["student__admission_number", "book__title"]
    date_hierarchy = "created_at"


# =============================================================================
# Library Notifications
# =============================================================================


@admin.register(LibraryNotification)
class LibraryNotificationAdmin(admin.ModelAdmin):
    list_display = ["student", "notification_type", "channel", "title", "is_read", "created_at"]
    list_filter = ["notification_type", "channel", "is_read"]
    search_fields = ["student__admission_number", "title"]
    date_hierarchy = "created_at"
