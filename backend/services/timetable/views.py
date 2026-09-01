"""
Timetable Service — Views and serializers for schedule management
"""

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    AcademicCalendar,
    CoCurricularSchedule,
    ConflictDetection,
    ExamSchedule,
    ExamScheduleEntry,
    Period,
    RoomBooking,
    SchoolClosure,
    SchoolEvent,
    SubstituteTeacher,
    TeacherPreference,
    TeacherTimetable,
    TimetableApproval,
    TimetableChange,
    TimetableReport,
    TimetableSlot,
    TimetableTemplate,
    TimetableTemplateSlot,
)

# ─── Serializers ──────────────────────────────────────────────────────────────


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ["id", "name", "period_number", "start_time", "end_time", "is_break"]

    def validate_period_number(self, value):
        request = self.context.get("request")
        if request and getattr(request, "user", None) and request.user.is_authenticated:
            school = request.user.school
            qs = Period.objects.filter(school=school, period_number=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(f"A period with number {value} already exists for this school.")
        return value


class TimetableSlotSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    subject_code = serializers.CharField(source="assignment.subject.code", read_only=True)
    teacher_name = serializers.CharField(source="assignment.teacher.full_name", read_only=True)
    classroom_name = serializers.SerializerMethodField()
    period_name = serializers.CharField(source="period.name", read_only=True)
    period_number = serializers.IntegerField(source="period.period_number", read_only=True)
    start_time = serializers.TimeField(source="period.start_time", read_only=True)
    end_time = serializers.TimeField(source="period.end_time", read_only=True)
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = TimetableSlot
        fields = [
            "id",
            "classroom",
            "classroom_name",
            "assignment",
            "subject_name",
            "subject_code",
            "teacher_name",
            "period",
            "period_name",
            "period_number",
            "start_time",
            "end_time",
            "day_of_week",
            "day_name",
            "room",
            "academic_year",
        ]

    def get_classroom_name(self, obj):
        return str(obj.classroom)

    def get_day_name(self, obj):
        return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week, "")

    def validate(self, attrs):
        # Conflict detection: teacher double-booking.
        # Use instance values for fields not present in a PATCH payload.
        assignment = attrs.get("assignment") or getattr(self.instance, "assignment", None)
        if assignment is None:
            return attrs
        teacher = assignment.teacher
        day = attrs.get("day_of_week", getattr(self.instance, "day_of_week", None))
        period = attrs.get("period", getattr(self.instance, "period", None))
        academic_year = attrs.get("academic_year", getattr(self.instance, "academic_year", None))
        existing = TimetableSlot.objects.filter(
            assignment__teacher=teacher,
            day_of_week=day,
            period=period,
            academic_year=academic_year,
        ).exclude(pk=self.instance.pk if self.instance else None)
        if existing.exists():
            raise serializers.ValidationError(
                f"Teacher '{teacher.full_name}' is already assigned to another class "
                f"in {period.name} on {dict(TimetableSlot.DAYS_OF_WEEK)[day]}."
            )
        return attrs


class SchoolEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolEvent
        fields = [
            "id",
            "title",
            "description",
            "event_type",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "venue",
            "is_school_wide",
            "target_grades",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# ─── Views ────────────────────────────────────────────────────────────────────


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
    filterset_fields = ["classroom", "day_of_week", "academic_year", "assignment__teacher"]

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
        return qs

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
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
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


class TeacherTimetableSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    classroom_name = serializers.CharField(source="classroom.__str__", read_only=True)
    period_name = serializers.CharField(source="period.name", read_only=True)
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherTimetable
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

    def get_day_name(self, obj):
        return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week, "")


