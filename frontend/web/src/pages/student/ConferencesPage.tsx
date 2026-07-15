/**
 * Conference Scheduler — Student view for viewing booked conference slots
 * and joining Zoom meetings.
 */

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import {
  CalendarDaysIcon, VideoCameraIcon,
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
  zoom_meeting_id?: string;
  zoom_join_url?: string;
  zoom_start_url?: string;
  zoom_password?: string;
  is_zoom_created?: boolean;
}

export default function StudentConferencesPage() {
  const [date, setDate] = useState(dayjs().format("YYYY-MM-DD"));

  // Fetch booked slots for this student
  const { data: slots = [], isLoading } = useQuery({
    queryKey: ["student-conference-slots", date],
    queryFn: async () => {
      const res = await api.get<{ results: ConferenceSlot[] }>("/conferences/conference-slots/", {
        date,
        is_booked: true,
      });
      return res.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">My Conferences</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          View your booked parent-teacher conferences and join Zoom meetings
        </p>
      </div>

      <div className="flex items-center gap-3">
        <CalendarDaysIcon className="h-5 w-5 text-slate-400" />
        <input
          type="date"
          value={date}
          onChange={e => setDate(e.target.value)}
          className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
        />
        <span className="text-sm text-slate-500 dark:text-slate-400">
          {slots.length} slot{slots.length !== 1 ? "s" : ""} booked
        </span>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />
          ))}
        </div>
      ) : slots.length === 0 ? (
        <EmptyState
          icon={CalendarDaysIcon}
          title="No conferences booked"
          description="You don&apos;t have any parent-teacher conferences scheduled for this date."
        />
      ) : (
        <div className="space-y-2">
          {slots.map(slot => (
            <div
              key={slot.id}
              className="bg-white dark:bg-slate-800 rounded-xl border border-indigo-200 dark:border-indigo-800 p-4 transition-shadow hover:shadow-sm"
            >
              {/* Main row */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex flex-col items-center w-16">
                    <span className="text-lg font-bold text-slate-900 dark:text-white">{slot.start_time}</span>
                    <span className="text-xs text-slate-400">—{slot.end_time}</span>
                  </div>
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">{slot.teacher_name}</p>
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
                    Zoom link pending
                  </span>
                ) : null}
              </div>

              {/* Zoom meeting details */}
              {slot.is_zoom_created && slot.zoom_join_url && (
                <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700">
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1.5 text-slate-500 dark:text-slate-400">
                      <VideoCameraIcon className="h-4 w-4" />
                      <span>
                        ID:{" "}
                        <span className="font-mono text-slate-700 dark:text-slate-300">
                          {slot.zoom_meeting_id}
                        </span>
                      </span>
                    </div>
                    {slot.zoom_password && (
                      <div className="text-slate-500 dark:text-slate-400">
                        Pass:{" "}
                        <span className="font-mono text-slate-700 dark:text-slate-300">
                          {slot.zoom_password}
                        </span>
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
    </div>
  );
}
