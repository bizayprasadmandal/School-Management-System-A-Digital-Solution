/**
 * Student Transport Page — view route assignment and bus info
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { TruckIcon, MapPinIcon, ClockIcon } from "@heroicons/react/24/outline";

function TransportSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[1, 2].map((i) => (
        <div key={i} className="h-40 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function TransportPage() {
  const { data: assignment, isLoading } = useQuery({
    queryKey: ["student-transport"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/transportation/route-assignments/");
      const results = r.results ?? [];
      return results[0] ?? null;
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Transportation</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          View your bus route and transport details
        </p>
      </div>

      {isLoading ? (
        <TransportSkeleton />
      ) : !assignment ? (
        <EmptyState
          icon={TruckIcon}
          title="No transport assignment"
          description="You haven't been assigned a transport route yet."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30">
                <TruckIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {assignment.route_name ?? "Route"}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {assignment.bus_number ?? "Bus"}
                </p>
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Driver</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.driver_name ?? "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Pickup Time</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.pickup_time ?? "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Drop-off Time</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.dropoff_time ?? "—"}
                </span>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/30">
                <MapPinIcon className="h-5 w-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">Stops</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {assignment.stop_name ?? "Your stop"}
                </p>
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Status</span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    assignment.status === "active"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                  }`}
                >
                  {assignment.status ?? "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Capacity</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.capacity ?? "—"}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
