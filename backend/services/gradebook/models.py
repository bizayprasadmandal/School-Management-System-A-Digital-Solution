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
