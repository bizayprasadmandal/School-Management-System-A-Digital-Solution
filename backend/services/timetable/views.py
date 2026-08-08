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

from .models import Period, SchoolEvent, TimetableSlot

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
        """Full weekly schedule for a teacher."""
        teacher_id = request.query_params.get("teacher_id", str(request.user.id))
        academic_year_id = request.query_params.get("academic_year_id")
        qs = self.get_queryset().filter(assignment__teacher_id=teacher_id)
        if academic_year_id:
            qs = qs.filter(academic_year_id=academic_year_id)
        qs = qs.order_by("day_of_week", "period__period_number")
        return Response(TimetableSlotSerializer(qs, many=True).data)


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
