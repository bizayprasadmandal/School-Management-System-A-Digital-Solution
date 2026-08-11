"""
Academics Service — Views for subjects, teacher assignments, lesson plans
"""

from uuid import uuid4

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember, IsTeacher
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import LessonPlan, Subject, TeacherAssignment, TeacherProfile
from .serializers import LessonPlanSerializer, SubjectSerializer, TeacherAssignmentSerializer, TeacherProfileSerializer


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
