"""
Academics Service — Subjects, curriculum, teacher assignments, student-subject enrollment,
curriculum standards mapping, syllabus management, teacher workload, teacher evaluation,
academic transcripts.
"""

import uuid

from django.db import models
from services.auth.models import School, User
from services.students.models import AcademicYear, Classroom, Grade, Student


class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="subjects")
    is_core = models.BooleanField(default=True)
    is_elective = models.BooleanField(default=False)
    max_marks = models.PositiveSmallIntegerField(default=100)
    pass_marks = models.PositiveSmallIntegerField(default=35)
    credit_hours = models.DecimalField(max_digits=4, decimal_places=1, default=1.0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "subjects"
        unique_together = [("school", "code", "grade")]

    def __str__(self):
        return f"{self.name} ({self.code}) — Grade {self.grade.name}"


class TeacherAssignment(models.Model):
    """Maps a teacher to a subject-classroom combination."""

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignments")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="assignments")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="assignments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=True)

    class Meta:
        db_table = "teacher_assignments"
        unique_together = [("teacher", "subject", "classroom", "academic_year")]

    def __str__(self):
        return f"{self.teacher.full_name} → {self.subject.name} @ {self.classroom}"


class TeacherProfile(models.Model):
    """Extended teacher information."""

    class QualificationLevel(models.TextChoices):
        DIPLOMA = "diploma", "Diploma"
        BACHELOR = "bachelor", "Bachelor's Degree"
        MASTER = "master", "Master's Degree"
        PHD = "phd", "PhD"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="teachers")
    employee_id = models.CharField(max_length=30, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female"), ("O", "Other")])
    qualification = models.CharField(max_length=20, choices=QualificationLevel.choices)
    specialization = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField()
    experience_years = models.PositiveSmallIntegerField(default=0)
    department = models.CharField(max_length=100, blank=True)
    salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    address = models.TextField()
    bio = models.TextField(blank=True, help_text="Professional bio / biography")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "teacher_profiles"

    def __str__(self):
        return f"{self.user.full_name} ({self.employee_id})"


class LessonPlan(models.Model):
    assignment = models.ForeignKey(TeacherAssignment, on_delete=models.CASCADE, related_name="lesson_plans")
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    objectives = models.TextField()
    content = models.TextField()
    resources = models.TextField(blank=True)
    date = models.DateField()
    duration_minutes = models.PositiveSmallIntegerField(default=45)
    status = models.CharField(
        max_length=20,
        choices=[("draft", "Draft"), ("approved", "Approved"), ("completed", "Completed")],
        default="draft",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lesson_plans"

    def __str__(self):
        return f"{self.title} — {self.date}"


class StudentSubjectEnrollment(models.Model):
    """Tracks which students are enrolled in which subjects per academic year.

    This is independent of classroom enrollment — a student may take subjects
    from different streams or have elective choices that differ from their
    classroom peers.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        DROPPED = "dropped", "Dropped"
        TRANSFERRED = "transferred", "Transferred"
        COMPLETED = "completed", "Completed"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="subject_enrollments")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="student_enrollments")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="subject_enrollments")
    enrolled_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_subject_enrollments"
        unique_together = [("student", "subject", "academic_year")]
        indexes = [
            models.Index(fields=["student", "academic_year"]),
            models.Index(fields=["subject", "academic_year"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["-enrolled_date"]

    def __str__(self):
        return f"{self.student} → {self.subject} ({self.academic_year})"

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE


class CurriculumStandard(models.Model):
    """A curriculum standard (e.g., Common Core, NGSS, CBSE, NCERT).

    Schools import or define the standards framework they follow,
    then map individual standards to subjects for tracking and
    accreditation reporting.
    """

    class Framework(models.TextChoices):
        COMMON_CORE = "common_core", "Common Core State Standards"
        NGSS = "ngss", "Next Generation Science Standards"
        CBSE = "cbse", "CBSE Curriculum"
        NCERT = "ncert", "NCERT Curriculum"
        NATIONAL_UK = "national_uk", "National Curriculum (UK)"
        IB = "ib", "International Baccalaureate"
        CUSTOM = "custom", "Custom / School-Defined"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="curriculum_standards")
    framework = models.CharField(max_length=20, choices=Framework.choices, default=Framework.CUSTOM)
    code = models.CharField(
        max_length=50,
        help_text="Unique standard code, e.g. CCSS.MATH.8.EE.1",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    grade = models.ForeignKey(
        Grade, on_delete=models.CASCADE, related_name="curriculum_standards", null=True, blank=True
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="curriculum_standards", null=True, blank=True
    )
    domain = models.CharField(
        max_length=100,
        blank=True,
        help_text="High-level domain, e.g. Algebra, Geometry, Life Science",
    )
    cluster = models.CharField(
        max_length=100,
        blank=True,
        help_text="Sub-domain cluster within the domain",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "curriculum_standards"
        unique_together = [("school", "code")]
        ordering = ["grade", "code"]
        indexes = [
            models.Index(fields=["school", "framework"]),
            models.Index(fields=["school", "grade"]),
        ]

    def __str__(self):
        return f"{self.code} — {self.name}"


class SubjectStandardMapping(models.Model):
    """Maps a subject to one or more curriculum standards.

    Tracks which standards a subject covers and to what extent,
    useful for accreditation and curriculum review.
    """

    class CoverageLevel(models.TextChoices):
        FULL = "full", "Fully Covered"
        PARTIAL = "partial", "Partially Covered"
        INTRODUCED = "introduced", "Introduced"
        NOT_COVERED = "not_covered", "Not Covered"

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="standard_mappings")
    standard = models.ForeignKey(CurriculumStandard, on_delete=models.CASCADE, related_name="subject_mappings")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="standard_mappings")
    coverage_level = models.CharField(max_length=15, choices=CoverageLevel.choices, default=CoverageLevel.PARTIAL)
    notes = models.TextField(blank=True)
    mapped_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="standard_mappings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subject_standard_mappings"
        unique_together = [("subject", "standard", "academic_year")]
        ordering = ["subject", "standard__code"]
        indexes = [
            models.Index(fields=["subject", "academic_year"]),
            models.Index(fields=["standard", "academic_year"]),
        ]

    def __str__(self):
        return f"{self.subject} ↔ {self.standard.code} ({self.get_coverage_level_display()})"


class Syllabus(models.Model):
    """Term-level syllabus for a subject.

    Defines the overall outline for a term/semester, including learning
    objectives, resources, and assessment criteria. Contains multiple
    SyllabusTopic records for granular topic-level tracking.
    """

    class Term(models.TextChoices):
        FIRST = "1st", "First Term"
        SECOND = "2nd", "Second Term"
        THIRD = "3rd", "Third Term"
        SEMESTER_1 = "sem1", "Semester 1"
        SEMESTER_2 = "sem2", "Semester 2"
        ANNUAL = "annual", "Annual"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        UNDER_REVIEW = "under_review", "Under Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="syllabi")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="syllabi")
    term = models.CharField(max_length=10, choices=Term.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    learning_objectives = models.TextField(help_text="High-level learning objectives for this term")
    resources = models.TextField(blank=True, help_text="Textbooks, online resources, lab materials")
    assessment_criteria = models.TextField(blank=True, help_text="How students will be assessed")
    total_hours = models.PositiveSmallIntegerField(default=0, help_text="Planned total teaching hours for the term")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_syllabi")
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_syllabi"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "syllabi"
        unique_together = [("subject", "academic_year", "term")]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["subject", "academic_year"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.subject.name} — {self.title} ({self.get_term_display()})"

    @property
    def topic_count(self):
        return self.topics.count()

    @property
    def completed_topic_count(self):
        return self.topics.filter(status="completed").count()

    @property
    def progress_percentage(self):
        total = self.topic_count
        if total == 0:
            return 0
        return round((self.completed_topic_count / total) * 100, 1)


class SyllabusTopic(models.Model):
    """Individual topic within a syllabus.

    Represents a single unit/topic that needs to be covered, with estimated
    hours and tracking of completion status.
    """

    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        SKIPPED = "skipped", "Skipped"

    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name="topics")
    order = models.PositiveSmallIntegerField(help_text="Sequence order within the syllabus")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    learning_outcomes = models.TextField(
        blank=True, help_text="What students should know/be able to do after this topic"
    )
    estimated_hours = models.DecimalField(
        max_digits=4, decimal_places=1, default=1.0, help_text="Estimated teaching hours"
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NOT_STARTED)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "syllabus_topics"
        unique_together = [("syllabus", "order")]
        ordering = ["order"]
        indexes = [
            models.Index(fields=["syllabus", "status"]),
        ]

    def __str__(self):
        return f"{self.order}. {self.title} ({self.syllabus.subject.name})"


class TeacherWorkloadConfig(models.Model):
    """School-level configuration for teacher workload limits.

    Defines maximum periods per week, maximum subjects, and other
    workload constraints that apply to all teachers in the school.
    """

    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name="teacher_workload_config")
    max_periods_per_week = models.PositiveSmallIntegerField(default=30, help_text="Maximum teaching periods per week")
    max_periods_per_day = models.PositiveSmallIntegerField(default=7, help_text="Maximum teaching periods per day")
    max_subjects = models.PositiveSmallIntegerField(default=3, help_text="Maximum different subjects per teacher")
    max_classes = models.PositiveSmallIntegerField(default=5, help_text="Maximum different classes per teacher")
    min_periods_per_week = models.PositiveSmallIntegerField(
        default=15, help_text="Minimum teaching periods (for full-time)"
    )
    warning_threshold_pct = models.PositiveSmallIntegerField(
        default=90, help_text="Workload % at which to trigger warnings"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "teacher_workload_configs"

    def __str__(self):
        return f"Workload Config — {self.school.name}"


class TeacherWorkloadSnapshot(models.Model):
    """Point-in-time snapshot of a teacher's workload for a given week.

    Calculated from timetable slots and assignments. Used for historical
    tracking and reporting.
    """

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workload_snapshots")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="workload_snapshots")
    week_start_date = models.DateField(help_text="Monday of the week")
    total_periods = models.PositiveSmallIntegerField(default=0)
    periods_per_day = models.JSONField(
        default=dict, blank=True, help_text='JSON map of day name to period count, e.g. {"Monday": 6}'
    )
    subjects_taught = models.PositiveSmallIntegerField(default=0)
    classes_taught = models.PositiveSmallIntegerField(default=0)
    utilization_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="Percentage of max periods used"
    )
    is_overloaded = models.BooleanField(default=False)
    is_underloaded = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "teacher_workload_snapshots"
        unique_together = [("teacher", "academic_year", "week_start_date")]
        ordering = ["-week_start_date"]
        indexes = [
            models.Index(fields=["teacher", "academic_year"]),
            models.Index(fields=["is_overloaded"]),
        ]

    def __str__(self):
        return f"{self.teacher.full_name} — Week of {self.week_start_date} ({self.total_periods} periods)"


class EvaluationCriteria(models.Model):
    """Defines evaluation criteria for teacher assessments.

    Schools create criteria like "Lesson Planning", "Classroom Management",
    "Student Engagement", etc. Each criterion has a weight and scale.
    """

    class Category(models.TextChoices):
        PLANNING = "planning", "Lesson Planning & Preparation"
        INSTRUCTION = "instruction", "Instructional Delivery"
        CLASSROOM = "classroom", "Classroom Management"
        ASSESSMENT = "assessment", "Assessment & Feedback"
        PROFESSIONAL = "professional", "Professional Development"
        COMMUNICATION = "communication", "Communication & Collaboration"
        STUDENT = "student", "Student Support & Engagement"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="evaluation_criteria")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    max_score = models.PositiveSmallIntegerField(default=5, help_text="Maximum score (e.g., 5 for a 1-5 scale)")
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, default=1.0, help_text="Weight in final score calculation"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "evaluation_criteria"
        unique_together = [("school", "name")]
        ordering = ["order", "category", "name"]
        indexes = [
            models.Index(fields=["school", "category"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class EvaluationTemplate(models.Model):
    """Reusable evaluation template that groups criteria.

    Defines a standard evaluation form with criteria and scoring guidance.
    """

    class EvalType(models.TextChoices):
        OBSERVATION = "observation", "Classroom Observation"
        SELF = "self", "Self-Evaluation"
        PEER = "peer", "Peer Evaluation"
        STUDENT_FEEDBACK = "student_feedback", "Student Feedback"
        PERFORMANCE = "performance", "Performance Review"
        PROBATIONARY = "probationary", "Probationary Review"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="evaluation_templates")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    eval_type = models.CharField(max_length=20, choices=EvalType.choices)
    criteria = models.ManyToManyField(EvaluationCriteria, related_name="templates", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "evaluation_templates"
        unique_together = [("school", "name")]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_eval_type_display()})"


class TeacherEvaluation(models.Model):
    """An evaluation instance for a teacher.

    Links to a template, tracks scores per criterion, and calculates
    an overall weighted score. Supports multi-phase workflow:
    draft → self_review → peer_review → admin_review → completed.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SELF_REVIEW = "self_review", "Awaiting Self-Review"
        PEER_REVIEW = "peer_review", "Awaiting Peer Review"
        ADMIN_REVIEW = "admin_review", "Awaiting Admin Review"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluations")
    template = models.ForeignKey(EvaluationTemplate, on_delete=models.SET_NULL, null=True, related_name="evaluations")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="evaluations")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    evaluation_period = models.CharField(
        max_length=50,
        blank=True,
        help_text='e.g. "Fall 2026", "Q1 2026-27"',
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    overall_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Calculated weighted overall score"
    )
    max_possible_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Maximum possible weighted score"
    )
    strength = models.TextField(blank=True, help_text="Identified strengths")
    areas_for_growth = models.TextField(blank=True, help_text="Areas for improvement")
    action_plan = models.TextField(blank=True, help_text="Development action plan")
    evaluator_notes = models.TextField(blank=True)
    teacher_comments = models.TextField(blank=True, help_text="Teacher's self-reflection")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_evaluations")
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_evaluations"
    )
    review_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "teacher_evaluations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["teacher", "academic_year"]),
            models.Index(fields=["status"]),
            models.Index(fields=["teacher", "status"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.teacher.full_name} ({self.get_status_display()})"

    @property
    def score_percentage(self):
        if not self.overall_score or not self.max_possible_score or self.max_possible_score == 0:
            return None
        return round((float(self.overall_score) / float(self.max_possible_score)) * 100, 1)

    @property
    def score_display(self):
        """Human-readable score like "4.2 / 5.0" or "85%"."""
        pct = self.score_percentage
        if pct is not None:
            return f"{pct}%"
        if self.overall_score is not None:
            return f"{self.overall_score} / {self.max_possible_score or '?'}"
        return "Not scored"


class EvaluationScore(models.Model):
    """Individual criterion score within an evaluation."""

    evaluation = models.ForeignKey(TeacherEvaluation, on_delete=models.CASCADE, related_name="scores")
    criterion = models.ForeignKey(EvaluationCriteria, on_delete=models.CASCADE, related_name="scores")
    score = models.DecimalField(max_digits=4, decimal_places=2, help_text="Score for this criterion")
    weighted_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Score multiplied by criterion weight"
    )
    evidence = models.TextField(blank=True, help_text="Supporting evidence or examples")
    comments = models.TextField(blank=True)
    scored_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="evaluation_scores")
    scored_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "evaluation_scores"
        unique_together = [("evaluation", "criterion")]
        ordering = ["criterion__order", "criterion__name"]
        indexes = [
            models.Index(fields=["evaluation", "criterion"]),
        ]

    def save(self, *args, **kwargs):
        # Auto-calculate weighted score
        self.weighted_score = float(self.score) * float(self.criterion.weight)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.criterion.name}: {self.score} / {self.criterion.max_score}"


