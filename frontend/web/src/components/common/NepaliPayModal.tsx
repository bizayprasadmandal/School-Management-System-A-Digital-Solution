/**
 * NepaliPayModal — Khalti & eSewa Payment Modal
 *
 * Lets users choose a Nepali payment gateway (Khalti or eSewa),
 * initiates the payment via our backend, and redirects to the
 * gateway's payment page for completion.
 */
import React, { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Modal, Button } from "./index";
import toast from "react-hot-toast";
import { npr } from "../../utils";
import type { FeeInvoice } from "../../types";
import {
  BanknotesIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowTopRightOnSquareIcon,
  CreditCardIcon,
} from "@heroicons/react/24/outline";

// ─── Types ──────────────────────────────────────────────────────────────────

interface InitiateResponse {
  gateway: "khalti" | "esewa";
  payment_url?: string;
  pidx?: string;
  gateway_url?: string;
  form_params?: Record<string, string>;
}

interface NepaliPayModalProps {
  invoice: FeeInvoice;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

// ─── Gateway Card ───────────────────────────────────────────────────────────

function GatewayCard({
  id,
  name,
  description,
  icon,
  selected,
  onSelect,
  disabled,
}: {
  id: string;
  name: string;
  description: string;
  icon: string;
  selected: boolean;
  onSelect: () => void;
  disabled: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      disabled={disabled}
      className={`relative w-full rounded-xl border-2 p-4 text-left transition-all ${
        selected
          ? "border-indigo-500 bg-indigo-50 shadow-sm"
          : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm"
      } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
    >
      <div className="flex items-center gap-3">
        <div
          className={`h-10 w-10 rounded-xl flex items-center justify-center text-xl ${
            selected ? "bg-indigo-100 text-indigo-600" : "bg-slate-100 text-slate-500"
          }`}
        >
          {icon}
        </div>
        <div className="flex-1">
          <p className="text-sm font-semibold text-slate-900">{name}</p>
          <p className="text-xs text-slate-500 mt-0.5">{description}</p>
        </div>
        {selected && (
          <div className="h-6 w-6 rounded-full bg-indigo-600 flex items-center justify-center">
            <CheckCircleIcon className="h-4 w-4 text-white" />
          </div>
        )}
      </div>
    </button>
  );
}

// ─── Gateway Selector Step ──────────────────────────────────────────────────

function GatewaySelector({
  selected,
  onSelect,
  onContinue,
  onCancel,
  loading,
}: {
  selected: string;
  onSelect: (gw: "khalti" | "esewa") => void;
  onContinue: () => void;
  onCancel: () => void;
  loading: boolean;
}) {
  const gateways = [
    {
      id: "khalti",
      name: "Khalti",
      description: "Pay with Khalti wallet, Mobile Banking, or Cards",
      icon: "💰",
    },
    {
      id: "esewa",
      name: "eSewa",
      description: "Pay with eSewa wallet or connected bank accounts",
      icon: "🏦",
    },
  ];

  return (
    <div className="space-y-5">
      <div className="text-center">
        <p className="text-sm text-slate-600">
          Select your preferred payment method to proceed
        </p>
      </div>

      <div className="space-y-3">
        {gateways.map((gw) => (
          <GatewayCard
            key={gw.id}
            id={gw.id}
            name={gw.name}
            description={gw.description}
            icon={gw.icon}
            selected={selected === gw.id}
            onSelect={() => onSelect(gw.id as "khalti" | "esewa")}
            disabled={loading}
          />
        ))}
      </div>

      <div className="flex items-center gap-2 rounded-lg bg-amber-50 border border-amber-200 p-3">
        <ShieldCheckIcon className="h-5 w-5 text-amber-600 flex-shrink-0" />
        <p className="text-xs text-amber-700">
          You will be redirected to the gateway&apos;s secure page to complete
          your payment. We never see your card or wallet credentials.
        </p>
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={onContinue}
          disabled={!selected || loading}
          loading={loading}
          leftIcon={<ArrowTopRightOnSquareIcon className="h-4 w-4" />}
        >
          Continue to Payment
        </Button>
      </div>
    </div>
  );
}

// ─── Success / Error View ───────────────────────────────────────────────────

function PaymentResult({
  status,
  amount,
  invoiceNumber,
  onClose,
  onRetry,
}: {
  status: "success" | "error" | "redirecting";
  amount: string;
  invoiceNumber: string;
  onClose: () => void;
  onRetry: () => void;
}) {
  if (status === "redirecting") {
    return (
      <div className="flex flex-col items-center py-12 text-center">
        <div className="h-16 w-16 rounded-full bg-indigo-100 flex items-center justify-center mb-4">
          <ArrowTopRightOnSquareIcon className="h-8 w-8 text-indigo-600 animate-pulse" />
        </div>
        <h3 className="text-lg font-bold text-slate-900">
          Redirecting to Gateway...
        </h3>
        <p className="text-sm text-slate-500 mt-2 max-w-xs">
          You&apos;ll be taken to the payment gateway to complete your
          transaction securely.
        </p>
      </div>
    );
  }

  if (status === "success") {
    return (
      <div className="flex flex-col items-center py-8 text-center">
        <div className="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center mb-4">
          <CheckCircleIcon className="h-8 w-8 text-green-600" />
        </div>
        <h3 className="text-lg font-bold text-slate-900">Payment Initiated!</h3>
        <p className="text-sm text-slate-500 mt-1">
          Your payment of {amount} for invoice {invoiceNumber} is being
          processed. You&apos;ll be redirected to complete it.
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center py-8 text-center">
      <div className="h-16 w-16 rounded-full bg-red-100 flex items-center justify-center mb-4">
        <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
      </div>
      <h3 className="text-lg font-bold text-slate-900">Payment Failed</h3>
      <p className="text-sm text-slate-500 mt-1">
        We couldn&apos;t initiate your payment. Please try again.
      </p>
      <div className="flex gap-3 mt-6">
        <Button variant="secondary" onClick={onClose}>
          Close
        </Button>
        <Button variant="primary" onClick={onRetry}>
          Try Again
        </Button>
      </div>
    </div>
  );
}

// ─── Main Component ─────────────────────────────────────────────────────────

export default function NepaliPayModal({
  invoice,
  open,
  onClose,
  onSuccess,
}: NepaliPayModalProps) {
  const [step, setStep] = useState<"select" | "processing" | "result">(
    "select",
  );
  const [selectedGateway, setSelectedGateway] = useState<
    "khalti" | "esewa" | ""
  >("");
  const [resultStatus, setResultStatus] = useState<
    "success" | "error" | "redirecting"
  >("redirecting");

  // ── Initiate payment ────────────────────────────────────────────────────────

  const initiateMutation = useMutation({
    mutationFn: (gateway: "khalti" | "esewa") =>
      api.post<InitiateResponse>("/fees/nepali/initiate/", {
        invoice_id: invoice.id,
        gateway,
        return_url: `${window.location.origin}/fees/callback?gateway=${gateway}&invoice_id=${invoice.id}`,
      }),
    onSuccess: (data) => {
      setStep("result");
      setResultStatus("redirecting");

      if (data.gateway === "khalti" && data.payment_url) {
        // Redirect to Khalti payment page
        setTimeout(() => {
          window.location.href = data.payment_url!;
        }, 800);
      } else if (data.gateway === "esewa" && data.form_params && data.gateway_url) {
        // Submit hidden form to eSewa
        setTimeout(() => {
          const form = document.createElement("form");
          form.method = "POST";
          form.action = data.gateway_url!;
          form.style.display = "none";
          for (const [key, value] of Object.entries(data.form_params!)) {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = key;
            input.value = value;
            form.appendChild(input);
          }
          document.body.appendChild(form);
          form.submit();
        }, 800);
      } else {
        setResultStatus("error");
        toast.error("Invalid gateway response");
      }
    },
    onError: () => {
      setStep("result");
      setResultStatus("error");
      toast.error("Failed to initiate payment. Please try again.");
    },
  });

  // ── Handlers ────────────────────────────────────────────────────────────────

  const handleContinue = () => {
    if (!selectedGateway) return;
    setStep("processing");
    initiateMutation.mutate(selectedGateway as "khalti" | "esewa");
  };

  const handleClose = () => {
    // Reset state
    setStep("select");
    setSelectedGateway("");
    setResultStatus("redirecting");
    onClose();
  };

  const handleRetry = () => {
    setStep("select");
    setResultStatus("redirecting");
  };

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title={
        step === "select"
          ? "Pay with Local Gateway"
          : step === "processing"
            ? "Processing Payment"
            : "Payment Status"
      }
      description={
        step === "select"
          ? `${invoice.invoice_number} — ${npr(invoice.outstanding_amount)} due`
          : undefined
      }
      size="md"
    >
      {/* Invoice summary (always shown) */}
      <div
        className={`${
          step === "select" ? "mb-5" : "mb-4"
        } rounded-lg bg-slate-50 p-4 space-y-2`}
      >
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Invoice</span>
          <span className="font-mono font-medium text-slate-900">
            {invoice.invoice_number}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Total</span>
          <span className="font-medium text-slate-900">
            {npr(invoice.total_amount)}
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-slate-600">Already Paid</span>
          <span className="font-medium text-green-600">
            {npr(invoice.paid_amount)}
          </span>
        </div>
        <div className="flex justify-between text-sm font-semibold border-t border-slate-200 pt-2">
          <span>Amount Due Now</span>
          <span className="text-lg text-indigo-600">
            {npr(invoice.outstanding_amount)}
          </span>
        </div>
      </div>

      {/* Step: Gateway selection */}
      {step === "select" && (
        <GatewaySelector
          selected={selectedGateway}
          onSelect={setSelectedGateway}
          onContinue={handleContinue}
          onCancel={handleClose}
          loading={initiateMutation.isPending}
        />
      )}

      {/* Step: Processing */}
      {step === "processing" && (
        <div className="flex flex-col items-center py-12 text-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-4" />
          <p className="text-sm text-slate-500">
            Connecting to{" "}
            {selectedGateway === "khalti" ? "Khalti" : "eSewa"}...
          </p>
        </div>
      )}

      {/* Step: Result / Redirecting */}
      {step === "result" && (
        <PaymentResult
          status={resultStatus}
          amount={npr(invoice.outstanding_amount)}
          invoiceNumber={invoice.invoice_number}
          onClose={handleClose}
          onRetry={handleRetry}
        />
      )}
    </Modal>
  );
}
