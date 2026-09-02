/**
 * Student Behavior Page — view behavior points and records
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { ExclamationTriangleIcon, CheckCircleIcon, XCircleIcon } from "@heroicons/react/24/outline";

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
  const { data: records = [], isLoading } = useQuery({
    queryKey: ["student-behavior"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/behavior/behavior-records/");
      return r.results ?? [];
    },
  });

  const totalPoints = records.reduce((sum: number, r: any) => sum + (r.points ?? 0), 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Behavior Points</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Track your behavior records and points
        </p>
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
            {records.filter((r: any) => r.points > 0).length}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-sm text-slate-500 dark:text-slate-400">Negative Records</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">
            {records.filter((r: any) => r.points < 0).length}
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
                    {record.title ?? "Behavior Record"}
                  </p>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {record.description ?? "—"}
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
