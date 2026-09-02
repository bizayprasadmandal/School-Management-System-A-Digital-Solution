/**
 * Teacher Sports Page — manage sports, teams, events
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import {
  TrophyIcon,
  UsersIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";

interface Sport {
  id: string;
  name: string;
  description: string;
  category: string;
  team_count: number;
  is_active: boolean;
  min_players: number;
  max_players: number;
}

function SportsSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-28 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function SportsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [sportFilter, setSportFilter] = useState("all");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Sport | null>(null);

  const { data: sports = [], isLoading } = useQuery({
    queryKey: ["teacher-sports"],
    queryFn: async () => {
      const r = await api.get<{ results: Sport[] }>("/sports/sports/");
      return r.results ?? [];
    },
  });

  const filteredSports = React.useMemo(() => {
    let items = sports;
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(
        (s) => s.name?.toLowerCase().includes(q) || s.description?.toLowerCase().includes(q),
      );
    }
    if (sportFilter !== "all") {
      items = items.filter((s) => s.name?.toLowerCase() === sportFilter);
    }
    return items;
  }, [sports, search, sportFilter]);

  const sportsList = React.useMemo(() => {
    const list = new Set(sports.map((s) => s.name).filter(Boolean));
    return ["all", ...Array.from(list)];
  }, [sports]);

  const createSport = useMutation({
    mutationFn: (data: Partial<Sport>) => api.post("/sports/sports/", data),
    onSuccess: () => {
      toast.success("Sport added");
      qc.invalidateQueries({ queryKey: ["teacher-sports"] });
      setShowForm(false);
    },
  });

  const updateSport = useMutation({
    mutationFn: (data: Partial<Sport>) => api.patch(`/sports/sports/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Sport updated");
      qc.invalidateQueries({ queryKey: ["teacher-sports"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteSport = useMutation({
    mutationFn: (id: string) => api.delete(`/sports/sports/${id}/`),
    onSuccess: () => {
      toast.success("Sport deleted");
      qc.invalidateQueries({ queryKey: ["teacher-sports"] });
    },
  });

  const paginatedFilteredSports = React.useMemo(() => {
    const start = (page - 1) * 12;
    return filteredSports.slice(start, start + 12);
  }, [filteredSports, page]);

  const totalPages = Math.ceil(filteredSports.length / 12);
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Sports & Activities</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Manage sports, teams, and extracurricular activities
          </p>
        </div>
        <Button
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <PlusIcon className="mr-1.5 h-4 w-4" />
          Add Sport
        </Button>
      </div>

      {/* Search + Filters */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700 space-y-3">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="search"
              placeholder="Search teams or sports..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-400"
            />
          </div>
          {sportsList.length > 2 && (
            <select
              value={sportFilter}
              onChange={(e) => {
                setSportFilter(e.target.value);
                setPage(1);
              }}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-700 dark:text-white"
            >
              {sportsList.map((s) => (
                <option key={s} value={s}>
                  {s === "all" ? "All Sports" : s}
                </option>
              ))}
            </select>
          )}
          {(search || sportFilter !== "all") && (
            <button
              onClick={() => {
                setSearch("");
                setSportFilter("all");
              }}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm text-slate-600 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-400 dark:hover:bg-slate-700"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {isLoading ? (
        <SportsSkeleton />
      ) : filteredSports.length === 0 ? (
        <EmptyState
          icon={TrophyIcon}
          title="No sports"
          description="Add sports and activities for students."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {paginatedFilteredSports.map((sport) => (
            <div
              key={sport.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="mb-2 flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <TrophyIcon className="h-5 w-5 text-amber-500" />
                  <h3 className="font-semibold text-slate-900 dark:text-white">{sport.name}</h3>
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(sport);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this sport?")) deleteSport.mutate(sport.id);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {sport.description || "No description"}
              </p>
              <div className="mt-3 flex items-center gap-3">
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <UsersIcon className="h-3.5 w-3.5" />
                  {sport.team_count ?? 0} teams
                </span>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    sport.is_active
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                  }`}
                >
                  {sport.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination page={page} total={filteredSports.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Sport" : "Add Sport"}
      >
        <SportForm
          sport={editing}
          saving={createSport.isPending || updateSport.isPending}
          onSave={(data) => {
            if (editing) updateSport.mutate(data);
            else createSport.mutate(data);
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

function SportForm({
  sport,
  saving,
  onSave,
  onCancel,
}: {
  sport: Sport | null;
  saving: boolean;
  onSave: (data: Partial<Sport>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    name: sport?.name ?? "",
    description: sport?.description ?? "",
    category: sport?.category ?? "sport",
    min_players: sport?.min_players ?? 1,
    max_players: sport?.max_players ?? 20,
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
        <label className="mb-1 block text-sm font-medium">Name *</label>
        <input
          value={f.name}
          onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          required
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Category</label>
        <select
          value={f.category}
          onChange={(e) => setF((p) => ({ ...p, category: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        >
          <option value="sport">Sport</option>
          <option value="academic">Academic</option>
          <option value="arts">Arts & Culture</option>
          <option value="club">Club & Society</option>
          <option value="other">Other</option>
        </select>
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
          {sport ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
