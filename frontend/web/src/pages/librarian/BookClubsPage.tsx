/**
 * Librarian Book Clubs Page — manage book clubs
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import { BulkActionBar } from "../../components/common/BulkActionBar";
import {
  UserGroupIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CalendarDaysIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface BookClub {
  id: string;
  name: string;
  book_title: string;
  description: string;
  meeting_day: string;
  members: number;
  status: string;
}

function BookClubSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="h-32 relative overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
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

export default function BookClubsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<BookClub | null>(null);

  const { data: allClubs = [], isLoading } = useQuery({
    queryKey: ["librarian-book-clubs"],
    queryFn: async () => {
      const r = await api.get<{ results: BookClub[] }>("/library/book-clubs/");
      return r.results ?? [];
    },
  });

  const clubs = React.useMemo(() => {
    if (!search.trim()) return allClubs;
    const q = search.toLowerCase();
    return allClubs.filter(
      (c) =>
        c.name?.toLowerCase().includes(q) ||
        c.description?.toLowerCase().includes(q) ||
        (c as any).leader?.toLowerCase().includes(q) ||
        (c as any).facilitator?.toLowerCase().includes(q),
    );
  }, [allClubs, search]);

  const createClub = useMutation({
    mutationFn: (data: Partial<BookClub>) => api.post("/library/book-clubs/", data),
    onSuccess: () => {
      toast.success("Book club created");
      qc.invalidateQueries({ queryKey: ["librarian-book-clubs"] });
      setShowForm(false);
    },
  });

  const updateClub = useMutation({
    mutationFn: (data: Partial<BookClub>) => api.patch(`/library/book-clubs/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Book club updated");
      qc.invalidateQueries({ queryKey: ["librarian-book-clubs"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteClub = useMutation({
    mutationFn: (id: string) => api.delete(`/library/book-clubs/${id}/`),
    onSuccess: () => {
      toast.success("Book club deleted");
      qc.invalidateQueries({ queryKey: ["librarian-book-clubs"] });
    },
  });

  const paginatedAllClubs = React.useMemo(() => {
    const start = (page - 1) * 12;
    return allClubs.slice(start, start + 12);
  }, [allClubs, page]);

  const totalPages = Math.ceil(allClubs.length / 12);

  const bulk = useBulkSelect(allClubs);

  const handleExport = () => {
    const cols = [
      { key: "name", label: "Name" },
      { key: "description", label: "Description" },
    ];
    const rows = allClubs.map((row) => ({
      name: row.name ?? "",
      description: row.description ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "book-clubs-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(
        bulk.selectedArray.map((id) => api.delete("/library/book-clubs//" + id + "/")),
      );
      toast.success(`${bulk.selectedCount} items deleted`);
      bulk.clear();
      qc.invalidateQueries({ queryKey: ["librarian-bookclubs"] });
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Book Clubs</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Manage book clubs and reading groups
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
          Create Club
        </Button>
      </div>

      {/* Search */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search book clubs..."
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
        <BookClubSkeleton />
      ) : clubs.length === 0 ? (
        <EmptyState
          icon={UserGroupIcon}
          title="No book clubs"
          description="Create book clubs to encourage reading among students."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {paginatedAllClubs.map((club) => (
            <div
              key={club.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="mb-2 flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">{club.name}</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Reading: {club.book_title || "—"}
                  </p>
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(club);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this club?")) deleteClub.mutate(club.id);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <p className="text-xs text-slate-400">{club.description || "—"}</p>
              <div className="mt-3 flex items-center gap-3">
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <CalendarDaysIcon className="h-3.5 w-3.5" />
                  {club.meeting_day || "—"}
                </span>
                <span className="text-xs text-slate-400">{club.members ?? 0} members</span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    club.status === "active"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : club.status === "upcoming"
                        ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                        : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                  }`}
                >
                  {club.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination page={page} total={clubs.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Club" : "Create Club"}
      >
        <ClubForm
          club={editing}
          saving={createClub.isPending || updateClub.isPending}
          onSave={(data) => {
            if (editing) updateClub.mutate(data);
            else createClub.mutate(data);
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

function ClubForm({
  club,
  saving,
  onSave,
  onCancel,
}: {
  club: BookClub | null;
  saving: boolean;
  onSave: (data: Partial<BookClub>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    name: club?.name ?? "",
    book_title: club?.book_title ?? "",
    description: club?.description ?? "",
    meeting_day: club?.meeting_day ?? "",
    status: club?.status ?? "upcoming",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.name.trim()) return toast.error("Name required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div>
        <label className="mb-1 block text-sm font-medium">Club Name *</label>
        <input
          value={f.name}
          onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          required
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Book Title</label>
        <input
          value={f.book_title}
          onChange={(e) => setF((p) => ({ ...p, book_title: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Meeting Day</label>
          <input
            value={f.meeting_day}
            onChange={(e) => setF((p) => ({ ...p, meeting_day: e.target.value }))}
            placeholder="e.g. Wednesday"
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
        <label className="mb-1 block text-sm font-medium">Description</label>
        <textarea
          value={f.description}
          onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
          rows={2}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {club ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
