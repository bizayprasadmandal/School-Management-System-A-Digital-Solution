/**
 * PayFeePickerModal — Unified gateway picker for Stripe, Khalti, and eSewa
 *
 * Shows available payment gateways as selectable cards (fetched from backend).
 * Selecting a gateway opens the appropriate payment modal:
 * - Stripe → PayFeeModal (Stripe Elements inline card form)
 * - Khalti/eSewa → NepaliPayModal (redirect to gateway)
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Modal, Button } from "./index";
import PayFeeModal from "./PayFeeModal";
import NepaliPayModal from "./NepaliPayModal";
import {
  CheckCircleIcon,
  CreditCardIcon,
  BanknotesIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { npr } from "../../utils";
import type { FeeInvoice } from "../../types";

// ─── Types ──────────────────────────────────────────────────────────────────

interface GatewayDef {
  id: "stripe" | "khalti" | "esewa";
  name: string;
  description: string;
  icon: string;
}

interface PayFeePickerModalProps {
  invoice: FeeInvoice;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
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
  gateways,
  selected,
  onSelect,
  onProceed,
  loading,
  onCancel,
}: {
  gateways: GatewayDef[];
  selected: GatewayDef | null;
  onSelect: (gw: GatewayDef) => void;
  onProceed: () => void;
  loading: boolean;
  onCancel: () => void;
}) {
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
            selected={selected?.id === gw.id}
            onSelect={() => onSelect(gw)}
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
            selected?.id === "stripe" ? (
              <CreditCardIcon className="h-4 w-4" />
            ) : (
              <BanknotesIcon className="h-4 w-4" />
            )
          }
        >
          {selected?.id === "stripe"
            ? "Pay with Card"
            : selected?.id === "khalti"
              ? "Pay with Khalti"
              : selected?.id === "esewa"
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
  const [selectedGateway, setSelectedGateway] = useState<GatewayDef | null>(null);

  // Sub-modal states
  const [showStripe, setShowStripe] = useState(false);
  const [showNepali, setShowNepali] = useState(false);

  // ── Fetch enabled gateways from backend ─────────────────────────────────────

  const {
    data: gateways = [],
    isLoading: gatewaysLoading,
    isError: gatewaysError,
  } = useQuery<GatewayDef[]>({
    queryKey: ["enabled-gateways"],
    queryFn: () => api.get<GatewayDef[]>("/fees/gateway-config/enabled/"),
    enabled: open && !showStripe && !showNepali,
    staleTime: 5 * 60 * 1000,
  });

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

    if (selectedGateway.id === "stripe") {
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
      {/* Picker modal */}
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

        {/* Loading state */}
        {gatewaysLoading ? (
          <div className="flex flex-col items-center py-12 text-center">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-4" />
            <p className="text-sm text-slate-500">Loading payment options...</p>
          </div>
        ) : gatewaysError ? (
          <div className="flex flex-col items-center py-8 text-center">
            <div className="h-14 w-14 rounded-full bg-red-100 flex items-center justify-center mb-3">
              <ExclamationTriangleIcon className="h-7 w-7 text-red-600" />
            </div>
            <p className="text-sm font-medium text-red-700">Failed to load payment options</p>
            <p className="text-xs text-slate-500 mt-1">Please try again or contact the school.</p>
          </div>
        ) : gateways.length === 0 ? (
          <div className="flex flex-col items-center py-8 text-center">
            <div className="h-14 w-14 rounded-full bg-amber-100 flex items-center justify-center mb-3">
              <ExclamationTriangleIcon className="h-7 w-7 text-amber-600" />
            </div>
            <p className="text-sm font-medium text-amber-700">No payment gateways enabled</p>
            <p className="text-xs text-slate-500 mt-1">
              No online payment methods are currently enabled for your school.
              Please contact the school administrator.
            </p>
          </div>
        ) : (
          <GatewayPicker
            gateways={gateways}
            selected={selectedGateway}
            onSelect={setSelectedGateway}
            onProceed={handleProceed}
            loading={false}
            onCancel={handleClose}
          />
        )}
      </Modal>

      {/* Stripe sub-modal */}
      {showStripe && (
        <PayFeeModal
          invoice={invoice}
          open={showStripe}
          onClose={() => setShowStripe(false)}
          onSuccess={handleSubSuccess}
        />
      )}

      {/* Nepali sub-modal */}
      {showNepali && (
        <NepaliPayModal
          invoice={invoice}
          open={showNepali}
          onClose={() => setShowNepali(false)}
          onSuccess={handleSubSuccess}
        />
      )}
    </>
  );
}
