/**
 * Parent Behavior Page — View child's behavior incidents and points.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { ExclamationTriangleIcon, StarIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface BehaviorIncident {
  id: string;
  student_name: string;
  incident_type_display: string;
  description: string;
  severity: string;
  incident_date: string;
}
interface BehaviorPoint {
  id: string;
  student_name: string;
  points: number;
  reason: string;
  awarded_date: string;
}

export default function ParentBehaviorPage() {
  useTitle("Behavior");
  const [tab, setTab] = useState<"incidents" | "points">("incidents");
  const { data: incidents = [], isLoading: iLoading } = useQuery({
    queryKey: ["parent-incidents"],
    queryFn: async () => {
      const r = await api.get<{ results: BehaviorIncident[] }>("/behavior/incidents/children/");
      return r.results ?? [];
    },
  });
  const { data: points = [], isLoading: pLoading } = useQuery({
    queryKey: ["parent-points"],
    queryFn: async () => {
      const r = await api.get<{ results: BehaviorPoint[] }>("/behavior/points/children/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Behavior</h1>
        <p className="text-sm text-slate-500 mt-1">Your children's behavior records</p>
      </div>
      <TabBar tab={tab} setTab={setTab} />

      {tab === "incidents" && <IncidentList incidents={incidents} isLoading={iLoading} />}
      {tab === "points" && <PointsList points={points} isLoading={pLoading} />}
    </div>
  );
}

function TabBar({ tab, setTab }: { tab: string; setTab: (v: "incidents" | "points") => void }) {
  return (
    <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
      <button
        onClick={() => setTab("incidents")}
        className={`px-4 py-2 rounded-md text-sm font-medium ${
          tab === "incidents" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
        }`}
      >
        <ExclamationTriangleIcon className="h-4 w-4 inline mr-1.5" />
        Incidents
      </button>
      <button
        onClick={() => setTab("points")}
        className={`px-4 py-2 rounded-md text-sm font-medium ${
          tab === "points" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
        }`}
      >
        <StarIcon className="h-4 w-4 inline mr-1.5" />
        Points
      </button>
    </div>
  );
}

function IncidentList({
  incidents,
  isLoading,
}: {
  incidents: BehaviorIncident[];
  isLoading: boolean;
}) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  }
  if (!incidents.length) {
    return (
      <EmptyState
        icon={ExclamationTriangleIcon}
        title="No incidents"
        description="No behavior incidents recorded for your children"
      />
    );
  }
  return (
    <div className="space-y-2">
      {incidents.map((inc) => (
        <div
          key={inc.id}
          className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="font-semibold text-slate-900 dark:text-white">{inc.student_name}</p>
              <p className="text-sm text-slate-500 mt-0.5">
                {inc.incident_type_display}: {inc.description}
              </p>
              <p className="text-xs text-slate-400 mt-1">
                {dayjs(inc.incident_date).format("MMM D, YYYY")}
              </p>
            </div>
            <Badge
              color={inc.severity === "high" ? "red" : inc.severity === "medium" ? "amber" : "blue"}
            >
              {inc.severity}
            </Badge>
          </div>
        </div>
      ))}
    </div>
  );
}

function PointsList({ points, isLoading }: { points: BehaviorPoint[]; isLoading: boolean }) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-12 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  }
  if (!points.length) {
    return (
      <EmptyState icon={StarIcon} title="No points" description="No behavior points awarded" />
    );
  }
  return (
    <div className="space-y-2">
      {points.map((p) => (
        <div
          key={p.id}
          className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3 flex items-center justify-between"
        >
          <div>
            <p className="text-sm font-medium text-slate-900 dark:text-white">{p.student_name}</p>
            <p className="text-xs text-slate-400">
              {p.reason} · {dayjs(p.awarded_date).format("MMM D")}
            </p>
          </div>
          <p className={`text-lg font-bold ${p.points > 0 ? "text-green-600" : "text-red-600"}`}>
            {p.points > 0 ? "+" : ""}
            {p.points}
          </p>
        </div>
      ))}
    </div>
  );
}
