"""
Attendance Service — Views for recording and querying attendance
"""

from datetime import date, timedelta
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import AttendanceRecord, AttendanceLeave
from .serializers import AttendanceRecordSerializer, AttendanceLeaveSerializer, BulkAttendanceSerializer
from .tasks import notify_absent_guardians
from core.permissions import IsSchoolMember, IsTeacher, IsSchoolAdmin
from services.students.models import Student, Classroom


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    Attendance recording. Teachers record attendance for their classes.
    Admins can view/edit all. Parents/students are read-only.
    """

    serializer_class = AttendanceRecordSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["date", "status", "classroom", "student"]

    def get_queryset(self):
        user = self.request.user
        qs = AttendanceRecord.objects.filter(
            student__school=user.school
        ).select_related("student__user", "classroom", "recorded_by")

        if user.role == "student":
            return qs.filter(student__user=user)
        if user.role == "parent":
            return qs.filter(student__guardians__user=user)
        if user.role == "teacher":
            return qs.filter(classroom__assignments__teacher=user).distinct()
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "bulk_record"]:
            return [IsAuthenticated(), IsTeacher()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        record = serializer.save(recorded_by=self.request.user)
        if record.status == AttendanceRecord.Status.ABSENT and not record.notified_guardian:
            notify_absent_guardians.delay(str(record.id))

    @action(detail=False, methods=["post"], url_path="bulk-record")
    def bulk_record(self, request):
        """Record attendance for an entire classroom in one request."""
        serializer = BulkAttendanceSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        records = serializer.save()

        # Trigger absent notifications asynchronously
        absent_ids = [
            str(r.id) for r in records
            if r.status == AttendanceRecord.Status.ABSENT and not r.notified_guardian
        ]
        if absent_ids:
            for rid in absent_ids:
                notify_absent_guardians.delay(rid)

        return Response(
            {"recorded": len(records), "absent_notifications_queued": len(absent_ids)},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="classroom-summary")
    def classroom_summary(self, request):
        """Attendance summary for a classroom on a given date."""
        classroom_id = request.query_params.get("classroom_id")
        target_date = request.query_params.get("date", date.today().isoformat())

        if not classroom_id:
            return Response({"error": "classroom_id is required"}, status=400)

        records = AttendanceRecord.objects.filter(
            classroom_id=classroom_id, date=target_date
        ).select_related("student__user")

        students_in_class = Student.objects.filter(
            enrollments__classroom_id=classroom_id, enrollments__is_active=True
        )
        total = students_in_class.count()
        recorded = records.count()

        return Response({
            "date": target_date,
            "total_students": total,
            "recorded": recorded,
            "not_recorded": total - recorded,
            "breakdown": {
                "present": records.filter(status="P").count(),
                "absent": records.filter(status="A").count(),
                "late": records.filter(status="L").count(),
                "excused": records.filter(status="E").count(),
            },
        })

    @action(detail=False, methods=["get"], url_path="student-report")
    def student_report(self, request):
        """Monthly attendance report for a student."""
        student_id = request.query_params.get("student_id")
        month = int(request.query_params.get("month", date.today().month))
        year = int(request.query_params.get("year", date.today().year))

        if not student_id:
            return Response({"error": "student_id is required"}, status=400)

        records = AttendanceRecord.objects.filter(
            student_id=student_id,
            date__year=year,
            date__month=month,
        ).order_by("date")

        total = records.count()
        present = records.filter(status__in=["P", "L"]).count()

        return Response({
            "student_id": student_id,
            "month": month,
            "year": year,
            "total_school_days": total,
            "present": present,
            "absent": records.filter(status="A").count(),
            "late": records.filter(status="L").count(),
            "excused": records.filter(status="E").count(),
            "percentage": round((present / total * 100) if total else 0, 2),
            "records": AttendanceRecordSerializer(records, many=True).data,
        })

    @action(detail=False, methods=["get"], url_path="streak")
    def streak(self, request):
        """
        Compute a student's attendance streak — consecutive days present
        leading up to today. Accepts student_id as query param.
        Returns the current streak length and the
        longest streak within the current academic year.
        """
        from services.students.models import AcademicYear, Student as StudentModel

        student_id = request.query_params.get("student_id")
        if not student_id:
            return Response({"error": "student_id is required"}, status=400)

        try:
            student = StudentModel.objects.get(id=student_id, school=request.user.school)
        except StudentModel.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        current_year = AcademicYear.objects.filter(
            school=student.school, is_current=True
        ).first()

        records_qs = AttendanceRecord.objects.filter(
            student=student
        ).order_by("-date")

        if current_year:
            records_qs = records_qs.filter(
                date__gte=current_year.start_date,
                date__lte=current_year.end_date,
            )

        records = list(records_qs.values("date", "status"))
        if not records:
            return Response({"current_streak": 0, "longest_streak": 0})

        # Current streak (consecutive from today backward)
        today = timezone.now().date()
        current_streak = 0
        for r in records:
            if r["status"] in ("P", "L"):
                expected_date = today - timedelta(days=current_streak)
                if r["date"] == expected_date:
                    current_streak += 1
                else:
                    break
            else:
                break

        # Longest streak (scan forward)
        sorted_asc = sorted(records, key=lambda x: x["date"])
        longest_streak = 0
        temp_streak = 0
        prev_date = None
        for r in sorted_asc:
            if r["status"] in ("P", "L"):
                if prev_date is None or r["date"] == prev_date + timedelta(days=1):
                    temp_streak += 1
                else:
                    temp_streak = 1
                longest_streak = max(longest_streak, temp_streak)
                prev_date = r["date"]
            else:
                temp_streak = 0
                prev_date = None

        return Response({
            "current_streak": current_streak,
            "longest_streak": longest_streak,
        })


class AttendanceLeaveViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceLeaveSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ["school_admin", "super_admin"]:
            return AttendanceLeave.objects.filter(student__school=user.school)
        if user.role == "teacher":
            return AttendanceLeave.objects.filter(
                student__enrollments__classroom__assignments__teacher=user
            ).distinct()
        if user.role == "student":
            return AttendanceLeave.objects.filter(student__user=user)
        if user.role == "parent":
            return AttendanceLeave.objects.filter(student__guardians__user=user)
        return AttendanceLeave.objects.none()

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = "approved"
        leave.reviewed_by = request.user
        leave.review_remarks = request.data.get("remarks", "")
        leave.reviewed_at = timezone.now()
        leave.save()

        # Auto-update attendance records for the leave period
        from .tasks import process_approved_leave
        process_approved_leave.delay(leave.id)

        return Response({"status": "approved"})

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = "rejected"
        leave.reviewed_by = request.user
        leave.review_remarks = request.data.get("remarks", "")
        leave.reviewed_at = timezone.now()
        leave.save()
        return Response({"status": "rejected"})
