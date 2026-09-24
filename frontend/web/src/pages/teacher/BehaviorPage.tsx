/**
 * Teacher Behavior Page — award and manage student behavior points.
 *
 * Backend: GET/POST /behavior/points/ (BehaviorPointViewSet — teachers may
 * award via create; fields: student pk, category, points, point_type,
 * reason). The form uses a student picker (roster dropdown) instead of a
 * free-text name field.
 */
import React, { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import {
  CheckCircleIcon,
  XCircleIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
  PlusIcon,
} from "@heroicons/react/24/outline";

interface BehaviorRecord {
  id: string;
  student: string;
  student_name: string;
  category: string | null;
  category_name: string | null;
  points: number;
  point_type: string;
  point_type_display: string;
  reason: string;
  awarded_by_name: string | null;
  created_at: string;
}

interface StudentOption {
  id: string;
  full_name: string;
  current_class_name?: string | null;
}

function BehaviorStatSkeleton() {
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

function ListSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="relative h-20 overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
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

export default function BehaviorPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);

  const { data: records = [] as BehaviorRecord[], isLoading } = useQuery({
    queryKey: ["teacher-behavior-points"],
    queryFn: async () => {
      const r = await api.get<{ results: BehaviorRecord[] }>("/behavior/points/");
      return (r.results ?? []) as BehaviorRecord[];
    },
    refetchInterval: 60000,
  });

  const { data: students = [] as StudentOption[] } = useQuery({
    queryKey: ["teacher-roster-options"],
    queryFn: async () => {
      const r = await api.get<{ results: StudentOption[] }>(
        "/students/?page_size=200",
      );
      return (r.results ?? []) as StudentOption[];
    },
    staleTime: 10 * 60 * 1000,
  });

  const filtered = useMemo(() => {
    let items: BehaviorRecord[] = records;
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(
        (r) =>
          r.student_name?.toLowerCase().includes(q) ||
          r.reason?.toLowerCase().includes(q) ||
          r.category_name?.toLowerCase().includes(q),
      );
    }
    if (typeFilter === "positive") items = items.filter((r) => r.points > 0);
    if (typeFilter === "negative") items = items.filter((r) => r.points < 0);
    return items;
  }, [records, search, typeFilter]);

  const totalPoints = records.reduce((sum, r) => sum + (r.points ?? 0), 0);

  const paginatedRecords = useMemo(() => {
    const start = (page - 1) * 12;
    return filtered.slice(start, start + 12);
  }, [filtered, page]);

  const totalPages = Math.ceil(filtered.length / 12);

  const createRecord = useMutation({
    mutationFn: (data: Partial<BehaviorRecord>) => api.post("/behavior/points/", data),
    onSuccess: () => {
      toast.success("Points awarded");
      qc.invalidateQueries({ queryKey: ["teacher-behavior-points"] });
      setShowForm(false);
    },
  });

  const handleExport = () => {
    const cols = [
      { key: "student", label: "Student" },
      { key: "points", label: "Points" },
      { key: "reason", label: "Reason" },
      { key: "date", label: "Date" },
    ];
    const rows = filtered.map((row) => ({
      student: row.student_name ?? "",
      points: row.points ?? "",
      reason: row.reason ?? "",
      date: row.created_at ? dayjs(row.created_at).format("YYYY-MM-DD") : "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "behavior-points-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Behavior Points</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Award and manage student behavior points
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
            onClick={handleExport}
          >
            Export CSV
          </Button>
          <Button
            onClick={() => {
              setShowForm(true);
            }}
          >
            <PlusIcon className="mr-1.5 h-4 w-4" />
            Award Points
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-sm text-slate-500 dark:text-slate-400">Points Awarded (page)</p>
          <p
            className={`text-2xl font-bold ${
              totalPoints >= 0
                ? "text-green-600 dark:text-green-400"
                : "text-red-600 dark:text-red-400"
            }`}
          >
            {totalPoints}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-sm text-slate-500 dark:text-slate-400">Positive Awards</p>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">
            {records.filter((r) => r.points > 0).length}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-sm text-slate-500 dark:text-slate-400">Negative Marks</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">
            {records.filter((r) => r.points < 0).length}
          </p>
        </div>
      </div>

      {/* Search + Filters */}
      <div className="space-y-3 rounded-xl border border-slate-100 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              placeholder="Search by student, reason, category..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-400"
            />
          </div>
          <select
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-700 dark:text-white"
          >
            <option value="all">All Types</option>
            <option value="positive">Positive</option>
            <option value="negative">Negative</option>
          </select>
          {(search || typeFilter !== "all") && (
            <button
              onClick={() => {
                setSearch("");
                setTypeFilter("all");
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
        <>
          <BehaviorStatSkeleton />
          <ListSkeleton />
        </>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={CheckCircleIcon}
          title="No behavior records"
          description="Award behavior points to students here."
        />
      ) : (
        <div className="space-y-3">
          {paginatedRecords.map((record) => (
            <div
              key={record.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-center gap-3">
                {record.points > 0 ? (
                  <CheckCircleIcon className="h-5 w-5 text-green-500" />
                ) : (
                  <XCircleIcon className="h-5 w-5 text-red-500" />
                )}
                <div>
                  <p className="font-medium text-slate-900 dark:text-white">
                    {record.student_name}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {record.reason || record.point_type_display || "—"}
                    {record.category_name ? ` · ${record.category_name}` : ""}
                    {record.awarded_by_name ? ` · by ${record.awarded_by_name}` : ""}
                  </p>
                </div>
              </div>
              <span
                className={`text-sm font-semibold ${
                  record.points > 0
                    ? "text-green-600 dark:text-green-400"
                    : "text-red-600 dark:text-red-400"
                }`}
              >
                {record.points > 0 ? "+" : ""}
                {record.points}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination page={page} total={filtered.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
        }}
        title="Award Points"
      >
        <BehaviorForm
          students={students}
          saving={createRecord.isPending}
          onSave={(data) => createRecord.mutate(data)}
          onCancel={() => setShowForm(false)}
        />
      </Modal>
    </div>
  );
}

function BehaviorForm({
  students,
  saving,
  onSave,
  onCancel,
}: {
  students: StudentOption[];
  saving: boolean;
  onSave: (data: Partial<BehaviorRecord>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    student: "",
    points: 5,
    point_type: "earned",
    reason: "",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.student) return toast.error("Student required");
        if (!f.reason.trim()) return toast.error("Reason required");
        if (!f.points) return toast.error("Points cannot be zero");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div>
        <label className="mb-1 block text-sm font-medium">Student *</label>
        <select
          value={f.student}
          onChange={(e) => setF((p) => ({ ...p, student: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          required
        >
          <option value="">Select student…</option>
          {students.map((s) => (
            <option key={s.id} value={s.id}>
              {s.full_name}
              {s.current_class_name ? ` — ${s.current_class_name}` : ""}
            </option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Type</label>
          <select
            value={f.point_type}
            onChange={(e) => setF((p) => ({ ...p, point_type: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          >
            <option value="earned">Earned (positive)</option>
            <option value="deducted">Deducted (negative)</option>
            <option value="adjusted">Adjusted</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Points *</label>
          <input
            type="number"
            value={f.points}
            onChange={(e) => setF((p) => ({ ...p, points: Number(e.target.value) }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Reason *</label>
        <input
          value={f.reason}
          onChange={(e) => setF((p) => ({ ...p, reason: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          placeholder="e.g. Helped a classmate, excellent homework"
          required
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          Award
        </Button>
      </div>
    </form>
  );
}
