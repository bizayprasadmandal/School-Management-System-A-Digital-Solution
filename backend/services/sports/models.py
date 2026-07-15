"""Sports & Extracurriculars — Teams, events, achievements, coach assignments."""

import uuid
from django.db import models
from services.auth.models import School, User


class Sport(models.Model):
    """Sports offered (e.g., Basketball, Soccer, Debate, Chess)."""

    class Category(models.TextChoices):
        SPORT = "sport", "Sport"
        ACADEMIC = "academic", "Academic"
        ARTS = "arts", "Arts & Culture"
        CLUB = "club", "Club & Society"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sports")
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.SPORT)
    description = models.TextField(blank=True)
    min_players = models.PositiveSmallIntegerField(default=1)
    max_players = models.PositiveSmallIntegerField(default=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_sports"
        unique_together = [("school", "name")]
        ordering = ["name"]
    def __str__(self):
        return self.name


class Team(models.Model):
    """Teams within a sport (e.g., U-14 Boys, Varsity Girls)."""

    class Gender(models.TextChoices):
        BOYS = "boys", "Boys"
        GIRLS = "girls", "Girls"
        MIXED = "mixed", "Mixed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sports_teams")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=Gender.choices, default=Gender.MIXED)
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="coached_teams")
    assistant_coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assistant_coached_teams")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_teams"
        unique_together = [("school", "sport", "name")]
        ordering = ["sport", "name"]
    def __str__(self):
        return f"{self.sport.name} - {self.name}"


class TeamMember(models.Model):
    """Students assigned to a team with role and status."""

    class Role(models.TextChoices):
        CAPTAIN = "captain", "Captain"
        VICE_CAPTAIN = "vice_captain", "Vice Captain"
        MEMBER = "member", "Member"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        DROPPED = "dropped", "Dropped"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="team_memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    joined_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "sports_team_members"
        unique_together = [("team", "student")]
        ordering = ["team", "student"]
    def __str__(self):
        return f"{self.student} → {self.team}"


class SportEvent(models.Model):
    """Matches, tournaments, competitions, or showcases."""

    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sport_events")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="events")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=50, blank=True, help_text="Match, Tournament, Tryout, etc.")
    opponent = models.CharField(max_length=150, blank=True, help_text="Opposing school/team name")
    location = models.CharField(max_length=200, blank=True)
    event_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    home_score = models.CharField(max_length=30, blank=True)
    opponent_score = models.CharField(max_length=30, blank=True)
    result = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_events"
        ordering = ["-event_date"]
    def __str__(self):
        return f"{self.title} - {self.event_date.date()}"


class SportAchievement(models.Model):
    """Individual or team achievements, awards, recognitions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sport_achievements")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, null=True, blank=True, related_name="sport_achievements")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="achievements")
    event = models.ForeignKey(SportEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name="achievements")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    position = models.CharField(max_length=50, blank=True, help_text="1st Place, Best Player, etc.")
    level = models.CharField(max_length=50, blank=True, help_text="School, District, State, National, International")
    awarded_date = models.DateField()
    certificate_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_achievements"
        ordering = ["-awarded_date"]
    def __str__(self):
        return self.title
