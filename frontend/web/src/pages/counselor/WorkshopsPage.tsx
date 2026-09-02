/**
 * Counselor Workshops Page — schedule and manage workshops
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { AcademicCapIcon, CalendarDaysIcon } from "@heroicons/react/24/outline";

function WorkshopSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function WorkshopsPage() {
  const { data: workshops = [], isLoading } = useQuery({
    queryKey: ["counselor-workshops"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/counseling/workshops/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Workshops</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Schedule and manage student development workshops
          </p>
        </div>
      </div>

      {isLoading ? (
        <WorkshopSkeleton />
      ) : workshops.length === 0 ? (
        <EmptyState
          icon={AcademicCapIcon}
          title="No workshops"
          description="Schedule workshops for student development."
        />
      ) : (
        <div className="space-y-3">
          {workshops.map((ws: any) => (
            <div
              key={ws.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">{ws.title}</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {ws.description ?? "—"}
                  </p>
                  <div className="mt-1 flex items-center gap-3">
                    <span className="flex items-center gap-1 text-xs text-slate-400">
                      <CalendarDaysIcon className="h-3.5 w-3.5" />
                      {ws.date ? new Date(ws.date).toLocaleDateString() : "—"}
                    </span>
                    <span className="text-xs text-slate-400">{ws.facilitator ?? "—"}</span>
                  </div>
                </div>
                <span className="text-sm text-slate-500 dark:text-slate-400">
                  {ws.attendees ?? 0}/{ws.max_attendees ?? "∞"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
