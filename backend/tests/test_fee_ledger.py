"""Unit tests for the shared invoice ledger helpers (services/fees/ledger.py).

The credit/debit behavior was previously copy-pasted across the manual
payment create view, the Stripe webhook/refund views, and the Khalti/eSewa
verify/refund views; these tests pin the shared semantics so a future change
in one path cannot silently break another.
"""

from decimal import Decimal

import pytest
from django.utils import timezone
from services.fees.ledger import credit_invoice, debit_invoice
from services.fees.models import AccountingEntry, FeeInvoice, RefundRecord, TransactionLog
from tests.factories import AdminUserFactory, FeeInvoiceFactory, PaymentFactory


@pytest.mark.django_db
class TestCreditInvoice:
    def test_full_payment_marks_invoice_paid(self):
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("0.00"))
        locked = credit_invoice(invoice, Decimal("500.00"))

        assert locked.paid_amount == Decimal("500.00")
        assert locked.status == FeeInvoice.Status.PAID

    def test_partial_payment_marks_invoice_partial(self):
        invoice = FeeInvoiceFactory(total_amount=Decimal("1000.00"), paid_amount=Decimal("0.00"))
        locked = credit_invoice(invoice, Decimal("400.00"))

        assert locked.paid_amount == Decimal("400.00")
        assert locked.status == FeeInvoice.Status.PARTIAL

    def test_accumulated_credits_can_cross_total(self):
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("300.00"))
        locked = credit_invoice(invoice, Decimal("300.00"))

        assert locked.paid_amount == Decimal("600.00")
        assert locked.status == FeeInvoice.Status.PAID

    def test_refunded_invoice_credit_flips_back_to_partial(self):
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("500.00"))
        debit_invoice(invoice, Decimal("500.00"))
        locked = credit_invoice(invoice, Decimal("200.00"))

        assert locked.paid_amount == Decimal("200.00")
        assert locked.status == FeeInvoice.Status.PARTIAL


@pytest.mark.django_db
class TestDebitInvoice:
    def test_full_refund_marks_invoice_unpaid(self):
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("500.00"))
        locked = debit_invoice(invoice, Decimal("500.00"))

        assert locked.paid_amount == Decimal("0.00")
        assert locked.status == FeeInvoice.Status.UNPAID

    def test_partial_refund_marks_invoice_partial(self):
        invoice = FeeInvoiceFactory(total_amount=Decimal("1000.00"), paid_amount=Decimal("800.00"))
        locked = debit_invoice(invoice, Decimal("500.00"))

        assert locked.paid_amount == Decimal("300.00")
        assert locked.status == FeeInvoice.Status.PARTIAL

    def test_refund_never_goes_negative(self):
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("300.00"))
        locked = debit_invoice(invoice, Decimal("500.00"))

        assert locked.paid_amount == Decimal("0.00")
        assert locked.status == FeeInvoice.Status.UNPAID

    def test_overpayment_refund_keeps_paid(self):
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("600.00"))
        locked = debit_invoice(invoice, Decimal("100.00"))

        assert locked.paid_amount == Decimal("500.00")
        assert locked.status == FeeInvoice.Status.PAID


@pytest.mark.django_db
class TestAuditTrail:
    def test_credit_with_payment_writes_transaction_log_and_revenue_entry(self):
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("0.00"))
        payment = PaymentFactory(invoice=invoice, amount=Decimal("500.00"))
        user = AdminUserFactory(school=invoice.student.school)

        credit_invoice(invoice, payment.amount, payment=payment, user=user)

        log = TransactionLog.objects.get(transaction_id=f"PAY-{payment.id}")
        assert log.transaction_type == TransactionLog.TransactionType.PAYMENT
        assert log.amount == payment.amount
        assert log.school_id == invoice.student.school_id
        assert log.student_id == invoice.student_id
        assert log.reference_number == payment.receipt_number

        entry = AccountingEntry.objects.get(reference_type="payment", reference_id=str(payment.id))
        assert entry.entry_type == AccountingEntry.EntryType.CREDIT
        assert entry.amount == payment.amount
        assert entry.account_code == "4000"
        assert entry.created_by == user

    def test_debit_with_payment_writes_refund_record_and_reversal(self):
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("500.00"))
        payment = PaymentFactory(invoice=invoice, amount=Decimal("500.00"))
        user = AdminUserFactory(school=invoice.student.school)

        debit_invoice(invoice, payment.amount, payment=payment, reason="Duplicate payment", user=user)

        log = TransactionLog.objects.get(transaction_id=f"RFD-{payment.id}")
        assert log.transaction_type == TransactionLog.TransactionType.REFUND
        assert log.amount == payment.amount

        refund = RefundRecord.objects.get(payment=payment)
        assert refund.amount == payment.amount
        assert refund.status == RefundRecord.Status.PROCESSED
        assert refund.student == invoice.student
        assert refund.approved_by == user
        assert refund.processed_date == timezone.now().date()

        entry = AccountingEntry.objects.get(reference_type="refund", reference_id=str(payment.id))
        assert entry.entry_type == AccountingEntry.EntryType.DEBIT
        assert entry.amount == payment.amount

    def test_audit_writes_are_idempotent_on_repeat(self):
        """Webhook retries / duplicate verifies must not double-log."""
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("0.00"))
        payment = PaymentFactory(invoice=invoice, amount=Decimal("200.00"))

        credit_invoice(invoice, Decimal("200.00"), payment=payment)
        credit_invoice(invoice, Decimal("200.00"), payment=payment)

        assert TransactionLog.objects.filter(transaction_id=f"PAY-{payment.id}").count() == 1
        assert AccountingEntry.objects.filter(reference_type="payment", reference_id=str(payment.id)).count() == 1

    def test_ledger_without_payment_skips_audit_writes(self):
        """Seeders call the ledger without a payment — no audit rows."""
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("0.00"))

        credit_invoice(invoice, Decimal("100.00"))
        debit_invoice(invoice, Decimal("50.00"))

        assert TransactionLog.objects.count() == 0
        assert AccountingEntry.objects.count() == 0
        assert RefundRecord.objects.count() == 0


@pytest.mark.django_db(transaction=True)
class TestLedgerRowLocking:
    def test_concurrent_credits_serialize(self):
        """Two racing credits against the same invoice must both land."""
        import threading

        invoice = FeeInvoiceFactory(total_amount=Decimal("1000.00"), paid_amount=Decimal("0.00"))
        results = {}

        def _run(i):
            try:
                results[i] = credit_invoice(invoice, Decimal("300.00")).paid_amount
            except Exception as exc:  # noqa: BLE001 - surfaced via assertion
                results[i] = exc
            finally:
                # Close only this thread's DB connections so racing credits
                # can't leak connections past test teardown.
                from django.db import connections

                thread_id = threading.get_ident()
                for conn in connections.all():
                    if getattr(conn, "_thread_ident", None) == thread_id:
                        conn.close()

        threads = [threading.Thread(target=_run, args=(i,)) for i in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(not isinstance(v, Exception) for v in results.values())
        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("600.00")
        assert invoice.status == FeeInvoice.Status.PARTIAL
