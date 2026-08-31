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
