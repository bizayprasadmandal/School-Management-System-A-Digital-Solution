/**
 * Alumni Management — Admin page for alumni profiles, events, donations, chapters.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import { PlusIcon, UsersIcon, CalendarDaysIcon, CurrencyDollarIcon, GlobeAltIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState } from "../../components/common";
import { useTitle } from "../../hooks";

interface Profile { id:string; user_name:string; user_email:string; graduation_year:number; occupation:string; employer:string; city:string; country:string; }
interface Event { id:string; title:string; event_date:string; location:string; status:string; status_display:string; }
interface Donation { id:string; alumni_name:string; amount:number; fund_type_display:string; donation_date:string; is_recurring:boolean; }
interface Chapter { id:string; name:string; city:string; country:string; president_name:string|null; is_active:boolean; }

type Tab = "profiles"|"events"|"donations"|"chapters";
const TABS:{key:Tab;label:string;icon:React.ComponentType<{className?:string}>}[] = [
  {key:"profiles",label:"Alumni",icon:UsersIcon},{key:"events",label:"Events",icon:CalendarDaysIcon},{key:"donations",label:"Donations",icon:CurrencyDollarIcon},{key:"chapters",label:"Chapters",icon:GlobeAltIcon},
];

export default function AlumniPage() {
  useTitle("Alumni Management"); const qc = useQueryClient();
  const [tab,setTab]=useState<Tab>("profiles"); const [search,setSearch]=useState("");
  const {data:profiles=[]}=useQuery({queryKey:["alumni-profiles"],queryFn:async()=>{const r=await api.get<{results:Profile[]}>("/alumni/profiles/");return r.results??[]}});
  const {data:events=[]}=useQuery({queryKey:["alumni-events"],queryFn:async()=>{const r=await api.get<{results:Event[]}>("/alumni/events/");return r.results??[]}});
  const {data:donations=[]}=useQuery({queryKey:["alumni-donations"],queryFn:async()=>{const r=await api.get<{results:Donation[]}>("/alumni/donations/");return r.results??[]}});
  const {data:chapters=[]}=useQuery({queryKey:["alumni-chapters"],queryFn:async()=>{const r=await api.get<{results:Chapter[]}>("/alumni/chapters/");return r.results??[]}});

  const filtered = search.trim()?profiles.filter(p=>p.user_name.toLowerCase().includes(search.toLowerCase())||p.occupation?.toLowerCase().includes(search.toLowerCase())):profiles;

  return (<div className="space-y-6">
    <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-slate-900 dark:text-white">Alumni Management</h1><p className="text-sm text-slate-500 mt-1">Manage alumni profiles, events, donations, and chapters</p></div></div>
    <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
      {TABS.map(t=>{const Icon=t.icon;return(<button key={t.key} onClick={()=>setTab(t.key)} className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap ${tab===t.key?"bg-white dark:bg-slate-700 shadow-sm":"text-slate-600 hover:text-slate-900"}`}><Icon className="h-4 w-4"/>{t.label}</button>)})}
    </div>
    {tab==="profiles"&&(<>{profiles.length>0&&<div className="relative max-w-sm"><input value={search} onChange={e=>setSearch(e.target.value)} className="w-full pl-3 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm" placeholder="Search alumni..."/></div>}
      {!profiles.length?<EmptyState icon={UsersIcon} title="No alumni profiles"/>:<div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{filtered.map(p=><div key={p.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md"><p className="font-semibold">{p.user_name}</p><p className="text-xs text-slate-400">{p.graduation_year} · {p.occupation||"—"}{p.employer?` at ${p.employer}`:""}</p><p className="text-xs text-slate-400 mt-1">{p.city}{p.country?`, ${p.country}`:""}</p></div>)}</div>}</>)}
    {tab==="events"&&(!events.length?<EmptyState icon={CalendarDaysIcon} title="No alumni events"/>:
      <div className="space-y-2">{events.map(e=><div key={e.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4 flex items-center justify-between"><div><p className="font-semibold">{e.title}</p><p className="text-xs text-slate-400">{dayjs(e.event_date).format("MMM D, YYYY")}{e.location?` · ${e.location}`:""}</p></div><span className="text-xs font-medium px-2 py-0.5 rounded bg-blue-100 text-blue-700">{e.status_display}</span></div>)}</div>)}
    {tab==="donations"&&(!donations.length?<EmptyState icon={CurrencyDollarIcon} title="No donations"/>:
      <div className="space-y-2">{donations.map(d=><div key={d.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4 flex items-center justify-between"><div><p className="font-semibold">{d.alumni_name}</p><p className="text-xs text-slate-400">{d.fund_type_display}{d.is_recurring?" · Recurring":""} · {dayjs(d.donation_date).format("MMM D, YYYY")}</p></div><p className="text-lg font-bold text-green-600">${Number(d.amount).toLocaleString()}</p></div>)}</div>)}
    {tab==="chapters"&&(!chapters.length?<EmptyState icon={GlobeAltIcon} title="No chapters"/>:
      <div className="grid gap-3 sm:grid-cols-2">{chapters.map(c=><div key={c.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><div className="flex items-start justify-between"><p className="font-semibold">{c.name}</p><span className={`text-xs font-medium px-2 py-0.5 rounded ${c.is_active?"bg-green-100 text-green-700":"bg-slate-100 text-slate-500"}`}>{c.is_active?"Active":"Inactive"}</span></div><p className="text-xs text-slate-400">{c.city}{c.country?`, ${c.country}`:""}{c.president_name?` · Head: ${c.president_name}`:""}</p></div>)}</div>)}
  </div>);
}
