"""
Attendance Service — Views for recording and querying attendance
"""

from datetime import timedelta

from core.permissions import IsSchoolAdmin, IsSchoolMember, IsSchoolStaff, IsTeacher
from django.conf import settings
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from services.students.models import Student

from .models import AttendanceChangeLog, AttendanceLeave, AttendanceRecord, PeriodAttendance
from .serializers import (
    AttendanceChangeLogSerializer,
    AttendanceLeaveSerializer,
    AttendanceRecordSerializer,
    BulkAttendanceSerializer,
    BulkPeriodAttendanceSerializer,
    PeriodAttendanceSerializer,
    log_attendance_change,
)
from .tasks import notify_absent_guardians

ATTENDANCE_EDIT_WINDOW_DAYS = getattr(settings, "ATTENDANCE_EDIT_WINDOW_DAYS", 7)


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
        if self.action in ["destroy", "import_csv"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        record = serializer.save(recorded_by=self.request.user)
        log_attendance_change("daily", record, "create", self.request.user, new_values={"status": record.status})
        if record.status == AttendanceRecord.Status.ABSENT and not record.notified_guardian:
            notify_absent_guardians.delay(str(record.id))

    def perform_update(self, serializer):
        instance = serializer.instance
        # Time-window check: only allow edits within configured days
        if instance.recorded_at:
            elapsed = timezone.now() - instance.recorded_at
            if elapsed.days > ATTENDANCE_EDIT_WINDOW_DAYS:
                raise PermissionDenied(f"Cannot edit attendance older than {ATTENDANCE_EDIT_WINDOW_DAYS} days.")
        old_values = {"status": instance.status, "remarks": instance.remarks}
        record = serializer.save(updated_by=self.request.user)
        new_values = {"status": record.status, "remarks": record.remarks}
        log_attendance_change(
            "daily",
            record,
            "update",
            self.request.user,
            old_values=old_values,
            new_values=new_values,
            reason=self.request.data.get("reason", ""),
        )
        # Notify guardian if status changed to absent
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

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request):
        """
        Attendance dashboard analytics for admins.
        Returns today's stats, weekly trends, at-risk students, and class comparisons.
        """
        from django.db.models import Avg, Count, Q
        from services.students.models import Classroom

        school = request.user.school
        today = timezone.localdate()
        month_ago = today - timedelta(days=30)

        # Today's stats
        today_records = AttendanceRecord.objects.filter(classroom__school=school, date=today)
        today_total = today_records.count()
        today_breakdown = {
            "present": today_records.filter(status="P").count(),
            "absent": today_records.filter(status="A").count(),
            "late": today_records.filter(status="L").count(),
            "excused": today_records.filter(status="E").count(),
        }
        today_percentage = (
            round((today_breakdown["present"] + today_breakdown["late"]) / today_total * 100, 1)
            if today_total > 0
            else 0
        )

        # Weekly trend (last 7 days)
        weekly_trend = []
        for i in range(7):
            day = today - timedelta(days=6 - i)
            day_records = AttendanceRecord.objects.filter(classroom__school=school, date=day)
            day_total = day_records.count()
            day_present = day_records.filter(status__in=["P", "L"]).count()
            weekly_trend.append(
                {
                    "date": day.isoformat(),
                    "day_name": day.strftime("%A"),
                    "total": day_total,
                    "present": day_present,
                    "percentage": round(day_present / day_total * 100, 1) if day_total > 0 else 0,
                }
            )

        # At-risk students (attendance < 75% in last 30 days)
        total_students = Student.objects.filter(school=school, enrollments__is_active=True).distinct().count()
        student_attendance = (
            AttendanceRecord.objects.filter(
                classroom__school=school,
                date__gte=month_ago,
            )
            .values("student__id", "student__user__first_name", "student__user__last_name", "student__admission_number")
            .annotate(
                total_days=Count("id"),
                present_days=Count("id", filter=Q(status__in=["P", "L"])),
            )
            .annotate(attendance_pct=Avg("present_days") * 100.0 / Avg("total_days"))
            .filter(attendance_pct__lt=75)
            .order_by("attendance_pct")
        )
        at_risk = [
            {
                "student_id": s["student__id"],
                "name": f"{s['student__user__first_name']} {s['student__user__last_name']}",
                "admission_number": s["student__admission_number"],
                "attendance_percentage": round(s["attendance_pct"], 1),
                "total_days": s["total_days"],
                "present_days": s["present_days"],
            }
            for s in student_attendance[:10]  # Top 10 at-risk
        ]

        # Class-wise comparison (today)
        class_comparison = []
        classrooms = Classroom.objects.filter(school=school, grade__academic_year__is_current=True)
        for classroom in classrooms[:20]:  # Limit to 20 classes
            class_records = today_records.filter(classroom=classroom)
            class_total = class_records.count()
            if class_total > 0:
                class_present = class_records.filter(status__in=["P", "L"]).count()
                class_comparison.append(
                    {
                        "classroom_id": classroom.id,
                        "classroom_name": str(classroom),
                        "total": class_total,
                        "present": class_present,
                        "percentage": round(class_present / class_total * 100, 1),
                    }
                )

        # Leave requests pending
        pending_leaves = AttendanceLeave.objects.filter(student__school=school, status="pending").count()

        return Response(
            {
                "date": today.isoformat(),
                "total_students": total_students,
                "today": {
                    "recorded": today_total,
                    "not_recorded": max(0, total_students - today_total),
                    "percentage": today_percentage,
                    **today_breakdown,
                },
                "weekly_trend": weekly_trend,
                "at_risk_students": at_risk,
                "class_comparison": class_comparison,
                "pending_leaves": pending_leaves,
            }
        )

    @action(detail=False, methods=["get"], url_path="export")
    def export_attendance(self, request):
        """
        Export attendance data as CSV.
        Query params: date_from, date_to, classroom_id, format (csv/json)
        """
        import csv
        import io

        from services.students.models import Classroom

        school = request.user.school
        date_from = request.query_params.get("date_from", (timezone.localdate() - timedelta(days=30)).isoformat())
        date_to = request.query_params.get("date_to", timezone.localdate().isoformat())
        classroom_id = request.query_params.get("classroom_id")
        export_format = request.query_params.get("format", "csv")

        qs = (
            AttendanceRecord.objects.filter(
                classroom__school=school,
                date__gte=date_from,
                date__lte=date_to,
            )
            .select_related("student__user", "classroom")
            .order_by("date", "classroom__name", "student__user__last_name")
        )

        if classroom_id:
            try:
                classroom = Classroom.objects.get(id=classroom_id, school=school)
                qs = qs.filter(classroom=classroom)
            except Classroom.DoesNotExist:
                return Response({"error": "Classroom not found"}, status=404)

        if export_format == "json":
            data = [
                {
                    "date": r.date.isoformat(),
                    "student_name": r.student.user.full_name,
                    "admission_number": r.student.admission_number,
                    "classroom": str(r.classroom),
                    "status": r.status,
                    "remarks": r.remarks,
                }
                for r in qs
            ]
            return Response({"data": data, "count": len(data)})

        # CSV export
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Student Name", "Admission Number", "Classroom", "Status", "Remarks"])
        for r in qs:
            writer.writerow(
                [
                    r.date.isoformat(),
                    r.student.user.full_name,
                    r.student.admission_number,
                    str(r.classroom),
                    r.get_status_display(),
                    r.remarks,
                ]
            )

        response = Response(
            {"csv_data": output.getvalue(), "count": qs.count(), "date_from": date_from, "date_to": date_to}
        )
        return response

    @action(detail=False, methods=["get"], url_path="at-risk")
    def at_risk_students(self, request):
        """
        List students with attendance below threshold.
        Query params: threshold (default 75), days (default 30)
        """
        from django.db.models import Avg, Count, Q

        school = request.user.school
        threshold = float(request.query_params.get("threshold", 75))
        days = int(request.query_params.get("days", 30))
        since = timezone.localdate() - timedelta(days=days)

        student_stats = (
            AttendanceRecord.objects.filter(
                classroom__school=school,
                date__gte=since,
            )
            .values(
                "student__id",
                "student__user__first_name",
                "student__user__last_name",
                "student__admission_number",
                "classroom__name",
            )
            .annotate(
                total_days=Count("id"),
                present_days=Count("id", filter=Q(status__in=["P", "L"])),
                absent_days=Count("id", filter=Q(status="A")),
            )
            .annotate(attendance_pct=Avg("present_days") * 100.0 / Avg("total_days"))
            .filter(attendance_pct__lt=threshold)
            .order_by("attendance_pct")
        )

        at_risk = [
            {
                "student_id": s["student__id"],
                "name": f"{s['student__user__first_name']} {s['student__user__last_name']}",
                "admission_number": s["student__admission_number"],
                "classroom": s["classroom__name"],
                "attendance_percentage": round(s["attendance_pct"], 1),
                "total_days": s["total_days"],
                "present_days": s["present_days"],
                "absent_days": s["absent_days"],
            }
            for s in student_stats
        ]

        return Response(
            {
                "threshold": threshold,
                "period_days": days,
                "count": len(at_risk),
                "students": at_risk,
            }
        )

    @action(detail=False, methods=["get"], url_path="classroom-summary")
    def classroom_summary(self, request):
        """Attendance summary for a classroom on a given date."""
        from services.students.models import Classroom

        classroom_id = request.query_params.get("classroom_id")
        target_date = request.query_params.get("date", timezone.localdate().isoformat())

        if not classroom_id:
            return Response({"error": "classroom_id is required"}, status=400)

        # Tenant isolation: the classroom must belong to the caller's school.
        try:
            classroom = Classroom.objects.get(id=classroom_id, school=request.user.school)
        except Classroom.DoesNotExist:
            raise PermissionDenied("Classroom not found in your school.")

        records = AttendanceRecord.objects.filter(classroom=classroom, date=target_date).select_related("student__user")

        students_in_class = Student.objects.filter(enrollments__classroom=classroom, enrollments__is_active=True)
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
        try:
            month = int(request.query_params.get("month", timezone.localdate().month))
            year = int(request.query_params.get("year", timezone.localdate().year))
        except (TypeError, ValueError):
            return Response({"error": "month and year must be integers"}, status=400)
        if not (1 <= month <= 12):
            return Response({"error": "month must be between 1 and 12"}, status=400)

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


