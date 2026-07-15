/**
 * Conference Scheduler — Parent view for booking slots for their children
 * and joining Zoom meetings for booked slots.
 */

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  CalendarDaysIcon, UsersIcon, CheckCircleIcon,
  VideoCameraIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, EmptyState, Badge } from "../../components/common";

interface ConferenceSlot {
  id: string;
  teacher_name: string;
  student_name: string | null;
  date: string;
  start_time: string;
  end_time: string;
  is_booked: boolean;
  notes: string;
  // Zoom fields (populated after migration)
  zoom_meeting_id?: string;
  zoom_join_url?: string;
  zoom_start_url?: string;
  zoom_password?: string;
  is_zoom_created?: boolean;
}

type TabId = "available" | "booked";

export default function ParentConferencesPage() {
  const [date, setDate] = useState(dayjs().format("YYYY-MM-DD"));
  const [selectedChild, setSelectedChild] = useState<string>("");
  const [activeTab, setActiveTab] = useState<TabId>("available");
  const qc = useQueryClient();

  const { data: children = [] } = useQuery({
    queryKey: ["my-children"],
    queryFn: async () => {
      const res = await api.get<{ results: any[] }>("/students/students/");
      return res.results ?? [];
    },
  });

  // Available slots for booking
  const { data: availableSlots = [], isLoading } = useQuery({
    queryKey: ["parent-conference-slots", date, "available"],
    queryFn: async () => {
      const res = await api.get<{ results: ConferenceSlot[] }>("/conferences/conference-slots/", { date });
      return (res.results ?? []).filter(s => !s.is_booked);
    },
  });

  // Booked slots (across all dates, for Zoom joining)
  const { data: bookedSlots = [], isLoading: bookedLoading } = useQuery({
    queryKey: ["parent-conference-slots-booked"],
    queryFn: async () => {
      const res = await api.get<{ results: ConferenceSlot[] }>("/conferences/conference-slots/", { is_booked: true });
      return res.results ?? [];
    },
  });

  const bookMut = useMutation({
    mutationFn: (slotId: string) =>
      api.post(`/conferences/conference-slots/${slotId}/book/`, { student_id: selectedChild }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["parent-conference-slots"] });
      qc.invalidateQueries({ queryKey: ["parent-conference-slots-booked"] });
      toast.success("Slot booked!");
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Failed to book slot"),
  });

  const tabs = [
    { id: "available" as TabId, label: "Available Slots", count: availableSlots.length },
    { id: "booked" as TabId, label: "My Booked Slots", count: bookedSlots.length },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Conference Scheduler</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          {activeTab === "available" ? "Book parent-teacher conference slots for your children" : "View your booked conferences and join Zoom meetings"}
        </p>
      </div>

      {/* Filters row */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <CalendarDaysIcon className="h-5 w-5 text-slate-400" />
          <input type="date" value={date} onChange={e => setDate(e.target.value)}
            className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        {children.length > 0 && activeTab === "available" && (
          <div className="flex items-center gap-2">
            <UsersIcon className="h-5 w-5 text-slate-400" />
            <select value={selectedChild} onChange={e => setSelectedChild(e.target.value)}
              className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">Select child...</option>
              {children.map((c: any) => (
                <option key={c.id} value={c.id}>{c.full_name ?? c.user?.full_name}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-700">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab.id
                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400 dark:border-indigo-400"
                : "border-transparent text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-300"
            }`}
          >
            {tab.label}
            <span className="ml-1.5 text-xs opacity-60">({tab.count})</span>
          </button>
        ))}
      </div>

      {/* Available Slots Tab */}
      {activeTab === "available" && (
        <>
          {isLoading ? (
            <div className="space-y-2">{[1,2,3].map(i => <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : availableSlots.length === 0 ? (
            <EmptyState icon={CalendarDaysIcon} title="No available slots" description="No conference slots available for this date. Check back later or try another date." />
          ) : (
            <div className="space-y-2">
              {availableSlots.map(slot => (
                <div key={slot.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 flex items-center justify-between hover:shadow-sm transition-shadow">
                  <div className="flex items-center gap-4">
                    <div className="flex flex-col items-center w-16">
                      <span className="text-lg font-bold text-slate-900 dark:text-white">{slot.start_time}</span>
                      <span className="text-xs text-slate-400">—{slot.end_time}</span>
                    </div>
                    <div>
                      <p className="font-medium text-slate-900 dark:text-white">{slot.teacher_name}</p>
                      {slot.notes && <p className="text-xs text-slate-400 mt-0.5">{slot.notes}</p>}
                    </div>
                  </div>
                  <Button onClick={() => bookMut.mutate(slot.id)} loading={bookMut.isPending} disabled={!selectedChild}>
                    <CheckCircleIcon className="h-4 w-4 mr-1" /> Book
                  </Button>
                </div>
              ))}
            </div>
          )}
          {!selectedChild && availableSlots.length > 0 && (
            <p className="text-sm text-amber-600 dark:text-amber-400 flex items-center gap-1">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
              </svg>
              Select a child to enable booking
            </p>
          )}
        </>
      )}

      {/* My Booked Slots Tab (with Zoom join) */}
      {activeTab === "booked" && (
        <>
          {bookedLoading ? (
            <div className="space-y-2">{[1,2,3].map(i => <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : bookedSlots.length === 0 ? (
            <EmptyState icon={CalendarDaysIcon} title="No booked slots" description="You haven&apos;t booked any conference slots yet. Switch to Available Slots to book one." />
          ) : (
            <div className="space-y-2">
              {bookedSlots.map(slot => (
                <div key={slot.id} className="bg-white dark:bg-slate-800 rounded-xl border border-indigo-200 dark:border-indigo-800 p-4 transition-shadow hover:shadow-sm">
                  {/* Main row */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="flex flex-col items-center w-16">
                        <span className="text-lg font-bold text-slate-900 dark:text-white">{slot.start_time}</span>
                        <span className="text-xs text-slate-400">—{slot.end_time}</span>
                      </div>
                      <div>
                        <p className="font-medium text-slate-900 dark:text-white">{slot.teacher_name}</p>
                        <p className="text-sm text-indigo-600 dark:text-indigo-400">{slot.student_name}</p>
                        {slot.notes && <p className="text-xs text-slate-400 mt-0.5">{slot.notes}</p>}
                        {/* Zoom status badge */}
                        {slot.is_zoom_created && (
                          <div className="mt-1"><Badge color="green" dot>Zoom meeting ready</Badge></div>
                        )}
                      </div>
                    </div>
                    {/* Zoom Join button */}
                    {slot.is_zoom_created && slot.zoom_join_url ? (
                      <a
                        href={slot.zoom_join_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition-colors"
                      >
                        <VideoCameraIcon className="h-4 w-4" />
                        Join Meeting
                      </a>
                    ) : slot.is_booked && !slot.is_zoom_created ? (
                      <span className="text-xs text-slate-400 dark:text-slate-500 italic">
                        Zoom meeting not yet created
                      </span>
                    ) : null}
                  </div>

                  {/* Zoom meeting details */}
                  {slot.is_zoom_created && slot.zoom_join_url && (
                    <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700">
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400">
                          <VideoCameraIcon className="h-4 w-4" />
                          <span>ID: <span className="font-mono text-slate-700 dark:text-slate-300">{slot.zoom_meeting_id}</span></span>
                        </div>
                        {slot.zoom_password && (
                          <div className="text-slate-500 dark:text-slate-400">
                            Pass: <span className="font-mono text-slate-700 dark:text-slate-300">{slot.zoom_password}</span>
                          </div>
                        )}
                        <span className="text-xs text-slate-400">{slot.date}</span>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