class EvaluationComment(models.Model):
    """Comment thread on an evaluation."""

    class CommentType(models.TextChoices):
        GENERAL = "general", "General Comment"
        STRENGTH = "strength", "Strength"
        GROWTH = "growth", "Area for Growth"
        ACTION = "action", "Action Item"
        TEACHER_RESPONSE = "teacher_response", "Teacher Response"

    evaluation = models.ForeignKey(TeacherEvaluation, on_delete=models.CASCADE, related_name="comments_list")
    comment_type = models.CharField(max_length=20, choices=CommentType.choices, default=CommentType.GENERAL)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="evaluation_comments")
    content = models.TextField()
    is_private = models.BooleanField(default=False, help_text="Private comments are only visible to admins")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "evaluation_comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["evaluation", "comment_type"]),
        ]

    def __str__(self):
        return f"{self.get_comment_type_display()} by {self.author} on {self.evaluation.title}"


class AcademicTranscript(models.Model):
    """Official academic transcript for a student.

    Aggregates grades across all exams and subjects for a given academic year.
    Generates a PDF-ready document with grades, GPA, rank, and attendance.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        GENERATED = "generated", "Generated"
        VERIFIED = "verified", "Verified"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="transcripts")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="transcripts")
    transcript_number = models.CharField(max_length=50, unique=True, help_text="Unique transcript identifier")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    total_marks = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, help_text="Sum of max marks across all subjects"
    )
    obtained_marks = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Sum of marks obtained")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gpa = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Cumulative GPA")
    grade_letter = models.CharField(max_length=5, blank=True, help_text="Overall letter grade")
    rank_in_class = models.PositiveSmallIntegerField(null=True, blank=True)
    rank_in_grade = models.PositiveSmallIntegerField(null=True, blank=True)
    attendance_days = models.PositiveSmallIntegerField(default=0)
    total_school_days = models.PositiveSmallIntegerField(default=0)
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    subjects_data = models.JSONField(
        default=list,
        blank=True,
        help_text='JSON array of per-subject data: [{"name": ..., "marks": ..., "grade": ...}]',
    )
    principal_name = models.CharField(max_length=255, blank=True)
    principal_signature = models.ImageField(upload_to="transcripts/signatures/", null=True, blank=True)
    class_teacher_name = models.CharField(max_length=255, blank=True)
    remarks = models.TextField(blank=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="generated_transcripts")
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_transcripts"
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    pdf_file = models.FileField(upload_to="transcripts/pdfs/%Y/%m/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academic_transcripts"
        unique_together = [("student", "academic_year")]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "academic_year"]),
            models.Index(fields=["transcript_number"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Transcript {self.transcript_number} — {self.student} ({self.academic_year})"

    def save(self, *args, **kwargs):
        if not self.transcript_number:
            self.transcript_number = f"TR-{self.student.admission_number}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def score_display(self):
        if self.grade_letter:
            return f"{self.grade_letter} ({self.percentage}%)"
        return f"{self.percentage}%"


# ---------------------------------------------------------------------------
# P1: Academic Calendar Integration
# ---------------------------------------------------------------------------


class AcademicTerm(models.Model):
    """Term/semester definition within an academic year.

    Defines the start/end dates for each term, along with key dates
    like report card distribution and parent-teacher conferences.
    """

    class TermType(models.TextChoices):
        TRIMESTER_1 = "t1", "Trimester 1"
        TRIMESTER_2 = "t2", "Trimester 2"
        TRIMESTER_3 = "t3", "Trimester 3"
        SEMESTER_1 = "s1", "Semester 1"
        SEMESTER_2 = "s2", "Semester 2"
        QUARTER_1 = "q1", "Quarter 1"
        QUARTER_2 = "q2", "Quarter 2"
        QUARTER_3 = "q3", "Quarter 3"
        QUARTER_4 = "q4", "Quarter 4"
        ANNUAL = "annual", "Annual"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_terms")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="terms")
    name = models.CharField(max_length=100, help_text="e.g. 'Term 1', 'Semester 2', 'Q1 2026-27'")
    term_type = models.CharField(max_length=10, choices=TermType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    report_card_date = models.DateField(null=True, blank=True, help_text="Date report cards are distributed")
    parent_teacher_date = models.DateField(null=True, blank=True, help_text="Parent-teacher conference date")
    enrollment_deadline = models.DateField(null=True, blank=True, help_text="Deadline for subject enrollment changes")
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academic_terms"
        unique_together = [("school", "academic_year", "name")]
        ordering = ["start_date"]
        indexes = [
            models.Index(fields=["school", "academic_year"]),
            models.Index(fields=["is_current"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

    @property
    def duration_days(self):
        return (self.end_date - self.start_date).days + 1


class AcademicEvent(models.Model):
    """Calendar events: exams, conferences, holidays, milestones.

    Ties into the academic calendar for scheduling and reporting.
    """

    class EventType(models.TextChoices):
        EXAM = "exam", "Examination"
        PARENT_TEACHER = "ptm", "Parent-Teacher Meeting"
        HOLIDAY = "holiday", "Holiday"
        MILESTONE = "milestone", "Academic Milestone"
        ENROLLMENT = "enrollment", "Enrollment Period"
        REPORT_CARD = "report_card", "Report Card Distribution"
        ORIENTATION = "orientation", "Orientation"
        FIELD_TRIP = "field_trip", "Field Trip"
        CULTURAL = "cultural", "Cultural Event"
        SPORTS = "sports", "Sports Event"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_events")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="academic_events")
    term = models.ForeignKey(AcademicTerm, on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=15, choices=EventType.choices)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_all_day = models.BooleanField(default=True)
    affected_grades = models.ManyToManyField(Grade, blank=True, related_name="academic_events")
    affected_subjects = models.ManyToManyField(Subject, blank=True, related_name="academic_events")
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=255, blank=True, help_text="iCal RRULE format for recurring events")
    location = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_academic_events")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academic_events"
        ordering = ["start_date", "start_time"]
        indexes = [
            models.Index(fields=["school", "academic_year"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["start_date"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()}) — {self.start_date}"

    @property
    def duration_days(self):
        end = self.end_date or self.start_date
        return (end - self.start_date).days + 1


class AcademicHoliday(models.Model):
    """Holiday calendar — links to attendance module for auto-absence marking."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_holidays")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="academic_holidays")
    name = models.CharField(max_length=200)
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="For multi-day holidays")
    holiday_type = models.CharField(
        max_length=20,
        choices=[
            ("public", "Public Holiday"),
            ("school", "School Holiday"),
            ("break", "Term Break"),
            ("other", "Other"),
        ],
        default="school",
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "academic_holidays"
        unique_together = [("school", "academic_year", "date")]
        ordering = ["date"]
        indexes = [
            models.Index(fields=["school", "academic_year"]),
        ]

    def __str__(self):
        return f"{self.name} — {self.date}"

    @property
    def duration_days(self):
        end = self.end_date or self.date
        return (end - self.date).days + 1


# ---------------------------------------------------------------------------
# P2: Assignment & Homework Tracking
# ---------------------------------------------------------------------------


class Assignment(models.Model):
    """Assignment posted by a teacher for a subject-classroom combination."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"
        ARCHIVED = "archived", "Archived"

    class AssignmentType(models.TextChoices):
        HOMEWORK = "homework", "Homework"
        CLASSWORK = "classwork", "Classwork"
        PROJECT = "project", "Project"
        QUIZ = "quiz", "Quiz"
        LAB = "lab", "Lab Work"
        READING = "reading", "Reading"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(TeacherAssignment, on_delete=models.CASCADE, related_name="assignments_list")
    title = models.CharField(max_length=255)
    description = models.TextField()
    assignment_type = models.CharField(max_length=15, choices=AssignmentType.choices, default=AssignmentType.HOMEWORK)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    due_date = models.DateField()
    due_time = models.TimeField(null=True, blank=True)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    weight_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="Weight in final grade calculation"
    )
    allow_late_submissions = models.BooleanField(default=True)
    late_penalty_per_day = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="Percentage deduction per day late"
    )
    attachments = models.JSONField(default=list, blank=True, help_text="List of file URLs attached to the assignment")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_assignments")
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assignments"
        ordering = ["-due_date", "-created_at"]
        indexes = [
            models.Index(fields=["assignment", "status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["assignment_type"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.assignment.subject.name} (Due: {self.due_date})"

    @property
    def is_overdue(self):
        from django.utils import timezone

        return self.due_date < timezone.now().date() and self.status == self.Status.PUBLISHED

    @property
    def submission_count(self):
        return self.submissions.count()

    @property
    def average_score(self):
        from django.db.models import Avg

        result = self.submissions.aggregate(avg=Avg("score"))
        return result["avg"] or 0


class AssignmentSubmission(models.Model):
    """Student submission for an assignment."""

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        LATE = "late", "Late Submission"
        GRADED = "graded", "Graded"
        RETURNED = "returned", "Returned for Revision"
        RESUBMITTED = "resubmitted", "Resubmitted"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="assignment_submissions")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SUBMITTED)
    content = models.TextField(blank=True, help_text="Text-based submission content")
    attachments = models.JSONField(default=list, blank=True, help_text="List of file URLs submitted by student")
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_late = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    grade_letter = models.CharField(max_length=5, blank=True)
    feedback = models.TextField(blank=True, help_text="Teacher feedback")
    graded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="graded_submissions"
    )
    graded_at = models.DateTimeField(null=True, blank=True)
    submission_number = models.PositiveSmallIntegerField(
        default=1, help_text="Incremental submission number for resubmissions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assignment_submissions"
        unique_together = [("assignment", "student", "submission_number")]
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["assignment", "student"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.student} → {self.assignment.title} (#{self.submission_number})"

    @property
    def score_percentage(self):
        if self.score is not None and self.assignment.max_score:
            return round((float(self.score) / float(self.assignment.max_score)) * 100, 1)
        return None


class HomeworkTracker(models.Model):
    """Daily homework tracking per classroom — records what homework was assigned."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="homework_entries")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    date = models.DateField(help_text="Date the homework is assigned for")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "homework_tracker"
        unique_together = [("classroom", "date", "subject")]
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["classroom", "date"]),
        ]

    def __str__(self):
        return f"{self.classroom} — {self.subject.name} — {self.date}"


