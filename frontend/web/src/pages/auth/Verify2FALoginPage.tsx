/**
 * Verify2FALoginPage
 *
 * The second step of the login flow when a user has 2FA enabled.
 * They've already entered their email + password, and now need to
 * provide either:
 *   - A 6-digit TOTP code from their authenticator app
 *   - A backup code (XXXXX-XXXXX format)
 *
 * On success, JWT tokens are stored and the user is redirected
 * to their role-appropriate dashboard.
 */

import React, { useState, useCallback, useRef, useEffect } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import {
  ShieldCheckIcon,
  KeyIcon,
  ArrowPathIcon,
  AcademicCapIcon,
  ExclamationTriangleIcon,
  ArrowLeftIcon,
} from "@heroicons/react/24/outline";
import { useAuthStore } from "../../store/authStore";
import { useQueryClient } from "@tanstack/react-query";
import { api, type NormalizedError } from "../../api/client";
import { QK } from "../../api/hooks";
import { trackEvent } from "../../utils/analytics";
import toast from "react-hot-toast";
import clsx from "clsx";
import type { User, AuthTokens } from "../../types";

// ─── Constants ────────────────────────────────────────────────────────────────

const ROLE_ROUTES: Record<string, string> = {
  super_admin:  "/admin",
  school_admin: "/admin",
  accountant:   "/admin",
  teacher:      "/teacher",
  student:      "/student",
  parent:       "/parent",
  librarian:    "/admin",
  counselor:    "/admin",
};

type AuthMode = "totp" | "backup";

interface Verify2FALocationState {
  user_id: string;
  email: string;
  backup_codes_remaining?: number;
}

import { getLockoutInfo, type LockoutInfo } from "../../utils/lockoutInfo";

// ─── Component ────────────────────────────────────────────────────────────────

