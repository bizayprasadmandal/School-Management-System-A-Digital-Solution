/**
 * Parent Settings Page — profile editing and notification preferences
 */
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Button, Input, SkeletonCard } from "../../components/common";
import { useProfile } from "../../api/hooks";
import { useTitle } from "../../hooks";
import toast from "react-hot-toast";
import {
  UserCircleIcon,
  BellIcon,
  ShieldCheckIcon,
  ArrowRightOnRectangleIcon,
} from "@heroicons/react/24/outline";
import { useAuthStore as useAuthStoreFromModule } from "../../store/authStore";

export default function ParentSettingsPage() {
  useTitle("Settings");
  const authStore = useAuthStoreFromModule();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { data: profile, isLoading } = useProfile();

  const [form, setForm] = useState({
    first_name: profile?.first_name || "",
    last_name: profile?.last_name || "",
    phone: profile?.phone || "",
  });
  const [notifPrefs, setNotifPrefs] = useState({
    notify_email: profile?.notify_email ?? true,
    notify_sms: profile?.notify_sms ?? false,
    notify_push: profile?.notify_push ?? true,
  });

  // Sync form when profile loads
  React.useEffect(() => {
    if (profile) {
      setForm({
        first_name: profile.first_name,
        last_name: profile.last_name,
        phone: profile.phone || "",
      });
      setNotifPrefs({
        notify_email: profile.notify_email,
        notify_sms: profile.notify_sms,
        notify_push: profile.notify_push,
      });
    }
  }, [profile]);

  const updateProfile = useMutation({
    mutationFn: (data: typeof form) => api.patch("/auth/profile/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      toast.success("Profile updated successfully!");
    },
    onError: () => toast.error("Failed to update profile."),
  });

  const updateNotifs = useMutation({
    mutationFn: (data: typeof notifPrefs) => api.patch("/auth/profile/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      toast.success("Notification preferences updated!");
    },
    onError: () => toast.error("Failed to update preferences."),
  });

  if (isLoading) return <div className="p-4"><SkeletonCard /></div>;

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">Manage your profile and preferences</p>
      </div>

      {/* Profile Section */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <UserCircleIcon className="h-5 w-5 text-violet-600" />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">Personal Information</h2>
        </div>
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="First Name"
              value={form.first_name}
              onChange={(e) => setForm((p) => ({ ...p, first_name: e.target.value }))}
            />
            <Input
              label="Last Name"
              value={form.last_name}
              onChange={(e) => setForm((p) => ({ ...p, last_name: e.target.value }))}
            />
          </div>
          <Input
            label="Phone Number"
            value={form.phone}
            onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
            placeholder="+1 (555) 123-4567"
          />
          <Input label="Email" value={profile?.email || ""} disabled hint="Email cannot be changed here" />
          <div className="flex justify-end">
            <Button
              variant="primary"
              onClick={() => updateProfile.mutate(form)}
              loading={updateProfile.isPending}
              disabled={!form.first_name || !form.last_name}
            >
              Save Changes
            </Button>
          </div>
        </div>
      </div>

      {/* Notification Preferences */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <BellIcon className="h-5 w-5 text-violet-600" />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">Notification Preferences</h2>
        </div>
        <div className="p-5 space-y-4">
          {[
            { key: "notify_email" as const, label: "Email Notifications", desc: "Receive updates via email about grades, attendance, and school announcements" },
            { key: "notify_sms" as const, label: "SMS Notifications", desc: "Receive text messages for urgent announcements and fee reminders" },
            { key: "notify_push" as const, label: "Push Notifications", desc: "Receive in-app notifications when logged into the portal" },
          ].map(({ key, label, desc }) => (
            <div key={key} className="flex items-center justify-between py-2">
              <div className="flex-1">
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{label}</p>
                <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
              </div>
              <label className="relative inline-flex h-6 w-11 cursor-pointer items-center">
                <input
                  type="checkbox"
                  checked={notifPrefs[key]}
                  onChange={(e) =>
                    setNotifPrefs((p) => ({ ...p, [key]: e.target.checked }))
                  }
                  className="peer sr-only"
                />
                <span className="absolute inset-0 rounded-full bg-slate-300 transition-colors peer-checked:bg-violet-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-violet-500" />
                <span className="absolute left-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-transform peer-checked:translate-x-5" />
              </label>
            </div>
          ))}
          <div className="flex justify-end pt-2">
            <Button
              variant="primary"
              onClick={() => updateNotifs.mutate(notifPrefs)}
              loading={updateNotifs.isPending}
            >
              Save Preferences
            </Button>
          </div>
        </div>
      </div>

      {/* Security Section */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <ShieldCheckIcon className="h-5 w-5 text-violet-600" />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">Security</h2>
        </div>
        <div className="p-5 space-y-3">
          <div className="flex items-center justify-between py-2">
            <div>
              <p className="text-sm font-semibold text-slate-800">Email Verification</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {profile?.email_verified
                  ? "Your email is verified"
                  : "Verify your email to access all features"}
              </p>
            </div>
            <Button
              variant={profile?.email_verified ? "secondary" : "primary"}
              size="sm"
              onClick={() => navigate("/parent/verify-email")}
            >
              {profile?.email_verified ? "Resend Verification" : "Verify Now"}
            </Button>
          </div>
          <div className="flex items-center justify-between py-2">
            <div>
              <p className="text-sm font-semibold text-slate-800">Two-Factor Authentication</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {profile?.two_factor_enabled
                  ? "2FA is enabled — extra security for your account"
                  : "Add an extra layer of security to your account"}
              </p>
            </div>
            <Button
              variant={profile?.two_factor_enabled ? "secondary" : "primary"}
              size="sm"
              onClick={() => navigate("/parent/setup-2fa")}
            >
              {profile?.two_factor_enabled ? "Manage 2FA" : "Enable 2FA"}
            </Button>
          </div>
        </div>
      </div>

      {/* Logout */}
      <div className="flex justify-end">
        <Button
          variant="danger"
          size="sm"
          onClick={() => {
            authStore.logout();
            navigate("/login");
          }}
          leftIcon={<ArrowRightOnRectangleIcon className="h-4 w-4" />}
        >
          Sign Out
        </Button>
      </div>
    </div>
  );
}