# ---------------------------------------------------------------------------
# P3: Exam Management Enhancements
# ---------------------------------------------------------------------------


class QuestionBank(models.Model):
    """Reusable question bank for exam paper generation."""

    class QuestionType(models.TextChoices):
        MCQ = "mcq", "Multiple Choice"
        TRUE_FALSE = "tf", "True/False"
        SHORT_ANSWER = "short", "Short Answer"
        LONG_ANSWER = "long", "Long Answer"
        FILL_BLANK = "fill", "Fill in the Blanks"
        MATCHING = "match", "Matching"
        ESSAY = "essay", "Essay"
        NUMERICAL = "numerical", "Numerical"

    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="question_bank")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="questions")
    question_type = models.CharField(max_length=10, choices=QuestionType.choices)
    difficulty = models.CharField(max_length=10, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    question_text = models.TextField()
    options = models.JSONField(default=list, blank=True, help_text='MCQ options: [{"key": "A", "text": "..."}]')
    correct_answer = models.TextField(help_text="Correct answer or option key")
    explanation = models.TextField(blank=True, help_text="Answer explanation")
    marks = models.PositiveSmallIntegerField(default=1)
    tags = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_questions")
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "question_bank"
        ordering = ["subject", "difficulty", "question_type"]
        indexes = [
            models.Index(fields=["school", "subject"]),
            models.Index(fields=["question_type", "difficulty"]),
        ]

    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.question_text[:60]}..."


