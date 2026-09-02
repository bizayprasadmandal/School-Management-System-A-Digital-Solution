/**
 * Teacher Counseling Page — create referrals and view sessions
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
  ClockIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";

interface Referral {
  id: string;
  student_name: string;
  reason: string;
  notes: string;
  status: string;
  created_at: string;
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
  const [editing, setEditing] = useState<Referral | null>(null);

  const { data: allReferrals = [], isLoading } = useQuery({
    queryKey: ["teacher-counseling"],
    queryFn: async () => {
      const r = await api.get<{ results: Referral[] }>("/counseling/referrals/");
      return r.results ?? [];
    },
  });

  const referrals = React.useMemo(() => {
    let items = allReferrals;
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(
        (r) =>
          r.student_name?.toLowerCase().includes(q) ||
          r.reason?.toLowerCase().includes(q) ||
          (r as any).priority?.toLowerCase().includes(q) ||
          (r as any).category?.toLowerCase().includes(q),
      );
    }
    if (statusFilter !== "all") {
      items = items.filter((r) => r.status === statusFilter);
    }
    return items;
  }, [allReferrals, search, statusFilter]);

  const createReferral = useMutation({
    mutationFn: (data: Partial<Referral>) => api.post("/counseling/referrals/", data),
    onSuccess: () => {
      toast.success("Referral created");
      qc.invalidateQueries({ queryKey: ["teacher-counseling"] });
      setShowForm(false);
    },
  });

  const updateReferral = useMutation({
    mutationFn: (data: Partial<Referral>) =>
      api.patch(`/counseling/referrals/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Referral updated");
      qc.invalidateQueries({ queryKey: ["teacher-counseling"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteReferral = useMutation({
    mutationFn: (id: string) => api.delete(`/counseling/referrals/${id}/`),
    onSuccess: () => {
      toast.success("Referral deleted");
      qc.invalidateQueries({ queryKey: ["teacher-counseling"] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Counseling Referrals
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Create referrals and track student counseling
          </p>
        </div>
        <Button
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <PlusIcon className="mr-1.5 h-4 w-4" />
          Create Referral
        </Button>
      </div>

      {/* Search + Filters */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700 space-y-3">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              placeholder="Search by student name or reason..."
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
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
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
      ) : referrals.length === 0 ? (
        <EmptyState
          icon={ChatBubbleLeftRightIcon}
          title="No referrals"
          description="Create counseling referrals for students who need support."
        />
      ) : (
        <div className="space-y-3">
          {referrals.map((ref) => (
            <div
              key={ref.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">
                    {ref.student_name}
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">{ref.reason || "—"}</p>
                  <div className="mt-1 flex items-center gap-1 text-xs text-slate-400">
                    <ClockIcon className="h-3.5 w-3.5" />
                    {ref.created_at || "—"}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                      ref.status === "resolved"
                        ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                        : ref.status === "in_progress"
                          ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                          : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                    }`}
                  >
                    {ref.status || "pending"}
                  </span>
                  <div className="flex gap-1">
                    <button
                      onClick={() => {
                        setEditing(ref);
                        setShowForm(true);
                      }}
                      className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => {
                        if (confirm("Delete this referral?")) deleteReferral.mutate(ref.id);
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
        title={editing ? "Edit Referral" : "Create Referral"}
      >
        <ReferralForm
          referral={editing}
          saving={createReferral.isPending || updateReferral.isPending}
          onSave={(data) => {
            if (editing) updateReferral.mutate(data);
            else createReferral.mutate(data);
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

function ReferralForm({
  referral,
  saving,
  onSave,
  onCancel,
}: {
  referral: Referral | null;
  saving: boolean;
  onSave: (data: Partial<Referral>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    student_name: referral?.student_name ?? "",
    reason: referral?.reason ?? "",
    notes: referral?.notes ?? "",
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
        <label className="mb-1 block text-sm font-medium">Notes</label>
        <textarea
          value={f.notes}
          onChange={(e) => setF((p) => ({ ...p, notes: e.target.value }))}
          rows={3}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {referral ? "Update" : "Submit"}
        </Button>
      </div>
    </form>
  );
}
