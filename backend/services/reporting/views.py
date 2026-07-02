"""
Reporting Service — Analytics, PDF generation, and data exports
"""

import io
import logging
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Count, Avg, Sum, Q
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, HRFlowable,
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

from core.permissions import IsSchoolAdmin, IsSchoolMember
from services.students.models import Student, Classroom, AcademicYear
from services.attendance.models import AttendanceRecord
from services.gradebook.models import Grade, ReportCard, Exam
from services.fees.models import FeeInvoice, Payment

logger = logging.getLogger(__name__)

BRAND_COLOR = colors.HexColor("#4F46E5")
ACCENT_COLOR = colors.HexColor("#E0E7FF")


class ReportingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsSchoolMember]

    @action(detail=False, methods=["get"], url_path="dashboard-stats")
    def dashboard_stats(self, request):
        school = request.user.school
        today = timezone.now().date()

        total_students = Student.objects.filter(school=school, is_active=True).count()
        prev_month_students = Student.objects.filter(
            school=school,
            is_active=True,
            admission_date__lt=today.replace(day=1),
        ).count()

        # Today's attendance
        today_records = AttendanceRecord.objects.filter(
            student__school=school, date=today
        )
        today_total = today_records.count()
        today_present = today_records.filter(status__in=["P", "L"]).count()
        attendance_pct = (today_present / today_total * 100) if today_total else 0

        # Yesterday attendance
        yesterday = today - timedelta(days=1)
        yesterday_records = AttendanceRecord.objects.filter(
            student__school=school, date=yesterday
        )
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

        from services.academics.models import TeacherProfile
        total_teachers = TeacherProfile.objects.filter(school=school, is_active=True).count()
        total_classrooms = Classroom.objects.filter(school=school).count()

        student_delta = (
            ((total_students - prev_month_students) / prev_month_students * 100)
            if prev_month_students else 0
        )
        attendance_delta = attendance_pct - yesterday_pct

        return Response({
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_classrooms": total_classrooms,
            "attendance_today_pct": round(attendance_pct, 2),
            "fees_collected_month": float(fees_collected),
            "fees_outstanding": float(fees_outstanding),
            "student_delta_pct": round(student_delta, 1),
            "attendance_delta_pct": round(attendance_delta, 1),
        })

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

        summary = records.values("date").annotate(
            total=Count("id"),
            present=Count("id", filter=Q(status__in=["P", "L"])),
            absent=Count("id", filter=Q(status="A")),
            late=Count("id", filter=Q(status="L")),
            excused=Count("id", filter=Q(status="E")),
        ).order_by("date")

        return Response({
            "from_date": from_date,
            "to_date": to_date,
            "daily": list(summary),
            "totals": records.aggregate(
                total=Count("id"),
                present=Count("id", filter=Q(status__in=["P", "L"])),
                absent=Count("id", filter=Q(status="A")),
            ),
        })

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
            "by_status": list(
                invoices.values("status").annotate(
                    count=Count("id"), amount=Sum("total_amount")
                )
            ),
        }
        summary["collection_rate"] = (
            float(summary["total_collected"]) / float(summary["total_invoiced"]) * 100
            if summary["total_invoiced"] else 0
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
        records = AttendanceRecord.objects.filter(
            classroom=classroom,
            date__range=[from_date_str, to_date_str],
        ).select_related("student__user").order_by("student__user__first_name", "date")

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
            "Title", parent=styles["Title"],
            textColor=BRAND_COLOR, fontSize=18, spaceAfter=6,
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
        students = Student.objects.filter(
            enrollments__classroom=classroom, enrollments__is_active=True
        ).select_related("user").order_by("user__first_name")

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
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (2, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ACCENT_COLOR]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
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
        students = Student.objects.filter(school=school, is_active=True).select_related(
            "user"
        ).prefetch_related("enrollments__classroom__grade")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="students.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Admission No", "Full Name", "Email", "Gender", "Date of Birth",
            "Grade", "Classroom", "Admission Date", "Status",
        ])

        for student in students:
            current_enrollment = student.enrollments.filter(is_active=True).first()
            writer.writerow([
                student.admission_number,
                student.user.full_name,
                student.user.email,
                student.get_gender_display(),
                student.date_of_birth.strftime("%Y-%m-%d"),
                current_enrollment.classroom.grade.name if current_enrollment else "",
                str(current_enrollment.classroom) if current_enrollment else "",
                student.admission_date.strftime("%Y-%m-%d"),
                "Active" if student.is_active else "Inactive",
            ])

        return response
