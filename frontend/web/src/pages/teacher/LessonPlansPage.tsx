import React, { useState } from "react";
import { PlusIcon, DocumentTextIcon } from "@heroicons/react/24/outline";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { api } from "../../api/client";
import { Button, Badge, Modal, Input, Select, EmptyState, SkeletonCard } from "../../components/common";
import { fmt } from "../../utils";
import { useTitle } from "../../hooks";

const STATUS_COLOR: Record<string, "slate" | "green" | "blue"> = { draft:"slate", approved:"green", completed:"blue" };

export default function TeacherLessonPlansPage() {
  useTitle("Lesson Plans");
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ title:"", topic:"", objectives:"", content:"", date:"", duration_minutes:"45" });
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({ queryKey:["lesson-plans"], queryFn:()=>api.get<any>("/academics/lesson-plans/") });
  const plans = data?.results ?? [];

  const create = useMutation({
    mutationFn: (d: Record<string, string>) => api.post("/academics/lesson-plans/", d),
    onSuccess: () => { toast.success("Lesson plan created"); qc.invalidateQueries({queryKey:["lesson-plans"]}); setShowCreate(false); },
    onError: () => toast.error("Failed to create"),
  });

  const set = (k: string, v: string) => setForm(f=>({...f,[k]:v}));

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold text-slate-900">Lesson Plans</h1><p className="text-sm text-slate-500 mt-0.5">Manage your teaching plans</p></div>
        <Button variant="primary" leftIcon={<PlusIcon className="h-4 w-4"/>} onClick={()=>setShowCreate(true)}>New Plan</Button>
      </div>
      {isLoading ? <div className="grid grid-cols-1 gap-3"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div>
        : plans.length === 0
        ? <div className="card p-8"><EmptyState icon={DocumentTextIcon} title="No lesson plans yet" description="Create your first lesson plan to get started." /></div>
        : <div className="space-y-3">
            {plans.map((p: { id: string; title: string; status: string; subject_name: string; classroom_name: string; date: string; duration_minutes: number; topic: string }) => (
              <div key={p.id} className="card p-4 hover:border-indigo-200 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1"><h3 className="text-sm font-semibold text-slate-900">{p.title}</h3><Badge color={STATUS_COLOR[p.status]}>{p.status}</Badge></div>
                    <p className="text-xs text-slate-500">{p.subject_name} · {p.classroom_name} · {fmt.date(p.date)} · {p.duration_minutes} min</p>
                    <p className="text-xs text-slate-600 mt-1 line-clamp-1">{p.topic}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
      }
      <Modal open={showCreate} onClose={()=>setShowCreate(false)} title="New Lesson Plan" size="lg"
        footer={<><Button variant="secondary" onClick={()=>setShowCreate(false)}>Cancel</Button><Button variant="primary" loading={create.isPending} onClick={()=>create.mutate(form)}>Save Plan</Button></>}>
        <div className="space-y-4">
          <Input label="Title" value={form.title} onChange={e=>set("title",e.target.value)} placeholder="Lesson title…"/>
          <Input label="Topic" value={form.topic} onChange={e=>set("topic",e.target.value)} placeholder="Topic covered…"/>
          <div className="grid grid-cols-2 gap-4">
            <Input label="Date" type="date" value={form.date} onChange={e=>set("date",e.target.value)}/>
            <Input label="Duration (min)" type="number" value={form.duration_minutes} onChange={e=>set("duration_minutes",e.target.value)}/>
          </div>
          <div><label className="text-xs font-semibold text-slate-700 mb-1.5 block">Learning Objectives</label><textarea rows={3} value={form.objectives} onChange={e=>set("objectives",e.target.value)} className="input resize-none" placeholder="Students will be able to…"/></div>
          <div><label className="text-xs font-semibold text-slate-700 mb-1.5 block">Content / Notes</label><textarea rows={4} value={form.content} onChange={e=>set("content",e.target.value)} className="input resize-none" placeholder="Lesson content…"/></div>
        </div>
      </Modal>
    </div>
  );
}
