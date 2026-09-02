/**
 * Librarian Acquisitions Page — track book purchases
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, EmptyState, Modal } from "../../components/common";
import { ShoppingCartIcon, PlusIcon, PencilIcon, TrashIcon } from "@heroicons/react/24/outline";

interface Acquisition {
  id: string;
  title: string;
  author: string;
  quantity: number;
  unit_cost: number;
  status: string;
  requested_by: string;
}

function AcquisitionSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-20 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function AcquisitionsPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Acquisition | null>(null);

  const { data: items = [], isLoading } = useQuery({
    queryKey: ["librarian-acquisitions"],
    queryFn: async () => {
      const r = await api.get<{ results: Acquisition[] }>("/library/acquisitions/");
      return r.results ?? [];
    },
  });

  const createItem = useMutation({
    mutationFn: (data: Partial<Acquisition>) => api.post("/library/acquisitions/", data),
    onSuccess: () => {
      toast.success("Acquisition requested");
      qc.invalidateQueries({ queryKey: ["librarian-acquisitions"] });
      setShowForm(false);
    },
  });

  const updateItem = useMutation({
    mutationFn: (data: Partial<Acquisition>) =>
      api.patch(`/library/acquisitions/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Acquisition updated");
      qc.invalidateQueries({ queryKey: ["librarian-acquisitions"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteItem = useMutation({
    mutationFn: (id: string) => api.delete(`/library/acquisitions/${id}/`),
    onSuccess: () => {
      toast.success("Acquisition deleted");
      qc.invalidateQueries({ queryKey: ["librarian-acquisitions"] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Acquisitions</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Track book and material purchase requests
          </p>
        </div>
        <Button
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <PlusIcon className="mr-1.5 h-4 w-4" />
          New Request
        </Button>
      </div>

      {isLoading ? (
        <AcquisitionSkeleton />
      ) : items.length === 0 ? (
        <EmptyState
          icon={ShoppingCartIcon}
          title="No acquisitions"
          description="Request new books and materials for the library."
        />
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">{item.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{item.author || "—"}</p>
                <p className="text-xs text-slate-400">
                  Qty: {item.quantity ?? 1} · ${item.unit_cost ?? "0.00"} ea ·{" "}
                  {item.requested_by || "—"}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    item.status === "received"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : item.status === "ordered"
                        ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                        : item.status === "cancelled"
                          ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                          : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                  }`}
                >
                  {item.status}
                </span>
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(item);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this request?")) deleteItem.mutate(item.id);
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

      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Request" : "New Request"}
      >
        <AcquisitionForm
          item={editing}
          saving={createItem.isPending || updateItem.isPending}
          onSave={(data) => {
            if (editing) updateItem.mutate(data);
            else createItem.mutate(data);
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

function AcquisitionForm({
  item,
  saving,
  onSave,
  onCancel,
}: {
  item: Acquisition | null;
  saving: boolean;
  onSave: (data: Partial<Acquisition>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    title: item?.title ?? "",
    author: item?.author ?? "",
    quantity: item?.quantity ?? 1,
    unit_cost: item?.unit_cost ?? 0,
    requested_by: item?.requested_by ?? "",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.title.trim()) return toast.error("Title required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div>
        <label className="mb-1 block text-sm font-medium">Title *</label>
        <input
          value={f.title}
          onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          required
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Author</label>
        <input
          value={f.author}
          onChange={(e) => setF((p) => ({ ...p, author: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Quantity</label>
          <input
            type="number"
            min={1}
            value={f.quantity}
            onChange={(e) => setF((p) => ({ ...p, quantity: Number(e.target.value) }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Unit Cost ($)</label>
          <input
            step="0.01"
            value={f.unit_cost}
            onChange={(e) => setF((p) => ({ ...p, unit_cost: Number(e.target.value) }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Requested By</label>
        <input
          value={f.requested_by}
          onChange={(e) => setF((p) => ({ ...p, requested_by: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {item ? "Update" : "Submit"}
        </Button>
      </div>
    </form>
  );
}
