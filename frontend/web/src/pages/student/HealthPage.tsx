/**
 * Student Health Page — the student's own health records (read-only).
 *
 * Backend: GET /health/records/ (self-scoped server-side for students).
 * Records are maintained by the school nurse/clinic; students view their own.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { api } from "../../api/client";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Pagination } from "../../components/common";
import { InfiniteScroll } from "../../components/common/InfiniteScroll";
import {
  HeartIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface HealthRecord {
  id: string;
  blood_type: string;
  height_cm: number | null;
  weight_kg: number | null;
  allergies: string;
  chronic_conditions: string;
  medications: string;
  updated_at: string;
}

function HealthSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="relative h-32 overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
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

export default function HealthPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");

  const { data: allRecords = [] as HealthRecord[], isLoading } = useQuery({
    queryKey: ["student-health-records"],
    queryFn: async () => {
      const r = await api.get<{ results: HealthRecord[] }>("/health/records/");
      return r.results ?? ([] as HealthRecord[]);
    },
    refetchInterval: 60000,
  });

  const [infinitePage, setInfinitePage] = useState(1);
  const PAGE_SIZE = 12;
  const infiniteItems = allRecords.slice(0, infinitePage * PAGE_SIZE);
  const infiniteHasMore = infiniteItems.length < allRecords.length;

  const records = React.useMemo(() => {
    if (!search.trim()) return allRecords;
    const q = search.toLowerCase();
    return allRecords.filter(
      (r) =>
        r.allergies?.toLowerCase().includes(q) ||
        r.chronic_conditions?.toLowerCase().includes(q) ||
        r.medications?.toLowerCase().includes(q) ||
        r.blood_type?.toLowerCase().includes(q),
    );
  }, [allRecords, search]);

  const paginatedRecords = React.useMemo(() => {
    const start = (page - 1) * 12;
    return records.slice(start, start + 12);
  }, [records, page]);

  const totalPages = Math.ceil(records.length / 12);

  const handleExport = () => {
    const cols = [
      { key: "blood_type", label: "Blood Type" },
      { key: "height_cm", label: "Height (cm)" },
      { key: "weight_kg", label: "Weight (kg)" },
      { key: "allergies", label: "Allergies" },
      { key: "medications", label: "Medications" },
    ];
    const rows = records.map((row) => ({
      blood_type: row.blood_type ?? "",
      height_cm: row.height_cm ?? "",
      weight_kg: row.weight_kg ?? "",
      allergies: row.allergies ?? "",
      medications: row.medications ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "health-records-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">My Health</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Your health record on file with the school clinic
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

      {/* Search */}
      <div className="rounded-xl border border-slate-100 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search allergies, medications, conditions..."
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
        <HealthSkeleton />
      ) : records.length === 0 ? (
        <EmptyState
          icon={HeartIcon}
          title="No health records"
          description="Your health record will appear here once added by the school nurse."
        />
      ) : viewMode === "infinite" ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {infiniteItems.map((record: HealthRecord) => (
            <RecordCard key={record.id} record={record} />
          ))}
          {infiniteHasMore && (
            <Button variant="secondary" onClick={() => setInfinitePage((p) => p + 1)}>
              Load more
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {paginatedRecords.map((record) => (
            <RecordCard key={record.id} record={record} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {viewMode === "pagination" && totalPages > 1 && (
        <Pagination page={page} total={records.length} pageSize={12} onChange={setPage} />
      )}
    </div>
  );
}

function RecordCard({ record }: { record: HealthRecord }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800">
      <div className="mb-2 flex items-start justify-between">
        <h3 className="font-semibold text-slate-900 dark:text-white">
          {record.blood_type ? `Blood type ${record.blood_type}` : "Health Record"}
        </h3>
        {record.blood_type && (
          <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
            {record.blood_type}
          </span>
        )}
      </div>
      <div className="space-y-1 text-sm text-slate-500 dark:text-slate-400">
        {(record.height_cm != null || record.weight_kg != null) && (
          <p>
            {record.height_cm != null ? `${record.height_cm} cm` : ""}
            {record.height_cm != null && record.weight_kg != null ? " · " : ""}
            {record.weight_kg != null ? `${record.weight_kg} kg` : ""}
          </p>
        )}
        {record.allergies && (
          <p>
            <span className="font-medium text-slate-700 dark:text-slate-300">Allergies:</span>{" "}
            {record.allergies}
          </p>
        )}
        {record.chronic_conditions && (
          <p>
            <span className="font-medium text-slate-700 dark:text-slate-300">Conditions:</span>{" "}
            {record.chronic_conditions}
          </p>
        )}
        {record.medications && (
          <p>
            <span className="font-medium text-slate-700 dark:text-slate-300">Medications:</span>{" "}
            {record.medications}
          </p>
        )}
      </div>
      <div className="mt-3 flex items-center gap-1 text-xs text-slate-400">
        Last updated: {record.updated_at ? dayjs(record.updated_at).format("MMM D, YYYY") : "—"}
      </div>
    </div>
  );
}
