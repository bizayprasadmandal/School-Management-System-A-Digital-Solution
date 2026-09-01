/**
 * Teacher Health Page — View student health records and log nurse visits.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import { HeartIcon, ClockIcon, PlusIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState } from "../../components/common";
import { useTitle } from "../../hooks";

interface HealthRecord {
  id: string;
  student_name: string;
  blood_type: string;
  allergies: string;
  chronic_conditions: string;
}
interface NurseVisit {
  id: string;
  student_name: string;
  visit_type_display: string;
  visit_date: string;
  symptoms: string;
  diagnosis: string;
}
interface Student {
  id: string;
  user_name: string;
}

type Tab = "records" | "visits";

export default function TeacherHealthPage() {
  useTitle("Student Health");
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>("records");
  const [showVisitForm, setShowVisitForm] = useState(false);

  const { data: records = [], isLoading: rLoading } = useQuery({
    queryKey: ["teacher-health-records"],
    queryFn: async () => {
      const r = await api.get<{ results: HealthRecord[] }>("/health/records/");
      return r.results ?? [];
    },
  });
  const { data: visits = [], isLoading: vLoading } = useQuery({
    queryKey: ["teacher-health-visits"],
    queryFn: async () => {
      const r = await api.get<{ results: NurseVisit[] }>("/health/visits/");
      return r.results ?? [];
    },
  });
  const { data: students = [] } = useQuery({
    queryKey: ["students-short"],
    queryFn: async () => {
      const r = await api.get<{ results: Student[] }>("/students/");
      return r.results ?? [];
    },
  });

  const delVisit = useMutation({
    mutationFn: (id: string) => api.delete(`/health/visits/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teacher-health-visits"] });
      toast.success("Deleted");
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Student Health</h1>
          <p className="text-sm text-slate-500 mt-1">View student health records and log visits</p>
        </div>
        {tab === "visits" && (
          <Button onClick={() => setShowVisitForm(true)}>
            <PlusIcon className="h-4 w-4 mr-1.5" />
            Log Visit
          </Button>
        )}
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        <button
          onClick={() => setTab("records")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "records" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <HeartIcon className="h-4 w-4 inline mr-1.5" />
          Records
        </button>
        <button
          onClick={() => setTab("visits")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "visits" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <ClockIcon className="h-4 w-4 inline mr-1.5" />
          Visits
        </button>
      </div>

      {tab === "records" &&
        (rLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !records.length ? (
          <EmptyState icon={HeartIcon} title="No records" description="No student health records" />
        ) : (
          <div className="space-y-2">
            {records.map((r) => (
              <div
                key={r.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <p className="font-semibold text-slate-900 dark:text-white">{r.student_name}</p>
                <p className="text-xs text-slate-400">
                  Blood: {r.blood_type}
                  {r.allergies ? ` · Allergies: ${r.allergies}` : ""}
                </p>
                {r.chronic_conditions && (
                  <p className="text-xs text-amber-600 mt-1">⚠️ {r.chronic_conditions}</p>
                )}
              </div>
            ))}
          </div>
        ))}

      {tab === "visits" &&
        (vLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !visits.length ? (
          <EmptyState icon={ClockIcon} title="No visits" description="No nurse visits logged" />
        ) : (
          <div className="space-y-2">
            {visits.map((v) => (
              <div
                key={v.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{v.student_name}</p>
                    <p className="text-xs text-slate-400">
                      {v.visit_type_display} · {dayjs(v.visit_date).format("MMM D, YYYY h:mm A")}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      if (confirm("Delete?")) delVisit.mutate(v.id);
                    }}
                    className="text-xs text-red-500 font-medium"
                  >
                    Delete
                  </button>
                </div>
                {v.diagnosis && (
                  <p className="text-sm text-slate-500 mt-1">Diagnosis: {v.diagnosis}</p>
                )}
              </div>
            ))}
          </div>
        ))}

      <VisitFormModal
        open={showVisitForm}
        onClose={() => setShowVisitForm(false)}
        students={students}
        onSaved={() => {
          setShowVisitForm(false);
          qc.invalidateQueries({ queryKey: ["teacher-health-visits"] });
        }}
      />
    </div>
  );
}

function VisitFormModal({
  open,
  onClose,
  students,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  students: Student[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    student: "",
    visit_type: "sick",
    symptoms: "",
    diagnosis: "",
    treatment: "",
  });
  const create = useMutation({
    mutationFn: (d: typeof f) => api.post("/health/visits/", d),
    onSuccess: () => {
      toast.success("Visit logged");
      onSaved();
    },
  });
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.student) return toast.error("Select student");
    create.mutate(f);
  };
  return (
    <Modal open={open} onClose={onClose} title="Log Nurse Visit">
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Student *</label>
          <select
            value={f.student}
            onChange={(e) => setF((p) => ({ ...p, student: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            required
          >
            <option value="">Select...</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>
                {s.user_name}
              </option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Type</label>
            <select
              value={f.visit_type}
              onChange={(e) => setF((p) => ({ ...p, visit_type: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            >
              <option value="sick">Sick</option>
              <option value="injury">Injury</option>
              <option value="medication">Medication</option>
              <option value="checkup">Checkup</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Diagnosis</label>
            <input
              value={f.diagnosis}
              onChange={(e) => setF((p) => ({ ...p, diagnosis: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Symptoms</label>
          <textarea
            value={f.symptoms}
            onChange={(e) => setF((p) => ({ ...p, symptoms: e.target.value }))}
            rows={2}
            className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={create.isPending}>
            Cancel
          </Button>
          <Button type="submit" loading={create.isPending}>
            Log Visit
          </Button>
        </div>
      </form>
    </Modal>
  );
}
