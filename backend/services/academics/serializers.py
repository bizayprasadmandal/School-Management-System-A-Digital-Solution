"""
Academics Service — Serializers
"""

from rest_framework import serializers
from .models import Subject, TeacherAssignment, TeacherProfile, LessonPlan


class SubjectSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source="grade.name", read_only=True)

    class Meta:
        model = Subject
        fields = [
            "id", "name", "code", "description", "grade", "grade_name",
            "is_core", "is_elective", "max_marks", "pass_marks",
            "credit_hours", "is_active",
        ]
        read_only_fields = ["id"]


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    classroom_name = serializers.SerializerMethodField()
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model = TeacherAssignment
        fields = [
            "id", "teacher", "teacher_name", "subject", "subject_name",
            "classroom", "classroom_name", "academic_year", "academic_year_name",
            "is_primary",
        ]

    def get_classroom_name(self, obj):
        return str(obj.classroom)


class TeacherProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    avatar = serializers.ImageField(source="user.avatar", read_only=True)
    current_assignments = serializers.SerializerMethodField()

    class Meta:
        model = TeacherProfile
        fields = [
            "id", "user", "full_name", "email", "phone", "avatar",
            "employee_id", "date_of_birth", "gender", "qualification",
            "specialization", "joining_date", "experience_years",
            "department", "address", "bio", "is_active", "current_assignments",
        ]
        read_only_fields = ["id"]

    def get_current_assignments(self, obj):
        """Return current-year teaching assignments for this teacher.

        Uses the prefetched `user__assignments` queryset from the ViewSet
        (via `.all()`) to avoid N+1 queries. The Prefetch in the ViewSet
        already filters to the current academic year.
        """
        assignments = obj.user.assignments.all()
        if not assignments:
            from services.students.models import AcademicYear
            current_year = AcademicYear.objects.filter(
                school=obj.school, is_current=True
            ).first()
            if not current_year:
                return []
            assignments = obj.user.assignments.filter(academic_year=current_year)
        return TeacherAssignmentSerializer(
            assignments, many=True,
            context=self.context,
        ).data


class TeacherSelfProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for teachers to update their own profile (limited fields).
    Admins still use TeacherProfileSerializer for full control.
    """
    class Meta:
        model = TeacherProfile
        fields = [
            "qualification", "specialization", "department",
            "experience_years", "bio",
        ]


class LessonPlanSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="assignment.teacher.full_name", read_only=True)
    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    classroom_name = serializers.SerializerMethodField()

    class Meta:
        model = LessonPlan
        fields = [
            "id", "assignment", "teacher_name", "subject_name", "classroom_name",
            "title", "topic", "objectives", "content", "resources",
            "date", "duration_minutes", "status", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_classroom_name(self, obj):
        return str(obj.assignment.classroom)
