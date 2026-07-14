/**
 * TeacherAssignmentsPage
 *
 * Teachers can create homework/quizzes/projects, view student submissions,
 * and grade them with marks and feedback.
 */
import React, { useState } from "react";
import {
  PlusIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  AcademicCapIcon,
  UsersIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  StarIcon,
} from "@heroicons/react/24/outline";
import {
  useTeacherAssessments,
  useCreateAssessment,
  useAssignmentSubmissions,
  useGradeSubmission,
  useTeacherAssignmentList,
} from "../../api/hooks";
import { Badge, EmptyState, SkeletonCard, ErrorState } from "../../components/common";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import toast from "react-hot-toast";
import clsx from "clsx";
import dayjs from "dayjs";
import type { Assessment, AssessmentSubmission, AssessmentType, TeacherAssignment } from "../../types";

// ─── Constants ────────────────────────────────────────────────────────────────

const ASSESSMENT_TYPES: { value: AssessmentType; label: string; icon: string }[] = [
  { value: "homework", label: "Homework", icon: "📝" },
  { value: "quiz", label: "Quiz", icon: "❓" },
  { value: "project", label: "Project", icon: "📊" },
  { value: "classwork", label: "Class Work", icon: "📋" },
  { value: "lab", label: "Lab Work", icon: "🔬" },
];

const TYPE_COLORS: Record<AssessmentType, string> = {
  homework:  "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  quiz:      "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
  project:   "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  classwork: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
  lab:       "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300",
};

// ─── Create Assessment Modal ──────────────────────────────────────────────────

