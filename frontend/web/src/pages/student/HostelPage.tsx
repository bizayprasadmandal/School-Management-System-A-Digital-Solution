/**
 * Student Hostel Page — View room assignment, complaints, and visitor logs.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { HomeIcon, ExclamationTriangleIcon, UserGroupIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface RoomAssignment {
  id: string;
  room_number: string;
  hostel_name: string;
  bed_number: string;
  check_in_date: string;
  status_display: string;
}
interface Complaint {
  id: string;
  category: string;
  description: string;
  status_display: string;
  priority: string;
  created_at: string;
}
interface Visitor {
  id: string;
  visitor_name: string;
  relationship: string;
  visit_date: string;
  purpose: string;
  status_display: string;
}

type Tab = "room" | "complaints" | "visitors";
const TABS: { key: Tab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "room", label: "My Room", icon: HomeIcon },
  { key: "complaints", label: "Complaints", icon: ExclamationTriangleIcon },
  { key: "visitors", label: "Visitors", icon: UserGroupIcon },
];

export default function StudentHostelPage() {
  useTitle("Hostel");
  const [tab, setTab] = useState<Tab>("room");

  const { data: room, isLoading: rLoading } = useQuery({
    queryKey: ["student-room"],
    queryFn: async () => {
      const r = await api.get<{ results: RoomAssignment[] }>("/hostel/assignments/my/");
      return r.results?.[0] ?? null;
    },
  });
  const { data: complaints = [], isLoading: cLoading } = useQuery({
    queryKey: ["student-complaints"],
    queryFn: async () => {
      const r = await api.get<{ results: Complaint[] }>("/hostel/complaints/my/");
      return r.results ?? [];
    },
  });
  const { data: visitors = [], isLoading: vLoading } = useQuery({
    queryKey: ["student-visitors"],
    queryFn: async () => {
      const r = await api.get<{ results: Visitor[] }>("/hostel/visitors/my/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Hostel</h1>
        <p className="text-sm text-slate-500 mt-1">Your room, complaints, and visitor logs</p>
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

      {tab === "room" &&
        (rLoading ? (
          <div className="h-32 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ) : !room ? (
          <EmptyState
            icon={HomeIcon}
            title="No room assigned"
            description="You don't have a hostel room assigned yet"
          />
        ) : (
          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
              {room.hostel_name}
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4">
              <InfoCard label="Room" value={room.room_number} />
              <InfoCard label="Bed" value={room.bed_number} />
              <InfoCard label="Check-in" value={dayjs(room.check_in_date).format("MMM D, YYYY")} />
              <InfoCard label="Status" value={room.status_display} />
            </div>
          </div>
        ))}

      {tab === "complaints" &&
        (cLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !complaints.length ? (
          <EmptyState
            icon={ExclamationTriangleIcon}
            title="No complaints"
            description="No complaints filed"
          />
        ) : (
          <div className="space-y-2">
            {complaints.map((c) => (
              <div
                key={c.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{c.category}</p>
                    <p className="text-sm text-slate-500 mt-0.5">{c.description}</p>
                    <p className="text-xs text-slate-400 mt-1">
                      {dayjs(c.created_at).format("MMM D, YYYY")}
                    </p>
                  </div>
                  <div className="text-right">
                    <Badge
                      color={
                        c.priority === "high" ? "red" : c.priority === "medium" ? "amber" : "blue"
                      }
                    >
                      {c.priority}
                    </Badge>
                    <Badge color="slate">{c.status_display}</Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}

      {tab === "visitors" &&
        (vLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !visitors.length ? (
          <EmptyState icon={UserGroupIcon} title="No visitors" description="No visitor logs" />
        ) : (
          <div className="space-y-2">
            {visitors.map((v) => (
              <div
                key={v.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">{v.visitor_name}</p>
                    <p className="text-xs text-slate-400">
                      {v.relationship} · {dayjs(v.visit_date).format("MMM D, YYYY")}
                    </p>
                    {v.purpose && (
                      <p className="text-xs text-slate-500 mt-0.5">Purpose: {v.purpose}</p>
                    )}
                  </div>
                  <Badge color="green">{v.status_display}</Badge>
                </div>
              </div>
            ))}
          </div>
        ))}
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-50 dark:bg-slate-700/50 rounded-xl p-4">
      <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase">{label}</p>
      <p className="text-sm font-semibold text-slate-900 dark:text-white mt-1">{value}</p>
    </div>
  );
}
