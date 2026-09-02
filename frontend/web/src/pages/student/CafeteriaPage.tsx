/**
 * Student Cafeteria Page — view menus, book meals
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { CakeIcon, CalendarDaysIcon } from "@heroicons/react/24/outline";

function CafeteriaSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="h-28 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function CafeteriaPage() {
  const { data: menus = [], isLoading } = useQuery({
    queryKey: ["student-cafeteria-menus"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/cafeteria/daily-menus/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Cafeteria</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          View daily menus and book your meals
        </p>
      </div>

      {isLoading ? (
        <CafeteriaSkeleton />
      ) : menus.length === 0 ? (
        <EmptyState
          icon={CakeIcon}
          title="No menus available"
          description="Daily menus will appear here once published."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {menus.map((menu: any) => (
            <div
              key={menu.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">
                    {menu.title ?? "Daily Menu"}
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {menu.description ?? "—"}
                  </p>
                </div>
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <CalendarDaysIcon className="h-3.5 w-3.5" />
                  {menu.date ?? "—"}
                </span>
              </div>
              <div className="mt-3 flex items-center gap-2">
                <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
                  ${menu.price ?? "0.00"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
