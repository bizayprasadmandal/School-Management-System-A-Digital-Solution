"""
Student Service — ViewSets with role-based access
"""

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db.models import CharField, OuterRef, Q, Subquery, Value
from django.db.models.functions import Concat
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from services.auth.utils import generate_secure_password

from .filters import StudentFilter
from .models import AcademicYear, Classroom, Document, Enrollment, Grade, Student
from .serializers import (
    ClassroomSerializer,
    DocumentSerializer,
    GradeSerializer,
    StudentCreateSerializer,
    StudentDetailSerializer,
    StudentListSerializer,
)

MAX_PROMOTE_BATCH = 200


class StudentViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for student records.
    Access control:
      - Admin: full CRUD on own school
      - Teacher: read-only, own classroom students
      - Student: read-only, own profile
      - Parent: read-only, own children
    """

    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StudentFilter
    search_fields = ["user__first_name", "user__last_name", "admission_number", "roll_number"]
    ordering_fields = ["user__first_name", "admission_number", "admission_date"]
    ordering = ["user__first_name"]

    def get_queryset(self):
        user = self.request.user
        # Annotate current classroom name (e.g. "Grade 5 A") on the active enrollment to avoid N+1
        current_class_name_subquery = (
            Enrollment.objects.filter(student=OuterRef("pk"), is_active=True)
            .annotate(
                full_name=Concat("classroom__grade__name", Value(" "), "classroom__name", output_field=CharField())
            )
            .values("full_name")[:1]
        )

        qs = (
            Student.objects.filter(school=user.school)
            .select_related("user", "school")
            .prefetch_related("enrollments__classroom__grade")
            .annotate(current_class_name=Subquery(current_class_name_subquery))
        )
        # Detail-only relations (enrollment academic year, guardians) are
        # prefetched just for retrieve so the hot list endpoint stays lean.
        if self.action == "retrieve":
            qs = qs.prefetch_related(
                "enrollments__academic_year",
                "studentguardian_set__guardian__user",
            )

        if user.role == "student":
            return qs.filter(user=user)
        if user.role == "parent":
            return qs.filter(guardians__user=user)
        if user.role == "teacher":
            # Teachers see students in their assigned classrooms
            return qs.filter(
                enrollments__classroom__assignments__teacher=user,
                enrollments__is_active=True,
            ).distinct()
        return qs  # admin / super_admin sees all in school

    def get_serializer_class(self):
        if self.action == "list":
            return StudentListSerializer
        if self.action == "create":
            return StudentCreateSerializer
        return StudentDetailSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "promote"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @extend_schema(summary="Get student's attendance summary")
    @action(detail=True, methods=["get"], url_path="attendance-summary")
    def attendance_summary(self, request, pk=None):
        from services.attendance.models import AttendanceRecord

        student = self.get_object()
        academic_year_id = request.query_params.get("academic_year")
        qs = AttendanceRecord.objects.filter(student=student)
        if academic_year_id:
            qs = qs.filter(academic_year_id=academic_year_id)
        total = qs.count()
        present = qs.filter(status__in=["P", "L"]).count()
        absent = qs.filter(status="A").count()
        return Response(
            {
                "total_days": total,
                "present": present,
                "absent": absent,
                "late": qs.filter(status="L").count(),
                "excused": qs.filter(status="E").count(),
                "attendance_percentage": round((present / total * 100) if total else 0, 2),
            }
        )

    @extend_schema(summary="Get student's grade summary")
    @action(detail=True, methods=["get"], url_path="grade-summary")
    def grade_summary(self, request, pk=None):
        from services.gradebook.models import Grade as GradeRecord

        student = self.get_object()
        grades = GradeRecord.objects.filter(student=student).select_related(
            "exam_schedule__subject", "exam_schedule__exam"
        )
        return Response(
            {
                "grades": [
                    {
                        "subject": g.exam_schedule.subject.name,
                        "exam": g.exam_schedule.exam.name,
                        "marks_obtained": g.marks_obtained,
                        "max_marks": g.exam_schedule.max_marks,
                        "percentage": g.percentage,
                        "is_pass": g.is_pass,
                    }
                    for g in grades
                ]
            }
        )

    @extend_schema(summary="Get student's cumulative GPA")
    @action(detail=True, methods=["get"], url_path="cumulative-gpa")
    def cumulative_gpa(self, request, pk=None):
        """Compute cumulative weighted GPA across all exams in the current academic year."""
        student = self.get_object()
        from services.gradebook.tasks import compute_cumulative_gpa

        result = compute_cumulative_gpa(str(student.id), student.school)
        if result is None:
            return Response({"detail": "No grades found for current academic year."}, status=404)
        return Response(result)

    @extend_schema(summary="Promote students to next grade")
    @action(detail=False, methods=["post"], url_path="promote")
    def promote(self, request):
        """Bulk-promote a list of students to a target classroom."""
        student_ids = request.data.get("student_ids", [])
        target_classroom_id = request.data.get("target_classroom_id")
        academic_year_id = request.data.get("academic_year_id")

        if not all([student_ids, target_classroom_id, academic_year_id]):
            return Response(
                {"error": "student_ids, target_classroom_id and academic_year_id are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enforce bulk size limit
        if len(student_ids) > MAX_PROMOTE_BATCH:
            return Response(
                {"error": f"Cannot promote more than {MAX_PROMOTE_BATCH} students at once."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.db import transaction

        # Tenant isolation: target classroom + academic year must belong to this school.
        if not AcademicYear.objects.filter(id=academic_year_id, school=request.user.school).exists():
            return Response(
                {"error": "Invalid academic year for this school."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        promoted = []
        with transaction.atomic():
            # Lock target classroom row to prevent race conditions
            try:
                classroom = Classroom.objects.select_for_update().get(
                    id=target_classroom_id, school=request.user.school
                )
            except Classroom.DoesNotExist:
                return Response(
                    {"error": "Target classroom not found in your school."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            for sid in student_ids:
                try:
                    student = Student.objects.get(id=sid, school=request.user.school)
                    old_enrollment = student.enrollments.filter(is_active=True).first()
                    if old_enrollment:
                        old_enrollment.is_active = False
                        old_enrollment.status = Enrollment.Status.GRADUATED
                        old_enrollment.save()
                    Enrollment.objects.create(
                        student=student,
                        classroom=classroom,
                        academic_year_id=academic_year_id,
                        promoted_from=old_enrollment,
                    )
                    promoted.append(str(student.id))
                except Student.DoesNotExist:
                    continue

        return Response({"promoted_count": len(promoted), "promoted_student_ids": promoted})

    @extend_schema(summary="Upload student document")
    @action(detail=True, methods=["post", "get"], url_path="documents")
    def documents(self, request, pk=None):
        student = self.get_object()
        if request.method == "GET":
            docs = Document.objects.filter(student=student)
            return Response(DocumentSerializer(docs, many=True).data)
        serializer = DocumentSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(student=student)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Restore a soft-deleted (inactive) student")
    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        """Restore an inactive student back to active status."""
        student = self.get_object()
        if not student.is_active:
            student.is_active = True
            student.save(update_fields=["is_active"])
            # Also reactivate user account and enrollments
            if student.user and not student.user.is_active:
                student.user.is_active = True
                student.user.save(update_fields=["is_active"])
            student.enrollments.filter(is_active=False).update(is_active=True)
            return Response({"detail": f"Student {student.admission_number} restored."})
        return Response({"detail": "Student is already active."}, status=400)

    @extend_schema(summary="Get/update current user's student profile")
    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        """
        GET: Return the student profile linked to the current authenticated user.
        PATCH: Update limited self-service fields (bio, interests, learning_goals).
        """
        try:
            student = (
                Student.objects.filter(user=request.user, school=request.user.school)
                .prefetch_related(
                    "enrollments__classroom__grade",
                    "enrollments__academic_year",
                    "studentguardian_set__guardian__user",
                )
                .get()
            )
        except Student.DoesNotExist:
            return Response(
                {"detail": "No student profile found for this user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == "PATCH":
            from .serializers import StudentSelfProfileSerializer

            serializer = StudentSelfProfileSerializer(student, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # Return full profile after update
            return Response(StudentDetailSerializer(student, context={"request": request}).data)

        serializer = StudentDetailSerializer(student, context={"request": request})
        return Response(serializer.data)

    @extend_schema(summary="Import students from CSV")
    @action(detail=False, methods=["post"], url_path="import-csv")
    def import_csv(self, request):
        """
        Bulk-import students from CSV data.
        Expected CSV columns (header row required):
        first_name, last_name, email, admission_number, date_of_birth,
        gender, classroom_name, address, city, state, country, password
        The ``password`` column is optional — when omitted, a secure random
        password is generated per student and returned in the response.
        """
        import csv
        import io

        from django.db import transaction
        from services.auth.models import User, UserRole

        csv_text = request.data.get("csv_data", "")
        if not csv_text:
            return Response({"error": "csv_data field is required."}, status=400)

        reader = csv.DictReader(io.StringIO(csv_text))
        max_records = int(request.data.get("max_records", 100))
        row_count = 0
        imported = 0
        errors = []
        generated_passwords = {}

        school = request.user.school
        current_year = AcademicYear.objects.filter(school=school, is_current=True).first()
        if not current_year:
            return Response({"error": "No current academic year set."}, status=400)

        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                if row_count >= max_records:
                    errors.append(f"Row {row_num}: Max records ({max_records}) reached, skipping remaining")
                    break
                try:
                    email = row.get("email", "").strip().lower()
                    if User.objects.filter(email=email).exists():
                        errors.append(f"Row {row_num}: email '{email}' already exists")
                        continue

                    password = (row.get("password") or "").strip()
                    generated = not password
                    if generated:
                        password = generate_secure_password()
                    classroom_name = row.get("classroom_name", "").strip()
                    classroom = Classroom.objects.filter(school=school, name=classroom_name).first()
                    if not classroom:
                        errors.append(f"Row {row_num}: classroom '{classroom_name}' not found")
                        continue

                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        first_name=row.get("first_name", "").strip(),
                        last_name=row.get("last_name", "").strip(),
                        role=UserRole.STUDENT,
                        school=school,
                    )
                    if generated:
                        generated_passwords[email] = password
                    student = Student.objects.create(
                        user=user,
                        school=school,
                        admission_number=row.get("admission_number", "").strip(),
                        date_of_birth=row.get("date_of_birth", "").strip(),
                        gender=row.get("gender", "M").strip().upper(),
                        address=row.get("address", "").strip(),
                        city=row.get("city", "").strip(),
                        state=row.get("state", "").strip(),
                        country=row.get("country", "").strip(),
                        admission_date=timezone.now().date(),
                    )
                    Enrollment.objects.create(
                        student=student,
                        classroom=classroom,
                        academic_year=current_year,
                    )
                    imported += 1
                    row_count += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)[:100]}")

        return Response(
            {
                "imported": imported,
                "errors": errors[:20],  # Limit error reporting
                "generated_passwords": generated_passwords,
            }
        )


class ClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = ClassroomSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "grade__name"]

    def get_queryset(self):
        return Classroom.objects.filter(school=self.request.user.school).select_related(
            "grade", "class_teacher", "academic_year"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "import_csv"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=True, methods=["get"], url_path="students")
    def students(self, request, pk=None):
        classroom = self.get_object()
        students = Student.objects.filter(enrollments__classroom=classroom, enrollments__is_active=True).select_related(
            "user"
        )
        return Response(StudentListSerializer(students, many=True).data)

    @extend_schema(summary="Import classrooms from CSV")
    @action(detail=False, methods=["post"], url_path="import-csv")
    def import_csv(self, request):
        """
        Bulk-import classrooms from CSV data.
        Expected CSV columns (header row required):
        grade_name, name, capacity, room_number, class_teacher_email, academic_year_name

        - ``grade_name`` (e.g. "Grade 5") and ``name`` (e.g. "A") are required.
        - If no ``academic_year_name`` is given, the current academic year is used.
        - ``class_teacher_email`` is optional; must match an existing teacher user.
        """
        import csv
        import io

        from django.db import transaction

        csv_text = request.data.get("csv_data", "")
        if not csv_text:
            return Response({"error": "csv_data field is required."}, status=400)

        school = request.user.school
        reader = csv.DictReader(io.StringIO(csv_text))
        max_records = int(request.data.get("max_records", 100))
        imported = 0
        errors = []
        row_count = 0

        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):
                if row_count >= max_records:
                    errors.append(f"Row {row_num}: Max records ({max_records}) reached, skipping remaining")
                    break
                try:
                    grade_name = (row.get("grade_name") or "").strip()
                    name = (row.get("name") or "").strip()
                    if not grade_name or not name:
                        errors.append(f"Row {row_num}: grade_name and name are required")
                        continue
                    grade = Grade.objects.filter(school=school, name=grade_name).first()
                    if not grade:
                        errors.append(f"Row {row_num}: grade '{grade_name}' not found")
                        continue

                    academic_year_name = (row.get("academic_year_name") or "").strip()
                    if academic_year_name:
                        academic_year = AcademicYear.objects.filter(school=school, name=academic_year_name).first()
                        if not academic_year:
                            errors.append(f"Row {row_num}: academic year '{academic_year_name}' not found")
                            continue
                    else:
                        academic_year = AcademicYear.objects.filter(school=school, is_current=True).first()
                        if not academic_year:
                            errors.append(f"Row {row_num}: no current academic year set")
                            continue

                    class_teacher = None
                    teacher_email = (row.get("class_teacher_email") or "").strip()
                    if teacher_email:
                        from services.auth.models import User, UserRole

                        class_teacher = User.objects.filter(
                            email=teacher_email, school=school, role=UserRole.TEACHER
                        ).first()
                        if not class_teacher:
                            errors.append(f"Row {row_num}: teacher '{teacher_email}' not found")
                            continue

                    try:
                        capacity = int((row.get("capacity") or "40").strip() or 40)
                    except ValueError:
                        capacity = 40

                    _, created = Classroom.objects.get_or_create(
                        school=school,
                        grade=grade,
                        name=name,
                        academic_year=academic_year,
                        defaults={
                            "capacity": capacity,
                            "room_number": (row.get("room_number") or "").strip(),
                            "class_teacher": class_teacher,
                        },
                    )
                    if created:
                        imported += 1
                    else:
                        errors.append(f"Row {row_num}: classroom '{name}' already exists for this grade/year")
                    row_count += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)[:100]}")

        return Response({"imported": imported, "errors": errors[:20]})


class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ["level"]

    def get_queryset(self):
        from django.db.models import Count

        # Annotate counts directly on the queryset to avoid N+1 per grade
        return Grade.objects.filter(school=self.request.user.school).annotate(
            classroom_count=Count("classrooms", distinct=True),
            student_count=Count(
                "classrooms__enrollments",
                filter=Q(classrooms__enrollments__is_active=True),
                distinct=True,
            ),
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
