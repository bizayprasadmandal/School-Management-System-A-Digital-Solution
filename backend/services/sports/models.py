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
    assistant_coach = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assistant_coached_teams"
    )
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
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, null=True, blank=True, related_name="sport_achievements"
    )
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


class SportsRegistration(models.Model):
    """Online registration for players/teams."""

    class RegistrationType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual"
        TEAM = "team", "Team"
        SEASON = "season", "Season"
        TRYOUT = "tryout", "Tryout"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        WAITLISTED = "waitlisted", "Waitlisted"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sports_registrations")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="sports_registrations")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="registrations")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="registrations")
    registration_type = models.CharField(
        max_length=15, choices=RegistrationType.choices, default=RegistrationType.INDIVIDUAL
    )
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Season info
    season = models.CharField(max_length=50, blank=True, help_text="e.g., Fall 2025, Spring 2026")
    academic_year = models.CharField(max_length=20, blank=True)
    # Payment
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=15,
        choices=[("unpaid", "Unpaid"), ("paid", "Paid"), ("waived", "Waived"), ("refunded", "Refunded")],
        default="unpaid",
    )
    payment_date = models.DateField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    # Medical
    medical_clearance = models.BooleanField(default=False)
    emergency_contact = models.CharField(max_length=150, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    # Forms
    consent_form_signed = models.BooleanField(default=False)
    physical_exam_date = models.DateField(null=True, blank=True)
    physical_exam_expiry = models.DateField(null=True, blank=True)
    # Parent/Guardian
    parent_name = models.CharField(max_length=150, blank=True)
    parent_email = models.EmailField(blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    parent_consent = models.BooleanField(default=False)
    # Notes
    notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_registrations"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_registrations"
        ordering = ["-registered_at"]

    def __str__(self):
        return f"{self.student} - {self.sport} ({self.get_status_display()})"


class PracticeSchedule(models.Model):
    """Practice sessions and training schedules."""

    class DayOfWeek(models.TextChoices):
        MONDAY = "monday", "Monday"
        TUESDAY = "tuesday", "Tuesday"
        WEDNESDAY = "wednesday", "Wednesday"
        THURSDAY = "thursday", "Thursday"
        FRIDAY = "friday", "Friday"
        SATURDAY = "saturday", "Saturday"
        SUNDAY = "sunday", "Sunday"

    class PracticeType(models.TextChoices):
        REGULAR = "regular", "Regular Practice"
        CONDITIONING = "conditioning", "Conditioning"
        SCRIMMAGE = "scrimmage", "Scrimmage"
        FILM = "film", "Film Session"
        MEETING = "meeting", "Team Meeting"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="practice_schedules")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="practices")
    practice_type = models.CharField(max_length=15, choices=PracticeType.choices, default=PracticeType.REGULAR)
    # Schedule
    day_of_week = models.CharField(max_length=10, choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    # Location
    location = models.CharField(max_length=200, blank=True)
    field_court = models.CharField(max_length=100, blank=True)
    # Recurring
    is_recurring = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # Attendance
    required = models.BooleanField(default=True)
    min_attendance = models.PositiveSmallIntegerField(default=0, help_text="Minimum attendance required")
    # Coach
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="coached_practices")
    # Notes
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "practice_schedules"
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.team} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class SportsAttendance(models.Model):
    """Track player attendance at practices and games."""

    class AttendanceStatus(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        TARDY = "tardy", "Late"
        EXCUSED = "excused", "Excused"
        INJURED = "injured", "Injured"

    class SessionType(models.TextChoices):
        PRACTICE = "practice", "Practice"
        GAME = "game", "Game"
        TRYOUT = "tryout", "Tryout"
        CONDITIONING = "conditioning", "Conditioning"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="sports_attendance")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="attendance_records")
    session_type = models.CharField(max_length=15, choices=SessionType.choices, default=SessionType.PRACTICE)
    # Reference
    practice = models.ForeignKey(
        PracticeSchedule, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance"
    )
    event = models.ForeignKey(SportEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance")
    # Status
    status = models.CharField(max_length=10, choices=AttendanceStatus.choices, default=AttendanceStatus.PRESENT)
    minutes_late = models.PositiveSmallIntegerField(default=0)
    # Date
    date = models.DateField()
    # Notes
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    # Recorded by
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="recorded_sports_attendance"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_attendance"
        unique_together = [("student", "team", "date", "session_type")]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student} - {self.team} ({self.get_status_display()}) on {self.date}"


