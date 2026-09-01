/**
 * Teacher Behavior Page — View and manage student behavior incidents and points.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import { ExclamationTriangleIcon, StarIcon, PlusIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface BehaviorIncident {
  id: string;
  student_name: string;
  incident_type_display: string;
  description: string;
  severity: string;
  status_display: string;
  points_deducted: number;
  incident_date: string;
}
interface BehaviorPoint {
  id: string;
  student_name: string;
  points: number;
  reason: string;
  category: string;
  awarded_date: string;
}
interface Student {
  id: string;
  user_name: string;
}

export default function TeacherBehaviorPage() {
  useTitle("Student Behavior");
  const qc = useQueryClient();
  const [tab, setTab] = useState<"incidents" | "points">("incidents");
  const [showPointForm, setShowPointForm] = useState(false);

  const { data: incidents = [], isLoading: iLoading } = useQuery({
    queryKey: ["teacher-incidents"],
    queryFn: async () => {
      const r = await api.get<{ results: BehaviorIncident[] }>("/behavior/incidents/");
      return r.results ?? [];
    },
  });
  const { data: points = [], isLoading: pLoading } = useQuery({
    queryKey: ["teacher-points"],
    queryFn: async () => {
      const r = await api.get<{ results: BehaviorPoint[] }>("/behavior/points/");
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

  const delIncident = useMutation({
    mutationFn: (id: string) => api.delete(`/behavior/incidents/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teacher-incidents"] });
      toast.success("Deleted");
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Student Behavior</h1>
          <p className="text-sm text-slate-500 mt-1">Manage behavior incidents and award points</p>
        </div>
        <Button onClick={() => setShowPointForm(true)}>
          <PlusIcon className="h-4 w-4 mr-1.5" />
          Award Points
        </Button>
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        <button
          onClick={() => setTab("incidents")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "incidents" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <ExclamationTriangleIcon className="h-4 w-4 inline mr-1.5" />
          Incidents
        </button>
        <button
          onClick={() => setTab("points")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "points" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <StarIcon className="h-4 w-4 inline mr-1.5" />
          Points
        </button>
      </div>

      {tab === "incidents" &&
        (iLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !incidents.length ? (
          <EmptyState icon={ExclamationTriangleIcon} title="No incidents" />
        ) : (
          <div className="space-y-2">
            {incidents.map((inc) => (
              <div
                key={inc.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">
                      {inc.student_name}
                    </p>
                    <p className="text-sm text-slate-500 mt-0.5">
                      {inc.incident_type_display}: {inc.description}
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                      {dayjs(inc.incident_date).format("MMM D, YYYY")}
                    </p>
                  </div>
                  <div className="flex gap-2 items-center">
                    <Badge
                      color={
                        inc.severity === "high"
                          ? "red"
                          : inc.severity === "medium"
                            ? "amber"
                            : "blue"
                      }
                    >
                      {inc.severity}
                    </Badge>
                    {inc.points_deducted > 0 && (
                      <span className="text-xs text-red-500">-{inc.points_deducted}</span>
                    )}
                    <button
                      onClick={() => {
                        if (confirm("Delete?")) delIncident.mutate(inc.id);
                      }}
                      className="text-xs text-red-500 font-medium"
                    >
                      Del
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}

      {tab === "points" &&
        (pLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-12 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !points.length ? (
          <EmptyState icon={StarIcon} title="No points" />
        ) : (
          <div className="space-y-2">
            {points.map((p) => (
              <div
                key={p.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3 flex items-center justify-between"
              >
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-white">
                    {p.student_name}
                  </p>
                  <p className="text-xs text-slate-400">
                    {p.reason} · {dayjs(p.awarded_date).format("MMM D")}
                  </p>
                </div>
                <p
                  className={`text-lg font-bold ${
                    p.points > 0 ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {p.points > 0 ? "+" : ""}
                  {p.points}
                </p>
              </div>
            ))}
          </div>
        ))}

      <PointFormModal
        open={showPointForm}
        onClose={() => setShowPointForm(false)}
        students={students}
        onSaved={() => {
          setShowPointForm(false);
          qc.invalidateQueries({ queryKey: ["teacher-points"] });
        }}
      />
    </div>
  );
}

function PointFormModal({
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
  const [f, setF] = useState({ student: "", points: 1, reason: "", category: "academic" });
  const create = useMutation({
    mutationFn: (d: typeof f) => api.post("/behavior/points/", d),
    onSuccess: () => {
      toast.success("Points awarded");
      onSaved();
    },
  });
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.student || !f.reason) return toast.error("Student and reason required");
    create.mutate(f);
  };
  return (
    <Modal open={open} onClose={onClose} title="Award Behavior Points">
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
            <label className="block text-sm font-medium mb-1">Points *</label>
            <input
              type="number"
              value={f.points}
              onChange={(e) => setF((p) => ({ ...p, points: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <select
              value={f.category}
              onChange={(e) => setF((p) => ({ ...p, category: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            >
              <option value="academic">Academic</option>
              <option value="behavior">Behavior</option>
              <option value="participation">Participation</option>
              <option value="leadership">Leadership</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Reason *</label>
          <textarea
            value={f.reason}
            onChange={(e) => setF((p) => ({ ...p, reason: e.target.value }))}
            rows={2}
            className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            required
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={create.isPending}>
            Cancel
          </Button>
          <Button type="submit" loading={create.isPending}>
            Award Points
          </Button>
        </div>
      </form>
    </Modal>
  );
}
