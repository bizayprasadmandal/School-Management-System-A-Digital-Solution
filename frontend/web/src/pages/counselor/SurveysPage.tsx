/**
 * Counselor Surveys Page — manage wellness surveys
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { Button, EmptyState, Modal } from "../../components/common";
import {
  ClipboardDocumentListIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
} from "@heroicons/react/24/outline";

interface Survey {
  id: string;
  title: string;
  description: string;
  status: string;
  responses: number;
}

function SurveySkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function SurveysPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Survey | null>(null);

  const { data: allSurveys = [], isLoading } = useQuery({
    queryKey: ["counselor-surveys"],
    queryFn: async () => {
      const r = await api.get<{ results: Survey[] }>("/counseling/surveys/");
      return r.results ?? [];
    },
  });

  const surveys = React.useMemo(() => {
    if (!search.trim()) return allSurveys;
    const q = search.toLowerCase();
    return allSurveys.filter(
      (s) => s.title?.toLowerCase().includes(q) || s.description?.toLowerCase().includes(q),
    );
  }, [allSurveys, search]);

  const createSurvey = useMutation({
    mutationFn: (data: Partial<Survey>) => api.post("/counseling/surveys/", data),
    onSuccess: () => {
      toast.success("Survey created");
      qc.invalidateQueries({ queryKey: ["counselor-surveys"] });
      setShowForm(false);
    },
  });

  const updateSurvey = useMutation({
    mutationFn: (data: Partial<Survey>) => api.patch(`/counseling/surveys/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Survey updated");
      qc.invalidateQueries({ queryKey: ["counselor-surveys"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteSurvey = useMutation({
    mutationFn: (id: string) => api.delete(`/counseling/surveys/${id}/`),
    onSuccess: () => {
      toast.success("Survey deleted");
      qc.invalidateQueries({ queryKey: ["counselor-surveys"] });
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Wellness Surveys</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Create and manage student wellness surveys
          </p>
        </div>
        <Button
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <PlusIcon className="mr-1.5 h-4 w-4" />
          Create Survey
        </Button>
      </div>

      {/* Search */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search surveys..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-400"
          />
        </div>
      </div>

      {isLoading ? (
        <SurveySkeleton />
      ) : surveys.length === 0 ? (
        <EmptyState
          icon={ClipboardDocumentListIcon}
          title="No surveys yet"
          description="Create wellness surveys to gather student feedback."
        />
      ) : (
        <div className="space-y-3">
          {surveys.map((survey) => (
            <div
              key={survey.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">{survey.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {survey.description || "—"}
                </p>
                <p className="mt-1 text-xs text-slate-400">{survey.responses ?? 0} responses</p>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    survey.status === "active"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : survey.status === "draft"
                        ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                        : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                  }`}
                >
                  {survey.status}
                </span>
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(survey);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this survey?")) deleteSurvey.mutate(survey.id);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Survey" : "Create Survey"}
      >
        <SurveyForm
          survey={editing}
          saving={createSurvey.isPending || updateSurvey.isPending}
          onSave={(data) => {
            if (editing) updateSurvey.mutate(data);
            else createSurvey.mutate(data);
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

function SurveyForm({
  survey,
  saving,
  onSave,
  onCancel,
}: {
  survey: Survey | null;
  saving: boolean;
  onSave: (data: Partial<Survey>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    title: survey?.title ?? "",
    description: survey?.description ?? "",
    status: survey?.status ?? "draft",
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
      <div>
        <label className="mb-1 block text-sm font-medium">Status</label>
        <select
          value={f.status}
          onChange={(e) => setF((p) => ({ ...p, status: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        >
          <option value="draft">Draft</option>
          <option value="active">Active</option>
          <option value="closed">Closed</option>
        </select>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {survey ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