class PlayerStatistics(models.Model):
    """Detailed player performance statistics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="player_statistics")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="player_statistics")
    event = models.ForeignKey(
        SportEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name="player_statistics"
    )
    # Game stats
    games_played = models.PositiveSmallIntegerField(default=0)
    games_started = models.PositiveSmallIntegerField(default=0)
    minutes_played = models.PositiveIntegerField(default=0)
    # Sport-specific stats (flexible JSON)
    stats = models.JSONField(default=dict, blank=True, help_text="Sport-specific statistics")
    # Common stats
    goals = models.PositiveSmallIntegerField(default=0)
    assists = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveSmallIntegerField(default=0)
    rebounds = models.PositiveSmallIntegerField(default=0)
    steals = models.PositiveSmallIntegerField(default=0)
    blocks = models.PositiveSmallIntegerField(default=0)
    turnovers = models.PositiveSmallIntegerField(default=0)
    fouls = models.PositiveSmallIntegerField(default=0)
    # Performance
    rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    # Season
    season = models.CharField(max_length=50, blank=True)
    academic_year = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "player_statistics"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.team} stats"


class TeamRoster(models.Model):
    """Official team rosters with jersey numbers."""

    class RosterType(models.TextChoices):
        VARSITY = "varsity", "Varsity"
        JV = "jv", "Junior Varsity"
        FRESHMAN = "freshman", "Freshman"
        CLUB = "club", "Club"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="rosters")
    roster_type = models.CharField(max_length=10, choices=RosterType.choices, default=RosterType.VARSITY)
    season = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)
    # Roster data
    roster_data = models.JSONField(default=list, blank=True, help_text="List of players with jersey numbers")
    # Stats
    total_players = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    # Settings
    max_roster_size = models.PositiveSmallIntegerField(default=25)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_rosters"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "team_rosters"
        unique_together = [("team", "roster_type", "season")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.team} - {self.get_roster_type_display()} ({self.season})"


class InjuryTracking(models.Model):
    """Track player injuries and recovery."""

    class InjuryType(models.TextChoices):
        SPRRAIN = "sprain", "Sprain"
        STRAIN = "strain", "Strain"
        FRACTURE = "fracture", "Fracture"
        CONCUSSION = "concussion", "Concussion"
        BRUISE = "bruise", "Bruise"
        CUT = "cut", "Cut/Laceration"
        OTHER = "other", "Other"

    class Severity(models.TextChoices):
        MINOR = "minor", "Minor"
        MODERATE = "moderate", "Moderate"
        SEVERE = "severe", "Severe"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RECOVERING = "recovering", "Recovering"
        CLEARED = "cleared", "Cleared"
        CHRONIC = "chronic", "Chronic"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sports_injuries")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="injuries")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="injuries")
    # Injury details
    injury_type = models.CharField(max_length=15, choices=InjuryType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.MODERATE)
    body_part = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    # Dates
    injury_date = models.DateField()
    reported_date = models.DateField(auto_now_add=True)
    expected_return = models.DateField(null=True, blank=True)
    actual_return = models.DateField(null=True, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Treatment
    treatment_notes = models.TextField(blank=True)
    doctor_name = models.CharField(max_length=150, blank=True)
    doctor_contact = models.CharField(max_length=100, blank=True)
    # Activity restriction
    activity_restriction = models.TextField(blank=True, help_text="Restricted activities")
    return_to_play_protocol = models.TextField(blank=True)
    # Cleared by
    cleared_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="cleared_injuries"
    )
    cleared_date = models.DateField(null=True, blank=True)
    # Documentation
    medical_report_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_injuries"
        ordering = ["-injury_date"]

    def __str__(self):
        return f"{self.student} - {self.get_injury_type_display()} ({self.get_status_display()})"


class EquipmentInventory(models.Model):
    """Track team equipment inventory."""

    class EquipmentType(models.TextChoices):
        BALL = "ball", "Ball"
        UNIFORM = "uniform", "Uniform"
        PROTECTIVE = "protective", "Protective Gear"
        TRAINING = "training", "Training Equipment"
        MAINTENANCE = "maintenance", "Maintenance"
        OTHER = "other", "Other"

    class Condition(models.TextChoices):
        NEW = "new", "New"
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        POOR = "poor", "Poor"
        RETIRED = "retired", "Retired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="equipment_inventory")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="equipment")
    # Equipment info
    name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=15, choices=EquipmentType.choices)
    description = models.TextField(blank=True)
    # Inventory
    quantity = models.PositiveIntegerField(default=1)
    condition = models.CharField(max_length=10, choices=Condition.choices, default=Condition.GOOD)
    # Purchase info
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vendor = models.CharField(max_length=150, blank=True)
    # Maintenance
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    maintenance_notes = models.TextField(blank=True)
    # Location
    storage_location = models.CharField(max_length=100, blank=True)
    # Status
    is_available = models.BooleanField(default=True)
    assigned_to = models.ForeignKey(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_equipment"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "equipment_inventory"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (x{self.quantity})"


class GameLineup(models.Model):
    """Starting lineups and substitutions."""

    class LineupType(models.TextChoices):
        STARTING = "starting", "Starting"
        BENCH = "bench", "Bench"
        SUBSTITUTE = "substitute", "Substitute"
        INJURED = "injured", "Injured"
        SCRATCHED = "scratched", "Scratched"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(SportEvent, on_delete=models.CASCADE, related_name="lineups")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="game_lineups")
    lineup_type = models.CharField(max_length=15, choices=LineupType.choices, default=LineupType.STARTING)
    # Position
    position = models.CharField(max_length=50, blank=True)
    jersey_number = models.PositiveSmallIntegerField(null=True, blank=True)
    # Substitution
    subbed_in_at = models.TimeField(null=True, blank=True)
    subbed_out_at = models.TimeField(null=True, blank=True)
    substitution_reason = models.CharField(max_length=100, blank=True)
    # Performance
    minutes_played = models.PositiveSmallIntegerField(default=0)
    stats_snapshot = models.JSONField(default=dict, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "game_lineups"
        ordering = ["lineup_type", "position"]

    def __str__(self):
        return f"{self.student} - {self.event} ({self.get_lineup_type_display()})"


class LeagueStanding(models.Model):
    """League tables and rankings."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="league_standings")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="league_standings")
    # League info
    league_name = models.CharField(max_length=200)
    season = models.CharField(max_length=50)
    division = models.CharField(max_length=100, blank=True)
    # Team
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="league_standings")
    # Standings
    games_played = models.PositiveSmallIntegerField(default=0)
    wins = models.PositiveSmallIntegerField(default=0)
    losses = models.PositiveSmallIntegerField(default=0)
    ties = models.PositiveSmallIntegerField(default=0)
    points_for = models.PositiveIntegerField(default=0)
    points_against = models.PositiveIntegerField(default=0)
    # Ranking
    rank = models.PositiveSmallIntegerField(default=0)
    streak = models.CharField(max_length=20, blank=True, help_text="e.g., W3, L1")
    last_5 = models.CharField(max_length=20, blank=True, help_text="Last 5 games: W3-L2")
    # Notes
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "league_standings"
        unique_together = [("league_name", "team", "season")]
        ordering = ["rank"]

    def __str__(self):
        return f"{self.team} - {self.league_name} (Rank: {self.rank})"

    @property
    def win_percentage(self):
        if self.games_played > 0:
            return round(self.wins / self.games_played * 100, 1)
        return 0

    @property
    def point_differential(self):
        return self.points_for - self.points_against


class SportsMedicalClearance(models.Model):
    """Medical forms and clearances."""

    class ClearanceType(models.TextChoices):
        PHYSICAL = "physical", "Physical Examination"
        CONCUSSION = "concussion", "Concussion Protocol"
        CARDIAC = "cardiac", "Cardiac Screening"
        ALLERGY = "allergy", "Allergy Action Plan"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        EXPIRED = "expired", "Expired"
        DENIED = "denied", "Denied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sports_medical_clearances")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="medical_clearances")
    clearance_type = models.CharField(max_length=15, choices=ClearanceType.choices, default=ClearanceType.PHYSICAL)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Medical info
    physician_name = models.CharField(max_length=150)
    physician_contact = models.CharField(max_length=100, blank=True)
    exam_date = models.DateField()
    expiry_date = models.DateField()
    # Documents
    document_url = models.URLField(blank=True)
    # Restrictions
    restrictions = models.TextField(blank=True, help_text="Medical restrictions")
    cleared_for = models.TextField(blank=True, help_text="Cleared for which activities")
    # Review
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_clearances"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_medical_clearances"
        ordering = ["-exam_date"]

    def __str__(self):
        return f"{self.student} - {self.get_clearance_type_display()} ({self.get_status_display()})"

    @property
    def is_valid(self):
        from django.utils import timezone

        return self.status == self.Status.APPROVED and self.expiry_date >= timezone.now().date()


