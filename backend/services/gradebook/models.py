"""
Gradebook Service — Exams, assessments, grades, report cards
"""

import uuid
from decimal import Decimal

from django.db import models
from services.academics.models import Subject, TeacherAssignment
from services.auth.models import School, User
from services.students.models import AcademicYear, Classroom, Student


class GradingScale(models.Model):
    """Configurable grading scale per school."""

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="grading_scales")
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "grading_scales"

    def __str__(self):
        return self.name


class GradingScaleEntry(models.Model):
    scale = models.ForeignKey(GradingScale, on_delete=models.CASCADE, related_name="entries")
    grade_letter = models.CharField(max_length=5)  # A+, A, B, etc.
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_point = models.DecimalField(max_digits=3, decimal_places=1)  # GPA points
    description = models.CharField(max_length=50)  # Excellent, Good, etc.

    class Meta:
        db_table = "grading_scale_entries"
        ordering = ["-min_percentage"]

    def __str__(self):
        return f"{self.scale} — {self.grade_letter} ({self.grade_point} pts)"


class ExamType(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="exam_types")
    name = models.CharField(max_length=100)  # Midterm, Final, Quiz, Assignment
    weightage = models.DecimalField(max_digits=5, decimal_places=2)  # % of total
    is_terminal = models.BooleanField(default=False)

    class Meta:
        db_table = "exam_types"

    def __str__(self):
        return self.name


class Exam(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="exams")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "exams"

    def __str__(self):
        return f"{self.name} ({self.status})"


class ExamSchedule(models.Model):
    """Date/time for a specific subject exam."""

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="schedules")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100, blank=True)
    invigilator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="invigilated_exams")
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    passing_marks = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = "exam_schedules"
        unique_together = [("exam", "subject", "classroom")]

    def __str__(self):
        return f"{self.exam} — {self.subject} @ {self.classroom}"


