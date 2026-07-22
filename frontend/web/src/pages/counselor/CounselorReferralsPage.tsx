/**
 * Counselor Referrals Page — Manage teacher-to-counselor student referrals
 * - Status & priority filters
 * - Create referral modal
 * - Assign to counselor modal
 * - Action Taken modal (record outcome/intervention plan)
 * - Close/Reopen actions
 * - Detail modal for full view
 */

import React, { useState, useMemo, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import {
  PlusIcon, FunnelIcon, MagnifyingGlassIcon,
  CheckCircleIcon, XCircleIcon, ClockIcon,
  PencilIcon, ArrowRightIcon, ExclamationTriangleIcon,
  UserGroupIcon, ShieldExclamationIcon, SparklesIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Spinner, Badge } from "../../components/common";
import { useAuthStore } from "../../store/authStore";
import type { StudentReferral } from "../../types";
import {
  useCounselingReferrals, useCreateReferral,
  useActionReferral, useCloseReferral,
  useReopenReferral,
} from "../../api/hooks";

dayjs.extend(relativeTime);

// ─── Constants ────────────────────────────────────────────────────────────────

const CATEGORIES = [
  { value: "academic", label: "📚 Academic Concern", color: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300" },
  { value: "attendance", label: "📅 Attendance Issue", color: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300" },
  { value: "behavior", label: "⚠️ Behavioral Concern", color: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300" },
  { value: "emotional", label: "❤️ Emotional / Mental Health", color: "bg-pink-100 text-pink-700 dark:bg-pink-900/40 dark:text-pink-300" },
  { value: "family", label: "🏠 Family / Home Issue", color: "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300" },
  { value: "social", label: "👥 Social / Peer Issue", color: "bg-teal-100 text-teal-700 dark:bg-teal-900/40 dark:text-teal-300" },
  { value: "safety", label: "🛡️ Safety Concern", color: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300" },
  { value: "other", label: "📋 Other", color: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400" },
] as const;

const PRIORITY_CONFIG = {
  low:    { label: "Low",    color: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400", icon: ClockIcon },
  medium: { label: "Medium", color: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300", icon: ExclamationTriangleIcon },
  high:   { label: "High",   color: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300", icon: ExclamationTriangleIcon },
  urgent: { label: "Urgent", color: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300", icon: ShieldExclamationIcon },
} as const;

const STATUS_CONFIG = {
  pending:     { label: "Pending Review",     color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300" },
  under_review:{ label: "Under Review",       color: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300" },
  contacted:   { label: "Student Contacted",  color: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300" },
  actioned:    { label: "Action Taken",       color: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300" },
  closed:      { label: "Closed",             color: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400" },
  declined:    { label: "Declined",           color: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300" },
} as const;

// ─── Stats Bar ────────────────────────────────────────────────────────────────

function ReferralStatsBar({ referrals }: { referrals: StudentReferral[] }) {
  const pending = referrals.filter(r => r.status === "pending" || r.status === "under_review" || r.status === "contacted").length;
  const urgent = referrals.filter(r => r.priority === "urgent" && r.status !== "closed" && r.status !== "declined").length;
  const actioned = referrals.filter(r => r.status === "actioned" || r.status === "closed").length;
  const total = referrals.length;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {[
        { label: "Pending", value: pending, color: "text-amber-600 dark:text-amber-400" },
        { label: "Urgent", value: urgent, color: "text-red-600 dark:text-red-400" },
        { label: "Resolved", value: actioned, color: "text-green-600 dark:text-green-400" },
        { label: "Total", value: total, color: "text-rose-600 dark:text-rose-400" },
      ].map(s => (
        <div key={s.label} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3 sm:p-4">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">{s.label}</p>
          <p className={`mt-1 text-xl sm:text-2xl font-bold ${s.color}`}>{s.value}</p>
        </div>
      ))}
    </div>
  );
}

// ─── Create Referral Modal ──────────────────────────────────────────────────

function CreateReferralModal({
  open, onClose, onSaved,
}: {
  open: boolean; onClose: () => void; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    student: "",
    category: "academic" as string,
    priority: "medium" as string,
    reason: "",
    notes: "",
    is_confidential: false,
    notify_counselor: true,
  });
  const [studentSearch, setStudentSearch] = useState("");
  const [studentResults, setStudentResults] = useState<Array<{ id: string; full_name: string; classroom?: { name: string; grade: { name: string } } }>>([]);
  const [searching, setSearching] = useState(false);

  const createMut = useCreateReferral();

  const handleStudentSearch = useCallback(async (q: string) => {
    setStudentSearch(q);
    if (q.length < 2) { setStudentResults([]); return; }
    setSearching(true);
    try {
      const res = await api.get<{ results: any[] }>("/students/students/", { search: q, page_size: 8 });
      setStudentResults(res.results ?? []);
    } catch { setStudentResults([]); }
    finally { setSearching(false); }
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.student) return toast.error("Please select a student");
    if (form.reason.trim().length < 10) return toast.error("Reason must be at least 10 characters");

    createMut.mutate({
      student: form.student,
      category: form.category,
      priority: form.priority as "low" | "medium" | "high" | "urgent",
      reason: form.reason,
      notes: form.notes,
      is_confidential: form.is_confidential,
      notify_counselor: form.notify_counselor,
    }, { onSuccess: () => onSaved() });
  };

  return (
    <Modal open={open} onClose={onClose} title="Create Referral"
      description="Refer a student to the counseling department for support"
      size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Student *</label>
          <input value={studentSearch} onChange={e => handleStudentSearch(e.target.value)}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
            placeholder="Search student by name..." autoComplete="off" />
          {searching && <Spinner size="sm" className="mt-1" />}
          {studentSearch.length >= 2 && !form.student && studentResults.length > 0 && (
            <div className="mt-1 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 shadow-lg max-h-48 overflow-y-auto">
              {studentResults.map(s => (
                <button key={s.id} type="button"
                  onClick={() => { setForm(p => ({ ...p, student: s.id })); setStudentSearch(s.full_name); setStudentResults([]); }}
                  className="w-full text-left px-3 py-2.5 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 dark:text-slate-200 border-b border-slate-50 dark:border-slate-700 last:border-0">
                  <span className="font-medium">{s.full_name}</span>
                  {s.classroom && <span className="text-xs text-slate-400 ml-2">{s.classroom.grade?.name} — {s.classroom.name}</span>}
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Category</label>
            <select value={form.category} onChange={e => setForm(p => ({ ...p, category: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200">
              {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Priority</label>
            <select value={form.priority} onChange={e => setForm(p => ({ ...p, priority: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Reason * <span className="text-xs text-slate-400">(min 10 chars)</span></label>
          <textarea value={form.reason} onChange={e => setForm(p => ({ ...p, reason: e.target.value }))}
            rows={3}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
            placeholder="Describe why this student is being referred..." />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Additional Notes</label>
          <textarea value={form.notes} onChange={e => setForm(p => ({ ...p, notes: e.target.value }))}
            rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
            placeholder="Any additional context or observations..." />
        </div>

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.is_confidential}
              onChange={e => setForm(p => ({ ...p, is_confidential: e.target.checked }))}
              className="rounded border-slate-300 text-rose-600 focus:ring-rose-500" />
            <span className="text-sm text-slate-700 dark:text-slate-300">Confidential</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.notify_counselor}
              onChange={e => setForm(p => ({ ...p, notify_counselor: e.target.checked }))}
              className="rounded border-slate-300 text-rose-600 focus:ring-rose-500" />
            <span className="text-sm text-slate-700 dark:text-slate-300">Notify counselor</span>
          </label>
        </div>

        <div className="flex justify-end gap-3 pt-2 border-t border-slate-100 dark:border-slate-700">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={createMut.isPending}>Create Referral</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Action Taken Modal ─────────────────────────────────────────────────────

function ActionTakenModal({
  open, onClose, referral, onSaved,
}: {
  open: boolean; onClose: () => void; referral: StudentReferral; onSaved: () => void;
}) {
  const [outcome, setOutcome] = useState("");
  const [interventionPlan, setInterventionPlan] = useState(referral.intervention_plan || "");
  const [followUpDate, setFollowUpDate] = useState(referral.follow_up_date || "");
  const actionMut = useActionReferral();
  const closeMut = useCloseReferral();
  const [action, setAction] = useState<"action" | "close">("action");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (action === "action") {
      actionMut.mutate({
        id: referral.id,
        outcome: outcome.trim() || undefined,
        intervention_plan: interventionPlan.trim() || undefined,
      }, { onSuccess: () => onSaved() });
    } else {
      closeMut.mutate(referral.id, { onSuccess: () => onSaved() });
    }
  };

  return (
    <Modal open={open} onClose={onClose} title="Record Action"
      description={`Follow up on referral for ${referral.student_name}`}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex gap-2 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 mb-2">
          <button type="button" onClick={() => setAction("action")}
            className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              action === "action" ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm" : "text-slate-600"
            }`}>
            <CheckCircleIcon className="h-4 w-4 inline mr-1" /> Action Taken
          </button>
          <button type="button" onClick={() => setAction("close")}
            className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              action === "close" ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm" : "text-slate-600"
            }`}>
            <XCircleIcon className="h-4 w-4 inline mr-1" /> Close Referral
          </button>
        </div>

        {action === "action" && (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Outcome</label>
              <textarea value={outcome} onChange={e => setOutcome(e.target.value)}
                rows={3}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
                placeholder="Describe the outcome of the intervention..." autoFocus />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Intervention Plan</label>
              <textarea value={interventionPlan} onChange={e => setInterventionPlan(e.target.value)}
                rows={2}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
                placeholder="Proposed intervention plan..." />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Follow-up Date</label>
              <input type="date" value={followUpDate} onChange={e => setFollowUpDate(e.target.value)}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200" />
            </div>
          </>
        )}

        {action === "close" && (
          <p className="text-sm text-slate-600 dark:text-slate-400 bg-amber-50 dark:bg-amber-900/30 p-3 rounded-lg">
            <ExclamationTriangleIcon className="h-4 w-4 inline mr-1 text-amber-500" />
            Closing this referral will mark it as resolved. Make sure all necessary actions have been documented.
          </p>
        )}

        <div className="flex justify-end gap-3 pt-2 border-t border-slate-100 dark:border-slate-700">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={actionMut.isPending || closeMut.isPending}>
            {action === "action" ? "Record Action" : "Close Referral"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Referral Detail Modal ──────────────────────────────────────────────────

function ReferralDetailModal({
  open, onClose, referral, onAction, onCloseReferral, onReopen,
  isClosing, isReopening,
}: {
  open: boolean; onClose: () => void; referral: StudentReferral;
  onAction: (r: StudentReferral) => void;
  onCloseReferral: (r: StudentReferral) => void;
  onReopen: (r: StudentReferral) => void;
  isClosing?: boolean;
  isReopening?: boolean;
}) {
  const catConfig = CATEGORIES.find(c => c.value === referral.category);
  const priConfig = PRIORITY_CONFIG[referral.priority];
  const staConfig = STATUS_CONFIG[referral.status];
  const isActive = ["pending", "under_review", "contacted"].includes(referral.status);
  const isClosed = referral.status === "closed";

  return (
    <Modal open={open} onClose={onClose} title="Referral Details" size="md">
      <div className="space-y-4">
        {/* Status badges */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${staConfig.color}`}>
            {staConfig.label}
          </span>
          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${priConfig.color}`}>
            <priConfig.icon className="h-3 w-3" />
            {priConfig.label} Priority
          </span>
          <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${catConfig?.color ?? ""}`}>
            {catConfig?.label ?? referral.category}
          </span>
          {referral.is_confidential && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-700">
              🔒 Confidential
            </span>
          )}
        </div>

        {/* Student & Referrer */}
        <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50 dark:bg-slate-700/30 rounded-lg">
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Student</p>
            <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-white">{referral.student_name}</p>
            {(referral.student_grade || referral.student_class) && (
              <p className="text-xs text-slate-500">{referral.student_grade}{referral.student_grade && referral.student_class ? " — " : ""}{referral.student_class}</p>
            )}
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Referred By</p>
            <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-white">{referral.referred_by_name || "—"}</p>
          </div>
        </div>

        {/* Assignee */}
        {referral.assigned_to_name && (
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Assigned To</p>
            <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-white">{referral.assigned_to_name}</p>
          </div>
        )}

        {/* Reason */}
        <div>
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Reason</p>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-700/30 p-3 rounded-lg">{referral.reason}</p>
        </div>

        {/* Notes */}
        {referral.notes && (
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Notes</p>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-700/30 p-3 rounded-lg">{referral.notes}</p>
          </div>
        )}

        {/* Intervention Plan */}
        {referral.intervention_plan && (
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Intervention Plan</p>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400 bg-green-50 dark:bg-green-900/20 p-3 rounded-lg">{referral.intervention_plan}</p>
          </div>
        )}

        {/* Outcome */}
        {referral.outcome && (
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Outcome</p>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400 bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg">{referral.outcome}</p>
          </div>
        )}

        {/* Created */}
        <p className="text-xs text-slate-400">Created {dayjs(referral.created_at).format("MMM D, YYYY [at] h:mm A")} · {dayjs(referral.created_at).fromNow()}</p>

        {/* Actions */}
        <div className="flex flex-wrap gap-2 pt-3 border-t border-slate-100 dark:border-slate-700">
          {isActive && (
            <>
              <Button size="sm" onClick={() => { onClose(); onAction(referral); }}>
                <CheckCircleIcon className="h-4 w-4" /> Record Action
              </Button>
              <Button size="sm" variant="danger" onClick={() => { onCloseReferral(referral); }} disabled={isClosing}>
                <XCircleIcon className="h-4 w-4" /> Close
              </Button>
            </>
          )}
          {isClosed && (
            <Button size="sm" variant="secondary" onClick={() => { onReopen(referral); }} disabled={isReopening}>
              <SparklesIcon className="h-4 w-4" /> Reopen
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
}

// ─── Main Page ─────────────────────────────────────────────────────────────

export default function CounselorReferralsPage() {
  const qc = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [priorityFilter, setPriorityFilter] = useState<string>("all");
  const [search, setSearch] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [detailRef, setDetailRef] = useState<StudentReferral | null>(null);
  const [actionRef, setActionRef] = useState<StudentReferral | null>(null);

  const closeMut = useCloseReferral();
  const reopenMut = useReopenReferral();

  const { data: refsResponse, isLoading } = useCounselingReferrals(
    statusFilter !== "all" || priorityFilter !== "all"
      ? { ...(statusFilter !== "all" && { status: statusFilter }), ...(priorityFilter !== "all" && { priority: priorityFilter }) }
      : undefined
  );
  const referrals = refsResponse?.results ?? [];

  // Filtered + searched
  const filtered = useMemo(() => {
    let items = referrals;
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(r =>
        r.student_name?.toLowerCase().includes(q) ||
        r.referred_by_name?.toLowerCase().includes(q) ||
        r.reason?.toLowerCase().includes(q) ||
        r.category?.toLowerCase().includes(q)
      );
    }
    return items;
  }, [referrals, search]);

  const handleAction = useCallback(async (ref: StudentReferral) => {
    setActionRef(ref);
  }, []);

  const handleClose = useCallback(async (ref: StudentReferral) => {
    if (!confirm(`Close referral for ${ref.student_name}?`)) return;
    closeMut.mutate(ref.id, { onSuccess: refreshAll });
  }, [closeMut]);

  const handleReopen = useCallback(async (ref: StudentReferral) => {
    reopenMut.mutate(ref.id, { onSuccess: refreshAll });
  }, [reopenMut]);

  const refreshAll = () => {
    qc.invalidateQueries({ queryKey: ["counseling"] });
    qc.invalidateQueries({ queryKey: ["counselor-dashboard"] });
    setShowCreateForm(false);
    setActionRef(null);
    setDetailRef(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Student Referrals</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Review and manage teacher referrals, take action, and track student outcomes
          </p>
        </div>
        <Button onClick={() => setShowCreateForm(true)}>
          <PlusIcon className="h-4 w-4 mr-1.5" /> New Referral
        </Button>
      </div>

      {/* Stats */}
      <ReferralStatsBar referrals={referrals} />

      {/* Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        {/* Status pills */}
        <div className="flex flex-wrap gap-1.5">
          {(["all", "pending", "under_review", "actioned", "closed"] as const).map(s => (
            <button key={s} onClick={() => setStatusFilter(s)}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                statusFilter === s
                  ? "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300"
                  : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-200"
              }`}>
              {s === "all" ? "All" : STATUS_CONFIG[s]?.label ?? s}
            </button>
          ))}
        </div>

        {/* Priority */}
        <div className="flex flex-wrap gap-1.5">
          {(["all", "urgent", "high", "medium", "low"] as const).map(p => (
            <button key={p} onClick={() => setPriorityFilter(p)}
              className={`px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                priorityFilter === p
                  ? "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300"
                  : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-200"
              }`}>
              {p === "all" ? "All Priority" : p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
          ))}
        </div>

        <div className="sm:ml-auto relative flex-1 max-w-xs">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input value={search} onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm dark:text-slate-200"
            placeholder="Search by student, reason..." />
        </div>
      </div>

      {/* Referral List */}
      {isLoading ? (
        <div className="space-y-3">{[1,2,3,4].map(i => <div key={i} className="h-24 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse" />)}</div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={UserGroupIcon} title="No referrals found"
          description={search ? "Try a different search term" : "No referrals yet. Teachers can refer students here."}
          action={<Button onClick={() => setShowCreateForm(true)}><PlusIcon className="h-4 w-4 mr-1" /> New Referral</Button>} />
      ) : (
        <div className="space-y-2">
          {filtered
            .sort((a, b) => {
              const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };
              return (priorityOrder[a.priority] ?? 99) - (priorityOrder[b.priority] ?? 99);
            })
            .map(ref => {
              const catConfig = CATEGORIES.find(c => c.value === ref.category);
              const priConfig = PRIORITY_CONFIG[ref.priority];
              const staConfig = STATUS_CONFIG[ref.status];
              const isActive = ["pending", "under_review", "contacted"].includes(ref.status);
              return (
                <div key={ref.id}
                  onClick={() => setDetailRef(ref)}
                  className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-rose-300 dark:hover:border-rose-600 hover:shadow-md transition-all cursor-pointer group">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-1.5 flex-wrap">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${staConfig.color}`}>
                          {staConfig.label}
                        </span>
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${priConfig.color}`}>
                          <priConfig.icon className="h-3 w-3" />
                          {priConfig.label}
                        </span>
                        {catConfig && (
                          <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${catConfig.color}`}>
                            {catConfig.label}
                          </span>
                        )}
                        {ref.is_confidential && <span className="text-xs text-purple-500">🔒</span>}
                      </div>
                      <p className="font-semibold text-slate-900 dark:text-white group-hover:text-rose-600 dark:group-hover:text-rose-400 transition-colors">
                        {ref.student_name}
                      </p>
                      <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-1">{ref.reason}</p>
                      <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-400">
                        <span>By: {ref.referred_by_name || "—"}</span>
                        {ref.assigned_to_name && <span>To: {ref.assigned_to_name}</span>}
                        <span>{dayjs(ref.created_at).fromNow()}</span>
                      </div>
                    </div>
                    {isActive && (
                      <div className="flex gap-1 ml-4" onClick={e => e.stopPropagation()}>
                        <button onClick={() => handleAction(ref)}
                          className="p-2 rounded-lg text-green-600 hover:bg-green-50 dark:hover:bg-green-900/30 transition-colors"
                          title="Record action">
                          <CheckCircleIcon className="h-4 w-4" />
                        </button>
                        <button onClick={() => handleClose(ref)}
                          className="p-2 rounded-lg text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
                          title="Close">
                          <XCircleIcon className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
        </div>
      )}

      {/* Modals */}
      {showCreateForm && (
        <CreateReferralModal
          open={showCreateForm} onClose={() => setShowCreateForm(false)} onSaved={refreshAll} />
      )}

      {actionRef && !showCreateForm && (
        <ActionTakenModal
          open={!!actionRef} onClose={() => setActionRef(null)}
          referral={actionRef} onSaved={refreshAll} />
      )}

      {detailRef && !actionRef && !showCreateForm && (
        <ReferralDetailModal
          open={!!detailRef} onClose={() => setDetailRef(null)}
          referral={detailRef}
          onAction={(r) => { setDetailRef(null); setActionRef(r); }}
          onCloseReferral={(r) => { setDetailRef(null); handleClose(r); }}
          onReopen={(r) => { setDetailRef(null); handleReopen(r); }}
          isClosing={closeMut.isPending}
          isReopening={reopenMut.isPending}
        />
      )}
    </div>
  );
}
