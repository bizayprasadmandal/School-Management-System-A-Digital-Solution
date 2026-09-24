/**
 * Student Behavior Page — the student's own behavior points (read-only).
 *
 * Backend: GET /behavior/points/ (self-scoped server-side for students).
 * Points are awarded by staff; students view their own history and balance.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { api } from "../../api/client";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Pagination } from "../../components/common";
import { InfiniteScroll } from "../../components/common/InfiniteScroll";
import {
  CheckCircleIcon,
  XCircleIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface BehaviorPoint {
  id: string;
  points: number;
  reason: string;
  point_type_display: string;
  category_name: string | null;
  awarded_by_name: string | null;
  created_at: string;
}

function StatSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800"
        >
          <div
            className="mb-2 h-4 w-24 animate-shimmer rounded bg-slate-200 dark:bg-slate-700"
            style={{ backgroundSize: "200% 100%" }}
          />
          <div
            className="h-8 w-16 animate-shimmer rounded bg-slate-200 dark:bg-slate-700"
            style={{ backgroundSize: "200% 100%" }}
          />
        </div>
      ))}
    </div>
  );
}

function ListSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="relative h-20 overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
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

export default function BehaviorPage() {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");

  const { data: points = [] as BehaviorPoint[], isLoading } = useQuery({
    queryKey: ["student-behavior-points"],
    queryFn: async () => {
      const r = await api.get<{ results: BehaviorPoint[] }>("/behavior/points/");
      return r.results ?? ([] as BehaviorPoint[]);
    },
    refetchInterval: 60000,
  });

  const [infinitePage, setInfinitePage] = useState(1);
  const PAGE_SIZE = 12;
  const infiniteItems = points.slice(0, infinitePage * PAGE_SIZE);
  const infiniteHasMore = infiniteItems.length < points.length;

  const filtered = React.useMemo<BehaviorPoint[]>(() => {
    let items: BehaviorPoint[] = points;
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(
        (r) =>
          r.reason?.toLowerCase().includes(q) ||
          r.category_name?.toLowerCase().includes(q),
      );
    }
    if (typeFilter === "positive") items = items.filter((r) => r.points > 0);
    if (typeFilter === "negative") items = items.filter((r) => r.points < 0);
    return items;
  }, [points, search, typeFilter]);

  const totalPoints = points.reduce((sum, r) => sum + (r.points ?? 0), 0);

  const paginated = React.useMemo(() => {
    const start = (page - 1) * 12;
    return filtered.slice(start, start + 12);
  }, [filtered, page]);

  const totalPages = Math.ceil(filtered.length / 12);

  const handleExport = () => {
    const cols = [
      { key: "date", label: "Date" },
      { key: "points", label: "Points" },
      { key: "reason", label: "Reason" },
      { key: "awarded_by", label: "Awarded By" },
    ];
    const rows = filtered.map((row) => ({
      date: row.created_at ? dayjs(row.created_at).format("YYYY-MM-DD") : "",
      points: row.points ?? "",
      reason: row.reason ?? "",
      awarded_by: row.awarded_by_name ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "behavior-points-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Behavior Points</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Your behavior record and points history
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

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-sm text-slate-500 dark:text-slate-400">Total Points</p>
          <p
            className={`text-2xl font-bold ${
              totalPoints >= 0
                ? "text-green-600 dark:text-green-400"
                : "text-red-600 dark:text-red-400"
            }`}
          >
            {totalPoints}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-sm text-slate-500 dark:text-slate-400">Positive Awards</p>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">
            {points.filter((r) => r.points > 0).length}
          </p>
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-sm text-slate-500 dark:text-slate-400">Negative Marks</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">
            {points.filter((r) => r.points < 0).length}
          </p>
        </div>
      </div>

      {/* Search + Filters */}
      <div className="space-y-3 rounded-xl border border-slate-100 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              placeholder="Search points history..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-400"
            />
          </div>
          <select
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value);
              setPage(1);
            }}
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-700 dark:text-white"
          >
            <option value="all">All Types</option>
            <option value="positive">Positive</option>
            <option value="negative">Negative</option>
          </select>
          {(search || typeFilter !== "all") && (
            <button
              onClick={() => {
                setSearch("");
                setTypeFilter("all");
              }}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-400 dark:hover:bg-slate-700"
              aria-label="Clear filters"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {isLoading ? (
        <>
          <StatSkeleton />
          <ListSkeleton />
        </>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={CheckCircleIcon}
          title="No behavior points yet"
          description="Points awarded by your teachers will appear here."
        />
      ) : viewMode === "infinite" ? (
        <InfiniteScroll
          items={infiniteItems}
          hasMore={infiniteHasMore}
          isLoading={isLoading}
          isFetchingNext={false}
          onLoadMore={() => setInfinitePage((p) => p + 1)}
          renderItem={(record: BehaviorPoint) => <PointRow record={record} />}
        />
      ) : (
        <div className="space-y-3">
          {paginated.map((record) => (
            <PointRow key={record.id} record={record} />
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

function PointRow({ record }: { record: BehaviorPoint }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800">
      <div className="flex items-center gap-3">
        {record.points > 0 ? (
          <CheckCircleIcon className="h-5 w-5 text-green-500" />
        ) : (
          <XCircleIcon className="h-5 w-5 text-red-500" />
        )}
        <div>
          <p className="font-medium text-slate-900 dark:text-white">
            {record.reason || record.point_type_display || "Point award"}
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {record.category_name ? record.category_name + " · " : ""}
            {record.awarded_by_name ? "by " + record.awarded_by_name + " · " : ""}
            {record.created_at ? dayjs(record.created_at).format("MMM D, YYYY") : ""}
          </p>
        </div>
      </div>
      <span
        className={`text-sm font-semibold ${
          record.points > 0
            ? "text-green-600 dark:text-green-400"
            : "text-red-600 dark:text-red-400"
        }`}
      >
        {record.points > 0 ? "+" : ""}
        {record.points}
      </span>
    </div>
  );
}
