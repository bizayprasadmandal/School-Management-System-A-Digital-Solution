"""
Counseling Service — Views for counseling appointments and student referrals.
"""

import logging

from core.permissions import IsSchoolMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    CaseManagement,
    CounselingAppointment,
    CounselingFeedback,
    CounselingOutcome,
    CounselingReport,
    CounselingSession,
    CounselorAvailability,
    CounselorProfile,
    CrisisFollowUp,
    CrisisIntervention,
    GroupSession,
    GroupSessionAttendance,
    InterventionGoal,
    InterventionPlan,
    MentalHealthScreening,
    ParentConsent,
    ProgressMilestone,
    ProgressTracking,
    ScreeningResponse,
    StudentReferral,
)
from .serializers import (
    CaseManagementSerializer,
    CounselingAppointmentCreateUpdateSerializer,
    CounselingAppointmentSerializer,
    CounselingFeedbackSerializer,
    CounselingOutcomeSerializer,
    CounselingReportSerializer,
    CounselingSessionSerializer,
    CounselorAvailabilitySerializer,
    CrisisFollowUpSerializer,
    CrisisInterventionSerializer,
    GroupSessionAttendanceSerializer,
    GroupSessionSerializer,
    InterventionGoalSerializer,
    InterventionPlanSerializer,
    MentalHealthScreeningSerializer,
    ParentConsentSerializer,
    ProgressMilestoneSerializer,
    ProgressTrackingSerializer,
    ScreeningResponseSerializer,
    StudentReferralCreateUpdateSerializer,
    StudentReferralSerializer,
)

logger = logging.getLogger(__name__)


COUNSELOR_ROLES = ("counselor", "school_admin", "super_admin")


