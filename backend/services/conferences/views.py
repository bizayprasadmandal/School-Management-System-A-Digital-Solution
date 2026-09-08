"""
Conference Scheduler — CRUD for parent-teacher conference slots
with Zoom meeting integration via Server-to-Server OAuth.
"""

import logging

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import zoom_service
from .models import (
    ConferenceAccessibilityRequirement,
    ConferenceAnalytics,
    ConferenceApproval,
    ConferenceAvailability,
    ConferenceBlockedSlot,
    ConferenceBooking,
    ConferenceBookingRule,
    ConferenceCalendarSync,
    ConferenceConferenceType,
    ConferenceExport,
    ConferenceFeedback,
    ConferenceFeedbackTemplate,
    ConferenceFollowUp,
    ConferenceHistory,
    ConferenceHistoryDetail,
    ConferenceLocation,
    ConferenceNoShow,
    ConferenceNotes,
    ConferenceNoteTemplate,
    ConferenceReminder,
    ConferenceReminderSchedule,
    ConferenceReport,
    ConferenceResource,
    ConferenceRoomBooking,
    ConferenceScheduleOverride,
    ConferenceSettings,
    ConferenceSlot,
    ConferenceSurvey,
    ConferenceSurveyResponse,
    ConferenceSystemNotification,
    ConferenceTemplate,
    ConferenceTemplateSection,
    ConferenceTimeSlot,
    ConferenceType,
    ConferenceWaitingList,
    FollowUpTracking,
    RecurringConference,
    RecurringConferenceParticipant,
    VirtualConference,
    WaitlistManagement,
)
from .serializers import (
    ConferenceAccessibilityRequirementSerializer,
    ConferenceAnalyticsSerializer,
    ConferenceApprovalSerializer,
    ConferenceAvailabilitySerializer,
    ConferenceBlockedSlotSerializer,
    ConferenceBookingRuleSerializer,
    ConferenceBookingSerializer,
    ConferenceCalendarSyncSerializer,
    ConferenceConferenceTypeSerializer,
    ConferenceExportSerializer,
    ConferenceFeedbackSerializer,
    ConferenceFeedbackTemplateSerializer,
    ConferenceFollowUpSerializer,
    ConferenceHistoryDetailSerializer,
    ConferenceHistorySerializer,
    ConferenceLocationSerializer,
    ConferenceNoShowSerializer,
    ConferenceNotesSerializer,
    ConferenceNoteTemplateSerializer,
    ConferenceReminderScheduleSerializer,
    ConferenceReminderSerializer,
    ConferenceReportSerializer,
    ConferenceResourceSerializer,
    ConferenceRoomBookingSerializer,
    ConferenceScheduleOverrideSerializer,
    ConferenceSettingsSerializer,
    ConferenceSlotCreateUpdateSerializer,
    ConferenceSlotSerializer,
    ConferenceSurveyResponseSerializer,
    ConferenceSurveySerializer,
    ConferenceSystemNotificationSerializer,
    ConferenceTemplateSectionSerializer,
    ConferenceTemplateSerializer,
    ConferenceTimeSlotSerializer,
    ConferenceTypeSerializer,
    ConferenceWaitingListSerializer,
    FollowUpTrackingSerializer,
    RecurringConferenceParticipantSerializer,
    RecurringConferenceSerializer,
    VirtualConferenceSerializer,
    WaitlistManagementSerializer,
    ZoomSettingsSerializer,
)

logger = logging.getLogger(__name__)


ADMIN_ROLES = ("school_admin", "super_admin", "admin")


class IsAdminOrTeacher(permissions.BasePermission):
    """Only school admins and teachers may perform this action."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role in ADMIN_ROLES or request.user.role == "teacher")
        )


class IsAdminOrTeacherOrReadStudentParent(permissions.BasePermission):
    """Admins and teachers can CRUD; students/parents read-only for their own school."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Only admins/teachers may create/update/delete slots. Students and
        # parents may only read slots and use the book/cancel/complete actions.
        if view.action in ("create", "update", "partial_update", "destroy"):
            return request.user.role in ADMIN_ROLES or request.user.role == "teacher"
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.role in ADMIN_ROLES or request.user.role == "teacher":
            return True
        if request.user.role == "parent":
            # Guardians link to a User account via Guardian.user (one-to-one,
            # nullable for non-portal guardians). Match on the user FK — the
            # same lookup the `book` action uses — not the Guardian.email field,
            # which may differ from the account email.
            return bool(obj.student and obj.student.guardians.filter(user=request.user).exists())
        if request.user.role == "student":
            return obj.student and obj.student.user == request.user
        return False


