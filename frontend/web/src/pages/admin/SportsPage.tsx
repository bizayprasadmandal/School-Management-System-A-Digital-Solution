/**
 * Sports & Extracurriculars — Full CRUD with form modals.
 */
import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import { PlusIcon, MagnifyingGlassIcon, TrophyIcon, UsersIcon, CalendarDaysIcon, StarIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface Sport { id:string; name:string; category:string; category_display:string; description:string; min_players:number; max_players:number; team_count:number; is_active:boolean; }
interface Team { id:string; sport:string; sport_name:string; name:string; gender:string; gender_display:string; coach_name:string|null; member_count:number; is_active:boolean; }
interface SportEvent { id:string; sport:string; sport_name:string; team:string|null; team_name:string|null; title:string; opponent:string; location:string; event_date:string; status:string; status_display:string; home_score:string; opponent_score:string; }
interface Achievement { id:string; student:string; student_name:string|null; team:string|null; team_name:string|null; title:string; position:string; level:string; awarded_date:string; }
interface Student { id:string; user_name:string; }

const SC:Record<string,string> = { active:"bg-green-100 text-green-700", scheduled:"bg-blue-100 text-blue-700", completed:"bg-green-100 text-green-700", cancelled:"bg-red-100 text-red-700", ongoing:"bg-amber-100 text-amber-700" };

type Tab = "sports"|"teams"|"events"|"achievements";
const TABS:{key:Tab;label:string;icon:React.ComponentType<{className?:string}>}[] = [
  {key:"sports",label:"Sports",icon:TrophyIcon},{key:"teams",label:"Teams",icon:UsersIcon},{key:"events",label:"Events",icon:CalendarDaysIcon},{key:"achievements",label:"Achievements",icon:StarIcon},
];

export default function SportsPage() {
  useTitle("Sports & Extracurriculars"); const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<Tab>("sports"); const [search, setSearch] = useState("");

  const [showSportForm, setShowSportForm] = useState(false); const [editingSport, setEditingSport] = useState<Sport|null>(null);
  const [showTeamForm, setShowTeamForm] = useState(false); const [editingTeam, setEditingTeam] = useState<Team|null>(null);
  const [showEventForm, setShowEventForm] = useState(false); const [editingEvent, setEditingEvent] = useState<SportEvent|null>(null);
  const [showAchForm, setShowAchForm] = useState(false); const [editingAch, setEditingAch] = useState<Achievement|null>(null);

  const {data:sports=[],isLoading:sLoading}=useQuery({queryKey:["sports"],queryFn:async()=>{const r=await api.get<{results:Sport[]}>("/sports/sports/");return r.results??[]}});
  const {data:teams=[],isLoading:tLoading}=useQuery({queryKey:["sports-teams"],queryFn:async()=>{const r=await api.get<{results:Team[]}>("/sports/teams/");return r.results??[]}});
  const {data:events=[],isLoading:eLoading}=useQuery({queryKey:["sports-events"],queryFn:async()=>{const r=await api.get<{results:SportEvent[]}>("/sports/events/");return r.results??[]}});
  const {data:achievements=[],isLoading:achLoading}=useQuery({queryKey:["sports-achievements"],queryFn:async()=>{const r=await api.get<{results:Achievement[]}>("/sports/achievements/");return r.results??[]}});
  const {data:students=[]}=useQuery({queryKey:["students-short"],queryFn:async()=>{const r=await api.get<{results:Student[]}>("/students/");return r.results??[]}});

  const delSport=useMutation({mutationFn:(id:string)=>api.delete(`/sports/sports/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["sports"]});toast.success("Sport deleted")}});
  const delTeam=useMutation({mutationFn:(id:string)=>api.delete(`/sports/teams/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["sports-teams"]});toast.success("Team deleted")}});
  const delEvent=useMutation({mutationFn:(id:string)=>api.delete(`/sports/events/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["sports-events"]});toast.success("Event deleted")}});
  const delAch=useMutation({mutationFn:(id:string)=>api.delete(`/sports/achievements/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["sports-achievements"]});toast.success("Achievement deleted")}});

  const filtered=useMemo(()=>{if(!search.trim())return sports;const q=search.toLowerCase();return sports.filter(s=>s.name.toLowerCase().includes(q))},[sports,search]);

  return (<div className="space-y-6">
    <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-slate-900 dark:text-white">Sports & Extracurriculars</h1><p className="text-sm text-slate-500 mt-1">Manage sports, teams, events, and achievements</p></div>
      <div className="flex gap-2">
        {activeTab==="sports"&&<Button onClick={()=>{setEditingSport(null);setShowSportForm(true)}}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Sport</Button>}
        {activeTab==="teams"&&<Button onClick={()=>{setEditingTeam(null);setShowTeamForm(true)}}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Team</Button>}
        {activeTab==="events"&&<Button onClick={()=>{setEditingEvent(null);setShowEventForm(true)}}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Event</Button>}
        {activeTab==="achievements"&&<Button onClick={()=>{setEditingAch(null);setShowAchForm(true)}}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Achievement</Button>}
      </div>
    </div>
    <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
      {TABS.map(t=>{const I=t.icon;return(<button key={t.key} onClick={()=>setActiveTab(t.key)} className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap ${activeTab===t.key?"bg-white dark:bg-slate-700 shadow-sm":"text-slate-600 hover:text-slate-900"}`}><I className="h-4 w-4"/>{t.label}</button>)})}
    </div>
    {activeTab==="sports"&&(<>{sports.length>5&&<div className="relative max-w-sm"><MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400"/><input value={search} onChange={e=>setSearch(e.target.value)} className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm" placeholder="Search sports..."/></div>}
      {sLoading?<div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1,2,3].map(i=><div key={i} className="h-24 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse"/>)}</div>:
      !filtered.length?<EmptyState icon={TrophyIcon} title="No sports" description="Add your first sport"/>:
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{filtered.map(s=><div key={s.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md"><div className="flex items-start justify-between mb-2"><div><p className="font-semibold text-slate-900 dark:text-white">{s.name}</p><p className="text-xs text-slate-400">{s.category_display}{s.description?` · ${s.description}`:""}</p></div><Badge color={s.is_active?"green":"slate"}>{s.is_active?"Active":"Inactive"}</Badge></div><p className="text-xs text-slate-400 mb-2">{s.team_count} team{s.team_count!==1?"s":""}</p><div className="flex gap-2 pt-2 border-t border-slate-100 dark:border-slate-700"><button onClick={()=>{setEditingSport(s);setShowSportForm(true)}} className="text-xs text-indigo-600 font-medium">Edit</button><button onClick={()=>{if(confirm("Delete?"))delSport.mutate(s.id)}} className="text-xs text-red-500 font-medium">Delete</button></div></div>)}</div>}</>)}
    {activeTab==="teams"&&(tLoading?<div className="grid gap-3 sm:grid-cols-2">{[1,2].map(i=><div key={i} className="h-24 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"/>)}</div>:
      !teams.length?<EmptyState icon={UsersIcon} title="No teams" description="Add your first team"/>:
      <div className="grid gap-3 sm:grid-cols-2">{teams.map(t=><div key={t.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md"><div className="flex items-start justify-between mb-2"><div><p className="font-semibold text-slate-900 dark:text-white">{t.name}</p><p className="text-xs text-slate-400">{t.sport_name} · {t.gender_display} · {t.member_count} members</p></div><Badge color={t.is_active?"green":"slate"}>{t.is_active?"Active":"Inactive"}</Badge></div>{t.coach_name&&<p className="text-xs text-slate-400">Coach: {t.coach_name}</p>}<div className="flex gap-2 mt-2 pt-2 border-t border-slate-100"><button onClick={()=>{setEditingTeam(t);setShowTeamForm(true)}} className="text-xs text-indigo-600 font-medium">Edit</button><button onClick={()=>{if(confirm("Delete?"))delTeam.mutate(t.id)}} className="text-xs text-red-500 font-medium">Delete</button></div></div>)}</div>)}
    {activeTab==="events"&&(eLoading?<div className="space-y-2">{[1,2,3].map(i=><div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"/>)}</div>:
      !events.length?<EmptyState icon={CalendarDaysIcon} title="No events" description="Schedule your first event"/>:
      <div className="space-y-2">{events.map(e=><div key={e.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md"><div className="flex items-start justify-between"><div><div className="flex items-center gap-2 mb-1"><p className="font-semibold text-slate-900 dark:text-white">{e.title}</p><span className={`text-xs font-medium px-2 py-0.5 rounded ${SC[e.status]||"bg-slate-100"}`}>{e.status_display}</span></div><p className="text-sm text-slate-500">{e.sport_name}{e.team_name?` · ${e.team_name}`:""}{e.opponent?` vs ${e.opponent}`:""}</p><p className="text-xs text-slate-400">{dayjs(e.event_date).format("MMM D, YYYY h:mm A")}{e.home_score?` · Score: ${e.home_score}-${e.opponent_score}`:""}</p></div><div className="flex gap-1 ml-4"><button onClick={()=>{setEditingEvent(e);setShowEventForm(true)}} className="text-xs text-indigo-600 font-medium">Edit</button><button onClick={()=>{if(confirm("Delete?"))delEvent.mutate(e.id)}} className="text-xs text-red-500 font-medium ml-2">Delete</button></div></div></div>)}</div>)}
    {activeTab==="achievements"&&(achLoading?<div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1,2,3].map(i=><div key={i} className="h-20 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"/>)}</div>:
      !achievements.length?<EmptyState icon={StarIcon} title="No achievements" description="Record your first achievement"/>:
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{achievements.map(a=><div key={a.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md"><div className="flex items-start justify-between"><div><p className="font-semibold text-slate-900 dark:text-white">{a.title}</p><p className="text-xs text-slate-400">{a.student_name||a.team_name}{a.position?` · ${a.position}`:""}{a.level?` · ${a.level}`:""}</p><p className="text-xs text-slate-400 mt-1">{dayjs(a.awarded_date).format("MMM D, YYYY")}</p></div><div className="flex gap-1 ml-4"><button onClick={()=>{if(confirm("Delete?"))delAch.mutate(a.id)}} className="text-xs text-red-500 font-medium">Delete</button></div></div></div>)}</div>)}
    <SportFormModal open={showSportForm} onClose={()=>{setShowSportForm(false);setEditingSport(null)}} sport={editingSport} onSaved={()=>{setShowSportForm(false);setEditingSport(null);qc.invalidateQueries({queryKey:["sports"]})}}/>
    <TeamFormModal open={showTeamForm} onClose={()=>{setShowTeamForm(false);setEditingTeam(null)}} team={editingTeam} sports={sports} onSaved={()=>{setShowTeamForm(false);setEditingTeam(null);qc.invalidateQueries({queryKey:["sports-teams"]})}}/>
    <EventFormModal open={showEventForm} onClose={()=>{setShowEventForm(false);setEditingEvent(null)}} event={editingEvent} sports={sports} teams={teams} onSaved={()=>{setShowEventForm(false);setEditingEvent(null);qc.invalidateQueries({queryKey:["sports-events"]})}}/>
    <AchievementFormModal open={showAchForm} onClose={()=>{setShowAchForm(false);setEditingAch(null)}} achievement={editingAch} students={students} teams={teams} onSaved={()=>{setShowAchForm(false);setEditingAch(null);qc.invalidateQueries({queryKey:["sports-achievements"]})}}/>
  </div>);
}

function SportFormModal({open,onClose,sport,onSaved}:{open:boolean;onClose:()=>void;sport?:Sport|null;onSaved:()=>void}){
  const [f,setF]=useState({name:sport?.name??"",category:sport?.category??"sport",description:sport?.description??"",min_players:sport?.min_players??1,max_players:sport?.max_players??20});
  const isEdit=!!sport;
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/sports/sports/",d),onSuccess:()=>{toast.success("Sport created");onSaved()}});
  const update=useMutation({mutationFn:(d:typeof f)=>api.patch(`/sports/sports/${sport!.id}/`,d),onSuccess:()=>{toast.success("Sport updated");onSaved()}});
  const saving=create.isPending||update.isPending;
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.name.trim())return toast.error("Name required");if(isEdit)update.mutate(f);else create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title={isEdit?"Edit Sport":"Add Sport"}><form onSubmit={submit} className="space-y-4">
    <div><label className="block text-sm font-medium mb-1">Name *</label><input value={f.name} onChange={e=>setF(p=>({...p,name:e.target.value}))} className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"/></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Category</label><select value={f.category} onChange={e=>setF(p=>({...p,category:e.target.value}))} className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="sport">Sport</option><option value="academic">Academic</option><option value="arts">Arts & Culture</option><option value="club">Club & Society</option><option value="other">Other</option></select></div></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Min Players</label><input type="number" min={1} value={f.min_players} onChange={e=>setF(p=>({...p,min_players:Number(e.target.value)}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div><div><label className="block text-sm font-medium mb-1">Max Players</label><input type="number" min={1} value={f.max_players} onChange={e=>setF(p=>({...p,max_players:Number(e.target.value)}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div></div>
    <div><label className="block text-sm font-medium mb-1">Description</label><textarea value={f.description} onChange={e=>setF(p=>({...p,description:e.target.value}))} rows={2} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={saving}>Cancel</Button><Button type="submit" loading={saving}>{isEdit?"Update":"Create"} Sport</Button></div>
  </form></Modal>);
}

function TeamFormModal({open,onClose,team,sports,onSaved}:{open:boolean;onClose:()=>void;team?:Team|null;sports:Sport[];onSaved:()=>void}){
  const [f,setF]=useState({sport:team?.sport??"",name:team?.name??"",gender:team?.gender??"mixed"});
  const isEdit=!!team;
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/sports/teams/",d),onSuccess:()=>{toast.success("Team created");onSaved()}});
  const update=useMutation({mutationFn:(d:typeof f)=>api.patch(`/sports/teams/${team!.id}/`,d),onSuccess:()=>{toast.success("Team updated");onSaved()}});
  const saving=create.isPending||update.isPending;
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.name.trim()||!f.sport)return toast.error("Name and sport required");if(isEdit)update.mutate(f);else create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title={isEdit?"Edit Team":"Add Team"}><form onSubmit={submit} className="space-y-4">
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Sport *</label><select value={f.sport} onChange={e=>setF(p=>({...p,sport:e.target.value}))} className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="">Select...</option>{sports.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></div><div><label className="block text-sm font-medium mb-1">Team Name *</label><input value={f.name} onChange={e=>setF(p=>({...p,name:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div></div>
    <div><label className="block text-sm font-medium mb-1">Gender</label><select value={f.gender} onChange={e=>setF(p=>({...p,gender:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="mixed">Mixed</option><option value="boys">Boys</option><option value="girls">Girls</option></select></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={saving}>Cancel</Button><Button type="submit" loading={saving}>{isEdit?"Update":"Create"} Team</Button></div>
  </form></Modal>);
}

function EventFormModal({open,onClose,event,sports,teams,onSaved}:{open:boolean;onClose:()=>void;event?:SportEvent|null;sports:Sport[];teams:Team[];onSaved:()=>void}){
  const [f,setF]=useState({sport:event?.sport??"",team:event?.team??"",title:event?.title??"",opponent:event?.opponent??"",event_date:event?.event_date??dayjs().format("YYYY-MM-DDTHH:mm"),location:event?.location??""});
  const isEdit=!!event;
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/sports/events/",d),onSuccess:()=>{toast.success("Event created");onSaved()}});
  const update=useMutation({mutationFn:(d:typeof f)=>api.patch(`/sports/events/${event!.id}/`,d),onSuccess:()=>{toast.success("Event updated");onSaved()}});
  const saving=create.isPending||update.isPending;
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.title.trim())return toast.error("Title required");if(isEdit)update.mutate(f);else create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title={isEdit?"Edit Event":"Add Event"}><form onSubmit={submit} className="space-y-4">
    <div><label className="block text-sm font-medium mb-1">Title *</label><input value={f.title} onChange={e=>setF(p=>({...p,title:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Sport</label><select value={f.sport} onChange={e=>setF(p=>({...p,sport:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="">Select...</option>{sports.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}</select></div><div><label className="block text-sm font-medium mb-1">Team</label><select value={f.team} onChange={e=>setF(p=>({...p,team:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="">None</option>{teams.map(t=><option key={t.id} value={t.id}>{t.name}</option>)}</select></div></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Opponent</label><input value={f.opponent} onChange={e=>setF(p=>({...p,opponent:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div><div><label className="block text-sm font-medium mb-1">Location</label><input value={f.location} onChange={e=>setF(p=>({...p,location:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div></div>
    <div><label className="block text-sm font-medium mb-1">Event Date/Time</label><input type="datetime-local" value={f.event_date} onChange={e=>setF(p=>({...p,event_date:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={saving}>Cancel</Button><Button type="submit" loading={saving}>{isEdit?"Update":"Create"} Event</Button></div>
  </form></Modal>);
}

function AchievementFormModal({open,onClose,achievement,students,teams,onSaved}:{open:boolean;onClose:()=>void;achievement?:Achievement|null;students:Student[];teams:Team[];onSaved:()=>void}){
  const [f,setF]=useState({student:achievement?.student??"",team:achievement?.team??"",title:achievement?.title??"",position:achievement?.position??"",level:achievement?.level??"",awarded_date:achievement?.awarded_date??dayjs().format("YYYY-MM-DD")});
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/sports/achievements/",d),onSuccess:()=>{toast.success("Achievement created");onSaved()}});
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.title.trim())return toast.error("Title required");create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title="Add Achievement"><form onSubmit={submit} className="space-y-4">
    <div><label className="block text-sm font-medium mb-1">Title *</label><input value={f.title} onChange={e=>setF(p=>({...p,title:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Student</label><select value={f.student} onChange={e=>setF(p=>({...p,student:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="">None</option>{students.map(s=><option key={s.id} value={s.id}>{s.user_name}</option>)}</select></div><div><label className="block text-sm font-medium mb-1">Team</label><select value={f.team} onChange={e=>setF(p=>({...p,team:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="">None</option>{teams.map(t=><option key={t.id} value={t.id}>{t.name}</option>)}</select></div></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Position</label><input value={f.position} onChange={e=>setF(p=>({...p,position:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" placeholder="1st Place, Best Player"/></div><div><label className="block text-sm font-medium mb-1">Level</label><select value={f.level} onChange={e=>setF(p=>({...p,level:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="">Select...</option><option value="School">School</option><option value="District">District</option><option value="State">State</option><option value="National">National</option><option value="International">International</option></select></div></div>
    <div><label className="block text-sm font-medium mb-1">Awarded Date</label><input type="date" value={f.awarded_date} onChange={e=>setF(p=>({...p,awarded_date:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={create.isPending}>Cancel</Button><Button type="submit" loading={create.isPending}>Add Achievement</Button></div>
  </form></Modal>);
}
