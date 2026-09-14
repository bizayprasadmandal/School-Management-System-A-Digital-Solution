/**
 * Parent Health Page — View child's health records, visits, and immunizations.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { HeartIcon, ClockIcon, ShieldCheckIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface HealthRecord {
  id: string;
  student_name: string;
  blood_type: string;
  allergies: string;
  chronic_conditions: string;
}
interface NurseVisit {
  id: string;
  student_name: string;
  visit_type_display: string;
  visit_date: string;
  diagnosis: string;
}
interface Immunization {
  id: string;
  student_name: string;
  vaccine_name: string;
  dose_number: number;
  date_administered: string;
  next_due_date: string | null;
}

type Tab = "records" | "visits" | "immunizations";

export default function ParentHealthPage() {
  useTitle("Child Health");
  const [tab, setTab] = useState<Tab>("records");

  const { data: records = [], isLoading: rLoading } = useQuery({
    queryKey: ["parent-health-records"],
    queryFn: async () => {
      const r = await api.get<{ results: HealthRecord[] }>("/health/records/children/");
      return r.results ?? [];
    },
  });
  const { data: visits = [], isLoading: vLoading } = useQuery({
    queryKey: ["parent-health-visits"],
    queryFn: async () => {
      const r = await api.get<{ results: NurseVisit[] }>("/health/visits/children/");
      return r.results ?? [];
    },
  });
  const { data: immunizations = [], isLoading: iLoading } = useQuery({
    queryKey: ["parent-health-imm"],
    queryFn: async () => {
      const r = await api.get<{ results: Immunization[] }>("/health/immunizations/children/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Child Health</h1>
        <p className="text-sm text-slate-500 mt-1">View your children&apos;s health records</p>
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        {[
          { key: "records" as Tab, label: "Health Records", icon: HeartIcon },
          { key: "visits" as Tab, label: "Nurse Visits", icon: ClockIcon },
          {
            key: "immunizations" as Tab,
            label: "Immunizations",
            icon: ShieldCheckIcon,
          },
        ].map((t) => {
          const I = t.icon;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap transition-colors ${
                tab === t.key
                  ? "bg-white dark:bg-slate-700 shadow-sm text-slate-900 dark:text-white"
                  : "text-slate-600 dark:text-slate-400"
              }`}
            >
              <I className="h-4 w-4" />
              {t.label}
            </button>
          );
        })}
      </div>

      {tab === "records" &&
        (rLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-20 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !records.length ? (
          <EmptyState icon={HeartIcon} title="No health records" />
        ) : (
          <div className="space-y-2">
            {records.map((r) => (
              <div
                key={r.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <p className="font-semibold text-slate-900 dark:text-white">{r.student_name}</p>
                <p className="text-xs text-slate-400">Blood: {r.blood_type}</p>
                {r.allergies && (
                  <p className="text-xs text-red-500 mt-1">⚠️ Allergies: {r.allergies}</p>
                )}
                {r.chronic_conditions && (
                  <p className="text-xs text-amber-600 mt-1">Conditions: {r.chronic_conditions}</p>
                )}
              </div>
            ))}
          </div>
        ))}

      {tab === "visits" &&
        (vLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !visits.length ? (
          <EmptyState icon={ClockIcon} title="No visits" />
        ) : (
          <div className="space-y-2">
            {visits.map((v) => (
              <div
                key={v.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <p className="font-semibold text-slate-900 dark:text-white">{v.student_name}</p>
                <p className="text-xs text-slate-400">
                  {v.visit_type_display} · {dayjs(v.visit_date).format("MMM D, YYYY")}
                </p>
                {v.diagnosis && (
                  <p className="text-sm text-slate-500 mt-1">Diagnosis: {v.diagnosis}</p>
                )}
              </div>
            ))}
          </div>
        ))}

      {tab === "immunizations" &&
        (iLoading ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-20 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !immunizations.length ? (
          <EmptyState icon={ShieldCheckIcon} title="No immunizations" />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {immunizations.map((i) => (
              <div
                key={i.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <p className="font-semibold text-sm text-slate-900 dark:text-white">
                  {i.vaccine_name}
                </p>
                <p className="text-xs text-slate-400">
                  {i.student_name} · Dose {i.dose_number} ·{" "}
                  {dayjs(i.date_administered).format("MMM D, YYYY")}
                </p>
                {i.next_due_date && (
                  <p className="text-xs text-amber-600 mt-1">
                    Next due: {dayjs(i.next_due_date).format("MMM D, YYYY")}
                  </p>
                )}
              </div>
            ))}
          </div>
        ))}
    </div>
  );
}
