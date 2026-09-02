/**
 * Counselor Peer Mentoring Page — manage mentor-mentee pairs
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { UserGroupIcon } from "@heroicons/react/24/outline";

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
  const { data: pairs = [], isLoading } = useQuery({
    queryKey: ["counselor-peer-mentoring"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/counseling/peer-mentoring/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Peer Mentoring</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Manage mentor-mentee pairs for student support
          </p>
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
          {pairs.map((pair: any) => (
            <div
              key={pair.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {pair.mentor_name ?? "Mentor"} → {pair.mentee_name ?? "Mentee"}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{pair.goals ?? "—"}</p>
                <p className="mt-1 text-xs text-slate-400">
                  {pair.sessions_completed ?? 0} sessions completed
                </p>
              </div>
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
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
