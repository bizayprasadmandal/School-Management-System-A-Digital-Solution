/**
 * Health & Clinic — Admin page for student health records, nurse visits, immunizations, medications.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import { PlusIcon, HeartIcon, ClockIcon, ShieldCheckIcon, BeakerIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState } from "../../components/common";
import { useTitle } from "../../hooks";

interface HealthRecord { id:string; student:string; student_name:string; blood_type:string; allergies:string; chronic_conditions:string; medications:string; }
interface NurseVisit { id:string; student:string; student_name:string; visit_type:string; visit_type_display:string; visit_date:string; symptoms:string; diagnosis:string; treatment:string; status_display:string; }
interface Immunization { id:string; student_name:string; vaccine_name:string; dose_number:number; date_administered:string; next_due_date:string|null; }
interface MedicationLog { id:string; student_name:string; medication_name:string; dosage:string; time_administered:string; }

type Tab = "records"|"visits"|"immunizations"|"medications";
const TABS:{key:Tab;label:string;icon:React.ComponentType<{className?:string}>}[] = [
  {key:"records",label:"Health Records",icon:HeartIcon},{key:"visits",label:"Nurse Visits",icon:ClockIcon},{key:"immunizations",label:"Immunizations",icon:ShieldCheckIcon},{key:"medications",label:"Medication Log",icon:BeakerIcon},
];

export default function HealthPage() {
  useTitle("Health & Clinic"); const qc = useQueryClient();
  const [tab,setTab]=useState<Tab>("records");
  const {data:records=[]}=useQuery({queryKey:["health-records"],queryFn:async()=>{const r=await api.get<{results:HealthRecord[]}>("/health/records/");return r.results??[]}});
  const {data:visits=[]}=useQuery({queryKey:["health-visits"],queryFn:async()=>{const r=await api.get<{results:NurseVisit[]}>("/health/visits/");return r.results??[]}});
  const {data:immunizations=[]}=useQuery({queryKey:["health-immunizations"],queryFn:async()=>{const r=await api.get<{results:Immunization[]}>("/health/immunizations/");return r.results??[]}});
  const {data:meds=[]}=useQuery({queryKey:["health-medications"],queryFn:async()=>{const r=await api.get<{results:MedicationLog[]}>("/health/medication-logs/");return r.results??[]}});
  const {data:students=[]}=useQuery({queryKey:["students-short"],queryFn:async()=>{const r=await api.get<{results:any[]}>("/students/");return r.results??[]}});

  return (<div className="space-y-6">
    <div><h1 className="text-2xl font-bold text-slate-900 dark:text-white">Health & Clinic</h1><p className="text-sm text-slate-500 mt-1">Student health records, nurse visits, immunizations, and medication logs</p></div>
    <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
      {TABS.map(t=>{const Icon=t.icon;return(<button key={t.key} onClick={()=>setTab(t.key)} className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap ${tab===t.key?"bg-white dark:bg-slate-700 shadow-sm":"text-slate-600 hover:text-slate-900"}`}><Icon className="h-4 w-4"/>{t.label}</button>)})}
    </div>
    {tab==="records"&&(!records.length?<EmptyState icon={HeartIcon} title="No health records" description="Create health records for students"/>:
      <div className="grid gap-3 sm:grid-cols-2">{records.map(r=><div key={r.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><p className="font-semibold">{r.student_name}</p><p className="text-xs text-slate-400">Blood: {r.blood_type}</p>{r.allergies&&<p className="text-xs text-red-500 mt-1">⚠️ Allergies: {r.allergies}</p>}{r.chronic_conditions&&<p className="text-xs text-amber-600 mt-1">Conditions: {r.chronic_conditions}</p>}</div>)}</div>)}
    {tab==="visits"&&(!visits.length?<EmptyState icon={ClockIcon} title="No visits" description="Log your first nurse visit"/>:
      <div className="space-y-2">{visits.map(v=><div key={v.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><div className="flex items-start justify-between"><div><p className="font-semibold">{v.student_name}</p><p className="text-xs text-slate-400">{v.visit_type_display} · {dayjs(v.visit_date).format("MMM D, h:mm A")}</p></div><span className="text-xs font-medium px-2 py-0.5 rounded bg-green-100 text-green-700">{v.status_display}</span></div>{v.symptoms&&<p className="text-xs text-slate-500 mt-1">Symptoms: {v.symptoms}</p>}{v.diagnosis&&<p className="text-xs text-slate-500">Diagnosis: {v.diagnosis}</p>}{v.treatment&&<p className="text-xs text-slate-500">Treatment: {v.treatment}</p>}</div>)}</div>)}
    {tab==="immunizations"&&(!immunizations.length?<EmptyState icon={ShieldCheckIcon} title="No immunizations" description="Record student immunizations"/>:
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{immunizations.map(i=><div key={i.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><p className="font-semibold text-sm">{i.vaccine_name}</p><p className="text-xs text-slate-400">{i.student_name} · Dose {i.dose_number}</p><p className="text-xs text-slate-400">{dayjs(i.date_administered).format("MMM D, YYYY")}{i.next_due_date?` · Next: ${dayjs(i.next_due_date).format("MMM D, YYYY")}`:""}</p></div>)}</div>)}
    {tab==="medications"&&(!meds.length?<EmptyState icon={BeakerIcon} title="No medication logs" description="Log student medications"/>:
      <div className="space-y-2">{meds.map(m=><div key={m.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><p className="font-semibold">{m.student_name}</p><p className="text-sm">{m.medication_name} · {m.dosage}</p><p className="text-xs text-slate-400">{dayjs(m.time_administered).format("MMM D, YYYY h:mm A")}</p></div>)}</div>)}
  </div>);
}
