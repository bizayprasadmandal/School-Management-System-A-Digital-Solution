/** Accountant Payment History — all payments with filters, search, receipt view */
import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  MagnifyingGlassIcon, ArrowDownTrayIcon, BanknotesIcon,
  ReceiptPercentIcon, ArrowPathIcon, FunnelIcon,
  ShieldCheckIcon, ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import {
  Button, Badge, Modal, Input, Select, EmptyState, DataTable,
} from "../../components/common";
import type { Column, BadgeColor } from "../../components/common";
import type { Payment, PaginatedResponse } from "../../types";
import { currency, fmt, toCsv, downloadCsv } from "../../utils";
import toast from "react-hot-toast";
import dayjs from "dayjs";

const STATUS_COLORS: Record<string, BadgeColor> = {
  successful: "green",
  pending: "amber",
  failed: "red",
  refunded: "blue",
};

const METHOD_LABELS: Record<string, string> = {
  cash: "Cash",
  bank_transfer: "Bank Transfer",
  card: "Credit/Debit Card",
  cheque: "Cheque",
  online: "Online Gateway",
  mobile: "Mobile Money",
  khalti: "Khalti",
  esewa: "eSewa",
};

function PaymentDetailModal({
  payment, open, onClose, onRefund,
}: {
  payment: Payment;
  open: boolean;
  onClose: () => void;
  onRefund: (p: Payment) => void;
}) {
  const gw = payment.gateway_response ?? {};

  return (
    <Modal open={open} onClose={onClose} title="Payment Details" size="md"
      description={`${payment.receipt_number} — ${currency(payment.amount)}`}
    >
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Receipt #</p>
            <p className="font-mono font-semibold text-slate-900 dark:text-white">{payment.receipt_number}</p>
          </div>
          <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Invoice</p>
            <p className="font-mono font-semibold text-slate-900 dark:text-white">{payment.invoice_number}</p>
          </div>
          <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Student</p>
            <p className="font-semibold text-slate-900 dark:text-white">{payment.student_name}</p>
          </div>
          <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Amount</p>
            <p className="font-bold text-green-600">{currency(payment.amount)}</p>
          </div>
          <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Method</p>
            <p className="font-semibold text-slate-900 dark:text-white capitalize">{METHOD_LABELS[payment.payment_method] ?? payment.payment_method}</p>
          </div>
          <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Date</p>
            <p className="font-semibold text-slate-900 dark:text-white">
              {payment.paid_at ? dayjs(payment.paid_at).format("MMM D, YYYY h:mm A") : "—"}
            </p>
          </div>
          <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Status</p>
            <Badge color={STATUS_COLORS[payment.status] ?? "slate"} dot>
              {payment.status.charAt(0).toUpperCase() + payment.status.slice(1)}
            </Badge>
          </div>
          <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Collected By</p>
            <p className="font-semibold text-slate-900 dark:text-white">{payment.collected_by_name ?? "—"}</p>
          </div>
        </div>

        {payment.transaction_id && (
          <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Transaction ID</p>
            <p className="font-mono text-xs text-slate-900 dark:text-white break-all">{payment.transaction_id}</p>
          </div>
        )}

        {payment.notes && (
          <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Notes</p>
            <p className="text-sm text-slate-900 dark:text-white">{payment.notes}</p>
          </div>
        )}

        {Boolean(gw.refund_id) && (
          <div className="rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 p-3 flex items-start gap-2">
            <ShieldCheckIcon className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-blue-800 dark:text-blue-300">Refunded</p>
              <p className="text-xs text-blue-700 dark:text-blue-400">
                Refund ID: {String(gw.refund_id)}
                {Boolean(gw.refund_reason) && ` — ${String(gw.refund_reason)}`}
              </p>
            </div>
          </div>
        )}

        <div className="flex gap-2 pt-2">
          <Button variant="secondary" onClick={onClose}>Close</Button>
          {payment.status === "successful" && (
            <Button
              variant="danger"
              onClick={() => { onClose(); onRefund(payment); }}
              leftIcon={<ArrowPathIcon className="h-4 w-4" />}
            >
              Refund Payment
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
}

function RefundConfirmModal({
  payment, onClose, onSuccess,
}: {
  payment: Payment;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [reason, setReason] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [gateway, setGateway] = useState<"stripe" | "nepali">("stripe");

  const refundMutation = useMutation({
    mutationFn: () => {
      const endpoint = gateway === "stripe" ? "/fees/stripe/refund/" : "/fees/nepali/refund/";
      return api.post(endpoint, { payment_id: payment.id, reason: reason.trim() || "Refund requested" });
    },
    onSuccess: () => {
      toast.success(`Refund of ${currency(payment.amount)} processed`);
      onSuccess();
    },
    onError: (err: any) => toast.error(err?.message || "Refund failed"),
  });

  return (
    <Modal open onClose={onClose} title="Confirm Refund" size="sm"
      description={`${payment.receipt_number} — ${currency(payment.amount)}`}
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={refundMutation.isPending}>Cancel</Button>
          <Button variant="danger" onClick={() => refundMutation.mutate()} loading={refundMutation.isPending} disabled={!confirmed}>
            Process Refund
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <div className="rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 p-3 flex items-start gap-2">
          <ExclamationTriangleIcon className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-amber-800 dark:text-amber-300">Are you sure?</p>
            <p className="text-xs text-amber-700 dark:text-amber-400 mt-1">
              This will refund {currency(payment.amount)} to the payer. The invoice balance will be adjusted.
            </p>
          </div>
        </div>

        <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3 space-y-1 text-sm">
          <div className="flex justify-between"><span className="text-slate-500">Receipt</span><span className="font-mono font-medium">{payment.receipt_number}</span></div>
          <div className="flex justify-between"><span className="text-slate-500">Amount</span><span className="font-bold">{currency(payment.amount)}</span></div>
          <div className="flex justify-between"><span className="text-slate-500">Method</span><span className="capitalize">{METHOD_LABELS[payment.payment_method] ?? payment.payment_method}</span></div>
        </div>

        <Select
          label="Refund Gateway"
          value={gateway}
          onChange={(e) => setGateway(e.target.value as typeof gateway)}
          options={[
            { value: "stripe", label: "Stripe (Card Payments)" },
            { value: "nepali", label: "Khalti / eSewa" },
          ]}
        />

        <div>
          <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Reason for Refund</label>
          <textarea value={reason} onChange={(e) => setReason(e.target.value)} rows={2} placeholder="e.g. Duplicate payment, student withdrew…"
            className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400" />
        </div>

        <label className="flex items-start gap-3 cursor-pointer">
          <input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)}
            className="mt-0.5 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
          <span className="text-sm text-slate-600 dark:text-slate-400">
            I confirm this refund is authorized
          </span>
        </label>
      </div>
    </Modal>
  );
}

export default function PaymentHistoryPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [methodFilter, setMethodFilter] = useState("all");
  const [detailPayment, setDetailPayment] = useState<Payment | null>(null);
  const [refundingPayment, setRefundingPayment] = useState<Payment | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["payments", "all", statusFilter, methodFilter, search],
    queryFn: () => api.get<PaginatedResponse<Payment>>("/fees/payments/", {
      status: statusFilter === "all" ? undefined : statusFilter,
      payment_method: methodFilter === "all" ? undefined : methodFilter,
      search: search || undefined,
    }),
  });

  const payments = data?.results ?? [];

  const summary = useMemo(() => ({
    total: payments.reduce((s, p) => s + Number(p.amount), 0),
    successful: payments.filter((p) => p.status === "successful").reduce((s, p) => s + Number(p.amount), 0),
    refunded: payments.filter((p) => p.status === "refunded").reduce((s, p) => s + Number(p.amount), 0),
    failed: payments.filter((p) => p.status === "failed").length,
  }), [payments]);

  const handleExport = () => {
    const cols = [
      { key: "receipt_number", label: "Receipt #" },
      { key: "invoice_number", label: "Invoice #" },
      { key: "student_name", label: "Student" },
      { key: "amount", label: "Amount" },
      { key: "payment_method", label: "Method" },
      { key: "status", label: "Status" },
      { key: "paid_at", label: "Date" },
    ];
    const rows = payments.map((p) => ({
      receipt_number: p.receipt_number,
      invoice_number: p.invoice_number,
      student_name: p.student_name,
      amount: Number(p.amount).toFixed(2),
      payment_method: METHOD_LABELS[p.payment_method] ?? p.payment_method,
      status: p.status,
      paid_at: p.paid_at ? dayjs(p.paid_at).format("YYYY-MM-DD HH:mm") : "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, `payments-${dayjs().format("YYYY-MM-DD")}.csv`);
    toast.success("Payments exported");
  };

  const handleRefundSuccess = () => {
    qc.invalidateQueries({ queryKey: ["payments"] });
    setRefundingPayment(null);
  };

  const columns: Column<Payment>[] = [
    {
      key: "receipt_number",
      header: "Receipt #",
      render: (p) => <span className="font-mono text-xs text-slate-600 dark:text-slate-400">{p.receipt_number}</span>,
    },
    {
      key: "student_name",
      header: "Student",
      render: (p) => <span className="font-medium text-slate-800 dark:text-slate-200">{p.student_name}</span>,
    },
    {
      key: "amount",
      header: "Amount",
      render: (p) => <span className="font-semibold text-green-600">${Number(p.amount).toLocaleString()}</span>,
    },
    {
      key: "payment_method",
      header: "Method",
      render: (p) => <span className="capitalize text-slate-600 dark:text-slate-400 text-sm">{METHOD_LABELS[p.payment_method] ?? p.payment_method}</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (p) => <Badge color={STATUS_COLORS[p.status] ?? "slate"} dot>{p.status.charAt(0).toUpperCase() + p.status.slice(1)}</Badge>,
    },
    {
      key: "paid_at",
      header: "Date",
      render: (p) => <span className="text-sm text-slate-500 dark:text-slate-400">{p.paid_at ? dayjs(p.paid_at).format("MMM D, YYYY") : "—"}</span>,
    },
    {
      key: "action",
      header: "Actions",
      render: (p) => (
        <div className="flex gap-1">
          <Button variant="ghost" size="sm" onClick={() => setDetailPayment(p)}>
            <ReceiptPercentIcon className="h-3.5 w-3.5" />
          </Button>
          {p.status === "successful" && (
            <Button variant="ghost" size="sm" className="text-red-500 hover:text-red-700" onClick={() => setRefundingPayment(p)}>
              <ArrowPathIcon className="h-3.5 w-3.5" />
            </Button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Payment History</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">All payments across the school</p>
        </div>
        <Button variant="secondary" onClick={handleExport} leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}>Export CSV</Button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Total Received</p>
          <p className="text-xl font-bold text-green-600">${(summary.total / 1000).toFixed(1)}K</p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Successful Payments</p>
          <p className="text-xl font-bold text-slate-900 dark:text-white">${(summary.successful / 1000).toFixed(1)}K</p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Refunded</p>
          <p className="text-xl font-bold text-blue-600">${(summary.refunded / 1000).toFixed(1)}K</p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Failed Transactions</p>
          <p className="text-xl font-bold text-red-600">{summary.failed}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700 flex flex-wrap items-end gap-3">
        <div className="flex-1 min-w-48">
          <Input type="search" placeholder="Search student or receipt…" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          options={[
            { value: "all", label: "All Status" },
            { value: "successful", label: "Successful" },
            { value: "refunded", label: "Refunded" },
            { value: "failed", label: "Failed" },
            { value: "pending", label: "Pending" },
          ]}
        />
        <Select value={methodFilter} onChange={(e) => setMethodFilter(e.target.value)}
          options={[
            { value: "all", label: "All Methods" },
            { value: "cash", label: "Cash" },
            { value: "bank_transfer", label: "Bank Transfer" },
            { value: "card", label: "Card" },
            { value: "cheque", label: "Cheque" },
            { value: "online", label: "Online" },
            { value: "khalti", label: "Khalti" },
            { value: "esewa", label: "eSewa" },
          ]}
        />
      </div>

      {/* Payments table */}
      {!isLoading && payments.length === 0 ? (
        <div className="rounded-xl bg-white dark:bg-slate-800 shadow-sm border border-slate-100 dark:border-slate-700">
          <EmptyState icon={BanknotesIcon} title="No payments found" description="Try adjusting your filters." />
        </div>
      ) : (
        <div className="rounded-xl bg-white dark:bg-slate-800 shadow-sm border border-slate-100 dark:border-slate-700 overflow-hidden">
          <DataTable<Payment> columns={columns} data={payments} loading={isLoading}
            rowKey={(p) => p.id} onRowClick={(p) => setDetailPayment(p)} />
        </div>
      )}

      {detailPayment && (
        <PaymentDetailModal payment={detailPayment} open onClose={() => setDetailPayment(null)}
          onRefund={(p) => { setDetailPayment(null); setRefundingPayment(p); }} />
      )}

      {refundingPayment && (
        <RefundConfirmModal payment={refundingPayment} onClose={() => setRefundingPayment(null)} onSuccess={handleRefundSuccess} />
      )}
    </div>
  );
}
