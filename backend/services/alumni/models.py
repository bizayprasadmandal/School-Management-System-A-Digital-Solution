"""Alumni Management — Profiles, events, donations, chapters."""

import uuid
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
    employment_status = models.CharField(max_length=20, choices=EmploymentStatus.choices, default=EmploymentStatus.EMPLOYED)
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
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="organized_alumni_events")
    cover_image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_events"
        ordering = ["-event_date"]
    def __str__(self):
        return self.title


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
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_donations"
        ordering = ["-donation_date"]
    def __str__(self):
        return f"{self.alumni} - ${self.amount}"


class AlumniChapter(models.Model):
    """Regional alumni chapters/groups."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="alumni_chapters")
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    president = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="presided_chapters")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "alumni_chapters"
        unique_together = [("school", "name")]
        ordering = ["name"]
    def __str__(self):
        return self.name
