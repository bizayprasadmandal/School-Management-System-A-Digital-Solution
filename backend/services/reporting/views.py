"""
Reporting Service — Analytics, PDF generation, and data exports
"""

import io
import logging
from datetime import date, timedelta
from decimal import Decimal

from core.permissions import IsSchoolAdmin, IsSchoolStaff
from django.core.cache import cache
from django.db.models import Avg, Count, Q, Sum
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from services.attendance.models import AttendanceRecord
from services.fees.models import FeeInvoice, Payment
from services.gradebook.models import ReportCard
from services.students.models import AcademicYear, Classroom, Student

logger = logging.getLogger(__name__)

BRAND_COLOR = colors.HexColor("#4F46E5")
ACCENT_COLOR = colors.HexColor("#E0E7FF")


class ReportingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsSchoolStaff]

    def get_permissions(self):
        """
        Read-only analytics are available to school staff (accountants and
        librarians render them on their dashboards; students/parents never
        see school-wide figures). State-changing actions (e.g. cache
        refresh) stay admin-only.
        """
        if self.action == "refresh_dashboard":
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolStaff()]

    @action(detail=False, methods=["get"], url_path="dashboard-stats")
    def dashboard_stats(self, request):
        school = request.user.school
        cache_key = f"dashboard_stats_{school.id}"

        # Try cache first; returns None on miss or if Redis is unavailable
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        logger.debug("Dashboard stats cache miss for school %s", school.id)

        today = timezone.now().date()

        total_students = Student.objects.filter(school=school, is_active=True).count()
        prev_month_students = Student.objects.filter(
            school=school,
            is_active=True,
            admission_date__lt=today.replace(day=1),
        ).count()

        # Today's attendance
        today_records = AttendanceRecord.objects.filter(student__school=school, date=today)
        today_total = today_records.count()
        today_present = today_records.filter(status__in=["P", "L"]).count()
        attendance_pct = (today_present / today_total * 100) if today_total else 0

        # Yesterday attendance
        yesterday = today - timedelta(days=1)
        yesterday_records = AttendanceRecord.objects.filter(student__school=school, date=yesterday)
        yesterday_total = yesterday_records.count()
        yesterday_present = yesterday_records.filter(status__in=["P", "L"]).count()
        yesterday_pct = (yesterday_present / yesterday_total * 100) if yesterday_total else 0

        # Fee stats
        current_month_start = today.replace(day=1)
        fees_collected = Payment.objects.filter(
            invoice__student__school=school,
            status="successful",
            paid_at__gte=current_month_start,
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

        fees_outstanding = FeeInvoice.objects.filter(
            student__school=school,
            status__in=["unpaid", "overdue", "partial"],
        ).aggregate(total=Sum("total_amount") - Sum("paid_amount"))["total"] or Decimal("0")

        from services.auth.models import User, UserRole

        total_teachers = User.objects.filter(school=school, role=UserRole.TEACHER, is_active=True).count()
        total_classrooms = Classroom.objects.filter(school=school).count()

        # Last 5 days with attendance records — present % per day for the trend chart
        attendance_days = (
            AttendanceRecord.objects.filter(student__school=school)
            .values("date")
            .annotate(
                total=Count("id"),
                present=Count("id", filter=Q(status__in=["P", "L"])),
            )
            .order_by("-date")[:5]
        )
        attendance_week = []
        for row in reversed(list(attendance_days)):
            present_pct = round(row["present"] / row["total"] * 100, 1) if row["total"] else 0
            attendance_week.append(
                {
                    "day": row["date"].strftime("%a"),
                    "present": present_pct,
                    "absent": round(100 - present_pct, 1),
                }
            )

        # Grade distribution from published report cards (current academic year)
        current_year = AcademicYear.objects.filter(school=school, is_current=True).first()
        rc_qs = ReportCard.objects.filter(
            student__school=school,
            status__in=["published", "sent"],
        )
        if current_year:
            rc_qs = rc_qs.filter(academic_year=current_year)
        grade_distribution = [
            {"name": row["grade_letter"], "value": row["count"]}
            for row in rc_qs.exclude(grade_letter="")
            .values("grade_letter")
            .annotate(count=Count("id"))
            .order_by("-count")
        ]

        student_delta = (
            ((total_students - prev_month_students) / prev_month_students * 100) if prev_month_students else 0
        )
        attendance_delta = attendance_pct - yesterday_pct

        result = {
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_classrooms": total_classrooms,
            "attendance_today_pct": round(attendance_pct, 2),
            "fees_collected_month": float(fees_collected),
            "fees_outstanding": float(fees_outstanding),
            "student_delta_pct": round(student_delta, 1),
            "attendance_delta_pct": round(attendance_delta, 1),
            "attendance_week": attendance_week,
            "grade_distribution": grade_distribution,
        }

        cache.set(cache_key, result, 300)  # 5 minute TTL
        return Response(result)

    @action(detail=False, methods=["get"], url_path="at-risk-students")
    def at_risk_students(self, request):
        """
        Identify students at academic risk: attendance below a threshold
        over the trailing window, and/or below a GPA/percentage threshold.
        Query params: attendance_threshold (default 80), days (default 30),
        academic_threshold_pct (optional).
        """
        from django.db.models import Count, Q

        school = request.user.school
        attendance_threshold = float(request.query_params.get("attendance_threshold", 80))
        days = min(int(request.query_params.get("days", 30)), 365)
        academic_threshold = request.query_params.get("academic_threshold_pct")
        academic_threshold = float(academic_threshold) if academic_threshold else None
        since = timezone.now().date() - timedelta(days=days)

        current_year = AcademicYear.objects.filter(school=school, is_current=True).first()

        # Attendance percentage per student over the window
        attendance_agg = (
            AttendanceRecord.objects.filter(student__school=school, date__gte=since)
            .values("student_id")
            .annotate(
                total=Count("id"),
                present=Count("id", filter=Q(status__in=["P", "L"])),
                absent=Count("id", filter=Q(status="A")),
            )
        )
        attendance_map = {row["student_id"]: row for row in attendance_agg}

        # Average percentage per student from report cards in the current year
        percentage_agg = {}
        if academic_threshold is not None and current_year:
            percentage_agg = dict(
                ReportCard.objects.filter(
                    student__school=school,
                    academic_year=current_year,
                )
                .values("student_id")
                .annotate(avg_pct=Avg("percentage"))
                .values_list("student_id", "avg_pct")
            )

        students = Student.objects.filter(school=school, is_active=True).select_related("user")
        at_risk = []
        for student in students.iterator(chunk_size=200):
            att = attendance_map.get(student.id)
            att_pct = None
            reasons = []
            if att and att["total"]:
                att_pct = round(att["present"] / att["total"] * 100, 2)
                if att_pct < attendance_threshold:
                    reasons.append("low_attendance")
            avg_pct = percentage_agg.get(student.id)
            if avg_pct is not None and avg_pct < academic_threshold:
                reasons.append("low_academics")
            if reasons:
                current_enrollment = (
                    student.enrollments.filter(is_active=True).select_related("classroom__grade").first()
                )
                at_risk.append(
                    {
                        "student_id": str(student.id),
                        "student_name": student.user.full_name,
                        "admission_number": student.admission_number,
                        "classroom": str(current_enrollment.classroom) if current_enrollment else None,
                        "attendance_pct": att_pct,
                        "absent_days": att["absent"] if att else 0,
                        "avg_percentage": round(float(avg_pct), 2) if avg_pct is not None else None,
                        "reasons": reasons,
                    }
                )

        at_risk.sort(key=lambda s: (s["attendance_pct"] if s["attendance_pct"] is not None else 101))
        return Response(
            {
                "threshold_attendance_pct": attendance_threshold,
                "window_days": days,
                "count": len(at_risk),
                "students": at_risk,
            }
        )

    @action(detail=False, methods=["get"], url_path="enrollment-funnel")
    def enrollment_funnel(self, request):
        """
        Admissions pipeline funnel — application counts per stage,
        with an optional intake_id filter and conversion rates.
        """
        from services.admissions.models import Application

        school = request.user.school
        qs = Application.objects.filter(school=school)
        intake_id = request.query_params.get("intake_id")
        if intake_id:
            qs = qs.filter(intake_id=intake_id)

        stages = [
            "submitted",
            "under_review",
            "shortlisted",
            "accepted",
            "enrolled",
            "rejected",
            "waitlisted",
        ]
        counts = {stage: 0 for stage in stages}
        for row in qs.values("status").annotate(n=Count("id")):
            if row["status"] in counts:
                counts[row["status"]] = row["n"]

        total = sum(counts[s] for s in ["submitted", "under_review", "shortlisted", "accepted", "enrolled"])
        funnel = [{"stage": stage, "count": counts[stage]} for stage in stages]

        return Response(
            {
                "intake_id": intake_id,
                "total_applications": total,
                "funnel": funnel,
                "conversion": {
                    "submitted_to_accepted": (
                        round(counts["accepted"] / counts["submitted"] * 100, 1) if counts["submitted"] else 0
                    ),
                    "accepted_to_enrolled": (
                        round(counts["enrolled"] / counts["accepted"] * 100, 1) if counts["accepted"] else 0
                    ),
                },
            }
        )

    @action(detail=False, methods=["get"], url_path="fee-forecast")
    def fee_forecast(self, request):
        """
        Fee collection forecast: next 90 days of expected due amounts vs
        already collected, plus trailing 3-month collection history.
        """
        school = request.user.school
        today = timezone.now().date()

        invoices = FeeInvoice.objects.filter(student__school=school)
        due_soon = invoices.filter(due_date__gte=today, due_date__lte=today + timedelta(days=90))
        overdue = invoices.filter(due_date__lt=today, status__in=["unpaid", "partial"])

        forecast = []
        for offset in (0, 30, 60):
            start = today + timedelta(days=offset)
            end = start + timedelta(days=30)
            window = due_soon.filter(due_date__gte=start, due_date__lte=end)
            forecast.append(
                {
                    "window_start": str(start),
                    "window_end": str(end),
                    "expected": float(window.aggregate(t=Sum("total_amount"))["t"] or 0),
                    "already_paid": float(window.aggregate(t=Sum("paid_amount"))["t"] or 0),
                }
            )

        history = []
        for months_ago in (1, 2, 3):
            month_start = (today.replace(day=1) - timedelta(days=months_ago * 31)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            collected = (
                Payment.objects.filter(
                    invoice__student__school=school,
                    status="successful",
                    paid_at__date__gte=month_start,
                    paid_at__date__lte=month_end,
                ).aggregate(t=Sum("amount"))["t"]
                or 0
            )
            history.append({"month": str(month_start)[:7], "collected": float(collected)})

        return Response(
            {
                "today": str(today),
                "overdue_total": float(overdue.aggregate(t=Sum("total_amount") - Sum("paid_amount"))["t"] or 0),
                "forecast_90d": forecast,
                "history_3m": history,
            }
        )

    @action(detail=False, methods=["post"], url_path="refresh-dashboard")
    def refresh_dashboard(self, request):
        """Manually invalidate the dashboard-stats cache so next request rebuilds."""
        cache_key = f"dashboard_stats_{request.user.school.id}"
        cache.delete(cache_key)
        logger.info("Dashboard stats cache invalidated by user %s", request.user.id)
        return Response({"status": "refreshed"})

    @action(detail=False, methods=["get"], url_path="attendance-report")
    def attendance_report(self, request):
        school = request.user.school
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        classroom_id = request.query_params.get("classroom_id")

        records = AttendanceRecord.objects.filter(student__school=school)
        if from_date:
            records = records.filter(date__gte=from_date)
        if to_date:
            records = records.filter(date__lte=to_date)
        if classroom_id:
            records = records.filter(classroom_id=classroom_id)

        summary = (
            records.values("date")
            .annotate(
                total=Count("id"),
                present=Count("id", filter=Q(status__in=["P", "L"])),
                absent=Count("id", filter=Q(status="A")),
                late=Count("id", filter=Q(status="L")),
                excused=Count("id", filter=Q(status="E")),
            )
            .order_by("date")
        )

        return Response(
            {
                "from_date": from_date,
                "to_date": to_date,
                "daily": list(summary),
                "totals": records.aggregate(
                    total=Count("id"),
                    present=Count("id", filter=Q(status__in=["P", "L"])),
                    absent=Count("id", filter=Q(status="A")),
                ),
            }
        )

    @action(detail=False, methods=["get"], url_path="fee-report")
    def fee_report(self, request):
        school = request.user.school
        academic_year_id = request.query_params.get("academic_year_id")

        invoices = FeeInvoice.objects.filter(student__school=school)
        if academic_year_id:
            invoices = invoices.filter(academic_year_id=academic_year_id)

        summary = {
            "total_invoiced": invoices.aggregate(t=Sum("total_amount"))["t"] or 0,
            "total_collected": invoices.aggregate(t=Sum("paid_amount"))["t"] or 0,
            "by_status": list(invoices.values("status").annotate(count=Count("id"), amount=Sum("total_amount"))),
        }
        summary["collection_rate"] = (
            float(summary["total_collected"]) / float(summary["total_invoiced"]) * 100
            if summary["total_invoiced"]
            else 0
        )
        return Response(summary)

    @action(detail=False, methods=["get"], url_path="export/attendance-pdf")
    def export_attendance_pdf(self, request):
        """Generate a PDF attendance report for a classroom."""
        school = request.user.school
        classroom_id = request.query_params.get("classroom_id")
        from_date_str = request.query_params.get("from_date", str(date.today().replace(day=1)))
        to_date_str = request.query_params.get("to_date", str(date.today()))

        classroom = Classroom.objects.get(id=classroom_id, school=school)
        records = (
            AttendanceRecord.objects.filter(
                classroom=classroom,
                date__range=[from_date_str, to_date_str],
            )
            .select_related("student__user")
            .order_by("student__user__first_name", "date")
        )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=2 * cm,
            bottomMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()
        elements = []

        # Header
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Title"],
            textColor=BRAND_COLOR,
            fontSize=18,
            spaceAfter=6,
        )
        elements.append(Paragraph(f"{school.name}", title_style))
        elements.append(
            Paragraph(
                f"Attendance Report — {classroom} | {from_date_str} to {to_date_str}",
                styles["Normal"],
            )
        )
        elements.append(HRFlowable(width="100%", thickness=1, color=BRAND_COLOR, spaceAfter=12))

        # Build data matrix
        students = (
            Student.objects.filter(enrollments__classroom=classroom, enrollments__is_active=True)
            .select_related("user")
            .order_by("user__first_name")
        )

        unique_dates = sorted(set(r.date for r in records))

        # Table header
        header = ["Student", "Adm. No."] + [d.strftime("%d/%m") for d in unique_dates] + ["P", "A", "%"]
        data = [header]

        # Status color map
        status_map: dict = {}
        for r in records:
            status_map[(r.student_id, r.date)] = r.status

        for student in students:
            row = [student.user.full_name, student.admission_number]
            present_count = 0
            absent_count = 0
            for d in unique_dates:
                status = status_map.get((student.id, d), "—")
                row.append(status)
                if status in ("P", "L"):
                    present_count += 1
                elif status == "A":
                    absent_count += 1
            total = present_count + absent_count
            pct = f"{present_count / total * 100:.0f}%" if total else "—"
            row.extend([present_count, absent_count, pct])
            data.append(row)

        col_widths = [4.5 * cm, 2.5 * cm] + [0.9 * cm] * len(unique_dates) + [1 * cm, 1 * cm, 1.2 * cm]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ALIGN", (2, 0), (-1, -1), "CENTER"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ACCENT_COLOR]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        elements.append(table)
        elements.append(Spacer(1, 1 * cm))

        # Footer
        elements.append(
            Paragraph(
                f"Generated by EduSphere SMS on {date.today().strftime('%B %d, %Y')}",
                ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey),
            )
        )

        doc.build(elements)
        buffer.seek(0)

        response = FileResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="attendance_{classroom}_{from_date_str}_{to_date_str}.pdf"'
        )
        return response

    @action(detail=False, methods=["get"], url_path="export/students-csv")
    def export_students_csv(self, request):
        """Export student list as CSV."""
        import csv

        school = request.user.school
        students = (
            Student.objects.filter(school=school, is_active=True)
            .select_related("user")
            .prefetch_related("enrollments__classroom__grade")
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="students.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Admission No",
                "Full Name",
                "Email",
                "Gender",
                "Date of Birth",
                "Grade",
                "Classroom",
                "Admission Date",
                "Status",
            ]
        )

        for student in students:
            current_enrollment = student.enrollments.filter(is_active=True).first()
            writer.writerow(
                [
                    student.admission_number,
                    student.user.full_name,
                    student.user.email,
                    student.get_gender_display(),
                    student.date_of_birth.strftime("%Y-%m-%d"),
                    current_enrollment.classroom.grade.name if current_enrollment else "",
                    str(current_enrollment.classroom) if current_enrollment else "",
                    student.admission_date.strftime("%Y-%m-%d"),
                    "Active" if student.is_active else "Inactive",
                ]
            )

        return response
