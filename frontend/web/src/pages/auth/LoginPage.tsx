/**
 * Login Page — JWT login with role-based redirect
 */

import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { EyeIcon, EyeSlashIcon, AcademicCapIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { QK } from "../../api/hooks";
import { trackEvent } from "../../utils/analytics";
import { Button, Input } from "../../components/common";
import { ROLE_ROUTES } from "../../utils/roleRoutes";
import type { User, AuthTokens } from "../../types";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

type LoginForm = z.infer<typeof loginSchema>;

const SHOW_DEMO_CREDENTIALS = process.env.REACT_APP_SHOW_DEMO_CREDENTIALS === "true";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [needsVerification, setNeedsVerification] = useState(false);
  const [resending, setResending] = useState(false);
  const { setAuth } = useAuthStore();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });

  const { ref: emailRef, ...emailReg } = register("email");

  const handleResend = async () => {
    setResending(true);
    try {
      await api.post<{ detail: string }>("/auth/send-verification/");
      trackEvent("verification_email_sent", { source: "login_page" });
      toast.success("Verification email sent! Check your inbox.");
    } catch (err: unknown) {
      const error = err as { message?: string };
      toast.error(error?.message ?? "Failed to send verification email.");
    } finally {
      setResending(false);
    }
  };

  const onSubmit = async (data: LoginForm) => {
    // Reset verification banner on each submission attempt
    setNeedsVerification(false);

    try {
      const response = await api.post<Record<string, unknown>>("/auth/login/", {
        email: data.email,
        password: data.password,
      });

      // ── 2FA check ────────────────────────────────────────────
      if (response.requires_2fa === true) {
        navigate("/verify-2fa", {
          state: {
            user_id: response.user_id as string,
            email: data.email,
            backup_codes_remaining: response.backup_codes_remaining as number,
          },
          replace: true,
        });
        return;
      }

      const loginResult = response as unknown as {
        user: User;
        access: string;
        refresh: string;
      };

      // ── Normal login ──────────────────────────────────────────
      setAuth(loginResult.user, {
        access: loginResult.access,
        refresh: loginResult.refresh,
      });

      // Invalidate notification queries to pick up any in-app notifications
      queryClient.invalidateQueries({ queryKey: QK.communication.notifications });
      queryClient.invalidateQueries({ queryKey: QK.communication.unreadCount });

      // Check if the user's email needs verification
      if (!loginResult.user.email_verified) {
        setNeedsVerification(true);
        toast("Please verify your email to access all features.", {
          icon: "📧",
          duration: 6000,
        });
        return; // Stay on the login page, don't redirect
      }

      const route = ROLE_ROUTES[loginResult.user.role] ?? "/login";
      toast.success(`Welcome back, ${loginResult.user.first_name}!`);
      navigate(route, { replace: true });
    } catch (err: unknown) {
      const error = err as { message?: string; status?: number };
      const msg = error?.message ?? "Invalid credentials. Please try again.";
      if (error?.status === 401) {
        setError("password", { message: "Incorrect email or password" });
      } else if (error?.status === 429) {
        toast.error("Too many attempts. Please wait 30 minutes.");
      } else {
        toast.error(msg);
      }
    }
  };

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
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-1">Welcome back</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
            Sign in to your account to continue
          </p>

          <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">
            {/* Email */}
            <Input
              ref={emailRef}
              {...emailReg}
              label="Email address"
              type="email"
              autoComplete="email"
              placeholder="you@school.edu"
              error={errors.email?.message}
            />

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                  Password
                </label>
                <Link
                  to="/forgot-password"
                  className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <input
                  {...register("password")}
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="••••••••••"
                  className={`w-full rounded-xl border px-4 py-2.5 pr-11 text-sm transition focus:outline-none focus:ring-2 ${
                    errors.password
                      ? "border-red-300 focus:ring-red-400"
                      : "border-slate-200 focus:ring-indigo-500 focus:border-indigo-400"
                  }`}
                />
                <button
                  type="button"
                  tabIndex={-1}
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5" />
                  ) : (
                    <EyeIcon className="h-5 w-5" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1.5 text-xs text-red-600">{errors.password.message}</p>
              )}
            </div>

            {/* Submit */}
            <Button type="submit" disabled={isSubmitting} loading={isSubmitting} className="w-full">
              {isSubmitting ? "Signing in…" : "Sign in"}
            </Button>
          </form>

          {/* Email verification banner */}
          {needsVerification && (
            <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 dark:border-amber-800/50 dark:bg-amber-900/20 px-4 py-4">
              <div className="flex items-start gap-3">
                <svg
                  className="h-5 w-5 mt-0.5 shrink-0 text-amber-500"
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
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-amber-800 dark:text-amber-300">
                    Email not verified
                  </p>
                  <p className="text-xs text-amber-700 dark:text-amber-400 mt-1">
                    Some features are restricted until you verify your email address. Check your
                    inbox or send a new verification link.
                  </p>
                  <button
                    type="button"
                    disabled={resending}
                    onClick={handleResend}
                    className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-amber-100 dark:bg-amber-800/40 px-3 py-1.5 text-xs font-semibold text-amber-800 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-700/50 transition-colors disabled:opacity-50"
                  >
                    {resending ? (
                      <>
                        <svg className="h-3.5 w-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          />
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                          />
                        </svg>
                        Sending…
                      </>
                    ) : (
                      <>
                        <svg
                          className="h-3.5 w-3.5"
                          fill="none"
                          viewBox="0 0 24 24"
                          strokeWidth={2}
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"
                          />
                        </svg>
                        Resend verification email
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Demo credentials hint */}
          {SHOW_DEMO_CREDENTIALS && (
            <div className="mt-6 rounded-xl bg-indigo-50 dark:bg-indigo-900/30 px-4 py-3 dark:border dark:border-indigo-800/50">
              <p className="text-xs font-semibold text-indigo-700 mb-2">Demo Credentials</p>
              <div className="space-y-1 text-xs text-indigo-600">
                <p>
                  Admin: <span className="font-mono">admin@school.edu / Admin@1234</span>
                </p>
                <p>
                  Teacher: <span className="font-mono">teacher@school.edu / Teacher@1234</span>
                </p>
                <p>
                  Student: <span className="font-mono">student@school.edu / Student@1234</span>
                </p>
              </div>
            </div>
          )}
        </div>

        <p className="text-center text-xs text-indigo-400/70 mt-6">
          © {new Date().getFullYear()} EduSphere. All rights reserved.
        </p>
      </div>
    </div>
  );
}
