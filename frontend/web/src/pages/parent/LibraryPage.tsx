/**
 * Parent Library Page — View child's library checkouts and fines.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { ClockIcon, BanknotesIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface Checkout {
  id: string;
  student_name: string;
  book_title: string;
  due_date: string;
  return_date: string | null;
}
interface Fine {
  id: string;
  checkout_book_title: string;
  amount: string;
  is_paid: boolean;
}

export default function ParentLibraryPage() {
  useTitle("Library");
  const [tab, setTab] = useState<"checkouts" | "fines">("checkouts");
  const { data: checkouts = [], isLoading: cLoading } = useQuery({
    queryKey: ["parent-lib-checkouts"],
    queryFn: async () => {
      const r = await api.get<{ results: Checkout[] }>("/library/checkouts/children/");
      return r.results ?? [];
    },
  });
  const { data: fines = [], isLoading: fLoading } = useQuery({
    queryKey: ["parent-lib-fines"],
    queryFn: async () => {
      const r = await api.get<{ results: Fine[] }>("/library/fines/children/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Library</h1>
        <p className="text-sm text-slate-500 mt-1">Your children&apos;s library activity</p>
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        <button
          onClick={() => setTab("checkouts")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "checkouts" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <ClockIcon className="h-4 w-4 inline mr-1.5" />
          Checkouts
        </button>
        <button
          onClick={() => setTab("fines")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "fines" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <BanknotesIcon className="h-4 w-4 inline mr-1.5" />
          Fines
        </button>
      </div>
      {tab === "checkouts" && <CheckoutList checkouts={checkouts} isLoading={cLoading} />}
      {tab === "fines" && <FineList fines={fines} isLoading={fLoading} />}
    </div>
  );
}

function CheckoutList({ checkouts, isLoading }: { checkouts: Checkout[]; isLoading: boolean }) {
  if (isLoading)
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  if (!checkouts.length) return <EmptyState icon={ClockIcon} title="No checkouts" />;
  return (
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
                {c.student_name} · Due: {dayjs(c.due_date).format("MMM D, YYYY")}
              </p>
            </div>
            <Badge
              color={c.return_date ? "green" : dayjs(c.due_date).isBefore(dayjs()) ? "red" : "blue"}
            >
              {c.return_date ? "Returned" : "Active"}
            </Badge>
          </div>
        </div>
      ))}
    </div>
  );
}

function FineList({ fines, isLoading }: { fines: Fine[]; isLoading: boolean }) {
  if (isLoading)
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  if (!fines.length) return <EmptyState icon={BanknotesIcon} title="No fines" />;
  return (
    <div className="space-y-2">
      {fines.map((f) => (
        <div
          key={f.id}
          className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
        >
          <div className="flex items-center justify-between">
            <p className="font-semibold text-slate-900 dark:text-white">{f.checkout_book_title}</p>
            <div className="text-right">
              <p className="font-bold text-red-600">${Number(f.amount).toFixed(2)}</p>
              <Badge color={f.is_paid ? "green" : "red"}>{f.is_paid ? "Paid" : "Unpaid"}</Badge>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
