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
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { Button, Input } from "../../components/common";
import type { User, AuthTokens } from "../../types";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(1, "Password is required"),
  remember_me: z.boolean().optional(),
});

type LoginForm = z.infer<typeof loginSchema>;

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

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const { setAuth } = useAuthStore();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "", remember_me: false },
  });

  const { ref: emailRef, ...emailReg } = register("email");

  const onSubmit = async (data: LoginForm) => {
    try {
      const response = await api.post<{ user: User; access: string; refresh: string }>(
        "/auth/login/",
        { email: data.email, password: data.password }
      );
      setAuth(response.user, { access: response.access, refresh: response.refresh });
      const route = ROLE_ROUTES[response.user.role] ?? "/login";
      toast.success(`Welcome back, ${response.user.first_name}!`);
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
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Sign in to your account to continue</p>

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
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Password</label>
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

            {/* Remember me */}
            <div className="flex items-center gap-2.5">
              <input
                {...register("remember_me")}
                id="remember_me"
                type="checkbox"
                className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label htmlFor="remember_me" className="text-sm text-slate-600">
                Keep me signed in for 7 days
              </label>
            </div>

            {/* Submit */}
            <Button
              type="submit"
              disabled={isSubmitting}
              loading={isSubmitting}
              className="w-full"
            >
              {isSubmitting ? "Signing in…" : "Sign in"}
            </Button>
          </form>

          {/* Demo credentials hint */}
          <div className="mt-6 rounded-xl bg-indigo-50 dark:bg-indigo-900/30 px-4 py-3 dark:border dark:border-indigo-800/50">
            <p className="text-xs font-semibold text-indigo-700 mb-2">Demo Credentials</p>
            <div className="space-y-1 text-xs text-indigo-600">
              <p>Admin: <span className="font-mono">admin@school.edu / Admin@1234</span></p>
              <p>Teacher: <span className="font-mono">teacher@school.edu / Teacher@1234</span></p>
              <p>Student: <span className="font-mono">student@school.edu / Student@1234</span></p>
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-indigo-400/70 mt-6">
          © {new Date().getFullYear()} EduSphere. All rights reserved.
        </p>
      </div>
    </div>
  );
}
