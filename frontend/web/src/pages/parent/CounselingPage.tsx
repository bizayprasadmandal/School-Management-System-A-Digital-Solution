/**
 * Parent Counseling Page — View child's counseling sessions and referrals.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { ChatBubbleLeftRightIcon, UserGroupIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface Session {
  id: string;
  student_name: string;
  counselor_name: string;
  session_type: string;
  session_date: string;
  session_summary: string;
}
interface Referral {
  id: string;
  student_name: string;
  category: string;
  status: string;
  reason: string;
  created_at: string;
}

export default function ParentCounselingPage() {
  useTitle("Counseling");
  const [tab, setTab] = useState<"sessions" | "referrals">("sessions");
  const { data: sessions = [], isLoading: sLoading } = useQuery({
    queryKey: ["parent-counsel-sessions"],
    queryFn: async () => {
      const r = await api.get<{ results: Session[] }>("/counseling/sessions/children/");
      return r.results ?? [];
    },
  });
  const { data: referrals = [], isLoading: rLoading } = useQuery({
    queryKey: ["parent-counsel-referrals"],
    queryFn: async () => {
      const r = await api.get<{ results: Referral[] }>("/counseling/referrals/children/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Counseling</h1>
        <p className="text-sm text-slate-500 mt-1">Your children's counseling activities</p>
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        <button
          onClick={() => setTab("sessions")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "sessions" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <ChatBubbleLeftRightIcon className="h-4 w-4 inline mr-1.5" />
          Sessions
        </button>
        <button
          onClick={() => setTab("referrals")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${
            tab === "referrals" ? "bg-white dark:bg-slate-700 shadow-sm" : "text-slate-600"
          }`}
        >
          <UserGroupIcon className="h-4 w-4 inline mr-1.5" />
          Referrals
        </button>
      </div>
      {tab === "sessions" && <SessionList sessions={sessions} isLoading={sLoading} />}
      {tab === "referrals" && <ReferralList referrals={referrals} isLoading={rLoading} />}
    </div>
  );
}

function SessionList({ sessions, isLoading }: { sessions: Session[]; isLoading: boolean }) {
  if (isLoading)
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  if (!sessions.length)
    return (
      <EmptyState
        icon={ChatBubbleLeftRightIcon}
        title="No sessions"
        description="No counseling sessions recorded"
      />
    );
  return (
    <div className="space-y-2">
      {sessions.map((s) => (
        <div
          key={s.id}
          className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
        >
          <p className="font-semibold text-slate-900 dark:text-white">{s.student_name}</p>
          <p className="text-xs text-slate-400">
            {s.session_type} · Counselor: {s.counselor_name} ·{" "}
            {dayjs(s.session_date).format("MMM D, YYYY")}
          </p>
          {s.session_summary && <p className="text-sm text-slate-500 mt-2">{s.session_summary}</p>}
        </div>
      ))}
    </div>
  );
}

function ReferralList({ referrals, isLoading }: { referrals: Referral[]; isLoading: boolean }) {
  if (isLoading)
    return (
      <div className="space-y-2">
        {[1, 2].map((i) => (
          <div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
        ))}
      </div>
    );
  if (!referrals.length)
    return (
      <EmptyState icon={UserGroupIcon} title="No referrals" description="No counseling referrals" />
    );
  return (
    <div className="space-y-2">
      {referrals.map((r) => (
        <div
          key={r.id}
          className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="font-semibold text-slate-900 dark:text-white">{r.student_name}</p>
              <p className="text-sm text-slate-500 mt-0.5">{r.reason}</p>
              <p className="text-xs text-slate-400 mt-1">
                {dayjs(r.created_at).format("MMM D, YYYY")}
              </p>
            </div>
            <div className="flex gap-2">
              <Badge color="indigo">{r.category}</Badge>
              <Badge
                color={
                  r.status === "closed" ? "green" : r.status === "in_progress" ? "amber" : "slate"
                }
              >
                {r.status}
              </Badge>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
