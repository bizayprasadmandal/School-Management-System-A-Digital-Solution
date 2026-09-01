/**
 * Student Health Page — View personal health records, nurse visits,
 * immunizations, and medication logs (read-only for students).
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { HeartIcon, ClockIcon, ShieldCheckIcon, BeakerIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, SkeletonCard } from "../../components/common";
import { useTitle } from "../../hooks";

interface HealthRecord {
  id: string;
  student_name: string;
  blood_type: string;
  allergies: string;
  chronic_conditions: string;
  medications: string;
  emergency_contact_name: string;
}
interface NurseVisit {
  id: string;
  student_name: string;
  visit_type_display: string;
  visit_date: string;
  symptoms: string;
  diagnosis: string;
  treatment: string;
  status_display: string;
}
interface Immunization {
  id: string;
  student_name: string;
  vaccine_name: string;
  dose_number: number;
  date_administered: string;
  next_due_date: string | null;
}
interface MedicationLog {
  id: string;
  student_name: string;
  medication_name: string;
  dosage: string;
  time_administered: string;
}

type Tab = "records" | "visits" | "immunizations" | "medications";
const TABS: { key: Tab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "records", label: "Health Record", icon: HeartIcon },
  { key: "visits", label: "Nurse Visits", icon: ClockIcon },
  { key: "immunizations", label: "Immunizations", icon: ShieldCheckIcon },
  { key: "medications", label: "Medications", icon: BeakerIcon },
];

export default function StudentHealthPage() {
  useTitle("Health");
  const [tab, setTab] = useState<Tab>("records");

  const { data: record, isLoading: rLoading } = useQuery({
    queryKey: ["student-health-record"],
    queryFn: async () => {
      const r = await api.get<{ results: HealthRecord[] }>("/health/records/my/");
      return r.results?.[0] ?? null;
    },
  });

  const { data: visits = [], isLoading: vLoading } = useQuery({
    queryKey: ["student-health-visits"],
    queryFn: async () => {
      const r = await api.get<{ results: NurseVisit[] }>("/health/visits/my/");
      return r.results ?? [];
    },
  });

  const { data: immunizations = [], isLoading: iLoading } = useQuery({
    queryKey: ["student-health-immunizations"],
    queryFn: async () => {
      const r = await api.get<{ results: Immunization[] }>("/health/immunizations/my/");
      return r.results ?? [];
    },
  });

  const { data: meds = [], isLoading: mLoading } = useQuery({
    queryKey: ["student-health-medications"],
    queryFn: async () => {
      const r = await api.get<{ results: MedicationLog[] }>("/health/medication-logs/my/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Health</h1>
        <p className="text-sm text-slate-500 mt-1">
          Your health records, nurse visits, and immunizations
        </p>
      </div>

      {/* Tab bar */}
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

      {/* Health Record Tab */}
      {tab === "records" &&
        (rLoading ? (
          <SkeletonCard />
        ) : !record ? (
          <EmptyState
            icon={HeartIcon}
            title="No health record"
            description="Your health record has not been created yet"
          />
        ) : (
          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <InfoCard label="Blood Type" value={record.blood_type || "Unknown"} />
              <InfoCard label="Emergency Contact" value={record.emergency_contact_name || "—"} />
              <InfoCard label="Medications" value={record.medications || "None"} />
            </div>
            {record.allergies && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4">
                <p className="text-sm font-semibold text-red-700 dark:text-red-400">⚠️ Allergies</p>
                <p className="text-sm text-red-600 dark:text-red-300 mt-1">{record.allergies}</p>
              </div>
            )}
            {record.chronic_conditions && (
              <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4">
                <p className="text-sm font-semibold text-amber-700 dark:text-amber-400">
                  Chronic Conditions
                </p>
                <p className="text-sm text-amber-600 dark:text-amber-300 mt-1">
                  {record.chronic_conditions}
                </p>
              </div>
            )}
          </div>
        ))}

      {/* Nurse Visits Tab */}
      {tab === "visits" &&
        (vLoading ? (
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !visits.length ? (
          <EmptyState
            icon={ClockIcon}
            title="No nurse visits"
            description="You have no recorded nurse visits"
          />
        ) : (
          <div className="space-y-2">
            {visits.map((v) => (
              <div
                key={v.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs text-slate-400">
                      {v.visit_type_display} · {dayjs(v.visit_date).format("MMM D, YYYY h:mm A")}
                    </p>
                    {v.symptoms && (
                      <p className="text-sm text-slate-600 dark:text-slate-300 mt-1">
                        Symptoms: {v.symptoms}
                      </p>
                    )}
                    {v.diagnosis && (
                      <p className="text-sm text-slate-600 dark:text-slate-300">
                        Diagnosis: {v.diagnosis}
                      </p>
                    )}
                    {v.treatment && (
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        Treatment: {v.treatment}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}

      {/* Immunizations Tab */}
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
          <EmptyState
            icon={ShieldCheckIcon}
            title="No immunizations"
            description="No immunization records found"
          />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {immunizations.map((i) => (
              <div
                key={i.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <p className="font-semibold text-sm text-slate-900 dark:text-white">
                  {i.vaccine_name}
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  Dose {i.dose_number} · {dayjs(i.date_administered).format("MMM D, YYYY")}
                </p>
                {i.next_due_date && (
                  <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                    Next due: {dayjs(i.next_due_date).format("MMM D, YYYY")}
                  </p>
                )}
              </div>
            ))}
          </div>
        ))}

      {/* Medications Tab */}
      {tab === "medications" &&
        (mLoading ? (
          <div className="space-y-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !meds.length ? (
          <EmptyState
            icon={BeakerIcon}
            title="No medication logs"
            description="No medications have been recorded"
          />
        ) : (
          <div className="space-y-2">
            {meds.map((m) => (
              <div
                key={m.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
              >
                <p className="font-semibold text-slate-900 dark:text-white">{m.medication_name}</p>
                <p className="text-sm text-slate-600 dark:text-slate-300">{m.dosage}</p>
                <p className="text-xs text-slate-400">
                  {dayjs(m.time_administered).format("MMM D, YYYY h:mm A")}
                </p>
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
      <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
        {label}
      </p>
      <p className="text-sm font-semibold text-slate-900 dark:text-white mt-1">{value}</p>
    </div>
  );
}
