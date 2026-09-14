"""
Timetable Service — Views and serializers for schedule management
"""

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    AcademicCalendar,
    AcademicSession,
    BellSchedule,
    BellScheduleEntry,
    ClassGroup,
    ClassGroupEnrollment,
    ClassSchedule,
    CoCurricularSchedule,
    ConflictDetection,
    DailySchedule,
    ExamAttendance,
    ExamRoomAllocation,
    ExamSchedule,
    ExamScheduleEntry,
    LessonPlan,
    Period,
    RoomBooking,
    RoomUtilization,
    SchoolClosure,
    SchoolEvent,
    SeatingArrangement,
    SubjectTeacherAssignment,
    SubstituteSchedule,
    SubstituteTeacher,
    TeacherPreference,
    TeacherTimetable,
    TeacherWorkload,
    TimetableAnalytics,
    TimetableApproval,
    TimetableChange,
    TimetableChangeRequest,
    TimetableReport,
    TimetableResource,
    TimetableResourceBooking,
    TimetableSlot,
    TimetableTemplate,
    TimetableTemplateSlot,
    TimetableValidationError,
    TimetableValidationRule,
    TimetableVersion,
)
from .serializers import (
    AcademicCalendarSerializer,
    AcademicSessionSerializer,
    BellScheduleEntrySerializer,
    BellScheduleSerializer,
    ClassGroupEnrollmentSerializer,
    ClassGroupSerializer,
    ClassScheduleSerializer,
    CoCurricularScheduleSerializer,
    ConflictDetectionSerializer,
    DailyScheduleSerializer,
    ExamAttendanceSerializer,
    ExamRoomAllocationSerializer,
    ExamScheduleEntrySerializer,
    ExamScheduleSerializer,
    LessonPlanSerializer,
    PeriodSerializer,
    RoomBookingSerializer,
    RoomUtilizationSerializer,
    SchoolClosureSerializer,
    SchoolEventSerializer,
    SeatingArrangementSerializer,
    SubjectTeacherAssignmentSerializer,
    SubstituteScheduleSerializer,
    SubstituteTeacherSerializer,
    TeacherPreferenceSerializer,
    TeacherTimetableSerializer,
    TeacherWorkloadSerializer,
    TimetableAnalyticsSerializer,
    TimetableApprovalSerializer,
    TimetableChangeRequestSerializer,
    TimetableChangeSerializer,
    TimetableReportSerializer,
    TimetableResourceBookingSerializer,
    TimetableResourceSerializer,
    TimetableSlotSerializer,
    TimetableTemplateSerializer,
    TimetableTemplateSlotSerializer,
    TimetableValidationErrorSerializer,
    TimetableValidationRuleSerializer,
    TimetableVersionSerializer,
)

# ─── Serializers ──────────────────────────────────────────────────────────────


class PeriodViewSet(viewsets.ModelViewSet):
    serializer_class = PeriodSerializer

    def get_queryset(self):
        return Period.objects.filter(school=self.request.user.school).order_by("period_number")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TimetableSlotViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSlotSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "classroom",
        "day_of_week",
        "academic_year",
        "assignment__teacher",
    ]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        user = self.request.user
        qs = TimetableSlot.objects.filter(classroom__school=user.school).select_related(
            "assignment__teacher",
            "assignment__subject",
            "classroom__grade",
            "period",
            "academic_year",
        )
        if user.role == "teacher":
            qs = qs.filter(assignment__teacher=user)
        return qs.order_by("day_of_week", "period")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=False, methods=["get"], url_path="weekly")
    def weekly(self, request):
        """Return complete weekly timetable for a classroom, structured by day."""
        classroom_id = request.query_params.get("classroom_id")
        academic_year_id = request.query_params.get("academic_year_id")
        if not classroom_id:
            return Response({"detail": "classroom_id is required."}, status=400)

        qs = self.get_queryset().filter(classroom_id=classroom_id)
        if academic_year_id:
            qs = qs.filter(academic_year_id=academic_year_id)

        # Structure by day
        week = {day: [] for day in range(6)}
        for slot in qs.order_by("day_of_week", "period__period_number"):
            week[slot.day_of_week].append(TimetableSlotSerializer(slot).data)

        return Response({dict(TimetableSlot.DAYS_OF_WEEK)[day]: slots for day, slots in week.items()})

    @action(detail=False, methods=["get"], url_path="teacher-schedule")
    def teacher_schedule(self, request):
        """
        Full weekly schedule for a teacher with statistics.
        Query params: teacher_id (optional, defaults to current user), academic_year_id (optional)
        """
        teacher_id = request.query_params.get("teacher_id", str(request.user.id))
        academic_year_id = request.query_params.get("academic_year_id")

        qs = self.get_queryset().filter(assignment__teacher_id=teacher_id)
        if academic_year_id:
            qs = qs.filter(academic_year_id=academic_year_id)

        qs = qs.order_by("day_of_week", "period__period_number")
        slots = TimetableSlotSerializer(qs, many=True).data

        # Structure by day
        weekly_schedule = {day: [] for day in range(6)}
        for slot in slots:
            weekly_schedule[slot["day_of_week"]].append(slot)

        # Calculate statistics
        day_names = dict(TimetableSlot.DAYS_OF_WEEK)
        total_periods = len(slots)

        # Count unique subjects
        subjects = set(slot["subject_name"] for slot in slots)

        # Count unique classrooms
        classrooms = set(slot["classroom_name"] for slot in slots)

        # Daily breakdown
        daily_breakdown = {}
        for day_num, day_slots in weekly_schedule.items():
            if day_slots:  # Only include days with slots
                daily_breakdown[day_names[day_num]] = {
                    "period_count": len(day_slots),
                    "periods": [slot["period_number"] for slot in day_slots],
                    "subjects": list(set(slot["subject_name"] for slot in day_slots)),
                }

        return Response(
            {
                "teacher_id": teacher_id,
                "total_periods_per_week": total_periods,
                "unique_subjects": list(subjects),
                "unique_classrooms": list(classrooms),
                "daily_breakdown": daily_breakdown,
                "schedule": {day_names[day]: slots_list for day, slots_list in weekly_schedule.items() if slots_list},
            }
        )


