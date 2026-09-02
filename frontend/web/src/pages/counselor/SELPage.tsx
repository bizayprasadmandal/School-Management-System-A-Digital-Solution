/**
 * Counselor SEL Page — manage Social-Emotional Learning programs
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { HeartIcon } from "@heroicons/react/24/outline";

function SELSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function SELPage() {
  const { data: programs = [], isLoading } = useQuery({
    queryKey: ["counselor-sel"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/counseling/sel-programs/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Social-Emotional Learning
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Manage SEL programs for students
          </p>
        </div>
      </div>

      {isLoading ? (
        <SELSkeleton />
      ) : programs.length === 0 ? (
        <EmptyState
          icon={HeartIcon}
          title="No SEL programs"
          description="Create social-emotional learning programs for students."
        />
      ) : (
        <div className="space-y-3">
          {programs.map((program: any) => {
            const progress = program.progress ?? 0;
            return (
              <div
                key={program.id}
                className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-900 dark:text-white">
                      {program.title}
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {program.category ?? "—"}
                    </p>
                    <p className="mt-1 text-xs text-slate-400">
                      {program.participants ?? 0} participants
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        program.status === "active"
                          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                          : program.status === "upcoming"
                            ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                            : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                      }`}
                    >
                      {program.status}
                    </span>
                    <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                      <div
                        className="h-full rounded-full bg-indigo-500"
                        style={{ width: `${Math.min(progress, 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
