/**
 * Verify Email Page
 *
 * Reads the verification token from the URL path (/verify-email/:token)
 * and calls POST /auth/verify-email/ to confirm the user's email address.
 *
 * On success, shows a confirmation with a link to log in.
 * On error, shows the failure reason with a link to request a new email.
 */

import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { AcademicCapIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import toast from "react-hot-toast";

type VerifyState = "verifying" | "success" | "error";

export default function VerifyEmailPage() {
  const { token } = useParams<{ token: string }>();
  const [state, setState] = useState<VerifyState>("verifying");
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    if (!token) {
      setState("error");
      setErrorMsg("No verification token found in the URL.");
      return;
    }

    let cancelled = false;

    const verify = async () => {
      try {
        await api.post<{ detail: string; email_verified: boolean }>(
          "/auth/verify-email/",
          { token }
        );
        if (!cancelled) {
          setState("success");
          toast.success("Email verified successfully!");
        }
      } catch (err: unknown) {
        if (cancelled) return;
        const error = err as { message?: string; status?: number };
        const msg =
          error?.message ??
          "Verification failed. The link may have expired.";
        setState("error");
        setErrorMsg(msg);
        toast.error(msg);
      }
    };

    verify();

    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-indigo-900 to-violet-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-white/10 backdrop-blur mb-4">
            <AcademicCapIcon className="h-9 w-9 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">EduSphere</h1>
          <p className="mt-1.5 text-indigo-300 text-sm">
            School Management System
          </p>
        </div>

        {/* Card */}
        <div className="rounded-2xl bg-white dark:bg-slate-800 p-8 shadow-2xl dark:shadow-none">
          {/* Verifying state */}
          {state === "verifying" && (
            <div className="flex flex-col items-center py-6 text-center">
              <div className="h-12 w-12 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-4" />
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                Verifying your email…
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                Please wait while we confirm your email address.
              </p>
            </div>
          )}

          {/* Success state */}
          {state === "success" && (
            <div className="flex flex-col items-center py-4 text-center">
              <div className="h-16 w-16 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mb-4">
                <svg
                  className="h-8 w-8 text-green-600 dark:text-green-400"
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
              </div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                Email verified!
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                Your email address has been confirmed. You can now access all
                features of the system.
              </p>
              <Link
                to="/login"
                className="mt-6 inline-flex items-center justify-center w-full rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow hover:bg-indigo-500 transition-colors"
              >
                Sign in to your account
              </Link>
            </div>
          )}

          {/* Error state */}
          {state === "error" && (
            <div className="flex flex-col items-center py-4 text-center">
              <div className="h-16 w-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mb-4">
                <svg
                  className="h-8 w-8 text-red-600 dark:text-red-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                Verification failed
              </h2>
              <p className="text-sm text-red-600 dark:text-red-400 mt-2">
                {errorMsg}
              </p>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-3">
                You can request a new verification email from your profile
                settings after signing in.
              </p>
              <Link
                to="/login"
                className="mt-6 inline-flex items-center justify-center w-full rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow hover:bg-indigo-500 transition-colors"
              >
                Go to login
              </Link>
            </div>
          )}

          {/* Footer link */}
          <Link
            to="/login"
            className="block text-center mt-5 text-sm text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back to login
          </Link>
        </div>

        <p className="text-center text-xs text-indigo-400/70 mt-6">
          &copy; {new Date().getFullYear()} EduSphere. All rights reserved.
        </p>
      </div>
    </div>
  );
}