class SchoolEventViewSet(viewsets.ModelViewSet):
    serializer_class = SchoolEventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["event_type", "is_school_wide"]
    search_fields = ["title", "description"]
    ordering_fields = ["start_date"]
    ordering = ["start_date"]

    def get_queryset(self):
        return SchoolEvent.objects.filter(school=self.request.user.school).prefetch_related("target_grades")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            created_by=self.request.user,
        )

    @action(detail=False, methods=["get"], url_path="upcoming")
    def upcoming(self, request):
        from django.utils import timezone

        qs = self.get_queryset().filter(start_date__gte=timezone.now().date())[:10]
        return Response(SchoolEventSerializer(qs, many=True).data)


# ─── New Serializers ─────────────────────────────────────────────────────────


class TeacherTimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherTimetableSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return TeacherTimetable.objects.filter(teacher=self.request.user)


class SubstituteTeacherViewSet(viewsets.ModelViewSet):
    serializer_class = SubstituteTeacherSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return SubstituteTeacher.objects.filter(school=self.request.user.school)


class ConflictDetectionViewSet(viewsets.ModelViewSet):
    serializer_class = ConflictDetectionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return ConflictDetection.objects.filter(school=self.request.user.school)


class ExamScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return ExamSchedule.objects.filter(school=self.request.user.school)


class ExamScheduleEntryViewSet(viewsets.ModelViewSet):
    serializer_class = ExamScheduleEntrySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return ExamScheduleEntry.objects.filter(exam_schedule__school=self.request.user.school)


class AcademicCalendarViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicCalendarSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return AcademicCalendar.objects.filter(school=self.request.user.school)


class RoomBookingViewSet(viewsets.ModelViewSet):
    serializer_class = RoomBookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return RoomBooking.objects.filter(school=self.request.user.school)


class TimetableTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableTemplateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return TimetableTemplate.objects.filter(school=self.request.user.school)


class TimetableTemplateSlotViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableTemplateSlotSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return TimetableTemplateSlot.objects.filter(template__school=self.request.user.school)


class TeacherPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return TeacherPreference.objects.filter(teacher=self.request.user)


class TimetableApprovalViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableApprovalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return TimetableApproval.objects.filter(school=self.request.user.school)


class TimetableChangeViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableChangeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return TimetableChange.objects.filter(school=self.request.user.school)


class CoCurricularScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = CoCurricularScheduleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return CoCurricularSchedule.objects.filter(school=self.request.user.school)


class TimetableReportViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableReportSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return TimetableReport.objects.filter(school=self.request.user.school)


class SchoolClosureViewSet(viewsets.ModelViewSet):
    serializer_class = SchoolClosureSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return SchoolClosure.objects.filter(school=self.request.user.school)


# ── Additional ViewSets (module expansion) ──


class BellScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = BellScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return BellSchedule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BellScheduleEntryViewSet(viewsets.ModelViewSet):
    serializer_class = BellScheduleEntrySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return BellScheduleEntry.objects.filter(bell_schedule__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class ClassGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ClassGroupSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ClassGroup.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ClassGroupEnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = ClassGroupEnrollmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ClassGroupEnrollment.objects.filter(class_group__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class SubjectTeacherAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectTeacherAssignmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return SubjectTeacherAssignment.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class LessonPlanViewSet(viewsets.ModelViewSet):
    serializer_class = LessonPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return LessonPlan.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ExamRoomAllocationViewSet(viewsets.ModelViewSet):
    serializer_class = ExamRoomAllocationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ExamRoomAllocation.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SeatingArrangementViewSet(viewsets.ModelViewSet):
    serializer_class = SeatingArrangementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return SeatingArrangement.objects.filter(room_allocation__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class ExamAttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = ExamAttendanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ExamAttendance.objects.filter(exam_entry__exam_schedule__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class AcademicSessionViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicSessionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return AcademicSession.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SubstituteScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = SubstituteScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return SubstituteSchedule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RoomUtilizationViewSet(viewsets.ModelViewSet):
    serializer_class = RoomUtilizationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return RoomUtilization.objects.filter(room__building__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class TimetableValidationRuleViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableValidationRuleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return TimetableValidationRule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TimetableValidationErrorViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableValidationErrorSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return TimetableValidationError.objects.filter(rule__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class TimetableResourceViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableResourceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return TimetableResource.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TimetableResourceBookingViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableResourceBookingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return TimetableResourceBooking.objects.filter(resource__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class TimetableAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableAnalyticsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return TimetableAnalytics.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TimetableChangeRequestViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableChangeRequestSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return TimetableChangeRequest.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class DailyScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = DailyScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return DailySchedule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TeacherWorkloadViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherWorkloadSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return TeacherWorkload.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ClassScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ClassScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return ClassSchedule.objects.filter(class_group__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class TimetableVersionViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableVersionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return TimetableVersion.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