class CounselingAppointmentViewSet(viewsets.ModelViewSet):
    """
    CRUD for counseling appointments.
    Counselors see their own appointments; admins see all school appointments.
    """

    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "appointment_type", "counselor", "student", "scheduled_date"]
    search_fields = ["reason", "notes", "student__user__first_name", "student__user__last_name"]
    ordering_fields = ["scheduled_date", "scheduled_time", "created_at"]
    ordering = ["-scheduled_date", "-scheduled_time"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CounselingAppointmentCreateUpdateSerializer
        return CounselingAppointmentSerializer

    def get_queryset(self):
        user = self.request.user
        qs = CounselingAppointment.objects.select_related(
            "counselor",
            "student__user",
        ).prefetch_related(
            "student__enrollments__classroom__grade",
        )
        if user.role in COUNSELOR_ROLES:
            if user.role == "counselor":
                # Counselors see their own appointments
                return qs.filter(school=user.school, counselor=user)
            # Admins see all
            return qs.filter(school=user.school)
        # Teachers see referrals they made or appointments for their students
        return qs.filter(
            school=user.school,
        )

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark an appointment as completed and record session notes."""
        appointment = self.get_object()
        notes = request.data.get("notes", "")
        follow_up = request.data.get("follow_up_needed", False)
        follow_up_date = request.data.get("follow_up_date", None)

        appointment.status = CounselingAppointment.Status.COMPLETED
        if notes:
            appointment.notes = notes
        appointment.follow_up_needed = follow_up
        if follow_up_date:
            appointment.follow_up_date = follow_up_date
        appointment.save()

        return Response(CounselingAppointmentSerializer(appointment).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel an appointment."""
        appointment = self.get_object()
        appointment.status = CounselingAppointment.Status.CANCELLED
        appointment.save()
        return Response({"detail": "Appointment cancelled."})

    @action(detail=True, methods=["post"])
    def no_show(self, request, pk=None):
        """Mark a student as no-show for their appointment."""
        appointment = self.get_object()
        appointment.status = CounselingAppointment.Status.NO_SHOW
        appointment.save()
        return Response({"detail": "Student marked as no-show."})


class StudentReferralViewSet(viewsets.ModelViewSet):
    """
    CRUD for student referrals to the counseling department.
    Teachers can create referrals; counselors/admin manage them.
    """

    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "category", "student", "assigned_to", "is_confidential"]
    search_fields = ["reason", "notes", "student__user__first_name", "student__user__last_name"]
    ordering_fields = ["priority", "created_at", "updated_at"]
    ordering = ["-priority", "-created_at"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return StudentReferralCreateUpdateSerializer
        return StudentReferralSerializer

    def get_queryset(self):
        user = self.request.user
        qs = StudentReferral.objects.select_related(
            "student__user",
            "referred_by",
            "assigned_to",
        ).prefetch_related(
            "student__enrollments__classroom__grade",
        )
        if user.role in COUNSELOR_ROLES:
            if user.role == "counselor":
                # Counselors see referrals assigned to them
                return qs.filter(school=user.school, assigned_to=user)
            # Admins see all
            return qs.filter(school=user.school)
        # Teachers see referrals they created
        return qs.filter(school=user.school, referred_by=user)

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            referred_by=self.request.user,
        )

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        """Assign or reassign a referral to a counselor."""
        referral = self.get_object()
        counselor_id = request.data.get("assigned_to")
        if not counselor_id:
            return Response(
                {"detail": "assigned_to (counselor user ID) is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            from services.auth.models import User

            counselor = User.objects.get(
                id=counselor_id,
                school=request.user.school,
                role="counselor",
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "Counselor not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        referral.assigned_to = counselor
        referral.status = StudentReferral.Status.UNDER_REVIEW
        referral.save()
        return Response(StudentReferralSerializer(referral).data)

    @action(detail=True, methods=["post"])
    def action_taken(self, request, pk=None):
        """Record action taken on a referral and close it."""
        from django.utils import timezone

        referral = self.get_object()
        outcome = request.data.get("outcome", "")
        intervention_plan = request.data.get("intervention_plan", "")
        follow_up_date = request.data.get("follow_up_date", None)

        if outcome:
            referral.outcome = outcome
        if intervention_plan:
            referral.intervention_plan = intervention_plan
        referral.status = StudentReferral.Status.ACTIONED
        referral.action_taken_at = timezone.now()
        if follow_up_date:
            referral.follow_up_date = follow_up_date
        referral.save()

        return Response(StudentReferralSerializer(referral).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        """Close a referral (final status)."""
        referral = self.get_object()
        referral.status = StudentReferral.Status.CLOSED
        referral.save()
        return Response({"detail": "Referral closed."})

    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        """Reopen a closed referral."""
        referral = self.get_object()
        referral.status = StudentReferral.Status.UNDER_REVIEW
        referral.save()
        return Response({"detail": "Referral reopened."})


# ─── Counselor Profile (self-service) ────────────────────────────────────


class CounselorProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /counseling/profile/ — View and update your own counselor profile.
    """

    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_object(self):
        profile, _ = CounselorProfile.objects.get_or_create(
            user=self.request.user,
            school=self.request.user.school,
        )
        return profile

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            from .serializers import CounselorSelfProfileSerializer

            return CounselorSelfProfileSerializer
        from .serializers import CounselorProfileSerializer

        return CounselorProfileSerializer


# ─── Dashboard Statistics ─────────────────────────────────────────────────


class CounselorDashboardStatsView(APIView):
    """
    GET: Returns aggregate stats for the counselor dashboard.
    Only accessible by counselor and admin roles.
    """

    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get(self, request):
        if request.user.role not in COUNSELOR_ROLES:
            return Response(
                {"detail": "Only counselors and admins can view these stats."},
                status=status.HTTP_403_FORBIDDEN,
            )

        from django.utils import timezone

        today = timezone.now().date()

        # Appointments
        total_appointments = CounselingAppointment.objects.filter(
            school=request.user.school,
            counselor=request.user if request.user.role == "counselor" else None,
        )
        if request.user.role != "counselor":
            total_appointments = CounselingAppointment.objects.filter(
                school=request.user.school,
            )

        today_appointments = total_appointments.filter(scheduled_date=today).count()
        upcoming_appointments = total_appointments.filter(
            scheduled_date__gte=today,
            status__in=["scheduled", "in_progress"],
        ).count()
        completed = total_appointments.filter(status="completed").count()

        # Referrals
        total_referrals = StudentReferral.objects.filter(
            school=request.user.school,
        )
        pending_referrals = total_referrals.filter(
            status__in=["pending", "under_review", "contacted"],
        ).count()
        urgent_referrals = total_referrals.filter(
            priority="urgent",
            status__in=["pending", "under_review"],
        ).count()
        resolved = total_referrals.filter(status="closed").count()

        return Response(
            {
                "today_appointments": today_appointments,
                "upcoming_appointments": upcoming_appointments,
                "appointments_completed": completed,
                "pending_referrals": pending_referrals,
                "urgent_referrals": urgent_referrals,
                "referrals_resolved": resolved,
                "total_appointments": total_appointments.count(),
                "total_referrals": total_referrals.count(),
            }
        )


# ─── Counseling Session ViewSet ─────────────────────────────────────────


class CounselingSessionViewSet(viewsets.ModelViewSet):
    """
    CRUD for counseling sessions (session notes and documentation).
    """

    serializer_class = CounselingSessionSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["session_type", "counselor", "student", "status"]
    search_fields = ["notes", "student__user__first_name", "student__user__last_name"]
    ordering_fields = ["session_date", "created_at"]
    ordering = ["-session_date"]

    def get_queryset(self):
        return CounselingSession.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# ─── Intervention Plan ViewSet ──────────────────────────────────────────


class InterventionPlanViewSet(viewsets.ModelViewSet):
    """
    CRUD for intervention plans and goals.
    """

    serializer_class = InterventionPlanSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "category", "counselor", "student"]
    search_fields = ["title", "description", "student__user__first_name"]
    ordering_fields = ["start_date", "target_date", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return InterventionPlan.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class InterventionGoalViewSet(viewsets.ModelViewSet):
    """
    CRUD for individual goals within an intervention plan.
    """

    serializer_class = InterventionGoalSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["plan", "status"]

    def get_queryset(self):
        return InterventionGoal.objects.filter(plan__school=self.request.user.school)


# ─── Mental Health Screening ViewSet ────────────────────────────────────


class MentalHealthScreeningViewSet(viewsets.ModelViewSet):
    """
    CRUD for mental health screening tools (PHQ-9, GAD-7, etc).
    """

    serializer_class = MentalHealthScreeningSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["screening_type", "is_active"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        return MentalHealthScreening.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ScreeningResponseViewSet(viewsets.ModelViewSet):
    """
    CRUD for student responses to screenings.
    """

    serializer_class = ScreeningResponseSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["screening", "student"]

    def get_queryset(self):
        return ScreeningResponse.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, completed_by=self.request.user)


# ─── Crisis Intervention ViewSet ────────────────────────────────────────


class CrisisInterventionViewSet(viewsets.ModelViewSet):
    """
    CRUD for crisis intervention tracking.
    """

    serializer_class = CrisisInterventionSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["severity", "status", "student"]
    search_fields = ["description", "student__user__first_name"]
    ordering_fields = ["incident_date", "created_at"]
    ordering = ["-incident_date"]

    def get_queryset(self):
        return CrisisIntervention.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, reported_by=self.request.user)


class CrisisFollowUpViewSet(viewsets.ModelViewSet):
    """
    CRUD for crisis follow-up actions.
    """

    serializer_class = CrisisFollowUpSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["intervention", "completed"]

    def get_queryset(self):
        return CrisisFollowUp.objects.filter(intervention__school=self.request.user.school)


# ─── Progress Tracking ViewSet ──────────────────────────────────────────


class ProgressTrackingViewSet(viewsets.ModelViewSet):
    """
    CRUD for tracking student progress over time.
    """

    serializer_class = ProgressTrackingSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["student", "status", "goal_category"]
    search_fields = ["title", "student__user__first_name"]

    def get_queryset(self):
        return ProgressTracking.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class ProgressMilestoneViewSet(viewsets.ModelViewSet):
    """
    CRUD for milestones within progress tracking.
    """

    serializer_class = ProgressMilestoneSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tracking", "status"]

    def get_queryset(self):
        return ProgressMilestone.objects.filter(tracking__school=self.request.user.school)


# ─── Parent Consent ViewSet ─────────────────────────────────────────────


class ParentConsentViewSet(viewsets.ModelViewSet):
    """
    CRUD for parent consent forms.
    """

    serializer_class = ParentConsentSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["student", "consent_type", "status"]
    search_fields = ["student__user__first_name", "parent__first_name"]

    def get_queryset(self):
        return ParentConsent.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# ─── Group Session ViewSet ──────────────────────────────────────────────


class GroupSessionViewSet(viewsets.ModelViewSet):
    """
    CRUD for group counseling sessions.
    """

    serializer_class = GroupSessionSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["counselor", "session_type", "status"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        return GroupSession.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, counselor=self.request.user)


class GroupSessionAttendanceViewSet(viewsets.ModelViewSet):
    """
    CRUD for group session attendance.
    """

    serializer_class = GroupSessionAttendanceSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["group_session", "student", "attended"]

    def get_queryset(self):
        return GroupSessionAttendance.objects.filter(group_session__school=self.request.user.school)


# ─── Case Management ViewSet ────────────────────────────────────────────


class CaseManagementViewSet(viewsets.ModelViewSet):
    """
    CRUD for comprehensive case management.
    """

    serializer_class = CaseManagementSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "case_worker", "student"]
    search_fields = ["case_number", "student__user__first_name", "title"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return CaseManagement.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, case_worker=self.request.user)


# ─── Counseling Outcome ViewSet ─────────────────────────────────────────


class CounselingOutcomeViewSet(viewsets.ModelViewSet):
    """
    CRUD for tracking outcomes of counseling.
    """

    serializer_class = CounselingOutcomeSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "outcome_type"]

    def get_queryset(self):
        return CounselingOutcome.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# ─── Counseling Report ViewSet ──────────────────────────────────────────


class CounselingReportViewSet(viewsets.ModelViewSet):
    """
    CRUD for counseling reports and analytics.
    """

    serializer_class = CounselingReportSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["report_type", "generated_by"]

    def get_queryset(self):
        return CounselingReport.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, generated_by=self.request.user)


# ─── Counselor Availability ViewSet ─────────────────────────────────────


class CounselorAvailabilityViewSet(viewsets.ModelViewSet):
    """
    CRUD for counselor availability and scheduling.
    """

    serializer_class = CounselorAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["counselor", "day_of_week", "is_available"]

    def get_queryset(self):
        return CounselorAvailability.objects.filter(counselor__school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save()


# ─── Counseling Feedback ViewSet ────────────────────────────────────────


class CounselingFeedbackViewSet(viewsets.ModelViewSet):
    """
    CRUD for student/parent feedback on counseling.
    """

    serializer_class = CounselingFeedbackSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "feedback_type"]

    def get_queryset(self):
        return CounselingFeedback.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, submitted_by=self.request.user)
