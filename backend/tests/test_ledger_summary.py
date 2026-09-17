"""Tests for the monthly debits-vs-credits ledger summary endpoint.

Pins: per-stream aggregation from reference_type, month scoping (only the
current month counts), tenant isolation, and permission (non-admin read,
anonymous rejected).
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

SUMMARY_URL = f"{API_PREFIX}/fees/accounting-entry/monthly_summary/"


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


def _entry(school, stream, entry_type, amount, days_ago=0):
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
        entry_date=timezone.localdate() - timedelta(days=days_ago),
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

        assert r.data["total_credits"] == "157.50"
        assert r.data["total_debits"] == "302.00"
        assert r.data["net"] == "-144.50"

    def test_scoped_to_current_month(self, admin_client, school):
        _entry(school, "payment", "credit", "100.00", days_ago=0)
        # Last month's entry must not count
        _entry(school, "payment", "credit", "999.00", days_ago=40)

        r = admin_client.get(SUMMARY_URL)
        by_stream = {row["stream"]: row for row in r.data["streams"]}
        assert by_stream["payment"]["total_credits"] == "100.00"

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
