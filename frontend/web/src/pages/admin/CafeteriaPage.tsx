/**
 * Cafeteria & Meal Management — Full CRUD with form modals.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import { PlusIcon, BookOpenIcon, CreditCardIcon, CalendarDaysIcon, NoSymbolIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface MealMenu { id:string; name:string; date:string; meal_type:string; meal_type_display:string; items:string; price:number; is_vegetarian:boolean; is_vegan:boolean; is_gluten_free:boolean; }
interface MealPlan { id:string; name:string; description:string; price_per_period:number; period_days:number; meals_included:string; is_active:boolean; }
interface MealBooking { id:string; user:string; user_name:string; menu:string; menu_name:string; meal_type_display:string; status_display:string; booking_date:string; }
interface Dietary { id:string; user:string; user_name:string; restriction_type:string; severity:string; }

type Tab = "menus"|"plans"|"bookings"|"dietary";
const TABS:{key:Tab;label:string;icon:React.ComponentType<{className?:string}>}[] = [
  {key:"menus",label:"Menus",icon:BookOpenIcon},{key:"plans",label:"Meal Plans",icon:CreditCardIcon},{key:"bookings",label:"Bookings",icon:CalendarDaysIcon},{key:"dietary",label:"Dietary",icon:NoSymbolIcon},
];

export default function CafeteriaPage() {
  useTitle("Cafeteria & Meals"); const qc = useQueryClient();
  const [tab,setTab]=useState<Tab>("menus");
  const [showMenuForm,setShowMenuForm]=useState(false); const [editingMenu,setEditingMenu]=useState<MealMenu|null>(null);
  const [showPlanForm,setShowPlanForm]=useState(false); const [editingPlan,setEditingPlan]=useState<MealPlan|null>(null);
  const [showBookingForm,setShowBookingForm]=useState(false);
  const [showDietaryForm,setShowDietaryForm]=useState(false);

  const {data:menus=[],isLoading:mLoading}=useQuery({queryKey:["cafe-menus"],queryFn:async()=>{const r=await api.get<{results:MealMenu[]}>("/cafeteria/menus/");return r.results??[]}});
  const {data:plans=[],isLoading:pLoading}=useQuery({queryKey:["cafe-plans"],queryFn:async()=>{const r=await api.get<{results:MealPlan[]}>("/cafeteria/plans/");return r.results??[]}});
  const {data:bookings=[],isLoading:bLoading}=useQuery({queryKey:["cafe-bookings"],queryFn:async()=>{const r=await api.get<{results:MealBooking[]}>("/cafeteria/bookings/");return r.results??[]}});
  const {data:dietary=[],isLoading:dLoading}=useQuery({queryKey:["cafe-dietary"],queryFn:async()=>{const r=await api.get<{results:Dietary[]}>("/cafeteria/dietary/");return r.results??[]}});

  const delMenu=useMutation({mutationFn:(id:string)=>api.delete(`/cafeteria/menus/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["cafe-menus"]});toast.success("Deleted")}});
  const delPlan=useMutation({mutationFn:(id:string)=>api.delete(`/cafeteria/plans/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["cafe-plans"]});toast.success("Deleted")}});
  const delBooking=useMutation({mutationFn:(id:string)=>api.delete(`/cafeteria/bookings/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["cafe-bookings"]});toast.success("Deleted")}});
  const delDietary=useMutation({mutationFn:(id:string)=>api.delete(`/cafeteria/dietary/${id}/`),onSuccess:()=>{qc.invalidateQueries({queryKey:["cafe-dietary"]});toast.success("Deleted")}});

  return (<div className="space-y-6">
    <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-slate-900 dark:text-white">Cafeteria & Meals</h1><p className="text-sm text-slate-500 mt-1">Daily menus, meal plans, bookings, and dietary tracking</p></div>
      <div className="flex gap-2">
        {tab==="menus"&&<Button onClick={()=>{setEditingMenu(null);setShowMenuForm(true)}}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Menu</Button>}
        {tab==="plans"&&<Button onClick={()=>{setEditingPlan(null);setShowPlanForm(true)}}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Plan</Button>}
        {tab==="bookings"&&<Button onClick={()=>setShowBookingForm(true)}><PlusIcon className="h-4 w-4 mr-1.5"/>New Booking</Button>}
        {tab==="dietary"&&<Button onClick={()=>setShowDietaryForm(true)}><PlusIcon className="h-4 w-4 mr-1.5"/>Add Restriction</Button>}
      </div>
    </div>
    <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
      {TABS.map(t=>{const I=t.icon;return(<button key={t.key} onClick={()=>setTab(t.key)} className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap ${tab===t.key?"bg-white dark:bg-slate-700 shadow-sm":"text-slate-600 hover:text-slate-900"}`}><I className="h-4 w-4"/>{t.label}</button>)})}
    </div>
    {tab==="menus"&&(mLoading?<div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1,2,3].map(i=><div key={i} className="h-24 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"/>)}</div>:
      !menus.length?<EmptyState icon={BookOpenIcon} title="No menus" description="Create your first meal menu"/>:
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{menus.map(m=><div key={m.id} onClick={()=>{setEditingMenu(m);setShowMenuForm(true)}} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group"><div className="flex items-start justify-between mb-1"><div><p className="font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{m.name}</p><p className="text-xs text-slate-400">{dayjs(m.date).format("MMM D, YYYY")}</p></div><Badge color="indigo">{m.meal_type_display}</Badge></div>{m.items&&<p className="text-xs text-slate-500 mt-1">🍽️ {m.items}</p>}<p className="text-xs text-slate-400">${Number(m.price).toLocaleString()}</p>
        <div className="flex items-center gap-2 mt-1 text-xs">{m.is_vegetarian&&<span className="text-green-600">🌱 Veg</span>}{m.is_vegan&&<span className="text-green-600">🌿 Vegan</span>}{m.is_gluten_free&&<span className="text-amber-600">🌾 GF</span>}</div>
        <div className="flex gap-2 mt-2 pt-2 border-t border-slate-100" onClick={e=>e.stopPropagation()}><button onClick={()=>{setEditingMenu(m);setShowMenuForm(true)}} className="text-xs text-indigo-600 font-medium">Edit</button><button onClick={()=>{if(confirm("Delete?"))delMenu.mutate(m.id)}} className="text-xs text-red-500 font-medium">Delete</button></div></div>)}</div>)}
    {tab==="plans"&&(pLoading?<div className="grid gap-3 sm:grid-cols-2">{[1,2].map(i=><div key={i} className="h-24 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"/>)}</div>:
      !plans.length?<EmptyState icon={CreditCardIcon} title="No meal plans"/>:
      <div className="grid gap-3 sm:grid-cols-2">{plans.map(p=><div key={p.id} onClick={()=>{setEditingPlan(p);setShowPlanForm(true)}} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group"><div className="flex items-start justify-between"><div><p className="font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{p.name}</p><p className="text-lg font-bold text-indigo-600">${Number(p.price_per_period).toLocaleString()}<span className="text-sm font-normal text-slate-400">/{p.period_days} days</span></p></div><Badge color={p.is_active?"green":"slate"}>{p.is_active?"Active":"Inactive"}</Badge></div>{p.meals_included&&<p className="text-xs text-slate-400">Meals: {p.meals_included}</p>}
        <div className="flex gap-2 mt-2 pt-2 border-t border-slate-100" onClick={e=>e.stopPropagation()}><button onClick={()=>{setEditingPlan(p);setShowPlanForm(true)}} className="text-xs text-indigo-600 font-medium">Edit</button><button onClick={()=>{if(confirm("Delete?"))delPlan.mutate(p.id)}} className="text-xs text-red-500 font-medium">Delete</button></div></div>)}</div>)}
    {tab==="bookings"&&(bLoading?<div className="space-y-2">{[1,2,3].map(i=><div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"/>)}</div>:
      !bookings.length?<EmptyState icon={CalendarDaysIcon} title="No bookings"/>:
      <div className="space-y-2">{bookings.map(b=><div key={b.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md"><div className="flex items-start justify-between"><div><p className="font-semibold text-slate-900 dark:text-white">{b.user_name}</p><p className="text-xs text-slate-400">{b.menu_name} · {b.meal_type_display} · {dayjs(b.booking_date).format("MMM D")}</p></div><div className="flex gap-1 ml-4"><Badge color="green">{b.status_display}</Badge><button onClick={()=>{if(confirm("Delete?"))delBooking.mutate(b.id)}} className="text-xs text-red-500 font-medium ml-2">Delete</button></div></div></div>)}</div>)}
    {tab==="dietary"&&(dLoading?<div className="grid gap-3 sm:grid-cols-2">{[1,2].map(i=><div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"/>)}</div>:
      !dietary.length?<EmptyState icon={NoSymbolIcon} title="No dietary restrictions"/>:
      <div className="grid gap-3 sm:grid-cols-2">{dietary.map(d=><div key={d.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md"><div className="flex items-start justify-between"><div><p className="font-semibold text-slate-900 dark:text-white">{d.user_name}</p><p className="text-sm text-amber-600">⚠️ {d.restriction_type}{d.severity?` (${d.severity})`:""}</p></div><button onClick={()=>{if(confirm("Delete?"))delDietary.mutate(d.id)}} className="text-xs text-red-500 font-medium">Delete</button></div></div>)}</div>)}
    <MenuFormModal open={showMenuForm} onClose={()=>{setShowMenuForm(false);setEditingMenu(null)}} menu={editingMenu} onSaved={()=>{setShowMenuForm(false);setEditingMenu(null);qc.invalidateQueries({queryKey:["cafe-menus"]})}}/>
    <PlanFormModal open={showPlanForm} onClose={()=>{setShowPlanForm(false);setEditingPlan(null)}} plan={editingPlan} onSaved={()=>{setShowPlanForm(false);setEditingPlan(null);qc.invalidateQueries({queryKey:["cafe-plans"]})}}/>
    <BookingFormModal open={showBookingForm} onClose={()=>setShowBookingForm(false)} menus={menus} onSaved={()=>{setShowBookingForm(false);qc.invalidateQueries({queryKey:["cafe-bookings"]})}}/>
    <DietaryFormModal open={showDietaryForm} onClose={()=>setShowDietaryForm(false)} onSaved={()=>{setShowDietaryForm(false);qc.invalidateQueries({queryKey:["cafe-dietary"]})}}/>
  </div>);
}

function MenuFormModal({open,onClose,menu,onSaved}:{open:boolean;onClose:()=>void;menu?:MealMenu|null;onSaved:()=>void}){
  const [f,setF]=useState({meal_type:menu?.meal_type??"lunch",name:menu?.name??"",date:menu?.date??dayjs().format("YYYY-MM-DD"),items:menu?.items??"",price:menu?.price??0,is_vegetarian:menu?.is_vegetarian??false,is_vegan:menu?.is_vegan??false,is_gluten_free:menu?.is_gluten_free??false});
  const isEdit=!!menu;
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/cafeteria/menus/",d),onSuccess:()=>{toast.success("Menu created");onSaved()}});
  const update=useMutation({mutationFn:(d:typeof f)=>api.patch(`/cafeteria/menus/${menu!.id}/`,d),onSuccess:()=>{toast.success("Menu updated");onSaved()}});
  const saving=create.isPending||update.isPending;
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.name.trim())return toast.error("Name required");if(isEdit)update.mutate(f);else create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title={isEdit?"Edit Menu":"Add Menu"}><form onSubmit={submit} className="space-y-4">
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Name *</label><input value={f.name} onChange={e=>setF(p=>({...p,name:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div><div><label className="block text-sm font-medium mb-1">Meal Type</label><select value={f.meal_type} onChange={e=>setF(p=>({...p,meal_type:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="breakfast">Breakfast</option><option value="lunch">Lunch</option><option value="dinner">Dinner</option><option value="snack">Snack</option></select></div></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Date</label><input type="date" value={f.date} onChange={e=>setF(p=>({...p,date:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div><div><label className="block text-sm font-medium mb-1">Price</label><input type="number" min={0} value={f.price} onChange={e=>setF(p=>({...p,price:Number(e.target.value)}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div></div>
    <div><label className="block text-sm font-medium mb-1">Items</label><textarea value={f.items} onChange={e=>setF(p=>({...p,items:e.target.value}))} rows={2} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" placeholder="Comma-separated list of food items"/></div>
    <div className="flex items-center gap-4 text-sm"><label className="flex items-center gap-2"><input type="checkbox" checked={f.is_vegetarian} onChange={e=>setF(p=>({...p,is_vegetarian:e.target.checked}))}/> Vegetarian</label><label className="flex items-center gap-2"><input type="checkbox" checked={f.is_vegan} onChange={e=>setF(p=>({...p,is_vegan:e.target.checked}))}/> Vegan</label><label className="flex items-center gap-2"><input type="checkbox" checked={f.is_gluten_free} onChange={e=>setF(p=>({...p,is_gluten_free:e.target.checked}))}/> Gluten-Free</label></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={saving}>Cancel</Button><Button type="submit" loading={saving}>{isEdit?"Update":"Create"} Menu</Button></div>
  </form></Modal>);
}

function PlanFormModal({open,onClose,plan,onSaved}:{open:boolean;onClose:()=>void;plan?:MealPlan|null;onSaved:()=>void}){
  const [f,setF]=useState({name:plan?.name??"",price_per_period:plan?.price_per_period??0,period_days:plan?.period_days??30,meals_included:plan?.meals_included??"breakfast,lunch,dinner",description:plan?.description??""});
  const isEdit=!!plan;
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/cafeteria/plans/",d),onSuccess:()=>{toast.success("Plan created");onSaved()}});
  const update=useMutation({mutationFn:(d:typeof f)=>api.patch(`/cafeteria/plans/${plan!.id}/`,d),onSuccess:()=>{toast.success("Plan updated");onSaved()}});
  const saving=create.isPending||update.isPending;
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.name.trim())return toast.error("Name required");if(isEdit)update.mutate(f);else create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title={isEdit?"Edit Plan":"Add Meal Plan"}><form onSubmit={submit} className="space-y-4">
    <div><label className="block text-sm font-medium mb-1">Name *</label><input value={f.name} onChange={e=>setF(p=>({...p,name:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Price</label><input type="number" min={0} value={f.price_per_period} onChange={e=>setF(p=>({...p,price_per_period:Number(e.target.value)}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div><div><label className="block text-sm font-medium mb-1">Period (days)</label><input type="number" min={1} value={f.period_days} onChange={e=>setF(p=>({...p,period_days:Number(e.target.value)}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"/></div></div>
    <div><label className="block text-sm font-medium mb-1">Meals Included</label><input value={f.meals_included} onChange={e=>setF(p=>({...p,meals_included:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" placeholder="breakfast,lunch,dinner"/></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={saving}>Cancel</Button><Button type="submit" loading={saving}>{isEdit?"Update":"Create"} Plan</Button></div>
  </form></Modal>);
}

function BookingFormModal({open,onClose,menus,onSaved}:{open:boolean;onClose:()=>void;menus:MealMenu[];onSaved:()=>void}){
  const [f,setF]=useState({user:"",menu:"",meal_type:"lunch"});
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/cafeteria/bookings/",d),onSuccess:()=>{toast.success("Booking created");onSaved()}});
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.user||!f.menu)return toast.error("User and menu required");create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title="New Booking"><form onSubmit={submit} className="space-y-4">
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">User ID</label><input value={f.user} onChange={e=>setF(p=>({...p,user:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" placeholder="User UUID"/></div><div><label className="block text-sm font-medium mb-1">Menu</label><select value={f.menu} onChange={e=>setF(p=>({...p,menu:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="">Select...</option>{menus.map(m=><option key={m.id} value={m.id}>{m.name} ({dayjs(m.date).format("MMM D")})</option>)}</select></div></div>
    <div><label className="block text-sm font-medium mb-1">Meal Type</label><select value={f.meal_type} onChange={e=>setF(p=>({...p,meal_type:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"><option value="breakfast">Breakfast</option><option value="lunch">Lunch</option><option value="dinner">Dinner</option></select></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={create.isPending}>Cancel</Button><Button type="submit" loading={create.isPending}>Create Booking</Button></div>
  </form></Modal>);
}

function DietaryFormModal({open,onClose,onSaved}:{open:boolean;onClose:()=>void;onSaved:()=>void}){
  const [f,setF]=useState({user:"",restriction_type:"",severity:""});
  const create=useMutation({mutationFn:(d:typeof f)=>api.post("/cafeteria/dietary/",d),onSuccess:()=>{toast.success("Restriction added");onSaved()}});
  const submit=(e:React.FormEvent)=>{e.preventDefault();if(!f.restriction_type.trim())return toast.error("Restriction type required");create.mutate(f)};
  return(<Modal open={open} onClose={onClose} title="Add Dietary Restriction"><form onSubmit={submit} className="space-y-4">
    <div><label className="block text-sm font-medium mb-1">User ID</label><input value={f.user} onChange={e=>setF(p=>({...p,user:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" placeholder="User UUID"/></div>
    <div className="grid grid-cols-2 gap-4"><div><label className="block text-sm font-medium mb-1">Restriction *</label><input value={f.restriction_type} onChange={e=>setF(p=>({...p,restriction_type:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" placeholder="Vegetarian, Vegan, Nut Allergy"/></div><div><label className="block text-sm font-medium mb-1">Severity</label><input value={f.severity} onChange={e=>setF(p=>({...p,severity:e.target.value}))} className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm" placeholder="Allergy, Preference, Medical"/></div></div>
    <div className="flex justify-end gap-3 pt-2"><Button variant="secondary" onClick={onClose} disabled={create.isPending}>Cancel</Button><Button type="submit" loading={create.isPending}>Add Restriction</Button></div>
  </form></Modal>);
}
