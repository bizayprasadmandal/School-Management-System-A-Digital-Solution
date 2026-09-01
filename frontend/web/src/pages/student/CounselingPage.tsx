/**
 * Student Counseling Page — View appointments, sessions, and self-assessments.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import {
  CalendarDaysIcon,
  ClipboardDocumentCheckIcon,
  ChatBubbleLeftRightIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface Appointment {
  id: string;
  counselor_name: string;
  appointment_type: string;
  scheduled_date: string;
  scheduled_time: string;
  status: string;
  status_display: string;
}
interface Session {
  id: string;
  counselor_name: string;
  session_type: string;
  session_date: string;
  start_time: string;
  end_time: string;
  session_summary: string;
}
interface Screening {
  id: string;
  screening_type: string;
  administered_date: string;
  total_score: number;
  risk_level: string;
}

type Tab = "appointments" | "sessions" | "screenings";
const TABS: { key: Tab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "appointments", label: "Appointments", icon: CalendarDaysIcon },
  { key: "sessions", label: "Past Sessions", icon: ChatBubbleLeftRightIcon },
  { key: "screenings", label: "Self-Assessments", icon: ClipboardDocumentCheckIcon },
];

export default function StudentCounselingPage() {
  useTitle("Counseling");
  const [tab, setTab] = useState<Tab>("appointments");

  const { data: appointments = [], isLoading: aLoading } = useQuery({
    queryKey: ["student-appointments"],
    queryFn: async () => {
      const r = await api.get<{ results: Appointment[] }>("/counseling/appointments/my/");
      return r.results ?? [];
    },
  });
  const { data: sessions = [], isLoading: sLoading } = useQuery({
    queryKey: ["student-sessions"],
    queryFn: async () => {
      const r = await api.get<{ results: Session[] }>("/counseling/sessions/my/");
      return r.results ?? [];
    },
  });
  const { data: screenings = [], isLoading: scLoading } = useQuery({
    queryKey: ["student-screenings"],
    queryFn: async () => {
      const r = await api.get<{ results: Screening[] }>("/counseling/screenings/my/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Counseling</h1>
        <p className="text-sm text-slate-500 mt-1">Your appointments, sessions, and assessments</p>
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
        {TABS.map((t) => {
          const I = t.icon;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
                tab === t.key
                  ? "bg-white dark:bg-slate-700 shadow-sm text-slate-900 dark:text-white"
                  : "text-slate-600 hover:text-slate-900 dark:text-slate-400"
              }`}
            >
              <I className="h-4 w-4" />
              {t.label}
            </button>
          );
        })}
      </div>

      {tab === "appointments" &&
        (aLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !appointments.length ? (
          <EmptyState
            icon={CalendarDaysIcon}
            title="No appointments"
            description="You have no counseling appointments"
          />
        ) : (
          <div className="space-y-2">
            {appointments.map((a) => (
              <div
                key={a.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">
                      {a.appointment_type}
                    </p>
                    <p className="text-xs text-slate-400">Counselor: {a.counselor_name}</p>
                    <p className="text-xs text-slate-400">
                      {dayjs(a.scheduled_date).format("MMM D, YYYY")} at {a.scheduled_time}
                    </p>
                  </div>
                  <Badge
                    color={
                      a.status === "confirmed" ? "green" : a.status === "cancelled" ? "red" : "blue"
                    }
                  >
                    {a.status_display}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        ))}

      {tab === "sessions" &&
        (sLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !sessions.length ? (
          <EmptyState
            icon={ChatBubbleLeftRightIcon}
            title="No sessions"
            description="No past counseling sessions"
          />
        ) : (
          <div className="space-y-2">
            {sessions.map((s) => (
              <div
                key={s.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{s.session_type}</p>
                    <p className="text-xs text-slate-400">
                      Counselor: {s.counselor_name} · {dayjs(s.session_date).format("MMM D")}{" "}
                      {s.start_time}-{s.end_time}
                    </p>
                  </div>
                </div>
                {s.session_summary && (
                  <p className="text-sm text-slate-500 mt-2">{s.session_summary}</p>
                )}
              </div>
            ))}
          </div>
        ))}

      {tab === "screenings" &&
        (scLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !screenings.length ? (
          <EmptyState
            icon={ClipboardDocumentCheckIcon}
            title="No assessments"
            description="No self-assessments recorded"
          />
        ) : (
          <div className="space-y-2">
            {screenings.map((sc) => (
              <div
                key={sc.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">
                      {sc.screening_type}
                    </p>
                    <p className="text-xs text-slate-400">
                      {dayjs(sc.administered_date).format("MMM D, YYYY")}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-slate-900 dark:text-white">
                      {sc.total_score}
                    </p>
                    <Badge
                      color={
                        sc.risk_level === "low"
                          ? "green"
                          : sc.risk_level === "moderate"
                            ? "amber"
                            : "red"
                      }
                    >
                      {sc.risk_level}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}
    </div>
  );
}
