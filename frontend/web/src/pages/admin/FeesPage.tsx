/**
 * Admin Fees Page — Invoice management, payment recording, outstanding tracking
 */

import React, { useState } from "react";
import {
  BanknotesIcon, CheckCircleIcon, ClockIcon,
  ExclamationCircleIcon, ArrowPathIcon,
} from "@heroicons/react/24/outline";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { api } from "../../api/client";
import type { FeeInvoice } from "../../types";
import dayjs from "dayjs";

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  unpaid:    { label: "Unpaid",   color: "text-amber-700 bg-amber-50 ring-amber-200",   icon: <ClockIcon className="h-3.5 w-3.5" /> },
  paid:      { label: "Paid",     color: "text-green-700 bg-green-50 ring-green-200",   icon: <CheckCircleIcon className="h-3.5 w-3.5" /> },
  overdue:   { label: "Overdue",  color: "text-red-700 bg-red-50 ring-red-200",         icon: <ExclamationCircleIcon className="h-3.5 w-3.5" /> },
  partial:   { label: "Partial",  color: "text-blue-700 bg-blue-50 ring-blue-200",      icon: <ArrowPathIcon className="h-3.5 w-3.5" /> },
  waived:    { label: "Waived",   color: "text-slate-700 bg-slate-50 ring-slate-200",   icon: <CheckCircleIcon className="h-3.5 w-3.5" /> },
  cancelled: { label: "Cancelled",color: "text-slate-500 bg-slate-50 ring-slate-200",   icon: null },
};

