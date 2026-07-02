"""
Gradebook Celery tasks — Report card generation, grade computation
"""

import io
import logging
from decimal import Decimal
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def generate_report_cards_task(self, exam_id: str):
    """
    Full report card pipeline:
    1. Aggregate grades per student
    2. Compute percentage, GPA, grade letter
    3. Rank within class and grade
    4. Generate PDF
    5. Update ReportCard records
    """
    try:
        from .models import Exam, Grade, ReportCard, GradingScale
        from services.students.models import Enrollment

        exam = Exam.objects.select_related("school", "academic_year").get(id=exam_id)
        school = exam.school
        grading_scale = GradingScale.objects.filter(
            school=school, is_default=True
        ).prefetch_related("entries").first()

        schedules = exam.schedules.select_related("subject", "classroom")
        classroom_ids = schedules.values_list("classroom_id", flat=True).distinct()

        total_created = 0
        for classroom_id in classroom_ids:
            enrollments = Enrollment.objects.filter(
                classroom_id=classroom_id,
                academic_year=exam.academic_year,
                is_active=True,
            ).select_related("student__user")

            student_results = []
            for enrollment in enrollments:
                student = enrollment.student
                student_grades = Grade.objects.filter(
                    student=student,
                    exam_schedule__exam=exam,
                    exam_schedule__classroom_id=classroom_id,
                )
                total_marks = sum(g.exam_schedule.max_marks for g in student_grades)
                obtained_marks = sum(
                    g.marks_obtained for g in student_grades
                    if g.marks_obtained and not g.is_absent
                ) or Decimal("0")

                pct = (obtained_marks / total_marks * 100) if total_marks else Decimal("0")
                grade_letter, gpa = _compute_grade(pct, grading_scale)

                student_results.append({
                    "student": student,
                    "total_marks": total_marks,
                    "obtained_marks": obtained_marks,
                    "percentage": pct,
                    "grade_letter": grade_letter,
                    "gpa": gpa,
                })

            # Sort by percentage descending for ranking
            student_results.sort(key=lambda x: x["percentage"], reverse=True)

            for rank, result in enumerate(student_results, start=1):
                report_card, _ = ReportCard.objects.update_or_create(
                    student=result["student"],
                    exam=exam,
                    defaults={
                        "academic_year": exam.academic_year,
                        "total_marks": result["total_marks"],
                        "obtained_marks": result["obtained_marks"],
                        "percentage": result["percentage"],
                        "grade_letter": result["grade_letter"],
                        "gpa": result["gpa"],
                        "rank_in_class": rank,
                        "status": "draft",
                        "generated_at": timezone.now(),
                    },
                )
                # Generate PDF
                pdf_buffer = _generate_pdf(report_card, result, exam)
                if pdf_buffer:
                    from django.core.files.base import ContentFile
                    report_card.pdf_file.save(
                        f"report_card_{report_card.student.admission_number}_{exam_id[:8]}.pdf",
                        ContentFile(pdf_buffer.read()),
                        save=True,
                    )
                total_created += 1

        logger.info("Generated %d report cards for exam %s", total_created, exam_id)
        return {"exam_id": exam_id, "report_cards_generated": total_created}

    except Exception as exc:
        logger.error("Report card generation failed for exam %s: %s", exam_id, exc)
        raise self.retry(exc=exc)


def _compute_grade(pct: Decimal, scale):
    """Return (letter_grade, gpa_points) for a given percentage."""
    if scale is None:
        # Default fallback scale
        if pct >= 90: return "A+", Decimal("4.0")
        if pct >= 80: return "A",  Decimal("3.7")
        if pct >= 70: return "B+", Decimal("3.3")
        if pct >= 60: return "B",  Decimal("3.0")
        if pct >= 50: return "C",  Decimal("2.0")
        if pct >= 40: return "D",  Decimal("1.0")
        return "F", Decimal("0.0")

    for entry in scale.entries.all():
        if entry.min_percentage <= pct <= entry.max_percentage:
            return entry.grade_letter, entry.grade_point
    return "F", Decimal("0.0")


