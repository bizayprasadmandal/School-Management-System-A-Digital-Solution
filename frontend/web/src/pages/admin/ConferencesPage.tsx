/** Conference Scheduler — Admin view for managing parent-teacher conference slots */

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  PlusIcon, CalendarDaysIcon, PencilIcon, TrashIcon, XCircleIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState } from "../../components/common";

interface ConferenceSlot {
  id: string;
  teacher: string;
  teacher_name: string;
  student: string | null;
  student_name: string | null;
  date: string;
  start_time: string;
  end_time: string;
  is_booked: boolean;
  notes: string;
}

function SlotFormModal({ open, onClose, slot, onSaved }: {
  open: boolean; onClose: () => void; slot?: ConferenceSlot | null; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    teacher: slot?.teacher ?? "",
    date: slot?.date ?? dayjs().format("YYYY-MM-DD"),
    start_time: slot?.start_time ?? "09:00",
    end_time: slot?.end_time ?? "09:30",
    notes: slot?.notes ?? "",
  });

  const [teacherSearch, setTeacherSearch] = useState(slot?.teacher_name ?? "");

  const { data: teachers = [] } = useQuery({
    queryKey: ["teacher-search", teacherSearch],
    queryFn: async () => {
      if (teacherSearch.length < 2) return [];
      const res = await api.get<{ results: any[] }>("/academics/teacher-profiles/", { search: teacherSearch, page_size: 10 });
      return res.results ?? [];
    },
    enabled: teacherSearch.length >= 2,
  });

  const isEdit = !!slot;
  const createMut = useMutation({
    mutationFn: (d: typeof form) => api.post("/conferences/conference-slots/", d),
    onSuccess: () => { toast.success("Slot created"); onSaved(); },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Failed to create slot"),
  });
  const updateMut = useMutation({
    mutationFn: (d: typeof form) => api.patch(`/conferences/conference-slots/${slot!.id}/`, d),
    onSuccess: () => { toast.success("Slot updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.teacher) return toast.error("Select a teacher");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Slot" : "Create Conference Slot"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Teacher *</label>
          <input value={teacherSearch} onChange={e => { setTeacherSearch(e.target.value); setForm(p => ({ ...p, teacher: "" })); }}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" placeholder="Search teacher..." disabled={isEdit} />
          {teacherSearch.length >= 2 && !form.teacher && teachers.length > 0 && (
            <div className="mt-1 border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-800 shadow-lg max-h-32 overflow-y-auto">
              {teachers.map((t: any) => (
                <button key={t.id} type="button" onClick={() => { setForm(p => ({ ...p, teacher: t.user })); setTeacherSearch(t.full_name ?? t.user_name); }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 dark:text-slate-200">{t.full_name ?? t.user_name}</button>
              ))}
            </div>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Date *</label>
          <input type="date" value={form.date} onChange={e => setForm(p => ({ ...p, date: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Start Time *</label>
            <input type="time" value={form.start_time} onChange={e => setForm(p => ({ ...p, start_time: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">End Time *</label>
            <input type="time" value={form.end_time} onChange={e => setForm(p => ({ ...p, end_time: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Notes</label>
          <textarea value={form.notes} onChange={e => setForm(p => ({ ...p, notes: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Slot</Button>
        </div>
      </form>
    </Modal>
  );
}

export default function ConferencesPage() {
  const [dateFilter, setDateFilter] = useState(dayjs().format("YYYY-MM-DD"));
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<ConferenceSlot | null>(null);
  const qc = useQueryClient();

  const { data: slots = [], isLoading } = useQuery({
    queryKey: ["conference-slots", dateFilter],
    queryFn: async () => {
      const res = await api.get<{ results: ConferenceSlot[] }>("/conferences/conference-slots/", { date: dateFilter });
      return res.results ?? [];
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => api.delete(`/conferences/conference-slots/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["conference-slots"] }); toast.success("Slot deleted"); },
  });

  const cancelMut = useMutation({
    mutationFn: (id: string) => api.post(`/conferences/conference-slots/${id}/cancel/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["conference-slots"] }); toast.success("Booking cancelled"); },
  });

  const booked = slots.filter(s => s.is_booked);
  const available = slots.filter(s => !s.is_booked);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Parent-Teacher Conferences</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Create and manage conference time slots</p>
        </div>
        <Button onClick={() => { setEditing(null); setShowForm(true); }}>
          <PlusIcon className="h-4 w-4 mr-1.5" /> Create Slots
        </Button>
      </div>

      {/* Date picker */}
      <div className="flex items-center gap-3">
        <CalendarDaysIcon className="h-5 w-5 text-slate-400" />
        <input type="date" value={dateFilter} onChange={e => setDateFilter(e.target.value)}
          className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        <div className="flex gap-2 text-sm text-slate-500">
          <span className="px-3 py-1.5 bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-lg font-medium">{booked.length} booked</span>
          <span className="px-3 py-1.5 bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-lg font-medium">{available.length} available</span>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-2">{[1,2,3].map(i => <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
      ) : slots.length === 0 ? (
        <EmptyState icon={CalendarDaysIcon} title="No slots for this date" description="Create conference slots for teachers" />
      ) : (
        <div className="space-y-2">
          {slots.map(slot => (
            <div key={slot.id} className={`bg-white dark:bg-slate-800 rounded-xl border p-4 flex items-center justify-between transition-shadow hover:shadow-sm ${
              slot.is_booked ? "border-indigo-200 dark:border-indigo-800" : "border-slate-200 dark:border-slate-700"
            }`}>
              <div className="flex items-center gap-4">
                <div className="flex flex-col items-center w-16">
                  <span className="text-lg font-bold text-slate-900 dark:text-white">{slot.start_time}</span>
                  <span className="text-xs text-slate-400">—{slot.end_time}</span>
                </div>
                <div>
                  <p className="font-medium text-slate-900 dark:text-white">{slot.teacher_name}</p>
                  {slot.is_booked ? (
                    <p className="text-sm text-indigo-600 dark:text-indigo-400">
                      Booked by {slot.student_name}
                    </p>
                  ) : (
                    <p className="text-sm text-green-600 dark:text-green-400">Available</p>
                  )}
                  {slot.notes && <p className="text-xs text-slate-400 mt-0.5">{slot.notes}</p>}
                </div>
              </div>
              <div className="flex gap-2">
                {slot.is_booked ? (
                  <Button size="sm" variant="secondary" onClick={() => cancelMut.mutate(slot.id)} loading={cancelMut.isPending}>
                    <XCircleIcon className="h-4 w-4 mr-1" /> Cancel
                  </Button>
                ) : (
                  <>
                    <button onClick={() => { setEditing(slot); setShowForm(true); }}
                      className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700">
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button onClick={() => { if (confirm("Delete this slot?")) deleteMut.mutate(slot.id); }}
                      className="p-2 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30">
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <SlotFormModal
          open={showForm} onClose={() => { setShowForm(false); setEditing(null); }}
          slot={editing} onSaved={() => { setShowForm(false); setEditing(null); qc.invalidateQueries({ queryKey: ["conference-slots"] }); }} />
      )}
    </div>
  );
}