export default function Verify2FALoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();
  const { setAuth } = useAuthStore();

  // Read user_id and email from location state (passed from LoginPage)
  const locationState = location.state as Verify2FALocationState | null;
  const userId = locationState?.user_id ?? "";
  const userEmail = locationState?.email ?? "";
  const backupCodesRemaining = locationState?.backup_codes_remaining;

  const [authMode, setAuthMode] = useState<AuthMode>("totp");
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [backupCode, setBackupCode] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [lockoutInfo, setLockoutInfo] = useState<LockoutInfo>(null);

  const codeInputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const backupInputRef = useRef<HTMLInputElement>(null);

  // ── Redirect if no user_id (direct URL access) ──────────────────────────

  useEffect(() => {
    if (!userId) {
      navigate("/login", { replace: true });
    }
  }, [userId, navigate]);

  // ── Verify TOTP code ─────────────────────────────────────────────────────

  const handleTOTPVerify = useCallback(async () => {
    const fullCode = code.join("");
    if (fullCode.length !== 6) {
      toast.error("Please enter the complete 6-digit code.");
      return;
    }

    setIsSubmitting(true);
    setErrorMsg("");
    setLockoutInfo(null);

    try {
      const response = await api.post<{
        access: string;
        refresh: string;
        user: User;
      }>("/auth/verify-2fa-login/", {
        user_id: userId,
        code: fullCode,
      });

      _completeLogin(response);
    } catch (err: unknown) {
      const error = err as NormalizedError;
      const msg = error?.message ?? "Invalid code. Please try again.";

      // Detect backup-code lockout/attempts — can trigger from TOTP tab too
      // since an invalid TOTP code falls through to backup code check on the backend
      const lockout = getLockoutInfo(error);
      if (lockout) {
        setLockoutInfo(lockout);
        toast.error(msg, { duration: 8000 });
      } else {
        toast.error(msg);
      }

      setErrorMsg(msg);
      setCode(["", "", "", "", "", ""]);
      codeInputRefs.current[0]?.focus();
    } finally {
      setIsSubmitting(false);
    }
  }, [code, userId]);

  // ── Verify backup code ───────────────────────────────────────────────────

  const handleBackupVerify = useCallback(async () => {
    const trimmed = backupCode.trim().toUpperCase();
    if (!trimmed) {
      toast.error("Please enter your backup code.");
      return;
    }

    setIsSubmitting(true);
    setErrorMsg("");
    setLockoutInfo(null);

    try {
      const response = await api.post<{
        access: string;
        refresh: string;
        user: User;
      }>("/auth/verify-2fa-login/", {
        user_id: userId,
        code: trimmed,
      });

      _completeLogin(response);
    } catch (err: unknown) {
      const error = err as NormalizedError;
      const msg = error?.message ?? "Invalid backup code.";

      // Detect lockout (429) vs. remaining attempts (400)
      const lockout = getLockoutInfo(error);
      if (lockout) {
        setLockoutInfo(lockout);
      }

      setErrorMsg(msg);
      setBackupCode("");
      backupInputRef.current?.focus();
      toast.error(msg, lockout?.type === "lockout" ? { duration: 8000 } : undefined);
    } finally {
      setIsSubmitting(false);
    }
  }, [backupCode, userId]);

  // ── Complete login after successful 2FA verification ────────────────────

  const _completeLogin = useCallback(
    (response: { access: string; refresh: string; user: User }) => {
      setAuth(response.user, {
        access: response.access,
        refresh: response.refresh,
      });

      queryClient.invalidateQueries({ queryKey: QK.communication.notifications });
      queryClient.invalidateQueries({ queryKey: QK.communication.unreadCount });

      const route = ROLE_ROUTES[response.user.role] ?? "/login";
      trackEvent("2fa_login_completed", { role: response.user.role });
      toast.success(`Welcome back, ${response.user.first_name}!`);
      navigate(route, { replace: true });
    },
    [setAuth, navigate, queryClient]
  );

  // ── TOTP code input handlers ────────────────────────────────────────────

  const handleCodeChange = (index: number, value: string) => {
    if (value && !/^\d$/.test(value)) return;
    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);
    if (value && index < 5) {
      codeInputRefs.current[index + 1]?.focus();
    }
  };

  const handleCodeKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !code[index] && index > 0) {
      codeInputRefs.current[index - 1]?.focus();
    }
    if (e.key === "Enter") {
      handleTOTPVerify();
    }
  };

  const handleCodePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    const newCode = pasted.split("").concat(Array(6).fill("")).slice(0, 6);
    setCode(newCode);
    const nextEmpty = newCode.findIndex((c) => !c);
    codeInputRefs.current[nextEmpty >= 0 ? nextEmpty : 5]?.focus();
  };

  // ── Switch mode ─────────────────────────────────────────────────────────

  const switchToTOTP = () => {
    setAuthMode("totp");
    setErrorMsg("");
    setLockoutInfo(null);
    setCode(["", "", "", "", "", ""]);
    setTimeout(() => codeInputRefs.current[0]?.focus(), 100);
  };

  const switchToBackup = () => {
    setAuthMode("backup");
    setErrorMsg("");
    setLockoutInfo(null);
    setBackupCode("");
    setTimeout(() => backupInputRef.current?.focus(), 100);
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-indigo-900 to-violet-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-white/10 backdrop-blur mb-4">
            <AcademicCapIcon className="h-9 w-9 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">EduSphere</h1>
          <p className="mt-1.5 text-indigo-300 text-sm">School Management System</p>
        </div>

        {/* Card */}
        <div className="rounded-2xl bg-white dark:bg-slate-800 p-8 shadow-2xl dark:shadow-none">
          {/* Back button */}
          <Link
            to="/login"
            className="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors mb-4"
          >
            <ArrowLeftIcon className="h-3.5 w-3.5" />
            Back to sign in
          </Link>

          {/* Icon */}
          <div className="flex justify-center mb-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-100 dark:bg-indigo-900/30">
              <ShieldCheckIcon className="h-7 w-7 text-indigo-600 dark:text-indigo-400" />
            </div>
          </div>

          <h2 className="text-xl font-bold text-slate-900 dark:text-white text-center mb-1">
            Two-factor authentication
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 text-center mb-6">
            {userEmail ? (
              <>Enter the verification code for <span className="font-medium text-slate-700 dark:text-slate-300">{userEmail}</span></>
            ) : (
              "Enter your verification code"
            )}
          </p>

          {/* ── Mode tabs ──────────────────────────────────── */}
          <div className="flex rounded-xl bg-slate-100 dark:bg-slate-700 p-1 mb-6">
            <button
              type="button"
              onClick={switchToTOTP}
              className={clsx(
                "flex-1 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-150",
                authMode === "totp"
                  ? "bg-white dark:bg-slate-600 text-slate-900 dark:text-white shadow-sm"
                  : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
              )}
            >
              Authenticator app
            </button>
            <button
              type="button"
              onClick={switchToBackup}
              className={clsx(
                "flex-1 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-150",
                authMode === "backup"
                  ? "bg-white dark:bg-slate-600 text-slate-900 dark:text-white shadow-sm"
                  : "text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300"
              )}
            >
              Backup code
            </button>
          </div>

          {/* ── Lockout or attempts-remaining warning (visible on both tabs) ── */}
          {lockoutInfo && (
            <div
              className={clsx(
                "rounded-xl border px-4 py-3 mb-4",
                lockoutInfo.type === "lockout"
                  ? "bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-800/40"
                  : "bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-700/50"
              )}
            >
              <div className="flex items-start gap-2.5">
                <ExclamationTriangleIcon
                  className={clsx(
                    "h-5 w-5 shrink-0 mt-0.5",
                    lockoutInfo.type === "lockout"
                      ? "text-red-500 dark:text-red-400"
                      : "text-amber-500 dark:text-amber-400"
                  )}
                />
                <div className="flex-1 min-w-0">
                  <p
                    className={clsx(
                      "text-sm font-semibold",
                      lockoutInfo.type === "lockout"
                        ? "text-red-800 dark:text-red-300"
                        : "text-amber-800 dark:text-amber-300"
                    )}
                  >
                    {lockoutInfo.type === "lockout"
                      ? "Access temporarily locked"
                      : `Warning: ${lockoutInfo.remaining} attempt${lockoutInfo.remaining === 1 ? "" : "s"} remaining`}
                  </p>
                  <p
                    className={clsx(
                      "text-xs mt-1",
                      lockoutInfo.type === "lockout"
                        ? "text-red-700 dark:text-red-400/80"
                        : "text-amber-700 dark:text-amber-400/80"
                    )}
                  >
                    {lockoutInfo.message}
                  </p>
                  {lockoutInfo.type === "lockout" && (
                    <p className="text-xs mt-1.5 text-red-700 dark:text-red-400/80">
                      You can still sign in using your authenticator app.
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ── TOTP Mode ──────────────────────────────────── */}
          {authMode === "totp" && (
            <div>
              <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 text-center mb-4">
                Enter the 6-digit code from your authenticator app
              </label>

              <div className="flex items-center justify-center gap-2">
                {code.map((digit, i) => (
                  <input
                    key={i}
                    ref={(el) => { codeInputRefs.current[i] = el; }}
                    type="text"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleCodeChange(i, e.target.value)}
                    onKeyDown={(e) => handleCodeKeyDown(i, e)}
                    onPaste={i === 0 ? handleCodePaste : undefined}
                    disabled={isSubmitting}
                    className={clsx(
                      "h-14 w-11 rounded-xl border text-center text-xl font-bold transition-all duration-100 focus:outline-none focus:ring-2",
                      errorMsg
                        ? "border-red-300 focus:ring-red-400"
                        : "border-slate-300 dark:border-slate-600 focus:ring-indigo-500 focus:border-indigo-400",
                      digit ? "border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20" : ""
                    )}
                    aria-label={`Digit ${i + 1}`}
                  />
                ))}
              </div>

              {errorMsg && (
                <p className="mt-3 text-center text-xs text-red-600 dark:text-red-400 flex items-center justify-center gap-1">
                  <ExclamationTriangleIcon className="h-3.5 w-3.5" />
                  {errorMsg}
                </p>
              )}

              <button
                type="button"
                disabled={isSubmitting || code.join("").length !== 6}
                onClick={handleTOTPVerify}
                className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 active:bg-indigo-700 transition-all duration-150 disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Verifying…
                  </>
                ) : (
                  <>
                    <KeyIcon className="h-4 w-4" />
                    Verify &amp; Sign In
                  </>
                )}
              </button>
            </div>
          )}

          {/* ── Backup Code Mode ───────────────────────────── */}
          {authMode === "backup" && (
            <div>
              {/* Backup codes remaining indicator */}
              {backupCodesRemaining !== undefined && backupCodesRemaining !== null && (
                <div
                  className={clsx(
                    "flex items-center justify-center gap-2 rounded-xl border px-4 py-2.5 mb-4",
                    backupCodesRemaining <= 2
                      ? "bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-700/50"
                      : "bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-700/50"
                  )}
                >
                  <KeyIcon
                    className={clsx(
                      "h-4 w-4",
                      backupCodesRemaining <= 2
                        ? "text-amber-500 dark:text-amber-400"
                        : "text-emerald-500 dark:text-emerald-400"
                    )}
                  />
                  <span
                    className={clsx(
                      "text-sm font-semibold",
                      backupCodesRemaining <= 2
                        ? "text-amber-800 dark:text-amber-300"
                        : "text-emerald-800 dark:text-emerald-300"
                    )}
                  >
                    {backupCodesRemaining} backup code{backupCodesRemaining === 1 ? "" : "s"} remaining
                  </span>
                </div>
              )}

              <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 text-center mb-4">
                Enter one of your backup codes
              </label>

              <div className="flex justify-center">
                <input
                  ref={backupInputRef}
                  type="text"
                  inputMode="text"
                  autoComplete="off"
                  placeholder="XXXXX-XXXXX"
                  value={backupCode}
                  onChange={(e) => {
                    const val = e.target.value.toUpperCase();
                    // Auto-insert dash after 5 characters
                    if (val.length === 6 && val[5] !== "-") {
                      setBackupCode(val.slice(0, 5) + "-" + val.slice(5));
                    } else if (val.length <= 11) {
                      setBackupCode(val);
                    }
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleBackupVerify();
                    // Auto-remove dash when backspacing
                    if (e.key === "Backspace" && backupCode.length === 6 && backupCode[5] === "-") {
                      setBackupCode(backupCode.slice(0, 5));
                    }
                  }}
                  disabled={isSubmitting}
                  className={clsx(
                    "w-full max-w-xs rounded-xl border px-4 py-3 text-center text-lg font-mono font-bold tracking-[0.25em] transition-all duration-100 focus:outline-none focus:ring-2 uppercase placeholder:normal-case placeholder:tracking-normal placeholder:font-normal",
                    errorMsg
                      ? "border-red-300 focus:ring-red-400"
                      : "border-slate-300 dark:border-slate-600 focus:ring-indigo-500 focus:border-indigo-400",
                    backupCode ? "border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20" : ""
                  )}
                />
              </div>

              {errorMsg && (
                <p className="mt-3 text-center text-xs text-red-600 dark:text-red-400 flex items-center justify-center gap-1">
                  <ExclamationTriangleIcon className="h-3.5 w-3.5" />
                  {errorMsg}
                </p>
              )}

              <button
                type="button"
                disabled={isSubmitting || backupCode.length < 10}
                onClick={handleBackupVerify}
                className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 active:bg-indigo-700 transition-all duration-150 disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Verifying…
                  </>
                ) : (
                  <>
                    <KeyIcon className="h-4 w-4" />
                    Verify &amp; Sign In
                  </>
                )}
              </button>

              <p className="mt-3 text-center text-xs text-slate-400 dark:text-slate-500">
                Each backup code can only be used once.
              </p>
            </div>
          )}

          {/* ── Need help? ───────────────────────────────────── */}
          <div className="mt-6 rounded-xl bg-indigo-50 dark:bg-indigo-900/20 px-4 py-3">
            <p className="text-xs font-semibold text-indigo-700 dark:text-indigo-400 mb-1">
              Need help signing in?
            </p>
            <p className="text-xs text-indigo-600 dark:text-indigo-400/70">
              If you've lost access to your authenticator app, use a backup code
              instead. If you don't have any backup codes, contact your school
              administrator to have 2FA disabled for your account.
            </p>
          </div>
        </div>

        <p className="text-center text-xs text-indigo-400/70 mt-6">
          &copy; {new Date().getFullYear()} EduSphere. All rights reserved.
        </p>
      </div>
    </div>
  );
}
