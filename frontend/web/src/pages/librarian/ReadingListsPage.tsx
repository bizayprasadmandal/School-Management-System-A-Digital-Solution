/**
 * Librarian Reading Lists Page — curated reading lists by grade
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { ListBulletIcon } from "@heroicons/react/24/outline";

function ReadingListSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function ReadingListsPage() {
  const { data: lists = [], isLoading } = useQuery({
    queryKey: ["librarian-reading-lists"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/library/reading-lists/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Reading Lists</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Curated reading lists for different grade levels
          </p>
        </div>
      </div>

      {isLoading ? (
        <ReadingListSkeleton />
      ) : lists.length === 0 ? (
        <EmptyState
          icon={ListBulletIcon}
          title="No reading lists"
          description="Create curated reading lists for different grade levels."
        />
      ) : (
        <div className="space-y-3">
          {lists.map((list: any) => (
            <div
              key={list.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">{list.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {list.description ?? "—"}
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  Grade: {list.grade_level ?? "—"} · {list.books_count ?? 0} books · Assigned to{" "}
                  {list.assigned_to ?? 0} students
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
