/**
 * Admin Fees Page — Invoice management, payment recording, outstanding tracking
 */

import React, { useState } from "react";
import {
  BanknotesIcon, CheckCircleIcon, ClockIcon,
  ExclamationCircleIcon, ReceiptPercentIcon, DocumentPlusIcon,
  AcademicCapIcon, TagIcon,
} from "@heroicons/react/24/outline";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { api } from "../../api/client";
import type { FeeInvoice } from "../../types";
import {
  Button, Badge, Modal, DataTable, Input, Select, EmptyState,
} from "../../components/common";
import type { Column, BadgeColor } from "../../components/common";
import PaymentHistoryModal from "../../components/common/PaymentHistoryModal";
import GenerateInvoicesModal from "../../components/common/GenerateInvoicesModal";
import ScholarshipsPanel from "../../components/common/ScholarshipsPanel";
import FeeCategoriesPanel from "../../components/common/FeeCategoriesPanel";
import FeeStructuresPanel from "../../components/common/FeeStructuresPanel";
import dayjs from "dayjs";

const STATUS_CONFIG: Record<string, { label: string; color: BadgeColor }> = {
  unpaid:    { label: "Unpaid",   color: "amber" },
  paid:      { label: "Paid",     color: "green" },
  overdue:   { label: "Overdue",  color: "red" },
  partial:   { label: "Partial",  color: "blue" },
  waived:    { label: "Waived",   color: "slate" },
  cancelled: { label: "Cancelled", color: "slate" },
};

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
    <Modal
      open
      onClose={onClose}
      title="Record Payment"
      description={`Invoice #${invoice.invoice_number}`}
      size="md"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button onClick={() => mutate()} loading={isPending} disabled={!amount || parseFloat(amount) <= 0}>
            Record Payment
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <div className="rounded-lg bg-slate-50 p-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-slate-600">Total</span>
            <span className="font-medium text-slate-900">${invoice.total_amount.toLocaleString()}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-slate-600">Already Paid</span>
            <span className="font-medium text-green-600">${invoice.paid_amount.toLocaleString()}</span>
          </div>
          <div className="flex justify-between text-sm font-semibold border-t border-slate-200 pt-2">
            <span>Outstanding</span>
            <span className="text-red-600">${invoice.outstanding_amount.toLocaleString()}</span>
          </div>
        </div>

        <Input
          label="Amount to Pay"
          type="number"
          min={0.01}
          max={invoice.outstanding_amount}
          value={amount}
          onChange={e => setAmount(e.target.value)}
        />

        <Select
          label="Payment Method"
          value={method}
          onChange={e => setMethod(e.target.value)}
          options={[
            { value: "cash", label: "Cash" },
            { value: "bank_transfer", label: "Bank Transfer" },
            { value: "card", label: "Card" },
            { value: "cheque", label: "Cheque" },
          { value: "online", label: "Online Gateway" },
          { value: "mobile", label: "Mobile Money" },
          { value: "khalti", label: "Khalti" },
          { value: "esewa", label: "eSewa" },
          ]}
        />
      </div>
    </Modal>
  );
}

type FeeTab = "invoices" | "scholarships" | "categories";

