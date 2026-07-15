/**
 * Admissions & Enrollment — Admin page for applications, intakes, and reviews.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import { PlusIcon, DocumentTextIcon, CalendarDaysIcon, ClipboardDocumentCheckIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface Application { id:string; application_number:string; full_name:string; email:string; phone:string; applying_for_grade:string; status:string; status_display:string; intake_name:string; submitted_at:string|null; }
interface Intake { id:string; name:string; academic_year:string; application_start:string; application_end:string; status:string; status_display:string; application_count:number; }
interface Review { id:string; application:string; reviewer_name:string; score:number|null; recommendation:string; notes:string; }

const ST_COLORS:Record<string,string> = { draft:"bg-slate-100 text-slate-600", submitted:"bg-blue-100 text-blue-700", under_review:"bg-amber-100 text-amber-700", shortlisted:"bg-indigo-100 text-indigo-700", accepted:"bg-green-100 text-green-700", rejected:"bg-red-100 text-red-700", waitlisted:"bg-yellow-100 text-yellow-700", enrolled:"bg-green-100 text-green-700", cancelled:"bg-slate-100 text-slate-500" };

type Tab = "applications"|"intakes"|"reviews";
const TABS:{key:Tab;label:string;icon:React.ComponentType<{className?:string}>}[] = [
  {key:"applications",label:"Applications",icon:DocumentTextIcon},{key:"intakes",label:"Intake Periods",icon:CalendarDaysIcon},{key:"reviews",label:"Reviews",icon:ClipboardDocumentCheckIcon},
];

export default function AdmissionsPage() {
  useTitle("Admissions & Enrollment"); const qc = useQueryClient();
  const [tab,setTab]=useState<Tab>("applications"); const [search,setSearch]=useState("");
  const {data:apps=[]}=useQuery({queryKey:["admissions-apps"],queryFn:async()=>{const r=await api.get<{results:Application[]}>("/admissions/applications/");return r.results??[]}});
  const {data:intakes=[]}=useQuery({queryKey:["admissions-intakes"],queryFn:async()=>{const r=await api.get<{results:Intake[]}>("/admissions/intakes/");return r.results??[]}});
  const {data:reviews=[]}=useQuery({queryKey:["admissions-reviews"],queryFn:async()=>{const r=await api.get<{results:Review[]}>("/admissions/reviews/");return r.results??[]}});

  const submitApp = useMutation({mutationFn:(id:string)=>api.post(`/admissions/applications/${id}/submit/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["admissions-apps"]});toast.success("Submitted")}});
  const updateStatus = useMutation({mutationFn:({id,status}:{id:string;status:string})=>api.post(`/admissions/applications/${id}/update-status/`,{status}),onSuccess:()=>{qc.invalidateQueries({queryKey:["admissions-apps"]});toast.success("Status updated")}});

  const filtered = search.trim()?apps.filter(a=>a.full_name?.toLowerCase().includes(search.toLowerCase())||a.application_number.toLowerCase().includes(search.toLowerCase())):apps;

  return (<div className="space-y-6">
    <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-slate-900 dark:text-white">Admissions & Enrollment</h1><p className="text-sm text-slate-500 mt-1">Manage applications, intake periods, and admission reviews</p></div></div>
    <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
      {TABS.map(t=>{const Icon=t.icon;return(<button key={t.key} onClick={()=>setTab(t.key)} className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap ${tab===t.key?"bg-white dark:bg-slate-700 shadow-sm":"text-slate-600 hover:text-slate-900"}`}><Icon className="h-4 w-4"/>{t.label}</button>)})}
    </div>
    {tab==="applications"&&(<>{apps.length>0&&<div className="relative max-w-sm"><input value={search} onChange={e=>setSearch(e.target.value)} className="w-full pl-3 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm" placeholder="Search applications..."/></div>}
      {!apps.length?<EmptyState icon={DocumentTextIcon} title="No applications"/>:
      <div className="space-y-2">{filtered.map(a=><div key={a.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><div className="flex items-start justify-between"><div className="flex-1"><div className="flex items-center gap-2 mb-1"><p className="font-semibold">{a.full_name||a.application_number}</p><span className={`text-xs font-medium px-2 py-0.5 rounded ${ST_COLORS[a.status]||"bg-slate-100"}`}>{a.status_display}</span></div><p className="text-xs text-slate-400">{a.application_number} · Grade {a.applying_for_grade}{a.intake_name?` · ${a.intake_name}`:""}</p><p className="text-xs text-slate-400">{a.email}{a.submitted_at?` · Submitted ${dayjs(a.submitted_at).format("MMM D")}`:""}</p></div><div className="flex gap-2 ml-4">{a.status==="draft"&&<Button size="sm" variant="secondary" onClick={()=>submitApp.mutate(a.id)}>Submit</Button>}{["submitted","under_review","shortlisted"].includes(a.status)&&<select onChange={e=>updateStatus.mutate({id:a.id,status:e.target.value})} className="text-xs rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-2 py-1"><option value="">Change...</option><option value="under_review">Under Review</option><option value="shortlisted">Shortlisted</option><option value="accepted">Accepted</option><option value="rejected">Rejected</option><option value="waitlisted">Waitlisted</option></select>}</div></div></div>)}</div>}</>)}
    {tab==="intakes"&&(!intakes.length?<EmptyState icon={CalendarDaysIcon} title="No intake periods"/>:
      <div className="grid gap-3 sm:grid-cols-2">{intakes.map(i=><div key={i.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><div className="flex items-start justify-between"><p className="font-semibold">{i.name}</p><span className={`text-xs font-medium px-2 py-0.5 rounded ${i.status==="open"?"bg-green-100 text-green-700":i.status==="upcoming"?"bg-blue-100 text-blue-700":"bg-slate-100 text-slate-500"}`}>{i.status_display}</span></div><p className="text-xs text-slate-400">{i.academic_year} · {dayjs(i.application_start).format("MMM D")} - {dayjs(i.application_end).format("MMM D, YYYY")}</p><p className="text-xs text-slate-400">{i.application_count} applicant{i.application_count!==1?"s":""}</p></div>)}</div>)}
    {tab==="reviews"&&(!reviews.length?<EmptyState icon={ClipboardDocumentCheckIcon} title="No reviews"/>:
      <div className="space-y-2">{reviews.map(r=><div key={r.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><p className="font-semibold">Application Review</p><p className="text-xs text-slate-400">Reviewer: {r.reviewer_name}{r.score?` · Score: ${r.score}/100`:""}{r.recommendation?` · ${r.recommendation}`:""}</p>{r.notes&&<p className="text-xs text-slate-500 mt-1">{r.notes}</p>}</div>)}</div>)}
  </div>);
}
