"""Alumni Management — Profiles, events, donations, chapters, mentorship, jobs, community."""

import uuid

from django.core.validators import MaxValueValidator
from django.db import models
from services.auth.models import School, User


class AlumniProfile(models.Model):
    """Extended profile for graduated students."""

    class EmploymentStatus(models.TextChoices):
        EMPLOYED = "employed", "Employed"
        SELF_EMPLOYED = "self_employed", "Self-Employed"
        STUDENT = "student", "Further Studies"
        UNEMPLOYED = "unemployed", "Unemployed"
        RETIRED = "retired", "Retired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_profiles")
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="alumni_profile")
    graduation_year = models.PositiveSmallIntegerField()
    student_id = models.CharField(max_length=30, blank=True)
    occupation = models.CharField(max_length=150, blank=True)
    employer = models.CharField(max_length=150, blank=True)
    employment_status = models.CharField(
        max_length=20, choices=EmploymentStatus.choices, default=EmploymentStatus.EMPLOYED
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_handle = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    is_newsletter_subscribed = models.BooleanField(default=True)
    is_visible_to_public = models.BooleanField(default=False)
    # Engagement tracking
    engagement_score = models.PositiveSmallIntegerField(
        default=0, validators=[MaxValueValidator(100)], help_text="Engagement score (0-100) based on activity"
    )
    last_activity_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_profiles"
        ordering = ["-graduation_year", "user__last_name", "user__first_name"]

    def __str__(self):
        return f"{self.user.full_name} ({self.graduation_year})"


class AlumniEvent(models.Model):
    """Events organized for alumni (reunions, networking, galas)."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_events")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    max_attendees = models.PositiveSmallIntegerField(default=0)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    organizer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="organized_alumni_events"
    )
    cover_image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_events"
        ordering = ["-event_date"]

    def __str__(self):
        return self.title


class AlumniEventRSVP(models.Model):
    """RSVP and attendance tracking for alumni events."""

    class RSVPStatus(models.TextChoices):
        REGISTERED = "registered", "Registered"
        CONFIRMED = "confirmed", "Confirmed"
        ATTENDED = "attended", "Attended"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No Show"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(AlumniEvent, on_delete=models.CASCADE, related_name="rsvps")
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="event_rsvps")
    status = models.CharField(max_length=20, choices=RSVPStatus.choices, default=RSVPStatus.REGISTERED)
    registered_at = models.DateTimeField(auto_now_add=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    check_in_code = models.CharField(max_length=50, blank=True, help_text="QR code for check-in")
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "alumni_event_rsvps"
        unique_together = [("event", "alumni")]
        ordering = ["-registered_at"]

    def __str__(self):
        return f"{self.alumni} -> {self.event}"


class AlumniDonation(models.Model):
    """Donations and pledges from alumni."""

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        CHECK = "check", "Check"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        ONLINE = "online", "Online Payment"
        OTHER = "other", "Other"

    class FundType(models.TextChoices):
        GENERAL = "general", "General Fund"
        SCHOLARSHIP = "scholarship", "Scholarship Fund"
        INFRASTRUCTURE = "infrastructure", "Infrastructure"
        SPORTS = "sports", "Sports Fund"
        LIBRARY = "library", "Library Fund"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_donations")
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="donations")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    fund_type = models.CharField(max_length=20, choices=FundType.choices, default=FundType.GENERAL)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.ONLINE)
    transaction_id = models.CharField(max_length=100, blank=True)
    donation_date = models.DateField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=20,
        choices=[("monthly", "Monthly"), ("quarterly", "Quarterly"), ("yearly", "Yearly")],
        blank=True,
        help_text="Frequency for recurring donations",
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_donations"
        ordering = ["-donation_date"]

    def __str__(self):
        return f"{self.alumni} - ${self.amount}"


class AlumniDonationReceipt(models.Model):
    """Tax receipts for alumni donations."""

    class ReceiptStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        GENERATED = "generated", "Generated"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donation = models.OneToOneField(AlumniDonation, on_delete=models.CASCADE, related_name="receipt")
    receipt_number = models.CharField(max_length=50, unique=True)
    receipt_date = models.DateField(auto_now_add=True)
    tax_deductible_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=ReceiptStatus.choices, default=ReceiptStatus.PENDING)
    pdf_url = models.URLField(blank=True, help_text="URL to downloaded receipt PDF")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_donation_receipts"
        ordering = ["-receipt_date"]

    def __str__(self):
        return f"Receipt {self.receipt_number} for {self.donation}"


class AlumniChapter(models.Model):
    """Regional alumni chapters/groups."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_chapters")
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    president = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="presided_chapters"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_chapters"
        unique_together = [("school", "name")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class AlumniChapterMember(models.Model):
    """Membership records for alumni chapters."""

    class Role(models.TextChoices):
        PRESIDENT = "president", "President"
        VICE_PRESIDENT = "vice_president", "Vice President"
        SECRETARY = "secretary", "Secretary"
        TREASURER = "treasurer", "Treasurer"
        MEMBER = "member", "Member"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chapter = models.ForeignKey(AlumniChapter, on_delete=models.CASCADE, related_name="members")
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="chapter_memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "alumni_chapter_members"
        unique_together = [("chapter", "alumni")]
        ordering = ["role", "-joined_at"]

    def __str__(self):
        return f"{self.alumni} - {self.chapter} ({self.get_role_display()})"


class AlumniMentorship(models.Model):
    """Mentorship program connecting alumni mentors with students."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class FocusArea(models.TextChoices):
        CAREER = "career", "Career Guidance"
        INDUSTRY = "industry", "Industry Insights"
        ACADEMIC = "academic", "Academic Advice"
        PERSONAL = "personal", "Personal Development"
        ENTREPRENEURSHIP = "entrepreneurship", "Entrepreneurship"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_mentorships")
    mentor = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="mentoring")
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mentorships")
    focus_area = models.CharField(max_length=20, choices=FocusArea.choices, default=FocusArea.CAREER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    goals = models.TextField(blank=True, help_text="Mentorship goals and expectations")
    meeting_frequency = models.CharField(
        max_length=20,
        choices=[("weekly", "Weekly"), ("biweekly", "Bi-weekly"), ("monthly", "Monthly")],
        default="monthly",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_mentorships"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.mentor} -> {self.mentee} ({self.get_focus_area_display()})"


class AlumniJobPosting(models.Model):
    """Job postings from alumni for other alumni and students."""

    class JobType(models.TextChoices):
        FULL_TIME = "full_time", "Full-Time"
        PART_TIME = "part_time", "Part-Time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"
        FREELANCE = "freelance", "Freelance"

    class ExperienceLevel(models.TextChoices):
        ENTRY = "entry", "Entry Level"
        MID = "mid", "Mid Level"
        SENIOR = "senior", "Senior Level"
        EXECUTIVE = "executive", "Executive"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_job_postings")
    posted_by = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="job_postings")
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=150, blank=True)
    is_remote = models.BooleanField(default=False)
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    experience_level = models.CharField(max_length=20, choices=ExperienceLevel.choices, default=ExperienceLevel.MID)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    application_url = models.URLField(blank=True)
    application_email = models.EmailField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_job_postings"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} at {self.company}"


class AlumniJobApplication(models.Model):
    """Applications to alumni job postings."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWED = "reviewed", "Reviewed"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"
        HIRED = "hired", "Hired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(AlumniJobPosting, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alumni_job_applications")
    resume_url = models.URLField(blank=True, help_text="Link to resume/CV")
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Internal notes for the poster")

    class Meta:
        db_table = "alumni_job_applications"
        unique_together = [("job", "applicant")]
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.applicant} -> {self.job}"


