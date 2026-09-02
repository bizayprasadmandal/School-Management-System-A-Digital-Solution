/**
 * Counselor Workshops Page — schedule and manage workshops
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import {
  AcademicCapIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CalendarDaysIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface Workshop {
  id: string;
  title: string;
  description: string;
  date: string;
  facilitator: string;
  attendees: number;
  max_attendees: number;
}

function WorkshopSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function WorkshopsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Workshop | null>(null);

  const { data: allWorkshops = [], isLoading } = useQuery({
    queryKey: ["counselor-workshops"],
    queryFn: async () => {
      const r = await api.get<{ results: Workshop[] }>("/counseling/workshops/");
      return r.results ?? [];
    },
  });

  const workshops = React.useMemo(() => {
    if (!search.trim()) return allWorkshops;
    const q = search.toLowerCase();
    return allWorkshops.filter(
      (w) =>
        w.title?.toLowerCase().includes(q) ||
        w.facilitator?.toLowerCase().includes(q) ||
        w.description?.toLowerCase().includes(q),
    );
  }, [allWorkshops, search]);

  const createWorkshop = useMutation({
    mutationFn: (data: Partial<Workshop>) => api.post("/counseling/workshops/", data),
    onSuccess: () => {
      toast.success("Workshop created");
      qc.invalidateQueries({ queryKey: ["counselor-workshops"] });
      setShowForm(false);
    },
  });

  const updateWorkshop = useMutation({
    mutationFn: (data: Partial<Workshop>) =>
      api.patch(`/counseling/workshops/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Workshop updated");
      qc.invalidateQueries({ queryKey: ["counselor-workshops"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteWorkshop = useMutation({
    mutationFn: (id: string) => api.delete(`/counseling/workshops/${id}/`),
    onSuccess: () => {
      toast.success("Workshop deleted");
      qc.invalidateQueries({ queryKey: ["counselor-workshops"] });
    },
  });

  const paginatedAllWorkshops = React.useMemo(() => {
    const start = (page - 1) * 12;
    return allWorkshops.slice(start, start + 12);
  }, [allWorkshops, page]);

  const totalPages = Math.ceil(allWorkshops.length / 12);

  const handleExport = () => {
    const cols = [
      { key: "title", label: "Title" },
      { key: "facilitator", label: "Facilitator" },
    ];
    const rows = allWorkshops.map((row) => ({
      title: row.title ?? "",
      facilitator: row.facilitator ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "workshops-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Workshops</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Schedule and manage student development workshops
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
          Schedule Workshop
        </Button>
      </div>

      {/* Search */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search workshops..."
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
        <WorkshopSkeleton />
      ) : workshops.length === 0 ? (
        <EmptyState
          icon={AcademicCapIcon}
          title="No workshops"
          description="Schedule workshops for student development."
        />
      ) : (
        <div className="space-y-3">
          {workshops.map((ws) => (
            <div
              key={ws.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">{ws.title}</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {ws.description || "—"}
                  </p>
                  <div className="mt-1 flex items-center gap-3">
                    <span className="flex items-center gap-1 text-xs text-slate-400">
                      <CalendarDaysIcon className="h-3.5 w-3.5" />
                      {ws.date ? new Date(ws.date).toLocaleDateString() : "—"}
                    </span>
                    <span className="text-xs text-slate-400">{ws.facilitator || "—"}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-500 dark:text-slate-400">
                    {ws.attendees ?? 0}/{ws.max_attendees ?? "∞"}
                  </span>
                  <div className="flex gap-1">
                    <button
                      onClick={() => {
                        setEditing(ws);
                        setShowForm(true);
                      }}
                      className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => {
                        if (confirm("Delete this workshop?")) deleteWorkshop.mutate(ws.id);
                      }}
                      className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination page={page} total={workshops.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Workshop" : "Schedule Workshop"}
      >
        <WorkshopForm
          workshop={editing}
          saving={createWorkshop.isPending || updateWorkshop.isPending}
          onSave={(data) => {
            if (editing) updateWorkshop.mutate(data);
            else createWorkshop.mutate(data);
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

function WorkshopForm({
  workshop,
  saving,
  onSave,
  onCancel,
}: {
  workshop: Workshop | null;
  saving: boolean;
  onSave: (data: Partial<Workshop>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    title: workshop?.title ?? "",
    description: workshop?.description ?? "",
    date: workshop?.date ?? "",
    facilitator: workshop?.facilitator ?? "",
    max_attendees: workshop?.max_attendees ?? 30,
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.title.trim()) return toast.error("Title required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div>
        <label className="mb-1 block text-sm font-medium">Title *</label>
        <input
          value={f.title}
          onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          required
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Description</label>
        <textarea
          value={f.description}
          onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
          rows={3}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Date *</label>
          <input
            type="datetime-local"
            value={f.date}
            onChange={(e) => setF((p) => ({ ...p, date: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Facilitator</label>
          <input
            value={f.facilitator}
            onChange={(e) => setF((p) => ({ ...p, facilitator: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Max Attendees</label>
        <input
          type="number"
          min={1}
          value={f.max_attendees}
          onChange={(e) => setF((p) => ({ ...p, max_attendees: Number(e.target.value) }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {workshop ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
