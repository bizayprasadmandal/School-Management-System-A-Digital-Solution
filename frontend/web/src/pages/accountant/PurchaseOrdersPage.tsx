/**
 * Accountant Purchase Orders Page — manage POs.
 *
 * Backed by the real inventory API: /inventory/purchase-orders/. Suppliers
 * come from /inventory/suppliers/ for the form's FK select; order numbers
 * are auto-generated server-side when omitted.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import { InfiniteScroll } from "../../components/common/InfiniteScroll";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { BulkActionBar } from "../../components/common/BulkActionBar";
import {
  ClipboardDocumentListIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ArrowDownTrayIcon,
  Bars3Icon,
} from "@heroicons/react/24/outline";

interface PurchaseOrder {
  id: string;
  order_number: string;
  supplier: string | null;
  supplier_name?: string;
  order_date: string;
  expected_date: string | null;
  status: string;
  subtotal: string | number;
  tax_amount: string | number;
  total_amount: string | number;
  notes: string;
  ordered_by?: string | number | null;
}

interface SupplierOption {
  id: string;
  name: string;
}

const STATUS_OPTIONS = [
  { value: "draft", label: "Draft" },
  { value: "submitted", label: "Submitted" },
  { value: "confirmed", label: "Confirmed" },
  { value: "partially_received", label: "Partially Received" },
  { value: "received", label: "Fully Received" },
  { value: "cancelled", label: "Cancelled" },
];

function POSkeleton() {
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

const num = (v: string | number | undefined | null) => Number(v ?? 0);
const fmtRs = (v: string | number | undefined | null) =>
  `Rs. ${num(v).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

export default function PurchaseOrdersPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<PurchaseOrder | null>(null);
  const shortcut = useShortcutHelp();

  const { data: ordersPage, isLoading } = useQuery({
    queryKey: ["accountant-pos"],
    queryFn: async () => {
      const r = await api.get<{ count: number; results: PurchaseOrder[] }>(
        "/inventory/purchase-orders/",
        { page_size: 200 },
      );
      return r.results ?? [];
    },
    refetchInterval: 60000,
  });
  const allOrders = React.useMemo(() => ordersPage ?? [], [ordersPage]);

  const { data: suppliers = [] } = useQuery({
    queryKey: ["supplier-options"],
    queryFn: async () => {
      const r = await api.get<{ results: SupplierOption[] }>("/inventory/suppliers/", {
        page_size: 200,
      });
      return r.results ?? [];
    },
  });
  const supplierName = React.useMemo(() => {
    const m = new Map<string, string>();
    suppliers.forEach((s) => m.set(s.id, s.name));
    return (id: string | null) => (id ? m.get(id) ?? "—" : "—");
  }, [suppliers]);

  const createPO = useMutation({
    mutationFn: (data: Partial<PurchaseOrder>) => api.post("/inventory/purchase-orders/", data),
    onSuccess: () => {
      toast.success("PO created");
      qc.invalidateQueries({ queryKey: ["accountant-pos"] });
      setShowForm(false);
    },
  });

  const updatePO = useMutation({
    mutationFn: (data: Partial<PurchaseOrder>) =>
      api.patch(`/inventory/purchase-orders/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("PO updated");
      qc.invalidateQueries({ queryKey: ["accountant-pos"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deletePO = useMutation({
    mutationFn: (id: string) => api.delete(`/inventory/purchase-orders/${id}/`),
    onSuccess: () => {
      toast.success("PO deleted");
      qc.invalidateQueries({ queryKey: ["accountant-pos"] });
    },
  });

  const orders = React.useMemo(() => {
    let items = allOrders;
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(
        (o) =>
          o.order_number?.toLowerCase().includes(q) ||
          supplierName(o.supplier)?.toLowerCase().includes(q) ||
          o.notes?.toLowerCase().includes(q),
      );
    }
    if (statusFilter !== "all") {
      items = items.filter((o) => o.status === statusFilter);
    }
    return items;
  }, [allOrders, search, statusFilter, supplierName]);

  const paginatedOrders = React.useMemo(() => {
    const start = (page - 1) * 12;
    return orders.slice(start, start + 12);
  }, [orders, page]);

  const totalPages = Math.ceil(orders.length / 12);

  const bulk = useBulkSelect(orders);
  const [reorderMode, setReorderMode] = React.useState(false);
  const [orderedItems, setOrderedItems] = React.useState(orders);

  React.useEffect(() => {
    setOrderedItems(orders);
  }, [orders]);

  const handleExport = () => {
    const cols = [
      { key: "order_number", label: "PO Number" },
      { key: "supplier", label: "Supplier" },
      { key: "order_date", label: "Order Date" },
      { key: "expected_date", label: "Expected" },
      { key: "total_amount", label: "Amount" },
      { key: "status", label: "Status" },
    ];
    const rows = orders.map((row) => ({
      order_number: row.order_number ?? "",
      supplier: supplierName(row.supplier),
      order_date: row.order_date ?? "",
      expected_date: row.expected_date ?? "",
      total_amount: row.total_amount ?? "",
      status: row.status ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "purchase-orders-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(
        bulk.selectedArray.map((id) => api.delete("/inventory/purchase-orders/" + id + "/")),
      );
      toast.success(`${bulk.selectedCount} items deleted`);
      bulk.clear();
      qc.invalidateQueries({ queryKey: ["accountant-pos"] });
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
      <KeyboardShortcutHelp open={shortcut.open} onClose={() => shortcut.setOpen(false)} />
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Purchase Orders</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Manage purchase orders for school supplies
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
        <div className="flex items-center gap-1 rounded-lg border border-slate-200 p-0.5 dark:border-slate-700">
          <button
            onClick={() => setViewMode("pagination")}
            className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
              viewMode === "pagination"
                ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
            }`}
          >
            Pages
          </button>
          <button
            onClick={() => setViewMode("infinite")}
            className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
              viewMode === "infinite"
                ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
            }`}
          >
            Scroll
          </button>
        </div>
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
          Create PO
        </Button>
      </div>

      {bulk.selectedCount > 0 && (
        <BulkActionBar
          selectedCount={bulk.selectedCount}
          onExport={handleBulkExport}
          onDelete={handleBulkDelete}
          onClear={bulk.clear}
        />
      )}

      {/* Search + Filters */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700 space-y-3">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              placeholder="Search purchase orders..."
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
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          {(search || statusFilter !== "all") && (
            <button
              onClick={() => {
                setSearch("");
                setStatusFilter("all");
              }}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-400 dark:hover:bg-slate-700"
              aria-label="Clear filters"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {isLoading ? (
        <POSkeleton />
      ) : orders.length === 0 ? (
        <EmptyState
          icon={ClipboardDocumentListIcon}
          title="No purchase orders"
          description="Create purchase orders for school supplies and services."
        />
      ) : (
        <div className="space-y-3">
          {(viewMode === "infinite" ? orders.slice(0, 12 * 3) : paginatedOrders).map((order) => (
            <div
              key={order.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {order.order_number}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {supplierName(order.supplier)} · {order.notes || "—"}
                </p>
                <p className="text-xs text-slate-400">
                  Ordered {order.order_date ? dayjs(order.order_date).format("MMM D, YYYY") : "—"}
                  {order.expected_date
                    ? ` · Expected ${dayjs(order.expected_date).format("MMM D, YYYY")}`
                    : ""}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-right">
                  <p className="text-sm font-medium text-slate-900 dark:text-white">
                    {fmtRs(order.total_amount)}
                  </p>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      order.status === "received"
                        ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                        : order.status === "cancelled"
                          ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                          : order.status === "confirmed" || order.status === "partially_received"
                            ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                            : "bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300"
                    }`}
                  >
                    {(order.status || "draft").replace(/_/g, " ")}
                  </span>
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(order);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                    aria-label="Edit"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this PO?")) deletePO.mutate(order.id);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                    aria-label="Delete"
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
      {viewMode === "pagination" && totalPages > 1 && (
        <Pagination page={page} total={orders.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit PO" : "Create PO"}
      >
        <POForm
          po={editing}
          suppliers={suppliers}
          saving={createPO.isPending || updatePO.isPending}
          onSave={(data) => {
            if (editing) updatePO.mutate(data);
            else createPO.mutate(data);
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

function POForm({
  po,
  suppliers,
  saving,
  onSave,
  onCancel,
}: {
  po: PurchaseOrder | null;
  suppliers: SupplierOption[];
  saving: boolean;
  onSave: (data: Partial<PurchaseOrder>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    order_number: po?.order_number ?? "",
    supplier: po?.supplier ?? "",
    order_date: po?.order_date ?? dayjs().format("YYYY-MM-DD"),
    expected_date: po?.expected_date ?? "",
    status: po?.status ?? "draft",
    subtotal: num(po?.subtotal),
    tax_amount: num(po?.tax_amount),
    notes: po?.notes ?? "",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.supplier) return toast.error("Supplier required");
        onSave({
          ...f,
          supplier: f.supplier,
          expected_date: f.expected_date || undefined,
          subtotal: String(f.subtotal),
          tax_amount: String(f.tax_amount),
        });
      }}
      className="space-y-4"
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">PO Number</label>
          <input
            value={f.order_number}
            onChange={(e) => setF((p) => ({ ...p, order_number: e.target.value }))}
            placeholder="Auto-generated if blank"
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Supplier *</label>
          <select
            value={f.supplier}
            onChange={(e) => setF((p) => ({ ...p, supplier: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-700 dark:text-slate-200"
            required
          >
            <option value="">Select supplier…</option>
            {suppliers.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Order Date</label>
          <input
            type="date"
            value={f.order_date}
            onChange={(e) => setF((p) => ({ ...p, order_date: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Expected Date</label>
          <input
            type="date"
            value={f.expected_date}
            onChange={(e) => setF((p) => ({ ...p, expected_date: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Subtotal (Rs.)</label>
          <input
            type="number"
            min={0}
            step="0.01"
            value={f.subtotal}
            onChange={(e) => setF((p) => ({ ...p, subtotal: Number(e.target.value) }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Tax (Rs.)</label>
          <input
            type="number"
            min={0}
            step="0.01"
            value={f.tax_amount}
            onChange={(e) => setF((p) => ({ ...p, tax_amount: Number(e.target.value) }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Status</label>
          <select
            value={f.status}
            onChange={(e) => setF((p) => ({ ...p, status: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-700 dark:text-slate-200"
          >
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Notes</label>
        <textarea
          value={f.notes}
          onChange={(e) => setF((p) => ({ ...p, notes: e.target.value }))}
          rows={2}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {po ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
