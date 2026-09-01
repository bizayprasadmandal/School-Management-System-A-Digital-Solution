/**
 * Student Cafeteria Page — View menus, meal plans, and make bookings.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  BookOpenIcon,
  CreditCardIcon,
  CalendarDaysIcon,
  NoSymbolIcon,
  PlusIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge, SkeletonCard } from "../../components/common";
import { useTitle } from "../../hooks";

interface MealMenu {
  id: string;
  name: string;
  date: string;
  meal_type: string;
  meal_type_display: string;
  items: string;
  price: number;
  is_vegetarian: boolean;
  is_vegan: boolean;
  is_gluten_free: boolean;
}
interface MealPlan {
  id: string;
  name: string;
  description: string;
  price_per_period: number;
  period_days: number;
  meals_included: string;
  is_active: boolean;
}
interface MealBooking {
  id: string;
  menu_name: string;
  meal_type_display: string;
  status_display: string;
  booking_date: string;
}

type Tab = "menus" | "plans" | "bookings";
const TABS: { key: Tab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "menus", label: "Today's Menu", icon: BookOpenIcon },
  { key: "plans", label: "Meal Plans", icon: CreditCardIcon },
  { key: "bookings", label: "My Bookings", icon: CalendarDaysIcon },
];

export default function StudentCafeteriaPage() {
  useTitle("Cafeteria");
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>("menus");
  const [showBooking, setShowBooking] = useState(false);
  const [selectedMenu, setSelectedMenu] = useState<string>("");

  const { data: menus = [], isLoading: mLoading } = useQuery({
    queryKey: ["student-cafe-menus"],
    queryFn: async () => {
      const r = await api.get<{ results: MealMenu[] }>("/cafeteria/menus/");
      return r.results ?? [];
    },
  });

  const { data: plans = [], isLoading: pLoading } = useQuery({
    queryKey: ["student-cafe-plans"],
    queryFn: async () => {
      const r = await api.get<{ results: MealPlan[] }>("/cafeteria/plans/");
      return r.results ?? [];
    },
  });

  const { data: bookings = [], isLoading: bLoading } = useQuery({
    queryKey: ["student-cafe-bookings"],
    queryFn: async () => {
      const r = await api.get<{ results: MealBooking[] }>("/cafeteria/bookings/my/");
      return r.results ?? [];
    },
  });

  const bookMeal = useMutation({
    mutationFn: (data: { menu: string }) => api.post("/cafeteria/bookings/", data),
    onSuccess: () => {
      toast.success("Meal booked!");
      qc.invalidateQueries({ queryKey: ["student-cafe-bookings"] });
      setShowBooking(false);
    },
    onError: () => toast.error("Failed to book meal"),
  });

  const todayMenus = menus.filter((m) => dayjs(m.date).isSame(dayjs(), "day"));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Cafeteria</h1>
        <p className="text-sm text-slate-500 mt-1">View menus, meal plans, and book meals</p>
      </div>

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

      {tab === "menus" &&
        (mLoading ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-32 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !menus.length ? (
          <EmptyState icon={BookOpenIcon} title="No menus" description="No meal menus available" />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {(todayMenus.length ? todayMenus : menus).map((m) => (
              <div
                key={m.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-all"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{m.name}</p>
                    <p className="text-xs text-slate-400">
                      {dayjs(m.date).format("MMM D, YYYY")} · ${Number(m.price).toFixed(2)}
                    </p>
                  </div>
                  <Badge color="indigo">{m.meal_type_display}</Badge>
                </div>
                {m.items && <p className="text-sm text-slate-500 mb-2">🍽️ {m.items}</p>}
                <div className="flex items-center gap-2 text-xs">
                  {m.is_vegetarian && <span className="text-green-600">🌱 Veg</span>}
                  {m.is_vegan && <span className="text-green-600">🌿 Vegan</span>}
                  {m.is_gluten_free && <span className="text-amber-600">🌾 GF</span>}
                </div>
                <Button
                  size="sm"
                  className="mt-3 w-full"
                  onClick={() => {
                    setSelectedMenu(m.id);
                    setShowBooking(true);
                  }}
                >
                  Book This Meal
                </Button>
              </div>
            ))}
          </div>
        ))}

      {tab === "plans" &&
        (pLoading ? (
          <SkeletonCard />
        ) : !plans.length ? (
          <EmptyState
            icon={CreditCardIcon}
            title="No meal plans"
            description="No meal plans available"
          />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {plans.map((p) => (
              <div
                key={p.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{p.name}</p>
                    <p className="text-lg font-bold text-indigo-600">
                      ${Number(p.price_per_period).toFixed(2)}
                      <span className="text-sm font-normal text-slate-400">
                        /{p.period_days} days
                      </span>
                    </p>
                  </div>
                  <Badge color={p.is_active ? "green" : "slate"}>
                    {p.is_active ? "Available" : "Unavailable"}
                  </Badge>
                </div>
                {p.meals_included && (
                  <p className="text-xs text-slate-400 mt-2">Meals: {p.meals_included}</p>
                )}
                {p.description && <p className="text-sm text-slate-500 mt-1">{p.description}</p>}
              </div>
            ))}
          </div>
        ))}

      {tab === "bookings" &&
        (bLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !bookings.length ? (
          <EmptyState
            icon={CalendarDaysIcon}
            title="No bookings"
            description="Book a meal to see it here"
          />
        ) : (
          <div className="space-y-2">
            {bookings.map((b) => (
              <div
                key={b.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{b.menu_name}</p>
                    <p className="text-xs text-slate-400">
                      {b.meal_type_display} · {dayjs(b.booking_date).format("MMM D, YYYY")}
                    </p>
                  </div>
                  <Badge color="green">{b.status_display}</Badge>
                </div>
              </div>
            ))}
          </div>
        ))}

      <Modal open={showBooking} onClose={() => setShowBooking(false)} title="Book Meal">
        <div className="space-y-4">
          <p className="text-sm text-slate-500">Confirm your meal booking?</p>
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setShowBooking(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => bookMeal.mutate({ menu: selectedMenu })}
              loading={bookMeal.isPending}
            >
              Confirm Booking
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
