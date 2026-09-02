/**
 * Student Hostel Page — view room assignment and hostel info
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import { useKeyboardShortcuts } from "../../hooks/useKeyboardShortcuts";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import { InfiniteScroll } from "../../components/common/InfiniteScroll";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { BulkActionBar } from "../../components/common/BulkActionBar";
import {
  HomeIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  UsersIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface RoomAssignment {
  id: string;
  room_number: string;
  hostel_name: string;
  floor: string;
  room_type: string;
  bed_number: string;
  warden_name: string;
  status: string;
}

function HostelSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[1, 2].map((i) => (
        <div
          key={i}
          className="h-40 relative overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
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
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<RoomAssignment | null>(null);

  const { data: assignments = [], isLoading } = useQuery({
    queryKey: ["student-hostel"],
    queryFn: async () => {
      const r = await api.get<{ results: RoomAssignment[] }>("/hostel/room-assignments/");
      return r.results ?? [];
    },
  });

  const [infinitePage, setInfinitePage] = useState(1);
  const PAGE_SIZE = 12;
  const infiniteItems = assignments.slice(0, infinitePage * PAGE_SIZE);
  const infiniteHasMore = infiniteItems.length < assignments.length;

  const assignment = assignments[0] ?? null;

  const createAssignment = useMutation({
    mutationFn: (data: Partial<RoomAssignment>) => api.post("/hostel/room-assignments/", data),
    onSuccess: () => {
      toast.success("Assignment created");
      qc.invalidateQueries({ queryKey: ["student-hostel"] });
      setShowForm(false);
    },
  });

  const updateAssignment = useMutation({
    mutationFn: (data: Partial<RoomAssignment>) =>
      api.patch(`/hostel/room-assignments/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Assignment updated");
      qc.invalidateQueries({ queryKey: ["student-hostel"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteAssignment = useMutation({
    mutationFn: (id: string) => api.delete(`/hostel/room-assignments/${id}/`),
    onSuccess: () => {
      toast.success("Assignment deleted");
      qc.invalidateQueries({ queryKey: ["student-hostel"] });
    },
  });

  const paginatedAssignments = React.useMemo(() => {
    const start = (page - 1) * 12;
    return assignments.slice(start, start + 12);
  }, [assignments, page]);

  const totalPages = Math.ceil(assignments.length / 12);

  const bulk = useBulkSelect(assignments);

  const handleExport = () => {
    const cols = [
      { key: "room_number", label: "Room" },
      { key: "block", label: "Block" },
    ];
    const rows = assignments.map((row) => ({
      room_number: row.room_number ?? "",
      block: row.floor ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "hostel-assignments-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(
        bulk.selectedArray.map((id) => api.delete("/hostel/assignments//" + id + "/")),
      );
      toast.success(`${bulk.selectedCount} items deleted`);
      bulk.clear();
      qc.invalidateQueries({ queryKey: ["student-hostel"] });
    } catch {
      toast.error("Failed to delete items");
    }
  };

  const handleBulkExport = () => {
    const cols = [{ key: "id", label: "ID" }];
    const rows = bulk.selectedItems.map((item) => ({ id: item.id }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "bulk-export-" + new Date().toISOString().slice(0, 10) + ".csv");
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Hostel</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            View your room assignment and hostel details
          </p>
        </div>

        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={bulk.allSelected}
            ref={(el) => {
              if (el) el.indeterminate = bulk.someSelected;
            }}
            onChange={bulk.toggleAll}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
          />
          <span className="text-sm text-slate-500 dark:text-slate-400">Select all</span>
        </label>
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
        <Button
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <PlusIcon className="mr-1.5 h-4 w-4" />
          {assignment ? "Edit" : "Add"} Assignment
        </Button>
      </div>

      {/* Search */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search rooms by number, block, or floor..."
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
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
                <HomeIcon className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {assignment.room_number}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {assignment.hostel_name}
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
                  {assignment.room_type || "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Bed</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.bed_number || "—"}
                </span>
              </div>
            </div>
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => {
                  setEditing(assignment);
                  setShowForm(true);
                }}
                className="flex items-center gap-1 text-xs text-indigo-600"
              >
                <PencilIcon className="h-3.5 w-3.5" /> Edit
              </button>
              <button
                onClick={() => {
                  if (confirm("Delete this assignment?")) deleteAssignment.mutate(assignment.id);
                }}
                className="flex items-center gap-1 text-xs text-red-500"
              >
                <TrashIcon className="h-3.5 w-3.5" /> Delete
              </button>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/30">
                <UsersIcon className="h-5 w-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">Room Info</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">Hostel details</p>
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
            </div>
          </div>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination page={page} total={assignments.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Assignment" : "Add Assignment"}
      >
        <AssignmentForm
          assignment={editing}
          saving={createAssignment.isPending || updateAssignment.isPending}
          onSave={(data) => {
            if (editing) updateAssignment.mutate(data);
            else createAssignment.mutate(data);
          }}
          onCancel={() => {
            setShowForm(false);
            setEditing(null);
          }}
        />
      </Modal>
    </div>
  );
}

function AssignmentForm({
  assignment,
  saving,
  onSave,
  onCancel,
}: {
  assignment: RoomAssignment | null;
  saving: boolean;
  onSave: (data: Partial<RoomAssignment>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    room_number: assignment?.room_number ?? "",
    hostel_name: assignment?.hostel_name ?? "",
    floor: assignment?.floor ?? "",
    room_type: assignment?.room_type ?? "single",
    bed_number: assignment?.bed_number ?? "",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.room_number.trim()) return toast.error("Room number required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Room Number *</label>
          <input
            value={f.room_number}
            onChange={(e) => setF((p) => ({ ...p, room_number: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Hostel *</label>
          <input
            value={f.hostel_name}
            onChange={(e) => setF((p) => ({ ...p, hostel_name: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Floor</label>
          <input
            value={f.floor}
            onChange={(e) => setF((p) => ({ ...p, floor: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Room Type</label>
          <select
            value={f.room_type}
            onChange={(e) => setF((p) => ({ ...p, room_type: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          >
            <option value="single">Single</option>
            <option value="double">Double</option>
            <option value="shared">Shared</option>
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Bed Number</label>
          <input
            value={f.bed_number}
            onChange={(e) => setF((p) => ({ ...p, bed_number: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {assignment ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
