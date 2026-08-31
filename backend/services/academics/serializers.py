"""
Academics Service — Serializers
"""

from rest_framework import serializers

from .models import (
    AcademicEvent,
    AcademicHoliday,
    AcademicNotification,
    AcademicTerm,
    AcademicTranscript,
    Assignment,
    AssignmentSubmission,
    CurriculumStandard,
    EvaluationComment,
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


class TeacherWorkloadConfigSerializer(serializers.ModelSerializer):
    """Serializer for teacher workload configuration."""

    class Meta:
        model = TeacherWorkloadConfig
        fields = [
            "id",
            "school",
            "max_periods_per_week",
            "max_periods_per_day",
            "max_subjects",
            "max_classes",
            "min_periods_per_week",
            "warning_threshold_pct",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "school", "created_at", "updated_at"]


class TeacherWorkloadSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for teacher workload snapshots."""

    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    teacher_email = serializers.CharField(source="teacher.email", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model = TeacherWorkloadSnapshot
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "teacher_email",
            "academic_year",
            "academic_year_name",
            "week_start_date",
            "total_periods",
            "periods_per_day",
            "subjects_taught",
            "classes_taught",
            "utilization_pct",
            "is_overloaded",
            "is_underloaded",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TeacherWorkloadSummarySerializer(serializers.Serializer):
    """Read-only serializer for live workload summary (not a model)."""

    teacher_id = serializers.UUIDField()
    teacher_name = serializers.CharField()
    employee_id = serializers.CharField()
    department = serializers.CharField()
    total_periods_per_week = serializers.IntegerField()
    periods_per_day = serializers.DictField()
    subjects_taught = serializers.IntegerField()
    classes_taught = serializers.IntegerField()
    students_taught = serializers.IntegerField()
    utilization_pct = serializers.DecimalField(max_digits=5, decimal_places=2)
    max_periods = serializers.IntegerField()
    status = serializers.CharField()


class EvaluationCriteriaSerializer(serializers.ModelSerializer):
    """Serializer for evaluation criteria."""

    class Meta:
        model = EvaluationCriteria
        fields = [
            "id",
            "school",
            "name",
            "description",
            "category",
            "max_score",
            "weight",
            "is_active",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "school", "created_at", "updated_at"]


class EvaluationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for evaluation templates."""

    criteria = EvaluationCriteriaSerializer(many=True, read_only=True)
    criteria_ids = serializers.PrimaryKeyRelatedField(
        queryset=EvaluationCriteria.objects.all(),
        many=True,
        write_only=True,
        source="criteria",
        required=False,
    )

    class Meta:
        model = EvaluationTemplate
        fields = [
            "id",
            "school",
            "name",
            "description",
            "eval_type",
            "criteria",
            "criteria_ids",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "school", "created_at", "updated_at"]


class EvaluationScoreSerializer(serializers.ModelSerializer):
    """Serializer for individual criterion scores."""

    criterion_name = serializers.CharField(source="criterion.name", read_only=True)
    criterion_max_score = serializers.IntegerField(source="criterion.max_score", read_only=True)
    criterion_weight = serializers.DecimalField(
        source="criterion.weight", max_digits=5, decimal_places=2, read_only=True
    )
    scored_by_name = serializers.CharField(source="scored_by.full_name", read_only=True, default=None)

    class Meta:
        model = EvaluationScore
        fields = [
            "id",
            "evaluation",
            "criterion",
            "criterion_name",
            "criterion_max_score",
            "criterion_weight",
            "score",
            "weighted_score",
            "evidence",
            "comments",
            "scored_by",
            "scored_by_name",
            "scored_at",
            "updated_at",
        ]
        read_only_fields = ["id", "weighted_score", "scored_at", "updated_at"]


class EvaluationCommentSerializer(serializers.ModelSerializer):
    """Serializer for evaluation comments."""

    author_name = serializers.CharField(source="author.full_name", read_only=True)

    class Meta:
        model = EvaluationComment
        fields = [
            "id",
            "evaluation",
            "comment_type",
            "author",
            "author_name",
            "content",
            "is_private",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


class TeacherEvaluationSerializer(serializers.ModelSerializer):
    """Serializer for teacher evaluations with nested scores and comments."""

    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    teacher_email = serializers.CharField(source="teacher.email", read_only=True)
    template_name = serializers.CharField(source="template.name", read_only=True, default=None)
    template_eval_type = serializers.CharField(source="template.eval_type", read_only=True, default=None)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True, default=None)
    scores = EvaluationScoreSerializer(many=True, read_only=True)
    comments_list = EvaluationCommentSerializer(many=True, read_only=True)
    score_percentage = serializers.FloatField(read_only=True)
    score_display = serializers.CharField(read_only=True)

    class Meta:
        model = TeacherEvaluation
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "teacher_email",
            "template",
            "template_name",
            "template_eval_type",
            "academic_year",
            "academic_year_name",
            "title",
            "description",
            "evaluation_period",
            "status",
            "overall_score",
            "max_possible_score",
            "score_percentage",
            "score_display",
            "strength",
            "areas_for_growth",
            "action_plan",
            "evaluator_notes",
            "teacher_comments",
            "created_by",
            "created_by_name",
            "reviewed_by",
            "reviewed_by_name",
            "review_date",
            "scores",
            "comments_list",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "overall_score",
            "max_possible_score",
            "created_by",
            "created_at",
            "updated_at",
        ]


