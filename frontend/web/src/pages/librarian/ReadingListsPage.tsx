/**
 * Librarian Reading Lists Page — curated reading lists by grade
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Reorder } from "framer-motion";
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
  ListBulletIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ArrowDownTrayIcon,
  Bars3Icon,
} from "@heroicons/react/24/outline";

interface ReadingList {
  id: string;
  title: string;
  description: string;
  grade_level: string;
  books_count: number;
  assigned_to: number;
}

function ReadingListSkeleton() {
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

export default function ReadingListsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<ReadingList | null>(null);

  const { data: allLists = [], isLoading } = useQuery({
    queryKey: ["librarian-reading-lists"],
    queryFn: async () => {
      const r = await api.get<{ results: ReadingList[] }>("/library/reading-lists/");
      return r.results ?? [];
    },
  });

  const [infinitePage, setInfinitePage] = useState(1);
  const PAGE_SIZE = 12;
  const infiniteItems = allLists.slice(0, infinitePage * PAGE_SIZE);
  const infiniteHasMore = infiniteItems.length < allLists.length;

  const lists = React.useMemo(() => {
    if (!search.trim()) return allLists;
    const q = search.toLowerCase();
    return allLists.filter(
      (l) =>
        l.title?.toLowerCase().includes(q) ||
        l.description?.toLowerCase().includes(q) ||
        (l as any).created_by?.toLowerCase().includes(q) ||
        (l as any).teacher?.toLowerCase().includes(q),
    );
  }, [allLists, search]);

  const createList = useMutation({
    mutationFn: (data: Partial<ReadingList>) => api.post("/library/reading-lists/", data),
    onSuccess: () => {
      toast.success("Reading list created");
      qc.invalidateQueries({ queryKey: ["librarian-reading-lists"] });
      setShowForm(false);
    },
  });

  const updateList = useMutation({
    mutationFn: (data: Partial<ReadingList>) =>
      api.patch(`/library/reading-lists/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Reading list updated");
      qc.invalidateQueries({ queryKey: ["librarian-reading-lists"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteList = useMutation({
    mutationFn: (id: string) => api.delete(`/library/reading-lists/${id}/`),
    onSuccess: () => {
      toast.success("Reading list deleted");
      qc.invalidateQueries({ queryKey: ["librarian-reading-lists"] });
    },
  });

  const paginatedAllLists = React.useMemo(() => {
    const start = (page - 1) * 12;
    return allLists.slice(start, start + 12);
  }, [allLists, page]);

  const totalPages = Math.ceil(allLists.length / 12);

  const bulk = useBulkSelect(allLists);
  const [reorderMode, setReorderMode] = React.useState(false);
  const [orderedItems, setOrderedItems] = React.useState(allLists);

  React.useEffect(() => {
    setOrderedItems(allLists);
  }, [allLists]);

  const handleExport = () => {
    const cols = [
      { key: "title", label: "Title" },
      { key: "description", label: "Description" },
    ];
    const rows = allLists.map((row) => ({
      title: row.title ?? "",
      description: row.description ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "reading-lists-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(
        bulk.selectedArray.map((id) => api.delete("/library/reading-lists//" + id + "/")),
      );
      toast.success(`${bulk.selectedCount} items deleted`);
      bulk.clear();
      qc.invalidateQueries({ queryKey: ["librarian-readinglists"] });
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Reading Lists</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Curated reading lists for different grade levels
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
          Create List
        </Button>
      </div>

      {/* Search */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search reading lists..."
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
        <ReadingListSkeleton />
      ) : lists.length === 0 ? (
        <EmptyState
          icon={ListBulletIcon}
          title="No reading lists"
          description="Create curated reading lists for different grade levels."
        />
      ) : (
        <div className="space-y-3">
          {
            /* Drag-and-drop: Use Reorder.Group with orderedItems for full DnD */
            paginatedAllLists.map((list) => (
              <div
                key={list.id}
                className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
              >
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">{list.title}</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {list.description || "—"}
                  </p>
                  <p className="mt-1 text-xs text-slate-400">
                    Grade: {list.grade_level || "—"} · {list.books_count ?? 0} books · Assigned to{" "}
                    {list.assigned_to ?? 0} students
                  </p>
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(list);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                    aria-label="Edit"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this list?")) deleteList.mutate(list.id);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                    aria-label="Delete"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))
          }
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination page={page} total={lists.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit List" : "Create List"}
      >
        <ListForm
          list={editing}
          saving={createList.isPending || updateList.isPending}
          onSave={(data) => {
            if (editing) updateList.mutate(data);
            else createList.mutate(data);
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

function ListForm({
  list,
  saving,
  onSave,
  onCancel,
}: {
  list: ReadingList | null;
  saving: boolean;
  onSave: (data: Partial<ReadingList>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    title: list?.title ?? "",
    description: list?.description ?? "",
    grade_level: list?.grade_level ?? "",
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
        <label className="mb-1 block text-sm font-medium">Grade Level</label>
        <input
          value={f.grade_level}
          onChange={(e) => setF((p) => ({ ...p, grade_level: e.target.value }))}
          placeholder="e.g. Grade 5, 9-10"
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
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
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {list ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