class TeamCommunication(models.Model):
    """Team chat and announcements."""

    class MessageType(models.TextChoices):
        ANNOUNCEMENT = "announcement", "Announcement"
        MESSAGE = "message", "Message"
        REMINDER = "reminder", "Reminder"
        ALERT = "alert", "Alert"

    class TargetAudience(models.TextChoices):
        ALL = "all", "All Members"
        PLAYERS = "players", "Players Only"
        COACHES = "coaches", "Coaches Only"
        PARENTS = "parents", "Parents Only"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="communications")
    message_type = models.CharField(max_length=15, choices=MessageType.choices, default=MessageType.MESSAGE)
    target_audience = models.CharField(max_length=10, choices=TargetAudience.choices, default=TargetAudience.ALL)
    # Message
    subject = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    # Sender
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sent_team_communications")
    # Attachments
    attachment_url = models.URLField(blank=True)
    # Delivery
    is_pinned = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    read_by = models.JSONField(default=list, blank=True)
    # Schedule
    send_immediately = models.BooleanField(default=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "team_communications"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.team} - {self.get_message_type_display()}: {self.content[:50]}"


class SportsPhotoGallery(models.Model):
    """Team photos and game highlights."""

    class PhotoType(models.TextChoices):
        TEAM = "team", "Team Photo"
        GAME = "game", "Game Photo"
        PRACTICE = "practice", "Practice Photo"
        AWARD = "award", "Award Photo"
        EVENT = "event", "Event Photo"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="photo_galleries")
    photo_type = models.CharField(max_length=10, choices=PhotoType.choices, default=PhotoType.TEAM)
    # Photo
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    photo_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    # Metadata
    photographer = models.CharField(max_length=150, blank=True)
    event = models.ForeignKey(SportEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name="photos")
    taken_date = models.DateField(auto_now_add=True)
    # Tags
    tags = models.JSONField(default=list, blank=True)
    # Stats
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    # Settings
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploaded_sports_photos"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_photo_galleries"
        ordering = ["-taken_date"]

    def __str__(self):
        return f"{self.team} - {self.title}"


class SportsFundraising(models.Model):
    """Team fundraising campaigns."""

    class CampaignType(models.TextChoices):
        EQUIPMENT = "equipment", "Equipment"
        TRAVEL = "travel", "Travel"
        FEES = "fees", "Player Fees"
        FACILITY = "facility", "Facility"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="fundraising")
    campaign_type = models.CharField(max_length=15, choices=CampaignType.choices, default=CampaignType.OTHER)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PLANNING)
    # Campaign info
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    # Donations
    donor_count = models.PositiveIntegerField(default=0)
    average_donation = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Settings
    is_online = models.BooleanField(default=True)
    online_donation_url = models.URLField(blank=True)
    # Created by
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="created_sports_fundraising"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_fundraising"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.team} - {self.title}"

    @property
    def progress_percentage(self):
        if self.goal_amount > 0:
            return round(self.raised_amount / self.goal_amount * 100, 1)
        return 0


class SportsSponsorship(models.Model):
    """Track team sponsors."""

    class SponsorshipLevel(models.TextChoices):
        PLATINUM = "platinum", "Platinum"
        GOLD = "gold", "Gold"
        SILVER = "silver", "Silver"
        BRONZE = "bronze", "Bronze"
        CUSTOM = "custom", "Custom"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        RENEWED = "renewed", "Renewed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="sponsorships")
    # Sponsor info
    sponsor_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=150, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    # Sponsorship details
    sponsorship_level = models.CharField(
        max_length=10, choices=SponsorshipLevel.choices, default=SponsorshipLevel.CUSTOM
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    in_kind_value = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, help_text="Value of in-kind donations"
    )
    # Duration
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    # Benefits
    logo_on_jersey = models.BooleanField(default=False)
    banner_at_field = models.BooleanField(default=False)
    mention_in_programs = models.BooleanField(default=False)
    social_media_recognition = models.BooleanField(default=False)
    other_benefits = models.TextField(blank=True)
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_sponsorships"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.sponsor_name} - {self.team} ({self.get_sponsorship_level_display()})"

    @property
    def total_value(self):
        return self.amount + self.in_kind_value


class SportsTravelManagement(models.Model):
    """Away game travel arrangements."""

    class TravelType(models.TextChoices):
        BUS = "bus", "Bus"
        VAN = "van", "Van"
        CARPOOL = "carpool", "Carpool"
        FLIGHT = "flight", "Flight"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PLANNED = "planned", "Planned"
        CONFIRMED = "confirmed", "Confirmed"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="travel_arrangements")
    event = models.ForeignKey(SportEvent, on_delete=models.CASCADE, related_name="travel")
    # Travel info
    travel_type = models.CharField(max_length=10, choices=TravelType.choices, default=TravelType.BUS)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PLANNED)
    # Schedule
    departure_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    # Transportation
    vehicle_info = models.CharField(max_length=200, blank=True)
    driver_name = models.CharField(max_length=150, blank=True)
    driver_contact = models.CharField(max_length=20, blank=True)
    # Accommodation
    hotel_name = models.CharField(max_length=200, blank=True)
    hotel_address = models.TextField(blank=True)
    hotel_confirmation = models.CharField(max_length=100, blank=True)
    # Meals
    meal_plan = models.TextField(blank=True)
    # Cost
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Travelers
    travelers = models.JSONField(default=list, blank=True)
    # Documents
    itinerary_url = models.URLField(blank=True)
    emergency_contact = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_travel_management"
        ordering = ["-departure_date"]

    def __str__(self):
        return f"{self.team} - {self.event.title} ({self.get_travel_type_display()})"


class SportsUniformOrder(models.Model):
    """Uniform sizing and orders."""

    class OrderStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SIZING = "sizing", "Sizing"
        ORDERED = "ordered", "Ordered"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="uniform_orders")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="uniform_orders")
    # Uniform info
    uniform_type = models.CharField(max_length=100, help_text="Jersey, Shorts, etc.")
    size = models.CharField(max_length=20)
    jersey_number = models.PositiveSmallIntegerField(null=True, blank=True)
    # Order
    status = models.CharField(max_length=15, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    quantity = models.PositiveSmallIntegerField(default=1)
    cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=15, choices=[("unpaid", "Unpaid"), ("paid", "Paid")], default="unpaid")
    # Delivery
    ordered_date = models.DateField(null=True, blank=True)
    expected_delivery = models.DateField(null=True, blank=True)
    delivered_date = models.DateField(null=True, blank=True)
    # Vendor
    vendor = models.CharField(max_length=150, blank=True)
    order_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_uniform_orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.uniform_type} ({self.size})"


class SportsVolunteerManagement(models.Model):
    """Parent volunteers and assignments."""

    class VolunteerType(models.TextChoices):
        COACH = "coach", "Coach"
        ASSISTANT = "assistant", "Assistant Coach"
        SCOREKEEPER = "scorekeeper", "Scorekeeper"
        TIMER = "timer", "Timer"
        CHAPERONE = "chaperone", "Chaperone"
        FUNDRAISER = "fundraiser", "Fundraiser"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        INTERESTED = "interested", "Interested"
        APPROVED = "approved", "Approved"
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="volunteers")
    # Volunteer info
    parent_name = models.CharField(max_length=150)
    parent_email = models.EmailField()
    parent_phone = models.CharField(max_length=20)
    student = models.ForeignKey(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="parent_volunteers"
    )
    volunteer_type = models.CharField(max_length=15, choices=VolunteerType.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.INTERESTED)
    # Availability
    availability = models.JSONField(default=list, blank=True, help_text="Available days/times")
    # Background check
    background_check_complete = models.BooleanField(default=False)
    background_check_date = models.DateField(null=True, blank=True)
    # Hours
    total_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Notes
    skills = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_volunteer_management"
        ordering = ["team", "parent_name"]

    def __str__(self):
        return f"{self.parent_name} - {self.team} ({self.get_volunteer_type_display()})"


