"""
Wide API coverage — Reporting & Timetable CRUD endpoints.

These two modules had the thinnest API test surface (17 and 24 tests
against 40+ viewsets each). This suite pins down the *breadth*:
parametrized create-through-the-API for every simple-payload viewset in
both modules, tenant isolation (other school's rows invisible, own rows
listed), and 401 for anonymous callers.

A failure here is a real bug — typically a serializer marking fields
read-only that its viewset's perform_create never injects (POST would
500 or silently drop data).
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import AcademicYearFactory, AdminUserFactory, SchoolFactory
from tests.url_helpers import url


@pytest.fixture
def school(db):
    s = SchoolFactory()
    # Realistic precondition: every school has a current academic year;
    # several timetable viewsets stamp it server-side on create.
    AcademicYearFactory(school=s, is_current=True)
    return s


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin(api_client, school):
    """Admin client authenticated against `school`."""
    admin_user = AdminUserFactory(school=school)
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def other_admin_client(db):
    """Independent client authenticated as another school's admin."""
    other_school = SchoolFactory()
    other_admin = AdminUserFactory(school=other_school)
    client = APIClient()
    client.force_authenticate(user=other_admin)
    return client


# ─── Create specs: (url path, minimal valid payload, list title key) ───────
# school / user fields are injected server-side by each viewset's
# perform_create; payloads only carry what the serializer requires.

REPORTING_CREATE_SPECS = [
    (
        "reporting/templates/",
        {"name": "Attendance Summary", "report_type": "attendance"},
        "name",
    ),
    (
        "reporting/report-folder/",
        {"name": "Board Pack"},
        "name",
    ),
    (
        "reporting/chart-configuration/",
        {"name": "Enrollment Trend", "chart_type": "line", "data_source": "students"},
        "name",
    ),
    (
        "reporting/dashboard-widget/",
        {"name": "Attendance KPI", "widget_type": "kpi"},
        "name",
    ),
    (
        "reporting/k-p-i-definition/",
        {"name": "Avg Attendance", "category": "academic", "data_type": "percentage", "target_value": 95},
        "name",
    ),
    (
        "reporting/report-alert/",
        {"name": "Fee Defaulters", "alert_type": "threshold", "metric": "fee_collection", "threshold_value": 80},
        "name",
    ),
    (
        "reporting/report-insight/",
        {
            "insight_type": "recommendation",
            "title": "Boost grade 9 attendance",
            "description": "Below 80% for three weeks",
        },
        "title",
    ),
    (
        "reporting/report-schedule/",
        {"name": "Weekly Fee Digest", "report_type": "fee", "frequency": "weekly", "time_of_day": "08:00:00"},
        "name",
    ),
]

TIMETABLE_CREATE_SPECS = [
    (
        "timetable/events/",
        {"title": "Sports Day", "event_type": "sports", "start_date": "2026-10-01", "end_date": "2026-10-01"},
        "title",
    ),
    (
        "timetable/templates/",
        {"name": "Standard 8-period"},
        "name",
    ),
    (
        "timetable/bell-schedule/",
        {"name": "Regular Day"},
        "name",
    ),
    (
        "timetable/academic-calendar/",
        {"title": "Fall Calendar", "start_date": "2026-10-01", "end_date": "2026-10-31"},
        "title",
    ),
    (
        "timetable/room-bookings/",
        {"room_name": "Auditorium", "date": "2026-10-05", "start_time": "09:00:00", "end_time": "11:00:00"},
        "room_name",
    ),
    (
        "timetable/closures/",
        {"title": "Snow Day", "date": "2026-12-21"},
        "title",
    ),
    (
        "timetable/co-curricular/",
        {"activity_name": "Chess Club", "day_of_week": 2, "start_time": "15:00:00", "end_time": "16:00:00"},
        "activity_name",
    ),
    (
        "timetable/daily-schedule/",
        {"date": "2026-10-06", "day_of_week": 2},
        "date",
    ),
    (
        "timetable/timetable-resource/",
        {"name": "Projector Cart 1", "resource_type": "projector"},
        "name",
    ),
]


@pytest.mark.django_db
@pytest.mark.parametrize("path,payload,list_key", REPORTING_CREATE_SPECS)
def test_reporting_create_and_list(admin, path, payload, list_key):
    """Admin can create via the reporting API and the row appears in the list."""
    response = admin.post(url(path), payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.data

    listed = admin.get(url(path))
    assert listed.status_code == status.HTTP_200_OK
    names = [row[list_key] for row in listed.data["results"]]
    assert payload[list_key] in names


@pytest.mark.django_db
@pytest.mark.parametrize("path,payload,list_key", TIMETABLE_CREATE_SPECS)
def test_timetable_create_and_list(admin, path, payload, list_key):
    """Admin can create via the timetable API and the row appears in the list."""
    response = admin.post(url(path), payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.data

    listed = admin.get(url(path))
    assert listed.status_code == status.HTTP_200_OK
    titles = [row[list_key] for row in listed.data["results"]]
    assert str(payload[list_key]) in [str(t) for t in titles]


@pytest.mark.django_db
def test_reporting_create_anonymous_forbidden(api_client):
    """Anonymous callers cannot create reporting objects."""
    response = api_client.post(url("reporting/templates/"), {"name": "X", "report_type": "custom"}, format="json")
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_timetable_create_anonymous_forbidden(api_client):
    """Anonymous callers cannot create timetable objects."""
    response = api_client.post(
        url("timetable/events/"),
        {"title": "X", "event_type": "other", "start_date": "2026-10-01", "end_date": "2026-10-01"},
        format="json",
    )
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


# ─── Tenant isolation ────────────────────────────────────────────────────────


@pytest.mark.django_db
def test_reporting_tenant_isolation(admin, other_admin_client, school):
    """Another school's admin can neither list nor fetch our report template."""
    create = admin.post(url("reporting/templates/"), {"name": "Internal Only", "report_type": "custom"}, format="json")
    assert create.status_code == status.HTTP_201_CREATED
    template_id = create.data["id"]

    listed = other_admin_client.get(url("reporting/templates/"))
    assert [row["name"] for row in listed.data["results"]] == []

    detail = other_admin_client.get(url(f"reporting/templates/{template_id}/"))
    assert detail.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_timetable_tenant_isolation(admin, other_admin_client):
    """Another school's admin can neither list nor fetch our school event."""
    create = admin.post(
        url("timetable/events/"),
        {"title": "Private Board Meeting", "event_type": "other", "start_date": "2026-10-02", "end_date": "2026-10-02"},
        format="json",
    )
    assert create.status_code == status.HTTP_201_CREATED
    event_id = create.data["id"]

    listed = other_admin_client.get(url("timetable/events/"))
    assert [row["title"] for row in listed.data["results"]] == []

    detail = other_admin_client.get(url(f"timetable/events/{event_id}/"))
    assert detail.status_code == status.HTTP_404_NOT_FOUND
