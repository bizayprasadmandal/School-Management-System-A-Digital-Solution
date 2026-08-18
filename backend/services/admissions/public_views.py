"""Public admissions API — no authentication required."""

import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Application, EnrollmentIntake
from .public_serializers import (
    PublicApplicationStatusSerializer,
    PublicApplicationSubmitSerializer,
    PublicIntakeSerializer,
)

logger = logging.getLogger(__name__)


class PublicIntakeListView(APIView):
    """List open intakes available for public application."""

    permission_classes = [AllowAny]

    def get(self, request):
        today = timezone.now().date()
        intakes = EnrollmentIntake.objects.filter(
            status="open",
            application_start__lte=today,
            application_end__gte=today,
        ).select_related("school")
        # Filter by school if provided (subdomain or query param)
        school_slug = request.query_params.get("school")
        if school_slug:
            intakes = intakes.filter(school__slug=school_slug)
        return Response(PublicIntakeSerializer(intakes, many=True).data)


class PublicApplicationSubmitView(APIView):
    """Submit a new application via the public portal."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PublicApplicationSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()

        # Send confirmation email to guardian (best-effort)
        self._send_confirmation_email(application)

        return Response(
            {
                "application_number": application.application_number,
                "status": application.status,
                "submitted_at": application.submitted_at,
                "intake_name": application.intake.name,
                "message": (
                    f"Application {application.application_number} submitted successfully. "
                    f"Please save your application number to check the status later."
                ),
            },
            status=status.HTTP_201_CREATED,
        )

    def _send_confirmation_email(self, application):
        from django.conf import settings as _settings
        from django.core.mail import send_mail

        recipient = application.guardian_email or application.email
        if not recipient:
            return
        try:
            send_mail(
                subject=f"Application Received — {application.application_number}",
                message=(
                    f"Dear {application.guardian_name or 'Parent'},\n\n"
                    f"Thank you for applying to {application.intake.school.name}.\n\n"
                    f"Application Number: {application.application_number}\n"
                    f"Student: {application.first_name} {application.last_name}\n"
                    f"Intake: {application.intake.name}\n"
                    f"Applying for Grade: {application.applying_for_grade}\n\n"
                    f"You can check your application status at any time using your\n"
                    f"application number.\n\n"
                    f"We will review your application and notify you of updates.\n\n"
                    f"Regards,\n{application.intake.school.name} Admissions"
                ),
                from_email=_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=True,
            )
        except Exception:
            logger.error("Confirmation email failed for %s", application.application_number, exc_info=True)


class PublicApplicationStatusView(APIView):
    """Check application status by application number."""

    permission_classes = [AllowAny]

    def get(self, request, application_number):
        application = (
            Application.objects.filter(
                application_number=application_number,
            )
            .select_related("intake")
            .first()
        )

        if not application:
            return Response(
                {"detail": "Application not found. Please check your application number."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PublicApplicationStatusSerializer(application)
        return Response(serializer.data)