def _generate_pdf(report_card, result, exam) -> io.BytesIO:
    """Generate a styled A4 PDF report card using ReportLab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table,
            TableStyle, HRFlowable,
        )

        BRAND = colors.HexColor("#4F46E5")
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            rightMargin=2 * cm, leftMargin=2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title", parent=styles["Title"],
            textColor=BRAND, fontSize=20, spaceAfter=4,
        )
        sub_style = ParagraphStyle(
            "Sub", parent=styles["Normal"],
            fontSize=10, textColor=colors.grey,
        )
        heading_style = ParagraphStyle(
            "Heading", parent=styles["Heading2"],
            textColor=BRAND, fontSize=12, spaceBefore=12, spaceAfter=6,
        )

        elems = []
        school = report_card.student.school
        student = report_card.student

        # School header
        elems.append(Paragraph(school.name, title_style))
        elems.append(Paragraph(f"{school.address} · {school.email}", sub_style))
        elems.append(HRFlowable(width="100%", thickness=2, color=BRAND, spaceAfter=12))

        # Report card title
        elems.append(Paragraph(
            f"<b>REPORT CARD — {exam.name.upper()}</b>", heading_style
        ))

        # Student info table
        info_data = [
            ["Student Name", student.user.full_name, "Admission No.", student.admission_number],
            ["Class",
             str(student.enrollments.filter(is_active=True).first().classroom if student.enrollments.filter(is_active=True).exists() else "—"),
             "Academic Year", report_card.academic_year.name],
            ["Date of Birth", student.date_of_birth.strftime("%B %d, %Y"), "Gender",
             student.get_gender_display()],
        ]
        info_table = Table(info_data, colWidths=[4 * cm, 7 * cm, 4 * cm, 4 * cm])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elems.append(info_table)
        elems.append(Spacer(1, 0.5 * cm))

        # Results summary box
        elems.append(Paragraph("Results Summary", heading_style))
        summary_data = [
            ["Total Marks", "Marks Obtained", "Percentage", "Grade", "Rank"],
            [
                str(result["total_marks"]),
                str(result["obtained_marks"]),
                f"{result['percentage']:.1f}%",
                result["grade_letter"],
                f"#{report_card.rank_in_class}" if report_card.rank_in_class else "—",
            ],
        ]
        summary_table = Table(summary_data, colWidths=[3.8 * cm] * 5)
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#eef2ff")]),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        elems.append(summary_table)
        elems.append(Spacer(1, 0.5 * cm))

        # Footer
        elems.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        elems.append(Spacer(1, 0.3 * cm))
        elems.append(Paragraph(
            f"Generated by EduSphere SMS · {timezone.now().strftime('%B %d, %Y')}",
            ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey),
        ))

        doc.build(elems)
        buffer.seek(0)
        return buffer

    except Exception as e:
        logger.error("PDF generation failed for report card %s: %s", report_card.id, e)
        return None


@shared_task
def generate_bulk_invoices(structure_id: int, academic_year_id: int):
    """Generate fee invoices for all students in a grade."""
    from services.fees.models import FeeStructure, FeeInvoice
    from services.students.models import Enrollment
    import uuid

    structure = FeeStructure.objects.select_related("grade", "academic_year").get(id=structure_id)
    enrollments = Enrollment.objects.filter(
        classroom__grade=structure.grade,
        academic_year_id=academic_year_id,
        is_active=True,
    ).select_related("student")

    created = 0
    for enrollment in enrollments:
        due_date = structure.academic_year.start_date.replace(day=structure.due_day)
        _, new = FeeInvoice.objects.get_or_create(
            student=enrollment.student,
            fee_structure=structure,
            academic_year_id=academic_year_id,
            defaults={
                "invoice_number": f"INV-{uuid.uuid4().hex[:8].upper()}",
                "due_date": due_date,
                "base_amount": structure.amount,
                "total_amount": structure.amount,
                "status": "unpaid",
            },
        )
        if new:
            created += 1

    logger.info(
        "Generated %d invoices for structure %d, academic_year %d",
        created, structure_id, academic_year_id,
    )
    return {"created": created, "structure_id": structure_id}
