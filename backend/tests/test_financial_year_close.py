"""Tests for the financial year close-out endpoint.

Pins: close snapshots revenue/expenses/refunds, locks the year, rolls
student carry-forward into the ledger, rejects re-closing, and is
tenant-isolated.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from services.fees.models import ExpenseTracking, FinancialYear, StudentLedger
from tests.factories import (
    AcademicYearFactory,
    AdminUserFactory,
    FeeInvoiceFactory,
    FeeStructureFactory,
    PaymentFactory,
    SchoolFactory,
    StudentFactory,
)


def _make_fy(school, name="FY 2025-26", start=None, end=None):
    start = start or date.today().replace(month=1, day=1)
    end = end or start + timedelta(days=364)
    return FinancialYear.objects.create(
        school=school,
        name=name,
        start_date=start,
        end_date=end,
        is_current=False,
    )


def _invoice(school, total=Decimal("500.00"), paid=Decimal("0.00"), status="unpaid"):
    student = StudentFactory(school=school)
    return FeeInvoiceFactory(
        student=student,
        academic_year=AcademicYearFactory(school=school),
        fee_structure=FeeStructureFactory(school=school),
        base_amount=total,
        total_amount=total,
        paid_amount=paid,
        status=status,
    )


def _close(admin, fy):
    client = APIClient()
    client.force_authenticate(user=admin)
    return client.post(f"/api/v1/fees/financial-year/{fy.id}/close/")


@pytest.mark.django_db
class TestFinancialYearClose:
    def test_close_snapshots_and_locks(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        fy = _make_fy(school)
        invoice = _invoice(school, total=Decimal("800.00"), status="paid")
        PaymentFactory(
            invoice=invoice,
            amount=Decimal("800.00"),
            status="successful",
        )
        ExpenseTracking.objects.create(
            school=school,
            expense_type="supplies",
            description="Chalk",
            amount=Decimal("100.00"),
            expense_date=fy.start_date + timedelta(days=5),
            status="paid",
        )

        resp = _close(admin, fy)

        assert resp.status_code == 200, resp.content
        body = resp.json()
        assert body["snapshot"]["revenue"] == "800.00"
        assert body["snapshot"]["expenses"] == "100.00"
        assert body["snapshot"]["net"] == "700.00"

        fy.refresh_from_db()
        assert fy.is_closed is True
        assert fy.closed_by == admin
        assert fy.closed_date == date.today()
        assert "Closed by" in fy.notes

    def test_carryforward_ledger_entries_created(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        fy = _make_fy(school)
        inv1 = _invoice(school, total=Decimal("500.00"), paid=Decimal("200.00"), status="partial")
        _invoice(school, total=Decimal("300.00"), paid=Decimal("0.00"), status="unpaid")

        resp = _close(admin, fy)

        body = resp.json()
        assert body["students_with_carryforward"] == 2
        assert body["carryforward_entries_created"] == 2

        entry = StudentLedger.objects.get(reference_number=f"FY-{str(fy.id)[:12]}-{str(inv1.student_id)[:12]}")
        assert entry.amount == Decimal("300.00")
        assert "carry-forward" in entry.description.lower()

    def test_reclosing_rejected(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        fy = _make_fy(school)
        _invoice(school)

        assert _close(admin, fy).status_code == 200
        resp = _close(admin, fy)

        assert resp.status_code == 400
        assert StudentLedger.objects.filter(reference_number__startswith=f"FY-{str(fy.id)[:12]}").count() == 1

    def test_fully_paid_students_get_no_carryforward(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        fy = _make_fy(school)
        _invoice(school, total=Decimal("500.00"), paid=Decimal("500.00"), status="paid")

        resp = _close(admin, fy)

        assert resp.json()["students_with_carryforward"] == 0
        assert StudentLedger.objects.filter(reference_number__startswith=f"FY-{str(fy.id)[:12]}").count() == 0

    def test_cross_tenant_close_rejected(self):
        school = SchoolFactory()
        other = SchoolFactory()
        admin = AdminUserFactory(school=other, is_staff=True)
        fy = _make_fy(school)

        resp = _close(admin, fy)

        assert resp.status_code == 404
        fy.refresh_from_db()
        assert fy.is_closed is False
