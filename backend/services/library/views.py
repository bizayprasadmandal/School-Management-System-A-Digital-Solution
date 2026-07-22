from django.db import transaction, models
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, Checkout
from .serializers import BookSerializer, CheckoutSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSchoolMember, IsSchoolAdmin
from core.pagination import StandardResultsSetPagination


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
        serializer.save(school=self.request.user.school)


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
        return Checkout.objects.filter(
            book__school=self.request.user.school
        ).select_related("book", "student__user", "checked_out_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    @transaction.atomic
    def perform_create(self, serializer):
        checkout = serializer.save(checked_out_by=self.request.user)
        Book.objects.filter(id=checkout.book_id).update(
            available_copies=models.F("available_copies") - 1
        )

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

        Book.objects.filter(id=checkout.book_id).update(
            available_copies=models.F("available_copies") + 1
        )
        return Response({"detail": "Book returned.", "fine": float(checkout.fine_amount)})

    @action(detail=True, methods=["post"])
    def pay_fine(self, request, pk=None):
        """Mark a fine as paid for a returned book."""
        checkout = self.get_object()
        checkout.fine_paid = True
        checkout.save(update_fields=["fine_paid"])
        return Response({"detail": "Fine paid."})
