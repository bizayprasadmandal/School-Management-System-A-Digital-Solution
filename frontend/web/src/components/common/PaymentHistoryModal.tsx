/**
 * PaymentHistoryModal — Shows all payments for an invoice with refund capability
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Modal, Button, Badge, EmptyState } from "./index";
import type { Payment, PaginatedResponse } from "../../types";
import { currency, fmt, downloadFromUrl } from "../../utils";
import { useAuthStore } from "../../store/authStore";
import toast from "react-hot-toast";
import {
  BanknotesIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
  ShieldCheckIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface PaymentHistoryModalProps {
  invoiceId: string;
  invoiceNumber: string;
  open: boolean;
  onClose: () => void;
}

const PAYMENT_STATUS_COLORS: Record<string, "green" | "red" | "amber" | "blue" | "slate"> = {
  successful: "green",
  pending: "amber",
  failed: "red",
  refunded: "blue",
};

const PAYMENT_METHOD_LABELS: Record<string, string> = {
  cash: "Cash",
  bank_transfer: "Bank Transfer",
  card: "Credit/Debit Card",
  cheque: "Cheque",
  online: "Online Gateway",
  mobile: "Mobile Money",
  khalti: "Khalti",
  esewa: "eSewa",
};

function RefundConfirmModal({
  payment,
  onClose,
  onSuccess,
}: {
  payment: Payment;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);

  const refundMutation = useMutation({
    mutationFn: () => {
      const method = payment.payment_method;
      const endpoint =
        method === "khalti" || method === "esewa" ? "/fees/nepali/refund/" : "/fees/stripe/refund/";
      return api.post(endpoint, {
        payment_id: payment.id,
        reason: reason.trim() || "Refund requested",
      });
    },
    onSuccess: () => {
      toast.success(`Refund of ${currency(payment.amount)} processed`);
      onSuccess(); // handleRefundSuccess already closes the refund modal
    },
    onError: (err: any) => {
      toast.error(err?.message || "Refund failed. Please try again.");
    },
  });

  return (
    <Modal
      open
      onClose={onClose}
      title="Confirm Refund"
      description={`${payment.receipt_number} — ${currency(payment.amount)}`}
      size="sm"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={refundMutation.isPending}>
            Cancel
          </Button>
          <Button
            variant="danger"
            onClick={() => refundMutation.mutate()}
            loading={refundMutation.isPending}
            disabled={!confirmed}
          >
            Process Refund
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <div className="rounded-lg bg-amber-50 border border-amber-200 p-3 flex items-start gap-2">
          <ExclamationTriangleIcon className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-amber-800">Are you sure?</p>
            <p className="text-xs text-amber-700 mt-1">
              This will refund {currency(payment.amount)} to the payer. The invoice balance will be
              adjusted. This action cannot be undone.
            </p>
          </div>
        </div>

        <div className="rounded-lg bg-slate-50 p-3 space-y-1 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-500">Receipt</span>
            <span className="font-mono font-medium">{payment.receipt_number}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500">Amount</span>
            <span className="font-bold">{currency(payment.amount)}</span>
          </div>
          {payment.transaction_id && (
            <div className="flex justify-between">
              <span className="text-slate-500">Transaction ID</span>
              <span className="font-mono text-xs">{payment.transaction_id.slice(0, 20)}…</span>
            </div>
          )}
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">
            Reason for Refund
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={2}
            placeholder="e.g. Duplicate payment, student withdrew, bank error…"
            className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            className="mt-0.5 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
          />
          <span className="text-sm text-slate-600">
            I confirm this refund is authorized and the payment will be returned to the payer.
          </span>
        </label>
      </div>
    </Modal>
  );
}

export default function PaymentHistoryModal({
  invoiceId,
  invoiceNumber,
  open,
  onClose,
}: PaymentHistoryModalProps) {
  const qc = useQueryClient();
  const [refundingPayment, setRefundingPayment] = useState<Payment | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["invoice-payments", invoiceId],
    queryFn: () => api.get<PaginatedResponse<Payment>>("/fees/payments/", { invoice: invoiceId }),
    enabled: open,
  });

  const payments = data?.results ?? [];

  const handleRefundSuccess = () => {
    qc.invalidateQueries({ queryKey: ["invoice-payments", invoiceId] });
    qc.invalidateQueries({ queryKey: ["fees"] });
    setRefundingPayment(null);
  };

  return (
    <>
      <Modal
        open={open}
        onClose={onClose}
        title="Payment History"
        description={`Invoice #${invoiceNumber}`}
        size="lg"
      >
        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
          </div>
        ) : payments.length === 0 ? (
          <EmptyState
            icon={BanknotesIcon}
            title="No payments recorded"
            description="No payments have been recorded for this invoice yet."
          />
        ) : (
          <div className="space-y-3">
            {payments.map((payment) => (
              <div
                key={payment.id}
                className="rounded-xl border border-slate-100 bg-white p-4 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge color={PAYMENT_STATUS_COLORS[payment.status] ?? "slate"} dot>
                        {payment.status.charAt(0).toUpperCase() + payment.status.slice(1)}
                      </Badge>
                      <span className="text-xs text-slate-400">
                        {payment.paid_at
                          ? fmt.datetime(payment.paid_at)
                          : fmt.datetime(payment.created_at)}
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-slate-900">
                      {currency(payment.amount)}
                    </p>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        {PAYMENT_METHOD_LABELS[payment.payment_method] ?? payment.payment_method}
                      </span>
                      <span className="font-mono">{payment.receipt_number}</span>
                      {payment.collected_by_name && <span>by {payment.collected_by_name}</span>}
                      {payment.transaction_id && (
                        <span className="font-mono text-slate-400" title={payment.transaction_id}>
                          {payment.payment_method === "khalti"
                            ? "Khalti"
                            : payment.payment_method === "esewa"
                              ? "eSewa"
                              : "Gateway"}
                          : {payment.transaction_id.slice(0, 14)}…
                        </span>
                      )}
                    </div>
                    {payment.notes && (
                      <p className="text-xs text-slate-400 mt-1 italic">{payment.notes}</p>
                    )}
                    {/* Gateway info for online payments */}
                    {Boolean(payment.gateway_response?.refund_id) && (
                      <div className="mt-2 rounded-lg bg-blue-50 p-2 flex items-center gap-2">
                        <ShieldCheckIcon className="h-4 w-4 text-blue-500 flex-shrink-0" />
                        <span className="text-xs text-blue-700">
                          Refund ID: {String(payment.gateway_response.refund_id)}
                          {payment.gateway_response.refund_reason
                            ? ` — ${String(payment.gateway_response.refund_reason)}`
                            : ""}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  {payment.status === "successful" && (
                    <div className="flex flex-shrink-0 gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          const token = useAuthStore.getState().tokens?.access ?? "";
                          const baseURL =
                            process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";
                          downloadFromUrl(
                            `${baseURL}/fees/payments/${payment.id}/receipt-pdf/`,
                            `receipt_${payment.receipt_number}.pdf`,
                            token,
                          ).catch(() => toast.error("Failed to download receipt"));
                        }}
                        className="text-slate-500 hover:text-indigo-600 hover:bg-indigo-50"
                        leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
                      >
                        Receipt
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setRefundingPayment(payment)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                        leftIcon={<ArrowPathIcon className="h-4 w-4" />}
                      >
                        Refund
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Modal>

      {refundingPayment && (
        <RefundConfirmModal
          payment={refundingPayment}
          onClose={() => setRefundingPayment(null)}
          onSuccess={handleRefundSuccess}
        />
      )}
    </>
  );
}