class SubstituteTeacherSerializer(serializers.ModelSerializer):
    original_teacher_name = serializers.CharField(source="original_teacher.get_full_name", read_only=True)
    substitute_teacher_name = serializers.CharField(source="substitute_teacher.get_full_name", read_only=True)

    class Meta:
        model = SubstituteTeacher
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ConflictDetectionSerializer(serializers.ModelSerializer):
    conflict_type_display = serializers.CharField(source="get_conflict_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ConflictDetection
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ExamScheduleEntrySerializer(serializers.ModelSerializer):
    classroom_name = serializers.CharField(source="classroom.__str__", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    invigilator_name = serializers.CharField(source="invigilator.get_full_name", read_only=True)

    class Meta:
        model = ExamScheduleEntry
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class ExamScheduleSerializer(serializers.ModelSerializer):
    entries = ExamScheduleEntrySerializer(many=True, read_only=True)

    class Meta:
        model = ExamSchedule
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AcademicCalendarSerializer(serializers.ModelSerializer):
    calendar_type_display = serializers.CharField(source="get_calendar_type_display", read_only=True)

    class Meta:
        model = AcademicCalendar
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class RoomBookingSerializer(serializers.ModelSerializer):
    booked_by_name = serializers.CharField(source="booked_by.get_full_name", read_only=True)
    booking_type_display = serializers.CharField(source="get_booking_type_display", read_only=True)

    class Meta:
        model = RoomBooking
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableTemplateSlotSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    period_name = serializers.CharField(source="period.name", read_only=True)
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = TimetableTemplateSlot
        fields = "__all__"

    def get_day_name(self, obj):
        return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week, "")


class TimetableTemplateSerializer(serializers.ModelSerializer):
    slots = TimetableTemplateSlotSerializer(many=True, read_only=True)

    class Meta:
        model = TimetableTemplate
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_day_name(self, obj):
        return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week, "")


class TeacherPreferenceSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)
    preference_type_display = serializers.CharField(source="get_preference_type_display", read_only=True)
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = TeacherPreference
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_day_name(self, obj):
        if obj.day_of_week is not None:
            return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week, "")
        return None


class TimetableApprovalSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source="submitted_by.get_full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = TimetableApproval
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class TimetableChangeSerializer(serializers.ModelSerializer):
    change_type_display = serializers.CharField(source="get_change_type_display", read_only=True)
    changed_by_name = serializers.CharField(source="changed_by.get_full_name", read_only=True)

    class Meta:
        model = TimetableChange
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CoCurricularScheduleSerializer(serializers.ModelSerializer):
    activity_type_display = serializers.CharField(source="get_activity_type_display", read_only=True)
    instructor_name = serializers.CharField(source="instructor.get_full_name", read_only=True)
    day_name = serializers.SerializerMethodField()

    class Meta:
        model = CoCurricularSchedule
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_day_name(self, obj):
        return dict(TimetableSlot.DAYS_OF_WEEK).get(obj.day_of_week, "")


class TimetableReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source="get_report_type_display", read_only=True)
    generated_by_name = serializers.CharField(source="generated_by.get_full_name", read_only=True)

    class Meta:
        model = TimetableReport
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SchoolClosureSerializer(serializers.ModelSerializer):
    closure_type_display = serializers.CharField(source="get_closure_type_display", read_only=True)

    class Meta:
        model = SchoolClosure
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


# ─── New Views ───────────────────────────────────────────────────────────────


class TeacherTimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherTimetableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TeacherTimetable.objects.filter(teacher=self.request.user)


class SubstituteTeacherViewSet(viewsets.ModelViewSet):
    serializer_class = SubstituteTeacherSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SubstituteTeacher.objects.filter(school=self.request.user.school)


class ConflictDetectionViewSet(viewsets.ModelViewSet):
    serializer_class = ConflictDetectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ConflictDetection.objects.filter(school=self.request.user.school)


class ExamScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ExamScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExamSchedule.objects.filter(school=self.request.user.school)


class ExamScheduleEntryViewSet(viewsets.ModelViewSet):
    serializer_class = ExamScheduleEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExamScheduleEntry.objects.filter(exam_schedule__school=self.request.user.school)


class AcademicCalendarViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicCalendarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AcademicCalendar.objects.filter(school=self.request.user.school)


class RoomBookingViewSet(viewsets.ModelViewSet):
    serializer_class = RoomBookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RoomBooking.objects.filter(school=self.request.user.school)


class TimetableTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimetableTemplate.objects.filter(school=self.request.user.school)


class TimetableTemplateSlotViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableTemplateSlotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimetableTemplateSlot.objects.filter(template__school=self.request.user.school)


class TeacherPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TeacherPreference.objects.filter(teacher=self.request.user)


class TimetableApprovalViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableApprovalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimetableApproval.objects.filter(school=self.request.user.school)


class TimetableChangeViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableChangeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimetableChange.objects.filter(school=self.request.user.school)


class CoCurricularScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = CoCurricularScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CoCurricularSchedule.objects.filter(school=self.request.user.school)


class TimetableReportViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TimetableReport.objects.filter(school=self.request.user.school)


class SchoolClosureViewSet(viewsets.ModelViewSet):
    serializer_class = SchoolClosureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SchoolClosure.objects.filter(school=self.request.user.school)