class SportsAnalytics(models.Model):
    """Performance analytics dashboards."""

    class AnalyticsType(models.TextChoices):
        TEAM_PERFORMANCE = "team_performance", "Team Performance"
        PLAYER_STATS = "player_stats", "Player Statistics"
        WIN_LOSS = "win_loss", "Win/Loss Analysis"
        SCORING_TRENDS = "scoring_trends", "Scoring Trends"
        ATTENDANCE = "attendance", "Attendance Analytics"
        INJURY = "injury", "Injury Analytics"
        OPPONENT = "opponent", "Opponent Analysis"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="analytics")
    analytics_type = models.CharField(max_length=20, choices=AnalyticsType.choices)
    title = models.CharField(max_length=200)
    # Date range
    start_date = models.DateField()
    end_date = models.DateField()
    # Data
    analytics_data = models.JSONField(default=dict, blank=True)
    insights = models.JSONField(default=list, blank=True)
    recommendations = models.TextField(blank=True)
    # Visualization
    chart_type = models.CharField(max_length=50, blank=True)
    chart_data = models.JSONField(default=dict, blank=True)
    # Stats summary
    key_metrics = models.JSONField(default=dict, blank=True)
    # Settings
    is_shared = models.BooleanField(default=False)
    generated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="generated_sports_analytics"
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_analytics"
        ordering = ["-generated_at"]

    def __str__(self):
        return f"{self.team} - {self.get_analytics_type_display()}: {self.title}"


