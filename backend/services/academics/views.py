"""
Academics Service — Views for subjects, teacher assignments, lesson plans
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Subject, TeacherAssignment, TeacherProfile, LessonPlan
from .serializers import (
    SubjectSerializer, TeacherAssignmentSerializer,
    TeacherProfileSerializer, LessonPlanSerializer,
)
from core.permissions import IsSchoolMember, IsTeacher, IsSchoolAdmin
from core.pagination import StandardResultsSetPagination


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["grade", "is_core", "is_elective", "is_active"]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "grade__level"]
    ordering = ["grade__level", "name"]

    def get_queryset(self):
        return Subject.objects.filter(
            school=self.request.user.school
        ).select_related("grade")

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
        qs = TeacherAssignment.objects.filter(
            teacher__school=user.school
        ).select_related("teacher", "subject", "classroom__grade", "academic_year")
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
        current_year = AcademicYear.objects.filter(
            school=self.request.user.school, is_current=True
        ).first()
        qs = TeacherProfile.objects.filter(
            school=self.request.user.school
        ).select_related("user")
        # Prefetch current year's assignments to avoid N+1 in serializer
        if current_year:
            from services.academics.models import TeacherAssignment
            from django.db.models import Prefetch
            qs = qs.prefetch_related(Prefetch(
                "user__assignments",
                queryset=TeacherAssignment.objects.filter(
                    academic_year=current_year
                ).select_related("subject", "classroom__grade", "academic_year"),
            ))
        return qs

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class LessonPlanViewSet(viewsets.ModelViewSet):
    serializer_class = LessonPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["assignment", "status", "date"]
    search_fields = ["title", "topic"]

    def get_queryset(self):
        user = self.request.user
        qs = LessonPlan.objects.filter(
            assignment__teacher__school=user.school
        ).select_related("assignment__teacher", "assignment__subject", "assignment__classroom")
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
