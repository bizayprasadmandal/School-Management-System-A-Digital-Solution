/**
 * Teacher Counseling Page — create referrals and view sessions
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, EmptyState } from "../../components/common";
import { ChatBubbleLeftRightIcon, PlusIcon, ClockIcon } from "@heroicons/react/24/outline";

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
  const [showForm, setShowForm] = useState(false);

  const { data: referrals = [], isLoading } = useQuery({
    queryKey: ["teacher-counseling"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/counseling/referrals/");
      return r.results ?? [];
    },
  });

  const createReferral = useMutation({
    mutationFn: (data: any) => api.post("/counseling/referrals/", data),
    onSuccess: () => {
      toast.success("Referral created");
      qc.invalidateQueries({ queryKey: ["teacher-counseling"] });
      setShowForm(false);
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
        <Button onClick={() => setShowForm(!showForm)}>
          <PlusIcon className="mr-1.5 h-4 w-4" />
          Create Referral
        </Button>
      </div>

      {showForm && (
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <h3 className="mb-3 font-semibold text-slate-900 dark:text-white">New Referral</h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const fd = new FormData(e.currentTarget);
              createReferral.mutate({
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
              placeholder="Reason for referral"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
              required
            />
            <textarea
              name="notes"
              placeholder="Additional notes"
              rows={2}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            />
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={createReferral.isPending}>
                Submit
              </Button>
            </div>
          </form>
        </div>
      )}

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
          {referrals.map((ref: any) => (
            <div
              key={ref.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">
                    {ref.student_name ?? "Student"}
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">{ref.reason ?? "—"}</p>
                  <div className="mt-1 flex items-center gap-1 text-xs text-slate-400">
                    <ClockIcon className="h-3.5 w-3.5" />
                    {ref.created_at ?? "—"}
                  </div>
                </div>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    ref.status === "resolved"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : ref.status === "in_progress"
                        ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                        : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                  }`}
                >
                  {ref.status ?? "pending"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
