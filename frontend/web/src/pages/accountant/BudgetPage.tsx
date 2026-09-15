/**
 * Accountant Budget Page — manage department budgets with progress tracking.
 *
 * Backed by the real BudgetPlan API: /fees/budget-plan/ (plan) and
 * /fees/budget-line-item/ (line items). Academic years come from
 * /students/academic-years/ for the form's required FK select.
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
  ChartBarIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  Bars3Icon,
} from "@heroicons/react/24/outline";

interface BudgetPlan {
  id: string;
  academic_year: string;
  title: string;
  total_budget: string | number;
  allocated: string | number;
  spent: string | number;
  status: string;
  notes: string;
  created_at: string;
}

interface AcademicYearOption {
  id: string;
  name: string;
  is_current: boolean;
}

const STATUS_OPTIONS = [
  { value: "draft", label: "Draft" },
  { value: "approved", label: "Approved" },
  { value: "active", label: "Active" },
  { value: "closed", label: "Closed" },
];

function BudgetStatSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800"
        >
          <div
            className="mb-2 h-4 w-24 animate-shimmer rounded bg-slate-200 dark:bg-slate-700"
            style={{ backgroundSize: "200% 100%" }}
          />
          <div
            className="h-8 w-16 animate-shimmer rounded bg-slate-200 dark:bg-slate-700"
            style={{ backgroundSize: "200% 100%" }}
          />
        </div>
      ))}
    </div>
  );
}

function BudgetSkeleton() {
  return (
    <>
      <BudgetStatSkeleton />
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
    </>
  );
}

const num = (v: string | number | undefined | null) => Number(v ?? 0);
const fmtRs = (v: string | number | undefined | null) =>
  `Rs. ${num(v).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;

export default function BudgetPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<BudgetPlan | null>(null);
  const shortcut = useShortcutHelp();

  const { data: plansPage, isLoading } = useQuery({
    queryKey: ["accountant-budgets"],
    queryFn: async () => {
      const r = await api.get<{ count: number; results: BudgetPlan[] }>("/fees/budget-plan/", {
        page_size: 200,
      });
      return r.results ?? [];
    },
  });
  const allBudgets = React.useMemo(() => plansPage ?? [], [plansPage]);

  const { data: years = [] } = useQuery({
    queryKey: ["academic-year-options"],
    queryFn: async () => {
      const r = await api.get<{ results: AcademicYearOption[] }>("/students/academic-years/", {
        page_size: 200,
      });
      return r.results ?? [];
    },
  });
  const yearName = React.useMemo(() => {
    const m = new Map<string, string>();
    years.forEach((y) => m.set(y.id, y.name));
    return (id: string) => m.get(id) ?? "—";
  }, [years]);

  const [infinitePage, setInfinitePage] = useState(1);
  const PAGE_SIZE = 12;
  const infiniteItems = allBudgets.slice(0, infinitePage * PAGE_SIZE);
  const infiniteHasMore = infiniteItems.length < allBudgets.length;

  const budgets = React.useMemo(() => {
    if (!search.trim()) return allBudgets;
    const q = search.toLowerCase();
    return allBudgets.filter(
      (b) =>
        b.title?.toLowerCase().includes(q) ||
        b.status?.toLowerCase().includes(q) ||
        yearName(b.academic_year)?.toLowerCase().includes(q) ||
        b.notes?.toLowerCase().includes(q),
    );
  }, [allBudgets, search, yearName]);

  const createBudget = useMutation({
    mutationFn: (data: Partial<BudgetPlan>) => api.post("/fees/budget-plan/", data),
    onSuccess: () => {
      toast.success("Budget created");
      qc.invalidateQueries({ queryKey: ["accountant-budgets"] });
      setShowForm(false);
    },
  });

  const updateBudget = useMutation({
    mutationFn: (data: Partial<BudgetPlan>) => api.patch(`/fees/budget-plan/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Budget updated");
      qc.invalidateQueries({ queryKey: ["accountant-budgets"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteBudget = useMutation({
    mutationFn: (id: string) => api.delete(`/fees/budget-plan/${id}/`),
    onSuccess: () => {
      toast.success("Budget deleted");
      qc.invalidateQueries({ queryKey: ["accountant-budgets"] });
    },
  });

  const totalBudget = budgets.reduce((s, b) => s + num(b.total_budget), 0);
  const totalAllocated = budgets.reduce((s, b) => s + num(b.allocated), 0);
  const totalSpent = budgets.reduce((s, b) => s + num(b.spent), 0);

  const paginatedAllBudgets = React.useMemo(() => {
    const start = (page - 1) * 12;
    return budgets.slice(start, start + 12);
  }, [budgets, page]);

  const totalPages = Math.ceil(budgets.length / 12);

  const bulk = useBulkSelect(budgets);
  const [reorderMode, setReorderMode] = React.useState(false);
  const [orderedItems, setOrderedItems] = React.useState(budgets);

  React.useEffect(() => {
    setOrderedItems(budgets);
  }, [budgets]);

  const handleExport = () => {
    const cols = [
      { key: "title", label: "Title" },
      { key: "academic_year", label: "Academic Year" },
      { key: "status", label: "Status" },
      { key: "total_budget", label: "Total Budget" },
      { key: "allocated", label: "Allocated" },
      { key: "spent", label: "Spent" },
    ];
    const rows = budgets.map((row) => ({
      title: row.title ?? "",
      academic_year: yearName(row.academic_year),
      status: row.status ?? "",
      total_budget: row.total_budget ?? "",
      allocated: row.allocated ?? "",
      spent: row.spent ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "budgets-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(
        bulk.selectedArray.map((id) => api.delete("/fees/budget-plan/" + id + "/")),
      );
      toast.success(`${bulk.selectedCount} items deleted`);
      bulk.clear();
      qc.invalidateQueries({ queryKey: ["accountant-budgets"] });
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Budget Management</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Track department budgets and spending
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
          Add Budget
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

      {!isLoading && budgets.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <p className="text-sm text-slate-500 dark:text-slate-400">Total Budget</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">
              {fmtRs(totalBudget)}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <p className="text-sm text-slate-500 dark:text-slate-400">Total Spent</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">{fmtRs(totalSpent)}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <p className="text-sm text-slate-500 dark:text-slate-400">Remaining</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              {fmtRs(totalBudget - totalSpent)}
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
          {viewMode === "infinite" ? (
            <InfiniteScroll
              items={infiniteItems}
              hasMore={infiniteHasMore}
              isLoading={false}
              isFetchingNext={false}
              onLoadMore={() => setInfinitePage((p) => p + 1)}
              renderItem={(b) => (
                <BudgetCard
                  key={b.id}
                  b={b}
                  yearName={yearName(b.academic_year)}
                  onEdit={() => {
                    setEditing(b);
                    setShowForm(true);
                  }}
                  onDelete={() => {
                    if (confirm("Delete this budget?")) deleteBudget.mutate(b.id);
                  }}
                />
              )}
            />
          ) : (
            paginatedAllBudgets.map((b) => (
              <BudgetCard
                key={b.id}
                b={b}
                yearName={yearName(b.academic_year)}
                onEdit={() => {
                  setEditing(b);
                  setShowForm(true);
                }}
                onDelete={() => {
                  if (confirm("Delete this budget?")) deleteBudget.mutate(b.id);
                }}
              />
            ))
          )}
        </div>
      )}

      {/* Pagination */}
      {viewMode === "pagination" && totalPages > 1 && (
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
          years={years}
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

function BudgetCard({
  b,
  yearName,
  onEdit,
  onDelete,
}: {
  b: BudgetPlan;
  yearName: string;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const allocated = num(b.allocated) || num(b.total_budget);
  const pct = allocated > 0 ? (num(b.spent) / allocated) * 100 : 0;
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-slate-900 dark:text-white">{b.title}</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">{yearName}</p>
          <p className="text-xs text-slate-400">{b.status}</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="text-right">
            <p className="text-sm text-slate-900 dark:text-white">
              {fmtRs(b.spent)} / {fmtRs(allocated)}
            </p>
            <p className="text-xs text-slate-400">{fmtRs(allocated - num(b.spent))} remaining</p>
          </div>
          <div className="flex gap-1">
            <button
              onClick={onEdit}
              className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
              aria-label="Edit"
            >
              <PencilIcon className="h-4 w-4" />
            </button>
            <button
              onClick={onDelete}
              className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
              aria-label="Delete"
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
}

function BudgetForm({
  budget,
  years,
  saving,
  onSave,
  onCancel,
}: {
  budget: BudgetPlan | null;
  years: AcademicYearOption[];
  saving: boolean;
  onSave: (data: Partial<BudgetPlan>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    title: budget?.title ?? "",
    academic_year: budget?.academic_year ?? "",
    total_budget: num(budget?.total_budget),
    allocated: num(budget?.allocated),
    status: budget?.status ?? "draft",
    notes: budget?.notes ?? "",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.title.trim()) return toast.error("Title required");
        if (!f.academic_year) return toast.error("Academic year required");
        onSave({
          ...f,
          academic_year: f.academic_year,
          total_budget: String(f.total_budget),
          allocated: String(f.allocated),
        });
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
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Academic Year *</label>
          <select
            value={f.academic_year}
            onChange={(e) => setF((p) => ({ ...p, academic_year: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-700 dark:text-slate-200"
            required
          >
            <option value="">Select year…</option>
            {years.map((y) => (
              <option key={y.id} value={y.id}>
                {y.name}
                {y.is_current ? " (current)" : ""}
              </option>
            ))}
          </select>
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
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Total Budget (Rs.)</label>
          <input
            type="number"
            min={0}
            step="0.01"
            value={f.total_budget}
            onChange={(e) => setF((p) => ({ ...p, total_budget: Number(e.target.value) }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Allocated (Rs.)</label>
          <input
            type="number"
            min={0}
            step="0.01"
            value={f.allocated}
            onChange={(e) => setF((p) => ({ ...p, allocated: Number(e.target.value) }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
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
          {budget ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
