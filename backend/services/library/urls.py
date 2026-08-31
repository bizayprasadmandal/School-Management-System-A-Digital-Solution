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

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", views.LibrarianProfileView.as_view(), name="librarian_profile"),
]
