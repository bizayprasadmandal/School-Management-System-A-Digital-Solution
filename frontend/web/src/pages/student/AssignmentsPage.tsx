/**
 * StudentAssignmentsPage
 *
 * Students can view assigned homework/quizzes/projects, submit their work
 * (file upload + remarks), and see graded results with teacher feedback.
 */
import React, { useState, useRef } from "react";
import {
  DocumentArrowUpIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  AcademicCapIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import {
  useStudentAssessments,
  useStudentSubmissions,
  useSubmitAssessment,
} from "../../api/hooks";
import { Badge, EmptyState, SkeletonCard, ErrorState } from "../../components/common";
import { useTitle } from "../../hooks";
import toast from "react-hot-toast";
import clsx from "clsx";
import dayjs from "dayjs";
import type { Assessment, AssessmentSubmission, AssessmentType } from "../../types";

// ─── Helpers ──────────────────────────────────────────────────────────────────

const ASSESSMENT_COLORS: Record<AssessmentType, string> = {
  homework:  "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  quiz:      "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
  project:   "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  classwork: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
  lab:       "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300",
};

const ASSESSMENT_ICONS: Record<AssessmentType, string> = {
  homework:  "📝",
  quiz:      "❓",
  project:   "📊",
  classwork: "📋",
  lab:       "🔬",
};

function typeBadge(type: AssessmentType) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${ASSESSMENT_COLORS[type]}`}>
      <span>{ASSESSMENT_ICONS[type]}</span>
      {type.charAt(0).toUpperCase() + type.slice(1)}
    </span>
  );
}

function statusBadge(sub: AssessmentSubmission | undefined, maxMarks: number = 100) {
  if (!sub) return <span className="text-xs font-medium text-slate-400">Not submitted</span>;
  if (sub.marks_obtained != null) {
    const pct = sub.percentage ?? 0;
    const color = pct >= 75 ? "text-green-600 bg-green-50 dark:bg-green-900/20" : pct >= 40 ? "text-amber-600 bg-amber-50 dark:bg-amber-900/20" : "text-red-600 bg-red-50 dark:bg-red-900/20";
    return (
      <div className="flex items-center gap-2">
        <CheckCircleIcon className="h-4 w-4 text-green-500" />
        <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${color}`}>
          Graded: {sub.marks_obtained}/{maxMarks}
        </span>
      </div>
    );
  }
  return (
    <div className="flex items-center gap-1.5">
      <ClockIcon className="h-4 w-4 text-amber-500" />
      <span className="rounded-full bg-amber-50 dark:bg-amber-900/20 px-2 py-0.5 text-xs font-semibold text-amber-600 dark:text-amber-400">
        Submitted{sub.is_late ? " (late)" : ""}
      </span>
    </div>
  );
}

// ─── Submit Modal ─────────────────────────────────────────────────────────────

