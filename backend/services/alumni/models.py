"""Alumni Management — Profiles, events, donations, chapters, mentorship, jobs, community, campaigns, badges."""

import uuid

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone
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
    skills = models.JSONField(default=list, blank=True, help_text="List of skills")
    interests = models.JSONField(default=list, blank=True, help_text="List of interests")
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
        unique_together = [("alumni", "target_type", "discussion"), ("alumni", "target_type", "reply")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.alumni} liked {self.target_type}"


class AlumniVerification(models.Model):
    """Alumni identity verification system."""

    class VerificationMethod(models.TextChoices):
        DEGREE = "degree", "Degree Certificate"
        STUDENT_ID = "student_id", "Student ID"
        ADMIN_APPROVAL = "admin_approval", "Admin Approval"
        EMAIL_VERIFICATION = "email_verification", "Email Verification"
        MANUAL = "manual", "Manual Review"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="verifications")
    verification_method = models.CharField(max_length=20, choices=VerificationMethod.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    document_url = models.URLField(blank=True, help_text="URL to uploaded verification document")
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_alumni"
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Verification expiry date")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_verifications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.alumni} - {self.get_verification_method_display()} ({self.get_status_display()})"


class AlumniNewsletter(models.Model):
    """Newsletter campaigns for alumni communication."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SCHEDULED = "scheduled", "Scheduled"
        SENDING = "sending", "Sending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_newsletters")
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    content = models.TextField(help_text="HTML content of the newsletter")
    plain_text = models.TextField(blank=True, help_text="Plain text version")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    # Targeting
    target_graduation_years = models.JSONField(default=list, blank=True, help_text="Target specific graduation years")
    target_cities = models.JSONField(default=list, blank=True, help_text="Target specific cities")
    # Analytics
    total_sent = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    total_bounced = models.PositiveIntegerField(default=0)
    total_unsubscribed = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_newsletters")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_newsletters"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def open_rate(self):
        return (self.total_opened / self.total_sent * 100) if self.total_sent > 0 else 0

    @property
    def click_rate(self):
        return (self.total_clicked / self.total_sent * 100) if self.total_sent > 0 else 0


class AlumniCampaign(models.Model):
    """Fundraising campaigns for alumni donations."""

    class CampaignType(models.TextChoices):
        GENERAL = "general", "General Fund"
        SCHOLARSHIP = "scholarship", "Scholarship"
        INFRASTRUCTURE = "infrastructure", "Infrastructure"
        EMERGENCY = "emergency", "Emergency Fund"
        ANNUAL = "annual", "Annual Fund"
        CLASS_GIFT = "class_gift", "Class Gift"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_campaigns")
    title = models.CharField(max_length=200)
    description = models.TextField()
    campaign_type = models.CharField(max_length=20, choices=CampaignType.choices, default=CampaignType.GENERAL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    # Financials
    goal_amount = models.DecimalField(max_digits=14, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    donor_count = models.PositiveIntegerField(default=0)
    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    # Matching
    has_matching = models.BooleanField(default=False, help_text="Enable matching gifts")
    matching_multiplier = models.DecimalField(
        max_digits=5, decimal_places=2, default=1.0, help_text="e.g., 2.0 = 2x match"
    )
    matching_deadline = models.DateField(null=True, blank=True)
    # Media
    cover_image_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    # Settings
    is_anonymous_allowed = models.BooleanField(default=True)
    is_recurring_allowed = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_campaigns")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_campaigns"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        return (self.raised_amount / self.goal_amount * 100) if self.goal_amount > 0 else 0

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE


class AlumniCampaignDonation(models.Model):
    """Donations linked to a specific campaign."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(AlumniCampaign, on_delete=models.CASCADE, related_name="donations")
    donation = models.ForeignKey("AlumniDonation", on_delete=models.CASCADE, related_name="campaign_links")
    is_matching = models.BooleanField(default=False, help_text="Is this a matching donation?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_campaign_donations"
        unique_together = [("campaign", "donation")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.campaign} - {self.donation}"


class AlumniBadge(models.Model):
    """Badges and achievements for alumni recognition."""

    class BadgeType(models.TextChoices):
        MILESTONE = "milestone", "Milestone"
        DONATION = "donation", "Donation"
        ENGAGEMENT = "engagement", "Engagement"
        MENTORSHIP = "mentorship", "Mentorship"
        EVENT = "event", "Event Attendance"
        VOLUNTEER = "volunteer", "Volunteering"
        REFERRAL = "referral", "Referral"
        SPECIAL = "special", "Special Recognition"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_badges")
    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BadgeType.choices)
    icon_url = models.URLField(blank=True, help_text="Badge icon image URL")
    color = models.CharField(max_length=7, default="#007bff", help_text="Hex color code")
    # Criteria
    criteria_description = models.TextField(blank=True, help_text="How to earn this badge")
    criteria_value = models.PositiveIntegerField(null=True, blank=True, help_text="Threshold value (e.g., donate $100)")
    # Stats
    total_awarded = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_badges"
        ordering = ["badge_type", "name"]

    def __str__(self):
        return self.name


class AlumniBadgeAward(models.Model):
    """Records of badges awarded to alumni."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    badge = models.ForeignKey(AlumniBadge, on_delete=models.CASCADE, related_name="awards")
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="badges")
    awarded_at = models.DateTimeField(auto_now_add=True)
    awarded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="awarded_badges"
    )
    reason = models.TextField(blank=True, help_text="Reason for awarding this badge")
    is_public = models.BooleanField(default=True, help_text="Show on public profile")

    class Meta:
        db_table = "alumni_badge_awards"
        unique_together = [("badge", "alumni")]
        ordering = ["-awarded_at"]

    def __str__(self):
        return f"{self.alumni} - {self.badge}"


class AlumniActivityFeed(models.Model):
    """Chronological feed of alumni activities."""

    class ActivityType(models.TextChoices):
        PROFILE_UPDATE = "profile_update", "Profile Updated"
        EVENT_REGISTERED = "event_registered", "Event Registration"
        EVENT_ATTENDED = "event_attended", "Event Attendance"
        DONATION_MADE = "donation_made", "Donation Made"
        BADGE_EARNED = "badge_earned", "Badge Earned"
        MENTORSHIP_STARTED = "mentorship_started", "Mentorship Started"
        JOB_POSTED = "job_posted", "Job Posted"
        DISCUSSION_CREATED = "discussion_created", "Discussion Created"
        CHAPTER_JOINED = "chapter_joined", "Chapter Joined"
        VOLUNTEERED = "volunteered", "Volunteered"
        REFERRAL_MADE = "referral_made", "Referral Made"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="activity_feed")
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Reference to related objects
    reference_id = models.UUIDField(null=True, blank=True, help_text="ID of related object")
    reference_model = models.CharField(max_length=50, blank=True, help_text="Model name of related object")
    # Metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional activity data")
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_activity_feed"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["alumni", "created_at"]),
            models.Index(fields=["activity_type"]),
        ]

    def __str__(self):
        return f"{self.alumni} - {self.get_activity_type_display()}"


class AlumniGroup(models.Model):
    """Interest-based alumni groups/clubs."""

    class GroupType(models.TextChoices):
        INTEREST = "interest", "Interest Group"
        BATCH = "batch", "Batch/Class"
        SPORTS = "sports", "Sports Team"
        CLUB = "club", "Club"
        INDUSTRY = "industry", "Industry Network"
        REGIONAL = "regional", "Regional Group"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_groups")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    group_type = models.CharField(max_length=20, choices=GroupType.choices, default=GroupType.INTEREST)
    # Leadership
    admin = models.ForeignKey(
        AlumniProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name="admin_groups"
    )
    # Settings
    is_private = models.BooleanField(default=False, help_text="Require approval to join")
    is_active = models.BooleanField(default=True)
    max_members = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    # Stats
    member_count = models.PositiveIntegerField(default=0)
    # Media
    cover_image_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_groups"
        unique_together = [("school", "name")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class AlumniGroupMember(models.Model):
    """Membership records for alumni groups."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MODERATOR = "moderator", "Moderator"
        MEMBER = "member", "Member"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        BANNED = "banned", "Banned"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(AlumniGroup, on_delete=models.CASCADE, related_name="memberships")
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="group_memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_muted = models.BooleanField(default=False, help_text="Mute notifications from this group")

    class Meta:
        db_table = "alumni_group_members"
        unique_together = [("group", "alumni")]
        ordering = ["role", "-joined_at"]

    def __str__(self):
        return f"{self.alumni} - {self.group} ({self.get_role_display()})"


class AlumniGroupPost(models.Model):
    """Posts within alumni groups."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(AlumniGroup, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="group_posts")
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    attachment_url = models.URLField(blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_group_posts"
        ordering = ["-is_pinned", "-created_at"]

    def __str__(self):
        return f"{self.group} - {self.title or self.content[:50]}"


class AlumniVolunteer(models.Model):
    """Volunteering opportunities for alumni."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        FULL = "full", "Full"
        CLOSED = "closed", "Closed"
        COMPLETED = "completed", "Completed"

    class TimeCommitment(models.TextChoices):
        ONE_TIME = "one_time", "One-time"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        FLEXIBLE = "flexible", "Flexible"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_volunteer_opportunities")
    title = models.CharField(max_length=200)
    description = models.TextField()
    # Requirements
    skills_required = models.JSONField(default=list, blank=True)
    max_volunteers = models.PositiveIntegerField(default=0)
    current_volunteers = models.PositiveIntegerField(default=0)
    # Schedule
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    time_commitment = models.CharField(max_length=20, choices=TimeCommitment.choices, default=TimeCommitment.ONE_TIME)
    estimated_hours = models.PositiveIntegerField(default=0)
    # Location
    location = models.CharField(max_length=200, blank=True)
    is_remote = models.BooleanField(default=False)
    # Status
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="organized_volunteer_opps")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_volunteer_opportunities"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class AlumniVolunteerSignup(models.Model):
    """Alumni signups for volunteer opportunities."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(AlumniVolunteer, on_delete=models.CASCADE, related_name="signups")
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="volunteer_signups")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    hours_logged = models.PositiveIntegerField(default=0)
    feedback = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(null=True, blank=True, help_text="1-5 rating")
    signed_up_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "alumni_volunteer_signups"
        unique_together = [("opportunity", "alumni")]
        ordering = ["-signed_up_at"]

    def __str__(self):
        return f"{self.alumni} -> {self.opportunity}"


class AlumniPoll(models.Model):
    """Polls and surveys for alumni feedback."""

    class PollType(models.TextChoices):
        POLL = "poll", "Poll"
        SURVEY = "survey", "Survey"
        FEEDBACK = "feedback", "Feedback"
        ELECTION = "election", "Election"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        CLOSED = "closed", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_polls")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    poll_type = models.CharField(max_length=20, choices=PollType.choices, default=PollType.POLL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    # Settings
    is_anonymous = models.BooleanField(default=False)
    allow_multiple_answers = models.BooleanField(default=False)
    # Dates
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    # Stats
    total_responses = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_polls")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_polls"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class AlumniPollOption(models.Model):
    """Options for polls/surveys."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(AlumniPoll, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=200)
    vote_count = models.PositiveIntegerField(default=0)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "alumni_poll_options"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.poll.title} - {self.text}"