class Grade(models.Model):
    """Individual student grade for a specific exam-subject."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grades")
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="grades")
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_absent = models.BooleanField(default=False)
    remarks = models.CharField(max_length=255, blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exam_grades"
        unique_together = [("student", "exam_schedule")]

    @property
    def percentage(self):
        if self.marks_obtained is None or self.is_absent:
            return None
        max_marks = self.exam_schedule.max_marks
        if max_marks == 0:
            return Decimal("0")
        return (self.marks_obtained / max_marks) * 100

    @property
    def is_pass(self):
        if self.marks_obtained is None or self.is_absent:
            return False
        return self.marks_obtained >= self.exam_schedule.passing_marks

    def __str__(self):
        return f"{self.student} — {self.exam_schedule.subject} [{self.marks_obtained}]"


class GradeChangeLog(models.Model):
    """
    Immutable audit trail for every grade create/update/delete.
    Records who changed what and when — supports forensic review
    of grade tampering and compliance expectations (FERPA-adjacent).
    """

    class Action(models.TextChoices):
        CREATE = "create", "Created"
        UPDATE = "update", "Updated"
        DELETE = "delete", "Deleted"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grade_change_logs")
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="grade_change_logs")
    action = models.CharField(max_length=10, choices=Action.choices)
    marks_obtained_old = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    marks_obtained_new = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_absent_old = models.BooleanField(null=True)
    is_absent_new = models.BooleanField(null=True)
    remarks_old = models.CharField(max_length=255, blank=True)
    remarks_new = models.CharField(max_length=255, blank=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="grade_change_logs")
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "grade_change_logs"
        ordering = ["-changed_at"]
        indexes = [
            models.Index(fields=["student", "exam_schedule"]),
            models.Index(fields=["changed_by"]),
        ]

    def __str__(self):
        return f"{self.get_action_display()} {self.student} [{self.exam_schedule.subject}] by {self.changed_by}"


class GradeChangeProposal(models.Model):
    """
    Pending grade change awaiting admin approval.

    When a grade for a *published* exam (student report card status in
    published/sent) is edited, the change is not applied directly — a
    proposal is created instead. An admin approves it (the change is then
    applied and written to the immutable GradeChangeLog) or rejects it.
    """

    class Status(models.TextChoices):
        PROPOSED = "proposed", "Proposed"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class Action(models.TextChoices):
        CREATE = "create", "Created"
        UPDATE = "update", "Updated"
        DELETE = "delete", "Deleted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grade_change_proposals")
    exam_schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name="grade_change_proposals")
    # The target grade. None for create proposals (the grade doesn't exist yet).
    # SET_NULL: when an approved delete removes the grade, the proposal row
    # survives so the review decision stays on record.
    grade = models.ForeignKey(
        Grade, on_delete=models.SET_NULL, null=True, blank=True, related_name="grade_change_proposals"
    )
    action = models.CharField(max_length=10, choices=Action.choices)
    marks_obtained_new = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_absent_new = models.BooleanField(null=True)
    remarks_new = models.CharField(max_length=255, blank=True)
    reason = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PROPOSED)
    proposed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="grade_change_proposals")
    proposed_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="reviewed_grade_change_proposals"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = "grade_change_proposals"
        ordering = ["-proposed_at"]
        indexes = [
            models.Index(fields=["student", "exam_schedule"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return (
            f"{self.get_action_display()} {self.student} [{self.exam_schedule.subject}] — {self.get_status_display()}"
        )


def grade_change_requires_approval(student, exam_schedule):
    """
    A grade change needs admin approval when the student's report card
    for that exam has been published (or sent to parents).
    """
    return ReportCard.objects.filter(
        exam=exam_schedule.exam,
        student=student,
        status__in=[ReportCard.Status.PUBLISHED, ReportCard.Status.SENT],
    ).exists()


def create_grade_change_proposal(
    student,
    exam_schedule,
    action,
    grade=None,
    new_values=None,
    proposed_by=None,
    reason="",
):
    """
    Create a proposal for a grade change on a published exam.
    Supersedes any still-pending proposal for the same (student, schedule)
    so there is never more than one live proposal per grade.
    """
    from django.utils import timezone

    values = new_values or {}
    GradeChangeProposal.objects.filter(
        student=student, exam_schedule=exam_schedule, status=GradeChangeProposal.Status.PROPOSED
    ).update(
        status=GradeChangeProposal.Status.REJECTED,
        reviewed_by=proposed_by,
        reviewed_at=timezone.now(),
        review_notes="Superseded by a newer proposal",
    )
    return GradeChangeProposal.objects.create(
        student=student,
        exam_schedule=exam_schedule,
        grade=grade,
        action=action,
        marks_obtained_new=values.get("marks_obtained"),
        is_absent_new=values.get("is_absent"),
        remarks_new=values.get("remarks", "") or "",
        reason=reason,
        proposed_by=proposed_by,
    )


def record_grade_change(grade, action, changed_by, old=None):
    """
    Append an immutable audit entry for a grade mutation.

    ``old`` is an optional snapshot of the pre-mutation values
    (a model instance or object with marks_obtained/is_absent/remarks).
    For deletes, the ``new`` fields record None — the value was removed,
    not changed to itself. Safe on all paths; never raises.
    """
    changed_by_id = grade.graded_by_id if changed_by is None else getattr(changed_by, "id", changed_by)

    old_marks = old.marks_obtained if old is not None else None
    old_absent = old.is_absent if old is not None else None
    old_remarks = old.remarks if old is not None else ""

    is_delete = action == "delete"
    GradeChangeLog.objects.create(
        student=grade.student,
        exam_schedule=grade.exam_schedule,
        action=action,
        marks_obtained_old=old_marks,
        marks_obtained_new=None if is_delete else grade.marks_obtained,
        is_absent_old=old_absent,
        is_absent_new=None if is_delete else grade.is_absent,
        remarks_old=old_remarks or "",
        remarks_new="" if is_delete else grade.remarks or "",
        changed_by_id=changed_by_id,
    )


class Assessment(models.Model):
    """Continuous assessment — homework, quizzes, projects."""

    class AssessmentType(models.TextChoices):
        HOMEWORK = "homework", "Homework"
        QUIZ = "quiz", "Quiz"
        PROJECT = "project", "Project"
        CLASSWORK = "classwork", "Class Work"
        LAB = "lab", "Lab Work"

    assignment = models.ForeignKey(TeacherAssignment, on_delete=models.CASCADE, related_name="assessments")
    title = models.CharField(max_length=255)
    assessment_type = models.CharField(max_length=20, choices=AssessmentType.choices)
    due_date = models.DateField()
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    attachment = models.FileField(upload_to="assessments/", null=True, blank=True)  # noqa: DJ01 — null for legacy rows
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "assessments"

    def __str__(self):
        return f"{self.title} ({self.get_assessment_type_display()})"


class AssessmentSubmission(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="assessment_submissions")
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    file = models.FileField(upload_to="submissions/", null=True, blank=True)  # noqa: DJ01 — null for legacy rows
    remarks = models.TextField(blank=True)
    is_late = models.BooleanField(default=False)

    class Meta:
        db_table = "assessment_submissions"
        unique_together = [("assessment", "student")]

    def __str__(self):
        return f"{self.student} — {self.assessment.title} [{self.marks_obtained}]"


class ReportCard(models.Model):
    """Generated report card per student per exam."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        SENT = "sent", "Sent to Parents"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="report_cards")
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="report_cards")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    obtained_marks = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade_letter = models.CharField(max_length=5, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    rank_in_class = models.PositiveSmallIntegerField(null=True, blank=True)
    rank_in_grade = models.PositiveSmallIntegerField(null=True, blank=True)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    teacher_remarks = models.TextField(blank=True)
    principal_remarks = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    pdf_file = models.FileField(  # noqa: DJ01 — null for legacy rows
        upload_to="report_cards/%Y/%m/", null=True, blank=True
    )
    generated_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "report_cards"
        unique_together = [("student", "exam")]

    def __str__(self):
        return f"{self.student} — {self.exam.name} ({self.get_status_display()})"


# =============================================================================
# NEW MODELS: Rubric-Based Grading
# =============================================================================


class RubricTemplate(models.Model):
    """Template for rubric-based grading with criteria and levels."""

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="rubric_templates")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rubric_templates"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} — {self.school}"


