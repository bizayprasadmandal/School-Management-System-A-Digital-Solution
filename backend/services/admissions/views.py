"""Admissions — School-scoped viewsets."""

import logging

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Application, ApplicationDocument, ApplicationReview, EnrollmentIntake
from .serializers import (
    ApplicationDocumentSerializer,
    ApplicationListSerializer,
    ApplicationReviewSerializer,
    ApplicationSerializer,
    EnrollmentIntakeSerializer,
)

logger = logging.getLogger(__name__)


class EnrollmentIntakeViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentIntakeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "academic_year"]
    filterset_fields = ["status"]

    def get_queryset(self):
        return EnrollmentIntake.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ApplicationViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "email", "application_number", "phone"]
    filterset_fields = ["intake", "status", "applying_for_grade"]
    ordering_fields = ["created_at", "last_name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ApplicationListSerializer
        return ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(school=self.request.user.school).select_related("intake")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "update_status"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        import uuid

        from django.utils import timezone as dj_timezone

        # application_number is NOT NULL and unique — generate it up front
        # (before the INSERT) so a missing value can't raise IntegrityError.
        application_number = f"APP-{dj_timezone.localdate():%Y%m}-{str(uuid.uuid4())[:6].upper()}"
        serializer.save(school=self.request.user.school, application_number=application_number)

    @action(detail=True, methods=["post"], url_path="submit")
    def submit(self, request, pk=None):
        """Submit an application for review."""
        app = self.get_object()
        if app.status != Application.Status.DRAFT:
            return Response({"detail": "Only draft applications can be submitted."}, status=400)
        from django.utils import timezone

        app.status = Application.Status.SUBMITTED
        app.submitted_at = timezone.now()
        app.save(update_fields=["status", "submitted_at"])
        return Response(ApplicationSerializer(app).data)

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        """Admin action to change application status."""
        app = self.get_object()
        new_status = request.data.get("status")
        if new_status not in [s.value for s in Application.Status]:
            return Response({"detail": "Invalid status."}, status=400)
        app.status = new_status
        app.reviewed_by = request.user
        app.review_notes = request.data.get("review_notes", app.review_notes)
        app.save(update_fields=["status", "reviewed_by", "review_notes"])
        return Response(ApplicationSerializer(app).data)


class ApplicationDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationDocumentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["application", "document_type", "is_verified"]

    def get_queryset(self):
        return ApplicationDocument.objects.filter(application__school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save()


class ApplicationReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationReviewSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["application", "reviewer"]

    def get_queryset(self):
        return ApplicationReview.objects.filter(application__school=self.request.user.school).select_related("reviewer")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
