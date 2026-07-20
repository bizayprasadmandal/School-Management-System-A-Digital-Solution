/**
 * Health & Clinic — Full CRUD with form modals.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import { PlusIcon, HeartIcon, ClockIcon, ShieldCheckIcon, BeakerIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState } from "../../components/common";
import { useTitle } from "../../hooks";

interface HealthRecord { id:string; student:string; student_name:string; blood_type:string; allergies:string; chronic_conditions:string; medications:string; emergency_contact_name:string; }
interface NurseVisit { id:string; student:string; student_name:string; visit_type:string; visit_type_display:string; visit_date:string; symptoms:string; diagnosis:string; treatment:string; status_display:string; }
interface Immunization { id:string; student:string; student_name:string; vaccine_name:string; dose_number:number; date_administered:string; next_due_date:string|null; }
interface MedicationLog { id:string; student:string; student_name:string; medication_name:string; dosage:string; time_administered:string; }
interface Student { id:string; user_name:string; }

type Tab = "records"|"visits"|"immunizations"|"medications";
const TABS:{key:Tab;label:string;icon:React.ComponentType<{className?:string}>}[] = [
  {key:"records",label:"Health Records",icon:HeartIcon},{key:"visits",label:"Nurse Visits",icon:ClockIcon},{key:"immunizations",label:"Immunizations",icon:ShieldCheckIcon},{key:"medications",label:"Medication Log",icon:BeakerIcon},
];

export default function HealthPage() {
  useTitle("Health & Clinic"); const qc = useQueryClient();
  const [tab,setTab]=useState<Tab>("records");
  const [showRecordForm,setShowRecordForm]=useState(false); const [editingRecord,setEditingRecord]=useState<HealthRecord|null>(null);
  const [showVisitForm,setShowVisitForm]=useState(false); const [editingVisit,setEditingVisit]=useState<NurseVisit|null>(null);
  const [showImmForm,setShowImmForm]=useState(false); const [editingImm,setEditingImm]=useState<Immunization|null>(null);
  const [showMedForm,setShowMedForm]=useState(false);

  const {data:records=[],isLoading:rLoading}=useQuery({queryKey:["health-records"],queryFn:async()=>{const r=await api.get<{results:HealthRecord[]}>("/health/records/");return r.results??[]}});
  const {data:visits=[],isLoading:vLoading}=useQuery({queryKey:["health-visits"],queryFn:async()=>{const r=await api.get<{results:NurseVisit[]}>("/health/visits/");return r.results??[]}});
  const {data:immunizations=[],isLoading:iLoading}=useQuery({queryKey:["health-immunizations"],queryFn:async()=>{const r=await api.get<{results:Immunization[]}>("/health/immunizations/");return r.results??[]}});
  const {data:meds=[],isLoading:mLoading}=useQuery({queryKey:["health-medications"],queryFn:async()=>{const r=await api.get<{results:MedicationLog[]}>("/health/medication-logs/");return r.results??[]}});
  const {data:students=[]}=useQuery({queryKey:["students-short"],queryFn:async()=>{const r=await api.get<{results:Student[]}>("/students/");return r.results??[]}});

  const delRecord=useMutation({mutationFn:(id:string)=>api.delete(`/health/records/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["health-records"]});toast.success("Deleted")}});
  const delVisit=useMutation({mutationFn:(id:string)=>api.delete(`/health/visits/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["health-visits"]});toast.success("Deleted")}});
  const delImm=useMutation({mutationFn:(id:string)=>api.delete(`/health/immunizations/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["health-immunizations"]});toast.success("Deleted")}});
  const delMed=useMutation({mutationFn:(id:string)=>api.delete(`/health/medication-logs/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["health-medications"]});toast.success("Deleted")}});

  return (<div className="space-y-6">
    <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-slate-900 dark:text-white">Health & Clinic</h1><p className="text-sm text-slate-500 mt-1">Student health records, nurse visits, immunizations, and medication logs</p></div>
      <div className="flex gap-2">
        {tab==="records"&&<Button onClick={()=>{setEditingRecord(null);setShowRecordForm(true)}}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Record</Button>}
        {tab==="visits"&&<Button onClick={()=>{setEditingVisit(null);setShowVisitForm(true)}}><PlusIcon className="h-4 w-4 mr-1.5"/>Log Visit</Button>}
        {tab==="immunizations"&&<Button onClick={()=>{setEditingImm(null);setShowImmForm(true)}}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Immunization</Button>}
        {tab==="medications"&&<Button onClick={()=>setShowMedForm(true)}><PlusIcon className="h-4 w-4 mr-1.5"/>Log Medication</Button>}
      </div>
    </div>
    <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
      {TABS.map(t=>{const I=t.icon;return(<button key={t.key} onClick={()=>setTab(t.key)} className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap ${tab===t.key?"bg-white dark:bg-slate-700 shadow-sm":"text-slate-600 hover:text-slate-900"}`}><I className="h-4 w-4"/>{t.label}</button>)})}
    </div>
    {tab==="records"&&(rLoading?<div className="grid gap-3 sm:grid-cols-2">{[1,2].map(i=><div key={i} className="h-24 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"/>)}</div>:
      !records.length?<EmptyState icon={HeartIcon} title="No health records" description="Create health records for students"/>:
      <div className="grid gap-3 sm:grid-cols-2">{records.map(r=><div key={r.id} onClick={()=>{setEditingRecord(r);setShowRecordForm(true)}} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group"><div className="flex items-start justify-between"><div><p className="font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{r.student_name}</p><p className="text-xs text-slate-400">Blood: {r.blood_type}{r.emergency_contact_name?` · Contact: ${r.emergency_contact_name}`:""}</p></div><div className="flex gap-1 ml-4" onClick={e=>e.stopPropagation()}><button onClick={()=>{setEditingRecord(r);setShowRecordForm(true)}} className="text-xs text-indigo-600 font-medium">Edit</button><button onClick={()=>{if(confirm("Delete?"))delRecord.mutate(r.id)}} className="text-xs text-red-500 font-medium ml-2">Delete</button></div></div>{r.allergies&&<p className="text-xs text-red-500 mt-1">⚠️ Allergies: {r.allergies}</p>}{r.chronic_conditions&&<p className="text-xs text-amber-600 mt-1">Conditions: {r.chronic_conditions}</p>}</div>)}</div>)}
    {tab==="visits"&&(vLoading?<div className="space-y-2">{[1,2,3].map(i=><div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"/>)}</div>:
      !visits.length?<EmptyState icon={ClockIcon} title="No visits" description="Log your first nurse visit"/>:
      <div className="space-y-2">{visits.map(v=><div key={v.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md"><div className="flex items-start justify-between"><div><div className="flex items-center gap-2 mb-1"><p className="font-semibold text-slate-900 dark:text-white">{v.student_name}</p><p className="text-xs text-slate-400">{v.visit_type_display} · {dayjs(v.visit_date).format("MMM D, h:mm A")}</p></div></div><div className="flex gap-1 ml-4"><button onClick={()=>{if(confirm("Delete?"))delVisit.mutate(v.id)}} className="text-xs text-red-500 font-medium">Delete</button></div></div>{v.symptoms&&<p className="text-xs text-slate-500 mt-1">Symptoms: {v.symptoms}</p>}{v.diagnosis&&<p className="text-xs text-slate-500">Diagnosis: {v.diagnosis}</p>}</div>)}</div>)}
    {tab==="immunizations"&&(iLoading?<div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1,2,3].map(i=><div key={i} className="h-20 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"/>)}</div>:
      !immunizations.length?<EmptyState icon={ShieldCheckIcon} title="No immunizations" description="Record student immunizations"/>:
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{immunizations.map(i=><div key={i.id} onClick={()=>{setEditingImm(i);setShowImmForm(true)}} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group"><div className="flex items-start justify-between"><div><p className="font-semibold text-sm text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{i.vaccine_name}</p><p className="text-xs text-slate-400">{i.student_name} · Dose {i.dose_number}</p><p className="text-xs text-slate-400">{dayjs(i.date_administered).format("MMM D, YYYY")}{i.next_due_date?` · Next: ${dayjs(i.next_due_date).format("MMM D, YYYY")}`:""}</p></div><div className="flex gap-1 ml-4" onClick={e=>e.stopPropagation()}><button onClick={()=>{if(confirm("Delete?"))delImm.mutate(i.id)}} className="text-xs text-red-500 font-medium">Delete</button></div></div></div>)}</div>)}
    {tab==="medications"&&(mLoading?<div className="space-y-2">{[1,2,3].map(i=><div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"/>)}</div>:
      !meds.length?<EmptyState icon={BeakerIcon} title="No medication logs" description="Log student medications"/>:
      <div className="space-y-2">{meds.map(m=><div key={m.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md"><div className="flex items-start justify-between"><div><p className="font-semibold text-slate-900 dark:text-white">{m.student_name}</p><p className="text-sm text-slate-600">{m.medication_name} · {m.dosage}</p><p className="text-xs text-slate-400">{dayjs(m.time_administered).format("MMM D, YYYY h:mm A")}</p></div><button onClick={()=>{if(confirm("Delete?"))delMed.mutate(m.id)}} className="text-xs text-red-500 font-medium">Delete</button></div></div>)}</div>)}
    <RecordFormModal open={showRecordForm} onClose={()=>{setShowRecordForm(false);setEditingRecord(null)}} record={editingRecord} students={students} onSaved={()=>{setShowRecordForm(false);setEditingRecord(null);qc.invalidateQueries({queryKey:["health-records"]})}}/>
    <VisitFormModal open={showVisitForm} onClose={()=>{setShowVisitForm(false);setEditingVisit(null)}} visit={editingVisit} students={students} onSaved={()=>{setShowVisitForm(false);setEditingVisit(null);qc.invalidateQueries({queryKey:["health-visits"]})}}/>
    <ImmFormModal open={showImmForm} onClose={()=>{setShowImmForm(false);setEditingImm(null)}} immunization={editingImm} students={students} onSaved={()=>{setShowImmForm(false);setEditingImm(null);qc.invalidateQueries({queryKey:["health-immunizations"]})}}/>
    <MedFormModal open={showMedForm} onClose={()=>setShowMedForm(false)} students={students} onSaved={()=>{setShowMedForm(false);qc.invalidateQueries({queryKey:["health-medications"]})}}/>
  </div>);
}

function RecordFormModal({open,onClose,record,students,onSaved}:{open:boolean;onClose:()=>void;record?:HealthRecord|null;students:Student[];onSaved:()=>void}){
  const [f,setF]=useState({student:record?.student??"",blood_type:record?.blood_type??"unknown",allergies:record?.allergies??"",chronic_conditions:record?.chronic_conditions??"",emergency_contact_name:record?.emergency_contact_name??"",emergency_contact_phone:""});
  const isEdit=!!record;
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/health/records/",d),onSuccess:()=>{toast.success("Record created");onSaved()}});
  const update=useMutation({mutationFn:(d:typeof f)=>api.patch(`/health/records/${record!.id}/`,d),onSuccess:()=>{toast.success("Record updated");onSaved()}});
  const saving=create.isPending||update.isPending;
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.student)return toast.error("Select student");if(isEdit)update.mutate(f);else create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title={isEdit?"Edit Health Record":"Add Health Record"}><form onSubmit={submit} className="space-y-4">
    <div><label className="block text-sm font-medium mb-1">Student *</label><select value={f.student} onChange={e=>setF(p=>({...p,student:e.target.value}))} className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm" required><option value="">Select...</option>{students.map(s=><option key={s.id} value={s.id}>{s.user_name}</option>)}</select></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Blood Type</label><select value={f.blood_type} onChange={e=>setF(p=>({...p,blood_type:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="unknown">Unknown</option><option value="A+">A+</option><option value="A-">A-</option><option value="B+">B+</option><option value="B-">B-</option><option value="AB+">AB+</option><option value="AB-">AB-</option><option value="O+">O+</option><option value="O-">O-</option></select></div><div><label className="block text-sm font-medium mb-1">Emergency Contact</label><input value={f.emergency_contact_name} onChange={e=>setF(p=>({...p,emergency_contact_name:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div></div>
    <div><label className="block text-sm font-medium mb-1">Allergies</label><textarea value={f.allergies} onChange={e=>setF(p=>({...p,allergies:e.target.value}))} rows={2} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" placeholder="Comma-separated list"/></div>
    <div><label className="block text-sm font-medium mb-1">Chronic Conditions</label><textarea value={f.chronic_conditions} onChange={e=>setF(p=>({...p,chronic_conditions:e.target.value}))} rows={2} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={saving}>Cancel</Button><Button type="submit" loading={saving}>{isEdit?"Update":"Create"} Record</Button></div>
  </form></Modal>);
}

function VisitFormModal({open,onClose,visit,students,onSaved}:{open:boolean;onClose:()=>void;visit?:NurseVisit|null;students:Student[];onSaved:()=>void}){
  const [f,setF]=useState({student:visit?.student??"",visit_type:visit?.visit_type??"sick",symptoms:visit?.symptoms??"",diagnosis:visit?.diagnosis??"",treatment:visit?.treatment??""});
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/health/visits/",d),onSuccess:()=>{toast.success("Visit logged");onSaved()}});
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.student)return toast.error("Select student");create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title="Log Nurse Visit"><form onSubmit={submit} className="space-y-4">
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Student *</label><select value={f.student} onChange={e=>setF(p=>({...p,student:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" required><option value="">Select...</option>{students.map(s=><option key={s.id} value={s.id}>{s.user_name}</option>)}</select></div><div><label className="block text-sm font-medium mb-1">Visit Type</label><select value={f.visit_type} onChange={e=>setF(p=>({...p,visit_type:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="sick">Sick Visit</option><option value="injury">Injury</option><option value="medication">Medication</option><option value="checkup">Routine Checkup</option><option value="followup">Follow-up</option><option value="other">Other</option></select></div></div>
    <div><label className="block text-sm font-medium mb-1">Symptoms</label><textarea value={f.symptoms} onChange={e=>setF(p=>({...p,symptoms:e.target.value}))} rows={2} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Diagnosis</label><textarea value={f.diagnosis} onChange={e=>setF(p=>({...p,diagnosis:e.target.value}))} rows={2} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div><div><label className="block text-sm font-medium mb-1">Treatment</label><textarea value={f.treatment} onChange={e=>setF(p=>({...p,treatment:e.target.value}))} rows={2} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={create.isPending}>Cancel</Button><Button type="submit" loading={create.isPending}>Log Visit</Button></div>
  </form></Modal>);
}

function ImmFormModal({open,onClose,immunization,students,onSaved}:{open:boolean;onClose:()=>void;immunization?:Immunization|null;students:Student[];onSaved:()=>void}){
  const [f,setF]=useState({student:immunization?.student??"",vaccine_name:immunization?.vaccine_name??"",dose_number:immunization?.dose_number??1,date_administered:immunization?.date_administered??dayjs().format("YYYY-MM-DD"),next_due_date:immunization?.next_due_date??""});
  const isEdit=!!immunization;
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/health/immunizations/",d),onSuccess:()=>{toast.success("Immunization added");onSaved()}});
  const update=useMutation({mutationFn:(d:typeof f)=>api.patch(`/health/immunizations/${immunization!.id}/`,d),onSuccess:()=>{toast.success("Updated");onSaved()}});
  const saving=create.isPending||update.isPending;
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.vaccine_name.trim())return toast.error("Vaccine name required");if(isEdit)update.mutate(f);else create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title={isEdit?"Edit Immunization":"Add Immunization"}><form onSubmit={submit} className="space-y-4">
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Student *</label><select value={f.student} onChange={e=>setF(p=>({...p,student:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" required><option value="">Select...</option>{students.map(s=><option key={s.id} value={s.id}>{s.user_name}</option>)}</select></div><div><label className="block text-sm font-medium mb-1">Vaccine *</label><input value={f.vaccine_name} onChange={e=>setF(p=>({...p,vaccine_name:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" required/></div></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Dose #</label><input type="number" min={1} value={f.dose_number} onChange={e=>setF(p=>({...p,dose_number:Number(e.target.value)}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div><div><label className="block text-sm font-medium mb-1">Date Administered</label><input type="date" value={f.date_administered} onChange={e=>setF(p=>({...p,date_administered:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div></div>
    <div><label className="block text-sm font-medium mb-1">Next Due Date</label><input type="date" value={f.next_due_date} onChange={e=>setF(p=>({...p,next_due_date:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={saving}>Cancel</Button><Button type="submit" loading={saving}>{isEdit?"Update":"Add"} Immunization</Button></div>
  </form></Modal>);
}

function MedFormModal({open,onClose,students,onSaved}:{open:boolean;onClose:()=>void;students:Student[];onSaved:()=>void}){
  const [f,setF]=useState({student:"",medication_name:"",dosage:"",time_administered:dayjs().format("YYYY-MM-DDTHH:mm")});
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/health/medication-logs/",d),onSuccess:()=>{toast.success("Medication logged");onSaved()}});
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.student||!f.medication_name.trim())return toast.error("Student and medication required");create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title="Log Medication"><form onSubmit={submit} className="space-y-4">
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Student *</label><select value={f.student} onChange={e=>setF(p=>({...p,student:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" required><option value="">Select...</option>{students.map(s=><option key={s.id} value={s.id}>{s.user_name}</option>)}</select></div><div><label className="block text-sm font-medium mb-1">Medication *</label><input value={f.medication_name} onChange={e=>setF(p=>({...p,medication_name:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" required/></div></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Dosage</label><input value={f.dosage} onChange={e=>setF(p=>({...p,dosage:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" placeholder="e.g. 500mg"/></div><div><label className="block text-sm font-medium mb-1">Time</label><input type="datetime-local" value={f.time_administered} onChange={e=>setF(p=>({...p,time_administered:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={create.isPending}>Cancel</Button><Button type="submit" loading={create.isPending}>Log Medication</Button></div>
  </form></Modal>);
}
