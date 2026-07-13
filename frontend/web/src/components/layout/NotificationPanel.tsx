/**
 * NotificationPanel — slide-in notification drawer for the topbar bell icon
 */

import React from "react";
import { XMarkIcon, BellIcon, CheckIcon } from "@heroicons/react/24/outline";
import { useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import {
  useNotifications,
  useMarkNotificationRead,
} from "../../api/hooks";
import { QK } from "../../api/hooks";
import { useClickOutside } from "../../hooks";
import { SkeletonText } from "../common";
import clsx from "clsx";

interface NotificationPanelProps {
  open: boolean;
  onClose: () => void;
}

const CHANNEL_ICONS: Record<string, string> = {
  in_app: "🔔",
  email:  "📧",
  sms:    "📱",
  push:   "📲",
};

export default function NotificationPanel({ open, onClose }: NotificationPanelProps) {
  const qc = useQueryClient();
  const ref = useClickOutside<HTMLDivElement>(onClose);
  const { data, isLoading } = useNotifications();
  const markRead = useMarkNotificationRead();

  const notifications = data?.results ?? [];
  const unread = notifications.filter(n => !n.read_at);
  const hasUnread = unread.length > 0;

  const handleMarkAllRead = async () => {
    await Promise.all(unread.map(n => markRead.mutateAsync(n.id)));
    qc.invalidateQueries({ queryKey: QK.communication.unreadCount });
  };

  const handleMarkOne = (id: string) => {
    markRead.mutate(id);
  };

  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 z-40" onClick={onClose} />

      {/* Panel */}
      <div
        ref={ref}
        className={clsx(
          "fixed right-0 top-0 z-50 flex h-full w-full max-w-sm flex-col bg-white shadow-2xl",
          "border-l border-slate-200 transition-transform duration-300",
          open ? "translate-x-0" : "translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div className="flex items-center gap-3">
            <BellIcon className="h-5 w-5 text-slate-600" />
            <div>
              <h2 className="text-base font-bold text-slate-900">Notifications</h2>
              {hasUnread && (
                <p className="text-xs text-slate-500">{unread.length} unread</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {hasUnread && (
              <button
                onClick={handleMarkAllRead}
                className="flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-medium text-indigo-600 hover:bg-indigo-50 transition-colors"
              >
                <CheckIcon className="h-3.5 w-3.5" />
                Mark all read
              </button>
            )}
            <button
              onClick={onClose}
              className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="px-5 py-4 space-y-3">
              <SkeletonText lines={4} />
              <SkeletonText lines={3} />
              <SkeletonText lines={4} />
            </div>
          ) : notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-slate-400">
              <BellIcon className="h-12 w-12 mb-3 opacity-20" />
              <p className="text-sm font-medium text-slate-600">You&apos;re all caught up!</p>
              <p className="text-xs mt-1">No notifications right now</p>
            </div>
          ) : (
            <ul className="divide-y divide-slate-50">
              {notifications.map((notif) => {
                const isUnread = !notif.read_at;
                return (
                  <li
                    key={notif.id}
                    className={clsx(
                      "flex items-start gap-3 px-5 py-4 cursor-pointer transition-colors",
                      isUnread
                        ? "bg-indigo-50/50 hover:bg-indigo-50"
                        : "hover:bg-slate-50"
                    )}
                    onClick={() => isUnread && handleMarkOne(notif.id)}
                  >
                    {/* Icon */}
                    <div className={clsx(
                      "flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full text-base",
                      isUnread ? "bg-indigo-100" : "bg-slate-100"
                    )}>
                      {CHANNEL_ICONS[notif.channel] ?? "🔔"}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <p className={clsx(
                        "text-sm leading-snug",
                        isUnread ? "font-semibold text-slate-900" : "font-medium text-slate-700"
                      )}>
                        {notif.title}
                      </p>
                      <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">
                        {notif.body}
                      </p>
                      <p className="text-[11px] text-slate-400 mt-1.5">
                        {dayjs(notif.created_at).fromNow()}
                      </p>
                    </div>

                    {/* Unread dot */}
                    {isUnread && (
                      <div className="mt-1.5 h-2.5 w-2.5 flex-shrink-0 rounded-full bg-indigo-500" />
                    )}
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-slate-100 px-5 py-3">
          <p className="text-xs text-slate-400 text-center">
            Showing {notifications.length} of {data?.count ?? 0} notifications
          </p>
        </div>
      </div>
    </>
  );
}
