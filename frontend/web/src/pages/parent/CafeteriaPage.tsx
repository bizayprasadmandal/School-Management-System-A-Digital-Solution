/**
 * Parent Cafeteria Page — View menus and child meal bookings.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { BookOpenIcon, CalendarDaysIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface MealMenu {
  id: string;
  name: string;
  date: string;
  meal_type_display: string;
  items: string;
  price: number;
}
interface MealBooking {
  id: string;
  student_name: string;
  menu_name: string;
  meal_type_display: string;
  status_display: string;
  booking_date: string;
}

export default function ParentCafeteriaPage() {
  useTitle("Cafeteria");
  const [tab, setTab] = useState<"menus" | "bookings">("menus");
  const { data: menus = [], isLoading: mLoading } = useQuery({
    queryKey: ["parent-cafe-menus"],
    queryFn: async () => {
      const r = await api.get<{ results: MealMenu[] }>("/cafeteria/menus/");
      return r.results ?? [];
    },
  });
  const { data: bookings = [], isLoading: bLoading } = useQuery({
    queryKey: ["parent-cafe-bookings"],
    queryFn: async () => {
      const r = await api.get<{ results: MealBooking[] }>("/cafeteria/bookings/children/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Cafeteria</h1>
        <p className="text-sm text-slate-500 mt-1">
          View menus and your children&apos;s meal bookings
        </p>
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        <button
          onClick={() => setTab("menus")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "menus" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <BookOpenIcon className="h-4 w-4 inline mr-1.5" />
          Menus
        </button>
        <button
          onClick={() => setTab("bookings")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "bookings" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <CalendarDaysIcon className="h-4 w-4 inline mr-1.5" />
          Bookings
        </button>
      </div>
      {tab === "menus" && <MenuList menus={menus} isLoading={mLoading} />}
      {tab === "bookings" && <BookingList bookings={bookings} isLoading={bLoading} />}
    </div>
  );
}

function MenuList({ menus, isLoading }: { menus: MealMenu[]; isLoading: boolean }) {
  if (isLoading)
    return (
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-28 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  if (!menus.length) return <EmptyState icon={BookOpenIcon} title="No menus" />;
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {menus.map((m) => (
        <div
          key={m.id}
          className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
        >
          <p className="font-semibold text-slate-900 dark:text-white">{m.name}</p>
          <p className="text-xs text-slate-400">
            {dayjs(m.date).format("MMM D")} · ${Number(m.price).toFixed(2)}
          </p>
          <Badge color="indigo">{m.meal_type_display}</Badge>
          {m.items && <p className="text-xs text-slate-500 mt-2">🍽️ {m.items}</p>}
        </div>
      ))}
    </div>
  );
}

function BookingList({ bookings, isLoading }: { bookings: MealBooking[]; isLoading: boolean }) {
  if (isLoading)
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  if (!bookings.length) return <EmptyState icon={CalendarDaysIcon} title="No bookings" />;
  return (
    <div className="space-y-2">
      {bookings.map((b) => (
        <div
          key={b.id}
          className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold text-slate-900 dark:text-white">{b.student_name}</p>
              <p className="text-xs text-slate-400">
                {b.menu_name} · {dayjs(b.booking_date).format("MMM D")}
              </p>
            </div>
            <Badge color="green">{b.status_display}</Badge>
          </div>
        </div>
      ))}
    </div>
  );
}
