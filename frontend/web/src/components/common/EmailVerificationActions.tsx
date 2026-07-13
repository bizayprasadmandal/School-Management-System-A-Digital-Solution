/**
 * EmailVerificationActions
 *
 * Small inline component for the settings page Security tab.
 * Shows a "Send verification email" button (or "Email sent!"
 * feedback) and handles the API call + toast notifications.
 *
 * Reads `email_verified` from the auth store directly so it
 * stays reactive if the user completes verification elsewhere.
 */

import React, { useState, useCallback } from "react";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { trackEvent } from "../../utils/analytics";
import toast from "react-hot-toast";

export default function EmailVerificationActions() {
  const emailVerified = useAuthStore((s) => s.user?.email_verified ?? false);
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  const handleSend = useCallback(async () => {
    setSending(true);
    try {
      await api.post<{ detail: string }>("/auth/send-verification/");
      trackEvent("verification_email_sent", { source: "settings_security_tab" });
      setSent(true);
      toast.success("Verification email sent! Check your inbox.");
    } catch (err: unknown) {
      const error = err as { message?: string };
      toast.error(error?.message ?? "Failed to send verification email.");
    } finally {
      setSending(false);
    }
  }, []);

  // Already verified — nothing actionable
  if (emailVerified) {
    return null;
  }

  // Success feedback after sending
  if (sent) {
    return (
      <div className="text-right">
        <span className="inline-flex items-center gap-1.5 rounded-lg bg-green-50 dark:bg-green-900/20 px-3 py-1.5 text-xs font-medium text-green-700 dark:text-green-400">
          <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
          Email sent!
        </span>
        <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-1">
          Check your inbox (and spam folder)
        </p>
      </div>
    );
  }

  // Send button
  return (
    <button
      type="button"
      disabled={sending}
      onClick={handleSend}
      className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-semibold text-white hover:bg-indigo-500 transition-colors disabled:opacity-50"
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
          Send verification email
        </>
      )}
    </button>
  );
}