class RubricCriterion(models.Model):
    """Individual criterion within a rubric template."""

    template = models.ForeignKey(RubricTemplate, on_delete=models.CASCADE, related_name="criteria")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=4)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "rubric_criteria"
        ordering = ["order"]

    def __str__(self):
        return f"{self.template.name} — {self.name}"


class RubricLevel(models.Model):
    """Performance level for a rubric criterion."""

    criterion = models.ForeignKey(RubricCriterion, on_delete=models.CASCADE, related_name="levels")
    name = models.CharField(max_length=100)  # e.g., Exemplary, Proficient, Developing, Beginning
    description = models.TextField(blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "rubric_levels"
        ordering = ["order"]

    def __str__(self):
        return f"{self.criterion.name} — {self.name} ({self.score} pts)"


class RubricAssessment(models.Model):
    """Student's rubric assessment for a specific assignment."""

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="rubric_assessments")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="rubric_assessments")
    rubric_template = models.ForeignKey(RubricTemplate, on_delete=models.CASCADE)
    total_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    graded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "rubric_assessments"
        unique_together = [("assessment", "student")]

    def __str__(self):
        return f"{self.student} — {self.assessment.title} ({self.total_score} pts)"


class RubricScore(models.Model):
    """Individual criterion score within a rubric assessment."""

    rubric_assessment = models.ForeignKey(RubricAssessment, on_delete=models.CASCADE, related_name="scores")
    criterion = models.ForeignKey(RubricCriterion, on_delete=models.CASCADE)
    selected_level = models.ForeignKey(RubricLevel, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2)
    feedback = models.TextField(blank=True)

    class Meta:
        db_table = "rubric_scores"
        unique_together = [("rubric_assessment", "criterion")]

    def __str__(self):
        return f"{self.criterion.name}: {self.score} pts"


# =============================================================================
# NEW MODELS: Standards-Based Grading
# =============================================================================