class AlumniPollResponse(models.Model):
    """Responses to polls/surveys."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(AlumniPoll, on_delete=models.CASCADE, related_name="responses")
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="poll_responses")
    option = models.ForeignKey(AlumniPollOption, on_delete=models.CASCADE, related_name="votes")
    text_response = models.TextField(blank=True, help_text="For open-ended questions")
    responded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_poll_responses"
        unique_together = [("poll", "alumni", "option")]
        ordering = ["-responded_at"]

    def __str__(self):
        return f"{self.alumni} -> {self.poll}"


class AlumniSuccessStory(models.Model):
    """Alumni success stories and testimonials."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending Review"
        PUBLISHED = "published", "Published"
        REJECTED = "rejected", "Rejected"

    class StoryType(models.TextChoices):
        CAREER = "career", "Career Achievement"
        ENTREPRENEURSHIP = "entrepreneurship", "Entrepreneurship"
        SOCIAL_IMPACT = "social_impact", "Social Impact"
        ACADEMIC = "academic", "Academic Excellence"
        SPORTS = "sports", "Sports Achievement"
        ARTS = "arts", "Arts & Culture"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_success_stories")
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="success_stories")
    title = models.CharField(max_length=200)
    content = models.TextField()
    story_type = models.CharField(max_length=20, choices=StoryType.choices, default=StoryType.CAREER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    # Media
    cover_image_url = models.URLField(blank=True)
    video_url = models.URLField(blank=True)
    # Stats
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    # SEO
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    # Admin
    featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_success_stories"
        ordering = ["-featured", "-published_at"]

    def __str__(self):
        return self.title


class AlumniReferral(models.Model):
    """Track alumni referrals for admissions/jobs."""

    class ReferralType(models.TextChoices):
        ADMISSION = "admission", "Admission Referral"
        JOB = "job", "Job Referral"
        EVENT = "event", "Event Referral"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONTACTED = "contacted", "Contacted"
        CONVERTED = "converted", "Converted"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_referrals")
    referrer = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="referrals_made")
    # Referred person info
    referred_name = models.CharField(max_length=150)
    referred_email = models.EmailField()
    referred_phone = models.CharField(max_length=20, blank=True)
    # Referral details
    referral_type = models.CharField(max_length=20, choices=ReferralType.choices, default=ReferralType.ADMISSION)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    # For job referrals
    job_posting = models.ForeignKey(
        "AlumniJobPosting", on_delete=models.SET_NULL, null=True, blank=True, related_name="referrals"
    )
    # Tracking
    referred_at = models.DateTimeField(auto_now_add=True)
    contacted_at = models.DateTimeField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    # Reward
    reward_points = models.PositiveIntegerField(default=0)
    reward_description = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "alumni_referrals"
        ordering = ["-referred_at"]

    def __str__(self):
        return f"{self.referrer} referred {self.referred_name}"