class ConferenceSlotViewSet(viewsets.ModelViewSet):
    """Manage parent-teacher conference time slots with optional Zoom meetings."""

    serializer_class = ConferenceSlotSerializer
    permission_classes = [IsAdminOrTeacherOrReadStudentParent]
    filterset_fields = ["teacher", "student", "is_booked", "date"]
    ordering_fields = ["date", "start_time"]
    ordering = ["date", "start_time"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ConferenceSlotCreateUpdateSerializer
        return ConferenceSlotSerializer

    def get_permissions(self):
        # Zoom creation/deletion and completing a conference are
        # admin/teacher-only actions. Everything else (CRUD via the class
        # permission, booking, cancelling) keeps the existing rule: admins
        # and teachers may mutate, students/parents read + book/cancel.
        if self.action in ("complete", "create_zoom_meeting", "delete_zoom_meeting"):
            return [IsAdminOrTeacher()]
        return [IsAdminOrTeacherOrReadStudentParent()]

    def get_queryset(self):
        user = self.request.user
        qs = ConferenceSlot.objects.select_related("teacher", "student__user")
        if user.role in ADMIN_ROLES:
            return qs.filter(school=user.school)
        elif user.role == "teacher":
            return qs.filter(teacher=user)
        elif user.role == "parent":
            # Parents see available (unbooked) slots for their school plus
            # slots booked for their own children.
            from django.db.models import Q

            return qs.filter(Q(student__guardians__email=user.email) | Q(is_booked=False, school=user.school))
        elif user.role == "student":
            # Students see available slots for their school plus their own bookings.
            from django.db.models import Q

            return qs.filter(Q(student__user=user) | Q(is_booked=False, school=user.school))
        return qs.none()

    def _get_slot(self, pk):
        """School-scoped lookup for actions so unbooked slots are reachable by
        students/parents even though their list queryset is role-filtered."""
        try:
            return ConferenceSlot.objects.select_related("teacher", "student__user").get(
                pk=pk, school=self.request.user.school
            )
        except ConferenceSlot.DoesNotExist:
            return None

    def perform_create(self, serializer):
        slot = serializer.save(school=self.request.user.school)
        # Auto-create Zoom meeting if requested
        create_zoom = serializer.validated_data.get("create_zoom_meeting", False)
        if create_zoom and (self.request.user.role in ADMIN_ROLES or self.request.user.role == "teacher"):
            self._auto_create_zoom(slot)

    @action(detail=True, methods=["post"])
    def book(self, request, pk=None):
        """Student/parent books an available slot."""
        slot = self._get_slot(pk)
        if slot is None:
            return Response({"detail": "Slot not found."}, status=status.HTTP_404_NOT_FOUND)
        if slot.is_booked:
            return Response({"detail": "Slot is already booked."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        from services.students.models import Student

        student = None
        if user.role == "student":
            # Students book for themselves.
            student = Student.objects.filter(user=user).first()
            if student is None:
                return Response(
                    {"detail": "No student profile found for this account."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            student_id = request.data.get("student_id")
            if not student_id:
                return Response({"detail": "student_id is required."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                student = Student.objects.get(id=student_id, school=user.school)
            except Student.DoesNotExist:
                return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
            if user.role == "parent" and not student.guardians.filter(user=user).exists():
                return Response(
                    {"detail": "You can only book conferences for your own children."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        slot.student = student
        slot.is_booked = True
        slot.booked_by = user
        slot.save()
        return Response(ConferenceSlotSerializer(slot).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a booked slot."""
        slot = self._get_slot(pk)
        if slot is None:
            return Response({"detail": "Slot not found."}, status=status.HTTP_404_NOT_FOUND)
        if not slot.is_booked:
            return Response({"detail": "Slot is not booked."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if user.role not in ADMIN_ROLES and user.role != "teacher":
            # Students/parents may only cancel their own bookings.
            if slot.booked_by_id != user.id:
                return Response(
                    {"detail": "You can only cancel your own bookings."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        slot.student = None
        slot.is_booked = False
        slot.booked_by = None
        slot.save()
        return Response(ConferenceSlotSerializer(slot).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Teacher marks a conference as completed; the slot is released."""
        slot = self._get_slot(pk)
        if slot is None:
            return Response({"detail": "Slot not found."}, status=status.HTTP_404_NOT_FOUND)
        if not slot.is_booked:
            return Response({"detail": "Slot must be booked first."}, status=status.HTTP_400_BAD_REQUEST)
        slot.delete()
        return Response({"detail": "Conference completed and slot released."})

    @staticmethod
    def _slot_topic(slot):
        """Default Zoom meeting topic for a slot."""
        if slot.student:
            teacher = slot.teacher.full_name
            pupil = slot.student.user.full_name
            return f"Parent-Teacher Conference: {teacher} & {pupil}"
        return f"Conference with {slot.teacher.full_name}"

    def _auto_create_zoom(self, slot):
        """Auto-create a Zoom meeting for a slot when create_zoom_meeting=True.
        This is called from perform_create; failures are logged but not raised
        so slot creation still succeeds even if Zoom is unavailable."""
        try:
            from datetime import datetime

            start_dt = datetime.combine(slot.date, slot.start_time)
            end_dt = datetime.combine(slot.date, slot.end_time)
            start_iso = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            duration_min = max(1, int((end_dt - start_dt).total_seconds() / 60))

            topic = self._slot_topic(slot)

            meeting = zoom_service.create_meeting(
                topic=topic,
                start_time=start_iso,
                duration_minutes=duration_min,
            )

            if meeting:
                slot.zoom_meeting_id = str(meeting.get("id", ""))
                slot.zoom_join_url = meeting.get("join_url", "")
                slot.zoom_start_url = meeting.get("start_url", "")
                slot.zoom_password = meeting.get("password", "")
                slot.is_zoom_created = True
                slot.save(
                    update_fields=[
                        "zoom_meeting_id",
                        "zoom_join_url",
                        "zoom_start_url",
                        "zoom_password",
                        "is_zoom_created",
                    ]
                )
        except Exception as e:
            logger.warning("Failed to auto-create Zoom meeting for slot %s: %s", slot.id, e)

    # ─── Zoom Integration Actions ──────────────────────────────────────────

    @action(detail=True, methods=["post"], url_path="create-zoom")
    def create_zoom_meeting(self, request, pk=None):
        """
        Create a Zoom meeting for this conference slot.
        The meeting topic defaults to the slot description.
        """
        slot = self.get_object()

        if not slot.is_booked:
            return Response(
                {"detail": "Slot must be booked before creating a Zoom meeting."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build start_time in ISO 8601
        from datetime import datetime as dt

        start_dt = dt.combine(slot.date, slot.start_time)
        start_iso = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Calculate duration from start/end times
        from datetime import datetime

        end_dt = datetime.combine(slot.date, slot.end_time)
        duration_min = max(1, int((end_dt - start_dt).total_seconds() / 60))

        topic = request.data.get("topic", self._slot_topic(slot))
        password = request.data.get("password", None)
        duration = request.data.get("duration_minutes", duration_min)

        meeting = zoom_service.create_meeting(
            topic=topic,
            start_time=start_iso,
            duration_minutes=duration,
            password=password,
        )

        if not meeting:
            return Response(
                {"detail": "Failed to create Zoom meeting. Check Zoom credentials."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Save Zoom details to the slot
        slot.zoom_meeting_id = str(meeting.get("id", ""))
        slot.zoom_join_url = meeting.get("join_url", "")
        slot.zoom_start_url = meeting.get("start_url", "")
        slot.zoom_password = meeting.get("password", "")
        slot.is_zoom_created = True
        slot.save()

        return Response(
            {
                "detail": "Zoom meeting created successfully",
                "meeting": {
                    "id": slot.zoom_meeting_id,
                    "topic": topic,
                    "join_url": slot.zoom_join_url,
                    "start_url": slot.zoom_start_url,
                    "password": slot.zoom_password,
                    "duration": duration,
                    "start_time": start_iso,
                },
            }
        )

    @action(detail=True, methods=["post"], url_path="delete-zoom")
    def delete_zoom_meeting(self, request, pk=None):
        """Delete the Zoom meeting associated with this slot."""
        slot = self.get_object()
        if not slot.is_zoom_created or not slot.zoom_meeting_id:
            return Response(
                {"detail": "No Zoom meeting to delete for this slot."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success = zoom_service.delete_meeting(slot.zoom_meeting_id)

        # Clear Zoom fields regardless (the meeting may have been deleted externally)
        slot.zoom_meeting_id = ""
        slot.zoom_join_url = ""
        slot.zoom_start_url = ""
        slot.zoom_password = ""
        slot.is_zoom_created = False
        slot.save()

        if not success:
            return Response(
                {"detail": ("Deleted local Zoom reference. " "The meeting may have already been removed from Zoom.")},
                status=status.HTTP_200_OK,
            )

        return Response({"detail": "Zoom meeting deleted successfully."})


# ─── Zoom Integration Management Views ────────────────────────────────────────


class ZoomConnectionView(APIView):
    """
    GET: Check current Zoom connection status.
    POST: Update Zoom OAuth credentials and test connection.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        """Return current Zoom connection status."""
        is_configured = bool(
            getattr(settings, "ZOOM_ACCOUNT_ID", "")
            and getattr(settings, "ZOOM_CLIENT_ID", "")
            and getattr(settings, "ZOOM_CLIENT_SECRET", "")
        )

        if not is_configured:
            return Response(
                {
                    "status": "disconnected",
                    "detail": ("Zoom credentials not configured. " "Provide Account ID, Client ID, and Client Secret."),
                    "user": None,
                }
            )

        # Test the connection
        result = zoom_service.check_connection()
        return Response(result)

    def post(self, request):
        """
        Set Zoom credentials (stored in env / settings) and test the connection.
        Note: In production, credentials should be set via environment variables.
        This endpoint allows admins to test connectivity.
        """
        serializer = ZoomSettingsSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # For Docker/containerized deployments, we can't easily persist env vars.
        # Instead, we test the provided credentials and return success/failure.
        account_id = serializer.validated_data["account_id"]
        client_id = serializer.validated_data["client_id"]
        client_secret = serializer.validated_data["client_secret"]

        # Save original settings to restore after test
        orig_account_id = getattr(settings, "ZOOM_ACCOUNT_ID", "")
        orig_client_id = getattr(settings, "ZOOM_CLIENT_ID", "")
        orig_client_secret = getattr(settings, "ZOOM_CLIENT_SECRET", "")

        # Temporarily set on Django settings for testing
        settings.ZOOM_ACCOUNT_ID = account_id
        settings.ZOOM_CLIENT_ID = client_id
        settings.ZOOM_CLIENT_SECRET = client_secret

        # Clear cached token so it picks up new credentials
        from django.core.cache import cache

        cache.delete(zoom_service.CACHE_KEY_TOKEN)

        result = zoom_service.check_connection()

        # Restore original settings
        settings.ZOOM_ACCOUNT_ID = orig_account_id
        settings.ZOOM_CLIENT_ID = orig_client_id
        settings.ZOOM_CLIENT_SECRET = orig_client_secret

        if result.get("status") == "connected":
            return Response(
                {
                    "status": "success",
                    "detail": "Zoom credentials are valid and connection is working!",
                    "user": result.get("user"),
                }
            )
        else:
            return Response(
                {"detail": result.get("detail", "Failed to connect with provided credentials.")},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ZoomMeetingsListView(APIView):
    """
    GET: List upcoming Zoom meetings (admin only — Zoom API is account-level).
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        """Fetch upcoming Zoom meetings from Zoom API."""
        meetings = zoom_service.list_meetings()
        return Response({"meetings": meetings})


# =============================================================================
# Conference Types ViewSets
# =============================================================================


class ConferenceTypeViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceTypeSerializer
    permission_classes = [IsAdminOrTeacher]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        return ConferenceType.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Conference Bookings ViewSets
# =============================================================================


class ConferenceBookingViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceBookingSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filterset_fields = ["status", "is_virtual", "teacher", "student", "parent"]
    search_fields = ["parent__first_name", "parent__last_name", "student__user__first_name"]
    ordering_fields = ["booked_at", "status"]
    ordering = ["-booked_at"]

    def get_queryset(self):
        user = self.request.user
        qs = ConferenceBooking.objects.select_related("parent", "student__user", "teacher", "slot", "booking_type")
        if user.role in ADMIN_ROLES:
            return qs.filter(teacher__school=user.school)
        elif user.role == "teacher":
            return qs.filter(teacher=user)
        elif user.role == "parent":
            return qs.filter(parent=user)
        elif user.role == "student":
            return qs.filter(student__user=user)
        return qs.none()

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Conference Reminders ViewSets
# =============================================================================


class ConferenceReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceReminderSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filterset_fields = ["booking", "reminder_type", "status"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return ConferenceReminder.objects.filter(booking__teacher__school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Conference Notes ViewSets
# =============================================================================


class ConferenceNotesViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceNotesSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filterset_fields = ["booking", "note_type", "has_action_items", "follow_up_needed"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return ConferenceNotes.objects.filter(booking__teacher__school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# =============================================================================
# Follow-up Tracking ViewSets
# =============================================================================


class FollowUpTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpTrackingSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filterset_fields = ["booking", "priority", "status", "assigned_to"]
    search_fields = ["title", "description"]
    ordering_fields = ["due_date", "priority"]
    ordering = ["due_date", "-priority"]

    def get_queryset(self):
        return FollowUpTracking.objects.filter(booking__teacher__school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Conference Availability ViewSets
# =============================================================================


class ConferenceAvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceAvailabilitySerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filterset_fields = ["teacher", "day_of_week", "availability_type", "is_active"]
    ordering_fields = ["day_of_week", "start_time"]
    ordering = ["day_of_week", "start_time"]

    def get_queryset(self):
        user = self.request.user
        if user.role in ADMIN_ROLES:
            return ConferenceAvailability.objects.filter(school=user.school)
        elif user.role == "teacher":
            return ConferenceAvailability.objects.filter(teacher=user)
        return ConferenceAvailability.objects.filter(school=user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Conference Reports ViewSets
# =============================================================================


class ConferenceReportViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceReportSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filterset_fields = ["report_type", "status"]
    search_fields = ["title", "summary"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return ConferenceReport.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, generated_by=self.request.user)


# =============================================================================
# Conference Feedback ViewSets
# =============================================================================


class ConferenceFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceFeedbackSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filterset_fields = ["booking", "feedback_for", "overall_rating"]
    search_fields = ["positive_feedback", "suggestions"]
    ordering_fields = ["submitted_at"]
    ordering = ["-submitted_at"]

    def get_queryset(self):
        return ConferenceFeedback.objects.filter(booking__teacher__school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


# =============================================================================
# Conference History ViewSets
# =============================================================================


class ConferenceHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceHistorySerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filterset_fields = ["teacher", "parent", "student", "was_virtual", "was_attended"]
    search_fields = ["teacher__first_name", "parent__first_name", "student__user__first_name"]
    ordering_fields = ["conference_date"]
    ordering = ["-conference_date"]

    def get_queryset(self):
        user = self.request.user
        qs = ConferenceHistory.objects.select_related("teacher", "parent", "student__user", "conference_type")
        if user.role in ADMIN_ROLES:
            return qs.filter(school=user.school)
        elif user.role == "teacher":
            return qs.filter(teacher=user)
        elif user.role == "parent":
            return qs.filter(parent=user)
        elif user.role == "student":
            return qs.filter(student__user=user)
        return qs.none()

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# =============================================================================
# Virtual Conference ViewSets
# =============================================================================


class VirtualConferenceViewSet(viewsets.ModelViewSet):
    serializer_class = VirtualConferenceSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filterset_fields = ["booking", "platform", "status"]
    search_fields = ["meeting_id", "meeting_url"]

    def get_queryset(self):
        return VirtualConference.objects.filter(booking__teacher__school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save()


# =============================================================================
# Conference Templates ViewSets
# =============================================================================


class ConferenceTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceTemplateSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filterset_fields = ["conference_type", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def get_queryset(self):
        return ConferenceTemplate.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


# =============================================================================
# Waitlist Management ViewSets
# =============================================================================


class WaitlistManagementViewSet(viewsets.ModelViewSet):
    serializer_class = WaitlistManagementSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]
    filterset_fields = ["slot", "parent", "student", "status"]
    search_fields = ["parent__first_name", "student__user__first_name"]
    ordering_fields = ["position", "joined_at"]
    ordering = ["position"]

    def get_queryset(self):
        user = self.request.user
        if user.role in ADMIN_ROLES:
            return WaitlistManagement.objects.filter(slot__school=user.school)
        elif user.role == "parent":
            return WaitlistManagement.objects.filter(parent=user)
        return WaitlistManagement.objects.filter(slot__school=user.school)

    def perform_create(self, serializer):
        serializer.save()


# ── Additional ViewSets (module expansion) ──


class ConferenceWaitingListViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceWaitingListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceWaitingList.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RecurringConferenceViewSet(viewsets.ModelViewSet):
    serializer_class = RecurringConferenceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return RecurringConference.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RecurringConferenceParticipantViewSet(viewsets.ModelViewSet):
    serializer_class = RecurringConferenceParticipantSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return RecurringConferenceParticipant.objects.filter(recurring_conference__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConferenceSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceSettingsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceSettings.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceAnalyticsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceAnalytics.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceBookingRuleViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceBookingRuleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceBookingRule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceSystemNotificationViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceSystemNotificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceSystemNotification.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceExportViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceExportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceExport.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceLocationViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceLocationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceLocation.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceBlockedSlotViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceBlockedSlotSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceBlockedSlot.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceScheduleOverrideViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceScheduleOverrideSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceScheduleOverride.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceReminderScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceReminderScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceReminderSchedule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceAccessibilityRequirementViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceAccessibilityRequirementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ConferenceAccessibilityRequirement.objects.filter(booking__slot__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class ConferenceNoteTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceNoteTemplateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceNoteTemplate.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceApprovalViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceApprovalSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ConferenceApproval.objects.filter(booking__slot__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class ConferenceResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceResourceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return ConferenceResource.objects.filter(booking__slot__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class ConferenceSurveyViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceSurveySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceSurvey.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceSurveyResponseViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceSurveyResponseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ConferenceSurveyResponse.objects.filter(survey__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class ConferenceCalendarSyncViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceCalendarSyncSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ConferenceCalendarSync.objects.filter(user__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConferenceHistoryDetailViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceHistoryDetailSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceHistoryDetail.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceTimeSlotViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceTimeSlotSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceTimeSlot.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceFeedbackTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceFeedbackTemplateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConferenceFeedbackTemplate.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ConferenceFollowUpViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceFollowUpSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ConferenceFollowUp.objects.filter(booking__slot__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class ConferenceRoomBookingViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceRoomBookingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ConferenceRoomBooking.objects.filter(location__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class ConferenceTemplateSectionViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceTemplateSectionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ConferenceTemplateSection.objects.filter(template__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class ConferenceNoShowViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceNoShowSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ConferenceNoShow.objects.filter(booking__slot__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ConferenceConferenceTypeViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceConferenceTypeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ConferenceConferenceType.objects.filter(conference_type__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()
