/**
 * Student Health Page — view health records, vaccinations, visits
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { HeartIcon, ShieldCheckIcon, ClockIcon } from "@heroicons/react/24/outline";

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
  const { data: records = [], isLoading } = useQuery({
    queryKey: ["student-health-records"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/health-clinic/health-records/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">My Health</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          View your health records, vaccinations, and clinic visits
        </p>
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
          {records.map((record: any) => (
            <div
              key={record.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="mb-2 flex items-center gap-2">
                <ShieldCheckIcon className="h-5 w-5 text-green-500" />
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {record.record_type ?? "Health Record"}
                </h3>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {record.description ?? "No description"}
              </p>
              <div className="mt-3 flex items-center gap-1 text-xs text-slate-400">
                <ClockIcon className="h-3.5 w-3.5" />
                {record.date ?? "—"}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
