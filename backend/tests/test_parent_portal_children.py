"""Parent-portal /children/ endpoint tests.

The twelve guardian-scoped endpoints back the parent SPA's module pages.
The headline properties:

1. **Guardian scoping** — a parent only ever sees rows belonging to children
   linked via ``StudentGuardian``; another school's student row never leaks.
2. **Cross-school safety** — every queryset is also bounded by the caller's
   own school, so even a forged link can't cross tenants.
3. **Response contract** — ``{count, results}`` with the field names the SPA
   interfaces expect (``student_name``, display fields, dates).
4. **Sports teams** are scoped through ``TeamMember`` (``Team`` has no
   student FK of its own) and are deduplicated per team.
"""

import uuid

import pytest
from rest_framework.test import APIClient
from services.students.models import Guardian, StudentGuardian
from tests.factories import ParentUserFactory, SchoolFactory, StudentFactory
from tests.url_helpers import url

ENDPOINTS = [
    "health/records/children/",
    "health/visits/children/",
    "health/immunizations/children/",
    "cafeteria/bookings/children/",
    "library/checkouts/children/",
    "library/fines/children/",
    "sports/teams/children/",
    "sports/achievements/children/",
    "behavior/incidents/children/",
    "behavior/points/children/",
    "counseling/sessions/children/",
    "counseling/referrals/children/",
]


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def parent_school(db):
    return SchoolFactory()


@pytest.fixture
def parent_with_child(db, parent_school):
    """A parent linked to exactly one child in their own school."""
    parent = ParentUserFactory(school=parent_school)
    child = StudentFactory(school=parent_school)
    _link(parent, child, "mother")
    return parent, child


def _auth(client, user):
    client.force_authenticate(user=user)
    return client


def _link(parent, child, relationship="father"):
    """Create a Guardian profile (idempotent) + the StudentGuardian link."""
    profile, _ = Guardian.objects.get_or_create(
        user=parent,
        defaults={
            "first_name": parent.first_name,
            "last_name": parent.last_name,
            "email": parent.email,
        },
    )
    StudentGuardian.objects.create(guardian=profile, student=child, relationship=relationship)


def _make_book(school):
    from services.library.models import Book

    return Book.objects.create(
        school=school,
        title="Test Book",
        isbn=uuid.uuid4().hex[:13],
    )


# ─── Contract: every endpoint answers 200 with the SPA's shape ────────────────


@pytest.mark.django_db
@pytest.mark.parametrize("endpoint", ENDPOINTS)
def test_children_endpoints_return_contract(api_client, parent_with_child, endpoint):
    parent, _ = parent_with_child
    res = _auth(api_client, parent).get(url(endpoint))
    assert res.status_code == 200
    assert set(res.data.keys()) == {"count", "results"}
    assert isinstance(res.data["results"], list)


# ─── Guardian scoping ─────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_parent_sees_only_linked_children_rows(api_client, parent_with_child):
    """Rows for a same-school non-linked student never appear."""
    from services.library.models import Checkout

    parent, child = parent_with_child
    other = StudentFactory(school=child.school)

    Checkout.objects.create(book=_make_book(child.school), student=child, due_date="2026-10-01")
    Checkout.objects.create(book=_make_book(child.school), student=other, due_date="2026-10-01")

    res = _auth(api_client, parent).get(url("library/checkouts/children/"))
    assert res.status_code == 200
    assert res.data["count"] == 1
    assert res.data["results"][0]["student_name"]


@pytest.mark.django_db
def test_cross_school_data_never_leaks(api_client, db):
    """A parent authenticated in school A gets nothing from school B."""
    school_a, school_b = SchoolFactory(), SchoolFactory()
    parent = ParentUserFactory(school=school_a)
    child_a = StudentFactory(school=school_a)
    child_b = StudentFactory(school=school_b)
    _link(parent, child_a)
    # even link the parent to school B's child — the school bound must win
    _link(parent, child_b)

    from services.library.models import Checkout

    Checkout.objects.create(book=_make_book(school_b), student=child_b, due_date="2026-10-01")

    res = _auth(api_client, parent).get(url("library/checkouts/children/"))
    assert res.status_code == 200
    assert res.data["count"] == 0


@pytest.mark.django_db
def test_unrelated_role_gets_empty_results(api_client, db):
    """A teacher (no guardian links, no child) gets an empty list, not an error."""
    from tests.factories import TeacherUserFactory

    teacher = TeacherUserFactory()
    for endpoint in ENDPOINTS:
        res = _auth(api_client, teacher).get(url(endpoint))
        assert res.status_code == 200, endpoint
        assert res.data["count"] == 0, endpoint


# ─── Sports teams (scoped through TeamMember) ─────────────────────────────────


@pytest.mark.django_db
def test_sports_teams_scope_through_membership(api_client, parent_with_child):
    from services.sports.models import Team, TeamMember

    parent, child = parent_with_child
    sport = Team.sport.field.related_model.objects.create(school=child.school, name="Soccer")
    my_team = Team.objects.create(school=child.school, sport=sport, name="U15 A")
    other_team = Team.objects.create(school=child.school, sport=sport, name="U15 B")
    TeamMember.objects.create(team=my_team, student=child, role="player")
    stranger = StudentFactory(school=child.school)
    TeamMember.objects.create(team=other_team, student=stranger, role="player")

    res = _auth(api_client, parent).get(url("sports/teams/children/"))
    assert res.status_code == 200
    assert res.data["count"] == 1
    row = res.data["results"][0]
    assert row["name"] == "U15 A"
    assert row["sport_name"] == "Soccer"
    assert row["member_count"] == 1
