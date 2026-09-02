/**
 * Accountant Purchase Orders Page — manage POs
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Reorder } from "framer-motion";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import { useKeyboardShortcuts } from "../../hooks/useKeyboardShortcuts";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
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
  po_number: string;
  vendor: string;
  description: string;
  total_amount: number;
  status: string;
  requested_by: string;
  created_at: string;
}

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

export default function PurchaseOrdersPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<PurchaseOrder | null>(null);

  const { data: allOrders = [], isLoading } = useQuery({
    queryKey: ["accountant-pos"],
    queryFn: async () => {
      const r = await api.get<{ results: PurchaseOrder[] }>("/fees/purchase-orders/");
      return r.results ?? [];
    },
  });

  const createPO = useMutation({
    mutationFn: (data: Partial<PurchaseOrder>) => api.post("/fees/purchase-orders/", data),
    onSuccess: () => {
      toast.success("PO created");
      qc.invalidateQueries({ queryKey: ["accountant-pos"] });
      setShowForm(false);
    },
  });

  const updatePO = useMutation({
    mutationFn: (data: Partial<PurchaseOrder>) =>
      api.patch(`/fees/purchase-orders/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("PO updated");
      qc.invalidateQueries({ queryKey: ["accountant-pos"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deletePO = useMutation({
    mutationFn: (id: string) => api.delete(`/fees/purchase-orders/${id}/`),
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
          (o as any).vendor?.toLowerCase().includes(q) ||
          (o as any).description?.toLowerCase().includes(q),
      );
    }
    if (statusFilter !== "all") {
      items = items.filter((o) => (o as any).status === statusFilter);
    }
    return items;
  }, [allOrders, search, statusFilter]);

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
      { key: "po_number", label: "PO Number" },
      { key: "vendor", label: "Vendor" },
      { key: "total_amount", label: "Amount" },
      { key: "status", label: "Status" },
    ];
    const rows = orders.map((row) => ({
      po_number: row.po_number ?? "",
      vendor: row.vendor ?? "",
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
        bulk.selectedArray.map((id) => api.delete("/fees/purchase-orders//" + id + "/")),
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
            <option value="draft">Draft</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="completed">Completed</option>
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
        <POSkeleton />
      ) : orders.length === 0 ? (
        <EmptyState
          icon={ClipboardDocumentListIcon}
          title="No purchase orders"
          description="Create purchase orders for school supplies and services."
        />
      ) : (
        <div className="space-y-3">
          {
            /* Drag-and-drop: Use Reorder.Group with orderedItems for full DnD */
            paginatedOrders.map((order) => (
              <div
                key={order.id}
                className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
              >
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">
                    {order.po_number}
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {order.vendor || "—"} · {order.description || "—"}
                  </p>
                  <p className="text-xs text-slate-400">
                    {order.requested_by || "—"} ·{" "}
                    {order.created_at ? new Date(order.created_at).toLocaleDateString() : "—"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <div className="text-right">
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                      ${(order.total_amount ?? 0).toLocaleString()}
                    </p>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        order.status === "approved" || order.status === "received"
                          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                          : order.status === "pending_approval"
                            ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                            : order.status === "cancelled"
                              ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                              : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
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
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => {
                        if (confirm("Delete this PO?")) deletePO.mutate(order.id);
                      }}
                      className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          }
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
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
  saving,
  onSave,
  onCancel,
}: {
  po: PurchaseOrder | null;
  saving: boolean;
  onSave: (data: Partial<PurchaseOrder>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    po_number: po?.po_number ?? "",
    vendor: po?.vendor ?? "",
    description: po?.description ?? "",
    total_amount: po?.total_amount ?? 0,
    requested_by: po?.requested_by ?? "",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.vendor.trim()) return toast.error("Vendor required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">PO Number</label>
          <input
            value={f.po_number}
            onChange={(e) => setF((p) => ({ ...p, po_number: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Vendor *</label>
          <input
            value={f.vendor}
            onChange={(e) => setF((p) => ({ ...p, vendor: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Description</label>
        <textarea
          value={f.description}
          onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
          rows={2}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Total Amount ($)</label>
          <input
            type="number"
            min={0}
            step="0.01"
            value={f.total_amount}
            onChange={(e) => setF((p) => ({ ...p, total_amount: Number(e.target.value) }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Requested By</label>
          <input
            value={f.requested_by}
            onChange={(e) => setF((p) => ({ ...p, requested_by: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
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