class AlumniDirectMessage(models.Model):
    """Private messaging between alumni."""

    class MessageType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        FILE = "file", "File"
        LINK = "link", "Link"
        SYSTEM = "system", "System"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="received_messages")
    message_type = models.CharField(max_length=20, choices=MessageType.choices, default=MessageType.TEXT)
    content = models.TextField()
    attachment_url = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_deleted_by_sender = models.BooleanField(default=False)
    is_deleted_by_receiver = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_direct_messages"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sender", "receiver"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:50]}"


class AlumniConversation(models.Model):
    """Tracks conversation metadata between two alumni."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participant1 = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="conversations_as_p1")
    participant2 = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="conversations_as_p2")
    last_message = models.ForeignKey(
        AlumniDirectMessage, on_delete=models.SET_NULL, null=True, blank=True, related_name="conversations"
    )
    last_message_at = models.DateTimeField(null=True, blank=True)
    is_archived_by_p1 = models.BooleanField(default=False)
    is_archived_by_p2 = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_conversations"
        unique_together = [("participant1", "participant2")]
        ordering = ["-last_message_at"]

    def __str__(self):
        return f"{self.participant1} <-> {self.participant2}"


class AlumniCalendarEvent(models.Model):
    """Calendar events with iCal/Google export support."""

    class EventType(models.TextChoices):
        REUNION = "reunion", "Reunion"
        NETWORKING = "networking", "Networking"
        GALA = "gala", "Gala"
        WORKSHOP = "workshop", "Workshop"
        WEBINAR = "webinar", "Webinar"
        SPORTS = "sports", "Sports"
        CULTURAL = "cultural", "Cultural"
        CAREER = "career", "Career"
        OTHER = "other", "Other"

    class RecurrenceType(models.TextChoices):
        NONE = "none", "None"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        YEARLY = "yearly", "Yearly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_calendar_events")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EventType.choices, default=EventType.OTHER)
    # Date/Time
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    all_day = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, default="UTC")
    # Recurrence
    recurrence_type = models.CharField(max_length=20, choices=RecurrenceType.choices, default=RecurrenceType.NONE)
    recurrence_end_date = models.DateField(null=True, blank=True)
    # Location
    location = models.CharField(max_length=200, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    is_virtual = models.BooleanField(default=False)
    virtual_link = models.URLField(blank=True)
    # Export
    ical_uid = models.CharField(max_length=100, unique=True, blank=True)
    google_event_id = models.CharField(max_length=100, blank=True)
    # Settings
    max_attendees = models.PositiveIntegerField(default=0)
    requires_registration = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    # Organizer
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="organized_calendar_events")
    # Status
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_calendar_events"
        ordering = ["start_datetime"]

    def __str__(self):
        return self.title

    def generate_ical(self):
        """Generate iCal format for this event."""
        from django.utils import timezone as tz

        now = tz.now().strftime("%Y%m%dT%H%M%SZ")
        start = self.start_datetime.strftime("%Y%m%dT%H%M%SZ")
        end = self.end_datetime.strftime("%Y%m%dT%H%M%SZ")
        return f"""BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:{self.ical_uid}
