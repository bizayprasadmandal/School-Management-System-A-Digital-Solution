/** Accountant Refund Management — process refunds, view refund history */
import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowPathIcon, BanknotesIcon, ShieldCheckIcon,
  ExclamationTriangleIcon, MagnifyingGlassIcon,
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

function ProcessRefundModal({
  open, onClose, onSuccess,
}: {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [paymentId, setPaymentId] = useState("");
  const [reason, setReason] = useState("");
  const [gateway, setGateway] = useState<"stripe" | "nepali">("stripe");
  const [confirmed, setConfirmed] = useState(false);
  const [paymentLookup, setPaymentLookup] = useState<Payment | null>(null);

  // Look up payment by ID
  const { isFetching: lookingUp } = useQuery({
    queryKey: ["payment-lookup", paymentId],
    queryFn: async () => {
      const data = await api.get<PaginatedResponse<Payment>>("/fees/payments/", { search: paymentId });
      const match = data.results.find((p) => p.id === paymentId || p.receipt_number === paymentId);
      setPaymentLookup(match ?? null);
      return match;
    },
    enabled: paymentId.length >= 8,
    staleTime: 0,
  });

  const refundMutation = useMutation({
    mutationFn: () => {
      const endpoint = gateway === "stripe" ? "/fees/stripe/refund/" : "/fees/nepali/refund/";
      return api.post(endpoint, { payment_id: paymentId, reason: reason.trim() || "Refund requested" });
    },
    onSuccess: () => {
      toast.success("Refund processed successfully");
      setPaymentId("");
      setReason("");
      setConfirmed(false);
      setPaymentLookup(null);
      onSuccess();
    },
    onError: (err: any) => toast.error(err?.message || "Refund failed"),
  });

  return (
    <Modal open={open} onClose={onClose} title="Process Refund" size="md"
      description="Refund a successful payment via gateway"
      footer={
        <>
          <Button variant="secondary" onClick={onClose} disabled={refundMutation.isPending}>Cancel</Button>
          <Button variant="danger" onClick={() => refundMutation.mutate()}
            loading={refundMutation.isPending} disabled={!confirmed || !paymentId}>
            Process Refund
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <div className="rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 p-3 flex items-start gap-2">
          <ExclamationTriangleIcon className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-amber-800 dark:text-amber-300">Refund will be processed via the selected gateway. This action cannot be undone.</p>
        </div>

        <Input label="Payment ID or Receipt #" value={paymentId}
          onChange={(e) => { setPaymentId(e.target.value); setPaymentLookup(null); }}
          placeholder="e.g. RCP-XXXXXXXX or payment UUID" />

        {lookingUp && <p className="text-xs text-slate-500">Looking up payment…</p>}
        {paymentLookup && (
          <div className="rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 p-3 text-sm">
            <p className="font-semibold text-green-800 dark:text-green-300">Payment Found</p>
            <p className="text-green-700 dark:text-green-400 mt-1">
              {paymentLookup.student_name} · {currency(paymentLookup.amount)} · {paymentLookup.receipt_number}
            </p>
          </div>
        )}

        <Select label="Refund Gateway" value={gateway}
          onChange={(e) => setGateway(e.target.value as typeof gateway)}
          options={[
            { value: "stripe", label: "Stripe (Card Payments)" },
            { value: "nepali", label: "Khalti / eSewa" },
          ]}
        />

        <div>
          <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Reason</label>
          <textarea value={reason} onChange={(e) => setReason(e.target.value)} rows={2}
            placeholder="e.g. Duplicate payment, student withdrew…"
            className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400" />
        </div>

        <label className="flex items-start gap-3 cursor-pointer">
          <input type="checkbox" checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            className="mt-0.5 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
          <span className="text-sm text-slate-600 dark:text-slate-400">I confirm this refund is authorized</span>
        </label>
      </div>
    </Modal>
  );
}

export default function RefundManagementPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [showProcessModal, setShowProcessModal] = useState(false);
  const [detailPayment, setDetailPayment] = useState<Payment | null>(null);
  const [refundingPayment, setRefundingPayment] = useState<Payment | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ["payments", "refunds", search],
    queryFn: () => api.get<PaginatedResponse<Payment>>("/fees/payments/", {
      status: "refunded",
      search: search || undefined,
    }),
  });

  const payments = data?.results ?? [];

  const summary = useMemo(() => ({
    total_refunded: payments.reduce((s, p) => s + Number(p.amount), 0),
    count: payments.length,
    by_method: payments.reduce((acc, p) => {
      acc[p.payment_method] = (acc[p.payment_method] ?? 0) + Number(p.amount);
      return acc;
    }, {} as Record<string, number>),
  }), [payments]);

  const handleRefundSuccess = () => {
    qc.invalidateQueries({ queryKey: ["payments"] });
    setShowProcessModal(false);
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
      header: "Amount Refunded",
      render: (p) => <span className="font-semibold text-blue-600">${Number(p.amount).toLocaleString()}</span>,
    },
    {
      key: "payment_method",
      header: "Original Method",
      render: (p) => <span className="capitalize text-slate-600 dark:text-slate-400 text-sm">{p.payment_method}</span>,
    },
    {
      key: "paid_at",
      header: "Refund Date",
      render: (p) => <span className="text-sm text-slate-500">{p.paid_at ? dayjs(p.paid_at).format("MMM D, YYYY") : "—"}</span>,
    },
    {
      key: "notes",
      header: "Reason",
      render: (p) => <span className="text-sm text-slate-500 dark:text-slate-400 truncate max-w-[200px] block">{p.notes || "—"}</span>,
    },
    {
      key: "action",
      header: "Details",
      render: (p) => (
        <Button variant="ghost" size="sm" onClick={() => setDetailPayment(p)}>
          <ShieldCheckIcon className="h-3.5 w-3.5" />
        </Button>
      ),
    },
  ];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Refund Management</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Process and track payment refunds</p>
        </div>
        <Button onClick={() => setShowProcessModal(true)}
          leftIcon={<ArrowPathIcon className="h-4 w-4" />}>
          Process Refund
        </Button>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Total Refunded</p>
          <p className="text-xl font-bold text-blue-600">${(summary.total_refunded / 1000).toFixed(1)}K</p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Refund Count</p>
          <p className="text-xl font-bold text-slate-900 dark:text-white">{summary.count}</p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">Avg Refund</p>
          <p className="text-xl font-bold text-slate-900 dark:text-white">
            {summary.count > 0 ? `$${(summary.total_refunded / summary.count / 1000).toFixed(1)}K` : "—"}
          </p>
        </div>
      </div>

      {/* Search */}
      <div className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700">
        <Input type="search" placeholder="Search by student name or receipt…" value={search}
          onChange={(e) => setSearch(e.target.value)} />
      </div>

      {/* Refunds table */}
      {!isLoading && payments.length === 0 ? (
        <div className="rounded-xl bg-white dark:bg-slate-800 shadow-sm border border-slate-100 dark:border-slate-700">
          <EmptyState icon={ShieldCheckIcon} title="No refunds yet"
            description="Refunded payments will appear here." />
        </div>
      ) : (
        <div className="rounded-xl bg-white dark:bg-slate-800 shadow-sm border border-slate-100 dark:border-slate-700 overflow-hidden">
          <DataTable<Payment> columns={columns} data={payments} loading={isLoading}
            rowKey={(p) => p.id} onRowClick={(p) => setDetailPayment(p)} />
        </div>
      )}

      {showProcessModal && (
        <ProcessRefundModal open onClose={() => setShowProcessModal(false)} onSuccess={handleRefundSuccess} />
      )}

      {detailPayment && (
        <Modal open onClose={() => setDetailPayment(null)} title="Refund Details" size="sm"
          description={`${detailPayment.receipt_number} — ${currency(detailPayment.amount)}`}
        >
          <div className="space-y-3 text-sm">
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Receipt</p>
                <p className="font-mono font-semibold">{detailPayment.receipt_number}</p>
              </div>
              <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Invoice</p>
                <p className="font-mono">{detailPayment.invoice_number}</p>
              </div>
              <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Student</p>
                <p className="font-semibold">{detailPayment.student_name}</p>
              </div>
              <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
                <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Amount</p>
                <p className="font-bold text-blue-600">{currency(detailPayment.amount)}</p>
              </div>
            </div>
            {detailPayment.notes && (
              <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3">
                <p className="text-xs text-slate-500 mb-1">Reason</p>
                <p className="text-slate-900 dark:text-slate-200">{detailPayment.notes}</p>
              </div>
            )}
            {Boolean(detailPayment.gateway_response?.refund_id) && (
              <div className="rounded-lg bg-blue-50 dark:bg-blue-900/20 p-3 flex items-start gap-2">
                <ShieldCheckIcon className="h-5 w-5 text-blue-500 flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-blue-800">Gateway Refund ID</p>
                  <p className="font-mono text-xs text-blue-700 break-all">{String(detailPayment.gateway_response?.refund_id)}</p>
                </div>
              </div>
            )}
          </div>
        </Modal>
      )}

      {refundingPayment && (
        <ProcessRefundModal open onClose={() => setRefundingPayment(null)} onSuccess={handleRefundSuccess} />
      )}
    </div>
  );
}
