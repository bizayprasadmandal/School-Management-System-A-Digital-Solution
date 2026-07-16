"""Tests for Sports Service — Sport, Team, TeamMember, SportEvent, SportAchievement."""

import pytest
from datetime import date, timedelta
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

SPORTS_SPORTS = f"{API_PREFIX}/sports/sports/"
SPORTS_TEAMS = f"{API_PREFIX}/sports/teams/"
SPORTS_MEMBERS = f"{API_PREFIX}/sports/members/"
SPORTS_EVENTS = f"{API_PREFIX}/sports/events/"
SPORTS_ACHIEVEMENTS = f"{API_PREFIX}/sports/achievements/"


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory
    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    from tests.factories import AdminUserFactory
    return AdminUserFactory(school=school)


@pytest.fixture
def teacher(db, school):
    from tests.factories import TeacherUserFactory
    return TeacherUserFactory(school=school)


@pytest.fixture
def admin_client(db, admin):
    c = APIClient()
    c.force_authenticate(user=admin)
    return c


@pytest.fixture
def teacher_client(db, teacher):
    c = APIClient()
    c.force_authenticate(user=teacher)
    return c


@pytest.mark.django_db
class TestSports:

    def test_create_sport(self, admin_client, school):
        payload = {
            "name": "Basketball",
            "description": "Indoor basketball",
            "max_players_per_team": 5,
        }
        r = admin_client.post(SPORTS_SPORTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Basketball"

    def test_list_sports(self, admin_client, school):
        from services.sports.models import Sport
        Sport.objects.create(
            school=school, name="Football",
            max_players_per_team=11,
        )
        r = admin_client.get(SPORTS_SPORTS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_teacher_cannot_create_sport(self, teacher_client):
        payload = {"name": "Tennis", "max_players_per_team": 2}
        r = teacher_client.post(SPORTS_SPORTS, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_tenant_isolation(self, db):
        from tests.factories import SchoolFactory, AdminUserFactory
        from services.sports.models import Sport
        school_a = SchoolFactory(code="SPTA")
        school_b = SchoolFactory(code="SPTB")
        admin_a = AdminUserFactory(school=school_a)
        Sport.objects.create(
            school=school_b, name="Secret Sport",
            max_players_per_team=5,
        )
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(SPORTS_SPORTS)
        names = [s["name"] for s in r.data["results"]]
        assert "Secret Sport" not in names


@pytest.mark.django_db
class TestTeams:

    def test_create_team(self, admin_client, school):
        from services.sports.models import Sport
        sport = Sport.objects.create(
            school=school, name="Basketball",
            max_players_per_team=5,
        )
        payload = {
            "sport": sport.id,
            "name": "Eagles",
            "coach_name": "Coach Mike",
        }
        r = admin_client.post(SPORTS_TEAMS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Eagles"

    def test_list_teams_filter_by_sport(self, admin_client, school):
        from services.sports.models import Sport, Team
        sport = Sport.objects.create(
            school=school, name="Volleyball",
            max_players_per_team=6,
        )
        Team.objects.create(school=school, sport=sport, name="Spartans")
        r = admin_client.get(f"{SPORTS_TEAMS}?sport={sport.id}")
        assert r.status_code == status.HTTP_200_OK
        for t in r.data["results"]:
            assert t["sport"] == sport.id


@pytest.mark.django_db
class TestTeamMembers:

    def test_add_member(self, admin_client, school):
        from tests.factories import StudentFactory
        from services.sports.models import Sport, Team
        pupil = StudentFactory(school=school)
        sport = Sport.objects.create(
            school=school, name="Cricket",
            max_players_per_team=11,
        )
        team = Team.objects.create(school=school, sport=sport, name="Tigers")
        payload = {
            "team": team.id,
            "student": pupil.id,
            "position": "Batsman",
            "jersey_number": 7,
        }
        r = admin_client.post(SPORTS_MEMBERS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert str(r.data["student"]) == str(pupil.id)


@pytest.mark.django_db
class TestSportEvents:

    def test_create_event(self, admin_client, school):
        from services.sports.models import Sport
        sport = Sport.objects.create(
            school=school, name="Athletics",
            max_players_per_team=1,
        )
        payload = {
            "sport": sport.id,
            "title": "Annual Sports Day",
            "event_date": (date.today() + timedelta(days=30)).isoformat(),
            "location": "Main Ground",
        }
        r = admin_client.post(SPORTS_EVENTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["title"] == "Annual Sports Day"

    def test_upcoming_events(self, admin_client, school):
        from services.sports.models import Sport, SportEvent
        sport = Sport.objects.create(
            school=school, name="Swimming",
            max_players_per_team=4,
        )
        SportEvent.objects.create(
            school=school, sport=sport,
            title="Swimming Competition",
            event_date=date.today() + timedelta(days=7),
            location="Pool",
        )
        r = admin_client.get(f"{SPORTS_EVENTS}?upcoming=true")
        assert r.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSportAchievements:

    def test_create_achievement(self, admin_client, school):
        from tests.factories import StudentFactory
        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "achievement_type": "gold_medal",
            "description": "First place in 100m sprint",
            "date_achieved": date.today().isoformat(),
            "competition_name": "Inter-School Athletics",
        }
        r = admin_client.post(SPORTS_ACHIEVEMENTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_list_achievements(self, admin_client, school):
        from tests.factories import StudentFactory
        from services.sports.models import SportAchievement
        pupil = StudentFactory(school=school)
        SportAchievement.objects.create(
            school=school, student=pupil,
            achievement_type="participation",
            description="Participated in relay",
            date_achieved=date.today(),
        )
        r = admin_client.get(SPORTS_ACHIEVEMENTS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1
