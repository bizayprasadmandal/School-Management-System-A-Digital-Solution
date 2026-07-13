/**
 * Admin Announcements — Create, publish and manage school announcements
 */

import React, { useState } from "react";
import { PlusIcon, MegaphoneIcon, EyeIcon, TrashIcon } from "@heroicons/react/24/outline";
import { Button, Input, Select, Modal, SkeletonCard } from "../../components/common";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import dayjs from "dayjs";
import { useAnnouncements } from "../../api/hooks";
import { api } from "../../api/client";
import type { Announcement } from "../../types";

const PRIORITY_COLORS: Record<string, string> = {
  low:    "bg-slate-100 text-slate-600",
  normal: "bg-blue-100 text-blue-700",
  high:   "bg-amber-100 text-amber-700",
  urgent: "bg-red-100 text-red-700",
};

const AUDIENCE_LABELS: Record<string, string> = {
  all: "All Users", teachers: "Teachers", students: "Students",
  parents: "Parents", staff: "Staff",
};

interface CreateModalProps { onClose: () => void; }

function CreateAnnouncementModal({ onClose }: CreateModalProps) {
  const [form, setForm] = useState({
    title: "", content: "", priority: "normal", audience: "all",
    send_email: false, send_push: true, is_draft: false,
  });
  const qc = useQueryClient();
  const { mutate, isPending } = useMutation({
    mutationFn: () => api.post<Announcement>("/communication/announcements/", form),
    onSuccess: () => {
      toast.success(form.is_draft ? "Draft saved" : "Announcement published!");
      qc.invalidateQueries({ queryKey: ["announcements"] });
      onClose();
    },
    onError: () => toast.error("Failed to publish announcement"),
  });

  const set = <K extends keyof typeof form>(k: K, v: (typeof form)[K]) => setForm(f => ({ ...f, [k]: v }));

  return (
    <Modal
      open
      onClose={onClose}
      title="New Announcement"
      size="lg"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button variant="secondary" onClick={() => { set("is_draft", true); setTimeout(() => mutate(), 0); }}
            disabled={isPending || !form.title}>Save Draft</Button>
          <Button onClick={() => mutate()} loading={isPending} disabled={!form.title || !form.content}>
            Publish Now
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <Input label="Title *" value={form.title} onChange={e => set("title", e.target.value)}
          placeholder="Announcement title…" />
        <div>
          <label className="text-xs font-medium text-slate-700 mb-1 block">Content *</label>
          <textarea rows={5} value={form.content} onChange={e => set("content", e.target.value)}
            placeholder="Write your announcement here…"
            className="w-full rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Select label="Priority" value={form.priority} onChange={e => set("priority", e.target.value)}
            options={[
              { value: "low", label: "Low" },
              { value: "normal", label: "Normal" },
              { value: "high", label: "High" },
              { value: "urgent", label: "🚨 Urgent" },
            ]} />
          <Select label="Audience" value={form.audience} onChange={e => set("audience", e.target.value)}
            options={Object.entries(AUDIENCE_LABELS).map(([v, l]) => ({ value: v, label: l }))} />
        </div>
        <div className="flex flex-wrap gap-4">
          {[
            { key: "send_push", label: "Send Push Notification" },
            { key: "send_email", label: "Send Email" },
          ].map(({ key, label }) => (
            <label key={key} className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
              <input type="checkbox" checked={(form)[key as keyof typeof form] as boolean}
                onChange={e => set(key as keyof typeof form, e.target.checked)}
                className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" />
              {label}
            </label>
          ))}
        </div>
      </div>
    </Modal>
  );
}

export default function AnnouncementsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const { data, isLoading } = useAnnouncements();
  const announcements = data?.results ?? [];
  const qc = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/communication/announcements/${id}/`),
    onSuccess: () => { toast.success("Announcement deleted"); qc.invalidateQueries({ queryKey: ["announcements"] }); },
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Announcements</h1>
          <p className="text-sm text-slate-500 mt-0.5">Communicate with students, parents and staff</p>
        </div>
        <Button variant="primary" leftIcon={<PlusIcon className="h-4 w-4" />} onClick={() => setShowCreate(true)}>
          New Announcement
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-3"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div>
      ) : announcements.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-400 rounded-xl bg-white border border-slate-100">
          <MegaphoneIcon className="h-12 w-12 mb-3 opacity-30" />
          <p className="text-base font-medium">No announcements yet</p>
          <p className="text-sm mt-1">Create your first announcement to communicate with your community</p>
        </div>
      ) : (
        <div className="space-y-3">
          {announcements.map(a => (
            <div key={a.id} className="rounded-xl bg-white p-5 shadow-sm border border-slate-100 hover:border-slate-200 transition-colors">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                    <span className={`rounded-full px-2 py-0.5 text-xs font-semibold uppercase ${PRIORITY_COLORS[a.priority]}`}>
                      {a.priority}
                    </span>
                    <span className="rounded-full bg-slate-100 text-slate-600 px-2 py-0.5 text-xs">
                      {AUDIENCE_LABELS[a.audience]}
                    </span>
                    {a.published_at && (
                      <span className="text-xs text-green-600 font-medium">✓ Published</span>
                    )}
                  </div>
                  <h3 className="text-base font-semibold text-slate-900 leading-snug">{a.title}</h3>
                  <p className="text-sm text-slate-500 mt-1 line-clamp-2">{a.content}</p>
                  <div className="flex items-center gap-4 mt-3 text-xs text-slate-400">
                    <span>{dayjs(a.created_at).format("MMM D, YYYY [at] h:mm A")}</span>
                    <span>{a.view_count} views</span>
                  </div>
                </div>
                <div className="flex items-center gap-1 flex-shrink-0">
                  <Button variant="ghost" size="sm">
                    <EyeIcon className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm"
                    onClick={() => {
                      if (window.confirm("Delete this announcement?")) deleteMutation.mutate(a.id);
                    }}>
                    <TrashIcon className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showCreate && <CreateAnnouncementModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
