"""
Gradebook Service — Serializers
"""

from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import (
    Exam, ExamSchedule, Grade, Assessment,
    AssessmentSubmission, ReportCard,
)


class ExamSerializer(serializers.ModelSerializer):
    exam_type_name = serializers.CharField(source="exam_type.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    schedule_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            "id", "name", "description", "exam_type", "exam_type_name",
            "academic_year", "academic_year_name", "start_date", "end_date",
            "status", "schedule_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_schedule_count(self, obj):
        return obj.schedules.count()


class ExamScheduleSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    exam_name = serializers.CharField(source="exam.name", read_only=True)
    classroom_name = serializers.SerializerMethodField()

    class Meta:
        model = ExamSchedule
        fields = [
            "id", "exam", "exam_name", "subject", "subject_name",
            "classroom", "classroom_name", "date", "start_time", "end_time",
            "venue", "invigilator", "max_marks", "passing_marks",
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
            "id", "student", "student_name", "exam_schedule",
            "subject_name", "exam_name", "marks_obtained", "max_marks",
            "percentage", "is_pass", "is_absent", "remarks", "graded_at",
        ]
        read_only_fields = ["id", "graded_by", "graded_at"]

    def get_percentage(self, obj):
        return float(obj.percentage) if obj.percentage is not None else None

    def get_is_pass(self, obj):
        return obj.is_pass


class BulkGradeSerializer(serializers.Serializer):
    exam_schedule_id = serializers.IntegerField()
    grades = serializers.ListField(
        child=serializers.DictField(), allow_empty=False
    )

    def validate_exam_schedule_id(self, value):
        try:
            return ExamSchedule.objects.get(id=value)
        except ExamSchedule.DoesNotExist:
            raise serializers.ValidationError("Exam schedule not found.")

    @transaction.atomic
    def save(self, graded_by=None):
        schedule = self.validated_data["exam_schedule_id"]
        created_grades = []
        for entry in self.validated_data["grades"]:
            marks = entry.get("marks_obtained")
            grade, _ = Grade.objects.update_or_create(
                student_id=entry["student_id"],
                exam_schedule=schedule,
                defaults={
                    "marks_obtained": Decimal(str(marks)) if marks is not None else None,
                    "is_absent": entry.get("is_absent", False),
                    "remarks": entry.get("remarks", ""),
                    "graded_by": graded_by,
                },
            )
            created_grades.append(grade)
        return created_grades


class AssessmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="assignment.subject.name", read_only=True)
    classroom_name = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = [
            "id", "assignment", "subject_name", "classroom_name",
            "title", "assessment_type", "due_date", "max_marks",
            "description", "attachment", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    MAX_FILE_SIZE_MB = 10

    def validate_attachment(self, value):
        if value and value.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f"File size must not exceed {self.MAX_FILE_SIZE_MB} MB."
            )
        if value:
            allowed_types = [
                "application/pdf",
                "image/jpeg", "image/png", "image/gif",
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

    class Meta:
        model = AssessmentSubmission
        fields = [
            "id", "assessment", "assessment_title", "student", "student_name",
            "marks_obtained", "submitted_at", "file", "remarks", "is_late",
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
            "id", "student", "student_name", "student_admission_number",
            "exam", "exam_name", "academic_year", "academic_year_name",
            "total_marks", "obtained_marks", "percentage", "grade_letter",
            "gpa", "rank_in_class", "rank_in_grade", "attendance_percentage",
            "teacher_remarks", "principal_remarks", "status",
            "pdf_url", "generated_at", "published_at",
        ]
        read_only_fields = [
            "id", "total_marks", "obtained_marks", "percentage", "grade_letter",
            "gpa", "rank_in_class", "rank_in_grade", "generated_at", "published_at",
        ]

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None
