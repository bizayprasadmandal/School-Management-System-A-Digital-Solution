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
