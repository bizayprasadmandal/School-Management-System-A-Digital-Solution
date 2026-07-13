/**
 * NotificationPanel — slide-in notification drawer for the topbar bell icon
 */

import React, { memo } from "react";
import { useNavigate } from "react-router-dom";
import { XMarkIcon, BellIcon, CheckIcon } from "@heroicons/react/24/outline";
import { useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import {
  useNotifications,
  useMarkNotificationRead,
} from "../../api/hooks";
import { QK } from "../../api/hooks";
import { useClickOutside } from "../../hooks";
import { VERIFICATION_REF } from "../../types";
import { useAuthStore } from "../../store/authStore";
import { useUIStore } from "../../store/uiStore";
import { SkeletonText } from "../common";
import clsx from "clsx";

interface NotificationPanelProps {
  open: boolean;
  onClose: () => void;
}

const ROLE_VERIFY_PATHS: Record<string, string> = {
  super_admin: "/admin/verify-email",
  school_admin: "/admin/verify-email",
  accountant: "/admin/verify-email",
  teacher: "/teacher/verify-email",
  student: "/student/verify-email",
  parent: "/parent/verify-email",
};

const CHANNEL_ICONS: Record<string, string> = {
  in_app: "🔔",
  email:  "📧",
  sms:    "📱",
  push:   "📲",
};

export default memo(function NotificationPanel({ open, onClose }: NotificationPanelProps) {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const ref = useClickOutside<HTMLDivElement>(onClose);
  const { data, isLoading } = useNotifications();
  const markRead = useMarkNotificationRead();
  const user = useAuthStore((s) => s.user);
  const dismissBanner = useUIStore((s) => s.dismissBanner);

  const verifyPath = ROLE_VERIFY_PATHS[user?.role ?? ""] ?? "/admin/verify-email";

  const notifications = data?.results ?? [];
  const unread = notifications.filter(n => !n.read_at);
  const unreadVerification = unread.filter(n => n.reference_type === VERIFICATION_REF);
  const hasUnread = unread.length > 0;
  const hasUnreadVerification = unreadVerification.length > 0;

  const handleMarkAllRead = async () => {
    await Promise.all(unread.map(n => markRead.mutateAsync(n.id)));
    qc.invalidateQueries({ queryKey: QK.communication.unreadCount });
    dismissBanner();
  };

  const handleDismissVerifications = async () => {
    await Promise.all(unreadVerification.map(n => markRead.mutateAsync(n.id)));
    qc.invalidateQueries({ queryKey: QK.communication.unreadCount });
    dismissBanner();
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
            {hasUnreadVerification && (
              <button
                onClick={handleDismissVerifications}
                className="flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-medium text-amber-700 hover:bg-amber-50 dark:hover:bg-amber-900/20 transition-colors"
              >
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                </svg>
                {unreadVerification.length} email
              </button>
            )}
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
                const isVerification = notif.reference_type === VERIFICATION_REF;

                return (
                  <li
                    key={notif.id}
                    className={clsx(
                      "flex items-start gap-3 px-5 py-4 transition-colors",
                      isVerification ? [
                        "border-l-2",
                        isUnread
                          ? "border-l-amber-400 bg-amber-50/70 hover:bg-amber-50"
                          : "border-l-amber-200 hover:bg-slate-50",
                      ] : [
                        "cursor-pointer",
                        isUnread
                          ? "bg-indigo-50/50 hover:bg-indigo-50"
                          : "hover:bg-slate-50",
                      ]
                    )}
                    onClick={() => {
                      if (isUnread && !isVerification) {
                        handleMarkOne(notif.id);
                      }
                    }}
                  >
                    {/* Icon */}
                    <div className={clsx(
                      "flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full text-base",
                      isVerification
                        ? "bg-amber-100"
                        : isUnread ? "bg-indigo-100" : "bg-slate-100"
                    )}>
                      {isVerification ? "📧" : (CHANNEL_ICONS[notif.channel] ?? "🔔")}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <p className={clsx(
                        "text-sm leading-snug",
                        isUnread ? "font-semibold text-slate-900" : "font-medium text-slate-700",
                        isVerification && "text-amber-900 dark:text-amber-200"
                      )}>
                        {notif.title}
                      </p>
                      <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">
                        {notif.body}
                      </p>
                      <p className="text-[11px] text-slate-400 mt-1.5">
                        {dayjs(notif.created_at).fromNow()}
                      </p>

                      {/* Verification actions */}
                      {isVerification && isUnread && (
                        <div className="mt-2 flex items-center gap-2">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleMarkOne(notif.id);
                              dismissBanner();
                            }}
                            className="inline-flex items-center gap-1 rounded-md bg-amber-100 dark:bg-amber-800/40 px-2.5 py-1 text-[11px] font-semibold text-amber-800 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-700/50 transition-colors"
                          >
                            <CheckIcon className="h-3 w-3" />
                            Mark as read
                          </button>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              onClose();
                              navigate(verifyPath);
                            }}
                            className="text-[11px] font-medium text-amber-700 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-300 underline underline-offset-2 transition-colors"
                          >
                            Verify now
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Unread dot */}
                    {isUnread && (
                      <div className={clsx(
                        "mt-1.5 h-2.5 w-2.5 flex-shrink-0 rounded-full",
                        isVerification ? "bg-amber-500" : "bg-indigo-500"
                      )} />
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
});
