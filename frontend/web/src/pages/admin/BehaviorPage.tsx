/** Behavior & Discipline — Admin incident tracking and referral management */

import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  PlusIcon, FunnelIcon, MagnifyingGlassIcon,
  ExclamationTriangleIcon, CheckCircleIcon, XCircleIcon,
  ClockIcon, PencilIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState } from "../../components/common";

interface Incident {
  id: string;
  student: string;
  student_name: string;
  incident_type: string;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  location: string;
  occurred_at: string;
  status: "open" | "investigating" | "resolved" | "closed";
  resolution: string;
  reported_by_name: string;
  created_at: string;
}

interface Referral {
  id: string;
  incident: string;
  referred_to_name: string;
  referred_by_name: string;
  reason: string;
  action_taken: string;
  status: "pending" | "actioned" | "closed";
  created_at: string;
}

const SEVERITY_COLORS: Record<string, string> = {
  low: "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
  medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

const STATUS_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  open: ClockIcon,
  investigating: ExclamationTriangleIcon,
  resolved: CheckCircleIcon,
  closed: XCircleIcon,
};

const STATUS_COLORS: Record<string, string> = {
  open: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300",
  investigating: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  resolved: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  closed: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
};

function IncidentFormModal({
  open, onClose, incident, onSaved,
}: {
  open: boolean; onClose: () => void; incident?: Incident | null; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    student: incident?.student ?? "",
    incident_type: incident?.incident_type ?? "",
    severity: incident?.severity as "low" | "medium" | "high" | "critical" ?? "medium",
    description: incident?.description ?? "",
    location: incident?.location ?? "",
    occurred_at: incident?.occurred_at ?? dayjs().format("YYYY-MM-DDTHH:mm"),
    status: incident?.status as "open" | "investigating" | "resolved" | "closed" ?? "open",
    resolution: incident?.resolution ?? "",
  });

  const [studentSearch, setStudentSearch] = useState(incident?.student_name ?? "");
  const { data: students = [] } = useQuery({
    queryKey: ["student-search", studentSearch],
    queryFn: async () => {
      if (studentSearch.length < 2) return [];
      const res = await api.get<{ results: any[] }>("/students/students/", { search: studentSearch, page_size: 10 });
      return res.results ?? [];
    },
    enabled: studentSearch.length >= 2,
  });

  const isEdit = !!incident;
  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/behavior/incidents/", data),
    onSuccess: () => { toast.success("Incident reported"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/behavior/incidents/${incident!.id}/`, data),
    onSuccess: () => { toast.success("Incident updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.student) return toast.error("Select a student");
    if (!form.incident_type.trim()) return toast.error("Incident type is required");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Incident" : "Report Incident"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Student *</label>
          <input value={studentSearch} onChange={e => { setStudentSearch(e.target.value); setForm(p => ({ ...p, student: "" })); }}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
            placeholder="Search student name..." disabled={isEdit} />
          {studentSearch.length >= 2 && !form.student && students.length > 0 && (
            <div className="mt-1 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 shadow-lg max-h-40 overflow-y-auto">
              {students.map((s: any) => (
                <button key={s.id} type="button" onClick={() => { setForm(p => ({ ...p, student: s.id })); setStudentSearch(s.full_name ?? s.user?.full_name); }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 dark:text-slate-200">{s.full_name ?? s.user?.full_name}</button>
              ))}
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Incident Type *</label>
            <input value={form.incident_type} onChange={e => setForm(p => ({ ...p, incident_type: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" placeholder="e.g. Bullying, Tardiness" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Severity</label>
            <select value={form.severity} onChange={e => setForm(p => ({ ...p, severity: e.target.value as "low" | "medium" | "high" | "critical" }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Location</label>
            <input value={form.location} onChange={e => setForm(p => ({ ...p, location: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" placeholder="Classroom, playground..." />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Date & Time</label>
            <input type="datetime-local" value={form.occurred_at} onChange={e => setForm(p => ({ ...p, occurred_at: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
          <textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} rows={3}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        {isEdit && (
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Status</label>
            <select value={form.status} onChange={e => setForm(p => ({ ...p, status: e.target.value as "open" | "investigating" | "resolved" | "closed" }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="open">Open</option>
              <option value="investigating">Investigating</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
        )}
        {isEdit && (
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Resolution</label>
            <textarea value={form.resolution} onChange={e => setForm(p => ({ ...p, resolution: e.target.value }))} rows={2}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        )}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Report"} Incident</Button>
        </div>
      </form>
    </Modal>
  );
}

export default function BehaviorPage() {
  const [activeTab, setActiveTab] = useState<"incidents" | "referrals">("incidents");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<Incident | null>(null);
  const [showForm, setShowForm] = useState(false);
  const qc = useQueryClient();

  const { data: incidents = [], isLoading } = useQuery({
    queryKey: ["behavior-incidents", statusFilter],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (statusFilter !== "all") params.status = statusFilter;
      const res = await api.get<{ results: Incident[] }>("/behavior/incidents/", params);
      return res.results ?? [];
    },
  });

  const { data: referrals = [] } = useQuery({
    queryKey: ["behavior-referrals"],
    queryFn: async () => {
      const res = await api.get<{ results: Referral[] }>("/behavior/referrals/");
      return res.results ?? [];
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => api.delete(`/behavior/incidents/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["behavior-incidents"] }); toast.success("Incident deleted"); },
  });

  const filtered = useMemo(() => {
    if (!search.trim()) return incidents;
    const q = search.toLowerCase();
    return incidents.filter(i =>
      i.student_name?.toLowerCase().includes(q) ||
      i.incident_type?.toLowerCase().includes(q) ||
      i.description?.toLowerCase().includes(q)
    );
  }, [incidents, search]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Behavior & Discipline</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Track incidents, referrals, and disciplinary actions</p>
        </div>
        <Button onClick={() => { setEditing(null); setShowForm(true); }}>
          <PlusIcon className="h-4 w-4 mr-1.5" /> Report Incident
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        <button onClick={() => setActiveTab("incidents")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === "incidents" ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm" : "text-slate-600 dark:text-slate-400 hover:text-slate-900"}`}>
          Incidents ({incidents.length})
        </button>
        <button onClick={() => setActiveTab("referrals")}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === "referrals" ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm" : "text-slate-600 dark:text-slate-400 hover:text-slate-900"}`}>
          Referrals ({referrals.length})
        </button>
      </div>

      {activeTab === "incidents" && (
        <>
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-sm">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input value={search} onChange={e => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm dark:text-slate-200"
                placeholder="Search incidents..." />
            </div>
            <FunnelIcon className="h-4 w-4 text-slate-400" />
            {["all", "open", "investigating", "resolved", "closed"].map(s => (
              <button key={s} onClick={() => setStatusFilter(s)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${statusFilter === s ? STATUS_COLORS[s] || "bg-indigo-100 text-indigo-700" : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-200"}`}>
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </button>
            ))}
          </div>

          {isLoading ? (
            <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-20 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : filtered.length === 0 ? (
            <EmptyState icon={ExclamationTriangleIcon} title="No incidents found"
              description={search ? "Try a different search term" : "No incidents have been reported yet"} />
          ) : (
            <div className="space-y-3">
              {filtered.map(inc => {
                const StatusIcon = STATUS_ICONS[inc.status] || ClockIcon;
                return (
                  <div key={inc.id}
                    onClick={() => { setEditing(inc); setShowForm(true); }}
                    className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${SEVERITY_COLORS[inc.severity]}`}>{inc.severity}</span>
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[inc.status]}`}>
                            <StatusIcon className="h-3 w-3" /> {inc.status}
                          </span>
                          <span className="text-xs text-slate-400">{inc.incident_type}</span>
                        </div>
                        <p className="font-medium text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{inc.student_name}</p>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mt-1 line-clamp-2">{inc.description}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-slate-400">
                          <span>📅 {dayjs(inc.occurred_at).format("MMM D, YYYY h:mm A")}</span>
                          {inc.location && <span>📍 {inc.location}</span>}
                          <span>👤 {inc.reported_by_name}</span>
                        </div>
                      </div>
                      <div className="flex gap-1 ml-4" onClick={e => e.stopPropagation()}>
                        <button onClick={() => { setEditing(inc); setShowForm(true); }}
                          className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700">
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        <button onClick={() => { if (confirm("Delete this incident?")) deleteMut.mutate(inc.id); }}
                          className="p-2 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30">
                          <XCircleIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {activeTab === "referrals" && (
        <div className="space-y-3">
          {referrals.length === 0 ? (
            <EmptyState icon={ExclamationTriangleIcon} title="No referrals" description="No referrals have been created yet" />
          ) : (
            referrals.map(ref => (
              <div key={ref.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">To: {ref.referred_to_name}</p>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{ref.reason}</p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-slate-400">
                      <span>By: {ref.referred_by_name}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        ref.status === "actioned" ? "bg-green-100 text-green-700" :
                        ref.status === "closed" ? "bg-slate-100 text-slate-600" :
                        "bg-yellow-100 text-yellow-700"
                      }`}>{ref.status}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {showForm && (
        <IncidentFormModal
          open={showForm}
          onClose={() => { setShowForm(false); setEditing(null); }}
          incident={editing}
          onSaved={() => { setShowForm(false); setEditing(null); qc.invalidateQueries({ queryKey: ["behavior-incidents"] }); }}
        />
      )}
    </div>
  );
}
