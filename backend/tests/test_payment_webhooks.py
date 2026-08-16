"""
Payment webhook verification tests — Stripe (server-to-server webhook with
signature verification) and the Nepali gateways Khalti/eSewa (lookup-based
verify flow that the frontend calls after the gateway redirect).

Each test exercises the full happy/failure path: a pending Payment record is
created, the gateway event/response arrives, and the Payment + FeeInvoice are
updated (successful → paid, failed → failed, unknown → left untouched).
"""

from decimal import Decimal
from unittest import mock
from uuid import uuid4

import pytest
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient
from services.fees.models import FeeInvoice, Payment
from tests.factories import FeeInvoiceFactory
from tests.url_helpers import FEES_NEPALI_REFUND, FEES_NEPALI_VERIFY, FEES_STRIPE_WEBHOOK


@pytest.fixture
def api():
    return APIClient()


def _make_pending_payment(invoice, *, transaction_id, method, amount="500.00"):
    return Payment.objects.create(
        invoice=invoice,
        amount=Decimal(amount),
        payment_method=method,
        status=Payment.Status.PENDING,
        transaction_id=transaction_id,
        receipt_number=f"REC-{uuid4().hex[:10].upper()}",
    )


def _stripe_event(event_type, pi_id, **extra):
    return {
        "type": event_type,
        "data": {"object": {"id": pi_id, **extra}},
    }


