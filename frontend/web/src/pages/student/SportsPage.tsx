/**
 * Student Sports Page — Browse sports, teams, events, and achievements.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { TrophyIcon, UsersIcon, CalendarDaysIcon, StarIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface Sport {
  id: string;
  name: string;
  category_display: string;
  description: string;
  min_players: number;
  max_players: number;
  is_active: boolean;
}
interface Team {
  id: string;
  sport_name: string;
  name: string;
  gender_display: string;
  coach_name: string | null;
  member_count: number;
  is_active: boolean;
}
interface SportEvent {
  id: string;
  sport_name: string;
  title: string;
  opponent: string;
  location: string;
  event_date: string;
  status_display: string;
  home_score: string;
  opponent_score: string;
}
interface Achievement {
  id: string;
  student_name: string | null;
  team_name: string | null;
  title: string;
  position: string;
  level: string;
  awarded_date: string;
}

type Tab = "sports" | "teams" | "events" | "achievements";
const TABS: { key: Tab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "sports", label: "Sports", icon: TrophyIcon },
  { key: "teams", label: "Teams", icon: UsersIcon },
  { key: "events", label: "Events", icon: CalendarDaysIcon },
  { key: "achievements", label: "Achievements", icon: StarIcon },
];

export default function StudentSportsPage() {
  useTitle("Sports");
  const [tab, setTab] = useState<Tab>("sports");

  const { data: sports = [], isLoading: sLoading } = useQuery({
    queryKey: ["student-sports"],
    queryFn: async () => {
      const r = await api.get<{ results: Sport[] }>("/sports/sports/");
      return r.results ?? [];
    },
  });
  const { data: teams = [], isLoading: tLoading } = useQuery({
    queryKey: ["student-teams"],
    queryFn: async () => {
      const r = await api.get<{ results: Team[] }>("/sports/teams/");
      return r.results ?? [];
    },
  });
  const { data: events = [], isLoading: eLoading } = useQuery({
    queryKey: ["student-sport-events"],
    queryFn: async () => {
      const r = await api.get<{ results: SportEvent[] }>("/sports/events/");
      return r.results ?? [];
    },
  });
  const { data: achievements = [], isLoading: aLoading } = useQuery({
    queryKey: ["student-achievements"],
    queryFn: async () => {
      const r = await api.get<{ results: Achievement[] }>("/sports/achievements/my/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Sports & Activities</h1>
        <p className="text-sm text-slate-500 mt-1">
          Browse sports, teams, events, and your achievements
        </p>
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
        {TABS.map((t) => {
          const I = t.icon;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
                tab === t.key
                  ? "bg-white dark:bg-slate-700 shadow-sm text-slate-900 dark:text-white"
                  : "text-slate-600 hover:text-slate-900 dark:text-slate-400"
              }`}
            >
              <I className="h-4 w-4" />
              {t.label}
            </button>
          );
        })}
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
          <EmptyState icon={TrophyIcon} title="No sports" description="No sports available" />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {sports.map((s) => (
              <div
                key={s.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-all"
              >
                <p className="font-semibold text-slate-900 dark:text-white">{s.name}</p>
                <Badge color="indigo">{s.category_display}</Badge>
                {s.description && (
                  <p className="text-xs text-slate-500 mt-2 line-clamp-2">{s.description}</p>
                )}
                <p className="text-xs text-slate-400 mt-2">
                  Players: {s.min_players}-{s.max_players}
                </p>
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
          <EmptyState icon={UsersIcon} title="No teams" description="No teams available" />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {teams.map((t) => (
              <div
                key={t.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{t.name}</p>
                    <p className="text-xs text-slate-400">
                      {t.sport_name} · {t.gender_display}
                    </p>
                  </div>
                  <Badge color={t.is_active ? "green" : "slate"}>
                    {t.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
                {t.coach_name && (
                  <p className="text-xs text-slate-500 mt-1">Coach: {t.coach_name}</p>
                )}
                <p className="text-xs text-slate-400 mt-1">Members: {t.member_count}</p>
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
          <EmptyState icon={CalendarDaysIcon} title="No events" description="No upcoming events" />
        ) : (
          <div className="space-y-2">
            {events.map((e) => (
              <div
                key={e.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{e.title}</p>
                    <p className="text-xs text-slate-400">
                      {e.sport_name} · {dayjs(e.event_date).format("MMM D, YYYY h:mm A")}
                    </p>
                    {e.opponent && <p className="text-xs text-slate-500">vs {e.opponent}</p>}
                    {e.location && <p className="text-xs text-slate-400">📍 {e.location}</p>}
                  </div>
                  <div className="text-right">
                    <Badge
                      color={
                        e.status_display === "Completed"
                          ? "green"
                          : e.status_display === "Cancelled"
                            ? "red"
                            : "blue"
                      }
                    >
                      {e.status_display}
                    </Badge>
                    {e.home_score && (
                      <p className="text-sm font-bold text-slate-900 dark:text-white mt-1">
                        {e.home_score} - {e.opponent_score}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}

      {tab === "achievements" &&
        (aLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !achievements.length ? (
          <EmptyState
            icon={StarIcon}
            title="No achievements"
            description="Your achievements will appear here"
          />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {achievements.map((a) => (
              <div
                key={a.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <p className="font-semibold text-slate-900 dark:text-white">{a.title}</p>
                {a.position && (
                  <p className="text-sm text-indigo-600 dark:text-indigo-400">🏆 {a.position}</p>
                )}
                <p className="text-xs text-slate-400 mt-1">
                  {a.level} · {dayjs(a.awarded_date).format("MMM D, YYYY")}
                </p>
                {a.team_name && (
                  <p className="text-xs text-slate-500 mt-0.5">Team: {a.team_name}</p>
                )}
              </div>
            ))}
          </div>
        ))}
    </div>
  );
}