export default function FeesPage() {
  const [tab, setTab] = useState<FeeTab>("invoices");
  const [statusFilter, setStatusFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [payingInvoice, setPayingInvoice] = useState<FeeInvoice | null>(null);
  const [historyInvoice, setHistoryInvoice] = useState<FeeInvoice | null>(null);
  const [showGenerateModal, setShowGenerateModal] = useState(false);

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

  const columns: Column<FeeInvoice>[] = [
    {
      key: "invoice_number",
      header: "Invoice #",
      render: (inv) => <span className="font-mono text-slate-600">{inv.invoice_number}</span>,
    },
    {
      key: "student",
      header: "Student",
      render: (inv) => <span className="font-medium text-slate-800">{inv.student}</span>,
    },
    {
      key: "due_date",
      header: "Due Date",
      render: (inv) => (
        <span className={dayjs(inv.due_date).isBefore(dayjs()) && inv.status === "unpaid" ? "text-red-600 font-medium" : "text-slate-600"}>
          {dayjs(inv.due_date).format("MMM D, YYYY")}
        </span>
      ),
    },
    {
      key: "total_amount",
      header: "Total",
      render: (inv) => <span className="font-medium text-slate-800">${Number(inv.total_amount).toLocaleString()}</span>,
    },
    {
      key: "paid_amount",
      header: "Paid",
      render: (inv) => <span className="text-green-600">${Number(inv.paid_amount).toLocaleString()}</span>,
    },
    {
      key: "outstanding_amount",
      header: "Outstanding",
      render: (inv) => <span className="font-semibold text-red-600">${Number(inv.outstanding_amount).toLocaleString()}</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (inv) => {
        const cfg = STATUS_CONFIG[inv.status] ?? { label: inv.status, color: "slate" as BadgeColor };
        return <Badge color={cfg.color} dot>{cfg.label}</Badge>;
      },
    },
    {
      key: "action",
      header: "Actions",
      render: (inv) => (
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setHistoryInvoice(inv)}
            leftIcon={<ReceiptPercentIcon className="h-3.5 w-3.5" />}
          >
            Payments
          </Button>
          {["unpaid", "overdue", "partial"].includes(inv.status) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setPayingInvoice(inv)}
            >
              Record
            </Button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-5">
      {/* Tab switcher */}
      <div className="flex items-center gap-1 rounded-xl bg-slate-100 p-1 w-fit">
        {[
          { key: "invoices" as FeeTab, label: "Invoices", icon: BanknotesIcon },
          { key: "categories" as FeeTab, label: "Categories", icon: TagIcon },
          { key: "scholarships" as FeeTab, label: "Scholarships", icon: AcademicCapIcon },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition-all ${
              tab === key
                ? "bg-white text-indigo-700 shadow-sm"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Fee Management</h1>
          <p className="text-sm text-slate-500 mt-0.5">Track invoices, payments and outstanding balances</p>
        </div>
        {tab === "invoices" && (
          <Button
            onClick={() => setShowGenerateModal(true)}
            leftIcon={<DocumentPlusIcon className="h-4 w-4" />}
          >
            Generate Invoices
          </Button>
        )}
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "Total Invoiced",  value: `$${(summary.total / 1000).toFixed(1)}K`, color: "bg-indigo-500", icon: BanknotesIcon },
          { label: "Collected",       value: `$${(summary.collected / 1000).toFixed(1)}K`, color: "bg-green-500", icon: CheckCircleIcon },
          { label: "Outstanding",     value: `$${(summary.outstanding / 1000).toFixed(1)}K`, color: "bg-amber-500", icon: ClockIcon },
          { label: "Overdue Invoices", value: summary.overdue, color: "bg-red-500", icon: ExclamationCircleIcon },
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

      {tab === "invoices" && (
        <>
          {/* Filters */}
          <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 flex flex-wrap items-end gap-3">
            <div className="flex-1 min-w-48">
              <Input
                type="search"
                placeholder="Search student name or invoice…"
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <Select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              options={[
                { value: "all", label: "All Status" },
                { value: "unpaid", label: "Unpaid" },
                { value: "paid", label: "Paid" },
                { value: "overdue", label: "Overdue" },
                { value: "partial", label: "Partial" },
                { value: "waived", label: "Waived" },
              ]}
            />
          </div>

          {/* Invoices table */}
          {!isLoading && invoices.length === 0 ? (
            <div className="rounded-xl bg-white shadow-sm border border-slate-100">
              <EmptyState
                icon={BanknotesIcon}
                title="No invoices found"
              />
            </div>
          ) : (
            <div className="rounded-xl bg-white shadow-sm border border-slate-100 overflow-hidden">
              <DataTable<FeeInvoice>
                columns={columns}
                data={invoices}
                loading={isLoading}
                rowKey={(inv) => inv.id}
              />
            </div>
          )}

          {payingInvoice && (
            <RecordPaymentModal invoice={payingInvoice} onClose={() => setPayingInvoice(null)} />
          )}

          {historyInvoice && (
            <PaymentHistoryModal
              invoiceId={historyInvoice.id}
              invoiceNumber={historyInvoice.invoice_number}
              open={!!historyInvoice}
              onClose={() => setHistoryInvoice(null)}
            />
          )}

          <GenerateInvoicesModal
            open={showGenerateModal}
            onClose={() => setShowGenerateModal(false)}
          />
        </>
      )}

      {tab === "categories" && (
        <div className="space-y-8">
          <FeeCategoriesPanel />
          <hr className="border-slate-200 dark:border-slate-700" />
          <FeeStructuresPanel />
        </div>
      )}

      {tab === "scholarships" && <ScholarshipsPanel />}

    </div>
  );
}