function SubmitModal({
  assessment,
  onClose,
}: {
  assessment: Assessment;
  onClose: () => void;
}) {
  const [remarks, setRemarks] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const submitMutation = useSubmitAssessment();

  const handleSubmit = async () => {
    if (!file && !remarks.trim()) {
      toast.error("Please upload a file or add remarks.");
      return;
    }
    const fd = new FormData();
    fd.append("assessment", String(assessment.id));
    if (file) fd.append("file", file);
    if (remarks.trim()) fd.append("remarks", remarks.trim());
    try {
      await submitMutation.mutateAsync(fd);
      toast.success("Assignment submitted!");
      onClose();
    } catch {
      toast.error("Failed to submit. Please try again.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div className="w-full max-w-lg rounded-2xl bg-white dark:bg-slate-800 shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 px-6 py-4">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Submit Assignment</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
            <XCircleIcon className="h-5 w-5" />
          </button>
        </div>
        <div className="px-6 py-4 space-y-4">
          <div>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">{assessment.title}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">{assessment.subject_name} · Due {dayjs(assessment.due_date).format("MMM D, YYYY")}</p>
          </div>
          {assessment.description && (
            <p className="text-sm text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-900/50 rounded-lg p-3">{assessment.description}</p>
          )}
          {/* File upload */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">Attachment (optional)</label>
            <div
              onClick={() => fileRef.current?.click()}
              className="flex cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600 p-6 text-slate-400 hover:border-indigo-400 hover:text-indigo-500 transition-colors"
            >
              {file ? (
                <div className="flex items-center gap-2 text-sm font-medium text-indigo-600 dark:text-indigo-400">
                  <DocumentTextIcon className="h-5 w-5" />
                  {file.name}
                  <button onClick={(e) => { e.stopPropagation(); setFile(null); }} className="text-red-400 hover:text-red-600 ml-2">Remove</button>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-1">
                  <DocumentArrowUpIcon className="h-8 w-8" />
                  <p className="text-sm font-medium">Click to upload a file</p>
                  <p className="text-xs">PDF, images, or documents (max 10 MB)</p>
                </div>
              )}
            </div>
            <input ref={fileRef} type="file" className="hidden" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          </div>
          {/* Remarks */}
          <div>
            <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">Remarks (optional)</label>
            <textarea
              value={remarks}
              onChange={(e) => setRemarks(e.target.value)}
              rows={3}
              placeholder="Add any notes or comments for your teacher…"
              className="w-full rounded-xl border border-slate-200 dark:border-slate-600 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-700 dark:text-slate-200"
            />
          </div>
        </div>
        <div className="flex justify-end gap-3 border-t border-slate-100 dark:border-slate-700 px-6 py-4">
          <button onClick={onClose} className="rounded-xl border border-slate-200 dark:border-slate-600 px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">Cancel</button>
          <button
            onClick={handleSubmit}
            disabled={submitMutation.isPending}
            className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors disabled:opacity-50"
          >
            {submitMutation.isPending ? (
              <><svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>Submitting…</>
            ) : (
              <><DocumentArrowUpIcon className="h-4 w-4" />Submit Assignment</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Submission Detail Modal ──────────────────────────────────────────────────

function SubmissionDetailModal({
  submission,
  assessment,
  onClose,
}: {
  submission: AssessmentSubmission;
  assessment: Assessment;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div className="w-full max-w-lg rounded-2xl bg-white dark:bg-slate-800 shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 px-6 py-4">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Submission Details</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
            <XCircleIcon className="h-5 w-5" />
          </button>
        </div>
        <div className="px-6 py-4 space-y-4">
          <div>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">{assessment.title}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400">{assessment.subject_name}</p>
          </div>
          {submission.submitted_at && (
            <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
              <ClockIcon className="h-4 w-4 text-slate-400" />
              Submitted {dayjs(submission.submitted_at).format("MMM D, YYYY h:mm A")}
              {submission.is_late && <span className="rounded bg-rose-100 dark:bg-rose-900/30 px-2 py-0.5 text-xs font-medium text-rose-600 dark:text-rose-400">Late</span>}
            </div>
          )}
          {submission.file && (
            <a href={submission.file} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 px-4 py-2 text-sm font-medium text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors">
              <DocumentTextIcon className="h-4 w-4" />
              View submitted file
            </a>
          )}
          {submission.remarks && (
            <div>
              <p className="text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Your remarks</p>
              <p className="text-sm text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-900/50 rounded-lg p-3">{submission.remarks}</p>
            </div>
          )}
          {submission.marks_obtained != null && (
            <div className="rounded-xl border border-green-200 dark:border-green-800/40 bg-green-50 dark:bg-green-900/20 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-green-800 dark:text-green-300">Grade</p>
                  <p className="text-2xl font-black text-green-700 dark:text-green-400">{submission.marks_obtained} / {assessment.max_marks}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-green-800 dark:text-green-300">Percentage</p>
                  <p className="text-2xl font-black text-green-700 dark:text-green-400">{submission.percentage?.toFixed(1) ?? "—"}%</p>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="flex justify-end border-t border-slate-100 dark:border-slate-700 px-6 py-4">
          <button onClick={onClose} className="rounded-xl border border-slate-200 dark:border-slate-600 px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">Close</button>
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

type FilterTab = "pending" | "submitted" | "graded" | "all";

export default function StudentAssignmentsPage() {
  useTitle("My Assignments");
  const [filter, setFilter] = useState<FilterTab>("pending");
  const [submitTarget, setSubmitTarget] = useState<Assessment | null>(null);
  const [detailTarget, setDetailTarget] = useState<{ sub: AssessmentSubmission; assessment: Assessment } | null>(null);

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ["student-me"],
    queryFn: () => api.get<{ id: string }>("/students/me/"),
  });

  const studentId = profile?.id ?? "";
  const { data: assessmentsData, isLoading: assLoading, isError: assError, refetch: refetchAss } = useStudentAssessments(studentId);
  const { data: submissionsData, isLoading: subLoading } = useStudentSubmissions(studentId);
  const assessments = assessmentsData?.results ?? [];
  const submissions = submissionsData?.results ?? [];

  // Build a lookup map: assessment_id → submission
  const subMap = new Map<number, AssessmentSubmission>();
  submissions.forEach((s) => subMap.set(s.assessment, s));

  // Categorise
  const now = dayjs();
  const categorized = assessments.map((a) => {
    const sub = subMap.get(a.id);
    const isPastDue = now.isAfter(dayjs(a.due_date));
    let category: FilterTab;
    if (sub?.marks_obtained != null) category = "graded";
    else if (sub) category = "submitted";
    else category = "pending";
    return { assessment: a, submission: sub, category, pastDue: isPastDue };
  });

  const filtered = filter === "all" ? categorized : categorized.filter((c) => c.category === filter);

  const counts = {
    pending: categorized.filter((c) => c.category === "pending").length,
    submitted: categorized.filter((c) => c.category === "submitted").length,
    graded: categorized.filter((c) => c.category === "graded").length,
  };

  const isLoading = profileLoading || assLoading || subLoading;

  if (isLoading) return <div className="p-4"><SkeletonCard /></div>;
  if (assError) return <ErrorState onRetry={() => refetchAss()} />;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">My Assignments</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Homework, quizzes, projects, and lab work</p>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: "Pending", value: counts.pending, color: "text-amber-600 bg-amber-50 dark:bg-amber-900/20", icon: ClockIcon },
          { label: "Submitted", value: counts.submitted, color: "text-blue-600 bg-blue-50 dark:bg-blue-900/20", icon: DocumentArrowUpIcon },
          { label: "Graded", value: counts.graded, color: "text-green-600 bg-green-50 dark:bg-green-900/20", icon: CheckCircleIcon },
        ].map(({ label, value, color, icon: Icon }) => (
          <button
            key={label}
            onClick={() => setFilter(label.toLowerCase() as FilterTab)}
            className={`rounded-xl p-4 text-left ${color.split(" ").slice(2).join(" ")} transition-all hover:scale-[1.02] ${filter === label.toLowerCase() ? "ring-2 ring-indigo-500" : ""}`}
          >
            <Icon className="h-5 w-5 mb-1" />
            <p className={`text-2xl font-bold ${color.split(" ")[0]}`}>{value}</p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{label}</p>
          </button>
        ))}
      </div>

      {/* Filter tabs */}
      <div className="flex gap-2 border-b border-slate-100 dark:border-slate-700 pb-0">
        {(["pending", "submitted", "graded", "all"] as FilterTab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setFilter(tab)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              filter === tab
                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 dark:border-indigo-400"
                : "border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
            }`}
          >
            {tab === "all" ? "All" : `${tab.charAt(0).toUpperCase() + tab.slice(1)} (${counts[tab]})`}
          </button>
        ))}
      </div>

      {/* Assignment cards */}
      {filtered.length === 0 ? (
        <div className="py-12">
          <EmptyState
            icon={AcademicCapIcon}
            title={filter === "all" ? "No assignments yet" : `No ${filter} assignments`}
            description={filter === "pending" ? "You're all caught up! No pending assignments." : "Nothing to show here yet."}
          />
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {filtered.map(({ assessment, submission, category, pastDue }) => (
            <div
              key={assessment.id}
              className={clsx(
                "rounded-xl border bg-white dark:bg-slate-800 shadow-sm overflow-hidden transition-all hover:shadow-md",
                pastDue && !submission ? "border-rose-200 dark:border-rose-800/40" : "border-slate-200 dark:border-slate-700"
              )}
            >
              <div className="p-5">
                {/* Header row */}
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {typeBadge(assessment.assessment_type)}
                      {pastDue && !submission && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-rose-100 dark:bg-rose-900/30 px-2 py-0.5 text-xs font-semibold text-rose-600 dark:text-rose-400">
                          <ExclamationTriangleIcon className="h-3 w-3" />
                          Overdue
                        </span>
                      )}
                    </div>
                    <h3 className="text-base font-bold text-slate-900 dark:text-white truncate">{assessment.title}</h3>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-xs text-slate-400 dark:text-slate-500">Max marks</p>
                    <p className="text-lg font-black text-slate-700 dark:text-slate-300">{assessment.max_marks}</p>
                  </div>
                </div>

                {/* Meta */}
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400 mb-3">
                  <span className="flex items-center gap-1">
                    <AcademicCapIcon className="h-3.5 w-3.5" />
                    {assessment.subject_name}
                  </span>
                  <span className="flex items-center gap-1">
                    <ClockIcon className="h-3.5 w-3.5" />
                    Due {dayjs(assessment.due_date).format("MMM D, YYYY")}
                  </span>
                  <span className="text-slate-300 dark:text-slate-600">·</span>
                  <span>{assessment.classroom_name}</span>
                </div>

                {/* Description */}
                {assessment.description && (
                  <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-2 mb-3">{assessment.description}</p>
                )}

                {/* Teacher attachment */}
                {assessment.attachment && (
                  <a href={assessment.attachment} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1.5 text-xs font-medium text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors mb-3">
                    <DocumentTextIcon className="h-3.5 w-3.5" />
                    View attachment
                  </a>
                )}

                {/* Footer */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-700">
                  {statusBadge(submission, assessment.max_marks)}
                  <div className="flex gap-2">
                    {submission && (
                      <button
                        onClick={() => setDetailTarget({ sub: submission, assessment })}
                        className="rounded-lg border border-slate-200 dark:border-slate-600 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                      >
                        View
                      </button>
                    )}
                    {!submission && (
                      <button
                        onClick={() => setSubmitTarget(assessment)}
                        className="inline-flex items-center gap-1 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 transition-colors"
                      >
                        <DocumentArrowUpIcon className="h-3.5 w-3.5" />
                        Submit
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      {submitTarget && <SubmitModal assessment={submitTarget} onClose={() => setSubmitTarget(null)} />}
      {detailTarget && (
        <SubmissionDetailModal
          submission={detailTarget.sub}
          assessment={detailTarget.assessment}
          onClose={() => setDetailTarget(null)}
        />
      )}
    </div>
  );
}
