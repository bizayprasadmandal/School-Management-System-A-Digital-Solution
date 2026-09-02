/**
 * Student Hostel Page — view room assignment and hostel info
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { HomeIcon, BuildingOffice2Icon, UsersIcon } from "@heroicons/react/24/outline";

function HostelSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[1, 2].map((i) => (
        <div key={i} className="h-40 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function HostelPage() {
  const { data: assignment, isLoading } = useQuery({
    queryKey: ["student-hostel"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/hostel/room-assignments/");
      const results = r.results ?? [];
      return results[0] ?? null;
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Hostel</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          View your room assignment and hostel details
        </p>
      </div>

      {isLoading ? (
        <HostelSkeleton />
      ) : !assignment ? (
        <EmptyState
          icon={HomeIcon}
          title="No room assignment"
          description="You haven't been assigned a hostel room yet."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
                <HomeIcon className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {assignment.room_number ?? "Room"}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {assignment.hostel_name ?? "Hostel"}
                </p>
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Floor</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.floor ?? "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Room Type</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.room_type ?? "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Bed</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.bed_number ?? "—"}
                </span>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/30">
                <UsersIcon className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">Roommates</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {assignment.roommate_count ?? 0} other students
                </p>
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Warden</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.warden_name ?? "—"}
                </span>
              </div>
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
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
