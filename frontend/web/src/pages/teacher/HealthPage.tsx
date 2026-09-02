/**
 * Teacher Health Page — log student health visits and view records
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import { useKeyboardShortcuts } from "../../hooks/useKeyboardShortcuts";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { BulkActionBar } from "../../components/common/BulkActionBar";
import {
  HeartIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ClockIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface HealthVisit {
  id: string;
  student_name: string;
  reason: string;
  notes: string;
  date: string;
  status: string;
}

function HealthSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="h-20 relative overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
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

export default function HealthPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<HealthVisit | null>(null);

  const { data: visits = [], isLoading } = useQuery({
    queryKey: ["teacher-health-visits"],
    queryFn: async () => {
      const r = await api.get<{ results: HealthVisit[] }>("/health-clinic/visits/");
      return r.results ?? [];
    },
  });

  const createVisit = useMutation({
    mutationFn: (data: Partial<HealthVisit>) => api.post("/health-clinic/visits/", data),
    onSuccess: () => {
      toast.success("Health visit logged");
      qc.invalidateQueries({ queryKey: ["teacher-health-visits"] });
      setShowForm(false);
    },
  });

  const updateVisit = useMutation({
    mutationFn: (data: Partial<HealthVisit>) =>
      api.patch(`/health-clinic/visits/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Visit updated");
      qc.invalidateQueries({ queryKey: ["teacher-health-visits"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteVisit = useMutation({
    mutationFn: (id: string) => api.delete(`/health-clinic/visits/${id}/`),
    onSuccess: () => {
      toast.success("Visit deleted");
      qc.invalidateQueries({ queryKey: ["teacher-health-visits"] });
    },
  });

  const paginatedVisits = React.useMemo(() => {
    const start = (page - 1) * 12;
    return visits.slice(start, start + 12);
  }, [visits, page]);

  const totalPages = Math.ceil(visits.length / 12);

  const bulk = useBulkSelect(visits);

  const handleExport = () => {
    const cols = [
      { key: "student_name", label: "Student" },
      { key: "reason", label: "Reason" },
      { key: "date", label: "Date" },
    ];
    const rows = visits.map((row) => ({
      student_name: row.student_name ?? "",
      reason: row.reason ?? "",
      date: row.date ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "health-visits-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(
        bulk.selectedArray.map((id) => api.delete("/health-clinic/health-records//" + id + "/")),
      );
      toast.success(`${bulk.selectedCount} items deleted`);
      bulk.clear();
      qc.invalidateQueries({ queryKey: ["teacher-health"] });
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Student Health</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Log health visits and view student records
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
          Log Visit
        </Button>
      </div>

      {/* Search */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search by student name, record type..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-400"
          />
        </div>
      </div>

      {isLoading ? (
        <HealthSkeleton />
      ) : visits.length === 0 ? (
        <EmptyState
          icon={HeartIcon}
          title="No health visits"
          description="Log health visits for students here."
        />
      ) : (
        <div className="space-y-3">
          {paginatedVisits.map((visit) => (
            <div
              key={visit.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <p className="font-medium text-slate-900 dark:text-white">{visit.student_name}</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">{visit.reason || "—"}</p>
                <div className="mt-1 flex items-center gap-1 text-xs text-slate-400">
                  <ClockIcon className="h-3.5 w-3.5" />
                  {visit.date || "—"}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    visit.status === "resolved"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                  }`}
                >
                  {visit.status || "pending"}
                </span>
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(visit);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this visit?")) deleteVisit.mutate(visit.id);
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
        <Pagination page={page} total={visits.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Visit" : "Log Health Visit"}
      >
        <VisitForm
          visit={editing}
          saving={createVisit.isPending || updateVisit.isPending}
          onSave={(data) => {
            if (editing) updateVisit.mutate(data);
            else createVisit.mutate(data);
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

function VisitForm({
  visit,
  saving,
  onSave,
  onCancel,
}: {
  visit: HealthVisit | null;
  saving: boolean;
  onSave: (data: Partial<HealthVisit>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    student_name: visit?.student_name ?? "",
    reason: visit?.reason ?? "",
    notes: visit?.notes ?? "",
    date: visit?.date ?? "",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.student_name.trim()) return toast.error("Student required");
        if (!f.reason.trim()) return toast.error("Reason required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div>
        <label className="mb-1 block text-sm font-medium">Student *</label>
        <input
          value={f.student_name}
          onChange={(e) => setF((p) => ({ ...p, student_name: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          required
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Reason *</label>
        <input
          value={f.reason}
          onChange={(e) => setF((p) => ({ ...p, reason: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          required
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Date</label>
        <input
          type="date"
          value={f.date}
          onChange={(e) => setF((p) => ({ ...p, date: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
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
          {visit ? "Update" : "Save"}
        </Button>
      </div>
    </form>
  );
}
