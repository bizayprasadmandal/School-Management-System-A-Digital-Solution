/**
 * Teacher Sports Page — manage sports, teams, events
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, EmptyState } from "../../components/common";
import { TrophyIcon, UsersIcon, PlusIcon } from "@heroicons/react/24/outline";

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
  const qc = useQueryClient();

  const { data: sports = [], isLoading } = useQuery({
    queryKey: ["teacher-sports"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/sports/sports/");
      return r.results ?? [];
    },
  });

  const { data: teams = [] } = useQuery({
    queryKey: ["teacher-sports-teams"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/sports/teams/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Sports & Activities</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Manage sports, teams, and extracurricular activities
          </p>
        </div>
      </div>

      {isLoading ? (
        <SportsSkeleton />
      ) : sports.length === 0 ? (
        <EmptyState
          icon={TrophyIcon}
          title="No sports"
          description="Add sports and activities for students."
        />
      ) : (
        <>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            Sports ({sports.length})
          </h2>
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
                <div className="mt-3 flex items-center gap-1 text-xs text-slate-400">
                  <UsersIcon className="h-3.5 w-3.5" />
                  {sport.team_count ?? 0} teams
                </div>
              </div>
            ))}
          </div>

          {teams.length > 0 && (
            <>
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                Teams ({teams.length})
              </h2>
              <div className="grid gap-4 sm:grid-cols-2">
                {teams.map((team: any) => (
                  <div
                    key={team.id}
                    className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
                  >
                    <h3 className="font-semibold text-slate-900 dark:text-white">{team.name}</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {team.sport_name} · {team.member_count ?? 0} members
                    </p>
                    {team.coach_name && (
                      <p className="mt-1 text-xs text-slate-400">Coach: {team.coach_name}</p>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
