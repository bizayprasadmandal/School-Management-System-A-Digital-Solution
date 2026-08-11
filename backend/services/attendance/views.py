"""
Attendance Service — Views for recording and querying attendance
"""

from datetime import date, timedelta

from core.permissions import IsSchoolAdmin, IsSchoolMember, IsTeacher
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from services.students.models import Student

from .models import AttendanceLeave, AttendanceRecord
from .serializers import AttendanceLeaveSerializer, AttendanceRecordSerializer, BulkAttendanceSerializer
from .tasks import notify_absent_guardians


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
        qs = (
            AttendanceRecord.objects.filter(student__school=user.school)
            .select_related("student__user", "classroom", "recorded_by")
            .order_by("-date", "-recorded_at", "-id")
        )

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
            str(r.id) for r in records if r.status == AttendanceRecord.Status.ABSENT and not r.notified_guardian
        ]
        if absent_ids:
            for rid in absent_ids:
                notify_absent_guardians.delay(rid)

        return Response(
            {"recorded": len(records), "absent_notifications_queued": len(absent_ids)},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="import-csv")
    def import_csv(self, request):
        """
        Bulk-import attendance from CSV data.
        Expected CSV columns (header row required):
        admission_number, date (YYYY-MM-DD), status (P/A/L/E/H),
        remarks, classroom_name (optional)
        Rows are upserted per (student, date); unknown students or
        invalid statuses are reported as row errors.
        """
        import csv
        import io

        from services.students.models import AcademicYear

        csv_text = request.data.get("csv_data", "")
        if not csv_text:
            return Response({"error": "csv_data field is required."}, status=400)

        school = request.user.school
        current_year = AcademicYear.objects.filter(school=school, is_current=True).first()
        if not current_year:
            return Response({"error": "No current academic year set."}, status=400)

        valid_statuses = [s for s, _ in AttendanceRecord.Status.choices]
        reader = csv.DictReader(io.StringIO(csv_text))
        imported = 0
        errors = []

        for row_num, row in enumerate(reader, start=2):
            try:
                admission_number = row.get("admission_number", "").strip()
                record_date = row.get("date", "").strip()
                status_val = row.get("status", "").strip().upper()

                if not admission_number or not record_date:
                    errors.append(f"Row {row_num}: admission_number and date are required")
                    continue
                if status_val not in valid_statuses:
                    errors.append(
                        f"Row {row_num}: invalid status '{status_val}' (allowed: {', '.join(valid_statuses)})"
                    )
                    continue

                student = Student.objects.filter(school=school, admission_number=admission_number).first()
                if not student:
                    errors.append(f"Row {row_num}: student with admission '{admission_number}' not found")
                    continue

                enrollment = student.enrollments.filter(is_active=True).first()
                classroom = enrollment.classroom if enrollment else None
                classroom_name = row.get("classroom_name", "").strip()
                if classroom_name:
                    from services.students.models import Classroom

                    named = Classroom.objects.filter(school=school, name=classroom_name).first()
                    if named:
                        classroom = named

                if not classroom:
                    errors.append(f"Row {row_num}: no classroom resolved for admission '{admission_number}'")
                    continue

                AttendanceRecord.objects.update_or_create(
                    student=student,
                    date=record_date,
                    defaults={
                        "classroom": classroom,
                        "academic_year": current_year,
                        "status": status_val,
                        "remarks": row.get("remarks", "").strip(),
                        "recorded_by": request.user,
                    },
                )
                imported += 1
            except Exception as e:
                # One bad row (e.g. unparseable date) must never 500 the whole import.
                errors.append(f"Row {row_num}: {str(e)[:100]}")

        return Response({"imported": imported, "errors": errors[:20]})

    @action(detail=False, methods=["get"], url_path="classroom-summary")
    def classroom_summary(self, request):
        """Attendance summary for a classroom on a given date."""
        classroom_id = request.query_params.get("classroom_id")
        target_date = request.query_params.get("date", date.today().isoformat())

        if not classroom_id:
            return Response({"error": "classroom_id is required"}, status=400)

        records = AttendanceRecord.objects.filter(classroom_id=classroom_id, date=target_date).select_related(
            "student__user"
        )

        students_in_class = Student.objects.filter(enrollments__classroom_id=classroom_id, enrollments__is_active=True)
        total = students_in_class.count()
        recorded = records.count()

        return Response(
            {
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
            }
        )

    @action(detail=False, methods=["get"], url_path="student-report")
    def student_report(self, request):
        """Monthly attendance report for a student."""
        student_id = request.query_params.get("student_id")
        month = int(request.query_params.get("month", date.today().month))
        year = int(request.query_params.get("year", date.today().year))

        if not student_id:
            return Response({"error": "student_id is required"}, status=400)

        # Tenant isolation: only students in the caller's school.
        try:
            student = Student.objects.get(id=student_id, school=request.user.school)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        records = (
            AttendanceRecord.objects.filter(
                student=student,
                date__year=year,
                date__month=month,
            )
            .select_related("student__user")
            .order_by("date")
        )

        # One aggregate query instead of five COUNT queries.
        from django.db.models import Count, Q

        summary = records.aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status__in=["P", "L"])),
            absent=Count("id", filter=Q(status="A")),
            late=Count("id", filter=Q(status="L")),
            excused=Count("id", filter=Q(status="E")),
        )
        total = summary["total"]
        present = summary["present"]

        return Response(
            {
                "student_id": student_id,
                "month": month,
                "year": year,
                "total_school_days": total,
                "present": present,
                "absent": summary["absent"],
                "late": summary["late"],
                "excused": summary["excused"],
                "percentage": round((present / total * 100) if total else 0, 2),
                "records": AttendanceRecordSerializer(records, many=True).data,
            }
        )

    @action(detail=False, methods=["get"], url_path="streak")
    def streak(self, request):
        """
        Compute a student's attendance streak — consecutive days present
        leading up to today. Accepts student_id as query param.
        Returns the current streak length and the
        longest streak within the current academic year.
        """
        from services.students.models import AcademicYear
        from services.students.models import Student as StudentModel

        student_id = request.query_params.get("student_id")
        if not student_id:
            return Response({"error": "student_id is required"}, status=400)

        try:
            student = StudentModel.objects.get(id=student_id, school=request.user.school)
        except StudentModel.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        current_year = AcademicYear.objects.filter(school=student.school, is_current=True).first()

        records_qs = AttendanceRecord.objects.filter(student=student).order_by("-date")

        if current_year:
            # Scope by the academic_year object rather than a date range:
            # the school's official year bounds may not cover every record
            # that is legitimately tagged with the current year (e.g. records
            # created before start_date or after end_date).
            records_qs = records_qs.filter(academic_year=current_year)

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

        return Response(
            {
                "current_streak": current_streak,
                "longest_streak": longest_streak,
            }
        )


class AttendanceLeaveViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceLeaveSerializer

    def get_queryset(self):
        user = self.request.user
        qs = AttendanceLeave.objects.order_by("-requested_at")
        if user.role in ["school_admin", "super_admin"]:
            return qs.filter(student__school=user.school)
        if user.role == "teacher":
            return qs.filter(student__enrollments__classroom__assignments__teacher=user).distinct()
        if user.role == "student":
            return qs.filter(student__user=user)
        if user.role == "parent":
            return qs.filter(student__guardians__user=user)
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