class RefereeManagement(models.Model):
    """Track referees/umpires and their assignments."""

    class RefereeType(models.TextChoices):
        REFEREE = "referee", "Referee"
        UMPIRE = "umpire", "Umpire"
        LINE_JUDGE = "line_judge", "Line Judge"
        OFFICIAL = "official", "Official"
        OTHER = "other", "Other"

    class CertificationLevel(models.TextChoices):
        ENTRY = "entry", "Entry Level"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
        ELITE = "elite", "Elite"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPENDED = "suspended", "Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="referees")
    # Personal info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    # Certification
    referee_type = models.CharField(max_length=15, choices=RefereeType.choices)
    certification_level = models.CharField(
        max_length=15, choices=CertificationLevel.choices, default=CertificationLevel.ENTRY
    )
    certification_number = models.CharField(max_length=50, blank=True)
    certification_expiry = models.DateField(null=True, blank=True)
    # Availability
    availability = models.JSONField(default=list, blank=True)
    # Stats
    games_officiated = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_referees"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_referee_type_display()})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class RefereeAssignment(models.Model):
    """Assign referees to games/events."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        DECLINED = "declined", "Declined"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referee = models.ForeignKey(RefereeManagement, on_delete=models.CASCADE, related_name="assignments")
    event = models.ForeignKey(SportEvent, on_delete=models.CASCADE, related_name="referee_assignments")
    # Assignment details
    role = models.CharField(max_length=50, blank=True, help_text="Head Referee, Line Judge, etc.")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Payment
    fee_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=15, choices=[("unpaid", "Unpaid"), ("paid", "Paid")], default="unpaid")
    # Performance
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    comments = models.TextField(blank=True)
    # Notes
    notes = models.TextField(blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_referee_assignments"
        ordering = ["-assigned_at"]

    def __str__(self):
        return f"{self.referee} - {self.event} ({self.get_status_display()})"


class FacilityBooking(models.Model):
    """Book fields, courts, gymnasiums."""

    class FacilityType(models.TextChoices):
        FIELD = "field", "Field"
        COURT = "court", "Court"
        GYM = "gym", "Gymnasium"
        POOL = "pool", "Swimming Pool"
        TRACK = "track", "Track"
        OTHER = "other", "Other"

    class BookingStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="facility_bookings")
    # Facility info
    facility_name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=10, choices=FacilityType.choices)
    location = models.CharField(max_length=200, blank=True)
    # Booking
    booked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="facility_bookings")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="facility_bookings")
    event = models.ForeignKey(
        SportEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name="facility_bookings"
    )
    # Schedule
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=50, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    # Cost
    rental_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=15, choices=[("unpaid", "Unpaid"), ("paid", "Paid")], default="unpaid")
    # Equipment
    equipment_needed = models.JSONField(default=list, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_facility_bookings"
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.facility_name} - {self.date} ({self.start_time}-{self.end_time})"

    @property
    def duration_hours(self):
        from datetime import datetime

        start = datetime.combine(self.date, self.start_time)
        end = datetime.combine(self.date, self.end_time)
        return (end - start).total_seconds() / 3600


class LiveGameScore(models.Model):
    """Real-time score updates for games."""

    class ScoreStatus(models.TextChoices):
        PRE_GAME = "pre_game", "Pre-Game"
        LIVE = "live", "Live"
        HALFTIME = "halftime", "Halftime"
        FINAL = "final", "Final"
        POSTPONED = "postponed", "Postponed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.OneToOneField(SportEvent, on_delete=models.CASCADE, related_name="live_score")
    # Score
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    # Period
    current_period = models.CharField(max_length=50, blank=True, help_text="Q1, Q2, Half, Final, etc.")
    period_time = models.CharField(max_length=20, blank=True, help_text="Time remaining in period")
    # Status
    status = models.CharField(max_length=15, choices=ScoreStatus.choices, default=ScoreStatus.PRE_GAME)
    # Stats
    possession = models.CharField(max_length=50, blank=True)
    shots_on_target = models.JSONField(default=dict, blank=True)
    # Updates
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="score_updates")
    # Commentary
    commentary = models.JSONField(default=list, blank=True)
    # Settings
    is_public = models.BooleanField(default=True)
    auto_update = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_live_scores"

    def __str__(self):
        return f"{self.event} - {self.home_score} : {self.away_score} ({self.get_status_display()})"

    @property
    def score_diff(self):
        return abs(self.home_score - self.away_score)


class VideoAnalysis(models.Model):
    """Upload and analyze game film."""

    class VideoType(models.TextChoices):
        GAME = "game", "Game Film"
        PRACTICE = "practice", "Practice Film"
        HIGHLIGHT = "highlight", "Highlights"
        BREAKDOWN = "breakdown", "Breakdown"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        UPLOADING = "uploading", "Uploading"
        PROCESSING = "processing", "Processing"
        READY = "ready", "Ready"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sports_videos")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="videos")
    event = models.ForeignKey(SportEvent, on_delete=models.SET_NULL, null=True, blank=True, related_name="videos")
    # Video info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_type = models.CharField(max_length=15, choices=VideoType.choices)
    # File
    video_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    file_size_mb = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Analysis
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.UPLOADING)
    analysis_notes = models.JSONField(default=list, blank=True)
    key_moments = models.JSONField(default=list, blank=True)
    # Tags
    tags = models.JSONField(default=list, blank=True)
    # Access
    is_public = models.BooleanField(default=False)
    shared_with = models.JSONField(default=list, blank=True)
    # Upload info
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="uploaded_sports_videos"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_videos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.team} - {self.title}"

    @property
    def duration_formatted(self):
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"


class WearableIntegration(models.Model):
    """Sync with fitness trackers and wearables."""

    class DeviceType(models.TextChoices):
        APPLE_WATCH = "apple_watch", "Apple Watch"
        FITBIT = "fitbit", "Fitbit"
        GARMIN = "garmin", "Garmin"
        WHOOP = "whoop", "Whoop"
        CATAPULT = "catapult", "Catapult"
        OTHER = "other", "Other"

    class SyncStatus(models.TextChoices):
        CONNECTED = "connected", "Connected"
        DISCONNECTED = "disconnected", "Disconnected"
        SYNCING = "syncing", "Syncing"
        ERROR = "error", "Error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="wearable_devices")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="wearable_devices")
    # Device info
    device_type = models.CharField(max_length=15, choices=DeviceType.choices)
    device_id = models.CharField(max_length=100, blank=True)
    # Sync
    sync_status = models.CharField(max_length=15, choices=SyncStatus.choices, default=SyncStatus.DISCONNECTED)
    last_sync = models.DateTimeField(null=True, blank=True)
    # Data
    heart_rate_data = models.JSONField(default=list, blank=True)
    gps_data = models.JSONField(default=list, blank=True)
    activity_data = models.JSONField(default=dict, blank=True)
    sleep_data = models.JSONField(default=list, blank=True)
    # Settings
    auto_sync = models.BooleanField(default=True)
    share_with_coach = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_wearable_devices"
        unique_together = [("student", "device_type")]
        ordering = ["-last_sync"]

    def __str__(self):
        return f"{self.student} - {self.get_device_type_display()}"


class PlayerDevelopmentPlan(models.Model):
    """Long-term athlete development tracking."""

    class DevelopmentPhase(models.TextChoices):
        FUNDAMENTALS = "fundamentals", "Fundamentals"
        SKILL_DEVELOPMENT = "skill_development", "Skill Development"
        COMPETITIVE = "competitive", "Competitive"
        ELITE = "elite", "Elite"
        MAINTENANCE = "maintenance", "Maintenance"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        ON_HOLD = "on_hold", "On Hold"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="development_plans")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="development_plans")
    # Plan info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    phase = models.CharField(max_length=20, choices=DevelopmentPhase.choices)
    # Goals
    short_term_goals = models.JSONField(default=list, blank=True)
    long_term_goals = models.JSONField(default=list, blank=True)
    # Metrics
    baseline_metrics = models.JSONField(default=dict, blank=True)
    current_metrics = models.JSONField(default=dict, blank=True)
    target_metrics = models.JSONField(default=dict, blank=True)
    # Progress
    progress_percentage = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Dates
    start_date = models.DateField()
    target_date = models.DateField(null=True, blank=True)
    review_date = models.DateField(null=True, blank=True)
    # Coach
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_development_plans"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_development_plans"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.title}"


class TryoutAssessment(models.Model):
    """Digital tryouts with scoring rubrics."""

    class TryoutStatus(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class SelectionStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SELECTED = "selected", "Selected"
        ALTERNATE = "alternate", "Alternate"
        NOT_SELECTED = "not_selected", "Not Selected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="tryouts")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="tryouts")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tryouts")
    # Tryout info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tryout_date = models.DateField()
    location = models.CharField(max_length=200, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=TryoutStatus.choices, default=TryoutStatus.SCHEDULED)
    # Scoring
    max_score = models.PositiveSmallIntegerField(default=100)
    passing_score = models.PositiveSmallIntegerField(default=60)
    # Settings
    max_participants = models.PositiveSmallIntegerField(default=50)
    current_participants = models.PositiveSmallIntegerField(default=0)
    # Created by
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_tryouts"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_tryouts"
        ordering = ["-tryout_date"]

    def __str__(self):
        return f"{self.team} - {self.title} ({self.tryout_date})"


class TryoutScore(models.Model):
    """Individual scores from tryouts."""

    class SelectionStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SELECTED = "selected", "Selected"
        ALTERNATE = "alternate", "Alternate"
        NOT_SELECTED = "not_selected", "Not Selected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tryout = models.ForeignKey(TryoutAssessment, on_delete=models.CASCADE, related_name="scores")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="tryout_scores")
    # Scores
    total_score = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    category_scores = models.JSONField(default=dict, blank=True)
    # Selection
    selection_status = models.CharField(max_length=15, choices=SelectionStatus.choices, default=SelectionStatus.PENDING)
    # Notes
    evaluator_notes = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    areas_for_improvement = models.TextField(blank=True)
    # Evaluator
    evaluated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tryout_evaluations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_tryout_scores"
        unique_together = [("tryout", "student")]
        ordering = ["-total_score"]

    def __str__(self):
        return f"{self.student} - {self.tryout} (Score: {self.total_score})"


class SeasonPassMembership(models.Model):
    """Season-based memberships with auto-renewal."""

    class MembershipType(models.TextChoices):
        PLAYER = "player", "Player"
        FAMILY = "family", "Family"
        COACH = "coach", "Coach"
        SUPPORTER = "supporter", "Supporter"
        LIFETIME = "lifetime", "Lifetime"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"
        SUSPENDED = "suspended", "Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="season_passes")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="season_passes")
    # Membership info
    membership_type = models.CharField(max_length=10, choices=MembershipType.choices)
    season = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)
    # Pricing
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    # Auto-renewal
    auto_renew = models.BooleanField(default=False)
    renewal_date = models.DateField(null=True, blank=True)
    # Payment
    payment_status = models.CharField(
        max_length=15,
        choices=[("unpaid", "Unpaid"), ("paid", "Paid"), ("refunded", "Refunded")],
        default="unpaid",
    )
    transaction_id = models.CharField(max_length=100, blank=True)
    # Benefits
    benefits = models.JSONField(default=list, blank=True)
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_season_passes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} - {self.get_membership_type_display()} ({self.season})"

    @property
    def is_valid(self):
        from django.utils import timezone

        return self.status == self.Status.ACTIVE and self.end_date >= timezone.now().date()


class MultiSportScheduling(models.Model):
    """Prevent conflicts across multiple sports."""

    class ConflictType(models.TextChoices):
        VENUE = "venue", "Venue Conflict"
        PLAYER = "player", "Player Conflict"
        COACH = "coach", "Coach Conflict"
        FACILITY = "facility", "Facility Conflict"
        OTHER = "other", "Other Conflict"

    class Status(models.TextChoices):
        DETECTED = "detected", "Detected"
        RESOLVED = "resolved", "Resolved"
        IGNORED = "ignored", "Ignored"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="schedule_conflicts")
    # Conflicting events
    event_1 = models.ForeignKey(SportEvent, on_delete=models.CASCADE, related_name="conflicts_as_event1")
    event_2 = models.ForeignKey(SportEvent, on_delete=models.CASCADE, related_name="conflicts_as_event2")
    # Conflict info
    conflict_type = models.CharField(max_length=10, choices=ConflictType.choices)
    description = models.TextField(blank=True)
    # Resolution
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DETECTED)
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_conflicts"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_schedule_conflicts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Conflict: {self.event_1} vs {self.event_2} ({self.get_conflict_type_display()})"


class RefundManagement(models.Model):
    """Process refunds with policies."""

    class RefundReason(models.TextChoices):
        INJURY = "injury", "Injury"
        SCHEDULE = "schedule", "Schedule Conflict"
        DISSATISFACTION = "dissatisfaction", "Dissatisfaction"
        DUPLICATE = "duplicate", "Duplicate Payment"
        OTHER = "other", "Other"

    class RefundStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        PROCESSED = "processed", "Processed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sports_refunds")
    # Request info
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="refund_requests")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="refund_requests")
    # Original payment
    registration = models.ForeignKey(
        SportsRegistration, on_delete=models.SET_NULL, null=True, blank=True, related_name="refunds"
    )
    original_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Refund details
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_reason = models.CharField(max_length=15, choices=RefundReason.choices)
    reason_details = models.TextField(blank=True)
    # Status
    status = models.CharField(max_length=15, choices=RefundStatus.choices, default=RefundStatus.PENDING)
    # Approval
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_refunds"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approval_notes = models.TextField(blank=True)
    # Processing
    processed_at = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    # Policy
    within_policy = models.BooleanField(default=True)
    policy_exception = models.BooleanField(default=False)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_refunds"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Refund: {self.student} - ${self.refund_amount} ({self.get_status_display()})"

    @property
    def refund_percentage(self):
        if self.original_amount > 0:
            return round(self.refund_amount / self.original_amount * 100, 1)
        return 0


class ComplianceTracking(models.Model):
    """Track coach certifications and background checks."""

    class ComplianceType(models.TextChoices):
        BACKGROUND_CHECK = "background_check", "Background Check"
        FIRST_AID = "first_aid", "First Aid Certification"
        CPR = "cpr", "CPR Certification"
        SAFEGUARDING = "safeguarding", "Safeguarding Training"
        CONCUSSION = "concussion", "Concussion Protocol"
        FIRE_SAFETY = "fire_safety", "Fire Safety"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        VALID = "valid", "Valid"
        EXPIRED = "expired", "Expired"
        PENDING = "pending", "Pending"
        SUSPENDED = "suspended", "Suspended"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="compliance_records")
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="compliance_records")
    # Compliance info
    compliance_type = models.CharField(max_length=20, choices=ComplianceType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Certification details
    certification_number = models.CharField(max_length=100, blank=True)
    issuing_organization = models.CharField(max_length=200, blank=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    # Documents
    document_url = models.URLField(blank=True)
    # Tracking
    reminder_sent = models.BooleanField(default=False)
    last_reminder = models.DateTimeField(null=True, blank=True)
    # Review
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_compliance"
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_compliance"
        ordering = ["expiry_date"]

    def __str__(self):
        return f"{self.staff_member} - {self.get_compliance_type_display()} ({self.get_status_display()})"

    @property
    def is_valid(self):
        from django.utils import timezone

        return self.status == self.Status.VALID and self.expiry_date >= timezone.now().date()


class WeatherIntegration(models.Model):
    """Auto-cancel/postpone for weather conditions."""

    class WeatherCondition(models.TextChoices):
        CLEAR = "clear", "Clear"
        RAIN = "rain", "Rain"
        HEAVY_RAIN = "heavy_rain", "Heavy Rain"
        SNOW = "snow", "Snow"
        STORM = "storm", "Storm"
        EXTREME_HEAT = "extreme_heat", "Extreme Heat"
        WIND = "wind", "High Wind"
        FOG = "fog", "Fog"
        OTHER = "other", "Other"

    class ActionTaken(models.TextChoices):
        NONE = "none", "No Action"
        DELAYED = "delayed", "Delayed"
        RESCHEDULED = "rescheduled", "Rescheduled"
        CANCELLED = "cancelled", "Cancelled"
        MOVED_INDOORS = "moved_indoors", "Moved Indoors"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="weather_alerts")
    event = models.ForeignKey(SportEvent, on_delete=models.CASCADE, related_name="weather_alerts")
    # Weather info
    weather_condition = models.CharField(max_length=15, choices=WeatherCondition.choices)
    temperature = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    wind_speed = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    precipitation_mm = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    # Action
    action_taken = models.CharField(max_length=15, choices=ActionTaken.choices, default=ActionTaken.NONE)
    action_reason = models.TextField(blank=True)
    # Notification
    notified_coaches = models.BooleanField(default=False)
    notified_players = models.BooleanField(default=False)
    notified_parents = models.BooleanField(default=False)
    # Decision
    decided_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="weather_decisions"
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_weather_alerts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event} - {self.get_weather_condition_display()} ({self.get_action_taken_display()})"


class LiveStreaming(models.Model):
    """Stream games for remote parents."""

    class StreamStatus(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        LIVE = "live", "Live"
        ENDED = "ended", "Ended"
        FAILED = "failed", "Failed"

    class StreamQuality(models.TextChoices):
        LOW = "low", "Low (480p)"
        MEDIUM = "medium", "Medium (720p)"
        HIGH = "high", "High (1080p)"
        AUTO = "auto", "Auto"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="live_streams")
    event = models.ForeignKey(SportEvent, on_delete=models.CASCADE, related_name="live_streams")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="live_streams")
    # Stream info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    stream_url = models.URLField(blank=True)
    embed_code = models.TextField(blank=True)
    # Status
    status = models.CharField(max_length=10, choices=StreamStatus.choices, default=StreamStatus.SCHEDULED)
    quality = models.CharField(max_length=10, choices=StreamQuality.choices, default=StreamQuality.AUTO)
    # Schedule
    scheduled_start = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    actual_end = models.DateTimeField(null=True, blank=True)
    # Viewers
    peak_viewers = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    # Recording
    recording_url = models.URLField(blank=True)
    is_recorded = models.BooleanField(default=True)
    # Access
    is_public = models.BooleanField(default=False)
    requires_login = models.BooleanField(default=True)
    password = models.CharField(max_length=50, blank=True)
    # Settings
    allow_chat = models.BooleanField(default=True)
    show_scoreboard = models.BooleanField(default=True)
    # Created by
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_live_streams"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_live_streams"
        ordering = ["-scheduled_start"]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    @property
    def duration_minutes(self):
        if self.actual_start and self.actual_end:
            delta = self.actual_end - self.actual_start
            return int(delta.total_seconds() / 60)
        return 0


class SuspensionManagement(models.Model):
    """Track player/coach suspensions."""

    class SuspensionType(models.TextChoices):
        GAME = "game", "Game Suspension"
        PRACTICE = "practice", "Practice Suspension"
        SEASON = "season", "Season Suspension"
        INDEFINITE = "indefinite", "Indefinite"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        APPEALED = "appealed", "Appealed"
        LIFTED = "lifted", "Lifted"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sports_suspensions")
    # Person suspended
    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, null=True, blank=True, related_name="sports_suspensions"
    )
    staff_member = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="sports_suspensions"
    )
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="suspensions")
    # Suspension details
    suspension_type = models.CharField(max_length=15, choices=SuspensionType.choices)
    reason = models.TextField()
    incident_date = models.DateField()
    # Duration
    games_missed = models.PositiveSmallIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Issued by
    issued_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="issued_sports_suspensions"
    )
    # Appeal
    appeal_submitted = models.BooleanField(default=False)
    appeal_date = models.DateField(null=True, blank=True)
    appeal_outcome = models.TextField(blank=True)
    # Documentation
    document_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_suspensions"
        ordering = ["-incident_date"]

    def __str__(self):
        person = self.student or self.staff_member
        return f"{person} - {self.get_suspension_type_display()} ({self.get_status_display()})"

    @property
    def is_currently_suspended(self):
        from django.utils import timezone

        if self.status == self.Status.ACTIVE:
            if self.end_date:
                return self.end_date >= timezone.now().date()
            return True
        return False


class TournamentBracket(models.Model):
    """Auto-generate tournament brackets."""

    class BracketType(models.TextChoices):
        SINGLE = "single", "Single Elimination"
        DOUBLE = "double", "Double Elimination"
        ROUND_ROBIN = "round_robin", "Round Robin"
        SWISS = "swiss", "Swiss System"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="tournament_brackets")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="tournament_brackets")
    # Tournament info
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    bracket_type = models.CharField(max_length=15, choices=BracketType.choices)
    # Schedule
    start_date = models.DateField()
    end_date = models.DateField()
    # Settings
    max_teams = models.PositiveSmallIntegerField(default=16)
    current_round = models.PositiveSmallIntegerField(default=0)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    # Bracket data
    bracket_data = models.JSONField(default=dict, blank=True)
    # Prize
    first_prize = models.CharField(max_length=200, blank=True)
    second_prize = models.CharField(max_length=200, blank=True)
    third_prize = models.CharField(max_length=200, blank=True)
    # Created by
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_tournaments"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_tournament_brackets"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.title} ({self.get_bracket_type_display()})"


class TournamentMatch(models.Model):
    """Individual matches within a tournament bracket."""

    class MatchStatus(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        BYE = "bye", "Bye"
        FORFEIT = "forfeit", "Forfeit"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bracket = models.ForeignKey(TournamentBracket, on_delete=models.CASCADE, related_name="matches")
    # Teams
    team_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tournament_matches_as_team1")
    team_2 = models.ForeignKey(
        Team, on_delete=models.CASCADE, null=True, blank=True, related_name="tournament_matches_as_team2"
    )
    # Round info
    round_number = models.PositiveSmallIntegerField()
    match_number = models.PositiveSmallIntegerField()
    # Scores
    team_1_score = models.PositiveSmallIntegerField(default=0)
    team_2_score = models.PositiveSmallIntegerField(default=0)
    # Winner
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="tournament_wins")
    # Status
    status = models.CharField(max_length=15, choices=MatchStatus.choices, default=MatchStatus.SCHEDULED)
    # Schedule
    match_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_tournament_matches"
        ordering = ["round_number", "match_number"]

    def __str__(self):
        return f"Round {self.round_number} Match {self.match_number}: {self.team_1} vs {self.team_2 or 'TBD'}"


class MerchandiseStore(models.Model):
    """Online team gear store."""

    class ProductType(models.TextChoices):
        JERSEY = "jersey", "Jersey"
        SHORTS = "shorts", "Shorts"
        JACKET = "jacket", "Jacket"
        CAP = "cap", "Cap"
        BAG = "bag", "Bag"
        ACCESSORY = "accessory", "Accessory"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        OUT_OF_STOCK = "out_of_stock", "Out of Stock"
        DISCONTINUED = "discontinued", "Discontinued"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="merchandise")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="merchandise")
    # Product info
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=15, choices=ProductType.choices)
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Inventory
    quantity_available = models.PositiveIntegerField(default=0)
    sizes_available = models.JSONField(default=list, blank=True)
    colors_available = models.JSONField(default=list, blank=True)
    # Media
    image_url = models.URLField(blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    # Sales
    total_sold = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Settings
    is_online = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_merchandise"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - ${self.price}"

    @property
    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price


class MerchandiseOrder(models.Model):
    """Track merchandise orders."""

    class OrderStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="merchandise_orders")
    product = models.ForeignKey(MerchandiseStore, on_delete=models.CASCADE, related_name="orders")
    # Buyer
    buyer_name = models.CharField(max_length=150)
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=20, blank=True)
    student = models.ForeignKey(
        "students.Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="merchandise_orders"
    )
    # Order details
    quantity = models.PositiveSmallIntegerField(default=1)
    size = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=50, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Status
    status = models.CharField(max_length=15, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    # Payment
    payment_status = models.CharField(
        max_length=15,
        choices=[("unpaid", "Unpaid"), ("paid", "Paid"), ("refunded", "Refunded")],
        default="unpaid",
    )
    transaction_id = models.CharField(max_length=100, blank=True)
    # Delivery
    shipping_address = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    shipped_date = models.DateField(null=True, blank=True)
    delivered_date = models.DateField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_merchandise_orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.buyer_name} - {self.product.name} (x{self.quantity})"


class InsuranceTracking(models.Model):
    """Player insurance verification."""

    class InsuranceType(models.TextChoices):
        PERSONAL = "personal", "Personal Insurance"
        SCHOOL = "school", "School Insurance"
        ATHLETIC = "athletic", "Athletic Insurance"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        PENDING = "pending", "Pending"
        DENIED = "denied", "Denied"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="insurance_records")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="insurance_records")
    # Insurance info
    insurance_type = models.CharField(max_length=10, choices=InsuranceType.choices)
    provider = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=100)
    group_number = models.CharField(max_length=100, blank=True)
    # Coverage
    coverage_start = models.DateField()
    coverage_end = models.DateField()
    # Contact
    provider_phone = models.CharField(max_length=20, blank=True)
    provider_email = models.EmailField(blank=True)
    # Documents
    insurance_card_url = models.URLField(blank=True)
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Verification
    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_insurance"
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_insurance"
        ordering = ["-coverage_end"]

    def __str__(self):
        return f"{self.student} - {self.get_insurance_type_display()} ({self.get_status_display()})"

    @property
    def is_valid(self):
        from django.utils import timezone

        return self.status == self.Status.ACTIVE and self.coverage_end >= timezone.now().date()


class EligibilityRule(models.Model):
    """Academic/age eligibility tracking."""

    class RuleType(models.TextChoices):
        ACADEMIC = "academic", "Academic Eligibility"
        AGE = "age", "Age Eligibility"
        GRADE = "grade", "Grade Eligibility"
        ATTENDANCE = "attendance", "Attendance Eligibility"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="eligibility_rules")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, null=True, blank=True, related_name="eligibility_rules")
    # Rule info
    rule_type = models.CharField(max_length=15, choices=RuleType.choices)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Criteria
    min_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    min_age = models.PositiveSmallIntegerField(null=True, blank=True)
    max_age = models.PositiveSmallIntegerField(null=True, blank=True)
    min_grade = models.PositiveSmallIntegerField(null=True, blank=True)
    max_grade = models.PositiveSmallIntegerField(null=True, blank=True)
    min_attendance = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Minimum attendance percentage"
    )
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_eligibility_rules"
        ordering = ["rule_type", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


class StudentEligibility(models.Model):
    """Track individual student eligibility status."""

    class Status(models.TextChoices):
        ELIGIBLE = "eligible", "Eligible"
        INELIGIBLE = "ineligible", "Ineligible"
        PROBATION = "probation", "Probation"
        PENDING = "pending", "Pending Review"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_eligibility")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="eligibility_status")
    sport = models.ForeignKey(
        Sport, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_eligibility"
    )
    # Status
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    # Current metrics
    current_gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    current_attendance = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True, help_text="Attendance percentage"
    )
    # Dates
    last_review_date = models.DateField(null=True, blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    # Review
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_eligibility"
    )
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_student_eligibility"
        unique_together = [("student", "school")]
        ordering = ["student"]

    def __str__(self):
        return f"{self.student} - {self.get_status_display()}"


class PlayerTransferSystem(models.Model):
    """Transfer between teams/clubs."""

    class TransferType(models.TextChoices):
        INTERNAL = "internal", "Internal Transfer"
        EXTERNAL = "external", "External Transfer"
        LOAN = "loan", "Loan"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="transfers")
    # Player
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="transfers")
    # Transfer details
    transfer_type = models.CharField(max_length=10, choices=TransferType.choices)
    from_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="transfers_out")
    to_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="transfers_in")
    from_school = models.CharField(max_length=200, blank=True, help_text="For external transfers")
    to_school = models.CharField(max_length=200, blank=True, help_text="For external transfers")
    # Reason
    reason = models.TextField(blank=True)
    # Dates
    request_date = models.DateField(auto_now_add=True)
    effective_date = models.DateField(null=True, blank=True)
    # Status
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    # Approval
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_transfers"
    )
    approval_date = models.DateField(null=True, blank=True)
    # Documents
    transfer_paperwork_url = models.URLField(blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_transfers"
        ordering = ["-request_date"]

    def __str__(self):
        return f"{self.student} - {self.get_transfer_type_display()} ({self.get_status_display()})"


class SeasonArchive(models.Model):
    """Historical season data."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="season_archives")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="season_archives")
    # Season info
    season = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)
    # Stats
    games_played = models.PositiveSmallIntegerField(default=0)
    wins = models.PositiveSmallIntegerField(default=0)
    losses = models.PositiveSmallIntegerField(default=0)
    ties = models.PositiveSmallIntegerField(default=0)
    # Performance
    points_scored = models.PositiveIntegerField(default=0)
    points_allowed = models.PositiveIntegerField(default=0)
    # Roster
    roster_snapshot = models.JSONField(default=list, blank=True)
    # Achievements
    championships = models.PositiveSmallIntegerField(default=0)
    tournament_appearances = models.PositiveSmallIntegerField(default=0)
    # Archive data
    archive_data = models.JSONField(default=dict, blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_season_archives"
        unique_together = [("team", "season")]
        ordering = ["-academic_year", "-season"]

    def __str__(self):
        return f"{self.team} - {self.season}"

    @property
    def win_percentage(self):
        if self.games_played > 0:
            return round(self.wins / self.games_played * 100, 1)
        return 0


class SportsGamification(models.Model):
    """Badges, achievements, leaderboards."""

    class BadgeType(models.TextChoices):
        PARTICIPATION = "participation", "Participation"
        ACHIEVEMENT = "achievement", "Achievement"
        MILESTONE = "milestone", "Milestone"
        SPECIAL = "special", "Special"
        TEAM = "team", "Team Badge"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sports_badges")
    # Badge info
    name = models.CharField(max_length=200)
    description = models.TextField()
    badge_type = models.CharField(max_length=15, choices=BadgeType.choices)
    # Icon
    icon_url = models.URLField(blank=True)
    icon_color = models.CharField(max_length=20, blank=True)
    # Criteria
    criteria = models.JSONField(default=dict, blank=True)
    points_value = models.PositiveIntegerField(default=0)
    # Status
    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)
    # Stats
    times_awarded = models.PositiveIntegerField(default=0)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_gamification_badges"
        ordering = ["badge_type", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_badge_type_display()})"