@pytest.mark.django_db
class TestStripeWebhook:
    def test_success_event_marks_payment_successful_and_pays_invoice(self, api):
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("0.00"))
        payment = _make_pending_payment(invoice, transaction_id="pi_123", method="online")

        resp = api.post(
            FEES_STRIPE_WEBHOOK,
            _stripe_event("payment_intent.succeeded", "pi_123", amount_received=50000),
            format="json",
        )

        assert resp.status_code == status.HTTP_200_OK
        payment.refresh_from_db()
        assert payment.status == Payment.Status.SUCCESSFUL
        assert payment.paid_at is not None
        assert payment.gateway_response.get("stripe_id") == "pi_123"

        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("500.00")
        assert invoice.status == FeeInvoice.Status.PAID

    def test_success_event_marks_invoice_partial_when_payment_covers_part(self, api):
        invoice = FeeInvoiceFactory(
            total_amount=Decimal("1000.00"),
            paid_amount=Decimal("0.00"),
            status="unpaid",
        )
        _make_pending_payment(invoice, transaction_id="pi_abc", method="online", amount="400.00")

        resp = api.post(
            FEES_STRIPE_WEBHOOK,
            _stripe_event("payment_intent.succeeded", "pi_abc", amount_received=40000),
            format="json",
        )

        assert resp.status_code == status.HTTP_200_OK
        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("400.00")
        assert invoice.status == FeeInvoice.Status.PARTIAL

    def test_failed_event_marks_payment_failed(self, api):
        invoice = FeeInvoiceFactory()
        payment = _make_pending_payment(invoice, transaction_id="pi_bad", method="online")

        resp = api.post(
            FEES_STRIPE_WEBHOOK,
            _stripe_event(
                "payment_intent.payment_failed",
                "pi_bad",
                last_payment_error={"message": "Card declined"},
            ),
            format="json",
        )

        assert resp.status_code == status.HTTP_200_OK
        payment.refresh_from_db()
        assert payment.status == Payment.Status.FAILED
        assert "Card declined" in payment.gateway_response.get("error", "")
        invoice.refresh_from_db()
        assert invoice.status == FeeInvoice.Status.UNPAID

    def test_unknown_payment_intent_is_ignored_gracefully(self, api):
        invoice = FeeInvoiceFactory()
        _make_pending_payment(invoice, transaction_id="pi_known", method="online")

        resp = api.post(
            FEES_STRIPE_WEBHOOK,
            _stripe_event("payment_intent.succeeded", "pi_unknown", amount_received=100),
            format="json",
        )

        assert resp.status_code == status.HTTP_200_OK
        # Existing pending payment untouched, invoice unchanged
        payment = Payment.objects.get(transaction_id="pi_known")
        assert payment.status == Payment.Status.PENDING
        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("0.00")

    @override_settings(STRIPE_WEBHOOK_SECRET="whsec_test_secret")
    def test_invalid_signature_is_rejected(self, api):
        FeeInvoiceFactory()
        resp = api.post(
            FEES_STRIPE_WEBHOOK,
            _stripe_event("payment_intent.succeeded", "pi_x", amount_received=100),
            format="json",
            HTTP_STRIPE_SIGNATURE="bad_signature",
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @override_settings(STRIPE_WEBHOOK_SECRET="", STRIPE_WEBHOOK_REQUIRE_SIGNATURE=True)
    def test_missing_webhook_secret_fails_closed(self, api):
        """No STRIPE_WEBHOOK_SECRET with signature requirement on → webhook rejected (no fail-open)."""
        FeeInvoiceFactory()
        resp = api.post(
            FEES_STRIPE_WEBHOOK,
            _stripe_event("payment_intent.succeeded", "pi_y", amount_received=100),
            format="json",
        )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_amount_mismatch_marks_payment_failed_and_does_not_credit_invoice(self, api):
        """Gateway amount must match Payment.amount (cents) or the payment is rejected."""
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"), paid_amount=Decimal("0.00"))
        _make_pending_payment(invoice, transaction_id="pi_mismatch", method="online", amount="500.00")

        resp = api.post(
            FEES_STRIPE_WEBHOOK,
            _stripe_event("payment_intent.succeeded", "pi_mismatch", amount_received=1000),
            format="json",
        )

        assert resp.status_code == status.HTTP_200_OK
        payment = Payment.objects.get(transaction_id="pi_mismatch")
        assert payment.status == Payment.Status.FAILED
        assert payment.gateway_response.get("status") == "amount_mismatch"
        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("0.00")
        assert invoice.status == FeeInvoice.Status.UNPAID


@pytest.mark.django_db
class TestKhaltiVerify:
    def test_completed_payment_is_marked_successful(self, api):
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"))
        payment = _make_pending_payment(invoice, transaction_id="pidx_1", method="khalti")

        with mock.patch("services.fees.nepali_views.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "status": "Completed",
                "transaction_id": "khalti_txn_1",
                "total_amount": 50000,
            }
            resp = api.post(
                FEES_NEPALI_VERIFY,
                {"gateway": "khalti", "pidx": "pidx_1"},
                format="json",
            )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == "successful"
        assert resp.data["gateway"] == "khalti"
        payment.refresh_from_db()
        assert payment.status == Payment.Status.SUCCESSFUL
        invoice.refresh_from_db()
        assert invoice.status == FeeInvoice.Status.PAID

    def test_non_completed_payment_is_marked_failed(self, api):
        invoice = FeeInvoiceFactory()
        payment = _make_pending_payment(invoice, transaction_id="pidx_2", method="khalti")

        with mock.patch("services.fees.nepali_views.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"status": "Pending"}
            resp = api.post(
                FEES_NEPALI_VERIFY,
                {"gateway": "khalti", "pidx": "pidx_2"},
                format="json",
            )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == "failed"
        payment.refresh_from_db()
        assert payment.status == Payment.Status.FAILED
        invoice.refresh_from_db()
        assert invoice.status == FeeInvoice.Status.UNPAID

    def test_unknown_pidx_returns_404(self, api):
        FeeInvoiceFactory()
        with mock.patch("services.fees.nepali_views.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"status": "Completed"}
            resp = api.post(
                FEES_NEPALI_VERIFY,
                {"gateway": "khalti", "pidx": "pidx_missing"},
                format="json",
            )

        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_gateway_lookup_failure_returns_502(self, api):
        FeeInvoiceFactory()
        # The view catches requests.RequestException (not bare Exception)
        from requests.exceptions import ConnectionError as RequestsConnectionError

        with mock.patch(
            "services.fees.nepali_views.requests.post",
            side_effect=RequestsConnectionError("connection refused"),
        ):
            resp = api.post(
                FEES_NEPALI_VERIFY,
                {"gateway": "khalti", "pidx": "pidx_3"},
                format="json",
            )

        assert resp.status_code == status.HTTP_502_BAD_GATEWAY

    def test_missing_pidx_returns_400(self, api):
        resp = api.post(FEES_NEPALI_VERIFY, {"gateway": "khalti"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_amount_mismatch_marks_payment_failed_and_returns_400(self, api):
        """Khalti's verified total_amount (paisa) must match Payment.amount."""
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"))
        _make_pending_payment(invoice, transaction_id="pidx_mm", method="khalti", amount="500.00")

        with mock.patch("services.fees.nepali_views.requests.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "status": "Completed",
                "transaction_id": "khalti_txn_mm",
                "total_amount": 99999,
            }
            resp = api.post(
                FEES_NEPALI_VERIFY,
                {"gateway": "khalti", "pidx": "pidx_mm"},
                format="json",
            )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        payment = Payment.objects.get(transaction_id="pidx_mm")
        assert payment.status == Payment.Status.FAILED
        assert payment.gateway_response.get("status") == "amount_mismatch"
        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("0.00")


@pytest.mark.django_db
class TestEsewaVerify:
    def test_complete_payment_is_marked_successful(self, api):
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"))
        txn_uuid = str(uuid4())
        payment = _make_pending_payment(invoice, transaction_id=f"ESEWA-{txn_uuid}", method="esewa")

        with mock.patch("services.fees.nepali_views.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "status": "COMPLETE",
                "ref_id": "esewa_ref_1",
                "total_amount": "500.00",
            }
            resp = api.post(
                FEES_NEPALI_VERIFY,
                {"gateway": "esewa", "transaction_uuid": txn_uuid, "total_amount": "500.00"},
                format="json",
            )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == "successful"
        assert resp.data["gateway"] == "esewa"
        payment.refresh_from_db()
        assert payment.status == Payment.Status.SUCCESSFUL
        invoice.refresh_from_db()
        assert invoice.status == FeeInvoice.Status.PAID

    def test_non_complete_payment_is_marked_failed(self, api):
        invoice = FeeInvoiceFactory()
        txn_uuid = str(uuid4())
        payment = _make_pending_payment(invoice, transaction_id=f"ESEWA-{txn_uuid}", method="esewa")

        with mock.patch("services.fees.nepali_views.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"status": "NOT_FOUND"}
            resp = api.post(
                FEES_NEPALI_VERIFY,
                {"gateway": "esewa", "transaction_uuid": txn_uuid, "total_amount": "500.00"},
                format="json",
            )

        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == "failed"
        payment.refresh_from_db()
        assert payment.status == Payment.Status.FAILED

    def test_missing_params_return_400(self, api):
        resp = api.post(FEES_NEPALI_VERIFY, {"gateway": "esewa"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_gateway_returns_400(self, api):
        resp = api.post(
            FEES_NEPALI_VERIFY,
            {"gateway": "paypal", "pidx": "x"},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_amount_mismatch_marks_payment_failed_and_returns_400(self, api):
        """Client-supplied amount is ignored; gateway total must match Payment.amount."""
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"))
        txn_uuid = str(uuid4())
        _make_pending_payment(invoice, transaction_id=f"ESEWA-{txn_uuid}", method="esewa", amount="500.00")

        with mock.patch("services.fees.nepali_views.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "status": "COMPLETE",
                "ref_id": "esewa_ref_mm",
                "total_amount": "999.00",
            }
            resp = api.post(
                FEES_NEPALI_VERIFY,
                {"gateway": "esewa", "transaction_uuid": txn_uuid, "total_amount": "500.00"},
                format="json",
            )

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        payment = Payment.objects.get(transaction_id=f"ESEWA-{txn_uuid}")
        assert payment.status == Payment.Status.FAILED
        assert payment.gateway_response.get("gateway_status") == "amount_mismatch"
        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("0.00")

    def test_spoofed_client_amount_does_not_change_status_api_amount(self, api):
        """The amount sent to the eSewa status API comes from our records."""
        invoice = FeeInvoiceFactory(total_amount=Decimal("500.00"))
        txn_uuid = str(uuid4())
        _make_pending_payment(invoice, transaction_id=f"ESEWA-{txn_uuid}", method="esewa", amount="500.00")

        with mock.patch("services.fees.nepali_views.requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "status": "COMPLETE",
                "ref_id": "esewa_ref_ok",
                "total_amount": "500.00",
            }
            resp = api.post(
                FEES_NEPALI_VERIFY,
                {"gateway": "esewa", "transaction_uuid": txn_uuid, "total_amount": "1.00"},
                format="json",
            )

            # The status API must be queried with the server-side amount.
            _, kwargs = mock_get.call_args
            assert kwargs["params"]["total_amount"] == "500"

        assert resp.status_code == status.HTTP_200_OK
        payment = Payment.objects.get(transaction_id=f"ESEWA-{txn_uuid}")
        assert payment.status == Payment.Status.SUCCESSFUL


@pytest.mark.django_db(transaction=True)
class TestConcurrentProcessing:
    """The verify/refund flows must credit/debit each invoice exactly once,
    even when two requests race with the same transaction id."""

    def _race(self, func, n=2, timeout=120):
        import threading

        from django.db import connections

        barrier = threading.Barrier(n)
        results = {}

        def _run(i):
            barrier.wait(timeout=timeout)
            try:
                results[i] = func()
            except Exception as exc:  # noqa: BLE001 - surfaced via the assertions below
                results[i] = exc
            finally:
                # Close only this thread's DB connections so racing requests
                # can't leak connections past test teardown (and so pytest
                # doesn't report unhandled thread exceptions on run exit).
                thread_id = threading.get_ident()
                for conn in connections.all():
                    if getattr(conn, "_thread_ident", None) == thread_id:
                        conn.close()

        threads = [threading.Thread(target=_run, args=(i,), name=f"race-{i}") for i in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=timeout)
        return results

    def _assert_no_thread_errors(self, results):
        errors = {k: v for k, v in results.items() if isinstance(v, Exception)}
        assert not errors, f"race thread(s) raised: {errors}"

    def test_concurrent_khalti_verify_credits_invoice_once(self):
        """Two simultaneous verify calls with the same pidx must not double-credit."""
        from services.fees.nepali_views import _mark_payment_successful

        invoice = FeeInvoiceFactory(total_amount=Decimal("1000.00"), paid_amount=Decimal("0.00"), status="unpaid")
        payment = _make_pending_payment(invoice, transaction_id="pidx_race", method="khalti", amount="500.00")

        def call():
            return _mark_payment_successful(
                payment,
                {"khalti_pidx": "pidx_race", "transaction_id": "txn_race", "status": "Completed"},
            )

        results = self._race(call)

        self._assert_no_thread_errors(results)
        assert sum(results.values()) == 1  # exactly one caller performed the transition
        payment.refresh_from_db()
        invoice.refresh_from_db()
        assert payment.status == Payment.Status.SUCCESSFUL
        assert invoice.paid_amount == Decimal("500.00")  # credited exactly once

    def test_concurrent_esewa_verify_credits_invoice_once(self):
        from services.fees.nepali_views import _mark_payment_successful

        invoice = FeeInvoiceFactory(total_amount=Decimal("1000.00"), paid_amount=Decimal("0.00"), status="unpaid")
        payment = _make_pending_payment(invoice, transaction_id="ESEWA-race", method="esewa", amount="400.00")

        def call():
            return _mark_payment_successful(
                payment,
                {"esewa_transaction_uuid": "race", "esewa_ref_id": "ref", "status": "COMPLETE"},
            )

        results = self._race(call)

        self._assert_no_thread_errors(results)
        assert sum(results.values()) == 1
        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("400.00")

    def test_concurrent_stripe_webhook_credits_invoice_once(self):
        invoice = FeeInvoiceFactory(total_amount=Decimal("1000.00"), paid_amount=Decimal("0.00"), status="unpaid")
        _make_pending_payment(invoice, transaction_id="pi_race", method="online", amount="500.00")

        def call():
            from rest_framework.test import APIClient

            client = APIClient()
            resp = client.post(
                FEES_STRIPE_WEBHOOK,
                _stripe_event("payment_intent.succeeded", "pi_race", amount_received=50000),
                format="json",
            )
            return resp.status_code

        results = self._race(call)
        self._assert_no_thread_errors(results)
        assert set(results.values()) == {status.HTTP_200_OK}

        invoice.refresh_from_db()
        assert invoice.paid_amount == Decimal("500.00")  # credited exactly once

    def test_concurrent_refund_debits_invoice_once(self):
        """Two racing refunds for the same successful payment must not double-refund."""
        from rest_framework.test import APIClient
        from tests.factories import AdminUserFactory

        admin = AdminUserFactory()
        invoice = FeeInvoiceFactory(
            total_amount=Decimal("1000.00"),
            paid_amount=Decimal("500.00"),
            status="partial",
            student__school=admin.school,
        )
        payment = _make_pending_payment(invoice, transaction_id="pidx_refund_race", method="khalti", amount="500.00")
        payment.status = Payment.Status.SUCCESSFUL
        payment.save(update_fields=["status"])

        def call():
            with mock.patch("services.fees.nepali_views.requests.post") as mock_post:
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = {"refund": {"state": "completed"}}
                client = APIClient()
                client.force_authenticate(user=admin)
                resp = client.post(
                    FEES_NEPALI_REFUND,
                    {"payment_id": str(payment.id)},
                    format="json",
                )
                return resp.status_code

        results = self._race(call)
        self._assert_no_thread_errors(results)

        # Exactly one request executes the refund (200); the loser is rejected
        # with 400 because the payment is already REFUNDED inside the lock.
        assert list(results.values()).count(status.HTTP_200_OK) == 1
        assert list(results.values()).count(status.HTTP_400_BAD_REQUEST) == 1
        payment.refresh_from_db()
        invoice.refresh_from_db()
        assert payment.status == Payment.Status.REFUNDED
        assert invoice.paid_amount == Decimal("0.00")  # debited exactly once
