"""Tests for the monthly RevenueReport snapshot task.

Pins: per-school report generation for the previous month, aggregation of
payments/refunds/outstanding, breakdown dicts, idempotency (one report per
school per period), and explicit year/month overrides.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from services.auth.models import School
from services.fees.models import Payment, RevenueReport, TransactionLog
from services.fees.tasks import generate_monthly_revenue_report
from tests.factories import (
    AcademicYearFactory,
    FeeInvoiceFactory,
    FeeStructureFactory,
    PaymentFactory,
    SchoolFactory,
    StudentFactory,
)


def _make_invoice(school, amount=Decimal("500.00"), **structure_kwargs):
    student = StudentFactory(school=school)
    return FeeInvoiceFactory(
        student=student,
        academic_year=AcademicYearFactory(school=school),
        fee_structure=FeeStructureFactory(school=school, **structure_kwargs),
        base_amount=amount,
        total_amount=amount,
        status="unpaid",
    )


@pytest.mark.django_db
class TestMonthlyRevenueReport:
    def test_generates_report_for_previous_month(self):
        school = SchoolFactory()
        last_month_end = timezone.now().date().replace(day=1) - timedelta(days=1)
        invoice = _make_invoice(school, amount=Decimal("500.00"))
        payment = PaymentFactory(
            invoice=invoice,
            amount=Decimal("500.00"),
            status=Payment.Status.SUCCESSFUL,
            paid_at=timezone.make_aware(timezone.datetime(last_month_end.year, last_month_end.month, 15, 12, 0)),
        )
        # Simulate the audit trail the ledger writes on refunds.
        refund_log = TransactionLog.objects.create(
            school=school,
            transaction_type=TransactionLog.TransactionType.REFUND,
            transaction_id="RFD-test-1",
            student=invoice.student,
            amount=Decimal("100.00"),
        )
        # Backdate into the report window (created_at is auto_now_add; in
        # production the ledger writes the log at refund time).
        TransactionLog.objects.filter(pk=refund_log.pk).update(
            created_at=timezone.make_aware(timezone.datetime(last_month_end.year, last_month_end.month, 20, 14, 0))
        )

        result = generate_monthly_revenue_report()

        assert result["reports_created"] >= 1  # ≥1: other schools may exist in the shared test DB
        report = RevenueReport.objects.get(school=school, report_type="monthly")
        assert report.period_start == date(last_month_end.year, last_month_end.month, 1)
        assert report.period_end == last_month_end
        assert report.total_collected == Decimal("500.00")
        assert report.total_refunded == Decimal("100.00")
        assert report.status == RevenueReport.Status.GENERATED
        assert "500.00" in report.summary

        _ = payment  # silence unused-var lints

    def test_breakdowns_populated(self):
        school = SchoolFactory()
        last_month_end = timezone.now().date().replace(day=1) - timedelta(days=1)
        invoice = _make_invoice(school)
        PaymentFactory(
            invoice=invoice,
            amount=Decimal("500.00"),
            payment_method="khalti",
            status=Payment.Status.SUCCESSFUL,
            paid_at=timezone.make_aware(timezone.datetime(last_month_end.year, last_month_end.month, 10, 9, 0)),
        )

        generate_monthly_revenue_report()

        report = RevenueReport.objects.get(school=school, report_type="monthly")
        assert report.collection_by_payment_method.get("khalti") == 500.0
        assert sum(report.collection_by_category.values()) == 500.0
        assert sum(report.collection_by_grade.values()) == 500.0

    def test_idempotent_one_report_per_school_per_period(self):
        school = SchoolFactory()

        generate_monthly_revenue_report()
        generate_monthly_revenue_report()

        assert RevenueReport.objects.filter(school=school, report_type="monthly").count() == 1

    def test_per_school_isolation(self):
        school_a = SchoolFactory()
        school_b = SchoolFactory()
        invoice_a = _make_invoice(school_a, amount=Decimal("700.00"))
        PaymentFactory(
            invoice=invoice_a,
            amount=Decimal("700.00"),
            status=Payment.Status.SUCCESSFUL,
            paid_at=timezone.make_aware(timezone.datetime(2026, 8, 15, 10, 0)),
        )

        generate_monthly_revenue_report(year=2026, month=8)

        # One report row per school per period, with isolated totals.
        report_a = RevenueReport.objects.get(school=school_a, period_start=date(2026, 8, 1))
        report_b = RevenueReport.objects.get(school=school_b, period_start=date(2026, 8, 1))
        assert report_a.total_collected == Decimal("700.00")
        assert report_b.total_collected == Decimal("0")  # B collected nothing

    def test_pending_payments_excluded(self):
        school = SchoolFactory()
        last_month_end = timezone.now().date().replace(day=1) - timedelta(days=1)
        invoice = _make_invoice(school)
        PaymentFactory(
            invoice=invoice,
            amount=Decimal("500.00"),
            status=Payment.Status.PENDING,
            paid_at=timezone.make_aware(timezone.datetime(last_month_end.year, last_month_end.month, 12, 8, 0)),
        )

        generate_monthly_revenue_report()

        report = RevenueReport.objects.get(school=school, report_type="monthly")
        assert report.total_collected == Decimal("0")

    def test_no_active_schools_is_safe(self):
        School.objects.all().delete()
        result = generate_monthly_revenue_report(year=2026, month=8)
        assert result["reports_created"] == 0
