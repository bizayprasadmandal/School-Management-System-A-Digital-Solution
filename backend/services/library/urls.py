"""URL Configuration for library."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AcquisitionRequestViewSet,
    BarcodeTrackingViewSet,
    BookCategoryViewSet,
    BookClubMembershipViewSet,
    BookClubViewSet,
    BookConditionLogViewSet,
    BookCopyViewSet,
    BookDonationViewSet,
    BookPurchaseViewSet,
    BookRecommendationViewSet,
    BookRepairViewSet,
    BookReservationViewSet,
    BookReviewViewSet,
    BookViewSet,
    CheckoutViewSet,
    DigitalResourceViewSet,
    EventRegistrationViewSet,
    FineManagementViewSet,
    FinePaymentViewSet,
    InterLibraryLoanViewSet,
    InventoryAuditItemViewSet,
    InventoryManagementViewSet,
    LibrarianProfileViewSet,
    LibraryAnalyticsViewSet,
    LibraryCardViewSet,
    LibraryEventViewSet,
    LibraryFeedbackViewSet,
    LibraryNotificationViewSet,
    ReadingChallengeProgressViewSet,
    ReadingChallengeViewSet,
    ReadingListItemViewSet,
    ReadingListViewSet,
    StudentReadingLogViewSet,
)

app_name = "library_v1"

router = DefaultRouter()
router.register(r"book", BookViewSet, basename="book")
router.register(r"checkout", CheckoutViewSet, basename="checkout")
router.register(r"librarian-profile", LibrarianProfileViewSet, basename="librarian-profile")
router.register(r"book-category", BookCategoryViewSet, basename="book-category")
router.register(r"book-reservation", BookReservationViewSet, basename="book-reservation")
router.register(r"reading-list", ReadingListViewSet, basename="reading-list")
router.register(r"reading-list-item", ReadingListItemViewSet, basename="reading-list-item")
router.register(r"digital-resource", DigitalResourceViewSet, basename="digital-resource")
router.register(r"inventory-management", InventoryManagementViewSet, basename="inventory-management")
router.register(r"inventory-audit-item", InventoryAuditItemViewSet, basename="inventory-audit-item")
router.register(r"barcode-tracking", BarcodeTrackingViewSet, basename="barcode-tracking")
router.register(r"fine-management", FineManagementViewSet, basename="fine-management")
router.register(r"fine-payment", FinePaymentViewSet, basename="fine-payment")
router.register(r"library-analytics", LibraryAnalyticsViewSet, basename="library-analytics")
router.register(r"library-event", LibraryEventViewSet, basename="library-event")
router.register(r"event-registration", EventRegistrationViewSet, basename="event-registration")
router.register(r"book-review", BookReviewViewSet, basename="book-review")
router.register(r"inter-library-loan", InterLibraryLoanViewSet, basename="inter-library-loan")
router.register(r"book-recommendation", BookRecommendationViewSet, basename="book-recommendation")
router.register(r"library-notification", LibraryNotificationViewSet, basename="library-notification")
router.register(r"book-copy", BookCopyViewSet, basename="book-copy")
router.register(r"book-condition-log", BookConditionLogViewSet, basename="book-condition-log")
router.register(r"book-repair", BookRepairViewSet, basename="book-repair")
router.register(r"book-donation", BookDonationViewSet, basename="book-donation")
router.register(r"book-purchase", BookPurchaseViewSet, basename="book-purchase")
router.register(r"library-card", LibraryCardViewSet, basename="library-card")
router.register(r"acquisition-request", AcquisitionRequestViewSet, basename="acquisition-request")
router.register(r"book-club", BookClubViewSet, basename="book-club")
router.register(r"book-club-membership", BookClubMembershipViewSet, basename="book-club-membership")
router.register(r"student-reading-log", StudentReadingLogViewSet, basename="student-reading-log")
router.register(r"reading-challenge", ReadingChallengeViewSet, basename="reading-challenge")
router.register(r"reading-challenge-progress", ReadingChallengeProgressViewSet, basename="reading-challenge-progress")
router.register(r"library-feedback", LibraryFeedbackViewSet, basename="library-feedback")

urlpatterns = [
    path("", include(router.urls)),
]
