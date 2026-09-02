/**
 * Teacher Health Page — log student health visits and view records
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, EmptyState } from "../../components/common";
import { HeartIcon, PlusIcon, ClockIcon } from "@heroicons/react/24/outline";

function HealthSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-20 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function HealthPage() {
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);

  const { data: visits = [], isLoading } = useQuery({
    queryKey: ["teacher-health-visits"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/health-clinic/visits/");
      return r.results ?? [];
    },
  });

  const createVisit = useMutation({
    mutationFn: (data: any) => api.post("/health-clinic/visits/", data),
    onSuccess: () => {
      toast.success("Health visit logged");
      qc.invalidateQueries({ queryKey: ["teacher-health-visits"] });
      setShowForm(false);
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Student Health</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Log health visits and view student records
          </p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          <PlusIcon className="mr-1.5 h-4 w-4" />
          Log Visit
        </Button>
      </div>

      {showForm && (
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <h3 className="mb-3 font-semibold text-slate-900 dark:text-white">Log Health Visit</h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const fd = new FormData(e.currentTarget);
              createVisit.mutate({
                student: fd.get("student"),
                reason: fd.get("reason"),
                notes: fd.get("notes"),
              });
            }}
            className="space-y-3"
          >
            <input
              name="student"
              placeholder="Student ID"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
              required
            />
            <input
              name="reason"
              placeholder="Reason for visit"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
              required
            />
            <textarea
              name="notes"
              placeholder="Notes"
              rows={2}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            />
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={createVisit.isPending}>
                Save
              </Button>
            </div>
          </form>
        </div>
      )}

      {isLoading ? (
        <HealthSkeleton />
      ) : visits.length === 0 ? (
        <EmptyState
          icon={HeartIcon}
          title="No health visits"
          description="Log health visits for students here."
        />
      ) : (
        <div className="space-y-3">
          {visits.map((visit: any) => (
            <div
              key={visit.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <p className="font-medium text-slate-900 dark:text-white">
                  {visit.student_name ?? "Student"}
                </p>
                <p className="text-sm text-slate-500 dark:text-slate-400">{visit.reason ?? "—"}</p>
                <div className="mt-1 flex items-center gap-1 text-xs text-slate-400">
                  <ClockIcon className="h-3.5 w-3.5" />
                  {visit.date ?? "—"}
                </div>
              </div>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  visit.status === "resolved"
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                }`}
              >
                {visit.status ?? "pending"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
