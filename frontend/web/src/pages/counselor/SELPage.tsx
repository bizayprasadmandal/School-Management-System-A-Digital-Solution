/**
 * Counselor SEL Page — manage Social-Emotional Learning programs
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Reorder } from "framer-motion";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import { BulkActionBar } from "../../components/common/BulkActionBar";
import {
  HeartIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ArrowDownTrayIcon,
  Bars3Icon,
} from "@heroicons/react/24/outline";

interface SELProgram {
  id: string;
  title: string;
  category: string;
  participants: number;
  status: string;
  progress: number;
}

function SELSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="h-24 relative overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
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

export default function SELPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<SELProgram | null>(null);

  const { data: allPrograms = [], isLoading } = useQuery({
    queryKey: ["counselor-sel"],
    queryFn: async () => {
      const r = await api.get<{ results: SELProgram[] }>("/counseling/sel-programs/");
      return r.results ?? [];
    },
  });

  const programs = React.useMemo(() => {
    if (!search.trim()) return allPrograms;
    const q = search.toLowerCase();
    return allPrograms.filter(
      (p) =>
        p.title?.toLowerCase().includes(q) ||
        (p as any).name?.toLowerCase().includes(q) ||
        (p as any).description?.toLowerCase().includes(q),
    );
  }, [allPrograms, search]);

  const createProgram = useMutation({
    mutationFn: (data: Partial<SELProgram>) => api.post("/counseling/sel-programs/", data),
    onSuccess: () => {
      toast.success("Program created");
      qc.invalidateQueries({ queryKey: ["counselor-sel"] });
      setShowForm(false);
    },
  });

  const updateProgram = useMutation({
    mutationFn: (data: Partial<SELProgram>) =>
      api.patch(`/counseling/sel-programs/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Program updated");
      qc.invalidateQueries({ queryKey: ["counselor-sel"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteProgram = useMutation({
    mutationFn: (id: string) => api.delete(`/counseling/sel-programs/${id}/`),
    onSuccess: () => {
      toast.success("Program deleted");
      qc.invalidateQueries({ queryKey: ["counselor-sel"] });
    },
  });

  const paginatedAllPrograms = React.useMemo(() => {
    const start = (page - 1) * 12;
    return allPrograms.slice(start, start + 12);
  }, [allPrograms, page]);

  const totalPages = Math.ceil(allPrograms.length / 12);

  const bulk = useBulkSelect(allPrograms);
  const [reorderMode, setReorderMode] = React.useState(false);
  const [orderedItems, setOrderedItems] = React.useState(allPrograms);

  React.useEffect(() => {
    setOrderedItems(allPrograms);
  }, [allPrograms]);

  const handleExport = () => {
    const cols = [
      { key: "title", label: "Title" },
      { key: "description", label: "Description" },
    ];
    const rows = allPrograms.map((row) => ({
      title: row.title ?? "",
      description: row.title ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "sel-programs-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(
        bulk.selectedArray.map((id) => api.delete("/counseling/sel-programs//" + id + "/")),
      );
      toast.success(`${bulk.selectedCount} items deleted`);
      bulk.clear();
      qc.invalidateQueries({ queryKey: ["counselor-sel"] });
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Social-Emotional Learning
          </h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Manage SEL programs for students
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
        <Button
          variant={reorderMode ? "primary" : "secondary"}
          leftIcon={<Bars3Icon className="h-4 w-4" />}
          onClick={() => setReorderMode(!reorderMode)}
        >
          {reorderMode ? "Done" : "Reorder"}
        </Button>
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
          Create Program
        </Button>
      </div>

      {/* Search */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search SEL programs..."
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
        <SELSkeleton />
      ) : programs.length === 0 ? (
        <EmptyState
          icon={HeartIcon}
          title="No SEL programs"
          description="Create social-emotional learning programs for students."
        />
      ) : (
        <div className="space-y-3">
          {
            /* Drag-and-drop: Use Reorder.Group with orderedItems for full DnD */
            paginatedAllPrograms.map((program) => {
              const progress = program.progress ?? 0;
              return (
                <div
                  key={program.id}
                  className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-slate-900 dark:text-white">
                        {program.title}
                      </h3>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {program.category || "—"}
                      </p>
                      <p className="mt-1 text-xs text-slate-400">
                        {program.participants ?? 0} participants
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="flex flex-col items-end gap-2">
                        <span
                          className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                            program.status === "active"
                              ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                              : program.status === "upcoming"
                                ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                                : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                          }`}
                        >
                          {program.status}
                        </span>
                        <div className="h-2 w-24 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                          <div
                            className="h-full rounded-full bg-indigo-500"
                            style={{ width: `${Math.min(progress, 100)}%` }}
                          />
                        </div>
                      </div>
                      <div className="flex gap-1">
                        <button
                          onClick={() => {
                            setEditing(program);
                            setShowForm(true);
                          }}
                          className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                        >
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => {
                            if (confirm("Delete this program?")) deleteProgram.mutate(program.id);
                          }}
                          className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          }
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination page={page} total={programs.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Program" : "Create Program"}
      >
        <SELForm
          program={editing}
          saving={createProgram.isPending || updateProgram.isPending}
          onSave={(data) => {
            if (editing) updateProgram.mutate(data);
            else createProgram.mutate(data);
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

function SELForm({
  program,
  saving,
  onSave,
  onCancel,
}: {
  program: SELProgram | null;
  saving: boolean;
  onSave: (data: Partial<SELProgram>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    title: program?.title ?? "",
    category: program?.category ?? "",
    status: program?.status ?? "upcoming",
    progress: program?.progress ?? 0,
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
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Category</label>
          <input
            value={f.category}
            onChange={(e) => setF((p) => ({ ...p, category: e.target.value }))}
            placeholder="e.g. Empathy, Self-regulation"
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Status</label>
          <select
            value={f.status}
            onChange={(e) => setF((p) => ({ ...p, status: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          >
            <option value="upcoming">Upcoming</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Progress (%)</label>
        <input
          type="number"
          min={0}
          max={100}
          value={f.progress}
          onChange={(e) => setF((p) => ({ ...p, progress: Number(e.target.value) }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {program ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
