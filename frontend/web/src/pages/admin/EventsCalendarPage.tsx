/** Event Calendar — month view, filters, and CRUD for school events */

import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  ChevronLeftIcon, ChevronRightIcon, PlusIcon,
  CalendarDaysIcon, MapPinIcon, TrashIcon, PencilIcon,
  XMarkIcon, FunnelIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState } from "../../components/common";
import { useAuthStore } from "../../store/authStore";

interface SchoolEvent {
  id: string;
  title: string;
  description: string;
  event_type: "academic" | "sports" | "cultural" | "holiday" | "meeting" | "other";
  start_date: string;
  end_date: string;
  start_time?: string;
  end_time?: string;
  location: string;
  is_public: boolean;
  created_by_name?: string;
}

const EVENT_COLORS: Record<string, string> = {
  academic: "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300 border-blue-300",
  sports: "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 border-green-300",
  cultural: "bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300 border-purple-300",
  holiday: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 border-amber-300",
  meeting: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300 border-indigo-300",
  other: "bg-slate-100 text-slate-800 dark:bg-slate-900/40 dark:text-slate-300 border-slate-300",
};

const EVENT_TYPES = ["academic", "sports", "cultural", "holiday", "meeting", "other"];

function EventFormModal({
  open, onClose, event, onSaved,
}: {
  open: boolean;
  onClose: () => void;
  event?: SchoolEvent | null;
  onSaved: () => void;
}) {
  const [form, setForm] = useState({
    title: event?.title ?? "",
    description: event?.description ?? "",
    event_type: (event?.event_type ?? "academic") as "academic" | "sports" | "cultural" | "holiday" | "meeting" | "other",
    start_date: event?.start_date ?? dayjs().format("YYYY-MM-DD"),
    end_date: event?.end_date ?? dayjs().format("YYYY-MM-DD"),
    start_time: event?.start_time ?? "",
    end_time: event?.end_time ?? "",
    location: event?.location ?? "",
    is_public: event?.is_public ?? true,
  });

  const createMutation = useMutation({
    mutationFn: (data: typeof form) => api.post("/timetable/events/", data),
    onSuccess: () => { toast.success("Event created"); onSaved(); },
    onError: (err: any) => toast.error(err?.response?.data?.detail ?? "Failed to create event"),
  });

  const updateMutation = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/timetable/events/${event!.id}/`, data),
    onSuccess: () => { toast.success("Event updated"); onSaved(); },
    onError: (err: any) => toast.error(err?.response?.data?.detail ?? "Failed to update event"),
  });

  const isSaving = createMutation.isPending || updateMutation.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) return toast.error("Title is required");
    if (event) updateMutation.mutate(form);
    else createMutation.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={event ? "Edit Event" : "New Event"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Title *</label>
          <input
            value={form.title} onChange={e => setForm(p => ({ ...p, title: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 dark:text-slate-200"
            placeholder="Event title" required
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Type</label>
            <select value={form.event_type} onChange={e => setForm(p => ({ ...p, event_type: e.target.value as "academic" | "sports" | "cultural" | "holiday" | "meeting" | "other" }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              {EVENT_TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Location</label>
            <input value={form.location} onChange={e => setForm(p => ({ ...p, location: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" placeholder="Room / Venue" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Start Date *</label>
            <input type="date" value={form.start_date} onChange={e => setForm(p => ({ ...p, start_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">End Date</label>
            <input type="date" value={form.end_date} onChange={e => setForm(p => ({ ...p, end_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Start Time</label>
            <input type="time" value={form.start_time} onChange={e => setForm(p => ({ ...p, start_time: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">End Time</label>
            <input type="time" value={form.end_time} onChange={e => setForm(p => ({ ...p, end_time: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
          <textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} rows={3}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input type="checkbox" checked={form.is_public} onChange={e => setForm(p => ({ ...p, is_public: e.target.checked }))}
            className="rounded border-slate-300" />
          Public event (visible to all)
        </label>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{event ? "Update" : "Create"} Event</Button>
        </div>
      </form>
    </Modal>
  );
}

export default function EventsCalendarPage() {
  const [currentMonth, setCurrentMonth] = useState(dayjs().startOf("month"));
  const [selectedEvent, setSelectedEvent] = useState<SchoolEvent | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const qc = useQueryClient();
  const user = useAuthStore(s => s.user);
  const isAdmin = user?.role === "school_admin" || user?.role === "super_admin";

  const { data: events = [], isLoading } = useQuery({
    queryKey: ["events", typeFilter],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (typeFilter !== "all") params.event_type = typeFilter;
      const res = await api.get<{ results: SchoolEvent[] }>("/timetable/events/", params);
      return res.results ?? [];
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/timetable/events/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["events"] }); toast.success("Event deleted"); },
  });

  const monthEvents = useMemo(() => events.filter(e => {
    const start = dayjs(e.start_date);
    return start.isSame(currentMonth, "month") || start.isSame(currentMonth, "year");
  }), [events, currentMonth]);

  const daysInMonth = currentMonth.daysInMonth();
  const startDay = currentMonth.startOf("month").day();
  const today = dayjs().format("YYYY-MM-DD");

  const prevMonth = () => setCurrentMonth(p => p.subtract(1, "month"));
  const nextMonth = () => setCurrentMonth(p => p.add(1, "month"));

  const getDayEvents = (day: number) => {
    const date = currentMonth.date(day).format("YYYY-MM-DD");
    return monthEvents.filter(e => dayjs(e.start_date).format("YYYY-MM-DD") === date);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Event Calendar</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage school events, holidays, and activities</p>
        </div>
        {isAdmin && (
          <Button onClick={() => { setSelectedEvent(null); setShowForm(true); }}>
            <PlusIcon className="h-4 w-4 mr-1.5" /> Add Event
          </Button>
        )}
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <FunnelIcon className="h-4 w-4 text-slate-400" />
        <div className="flex gap-1.5 flex-wrap">
          {["all", ...EVENT_TYPES].map(t => (
            <button key={t} onClick={() => setTypeFilter(t)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                typeFilter === t
                  ? t === "all" ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300"
                    : EVENT_COLORS[t]
                  : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 hover:bg-slate-200"
              }`}>
              {t === "all" ? "All" : t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 dark:border-slate-700">
          <button onClick={prevMonth} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400">
            <ChevronLeftIcon className="h-5 w-5" />
          </button>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
            {currentMonth.format("MMMM YYYY")}
          </h2>
          <button onClick={nextMonth} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400">
            <ChevronRightIcon className="h-5 w-5" />
          </button>
        </div>

        <div className="grid grid-cols-7 text-center text-xs font-semibold text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/50 py-2">
          {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map(d => <div key={d}>{d}</div>)}
        </div>

        <div className="grid grid-cols-7">
          {Array.from({ length: startDay }).map((_, i) => (
            <div key={`empty-${i}`} className="min-h-[100px] border-b border-r border-slate-100 dark:border-slate-700/50 bg-slate-50/50 dark:bg-slate-800/30" />
          ))}
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = i + 1;
            const dateStr = currentMonth.date(day).format("YYYY-MM-DD");
            const dayEvents = getDayEvents(day);
            const isToday = dateStr === today;
            return (
              <div key={day} className={`min-h-[100px] border-b border-r border-slate-100 dark:border-slate-700/50 p-1.5 transition-colors ${
                isToday ? "bg-indigo-50/50 dark:bg-indigo-900/20" : "hover:bg-slate-50 dark:hover:bg-slate-800/40"
              }`}>
                <span className={`inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium ${
                  isToday ? "bg-indigo-600 text-white" : "text-slate-700 dark:text-slate-300"
                }`}>
                  {day}
                </span>
                <div className="mt-1 space-y-0.5">
                  {dayEvents.slice(0, 3).map(e => (
                    <button key={e.id} onClick={() => setSelectedEvent(e)}
                      className={`w-full text-left text-[10px] px-1.5 py-0.5 rounded border truncate ${EVENT_COLORS[e.event_type] ?? EVENT_COLORS.other} hover:opacity-80 transition-opacity`}>
                      {e.title}
                    </button>
                  ))}
                  {dayEvents.length > 3 && (
                    <p className="text-[10px] text-slate-400 pl-1">+{dayEvents.length - 3} more</p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Event detail popover */}
      {selectedEvent && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/30" onClick={() => setSelectedEvent(null)}>
          <div className="bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 p-6 max-w-md w-full mx-4" onClick={e => e.stopPropagation()}>
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${EVENT_COLORS[selectedEvent.event_type]}`}>
                  {selectedEvent.event_type}
                </span>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{selectedEvent.title}</h3>
              </div>
              <button onClick={() => setSelectedEvent(null)} className="text-slate-400 hover:text-slate-600">
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
            {selectedEvent.description && (
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">{selectedEvent.description}</p>
            )}
            <div className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <div className="flex items-center gap-2">
                <CalendarDaysIcon className="h-4 w-4" />
                <span>{dayjs(selectedEvent.start_date).format("MMM D, YYYY")}{selectedEvent.end_date && selectedEvent.end_date !== selectedEvent.start_date ? ` — ${dayjs(selectedEvent.end_date).format("MMM D, YYYY")}` : ""}</span>
              </div>
              {selectedEvent.location && (
                <div className="flex items-center gap-2">
                  <MapPinIcon className="h-4 w-4" />
                  <span>{selectedEvent.location}</span>
                </div>
              )}
              {selectedEvent.start_time && (
                <p className="text-slate-500">{selectedEvent.start_time}{selectedEvent.end_time ? ` — ${selectedEvent.end_time}` : ""}</p>
              )}
            </div>
            {isAdmin && (
              <div className="flex justify-end gap-2 mt-6 pt-4 border-t border-slate-200 dark:border-slate-700">
                <Button variant="secondary" size="sm"
                  onClick={() => { setShowForm(true); }}>
                  <PencilIcon className="h-3.5 w-3.5 mr-1" /> Edit
                </Button>
                <Button variant="danger" size="sm" loading={deleteMutation.isPending}
                  onClick={() => { if (confirm("Delete this event?")) deleteMutation.mutate(selectedEvent.id); }}>
                  <TrashIcon className="h-3.5 w-3.5 mr-1" /> Delete
                </Button>
              </div>
            )}
          </div>
        </div>
      )}

      {showForm && (
        <EventFormModal
          open={showForm}
          onClose={() => { setShowForm(false); setSelectedEvent(null); }}
          event={selectedEvent}
          onSaved={() => { setShowForm(false); setSelectedEvent(null); qc.invalidateQueries({ queryKey: ["events"] }); }}
        />
      )}
    </div>
  );
}
