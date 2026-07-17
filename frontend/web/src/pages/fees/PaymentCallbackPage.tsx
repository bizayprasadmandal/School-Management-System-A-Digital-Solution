/**
 * PaymentCallbackPage — Handles redirect from Khalti/eSewa
 *
 * After a user completes payment on Khalti or eSewa, the gateway
 * redirects back to this page. This page reads the gateway query
 * params, calls the backend to verify the payment, and shows the
 * result to the user.
 */
import React, { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { api } from "../../api/client";
import { useTitle } from "../../hooks";
import { useAuthStore } from "../../store/authStore";
import toast from "react-hot-toast";
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowLeftIcon,
} from "@heroicons/react/24/outline";

interface VerifyResult {
  status: "successful" | "failed";
  receipt_number: string;
  invoice_id: string;
  gateway: string;
  detail?: string;
}

type PageState =
  | { status: "verifying" }
  | { status: "success"; receipt: string; gateway: string; invoiceId: string }
  | { status: "failed"; detail: string; gateway: string }
  | { status: "error"; detail: string };

export default function PaymentCallbackPage() {
  useTitle("Payment Status");
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [state, setState] = useState<PageState>({ status: "verifying" });
  const [elapsed, setElapsed] = useState(0);

  const { user } = useAuthStore();
  const gateway = searchParams.get("gateway") || "";
  const invoiceId = searchParams.get("invoice_id") || "";

  // Determine role-appropriate fees page
  const feesPath = user?.role === "student" ? "/student/fees" : "/parent/fees";

  // Verify payment on mount
  useEffect(() => {
    if (!gateway || !invoiceId) {
      setState({
        status: "error",
        detail: "Invalid callback: missing gateway or invoice information.",
      });
      return;
    }

    const verifyPayment = async () => {
      try {
        let payload: Record<string, string> = { gateway };

        if (gateway === "khalti") {
          const pidx = searchParams.get("pidx") || "";
          if (!pidx) {
            setState({
              status: "error",
              detail: "Missing payment identifier from Khalti.",
            });
            return;
          }
          payload.pidx = pidx;
        } else if (gateway === "esewa") {
          const transactionUuid = searchParams.get("transaction_uuid") || "";
          const totalAmount = searchParams.get("total_amount") || "";
          if (!transactionUuid || !totalAmount) {
            setState({
              status: "error",
              detail: "Missing transaction details from eSewa.",
            });
            return;
          }
          payload.transaction_uuid = transactionUuid;
          payload.total_amount = totalAmount;
        } else {
          setState({
            status: "error",
            detail: `Unknown gateway: ${gateway}`,
          });
          return;
        }

        const result = await api.post<VerifyResult>(
          "/fees/nepali/verify/",
          payload,
        );

        if (result.status === "successful") {
          setState({
            status: "success",
            receipt: result.receipt_number,
            gateway: result.gateway,
            invoiceId: result.invoice_id,
          });
          toast.success("Payment successful!");
        } else {
          setState({
            status: "failed",
            detail: result.detail || "Payment was not completed.",
            gateway: result.gateway,
          });
          toast.error(result.detail || "Payment failed.");
        }
      } catch (err: any) {
        setState({
          status: "error",
          detail: err?.message || "Failed to verify payment. Please contact support.",
        });
        toast.error("Payment verification failed.");
      }
    };

    verifyPayment();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Timer for elapsed time
  useEffect(() => {
    if (state.status !== "verifying") return;
    const interval = setInterval(() => setElapsed((s) => s + 1), 1000);
    return () => clearInterval(interval);
  }, [state.status]);

  const gatewayName = gateway === "khalti" ? "Khalti" : gateway === "esewa" ? "eSewa" : gateway;

  // ── Render States ──────────────────────────────────────────────────────────

  if (state.status === "verifying") {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center max-w-sm">
          <div className="h-16 w-16 rounded-full bg-indigo-100 flex items-center justify-center mx-auto mb-5">
            <ClockIcon className="h-8 w-8 text-indigo-600 animate-pulse" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">
            Verifying Payment
          </h2>
          <p className="text-sm text-slate-500 mt-2">
            Please wait while we verify your payment with {gatewayName}...
          </p>
          {elapsed > 10 && (
            <p className="text-xs text-slate-400 mt-3">
              Taking longer than usual. This doesn&apos;t mean your payment failed —
              we&apos;ll notify you of the result.
            </p>
          )}
        </div>
      </div>
    );
  }

  if (state.status === "success") {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-center max-w-sm">
          <div className="h-20 w-20 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-5">
            <CheckCircleIcon className="h-10 w-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900">
            Payment Successful! 🎉
          </h2>
          <p className="text-sm text-slate-500 mt-2">
            Your payment via {gatewayName} has been confirmed.
          </p>
          <div className="mt-6 rounded-xl bg-slate-50 border border-slate-200 p-4 space-y-2 text-left">
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Receipt</span>
              <span className="font-mono font-medium text-slate-900">
                {state.receipt}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">Gateway</span>
              <span className="font-medium text-slate-900">{gatewayName}</span>
            </div>
          </div>
          <div className="mt-8 flex justify-center gap-3">
            <button
              onClick={() => navigate(feesPath)}
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition-colors"
            >
              <ArrowLeftIcon className="h-4 w-4" />
              Back to Fees
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Failed / Error
  const isFailed = state.status === "failed";
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center max-w-sm">
        <div className="h-20 w-20 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-5">
          {isFailed ? (
            <XCircleIcon className="h-10 w-10 text-red-600" />
          ) : (
            <ExclamationTriangleIcon className="h-10 w-10 text-amber-600" />
          )}
        </div>
        <h2 className="text-2xl font-bold text-slate-900">
          {isFailed ? "Payment Incomplete" : "Verification Error"}
        </h2>
        {isFailed ? (
          <p className="text-sm text-slate-500 mt-2">
            Your payment via {gatewayName} was {state.detail.toLowerCase()}.
          </p>
        ) : (
          <p className="text-sm text-slate-500 mt-2">{state.detail}</p>
        )}
        <div className="mt-4 rounded-lg bg-amber-50 border border-amber-200 p-3 text-left">
          <p className="text-xs text-amber-700">
            <strong>Don&apos;t worry!</strong> If any amount was deducted, it will
            be refunded automatically within 3-5 business days. Please contact
            the school admin if the issue persists.
          </p>
        </div>
        <div className="mt-8 flex justify-center gap-3">
          <button
            onClick={() => navigate(feesPath)}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 transition-colors"
          >
            <ArrowLeftIcon className="h-4 w-4" />
            Back to Fees
          </button>
          <button
            onClick={() => window.location.reload()}
            className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    </div>
  );
}
