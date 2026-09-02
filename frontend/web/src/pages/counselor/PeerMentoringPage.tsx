/**
 * Counselor Peer Mentoring Page — manage mentor-mentee pairs
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import {
  UserGroupIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";

interface MentoringPair {
  id: string;
  mentor_name: string;
  mentee_name: string;
  goals: string;
  sessions_completed: number;
  status: string;
}

function MentoringSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function PeerMentoringPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<MentoringPair | null>(null);

  const { data: pairs = [], isLoading } = useQuery({
    queryKey: ["counselor-peer-mentoring"],
    queryFn: async () => {
      const r = await api.get<{ results: MentoringPair[] }>("/counseling/peer-mentoring/");
      return r.results ?? [];
    },
  });

  const createPair = useMutation({
    mutationFn: (data: Partial<MentoringPair>) => api.post("/counseling/peer-mentoring/", data),
    onSuccess: () => {
      toast.success("Pair created");
      qc.invalidateQueries({ queryKey: ["counselor-peer-mentoring"] });
      setShowForm(false);
    },
  });

  const updatePair = useMutation({
    mutationFn: (data: Partial<MentoringPair>) =>
      api.patch(`/counseling/peer-mentoring/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Pair updated");
      qc.invalidateQueries({ queryKey: ["counselor-peer-mentoring"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deletePair = useMutation({
    mutationFn: (id: string) => api.delete(`/counseling/peer-mentoring/${id}/`),
    onSuccess: () => {
      toast.success("Pair deleted");
      qc.invalidateQueries({ queryKey: ["counselor-peer-mentoring"] });
    },
  });

  const paginatedPairs = React.useMemo(() => {
    const start = (page - 1) * 12;
    return pairs.slice(start, start + 12);
  }, [pairs, page]);

  const totalPages = Math.ceil(pairs.length / 12);
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Peer Mentoring</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Manage mentor-mentee pairs for student support
          </p>
        </div>
        <Button
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <PlusIcon className="mr-1.5 h-4 w-4" />
          Create Pair
        </Button>
      </div>

      {/* Search */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search mentors or mentees..."
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
        <MentoringSkeleton />
      ) : pairs.length === 0 ? (
        <EmptyState
          icon={UserGroupIcon}
          title="No mentoring pairs"
          description="Pair students for peer mentoring support."
        />
      ) : (
        <div className="space-y-3">
          {paginatedPairs.map((pair) => (
            <div
              key={pair.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {pair.mentor_name} → {pair.mentee_name}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{pair.goals || "—"}</p>
                <p className="mt-1 text-xs text-slate-400">
                  {pair.sessions_completed ?? 0} sessions completed
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    pair.status === "active"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : pair.status === "pending"
                        ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                        : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                  }`}
                >
                  {pair.status}
                </span>
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(pair);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this pair?")) deletePair.mutate(pair.id);
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
        <Pagination page={page} total={pairs.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Pair" : "Create Pair"}
      >
        <PairForm
          pair={editing}
          saving={createPair.isPending || updatePair.isPending}
          onSave={(data) => {
            if (editing) updatePair.mutate(data);
            else createPair.mutate(data);
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

function PairForm({
  pair,
  saving,
  onSave,
  onCancel,
}: {
  pair: MentoringPair | null;
  saving: boolean;
  onSave: (data: Partial<MentoringPair>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    mentor_name: pair?.mentor_name ?? "",
    mentee_name: pair?.mentee_name ?? "",
    goals: pair?.goals ?? "",
    status: pair?.status ?? "pending",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.mentor_name.trim()) return toast.error("Mentor required");
        if (!f.mentee_name.trim()) return toast.error("Mentee required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Mentor *</label>
          <input
            value={f.mentor_name}
            onChange={(e) => setF((p) => ({ ...p, mentor_name: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Mentee *</label>
          <input
            value={f.mentee_name}
            onChange={(e) => setF((p) => ({ ...p, mentee_name: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Goals</label>
        <textarea
          value={f.goals}
          onChange={(e) => setF((p) => ({ ...p, goals: e.target.value }))}
          rows={3}
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
          <option value="pending">Pending</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
        </select>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {pair ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
