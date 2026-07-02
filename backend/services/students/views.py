"""
Student Service — ViewSets with role-based access
"""

from django.db.models import Q
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Student, Guardian, Enrollment, Grade, Classroom, Document
from .serializers import (
    StudentListSerializer, StudentDetailSerializer, StudentCreateSerializer,
    GuardianSerializer, EnrollmentSerializer, GradeSerializer,
    ClassroomSerializer, DocumentSerializer,
)
from .filters import StudentFilter
from core.permissions import (
    IsSchoolAdmin, IsTeacher, IsStudent, IsParent, IsSchoolMember,
)
from core.pagination import StandardResultsSetPagination


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
        qs = Student.objects.filter(school=user.school).select_related(
            "user", "school"
        ).prefetch_related("enrollments__classroom__grade")

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
        return Response({
            "total_days": total,
            "present": present,
            "absent": absent,
            "late": qs.filter(status="L").count(),
            "excused": qs.filter(status="E").count(),
            "attendance_percentage": round((present / total * 100) if total else 0, 2),
        })

    @extend_schema(summary="Get student's grade summary")
    @action(detail=True, methods=["get"], url_path="grade-summary")
    def grade_summary(self, request, pk=None):
        from services.gradebook.models import Grade as GradeRecord
        student = self.get_object()
        grades = GradeRecord.objects.filter(
            student=student
        ).select_related("exam_schedule__subject", "exam_schedule__exam")
        return Response({
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
        })

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

        from django.db import transaction
        promoted = []
        with transaction.atomic():
            for sid in student_ids:
                try:
                    student = Student.objects.get(id=sid, school=request.user.school)
                    old_enrollment = student.enrollments.filter(is_active=True).first()
                    if old_enrollment:
                        old_enrollment.is_active = False
                        old_enrollment.status = Enrollment.Status.GRADUATED
                        old_enrollment.save()
                    new_enrollment = Enrollment.objects.create(
                        student=student,
                        classroom_id=target_classroom_id,
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


class ClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = ClassroomSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "grade__name"]

    def get_queryset(self):
        return Classroom.objects.filter(
            school=self.request.user.school
        ).select_related("grade", "class_teacher", "academic_year")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=True, methods=["get"], url_path="students")
    def students(self, request, pk=None):
        classroom = self.get_object()
        students = Student.objects.filter(
            enrollments__classroom=classroom, enrollments__is_active=True
        ).select_related("user")
        return Response(StudentListSerializer(students, many=True).data)


class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ["level"]

    def get_queryset(self):
        return Grade.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
