/**
 * Cafeteria & Meal Management — Admin page for menus, meal plans, bookings, dietary restrictions.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import { PlusIcon, BookOpenIcon, CreditCardIcon, CalendarDaysIcon, NoSymbolIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface MealMenu { id:string; name:string; date:string; meal_type_display:string; items:string; price:number; is_vegetarian:boolean; is_vegan:boolean; }
interface MealPlan { id:string; name:string; price_per_period:number; period_days:number; meals_included:string; is_active:boolean; }
interface MealBooking { id:string; user_name:string; menu_name:string; meal_type_display:string; status_display:string; booking_date:string; }
interface DietaryRestriction { id:string; user_name:string; restriction_type:string; severity:string; }

type Tab = "menus"|"plans"|"bookings"|"dietary";
const TABS:{key:Tab;label:string;icon:React.ComponentType<{className?:string}>}[] = [
  {key:"menus",label:"Menus",icon:BookOpenIcon},{key:"plans",label:"Meal Plans",icon:CreditCardIcon},{key:"bookings",label:"Bookings",icon:CalendarDaysIcon},{key:"dietary",label:"Dietary",icon:NoSymbolIcon},
];

export default function CafeteriaPage() {
  useTitle("Cafeteria & Meals"); const qc = useQueryClient();
  const [tab,setTab]=useState<Tab>("menus");
  const {data:menus=[]}=useQuery({queryKey:["cafe-menus"],queryFn:async()=>{const r=await api.get<{results:MealMenu[]}>("/cafeteria/menus/");return r.results??[]}});
  const {data:plans=[]}=useQuery({queryKey:["cafe-plans"],queryFn:async()=>{const r=await api.get<{results:MealPlan[]}>("/cafeteria/plans/");return r.results??[]}});
  const {data:bookings=[]}=useQuery({queryKey:["cafe-bookings"],queryFn:async()=>{const r=await api.get<{results:MealBooking[]}>("/cafeteria/bookings/");return r.results??[]}});
  const {data:dietary=[]}=useQuery({queryKey:["cafe-dietary"],queryFn:async()=>{const r=await api.get<{results:DietaryRestriction[]}>("/cafeteria/dietary/");return r.results??[]}});

  return (<div className="space-y-6">
    <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-slate-900 dark:text-white">Cafeteria & Meals</h1><p className="text-sm text-slate-500 mt-1">Daily menus, meal plans, bookings, and dietary tracking</p></div></div>
    <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
      {TABS.map(t=>{const Icon=t.icon;return(<button key={t.key} onClick={()=>setTab(t.key)} className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap ${tab===t.key?"bg-white dark:bg-slate-700 shadow-sm":"text-slate-600 hover:text-slate-900"}`}><Icon className="h-4 w-4"/>{t.label}</button>)})}
    </div>
    {tab==="menus"&&(!menus.length?<EmptyState icon={BookOpenIcon} title="No menus" description="Create your first meal menu"/>:
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{menus.map(m=><div key={m.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><div className="flex items-start justify-between mb-1"><p className="font-semibold">{m.name}</p><Badge color="indigo">{m.meal_type_display}</Badge></div><p className="text-xs text-slate-400">{dayjs(m.date).format("MMM D, YYYY")} · ${Number(m.price).toLocaleString()}</p>{m.items&&<p className="text-xs text-slate-500 mt-1">🍽️ {m.items}</p>}<div className="flex gap-2 mt-1 text-xs">{m.is_vegetarian&&<span className="text-green-600">🌱 Vegetarian</span>}{m.is_vegan&&<span className="text-green-600">🌿 Vegan</span>}</div></div>)}</div>)}
    {tab==="plans"&&(!plans.length?<EmptyState icon={CreditCardIcon} title="No meal plans"/>:
      <div className="grid gap-3 sm:grid-cols-2">{plans.map(p=><div key={p.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><p className="font-semibold">{p.name}</p><p className="text-lg font-bold text-indigo-600">${Number(p.price_per_period).toLocaleString()}<span className="text-sm font-normal text-slate-400">/{p.period_days} days</span></p>{p.meals_included&&<p className="text-xs text-slate-400">Meals: {p.meals_included}</p>}</div>)}</div>)}
    {tab==="bookings"&&(!bookings.length?<EmptyState icon={CalendarDaysIcon} title="No bookings"/>:
      <div className="space-y-2">{bookings.map(b=><div key={b.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4 flex items-center justify-between"><div><p className="font-semibold">{b.user_name}</p><p className="text-xs text-slate-400">{b.menu_name} · {b.meal_type_display} · {dayjs(b.booking_date).format("MMM D")}</p></div><span className="text-xs font-medium px-2 py-0.5 rounded bg-green-100 text-green-700">{b.status_display}</span></div>)}</div>)}
    {tab==="dietary"&&(!dietary.length?<EmptyState icon={NoSymbolIcon} title="No dietary restrictions"/>:
      <div className="grid gap-3 sm:grid-cols-2">{dietary.map(d=><div key={d.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 p-4"><p className="font-semibold">{d.user_name}</p><p className="text-sm text-amber-600">⚠️ {d.restriction_type}{d.severity?` (${d.severity})`:""}</p></div>)}</div>)}
  </div>);
}
