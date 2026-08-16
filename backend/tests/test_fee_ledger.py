"""Unit tests for the shared invoice ledger helpers (services/fees/ledger.py).

The credit/debit behavior was previously copy-pasted across the manual
payment create view, the Stripe webhook/refund views, and the Khalti/eSewa
verify/refund views; these tests pin the shared semantics so a future change
in one path cannot silently break another.
"""

from decimal import Decimal

import pytest
from services.fees.ledger import credit_invoice, debit_invoice
from services.fees.models import FeeInvoice
from tests.factories import FeeInvoiceFactory


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

        threads = [threading.Thread(target=_run, args=(i,)) for i in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(not isinstance(v, Exception) for v in results.values())
        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("600.00")
        assert invoice.status == FeeInvoice.Status.PARTIAL
