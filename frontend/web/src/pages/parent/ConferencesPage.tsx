/** Conference Scheduler — Parent view for booking slots for their children */

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  CalendarDaysIcon, UsersIcon, CheckCircleIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, EmptyState } from "../../components/common";

interface ConferenceSlot {
  id: string;
  teacher_name: string;
  student_name: string | null;
  date: string;
  start_time: string;
  end_time: string;
  is_booked: boolean;
  notes: string;
}

export default function ParentConferencesPage() {
  const [date, setDate] = useState(dayjs().format("YYYY-MM-DD"));
  const [selectedChild, setSelectedChild] = useState<string>("");
  const qc = useQueryClient();

  const { data: children = [] } = useQuery({
    queryKey: ["my-children"],
    queryFn: async () => {
      const res = await api.get<{ results: any[] }>("/students/students/");
      return res.results ?? [];
    },
  });

  const { data: slots = [], isLoading } = useQuery({
    queryKey: ["parent-conference-slots", date],
    queryFn: async () => {
      const res = await api.get<{ results: ConferenceSlot[] }>("/conferences/conference-slots/", { date });
      return (res.results ?? []).filter(s => !s.is_booked);
    },
  });

  const bookMut = useMutation({
    mutationFn: (slotId: string) =>
      api.post(`/conferences/conference-slots/${slotId}/book/`, { student_id: selectedChild }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["parent-conference-slots"] }); toast.success("Slot booked!"); },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Failed to book slot"),
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Conference Scheduler</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Book parent-teacher conference slots for your children</p>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <CalendarDaysIcon className="h-5 w-5 text-slate-400" />
          <input type="date" value={date} onChange={e => setDate(e.target.value)}
            className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        {children.length > 0 && (
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

      {isLoading ? (
        <div className="space-y-2">{[1,2,3].map(i => <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
      ) : slots.length === 0 ? (
        <EmptyState icon={CalendarDaysIcon} title="No available slots" description="No conference slots available for this date. Check back later or try another date." />
      ) : (
        <div className="space-y-2">
          {slots.map(slot => (
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

      {!selectedChild && slots.length > 0 && (
        <p className="text-sm text-amber-600 dark:text-amber-400 flex items-center gap-1">
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
          Select a child to enable booking
        </p>
      )}
    </div>
  );
}
