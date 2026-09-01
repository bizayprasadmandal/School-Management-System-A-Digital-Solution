/**
 * Student Library Page — Browse books, view checkouts, and fines.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import {
  BookOpenIcon,
  ClockIcon,
  BanknotesIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, SkeletonCard, Badge } from "../../components/common";
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
  book_title: string;
  checkout_date: string;
  due_date: string;
  return_date: string | null;
  status_display: string;
  fine_amount: string;
}
interface Fine {
  id: string;
  checkout_book_title: string;
  amount: string;
  reason: string;
  is_paid: boolean;
  created_at: string;
}

type Tab = "catalog" | "checkouts" | "fines";
const TABS: { key: Tab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "catalog", label: "Book Catalog", icon: BookOpenIcon },
  { key: "checkouts", label: "My Checkouts", icon: ClockIcon },
  { key: "fines", label: "Fines", icon: BanknotesIcon },
];

export default function StudentLibraryPage() {
  useTitle("Library");
  const [tab, setTab] = useState<Tab>("catalog");
  const [search, setSearch] = useState("");

  const { data: books = [], isLoading: bLoading } = useQuery({
    queryKey: ["student-library-catalog", search],
    queryFn: async () => {
      const params = search ? `?search=${encodeURIComponent(search)}` : "";
      const r = await api.get<{ results: Book[] }>(`/library/books/${params}`);
      return r.results ?? [];
    },
  });

  const { data: checkouts = [], isLoading: cLoading } = useQuery({
    queryKey: ["student-library-checkouts"],
    queryFn: async () => {
      const r = await api.get<{ results: Checkout[] }>("/library/checkouts/my/");
      return r.results ?? [];
    },
  });

  const { data: fines = [], isLoading: fLoading } = useQuery({
    queryKey: ["student-library-fines"],
    queryFn: async () => {
      const r = await api.get<{ results: Fine[] }>("/library/fines/my/");
      return r.results ?? [];
    },
  });

  const totalFines = fines.filter((f) => !f.is_paid).reduce((sum, f) => sum + Number(f.amount), 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Library</h1>
        <p className="text-sm text-slate-500 mt-1">
          Browse books, view checkouts, and manage fines
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard
          label="Available Books"
          value={books.filter((b) => b.available_copies > 0).length}
          icon={BookOpenIcon}
          color="indigo"
        />
        <StatCard
          label="My Checkouts"
          value={checkouts.filter((c) => !c.return_date).length}
          icon={ClockIcon}
          color="amber"
        />
        <StatCard
          label="Outstanding Fines"
          value={`$${totalFines.toFixed(2)}`}
          icon={BanknotesIcon}
          color="red"
        />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
        {TABS.map((t) => {
          const I = t.icon;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
                tab === t.key
                  ? "bg-white dark:bg-slate-700 shadow-sm text-slate-900 dark:text-white"
                  : "text-slate-600 hover:text-slate-900 dark:text-slate-400"
              }`}
            >
              <I className="h-4 w-4" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Catalog Tab */}
      {tab === "catalog" && (
        <>
          <div className="relative max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search books by title, author, or ISBN..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm"
            />
          </div>
          {bLoading ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-32 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
                />
              ))}
            </div>
          ) : !books.length ? (
            <EmptyState
              icon={BookOpenIcon}
              title="No books found"
              description="Try a different search term"
            />
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {books.map((b) => (
                <div
                  key={b.id}
                  className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-all"
                >
                  <p className="font-semibold text-slate-900 dark:text-white">{b.title}</p>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">{b.author}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge color={b.available_copies > 0 ? "green" : "red"}>
                      {b.available_copies > 0 ? `${b.available_copies} available` : "Unavailable"}
                    </Badge>
                    {b.category_name && <Badge color="slate">{b.category_name}</Badge>}
                  </div>
                  {b.isbn && <p className="text-xs text-slate-400 mt-2">ISBN: {b.isbn}</p>}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Checkouts Tab */}
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
          <EmptyState
            icon={ClockIcon}
            title="No checkouts"
            description="You have no book checkouts"
          />
        ) : (
          <div className="space-y-2">
            {checkouts.map((c) => (
              <div
                key={c.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{c.book_title}</p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Checked out: {dayjs(c.checkout_date).format("MMM D")} · Due:{" "}
                      {dayjs(c.due_date).format("MMM D, YYYY")}
                    </p>
                    {c.return_date && (
                      <p className="text-xs text-green-600 mt-0.5">
                        Returned: {dayjs(c.return_date).format("MMM D, YYYY")}
                      </p>
                    )}
                  </div>
                  <Badge
                    color={
                      c.return_date ? "green" : dayjs(c.due_date).isBefore(dayjs()) ? "red" : "blue"
                    }
                  >
                    {c.status_display}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        ))}

      {/* Fines Tab */}
      {tab === "fines" &&
        (fLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !fines.length ? (
          <EmptyState
            icon={BanknotesIcon}
            title="No fines"
            description="You have no outstanding fines"
          />
        ) : (
          <div className="space-y-2">
            {fines.map((f) => (
              <div
                key={f.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">
                      {f.checkout_book_title}
                    </p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {f.reason} · {dayjs(f.created_at).format("MMM D, YYYY")}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-red-600 dark:text-red-400">
                      ${Number(f.amount).toFixed(2)}
                    </p>
                    <Badge color={f.is_paid ? "green" : "red"}>
                      {f.is_paid ? "Paid" : "Unpaid"}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}
    </div>
  );
}

function StatCard({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}) {
  const colors: Record<string, string> = {
    indigo: "bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400",
    amber: "bg-amber-50 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400",
    red: "bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400",
  };
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${colors[color]}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
          <p className="text-lg font-bold text-slate-900 dark:text-white">{value}</p>
        </div>
      </div>
    </div>
  );
}