class AlumniDiscussion(models.Model):
    """Discussion forums for alumni community."""

    class Category(models.TextChoices):
        GENERAL = "general", "General"
        CAREER = "career", "Career"
        INDUSTRY = "industry", "Industry"
        EVENTS = "events", "Events"
        NETWORKING = "networking", "Networking"
        MENTORSHIP = "mentorship", "Mentorship"
        ANNOUNCEMENTS = "announcements", "Announcements"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        PINNED = "pinned", "Pinned"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_discussions")
    author = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="discussions")
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_discussions"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class AlumniDiscussionReply(models.Model):
    """Replies to discussion threads."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discussion = models.ForeignKey(AlumniDiscussion, on_delete=models.CASCADE, related_name="replies")
    author = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="discussion_replies")
    content = models.TextField()
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children", help_text="For nested replies"
    )
    likes_count = models.PositiveIntegerField(default=0)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_discussion_replies"
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply by {self.author} on {self.discussion}"


class AlumniDiscussionLike(models.Model):
    """Likes on discussions and replies."""

    class TargetType(models.TextChoices):
        DISCUSSION = "discussion", "Discussion"
        REPLY = "reply", "Reply"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="discussion_likes")
    target_type = models.CharField(max_length=20, choices=TargetType.choices)
    discussion = models.ForeignKey(
        AlumniDiscussion, on_delete=models.CASCADE, null=True, blank=True, related_name="likes"
    )
    reply = models.ForeignKey(
        AlumniDiscussionReply, on_delete=models.CASCADE, null=True, blank=True, related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_discussion_likes"
        unique_together = [
            ("alumni", "target_type", "discussion"),
            ("alumni", "target_type", "reply"),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.alumni} liked {self.target_type}"
