/**
 * Student Counseling Page — view counseling sessions
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, EmptyState, Modal } from "../../components/common";
import {
  ChatBubbleLeftRightIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CalendarDaysIcon,
  ClockIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";

interface Session {
  id: string;
  title: string;
  counselor_name: string;
  date: string;
  time: string;
  status: string;
}

function CounselingSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function CounselingPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Session | null>(null);

  const { data: allSessions = [], isLoading } = useQuery({
    queryKey: ["student-counseling"],
    queryFn: async () => {
      const r = await api.get<{ results: Session[] }>("/counseling/sessions/");
      return r.results ?? [];
    },
  });

  const sessions = React.useMemo(() => {
    let items = allSessions;
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(
        (s) =>
          s.counselor_name?.toLowerCase().includes(q) ||
          (s as any).topic?.toLowerCase().includes(q) ||
          (s as any).reason?.toLowerCase().includes(q) ||
          s.status?.toLowerCase().includes(q),
      );
    }
    if (statusFilter !== "all") {
      items = items.filter((s) => s.status === statusFilter);
    }
    return items;
  }, [allSessions, search, statusFilter]);

  const createSession = useMutation({
    mutationFn: (data: Partial<Session>) => api.post("/counseling/sessions/", data),
    onSuccess: () => {
      toast.success("Session created");
      qc.invalidateQueries({ queryKey: ["student-counseling"] });
      setShowForm(false);
    },
  });

  const updateSession = useMutation({
    mutationFn: (data: Partial<Session>) => api.patch(`/counseling/sessions/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Session updated");
      qc.invalidateQueries({ queryKey: ["student-counseling"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteSession = useMutation({
    mutationFn: (id: string) => api.delete(`/counseling/sessions/${id}/`),
    onSuccess: () => {
      toast.success("Session deleted");
      qc.invalidateQueries({ queryKey: ["student-counseling"] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Counseling</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            View your counseling sessions and referrals
          </p>
        </div>
        <Button
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <PlusIcon className="mr-1.5 h-4 w-4" />
          Book Session
        </Button>
      </div>

      {/* Search + Filters */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700 space-y-3">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              placeholder="Search sessions..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-400"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-700 dark:text-white"
          >
            <option value="all">All Status</option>
            <option value="scheduled">Scheduled</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
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
        <CounselingSkeleton />
      ) : sessions.length === 0 ? (
        <EmptyState
          icon={ChatBubbleLeftRightIcon}
          title="No counseling sessions"
          description="Your counseling sessions will appear here."
        />
      ) : (
        <div className="space-y-3">
          {sessions.map((session) => (
            <div
              key={session.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">{session.title}</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {session.counselor_name || "—"}
                  </p>
                  <div className="mt-2 flex items-center gap-3">
                    <span className="flex items-center gap-1 text-xs text-slate-400">
                      <CalendarDaysIcon className="h-3.5 w-3.5" />
                      {session.date || "—"}
                    </span>
                    <span className="flex items-center gap-1 text-xs text-slate-400">
                      <ClockIcon className="h-3.5 w-3.5" />
                      {session.time || "—"}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      session.status === "completed"
                        ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                        : session.status === "scheduled"
                          ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                          : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                    }`}
                  >
                    {session.status || "pending"}
                  </span>
                  <div className="flex gap-1">
                    <button
                      onClick={() => {
                        setEditing(session);
                        setShowForm(true);
                      }}
                      className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => {
                        if (confirm("Delete this session?")) deleteSession.mutate(session.id);
                      }}
                      className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
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
        title={editing ? "Edit Session" : "Book Session"}
      >
        <SessionForm
          session={editing}
          saving={createSession.isPending || updateSession.isPending}
          onSave={(data) => {
            if (editing) updateSession.mutate(data);
            else createSession.mutate(data);
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

function SessionForm({
  session,
  saving,
  onSave,
  onCancel,
}: {
  session: Session | null;
  saving: boolean;
  onSave: (data: Partial<Session>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    title: session?.title ?? "",
    counselor_name: session?.counselor_name ?? "",
    date: session?.date ?? "",
    time: session?.time ?? "",
    reason: "",
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
        <label className="mb-1 block text-sm font-medium">Counselor</label>
        <input
          value={f.counselor_name}
          onChange={(e) => setF((p) => ({ ...p, counselor_name: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Date *</label>
          <input
            type="date"
            value={f.date}
            onChange={(e) => setF((p) => ({ ...p, date: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Time</label>
          <input
            type="time"
            value={f.time}
            onChange={(e) => setF((p) => ({ ...p, time: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Reason</label>
        <textarea
          value={f.reason}
          onChange={(e) => setF((p) => ({ ...p, reason: e.target.value }))}
          rows={2}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {session ? "Update" : "Book"}
        </Button>
      </div>
    </form>
  );
}
