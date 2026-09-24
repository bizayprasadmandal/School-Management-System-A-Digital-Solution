from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db import models, transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
from .serializers import (
    AcquisitionRequestSerializer,
    BarcodeTrackingSerializer,
    BookCategorySerializer,
    BookClubMembershipSerializer,
    BookClubSerializer,
    BookConditionLogSerializer,
    BookCopySerializer,
    BookDonationSerializer,
    BookPurchaseSerializer,
    BookRecommendationSerializer,
    BookRepairSerializer,
    BookReservationSerializer,
    BookReviewSerializer,
    BookSerializer,
    CheckoutSerializer,
    DigitalResourceSerializer,
    EventRegistrationSerializer,
    FineManagementSerializer,
    FinePaymentSerializer,
    InterLibraryLoanSerializer,
    InventoryAuditItemSerializer,
    InventoryManagementSerializer,
    LibrarianProfileSerializer,
    LibraryAnalyticsSerializer,
    LibraryCardSerializer,
    LibraryEventSerializer,
    LibraryFeedbackSerializer,
    LibraryNotificationSerializer,
    ReadingChallengeProgressSerializer,
    ReadingChallengeSerializer,
    ReadingListItemSerializer,
    ReadingListSerializer,
    StudentReadingLogSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "is_active", "author"]
    search_fields = ["title", "author", "isbn"]
    ordering = ["title"]

    def get_queryset(self):
        return Book.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        # Newly added books are fully available immediately (available_copies is
        # stock-managed downstream by checkout/return flows).
        serializer.save(
            school=self.request.user.school,
            available_copies=serializer.validated_data.get("total_copies", 1),
        )