class PeriodAttendanceViewSet(viewsets.ModelViewSet):
    """
    Period-level attendance tracking.
    Teachers record attendance per subject/period.
    Admins can view/edit all. Students/parents are read-only.
    """

    serializer_class = PeriodAttendanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["date", "status", "assignment", "period_number"]

    def get_queryset(self):
        user = self.request.user
        qs = (
            PeriodAttendance.objects.filter(assignment__subject__school=user.school)
            .select_related("student__user", "assignment__subject", "assignment__teacher", "recorded_by")
            .order_by("-date", "-period_number", "-id")
        )

        if user.role == "student":
            return qs.filter(student__user=user)
        if user.role == "parent":
            return qs.filter(student__guardians__user=user)
        if user.role == "teacher":
            return qs.filter(assignment__teacher=user).distinct()
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "bulk_record"]:
            return [IsAuthenticated(), IsTeacher()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        record = serializer.save(recorded_by=self.request.user)
        log_attendance_change("period", record, "create", self.request.user, new_values={"status": record.status})

    def perform_update(self, serializer):
        instance = serializer.instance
        # Time-window check
        if instance.recorded_at:
            elapsed = timezone.now() - instance.recorded_at
            if elapsed.days > ATTENDANCE_EDIT_WINDOW_DAYS:
                raise PermissionDenied(f"Cannot edit attendance older than {ATTENDANCE_EDIT_WINDOW_DAYS} days.")
        old_values = {"status": instance.status}
        record = serializer.save(updated_by=self.request.user)
        new_values = {"status": record.status}
        log_attendance_change(
            "period",
            record,
            "update",
            self.request.user,
            old_values=old_values,
            new_values=new_values,
            reason=self.request.data.get("reason", ""),
        )

    @action(detail=False, methods=["post"], url_path="bulk-record")
    def bulk_record(self, request):
        """Record period attendance for multiple students in one request."""
        serializer = BulkPeriodAttendanceSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        records = serializer.save()

        return Response(
            {
                "recorded": len(records),
                "assignment": str(records[0].assignment) if records else None,
                "date": str(records[0].date) if records else None,
                "period_number": records[0].period_number if records else None,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="period-summary")
    def period_summary(self, request):
        """
        Period-wise attendance summary for a date.
        Query params: date (optional), classroom_id (optional)
        Returns breakdown by period number.
        """
        target_date = request.query_params.get("date", timezone.localdate().isoformat())
        classroom_id = request.query_params.get("classroom_id")

        qs = PeriodAttendance.objects.filter(
            assignment__subject__school=request.user.school,
            date=target_date,
        )

        if classroom_id:
            from services.students.models import Classroom

            try:
                classroom = Classroom.objects.get(id=classroom_id, school=request.user.school)
            except Classroom.DoesNotExist:
                raise PermissionDenied("Classroom not found in your school.")
            # Filter by students enrolled in this classroom
            qs = qs.filter(student__enrollments__classroom=classroom, student__enrollments__is_active=True)

        # Group by period number
        from django.db.models import Count, Q

        periods = (
            qs.values("period_number")
            .annotate(
                total=Count("id"),
                present=Count("id", filter=Q(status="P")),
                absent=Count("id", filter=Q(status="A")),
                late=Count("id", filter=Q(status="L")),
            )
            .order_by("period_number")
        )

        return Response(
            {
                "date": target_date,
                "periods": list(periods),
            }
        )

    @action(detail=False, methods=["get"], url_path="student-report")
    def student_report(self, request):
        """
        Period-wise attendance report for a student.
        Query params: student_id, month, year
        Returns breakdown by subject and period.
        """
        student_id = request.query_params.get("student_id")
        try:
            month = int(request.query_params.get("month", timezone.localdate().month))
            year = int(request.query_params.get("year", timezone.localdate().year))
        except (TypeError, ValueError):
            return Response({"error": "month and year must be integers"}, status=400)
        if not (1 <= month <= 12):
            return Response({"error": "month must be between 1 and 12"}, status=400)

        if not student_id:
            return Response({"error": "student_id is required"}, status=400)

        from services.students.models import Student

        try:
            student = Student.objects.get(id=student_id, school=request.user.school)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        records = (
            PeriodAttendance.objects.filter(
                student=student,
                date__year=year,
                date__month=month,
            )
            .select_related("assignment__subject")
            .order_by("date", "period_number")
        )

        # Aggregate by subject
        from django.db.models import Count, Q

        by_subject = (
            records.values("assignment__subject__name")
            .annotate(
                total=Count("id"),
                present=Count("id", filter=Q(status__in=["P"])),
                absent=Count("id", filter=Q(status="A")),
                late=Count("id", filter=Q(status="L")),
            )
            .order_by("assignment__subject__name")
        )

        # Overall summary
        overall = records.aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status="P")),
            absent=Count("id", filter=Q(status="A")),
            late=Count("id", filter=Q(status="L")),
        )
        total = overall["total"]
        present = overall["present"]

        return Response(
            {
                "student_id": student_id,
                "month": month,
                "year": year,
                "overall": {
                    "total_periods": total,
                    "present": present,
                    "absent": overall["absent"],
                    "late": overall["late"],
                    "percentage": round((present / total * 100) if total else 0, 2),
                },
                "by_subject": list(by_subject),
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

    def get_permissions(self):
        # Approving/rejecting leave is a staff decision — never the student
        # themselves and never a parent. Teachers are scoped to their own
        # classes via the queryset above.
        if self.action in ["approve", "reject"]:
            return [IsAuthenticated(), IsSchoolStaff()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = self.request.user
        student = serializer.validated_data.get("student")
        if student is not None:
            if student.school != user.school:
                raise PermissionDenied("You can only request leave for students in your school.")
            if user.role == "student" and student.user != user:
                raise PermissionDenied("You can only request leave for yourself.")
            if user.role == "parent" and not student.guardians.filter(user=user).exists():
                raise PermissionDenied("You can only request leave for your own children.")
        serializer.save()

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


class AttendanceChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for viewing attendance change logs.
    Supports filtering by attendance_type, attendance_id, changed_by, date range.
    """

    serializer_class = AttendanceChangeLogSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["attendance_type", "change_type", "changed_by"]

    def get_queryset(self):
        user = self.request.user
        qs = (
            AttendanceChangeLog.objects.filter(changed_by__school=user.school)
            .select_related("changed_by")
            .order_by("-changed_at")
        )

        # Filter by attendance_id if provided
        attendance_id = self.request.query_params.get("attendance_id")
        if attendance_id:
            qs = qs.filter(attendance_id=attendance_id)

        # Filter by date range if provided
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            qs = qs.filter(changed_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(changed_at__date__lte=date_to)

        return qs
