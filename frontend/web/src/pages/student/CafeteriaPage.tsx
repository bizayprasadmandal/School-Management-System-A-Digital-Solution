/**
 * Student Cafeteria Page — daily menus (read-only) plus the student's own
 * meal pre-orders.
 *
 * Backend: GET /cafeteria/menus/ (school menus), GET /cafeteria/pre-orders/
 * (self-scoped server-side for students).
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { api } from "../../api/client";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Pagination } from "../../components/common";
import { InfiniteScroll } from "../../components/common/InfiniteScroll";
import {
  CakeIcon,
  CalendarDaysIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface MenuItem {
  id: string;
  name: string;
  description: string;
  meal_type: string;
  date: string;
  price: string;
  items: string;
  calories: number | null;
  is_vegetarian: boolean;
}

interface PreOrder {
  id: string;
  meal_date: string;
  meal_type: string;
  menu_items: string;
  total_amount: string;
  status: string;
}

function MenuSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[1, 2, 3, 4].map((i) => (
        <div
          key={i}
          className="relative h-28 overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
        >
          <div
            className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-slate-200/50 to-transparent dark:via-slate-600/30"
            style={{ backgroundSize: "200% 100%" }}
          />
        </div>
      ))}
    </div>
  );
}

const MEAL_TYPE_LABELS: Record<string, string> = {
  breakfast: "Breakfast",
  lunch: "Lunch",
  dinner: "Dinner",
  snack: "Snack",
};

export default function CafeteriaPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");

  const { data: menus = [] as MenuItem[], isLoading } = useQuery({
    queryKey: ["student-cafeteria-menus"],
    queryFn: async () => {
      const r = await api.get<{ results: MenuItem[] }>("/cafeteria/menus/");
      return r.results ?? ([] as MenuItem[]);
    },
  });

  const { data: preOrders = [] as PreOrder[] } = useQuery({
    queryKey: ["student-cafeteria-preorders"],
    queryFn: async () => {
      const r = await api.get<{ results: PreOrder[] }>("/cafeteria/pre-orders/");
      return r.results ?? ([] as PreOrder[]);
    },
  });

  const [infinitePage, setInfinitePage] = useState(1);
  const PAGE_SIZE = 12;
  const infiniteItems = menus.slice(0, infinitePage * PAGE_SIZE);
  const infiniteHasMore = infiniteItems.length < menus.length;

  const filtered = React.useMemo(() => {
    if (!search.trim()) return menus;
    const q = search.toLowerCase();
    return menus.filter(
      (m) =>
        m.name?.toLowerCase().includes(q) ||
        m.description?.toLowerCase().includes(q) ||
        m.items?.toLowerCase().includes(q),
    );
  }, [menus, search]);

  const paginatedMenus = React.useMemo(() => {
    const start = (page - 1) * 12;
    return filtered.slice(start, start + 12);
  }, [filtered, page]);

  const totalPages = Math.ceil(filtered.length / 12);

  const handleExport = () => {
    const cols = [
      { key: "date", label: "Date" },
      { key: "meal_type", label: "Meal" },
      { key: "name", label: "Menu" },
      { key: "price", label: "Price" },
    ];
    const rows = filtered.map((row) => ({
      date: row.date ?? "",
      meal_type: MEAL_TYPE_LABELS[row.meal_type] ?? row.meal_type ?? "",
      name: row.name ?? "",
      price: row.price ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "cafeteria-menus-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Cafeteria</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Daily menus and your meal pre-orders
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 rounded-lg border border-slate-200 p-0.5 dark:border-slate-700">
            <button
              onClick={() => setViewMode("pagination")}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                viewMode === "pagination"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
              }`}
            >
              Pages
            </button>
            <button
              onClick={() => setViewMode("infinite")}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                viewMode === "infinite"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
              }`}
            >
              Scroll
            </button>
          </div>
          <Button
            variant="secondary"
            leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
            onClick={handleExport}
          >
            Export CSV
          </Button>
        </div>
      </div>

      {/* My pre-orders */}
      {preOrders.length > 0 && (
        <div>
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
            My Meal Orders
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {preOrders.slice(0, 6).map((o) => (
              <div
                key={o.id}
                className="flex items-center justify-between rounded-xl border border-indigo-100 bg-indigo-50/50 p-3 dark:border-indigo-900/40 dark:bg-indigo-900/20"
              >
                <div>
                  <p className="text-sm font-medium text-slate-900 dark:text-white">
                    {o.menu_items || MEAL_TYPE_LABELS[o.meal_type] || o.meal_type}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {o.meal_date ? dayjs(o.meal_date).format("MMM D, YYYY") : ""}
                  </p>
                </div>
                <span className="rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300">
                  {o.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Search */}
      <div className="rounded-xl border border-slate-100 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search meals..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-400"
          />
        </div>
      </div>

      {isLoading ? (
        <MenuSkeleton />
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={CakeIcon}
          title="No menus available"
          description="Daily menus will appear here once published."
        />
      ) : viewMode === "infinite" ? (
        <InfiniteScroll
          items={infiniteItems}
          hasMore={infiniteHasMore}
          isLoading={isLoading}
          isFetchingNext={false}
          onLoadMore={() => setInfinitePage((p) => p + 1)}
          renderItem={(menu: MenuItem) => <MenuCard menu={menu} />}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {paginatedMenus.map((menu) => (
            <MenuCard key={menu.id} menu={menu} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {viewMode === "pagination" && totalPages > 1 && (
        <Pagination page={page} total={filtered.length} pageSize={12} onChange={setPage} />
      )}
    </div>
  );
}

function MenuCard({ menu }: { menu: MenuItem }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800">
      <div className="mb-2 flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-slate-900 dark:text-white">{menu.name}</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">{menu.description || "—"}</p>
        </div>
        <span className="rounded-full bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300">
          {MEAL_TYPE_LABELS[menu.meal_type] ?? menu.meal_type}
        </span>
      </div>
      {menu.items && (
        <p className="mb-2 text-xs text-slate-500 dark:text-slate-400">{menu.items}</p>
      )}
      <div className="flex flex-wrap items-center gap-3">
        <span className="flex items-center gap-1 text-xs text-slate-400">
          <CalendarDaysIcon className="h-3.5 w-3.5" />
          {menu.date ? dayjs(menu.date).format("MMM D, YYYY") : "—"}
        </span>
        <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
          ${menu.price || "0.00"}
        </span>
        {menu.is_vegetarian && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
            Veg
          </span>
        )}
        {menu.calories != null && (
          <span className="text-xs text-slate-400">{menu.calories} kcal</span>
        )}
      </div>
    </div>
  );
}
