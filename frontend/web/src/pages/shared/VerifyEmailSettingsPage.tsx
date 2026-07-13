/**
 * VerifyEmailSettingsPage
 *
 * An in-app page (not the public token-based one) where authenticated users
 * can check their email verification status and send a new verification link.
 *
 * Routed as /{role}/verify-email inside each layout shell.
 */

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ShieldCheckIcon,
  KeyIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { EnvelopeIcon } from "@heroicons/react/24/solid";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { trackEvent } from "../../utils/analytics";
import toast from "react-hot-toast";
import clsx from "clsx";

export default function VerifyEmailSettingsPage() {
  const user = useAuthStore((s) => s.user);
  const navigate = useNavigate();
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  const isVerified = user?.email_verified ?? false;
  const email = user?.email ?? "";
  const is2FAEnabled = user?.two_factor_enabled ?? false;
  const remaining = user?.backup_codes_remaining ?? null;

  const handleSend = async () => {
    setSending(true);
    try {
      await api.post<{ detail: string }>("/auth/send-verification/");
      trackEvent("verification_email_sent", { source: "verify_email_settings_page" });
      setSent(true);
      toast.success("Verification email sent!");
    } catch (err: unknown) {
      const error = err as { message?: string };
      toast.error(error?.message ?? "Failed to send verification email.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl">
      {/* Page heading */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Email Verification
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Manage your email verification status
        </p>
      </div>

      {/* Status card */}
      <div className="rounded-xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800 shadow-sm">
        <div className="p-6">
          <div className="flex items-start gap-4">
            {/* Icon */}
            <div
              className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl ${
                isVerified
                  ? "bg-green-100 dark:bg-green-900/30"
                  : "bg-amber-100 dark:bg-amber-900/30"
              }`}
            >
              {isVerified ? (
                <svg
                  className="h-7 w-7 text-green-600 dark:text-green-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              ) : (
                <svg
                  className="h-7 w-7 text-amber-600 dark:text-amber-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
                  />
                </svg>
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-3">
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                  {isVerified ? "Email verified" : "Email not verified"}
                </h2>
                <span
                  className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
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
                  {isVerified ? "Verified" : "Unverified"}
                </span>
              </div>

              {/* Email display */}
              <div className="mt-3 flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                <EnvelopeIcon className="h-4 w-4" />
                <span className="font-mono">{email}</span>
              </div>

              {/* Description */}
              <p className="mt-3 text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
                {isVerified
                  ? "Your email address has been confirmed. You have full access to all features including notifications, password recovery, and account communications."
                  : "Your email address has not been verified yet. Some features may be restricted until you confirm your email. A verification link was sent when your account was created."}
              </p>
            </div>
          </div>
        </div>

        {/* Action bar */}
        <div className="border-t border-slate-100 dark:border-slate-700 px-6 py-4">
          {isVerified ? (
            <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
              <svg
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="font-medium">All good — your email is verified.</span>
            </div>
          ) : sent ? (
            <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
              <svg
                className="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M4.5 12.75l6 6 9-13.5"
                />
              </svg>
              <span className="font-medium">
                Verification email sent! Check your inbox (and spam folder).
              </span>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Click the button to receive a new verification link.
              </p>
              <button
                type="button"
                disabled={sending}
                onClick={handleSend}
                className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 active:bg-indigo-700 transition-all duration-150 disabled:opacity-50"
              >
                {sending ? (
                  <>
                    <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Sending…
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                    </svg>
                    Send verification email
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* ── Security card: 2FA & backup codes ─────────────────────────────── */}
      <div className="mt-6 rounded-xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800 shadow-sm">
        <div className="p-6">
          <div className="flex items-start gap-4">
            {/* Icon */}
            <div
              className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl ${
                is2FAEnabled
                  ? "bg-green-100 dark:bg-green-900/30"
                  : "bg-slate-100 dark:bg-slate-700"
              }`}
            >
              <ShieldCheckIcon
                className={`h-7 w-7 ${
                  is2FAEnabled
                    ? "text-green-600 dark:text-green-400"
                    : "text-slate-400 dark:text-slate-500"
                }`}
              />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-center gap-3">
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                  Two-Factor Authentication
                </h2>
                <span
                  className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                    is2FAEnabled
                      ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400"
                      : "bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-400"
                  }`}
                >
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      is2FAEnabled ? "bg-green-500" : "bg-slate-400"
                    }`}
                  />
                  {is2FAEnabled ? "Enabled" : "Not configured"}
                </span>
              </div>

              <p className="mt-3 text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
                {is2FAEnabled
                  ? "Your account is protected with two-factor authentication. In addition to your password, you'll need a one-time code from your authenticator app or a backup code to sign in."
                  : "Add an extra layer of security to your account by enabling two-factor authentication."}
              </p>

              {/* Backup codes remaining (only when 2FA enabled) */}
              {is2FAEnabled && remaining !== null && remaining <= 5 && (
                <div
                  className={clsx(
                    "mt-4 rounded-lg border px-4 py-3",
                    remaining <= 2
                      ? "border-red-200 bg-red-50 dark:border-red-800/40 dark:bg-red-900/20"
                      : "border-amber-200 bg-amber-50 dark:border-amber-800/40 dark:bg-amber-900/20"
                  )}
                >
                  <div className="flex items-start gap-2.5">
                    <ExclamationTriangleIcon
                      className={`h-5 w-5 shrink-0 mt-0.5 ${
                        remaining <= 2
                          ? "text-red-500 dark:text-red-400"
                          : "text-amber-500 dark:text-amber-400"
                      }`}
                    />
                    <div className="flex-1">
                      <p
                        className={`text-sm font-semibold ${
                          remaining <= 2
                            ? "text-red-800 dark:text-red-300"
                            : "text-amber-800 dark:text-amber-300"
                        }`}
                      >
                        {remaining} of 8 backup codes remaining
                      </p>
                      <p
                        className={`text-xs mt-0.5 ${
                          remaining <= 2
                            ? "text-red-700 dark:text-red-400"
                            : "text-amber-700 dark:text-amber-400"
                        }`}
                      >
                        {remaining === 0
                          ? "You have no backup codes left. Generate new ones immediately."
                          : remaining <= 2
                            ? "You're running low on backup codes. Generate new ones soon."
                            : "Consider generating new backup codes to ensure you always have a recovery option."}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {is2FAEnabled && remaining !== null && remaining > 5 && (
                <p className="mt-3 text-xs text-green-600 dark:text-green-400 flex items-center gap-1.5">
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {remaining} of 8 backup codes remaining
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Action bar */}
        <div className="border-t border-slate-100 dark:border-slate-700 px-6 py-4">
          <button
            type="button"
            onClick={() => navigate("../setup-2fa")}
            className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 active:bg-indigo-700 transition-all duration-150"
          >
            <KeyIcon className="h-4 w-4" />
            {is2FAEnabled ? "Manage two-factor authentication" : "Set up two-factor authentication"}
          </button>
        </div>
      </div>

      {/* Info cards */}
      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800 p-5 shadow-sm">
          <div className="flex items-center gap-2.5 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30">
              <svg className="h-4 w-4 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Why verify?</h3>
          </div>
          <ul className="space-y-1.5 text-xs text-slate-500 dark:text-slate-400">
            <li className="flex items-start gap-1.5">
              <span className="mt-0.5 text-green-500">✓</span>
              Receive important notifications
            </li>
            <li className="flex items-start gap-1.5">
              <span className="mt-0.5 text-green-500">✓</span>
              Reset your password if forgotten
            </li>
            <li className="flex items-start gap-1.5">
              <span className="mt-0.5 text-green-500">✓</span>
              Get communication from the school
            </li>
          </ul>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800 p-5 shadow-sm">
          <div className="flex items-center gap-2.5 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/30">
              <svg className="h-4 w-4 text-amber-600 dark:text-amber-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">What happens next?</h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            Once you click the link in the verification email, your status will update
            automatically and you'll gain access to all features. The link expires in 24 hours.
          </p>
        </div>
      </div>

      {/* Link to settings */}
      <div className="mt-6 text-center">
        <Link
          to=".."
          className="text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 transition-colors"
        >
          ← Back to dashboard
        </Link>
      </div>
    </div>
  );
}
