/**
 * NotificationBell — shared topbar bell icon with dual badge.
 *
 * Primary badge (red, top-right): total unread notification count.
 * Secondary badge (amber, bottom-right): unread email-verification count,
 * shown with a small envelope icon so users can see "2 email-related" at a glance.
 */

import React from "react";
import { BellIcon } from "@heroicons/react/24/outline";
import { useUnreadNotificationCount, useUnreadVerificationCount } from "../../api/hooks";
import { useUIStore, type WSStatus } from "../../store/uiStore";

interface NotificationBellProps {
  onClick: () => void;
}

/** Colour / tooltip mapping for each WebSocket status */
const WS_DOT: Record<WSStatus, { bg: string; pulse: string; title: string }> = {
  connected:    { bg: "bg-green-500",  pulse: "shadow-[0_0_4px_rgba(34,197,94,0.6)]",  title: "Connected" },
  connecting:   { bg: "bg-yellow-400", pulse: "animate-pulse",                         title: "Reconnecting…" },
  disconnected: { bg: "bg-red-400",    pulse: "",                                      title: "Disconnected" },
  error:        { bg: "bg-red-500",    pulse: "animate-pulse",                         title: "Connection error" },
};

export default function NotificationBell({ onClick }: NotificationBellProps) {
  const { data: unreadCount = 0 } = useUnreadNotificationCount();
  const verificationCount = useUnreadVerificationCount();
  const wsStatus = useUIStore((s) => s.wsStatus);

  const dot = WS_DOT[wsStatus];
  const isConnected = wsStatus === "connected";

  return (
    <button
      className={`relative rounded-lg p-2 transition-colors ${
        isConnected
          ? "text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white"
          : "text-slate-400 dark:text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700"
      }`}
      onClick={onClick}
      aria-label={`Notifications${unreadCount > 0 ? `, ${unreadCount} unread` : ""}${verificationCount > 0 ? `, ${verificationCount} email-related` : ""} — WebSocket ${dot.title.toLowerCase()}`}
    >
      <BellIcon className="h-5 w-5" />

      {/* WebSocket status dot (top-left) */}
      <span
        className={`absolute -top-0.5 -left-0.5 h-2 w-2 rounded-full ${dot.bg} ${dot.pulse} ring-1 ring-white dark:ring-slate-800 transition-colors duration-300`}
        title={dot.title}
      />

      {/* Total unread badge (red) */}
      {unreadCount > 0 && (
        <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white shadow-sm">
          {unreadCount > 9 ? "9+" : unreadCount}
        </span>
      )}

      {/* Verification-unread badge (amber) */}
      {verificationCount > 0 && (
        <span
          className="absolute -bottom-0.5 -right-0.5 flex h-3.5 min-w-[14px] items-center justify-center gap-[1px] rounded-full bg-amber-400 px-[3px] text-[8px] font-bold text-white shadow-sm"
          title={`${verificationCount} email-related notification${verificationCount !== 1 ? "s" : ""}`}
        >
          {/* Tiny envelope icon */}
          <svg className="h-2 w-2" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
          </svg>
          {verificationCount > 9 ? "9+" : verificationCount}
        </span>
      )}
    </button>
  );
}
