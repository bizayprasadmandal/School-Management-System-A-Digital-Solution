/**
 * Teacher Health Page — log student health visits and view records.
 *
 * Backend: GET/POST /health/visits/ (NurseVisitViewSet — staff-writable,
 * teacher-friendly fields: student pk, visit_type, symptoms, diagnosis,
 * treatment, medication_given, status). The form uses a student picker
 * (class-roster dropdown) instead of a free-text name field.
 */
import React, { useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import {
  HeartIcon,
  PlusIcon,
  ClockIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface HealthVisit {
  id: string;
  student: string;
  student_name: string;
  visit_type: string;
  visit_date: string;
  symptoms: string;
  diagnosis: string;
  treatment: string;
  medication_given: string;
  status: string;
  treated_by_name: string | null;
}

interface StudentOption {
  id: string;
  full_name: string;
  current_class_name?: string | null;
}

const VISIT_STATUSES = ["pending", "in_progress", "completed", "cancelled"];

function HealthSkeleton() {
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

export default function HealthPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<HealthVisit | null>(null);

  const { data: visits = [] as HealthVisit[], isLoading } = useQuery({
    queryKey: ["teacher-health-visits"],
    queryFn: async () => {
      const r = await api.get<{ results: HealthVisit[] }>("/health/visits/");
      return (r.results ?? []) as HealthVisit[];
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
    if (!search.trim()) return visits;
    const q = search.toLowerCase();
    return visits.filter(
      (v) =>
        v.student_name?.toLowerCase().includes(q) ||
        v.symptoms?.toLowerCase().includes(q) ||
        v.diagnosis?.toLowerCase().includes(q),
    );
  }, [visits, search]);

  const paginatedVisits = useMemo(() => {
    const start = (page - 1) * 12;
    return filtered.slice(start, start + 12);
  }, [filtered, page]);

  const totalPages = Math.ceil(filtered.length / 12);

  const createVisit = useMutation({
    mutationFn: (data: Partial<HealthVisit>) => api.post("/health/visits/", data),
    onSuccess: () => {
      toast.success("Health visit logged");
      qc.invalidateQueries({ queryKey: ["teacher-health-visits"] });
      setShowForm(false);
    },
  });

  const updateVisit = useMutation({
    mutationFn: (data: Partial<HealthVisit>) =>
      api.patch(`/health/visits/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Visit updated");
      qc.invalidateQueries({ queryKey: ["teacher-health-visits"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const bulk = useBulkSelect(visits);

  const handleExport = () => {
    const cols = [
      { key: "student", label: "Student" },
      { key: "visit_type", label: "Type" },
      { key: "date", label: "Date" },
      { key: "symptoms", label: "Symptoms" },
      { key: "status", label: "Status" },
    ];
    const rows = filtered.map((row) => ({
      student: row.student_name ?? "",
      visit_type: row.visit_type ?? "",
      date: row.visit_date ?? "",
      symptoms: row.symptoms ?? "",
      status: row.status ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "health-visits-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Student Health</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Log health visits and view student records
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
              setEditing(null);
              setShowForm(true);
            }}
          >
            <PlusIcon className="mr-1.5 h-4 w-4" />
            Log Visit
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="rounded-xl border border-slate-100 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search by student, symptoms, diagnosis..."
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
      ) : filtered.length === 0 ? (
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
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {visit.symptoms || visit.diagnosis || "—"}
                </p>
                <div className="mt-1 flex items-center gap-1 text-xs text-slate-400">
                  <ClockIcon className="h-3.5 w-3.5" />
                  {visit.visit_date ? dayjs(visit.visit_date).format("MMM D, YYYY") : "—"}
                  {visit.treated_by_name ? ` · treated by ${visit.treated_by_name}` : ""}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    visit.status === "completed"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : visit.status === "cancelled"
                        ? "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                        : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                  }`}
                >
                  {visit.status || "pending"}
                </span>
                <Button
                  variant="secondary"
                  onClick={() => {
                    setEditing(visit);
                    setShowForm(true);
                  }}
                >
                  Edit
                </Button>
              </div>
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
          setEditing(null);
        }}
        title={editing ? "Edit Visit" : "Log Health Visit"}
      >
        <VisitForm
          visit={editing}
          students={students}
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
  students,
  saving,
  onSave,
  onCancel,
}: {
  visit: HealthVisit | null;
  students: StudentOption[];
  saving: boolean;
  onSave: (data: Partial<HealthVisit>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    student: visit?.student ?? "",
    visit_type: visit?.visit_type ?? "sick_bay",
    symptoms: visit?.symptoms ?? "",
    diagnosis: visit?.diagnosis ?? "",
    treatment: visit?.treatment ?? "",
    medication_given: visit?.medication_given ?? "",
    status: visit?.status ?? "pending",
    visit_date: visit?.visit_date ?? dayjs().format("YYYY-MM-DD"),
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.student) return toast.error("Student required");
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
          <label className="mb-1 block text-sm font-medium">Visit Type</label>
          <input
            value={f.visit_type}
            onChange={(e) => setF((p) => ({ ...p, visit_type: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Date</label>
          <input
            type="date"
            value={f.visit_date}
            onChange={(e) => setF((p) => ({ ...p, visit_date: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Symptoms</label>
        <textarea
          value={f.symptoms}
          onChange={(e) => setF((p) => ({ ...p, symptoms: e.target.value }))}
          rows={2}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Diagnosis</label>
        <textarea
          value={f.diagnosis}
          onChange={(e) => setF((p) => ({ ...p, diagnosis: e.target.value }))}
          rows={2}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Treatment</label>
        <textarea
          value={f.treatment}
          onChange={(e) => setF((p) => ({ ...p, treatment: e.target.value }))}
          rows={2}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Medication Given</label>
        <input
          value={f.medication_given}
          onChange={(e) => setF((p) => ({ ...p, medication_given: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Status</label>
        <select
          value={f.status}
          onChange={(e) => setF((p) => ({ ...p, status: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        >
          {VISIT_STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
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
