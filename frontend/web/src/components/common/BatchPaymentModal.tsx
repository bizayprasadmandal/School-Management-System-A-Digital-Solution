/**
 * BatchPaymentModal — Record cash/bank payments for multiple invoices at once.
 */
import React, { useState, useMemo } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Modal, Button, Badge } from "./index";
import { npr, fmt } from "../../utils";
import toast from "react-hot-toast";
import {
  BanknotesIcon,
  PlusIcon,
  TrashIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";

interface Invoice {
  id: string;
  invoice_number: string;
  student_name?: string;
  total_amount: number;
  paid_amount: number;
  outstanding_amount?: number;
  status: string;
}

interface BatchPaymentModalProps {
  invoices: Invoice[];
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface PaymentEntry {
  invoice_id: string;
  amount: string;
  payment_method: string;
  notes: string;
}

const PAYMENT_METHODS = [
  { value: "cash", label: "Cash" },
  { value: "bank_transfer", label: "Bank Transfer" },
  { value: "cheque", label: "Cheque" },
  { value: "card", label: "Card" },
];

export default function BatchPaymentModal({
  invoices,
  open,
  onClose,
  onSuccess,
}: BatchPaymentModalProps) {
  const qc = useQueryClient();
  const [payments, setPayments] = useState<PaymentEntry[]>([]);
  const [selectedInvoices, setSelectedInvoices] = useState<Set<string>>(new Set());

  const eligibleInvoices = useMemo(
    () => invoices.filter((inv) => ["unpaid", "overdue", "partial"].includes(inv.status)),
    [invoices],
  );

  const totalBatch = useMemo(
    () => payments.reduce((s, p) => s + (parseFloat(p.amount) || 0), 0),
    [payments],
  );

  const addPayment = (invoiceId: string) => {
    const inv = eligibleInvoices.find((i) => i.id === invoiceId);
    if (!inv) return;
    const outstanding = inv.outstanding_amount ?? inv.total_amount - inv.paid_amount;
    setPayments((prev) => [
      ...prev,
      {
        invoice_id: invoiceId,
        amount: outstanding.toString(),
        payment_method: "cash",
        notes: "",
      },
    ]);
    setSelectedInvoices((prev) => new Set(prev).add(invoiceId));
  };

  const removePayment = (index: number) => {
    const invId = payments[index]?.invoice_id;
    setPayments((prev) => prev.filter((_, i) => i !== index));
    if (invId) {
      setSelectedInvoices((prev) => {
        const next = new Set(prev);
        next.delete(invId);
        return next;
      });
    }
  };

  const updatePayment = (index: number, field: keyof PaymentEntry, value: string) => {
    setPayments((prev) => prev.map((p, i) => (i === index ? { ...p, [field]: value } : p)));
  };

  const batchMutation = useMutation({
    mutationFn: () =>
      api.post<{ created: unknown[]; errors: unknown[] }>("/fees/payments/batch/", {
        payments: payments.map((p) => ({
          invoice: p.invoice_id,
          amount: parseFloat(p.amount),
          payment_method: p.payment_method,
          notes: p.notes,
        })),
      }),
    onSuccess: (data) => {
      const created = (data as { created: unknown[] }).created ?? [];
      const errors = (data as { errors: unknown[] }).errors ?? [];
      if (created.length > 0) {
        toast.success(`${created.length} payment(s) recorded successfully`);
      }
      if (errors.length > 0) {
        toast.error(`${errors.length} payment(s) failed`);
      }
      qc.invalidateQueries({ queryKey: ["accountant-invoices"] });
      qc.invalidateQueries({ queryKey: ["accountant-payments"] });
      onSuccess();
    },
    onError: () => {
      toast.error("Failed to record batch payments");
    },
  });

  const handleSubmit = () => {
    if (payments.length === 0) {
      toast.error("Add at least one payment");
      return;
    }
    batchMutation.mutate();
  };

  return (
    <Modal open={open} onClose={onClose} title="Batch Payment Recording" size="lg">
      <div className="space-y-4">
        {/* Instructions */}
        <p className="text-sm text-slate-500">
          Select invoices and record cash/bank payments for multiple students at once.
        </p>

        {/* Invoice selector */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Add Invoice</label>
          <select
            className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            onChange={(e) => {
              if (e.target.value) {
                addPayment(e.target.value);
                e.target.value = "";
              }
            }}
            defaultValue=""
          >
            <option value="">Select an invoice...</option>
            {eligibleInvoices
              .filter((inv) => !selectedInvoices.has(inv.id))
              .map((inv) => (
                <option key={inv.id} value={inv.id}>
                  {inv.invoice_number} — {inv.student_name} —{" "}
                  {npr(inv.total_amount - inv.paid_amount)} outstanding
                </option>
              ))}
          </select>
        </div>

        {/* Payment entries */}
        {payments.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            <BanknotesIcon className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No payments added yet. Select an invoice above.</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {payments.map((payment, idx) => {
              const inv = eligibleInvoices.find((i) => i.id === payment.invoice_id);
              return (
                <div
                  key={`${payment.invoice_id}-${idx}`}
                  className="rounded-lg border border-slate-200 p-3 bg-slate-50/50"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className="text-sm font-semibold text-slate-800">
                        {inv?.invoice_number ?? "Unknown"}
                      </span>
                      <span className="text-xs text-slate-500 ml-2">{inv?.student_name}</span>
                    </div>
                    <button
                      onClick={() => removePayment(idx)}
                      className="text-red-400 hover:text-red-600 p-1"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <div>
                      <label className="text-xs text-slate-500">Amount (Rs.)</label>
                      <input
                        type="number"
                        value={payment.amount}
                        onChange={(e) => updatePayment(idx, "amount", e.target.value)}
                        className="w-full rounded border border-slate-200 px-2 py-1.5 text-sm"
                        min="0"
                        step="0.01"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-500">Method</label>
                      <select
                        value={payment.payment_method}
                        onChange={(e) => updatePayment(idx, "payment_method", e.target.value)}
                        className="w-full rounded border border-slate-200 px-2 py-1.5 text-sm"
                      >
                        {PAYMENT_METHODS.map((m) => (
                          <option key={m.value} value={m.value}>
                            {m.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-slate-500">Notes</label>
                      <input
                        type="text"
                        value={payment.notes}
                        onChange={(e) => updatePayment(idx, "notes", e.target.value)}
                        placeholder="Optional"
                        className="w-full rounded border border-slate-200 px-2 py-1.5 text-sm"
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Summary */}
        {payments.length > 0 && (
          <div className="flex items-center justify-between rounded-lg bg-indigo-50 border border-indigo-100 p-3">
            <div className="flex items-center gap-2">
              <CheckCircleIcon className="h-5 w-5 text-indigo-500" />
              <span className="text-sm font-medium text-indigo-700">
                {payments.length} payment(s)
              </span>
            </div>
            <span className="text-lg font-bold text-indigo-800">{npr(totalBatch)}</span>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={payments.length === 0 || batchMutation.isPending}
            leftIcon={<BanknotesIcon className="h-4 w-4" />}
          >
            {batchMutation.isPending ? "Recording..." : "Record Payments"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
