/**
 * Accountant Invoices Page — generate and manage student invoices
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Reorder } from "framer-motion";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import { BulkActionBar } from "../../components/common/BulkActionBar";
import {
  DocumentTextIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ArrowDownTrayIcon,
  Bars3Icon,
} from "@heroicons/react/24/outline";

interface Invoice {
  id: string;
  invoice_number: string;
  student_name: string;
  description: string;
  amount: number;
  due_date: string;
  status: string;
}

function InvoiceSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="h-24 relative overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
        >
          <div
            className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-slate-200/50 to-transparent dark:via-slate-600/30"
            style={{ backgroundSize: "200% 100%" }}
          />
        </div>
      ))}
    </div>
  );
}

export default function InvoicesPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Invoice | null>(null);

  const { data: allInvoices = [], isLoading } = useQuery({
    queryKey: ["accountant-invoices"],
    queryFn: async () => {
      const r = await api.get<{ results: Invoice[] }>("/fees/invoices/");
      return r.results ?? [];
    },
  });

  const invoices = React.useMemo(() => {
    let items = allInvoices;
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(
        (i) =>
          i.invoice_number?.toLowerCase().includes(q) ||
          (i as any).vendor?.toLowerCase().includes(q) ||
          (i as any).client?.toLowerCase().includes(q) ||
          i.description?.toLowerCase().includes(q),
      );
    }
    if (statusFilter !== "all") {
      items = items.filter((i) => i.status === statusFilter);
    }
    return items;
  }, [allInvoices, search, statusFilter]);

  const createInvoice = useMutation({
    mutationFn: (data: Partial<Invoice>) => api.post("/fees/invoices/", data),
    onSuccess: () => {
      toast.success("Invoice created");
      qc.invalidateQueries({ queryKey: ["accountant-invoices"] });
      setShowForm(false);
    },
  });

  const updateInvoice = useMutation({
    mutationFn: (data: Partial<Invoice>) => api.patch(`/fees/invoices/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Invoice updated");
      qc.invalidateQueries({ queryKey: ["accountant-invoices"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteInvoice = useMutation({
    mutationFn: (id: string) => api.delete(`/fees/invoices/${id}/`),
    onSuccess: () => {
      toast.success("Invoice deleted");
      qc.invalidateQueries({ queryKey: ["accountant-invoices"] });
    },
  });

  const paginatedInvoices = React.useMemo(() => {
    const start = (page - 1) * 12;
    return invoices.slice(start, start + 12);
  }, [invoices, page]);

  const totalPages = Math.ceil(invoices.length / 12);

  const bulk = useBulkSelect(invoices);
  const [reorderMode, setReorderMode] = React.useState(false);
  const [orderedItems, setOrderedItems] = React.useState(invoices);

  React.useEffect(() => {
    setOrderedItems(invoices);
  }, [invoices]);

  const handleExport = () => {
    const cols = [
      { key: "invoice_number", label: "Invoice #" },
      { key: "client", label: "Client" },
      { key: "total_amount", label: "Amount" },
      { key: "status", label: "Status" },
    ];
    const rows = invoices.map((row) => ({
      invoice_number: row.invoice_number ?? "",
      client: row.description ?? "",
      total_amount: row.amount ?? "",
      status: row.status ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "invoices-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(bulk.selectedArray.map((id) => api.delete("/fees/invoices//" + id + "/")));
      toast.success(`${bulk.selectedCount} items deleted`);
      bulk.clear();
      qc.invalidateQueries({ queryKey: ["accountant-invoices"] });
    } catch {
      toast.error("Failed to delete items");
    }
  };

  const handleBulkExport = () => {
    const cols = [{ key: "id", label: "ID" }];
    const rows = bulk.selectedItems.map((item) => ({ id: item.id }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "bulk-export-" + new Date().toISOString().slice(0, 10) + ".csv");
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Invoices</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Generate and manage student invoices
          </p>
        </div>

        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={bulk.allSelected}
            ref={(el) => {
              if (el) el.indeterminate = bulk.someSelected;
            }}
            onChange={bulk.toggleAll}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
          />
          <span className="text-sm text-slate-500 dark:text-slate-400">Select all</span>
        </label>
        <Button
          variant={reorderMode ? "primary" : "secondary"}
          leftIcon={<Bars3Icon className="h-4 w-4" />}
          onClick={() => setReorderMode(!reorderMode)}
        >
          {reorderMode ? "Done" : "Reorder"}
        </Button>
        <Button
          variant="secondary"
          leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
          onClick={handleExport}
        >
          Export CSV
        </Button>
        <Button
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <PlusIcon className="mr-1.5 h-4 w-4" />
          Create Invoice
        </Button>
      </div>

      {/* Search + Filters */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700 space-y-3">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              placeholder="Search invoices..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-400"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-700 dark:text-white"
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="sent">Sent</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
          </select>
          {(search || statusFilter !== "all") && (
            <button
              onClick={() => {
                setSearch("");
                setStatusFilter("all");
              }}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-400 dark:hover:bg-slate-700"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {isLoading ? (
        <InvoiceSkeleton />
      ) : invoices.length === 0 ? (
        <EmptyState
          icon={DocumentTextIcon}
          title="No invoices"
          description="Generate and manage student invoices."
        />
      ) : (
        <div className="space-y-3">
          {invoices.map((inv) => (
            <div
              key={inv.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {inv.invoice_number}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {inv.student_name || "—"} · {inv.description || "—"}
                </p>
                <p className="text-xs text-slate-400">
                  Due: {inv.due_date ? new Date(inv.due_date).toLocaleDateString() : "—"}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-right">
                  <p className="text-sm font-medium text-slate-900 dark:text-white">
                    ${(inv.amount ?? 0).toLocaleString()}
                  </p>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      inv.status === "paid"
                        ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                        : inv.status === "overdue"
                          ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                          : inv.status === "sent"
                            ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                            : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                    }`}
                  >
                    {inv.status}
                  </span>
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(inv);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this invoice?")) deleteInvoice.mutate(inv.id);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination page={page} total={invoices.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Invoice" : "Create Invoice"}
      >
        <InvoiceForm
          invoice={editing}
          saving={createInvoice.isPending || updateInvoice.isPending}
          onSave={(data) => {
            if (editing) updateInvoice.mutate(data);
            else createInvoice.mutate(data);
          }}
          onCancel={() => {
            setShowForm(false);
            setEditing(null);
          }}
        />
      </Modal>
    </div>
  );
}

function InvoiceForm({
  invoice,
  saving,
  onSave,
  onCancel,
}: {
  invoice: Invoice | null;
  saving: boolean;
  onSave: (data: Partial<Invoice>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    invoice_number: invoice?.invoice_number ?? "",
    student_name: invoice?.student_name ?? "",
    description: invoice?.description ?? "",
    amount: invoice?.amount ?? 0,
    due_date: invoice?.due_date ?? "",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.student_name.trim()) return toast.error("Student required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Invoice Number</label>
          <input
            value={f.invoice_number}
            onChange={(e) => setF((p) => ({ ...p, invoice_number: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Student *</label>
          <input
            value={f.student_name}
            onChange={(e) => setF((p) => ({ ...p, student_name: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Description</label>
        <input
          value={f.description}
          onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Amount ($)</label>
          <input
            type="number"
            min={0}
            step="0.01"
            value={f.amount}
            onChange={(e) => setF((p) => ({ ...p, amount: Number(e.target.value) }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Due Date</label>
          <input
            type="date"
            value={f.due_date}
            onChange={(e) => setF((p) => ({ ...p, due_date: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {invoice ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
