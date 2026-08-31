"""
Academics Service — Views for subjects, teacher assignments, lesson plans, student-subject enrollments
"""

from decimal import Decimal
from uuid import uuid4

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember, IsTeacher
from django.db import models, transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from services.auth.models import User
from services.students.models import Student

from .models import (
    AcademicEvent,
    AcademicHoliday,
    AcademicNotification,
    AcademicTerm,
    AcademicTranscript,
    Assignment,
    AssignmentSubmission,
    CurriculumStandard,
    EvaluationCriteria,
    EvaluationScore,
    EvaluationTemplate,
    ExamPaper,
    HomeworkTracker,
    LessonPlan,
    QuestionBank,
    StudentProgressReport,
    StudentSubjectEnrollment,
    Subject,
    SubjectPerformance,
    SubjectStandardMapping,
    Syllabus,
    SyllabusTopic,
    TeacherAssignment,
    TeacherEffectiveness,
    TeacherEvaluation,
    TeacherProfile,
    TeacherWorkloadConfig,
    TeacherWorkloadSnapshot,
)
from .serializers import (
    AcademicEventSerializer,
    AcademicHolidaySerializer,
    AcademicNotificationSerializer,
    AcademicTermSerializer,
    AcademicTranscriptSerializer,
    AssignmentSerializer,
    AssignmentSubmissionSerializer,
    CurriculumStandardSerializer,
    EvaluationCommentSerializer,
    EvaluationCriteriaSerializer,
    EvaluationTemplateSerializer,
    ExamPaperSerializer,
    HomeworkTrackerSerializer,
    LessonPlanSerializer,
    QuestionBankSerializer,
    StudentProgressReportSerializer,
    StudentSubjectEnrollmentSerializer,
    SubjectPerformanceSerializer,
    SubjectSerializer,
    SubjectStandardMappingSerializer,
    SyllabusSerializer,
    SyllabusTopicSerializer,
    TeacherAssignmentSerializer,
    TeacherEffectivenessSerializer,
    TeacherEvaluationSerializer,
    TeacherProfileSerializer,
    TeacherWorkloadConfigSerializer,
    TeacherWorkloadSnapshotSerializer,
    TeacherWorkloadSummarySerializer,
)


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["grade", "is_core", "is_elective", "is_active"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "grade__level"]
    ordering = ["grade__level", "name"]

    def get_queryset(self):
        return Subject.objects.filter(school=self.request.user.school).select_related("grade")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherAssignmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["teacher", "subject", "classroom", "academic_year"]

    def get_queryset(self):
        user = self.request.user
        qs = TeacherAssignment.objects.filter(teacher__school=user.school).select_related(
            "teacher", "subject", "classroom__grade", "academic_year"
        )
        if user.role == "teacher":
            qs = qs.filter(teacher=user)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=False, methods=["get"], url_path="my-assignments")
    def my_assignments(self, request):
        qs = self.get_queryset().filter(teacher=request.user)
        return Response(TeacherAssignmentSerializer(qs, many=True).data)


class TeacherProfileViewSet(viewsets.ModelViewSet):
    serializer_class = TeacherProfileSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["user__first_name", "user__last_name", "employee_id", "department"]
    filterset_fields = ["is_active", "qualification", "department"]

    def get_queryset(self):
        from services.students.models import AcademicYear

        current_year = AcademicYear.objects.filter(school=self.request.user.school, is_current=True).first()
        qs = TeacherProfile.objects.filter(school=self.request.user.school).select_related("user")
        # Prefetch current year's assignments to avoid N+1 in serializer
        if current_year:
            from django.db.models import Prefetch
            from services.academics.models import TeacherAssignment

            qs = qs.prefetch_related(
                Prefetch(
                    "user__assignments",
                    queryset=TeacherAssignment.objects.filter(academic_year=current_year).select_related(
                        "subject", "classroom__grade", "academic_year"
                    ),
                )
            )
        return qs

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def my_profile(self, request):
        """
        GET: Return the current teacher's own profile.
        PATCH: Update limited self-service fields (qualification, specialization,
               department, experience_years, bio).
        """
        try:
            profile = TeacherProfile.objects.get(user=request.user, school=request.user.school)
        except TeacherProfile.DoesNotExist:
            return Response({"detail": "Teacher profile not found."}, status=404)

        if request.method == "PATCH":
            from .serializers import TeacherSelfProfileSerializer

            serializer = TeacherSelfProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(TeacherProfileSerializer(profile).data)

        return Response(TeacherProfileSerializer(profile).data)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "import_csv"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=False, methods=["post"], url_path="import-csv")
    def import_csv(self, request):
        """
        Bulk-import teachers from CSV data.
        Expected CSV columns (header row required):
        email, first_name, last_name, employee_id, gender, qualification,
        joining_date, department, specialization, address, salary, password

        - ``email``, ``first_name``, ``last_name`` and ``joining_date`` are required.
        - ``gender`` is M/F/O, ``qualification`` is diploma/bachelor/master/phd.
        - ``password`` is optional — a secure random password is generated and
          returned per teacher when omitted.
        """
        import csv
        import io

        from django.db import transaction
        from services.auth.models import User, UserRole
        from services.auth.utils import generate_secure_password

        csv_text = request.data.get("csv_data", "")
        if not csv_text:
            return Response({"error": "csv_data field is required."}, status=400)

        school = request.user.school
        reader = csv.DictReader(io.StringIO(csv_text))
        max_records = int(request.data.get("max_records", 100))
        imported = 0
        errors = []
        generated_passwords = {}
        row_count = 0

        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                if row_count >= max_records:
                    errors.append(f"Row {row_num}: Max records ({max_records}) reached, skipping remaining")
                    break
                try:
                    email = (row.get("email") or "").strip().lower()
                    first_name = (row.get("first_name") or "").strip()
                    last_name = (row.get("last_name") or "").strip()
                    joining_date = (row.get("joining_date") or "").strip()
                    if not email or not first_name or not last_name:
                        errors.append(f"Row {row_num}: email, first_name and last_name are required")
                        continue
                    if User.objects.filter(email=email).exists():
                        errors.append(f"Row {row_num}: email '{email}' already exists")
                        continue

                    employee_id = (row.get("employee_id") or "").strip() or f"EMP-{uuid4().hex[:6].upper()}"
                    if TeacherProfile.objects.filter(employee_id=employee_id).exists():
                        errors.append(f"Row {row_num}: employee_id '{employee_id}' already exists")
                        continue

                    password = (row.get("password") or "").strip()
                    generated = not password
                    if generated:
                        password = generate_secure_password()

                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        role=UserRole.TEACHER,
                        school=school,
                    )
                    TeacherProfile.objects.create(
                        user=user,
                        school=school,
                        employee_id=employee_id,
                        gender=((row.get("gender") or "O").strip().upper()[:1] or "O"),
                        qualification=((row.get("qualification") or "bachelor").strip().lower() or "bachelor"),
                        specialization=(row.get("specialization") or "").strip(),
                        joining_date=joining_date or "2024-01-01",
                        department=(row.get("department") or "").strip(),
                        address=(row.get("address") or "").strip(),
                        salary=(row.get("salary") or None),
                    )
                    if generated:
                        generated_passwords[email] = password
                    imported += 1
                    row_count += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)[:100]}")

        return Response({"imported": imported, "errors": errors[:20], "generated_passwords": generated_passwords})


class LessonPlanViewSet(viewsets.ModelViewSet):
    serializer_class = LessonPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["assignment", "status", "date"]
    search_fields = ["title", "topic"]

    def get_queryset(self):
        user = self.request.user
        qs = LessonPlan.objects.filter(assignment__teacher__school=user.school).select_related(
            "assignment__teacher", "assignment__subject", "assignment__classroom"
        )
        if user.role == "teacher":
            qs = qs.filter(assignment__teacher=user)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "approve"]:
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        plan = self.get_object()
        if request.user.role not in ["school_admin", "super_admin"]:
            return Response({"detail": "Only admins can approve lesson plans."}, status=403)
        plan.status = "approved"
        plan.save(update_fields=["status"])
        return Response({"status": "approved"})


