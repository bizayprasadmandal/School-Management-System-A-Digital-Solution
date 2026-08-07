"""
Gradebook Service — Views for exams, grades, assessments, report cards
"""

import logging
from decimal import Decimal
from uuid import UUID

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember, IsTeacher
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Assessment, AssessmentSubmission, Exam, Grade, ReportCard
from .serializers import (
    AssessmentSerializer,
    AssessmentSubmissionSerializer,
    BulkGradeSerializer,
    ExamSerializer,
    GradeSerializer,
    ReportCardSerializer,
)

logger = logging.getLogger(__name__)


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Exam.objects.filter(school=self.request.user.school).select_related("exam_type", "academic_year")
        academic_year = self.request.query_params.get("academic_year")
        if academic_year:
            qs = qs.filter(academic_year_id=academic_year)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "generate_report_cards", "publish_results"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"], url_path="generate-report-cards")
    def generate_report_cards(self, request, pk=None):
        """
        Compute aggregate marks, assign grade letters, rank students,
        and generate PDF report cards for all students in the exam.
        Runs as a background Celery task for large cohorts.
        """
        exam = self.get_object()
        from .tasks import generate_report_cards_task

        task = generate_report_cards_task.delay(str(exam.id))
        return Response(
            {
                "detail": "Report card generation queued.",
                "task_id": task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"], url_path="publish-results")
    def publish_results(self, request, pk=None):
        exam = self.get_object()
        updated = ReportCard.objects.filter(exam=exam, status="draft").update(
            status="published", published_at=timezone.now()
        )
        return Response({"published": updated})

    @action(detail=True, methods=["get"], url_path="leaderboard")
    def leaderboard(self, request, pk=None):
        """Top-N students by percentage for this exam."""
        exam = self.get_object()
        limit = int(request.query_params.get("limit", 10))
        report_cards = (
            ReportCard.objects.filter(exam=exam, status__in=["published", "sent"])
            .select_related("student__user")
            .order_by("rank_in_grade")[:limit]
        )
        data = [
            {
                "rank": rc.rank_in_grade,
                "student_name": rc.student.user.full_name,
                "admission_number": rc.student.admission_number,
                "percentage": float(rc.percentage),
                "grade_letter": rc.grade_letter,
                "gpa": float(rc.gpa) if rc.gpa else None,
            }
            for rc in report_cards
        ]
        return Response(data)


class GradeViewSet(viewsets.ModelViewSet):
    """Individual student grade records per exam schedule."""

    serializer_class = GradeSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        qs = Grade.objects.filter(student__school=user.school).select_related(
            "student__user", "exam_schedule__subject", "exam_schedule__exam"
        )

        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "parent":
            qs = qs.filter(student__guardians__user=user)
        elif user.role == "teacher":
            qs = qs.filter(exam_schedule__assignment__teacher=user)

        exam_id = self.request.query_params.get("exam_id")
        if exam_id:
            qs = qs.filter(exam_schedule__exam_id=exam_id)
        student_id = self.request.query_params.get("student_id")
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "bulk_submit"]:
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_submit(self, request):
        """Submit grades for all students in one exam schedule."""
        serializer = BulkGradeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        grades = serializer.save(graded_by=request.user)
        return Response(
            {"graded": len(grades), "exam_schedule_id": request.data.get("exam_schedule_id")},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        """Export grades for a given exam as CSV."""
        import csv

        exam_id = request.query_params.get("exam_id")
        if not exam_id:
            return Response({"error": "exam_id query parameter is required."}, status=400)

        user = self.request.user
        grades = (
            Grade.objects.filter(
                exam_schedule__exam_id=exam_id,
                student__school=user.school,
            )
            .select_related("student__user", "exam_schedule__subject", "exam_schedule__exam")
            .order_by("student__user__first_name", "exam_schedule__subject__name")
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="grades_exam_{exam_id}.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Admission No",
                "Student Name",
                "Subject",
                "Marks Obtained",
                "Max Marks",
                "Percentage",
                "Is Absent",
                "Remarks",
            ]
        )

        for g in grades:
            writer.writerow(
                [
                    g.student.admission_number,
                    g.student.user.full_name,
                    g.exam_schedule.subject.name,
                    g.marks_obtained if g.marks_obtained is not None else "",
                    g.exam_schedule.max_marks,
                    f"{g.percentage:.2f}" if g.percentage is not None else "",
                    "Yes" if g.is_absent else "No",
                    g.remarks or "",
                ]
            )

        return response

    @action(detail=False, methods=["post"], url_path="import-csv")
    def import_csv(self, request):
        """
        Import grades from CSV data.
        Expected CSV columns (header row required):
        admission_number, exam_schedule_id, marks_obtained, is_absent, remarks
        """
        import csv
        import io

        csv_text = request.data.get("csv_data", "")
        if not csv_text:
            return Response({"error": "csv_data field is required."}, status=400)

        from .models import ExamSchedule

        reader = csv.DictReader(io.StringIO(csv_text))
        imported = 0
        errors = []

        for row_num, row in enumerate(reader, start=2):
            try:
                admission_number = row.get("admission_number", "").strip()
                exam_schedule_id = row.get("exam_schedule_id", "").strip()
                marks_raw = row.get("marks_obtained", "").strip()

                if not admission_number or not exam_schedule_id:
                    errors.append(f"Row {row_num}: admission_number and exam_schedule_id are required")
                    continue

                # Tenant isolation: schedule must belong to the caller's school.
                schedule = ExamSchedule.objects.get(id=exam_schedule_id, exam__school=request.user.school)
                student = schedule.exam.school.students.filter(admission_number=admission_number).first()
                if not student:
                    errors.append(f"Row {row_num}: student with admission '{admission_number}' not found")
                    continue

                marks_obtained = Decimal(marks_raw) if marks_raw else None
                is_absent = row.get("is_absent", "").strip().lower() in ("yes", "true", "1")

                grade, created = Grade.objects.update_or_create(
                    student=student,
                    exam_schedule=schedule,
                    defaults={
                        "marks_obtained": marks_obtained,
                        "is_absent": is_absent,
                        "remarks": row.get("remarks", "").strip(),
                        "graded_by": request.user,
                    },
                )
                imported += 1
            except ExamSchedule.DoesNotExist:
                errors.append(
                    f"Row {row_num}: exam_schedule_id '{row.get('exam_schedule_id')}' not found in your school"
                )
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)[:100]}")

        return Response(
            {
                "imported": imported,
                "errors": errors[:20],
            }
        )


class AssessmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssessmentSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        qs = Assessment.objects.filter(assignment__teacher__school=user.school)
        if user.role == "teacher":
            qs = qs.filter(assignment__teacher=user)
        return qs.select_related("assignment__subject", "assignment__classroom")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated(), IsSchoolMember()]


class AssessmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssessmentSubmissionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        qs = AssessmentSubmission.objects.filter(student__school=user.school)
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "teacher":
            qs = qs.filter(assessment__assignment__teacher=user)
        return qs.select_related("student__user", "assessment")

    def perform_create(self, serializer):
        from services.students.models import Student

        student = Student.objects.get(user=self.request.user)
        serializer.save(student=student)


class ReportCardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReportCardSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        qs = ReportCard.objects.filter(student__school=user.school)
        if user.role == "student":
            qs = qs.filter(student__user=user, status__in=["published", "sent"])
        elif user.role == "parent":
            qs = qs.filter(student__guardians__user=user, status__in=["published", "sent"])
        student_id = self.request.query_params.get("student")
        if student_id:
            try:
                UUID(student_id, version=4)
                qs = qs.filter(student_id=student_id)
            except (ValueError, AttributeError):
                pass  # silently ignore invalid UUID strings
        return qs.select_related("student__user", "exam")

    @action(detail=True, methods=["get"], url_path="download-pdf")
    def download_pdf(self, request, pk=None):
        report_card = self.get_object()
        if report_card.pdf_file:
            return FileResponse(report_card.pdf_file.open(), content_type="application/pdf")
        return Response({"detail": "PDF not yet generated."}, status=404)
