/**
 * Student Transport Page — view route assignment and bus info
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import {
  TruckIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MapPinIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface RouteAssignment {
  id: string;
  route_name: string;
  bus_number: string;
  driver_name: string;
  pickup_time: string;
  dropoff_time: string;
  stop_name: string;
  status: string;
  capacity: number;
}

function TransportSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[1, 2].map((i) => (
        <div key={i} className="h-40 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function TransportPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<RouteAssignment | null>(null);

  const { data: assignments = [], isLoading } = useQuery({
    queryKey: ["student-transport"],
    queryFn: async () => {
      const r = await api.get<{ results: RouteAssignment[] }>("/transportation/route-assignments/");
      return r.results ?? [];
    },
  });

  const assignment = assignments[0] ?? null;

  const createAssignment = useMutation({
    mutationFn: (data: Partial<RouteAssignment>) =>
      api.post("/transportation/route-assignments/", data),
    onSuccess: () => {
      toast.success("Assignment created");
      qc.invalidateQueries({ queryKey: ["student-transport"] });
      setShowForm(false);
    },
  });

  const updateAssignment = useMutation({
    mutationFn: (data: Partial<RouteAssignment>) =>
      api.patch(`/transportation/route-assignments/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Assignment updated");
      qc.invalidateQueries({ queryKey: ["student-transport"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteAssignment = useMutation({
    mutationFn: (id: string) => api.delete(`/transportation/route-assignments/${id}/`),
    onSuccess: () => {
      toast.success("Assignment deleted");
      qc.invalidateQueries({ queryKey: ["student-transport"] });
    },
  });

  const paginatedAssignments = React.useMemo(() => {
    const start = (page - 1) * 12;
    return assignments.slice(start, start + 12);
  }, [assignments, page]);

  const totalPages = Math.ceil(assignments.length / 12);

  const handleExport = () => {
    const cols = [
      { key: "route_name", label: "Route" },
      { key: "driver_name", label: "Driver" },
      { key: "bus_number", label: "Bus" },
    ];
    const rows = assignments.map((row) => ({
      route_name: row.route_name ?? "",
      driver_name: row.driver_name ?? "",
      bus_number: row.bus_number ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "transport-assignments-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Transportation</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            View your bus route and transport details
          </p>
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
            placeholder="Search routes, vehicles, or drivers..."
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
        <TransportSkeleton />
      ) : !assignment ? (
        <EmptyState
          icon={TruckIcon}
          title="No transport assignment"
          description="You haven't been assigned a transport route yet."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30">
                <TruckIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {assignment.route_name}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {assignment.bus_number}
                </p>
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Driver</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.driver_name || "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Pickup Time</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.pickup_time || "—"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Drop-off Time</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.dropoff_time || "—"}
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
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/30">
                <MapPinIcon className="h-5 w-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">Stop Details</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {assignment.stop_name || "Your stop"}
                </p>
              </div>
            </div>
            <div className="space-y-2 text-sm">
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
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Capacity</span>
                <span className="font-medium text-slate-900 dark:text-white">
                  {assignment.capacity || "—"}
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
        <TransportForm
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

function TransportForm({
  assignment,
  saving,
  onSave,
  onCancel,
}: {
  assignment: RouteAssignment | null;
  saving: boolean;
  onSave: (data: Partial<RouteAssignment>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    route_name: assignment?.route_name ?? "",
    bus_number: assignment?.bus_number ?? "",
    driver_name: assignment?.driver_name ?? "",
    pickup_time: assignment?.pickup_time ?? "",
    dropoff_time: assignment?.dropoff_time ?? "",
    stop_name: assignment?.stop_name ?? "",
    capacity: assignment?.capacity ?? 40,
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.route_name.trim()) return toast.error("Route name required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Route Name *</label>
          <input
            value={f.route_name}
            onChange={(e) => setF((p) => ({ ...p, route_name: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Bus Number *</label>
          <input
            value={f.bus_number}
            onChange={(e) => setF((p) => ({ ...p, bus_number: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Driver</label>
        <input
          value={f.driver_name}
          onChange={(e) => setF((p) => ({ ...p, driver_name: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Pickup Time</label>
          <input
            type="time"
            value={f.pickup_time}
            onChange={(e) => setF((p) => ({ ...p, pickup_time: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Drop-off Time</label>
          <input
            type="time"
            value={f.dropoff_time}
            onChange={(e) => setF((p) => ({ ...p, dropoff_time: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Stop Name</label>
          <input
            value={f.stop_name}
            onChange={(e) => setF((p) => ({ ...p, stop_name: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Capacity</label>
          <input
            type="number"
            min={1}
            value={f.capacity}
            onChange={(e) => setF((p) => ({ ...p, capacity: Number(e.target.value) }))}
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
