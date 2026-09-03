from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "library_v1"
router = DefaultRouter()

# Core library endpoints
router.register("books", views.BookViewSet, basename="book")
router.register("checkouts", views.CheckoutViewSet, basename="checkout")

# Book categories
router.register("categories", views.BookCategoryViewSet, basename="book-category")

# Book reservations
router.register("reservations", views.BookReservationViewSet, basename="book-reservation")

# Reading lists
router.register("reading-lists", views.ReadingListViewSet, basename="reading-list")
router.register("reading-list-items", views.ReadingListItemViewSet, basename="reading-list-item")

# Digital resources
router.register("digital-resources", views.DigitalResourceViewSet, basename="digital-resource")

# Inventory management
router.register("inventory-audits", views.InventoryManagementViewSet, basename="inventory-audit")
router.register("inventory-items", views.InventoryAuditItemViewSet, basename="inventory-item")

# Barcode tracking
router.register("barcodes", views.BarcodeTrackingViewSet, basename="barcode-tracking")

# Fine management
router.register("fines", views.FineManagementViewSet, basename="fine-management")
router.register("fine-payments", views.FinePaymentViewSet, basename="fine-payment")

# Library analytics
router.register("analytics", views.LibraryAnalyticsViewSet, basename="library-analytics")

# Library events
router.register("events", views.LibraryEventViewSet, basename="library-event")
router.register("event-registrations", views.EventRegistrationViewSet, basename="event-registration")

# Book reviews
router.register("reviews", views.BookReviewViewSet, basename="book-review")

# Inter-library loans
router.register("inter-library-loans", views.InterLibraryLoanViewSet, basename="inter-library-loan")

# Book recommendations
router.register("recommendations", views.BookRecommendationViewSet, basename="book-recommendation")

# Library notifications
router.register("notifications", views.LibraryNotificationViewSet, basename="library-notification")


# ── Additional registrations (module expansion) ──
router.register(r"librarian-profile", views.LibrarianProfileViewSet, basename="librarian-profile")
router.register(r"book-copy", views.BookCopyViewSet, basename="book-copy")
router.register(r"book-condition-log", views.BookConditionLogViewSet, basename="book-condition-log")
router.register(r"book-repair", views.BookRepairViewSet, basename="book-repair")
router.register(r"book-donation", views.BookDonationViewSet, basename="book-donation")
router.register(r"book-purchase", views.BookPurchaseViewSet, basename="book-purchase")
router.register(r"library-card", views.LibraryCardViewSet, basename="library-card")
router.register(r"acquisition-request", views.AcquisitionRequestViewSet, basename="acquisition-request")
router.register(r"book-club", views.BookClubViewSet, basename="book-club")
router.register(r"book-club-membership", views.BookClubMembershipViewSet, basename="book-club-membership")
router.register(r"student-reading-log", views.StudentReadingLogViewSet, basename="student-reading-log")
router.register(r"reading-challenge", views.ReadingChallengeViewSet, basename="reading-challenge")
router.register(
    r"reading-challenge-progress", views.ReadingChallengeProgressViewSet, basename="reading-challenge-progress"
)
router.register(r"library-feedback", views.LibraryFeedbackViewSet, basename="library-feedback")

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", views.LibrarianProfileView.as_view(), name="librarian_profile"),
]
