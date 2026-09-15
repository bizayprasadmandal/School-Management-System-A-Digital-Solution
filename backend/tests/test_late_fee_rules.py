"""Tests for LateFeeRule-driven late fees in mark_overdue_invoices.

Rules take precedence over the legacy fee_structure.late_fee_per_day
fallback; fixed vs percentage fee types, caps, rule-severity selection,
fallback behavior, and the one-time LATE-<id> TransactionLog audit entry
are pinned here.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from services.fees.tasks import mark_overdue_invoices
from tests.factories import (
    AcademicYearFactory,
    FeeInvoiceFactory,
    FeeStructureFactory,
    LateFeeRuleFactory,
    SchoolFactory,
    StudentFactory,
)


def _overdue_invoice(school, days=10, amount=Decimal("500.00")):
    student = StudentFactory(school=school)
    return FeeInvoiceFactory(
        student=student,
        academic_year=AcademicYearFactory(school=school),
        fee_structure=FeeStructureFactory(school=school),
        due_date=timezone.localdate() - timedelta(days=days),
        base_amount=amount,
        total_amount=amount,
        status="unpaid",
    )


@pytest.mark.django_db
class TestRuleBasedLateFees:
    def test_active_rule_applies_fixed_fee(self):
        school = SchoolFactory()
        LateFeeRuleFactory(school=school, days_after_due=5, fee_amount=Decimal("75.00"))
        invoice = _overdue_invoice(school, days=10)

        result = mark_overdue_invoices()

        invoice.refresh_from_db()
        assert result["marked_overdue"] == 1
        assert invoice.status == "overdue"
        assert invoice.late_fee == Decimal("75.00")
        assert invoice.total_amount == Decimal("575.00")

    def test_percentage_rule_uses_base_amount(self):
        school = SchoolFactory()
        LateFeeRuleFactory(
            school=school,
            days_after_due=1,
            fee_type="percentage",
            fee_amount=Decimal("0"),
            percentage=Decimal("2.5"),
        )
        invoice = _overdue_invoice(school, days=10, amount=Decimal("800.00"))

        mark_overdue_invoices()

        invoice.refresh_from_db()
        assert invoice.late_fee == Decimal("20.00")  # 2.5% of 800

    def test_max_late_fee_caps_the_charge(self):
        school = SchoolFactory()
        LateFeeRuleFactory(
            school=school,
            days_after_due=1,
            fee_type="percentage",
            fee_amount=Decimal("0"),
            percentage=Decimal("10"),
            max_late_fee=Decimal("50.00"),
        )
        invoice = _overdue_invoice(school, days=10, amount=Decimal("1000.00"))

        mark_overdue_invoices()

        invoice.refresh_from_db()
        assert invoice.late_fee == Decimal("50.00")  # 10% would be 100

    def test_most_severe_eligible_rule_wins(self):
        """The largest days_after_due that has elapsed applies."""
        school = SchoolFactory()
        LateFeeRuleFactory(school=school, days_after_due=1, fee_amount=Decimal("20.00"))
        LateFeeRuleFactory(school=school, days_after_due=7, fee_amount=Decimal("100.00"))
        LateFeeRuleFactory(school=school, days_after_due=30, fee_amount=Decimal("500.00"))
        invoice = _overdue_invoice(school, days=15)

        mark_overdue_invoices()

        invoice.refresh_from_db()
        assert invoice.late_fee == Decimal("100.00")  # 30-day rule not yet earned

    def test_inactive_rule_ignored(self):
        school = SchoolFactory()
        LateFeeRuleFactory(school=school, days_after_due=1, fee_amount=Decimal("99.00"), is_active=False)
        invoice = _overdue_invoice(school, days=10)

        mark_overdue_invoices()

        invoice.refresh_from_db()
        assert invoice.late_fee == Decimal("0")  # no active rules → no fee

    def test_rules_do_not_leak_across_schools(self):
        school_a = SchoolFactory()
        school_b = SchoolFactory()
        LateFeeRuleFactory(school=school_a, days_after_due=1, fee_amount=Decimal("80.00"))
        invoice_b = _overdue_invoice(school_b, days=10)

        mark_overdue_invoices()

        invoice_b.refresh_from_db()
        assert invoice_b.late_fee == Decimal("0")  # B has no rules of its own

    def test_no_rules_falls_back_to_structure_per_day(self):
        school = SchoolFactory()
        structure = FeeStructureFactory(school=school, late_fee_per_day=Decimal("5.00"))
        student = StudentFactory(school=school)
        invoice = FeeInvoiceFactory(
            student=student,
            academic_year=AcademicYearFactory(school=school),
            fee_structure=structure,
            due_date=timezone.localdate() - timedelta(days=3),
            base_amount=Decimal("500.00"),
            total_amount=Decimal("500.00"),
            status="unpaid",
        )

        mark_overdue_invoices()

        invoice.refresh_from_db()
        assert invoice.late_fee == Decimal("15.00")  # 5/day × 3 days

    def test_late_fee_logged_once_in_transaction_log(self):
        school = SchoolFactory()
        LateFeeRuleFactory(school=school, days_after_due=1, fee_amount=Decimal("50.00"))
        invoice = _overdue_invoice(school, days=5)

        mark_overdue_invoices()
        mark_overdue_invoices()  # second run must not re-fee or re-log

        invoice.refresh_from_db()
        from services.fees.models import TransactionLog

        logs = TransactionLog.objects.filter(transaction_id=f"LATE-{invoice.id}")
        assert logs.count() == 1
        assert logs.get().transaction_type == TransactionLog.TransactionType.LATE_FEE
        # Already overdue → not re-processed at all
        assert invoice.late_fee == Decimal("50.00")
