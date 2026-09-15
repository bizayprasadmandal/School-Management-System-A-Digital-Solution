"""Tests for the installment automation task (process_installments).

Pins: pending→overdue transition with the plan's late fee, one-time
TransactionLog audit entry per installment, deduplicated reminders,
completed-plan auto-close, and active plans left alone.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from services.communication.models import Notification
from services.fees.models import InstallmentPayment, InstallmentPlan, TransactionLog
from services.fees.tasks import process_installments
from tests.factories import AcademicYearFactory, FeeInvoiceFactory, FeeStructureFactory, SchoolFactory, StudentFactory


def _make_plan(school, num_installments=2, late_fee=Decimal("25.00"), end_offset_days=-10):
    student = StudentFactory(school=school)
    invoice = FeeInvoiceFactory(
        student=student,
        academic_year=AcademicYearFactory(school=school),
        fee_structure=FeeStructureFactory(school=school),
        base_amount=Decimal("1000.00"),
        total_amount=Decimal("1000.00"),
        status="unpaid",
    )
    plan = InstallmentPlan.objects.create(
        school=school,
        student=student,
        invoice=invoice,
        total_amount=Decimal("1000.00"),
        number_of_installments=num_installments,
        installment_amount=Decimal("500.00"),
        start_date=date.today() - timedelta(days=100),
        end_date=date.today() + timedelta(days=end_offset_days),
        late_fee_per_installment=late_fee,
        status=InstallmentPlan.Status.ACTIVE,
    )
    installments = []
    for n in range(1, num_installments + 1):
        installments.append(
            InstallmentPayment.objects.create(
                installment_plan=plan,
                installment_number=n,
                amount=Decimal("500.00"),
                due_date=date.today() - timedelta(days=10 * n),
                status=InstallmentPayment.Status.PENDING,
            )
        )
    return plan, installments


@pytest.mark.django_db
class TestProcessInstallments:
    def test_pending_becomes_overdue_with_late_fee(self):
        school = SchoolFactory()
        plan, installments = _make_plan(school)

        result = process_installments()

        assert result["overdue_marked"] == 2
        assert result["late_fees_applied"] == 2
        for inst in installments:
            inst.refresh_from_db()
            assert inst.status == InstallmentPayment.Status.OVERDUE
            assert inst.late_fee == Decimal("25.00")

    def test_late_fee_transaction_log_written_once(self):
        school = SchoolFactory()
        plan, installments = _make_plan(school, num_installments=1)

        process_installments()
        process_installments()  # second run must not re-log

        logs = TransactionLog.objects.filter(transaction_id=f"INST-{installments[0].id}")
        assert logs.count() == 1
        assert logs.get().transaction_type == TransactionLog.TransactionType.LATE_FEE

    def test_reminders_sent_once_per_installment(self):
        school = SchoolFactory()
        plan, installments = _make_plan(school, num_installments=1)

        process_installments()

        # Notification rows are written by the (eager) in-app task; dedupe
        # via the reference the task used.
        count = Notification.objects.filter(
            reference_type="installment",
            reference_id=str(installments[0].id),
        ).count()
        assert count >= 1
        process_installments()  # re-run: no duplicate reminders
        count2 = Notification.objects.filter(
            reference_type="installment",
            reference_id=str(installments[0].id),
        ).count()
        assert count2 == count

    def test_paid_installment_untouched(self):
        school = SchoolFactory()
        plan, installments = _make_plan(school, num_installments=1)
        inst = installments[0]
        inst.status = InstallmentPayment.Status.PAID
        inst.save()

        result = process_installments()

        assert result["overdue_marked"] == 0
        inst.refresh_from_db()
        assert inst.status == InstallmentPayment.Status.PAID

    def test_completed_plan_when_all_settled_and_past_end(self):
        school = SchoolFactory()
        plan, installments = _make_plan(school, num_installments=1, end_offset_days=-1)
        inst = installments[0]
        inst.status = InstallmentPayment.Status.PAID
        inst.save()

        result = process_installments()

        assert result["plans_completed"] == 1
        plan.refresh_from_db()
        assert plan.status == InstallmentPlan.Status.COMPLETED

    def test_active_plan_with_unsettled_installments_stays_active(self):
        school = SchoolFactory()
        plan, _ = _make_plan(school, end_offset_days=-1)  # unsettled

        process_installments()

        plan.refresh_from_db()
        assert plan.status == InstallmentPlan.Status.ACTIVE