class BadgeAward(models.Model):
    """Records of badges earned."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    badge = models.ForeignKey(SportsGamification, on_delete=models.CASCADE, related_name="awards")
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="sports_badge_awards")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="badge_awards")
    # Award info
    awarded_date = models.DateField(auto_now_add=True)
    awarded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="awarded_sports_badges"
    )
    reason = models.TextField(blank=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sports_badge_awards"
        unique_together = [("badge", "student")]
        ordering = ["-awarded_date"]

    def __str__(self):
        return f"{self.student} - {self.badge.name}"


class SportsLeaderboard(models.Model):
    """School-wide/house competitions."""

    class LeaderboardType(models.TextChoices):
        POINTS = "points", "Points Leaderboard"
        WINS = "wins", "Wins Leaderboard"
        GOALS = "goals", "Goals Leaderboard"
        ATTENDANCE = "attendance", "Attendance Leaderboard"
        ACADEMIC = "academic", "Academic-Athletic"
        OVERALL = "overall", "Overall"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="sports_leaderboards")
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True, blank=True, related_name="leaderboards")
    # Leaderboard info
    name = models.CharField(max_length=200)
    leaderboard_type = models.CharField(max_length=15, choices=LeaderboardType.choices)
    season = models.CharField(max_length=50)
    # Data
    entries = models.JSONField(default=list, blank=True)
    # Settings
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    # Notes
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sports_leaderboards"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_leaderboard_type_display()})"
