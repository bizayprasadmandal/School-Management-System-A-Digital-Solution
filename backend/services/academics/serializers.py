"""
Academics Service — Serializers
"""

from rest_framework import serializers

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


class SubjectSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source="grade.name", read_only=True)

    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "code",
            "description",
            "grade",
            "grade_name",
            "is_core",
            "is_elective",
            "max_marks",
            "pass_marks",
            "credit_hours",
            "is_active",
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
            "id",
            "teacher",
            "teacher_name",
            "subject",
            "subject_name",
            "classroom",
            "classroom_name",
            "academic_year",
            "academic_year_name",
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
            "id",
            "user",
            "full_name",
            "email",
            "phone",
            "avatar",
            "employee_id",
            "date_of_birth",
            "gender",
            "qualification",
            "specialization",
            "joining_date",
            "experience_years",
            "department",
            "address",
            "bio",
            "is_active",
            "current_assignments",
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

            current_year = AcademicYear.objects.filter(school=obj.school, is_current=True).first()
            if not current_year:
                return []
            assignments = obj.user.assignments.filter(academic_year=current_year)
        return TeacherAssignmentSerializer(
            assignments,
            many=True,
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
            "qualification",
            "specialization",
            "department",
            "experience_years",
            "bio",
        ]


class LessonPlanSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="assignment.teacher.full_name", read_only=True)
    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    classroom_name = serializers.SerializerMethodField()

    class Meta:
        model = LessonPlan
        fields = [
            "id",
            "assignment",
            "teacher_name",
            "subject_name",
            "classroom_name",
            "title",
            "topic",
            "objectives",
            "content",
            "resources",
            "date",
            "duration_minutes",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_classroom_name(self, obj):
        return str(obj.assignment.classroom)


class StudentSubjectEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for student-subject enrollments."""

    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    admission_number = serializers.CharField(source="student.admission_number", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    grade_name = serializers.CharField(source="subject.grade.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model = StudentSubjectEnrollment
        fields = [
            "id",
            "student",
            "student_name",
            "admission_number",
            "subject",
            "subject_name",
            "subject_code",
            "grade_name",
            "academic_year",
            "academic_year_name",
            "enrolled_date",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "enrolled_date", "created_at", "updated_at"]


class CurriculumStandardSerializer(serializers.ModelSerializer):
    """Serializer for curriculum standards."""

    grade_name = serializers.CharField(source="grade.name", read_only=True, default=None)
    subject_name = serializers.CharField(source="subject.name", read_only=True, default=None)
    mappings_count = serializers.SerializerMethodField()

    class Meta:
        model = CurriculumStandard
        fields = [
            "id",
            "school",
            "framework",
            "code",
            "name",
            "description",
            "grade",
            "grade_name",
            "subject",
            "subject_name",
            "domain",
            "cluster",
            "is_active",
            "mappings_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "school", "created_at", "updated_at"]

    def get_mappings_count(self, obj):
        return obj.subject_mappings.count()


class SubjectStandardMappingSerializer(serializers.ModelSerializer):
    """Serializer for subject-standard mappings."""

    subject_name = serializers.CharField(source="subject.name", read_only=True)
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    standard_code = serializers.CharField(source="standard.code", read_only=True)
    standard_name = serializers.CharField(source="standard.name", read_only=True)
    standard_framework = serializers.CharField(source="standard.framework", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    mapped_by_name = serializers.CharField(source="mapped_by.full_name", read_only=True, default=None)

    class Meta:
        model = SubjectStandardMapping
        fields = [
            "id",
            "subject",
            "subject_name",
            "subject_code",
            "standard",
            "standard_code",
            "standard_name",
            "standard_framework",
            "academic_year",
            "academic_year_name",
            "coverage_level",
            "notes",
            "mapped_by",
            "mapped_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SyllabusTopicSerializer(serializers.ModelSerializer):
    """Serializer for syllabus topics."""

    class Meta:
        model = SyllabusTopic
        fields = [
            "id",
            "syllabus",
            "order",
            "title",
            "description",
            "learning_outcomes",
            "estimated_hours",
            "status",
            "started_at",
            "completed_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SyllabusSerializer(serializers.ModelSerializer):
    """Serializer for syllabus with nested topics."""

    subject_name = serializers.CharField(source="subject.name", read_only=True)
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    grade_name = serializers.CharField(source="subject.grade.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)
    topics = SyllabusTopicSerializer(many=True, read_only=True)
    topic_count = serializers.IntegerField(read_only=True)
    completed_topic_count = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Syllabus
        fields = [
            "id",
            "subject",
            "subject_name",
            "subject_code",
            "grade_name",
            "academic_year",
            "academic_year_name",
            "term",
            "title",
            "description",
            "learning_objectives",
            "resources",
            "assessment_criteria",
            "total_hours",
            "status",
            "created_by",
            "created_by_name",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejection_reason",
            "topics",
            "topic_count",
            "completed_topic_count",
            "progress_percentage",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
        ]
