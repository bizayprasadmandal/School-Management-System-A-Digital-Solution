/**
 * PayFeeModal — Stripe Payment Modal for parents
 *
 * Fetches a PaymentIntent client_secret from the backend, renders
 * Stripe Elements for card payment, and handles the confirm/cancel flow.
 */
import React, { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { loadStripe } from "@stripe/stripe-js";
import {
  Elements,
  PaymentElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";
import { api } from "../../api/client";
import { Modal, Button } from "./index";
import toast from "react-hot-toast";
import {
  CreditCardIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";
import { currency } from "../../utils";
import type { FeeInvoice } from "../../types";

// ─── Types ──────────────────────────────────────────────────────────────────

interface CreateIntentResponse {
  client_secret: string;
  publishable_key: string;
  amount: number;
  invoice_id: string;
  payment_intent_id: string;
}

interface PayFeeModalProps {
  invoice: FeeInvoice;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

// ─── Static Stripe promise (lazy-loaded) ─────────────────────────────────────

let stripePromise: ReturnType<typeof loadStripe> | null = null;

function getStripePromise(publishableKey: string) {
  if (!stripePromise) {
    stripePromise = loadStripe(publishableKey);
  }
  return stripePromise;
}

// ─── Inner Payment Form ──────────────────────────────────────────────────────

function PaymentForm({
  clientSecret: _clientSecret,
  invoice,
  onSuccess,
  onClose,
}: {
  clientSecret: string;
  invoice: FeeInvoice;
  onSuccess: () => void;
  onClose: () => void;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState<string>("");
  const [processing, setProcessing] = useState(false);
  const [succeeded, setSucceeded] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!stripe || !elements) return;

    setProcessing(true);
    setError("");

    const { error: submitError } = await elements.submit();
    if (submitError) {
      setError(submitError.message ?? "Validation failed.");
      setProcessing(false);
      return;
    }

    const { error: confirmError } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/parent/fees`,
      },
      redirect: "if_required",
    });

    if (confirmError) {
      setError(confirmError.message ?? "Payment failed.");
      setProcessing(false);
      return;
    }

    // Payment succeeded (no redirect needed for cards that complete immediately)
    setSucceeded(true);
    setProcessing(false);
    toast.success("Payment successful!");
    setTimeout(() => {
      onSuccess();
      onClose();
    }, 1500);
  };

  if (succeeded) {
    return (
      <div className="flex flex-col items-center py-8 text-center">
        <div className="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center mb-4">
          <CheckCircleIcon className="h-8 w-8 text-green-600" />
        </div>
        <h3 className="text-lg font-bold text-slate-900">Payment Successful!</h3>
        <p className="text-sm text-slate-500 mt-1">
          Your payment of {currency(invoice.outstanding_amount)} for invoice {invoice.invoice_number} has been processed.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Invoice summary */}
      <div className="rounded-lg bg-slate-50 p-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Invoice</span>
          <span className="font-mono font-medium text-slate-900">{invoice.invoice_number}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Total</span>
          <span className="font-medium text-slate-900">{currency(invoice.total_amount)}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Already Paid</span>
          <span className="font-medium text-green-600">{currency(invoice.paid_amount)}</span>
        </div>
        <div className="flex justify-between text-sm font-semibold border-t border-slate-200 pt-2">
          <span>Amount Due Now</span>
          <span className="text-lg text-red-600">{currency(invoice.outstanding_amount)}</span>
        </div>
      </div>

      {/* Payment element */}
      <div className="rounded-lg border border-slate-200 p-4">
        <PaymentElement />
      </div>

      {/* Security badge */}
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <ShieldCheckIcon className="h-4 w-4 text-green-500" />
        Secured by Stripe — your card details are encrypted
      </div>

      {/* Error message */}
      {error && (
        <div className="flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <ExclamationTriangleIcon className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onClose} disabled={processing}>
          Cancel
        </Button>
        <Button
          type="submit"
          variant="primary"
          disabled={!stripe || processing}
          loading={processing}
          leftIcon={<CreditCardIcon className="h-4 w-4" />}
        >
          {processing ? "Processing…" : `Pay ${currency(invoice.outstanding_amount)}`}
        </Button>
      </div>
    </form>
  );
}

// ─── PayFeeModal (outer shell with Elements provider) ────────────────────────

export default function PayFeeModal({ invoice, open, onClose, onSuccess }: PayFeeModalProps) {
  const [intentData, setIntentData] = useState<CreateIntentResponse | null>(null);
  const [loadingIntent, setLoadingIntent] = useState(false);
  const [intentError, setIntentError] = useState("");

  // Create PaymentIntent when modal opens
  const createIntent = useMutation({
    mutationFn: () =>
      api.post<CreateIntentResponse>("/fees/stripe/create-payment-intent/", {
        invoice_id: invoice.id,
      }),
    onSuccess: (data) => {
      setIntentData(data);
      setLoadingIntent(false);
    },
    onError: (err: any) => {
      setIntentError(err?.message || "Failed to initialize payment. Please try again.");
      setLoadingIntent(false);
    },
  });

  // Trigger intent creation when modal opens
  React.useEffect(() => {
    if (open && !intentData && !loadingIntent) {
      setLoadingIntent(true);
      setIntentError("");
      createIntent.mutate();
    }
  }, [open]);

  // Reset state when modal closes
  const handleClose = () => {
    setIntentData(null);
    setIntentError("");
    onClose();
  };

  const handleSuccess = () => {
    setIntentData(null);
    onSuccess();
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Pay Invoice"
      description={`${invoice.invoice_number} — ${currency(invoice.outstanding_amount)} due`}
      size="md"
    >
      {loadingIntent ? (
        <div className="flex flex-col items-center py-12 text-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-4" />
          <p className="text-sm text-slate-500">Initializing payment…</p>
        </div>
      ) : intentError ? (
        <div className="flex flex-col items-center py-8 text-center">
          <div className="h-14 w-14 rounded-full bg-red-100 flex items-center justify-center mb-3">
            <ExclamationTriangleIcon className="h-7 w-7 text-red-600" />
          </div>
          <p className="text-sm font-medium text-red-700">{intentError}</p>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              setLoadingIntent(true);
              setIntentError("");
              createIntent.mutate();
            }}
            className="mt-4"
          >
            Try Again
          </Button>
        </div>
      ) : intentData ? (
        <Elements
          stripe={getStripePromise(intentData.publishable_key)}
          options={{
            clientSecret: intentData.client_secret,
            appearance: {
              theme: "stripe",
              variables: {
                colorPrimary: "#6366f1",
                borderRadius: "8px",
              },
            },
          }}
        >
          <PaymentForm
            clientSecret={intentData.client_secret}
            invoice={invoice}
            onSuccess={handleSuccess}
            onClose={handleClose}
          />
        </Elements>
      ) : null}
    </Modal>
  );
}