function StatusBadge({ status }: { status: string }) {
  const cfg = STATUS_CONFIG[status] ?? { label: status, color: "text-slate-600 bg-slate-100 ring-slate-200", icon: null };
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ${cfg.color}`}>
      {cfg.icon}{cfg.label}
    </span>
  );
}

interface PaymentModalProps {
  invoice: FeeInvoice;
  onClose: () => void;
}

function RecordPaymentModal({ invoice, onClose }: PaymentModalProps) {
  const [amount, setAmount] = useState(String(invoice.outstanding_amount));
  const [method, setMethod] = useState("cash");
  const qc = useQueryClient();

  const { mutate, isPending } = useMutation({
    mutationFn: () => api.post("/fees/payments/", {
      invoice_id: invoice.id,
      amount: parseFloat(amount),
      payment_method: method,
    }),
    onSuccess: () => {
      toast.success("Payment recorded successfully");
      qc.invalidateQueries({ queryKey: ["fees"] });
      onClose();
    },
    onError: () => toast.error("Failed to record payment"),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="text-lg font-bold text-slate-900 mb-1">Record Payment</h2>
        <p className="text-sm text-slate-500 mb-5">Invoice #{invoice.invoice_number}</p>

        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-slate-600">Total</span>
              <span className="font-medium">${invoice.total_amount.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-slate-600">Already Paid</span>
              <span className="font-medium text-green-600">${invoice.paid_amount.toLocaleString()}</span>
            </div>
            <div className="flex justify-between text-sm font-semibold border-t pt-2">
              <span>Outstanding</span>
              <span className="text-red-600">${invoice.outstanding_amount.toLocaleString()}</span>
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1.5">Amount to Pay</label>
            <input type="number" min={0.01} max={invoice.outstanding_amount} value={amount}
              onChange={e => setAmount(e.target.value)}
              className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1.5">Payment Method</label>
            <select value={method} onChange={e => setMethod(e.target.value)}
              className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="cash">Cash</option>
              <option value="bank_transfer">Bank Transfer</option>
              <option value="card">Card</option>
              <option value="cheque">Cheque</option>
              <option value="online">Online Gateway</option>
              <option value="mobile">Mobile Money</option>
            </select>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button onClick={onClose} className="flex-1 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors">
            Cancel
          </button>
          <button onClick={() => mutate()} disabled={isPending || !amount || parseFloat(amount) <= 0}
            className="flex-1 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors">
            {isPending ? "Processing…" : "Record Payment"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function FeesPage() {
  const [statusFilter, setStatusFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [payingInvoice, setPayingInvoice] = useState<FeeInvoice | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["fees", "all-invoices", statusFilter, search],
    queryFn: () => api.get<{ count: number; results: FeeInvoice[] }>("/fees/invoices/", {
      status: statusFilter === "all" ? undefined : statusFilter,
      search: search || undefined,
    }),
  });

  const invoices = data?.results ?? [];

  const summary = {
    total: invoices.reduce((s, i) => s + Number(i.total_amount), 0),
    collected: invoices.reduce((s, i) => s + Number(i.paid_amount), 0),
    outstanding: invoices.filter(i => ["unpaid", "overdue", "partial"].includes(i.status))
      .reduce((s, i) => s + Number(i.outstanding_amount), 0),
    overdue: invoices.filter(i => i.status === "overdue").length,
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Fee Management</h1>
          <p className="text-sm text-slate-500 mt-0.5">Track invoices, payments and outstanding balances</p>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "Total Invoiced",  value: `$${(summary.total / 1000).toFixed(1)}K`, color: "bg-indigo-500", icon: BanknotesIcon },
          { label: "Collected",       value: `$${(summary.collected / 1000).toFixed(1)}K`, color: "bg-green-500", icon: CheckCircleIcon },
          { label: "Outstanding",     value: `$${(summary.outstanding / 1000).toFixed(1)}K`, color: "bg-amber-500", icon: ClockIcon },
          { label: "Overdue Invoices",value: summary.overdue, color: "bg-red-500", icon: ExclamationCircleIcon },
        ].map(({ label, value, color, icon: Icon }) => (
          <div key={label} className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 flex items-center gap-4">
            <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${color}`}>
              <Icon className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500">{label}</p>
              <p className="text-xl font-bold text-slate-900">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 flex flex-wrap gap-3">
        <input type="search" placeholder="Search student name or invoice…"
          value={search} onChange={e => setSearch(e.target.value)}
          className="flex-1 min-w-48 rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
          <option value="all">All Status</option>
          <option value="unpaid">Unpaid</option>
          <option value="paid">Paid</option>
          <option value="overdue">Overdue</option>
          <option value="partial">Partial</option>
          <option value="waived">Waived</option>
        </select>
      </div>

      {/* Invoices table */}
      <div className="rounded-xl bg-white shadow-sm border border-slate-100 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-20 text-slate-400">
            <div className="h-7 w-7 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent mr-3" />
            Loading invoices…
          </div>
        ) : invoices.length === 0 ? (
          <div className="text-center py-16 text-slate-400">
            <BanknotesIcon className="h-10 w-10 mx-auto mb-2 opacity-30" />
            <p>No invoices found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-100">
              <thead className="bg-slate-50">
                <tr>
                  {["Invoice #", "Student", "Due Date", "Total", "Paid", "Outstanding", "Status", "Action"].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {invoices.map(inv => (
                  <tr key={inv.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-4 py-3 text-sm font-mono text-slate-600">{inv.invoice_number}</td>
                    <td className="px-4 py-3 text-sm font-medium text-slate-800">{inv.student}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">
                      <span className={dayjs(inv.due_date).isBefore(dayjs()) && inv.status === "unpaid" ? "text-red-600 font-medium" : ""}>
                        {dayjs(inv.due_date).format("MMM D, YYYY")}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm font-medium text-slate-800">${Number(inv.total_amount).toLocaleString()}</td>
                    <td className="px-4 py-3 text-sm text-green-600">${Number(inv.paid_amount).toLocaleString()}</td>
                    <td className="px-4 py-3 text-sm font-semibold text-red-600">${Number(inv.outstanding_amount).toLocaleString()}</td>
                    <td className="px-4 py-3"><StatusBadge status={inv.status} /></td>
                    <td className="px-4 py-3">
                      {["unpaid", "overdue", "partial"].includes(inv.status) && (
                        <button onClick={() => setPayingInvoice(inv)}
                          className="rounded-lg bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-700 hover:bg-indigo-100 transition-colors">
                          Record Payment
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {payingInvoice && (
        <RecordPaymentModal invoice={payingInvoice} onClose={() => setPayingInvoice(null)} />
      )}
    </div>
  );
}
