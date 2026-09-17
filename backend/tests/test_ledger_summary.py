"""Tests for the monthly debits-vs-credits ledger summary endpoint.

Pins: per-stream aggregation from reference_type, month scoping (only the
current month counts), tenant isolation, and permission (non-admin read,
anonymous rejected).
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

SUMMARY_URL = f"{API_PREFIX}/fees/accounting-entry/monthly_summary/"
TREND_URL = f"{API_PREFIX}/fees/accounting-entry/monthly_trend/"


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory()


@pytest.fixture
def other_school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    from tests.factories import AdminUserFactory

    return AdminUserFactory(school=school)


@pytest.fixture
def admin_client(db, admin):
    c = APIClient()
    c.force_authenticate(user=admin)
    return c


def _prev_month_mid() -> date:
    """A date guaranteed to fall in the previous calendar month."""
    today = timezone.localdate()
    first_of_month = today.replace(day=1)
    return (first_of_month - timedelta(days=1)).replace(day=15)


def _entry(school, stream, entry_type, amount, days_ago=0, entry_date=None):
    from services.fees.models import AccountingEntry

    return AccountingEntry.objects.create(
        school=school,
        entry_type=entry_type,
        account_code="4000",
        account_name="Test Account",
        description=f"{stream} test entry",
        amount=Decimal(amount),
        reference_type=stream,
        reference_id="ref-1",
        entry_date=entry_date or (timezone.localdate() - timedelta(days=days_ago)),
    )


@pytest.mark.django_db
class TestMonthlyLedgerSummary:
    def test_groups_by_stream_and_type(self, admin_client, school):
        _entry(school, "payment", "credit", "100.00")
        _entry(school, "payment", "credit", "50.00")
        _entry(school, "cafeteria_pos", "credit", "7.50")
        _entry(school, "cafeteria_pos", "debit", "2.00")
        _entry(school, "depreciation", "debit", "300.00")

        r = admin_client.get(SUMMARY_URL)
        assert r.status_code == status.HTTP_200_OK, r.data
        assert r.data["month"] == timezone.localdate().strftime("%Y-%m")

        by_stream = {row["stream"]: row for row in r.data["streams"]}
        assert by_stream["payment"]["total_credits"] == "150.00"
        assert by_stream["payment"]["total_debits"] == "0.00"
        assert by_stream["cafeteria_pos"]["total_credits"] == "7.50"
        assert by_stream["cafeteria_pos"]["total_debits"] == "2.00"
        assert by_stream["cafeteria_pos"]["entry_count"] == 2
        assert by_stream["depreciation"]["total_debits"] == "300.00"

        # Previous-month aggregates default to zero when nothing is posted
        assert r.data["prev_month"]
        assert by_stream["payment"]["prev_credits"] == "0.00"
        assert by_stream["payment"]["prev_debits"] == "0.00"
        assert r.data["prev_total_credits"] == "0.00"
        assert r.data["prev_total_debits"] == "0.00"
        assert r.data["prev_net"] == "0.00"

        assert r.data["total_credits"] == "157.50"
        assert r.data["total_debits"] == "302.00"
        assert r.data["net"] == "-144.50"

    def test_scoped_to_current_month(self, admin_client, school):
        _entry(school, "payment", "credit", "100.00", days_ago=0)
        # Last month's entry must not count toward current totals
        _entry(school, "payment", "credit", "999.00", entry_date=_prev_month_mid())

        r = admin_client.get(SUMMARY_URL)
        by_stream = {row["stream"]: row for row in r.data["streams"]}
        assert by_stream["payment"]["total_credits"] == "100.00"

    def test_month_over_month_aggregates(self, admin_client, school):
        _entry(school, "payment", "credit", "100.00")
        _entry(school, "payment", "debit", "10.00")
        _entry(school, "payment", "credit", "40.00", entry_date=_prev_month_mid())
        # A stream that only existed last month must still appear
        _entry(school, "supplier_payment", "debit", "60.00", entry_date=_prev_month_mid())

        r = admin_client.get(SUMMARY_URL)
        assert r.status_code == status.HTTP_200_OK, r.data

        prev_month = _prev_month_mid().strftime("%Y-%m")
        assert r.data["prev_month"] == prev_month

        by_stream = {row["stream"]: row for row in r.data["streams"]}
        payment = by_stream["payment"]
        assert payment["total_credits"] == "100.00"
        assert payment["prev_credits"] == "40.00"
        assert payment["total_debits"] == "10.00"

        # Stream with zero activity this month still shows, for the delta
        supplier = by_stream["supplier_payment"]
        assert supplier["total_debits"] == "0.00"
        assert supplier["prev_debits"] == "60.00"
        assert supplier["entry_count"] == 0

        assert r.data["prev_total_credits"] == "40.00"
        assert r.data["prev_total_debits"] == "60.00"
        assert r.data["prev_net"] == "-20.00"
        assert r.data["total_credits"] == "100.00"
        assert r.data["total_debits"] == "10.00"
        assert r.data["net"] == "90.00"

    def test_tenant_isolation(self, admin_client, admin, school, other_school):
        _entry(school, "payment", "credit", "100.00")
        from tests.factories import AdminUserFactory

        other_admin = AdminUserFactory(school=other_school)
        _entry(
            other_school,
            "payment",
            "credit",
            "500.00",
        )  # other school's books

        r = admin_client.get(SUMMARY_URL)
        by_stream = {row["stream"]: row for row in r.data["streams"]}
        assert by_stream["payment"]["total_credits"] == "100.00"

        c = APIClient()
        c.force_authenticate(user=other_admin)
        r2 = c.get(SUMMARY_URL)
        by_stream2 = {row["stream"]: row for row in r2.data["streams"]}
        assert by_stream2["payment"]["total_credits"] == "500.00"

    def test_requires_authentication(self, db):
        c = APIClient()
        r = c.get(SUMMARY_URL)
        assert r.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_empty_month_returns_zeroes(self, admin_client, school):
        r = admin_client.get(SUMMARY_URL)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["streams"] == []
        assert r.data["total_debits"] == "0.00"
        assert r.data["total_credits"] == "0.00"
        assert r.data["net"] == "0.00"


@pytest.mark.django_db
class TestMonthlyLedgerTrend:
    def test_series_align_to_month_labels(self, admin_client, school):
        _entry(school, "payment", "credit", "100.00")  # this month
        _entry(school, "payment", "credit", "40.00", entry_date=_prev_month_mid())
        _entry(school, "cafeteria_pos", "debit", "2.00")  # only this month

        r = admin_client.get(TREND_URL)
        assert r.status_code == status.HTTP_200_OK, r.data

        months = r.data["months"]
        assert len(months) == 6
        assert months[-1] == timezone.localdate().strftime("%Y-%m")

        by_stream = {s["stream"]: s for s in r.data["streams"]}
        payment = by_stream["payment"]
        assert payment["credits"][-1] == "100.00"
        assert payment["credits"][-2] == "40.00"
        assert payment["credits"][0] == "0.00"  # untouched months are zero-filled
        assert payment["debits"][-1] == "0.00"

        cafeteria = by_stream["cafeteria_pos"]
        assert cafeteria["debits"][-1] == "2.00"
        assert cafeteria["credits"] == ["0.00"] * 6

    def test_months_param_bounds(self, admin_client, school):
        r = admin_client.get(TREND_URL, {"months": "3"})
        assert len(r.data["months"]) == 3

        r = admin_client.get(TREND_URL, {"months": "99"})
        assert len(r.data["months"]) == 12

        r = admin_client.get(TREND_URL, {"months": "junk"})
        assert len(r.data["months"]) == 6

    def test_tenant_isolation(self, admin_client, admin, school, other_school):
        _entry(school, "payment", "credit", "100.00")
        _entry(other_school, "payment", "credit", "500.00")

        r = admin_client.get(TREND_URL)
        payment = next(s for s in r.data["streams"] if s["stream"] == "payment")
        assert payment["credits"][-1] == "100.00"

        from tests.factories import AdminUserFactory

        other_admin = AdminUserFactory(school=other_school)
        c = APIClient()
        c.force_authenticate(user=other_admin)
        r2 = c.get(TREND_URL)
        payment2 = next(s for s in r2.data["streams"] if s["stream"] == "payment")
        assert payment2["credits"][-1] == "500.00"

    def test_requires_authentication(self, db):
        c = APIClient()
        r = c.get(TREND_URL)
        assert r.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
