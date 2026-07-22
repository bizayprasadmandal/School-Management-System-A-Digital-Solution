/**
 * Counselor Appointments Page — Full booking workflow
 * - Today's schedule highlight
 * - Upcoming / past / all appointment views with status filters
 * - Create appointment modal with student search
 * - Complete appointment modal (add session notes)
 * - Cancel, No-Show action buttons
 * - Dashboard-like stats summary
 */

import React, { useState, useMemo, useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import isBetween from "dayjs/plugin/isBetween";
import relativeTime from "dayjs/plugin/relativeTime";
import {
  PlusIcon, FunnelIcon, MagnifyingGlassIcon,
  CalendarDaysIcon, CheckCircleIcon, XCircleIcon,
  ClockIcon, PencilIcon, ArrowRightIcon,
  VideoCameraIcon, ChevronLeftIcon, ChevronRightIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Spinner, Badge } from "../../components/common";
import { useAuthStore } from "../../store/authStore";
import type { CounselingAppointment, CounselingAppointmentStatus, CounselingAppointmentType } from "../../types";
import { useCounselingAppointments, useCreateCounselingAppointment, useUpdateCounselingAppointment, useCompleteAppointment, useCancelAppointment, useNoShowAppointment } from "../../api/hooks";

dayjs.extend(isBetween);
dayjs.extend(relativeTime);

// ─── Constants ────────────────────────────────────────────────────────────────

const APPOINTMENT_TYPES = [
  { value: "academic", label: "📚 Academic Counseling" },
  { value: "career", label: "💼 Career Guidance" },
  { value: "personal", label: "❤️ Personal / Emotional" },
  { value: "behavioral", label: "⚠️ Behavioral Intervention" },
  { value: "college", label: "🎓 College Preparation" },
  { value: "group", label: "👥 Group Session" },
  { value: "other", label: "📋 Other" },
] as const;

const STATUS_CONFIG: Record<CounselingAppointmentStatus, { label: string; color: string; icon: React.ComponentType<{ className?: string }> }> = {
  scheduled:    { label: "Scheduled",    color: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300", icon: ClockIcon },
  in_progress:  { label: "In Progress",  color: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300", icon: ClockIcon },
  completed:    { label: "Completed",    color: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300", icon: CheckCircleIcon },
  cancelled:    { label: "Cancelled",    color: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300", icon: XCircleIcon },
  no_show:      { label: "No Show",      color: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400", icon: XCircleIcon },
};

// ─── Today's Schedule ─────────────────────────────────────────────────────────

function TodaySchedule({
  appointments,
  onComplete,
  onCancel,
  onNoShow,
  onEdit,
}: {
  appointments: CounselingAppointment[];
  onComplete: (a: CounselingAppointment) => void;
  onCancel: (a: CounselingAppointment) => void;
  onNoShow: (a: CounselingAppointment) => void;
  onEdit: (a: CounselingAppointment) => void;
}) {
  const today = dayjs().format("YYYY-MM-DD");
  const todayApps = appointments.filter(a => a.scheduled_date === today && a.status !== "cancelled");
  const upcomingToday = todayApps.filter(a => a.status === "scheduled" || a.status === "in_progress");
  const completedToday = todayApps.filter(a => a.status === "completed");

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <CalendarDaysIcon className="h-5 w-5 text-pink-500" />
          <h2 className="font-semibold text-slate-900 dark:text-white">Today&apos;s Schedule</h2>
          <Badge color={upcomingToday.length > 0 ? "blue" : "slate"}>{upcomingToday.length} upcoming</Badge>
          {completedToday.length > 0 && <Badge color="green">{completedToday.length} done</Badge>}
        </div>
        <p className="text-sm text-slate-500">{dayjs().format("dddd, MMMM D")}</p>
      </div>
      <div className="divide-y divide-slate-100 dark:divide-slate-700">
        {todayApps.length === 0 ? (
          <div className="px-5 py-8 text-center">
            <CalendarDaysIcon className="h-8 w-8 text-slate-300 mx-auto mb-2" />
            <p className="text-sm text-slate-500">No appointments scheduled for today</p>
          </div>
        ) : (
          todayApps.sort((a, b) => a.scheduled_time.localeCompare(b.scheduled_time)).map(app => {
            const cfg = STATUS_CONFIG[app.status];
            const isActive = app.status === "scheduled" || app.status === "in_progress";
            return (
              <div key={app.id} className="flex items-center gap-4 px-5 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors group">
                <div className="flex flex-col items-center min-w-[4rem]">
                  <span className="text-lg font-bold text-slate-800 dark:text-slate-200">
                    {dayjs(app.scheduled_time, "HH:mm").format("h:mm")}
                  </span>
                  <span className="text-xs text-slate-400">
                    {dayjs(app.scheduled_time, "HH:mm").format("A")}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-slate-900 dark:text-white truncate">{app.student_name}</p>
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${cfg.color}`}>
                      <cfg.icon className="h-3 w-3" />
                      {cfg.label}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    {APPOINTMENT_TYPES.find(t => t.value === app.appointment_type)?.label ?? app.appointment_type}
                    {app.location ? ` · 📍 ${app.location}` : ""}
                    {app.duration_minutes ? ` · ${app.duration_minutes} min` : ""}
                  </p>
                </div>
                {isActive && (
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity" onClick={e => e.stopPropagation()}>
                    <button onClick={() => onComplete(app)}
                      className="p-1.5 rounded-lg text-green-600 hover:bg-green-50 dark:hover:bg-green-900/30 transition-colors"
                      title="Mark completed">
                      <CheckCircleIcon className="h-4 w-4" />
                    </button>
                    <button onClick={() => onNoShow(app)}
                      className="p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors"
                      title="Mark no-show">
                      <XCircleIcon className="h-4 w-4" />
                    </button>
                    <button onClick={() => onCancel(app)}
                      className="p-1.5 rounded-lg text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
                      title="Cancel">
                      <ExclamationTriangleIcon className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

// ─── Stats Bar ────────────────────────────────────────────────────────────────

function StatsBar({ stats }: { stats: { today: number; upcoming: number; completed: number; total: number } }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {[
        { label: "Today", value: stats.today, color: "text-blue-600 dark:text-blue-400" },
        { label: "Upcoming", value: stats.upcoming, color: "text-amber-600 dark:text-amber-400" },
        { label: "Completed", value: stats.completed, color: "text-green-600 dark:text-green-400" },
        { label: "Total", value: stats.total, color: "text-pink-600 dark:text-pink-400" },
      ].map(s => (
        <div key={s.label} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-3 sm:p-4">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400">{s.label}</p>
          <p className={`mt-1 text-xl sm:text-2xl font-bold ${s.color}`}>{s.value}</p>
        </div>
      ))}
    </div>
  );
}

// ─── Create/Edit Appointment Modal ────────────────────────────────────────────

function AppointmentFormModal({
  open, onClose, appointment, onSaved,
}: {
  open: boolean; onClose: () => void; appointment?: CounselingAppointment | null; onSaved: () => void;
}) {
  const { user } = useAuthStore();
  const qc = useQueryClient();
  const isEdit = !!appointment;

  const [form, setForm] = useState({
    student: appointment?.student ?? "",
    appointment_type: appointment?.appointment_type ?? "academic",
    scheduled_date: appointment?.scheduled_date ?? dayjs().add(1, "day").format("YYYY-MM-DD"),
    scheduled_time: appointment?.scheduled_time ?? "09:00",
    duration_minutes: appointment?.duration_minutes ?? 30,
    location: appointment?.location ?? "",
    reason: appointment?.reason ?? "",
    notes: appointment?.notes ?? "",
    follow_up_needed: appointment?.follow_up_needed ?? false,
    follow_up_date: appointment?.follow_up_date ?? "",
    send_reminder: false,
  });
  const [studentSearch, setStudentSearch] = useState(appointment?.student_name ?? "");
  const [studentResults, setStudentResults] = useState<Array<{ id: string; full_name: string; classroom?: { name: string; grade: { name: string } } }>>([]);
  const [searching, setSearching] = useState(false);

  const createMut = useCreateCounselingAppointment();
  const updateMut = useUpdateCounselingAppointment();
  const isSaving = createMut.isPending || updateMut.isPending;

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
    if (!form.scheduled_date) return toast.error("Please select a date");
    if (!form.scheduled_time) return toast.error("Please select a time");

    if (isEdit) {
      updateMut.mutate({
        id: appointment!.id,
        appointment_type: form.appointment_type,
        scheduled_date: form.scheduled_date,
        scheduled_time: form.scheduled_time,
        duration_minutes: form.duration_minutes,
        location: form.location,
        reason: form.reason,
        notes: form.notes,
        follow_up_needed: form.follow_up_needed,
        follow_up_date: form.follow_up_date || undefined,
      }, { onSuccess: () => onSaved() });
    } else {
      createMut.mutate({
        student: form.student,
        appointment_type: form.appointment_type,
        scheduled_date: form.scheduled_date,
        scheduled_time: form.scheduled_time,
        duration_minutes: form.duration_minutes,
        location: form.location,
        reason: form.reason,
        send_reminder: form.send_reminder,
      }, { onSuccess: () => onSaved() });
    }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Appointment" : "Schedule New Appointment"}
      description={isEdit ? "Update appointment details or add session notes" : "Book a counseling session with a student"}
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        {!isEdit && (
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Student *</label>
            <input
              value={studentSearch}
              onChange={e => handleStudentSearch(e.target.value)}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
              placeholder="Search student by name..."
              autoComplete="off"
            />
            {searching && <Spinner size="sm" className="mt-1" />}
            {studentSearch.length >= 2 && !form.student && studentResults.length > 0 && (
              <div className="mt-1 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 shadow-lg max-h-48 overflow-y-auto">
                {studentResults.map(s => (
                  <button key={s.id} type="button"
                    onClick={() => {
                      setForm(p => ({ ...p, student: s.id }));
                      setStudentSearch(s.full_name);
                      setStudentResults([]);
                    }}
                    className="w-full text-left px-3 py-2.5 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 dark:text-slate-200 border-b border-slate-50 dark:border-slate-700 last:border-0">
                    <span className="font-medium">{s.full_name}</span>
                    {s.classroom && <span className="text-xs text-slate-400 ml-2">{s.classroom.grade?.name} — {s.classroom.name}</span>}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Date *</label>
            <input type="date" value={form.scheduled_date}
              onChange={e => setForm(p => ({ ...p, scheduled_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Time *</label>
            <input type="time" value={form.scheduled_time}
              onChange={e => setForm(p => ({ ...p, scheduled_time: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200" />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Appointment Type</label>
            <select value={form.appointment_type}
              onChange={e => setForm(p => ({ ...p, appointment_type: e.target.value as CounselingAppointmentType }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200">
              {APPOINTMENT_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Duration (minutes)</label>
            <select value={form.duration_minutes}
              onChange={e => setForm(p => ({ ...p, duration_minutes: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200">
              {[15, 30, 45, 60, 90].map(m => <option key={m} value={m}>{m} min</option>)}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Location</label>
          <input value={form.location}
            onChange={e => setForm(p => ({ ...p, location: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
            placeholder="Room 204, Zoom link, or virtual office" />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Reason *</label>
          <textarea value={form.reason}
            onChange={e => setForm(p => ({ ...p, reason: e.target.value }))}
            rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
            placeholder="Brief reason for the appointment..." />
        </div>

        {isEdit && (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Session Notes (post-session)</label>
              <textarea value={form.notes}
                onChange={e => setForm(p => ({ ...p, notes: e.target.value }))}
                rows={3}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
                placeholder="Document session notes, observations, and action items..." />
            </div>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={form.follow_up_needed}
                  onChange={e => setForm(p => ({ ...p, follow_up_needed: e.target.checked }))}
                  className="rounded border-slate-300 text-pink-600 focus:ring-pink-500" />
                <span className="text-sm text-slate-700 dark:text-slate-300">Follow-up needed</span>
              </label>
              {form.follow_up_needed && (
                <input type="date" value={form.follow_up_date}
                  onChange={e => setForm(p => ({ ...p, follow_up_date: e.target.value }))}
                  className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-1.5 text-sm dark:text-slate-200" />
              )}
            </div>
          </>
        )}

        {!isEdit && (
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.send_reminder}
              onChange={e => setForm(p => ({ ...p, send_reminder: e.target.checked }))}
              className="rounded border-slate-300 text-pink-600 focus:ring-pink-500" />
            <span className="text-sm text-slate-700 dark:text-slate-300">Send reminder notification to student</span>
          </label>
        )}

        <div className="flex justify-end gap-3 pt-2 border-t border-slate-100 dark:border-slate-700">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>
            {isEdit ? "Update Appointment" : "Schedule Appointment"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Complete Appointment Modal ───────────────────────────────────────────────

function CompleteAppointmentModal({
  open, onClose, appointment, onSaved,
}: {
  open: boolean; onClose: () => void; appointment: CounselingAppointment; onSaved: () => void;
}) {
  const [notes, setNotes] = useState("");
  const [followUp, setFollowUp] = useState(false);
  const [followUpDate, setFollowUpDate] = useState("");
  const completeMut = useCompleteAppointment();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    completeMut.mutate({
      id: appointment.id,
      notes: notes.trim() || undefined,
      follow_up_needed: followUp,
      follow_up_date: followUpDate || undefined,
    }, { onSuccess: () => onSaved() });
  };

  return (
    <Modal open={open} onClose={onClose} title="Complete Appointment"
      description={`Record session notes for ${appointment.student_name}`}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Session Notes</label>
          <textarea value={notes} onChange={e => setNotes(e.target.value)}
            rows={4}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
            placeholder="Document observations, progress, concerns, and action items..." autoFocus />
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={followUp}
              onChange={e => setFollowUp(e.target.checked)}
              className="rounded border-slate-300 text-pink-600 focus:ring-pink-500" />
            <span className="text-sm text-slate-700 dark:text-slate-300">Needs follow-up</span>
          </label>
          {followUp && (
            <input type="date" value={followUpDate}
              onChange={e => setFollowUpDate(e.target.value)}
              className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-1.5 text-sm dark:text-slate-200" />
          )}
        </div>
        <div className="flex justify-end gap-3 pt-2 border-t border-slate-100 dark:border-slate-700">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button type="submit" loading={completeMut.isPending}>
            <CheckCircleIcon className="h-4 w-4" /> Complete Session
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Appointment Detail Modal ─────────────────────────────────────────────────

function AppointmentDetailModal({
  open, onClose, appointment, onEdit, onComplete, onCancel, onNoShow,
}: {
  open: boolean; onClose: () => void; appointment: CounselingAppointment;
  onEdit: (a: CounselingAppointment) => void;
  onComplete: (a: CounselingAppointment) => void;
  onCancel: (a: CounselingAppointment) => void;
  onNoShow: (a: CounselingAppointment) => void;
}) {
  const cfg = STATUS_CONFIG[appointment.status];
  const isActive = appointment.status === "scheduled" || appointment.status === "in_progress";

  return (
    <Modal open={open} onClose={onClose} title="Appointment Details" size="md">
      <div className="space-y-4">
        {/* Status & Type */}
        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold ${cfg.color}`}>
            <cfg.icon className="h-3.5 w-3.5" />
            {cfg.label}
          </span>
          <span className="text-sm text-slate-500">
            {APPOINTMENT_TYPES.find(t => t.value === appointment.appointment_type)?.label ?? appointment.appointment_type}
          </span>
        </div>

        {/* Student & Counselor */}
        <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50 dark:bg-slate-700/30 rounded-lg">
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Student</p>
            <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-white">{appointment.student_name}</p>
            {(appointment.student_grade || appointment.student_class) && (
              <p className="text-xs text-slate-500">{appointment.student_grade}{appointment.student_grade && appointment.student_class ? " — " : ""}{appointment.student_class}</p>
            )}
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Counselor</p>
            <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-white">{appointment.counselor_name}</p>
          </div>
        </div>

        {/* Date, Time, Duration */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Date</p>
            <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-white">
              {dayjs(appointment.scheduled_date).format("MMM D, YYYY")}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Time</p>
            <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-white">
              {dayjs(appointment.scheduled_time, "HH:mm").format("h:mm A")}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Duration</p>
            <p className="mt-1 text-sm font-semibold text-slate-900 dark:text-white">{appointment.duration_minutes} min</p>
          </div>
        </div>

        {/* Location */}
        {appointment.location && (
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Location</p>
            <p className="mt-1 text-sm text-slate-700 dark:text-slate-300">{appointment.location}</p>
          </div>
        )}

        {/* Reason */}
        {appointment.reason && (
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Reason</p>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-700/30 p-3 rounded-lg">{appointment.reason}</p>
          </div>
        )}

        {/* Notes */}
        {appointment.notes && (
          <div>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Session Notes</p>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-700/30 p-3 rounded-lg">{appointment.notes}</p>
          </div>
        )}

        {/* Follow-up */}
        {appointment.follow_up_needed && (
          <div className="flex items-center gap-2 text-sm text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/30 p-3 rounded-lg">
            <ExclamationTriangleIcon className="h-4 w-4" />
            <span>Follow-up needed{appointment.follow_up_date ? ` by ${dayjs(appointment.follow_up_date).format("MMM D, YYYY")}` : ""}</span>
          </div>
        )}

        {/* Actions */}
        {isActive && (
          <div className="flex flex-wrap gap-2 pt-3 border-t border-slate-100 dark:border-slate-700">
            <Button size="sm" onClick={() => { onClose(); onComplete(appointment); }}>
              <CheckCircleIcon className="h-4 w-4" /> Complete
            </Button>
            <Button size="sm" variant="secondary" onClick={() => { onClose(); onEdit(appointment); }}>
              <PencilIcon className="h-4 w-4" /> Edit
            </Button>
            <Button size="sm" variant="ghost" onClick={() => { onClose(); onNoShow(appointment); }}>
              No Show
            </Button>
            <Button size="sm" variant="danger" onClick={() => { onClose(); onCancel(appointment); }}>
              Cancel
            </Button>
          </div>
        )}
      </div>
    </Modal>
  );
}

// ─── Main Appointments Page ──────────────────────────────────────────────────

export default function CounselorAppointmentsPage() {
  const qc = useQueryClient();
  const [activeFilter, setActiveFilter] = useState<string>("upcoming");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<CounselingAppointment | null>(null);
  const [detailApp, setDetailApp] = useState<CounselingAppointment | null>(null);
  const [completingApp, setCompletingApp] = useState<CounselingAppointment | null>(null);

  const { data: appsResponse, isLoading } = useCounselingAppointments(
    statusFilter !== "all" ? { status: statusFilter } : undefined
  );
  const appointments = appsResponse?.results ?? [];

  // Compute stats
  const today = dayjs().format("YYYY-MM-DD");
  const stats = useMemo(() => ({
    today: appointments.filter(a => a.scheduled_date === today && a.status !== "cancelled").length,
    upcoming: appointments.filter(a => a.scheduled_date >= today && a.status === "scheduled").length,
    completed: appointments.filter(a => a.status === "completed").length,
    total: appointments.length,
  }), [appointments, today]);

  // Filtered + searched
  const filtered = useMemo(() => {
    let items = appointments;
    // Time filter
    if (activeFilter === "upcoming") items = items.filter(a => a.scheduled_date >= today && ["scheduled", "in_progress"].includes(a.status));
    else if (activeFilter === "today") items = items.filter(a => a.scheduled_date === today);
    else if (activeFilter === "past") items = items.filter(a => a.scheduled_date < today || ["completed", "cancelled", "no_show"].includes(a.status));

    // Search
    if (search.trim()) {
      const q = search.toLowerCase();
      items = items.filter(a =>
        a.student_name?.toLowerCase().includes(q) ||
        a.counselor_name?.toLowerCase().includes(q) ||
        a.reason?.toLowerCase().includes(q) ||
        a.location?.toLowerCase().includes(q)
      );
    }
    return items;
  }, [appointments, activeFilter, today, search]);

  const cancelMut = useCancelAppointment();
  const noShowMut = useNoShowAppointment();

  // ─── Handlers ─────────────────────────────────────────────────────────

  const handleComplete = useCallback(async (app: CounselingAppointment) => {
    setCompletingApp(app);
  }, []);

  const handleCancel = useCallback(async (app: CounselingAppointment) => {
    if (!confirm(`Cancel appointment with ${app.student_name} on ${dayjs(app.scheduled_date).format("MMM D")}?`)) return;
    cancelMut.mutate(app.id);
  }, [cancelMut]);

  const handleNoShow = useCallback(async (app: CounselingAppointment) => {
    if (!confirm(`Mark ${app.student_name} as no-show?`)) return;
    noShowMut.mutate(app.id);
  }, [noShowMut]);

  const refreshAll = () => {
    qc.invalidateQueries({ queryKey: ["counseling"] });
    qc.invalidateQueries({ queryKey: ["counselor-dashboard"] });
    setShowForm(false);
    setEditing(null);
    setCompletingApp(null);
    setDetailApp(null);
  };

  // ─── Render ───────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Appointments</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Manage counseling sessions, book new appointments, and track student progress
          </p>
        </div>
        <Button onClick={() => { setEditing(null); setShowForm(true); }}>
          <PlusIcon className="h-4 w-4 mr-1.5" /> New Appointment
        </Button>
      </div>

      {/* Stats */}
      <StatsBar stats={stats} />

      {/* Today&apos;s Schedule */}
      <TodaySchedule
        appointments={appointments}
        onComplete={handleComplete}
        onCancel={handleCancel}
        onNoShow={handleNoShow}
        onEdit={(a) => { setEditing(a); setShowForm(true); }}
      />

      {/* Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        {/* Time filters */}
        <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
          {[
            { key: "upcoming", label: "Upcoming" },
            { key: "today", label: "Today" },
            { key: "past", label: "Past" },
            { key: "all", label: "All" },
          ].map(f => (
            <button key={f.key} onClick={() => setActiveFilter(f.key)}
              className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                activeFilter === f.key
                  ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
              }`}>
              {f.label}
            </button>
          ))}
        </div>

        {/* Status pills */}
        <div className="flex flex-wrap gap-1.5">
          {(["all", "scheduled", "completed", "cancelled", "no_show"] as const).map(s => (
            <button key={s} onClick={() => setStatusFilter(s === "all" ? "all" : s)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                statusFilter === s
                  ? "bg-pink-100 text-pink-700 dark:bg-pink-900/40 dark:text-pink-300"
                  : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-200"
              }`}>
              {s === "all" ? "All" : STATUS_CONFIG[s]?.label ?? s}
            </button>
          ))}
        </div>

        <div className="sm:ml-auto relative flex-1 max-w-xs">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input value={search} onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm dark:text-slate-200"
            placeholder="Search by student, reason, location..." />
        </div>
      </div>

      {/* Appointment List */}
      {isLoading ? (
        <div className="space-y-3">
          {[1,2,3,4].map(i => <div key={i} className="h-20 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse" />)}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={CalendarDaysIcon} title="No appointments found"
          description={search ? "Try a different search term" : "No appointments scheduled yet. Click &apos;New Appointment&apos; to book one."}
          action={<Button onClick={() => setShowForm(true)}><PlusIcon className="h-4 w-4 mr-1" /> New Appointment</Button>} />
      ) : (
        <div className="space-y-2">
          {filtered
            .sort((a, b) => a.scheduled_date.localeCompare(b.scheduled_date) || a.scheduled_time.localeCompare(b.scheduled_time))
            .map(app => {
              const cfg = STATUS_CONFIG[app.status];
              const isActive = app.status === "scheduled" || app.status === "in_progress";
              return (
                <div key={app.id}
                  onClick={() => setDetailApp(app)}
                  className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-pink-300 dark:hover:border-pink-600 hover:shadow-md transition-all cursor-pointer group">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${cfg.color}`}>
                          <cfg.icon className="h-3 w-3" />
                          {cfg.label}
                        </span>
                        <span className="text-xs font-medium text-pink-600 dark:text-pink-400">
                          {APPOINTMENT_TYPES.find(t => t.value === app.appointment_type)?.label ?? app.appointment_type}
                        </span>
                      </div>
                      <p className="font-semibold text-slate-900 dark:text-white group-hover:text-pink-600 dark:group-hover:text-pink-400 transition-colors">
                        {app.student_name}
                      </p>
                      <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
                        {dayjs(app.scheduled_date).format("MMM D, YYYY")} · {dayjs(app.scheduled_time, "HH:mm").format("h:mm A")}
                        {app.duration_minutes ? ` · ${app.duration_minutes} min` : ""}
                        {app.location ? ` · 📍 ${app.location}` : ""}
                      </p>
                      {app.reason && (
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 line-clamp-1">{app.reason}</p>
                      )}
                      {app.follow_up_needed && (
                        <span className="inline-flex items-center gap-1 mt-1 text-xs text-amber-600 dark:text-amber-400">
                          <ExclamationTriangleIcon className="h-3 w-3" />
                          Follow-up {app.follow_up_date ? `by ${dayjs(app.follow_up_date).format("MMM D")}` : "needed"}
                        </span>
                      )}
                    </div>
                    {isActive && (
                      <div className="flex gap-1 ml-4" onClick={e => e.stopPropagation()}>
                        <button onClick={() => handleComplete(app)}
                          className="p-2 rounded-lg text-green-600 hover:bg-green-50 dark:hover:bg-green-900/30 transition-colors"
                          title="Complete">
                          <CheckCircleIcon className="h-4 w-4" />
                        </button>
                        <button onClick={() => { setEditing(app); setShowForm(true); }}
                          className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                          title="Edit">
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        <button onClick={() => handleCancel(app)}
                          className="p-2 rounded-lg text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
                          title="Cancel">
                          <XCircleIcon className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                    {!isActive && (
                      <span className="text-xs text-slate-400 ml-4 whitespace-nowrap">
                        {dayjs(app.scheduled_date).fromNow()}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
        </div>
      )}

      {/* Modals */}
      {showForm && (
        <AppointmentFormModal
          open={showForm}
          onClose={() => { setShowForm(false); setEditing(null); }}
          appointment={editing}
          onSaved={refreshAll}
        />
      )}

      {completingApp && (
        <CompleteAppointmentModal
          open={!!completingApp}
          onClose={() => setCompletingApp(null)}
          appointment={completingApp}
          onSaved={refreshAll}
        />
      )}

      {detailApp && !showForm && !completingApp && (
        <AppointmentDetailModal
          open={!!detailApp}
          onClose={() => setDetailApp(null)}
          appointment={detailApp}
          onEdit={(a) => { setDetailApp(null); setEditing(a); setShowForm(true); }}
          onComplete={(a) => { setDetailApp(null); setCompletingApp(a); }}
          onCancel={(a) => { setDetailApp(null); handleCancel(a); }}
          onNoShow={(a) => { setDetailApp(null); handleNoShow(a); }}
        />
      )}
    </div>
  );
}
