/**
 * Student Counseling Page — view counseling sessions
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { ChatBubbleLeftRightIcon, CalendarDaysIcon, ClockIcon } from "@heroicons/react/24/outline";

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
  const { data: sessions = [], isLoading } = useQuery({
    queryKey: ["student-counseling"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/counseling/sessions/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Counseling</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          View your counseling sessions and referrals
        </p>
      </div>

      {isLoading ? (
        <CounselingSkeleton />
      ) : sessions.length === 0 ? (
        <EmptyState
          icon={ChatBubbleLeftRightIcon}
          title="No counseling sessions"
          description="Your counseling sessions will appear here."
        />
      ) : (
        <div className="space-y-3">
          {sessions.map((session: any) => (
            <div
              key={session.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">
                    {session.title ?? "Counseling Session"}
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {session.counselor_name ?? "—"}
                  </p>
                  <div className="mt-2 flex items-center gap-3">
                    <span className="flex items-center gap-1 text-xs text-slate-400">
                      <CalendarDaysIcon className="h-3.5 w-3.5" />
                      {session.date ?? "—"}
                    </span>
                    <span className="flex items-center gap-1 text-xs text-slate-400">
                      <ClockIcon className="h-3.5 w-3.5" />
                      {session.time ?? "—"}
                    </span>
                  </div>
                </div>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    session.status === "completed"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : session.status === "scheduled"
                        ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                        : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                  }`}
                >
                  {session.status ?? "pending"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
