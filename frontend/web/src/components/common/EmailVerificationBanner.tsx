/**
 * EmailVerificationBanner
 *
 * Shows an amber warning banner on dashboard pages when the authenticated
 * user's email has not been verified.  Includes a "Resend verification email"
 * button that calls POST /auth/send-verification/.
 *
 * The banner can be dismissed by the user and won't reappear until the
 * page is reloaded or they navigate to a different route.
 */

import React, { useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { useUIStore } from "../../store/uiStore";
import { api } from "../../api/client";
import { trackEvent } from "../../utils/analytics";
import toast from "react-hot-toast";

export default function EmailVerificationBanner() {
  const user = useAuthStore((s) => s.user);
  const dismissed = useUIStore((s) => s.bannerDismissed);
  const dismissBanner = useUIStore((s) => s.dismissBanner);
  const [sending, setSending] = useState(false);

  // Don't render if email is verified, user isn't loaded, or dismissed
  if (!user || user.email_verified || dismissed) return null;

  const handleResend = async () => {
    setSending(true);
    try {
      await api.post<{ detail: string }>("/auth/send-verification/");
      trackEvent("verification_email_sent", { source: "dashboard_banner" });
      toast.success("Verification email sent! Check your inbox.");
    } catch (err: unknown) {
      const error = err as { message?: string };
      toast.error(error?.message ?? "Failed to send verification email.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 dark:border-amber-800/40 dark:bg-amber-900/20 px-4 py-3">
      <div className="flex items-start gap-3">
        {/* Warning icon */}
        <svg
          className="mt-0.5 h-5 w-5 shrink-0 text-amber-500"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
          />
        </svg>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-semibold text-amber-800 dark:text-amber-300">
              Email not verified
            </p>
            <button
              type="button"
              onClick={() => dismissBanner()}
              className="shrink-0 rounded p-0.5 text-amber-400 hover:text-amber-600 dark:hover:text-amber-200 transition-colors"
              aria-label="Dismiss"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="text-xs text-amber-700 dark:text-amber-400 mt-0.5">
            Some features are restricted until you verify your email address.
          </p>

          {/* Actions */}
          <div className="mt-2.5 flex flex-wrap items-center gap-2">
            <button
              type="button"
              disabled={sending}
              onClick={handleResend}
              className="inline-flex items-center gap-1.5 rounded-lg bg-amber-100 dark:bg-amber-800/40 px-3 py-1.5 text-xs font-semibold text-amber-800 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-700/50 transition-colors disabled:opacity-50"
            >
              {sending ? (
                <>
                  <svg className="h-3.5 w-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Sending…
                </>
              ) : (
                <>
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                  </svg>
                  Resend verification email
                </>
              )}
            </button>
            <button
              type="button"
              onClick={() => dismissBanner()}
              className="text-xs text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 underline underline-offset-2"
            >
              Remind me later
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
