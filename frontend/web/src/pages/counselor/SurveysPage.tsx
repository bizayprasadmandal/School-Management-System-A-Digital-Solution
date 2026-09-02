/**
 * Counselor Surveys Page — manage wellness surveys
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { ClipboardDocumentListIcon } from "@heroicons/react/24/outline";

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
  const { data: surveys = [], isLoading } = useQuery({
    queryKey: ["counselor-surveys"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/counseling/surveys/");
      return r.results ?? [];
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
          {surveys.map((survey: any) => (
            <div
              key={survey.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">{survey.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {survey.description ?? "—"}
                </p>
                <p className="mt-1 text-xs text-slate-400">{survey.responses ?? 0} responses</p>
              </div>
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
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
