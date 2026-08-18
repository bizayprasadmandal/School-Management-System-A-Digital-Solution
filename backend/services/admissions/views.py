"""Admissions — School-scoped viewsets."""

import logging

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Application, ApplicationDocument, ApplicationReview, ApplicationTimelineEvent, EnrollmentIntake
from .serializers import (
    ApplicationDocumentSerializer,
    ApplicationListSerializer,
    ApplicationReviewSerializer,
    ApplicationSerializer,
    EnrollmentIntakeSerializer,
)


def _log_timeline(application, stage, request, note=""):
    """Append an immutable stage event to an application's pipeline timeline."""
    ApplicationTimelineEvent.objects.create(
        application=application,
        stage=stage,
        note=note,
        created_by=request.user,
    )


logger = logging.getLogger(__name__)


class EnrollmentIntakeViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentIntakeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "academic_year"]
    filterset_fields = ["status"]

    def get_queryset(self):
        return EnrollmentIntake.objects.filter(school=self.request.user.school).annotate(
            application_count=Count("applications")
        )

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
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "update_status",
            "schedule_tour",
            "complete_tour",
            "send_offer",
            "accept_offer",
            "enroll",
        ]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        import uuid

        from django.utils import timezone as dj_timezone

        # application_number is NOT NULL and unique — generate it up front
        # (before the INSERT) so a missing value can't raise IntegrityError.
        application_number = f"APP-{dj_timezone.localdate():%Y%m}-{str(uuid.uuid4())[:6].upper()}"
        app = serializer.save(school=self.request.user.school, application_number=application_number)
        _log_timeline(app, ApplicationTimelineEvent.Stage.CREATED, self.request)

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
        _log_timeline(app, ApplicationTimelineEvent.Stage.SUBMITTED, request)
        return Response(ApplicationSerializer(app).data)

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        """Admin action to change application status."""
        app = self.get_object()
        new_status = request.data.get("status")
        if new_status not in [s.value for s in Application.Status]:
            return Response({"detail": "Invalid status."}, status=400)
        old_status = app.status
        app.status = new_status
        app.reviewed_by = request.user
        app.review_notes = request.data.get("review_notes", app.review_notes)
        app.save(update_fields=["status", "reviewed_by", "review_notes"])
        _log_timeline(
            app,
            ApplicationTimelineEvent.Stage.STATUS_CHANGED,
            request,
            note=f"{old_status} → {new_status}",
        )
        return Response(ApplicationSerializer(app).data)

    @action(detail=True, methods=["post"], url_path="schedule-tour")
    def schedule_tour(self, request, pk=None):
        """Schedule a campus tour for this applicant."""
        app = self.get_object()
        if app.status == Application.Status.ENROLLED:
            return Response({"detail": "Already enrolled."}, status=400)
        tour_date = request.data.get("tour_date")
        if not tour_date:
            return Response({"detail": "tour_date is required."}, status=400)
        app.tour_date = tour_date
        app.toured_at = None
        app.save(update_fields=["tour_date", "toured_at"])
        note = request.data.get("note", "")
        _log_timeline(app, ApplicationTimelineEvent.Stage.TOUR_SCHEDULED, request, note=note)
        return Response(ApplicationSerializer(app).data)

    @action(detail=True, methods=["post"], url_path="complete-tour")
    def complete_tour(self, request, pk=None):
        """Mark the applicant's campus tour as completed."""
        from django.utils import timezone

        app = self.get_object()
        if not app.tour_date:
            return Response({"detail": "No tour scheduled for this application."}, status=400)
        app.toured_at = timezone.now()
        app.save(update_fields=["toured_at"])
        _log_timeline(
            app,
            ApplicationTimelineEvent.Stage.TOUR_COMPLETED,
            request,
            note=request.data.get("note", ""),
        )
        return Response(ApplicationSerializer(app).data)

    @action(detail=True, methods=["post"], url_path="send-offer")
    def send_offer(self, request, pk=None):
        """Extend an admission offer — requires shortlisted or accepted status."""
        from django.utils import timezone

        app = self.get_object()
        if app.status not in [
            Application.Status.SHORTLISTED,
            Application.Status.ACCEPTED,
            Application.Status.WAITLISTED,
        ]:
            return Response(
                {"detail": "Offer can only be sent for shortlisted, accepted or waitlisted applications."},
                status=400,
            )
        app.status = Application.Status.ACCEPTED
        app.offer_sent_at = timezone.now()
        app.save(update_fields=["status", "offer_sent_at"])
        _log_timeline(
            app,
            ApplicationTimelineEvent.Stage.OFFER_SENT,
            request,
            note=request.data.get("note", ""),
        )
        return Response(ApplicationSerializer(app).data)

    @action(detail=True, methods=["post"], url_path="accept-offer")
    def accept_offer(self, request, pk=None):
        """Record the family's acceptance of the offer."""
        from django.utils import timezone

        app = self.get_object()
        if not app.offer_sent_at:
            return Response({"detail": "No offer has been sent yet."}, status=400)
        app.offer_accepted_at = timezone.now()
        app.save(update_fields=["offer_accepted_at"])
        _log_timeline(
            app,
            ApplicationTimelineEvent.Stage.OFFER_ACCEPTED,
            request,
            note=request.data.get("note", ""),
        )
        return Response(ApplicationSerializer(app).data)

    @action(detail=True, methods=["post"], url_path="enroll")
    def enroll(self, request, pk=None):
        """Convert an accepted application into a student + enrollment.

        Creates the User + Student profile + active Enrollment in the current
        academic year, links it back to the application and marks it enrolled.
        """
        import uuid

        from django.db import transaction
        from django.utils import timezone
        from services.auth.models import User, UserRole
        from services.auth.utils import generate_secure_password
        from services.students.models import AcademicYear, Classroom, Enrollment, Student

        app = self.get_object()
        if app.status != Application.Status.ACCEPTED or not app.offer_sent_at:
            return Response(
                {"detail": "Only accepted applications with a sent offer can be enrolled."},
                status=400,
            )
        if app.linked_student:
            return Response({"detail": "Application is already enrolled."}, status=400)

        classroom_id = request.data.get("classroom_id")
        if not classroom_id:
            return Response({"detail": "classroom_id is required."}, status=400)

        school = request.user.school
        with transaction.atomic():
            classroom = Classroom.objects.filter(id=classroom_id, school=school).select_related("grade").first()
            if not classroom:
                return Response({"detail": "Classroom not found in your school."}, status=400)
            academic_year = AcademicYear.objects.filter(school=school, is_current=True).first()
            if not academic_year:
                return Response({"detail": "No current academic year set."}, status=400)

            email = app.email.strip().lower()
            if User.objects.filter(email=email).exists():
                return Response({"detail": f"A user already exists with email {email}."}, status=400)

            password = generate_secure_password()
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=app.first_name,
                last_name=app.last_name,
                role=UserRole.STUDENT,
                school=school,
            )
            student = Student.objects.create(
                user=user,
                school=school,
                admission_number=f"STU-{uuid.uuid4().hex[:8].upper()}",
                date_of_birth=app.date_of_birth,
                gender={"male": "M", "female": "F"}.get(app.gender, "O"),
                address=app.address or "",
                city=app.city or "",
                state=app.state or "",
                country=app.nationality or "",
                admission_date=timezone.now().date(),
            )
            Enrollment.objects.create(
                student=student,
                classroom=classroom,
                academic_year=academic_year,
            )
            app.linked_student = student
            app.status = Application.Status.ENROLLED
            app.save(update_fields=["linked_student", "status"])
            _log_timeline(app, ApplicationTimelineEvent.Stage.ENROLLED, request)

        return Response(
            {
                **ApplicationSerializer(app).data,
                "generated_password": password,
            }
        )


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