DTSTAMP:{now}
DTSTART:{start}
DTEND:{end}
SUMMARY:{self.title}
DESCRIPTION:{self.description}
LOCATION:{self.location}
END:VEVENT
END:VCALENDAR"""


class AlumniCalendarRSVP(models.Model):
    """RSVP for calendar events."""

    class RSVPStatus(models.TextChoices):
        ACCEPTED = "accepted", "Accepted"
        TENTATIVE = "tentative", "Tentative"
        DECLINED = "declined", "Declined"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(AlumniCalendarEvent, on_delete=models.CASCADE, related_name="calendar_rsvps")
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="calendar_rsvps")
    status = models.CharField(max_length=20, choices=RSVPStatus.choices, default=RSVPStatus.ACCEPTED)
    responded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_calendar_rsvps"
        unique_together = [("event", "alumni")]
        ordering = ["-responded_at"]

    def __str__(self):
        return f"{self.alumni} -> {self.event} ({self.get_status_display()})"


class AlumniPhotoAlbum(models.Model):
    """Photo albums for events and memories."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_photo_albums")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event = models.ForeignKey(
        AlumniEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name="photo_albums"
    )
    cover_photo_url = models.URLField(blank=True)
    photo_count = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(AlumniProfile, on_delete=models.SET_NULL, null=True, related_name="created_albums")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_photo_albums"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class AlumniPhoto(models.Model):
    """Individual photos in albums."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    album = models.ForeignKey(AlumniPhotoAlbum, on_delete=models.CASCADE, related_name="photos")
    photo_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    caption = models.CharField(max_length=300, blank=True)
    uploaded_by = models.ForeignKey(AlumniProfile, on_delete=models.SET_NULL, null=True, related_name="uploaded_photos")
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_photos"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.album} - {self.caption or self.id}"


class AlumniPhotoComment(models.Model):
    """Comments on photos."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    photo = models.ForeignKey(AlumniPhoto, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="photo_comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_photo_comments"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author} on {self.photo}"