function CreateAssessmentModal({ onClose }: { onClose: () => void }) {
  const [title, setTitle] = useState("");
  const [type, setType] = useState<AssessmentType>("homework");
  const [dueDate, setDueDate] = useState(dayjs().add(7, "day").format("YYYY-MM-DD"));
  const [maxMarks, setMaxMarks] = useState(100);
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [assignmentId, setAssignmentId] = useState<number | "">("");
  const createMutation = useCreateAssessment();
  const { data: assignments = [] } = useTeacherAssignmentList();

  const handleCreate = async () => {
    if (!title.trim()) { toast.error("Title is required."); return; }
    if (!assignmentId) { toast.error("Please select a class and subject."); return; }
    const fd = new FormData();
    fd.append("title", title.trim());
    fd.append("assessment_type", type);
    fd.append("due_date", dueDate);
    fd.append("max_marks", String(maxMarks));
    fd.append("description", description.trim());
    fd.append("assignment", String(assignmentId));
    if (file) fd.append("attachment", file);
    try {
      await createMutation.mutateAsync(fd);
      toast.success("Assessment created!");
      onClose();
    } catch {
      toast.error("Failed to create assessment.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div className="w-full max-w-xl rounded-2xl bg-white dark:bg-slate-800 shadow-2xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 px-6 py-4">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Create Assessment</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
            <XCircleIcon className="h-5 w-5" />
          </button>
        </div>
        <div className="px-6 py-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Title *</label>
              <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Chapter 5 Homework" className="w-full rounded-xl border border-slate-200 dark:border-slate-600 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-700 dark:text-slate-200" />
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Class & Subject *</label>
              <select value={assignmentId} onChange={(e) => setAssignmentId(e.target.value ? Number(e.target.value) : "")} className="w-full rounded-xl border border-slate-200 dark:border-slate-600 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-700 dark:text-slate-200">
                <option value="">Select a class and subject…</option>
                {assignments.map((a: TeacherAssignment) => (
                  <option key={a.id} value={a.id}>{a.subject_name} — {a.classroom_name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Type *</label>
              <select value={type} onChange={(e) => setType(e.target.value as AssessmentType)} className="w-full rounded-xl border border-slate-200 dark:border-slate-600 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-700 dark:text-slate-200">
                {ASSESSMENT_TYPES.map((t) => <option key={t.value} value={t.value}>{t.icon} {t.label}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Due Date *</label>
              <input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} className="w-full rounded-xl border border-slate-200 dark:border-slate-600 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-700 dark:text-slate-200" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Max Marks</label>
              <input type="number" min={1} max={1000} value={maxMarks} onChange={(e) => setMaxMarks(Number(e.target.value))} className="w-full rounded-xl border border-slate-200 dark:border-slate-600 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-700 dark:text-slate-200" />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Attachment (optional)</label>
              <input type="file" onChange={(e) => setFile(e.target.files?.[0] ?? null)} className="w-full text-sm text-slate-500 file:mr-3 file:rounded-lg file:border-0 file:bg-indigo-50 file:px-3 file:py-1.5 file:text-xs file:font-semibold file:text-indigo-700 hover:file:bg-indigo-100 dark:file:bg-indigo-900/30 dark:file:text-indigo-300" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1">Description</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={4} placeholder="Describe the assignment, instructions, and expectations…" className="w-full rounded-xl border border-slate-200 dark:border-slate-600 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-700 dark:text-slate-200" />
          </div>
        </div>
        <div className="flex justify-end gap-3 border-t border-slate-100 dark:border-slate-700 px-6 py-4">
          <button onClick={onClose} className="rounded-xl border border-slate-200 dark:border-slate-600 px-4 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">Cancel</button>
          <button onClick={handleCreate} disabled={createMutation.isPending} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors disabled:opacity-50">
            {createMutation.isPending ? "Creating…" : "Create Assessment"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Grade Modal ──────────────────────────────────────────────────────────────

function GradeModal({
  assessment,
  onClose,
}: {
  assessment: Assessment;
  onClose: () => void;
}) {
  const { data: subsData, isLoading } = useAssignmentSubmissions(assessment.id);
  const submissions = subsData?.results ?? [];
  const [grades, setGrades] = useState<Record<number, string>>({});
  const [remarks, setRemarks] = useState<Record<number, string>>({});
  const gradeMutation = useGradeSubmission();
  const [saving, setSaving] = useState<number | null>(null);

  const handleGrade = async (sub: AssessmentSubmission) => {
    const marks = parseFloat(grades[sub.id] as string);
    if (isNaN(marks) || marks < 0) { toast.error("Enter valid marks"); return; }
    setSaving(sub.id);
    try {
      await gradeMutation.mutateAsync({ id: sub.id, marks_obtained: marks, remarks: remarks[sub.id] });
      toast.success("Graded!");
    } catch { toast.error("Failed to save grade."); }
    finally { setSaving(null); }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={onClose}>
      <div className="w-full max-w-2xl rounded-2xl bg-white dark:bg-slate-800 shadow-2xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-700 px-6 py-4 sticky top-0 bg-white dark:bg-slate-800 z-10">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">Grade Submissions</h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">{assessment.title}</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
            <XCircleIcon className="h-5 w-5" />
          </button>
        </div>
        <div className="p-6">
          {isLoading ? (
            <SkeletonCard />
          ) : submissions.length === 0 ? (
            <EmptyState icon={UsersIcon} title="No submissions yet" description="Students haven't submitted anything for this assessment." />
          ) : (
            <table className="w-full">
              <thead>
                <tr className="text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase border-b border-slate-100 dark:border-slate-700">
                  <th className="pb-2 pr-4">Student</th>
                  <th className="pb-2 pr-4">Status</th>
                  <th className="pb-2 pr-4 w-24">Marks</th>
                  <th className="pb-2 w-40">Feedback</th>
                  <th className="pb-2 w-16">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50 dark:divide-slate-800">
                {submissions.map((sub) => (
                  <tr key={sub.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30 transition-colors">
                    <td className="py-3 pr-4">
                      <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{sub.student_name}</p>
                    </td>
                    <td className="py-3 pr-4">
                      {sub.marks_obtained != null ? (
                        <span className="inline-flex items-center gap-1 rounded-full bg-green-50 dark:bg-green-900/20 px-2 py-0.5 text-xs font-semibold text-green-700 dark:text-green-400">
                          <CheckCircleIcon className="h-3 w-3" />
                          Graded
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 dark:bg-amber-900/20 px-2 py-0.5 text-xs font-semibold text-amber-700 dark:text-amber-400">
                          <ClockIcon className="h-3 w-3" />
                          Pending
                        </span>
                      )}
                      {sub.is_late && <span className="ml-1 text-xs text-rose-500">(late)</span>}
                    </td>
                    <td className="py-3 pr-4">
                      {sub.marks_obtained != null ? (
                        <span className="text-sm font-bold">{sub.marks_obtained}<span className="text-slate-400 font-normal">/{assessment.max_marks}</span></span>
                      ) : (
                        <div className="flex items-center gap-1">
                          <input
                            type="number" min={0} max={assessment.max_marks}
                            placeholder="—"
                            value={grades[sub.id] ?? ""}
                            onChange={(e) => setGrades((g) => ({ ...g, [sub.id]: e.target.value }))}
                            className="w-20 rounded-lg border border-slate-200 dark:border-slate-600 px-2 py-1 text-sm text-center focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-700 dark:text-slate-200"
                          />
                          <span className="text-xs text-slate-400">/{assessment.max_marks}</span>
                        </div>
                      )}
                    </td>
                    <td className="py-3">
                      <input
                        type="text" placeholder={sub.marks_obtained != null ? sub.remarks || "—" : "Feedback…"}
                        value={remarks[sub.id] ?? sub.remarks ?? ""}
                        onChange={(e) => setRemarks((r) => ({ ...r, [sub.id]: e.target.value }))}
                        disabled={sub.marks_obtained != null}
                        className="w-full rounded-lg border border-slate-200 dark:border-slate-600 px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-slate-700 dark:text-slate-200 disabled:bg-slate-50 disabled:text-slate-400 disabled:dark:bg-slate-800"
                      />
                    </td>
                    <td className="py-3">
                      {sub.marks_obtained == null ? (
                        <button onClick={() => handleGrade(sub)} disabled={saving === sub.id} className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500 transition-colors disabled:opacity-50">
                          {saving === sub.id ? "…" : "Grade"}
                        </button>
                      ) : (
                        <span className="text-xs text-green-600 flex items-center gap-1"><CheckCircleIcon className="h-3.5 w-3.5" />Done</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function TeacherAssignmentsPage() {
  useTitle("Assignments");
  const [showCreate, setShowCreate] = useState(false);
  const [gradeTarget, setGradeTarget] = useState<Assessment | null>(null);
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  const { data: assData, isLoading, isError, refetch } = useTeacherAssessments();
  const assessments = assData?.results ?? [];

  const toggleExpand = (id: number) => setExpanded((e) => ({ ...e, [id]: !e[id] }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Assignments</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Create and manage homework, quizzes, and projects</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors">
          <PlusIcon className="h-4 w-4" />
          Create
        </button>
      </div>

      {/* Stats */}
      {assessments.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { label: "Total", value: assessments.length, color: "text-slate-600 bg-slate-50 dark:bg-slate-800" },
            { label: "Homework", value: assessments.filter((a) => a.assessment_type === "homework").length, color: "text-blue-600 bg-blue-50 dark:bg-blue-900/20" },
            { label: "Quizzes", value: assessments.filter((a) => a.assessment_type === "quiz").length, color: "text-purple-600 bg-purple-50 dark:bg-purple-900/20" },
            { label: "Projects", value: assessments.filter((a) => a.assessment_type === "project").length, color: "text-amber-600 bg-amber-50 dark:bg-amber-900/20" },
          ].map(({ label, value, color }) => (
            <div key={label} className={`rounded-xl px-4 py-3 ${color.split(" ").slice(2).join(" ")}`}>
              <p className={`text-xl font-bold ${color.split(" ")[0]}`}>{value}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* List */}
      {isLoading ? (
        <SkeletonCard />
      ) : isError ? (
        <ErrorState onRetry={() => refetch()} />
      ) : assessments.length === 0 ? (
        <EmptyState
          icon={AcademicCapIcon}
          title="No assignments yet"
          description="Create your first homework, quiz, or project for your students."
          action={
            <button onClick={() => setShowCreate(true)} className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors">
              <PlusIcon className="h-4 w-4" />
              Create Assessment
            </button>
          }
        />
      ) : (
        <div className="space-y-3">
          {assessments.map((ass) => (
            <div key={ass.id} className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-sm overflow-hidden">
              <button onClick={() => toggleExpand(ass.id)} className="w-full flex items-center justify-between p-5 hover:bg-slate-50/50 dark:hover:bg-slate-700/30 transition-colors text-left">
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${TYPE_COLORS[ass.assessment_type]}`}>{ass.assessment_type.charAt(0).toUpperCase() + ass.assessment_type.slice(1)}</span>
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-slate-900 dark:text-white truncate">{ass.title}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">{ass.subject_name} · {ass.classroom_name} · Due {dayjs(ass.due_date).format("MMM D")}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className="text-xs font-medium text-slate-500 dark:text-slate-400">{ass.max_marks} marks</span>
                  {expanded[ass.id] ? <ChevronUpIcon className="h-4 w-4 text-slate-400" /> : <ChevronDownIcon className="h-4 w-4 text-slate-400" />}
                </div>
              </button>

              {expanded[ass.id] && (
                <div className="px-5 pb-5 border-t border-slate-100 dark:border-slate-700 pt-4 space-y-3">
                  {ass.description && <p className="text-sm text-slate-600 dark:text-slate-300">{ass.description}</p>}
                  {ass.attachment && (
                    <a href={ass.attachment} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 px-3 py-1.5 text-xs font-medium text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors">
                      <DocumentTextIcon className="h-3.5 w-3.5" />
                      View attachment
                    </a>
                  )}
                  <button onClick={() => setGradeTarget(ass)} className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-emerald-500 transition-colors">
                    <StarIcon className="h-4 w-4" />
                    Grade Submissions
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showCreate && <CreateAssessmentModal onClose={() => setShowCreate(false)} />}
      {gradeTarget && <GradeModal assessment={gradeTarget} onClose={() => setGradeTarget(null)} />}
    </div>
  );
}
