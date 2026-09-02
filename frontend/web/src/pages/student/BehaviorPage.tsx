/**
 * Student Behavior Page — view behavior points and records
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, EmptyState, Modal } from "../../components/common";
import {
  ExclamationTriangleIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";

interface BehaviorRecord {
  id: string;
  title: string;
  description: string;
  points: number;
  date: string;
}

function BehaviorSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-20 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function BehaviorPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<BehaviorRecord | null>(null);

  const { data: records = [], isLoading } = useQuery({
    queryKey: ["student-behavior"],
    queryFn: async () => {
      const r = await api.get<{ results: BehaviorRecord[] }>("/behavior/behavior-records/");
      return r.results ?? [];
    },
  });

  const createRecord = useMutation({
    mutationFn: (data: Partial<BehaviorRecord>) => api.post("/behavior/behavior-records/", data),
    onSuccess: () => {
      toast.success("Record created");
      qc.invalidateQueries({ queryKey: ["student-behavior"] });
      setShowForm(false);
    },
  });

  const updateRecord = useMutation({
    mutationFn: (data: Partial<BehaviorRecord>) =>
      api.patch(`/behavior/behavior-records/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Record updated");
      qc.invalidateQueries({ queryKey: ["student-behavior"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteRecord = useMutation({
    mutationFn: (id: string) => api.delete(`/behavior/behavior-records/${id}/`),
    onSuccess: () => {
      toast.success("Record deleted");
      qc.invalidateQueries({ queryKey: ["student-behavior"] });
    },
  });

  const totalPoints = records.reduce((sum, r) => sum + (r.points ?? 0), 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Behavior Points</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Track your behavior records and points
          </p>
        </div>
        <Button
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <PlusIcon className="mr-1.5 h-4 w-4" />
          Add Record
        </Button>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-sm text-slate-500 dark:text-slate-400">Total Points</p>
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
          <p className="text-sm text-slate-500 dark:text-slate-400">Positive Records</p>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">
            {records.filter((r) => r.points > 0).length}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-sm text-slate-500 dark:text-slate-400">Negative Records</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">
            {records.filter((r) => r.points < 0).length}
          </p>
        </div>
      </div>

      {isLoading ? (
        <BehaviorSkeleton />
      ) : records.length === 0 ? (
        <EmptyState
          icon={ExclamationTriangleIcon}
          title="No behavior records"
          description="Your behavior records will appear here."
        />
      ) : (
        <div className="space-y-3">
          {records.map((record) => (
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
                  <p className="font-medium text-slate-900 dark:text-white">{record.title}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {record.description || "—"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
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
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(record);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this record?")) deleteRecord.mutate(record.id);
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

      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Record" : "Add Record"}
      >
        <BehaviorForm
          record={editing}
          saving={createRecord.isPending || updateRecord.isPending}
          onSave={(data) => {
            if (editing) updateRecord.mutate(data);
            else createRecord.mutate(data);
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

function BehaviorForm({
  record,
  saving,
  onSave,
  onCancel,
}: {
  record: BehaviorRecord | null;
  saving: boolean;
  onSave: (data: Partial<BehaviorRecord>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    title: record?.title ?? "",
    description: record?.description ?? "",
    points: record?.points ?? 0,
    date: record?.date ?? "",
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
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Points (+/-) *</label>
          <input
            type="number"
            value={f.points}
            onChange={(e) => setF((p) => ({ ...p, points: Number(e.target.value) }))}
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
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Description</label>
        <textarea
          value={f.description}
          onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
          rows={2}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {record ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
