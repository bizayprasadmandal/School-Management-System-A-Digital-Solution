/**
 * UserMenuDropdown
 *
 * A topbar avatar dropdown showing user info, email verification status
 * (with inline resend action), and a sign-out button.
 *
 * Uses click-outside detection to auto-close.
 */

import React, { useState, useRef, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowRightOnRectangleIcon, UserIcon } from "@heroicons/react/24/outline";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { trackEvent } from "../../utils/analytics";
import toast from "react-hot-toast";

interface UserMenuDropdownProps {
  /** Path to the verify-email settings page for this role */
  verifyEmailPath?: string;
  /** Path to the profile/settings page for this role e.g. /admin/settings?tab=security */
  profilePath?: string;
  /** Tailwind accent color for the avatar initials badge (default: indigo) */
  accent?: "indigo" | "emerald" | "blue" | "violet";
}

const ACCENT_CLASSES: Record<string, string> = {
  indigo: "bg-indigo-600",
  emerald: "bg-emerald-600",
  blue: "bg-blue-600",
  violet: "bg-violet-600",
};

export default function UserMenuDropdown({ verifyEmailPath, profilePath, accent = "indigo" }: UserMenuDropdownProps) {
  const [open, setOpen] = useState(false);
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  // Don't render if user data hasn't loaded
  if (!user) return null;

  // Close on click outside
  useEffect(() => {
    if (!open) return;
    const handleClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick, true);
    return () => document.removeEventListener("mousedown", handleClick, true);
  }, [open]);

  const handleLogout = useCallback(() => {
    logout();
    navigate("/login");
  }, [logout, navigate]);

  const handleResend = async () => {
    setSending(true);
    try {
      await api.post<{ detail: string }>("/auth/send-verification/");
      trackEvent("verification_email_sent", { source: "user_menu_dropdown" });
      setSent(true);
      toast.success("Verification email sent!");
    } catch (err: unknown) {
      const error = err as { message?: string };
      toast.error(error?.message ?? "Failed to send verification email.");
    } finally {
      setSending(false);
    }
  };

  const isVerified = user?.email_verified ?? false;

  return (
    <div ref={menuRef} className="relative">
      {/* Trigger button */}
      <button
        data-testid="user-menu-trigger"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 rounded-lg p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
      >
        {user?.avatar ? (
          <img
            src={user.avatar}
            alt=""
            loading="lazy"
            className="h-8 w-8 rounded-full object-cover"
          />
        ) : (
          <div className={`flex h-8 w-8 items-center justify-center rounded-full ${ACCENT_CLASSES[accent]} text-white text-xs font-semibold`}>
            {user?.first_name?.[0] ?? "?"}
            {user?.last_name?.[0] ?? ""}
          </div>
        )}
        <span className="hidden md:block text-sm font-medium text-slate-700 dark:text-slate-300">
          {user?.first_name}
        </span>
      </button>

      {/* Dropdown — always rendered, animated via Tailwind transitions */}
      <div
        aria-hidden={!open}
        {...(!open ? { inert: "" } : {})}
        className={`absolute right-0 top-full mt-2 w-72 rounded-xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800 shadow-xl z-50 overflow-hidden transition-all duration-200 ease-out ${
          open
            ? "translate-y-0 opacity-100 pointer-events-auto"
            : "translate-y-1 opacity-0 pointer-events-none"
        }`}
      >
          {/* User info header */}
          <div className="px-4 pt-4 pb-3 border-b border-slate-100 dark:border-slate-700">
            <div className="flex items-center gap-3">
              {user?.avatar ? (
                <img
                  src={user.avatar}
                  alt=""
                  loading="lazy"
                  className="h-10 w-10 rounded-full object-cover"
                />
              ) : (
                <div className={`flex h-10 w-10 items-center justify-center rounded-full ${ACCENT_CLASSES[accent]} text-white font-semibold text-sm`}>
                  {user?.first_name?.[0] ?? "?"}
                  {user?.last_name?.[0] ?? ""}
                </div>
              )}
              <div className="min-w-0 flex-1">
                <p className="text-sm font-bold text-slate-900 dark:text-white truncate">
                  {user?.full_name}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                  {user?.email}
                </p>
              </div>
            </div>
            <p className="mt-1.5 text-[11px] uppercase tracking-wider text-slate-400 dark:text-slate-500 font-medium">
              {user?.role?.replace("_", " ")}
            </p>
          </div>

          {/* Email verification section */}
          <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                Email Verification
              </span>
              <span
                className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold ${
                  isVerified
                    ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400"
                    : "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400"
                }`}
              >
                <span
                  className={`h-1.5 w-1.5 rounded-full ${
                    isVerified ? "bg-green-500" : "bg-amber-500"
                  }`}
                />
                {isVerified ? "Verified" : "Not Verified"}
              </span>
            </div>

            {isVerified ? (
              <p className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1.5">
                <svg className="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
                Your email is verified.
              </p>
            ) : sent ? (
              <p className="text-xs text-green-600 dark:text-green-400 flex items-center gap-1.5">
                <svg className="h-3.5 w-3.5 shrink-0" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
                Verification email sent! Check your inbox.
              </p>
            ) : (
              <div className="space-y-2">
                <p className="text-xs text-amber-600 dark:text-amber-400">
                  Verify your email to unlock all features.
                </p>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    disabled={sending}
                    onClick={handleResend}
                    className="inline-flex items-center gap-1 rounded-lg bg-amber-100 dark:bg-amber-800/40 px-2.5 py-1.5 text-[11px] font-semibold text-amber-800 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-700/50 transition-colors disabled:opacity-50"
                  >
                    {sending ? (
                      <>
                        <svg className="h-3 w-3 animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                        Sending…
                      </>
                    ) : (
                      <>
                        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                        </svg>
                        Resend
                      </>
                    )}
                  </button>
                  {verifyEmailPath && (
                    <button
                      type="button"
                      onClick={() => { setOpen(false); navigate(verifyEmailPath); }}
                      className="text-[11px] font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 underline underline-offset-2"
                    >
                      Settings
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Footer actions */}
          <div className="px-2 py-2 space-y-0.5">
            {(profilePath || verifyEmailPath) && (
              <button
                onClick={() => { setOpen(false); navigate(profilePath ?? verifyEmailPath!); }}
                className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 hover:text-indigo-700 dark:hover:text-indigo-400 transition-colors"
              >
                <UserIcon className="h-4 w-4" />
                View Profile
              </button>
            )}
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-700 dark:hover:text-red-400 transition-colors"
            >
              <ArrowRightOnRectangleIcon className="h-4 w-4" />
              Sign out
            </button>
          </div>
        </div>
    </div>
  );
}
