/** Bulk Messages — Compose and send SMS/Email/Push messages to targeted audiences */

import React, { useState, useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  EnvelopeIcon, ChatBubbleBottomCenterTextIcon,
  BellIcon, UsersIcon, PaperAirplaneIcon, ClockIcon,
  CheckCircleIcon, XCircleIcon, MegaphoneIcon,
  AcademicCapIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, Badge, EmptyState, Input, Select } from "../../components/common";
import { useAnnouncements, useGradeLevels } from "../../api/hooks";
import type { Announcement, GradeLevel, Classroom } from "../../types";

const AUDIENCE_LABELS: Record<string, string> = {
  all: "All Users",
  teachers: "Teachers Only",
  students: "Students Only",
  parents: "Parents Only",
  staff: "Staff Only",
};

const CHANNEL_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  email: EnvelopeIcon,
  sms: ChatBubbleBottomCenterTextIcon,
  push: BellIcon,
};

function ChannelBadge({ channel }: { channel: string }) {
  const Icon = CHANNEL_ICONS[channel] || BellIcon;
  const colors: Record<string, string> = {
    email: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
    sms: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
    push: "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
  };
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${colors[channel] || "bg-slate-100 text-slate-600"}`}>
      <Icon className="h-3 w-3" />
      {channel === "email" ? "Email" : channel === "sms" ? "SMS" : "Push"}
    </span>
  );
}

export default function BulkMessagesPage() {
  const [mode, setMode] = useState<"compose" | "history">("compose");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [audience, setAudience] = useState("all");
  const [channels, setChannels] = useState({ email: true, sms: false, push: true });
  const [gradeId, setGradeId] = useState<number | "">("");
  const [classroomId, setClassroomId] = useState<number | "">("");
  const qc = useQueryClient();

  const { data: gradesData } = useGradeLevels();
  const grades = gradesData?.results ?? [];

  const { data: classroomsData } = useQuery({
    queryKey: ["classrooms", "by-grade", gradeId],
    queryFn: async () => {
      if (!gradeId) return [];
      const res = await api.get<{ results: Classroom[] }>("/students/classrooms/", { grade: gradeId });
      return res.results ?? [];
    },
    enabled: !!gradeId,
  });
  const classrooms = classroomsData ?? [];

  const { data: historyData, isLoading: historyLoading } = useAnnouncements();

  const sentMessages = useMemo(() => {
    if (!historyData?.results) return [];
    return historyData.results.filter(a => !a.is_draft);
  }, [historyData]);

  const sendMut = useMutation({
    mutationFn: () => api.post<Announcement>("/communication/announcements/", {
      title,
      content,
      priority: "normal",
      audience,
      send_email: channels.email,
      send_sms: channels.sms,
      send_push: channels.push,
      target_grades: gradeId ? [gradeId] : [],
      target_classrooms: classroomId ? [classroomId] : [],
      is_draft: false,
    }),
    onSuccess: () => {
      toast.success("Message sent successfully!");
      setTitle("");
      setContent("");
      qc.invalidateQueries({ queryKey: ["announcements"] });
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail ?? "Failed to send message"),
  });

  const estimatedRecipients = useMemo(() => {
    switch (audience) {
      case "all": return "All school members";
      case "teachers": return "All teachers";
      case "students": return "All students";
      case "parents": return "All parents/guardians";
      case "staff": return "All staff";
      default: return "Selected audience";
    }
  }, [audience]);

  const activeChannelCount = [channels.email, channels.sms, channels.push].filter(Boolean).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Bulk Messages</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Send mass SMS, email, and push notifications to targeted groups</p>
        </div>
      </div>

      {/* Mode tabs */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        <button onClick={() => setMode("compose")}
          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${mode === "compose" ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm" : "text-slate-600 dark:text-slate-400"}`}>
          <PaperAirplaneIcon className="h-4 w-4" /> Compose Message
        </button>
        <button onClick={() => setMode("history")}
          className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${mode === "history" ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm" : "text-slate-600 dark:text-slate-400"}`}>
          <ClockIcon className="h-4 w-4" /> Sent History ({sentMessages.length})
        </button>
      </div>

      {mode === "compose" ? (
        <div className="grid grid-cols-3 gap-6">
          {/* Main compose area */}
          <div className="col-span-2 space-y-5">
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 space-y-5">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Message</h2>

              <Input label="Subject / Title *" value={title} onChange={e => setTitle(e.target.value)}
                placeholder="e.g. School Closure Notice, Exam Schedule Update" />

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Message Body *</label>
                <textarea rows={6} value={content} onChange={e => setContent(e.target.value)}
                  placeholder="Write your message here..."
                  className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 focus:ring-2 focus:ring-indigo-500 resize-none" />
                <p className="text-xs text-slate-400 mt-1">{content.length} characters{channels.sms ? ` — SMS limit: 160 chars (${content.length > 160 ? '⚠️ will be split' : '✓ ok'})` : ""}</p>
              </div>
            </div>

            {/* Channel selection */}
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 space-y-4">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Delivery Channels</h2>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { key: "email" as const, label: "Email", icon: EnvelopeIcon, desc: "Via SendGrid", activeColor: "border-blue-500 bg-blue-50 dark:bg-blue-900/20", textColor: "text-blue-700", mutedText: "text-blue-600", checkColor: "text-blue-500" },
                  { key: "sms" as const, label: "SMS", icon: ChatBubbleBottomCenterTextIcon, desc: "Via Twilio", activeColor: "border-emerald-500 bg-emerald-50 dark:bg-emerald-900/20", textColor: "text-emerald-700", mutedText: "text-emerald-600", checkColor: "text-emerald-500" },
                  { key: "push" as const, label: "Push", icon: BellIcon, desc: "Via FCM", activeColor: "border-purple-500 bg-purple-50 dark:bg-purple-900/20", textColor: "text-purple-700", mutedText: "text-purple-600", checkColor: "text-purple-500" },
                ].map(({ key, label, icon: Icon, desc, activeColor, textColor, mutedText, checkColor }) => (
                  <button key={key} onClick={() => setChannels(p => ({ ...p, [key]: !p[key] }))}
                    className={`relative rounded-xl border-2 p-4 text-left transition-all ${
                      channels[key]
                        ? activeColor
                        : "border-slate-200 dark:border-slate-700 hover:border-slate-300"
                    }`}>
                    <div className={`flex items-center gap-2 mb-1.5 ${channels[key] ? textColor : "text-slate-500"}`}>
                      <Icon className="h-5 w-5" />
                      <span className="font-semibold text-sm">{label}</span>
                    </div>
                    <p className={`text-xs ${channels[key] ? mutedText : "text-slate-400"}`}>{desc}</p>
                    {channels[key] && (
                      <CheckCircleIcon className={`absolute top-2 right-2 h-4 w-4 ${checkColor}`} />
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Sidebar - targeting */}
          <div className="space-y-5">
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6 space-y-4">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Target Audience</h2>

              <Select label="Audience" value={audience} onChange={e => setAudience(e.target.value)}
                options={Object.entries(AUDIENCE_LABELS).map(([v, l]) => ({ value: v, label: l }))} />

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Filter by Grade (optional)</label>
                <select value={gradeId} onChange={e => { setGradeId(e.target.value ? parseInt(e.target.value) : ""); setClassroomId(""); }}
                  className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
                  <option value="">All Grades</option>
                  {grades.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
                </select>
              </div>

              {gradeId && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">Filter by Classroom</label>
                  <select value={classroomId} onChange={e => setClassroomId(e.target.value ? parseInt(e.target.value) : "")}
                    className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
                    <option value="">All Classrooms</option>
                    {classrooms.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
              )}

              <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3 space-y-2">
                <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                  <UsersIcon className="h-3.5 w-3.5" />
                  <span>Targeting: <strong className="text-slate-700 dark:text-slate-200">{estimatedRecipients}</strong></span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <PaperAirplaneIcon className="h-3.5 w-3.5" />
                  <span>Channels: <strong className="text-slate-700 dark:text-slate-200">{activeChannelCount} selected</strong></span>
                </div>
                {gradeId && (
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <AcademicCapIcon className="h-3.5 w-3.5" />
                    <span>Filter: Grade {grades.find(g => g.id === gradeId)?.name}{classroomId ? ` / ${classrooms.find((c: Classroom) => c.id === classroomId)?.name}` : ""}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Send button */}
            <Button className="w-full py-3" onClick={() => sendMut.mutate()} loading={sendMut.isPending}
              disabled={!title.trim() || !content.trim()}>
              <PaperAirplaneIcon className="h-4 w-4" />
              Send to {estimatedRecipients}
              {activeChannelCount > 0 && ` (${activeChannelCount} channels)`}
            </Button>
          </div>
        </div>
      ) : (
        /* Sent history */
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          {historyLoading ? (
            <div className="p-6 space-y-3">{[1,2,3].map(i => <div key={i} className="h-16 bg-slate-100 dark:bg-slate-700 rounded-lg animate-pulse" />)}</div>
          ) : sentMessages.length === 0 ? (
            <EmptyState icon={MegaphoneIcon} title="No messages sent yet" description="Your sent bulk messages will appear here" />
          ) : (
            <div className="divide-y divide-slate-100 dark:divide-slate-700">
              {sentMessages.slice(0, 50).map(msg => (
                <div key={msg.id} className="p-5 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <h3 className="font-semibold text-slate-900 dark:text-white text-sm">{msg.title}</h3>
                        <Badge color={msg.audience === "all" ? "indigo" : "blue"}>{AUDIENCE_LABELS[msg.audience]}</Badge>
                      </div>
                      <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-1 mb-2">{msg.content}</p>
                      <div className="flex items-center gap-2 flex-wrap">
                        {(msg.send_email || msg.send_sms || msg.send_push) && (
                          <>
                            {msg.send_email && <ChannelBadge channel="email" />}
                            {msg.send_sms && <ChannelBadge channel="sms" />}
                            {msg.send_push && <ChannelBadge channel="push" />}
                          </>
                        )}
                        <span className="text-xs text-slate-400">{dayjs(msg.created_at).format("MMM D, YYYY h:mm A")}</span>
                        <span className="text-xs text-slate-400">{msg.view_count} views</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