class StudentSubjectEnrollmentViewSet(viewsets.ModelViewSet):
    """CRUD for student-subject enrollments.

    Supports filtering by student, subject, academic_year, and status.
    Teachers see only enrollments for their own subjects.
    Admins see all enrollments for their school.
    """

    serializer_class = StudentSubjectEnrollmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["student", "subject", "academic_year", "status"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "student__admission_number",
        "subject__name",
        "subject__code",
    ]
    ordering_fields = ["enrolled_date", "created_at"]
    ordering = ["-enrolled_date"]

    def get_queryset(self):
        user = self.request.user
        qs = StudentSubjectEnrollment.objects.filter(subject__school=user.school).select_related(
            "student__user",
            "subject__grade",
            "academic_year",
        )
        if user.role == "teacher":
            qs = qs.filter(subject__assignments__teacher=user).distinct()
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "bulk_enroll"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=["post"], url_path="bulk-enroll")
    def bulk_enroll(self, request):
        """Bulk-enroll students into a subject.

        Request body:
        {
            "subject": <subject_id>,
            "academic_year": <academic_year_id>,
            "student_ids": [<student_id>, ...],
            "notes": "optional"
        }
        """
        subject_id = request.data.get("subject")
        academic_year_id = request.data.get("academic_year")
        student_ids = request.data.get("student_ids", [])
        notes = request.data.get("notes", "")

        if not subject_id or not academic_year_id or not student_ids:
            return Response(
                {"error": "subject, academic_year, and student_ids are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        enrolled = 0
        skipped = 0
        errors = []

        with transaction.atomic():
            for idx, student_id in enumerate(student_ids):
                try:
                    obj, created = StudentSubjectEnrollment.objects.get_or_create(
                        student_id=student_id,
                        subject_id=subject_id,
                        academic_year_id=academic_year_id,
                        defaults={"notes": notes},
                    )
                    if created:
                        enrolled += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors.append({"student_id": student_id, "error": str(e)[:100]})

        return Response(
            {
                "enrolled": enrolled,
                "skipped": skipped,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="my-subjects")
    def my_subjects(self, request):
        """Return subjects the current student is enrolled in."""
        user = request.user
        if user.role != "student":
            return Response(
                {"detail": "This endpoint is for students only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = self.get_queryset().filter(
            student__user=user,
            status=StudentSubjectEnrollment.Status.ACTIVE,
        )
        return Response(StudentSubjectEnrollmentSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="subject-students/(?P<subject_id>[^/.]+)")
    def subject_students(self, request, subject_id=None):
        """Return all active students enrolled in a specific subject."""
        qs = self.get_queryset().filter(
            subject_id=subject_id,
            status=StudentSubjectEnrollment.Status.ACTIVE,
        )
        return Response(StudentSubjectEnrollmentSerializer(qs, many=True).data)


class CurriculumStandardViewSet(viewsets.ModelViewSet):
    """CRUD for curriculum standards.

    Admins can manage all standards. Teachers and other school members
    can read standards for reference.
    """

    serializer_class = CurriculumStandardSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["framework", "grade", "subject", "domain", "is_active"]
    search_fields = ["code", "name", "description", "domain", "cluster"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["grade", "code"]

    def get_queryset(self):
        return CurriculumStandard.objects.filter(school=self.request.user.school).select_related("grade", "subject")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "bulk_create"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """Bulk-create curriculum standards.

        Request body:
        {
            "framework": "common_core",
            "standards": [
                {"code": "CCSS.MATH.8.EE.1", "name": "...', "grade_id": ..., ...},
            ]
        }
        """
        framework = request.data.get("framework", "custom")
        standards_data = request.data.get("standards", [])

        if not standards_data:
            return Response(
                {"error": "standards list is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        school = request.user.school
        created = 0
        skipped = 0
        errors = []

        with transaction.atomic():
            for idx, item in enumerate(standards_data):
                code = (item.get("code") or "").strip()
                name = (item.get("name") or "").strip()
                if not code or not name:
                    errors.append({"index": idx, "error": "code and name are required"})
                    continue
                if CurriculumStandard.objects.filter(school=school, code=code).exists():
                    skipped += 1
                    continue
                try:
                    CurriculumStandard.objects.create(
                        school=school,
                        framework=framework,
                        code=code,
                        name=name,
                        description=item.get("description", ""),
                        grade_id=item.get("grade_id"),
                        subject_id=item.get("subject_id"),
                        domain=item.get("domain", ""),
                        cluster=item.get("cluster", ""),
                    )
                    created += 1
                except Exception as e:
                    errors.append({"index": idx, "error": str(e)[:100]})

        return Response(
            {"created": created, "skipped": skipped, "errors": errors},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="by-framework")
    def by_framework(self, request):
        """List standards grouped by framework."""
        qs = self.get_queryset().filter(is_active=True)
        framework = request.query_params.get("framework")
        if framework:
            qs = qs.filter(framework=framework)

        from collections import defaultdict

        grouped = defaultdict(list)
        for std in qs:
            grouped[std.framework].append(CurriculumStandardSerializer(std).data)
        return Response(grouped)


class SubjectStandardMappingViewSet(viewsets.ModelViewSet):
    """CRUD for subject-standard mappings.

    Maps which curriculum standards each subject covers and to what extent.
    Teachers see mappings for their assigned subjects; admins see all.
    """

    serializer_class = SubjectStandardMappingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["subject", "standard", "academic_year", "coverage_level"]
    search_fields = [
        "subject__name",
        "subject__code",
        "standard__code",
        "standard__name",
    ]
    ordering_fields = ["created_at", "coverage_level"]
    ordering = ["subject", "standard__code"]

    def get_queryset(self):
        user = self.request.user
        qs = SubjectStandardMapping.objects.filter(subject__school=user.school).select_related(
            "subject", "standard", "academic_year", "mapped_by"
        )
        if user.role == "teacher":
            qs = qs.filter(subject__assignments__teacher=user).distinct()
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "bulk_map"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(mapped_by=self.request.user)

    @action(detail=False, methods=["post"], url_path="bulk-map")
    def bulk_map(self, request):
        """Bulk-map standards to a subject.

        Request body:
        {
            "subject": <subject_id>,
            "academic_year": <academic_year_id>,
            "standard_ids": [<standard_id>, ...],
            "coverage_level": "partial"
        }
        """
        subject_id = request.data.get("subject")
        academic_year_id = request.data.get("academic_year")
        standard_ids = request.data.get("standard_ids", [])
        coverage_level = request.data.get("coverage_level", "partial")

        if not subject_id or not academic_year_id or not standard_ids:
            return Response(
                {"error": "subject, academic_year, and standard_ids are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mapped = 0
        skipped = 0
        errors = []

        with transaction.atomic():
            for idx, standard_id in enumerate(standard_ids):
                try:
                    obj, created = SubjectStandardMapping.objects.get_or_create(
                        subject_id=subject_id,
                        standard_id=standard_id,
                        academic_year_id=academic_year_id,
                        defaults={
                            "coverage_level": coverage_level,
                            "mapped_by": request.user,
                        },
                    )
                    if created:
                        mapped += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors.append({"standard_id": standard_id, "error": str(e)[:100]})

        return Response(
            {"mapped": mapped, "skipped": skipped, "errors": errors},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="subject-coverage/(?P<subject_id>[^/.]+)")
    def subject_coverage(self, request, subject_id=None):
        """Return all standards mapped to a subject for a given academic year."""
        academic_year = request.query_params.get("academic_year")
        qs = self.get_queryset().filter(subject_id=subject_id)
        if academic_year:
            qs = qs.filter(academic_year_id=academic_year)
        return Response(SubjectStandardMappingSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="coverage-report")
    def coverage_report(self, request):
        """Generate a coverage report for an academic year."""
        academic_year = request.query_params.get("academic_year")
        if not academic_year:
            return Response(
                {"error": "academic_year query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.db.models import Count, Q

        qs = self.get_queryset().filter(academic_year_id=academic_year)

        report = (
            qs.values("subject__id", "subject__name", "subject__code")
            .annotate(
                total_standards=Count("standard", distinct=True),
                full_count=Count("id", filter=Q(coverage_level="full")),
                partial_count=Count("id", filter=Q(coverage_level="partial")),
                introduced_count=Count("id", filter=Q(coverage_level="introduced")),
                not_covered_count=Count("id", filter=Q(coverage_level="not_covered")),
            )
            .order_by("subject__name")
        )

        return Response(list(report))


class SyllabusViewSet(viewsets.ModelViewSet):
    """CRUD for syllabus management.

    Teachers create syllabi for their assigned subjects. Admins approve/reject.
    Includes nested topic management via SyllabusTopicViewSet.
    """

    serializer_class = SyllabusSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["subject", "academic_year", "term", "status"]
    search_fields = ["title", "description", "subject__name", "subject__code"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Syllabus.objects.filter(subject__school=user.school)
            .select_related("subject__grade", "academic_year", "created_by", "approved_by")
            .prefetch_related("topics")
        )
        if user.role == "teacher":
            qs = qs.filter(subject__assignments__teacher=user).distinct()
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsTeacher()]
        if self.action in ["approve", "reject"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Admin approves a syllabus."""
        from django.utils import timezone

        syllabus = self.get_object()
        if syllabus.status != Syllabus.Status.UNDER_REVIEW:
            return Response(
                {"detail": "Syllabus must be under review to approve."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        syllabus.status = Syllabus.Status.APPROVED
        syllabus.approved_by = request.user
        syllabus.approved_at = timezone.now()
        syllabus.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])
        return Response(SyllabusSerializer(syllabus).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Admin rejects a syllabus with reason."""
        syllabus = self.get_object()
        if syllabus.status != Syllabus.Status.UNDER_REVIEW:
            return Response(
                {"detail": "Syllabus must be under review to reject."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reason = request.data.get("reason", "")
        if not reason:
            return Response(
                {"detail": "Rejection reason is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        syllabus.status = Syllabus.Status.REJECTED
        syllabus.rejection_reason = reason
        syllabus.save(update_fields=["status", "rejection_reason", "updated_at"])
        return Response(SyllabusSerializer(syllabus).data)

    @action(detail=True, methods=["post"], url_path="submit-for-review")
    def submit_for_review(self, request, pk=None):
        """Teacher submits a draft syllabus for admin review."""
        syllabus = self.get_object()
        if syllabus.status != Syllabus.Status.DRAFT:
            return Response(
                {"detail": "Only draft syllabi can be submitted for review."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        syllabus.status = Syllabus.Status.UNDER_REVIEW
        syllabus.save(update_fields=["status", "updated_at"])
        return Response(SyllabusSerializer(syllabus).data)

    @action(detail=True, methods=["get"], url_path="progress")
    def progress(self, request, pk=None):
        """Get detailed progress of a syllabus."""
        syllabus = self.get_object()
        topics = syllabus.topics.all().order_by("order")
        topic_data = SyllabusTopicSerializer(topics, many=True).data
        return Response(
            {
                "syllabus_id": str(syllabus.id),
                "title": syllabus.title,
                "total_topics": syllabus.topic_count,
                "completed_topics": syllabus.completed_topic_count,
                "progress_percentage": syllabus.progress_percentage,
                "total_hours": float(syllabus.total_hours),
                "topics": topic_data,
            }
        )


class SyllabusTopicViewSet(viewsets.ModelViewSet):
    """CRUD for syllabus topics.

    Topics are nested under a syllabus. The syllabus_id is passed via URL.
    """

    serializer_class = SyllabusTopicSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        user = self.request.user
        syllabus_id = self.kwargs.get("syllabus_pk")
        return SyllabusTopic.objects.filter(
            syllabus__id=syllabus_id,
            syllabus__subject__school=user.school,
        ).select_related("syllabus__subject")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None, syllabus_pk=None):
        """Mark a topic as in progress."""
        from django.utils import timezone

        topic = self.get_object()
        if topic.status != SyllabusTopic.Status.NOT_STARTED:
            return Response(
                {"detail": "Topic must be not started to begin."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        topic.status = SyllabusTopic.Status.IN_PROGRESS
        topic.started_at = timezone.now()
        topic.save(update_fields=["status", "started_at", "updated_at"])
        return Response(SyllabusTopicSerializer(topic).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None, syllabus_pk=None):
        """Mark a topic as completed."""
        from django.utils import timezone

        topic = self.get_object()
        if topic.status != SyllabusTopic.Status.IN_PROGRESS:
            return Response(
                {"detail": "Topic must be in progress to complete."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        topic.status = SyllabusTopic.Status.COMPLETED
        topic.completed_at = timezone.now()
        topic.save(update_fields=["status", "completed_at", "updated_at"])
        return Response(SyllabusTopicSerializer(topic).data)


class TeacherWorkloadConfigViewSet(viewsets.ModelViewSet):
    """CRUD for teacher workload configuration (admin only)."""

    serializer_class = TeacherWorkloadConfigSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        return TeacherWorkloadConfig.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TeacherWorkloadViewSet(viewsets.GenericViewSet):
    """Teacher workload calculation and reporting.

    Provides live workload summaries and historical snapshots.
    All endpoints are read-only — snapshots are generated on demand.
    """

    serializer_class = TeacherWorkloadSummarySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def _get_config(self, school):
        """Get or create workload config for the school."""
        config, _ = TeacherWorkloadConfig.objects.get_or_create(
            school=school,
            defaults={
                "max_periods_per_week": 30,
                "max_periods_per_day": 7,
                "max_subjects": 3,
                "max_classes": 5,
            },
        )
        return config

    def _calculate_teacher_workload(self, teacher, academic_year, config):
        """Calculate workload for a single teacher from timetable slots."""
        from services.students.models import Enrollment
        from services.timetable.models import TimetableSlot

        slots = TimetableSlot.objects.filter(
            assignment__teacher=teacher,
            academic_year=academic_year,
        ).select_related("period", "assignment__subject", "classroom")

        # Count periods per day
        day_names = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday"}
        periods_per_day = {}
        for slot in slots:
            day = day_names.get(slot.day_of_week, f"Day {slot.day_of_week}")
            periods_per_day[day] = periods_per_day.get(day, 0) + 1

        # Count unique subjects, classes, and students
        subjects = set()
        classes = set()
        for slot in slots:
            subjects.add(slot.assignment.subject_id)
            classes.add(slot.classroom_id)

        # Count unique students across all classes
        students = set()
        for class_id in classes:
            student_ids = Enrollment.objects.filter(
                classroom_id=class_id,
                academic_year=academic_year,
                is_active=True,
            ).values_list("student_id", flat=True)
            students.update(student_ids)

        total_periods = len(slots)
        max_periods = config.max_periods_per_week
        utilization = round((total_periods / max_periods) * 100, 2) if max_periods > 0 else 0

        # Determine status
        if utilization >= config.warning_threshold_pct:
            workload_status = "overloaded"
        elif utilization < (config.min_periods_per_week / max_periods * 100) if max_periods > 0 else False:
            workload_status = "underloaded"
        else:
            workload_status = "normal"

        return {
            "teacher_id": teacher.id,
            "teacher_name": teacher.full_name,
            "employee_id": getattr(teacher, "teacher_profile", None) and teacher.teacher_profile.employee_id or "",
            "department": getattr(teacher, "teacher_profile", None) and teacher.teacher_profile.department or "",
            "total_periods_per_week": total_periods,
            "periods_per_day": periods_per_day,
            "subjects_taught": len(subjects),
            "classes_taught": len(classes),
            "students_taught": len(students),
            "utilization_pct": utilization,
            "max_periods": max_periods,
            "status": workload_status,
        }

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        """Get live workload summary for all teachers (or a specific teacher).

        Query params:
        - academic_year: required
        - teacher_id: optional (filter to one teacher)
        """
        academic_year_id = request.query_params.get("academic_year")
        if not academic_year_id:
            return Response(
                {"error": "academic_year query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        school = request.user.school
        config = self._get_config(school)

        from services.students.models import AcademicYear

        academic_year = AcademicYear.objects.filter(id=academic_year_id, school=school).first()
        if not academic_year:
            return Response(
                {"error": "Academic year not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        teacher_id = request.query_params.get("teacher_id")
        teachers = User.objects.filter(school=school, role="teacher", is_active=True)
        if teacher_id:
            teachers = teachers.filter(id=teacher_id)

        summaries = []
        for teacher in teachers:
            summary = self._calculate_teacher_workload(teacher, academic_year, config)
            summaries.append(summary)

        # Sort by utilization (highest first)
        summaries.sort(key=lambda x: x["utilization_pct"], reverse=True)

        serializer = TeacherWorkloadSummarySerializer(summaries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="overloaded")
    def overloaded(self, request):
        """Get teachers exceeding the workload threshold."""
        academic_year_id = request.query_params.get("academic_year")
        if not academic_year_id:
            return Response(
                {"error": "academic_year query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        school = request.user.school
        config = self._get_config(school)

        from services.students.models import AcademicYear

        academic_year = AcademicYear.objects.filter(id=academic_year_id, school=school).first()
        if not academic_year:
            return Response(
                {"error": "Academic year not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        teachers = User.objects.filter(school=school, role="teacher", is_active=True)
        overloaded = []
        for teacher in teachers:
            wl = self._calculate_teacher_workload(teacher, academic_year, config)
            if wl["status"] == "overloaded":
                overloaded.append(wl)

        serializer = TeacherWorkloadSummarySerializer(overloaded, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-workload")
    def my_workload(self, request):
        """Get the current teacher's own workload."""
        user = request.user
        if user.role != "teacher":
            return Response(
                {"detail": "This endpoint is for teachers only."},
                status=status.HTTP_403_FORBIDDEN,
            )

        academic_year_id = request.query_params.get("academic_year")
        if not academic_year_id:
            return Response(
                {"error": "academic_year query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        school = user.school
        config = self._get_config(school)

        from services.students.models import AcademicYear

        academic_year = AcademicYear.objects.filter(id=academic_year_id, school=school).first()
        if not academic_year:
            return Response(
                {"error": "Academic year not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        wl = self._calculate_teacher_workload(user, academic_year, config)
        serializer = TeacherWorkloadSummarySerializer(wl)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="snapshot")
    def create_snapshot(self, request):
        """Create a workload snapshot for a specific week."""
        academic_year_id = request.data.get("academic_year")
        week_start = request.data.get("week_start_date")
        teacher_ids = request.data.get("teacher_ids", [])

        if not academic_year_id or not week_start:
            return Response(
                {"error": "academic_year and week_start_date are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        school = request.user.school
        config = self._get_config(school)

        from services.students.models import AcademicYear

        academic_year = AcademicYear.objects.filter(id=academic_year_id, school=school).first()
        if not academic_year:
            return Response(
                {"error": "Academic year not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        teachers = User.objects.filter(school=school, role="teacher", is_active=True)
        if teacher_ids:
            teachers = teachers.filter(id__in=teacher_ids)

        created = 0
        for teacher in teachers:
            wl = self._calculate_teacher_workload(teacher, academic_year, config)
            TeacherWorkloadSnapshot.objects.update_or_create(
                teacher=teacher,
                academic_year=academic_year,
                week_start_date=week_start,
                defaults={
                    "total_periods": wl["total_periods_per_week"],
                    "periods_per_day": wl["periods_per_day"],
                    "subjects_taught": wl["subjects_taught"],
                    "classes_taught": wl["classes_taught"],
                    "utilization_pct": wl["utilization_pct"],
                    "is_overloaded": wl["status"] == "overloaded",
                    "is_underloaded": wl["status"] == "underloaded",
                },
            )
            created += 1

        return Response({"snapshots_created": created}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="history/(?P<teacher_id>[^/.]+)")
    def history(self, request, teacher_id=None):
        """Get workload snapshot history for a teacher."""
        academic_year_id = request.query_params.get("academic_year")
        qs = TeacherWorkloadSnapshot.objects.filter(
            teacher_id=teacher_id,
            teacher__school=request.user.school,
        ).select_related("teacher", "academic_year")
        if academic_year_id:
            qs = qs.filter(academic_year_id=academic_year_id)
        serializer = TeacherWorkloadSnapshotSerializer(qs[:20], many=True)
        return Response(serializer.data)


class EvaluationCriteriaViewSet(viewsets.ModelViewSet):
    """CRUD for evaluation criteria (admin only)."""

    serializer_class = EvaluationCriteriaSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "is_active"]
    search_fields = ["name", "description"]
    ordering_fields = ["order", "category", "name"]
    ordering = ["order"]

    def get_queryset(self):
        return EvaluationCriteria.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class EvaluationTemplateViewSet(viewsets.ModelViewSet):
    """CRUD for evaluation templates (admin only)."""

    serializer_class = EvaluationTemplateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["eval_type", "is_active"]
    search_fields = ["name", "description"]

    def get_queryset(self):
        return EvaluationTemplate.objects.filter(school=self.request.user.school).prefetch_related("criteria")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class TeacherEvaluationViewSet(viewsets.ModelViewSet):
    """CRUD for teacher evaluations with workflow management.

    Supports: draft → self_review → peer_review → admin_review → completed
    Teachers see their own evaluations; admins see all.
    """

    serializer_class = TeacherEvaluationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["teacher", "academic_year", "status", "template"]
    search_fields = ["title", "description", "teacher__first_name", "teacher__last_name"]
    ordering_fields = ["created_at", "overall_score", "review_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = (
            TeacherEvaluation.objects.filter(teacher__school=user.school)
            .select_related("teacher", "template", "academic_year", "created_by", "reviewed_by")
            .prefetch_related("scores__criterion", "comments_list__author")
        )
        if user.role == "teacher":
            qs = qs.filter(teacher=user)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        if self.action in ["submit_scores", "complete", "comment"]:
            return [IsAuthenticated(), IsSchoolMember()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="submit-scores")
    def submit_scores(self, request, pk=None):
        """Submit criterion scores for an evaluation.

        Request body:
        {
            "scores": [
                {"criterion_id": "...", "score": 4.5, "evidence": "...", "comments": "..."},
            ]
        }
        """
        evaluation = self.get_object()
        scores_data = request.data.get("scores", [])

        if not scores_data:
            return Response(
                {"error": "scores list is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if evaluation.status not in [
            TeacherEvaluation.Status.DRAFT,
            TeacherEvaluation.Status.SELF_REVIEW,
            TeacherEvaluation.Status.PEER_REVIEW,
            TeacherEvaluation.Status.ADMIN_REVIEW,
        ]:
            return Response(
                {"detail": "Cannot submit scores for a completed/archived evaluation."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            for item in scores_data:
                criterion_id = item.get("criterion_id")
                score_val = item.get("score")
                if not criterion_id or score_val is None:
                    continue
                EvaluationScore.objects.update_or_create(
                    evaluation=evaluation,
                    criterion_id=criterion_id,
                    defaults={
                        "score": score_val,
                        "evidence": item.get("evidence", ""),
                        "comments": item.get("comments", ""),
                        "scored_by": request.user,
                    },
                )

        # Recalculate overall score
        self._recalculate_scores(evaluation)
        return Response(TeacherEvaluationSerializer(evaluation).data)

    def _recalculate_scores(self, evaluation):
        """Recalculate weighted overall score from individual scores."""
        scores = evaluation.scores.select_related("criterion").all()
        if not scores:
            return

        total_weighted = sum(float(s.weighted_score or 0) for s in scores)
        max_weighted = sum(float(s.criterion.max_score) * float(s.criterion.weight) for s in scores)

        evaluation.overall_score = round(total_weighted, 2)
        evaluation.max_possible_score = round(max_weighted, 2)
        evaluation.save(update_fields=["overall_score", "max_possible_score", "updated_at"])

    @action(detail=True, methods=["post"], url_path="submit-self-review")
    def submit_self_review(self, request, pk=None):
        """Teacher submits their self-review comments."""
        evaluation = self.get_object()
        if evaluation.teacher != request.user:
            return Response(
                {"detail": "Only the teacher being evaluated can submit self-review."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if evaluation.status != TeacherEvaluation.Status.SELF_REVIEW:
            return Response(
                {"detail": "Evaluation is not in self_review status."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        evaluation.teacher_comments = request.data.get("teacher_comments", "")
        evaluation.status = TeacherEvaluation.Status.PEER_REVIEW
        evaluation.save(update_fields=["teacher_comments", "status", "updated_at"])
        return Response(TeacherEvaluationSerializer(evaluation).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Admin marks evaluation as completed."""
        if request.user.role not in ["school_admin", "super_admin"]:
            return Response(
                {"detail": "Only admins can complete evaluations."},
                status=status.HTTP_403_FORBIDDEN,
            )
        evaluation = self.get_object()
        if evaluation.status != TeacherEvaluation.Status.ADMIN_REVIEW:
            return Response(
                {"detail": "Evaluation must be in admin_review status."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        evaluation.status = TeacherEvaluation.Status.COMPLETED
        evaluation.reviewed_by = request.user
        from django.utils import timezone

        evaluation.review_date = timezone.now().date()
        evaluation.strength = request.data.get("strength", evaluation.strength)
        evaluation.areas_for_growth = request.data.get("areas_for_growth", evaluation.areas_for_growth)
        evaluation.action_plan = request.data.get("action_plan", evaluation.action_plan)
        evaluation.evaluator_notes = request.data.get("evaluator_notes", evaluation.evaluator_notes)
        evaluation.save(
            update_fields=[
                "status",
                "reviewed_by",
                "review_date",
                "strength",
                "areas_for_growth",
                "action_plan",
                "evaluator_notes",
                "updated_at",
            ]
        )
        return Response(TeacherEvaluationSerializer(evaluation).data)

    @action(detail=True, methods=["post"], url_path="advance-status")
    def advance_status(self, request, pk=None):
        """Advance evaluation to the next status in the workflow."""
        evaluation = self.get_object()
        transitions = {
            TeacherEvaluation.Status.DRAFT: TeacherEvaluation.Status.SELF_REVIEW,
            TeacherEvaluation.Status.SELF_REVIEW: TeacherEvaluation.Status.PEER_REVIEW,
            TeacherEvaluation.Status.PEER_REVIEW: TeacherEvaluation.Status.ADMIN_REVIEW,
        }
        next_status = transitions.get(evaluation.status)
        if not next_status:
            return Response(
                {"detail": f"Cannot advance from {evaluation.status}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        evaluation.status = next_status
        evaluation.save(update_fields=["status", "updated_at"])
        return Response(TeacherEvaluationSerializer(evaluation).data)

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        """GET: List comments. POST: Add a comment."""
        evaluation = self.get_object()
        if request.method == "GET":
            qs = evaluation.comments_list.select_related("author").all()
            return Response(EvaluationCommentSerializer(qs, many=True).data)

        # POST — add comment
        serializer = EvaluationCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(evaluation=evaluation, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="my-evaluations")
    def my_evaluations(self, request):
        """Return evaluations for the current teacher."""
        if request.user.role != "teacher":
            return Response(
                {"detail": "This endpoint is for teachers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = self.get_queryset().filter(teacher=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(TeacherEvaluationSerializer(page, many=True).data)
        return Response(TeacherEvaluationSerializer(qs, many=True).data)


class AcademicTranscriptViewSet(viewsets.ModelViewSet):
    """CRUD for academic transcripts.

    Admins generate and verify transcripts. Teachers/students can view.
    Supports bulk generation and PDF export.
    """

    serializer_class = AcademicTranscriptSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["student", "academic_year", "status"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "student__admission_number",
        "transcript_number",
    ]
    ordering_fields = ["created_at", "percentage", "gpa"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = AcademicTranscript.objects.filter(student__school=user.school).select_related(
            "student__user",
            "academic_year",
            "generated_by",
            "verified_by",
        )
        if user.role == "student":
            qs = qs.filter(student__user=user)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "bulk_generate"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)

    @action(detail=False, methods=["post"], url_path="generate")
    def generate_transcript(self, request):
        """Generate a transcript for a specific student and academic year.

        Collects grade data from the gradebook, attendance from attendance module,
        calculates GPA and rank, and creates the transcript.

        Request body:
        {
            "student": <student_id>,
            "academic_year": <academic_year_id>,
            "remarks": "optional",
            "principal_name": "optional",
            "class_teacher_name": "optional"
        }
        """
        student_id = request.data.get("student")
        academic_year_id = request.data.get("academic_year")

        if not student_id or not academic_year_id:
            return Response(
                {"error": "student and academic_year are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from services.attendance.models import AttendanceRecord
        from services.gradebook.models import Grade as GradeRecord
        from services.students.models import AcademicYear as AY

        student = request.user.school.students.filter(id=student_id).first()
        if not student:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        academic_year = AY.objects.filter(id=academic_year_id, school=request.user.school).first()
        if not academic_year:
            return Response({"error": "Academic year not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check for existing transcript
        existing = AcademicTranscript.objects.filter(student_id=student_id, academic_year_id=academic_year_id).first()
        if existing:
            return Response(
                {"error": "Transcript already exists.", "transcript_id": str(existing.id)},
                status=status.HTTP_409_CONFLICT,
            )

        # Collect grade data from gradebook
        grade_records = GradeRecord.objects.filter(
            student_id=student_id,
            exam_schedule__exam__academic_year_id=academic_year_id,
            is_absent=False,
        ).select_related("exam_schedule__subject", "exam_schedule")

        # Also check for the student directly via user link
        if not grade_records.exists():
            student_user = Student.objects.filter(id=student_id).values_list("user_id", flat=True).first()
            if student_user:
                grade_records = GradeRecord.objects.filter(
                    student__user_id=student_user,
                    exam_schedule__exam__academic_year_id=academic_year_id,
                    is_absent=False,
                ).select_related("exam_schedule__subject", "exam_schedule")

        subjects_data = []
        total_marks = Decimal("0")
        obtained_marks = Decimal("0")
        subject_grades = []

        # Group by subject to calculate per-subject totals
        from collections import defaultdict
        from decimal import Decimal as D

        subject_totals = defaultdict(lambda: {"total_max": D("0"), "total_obtained": D("0"), "name": "", "code": ""})
        for gr in grade_records:
            subj = gr.exam_schedule.subject
            key = str(subj.id)
            subject_totals[key]["total_max"] += gr.exam_schedule.max_marks
            subject_totals[key]["total_obtained"] += gr.marks_obtained or D("0")
            subject_totals[key]["name"] = subj.name
            subject_totals[key]["code"] = subj.code

        for subj_id, data in subject_totals.items():
            total_marks += data["total_max"]
            obtained_marks += data["total_obtained"]
            pct = (
                round((float(data["total_obtained"]) / float(data["total_max"]) * 100), 1)
                if data["total_max"] > 0
                else 0
            )
            grade_letter = _calculate_grade_letter(pct)
            subject_grades.append(pct)
            subjects_data.append(
                {
                    "subject_id": subj_id,
                    "name": data["name"],
                    "code": data["code"],
                    "total_marks": float(data["total_max"]),
                    "obtained_marks": float(data["total_obtained"]),
                    "percentage": pct,
                    "grade_letter": grade_letter,
                }
            )

        # Calculate overall stats
        percentage = round((float(obtained_marks) / float(total_marks) * 100), 2) if total_marks > 0 else 0
        gpa = round(percentage / 25, 2) if percentage > 0 else 0  # Simple 4.0 scale
        grade_letter = _calculate_grade_letter(percentage)

        # Attendance data
        attendance_records = AttendanceRecord.objects.filter(
            student_id=student_id,
            academic_year_id=academic_year_id,
        )
        total_school_days = attendance_records.count()
        attendance_days = attendance_records.filter(status="P").count()
        attendance_pct = round((attendance_days / total_school_days * 100), 2) if total_school_days > 0 else 0

        transcript = AcademicTranscript.objects.create(
            student_id=student_id,
            academic_year_id=academic_year_id,
            status=AcademicTranscript.Status.DRAFT,
            total_marks=total_marks,
            obtained_marks=obtained_marks,
            percentage=percentage,
            gpa=gpa,
            grade_letter=grade_letter,
            attendance_days=attendance_days,
            total_school_days=total_school_days,
            attendance_percentage=attendance_pct,
            subjects_data=subjects_data,
            remarks=request.data.get("remarks", ""),
            principal_name=request.data.get("principal_name", ""),
            class_teacher_name=request.data.get("class_teacher_name", ""),
            generated_by=request.user,
        )

        return Response(
            AcademicTranscriptSerializer(transcript).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="bulk-generate")
    def bulk_generate(self, request):
        """Bulk-generate transcripts for all students in a classroom."""
        classroom_id = request.data.get("classroom")
        academic_year_id = request.data.get("academic_year")

        if not classroom_id or not academic_year_id:
            return Response(
                {"error": "classroom and academic_year are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from services.students.models import Enrollment

        enrolled = Enrollment.objects.filter(
            classroom_id=classroom_id,
            academic_year_id=academic_year_id,
            is_active=True,
        ).select_related("student")

        generated = 0
        skipped = 0
        errors = []

        for enrollment in enrolled:
            existing = AcademicTranscript.objects.filter(
                student=enrollment.student,
                academic_year_id=academic_year_id,
            ).exists()
            if existing:
                skipped += 1
                continue
            try:
                # Use the generate logic inline
                self._generate_single_transcript(
                    enrollment.student.id,
                    academic_year_id,
                    request.user,
                )
                generated += 1
            except Exception as e:
                errors.append({"student_id": str(enrollment.student.id), "error": str(e)[:100]})

        return Response(
            {"generated": generated, "skipped": skipped, "errors": errors},
            status=status.HTTP_200_OK,
        )

    def _generate_single_transcript(self, student_id, academic_year_id, user):
        """Internal method to generate a single transcript."""
        from collections import defaultdict
        from decimal import Decimal as D

        from services.attendance.models import AttendanceRecord
        from services.gradebook.models import Grade as GradeRecord

        grade_records = GradeRecord.objects.filter(
            student_id=student_id,
            exam_schedule__exam__academic_year_id=academic_year_id,
            is_absent=False,
        ).select_related("exam_schedule__subject")

        subjects_data = []
        total_marks = D("0")
        obtained_marks = D("0")
        subject_totals = defaultdict(lambda: {"total_max": D("0"), "total_obtained": D("0"), "name": "", "code": ""})

        for gr in grade_records:
            subj = gr.exam_schedule.subject
            key = str(subj.id)
            subject_totals[key]["total_max"] += gr.exam_schedule.max_marks
            subject_totals[key]["total_obtained"] += gr.marks_obtained or D("0")
            subject_totals[key]["name"] = subj.name
            subject_totals[key]["code"] = subj.code

        for subj_id, data in subject_totals.items():
            total_marks += data["total_max"]
            obtained_marks += data["total_obtained"]
            pct = (
                round((float(data["total_obtained"]) / float(data["total_max"]) * 100), 1)
                if data["total_max"] > 0
                else 0
            )
            subjects_data.append(
                {
                    "subject_id": subj_id,
                    "name": data["name"],
                    "code": data["code"],
                    "total_marks": float(data["total_max"]),
                    "obtained_marks": float(data["total_obtained"]),
                    "percentage": pct,
                    "grade_letter": _calculate_grade_letter(pct),
                }
            )

        percentage = round((float(obtained_marks) / float(total_marks) * 100), 2) if total_marks > 0 else 0
        gpa = round(percentage / 25, 2) if percentage > 0 else 0

        attendance_records = AttendanceRecord.objects.filter(student_id=student_id, academic_year_id=academic_year_id)
        total_days = attendance_records.count()
        present_days = attendance_records.filter(status="P").count()

        AcademicTranscript.objects.create(
            student_id=student_id,
            academic_year_id=academic_year_id,
            status=AcademicTranscript.Status.DRAFT,
            total_marks=total_marks,
            obtained_marks=obtained_marks,
            percentage=percentage,
            gpa=gpa,
            grade_letter=_calculate_grade_letter(percentage),
            attendance_days=present_days,
            total_school_days=total_days,
            attendance_percentage=round((present_days / total_days * 100), 2) if total_days > 0 else 0,
            subjects_data=subjects_data,
            generated_by=user,
        )

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        """Admin verifies a transcript."""
        if request.user.role not in ["school_admin", "super_admin"]:
            return Response(
                {"detail": "Only admins can verify transcripts."},
                status=status.HTTP_403_FORBIDDEN,
            )
        transcript = self.get_object()
        if transcript.status == AcademicTranscript.Status.VERIFIED:
            return Response(
                {"detail": "Transcript is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        transcript.status = AcademicTranscript.Status.VERIFIED
        transcript.verified_by = request.user
        from django.utils import timezone

        transcript.verified_at = timezone.now()
        transcript.save(update_fields=["status", "verified_by", "verified_at", "updated_at"])
        return Response(AcademicTranscriptSerializer(transcript).data)

    @action(detail=True, methods=["get"], url_path="pdf")
    def download_pdf(self, request, pk=None):
        """Download the PDF version of a transcript.

        If a cached PDF exists, returns it. Otherwise generates one on the fly.
        """
        transcript = self.get_object()
        if transcript.pdf_file:
            from django.http import FileResponse

            return FileResponse(transcript.pdf_file.open(), content_type="application/pdf")

        # Generate PDF on the fly
        try:
            pdf_bytes = self._generate_pdf(transcript)
            # Save to model
            from django.core.files.base import ContentFile

            filename = f"transcript_{transcript.transcript_number}.pdf"
            transcript.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)
            transcript.status = AcademicTranscript.Status.GENERATED
            transcript.save(update_fields=["status", "updated_at"])

            from django.http import HttpResponse

            response = HttpResponse(pdf_bytes, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except ImportError:
            return Response(
                {"detail": "PDF generation requires reportlab. Install with: pip install reportlab"},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

    def _generate_pdf(self, transcript):
        """Generate PDF bytes for a transcript using reportlab."""
        import io

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=16, spaceAfter=6)
        elements.append(Paragraph(transcript.student.school.name, title_style))
        elements.append(Paragraph("ACADEMIC TRANSCRIPT", styles["Heading1"]))
        elements.append(Spacer(1, 0.2 * inch))

        # Student info table
        info_data = [
            ["Student Name:", str(transcript.student), "Transcript #:", transcript.transcript_number],
            ["Admission #:", transcript.student.admission_number, "Academic Year:", str(transcript.academic_year)],
            [
                "Date of Birth:",
                str(transcript.student.date_of_birth or ""),
                "Generated:",
                str(transcript.generated_at.date()),
            ],
        ]
        info_table = Table(info_data, colWidths=[1.5 * inch, 2 * inch, 1.5 * inch, 2 * inch])
        info_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(info_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Grades table
        elements.append(Paragraph("Subject Results", styles["Heading2"]))
        grade_data = [["Subject", "Code", "Max Marks", "Obtained", "Percentage", "Grade"]]
        for subj in transcript.subjects_data or []:
            grade_data.append(
                [
                    subj.get("name", ""),
                    subj.get("code", ""),
                    str(subj.get("total_marks", "")),
                    str(subj.get("obtained_marks", "")),
                    f"{subj.get('percentage', 0)}%",
                    subj.get("grade_letter", ""),
                ]
            )

        if len(grade_data) > 1:
            grade_table = Table(grade_data, colWidths=[2 * inch, 1 * inch, 1 * inch, 1 * inch, 1 * inch, 0.8 * inch])
            grade_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            elements.append(grade_table)

        elements.append(Spacer(1, 0.2 * inch))

        # Summary
        elements.append(Paragraph("Summary", styles["Heading2"]))
        summary_data = [
            ["Total Marks:", f"{transcript.obtained_marks} / {transcript.total_marks}"],
            ["Percentage:", f"{transcript.percentage}%"],
            ["GPA:", f"{transcript.gpa}"],
            ["Grade:", transcript.grade_letter],
            [
                "Attendance:",
                f"{transcript.attendance_days} / "
                f"{transcript.total_school_days} days "
                f"({transcript.attendance_percentage}%)",
            ],
        ]
        if transcript.rank_in_class:
            summary_data.append(["Class Rank:", str(transcript.rank_in_class)])
        if transcript.rank_in_grade:
            summary_data.append(["Grade Rank:", str(transcript.rank_in_grade)])

        summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3 * inch))

        # Signatures
        sig_data = [
            ["_____________________", "", "_____________________"],
            [f"{transcript.principal_name or 'Principal'}", "", f"{transcript.class_teacher_name or 'Class Teacher'}"],
            ["Signature & Seal", "", "Signature"],
        ]
        sig_table = Table(sig_data, colWidths=[3 * inch, 1 * inch, 3 * inch])
        sig_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(sig_table)

        if transcript.remarks:
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph("Remarks", styles["Heading2"]))
            elements.append(Paragraph(transcript.remarks, styles["Normal"]))

        doc.build(elements)
        return buffer.getvalue()

    @action(detail=False, methods=["get"], url_path="my-transcript")
    def my_transcript(self, request):
        """Return transcripts for the current student."""
        if request.user.role != "student":
            return Response(
                {"detail": "This endpoint is for students only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = self.get_queryset().filter(student__user=request.user)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(AcademicTranscriptSerializer(page, many=True).data)
        return Response(AcademicTranscriptSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="class-rankings/(?P<academic_year_id>[^/.]+)")
    def class_rankings(self, request, academic_year_id=None):
        """Get rankings of students by class based on transcript percentages."""
        transcripts = (
            AcademicTranscript.objects.filter(
                academic_year_id=academic_year_id,
                student__school=request.user.school,
                status__in=[AcademicTranscript.Status.GENERATED, AcademicTranscript.Status.VERIFIED],
            )
            .select_related("student__user")
            .order_by("-percentage")
        )

        # Group by classroom
        from collections import defaultdict

        rankings = defaultdict(list)
        for idx, t in enumerate(transcripts, start=1):
            try:
                enrollment = t.student.user.enrollments.filter(academic_year_id=academic_year_id).first()
                classroom_key = str(enrollment.classroom) if enrollment else "Unassigned"
            except Exception:
                classroom_key = "Unassigned"
            rankings[classroom_key].append(
                {
                    "rank": len(rankings[classroom_key]) + 1,
                    "student_id": str(t.student.id),
                    "student_name": str(t.student),
                    "admission_number": t.student.admission_number,
                    "percentage": float(t.percentage),
                    "gpa": float(t.gpa) if t.gpa else None,
                    "grade_letter": t.grade_letter,
                }
            )

        return Response(dict(rankings))


def _calculate_grade_letter(percentage):
    """Convert a percentage to a letter grade."""
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B+"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C+"
    elif percentage >= 40:
        return "C"
    elif percentage >= 30:
        return "D"
    else:
        return "F"


# ---------------------------------------------------------------------------
# P1: Academic Calendar ViewSets
# ---------------------------------------------------------------------------


class AcademicTermViewSet(viewsets.ModelViewSet):
    """CRUD for academic terms."""

    serializer_class = AcademicTermSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["academic_year", "term_type", "is_current"]
    search_fields = ["name"]
    ordering_fields = ["start_date", "end_date"]
    ordering = ["start_date"]

    def get_queryset(self):
        return AcademicTerm.objects.filter(school=self.request.user.school).select_related("academic_year")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """Get the current active term."""
        term = AcademicTerm.objects.filter(school=request.user.school, is_current=True).first()
        if not term:
            return Response(
                {"detail": "No current term found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(AcademicTermSerializer(term).data)

    @action(detail=True, methods=["post"], url_path="set-current")
    def set_current(self, request, pk=None):
        """Set a term as current (deactivates others)."""
        if request.user.role not in ["school_admin", "super_admin"]:
            return Response(
                {"detail": "Only admins can set current term."},
                status=status.HTTP_403_FORBIDDEN,
            )
        term = self.get_object()
        AcademicTerm.objects.filter(school=request.user.school, is_current=True).update(is_current=False)
        term.is_current = True
        term.save(update_fields=["is_current", "updated_at"])
        return Response(AcademicTermSerializer(term).data)


class AcademicEventViewSet(viewsets.ModelViewSet):
    """CRUD for academic calendar events."""

    serializer_class = AcademicEventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["academic_year", "term", "event_type", "is_published"]
    search_fields = ["title", "description"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    ordering = ["start_date"]

    def get_queryset(self):
        user = self.request.user
        qs = (
            AcademicEvent.objects.filter(school=user.school)
            .select_related("academic_year", "term", "created_by")
            .prefetch_related("affected_grades", "affected_subjects")
        )
        if user.role == "teacher":
            qs = qs.filter(
                models.Q(affected_subjects__assignments__teacher=user) | models.Q(affected_grades__isnull=True)
            ).distinct()
        return qs

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
        """Get upcoming events for the next 30 days."""
        from datetime import timedelta

        from django.utils import timezone

        today = timezone.now().date()
        future = today + timedelta(days=30)
        qs = self.get_queryset().filter(
            start_date__gte=today,
            start_date__lte=future,
            is_published=True,
        )
        return Response(AcademicEventSerializer(qs, many=True).data)


class AcademicHolidayViewSet(viewsets.ModelViewSet):
    """CRUD for academic holidays."""

    serializer_class = AcademicHolidaySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["academic_year", "holiday_type"]
    search_fields = ["name"]
    ordering_fields = ["date"]
    ordering = ["date"]

    def get_queryset(self):
        return AcademicHoliday.objects.filter(school=self.request.user.school).select_related("academic_year")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


# ---------------------------------------------------------------------------
# P2: Assignment & Homework ViewSets
# ---------------------------------------------------------------------------


class AssignmentViewSet(viewsets.ModelViewSet):
    """CRUD for assignments with submission tracking."""

    serializer_class = AssignmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["assignment", "assignment_type", "status", "due_date"]
    search_fields = ["title", "description"]
    ordering_fields = ["due_date", "created_at"]
    ordering = ["-due_date"]

    def get_queryset(self):
        user = self.request.user
        qs = Assignment.objects.filter(assignment__teacher__school=user.school).select_related(
            "assignment__teacher",
            "assignment__subject",
            "assignment__classroom",
            "created_by",
        )
        if user.role == "teacher":
            qs = qs.filter(assignment__teacher=user)
        elif user.role == "student":
            qs = qs.filter(
                assignment__classroom__enrollments__student__user=user,
                status="published",
            ).distinct()
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        """Publish a draft assignment."""
        from django.utils import timezone

        assignment = self.get_object()
        if assignment.status != Assignment.Status.DRAFT:
            return Response(
                {"detail": "Only draft assignments can be published."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        assignment.status = Assignment.Status.PUBLISHED
        assignment.published_at = timezone.now()
        assignment.save(update_fields=["status", "published_at", "updated_at"])

        # Send notifications to students
        students = User.objects.filter(
            role="student",
            enrollments__classroom=assignment.assignment.classroom,
            enrollments__academic_year=assignment.assignment.academic_year,
            enrollments__is_active=True,
        ).distinct()
        for student in students:
            AcademicNotification.objects.create(
                school=request.user.school,
                recipient=student,
                notification_type=AcademicNotification.NotificationType.ASSIGNMENT_POSTED,
                title=f"New Assignment: {assignment.title}",
                message=f"{assignment.assignment.subject.name} — Due: {assignment.due_date}",
                metadata={"assignment_id": str(assignment.id)},
            )
        return Response(AssignmentSerializer(assignment).data)

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        """Close assignment submissions."""
        assignment = self.get_object()
        if assignment.status != Assignment.Status.PUBLISHED:
            return Response(
                {"detail": "Only published assignments can be closed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        assignment.status = Assignment.Status.CLOSED
        assignment.save(update_fields=["status", "updated_at"])
        return Response(AssignmentSerializer(assignment).data)

    @action(detail=False, methods=["get"], url_path="my-assignments")
    def my_assignments(self, request):
        """Get assignments for the current student."""
        if request.user.role != "student":
            return Response(
                {"detail": "This endpoint is for students only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = (
            self.get_queryset()
            .filter(
                assignment__classroom__enrollments__student__user=request.user,
                status="published",
            )
            .distinct()
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(AssignmentSerializer(page, many=True).data)
        return Response(AssignmentSerializer(qs, many=True).data)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    """CRUD for assignment submissions."""

    serializer_class = AssignmentSubmissionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["assignment", "student", "status"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "assignment__title",
    ]
    ordering_fields = ["submitted_at", "score"]
    ordering = ["-submitted_at"]

    def get_queryset(self):
        user = self.request.user
        qs = AssignmentSubmission.objects.filter(assignment__assignment__teacher__school=user.school).select_related(
            "assignment", "student__user", "graded_by"
        )
        if user.role == "student":
            qs = qs.filter(student__user=user)
        elif user.role == "teacher":
            qs = qs.filter(assignment__assignment__teacher=user)
        return qs

    def get_permissions(self):
        if self.action in ["grade"]:
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=True, methods=["post"])
    def grade(self, request, pk=None):
        """Grade a submission."""
        from django.utils import timezone

        submission = self.get_object()
        if request.user.role not in ["teacher", "school_admin"]:
            return Response(
                {"detail": "Only teachers can grade submissions."},
                status=status.HTTP_403_FORBIDDEN,
            )
        score = request.data.get("score")
        feedback = request.data.get("feedback", "")
        if score is None:
            return Response(
                {"error": "score is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        submission.score = score
        submission.feedback = feedback
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        submission.status = AssignmentSubmission.Status.GRADED
        submission.save(
            update_fields=[
                "score",
                "feedback",
                "graded_by",
                "graded_at",
                "status",
                "updated_at",
            ]
        )
        # Notify student
        AcademicNotification.objects.create(
            school=request.user.school,
            recipient=submission.student.user,
            notification_type=AcademicNotification.NotificationType.ASSIGNMENT_GRADED,
            title=f"Assignment Graded: {submission.assignment.title}",
            message=f"Score: {score}/{submission.assignment.max_score}",
            metadata={"submission_id": str(submission.id)},
        )
        return Response(AssignmentSubmissionSerializer(submission).data)

    @action(detail=True, methods=["post"], url_path="return-for-revision")
    def return_for_revision(self, request, pk=None):
        """Return submission to student for revision."""
        submission = self.get_object()
        feedback = request.data.get("feedback", "")
        submission.status = AssignmentSubmission.Status.RETURNED
        submission.feedback = feedback
        submission.save(update_fields=["status", "feedback", "updated_at"])
        AcademicNotification.objects.create(
            school=request.user.school,
            recipient=submission.student.user,
            notification_type=AcademicNotification.NotificationType.GENERAL,
            title="Assignment Returned for Revision",
            message=f"{submission.assignment.title}: {feedback[:100]}",
            priority="high",
            metadata={"submission_id": str(submission.id)},
        )
        return Response(AssignmentSubmissionSerializer(submission).data)


class HomeworkTrackerViewSet(viewsets.ModelViewSet):
    """CRUD for daily homework tracking."""

    serializer_class = HomeworkTrackerSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["classroom", "subject", "date", "is_completed"]
    search_fields = ["description"]
    ordering_fields = ["date", "due_date"]
    ordering = ["-date"]

    def get_queryset(self):
        user = self.request.user
        qs = HomeworkTracker.objects.filter(classroom__school=user.school).select_related(
            "subject", "teacher", "classroom"
        )
        if user.role == "teacher":
            qs = qs.filter(teacher=user)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


# ---------------------------------------------------------------------------
# P3: Exam Management ViewSets
# ---------------------------------------------------------------------------


class QuestionBankViewSet(viewsets.ModelViewSet):
    """CRUD for question bank entries."""

    serializer_class = QuestionBankSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["subject", "question_type", "difficulty", "is_active"]
    search_fields = ["question_text", "tags"]
    ordering_fields = ["created_at", "usage_count", "difficulty"]
    ordering = ["subject", "difficulty"]

    def get_queryset(self):
        return QuestionBank.objects.filter(school=self.request.user.school).select_related("subject", "created_by")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            created_by=self.request.user,
        )

    @action(detail=False, methods=["post"], url_path="bulk-import")
    def bulk_import(self, request):
        """Bulk-import questions from a list."""
        questions_data = request.data.get("questions", [])
        if not questions_data:
            return Response(
                {"error": "questions list is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        created = 0
        errors = []
        school = request.user.school
        with transaction.atomic():
            for idx, item in enumerate(questions_data):
                subject_id = item.get("subject_id")
                if not subject_id:
                    errors.append({"index": idx, "error": "subject_id required"})
                    continue
                try:
                    QuestionBank.objects.create(
                        school=school,
                        subject_id=subject_id,
                        question_type=item.get("question_type", "mcq"),
                        difficulty=item.get("difficulty", "medium"),
                        question_text=item.get("question_text", ""),
                        options=item.get("options", []),
                        correct_answer=item.get("correct_answer", ""),
                        explanation=item.get("explanation", ""),
                        marks=item.get("marks", 1),
                        tags=item.get("tags", []),
                        created_by=request.user,
                    )
                    created += 1
                except Exception as e:
                    errors.append({"index": idx, "error": str(e)[:100]})
        return Response(
            {"created": created, "errors": errors},
            status=status.HTTP_200_OK,
        )


class ExamPaperViewSet(viewsets.ModelViewSet):
    """CRUD for exam papers with random generation."""

    serializer_class = ExamPaperSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["subject", "academic_year", "status"]
    search_fields = ["title"]
    ordering_fields = ["created_at", "total_marks"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return ExamPaper.objects.filter(school=self.request.user.school).select_related(
            "subject", "academic_year", "created_by"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(
            school=self.request.user.school,
            created_by=self.request.user,
        )

    @action(detail=True, methods=["post"], url_path="generate-random")
    def generate_random(self, request, pk=None):
        """Randomly select questions from the bank."""
        paper = self.get_object()
        distribution = request.data.get("distribution")
        count = paper.generate_random(distribution)
        return Response(
            {"questions_added": count, "total": paper.question_count},
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="finalize")
    def finalize(self, request, pk=None):
        """Finalize a paper so it can be used."""
        paper = self.get_object()
        if paper.status != ExamPaper.Status.DRAFT:
            return Response(
                {"detail": "Only draft papers can be finalized."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if paper.questions.count() == 0:
            return Response(
                {"detail": "Cannot finalize an empty paper."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        paper.status = ExamPaper.Status.FINALIZED
        paper.save(update_fields=["status", "updated_at"])
        return Response(ExamPaperSerializer(paper).data)


# ---------------------------------------------------------------------------
# P4: Notification ViewSet
# ---------------------------------------------------------------------------


class AcademicNotificationViewSet(viewsets.ModelViewSet):
    """CRUD for academic notifications."""

    serializer_class = AcademicNotificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["notification_type", "priority", "is_read"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return AcademicNotification.objects.filter(
            school=self.request.user.school,
            recipient=self.request.user,
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        from django.utils import timezone

        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at"])
        return Response(AcademicNotificationSerializer(notification).data)

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        from django.utils import timezone

        updated = AcademicNotification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        return Response({"marked_read": updated})

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = AcademicNotification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({"unread_count": count})


# ---------------------------------------------------------------------------
# P5: Analytics ViewSets
# ---------------------------------------------------------------------------


class SubjectPerformanceViewSet(viewsets.ModelViewSet):
    """CRUD for subject performance analytics."""

    serializer_class = SubjectPerformanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["subject", "academic_year", "term"]
    search_fields = ["subject__name", "subject__code"]
    ordering_fields = ["average_score", "pass_rate", "calculated_at"]
    ordering = ["-average_score"]

    def get_queryset(self):
        return SubjectPerformance.objects.filter(subject__school=self.request.user.school).select_related(
            "subject", "academic_year", "term"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=False, methods=["post"], url_path="calculate")
    def calculate(self, request):
        """Calculate performance stats for all subjects."""
        from django.db.models import Avg, F, Max, Min
        from services.gradebook.models import Grade as GradeRecord

        academic_year_id = request.data.get("academic_year")
        if not academic_year_id:
            return Response(
                {"error": "academic_year is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        school = request.user.school
        subjects = Subject.objects.filter(school=school, is_active=True)
        created = 0
        for subject in subjects:
            grades = GradeRecord.objects.filter(
                exam_schedule__subject=subject,
                exam_schedule__exam__academic_year_id=academic_year_id,
                is_absent=False,
            )
            if not grades.exists():
                continue
            stats = grades.aggregate(
                avg=Avg("marks_obtained"),
                max=Max("marks_obtained"),
                min=Min("marks_obtained"),
            )
            total = grades.count()
            passed = grades.filter(marks_obtained__gte=F("exam_schedule__pass_marks")).count()
            # Grade distribution
            grade_dist = {}
            for grade_letter, lower, upper in [
                ("A", 90, 101),
                ("B", 80, 90),
                ("C", 70, 80),
                ("D", 60, 70),
                ("E", 50, 60),
                ("F", 0, 50),
            ]:
                count = grades.filter(marks_obtained__gte=lower, marks_obtained__lt=upper).count()
                if count > 0:
                    grade_dist[grade_letter] = count
            perf, _ = SubjectPerformance.objects.update_or_create(
                subject=subject,
                academic_year_id=academic_year_id,
                defaults={
                    "total_students": total,
                    "average_score": round(stats["avg"] or 0, 2),
                    "highest_score": stats["max"] or 0,
                    "lowest_score": stats["min"] or 0,
                    "pass_rate": round((passed / total * 100), 2) if total > 0 else 0,
                    "grade_distribution": grade_dist,
                },
            )
            created += 1
        return Response({"subjects_calculated": created})


class StudentProgressViewSet(viewsets.ModelViewSet):
    """CRUD for student progress reports."""

    serializer_class = StudentProgressReportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["student", "academic_year", "term", "subject", "trend"]
    search_fields = [
        "student__user__first_name",
        "student__user__last_name",
        "subject__name",
    ]
    ordering_fields = ["current_score", "score_change", "calculated_at"]
    ordering = ["-calculated_at"]

    def get_queryset(self):
        user = self.request.user
        qs = StudentProgressReport.objects.filter(student__school=user.school).select_related(
            "student__user", "academic_year", "term", "subject"
        )
        if user.role == "student":
            qs = qs.filter(student__user=user)
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "calculate"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=False, methods=["get"], url_path="my-progress")
    def my_progress(self, request):
        """Get progress reports for the current student."""
        if request.user.role != "student":
            return Response(
                {"detail": "This endpoint is for students only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = self.get_queryset().filter(student__user=request.user)
        return Response(StudentProgressReportSerializer(qs, many=True).data)


class TeacherEffectivenessViewSet(viewsets.ModelViewSet):
    """CRUD for teacher effectiveness metrics."""

    serializer_class = TeacherEffectivenessSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["teacher", "academic_year", "term", "subject"]
    search_fields = [
        "teacher__first_name",
        "teacher__last_name",
        "subject__name",
    ]
    ordering_fields = ["effectiveness_score", "average_student_score"]
    ordering = ["-effectiveness_score"]

    def get_queryset(self):
        return TeacherEffectiveness.objects.filter(teacher__school=self.request.user.school).select_related(
            "teacher", "academic_year", "term", "subject"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=False, methods=["get"], url_path="leaderboard")
    def leaderboard(self, request):
        """Get top teachers ranked by effectiveness."""
        academic_year_id = request.query_params.get("academic_year")
        qs = self.get_queryset()
        if academic_year_id:
            qs = qs.filter(academic_year_id=academic_year_id)
        qs = qs.order_by("-effectiveness_score")[:20]
        return Response(TeacherEffectivenessSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"], url_path="my-stats")
    def my_stats(self, request):
        """Get effectiveness stats for the current teacher."""
        if request.user.role != "teacher":
            return Response(
                {"detail": "This endpoint is for teachers only."},
                status=status.HTTP_403_FORBIDDEN,
            )
        qs = self.get_queryset().filter(teacher=request.user)
        return Response(TeacherEffectivenessSerializer(qs, many=True).data)
