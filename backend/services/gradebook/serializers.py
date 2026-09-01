"""
Gradebook Service — Serializers
"""

from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from .models import (
    Assessment,
    AssessmentSubmission,
    CategoryAssignment,
    CourseGradeCalculation,
    Exam,
    ExamSchedule,
    ExamType,
    ExtraCredit,
    ExtraCreditSubmission,
    GPACalculation,
    Grade,
    GradeChangeLog,
    GradeChangeProposal,
    GradeComment,
    GradeHistory,
    GradeNotification,
    GradingCategory,
    GradingScale,
    GradingScaleEntry,
    LatePenaltyRule,
    ReportCard,
    ReportCardComment,
    RubricAssessment,
    RubricCriterion,
    RubricLevel,
    RubricScore,
    RubricTemplate,
    Standard,
    StandardMasteryScale,
    StudentStandardGrade,
    Transcript,
    TranscriptEntry,
)


class GradingScaleSerializer(serializers.ModelSerializer):
    entries = serializers.SerializerMethodField()

    class Meta:
        model = GradingScale
        fields = ["id", "name", "school", "is_default", "entries"]
        read_only_fields = ["id"]

    def get_entries(self, obj):
        return GradingScaleEntrySerializer(obj.entries.all(), many=True).data


class GradingScaleEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = GradingScaleEntry
        fields = ["id", "scale", "grade_letter", "min_percentage", "max_percentage", "grade_point", "description"]


