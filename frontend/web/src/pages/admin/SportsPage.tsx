/**
 * Sports & Extracurriculars — Admin page for managing sports, teams, events, achievements.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import { PlusIcon, MagnifyingGlassIcon, TrophyIcon, UsersIcon, CalendarDaysIcon, StarIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface Sport { id: string; name: string; category: string; category_display: string; team_count: number; is_active: boolean; }
interface Team { id: string; sport: string; sport_name: string; name: string; gender: string; gender_display: string; coach_name: string | null; member_count: number; is_active: boolean; }
interface TeamMember { id: string; team: string; student: string; student_name: string; role: string; role_display: string; status: string; }
interface SportEvent { id: string; sport: string; sport_name: string; team_name: string | null; title: string; opponent: string; event_date: string; status: string; status_display: string; home_score: string; opponent_score: string; }
interface Achievement { id: string; student_name: string | null; team_name: string | null; title: string; position: string; level: string; awarded_date: string; }

const ST_COLORS: Record<string,string> = { active:"bg-green-100 text-green-700", scheduled:"bg-blue-100 text-blue-700", completed:"bg-green-100 text-green-700", cancelled:"bg-red-100 text-red-700", ongoing:"bg-amber-100 text-amber-700" };

type Tab = "sports"|"teams"|"events"|"achievements";
const TABS: {key:Tab;label:string;icon:React.ComponentType<{className?:string}>}[] = [
  {key:"sports",label:"Sports",icon:TrophyIcon},{key:"teams",label:"Teams",icon:UsersIcon},{key:"events",label:"Events",icon:CalendarDaysIcon},{key:"achievements",label:"Achievements",icon:StarIcon},
];

export default function SportsPage() {
  useTitle("Sports & Extracurriculars"); const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<Tab>("sports"); const [search, setSearch] = useState("");
  const [showSportForm, setShowSportForm] = useState(false); const [editingSport, setEditingSport] = useState<Sport|null>(null);
  const [showTeamForm, setShowTeamForm] = useState(false); const [editingTeam, setEditingTeam] = useState<Team|null>(null);
  const [showEventForm, setShowEventForm] = useState(false); const [showAchievementForm, setShowAchievementForm] = useState(false);

  const {data:sports=[]} = useQuery({queryKey:["sports"],queryFn:async()=>{const r=await api.get<{results:Sport[]}>("/sports/sports/");return r.results??[]}});
  const {data:teams=[]} = useQuery({queryKey:["sports-teams"],queryFn:async()=>{const r=await api.get<{results:Team[]}>("/sports/teams/");return r.results??[]}});
  const {data:events=[]} = useQuery({queryKey:["sports-events"],queryFn:async()=>{const r=await api.get<{results:SportEvent[]}>("/sports/events/");return r.results??[]}});
  const {data:achievements=[]} = useQuery({queryKey:["sports-achievements"],queryFn:async()=>{const r=await api.get<{results:Achievement[]}>("/sports/achievements/");return r.results??[]}});
  const {data:students=[]} = useQuery({queryKey:["students-short"],queryFn:async()=>{const r=await api.get<{results:any[]}>("/students/");return r.results??[]}});

  const deleteSport = useMutation({mutationFn:(id:string)=>api.delete(`/sports/sports/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["sports"]});toast.success("Deleted")}});

  const filtered = search.trim()?sports.filter(s=>s.name.toLowerCase().includes(search.toLowerCase())):sports;

  return (<div className="space-y-6">
    <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-slate-900 dark:text-white">Sports & Extracurriculars</h1><p className="text-sm text-slate-500 mt-1">Manage sports, teams, events, and achievements</p></div>
      <div className="flex gap-2">
        {activeTab==="sports"&&<Button onClick={()=>{setEditingSport(null);setShowSportForm(true)}}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Sport</Button>}
        {activeTab==="teams"&&<Button onClick={()=>{setEditingTeam(null);setShowTeamForm(true)}}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Team</Button>}
        {activeTab==="events"&&<Button onClick={()=>setShowEventForm(true)}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Event</Button>}
        {activeTab==="achievements"&&<Button onClick={()=>setShowAchievementForm(true)}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Achievement</Button>}
      </div>
    </div>
    <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
      {TABS.map(t=>{const Icon=t.icon;return(<button key={t.key} onClick={()=>setActiveTab(t.key)} className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap ${activeTab===t.key?"bg-white dark:bg-slate-700 shadow-sm":"text-slate-600 hover:text-slate-900"}`}><Icon className="h-4 w-4"/>{t.label}</button>)})}
    </div>
    {activeTab==="sports"&&(<>{sports.length>0&&<div className="relative max-w-sm"><MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400"/><input value={search} onChange={e=>setSearch(e.target.value)} className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm" placeholder="Search sports..."/></div>}
      {!sports.length?<EmptyState icon={TrophyIcon} title="No sports" description="Add your first sport"/>:
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{filtered.map(s=><div key={s.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md"><div className="flex items-start justify-between mb-2"><div><p className="font-semibold">{s.name}</p><p className="text-xs text-slate-400">{s.category_display}</p></div><span className={`text-xs font-medium px-2 py-0.5 rounded ${s.is_active?"bg-green-100 text-green-700":"bg-slate-100 text-slate-500"}`}>{s.is_active?"Active":"Inactive"}</span></div><p className="text-xs text-slate-400">{s.team_count} team{s.team_count!==1?"s":""}</p>
        <div className="flex gap-2 mt-2 pt-2 border-t border-slate-100"><button onClick={()=>{setEditingSport(s);setShowSportForm(true)}} className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button><button onClick={()=>{if(confirm("Delete?"))deleteSport.mutate(s.id)}} className="text-xs text-red-500 font-medium">Delete</button></div></div>)}</div>}</>)}
    {activeTab==="teams"&&(!teams.length?<EmptyState icon={UsersIcon} title="No teams" description="Add your first team"/>:
      <div className="grid gap-3 sm:grid-cols-2">{teams.map(t=><div key={t.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4 hover:shadow-md"><div className="flex items-start justify-between mb-2"><div><p className="font-semibold">{t.name}</p><p className="text-xs text-slate-400">{t.sport_name} · {t.gender_display} · {t.member_count} members</p></div><span className={`text-xs font-medium px-2 py-0.5 rounded ${t.is_active?"bg-green-100":"bg-slate-100"}`}>{t.is_active?"Active":"Inactive"}</span></div>{t.coach_name&&<p className="text-xs text-slate-400">Coach: {t.coach_name}</p>}
        <div className="flex gap-2 mt-2 pt-2 border-t border-slate-100"><button onClick={()=>{setEditingTeam(t);setShowTeamForm(true)}} className="text-xs text-indigo-600 font-medium">Edit</button></div></div>)}</div>)}
    {activeTab==="events"&&(!events.length?<EmptyState icon={CalendarDaysIcon} title="No events" description="Schedule your first event"/>:
      <div className="space-y-2">{events.map(e=><div key={e.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><div className="flex items-start justify-between"><div><div className="flex items-center gap-2 mb-1"><p className="font-semibold">{e.title}</p><span className={`text-xs font-medium px-2 py-0.5 rounded ${ST_COLORS[e.status]||"bg-slate-100"}`}>{e.status_display}</span></div><p className="text-sm text-slate-500">{e.sport_name}{e.team_name?` · ${e.team_name}`:""}{e.opponent?` vs ${e.opponent}`:""}</p><p className="text-xs text-slate-400">{dayjs(e.event_date).format("MMM D, YYYY h:mm A")}{e.home_score?` · Score: ${e.home_score}-${e.opponent_score}`:""}</p></div></div></div>)}</div>)}
    {activeTab==="achievements"&&(!achievements.length?<EmptyState icon={StarIcon} title="No achievements" description="Record your first achievement"/>:
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{achievements.map(a=><div key={a.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><p className="font-semibold">{a.title}</p><p className="text-xs text-slate-400">{a.student_name||a.team_name}{a.position?` · ${a.position}`:""}{a.level?` · ${a.level}`:""}</p><p className="text-xs text-slate-400 mt-1">{dayjs(a.awarded_date).format("MMM D, YYYY")}</p></div>)}</div>)}
  </div>);
}