class Standard(models.Model):
    """Academic standard for standards-based grading."""

    class StandardType(models.TextChoices):
        COURSE = "course", "Course Standard"
        GRADE_LEVEL = "grade_level", "Grade Level Standard"
        DISTRICT = "district", "District Standard"
        STATE = "state", "State Standard"

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="standards")
    code = models.CharField(max_length=50)  # e.g., CCSS.MATH.6.EE.1
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    standard_type = models.CharField(max_length=15, choices=StandardType.choices, default=StandardType.COURSE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="standards")
    grade_level = models.ForeignKey("students.Grade", on_delete=models.SET_NULL, null=True, blank=True)
    parent_standard = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="sub_standards"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "standards"
        ordering = ["code"]
        unique_together = [("school", "code")]

    def __str__(self):
        return f"{self.code} — {self.name}"


class StandardMasteryScale(models.Model):
    """Mastery levels for standards-based grading."""

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="mastery_scales")
    name = models.CharField(max_length=100)
    levels = models.JSONField(default=list, help_text="List of mastery levels with scores")
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "standard_mastery_scales"

    def __str__(self):
        return f"{self.name} — {self.school}"


class StudentStandardGrade(models.Model):
    """Student's grade for a specific standard."""

    class MasteryLevel(models.TextChoices):
        EXCEEDING = "exceeding", "Exceeding Mastery"
        MEETING = "meeting", "Meeting Mastery"
        APPROACHING = "approaching", "Approaching Mastery"
        BEGINNING = "beginning", "Beginning"
        NOT_YET = "not_yet", "Not Yet Meeting"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="standard_grades")
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name="student_grades")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    mastery_level = models.CharField(max_length=15, choices=MasteryLevel.choices)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    evidence = models.TextField(blank=True, help_text="Evidence supporting this grade")
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    graded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_standard_grades"
        unique_together = [("student", "standard", "academic_year")]

    def __str__(self):
        return f"{self.student} — {self.standard.code}: {self.get_mastery_level_display()}"


# =============================================================================
# NEW MODELS: Grading Categories (Weighted)
# =============================================================================


class GradingCategory(models.Model):
    """Weighted grading category for assignments."""

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="grading_categories")
    name = models.CharField(max_length=100)  # e.g., Homework, Quizzes, Exams
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage weight (0-100)")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="grading_categories")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    drop_lowest = models.PositiveIntegerField(default=0, help_text="Number of lowest scores to drop")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "grading_categories"
        ordering = ["-weight"]
        unique_together = [("name", "subject", "academic_year")]

    def __str__(self):
        return f"{self.name} ({self.weight}%) — {self.subject}"