class ExamSerializer(serializers.ModelSerializer):
    exam_type_name = serializers.CharField(source="exam_type.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    schedule_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            "id",
            "name",
            "description",
            "exam_type",
            "exam_type_name",
            "academic_year",
            "academic_year_name",
            "start_date",
            "end_date",
            "status",
            "schedule_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_schedule_count(self, obj):
        return getattr(obj, "schedule_count", obj.schedules.count())


class ExamScheduleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    exam_name = serializers.CharField(source="exam.name", read_only=True)
    classroom_name = serializers.SerializerMethodField()

    class Meta:
        model = ExamSchedule
        fields = [
            "id",
            "exam",
            "exam_name",
            "subject",
            "subject_name",
            "classroom",
            "classroom_name",
            "date",
            "start_time",
            "end_time",
            "venue",
            "invigilator",
            "max_marks",
            "passing_marks",
        ]

    def get_classroom_name(self, obj):
        return str(obj.classroom)


class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    subject_name = serializers.CharField(source="exam_schedule.subject.name", read_only=True)
    exam_name = serializers.CharField(source="exam_schedule.exam.name", read_only=True)
    max_marks = serializers.DecimalField(
        source="exam_schedule.max_marks", max_digits=6, decimal_places=2, read_only=True
    )
    percentage = serializers.SerializerMethodField()
    is_pass = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = [
            "id",
            "student",
            "student_name",
            "exam_schedule",
            "subject_name",
            "exam_name",
            "marks_obtained",
            "max_marks",
            "percentage",
            "is_pass",
            "is_absent",
            "remarks",
            "graded_at",
        ]
        read_only_fields = ["id", "graded_by", "graded_at"]

    def get_percentage(self, obj):
        return float(obj.percentage) if obj.percentage is not None else None

    def get_is_pass(self, obj):
        return obj.is_pass


class BulkGradeSerializer(serializers.Serializer):
    exam_schedule_id = serializers.IntegerField()
    grades = serializers.ListField(child=serializers.DictField(), allow_empty=False)

    def validate_exam_schedule_id(self, value):
        # Tenant isolation: schedule must belong to the caller's school.
        school = self.context["request"].user.school
        try:
            return ExamSchedule.objects.get(id=value, exam__school=school)
        except ExamSchedule.DoesNotExist:
            raise serializers.ValidationError("Exam schedule not found in your school.")

    @transaction.atomic
    def save(self, graded_by=None):
        from .models import record_grade_change

        schedule = self.validated_data["exam_schedule_id"]
        created_grades = []
        for entry in self.validated_data["grades"]:
            marks = Decimal(str(marks)) if (marks := entry.get("marks_obtained")) is not None else None
            is_absent = entry.get("is_absent", False)
            remarks = entry.get("remarks", "")

            # Snapshot pre-mutation values for the audit trail.
            existing = Grade.objects.filter(student_id=entry["student_id"], exam_schedule=schedule).first()

            grade, created = Grade.objects.update_or_create(
                student_id=entry["student_id"],
                exam_schedule=schedule,
                defaults={
                    "marks_obtained": marks,
                    "is_absent": is_absent,
                    "remarks": remarks,
                    "graded_by": graded_by,
                },
            )
            record_grade_change(
                grade,
                "create" if created else "update",
                graded_by,
                old=existing if existing is not None else None,
            )
            created_grades.append(grade)
        return created_grades


class GradeChangeProposalSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    admission_number = serializers.CharField(source="student.admission_number", read_only=True)
    subject = serializers.CharField(source="exam_schedule.subject.name", read_only=True)
    exam = serializers.CharField(source="exam_schedule.exam.name", read_only=True)
    max_marks = serializers.DecimalField(
        source="exam_schedule.max_marks", max_digits=6, decimal_places=2, read_only=True
    )
    marks_obtained_current = serializers.SerializerMethodField()
    proposed_by = serializers.CharField(source="proposed_by.full_name", read_only=True)
    reviewed_by = serializers.CharField(source="reviewed_by.full_name", read_only=True)

    class Meta:
        model = GradeChangeProposal
        fields = [
            "id",
            "student",
            "student_name",
            "admission_number",
            "exam_schedule",
            "subject",
            "exam",
            "max_marks",
            "action",
            "status",
            "marks_obtained_new",
            "marks_obtained_current",
            "is_absent_new",
            "remarks_new",
            "reason",
            "proposed_by",
            "proposed_at",
            "reviewed_by",
            "reviewed_at",
            "review_notes",
        ]
        read_only_fields = fields

    def get_marks_obtained_current(self, obj):
        if obj.grade is not None and obj.grade.marks_obtained is not None:
            return float(obj.grade.marks_obtained)
        return None


class AssessmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    classroom_name = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            "id",
            "assignment",
            "subject_name",
            "classroom_name",
            "title",
            "assessment_type",
            "due_date",
            "max_marks",
            "description",
            "attachment",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    MAX_FILE_SIZE_MB = 10

    def validate_attachment(self, value):
        if value and value.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(f"File size must not exceed {self.MAX_FILE_SIZE_MB} MB.")
        if value:
            allowed_types = [
                "application/pdf",
                "image/jpeg",
                "image/png",
                "image/gif",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "text/plain",
            ]
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    f"File type '{value.content_type}' is not allowed. "
                    f"Allowed types: PDF, JPEG, PNG, GIF, DOC, DOCX, TXT."
                )
        return value

    def get_classroom_name(self, obj):
        return str(obj.assignment.classroom)


class AssessmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    assessment_title = serializers.CharField(source="assessment.title", read_only=True)
    percentage = serializers.SerializerMethodField()

    def validate(self, attrs):
        """
        Students may submit WITHOUT marks; only a teacher may set marks via
        update. This closes the self-grading hole where a student POSTed a
        submission with marks_obtained pre-filled (and the post_save signal
        then crashed on a missing attribute, 500-ing while persisting the marks).
        """
        request = self.context.get("request")
        if request is not None and request.method == "POST" and attrs.get("marks_obtained") is not None:
            raise serializers.ValidationError({"marks_obtained": "Marks can only be set by a teacher."})
        return attrs

    class Meta:
        model = AssessmentSubmission
        fields = [
            "id",
            "assessment",
            "assessment_title",
            "student",
            "student_name",
            "marks_obtained",
            "submitted_at",
            "file",
            "remarks",
            "is_late",
            "percentage",
        ]
        read_only_fields = ["id", "is_late"]

    def get_percentage(self, obj):
        if obj.marks_obtained is None:
            return None
        max_marks = obj.assessment.max_marks
        return float(obj.marks_obtained / max_marks * 100) if max_marks else 0


class ReportCardSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    student_admission_number = serializers.CharField(source="student.admission_number", read_only=True)
    exam_name = serializers.CharField(source="exam.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = ReportCard
        fields = [
            "id",
            "student",
            "student_name",
            "student_admission_number",
            "exam",
            "exam_name",
            "academic_year",
            "academic_year_name",
            "total_marks",
            "obtained_marks",
            "percentage",
            "grade_letter",
            "gpa",
            "rank_in_class",
            "rank_in_grade",
            "attendance_percentage",
            "teacher_remarks",
            "principal_remarks",
            "status",
            "pdf_url",
            "generated_at",
            "published_at",
        ]
        read_only_fields = [
            "id",
            "total_marks",
            "obtained_marks",
            "percentage",
            "grade_letter",
            "gpa",
            "rank_in_class",
            "rank_in_grade",
            "generated_at",
            "published_at",
        ]

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None


# =============================================================================
# Rubric-Based Grading Serializers
# =============================================================================


class RubricTemplateSerializer(serializers.ModelSerializer):
    criteria_count = serializers.SerializerMethodField()

    class Meta:
        model = RubricTemplate
        fields = [
            "id",
            "name",
            "description",
            "subject",
            "is_active",
            "created_at",
            "criteria_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_criteria_count(self, obj):
        return obj.criteria.count()


class RubricLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubricLevel
        fields = ["id", "criterion", "name", "description", "score", "order"]


class RubricCriterionSerializer(serializers.ModelSerializer):
    levels = RubricLevelSerializer(many=True, read_only=True)

    class Meta:
        model = RubricCriterion
        fields = ["id", "template", "name", "description", "max_score", "order", "levels"]
        read_only_fields = ["id"]


class RubricScoreSerializer(serializers.ModelSerializer):
    criterion_name = serializers.CharField(source="criterion.name", read_only=True)

    class Meta:
        model = RubricScore
        fields = ["id", "rubric_assessment", "criterion", "criterion_name", "selected_level", "score", "feedback"]


class RubricAssessmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    scores = RubricScoreSerializer(many=True, read_only=True)

    class Meta:
        model = RubricAssessment
        fields = [
            "id",
            "assessment",
            "student",
            "student_name",
            "rubric_template",
            "total_score",
            "graded_at",
            "notes",
            "scores",
        ]
        read_only_fields = ["id", "total_score", "graded_at"]


# =============================================================================
# Standards-Based Grading Serializers
# =============================================================================


class StandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Standard
        fields = ["id", "code", "name", "description", "standard_type", "subject", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class StandardMasteryScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StandardMasteryScale
        fields = ["id", "name", "levels", "is_default"]


class StudentStandardGradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    standard_code = serializers.CharField(source="standard.code", read_only=True)
    standard_name = serializers.CharField(source="standard.name", read_only=True)

    class Meta:
        model = StudentStandardGrade
        fields = [
            "id",
            "student",
            "student_name",
            "standard",
            "standard_code",
            "standard_name",
            "mastery_level",
            "score",
            "evidence",
            "graded_at",
        ]
        read_only_fields = ["id", "graded_at"]


# =============================================================================
# Grading Categories Serializers
# =============================================================================


class GradingCategorySerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    assignments_count = serializers.SerializerMethodField()

    class Meta:
        model = GradingCategory
        fields = [
            "id",
            "name",
            "weight",
            "subject",
            "subject_name",
            "academic_year",
            "drop_lowest",
            "is_active",
            "assignments_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_assignments_count(self, obj):
        return obj.assignments.count()


class CategoryAssignmentSerializer(serializers.ModelSerializer):
    assessment_title = serializers.CharField(source="assessment.title", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = CategoryAssignment
        fields = ["id", "assessment", "assessment_title", "category", "category_name"]


# =============================================================================
# GPA Calculation Serializers
# =============================================================================


class CourseGradeCalculationSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = CourseGradeCalculation
        fields = [
            "id",
            "gpa_calculation",
            "subject",
            "subject_name",
            "marks_obtained",
            "max_marks",
            "percentage",
            "grade_letter",
            "grade_points",
            "credits",
            "is_honors",
            "is_pass_fail",
        ]


class GPACalculationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    course_grades = CourseGradeCalculationSerializer(many=True, read_only=True)
    percentile_rank = serializers.SerializerMethodField()

    class Meta:
        model = GPACalculation
        fields = [
            "id",
            "student",
            "student_name",
            "academic_year",
            "semester",
            "gpa_type",
            "gpa_value",
            "total_grade_points",
            "total_credits",
            "class_rank",
            "class_size",
            "percentile_rank",
            "calculated_at",
            "course_grades",
        ]
        read_only_fields = ["id", "calculated_at"]

    def get_percentile_rank(self, obj):
        return obj.percentile_rank


# =============================================================================
# Transcript Serializers
# =============================================================================


class TranscriptEntrySerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = TranscriptEntry
        fields = [
            "id",
            "transcript",
            "subject",
            "subject_name",
            "academic_year",
            "semester",
            "marks_obtained",
            "max_marks",
            "percentage",
            "grade_letter",
            "grade_points",
            "credits",
            "is_honors",
            "is_repeated",
        ]


class TranscriptSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    entries = TranscriptEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Transcript
        fields = [
            "id",
            "student",
            "student_name",
            "academic_year",
            "transcript_number",
            "status",
            "cumulative_gpa",
            "class_rank",
            "class_size",
            "total_credits_earned",
            "graduation_date",
            "notes",
            "issued_at",
            "entries",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# =============================================================================
# Grade Notification Serializers
# =============================================================================


class GradeNotificationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True, default=None)

    class Meta:
        model = GradeNotification
        fields = [
            "id",
            "student",
            "student_name",
            "notification_type",
            "channel",
            "title",
            "message",
            "subject",
            "subject_name",
            "grade_value",
            "previous_grade",
            "status",
            "sent_at",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Grade History Serializers
# =============================================================================


class GradeHistorySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)

    class Meta:
        model = GradeHistory
        fields = [
            "id",
            "student",
            "student_name",
            "subject",
            "subject_name",
            "academic_year",
            "semester",
            "final_marks",
            "max_marks",
            "percentage",
            "grade_letter",
            "grade_points",
            "is_pass",
            "teacher_name",
            "notes",
            "recorded_at",
        ]


# =============================================================================
# Late Penalty Rule Serializers
# =============================================================================


class LatePenaltyRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatePenaltyRule
        fields = [
            "id",
            "name",
            "penalty_type",
            "penalty_value",
            "max_penalty",
            "grace_period_hours",
            "subject",
            "academic_year",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Extra Credit Serializers
# =============================================================================


class ExtraCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraCredit
        fields = [
            "id",
            "assessment",
            "credit_type",
            "title",
            "description",
            "max_bonus_marks",
            "due_date",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ExtraCreditSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)

    class Meta:
        model = ExtraCreditSubmission
        fields = [
            "id",
            "extra_credit",
            "student",
            "student_name",
            "bonus_marks_obtained",
            "submitted_at",
            "remarks",
            "graded_at",
        ]
        read_only_fields = ["id", "submitted_at", "graded_at"]


# =============================================================================
# Grade Comment Serializers
# =============================================================================


class GradeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeComment
        fields = ["id", "category", "comment_text", "grade_range_min", "grade_range_max", "is_active", "usage_count"]
        read_only_fields = ["id", "usage_count"]


class ReportCardCommentSerializer(serializers.ModelSerializer):
    comment_text = serializers.CharField(source="comment.comment_text", read_only=True)

    class Meta:
        model = ReportCardComment
        fields = ["id", "report_card", "comment", "comment_text", "custom_text", "added_at"]
        read_only_fields = ["id", "added_at"]


class ExamTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamType
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class GradeChangeLogSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(source="changed_by.full_name", read_only=True)

    class Meta:
        model = GradeChangeLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