class ExamPaper(models.Model):
    """Generated exam paper from question bank with random selection."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        FINALIZED = "finalized", "Finalized"
        USED = "used", "Used"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="exam_papers")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    total_marks = models.PositiveSmallIntegerField(default=100)
    duration_minutes = models.PositiveSmallIntegerField(default=120)
    questions = models.ManyToManyField(QuestionBank, related_name="papers", blank=True)
    question_distribution = models.JSONField(default=dict, blank=True, help_text='{"mcq": 10, "short": 5, "long": 3}')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exam_papers"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["school", "subject"]),
        ]

    def __str__(self):
        return f"{self.title} — {self.subject.name} ({self.total_marks} marks)"

    @property
    def question_count(self):
        return self.questions.count()

    def generate_random(self, distribution=None):
        """Auto-select questions from the bank based on distribution."""
        if distribution is None:
            distribution = self.question_distribution or {}
        questions = []
        for q_type, count in distribution.items():
            pool = list(
                QuestionBank.objects.filter(
                    subject=self.subject,
                    question_type=q_type,
                    is_active=True,
                ).order_by(
                    "?"
                )[:count]
            )
            questions.extend(pool)
        self.questions.set(questions)
        self.save(update_fields=["updated_at"])
        return len(questions)


# ---------------------------------------------------------------------------
# P4: Notification Hooks
# ---------------------------------------------------------------------------


class AcademicNotification(models.Model):
    """In-app notifications for academic events and updates."""

    class NotificationType(models.TextChoices):
        LESSON_PLAN_APPROVED = "lesson_plan_approved", "Lesson Plan Approved"
        LESSON_PLAN_REJECTED = "lesson_plan_rejected", "Lesson Plan Rejected"
        ASSIGNMENT_POSTED = "assignment_posted", "Assignment Posted"
        ASSIGNMENT_GRADED = "assignment_graded", "Assignment Graded"
        ASSIGNMENT_DUE_SOON = "assignment_due_soon", "Assignment Due Soon"
        GRADE_PUBLISHED = "grade_published", "Grade Published"
        TRANSCRIPT_READY = "transcript_ready", "Transcript Ready"
        EVALUATION_STATUS = "evaluation_status", "Evaluation Status Update"
        EXAM_SCHEDULED = "exam_scheduled", "Exam Scheduled"
        TERM_START = "term_start", "Term Starting Soon"
        ENROLLMENT_DEADLINE = "enrollment_deadline", "Enrollment Deadline Approaching"
        ATTENDANCE_ALERT = "attendance_alert", "Attendance Alert"
        GENERAL = "general", "General Announcement"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="academic_notifications")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="academic_notifications")
    notification_type = models.CharField(max_length=25, choices=NotificationType.choices)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    title = models.CharField(max_length=255)
    message = models.TextField()
    action_url = models.CharField(max_length=500, blank=True, help_text="Deep link to the relevant page")
    metadata = models.JSONField(
        default=dict, blank=True, help_text='Extra context: {"assignment_id": "...", "subject": "..."}'
    )
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_emailed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "academic_notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["notification_type"]),
            models.Index(fields=["school", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} → {self.recipient}"

    @classmethod
    def create_notification(cls, recipient, notification_type, title, message, **kwargs):
        """Helper to create and return a notification."""
        return cls.objects.create(
            school=recipient.school,
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            **kwargs,
        )


# ---------------------------------------------------------------------------
# P5: Analytics & Reporting
# ---------------------------------------------------------------------------


class SubjectPerformance(models.Model):
    """Aggregated subject performance analytics per academic year."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="performance_stats")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.SET_NULL, null=True, blank=True)
    total_students = models.PositiveIntegerField(default=0)
    average_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    median_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    highest_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    lowest_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade_distribution = models.JSONField(
        default=dict, blank=True, help_text='{"A": 10, "B": 20, "C": 15, "D": 5, "F": 2}'
    )
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subject_performance"
        unique_together = [("subject", "academic_year", "term")]
        indexes = [
            models.Index(fields=["subject", "academic_year"]),
        ]

    def __str__(self):
        return f"{self.subject.name} — Avg: {self.average_score}% ({self.academic_year})"


