/**
 * Student Behavior Page — View own behavior records and points.
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { ExclamationTriangleIcon, StarIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface BehaviorIncident {
  id: string;
  incident_type: string;
  incident_type_display: string;
  description: string;
  severity: string;
  status_display: string;
  points_deducted: number;
  incident_date: string;
}
interface BehaviorPoint {
  id: string;
  points: number;
  reason: string;
  category: string;
  awarded_date: string;
}

export default function StudentBehaviorPage() {
  useTitle("Behavior");
  const { data: incidents = [], isLoading: iLoading } = useQuery({
    queryKey: ["student-incidents"],
    queryFn: async () => {
      const r = await api.get<{ results: BehaviorIncident[] }>("/behavior/incidents/my/");
      return r.results ?? [];
    },
  });
  const { data: points = [], isLoading: pLoading } = useQuery({
    queryKey: ["student-points"],
    queryFn: async () => {
      const r = await api.get<{ results: BehaviorPoint[] }>("/behavior/points/my/");
      return r.results ?? [];
    },
  });

  const totalPoints = points.reduce((s, p) => s + p.points, 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Behavior</h1>
        <p className="text-sm text-slate-500 mt-1">View your behavior records and points</p>
      </div>
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-lg bg-amber-50 dark:bg-amber-900/30">
            <StarIcon className="h-6 w-6 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <p className="text-xs text-slate-500 uppercase">Total Points</p>
            <p className="text-3xl font-bold text-slate-900 dark:text-white">{totalPoints}</p>
          </div>
        </div>
      </div>

      <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Incidents</h2>
      {iLoading ? (
        <div className="space-y-2">
          {[1, 2].map((i) => (
            <div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
          ))}
        </div>
      ) : !incidents.length ? (
        <EmptyState
          icon={ExclamationTriangleIcon}
          title="No incidents"
          description="No behavior incidents recorded"
        />
      ) : (
        <div className="space-y-2">
          {incidents.map((inc) => (
            <div
              key={inc.id}
              className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-slate-900 dark:text-white">
                    {inc.incident_type_display}
                  </p>
                  <p className="text-sm text-slate-500 mt-0.5">{inc.description}</p>
                  <p className="text-xs text-slate-400 mt-1">
                    {dayjs(inc.incident_date).format("MMM D, YYYY")}
                  </p>
                </div>
                <div className="text-right">
                  <Badge
                    color={
                      inc.severity === "high" ? "red" : inc.severity === "medium" ? "amber" : "blue"
                    }
                  >
                    {inc.severity}
                  </Badge>
                  {inc.points_deducted > 0 && (
                    <p className="text-xs text-red-500 mt-1">-{inc.points_deducted} pts</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Points History</h2>
      {pLoading ? (
        <div className="space-y-2">
          {[1, 2].map((i) => (
            <div key={i} className="h-12 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
          ))}
        </div>
      ) : !points.length ? (
        <EmptyState icon={StarIcon} title="No points" description="No behavior points awarded" />
      ) : (
        <div className="space-y-2">
          {points.map((p) => (
            <div
              key={p.id}
              className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3 flex items-center justify-between"
            >
              <div>
                <p className="text-sm font-medium text-slate-900 dark:text-white">{p.reason}</p>
                <p className="text-xs text-slate-400">
                  {p.category} · {dayjs(p.awarded_date).format("MMM D")}
                </p>
              </div>
              <p
                className={`text-lg font-bold ${p.points > 0 ? "text-green-600" : "text-red-600"}`}
              >
                {p.points > 0 ? "+" : ""}
                {p.points}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