class AlumniVideoGallery(models.Model):
    """Video gallery for event recordings and testimonials."""

    class VideoType(models.TextChoices):
        EVENT_RECORDING = "event_recording", "Event Recording"
        TESTIMONIAL = "testimonial", "Testimonial"
        INTERVIEW = "interview", "Interview"
        TUTORIAL = "tutorial", "Tutorial"
        HIGHLIGHTS = "highlights", "Highlights"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_videos")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_type = models.CharField(max_length=20, choices=VideoType.choices, default=VideoType.OTHER)
    video_url = models.URLField(help_text="YouTube, Vimeo, or direct URL")
    thumbnail_url = models.URLField(blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    event = models.ForeignKey(AlumniEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name="videos")
    uploaded_by = models.ForeignKey(AlumniProfile, on_delete=models.SET_NULL, null=True, related_name="uploaded_videos")
    is_featured = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_videos"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title

    @property
    def duration_formatted(self):
        """Return duration as HH:MM:SS."""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class AlumniDirectoryFilter(models.Model):
    """Saved directory filters for quick access."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="saved_filters")
    name = models.CharField(max_length=100)
    # Filter criteria
    graduation_year_min = models.PositiveSmallIntegerField(null=True, blank=True)
    graduation_year_max = models.PositiveSmallIntegerField(null=True, blank=True)
    cities = models.JSONField(default=list, blank=True)
    countries = models.JSONField(default=list, blank=True)
    industries = models.JSONField(default=list, blank=True)
    companies = models.JSONField(default=list, blank=True)
    skills = models.JSONField(default=list, blank=True)
    employment_status = models.JSONField(default=list, blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_directory_filters"
        ordering = ["name"]

    def __str__(self):
        return f"{self.alumni} - {self.name}"


class AlumniProfileView(models.Model):
    """Track who viewed whose profile."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    viewer = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="profile_views_made")
    viewed = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="profile_views_received")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_profile_views"
        ordering = ["-viewed_at"]
        indexes = [
            models.Index(fields=["viewer", "viewed"]),
            models.Index(fields=["viewed", "viewed_at"]),
        ]

    def __str__(self):
        return f"{self.viewer} viewed {self.viewed}"


