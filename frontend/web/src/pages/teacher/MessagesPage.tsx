import React from "react";
import { ChatBubbleLeftEllipsisIcon } from "@heroicons/react/24/outline";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Avatar, EmptyState, SkeletonText } from "../../components/common";
import { useTitle } from "../../hooks";
import dayjs from "dayjs";

export default function TeacherMessagesPage() {
  useTitle("Messages");
  const { data: inbox, isLoading } = useQuery({ queryKey:["inbox"], queryFn:()=>api.get<any[]>("/communication/messages/inbox/") });
  const threads = inbox ?? [];

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold text-slate-900">Messages</h1><p className="text-sm text-slate-500 mt-1">Direct messages with students and parents</p></div>
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none" style={{minHeight:480}}>
        <div className="flex" style={{minHeight:480}}>
          <div className="w-80 border-r border-slate-100 flex-shrink-0">
            <div className="p-3 border-b border-slate-100"><p className="text-xs font-semibold text-slate-500 uppercase">Conversations</p></div>
            {isLoading ? <div className="p-4"><SkeletonText lines={6} /></div>
              : threads.length === 0
              ? <div className="p-8"><EmptyState icon={ChatBubbleLeftEllipsisIcon} title="No messages yet" description="Messages from students and parents appear here." /></div>
              : threads.map((t: { partner: { id: string; name: string }; last_message: { content: string; sent_at: string }; unread_count: number }) => (
                <div key={t.partner.id} className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 cursor-pointer transition-colors">
                  <Avatar name={t.partner.name} size="md" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-semibold text-slate-800 truncate">{t.partner.name}</p>
                      <p className="text-xs text-slate-400">{dayjs(t.last_message.sent_at).fromNow()}</p>
                    </div>
                    <p className="text-xs text-slate-500 truncate mt-0.5">{t.last_message.content}</p>
                  </div>
                  {t.unread_count > 0 && <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white">{t.unread_count}</span>}
                </div>
              ))
            }
          </div>
          <div className="flex-1 flex items-center justify-center text-slate-400">
            <div className="text-center"><ChatBubbleLeftEllipsisIcon className="h-12 w-12 mx-auto mb-2 opacity-20"/><p className="text-sm">Select a conversation to read messages</p></div>
          </div>
        </div>
      </div>
    </div>
  );
}
