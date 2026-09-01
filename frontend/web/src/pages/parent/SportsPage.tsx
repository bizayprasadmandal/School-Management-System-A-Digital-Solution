/**
 * Parent Sports Page — View child's teams, events, achievements.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { UsersIcon, CalendarDaysIcon, StarIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface Team {
  id: string;
  sport_name: string;
  name: string;
  member_count: number;
  is_active: boolean;
}
interface SportEvent {
  id: string;
  sport_name: string;
  title: string;
  event_date: string;
  status_display: string;
}
interface Achievement {
  id: string;
  student_name: string;
  title: string;
  position: string;
  level: string;
  awarded_date: string;
}

export default function ParentSportsPage() {
  useTitle("Sports");
  const [tab, setTab] = useState<"teams" | "events" | "achievements">("teams");
  const { data: teams = [], isLoading: tLoading } = useQuery({
    queryKey: ["parent-teams"],
    queryFn: async () => {
      const r = await api.get<{ results: Team[] }>("/sports/teams/children/");
      return r.results ?? [];
    },
  });
  const { data: events = [], isLoading: eLoading } = useQuery({
    queryKey: ["parent-sport-events"],
    queryFn: async () => {
      const r = await api.get<{ results: SportEvent[] }>("/sports/events/");
      return r.results ?? [];
    },
  });
  const { data: achievements = [], isLoading: aLoading } = useQuery({
    queryKey: ["parent-achievements"],
    queryFn: async () => {
      const r = await api.get<{ results: Achievement[] }>("/sports/achievements/children/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Sports</h1>
        <p className="text-sm text-slate-500 mt-1">Your children's sports activities</p>
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
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
        <button
          onClick={() => setTab("achievements")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "achievements" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <StarIcon className="h-4 w-4 inline mr-1.5" />
          Achievements
        </button>
      </div>
      {tab === "teams" && <TeamList teams={teams} isLoading={tLoading} />}
      {tab === "events" && <EventList events={events} isLoading={eLoading} />}
      {tab === "achievements" && (
        <AchievementList achievements={achievements} isLoading={aLoading} />
      )}
    </div>
  );
}

function TeamList({ teams, isLoading }: { teams: Team[]; isLoading: boolean }) {
  if (isLoading)
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  if (!teams.length) return <EmptyState icon={UsersIcon} title="No teams" />;
  return (
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
                {t.sport_name} · {t.member_count} members
              </p>
            </div>
            <Badge color={t.is_active ? "green" : "slate"}>
              {t.is_active ? "Active" : "Inactive"}
            </Badge>
          </div>
        </div>
      ))}
    </div>
  );
}

function EventList({ events, isLoading }: { events: SportEvent[]; isLoading: boolean }) {
  if (isLoading)
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  if (!events.length) return <EmptyState icon={CalendarDaysIcon} title="No events" />;
  return (
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
            </div>
            <Badge color={e.status_display === "Completed" ? "green" : "blue"}>
              {e.status_display}
            </Badge>
          </div>
        </div>
      ))}
    </div>
  );
}

function AchievementList({
  achievements,
  isLoading,
}: {
  achievements: Achievement[];
  isLoading: boolean;
}) {
  if (isLoading)
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  if (!achievements.length) return <EmptyState icon={StarIcon} title="No achievements" />;
  return (
    <div className="space-y-2">
      {achievements.map((a) => (
        <div
          key={a.id}
          className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
        >
          <p className="font-semibold text-slate-900 dark:text-white">{a.title}</p>
          {a.position && <p className="text-sm text-indigo-600">🏆 {a.position}</p>}
          <p className="text-xs text-slate-400">
            {a.student_name} · {a.level} · {dayjs(a.awarded_date).format("MMM D, YYYY")}
          </p>
        </div>
      ))}
    </div>
  );
}
