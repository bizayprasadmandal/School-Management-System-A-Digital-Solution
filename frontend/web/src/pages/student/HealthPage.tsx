/**
 * Student Health Page — view health records, vaccinations, visits
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, EmptyState, Modal } from "../../components/common";
import { HeartIcon, PlusIcon, PencilIcon, TrashIcon, ClockIcon } from "@heroicons/react/24/outline";

interface HealthRecord {
  id: string;
  record_type: string;
  description: string;
  date: string;
  notes: string;
}

function HealthSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-32 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function HealthPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<HealthRecord | null>(null);

  const { data: records = [], isLoading } = useQuery({
    queryKey: ["student-health-records"],
    queryFn: async () => {
      const r = await api.get<{ results: HealthRecord[] }>("/health-clinic/health-records/");
      return r.results ?? [];
    },
  });

  const createRecord = useMutation({
    mutationFn: (data: Partial<HealthRecord>) => api.post("/health-clinic/health-records/", data),
    onSuccess: () => {
      toast.success("Health record created");
      qc.invalidateQueries({ queryKey: ["student-health-records"] });
      setShowForm(false);
    },
  });

  const updateRecord = useMutation({
    mutationFn: (data: Partial<HealthRecord>) =>
      api.patch(`/health-clinic/health-records/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Health record updated");
      qc.invalidateQueries({ queryKey: ["student-health-records"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteRecord = useMutation({
    mutationFn: (id: string) => api.delete(`/health-clinic/health-records/${id}/`),
    onSuccess: () => {
      toast.success("Health record deleted");
      qc.invalidateQueries({ queryKey: ["student-health-records"] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">My Health</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            View your health records, vaccinations, and clinic visits
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

      {isLoading ? (
        <HealthSkeleton />
      ) : records.length === 0 ? (
        <EmptyState
          icon={HeartIcon}
          title="No health records"
          description="Your health records will appear here once added by the school nurse."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {records.map((record) => (
            <div
              key={record.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="mb-2 flex items-start justify-between">
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {record.record_type}
                </h3>
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
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {record.description || "No description"}
              </p>
              <div className="mt-3 flex items-center gap-1 text-xs text-slate-400">
                <ClockIcon className="h-3.5 w-3.5" />
                {record.date || "—"}
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
        title={editing ? "Edit Health Record" : "Add Health Record"}
      >
        <HealthRecordForm
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

function HealthRecordForm({
  record,
  saving,
  onSave,
  onCancel,
}: {
  record: HealthRecord | null;
  saving: boolean;
  onSave: (data: Partial<HealthRecord>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    record_type: record?.record_type ?? "",
    description: record?.description ?? "",
    date: record?.date ?? "",
    notes: record?.notes ?? "",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.record_type.trim()) return toast.error("Record type required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div>
        <label className="mb-1 block text-sm font-medium">Record Type *</label>
        <input
          value={f.record_type}
          onChange={(e) => setF((p) => ({ ...p, record_type: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          placeholder="e.g. Vaccination, Check-up"
          required
        />
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
          {editing ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
