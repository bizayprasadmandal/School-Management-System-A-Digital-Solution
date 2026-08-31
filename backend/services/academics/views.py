"""
Academics Service — Views for subjects, teacher assignments, lesson plans, student-subject enrollments
"""

from uuid import uuid4

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember, IsTeacher
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    CurriculumStandard,
    LessonPlan,
    StudentSubjectEnrollment,
    Subject,
    SubjectStandardMapping,
    Syllabus,
    SyllabusTopic,
    TeacherAssignment,
    TeacherProfile,
)
from .serializers import (
    CurriculumStandardSerializer,
    LessonPlanSerializer,
    StudentSubjectEnrollmentSerializer,
    SubjectSerializer,
    SubjectStandardMappingSerializer,
    SyllabusSerializer,
    SyllabusTopicSerializer,
    TeacherAssignmentSerializer,
    TeacherProfileSerializer,
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
