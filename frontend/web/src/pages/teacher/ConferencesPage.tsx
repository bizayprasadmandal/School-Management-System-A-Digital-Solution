/**
 * Conference Scheduler — Teacher view for managing their own slots
 * with Zoom meeting integration.
 */

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  PlusIcon,
  CalendarDaysIcon,
  CheckCircleIcon,
  XCircleIcon,
  VideoCameraIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";

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

interface ZoomMeetingResponse {
  detail: string;
  meeting?: {
    id: string;
    topic: string;
    join_url: string;
    start_url: string;
    password: string;
    duration: number;
    start_time: string;
  };
}

export default function TeacherConferencesPage() {
  const [date, setDate] = useState(dayjs().format("YYYY-MM-DD"));
  const [showForm, setShowForm] = useState(false);
  const qc = useQueryClient();

  const { data: slots = [], isLoading } = useQuery({
    queryKey: ["teacher-conference-slots", date],
    queryFn: async () => {
      const res = await api.get<{ results: ConferenceSlot[] }>("/conferences/conference-slots/", {
        date,
      });
      return res.results ?? [];
    },
  });

  const createMut = useMutation({
    mutationFn: (data: { date: string; start_time: string; end_time: string; notes: string }) =>
      api.post("/conferences/conference-slots/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teacher-conference-slots"] });
      toast.success("Slot created");
      setShowForm(false);
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Failed to create slot"),
  });

  const cancelMut = useMutation({
    mutationFn: (id: string) => api.post(`/conferences/conference-slots/${id}/cancel/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teacher-conference-slots"] });
      toast.success("Booking cancelled");
    },
  });

  const completeMut = useMutation({
    mutationFn: (id: string) => api.post(`/conferences/conference-slots/${id}/complete/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teacher-conference-slots"] });
      toast.success("Conference completed");
    },
  });

  // ─── Zoom Meeting Mutations ──────────────────────────────────────────────

  const createZoomMut = useMutation({
    mutationFn: (slotId: string) =>
      api.post<ZoomMeetingResponse>(`/conferences/conference-slots/${slotId}/create-zoom/`),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["teacher-conference-slots"] });
      toast.success(data.detail || "Zoom meeting created!");
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Failed to create Zoom meeting"),
  });

  const deleteZoomMut = useMutation({
    mutationFn: (slotId: string) =>
      api.post<{ detail: string }>(`/conferences/conference-slots/${slotId}/delete-zoom/`),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["teacher-conference-slots"] });
      toast.success(data.detail || "Zoom meeting removed");
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Failed to delete Zoom meeting"),
  });

  const [newSlot, setNewSlot] = useState({ start_time: "09:00", end_time: "09:30", notes: "" });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">My Conference Slots</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Manage your parent-teacher conference availability
          </p>
        </div>
        <Button onClick={() => setShowForm(true)}>
          <PlusIcon className="h-4 w-4 mr-1.5" /> Add Slot
        </Button>
      </div>

      <div className="flex items-center gap-3">
        <CalendarDaysIcon className="h-5 w-5 text-slate-400" />
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
        />
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />
          ))}
        </div>
      ) : slots.length === 0 ? (
        <EmptyState
          icon={CalendarDaysIcon}
          title="No slots"
          description="Create your first conference slot for this date"
        />
      ) : (
        <div className="space-y-2">
          {slots.map((slot) => (
            <div
              key={slot.id}
              className={`bg-white dark:bg-slate-800 rounded-xl border p-4 ${
                slot.is_booked
                  ? "border-indigo-200 dark:border-indigo-800"
                  : "border-slate-200 dark:border-slate-700"
              }`}
            >
              {/* Main row */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex flex-col items-center w-16">
                    <span className="text-lg font-bold text-slate-900 dark:text-white">
                      {slot.start_time}
                    </span>
                    <span className="text-xs text-slate-400">—{slot.end_time}</span>
                  </div>
                  <div>
                    {slot.is_booked ? (
                      <>
                        <p className="font-medium text-indigo-600 dark:text-indigo-400">
                          Booked — {slot.student_name}
                        </p>
                        <p className="text-xs text-slate-400 mt-0.5">{slot.notes}</p>
                      </>
                    ) : (
                      <>
                        <p className="font-medium text-green-600 dark:text-green-400">Available</p>
                        {slot.notes && (
                          <p className="text-xs text-slate-400 mt-0.5">{slot.notes}</p>
                        )}
                      </>
                    )}
                    {/* Zoom status badge */}
                    {slot.is_zoom_created && (
                      <div className="mt-1">
                        <Badge color="green" dot>
                          Zoom meeting ready
                        </Badge>
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  {slot.is_booked ? (
                    <>
                      {/* Zoom actions */}
                      {slot.is_zoom_created ? (
                        <div className="flex items-center gap-2">
                          <a
                            href={slot.zoom_join_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-700 transition-colors"
                          >
                            <VideoCameraIcon className="h-3.5 w-3.5" />
                            Join
                          </a>
                          <Button
                            size="sm"
                            variant="danger"
                            onClick={() => {
                              if (confirm("Remove the Zoom meeting for this slot?"))
                                deleteZoomMut.mutate(slot.id);
                            }}
                            loading={deleteZoomMut.isPending}
                            title="Delete Zoom meeting"
                          >
                            <TrashIcon className="h-4 w-4 mr-1" /> Remove Zoom
                          </Button>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => createZoomMut.mutate(slot.id)}
                          loading={createZoomMut.isPending}
                        >
                          <VideoCameraIcon className="h-4 w-4 mr-1" /> Zoom
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => completeMut.mutate(slot.id)}
                        loading={completeMut.isPending}
                      >
                        <CheckCircleIcon className="h-4 w-4 mr-1" /> Complete
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => cancelMut.mutate(slot.id)}
                        loading={cancelMut.isPending}
                      >
                        <XCircleIcon className="h-4 w-4 mr-1" /> Cancel
                      </Button>
                    </>
                  ) : (
                    <Button
                      size="sm"
                      variant="danger"
                      onClick={() => cancelMut.mutate(slot.id)}
                      loading={cancelMut.isPending}
                    >
                      <XCircleIcon className="h-4 w-4 mr-1" /> Remove
                    </Button>
                  )}
                </div>
              </div>

              {/* Zoom meeting details (collapsible) */}
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
                    <a
                      href={slot.zoom_start_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-semibold text-xs"
                    >
                      Start meeting →
                    </a>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <Modal open={showForm} onClose={() => setShowForm(false)} title="Create Conference Slot">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Date
            </label>
            <input
              type="date"
              value={date}
              disabled
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 px-3 py-2 text-sm dark:text-slate-200"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Start Time
              </label>
              <input
                type="time"
                value={newSlot.start_time}
                onChange={(e) => setNewSlot((p) => ({ ...p, start_time: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                End Time
              </label>
              <input
                type="time"
                value={newSlot.end_time}
                onChange={(e) => setNewSlot((p) => ({ ...p, end_time: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
              />
            </div>
          </div>
          <div>
            <label
              htmlFor="slot-notes"
              className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1"
            >
              Notes (optional)
            </label>
            <textarea
              id="slot-notes"
              value={newSlot.notes}
              onChange={(e) => setNewSlot((p) => ({ ...p, notes: e.target.value }))}
              rows={2}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setShowForm(false)}>
              Cancel
            </Button>
            <Button
              onClick={() => createMut.mutate({ date, ...newSlot })}
              loading={createMut.isPending}
            >
              Create Slot
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