class StudentProgressReport(models.Model):
    """Individual student progress tracking across terms."""

    class Trend(models.TextChoices):
        IMPROVING = "improving", "Improving"
        STABLE = "stable", "Stable"
        DECLINING = "declining", "Declining"
        INSUFFICIENT = "insufficient", "Insufficient Data"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="progress_reports")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    current_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    previous_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    score_change = models.DecimalField(
        max_digits=6, decimal_places=2, default=0, help_text="Positive = improvement, Negative = decline"
    )
    trend = models.CharField(max_length=15, choices=Trend.choices, default=Trend.INSUFFICIENT)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    assignment_completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    teacher_remarks = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_progress_reports"
        unique_together = [("student", "academic_year", "term", "subject")]
        ordering = ["subject__name"]
        indexes = [
            models.Index(fields=["student", "academic_year"]),
            models.Index(fields=["trend"]),
        ]

    def __str__(self):
        return f"{self.student} — {self.subject.name} ({self.trend})"

    def calculate_trend(self):
        """Determine trend from score change."""
        if self.previous_score is None:
            self.trend = self.Trend.INSUFFICIENT
        elif self.score_change > 5:
            self.trend = self.Trend.IMPROVING
        elif self.score_change < -5:
            self.trend = self.Trend.DECLINING
        else:
            self.trend = self.Trend.STABLE
        return self.trend


