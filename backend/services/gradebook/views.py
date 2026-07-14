"""
Gradebook Service — Views for exams, grades, assessments, report cards
"""

import io
import logging
from decimal import Decimal
from uuid import UUID
from django.db import transaction
from django.http import FileResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Exam, ExamSchedule, Grade, Assessment,
    AssessmentSubmission, ReportCard, GradingScale,
)
from .serializers import (
    ExamSerializer, ExamScheduleSerializer, GradeSerializer,
    AssessmentSerializer, AssessmentSubmissionSerializer,
    ReportCardSerializer, BulkGradeSerializer,
)
from core.permissions import IsSchoolMember, IsTeacher, IsSchoolAdmin
from core.pagination import StandardResultsSetPagination

logger = logging.getLogger(__name__)


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Exam.objects.filter(
            school=self.request.user.school
        ).select_related("exam_type", "academic_year")
        academic_year = self.request.query_params.get("academic_year")
        if academic_year:
            qs = qs.filter(academic_year_id=academic_year)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy",
                           "generate_report_cards", "publish_results"]:
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
        return Response({
            "detail": "Report card generation queued.",
            "task_id": task.id,
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["post"], url_path="publish-results")
    def publish_results(self, request, pk=None):
        exam = self.get_object()
        updated = ReportCard.objects.filter(
            exam=exam, status="draft"
        ).update(status="published", published_at=timezone.now())
        return Response({"published": updated})

    @action(detail=True, methods=["get"], url_path="leaderboard")
    def leaderboard(self, request, pk=None):
        """Top-N students by percentage for this exam."""
        exam = self.get_object()
        limit = int(request.query_params.get("limit", 10))
        report_cards = ReportCard.objects.filter(
            exam=exam, status__in=["published", "sent"]
        ).select_related("student__user").order_by("rank_in_grade")[:limit]
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
        qs = Grade.objects.filter(
            student__school=user.school
        ).select_related("student__user", "exam_schedule__subject", "exam_schedule__exam")

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
