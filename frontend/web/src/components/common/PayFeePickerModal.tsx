/**
 * PayFeePickerModal — Unified gateway picker for Stripe, Khalti, and eSewa
 *
 * Shows all available payment gateways as selectable cards.
 * Selecting a gateway opens the appropriate payment modal:
 * - Stripe → PayFeeModal (Stripe Elements inline card form)
 * - Khalti/eSewa → NepaliPayModal (redirect to gateway)
 */
import React, { useState } from "react";
import { Modal, Button } from "./index";
import PayFeeModal from "./PayFeeModal";
import NepaliPayModal from "./NepaliPayModal";
import {
  CheckCircleIcon,
  CreditCardIcon,
  BanknotesIcon,
  ShieldCheckIcon,
} from "@heroicons/react/24/outline";
import { npr } from "../../utils";
import type { FeeInvoice } from "../../types";

// ─── Types ──────────────────────────────────────────────────────────────────

interface PayFeePickerModalProps {
  invoice: FeeInvoice;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

type GatewayOption = "stripe" | "khalti" | "esewa";

interface GatewayDef {
  id: GatewayOption;
  name: string;
  description: string;
  icon: string;
}

// ─── Gateway Card ───────────────────────────────────────────────────────────

function GatewayCard({
  gateway,
  selected,
  onSelect,
  disabled,
}: {
  gateway: GatewayDef;
  selected: boolean;
  onSelect: () => void;
  disabled: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      disabled={disabled}
      className={`relative w-full rounded-2xl border-2 p-5 text-left transition-all duration-200 ${
        selected
          ? "border-indigo-500 bg-indigo-50 shadow-md ring-1 ring-indigo-200"
          : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-md hover:-translate-y-0.5"
      } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
    >
      <div className="flex items-start gap-4">
        <div
          className={`h-12 w-12 rounded-2xl flex items-center justify-center text-2xl flex-shrink-0 ${
            selected ? "bg-indigo-100 text-indigo-600" : "bg-slate-100 text-slate-500"
          }`}
        >
          {gateway.icon}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-base font-bold text-slate-900">{gateway.name}</p>
          <p className="text-sm text-slate-500 mt-1 leading-relaxed">
            {gateway.description}
          </p>
        </div>
        {selected && (
          <div className="h-7 w-7 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0 mt-1">
            <CheckCircleIcon className="h-4 w-4 text-white" />
          </div>
        )}
      </div>
    </button>
  );
}

// ─── Gateway Picker Content ─────────────────────────────────────────────────

function GatewayPicker({
  selected,
  onSelect,
  onProceed,
  loading,
  onCancel,
}: {
  selected: GatewayOption | null;
  onSelect: (gw: GatewayOption) => void;
  onProceed: () => void;
  loading: boolean;
  onCancel: () => void;
}) {
  const gateways: GatewayDef[] = [
    {
      id: "stripe",
      name: "Credit / Debit Card",
      description: "Pay securely with any international Visa, Mastercard, or American Express card. Processed via Stripe.",
      icon: "💳",
    },
    {
      id: "khalti",
      name: "Khalti",
      description: "Pay using your Khalti wallet, Mobile Banking, or connected bank accounts. Popular in Nepal.",
      icon: "💰",
    },
    {
      id: "esewa",
      name: "eSewa",
      description: "Pay using your eSewa wallet or connected bank accounts. Widely used across Nepal.",
      icon: "🏦",
    },
  ];

  return (
    <div className="space-y-5">
      <div className="text-center">
        <p className="text-sm text-slate-600">
          Choose your preferred payment method
        </p>
      </div>

      <div className="space-y-3">
        {gateways.map((gw) => (
          <GatewayCard
            key={gw.id}
            gateway={gw}
            selected={selected === gw.id}
            onSelect={() => onSelect(gw.id)}
            disabled={loading}
          />
        ))}
      </div>

      {/* Security notice */}
      <div className="flex items-start gap-3 rounded-xl bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 p-4">
        <ShieldCheckIcon className="h-6 w-6 text-indigo-500 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-sm font-semibold text-indigo-900">Secure Payment</p>
          <p className="text-xs text-indigo-700 mt-1 leading-relaxed">
            Your payment is processed directly by the gateway. We never see or store
            your card details, wallet credentials, or banking information.
          </p>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={onProceed}
          disabled={!selected || loading}
          loading={loading}
          leftIcon={
            selected === "stripe" ? (
              <CreditCardIcon className="h-4 w-4" />
            ) : (
              <BanknotesIcon className="h-4 w-4" />
            )
          }
        >
          {selected === "stripe"
            ? "Pay with Card"
            : selected === "khalti"
              ? "Pay with Khalti"
              : selected === "esewa"
                ? "Pay with eSewa"
                : "Continue"}
        </Button>
      </div>
    </div>
  );
}

// ─── Main Component ─────────────────────────────────────────────────────────

export default function PayFeePickerModal({
  invoice,
  open,
  onClose,
  onSuccess,
}: PayFeePickerModalProps) {
  const [selectedGateway, setSelectedGateway] = useState<GatewayOption | null>(null);

  // Sub-modal states
  const [showStripe, setShowStripe] = useState(false);
  const [showNepali, setShowNepali] = useState(false);

  // ── Reset handler ──────────────────────────────────────────────────────────

  const handleClose = () => {
    setSelectedGateway(null);
    setShowStripe(false);
    setShowNepali(false);
    onClose();
  };

  // ── Proceed to selected gateway ──────────────────────────────────────────

  const handleProceed = () => {
    if (!selectedGateway) return;

    // Open the sub-modal directly — the picker modal closes automatically
    // since its `open` prop depends on `!showStripe && !showNepali`
    if (selectedGateway === "stripe") {
      setShowStripe(true);
    } else {
      setShowNepali(true);
    }
  };

  // ── Success handler (called by sub-modals) ─────────────────────────────────

  const handleSubSuccess = () => {
    setShowStripe(false);
    setShowNepali(false);
    handleClose();
    onSuccess();
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <>
      {/* Picker modal — only rendered when no sub-modal is active */}
        <Modal
          open={open && !showStripe && !showNepali}
          onClose={handleClose}
          title="Pay Invoice"
          description={`${invoice.invoice_number} — ${npr(invoice.outstanding_amount)} due`}
          size="md"
        >
          {/* Invoice summary */}
          <div className="mb-5 rounded-xl bg-gradient-to-r from-slate-50 to-indigo-50 border border-slate-200 p-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-600">Invoice</span>
              <span className="font-mono font-semibold text-slate-900">
                {invoice.invoice_number}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-600">Amount Due</span>
              <span className="text-lg font-bold text-indigo-600">{npr(invoice.outstanding_amount)}</span>
            </div>
          </div>

          <GatewayPicker
            selected={selectedGateway}
            onSelect={setSelectedGateway}
            onProceed={handleProceed}
            loading={false}
            onCancel={handleClose}
          />
        </Modal>

      {/* Stripe sub-modal — replaces the picker */}
      {showStripe && (
        <PayFeeModal
          invoice={invoice}
          open={showStripe}
          onClose={() => {
            setShowStripe(false);
          }}
          onSuccess={handleSubSuccess}
        />
      )}

      {/* Nepali sub-modal — replaces the picker */}
      {showNepali && (
        <NepaliPayModal
          invoice={invoice}
          open={showNepali}
          onClose={() => {
            setShowNepali(false);
          }}
          onSuccess={handleSubSuccess}
        />
      )}
    </>
  );
}
