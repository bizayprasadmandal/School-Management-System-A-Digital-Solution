/**
 * Librarian Book Clubs Page — manage book clubs
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { UserGroupIcon, CalendarDaysIcon } from "@heroicons/react/24/outline";

function BookClubSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-32 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function BookClubsPage() {
  const { data: clubs = [], isLoading } = useQuery({
    queryKey: ["librarian-book-clubs"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/library/book-clubs/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Book Clubs</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Manage book clubs and reading groups
          </p>
        </div>
      </div>

      {isLoading ? (
        <BookClubSkeleton />
      ) : clubs.length === 0 ? (
        <EmptyState
          icon={UserGroupIcon}
          title="No book clubs"
          description="Create book clubs to encourage reading among students."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {clubs.map((club: any) => (
            <div
              key={club.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <h3 className="font-semibold text-slate-900 dark:text-white">{club.name}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Reading: {club.book_title ?? "—"}
              </p>
              <p className="mt-1 text-xs text-slate-400">{club.description ?? "—"}</p>
              <div className="mt-3 flex items-center gap-3">
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <CalendarDaysIcon className="h-3.5 w-3.5" />
                  {club.meeting_day ?? "—"}
                </span>
                <span className="text-xs text-slate-400">{club.members ?? 0} members</span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    club.status === "active"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : club.status === "upcoming"
                        ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                        : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                  }`}
                >
                  {club.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
