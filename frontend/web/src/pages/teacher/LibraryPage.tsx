/**
 * Teacher Library Page — Browse books, view checkouts, recommend books to students.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { BookOpenIcon, ClockIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface Book {
  id: string;
  title: string;
  author: string;
  isbn: string;
  category_name: string;
  available_copies: number;
  total_copies: number;
}
interface Checkout {
  id: string;
  student_name: string;
  book_title: string;
  checkout_date: string;
  due_date: string;
  return_date: string | null;
}

export default function TeacherLibraryPage() {
  useTitle("Library");
  const [search, setSearch] = useState("");
  const [tab, setTab] = useState<"catalog" | "checkouts">("catalog");

  const { data: books = [], isLoading: bLoading } = useQuery({
    queryKey: ["teacher-lib-catalog", search],
    queryFn: async () => {
      const p = search ? `?search=${encodeURIComponent(search)}` : "";
      const r = await api.get<{ results: Book[] }>(`/library/books/${p}`);
      return r.results ?? [];
    },
  });
  const { data: checkouts = [], isLoading: cLoading } = useQuery({
    queryKey: ["teacher-lib-checkouts"],
    queryFn: async () => {
      const r = await api.get<{ results: Checkout[] }>("/library/checkouts/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Library</h1>
        <p className="text-sm text-slate-500 mt-1">Browse books and view student checkouts</p>
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        <button
          onClick={() => setTab("catalog")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "catalog" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <BookOpenIcon className="h-4 w-4 inline mr-1.5" />
          Catalog
        </button>
        <button
          onClick={() => setTab("checkouts")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "checkouts" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <ClockIcon className="h-4 w-4 inline mr-1.5" />
          Checkouts
        </button>
      </div>

      {tab === "catalog" && (
        <>
          <div className="relative max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search books..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm"
            />
          </div>
          {bLoading ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-28 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
                />
              ))}
            </div>
          ) : !books.length ? (
            <EmptyState icon={BookOpenIcon} title="No books" description="No books found" />
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {books.map((b) => (
                <div
                  key={b.id}
                  className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-all"
                >
                  <p className="font-semibold text-slate-900 dark:text-white">{b.title}</p>
                  <p className="text-sm text-slate-500">{b.author}</p>
                  <div className="flex gap-2 mt-2">
                    <Badge color={b.available_copies > 0 ? "green" : "red"}>
                      {b.available_copies > 0 ? `${b.available_copies} available` : "Unavailable"}
                    </Badge>
                    {b.category_name && <Badge color="slate">{b.category_name}</Badge>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {tab === "checkouts" &&
        (cLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !checkouts.length ? (
          <EmptyState icon={ClockIcon} title="No checkouts" description="No active checkouts" />
        ) : (
          <div className="space-y-2">
            {checkouts.map((c) => (
              <div
                key={c.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{c.book_title}</p>
                    <p className="text-xs text-slate-400">
                      {c.student_name} · Due: {dayjs(c.due_date).format("MMM D")}
                    </p>
                  </div>
                  <Badge
                    color={
                      c.return_date ? "green" : dayjs(c.due_date).isBefore(dayjs()) ? "red" : "blue"
                    }
                  >
                    {c.return_date
                      ? "Returned"
                      : dayjs(c.due_date).isBefore(dayjs())
                        ? "Overdue"
                        : "Active"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        ))}
    </div>
  );
}