class AlumniProfileCompleteness(models.Model):
    """Track profile completion progress."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumni = models.OneToOneField(AlumniProfile, on_delete=models.CASCADE, related_name="completeness")
    # Completion tracking
    has_photo = models.BooleanField(default=False)
    has_bio = models.BooleanField(default=False)
    has_occupation = models.BooleanField(default=False)
    has_employer = models.BooleanField(default=False)
    has_phone = models.BooleanField(default=False)
    has_address = models.BooleanField(default=False)
    has_linkedin = models.BooleanField(default=False)
    has_skills = models.BooleanField(default=False)
    has_interests = models.BooleanField(default=False)
    has_graduation_year = models.BooleanField(default=False)
    # Calculated
    completion_percentage = models.PositiveSmallIntegerField(default=0)
    last_calculated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_profile_completeness"

    def __str__(self):
        return f"{self.alumni} - {self.completion_percentage}%"

    def calculate_completion(self):
        """Calculate and update completion percentage."""
        fields = [
            self.has_photo,
            self.has_bio,
            self.has_occupation,
            self.has_employer,
            self.has_phone,
            self.has_address,
            self.has_linkedin,
            self.has_skills,
            self.has_interests,
            self.has_graduation_year,
        ]
        completed = sum(1 for f in fields if f)
        self.completion_percentage = int((completed / len(fields)) * 100)
        self.last_calculated_at = timezone.now()
        self.save(update_fields=["completion_percentage", "last_calculated_at"])
        return self.completion_percentage


class AlumniEmailCampaignAnalytics(models.Model):
    """Detailed analytics for email campaigns."""

    class EventType(models.TextChoices):
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        OPENED = "opened", "Opened"
        CLICKED = "clicked", "Clicked"
        BOUNCED = "bounced", "Bounced"
        UNSUBSCRIBED = "unsubscribed", "Unsubscribed"
        SPAM_REPORT = "spam_report", "Spam Report"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    newsletter = models.ForeignKey(AlumniNewsletter, on_delete=models.CASCADE, related_name="analytics_events")
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="email_analytics")
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    link_url = models.URLField(blank=True, help_text="Clicked link URL")
    bounce_reason = models.CharField(max_length=200, blank=True)
    # Timestamps
    event_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_email_campaign_analytics"
        ordering = ["-event_at"]
        indexes = [
            models.Index(fields=["newsletter", "event_type"]),
            models.Index(fields=["alumni", "event_type"]),
        ]

    def __str__(self):
        return f"{self.alumni} - {self.get_event_type_display()} - {self.newsletter}"


class AlumniDonationRecurring(models.Model):
    """Recurring donation management."""

    class Frequency(models.TextChoices):
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        YEARLY = "yearly", "Yearly"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PAUSED = "paused", "Paused"
        CANCELLED = "cancelled", "Cancelled"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="recurring_donations")
    fund_type = models.CharField(
        max_length=20, choices=AlumniDonation.FundType.choices, default=AlumniDonation.FundType.GENERAL
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.MONTHLY)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    # Dates
    start_date = models.DateField()
    next_payment_date = models.DateField(null=True, blank=True)
    last_payment_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # Payment
    payment_method = models.CharField(
        max_length=20, choices=AlumniDonation.PaymentMethod.choices, default=AlumniDonation.PaymentMethod.ONLINE
    )
    payment_token = models.CharField(max_length=200, blank=True, help_text="Payment processor token")
    # Stats
    total_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_payments = models.PositiveIntegerField(default=0)
    failed_payments = models.PositiveIntegerField(default=0)
    # Settings
    is_anonymous = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_donation_recurring"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.alumni} - ${self.amount} {self.get_frequency_display()}"


class AlumniPodcastEpisode(models.Model):
    """Alumni-hosted podcast episodes."""

    class EpisodeType(models.TextChoices):
        INTERVIEW = "interview", "Interview"
        PANEL = "panel", "Panel Discussion"
        SOLO = "solo", "Solo"
        Q_AND_A = "q_and_a", "Q&A"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_podcasts")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    episode_type = models.CharField(max_length=20, choices=EpisodeType.choices, default=EpisodeType.INTERVIEW)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    # Media
    audio_url = models.URLField(help_text="Podcast audio URL")
    thumbnail_url = models.URLField(blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    # Host & Guests
    host = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="hosted_podcasts")
    guests = models.ManyToManyField(AlumniProfile, blank=True, related_name="guest_podcasts")
    # Stats
    play_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    # Metadata
    episode_number = models.PositiveIntegerField(null=True, blank=True)
    season_number = models.PositiveIntegerField(default=1)
    tags = models.JSONField(default=list, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_podcast_episodes"
        ordering = ["-season_number", "-episode_number"]

    def __str__(self):
        return f"S{self.season_number}E{self.episode_number}: {self.title}" if self.episode_number else self.title

    @property
    def duration_formatted(self):
        """Return duration as HH:MM:SS."""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class AlumniPodcastSubscription(models.Model):
    """Alumni subscriptions to podcast updates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="podcast_subscriptions")
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "alumni_podcast_subscriptions"
        unique_together = [("alumni",)]
        ordering = ["-subscribed_at"]

    def __str__(self):
        return f"{self.alumni} subscribed to podcast"