class CategoryAssignment(models.Model):
    """Link an assessment to a weighted category."""

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="category_links")
    category = models.ForeignKey(GradingCategory, on_delete=models.CASCADE, related_name="assignments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "category_assignments"
        unique_together = [("assessment", "category")]

    def __str__(self):
        return f"{self.assessment.title} → {self.category.name}"


# =============================================================================
# NEW MODELS: GPA Calculation Engine
# =============================================================================


class GPACalculation(models.Model):
    """Cumulative GPA calculation for a student."""

    class GPAType(models.TextChoices):
        SEMESTER = "semester", "Semester GPA"
        CUMULATIVE = "cumulative", "Cumulative GPA"
        WEIGHTED = "weighted", "Weighted GPA"
        UNWEIGHTED = "unweighted", "Unweighted GPA"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="gpa_calculations")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20, blank=True, help_text="e.g., Fall 2025, Spring 2026")
    gpa_type = models.CharField(max_length=15, choices=GPAType.choices, default=GPAType.CUMULATIVE)
    gpa_value = models.DecimalField(max_digits=4, decimal_places=3)
    total_grade_points = models.DecimalField(max_digits=8, decimal_places=2)
    total_credits = models.DecimalField(max_digits=6, decimal_places=2)
    class_rank = models.PositiveIntegerField(null=True, blank=True)
    class_size = models.PositiveIntegerField(null=True, blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "gpa_calculations"
        ordering = ["-academic_year", "-semester"]
        unique_together = [("student", "academic_year", "semester", "gpa_type")]

    def __str__(self):
        return f"{self.student} — {self.get_gpa_type_display()}: {self.gpa_value}"

    @property
    def percentile_rank(self):
        """Calculate percentile rank based on class standing."""
        if self.class_rank and self.class_size and self.class_size > 0:
            return round(((self.class_size - self.class_rank) / self.class_size) * 100, 1)
        return None


class CourseGradeCalculation(models.Model):
    """Individual course grade used in GPA calculation."""

    gpa_calculation = models.ForeignKey(GPACalculation, on_delete=models.CASCADE, related_name="course_grades")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_letter = models.CharField(max_length=5)
    grade_points = models.DecimalField(max_digits=3, decimal_places=2)
    credits = models.DecimalField(max_digits=4, decimal_places=2, default=1)
    is_honors = models.BooleanField(default=False, help_text="Honors/AP course")
    is_pass_fail = models.BooleanField(default=False)

    class Meta:
        db_table = "course_grade_calculations"

    def __str__(self):
        return f"{self.subject}: {self.grade_letter} ({self.grade_points} pts)"


# =============================================================================
# NEW MODELS: Transcript Generation
# =============================================================================


class Transcript(models.Model):
    """Official academic transcript."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        FINAL = "final", "Final"
        REQUESTED = "requested", "Requested"
        SENT = "sent", "Sent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="gradebook_transcripts")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    transcript_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    cumulative_gpa = models.DecimalField(max_digits=4, decimal_places=3)
    class_rank = models.PositiveIntegerField(null=True, blank=True)
    class_size = models.PositiveIntegerField(null=True, blank=True)
    total_credits_earned = models.DecimalField(max_digits=6, decimal_places=2)
    graduation_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="issued_transcripts")
    issued_at = models.DateTimeField(null=True, blank=True)
    pdf_file = models.FileField(upload_to="transcripts/%Y/%m/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "transcripts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Transcript {self.transcript_number} — {self.student}"


class TranscriptEntry(models.Model):
    """Individual course entry on a transcript."""

    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE, related_name="entries")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20, blank=True)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_letter = models.CharField(max_length=5)
    grade_points = models.DecimalField(max_digits=3, decimal_places=2)
    credits = models.DecimalField(max_digits=4, decimal_places=2, default=1)
    is_honors = models.BooleanField(default=False)
    is_repeated = models.BooleanField(default=False)

    class Meta:
        db_table = "transcript_entries"
        ordering = ["academic_year", "semester", "subject"]

    def __str__(self):
        return f"{self.subject}: {self.grade_letter} ({self.grade_points} pts)"


# =============================================================================
# NEW MODELS: Grade Notifications
# =============================================================================


class GradeNotification(models.Model):
    """Notifications for grade changes to parents/students."""

    class NotificationType(models.TextChoices):
        GRADE_POSTED = "grade_posted", "Grade Posted"
        GRADE_CHANGED = "grade_changed", "Grade Changed"
        MISSING_ASSIGNMENT = "missing_assignment", "Missing Assignment"
        GRADE_WARNING = "grade_warning", "Grade Warning"
        REPORT_CARD = "report_card", "Report Card Available"
        TRANSCRIPT = "transcript", "Transcript Ready"

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push Notification"
        IN_APP = "in_app", "In-App"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="grade_notifications")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grade_notifications")
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.EMAIL)
    title = models.CharField(max_length=200)
    message = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    grade_value = models.CharField(max_length=20, blank=True)
    previous_grade = models.CharField(max_length=20, blank=True)
    recipient_email = models.EmailField(blank=True)
    recipient_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=15, default="pending")
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "grade_notifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} — {self.get_notification_type_display()}"


# =============================================================================
# NEW MODELS: Grade History
# =============================================================================


class GradeHistory(models.Model):
    """Historical grade records for a student."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grade_history")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20, blank=True)
    final_marks = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    grade_letter = models.CharField(max_length=5)
    grade_points = models.DecimalField(max_digits=3, decimal_places=2)
    is_pass = models.BooleanField(default=True)
    teacher_name = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "grade_history"
        unique_together = [("student", "subject", "academic_year", "semester")]
        ordering = ["-academic_year", "-semester"]

    def __str__(self):
        return f"{self.student} — {self.subject}: {self.grade_letter} ({self.academic_year})"


# =============================================================================
# NEW MODELS: Late Penalty Rules
# =============================================================================


