/**
 * Accountant Budget Page — manage department budgets with progress tracking
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import {
  ChartBarIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface BudgetItem {
  id: string;
  category: string;
  allocated: number;
  spent: number;
  remaining: number;
  fiscal_year: string;
  department: string;
}

function BudgetSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function BudgetPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<BudgetItem | null>(null);

  const { data: allBudgets = [], isLoading } = useQuery({
    queryKey: ["accountant-budgets"],
    queryFn: async () => {
      const r = await api.get<{ results: BudgetItem[] }>("/fees/budgets/");
      return r.results ?? [];
    },
  });

  const budgets = React.useMemo(() => {
    if (!search.trim()) return allBudgets;
    const q = search.toLowerCase();
    return allBudgets.filter(
      (b) =>
        (b as any).name?.toLowerCase().includes(q) ||
        (b as any).title?.toLowerCase().includes(q) ||
        b.department?.toLowerCase().includes(q) ||
        (b as any).category?.toLowerCase().includes(q) ||
        (b as any).description?.toLowerCase().includes(q),
    );
  }, [allBudgets, search]);

  const createBudget = useMutation({
    mutationFn: (data: Partial<BudgetItem>) => api.post("/fees/budgets/", data),
    onSuccess: () => {
      toast.success("Budget created");
      qc.invalidateQueries({ queryKey: ["accountant-budgets"] });
      setShowForm(false);
    },
  });

  const updateBudget = useMutation({
    mutationFn: (data: Partial<BudgetItem>) => api.patch(`/fees/budgets/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Budget updated");
      qc.invalidateQueries({ queryKey: ["accountant-budgets"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteBudget = useMutation({
    mutationFn: (id: string) => api.delete(`/fees/budgets/${id}/`),
    onSuccess: () => {
      toast.success("Budget deleted");
      qc.invalidateQueries({ queryKey: ["accountant-budgets"] });
    },
  });

  const totalAllocated = budgets.reduce((sum, b) => sum + (b.allocated ?? 0), 0);
  const totalSpent = budgets.reduce((sum, b) => sum + (b.spent ?? 0), 0);

  const paginatedAllBudgets = React.useMemo(() => {
    const start = (page - 1) * 12;
    return allBudgets.slice(start, start + 12);
  }, [allBudgets, page]);

  const totalPages = Math.ceil(allBudgets.length / 12);

  const handleExport = () => {
    const cols = [
      { key: "name", label: "Name" },
      { key: "department", label: "Department" },
      { key: "amount", label: "Amount" },
    ];
    const rows = allBudgets.map((row) => ({
      name: row.category ?? "",
      department: row.department ?? "",
      amount: row.allocated ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "budgets-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Budget Management</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Track department budgets and spending
          </p>
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
          Add Budget
        </Button>
      </div>

      {!isLoading && budgets.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <p className="text-sm text-slate-500 dark:text-slate-400">Total Allocated</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">
              ${totalAllocated.toLocaleString()}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <p className="text-sm text-slate-500 dark:text-slate-400">Total Spent</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">
              ${totalSpent.toLocaleString()}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <p className="text-sm text-slate-500 dark:text-slate-400">Remaining</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              ${(totalAllocated - totalSpent).toLocaleString()}
            </p>
          </div>
        </div>
      )}

      {isLoading ? (
        <BudgetSkeleton />
      ) : budgets.length === 0 ? (
        <EmptyState
          icon={ChartBarIcon}
          title="No budget data"
          description="Set up budgets for different departments and categories."
        />
      ) : (
        <div className="space-y-3">
          {budgets.map((b) => {
            const pct = b.allocated > 0 ? (b.spent / b.allocated) * 100 : 0;
            return (
              <div
                key={b.id}
                className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white">{b.category}</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {b.department || "—"}
                    </p>
                    <p className="text-xs text-slate-400">{b.fiscal_year || "—"}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-right">
                      <p className="text-sm text-slate-900 dark:text-white">
                        ${(b.spent ?? 0).toLocaleString()} / ${(b.allocated ?? 0).toLocaleString()}
                      </p>
                      <p className="text-xs text-slate-400">
                        ${(b.remaining ?? 0).toLocaleString()} remaining
                      </p>
                    </div>
                    <div className="flex gap-1">
                      <button
                        onClick={() => {
                          setEditing(b);
                          setShowForm(true);
                        }}
                        className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => {
                          if (confirm("Delete this budget?")) deleteBudget.mutate(b.id);
                        }}
                        className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                  <div
                    className={`h-full rounded-full ${
                      pct > 90 ? "bg-red-500" : pct > 70 ? "bg-amber-500" : "bg-green-500"
                    }`}
                    style={{ width: `${Math.min(pct, 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination page={page} total={budgets.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Budget" : "Add Budget"}
      >
        <BudgetForm
          budget={editing}
          saving={createBudget.isPending || updateBudget.isPending}
          onSave={(data) => {
            if (editing) updateBudget.mutate(data);
            else createBudget.mutate(data);
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

function BudgetForm({
  budget,
  saving,
  onSave,
  onCancel,
}: {
  budget: BudgetItem | null;
  saving: boolean;
  onSave: (data: Partial<BudgetItem>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    category: budget?.category ?? "",
    department: budget?.department ?? "",
    allocated: budget?.allocated ?? 0,
    fiscal_year: budget?.fiscal_year ?? new Date().getFullYear().toString(),
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.category.trim()) return toast.error("Category required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div>
        <label className="mb-1 block text-sm font-medium">Category *</label>
        <input
          value={f.category}
          onChange={(e) => setF((p) => ({ ...p, category: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          required
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Department</label>
          <input
            value={f.department}
            onChange={(e) => setF((p) => ({ ...p, department: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Fiscal Year</label>
          <input
            value={f.fiscal_year}
            onChange={(e) => setF((p) => ({ ...p, fiscal_year: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Allocated Amount ($)</label>
        <input
          type="number"
          min={0}
          step="0.01"
          value={f.allocated}
          onChange={(e) => setF((p) => ({ ...p, allocated: Number(e.target.value) }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {budget ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