class AlumniAwardCategory(models.Model):
    """Categories for alumni awards program."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_award_categories")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    icon_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_award_categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AlumniAward(models.Model):
    """Annual alumni awards."""

    class Status(models.TextChoices):
        NOMINATIONS_OPEN = "nominations_open", "Nominations Open"
        NOMINATIONS_CLOSED = "nominations_closed", "Nominations Closed"
        JUDGING = "judging", "Judging"
        WINNERS_ANNOUNCED = "winners_announced", "Winners Announced"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_awards")
    category = models.ForeignKey(AlumniAwardCategory, on_delete=models.CASCADE, related_name="awards")
    title = models.CharField(max_length=200)
    description = models.TextField()
    year = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOMINATIONS_OPEN)
    # Dates
    nominations_start = models.DateField()
    nominations_end = models.DateField()
    judging_end = models.DateField(null=True, blank=True)
    announcement_date = models.DateField(null=True, blank=True)
    ceremony_date = models.DateField(null=True, blank=True)
    # Settings
    max_nominations_per_person = models.PositiveSmallIntegerField(default=3)
    requires_nomination_statement = models.BooleanField(default=True)
    # Stats
    total_nominations = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_awards")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumni_awards"
        ordering = ["-year", "-created_at"]

    def __str__(self):
        return f"{self.title} ({self.year})"


class AlumniAwardNomination(models.Model):
    """Nominations for alumni awards."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        WINNER = "winner", "Winner"
        RUNNER_UP = "runner_up", "Runner Up"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    award = models.ForeignKey(AlumniAward, on_delete=models.CASCADE, related_name="nominations")
    nominee = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="award_nominations_received")
    nominated_by = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name="award_nominations_made")
    statement = models.TextField(help_text="Why this person deserves this award")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    # Supporting evidence
    evidence_urls = models.JSONField(default=list, blank=True, help_text="Links to supporting evidence")
    # Results
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    judge_notes = models.TextField(blank=True)
    # Dates
    nominated_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "alumni_award_nominations"
        unique_together = [("award", "nominee", "nominated_by")]
        ordering = ["-nominated_at"]

    def __str__(self):
        return f"{self.nominee} nominated for {self.award} by {self.nominated_by}"