class TeacherEffectiveness(models.Model):
    """Teacher effectiveness metrics correlated with student outcomes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="effectiveness_stats")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    total_students = models.PositiveIntegerField(default=0)
    average_student_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    pass_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    evaluation_score = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Latest evaluation score (0-100)"
    )
    lesson_completion_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="Percentage of syllabus completed"
    )
    assignment_count = models.PositiveIntegerField(default=0)
    average_assignment_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    attendance_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="Student attendance in this teacher's classes"
    )
    effectiveness_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="Composite score (0-100)"
    )
    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "teacher_effectiveness"
        unique_together = [("teacher", "academic_year", "term", "subject")]
        ordering = ["-effectiveness_score"]
        indexes = [
            models.Index(fields=["teacher", "academic_year"]),
            models.Index(fields=["-effectiveness_score"]),
        ]

    def __str__(self):
        return f"{self.teacher.full_name} — {self.subject.name} (Score: {self.effectiveness_score})"

    def calculate_effectiveness(self):
        """Calculate composite effectiveness score from multiple factors."""
        scores = []
        # Student performance (40% weight)
        if self.average_student_score:
            scores.append((float(self.average_student_score), 0.4))
        # Pass rate (20% weight)
        if self.pass_rate:
            scores.append((float(self.pass_rate), 0.2))
        # Evaluation score (20% weight)
        if self.evaluation_score:
            scores.append((float(self.evaluation_score), 0.2))
        # Lesson completion (10% weight)
        if self.lesson_completion_rate:
            scores.append((float(self.lesson_completion_rate), 0.1))
        # Attendance rate (10% weight)
        if self.attendance_rate:
            scores.append((float(self.attendance_rate), 0.1))

        if scores:
            total_weight = sum(w for _, w in scores)
            weighted_sum = sum(s * w for s, w in scores)
            self.effectiveness_score = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0
        return self.effectiveness_score
