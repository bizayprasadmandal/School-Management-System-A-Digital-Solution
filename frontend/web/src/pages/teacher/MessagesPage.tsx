/**
 * Teacher Messages Page — direct messages with students and parents
 * Full compose/reply UI with thread list, conversation view, and send message
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import {
  Avatar,
  EmptyState,
  Button,
  SkeletonText,
  SkeletonCard,
  ErrorState,
} from "../../components/common";
import { useTitle, useChatSocket } from "../../hooks";
import { ChatBubbleLeftEllipsisIcon, PaperAirplaneIcon } from "@heroicons/react/24/outline";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import toast from "react-hot-toast";

dayjs.extend(relativeTime);

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

export default function TeacherMessagesPage() {
  useTitle("Messages");
  const qc = useQueryClient();
  const [activeThread, setActiveThread] = useState<string | null>(null);
  const [msgText, setMsgText] = useState("");

  // ── Inbox (thread list) ──────────────────────────────────────────────────

  const {
    data: inbox,
    isLoading,
    isError: inboxError,
    refetch: refetchInbox,
  } = useQuery({
    queryKey: ["teacher-inbox"],
    queryFn: () => api.get<MessageThread[]>("/communication/messages/inbox/"),
  });

  // ── Active conversation ──────────────────────────────────────────────────

  const {
    data: thread,
    isLoading: threadLoading,
    isError: threadError,
    refetch: refetchThread,
  } = useQuery({
    queryKey: ["teacher-thread", activeThread],
    queryFn: () =>
      api.get<ThreadMessage[]>(`/communication/messages/conversation/${activeThread}/`),
    enabled: !!activeThread,
  });

  // Live updates over WebSocket — replaces polling. Invalidating the thread
  // query on each inbound message avoids duplicating the echoed send.
  const { isTyping, sendTyping } = useChatSocket(
    activeThread ?? "",
    () => {
      if (activeThread) {
        qc.invalidateQueries({ queryKey: ["teacher-thread", activeThread] });
        qc.invalidateQueries({ queryKey: ["teacher-inbox"] });
      }
    },
    !!activeThread,
  );

  // ── Send message ─────────────────────────────────────────────────────────

  const sendMsg = useMutation({
    mutationFn: (content: string) =>
      api.post("/communication/messages/", { recipient: activeThread, content }),
    onSuccess: () => {
      setMsgText("");
      qc.invalidateQueries({ queryKey: ["teacher-thread", activeThread] });
    },
    onError: () => toast.error("Failed to send message."),
  });

  const threads = inbox ?? [];

  return (
    <div className="space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Messages</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Direct messages with students and parents
        </p>
      </div>

      {/* Main panel */}
      <div
        className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden"
        style={{ minHeight: 480 }}
      >
        <div className="flex h-full" style={{ minHeight: 480 }}>
          {/* ── Thread list ─────────────────────────────────────────────── */}
          <div className="w-full sm:w-72 border-r border-slate-100 dark:border-slate-700 flex-shrink-0 flex flex-col">
            <div className="p-3 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                Conversations
              </p>
              {threads.length > 0 && (
                <span className="text-xs text-slate-400 dark:text-slate-500">{threads.length}</span>
              )}
            </div>
            <div className="flex-1 overflow-y-auto">
              {isLoading ? (
                <div className="p-4">
                  <SkeletonText lines={6} />
                </div>
              ) : inboxError ? (
                <div className="p-4">
                  <ErrorState onRetry={() => refetchInbox()} />
                </div>
              ) : threads.length === 0 ? (
                <div className="p-6">
                  <EmptyState
                    icon={ChatBubbleLeftEllipsisIcon}
                    title="No messages yet"
                    description="Messages from students and parents appear here."
                  />
                </div>
              ) : (
                threads.map((t: MessageThread) => (
                  <button
                    key={t.partner.id}
                    onClick={() => setActiveThread(t.partner.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors text-left ${
                      activeThread === t.partner.id
                        ? "bg-indigo-50 dark:bg-indigo-900/20 border-r-2 border-indigo-600 dark:border-indigo-400"
                        : ""
                    }`}
                  >
                    <Avatar name={t.partner.name} size="md" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-semibold text-slate-800 dark:text-white truncate">
                          {t.partner.name}
                        </p>
                        <p className="text-[10px] text-slate-400 dark:text-slate-500 flex-shrink-0 ml-1">
                          {dayjs(t.last_message.sent_at).fromNow()}
                        </p>
                      </div>
                      <p className="text-xs text-slate-500 dark:text-slate-400 truncate mt-0.5">
                        {t.last_message.content}
                      </p>
                    </div>
                    {t.unread_count > 0 && (
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 dark:bg-indigo-500 text-[10px] font-bold text-white flex-shrink-0">
                        {t.unread_count}
                      </span>
                    )}
                  </button>
                ))
              )}
            </div>
          </div>

          {/* ── Message area ─────────────────────────────────────────────── */}
          <div className="flex-1 flex flex-col">
            {!activeThread ? (
              <div className="flex-1 flex items-center justify-center text-slate-400 dark:text-slate-500">
                <div className="text-center">
                  <ChatBubbleLeftEllipsisIcon className="h-12 w-12 mx-auto mb-2 opacity-20" />
                  <p className="text-sm">Select a conversation to read messages</p>
                </div>
              </div>
            ) : threadLoading ? (
              <div className="flex-1 p-4">
                <SkeletonCard />
              </div>
            ) : threadError ? (
              <div className="flex-1 p-4">
                <ErrorState onRetry={() => refetchThread()} />
              </div>
            ) : (
              <>
                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 flex flex-col-reverse gap-2">
                  {[...(thread ?? [])].reverse().map((m: ThreadMessage) => (
                    <div
                      key={m.id}
                      className={`flex ${m.is_mine ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md rounded-2xl px-4 py-2.5 text-sm ${
                          m.is_mine
                            ? "bg-indigo-600 text-white rounded-br-md"
                            : "bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-bl-md"
                        }`}
                      >
                        <p>{m.content}</p>
                        <p
                          className={`text-[10px] mt-1 ${
                            m.is_mine ? "text-indigo-200" : "text-slate-400 dark:text-slate-500"
                          }`}
                        >
                          {dayjs(m.sent_at).format("h:mm A")}
                        </p>
                      </div>
                    </div>
                  ))}
                  {(!thread || thread.length === 0) && (
                    <div className="flex-1 flex items-center justify-center text-slate-400 dark:text-slate-500">
                      <p className="text-sm">No messages yet. Send the first message below.</p>
                    </div>
                  )}
                </div>

                {/* Compose bar */}
                <div className="border-t border-slate-100 dark:border-slate-700 p-3 flex gap-2 bg-white dark:bg-slate-800">
                  {isTyping && (
                    <p className="w-full text-xs text-indigo-500 dark:text-indigo-400 px-1 pb-1">
                      typing…
                    </p>
                  )}
                  <textarea
                    rows={1}
                    value={msgText}
                    onChange={(e) => {
                      setMsgText(e.target.value);
                      sendTyping(!!e.target.value.trim());
                    }}
                    onBlur={() => sendTyping(false)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        if (msgText.trim()) sendMsg.mutate(msgText);
                      }
                    }}
                    placeholder="Type your reply…"
                    className="flex-1 resize-none rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500"
                  />
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => {
                      if (msgText.trim()) sendMsg.mutate(msgText);
                    }}
                    loading={sendMsg.isPending}
                    disabled={!msgText.trim()}
                    className="self-end"
                  >
                    <PaperAirplaneIcon className="h-4 w-4 mr-1.5" />
                    Send
                  </Button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