class LibrarianProfileView(generics.RetrieveUpdateAPIView):
    """Get/update the authenticated librarian's own profile."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            from .serializers import LibrarianSelfProfileSerializer

            return LibrarianSelfProfileSerializer
        from .serializers import LibrarianProfileSerializer

        return LibrarianProfileSerializer

    def get_object(self):
        from .models import LibrarianProfile

        profile, _ = LibrarianProfile.objects.get_or_create(
            user=self.request.user,
            school=self.request.user.school,
        )
        return profile


class CheckoutViewSet(viewsets.ModelViewSet):
    serializer_class = CheckoutSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["book", "student", "fine_paid"]
    search_fields = ["book__title", "student__user__first_name"]
    ordering = ["-checked_out_at"]

    def get_queryset(self):
        return Checkout.objects.filter(book__school=self.request.user.school).select_related(
            "book", "student__user", "checked_out_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    @transaction.atomic
    def perform_create(self, serializer):
        book = Book.objects.select_for_update().get(pk=serializer.validated_data["book"].id)
        if book.available_copies < 1:
            raise serializers.ValidationError({"detail": "No available copies of this book to check out."})
        checkout = serializer.save(checked_out_by=self.request.user, book=book)
        Book.objects.filter(id=checkout.book_id).update(available_copies=models.F("available_copies") - 1)

    @action(detail=True, methods=["post"], url_path="return")
    def return_book(self, request, pk=None):
        """Return a checked-out book, calculate overdue fine if any."""
        checkout = self.get_object()
        if checkout.returned_at:
            return Response({"detail": "Already returned."}, status=400)

        checkout.returned_at = timezone.now()
        overdue_days = (timezone.now().date() - checkout.due_date).days
        if overdue_days > 0:
            checkout.fine_amount = overdue_days * 0.50  # $0.50/day
        checkout.save()

        Book.objects.filter(id=checkout.book_id).update(available_copies=models.F("available_copies") + 1)
        return Response({"detail": "Book returned.", "fine": float(checkout.fine_amount)})

    @action(detail=True, methods=["post"])
    def pay_fine(self, request, pk=None):
        """Mark a fine as paid for a returned book."""
        checkout = self.get_object()
        checkout.fine_paid = True
        checkout.save(update_fields=["fine_paid"])
        return Response({"detail": "Fine paid."})


# =============================================================================
# Book Categories Views
# =============================================================================


class BookCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = BookCategorySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        return BookCategory.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Book Reservations Views
# =============================================================================


class BookReservationViewSet(viewsets.ModelViewSet):
    serializer_class = BookReservationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["school_admin", "super_admin", "librarian"]:
            return BookReservation.objects.filter(book__school=user.school)
        from services.students.models import Student

        student = Student.objects.filter(user=user).first()
        if student:
            return BookReservation.objects.filter(student=student)
        return BookReservation.objects.none()

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsSchoolMember()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_reservation(self, request, pk=None):
        reservation = self.get_object()
        reservation.status = BookReservation.Status.CANCELLED
        reservation.save(update_fields=["status"])
        return Response({"detail": "Reservation cancelled"})


# =============================================================================
# Reading Lists Views
# =============================================================================


class ReadingListViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user = self.request.user
        return ReadingList.objects.filter(school=user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class ReadingListItemViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingListItemSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        reading_list_id = self.request.query_params.get("reading_list_id")
        if reading_list_id:
            return ReadingListItem.objects.filter(reading_list_id=reading_list_id)
        return ReadingListItem.objects.filter(reading_list__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


# =============================================================================
# Digital Resources Views
# =============================================================================


class DigitalResourceViewSet(viewsets.ModelViewSet):
    serializer_class = DigitalResourceSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["resource_type", "language", "is_active"]
    search_fields = ["title", "author"]

    def get_queryset(self):
        return DigitalResource.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=True, methods=["post"], url_path="access")
    def access_resource(self, request, pk=None):
        resource = self.get_object()
        if not resource.is_available:
            return Response({"error": "Resource not available"}, status=400)
        resource.current_users += 1
        resource.access_count += 1
        resource.save(update_fields=["current_users", "access_count"])
        return Response({"detail": "Resource accessed"})

    @action(detail=True, methods=["post"], url_path="release")
    def release_resource(self, request, pk=None):
        resource = self.get_object()
        resource.current_users = max(0, resource.current_users - 1)
        resource.save(update_fields=["current_users"])
        return Response({"detail": "Resource released"})


# =============================================================================
# Inventory Management Views
# =============================================================================


class InventoryManagementViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryManagementSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        return InventoryManagement.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, conducted_by=self.request.user)


class InventoryAuditItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryAuditItemSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        audit_id = self.request.query_params.get("audit_id")
        if audit_id:
            return InventoryAuditItem.objects.filter(audit_id=audit_id)
        return InventoryAuditItem.objects.filter(audit__school=self.request.user.school)


# =============================================================================
# Barcode Tracking Views
# =============================================================================


class BarcodeTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = BarcodeTrackingSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        return BarcodeTracking.objects.filter(book__school=self.request.user.school)

    @action(detail=False, methods=["post"], url_path="scan")
    def scan_barcode(self, request):
        barcode_value = request.data.get("barcode_value")
        if not barcode_value:
            return Response({"error": "barcode_value is required"}, status=400)
        try:
            tracking = BarcodeTracking.objects.select_related("book").get(barcode_value=barcode_value)
        except BarcodeTracking.DoesNotExist:
            return Response({"error": "Barcode not found"}, status=404)
        tracking.last_scanned_at = timezone.now()
        tracking.save(update_fields=["last_scanned_at"])
        return Response(
            {
                "book_title": tracking.book.title,
                "book_author": tracking.book.author,
                "status": tracking.status,
                "available_copies": tracking.book.available_copies,
            }
        )


# =============================================================================
# Fine Management Views
# =============================================================================


class FineManagementViewSet(viewsets.ModelViewSet):
    serializer_class = FineManagementSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    def get_queryset(self):
        return FineManagement.objects.filter(school=self.request.user.school)

    @action(detail=True, methods=["post"], url_path="waive")
    def waive_fine(self, request, pk=None):
        fine = self.get_object()
        fine.status = FineManagement.Status.WAIVED
        fine.waived_by = request.user
        fine.waive_reason = request.data.get("reason", "")
        fine.save(update_fields=["status", "waived_by", "waive_reason"])
        return Response({"detail": "Fine waived"})


class FinePaymentViewSet(viewsets.ModelViewSet):
    serializer_class = FinePaymentSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        fine_id = self.request.query_params.get("fine_id")
        if fine_id:
            return FinePayment.objects.filter(fine_id=fine_id)
        return FinePayment.objects.filter(fine__school=self.request.user.school)

    def perform_create(self, serializer):
        payment = serializer.save(received_by=self.request.user)
        # Update fine amount_paid
        fine = payment.fine
        fine.amount_paid = sum(p.amount for p in fine.payments.all())
        if fine.amount_paid >= fine.amount:
            fine.status = FineManagement.Status.PAID
        else:
            fine.status = FineManagement.Status.PARTIAL
        fine.save(update_fields=["amount_paid", "status"])


# =============================================================================
# Library Analytics Views
# =============================================================================


class LibraryAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = LibraryAnalyticsSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        return LibraryAnalytics.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, generated_by=self.request.user)


# =============================================================================
# Library Events Views
# =============================================================================


class LibraryEventViewSet(viewsets.ModelViewSet):
    serializer_class = LibraryEventSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        return LibraryEvent.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, organizer=self.request.user)


class EventRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        event_id = self.request.query_params.get("event_id")
        if event_id:
            return EventRegistration.objects.filter(event_id=event_id)
        return EventRegistration.objects.filter(event__school=self.request.user.school)

    def perform_create(self, serializer):
        registration = serializer.save()
        # Increment participant count
        registration.event.current_participants += 1
        registration.event.save(update_fields=["current_participants"])


# =============================================================================
# Book Reviews Views
# =============================================================================


class BookReviewViewSet(viewsets.ModelViewSet):
    serializer_class = BookReviewSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        book_id = self.request.query_params.get("book_id")
        if book_id:
            return BookReview.objects.filter(book_id=book_id, is_approved=True)
        return BookReview.objects.filter(book__school=self.request.user.school, is_approved=True)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolMember()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        from services.students.models import Student

        student = Student.objects.filter(user=self.request.user).first()
        if not student:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Only students can create reviews")
        serializer.save(student=student)

    @action(detail=True, methods=["post"], url_path="helpful")
    def mark_helpful(self, request, pk=None):
        review = self.get_object()
        review.helpful_count += 1
        review.save(update_fields=["helpful_count"])
        return Response({"detail": "Marked as helpful"})


# =============================================================================
# Inter-Library Loans Views
# =============================================================================


class InterLibraryLoanViewSet(viewsets.ModelViewSet):
    serializer_class = InterLibraryLoanSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["school_admin", "super_admin", "librarian"]:
            return InterLibraryLoan.objects.filter(school=user.school)
        from services.students.models import Student

        student = Student.objects.filter(user=user).first()
        if student:
            return InterLibraryLoan.objects.filter(requesting_student=student)
        return InterLibraryLoan.objects.none()

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsSchoolMember()]
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        from services.students.models import Student

        student = Student.objects.filter(user=self.request.user).first()
        serializer.save(school=self.request.user.school, requesting_student=student)


# =============================================================================
# Book Recommendations Views
# =============================================================================


class BookRecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = BookRecommendationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user = self.request.user
        from services.students.models import Student

        student = Student.objects.filter(user=user).first()
        if student:
            return BookRecommendation.objects.filter(student=student, is_dismissed=False)
        # staff/admin view: every recommendation in the school — the admin
        # panel's Recommendations tab otherwise renders permanently empty
        return BookRecommendation.objects.filter(student__school=user.school, is_dismissed=False)

    @action(detail=True, methods=["post"], url_path="dismiss")
    def dismiss_recommendation(self, request, pk=None):
        recommendation = self.get_object()
        recommendation.is_dismissed = True
        recommendation.save(update_fields=["is_dismissed"])
        return Response({"detail": "Recommendation dismissed"})

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        recommendation = self.get_object()
        recommendation.is_read = True
        recommendation.save(update_fields=["is_read"])
        return Response({"detail": "Marked as read"})


# =============================================================================
# Library Notifications Views
# =============================================================================


class LibraryNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = LibraryNotificationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    def get_queryset(self):
        user = self.request.user
        if user.role in ["school_admin", "super_admin", "librarian"]:
            return LibraryNotification.objects.filter(school=user.school)
        from services.students.models import Student

        student = Student.objects.filter(user=user).first()
        if student:
            return LibraryNotification.objects.filter(student=student)
        return LibraryNotification.objects.none()

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=["is_read", "read_at"])
        return Response({"detail": "Marked as read"})

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        user = request.user
        from services.students.models import Student

        student = Student.objects.filter(user=user).first()
        if student:
            LibraryNotification.objects.filter(student=student, is_read=False).update(
                is_read=True, read_at=timezone.now()
            )
        return Response({"detail": "All notifications marked as read"})


# ── Additional ViewSets (module expansion) ──


class LibrarianProfileViewSet(viewsets.ModelViewSet):
    serializer_class = LibrarianProfileSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return LibrarianProfile.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BookCopyViewSet(viewsets.ModelViewSet):
    serializer_class = BookCopySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return BookCopy.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BookConditionLogViewSet(viewsets.ModelViewSet):
    serializer_class = BookConditionLogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return BookConditionLog.objects.filter(book_copy__book__school=self.request.user.school).select_related(
            "book_copy__book"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BookRepairViewSet(viewsets.ModelViewSet):
    serializer_class = BookRepairSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return BookRepair.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BookDonationViewSet(viewsets.ModelViewSet):
    serializer_class = BookDonationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return BookDonation.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BookPurchaseViewSet(viewsets.ModelViewSet):
    serializer_class = BookPurchaseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return BookPurchase.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class LibraryCardViewSet(viewsets.ModelViewSet):
    serializer_class = LibraryCardSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return LibraryCard.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AcquisitionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = AcquisitionRequestSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return AcquisitionRequest.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BookClubViewSet(viewsets.ModelViewSet):
    serializer_class = BookClubSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return BookClub.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BookClubMembershipViewSet(viewsets.ModelViewSet):
    serializer_class = BookClubMembershipSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return BookClubMembership.objects.filter(book_club__school=self.request.user.school).select_related("book_club")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class StudentReadingLogViewSet(viewsets.ModelViewSet):
    serializer_class = StudentReadingLogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return StudentReadingLog.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ReadingChallengeViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingChallengeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ReadingChallenge.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ReadingChallengeProgressViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingChallengeProgressSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ReadingChallengeProgress.objects.filter(challenge__school=self.request.user.school).select_related(
            "challenge"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class LibraryFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = LibraryFeedbackSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return LibraryFeedback.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