class LatePenaltyRule(models.Model):
    """Rules for auto-deducting marks for late submissions."""

    class PenaltyType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage Deduction"
        FIXED = "fixed", "Fixed Points Deduction"
        PER_DAY = "per_day", "Per Day Deduction"
        STEPWISE = "stepwise", "Stepwise Deduction"

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="late_penalty_rules")
    name = models.CharField(max_length=100)
    penalty_type = models.CharField(max_length=15, choices=PenaltyType.choices)
    penalty_value = models.DecimalField(max_digits=6, decimal_places=2, help_text="Points or percentage")
    max_penalty = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, help_text="Maximum deduction"
    )
    grace_period_hours = models.PositiveIntegerField(default=0, help_text="Hours before penalty applies")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "late_penalty_rules"

    def __str__(self):
        return f"{self.name} ({self.get_penalty_type_display()})"

    def calculate_penalty(self, hours_late, original_marks):
        """Calculate penalty based on hours late and original marks."""
        if hours_late <= self.grace_period_hours:
            return Decimal("0")

        effective_hours = hours_late - self.grace_period_hours

        if self.penalty_type == self.PenaltyType.PERCENTAGE:
            penalty = original_marks * (self.penalty_value / 100)
        elif self.penalty_type == self.PenaltyType.FIXED:
            penalty = self.penalty_value
        elif self.penalty_type == self.PenaltyType.PER_DAY:
            days_late = max(1, effective_hours // 24)
            penalty = self.penalty_value * days_late
        else:  # STEPWISE
            penalty = self.penalty_value * max(1, effective_hours // 24)

        if self.max_penalty and penalty > self.max_penalty:
            penalty = self.max_penalty

        return min(penalty, original_marks)


# =============================================================================
# NEW MODELS: Extra Credit
# =============================================================================


class ExtraCredit(models.Model):
    """Extra credit assignments and bonus points."""

    class CreditType(models.TextChoices):
        ASSIGNMENT = "assignment", "Extra Credit Assignment"
        BONUS_POINTS = "bonus_points", "Bonus Points"
        PARTICIPATION = "participation", "Participation Bonus"

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name="extra_credit_options")
    credit_type = models.CharField(max_length=15, choices=CreditType.choices, default=CreditType.ASSIGNMENT)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    max_bonus_marks = models.DecimalField(max_digits=6, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    attachment = models.FileField(upload_to="extra_credit/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "extra_credit"

    def __str__(self):
        return f"{self.title} (+{self.max_bonus_marks} pts)"


class ExtraCreditSubmission(models.Model):
    """Student submission for extra credit."""

    extra_credit = models.ForeignKey(ExtraCredit, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="extra_credit_submissions")
    bonus_marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="extra_credit_submissions/", null=True, blank=True)
    remarks = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "extra_credit_submissions"
        unique_together = [("extra_credit", "student")]

    def __str__(self):
        return f"{self.student} — {self.extra_credit.title}: +{self.bonus_marks_obtained} pts"


# =============================================================================
# NEW MODELS: Grade Comments
# =============================================================================


class GradeComment(models.Model):
    """Pre-defined comments for report cards."""

    class CommentCategory(models.TextChoices):
        ACADEMIC = "academic", "Academic Performance"
        BEHAVIOR = "behavior", "Behavior"
        ATTENDANCE = "attendance", "Attendance"
        WORK_HABITS = "work_habits", "Work Habits"
        SOCIAL = "social", "Social Skills"
        GENERAL = "general", "General"

    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="grade_comments")
    category = models.CharField(max_length=15, choices=CommentCategory.choices)
    comment_text = models.TextField()
    grade_range_min = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Min percentage for this comment"
    )
    grade_range_max = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Max percentage for this comment"
    )
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "grade_comments"
        ordering = ["category", "comment_text"]

    def __str__(self):
        return f"{self.get_category_display()}: {self.comment_text[:50]}..."


class ReportCardComment(models.Model):
    """Selected comments for a specific report card."""

    report_card = models.ForeignKey(ReportCard, on_delete=models.CASCADE, related_name="selected_comments")
    comment = models.ForeignKey(GradeComment, on_delete=models.CASCADE)
    custom_text = models.TextField(blank=True, help_text="Customized version of the comment")
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "report_card_comments"
        unique_together = [("report_card", "comment")]

    def __str__(self):
        return f"Report Card {self.report_card.id} — {self.comment.comment_text[:30]}"
