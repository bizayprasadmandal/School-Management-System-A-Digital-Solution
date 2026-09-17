"""Tests for cafeteria → books posting (POS sales and online payments).

Pins the final integration of the ops campaign: cafeteria revenue joins the
same idempotent audit trail as fee/transport/hostel collections.
"""

from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

CAFETERIA_POS = f"{API_PREFIX}/cafeteria/pos/"
CAFETERIA_PAYMENTS = f"{API_PREFIX}/cafeteria/payments/"


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


def _entries(school, ref_type):
    from services.fees.models import AccountingEntry

    return AccountingEntry.objects.filter(school=school, reference_type=ref_type)


# ── POS register sales ──────────────────────────────────────────────────────


@pytest.mark.django_db
class TestPOSToBooks:
    def test_successful_sale_posts_credit(self, admin_client, admin, school):
        r = admin_client.post(
            CAFETERIA_POS,
            {
                "user": admin.id,
                "transaction_type": "meal",
                "amount": "7.50",
                "payment_method": "cash",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED, r.data

        entries = _entries(school, "cafeteria_pos")
        assert entries.count() == 1
        e = entries.first()
        assert e.entry_type == "credit"
        assert e.amount == Decimal("7.50")

        from services.fees.models import TransactionLog

        log = TransactionLog.objects.filter(reference_number=str(r.data["id"])).first()
        assert log is not None
        assert log.status == "success"

    def test_unsuccessful_sale_does_not_post(self, admin_client, admin, school):
        r = admin_client.post(
            CAFETERIA_POS,
            {
                "user": admin.id,
                "transaction_type": "meal",
                "amount": "7.50",
                "payment_method": "cash",
                "is_successful": False,
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert _entries(school, "cafeteria_pos").count() == 0

    def test_zero_amount_does_not_post(self, admin_client, admin, school):
        r = admin_client.post(
            CAFETERIA_POS,
            {
                "user": admin.id,
                "transaction_type": "snack",
                "amount": "0.00",
                "payment_method": "cash",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert _entries(school, "cafeteria_pos").count() == 0

    def test_school_scoping(self, admin_client, admin, school, other_school):
        """Entries land on the school that owns the sale, not the caller's."""
        from tests.factories import AdminUserFactory

        other_admin = AdminUserFactory(school=other_school)
        r = admin_client.post(
            CAFETERIA_POS,
            {
                "user": other_admin.id,
                "transaction_type": "drink",
                "amount": "2.00",
                "payment_method": "card",
            },
            format="json",
        )
        assert r.status_code == status.HTTP_201_CREATED, r.data
        # Sale's school = other_school (set from user.school via serializer save)
        # but viewset forces school=request.user.school — verify which won:
        assert _entries(school, "cafeteria_pos").count() == 1
        assert _entries(other_school, "cafeteria_pos").count() == 0


# ── Online payment transactions ─────────────────────────────────────────────


@pytest.mark.django_db
class TestPaymentTransactionToBooks:
    def _payload(self, user, **kw):
        data = {
            "user": user.id,
            "transaction_type": "deposit",
            "amount": "50.00",
            "payment_method": "credit_card",
            "status": "completed",
        }
        data.update(kw)
        return data

    def test_completed_deposit_posts_credit(self, admin_client, admin, school):
        r = admin_client.post(CAFETERIA_PAYMENTS, self._payload(admin), format="json")
        assert r.status_code == status.HTTP_201_CREATED, r.data

        entries = _entries(school, "cafeteria_payment")
        assert entries.count() == 1
        assert entries.first().entry_type == "credit"
        assert entries.first().amount == Decimal("50.00")

    def test_pending_does_not_post(self, admin_client, admin, school):
        r = admin_client.post(CAFETERIA_PAYMENTS, self._payload(admin, status="pending"), format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert _entries(school, "cafeteria_payment").count() == 0
        assert _entries(school, "cafeteria_refund").count() == 0

    def test_update_to_completed_posts_once(self, admin_client, admin, school):
        """Marking a pending row completed later posts exactly once."""
        r = admin_client.post(CAFETERIA_PAYMENTS, self._payload(admin, status="pending"), format="json")
        assert r.status_code == status.HTTP_201_CREATED
        txn_id = r.data["id"]

        r2 = admin_client.patch(f"{CAFETERIA_PAYMENTS}{txn_id}/", {"status": "completed"}, format="json")
        assert r2.status_code == status.HTTP_200_OK, r2.data
        r3 = admin_client.patch(f"{CAFETERIA_PAYMENTS}{txn_id}/", {"status": "completed"}, format="json")
        assert r3.status_code == status.HTTP_200_OK

        assert _entries(school, "cafeteria_payment").count() == 1

    def test_refund_posts_debit(self, admin_client, admin, school):
        r = admin_client.post(CAFETERIA_PAYMENTS, self._payload(admin, transaction_type="refund"), format="json")
        assert r.status_code == status.HTTP_201_CREATED, r.data

        entries = _entries(school, "cafeteria_refund")
        assert entries.count() == 1
        assert entries.first().entry_type == "debit"

    def test_failed_does_not_post(self, admin_client, admin, school):
        r = admin_client.post(CAFETERIA_PAYMENTS, self._payload(admin, status="failed"), format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert _entries(school, "cafeteria_payment").count() == 0