class AcademicTranscriptSerializer(serializers.ModelSerializer):
    """Serializer for academic transcripts."""

    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    admission_number = serializers.CharField(source="student.admission_number", read_only=True)
    student_dob = serializers.DateField(source="student.date_of_birth", read_only=True)
    student_gender = serializers.CharField(source="student.gender", read_only=True)
    grade_name = serializers.SerializerMethodField()
    classroom_name = serializers.SerializerMethodField()
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    school_name = serializers.CharField(source="student.school.name", read_only=True)
    school_address = serializers.CharField(source="student.school.address", read_only=True)
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default=None)
    verified_by_name = serializers.CharField(source="verified_by.full_name", read_only=True, default=None)
    score_display = serializers.CharField(read_only=True)
    subjects_data = serializers.JSONField(read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = AcademicTranscript
        fields = [
            "id",
            "student",
            "student_name",
            "admission_number",
            "student_dob",
            "student_gender",
            "grade_name",
            "classroom_name",
            "academic_year",
            "academic_year_name",
            "school_name",
            "school_address",
            "transcript_number",
            "status",
            "total_marks",
            "obtained_marks",
            "percentage",
            "gpa",
            "grade_letter",
            "rank_in_class",
            "rank_in_grade",
            "attendance_days",
            "total_school_days",
            "attendance_percentage",
            "subjects_data",
            "score_display",
            "principal_name",
            "class_teacher_name",
            "remarks",
            "generated_by",
            "generated_by_name",
            "verified_by",
            "verified_by_name",
            "verified_at",
            "generated_at",
            "pdf_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "transcript_number",
            "generated_at",
            "created_at",
            "updated_at",
        ]

    def get_grade_name(self, obj):
        try:
            return obj.student.user.enrollments.filter(academic_year=obj.academic_year).first().classroom.grade.name
        except Exception:
            return ""

    def get_classroom_name(self, obj):
        try:
            return str(obj.student.user.enrollments.filter(academic_year=obj.academic_year).first().classroom)
        except Exception:
            return ""

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            return self.context["request"].build_absolute_uri(obj.pdf_file.url)
        return None


# ---------------------------------------------------------------------------
# P1: Academic Calendar Serializers
# ---------------------------------------------------------------------------


class AcademicTermSerializer(serializers.ModelSerializer):
    """Serializer for academic terms."""

    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    duration_days = serializers.IntegerField(read_only=True)
    events_count = serializers.SerializerMethodField()

    class Meta:
        model = AcademicTerm
        fields = [
            "id",
            "school",
            "academic_year",
            "academic_year_name",
            "name",
            "term_type",
            "start_date",
            "end_date",
            "report_card_date",
            "parent_teacher_date",
            "enrollment_deadline",
            "is_current",
            "duration_days",
            "events_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "school", "created_at", "updated_at"]

    def get_events_count(self, obj):
        return obj.events.count()


class AcademicEventSerializer(serializers.ModelSerializer):
    """Serializer for academic calendar events."""

    event_type_display = serializers.CharField(source="get_event_type_display", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    term_name = serializers.CharField(source="term.name", read_only=True, default=None)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)
    duration_days = serializers.IntegerField(read_only=True)
    grade_names = serializers.SerializerMethodField()
    subject_names = serializers.SerializerMethodField()

    class Meta:
        model = AcademicEvent
        fields = [
            "id",
            "school",
            "academic_year",
            "academic_year_name",
            "term",
            "term_name",
            "title",
            "description",
            "event_type",
            "event_type_display",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "is_all_day",
            "affected_grades",
            "grade_names",
            "affected_subjects",
            "subject_names",
            "is_recurring",
            "recurrence_rule",
            "location",
            "created_by",
            "created_by_name",
            "is_published",
            "duration_days",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "school", "created_at", "updated_at"]

    def get_grade_names(self, obj):
        return list(obj.affected_grades.values_list("name", flat=True))

    def get_subject_names(self, obj):
        return list(obj.affected_subjects.values_list("name", flat=True))


class AcademicHolidaySerializer(serializers.ModelSerializer):
    """Serializer for academic holidays."""

    duration_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = AcademicHoliday
        fields = [
            "id",
            "school",
            "academic_year",
            "name",
            "date",
            "end_date",
            "holiday_type",
            "description",
            "duration_days",
            "created_at",
        ]
        read_only_fields = ["id", "school", "created_at"]


# ---------------------------------------------------------------------------
# P2: Assignment & Homework Serializers
# ---------------------------------------------------------------------------


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for assignments."""

    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    subject_code = serializers.CharField(source="assignment.subject.code", read_only=True)
    teacher_name = serializers.CharField(source="assignment.teacher.full_name", read_only=True)
    classroom_name = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    submission_count = serializers.IntegerField(read_only=True)
    average_score = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "id",
            "assignment",
            "title",
            "description",
            "assignment_type",
            "status",
            "due_date",
            "due_time",
            "max_score",
            "weight_percentage",
            "allow_late_submissions",
            "late_penalty_per_day",
            "attachments",
            "created_by",
            "published_at",
            "subject_name",
            "subject_code",
            "teacher_name",
            "classroom_name",
            "is_overdue",
            "submission_count",
            "average_score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "published_at",
            "created_at",
            "updated_at",
        ]

    def get_classroom_name(self, obj):
        return str(obj.assignment.classroom)


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for assignment submissions."""

    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    graded_by_name = serializers.CharField(source="graded_by.full_name", read_only=True, default=None)
    score_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = [
            "id",
            "assignment",
            "assignment_title",
            "student",
            "student_name",
            "status",
            "content",
            "attachments",
            "submitted_at",
            "is_late",
            "score",
            "grade_letter",
            "score_percentage",
            "feedback",
            "graded_by",
            "graded_by_name",
            "graded_at",
            "submission_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "submitted_at",
            "is_late",
            "submission_number",
            "created_at",
            "updated_at",
        ]


class HomeworkTrackerSerializer(serializers.ModelSerializer):
    """Serializer for daily homework tracking."""

    subject_name = serializers.CharField(source="subject.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    classroom_name = serializers.SerializerMethodField()

    class Meta:
        model = HomeworkTracker
        fields = [
            "id",
            "classroom",
            "classroom_name",
            "academic_year",
            "date",
            "subject",
            "subject_name",
            "teacher",
            "teacher_name",
            "description",
            "due_date",
            "is_completed",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_classroom_name(self, obj):
        return str(obj.classroom)


# ---------------------------------------------------------------------------
# P3: Exam Management Serializers
# ---------------------------------------------------------------------------


class QuestionBankSerializer(serializers.ModelSerializer):
    """Serializer for question bank entries."""

    subject_name = serializers.CharField(source="subject.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = QuestionBank
        fields = [
            "id",
            "school",
            "subject",
            "subject_name",
            "question_type",
            "difficulty",
            "question_text",
            "options",
            "correct_answer",
            "explanation",
            "marks",
            "tags",
            "created_by",
            "created_by_name",
            "is_active",
            "usage_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "school",
            "usage_count",
            "created_at",
            "updated_at",
        ]


class ExamPaperSerializer(serializers.ModelSerializer):
    """Serializer for exam papers."""

    subject_name = serializers.CharField(source="subject.name", read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default=None)

    class Meta:
        model = ExamPaper
        fields = [
            "id",
            "school",
            "subject",
            "subject_name",
            "academic_year",
            "title",
            "total_marks",
            "duration_minutes",
            "questions",
            "question_distribution",
            "status",
            "created_by",
            "created_by_name",
            "question_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "school",
            "created_at",
            "updated_at",
        ]


# ---------------------------------------------------------------------------
# P4: Notification Serializer
# ---------------------------------------------------------------------------


class AcademicNotificationSerializer(serializers.ModelSerializer):
    """Serializer for academic notifications."""

    notification_type_display = serializers.CharField(source="get_notification_type_display", read_only=True)
    recipient_name = serializers.CharField(source="recipient.full_name", read_only=True)

    class Meta:
        model = AcademicNotification
        fields = [
            "id",
            "school",
            "recipient",
            "recipient_name",
            "notification_type",
            "notification_type_display",
            "priority",
            "title",
            "message",
            "action_url",
            "metadata",
            "is_read",
            "read_at",
            "is_emailed",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "school",
            "is_read",
            "read_at",
            "is_emailed",
            "created_at",
        ]


# ---------------------------------------------------------------------------
# P5: Analytics Serializers
# ---------------------------------------------------------------------------


class SubjectPerformanceSerializer(serializers.ModelSerializer):
    """Serializer for subject performance analytics."""

    subject_name = serializers.CharField(source="subject.name", read_only=True)
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    term_name = serializers.CharField(source="term.name", read_only=True, default=None)

    class Meta:
        model = SubjectPerformance
        fields = [
            "id",
            "subject",
            "subject_name",
            "subject_code",
            "academic_year",
            "academic_year_name",
            "term",
            "term_name",
            "total_students",
            "average_score",
            "median_score",
            "highest_score",
            "lowest_score",
            "pass_rate",
            "grade_distribution",
            "calculated_at",
        ]
        read_only_fields = ["id", "calculated_at"]


class StudentProgressReportSerializer(serializers.ModelSerializer):
    """Serializer for student progress reports."""

    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    term_name = serializers.CharField(source="term.name", read_only=True, default=None)

    class Meta:
        model = StudentProgressReport
        fields = [
            "id",
            "student",
            "student_name",
            "academic_year",
            "academic_year_name",
            "term",
            "term_name",
            "subject",
            "subject_name",
            "current_score",
            "previous_score",
            "score_change",
            "trend",
            "attendance_rate",
            "assignment_completion_rate",
            "teacher_remarks",
            "strengths",
            "areas_for_improvement",
            "calculated_at",
        ]
        read_only_fields = ["id", "calculated_at"]


class TeacherEffectivenessSerializer(serializers.ModelSerializer):
    """Serializer for teacher effectiveness metrics."""

    teacher_name = serializers.CharField(source="teacher.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    term_name = serializers.CharField(source="term.name", read_only=True, default=None)

    class Meta:
        model = TeacherEffectiveness
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "academic_year",
            "academic_year_name",
            "term",
            "term_name",
            "subject",
            "subject_name",
            "total_students",
            "average_student_score",
            "pass_rate",
            "evaluation_score",
            "lesson_completion_rate",
            "assignment_count",
            "average_assignment_score",
            "attendance_rate",
            "effectiveness_score",
            "calculated_at",
        ]
        read_only_fields = ["id", "calculated_at"]
