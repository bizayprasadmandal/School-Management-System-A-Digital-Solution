/**
 * Student Hostel Page — the student's own room assignment (read-only).
 *
 * Backend: GET /hostel/allocations/ (self-scoped server-side for students;
 * serializer exposes room_number, hostel_name, floor, room_type, warden_name).
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { api } from "../../api/client";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Pagination } from "../../components/common";
import {
  HomeIcon,
  UsersIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface RoomAssignment {
  id: string;
  room_number: string;
  hostel_name: string;
  floor: string;
  room_type: string;
  room_type_display: string;
  warden_name: string | null;
  status: string;
  check_in_date: string | null;
  check_out_date: string | null;
  fee_amount: string | null;
  is_paid: boolean | null;
}

function HostelSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[1, 2].map((i) => (
        <div
          key={i}
          className="relative h-40 overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
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

export default function HostelPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");

  const { data: assignments = [] as RoomAssignment[], isLoading } = useQuery({
    queryKey: ["student-hostel"],
    queryFn: async () => {
      const r = await api.get<{ results: RoomAssignment[] }>("/hostel/allocations/");
      return r.results ?? ([] as RoomAssignment[]);
    },
  });

  const [infinitePage, setInfinitePage] = useState(1);
  const PAGE_SIZE = 12;
  const infiniteItems = assignments.slice(0, infinitePage * PAGE_SIZE);
  const infiniteHasMore = infiniteItems.length < assignments.length;

  const assignment = assignments[0] ?? null;

  const filtered = React.useMemo(() => {
    if (!search.trim()) return assignments;
    const q = search.toLowerCase();
    return assignments.filter(
      (a) =>
        a.room_number?.toLowerCase().includes(q) ||
        a.hostel_name?.toLowerCase().includes(q) ||
        a.floor?.toLowerCase().includes(q),
    );
  }, [assignments, search]);

  const paginatedAssignments = React.useMemo(() => {
    const start = (page - 1) * 12;
    return filtered.slice(start, start + 12);
  }, [filtered, page]);

  const totalPages = Math.ceil(filtered.length / 12);

  const handleExport = () => {
    const cols = [
      { key: "hostel", label: "Hostel" },
      { key: "room", label: "Room" },
      { key: "floor", label: "Floor" },
      { key: "status", label: "Status" },
    ];
    const rows = filtered.map((row) => ({
      hostel: row.hostel_name ?? "",
      room: row.room_number ?? "",
      floor: row.floor ?? "",
      status: row.status ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "hostel-assignments-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Hostel</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Your room assignment and hostel details
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
            placeholder="Search by room number, hostel, or floor..."
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
        <HostelSkeleton />
      ) : !assignment ? (
        <EmptyState
          icon={HomeIcon}
          title="No room assignment"
          description="You haven't been assigned a hostel room yet."
        />
      ) : viewMode === "infinite" ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {infiniteItems.map((a) => (
            <AssignmentCard key={a.id} assignment={a} />
          ))}
          {infiniteHasMore && (
            <Button variant="secondary" onClick={() => setInfinitePage((p) => p + 1)}>
              Load more
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {paginatedAssignments.map((a) => (
            <AssignmentCard key={a.id} assignment={a} />
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

function AssignmentCard({ assignment }: { assignment: RoomAssignment }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 sm:col-span-2">
      <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
            <HomeIcon className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 dark:text-white">
              Room {assignment.room_number || "—"}
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {assignment.hostel_name || "—"}
            </p>
          </div>
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-500 dark:text-slate-400">Floor</span>
            <span className="font-medium text-slate-900 dark:text-white">
              {assignment.floor || "—"}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500 dark:text-slate-400">Room Type</span>
            <span className="font-medium text-slate-900 dark:text-white">
              {assignment.room_type_display || assignment.room_type || "—"}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500 dark:text-slate-400">Check-in</span>
            <span className="font-medium text-slate-900 dark:text-white">
              {assignment.check_in_date
                ? dayjs(assignment.check_in_date).format("MMM D, YYYY")
                : "—"}
            </span>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/30">
            <UsersIcon className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 dark:text-white">Hostel Info</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">Warden & stay details</p>
          </div>
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-500 dark:text-slate-400">Warden</span>
            <span className="font-medium text-slate-900 dark:text-white">
              {assignment.warden_name || "—"}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-500 dark:text-slate-400">Status</span>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                assignment.status === "active"
                  ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                  : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
              }`}
            >
              {assignment.status || "—"}
            </span>
          </div>
          {assignment.fee_amount != null && (
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Fee</span>
              <span className="font-medium text-slate-900 dark:text-white">
                ${assignment.fee_amount}
                {assignment.is_paid === false && (
                  <span className="ml-1 rounded-full bg-red-100 px-1.5 py-0.5 text-xs font-medium text-red-700 dark:bg-red-900/30 dark:text-red-400">
                    unpaid
                  </span>
                )}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
