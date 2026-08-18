"""
Gradebook Service — Views for exams, grades, assessments, report cards
"""

import logging
from decimal import Decimal
from uuid import UUID

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember, IsSchoolStaff, IsStudent, IsTeacher
from django.db.models import Count
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Assessment, AssessmentSubmission, Exam, ExamSchedule, Grade, GradeChangeProposal, ReportCard
from .serializers import (
    AssessmentSerializer,
    AssessmentSubmissionSerializer,
    BulkGradeSerializer,
    ExamScheduleSerializer,
    ExamSerializer,
    GradeChangeProposalSerializer,
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
        return qs.annotate(schedule_count=Count("schedules"))

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

    @action(detail=True, methods=["get"], url_path="schedules")
    def schedules(self, request, pk=None):
        """Exam schedules (subject/classroom) for the teacher gradebook selector."""
        exam = self.get_object()
        qs = ExamSchedule.objects.filter(exam=exam).select_related("subject", "classroom")
        classroom_id = request.query_params.get("classroom_id")
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
        return Response(ExamScheduleSerializer(qs, many=True).data)

    @action(detail=True, methods=["get"], url_path="leaderboard")
    def leaderboard(self, request, pk=None):
        """Top-N students by percentage for this exam."""
        exam = self.get_object()
        try:
            limit = int(request.query_params.get("limit", 10))
        except (TypeError, ValueError):
            limit = 10
        limit = min(max(limit, 1), 50)
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
            # Teachers may grade exams they invigilate or teach the subject for.
            from django.db.models import Q

            qs = qs.filter(
                Q(exam_schedule__invigilator=user) | Q(exam_schedule__subject__assignments__teacher=user)
            ).distinct()

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
        if self.action == "history":
            return [IsAuthenticated(), IsSchoolAdmin()]
        if self.action == "export_csv":
            return [IsAuthenticated(), IsSchoolStaff()]
        if self.action == "import_csv":
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        grade = serializer.save()
        from .models import record_grade_change

        record_grade_change(grade, "create", self.request.user)

    def create(self, request, *args, **kwargs):
        """Adding a grade to a published exam goes through admin approval too."""
        from .models import create_grade_change_proposal, grade_change_requires_approval

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.validated_data.get("student")
        exam_schedule = serializer.validated_data.get("exam_schedule")
        if student is not None and exam_schedule is not None and grade_change_requires_approval(student, exam_schedule):
            proposal = create_grade_change_proposal(
                student=student,
                exam_schedule=exam_schedule,
                action="create",
                grade=None,
                new_values=serializer.validated_data,
                proposed_by=request.user,
            )
            return Response(
                {
                    "status": "pending_approval",
                    "proposal_id": str(proposal.id),
                    "detail": "Grade addition submitted for admin approval.",
                },
                status=status.HTTP_202_ACCEPTED,
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Edits to a grade on a *published* exam are routed to an admin approval
        proposal instead of being applied directly. Unpublished grades behave
        as before (direct update + audit trail).
        """
        from .models import create_grade_change_proposal, grade_change_requires_approval

        instance = self.get_object()
        if grade_change_requires_approval(instance.student, instance.exam_schedule):
            serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop("partial", False))
            serializer.is_valid(raise_exception=True)
            proposal = create_grade_change_proposal(
                student=instance.student,
                exam_schedule=instance.exam_schedule,
                action="update",
                grade=instance,
                new_values=serializer.validated_data,
                proposed_by=request.user,
            )
            return Response(
                {
                    "status": "pending_approval",
                    "proposal_id": str(proposal.id),
                    "detail": "Grade change submitted for admin approval.",
                },
                status=status.HTTP_202_ACCEPTED,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Deleting a grade on a published exam also requires admin approval."""
        from .models import create_grade_change_proposal, grade_change_requires_approval

        instance = self.get_object()
        if grade_change_requires_approval(instance.student, instance.exam_schedule):
            proposal = create_grade_change_proposal(
                student=instance.student,
                exam_schedule=instance.exam_schedule,
                action="delete",
                grade=instance,
                proposed_by=request.user,
                reason=request.data.get("reason", "") if isinstance(request.data, dict) else "",
            )
            return Response(
                {
                    "status": "pending_approval",
                    "proposal_id": str(proposal.id),
                    "detail": "Grade deletion submitted for admin approval.",
                },
                status=status.HTTP_202_ACCEPTED,
            )
        return super().destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        # Snapshot pre-mutation values for the audit trail.
        # ``serializer.instance`` is mutated in place by save(), so copy the
        # attribute values first.
        import copy

        old = copy.copy(serializer.instance)
        grade = serializer.save()
        from .models import record_grade_change

        record_grade_change(grade, "update", self.request.user, old=old)

    def perform_destroy(self, instance):
        from .models import record_grade_change

        record_grade_change(instance, "delete", self.request.user, old=instance)
        instance.delete()

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        """
        Immutable audit trail of all grade mutations in this school.
        Filters: student_id, exam_schedule_id, action, limit.
        """
        from .models import GradeChangeLog

        qs = GradeChangeLog.objects.filter(student__school=request.user.school).select_related(
            "student__user", "exam_schedule__subject", "changed_by"
        )

        student_id = request.query_params.get("student_id")
        if student_id:
            qs = qs.filter(student_id=student_id)
        exam_schedule_id = request.query_params.get("exam_schedule_id")
        if exam_schedule_id:
            qs = qs.filter(exam_schedule_id=exam_schedule_id)
        action = request.query_params.get("action")
        if action:
            qs = qs.filter(action=action)

        try:
            limit = int(request.query_params.get("limit", 100))
        except (TypeError, ValueError):
            limit = 100
        limit = min(max(limit, 1), 500)
        qs = qs[:limit]

        data = [
            {
                "id": str(entry.id),
                "student": str(entry.student_id),
                "student_name": entry.student.user.full_name,
                "admission_number": entry.student.admission_number,
                "subject": entry.exam_schedule.subject.name,
                "action": entry.action,
                "marks_obtained_old": float(entry.marks_obtained_old) if entry.marks_obtained_old is not None else None,
                "marks_obtained_new": float(entry.marks_obtained_new) if entry.marks_obtained_new is not None else None,
                "is_absent_old": entry.is_absent_old,
                "is_absent_new": entry.is_absent_new,
                "changed_by": entry.changed_by.full_name if entry.changed_by else None,
                "changed_at": entry.changed_at.isoformat(),
            }
            for entry in qs
        ]
        return Response(data)

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_submit(self, request):
        """
        Submit grades for all students in one exam schedule.
        Entries for published exams become pending proposals; the rest are
        applied directly and logged.
        """
        from django.db import transaction

        from .models import create_grade_change_proposal, grade_change_requires_approval, record_grade_change

        serializer = BulkGradeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        schedule = serializer.validated_data["exam_schedule_id"]

        graded = 0
        pending = 0
        with transaction.atomic():
            for entry in serializer.validated_data["grades"]:
                student_id = entry["student_id"]
                student = schedule.exam.school.students.filter(id=student_id).first()
                if not student:
                    continue  # validated by caller; skip defensively

                existing = Grade.objects.filter(student=student, exam_schedule=schedule).first()
                new_values = {
                    "marks_obtained": entry.get("marks_obtained"),
                    "is_absent": entry.get("is_absent", False),
                    "remarks": entry.get("remarks", ""),
                }

                if grade_change_requires_approval(student, schedule):
                    create_grade_change_proposal(
                        student=student,
                        exam_schedule=schedule,
                        action="update" if existing else "create",
                        grade=existing,
                        new_values=new_values,
                        proposed_by=request.user,
                    )
                    pending += 1
                    continue

                marks = new_values["marks_obtained"]
                grade, created = Grade.objects.update_or_create(
                    student=student,
                    exam_schedule=schedule,
                    defaults={
                        "marks_obtained": Decimal(str(marks)) if marks is not None else None,
                        "is_absent": new_values["is_absent"],
                        "remarks": new_values["remarks"] or "",
                        "graded_by": request.user,
                    },
                )
                record_grade_change(
                    grade,
                    "create" if created else "update",
                    request.user,
                    old=existing if existing is not None else None,
                )
                graded += 1

        return Response(
            {
                "graded": graded,
                "pending_approval": pending,
                "exam_schedule_id": request.data.get("exam_schedule_id"),
            },
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

        from .models import ExamSchedule, create_grade_change_proposal, grade_change_requires_approval

        reader = csv.DictReader(io.StringIO(csv_text))
        imported = 0
        pending = 0
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

                existing = Grade.objects.filter(student=student, exam_schedule=schedule).first()

                if grade_change_requires_approval(student, schedule):
                    create_grade_change_proposal(
                        student=student,
                        exam_schedule=schedule,
                        action="update" if existing else "create",
                        grade=existing,
                        new_values={
                            "marks_obtained": marks_obtained,
                            "is_absent": is_absent,
                            "remarks": row.get("remarks", "").strip(),
                        },
                        proposed_by=request.user,
                    )
                    pending += 1
                    continue

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
                from .models import record_grade_change

                record_grade_change(
                    grade,
                    "create" if created else "update",
                    request.user,
                    old=existing if existing is not None else None,
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
                "pending_approval": pending,
                "errors": errors[:20],
            }
        )


class GradeChangeProposalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin review queue for grade changes proposed on published exams.
    Approving applies the change (and writes it to the immutable audit
    trail); rejecting leaves the grade untouched.
    """

    serializer_class = GradeChangeProposalSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        qs = GradeChangeProposal.objects.filter(student__school=self.request.user.school).select_related(
            "student__user", "exam_schedule__subject", "exam_schedule__exam", "grade", "proposed_by", "reviewed_by"
        )
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        exam_id = self.request.query_params.get("exam_id")
        if exam_id:
            qs = qs.filter(exam_schedule__exam_id=exam_id)
        student_id = self.request.query_params.get("student_id")
        if student_id:
            qs = qs.filter(student_id=student_id)
        return qs

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request, pk=None):
        """Apply the proposed change and append it to the audit trail."""
        import copy

        from django.db import transaction

        from .models import record_grade_change

        proposal = self.get_object()
        if proposal.status != GradeChangeProposal.Status.PROPOSED:
            return Response(
                {"detail": f"Proposal is already {proposal.get_status_display()}."}, status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            if proposal.action == GradeChangeProposal.Action.DELETE:
                grade = proposal.grade
                record_grade_change(grade, "delete", request.user, old=grade)
                grade.delete()
                # Detach so the review record survives (FK is SET_NULL).
                proposal.grade = None
            elif proposal.action == GradeChangeProposal.Action.CREATE:
                # A create proposal may omit is_absent; the grade field is non-null.
                grade = Grade.objects.create(
                    student=proposal.student,
                    exam_schedule=proposal.exam_schedule,
                    marks_obtained=proposal.marks_obtained_new,
                    is_absent=bool(proposal.is_absent_new),
                    remarks=proposal.remarks_new,
                    graded_by=request.user,
                )
                record_grade_change(grade, "create", request.user)
            else:  # update
                grade = proposal.grade
                old = copy.copy(grade)
                grade.marks_obtained = proposal.marks_obtained_new
                if proposal.is_absent_new is not None:
                    grade.is_absent = proposal.is_absent_new
                if proposal.remarks_new:
                    grade.remarks = proposal.remarks_new
                grade.graded_by = request.user
                grade.save()
                record_grade_change(grade, "update", request.user, old=old)

            proposal.status = GradeChangeProposal.Status.APPROVED
            proposal.reviewed_by = request.user
            proposal.reviewed_at = timezone.now()
            proposal.save()

        return Response({"status": "approved", "detail": "Grade change applied."})

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """Reject the proposed change; the grade stays as-is."""
        proposal = self.get_object()
        if proposal.status != GradeChangeProposal.Status.PROPOSED:
            return Response(
                {"detail": f"Proposal is already {proposal.get_status_display()}."}, status=status.HTTP_400_BAD_REQUEST
            )

        proposal.status = GradeChangeProposal.Status.REJECTED
        proposal.reviewed_by = request.user
        proposal.reviewed_at = timezone.now()
        proposal.review_notes = request.data.get("notes", "")[:500]
        proposal.save()

        return Response({"status": "rejected", "detail": "Grade change rejected."})


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

    def get_permissions(self):
        # Only the student themself may submit; only teachers/admins may grade
        # (set marks). This closes the self-grading hole where a student could
        # POST a submission with marks_obtained pre-filled.
        if self.action == "create":
            return [IsAuthenticated(), IsStudent()]
        if self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), IsTeacher()]
        if self.action == "destroy":
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        from services.students.models import Student

        user = self.request.user
        student = Student.objects.filter(user=user).first()
        if student is None:
            raise PermissionDenied("No student profile found for your account.")

        # Tenant isolation on the write path: the assessment must belong to the
        # student's own school (assessment -> assignment -> teacher.school).
        assessment = serializer.validated_data.get("assessment")
        if assessment is not None and assessment.assignment.teacher.school_id != student.school_id:
            raise PermissionDenied("Assessment not found in your school.")

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
