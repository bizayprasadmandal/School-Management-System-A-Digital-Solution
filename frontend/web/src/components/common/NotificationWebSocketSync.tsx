/**
 * NotificationWebSocketSync
 *
 * Connects the notification WebSocket to the React Query cache so that
 * new notifications pushed from the backend appear instantly in the
 * notification panel and bell badge, without waiting for the polling
 * interval (30s for count, 60s for list).
 *
 * Also shows a live toast when a new notification arrives so the user
 * knows about it immediately, even if the panel is closed.
 *
 * This component renders nothing — it only manages side effects.
 * It should be mounted once inside <QueryClientProvider>.
 */

import { useEffect, useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { useNotificationSocket } from "../../hooks";
import { QK } from "../../api/hooks";
import { useAuthStore } from "../../store/authStore";
import { useUIStore } from "../../store/uiStore";
import type { WSStatus } from "../../store/uiStore";

export default function NotificationWebSocketSync() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const qc = useQueryClient();
  const setWsStatus = useUIStore((s) => s.setWsStatus);

  const handleNewNotification = useCallback((
    notif: { id: string; title: string; body: string; created_at: string; read_at: string | null }
  ) => {
    // Invalidate queries so the panel and badge update immediately
    qc.invalidateQueries({ queryKey: QK.communication.notifications });
    qc.invalidateQueries({ queryKey: QK.communication.unreadCount });

    // Determine if this is an email-verification notification by keywords
    const isVerification =
      notif.title.toLowerCase().includes("email") ||
      notif.title.toLowerCase().includes("verif");

    // Show a live toast with the notification title
    toast(
      (t) => (
        <div className="flex items-start gap-3 w-72">
          {/* Icon */}
          <div
            className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-sm ${
              isVerification
                ? "bg-amber-100 text-amber-600"
                : "bg-indigo-100 text-indigo-600"
            }`}
          >
            {isVerification ? "📧" : "🔔"}
          </div>

          {/* Content */}
          <div className="min-w-0 flex-1">
            <p
              className={`text-sm font-semibold leading-snug ${
                isVerification ? "text-amber-900" : "text-slate-900"
              }`}
            >
              {notif.title}
            </p>
            {notif.body && (
              <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">
                {notif.body}
              </p>
            )}
          </div>

          {/* Dismiss */}
          <button
            onClick={() => toast.dismiss(t.id)}
            className="flex-shrink-0 rounded p-0.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ),
      {
        duration: isVerification ? 8000 : 5000,
        position: "bottom-right",
      }
    );
  }, [qc]);

  const { unreadCount, status } = useNotificationSocket(handleNewNotification);

  // Sync the WebSocket connection status to the UI store so the bell can
  // display a live indicator dot.
  useEffect(() => {
    setWsStatus(status as WSStatus);
  }, [status, setWsStatus]);

  // When the WebSocket pushes an unread_count update that differs from
  // what React Query has cached, update the cache directly for zero-delay
  // badge updates.  This handles unread_count messages sent on connect
  // and when another device marks a notification as read.
  useEffect(() => {
    if (!isAuthenticated) return;

    qc.setQueryData(QK.communication.unreadCount, unreadCount);
  }, [unreadCount, isAuthenticated, qc]);

  return null;
}
