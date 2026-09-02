/**
 * Student Sports Page — browse sports, teams, events, achievements
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { TrophyIcon, UsersIcon, CalendarDaysIcon, StarIcon } from "@heroicons/react/24/outline";

function SportsSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-28 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function SportsPage() {
  const { data: sports = [], isLoading } = useQuery({
    queryKey: ["student-sports"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/sports/sports/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Sports & Activities</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Explore sports, teams, events, and achievements
        </p>
      </div>

      {isLoading ? (
        <SportsSkeleton />
      ) : sports.length === 0 ? (
        <EmptyState
          icon={TrophyIcon}
          title="No sports yet"
          description="Sports and activities will appear here once added."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {sports.map((sport: any) => (
            <div
              key={sport.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="mb-2 flex items-center gap-2">
                <TrophyIcon className="h-5 w-5 text-amber-500" />
                <h3 className="font-semibold text-slate-900 dark:text-white">{sport.name}</h3>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {sport.description ?? "No description"}
              </p>
              <div className="mt-3 flex items-center gap-3">
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <UsersIcon className="h-3.5 w-3.5" />
                  {sport.team_count ?? 0} teams
                </span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    sport.is_active
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                  }`}
                >
                  {sport.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
