/**
 * Teacher Sports Page — Manage sports teams and view events.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { TrophyIcon, UsersIcon, CalendarDaysIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface Sport {
  id: string;
  name: string;
  category_display: string;
  is_active: boolean;
}
interface Team {
  id: string;
  sport_name: string;
  name: string;
  coach_name: string | null;
  member_count: number;
  is_active: boolean;
}
interface SportEvent {
  id: string;
  sport_name: string;
  title: string;
  event_date: string;
  status_display: string;
  location: string;
}

export default function TeacherSportsPage() {
  useTitle("Sports");
  const [tab, setTab] = useState<"sports" | "teams" | "events">("sports");

  const { data: sports = [], isLoading: sLoading } = useQuery({
    queryKey: ["teacher-sports"],
    queryFn: async () => {
      const r = await api.get<{ results: Sport[] }>("/sports/sports/");
      return r.results ?? [];
    },
  });
  const { data: teams = [], isLoading: tLoading } = useQuery({
    queryKey: ["teacher-teams"],
    queryFn: async () => {
      const r = await api.get<{ results: Team[] }>("/sports/teams/");
      return r.results ?? [];
    },
  });
  const { data: events = [], isLoading: eLoading } = useQuery({
    queryKey: ["teacher-sport-events"],
    queryFn: async () => {
      const r = await api.get<{ results: SportEvent[] }>("/sports/events/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Sports & Activities</h1>
        <p className="text-sm text-slate-500 mt-1">Manage teams and view events</p>
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        <button
          onClick={() => setTab("sports")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "sports" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <TrophyIcon className="h-4 w-4 inline mr-1.5" />
          Sports
        </button>
        <button
          onClick={() => setTab("teams")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "teams" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <UsersIcon className="h-4 w-4 inline mr-1.5" />
          Teams
        </button>
        <button
          onClick={() => setTab("events")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "events" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <CalendarDaysIcon className="h-4 w-4 inline mr-1.5" />
          Events
        </button>
      </div>

      {tab === "sports" &&
        (sLoading ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-24 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !sports.length ? (
          <EmptyState icon={TrophyIcon} title="No sports" />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {sports.map((s) => (
              <div
                key={s.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <p className="font-semibold text-slate-900 dark:text-white">{s.name}</p>
                <Badge color="indigo">{s.category_display}</Badge>
                <Badge color={s.is_active ? "green" : "slate"}>
                  {s.is_active ? "Active" : "Inactive"}
                </Badge>
              </div>
            ))}
          </div>
        ))}

      {tab === "teams" &&
        (tLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !teams.length ? (
          <EmptyState icon={UsersIcon} title="No teams" />
        ) : (
          <div className="space-y-2">
            {teams.map((t) => (
              <div
                key={t.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{t.name}</p>
                    <p className="text-xs text-slate-400">
                      {t.sport_name}
                      {t.coach_name ? ` · Coach: ${t.coach_name}` : ""}
                    </p>
                  </div>
                  <div className="flex gap-2 items-center">
                    <p className="text-xs text-slate-400">{t.member_count} members</p>
                    <Badge color={t.is_active ? "green" : "slate"}>
                      {t.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}

      {tab === "events" &&
        (eLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !events.length ? (
          <EmptyState icon={CalendarDaysIcon} title="No events" />
        ) : (
          <div className="space-y-2">
            {events.map((e) => (
              <div
                key={e.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{e.title}</p>
                    <p className="text-xs text-slate-400">
                      {e.sport_name} · {dayjs(e.event_date).format("MMM D, YYYY")}
                    </p>
                    {e.location && <p className="text-xs text-slate-400">📍 {e.location}</p>}
                  </div>
                  <Badge color={e.status_display === "Completed" ? "green" : "blue"}>
                    {e.status_display}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        ))}
    </div>
  );
}
