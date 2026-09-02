/**
 * Teacher Behavior Page — view and award behavior points
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, EmptyState } from "../../components/common";
import {
  ExclamationTriangleIcon,
  PlusIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";

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

  const { data: records = [], isLoading } = useQuery({
    queryKey: ["teacher-behavior"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/behavior/behavior-records/");
      return r.results ?? [];
    },
  });

  const createRecord = useMutation({
    mutationFn: (data: any) => api.post("/behavior/behavior-records/", data),
    onSuccess: () => {
      toast.success("Behavior record created");
      qc.invalidateQueries({ queryKey: ["teacher-behavior"] });
      setShowForm(false);
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Behavior Points</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Award and manage student behavior points
          </p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          <PlusIcon className="mr-1.5 h-4 w-4" />
          Award Points
        </Button>
      </div>

      {showForm && (
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <h3 className="mb-3 font-semibold text-slate-900 dark:text-white">
            Award Behavior Points
          </h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const fd = new FormData(e.currentTarget);
              createRecord.mutate({
                student: fd.get("student"),
                points: Number(fd.get("points")),
                title: fd.get("title"),
                description: fd.get("description"),
              });
            }}
            className="space-y-3"
          >
            <div className="grid gap-3 sm:grid-cols-2">
              <input
                name="student"
                placeholder="Student ID"
                className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
                required
              />
              <input
                name="points"
                type="number"
                placeholder="Points (+/-)"
                className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
                required
              />
            </div>
            <input
              name="title"
              placeholder="Title"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
              required
            />
            <textarea
              name="description"
              placeholder="Description"
              rows={2}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            />
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={createRecord.isPending}>
                Save
              </Button>
            </div>
          </form>
        </div>
      )}

      {isLoading ? (
        <BehaviorSkeleton />
      ) : records.length === 0 ? (
        <EmptyState
          icon={ExclamationTriangleIcon}
          title="No behavior records"
          description="Award behavior points to students here."
        />
      ) : (
        <div className="space-y-3">
          {records.map((record: any) => (
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
                    {record.student_name ?? "Student"}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {record.title ?? "—"}
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
    </div>
  );
}
