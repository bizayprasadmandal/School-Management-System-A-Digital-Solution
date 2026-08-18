"""Payment receipt notification tests.

Covers the transition-based receipt signal (services/fees/signals.py): gateway
payments (Stripe/Khalti/eSewa) are created PENDING and flipped to SUCCESSFUL by
the webhook/verify handler, so the old ``created and status == successful``
gate silently skipped every online receipt. The signal must fire on the
transition itself, exactly once per payment, and must never break the payment
write.
"""

from contextlib import contextmanager
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone
from services.fees.models import Payment
from tests.factories import FeeInvoiceFactory


@pytest.mark.django_db
class TestPaymentReceiptNotifications:
    def _invoice(self):
        return FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("0.00"))

    @contextmanager
    def _receipt_patches(self):
        with (
            patch("services.communication.services.send_in_app_notification") as mock_inapp,
            patch("services.communication.services.send_email_notification") as mock_email,
        ):
            yield mock_inapp, mock_email

    def _assert_sent_once(self, mock_inapp, mock_email, payment):
        mock_inapp.delay.assert_called_once()
        mock_email.delay.assert_called_once()
        payment.refresh_from_db()
        assert payment.receipt_sent_at is not None

    def test_gateway_payment_flip_sends_receipt(self):
        """A payment created PENDING then flipped SUCCESSFUL gets a receipt."""
        invoice = self._invoice()
        payment = Payment.objects.create(
            invoice=invoice,
            amount=Decimal("500.00"),
            payment_method="online",
            status=Payment.Status.PENDING,
            receipt_number="STRIPE-TEST0001",
        )

        with self._receipt_patches() as (mock_inapp, mock_email):
            payment.status = Payment.Status.SUCCESSFUL
            payment.paid_at = timezone.now()
            payment.save(update_fields=["status", "paid_at"])

        self._assert_sent_once(mock_inapp, mock_email, payment)

    def test_manual_payment_create_sends_receipt(self):
        """A manual/cash payment created directly as successful gets a receipt."""
        with self._receipt_patches() as (mock_inapp, mock_email):
            payment = Payment.objects.create(
                invoice=self._invoice(),
                amount=Decimal("500.00"),
                payment_method="cash",
                status=Payment.Status.SUCCESSFUL,
                paid_at=timezone.now(),
                receipt_number="RCP-TEST0001",
            )

        self._assert_sent_once(mock_inapp, mock_email, payment)

    def test_resave_of_successful_payment_does_not_resend(self):
        """Re-saving an already-successful payment must not duplicate receipts."""
        with self._receipt_patches() as (mock_inapp, mock_email):
            payment = Payment.objects.create(
                invoice=self._invoice(),
                amount=Decimal("500.00"),
                payment_method="cash",
                status=Payment.Status.SUCCESSFUL,
                paid_at=timezone.now(),
                receipt_number="RCP-TEST0002",
            )
            payment.notes = "edited later"
            payment.save(update_fields=["notes"])

        mock_inapp.delay.assert_called_once()
        mock_email.delay.assert_called_once()

    def test_refund_transition_does_not_resend_receipt(self):
        """Moving a successful payment to REFUNDED must not re-send a receipt."""
        invoice = self._invoice()
        with self._receipt_patches() as (mock_inapp, mock_email):
            payment = Payment.objects.create(
                invoice=invoice,
                amount=Decimal("500.00"),
                payment_method="online",
                status=Payment.Status.PENDING,
                receipt_number="STRIPE-TEST0003",
            )
            # Gateway flip → receipt sent once.
            payment.status = Payment.Status.SUCCESSFUL
            payment.paid_at = timezone.now()
            payment.save(update_fields=["status", "paid_at"])
            # Refund → must not send a second receipt.
            payment.status = Payment.Status.REFUNDED
            payment.save(update_fields=["status"])

        mock_inapp.delay.assert_called_once()
        mock_email.delay.assert_called_once()

    def test_failed_payment_flip_does_not_send_receipt(self):
        """PENDING -> FAILED must never fire the receipt signal."""
        with self._receipt_patches() as (mock_inapp, mock_email):
            payment = Payment.objects.create(
                invoice=self._invoice(),
                amount=Decimal("500.00"),
                payment_method="online",
                status=Payment.Status.PENDING,
                receipt_number="STRIPE-TEST0002",
            )
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status"])

        mock_inapp.delay.assert_not_called()
        mock_email.delay.assert_not_called()

    def test_notification_failure_does_not_break_payment_write(self):
        """A raising notification task must not roll back the payment save."""
        invoice = self._invoice()
        with self._receipt_patches() as (mock_inapp, mock_email):
            mock_inapp.delay.side_effect = RuntimeError("broker down")
            mock_email.delay.side_effect = RuntimeError("broker down")
            payment = Payment.objects.create(
                invoice=invoice,
                amount=Decimal("500.00"),
                payment_method="cash",
                status=Payment.Status.SUCCESSFUL,
                paid_at=timezone.now(),
                receipt_number="RCP-TEST0004",
            )

        # Payment write succeeded and the receipt was marked attempted.
        payment.refresh_from_db()
        assert payment.status == Payment.Status.SUCCESSFUL
        assert payment.receipt_sent_at is not None

    def test_receipt_message_references_invoice_and_receipt(self):
        """The receipt body names the invoice number and receipt number."""
        invoice = self._invoice()
        with self._receipt_patches() as (mock_inapp, mock_email):
            Payment.objects.create(
                invoice=invoice,
                amount=Decimal("500.00"),
                payment_method="cash",
                status=Payment.Status.SUCCESSFUL,
                paid_at=timezone.now(),
                receipt_number="RCP-TEST0005",
            )

        call_kwargs = mock_inapp.delay.call_args.kwargs
        assert call_kwargs["title"] == "Payment Confirmed"
        assert invoice.invoice_number in call_kwargs["body"]
        assert "RCP-TEST0005" in call_kwargs["body"]
        assert mock_email.delay.call_args.kwargs["subject"] == "Payment Receipt — RCP-TEST0005"
