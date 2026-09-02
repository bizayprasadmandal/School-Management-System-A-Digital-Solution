/**
 * Teacher Library Page — browse catalog and manage checkouts
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { BookOpenIcon, BanknotesIcon } from "@heroicons/react/24/outline";

function LibrarySkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-40 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function LibraryPage() {
  const { data: books = [], isLoading } = useQuery({
    queryKey: ["teacher-library-books"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/library/books/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Library</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Browse the library catalog
        </p>
      </div>

      {isLoading ? (
        <LibrarySkeleton />
      ) : books.length === 0 ? (
        <EmptyState
          icon={BookOpenIcon}
          title="No books available"
          description="The library catalog will appear here once books are added."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {books.map((book: any) => (
            <div
              key={book.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <h3 className="font-semibold text-slate-900 dark:text-white">{book.title}</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {book.author ?? "Unknown author"}
              </p>
              <div className="mt-3 flex items-center gap-3">
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <BookOpenIcon className="h-3.5 w-3.5" />
                  {book.available_copies ?? 0} available
                </span>
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <BanknotesIcon className="h-3.5 w-3.5" />${book.fine_per_day ?? "0.00"}/day
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
