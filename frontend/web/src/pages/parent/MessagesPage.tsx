/**
 * Parent Messages Page — message teachers and staff
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Avatar, Badge, EmptyState, Button, SkeletonText, SkeletonCard } from "../../components/common";
import { useTitle } from "../../hooks";
import { ChatBubbleLeftEllipsisIcon, PaperAirplaneIcon } from "@heroicons/react/24/outline";

interface MessageThread {
  partner: { id: string; name: string; avatar?: string; role: string };
  last_message: { content: string; sent_at: string };
  unread_count: number;
}

interface ThreadMessage {
  id: string;
  content: string;
  sent_at: string;
  is_mine: boolean;
}
import dayjs from "dayjs";
import toast from "react-hot-toast";

export default function ParentMessagesPage() {
  useTitle("Messages");
  const qc = useQueryClient();
  const [activeThread, setActiveThread] = useState<string | null>(null);
  const [msgText, setMsgText] = useState("");

  const { data: inbox, isLoading } = useQuery({
    queryKey: ["parent-inbox"],
    queryFn: () => api.get<MessageThread[]>("/communication/messages/inbox/"),
  });

  const { data: thread, isLoading: threadLoading } = useQuery({
    queryKey: ["parent-thread", activeThread],
    queryFn: () => api.get<ThreadMessage[]>(`/communication/messages/conversation/${activeThread}/`),
    enabled: !!activeThread,
    refetchInterval: 5000,
  });

  const sendMsg = useMutation({
    mutationFn: (content: string) => api.post("/communication/messages/", { recipient: activeThread, content }),
    onSuccess: () => { setMsgText(""); qc.invalidateQueries({ queryKey: ["parent-thread", activeThread] }); },
    onError: () => toast.error("Failed to send message."),
  });

  const threads = inbox ?? [];

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold text-slate-900">Messages</h1><p className="text-sm text-slate-500 mt-1">Communicate with your children&apos;s teachers</p></div>
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden" style={{minHeight:480}}>
        <div className="flex h-full" style={{minHeight:480}}>
          {/* Thread list */}
          <div className="w-full sm:w-72 border-r border-slate-100 flex-shrink-0 flex flex-col">
            <div className="p-3 border-b border-slate-100 flex items-center justify-between">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Conversations</p>
              {threads.length > 0 && <span className="text-xs text-slate-400">{threads.length}</span>}
            </div>
            <div className="flex-1 overflow-y-auto">
              {isLoading ? <div className="p-4"><SkeletonText lines={6} /></div>
                : threads.length === 0
                ? <div className="p-6"><EmptyState icon={ChatBubbleLeftEllipsisIcon} title="No messages yet" description="Start a conversation with a teacher from the school portal." /></div>
                : threads.map((t: MessageThread) => (
                  <button key={t.partner.id} onClick={() => setActiveThread(t.partner.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-50 transition-colors text-left ${activeThread===t.partner.id?"bg-violet-50 border-r-2 border-violet-600":""}`}>
                    <Avatar name={t.partner.name} size="md" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-semibold text-slate-800 truncate">{t.partner.name}</p>
                        <p className="text-[10px] text-slate-400 flex-shrink-0 ml-1">{dayjs(t.last_message.sent_at).fromNow()}</p>
                      </div>
                      <p className="text-xs text-slate-500 truncate mt-0.5">{t.last_message.content}</p>
                    </div>
                    {t.unread_count > 0 && <span className="flex h-5 w-5 items-center justify-center rounded-full bg-violet-600 text-[10px] font-bold text-white">{t.unread_count}</span>}
                  </button>
                ))
              }
            </div>
          </div>

          {/* Message area */}
          <div className="flex-1 flex flex-col">
            {!activeThread
              ? <div className="flex-1 flex items-center justify-center text-slate-400"><div className="text-center"><ChatBubbleLeftEllipsisIcon className="h-12 w-12 mx-auto mb-2 opacity-20"/><p className="text-sm">Select a conversation to read messages</p></div></div>
              : threadLoading
              ? <div className="flex-1 p-4"><SkeletonCard /></div>
              : (
                <>
                  <div className="flex-1 overflow-y-auto p-4 flex flex-col-reverse gap-2">
                    {[...(thread ?? [])].reverse().map((m: ThreadMessage) => (
                      <div key={m.id} className={`flex ${m.is_mine ? "justify-end" : "justify-start"}`}>
                        <div className={`max-w-xs rounded-2xl px-4 py-2.5 text-sm ${m.is_mine ? "bg-violet-600 text-white" : "bg-slate-100 text-slate-800"}`}>
                          <p>{m.content}</p>
                          <p className={`text-[10px] mt-1 ${m.is_mine ? "text-violet-200" : "text-slate-400"}`}>{dayjs(m.sent_at).format("h:mm A")}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="border-t border-slate-100 p-3 flex gap-2">
                    <textarea rows={1} value={msgText} onChange={e=>setMsgText(e.target.value)}
                      onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();msgText.trim()&&sendMsg.mutate(msgText);}}}
                      placeholder="Message a teacher…"
                      className="flex-1 resize-none rounded-xl border border-slate-200 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500" />
                    <Button variant="primary" size="sm" onClick={()=>msgText.trim()&&sendMsg.mutate(msgText)} loading={sendMsg.isPending}
                      leftIcon={<PaperAirplaneIcon className="h-4 w-4"/>} className="bg-violet-600 hover:bg-violet-700">Send</Button>
                  </div>
                </>
              )
            }
          </div>
        </div>
      </div>
    </div>
  );
}
