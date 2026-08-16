/**
 * ProfileSettingsSection — Reusable profile editing component with avatar upload,
 * personal info editing, change password, notification prefs, and auth store sync.
 * Used by all role-specific Settings pages.
 */
import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { api } from "../../api/client";
import type { User } from "../../types";
import { Button, Input, SkeletonCard } from "./index";
import { useProfile } from "../../api/hooks";
import { useAuthStore } from "../../store/authStore";
import {
  UserCircleIcon,
  BellIcon,
  ShieldCheckIcon,
  ArrowRightOnRectangleIcon,
  CameraIcon,
  KeyIcon,
  XCircleIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";

interface ProfileSettingsSectionProps {
  /** Base path for relative navigation (e.g. "/teacher" or "/student") */
  basePath: string;
  /** Color accent for icon headers (e.g. "violet", "emerald", "blue", "pink") */
  accent?: string;
}

const ACCENT_MAP: Record<string, { icon: string; toggle: string }> = {
  violet: { icon: "text-violet-600", toggle: "bg-violet-600" },
  emerald: { icon: "text-emerald-600", toggle: "bg-emerald-600" },
  blue: { icon: "text-blue-600", toggle: "bg-blue-600" },
  pink: { icon: "text-pink-600", toggle: "bg-pink-600" },
  amber: { icon: "text-amber-600", toggle: "bg-amber-600" },
  teal: { icon: "text-teal-600", toggle: "bg-teal-600" },
};

export default function ProfileSettingsSection({
  basePath,
  accent = "violet",
}: ProfileSettingsSectionProps) {
  const colors = ACCENT_MAP[accent] ?? ACCENT_MAP.violet;
  const navigate = useNavigate();
  const qc = useQueryClient();
  const authLogout = useAuthStore((s) => s.logout);
  const setUser = useAuthStore((s) => s.setUser);
  const currentUser = useAuthStore((s) => s.user);
  const { data: profile, isLoading } = useProfile();

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    phone: "",
  });
  const [notifPrefs, setNotifPrefs] = useState({
    notify_email: true,
    notify_sms: false,
    notify_push: true,
  });

  // ─── Avatar ────────────────────────────────────────────────────────────────
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);

  // ─── Change Password ────────────────────────────────────────────────────────
  const [pwdForm, setPwdForm] = useState({
    old_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [pwdErrors, setPwdErrors] = useState<Record<string, string>>({});

  // Sync form when profile loads
  useEffect(() => {
    if (profile) {
      setForm({
        first_name: profile.first_name || "",
        last_name: profile.last_name || "",
        phone: profile.phone || "",
      });
      setNotifPrefs({
        notify_email: profile.notify_email ?? true,
        notify_sms: profile.notify_sms ?? false,
        notify_push: profile.notify_push ?? true,
      });
    }
  }, [profile]);

  // ─── Update Profile ─────────────────────────────────────────────────────────

  const updateProfile = useMutation({
    mutationFn: (data: typeof form) => api.patch<User>("/auth/profile/", data),
    onSuccess: (updatedUser) => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      // Sync auth store so sidebar avatar/name updates immediately
      if (updatedUser && currentUser) {
        setUser({ ...currentUser, ...updatedUser });
      }
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

  // ─── Avatar Upload ──────────────────────────────────────────────────────────

  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type and size
    if (!file.type.startsWith("image/")) {
      toast.error("Please select an image file.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error("Image must be under 5MB.");
      return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onload = (ev) => setAvatarPreview(ev.target?.result as string);
    reader.readAsDataURL(file);

    // Upload
    setUploadingAvatar(true);
    const formData = new FormData();
    formData.append("avatar", file);

    api
      .upload<{ avatar: string; detail: string }>("/auth/upload-avatar/", formData)
      .then((res) => {
        toast.success("Avatar updated!");
        qc.invalidateQueries({ queryKey: ["profile"] });
        // Update auth store
        if (res.avatar && currentUser) {
          setUser({ ...currentUser, avatar: res.avatar });
        }
        setAvatarPreview(null);
      })
      .catch(() => toast.error("Failed to upload avatar."))
      .finally(() => setUploadingAvatar(false));
  };

  const handleRemoveAvatar = () => {
    api
      .delete("/auth/upload-avatar/")
      .then(() => {
        toast.success("Avatar removed.");
        qc.invalidateQueries({ queryKey: ["profile"] });
        if (currentUser) setUser({ ...currentUser, avatar: undefined });
      })
      .catch(() => toast.error("Failed to remove avatar."));
  };

  // ─── Change Password ────────────────────────────────────────────────────────

  const changePassword = useMutation({
    mutationFn: (data: { old_password: string; new_password: string }) =>
      api.post("/auth/change-password/", data),
    onSuccess: () => {
      toast.success("Password changed successfully!");
      setPwdForm({ old_password: "", new_password: "", confirm_password: "" });
      setPwdErrors({});
    },
    onError: (err: any) => {
      if (err?.fieldErrors) {
        setPwdErrors(
          Object.fromEntries(
            Object.entries(err.fieldErrors).map(([k, v]) => [k, (v as string[]).join(", ")]),
          ),
        );
      } else {
        toast.error(err?.message || "Failed to change password.");
      }
    },
  });

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault();
    const errors: Record<string, string> = {};
    if (!pwdForm.old_password) errors.old_password = "Current password is required.";
    if (pwdForm.new_password.length < 8)
      errors.new_password = "Password must be at least 8 characters.";
    if (pwdForm.new_password !== pwdForm.confirm_password)
      errors.confirm_password = "Passwords do not match.";
    setPwdErrors(errors);
    if (Object.keys(errors).length > 0) return;
    changePassword.mutate({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password,
    });
  };

  if (isLoading) return <SkeletonCard />;

  const avatarUrl = avatarPreview || profile?.avatar;

  return (
    <div className="space-y-6">
      {/* Avatar Upload */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <CameraIcon className={`h-5 w-5 ${colors.icon}`} />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Profile Picture
          </h2>
        </div>
        <div className="p-5 flex items-center gap-6">
          <div className="relative group">
            <div className="h-24 w-24 rounded-full overflow-hidden bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center">
              {avatarUrl ? (
                <img
                  src={avatarUrl}
                  alt="Avatar"
                  className="h-full w-full object-cover"
                  loading="lazy"
                />
              ) : (
                <UserCircleIcon className="h-14 w-14 text-indigo-400" />
              )}
            </div>
            {profile?.avatar && !avatarPreview && (
              <button
                onClick={handleRemoveAvatar}
                className="absolute -top-1 -right-1 rounded-full bg-red-500 p-1 text-white shadow hover:bg-red-600 transition-colors"
                title="Remove avatar"
              >
                <XCircleIcon className="h-4 w-4" />
              </button>
            )}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
              {profile?.full_name || "Your Name"}
            </p>
            <p className="text-xs text-slate-500 mt-0.5 mb-3">JPEG, PNG, or WebP. Max 5MB.</p>
            <div className="flex gap-2">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={handleAvatarChange}
              />
              <Button
                variant="secondary"
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                loading={uploadingAvatar}
                leftIcon={<CameraIcon className="h-4 w-4" />}
              >
                {profile?.avatar ? "Change Photo" : "Upload Photo"}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Personal Information */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <UserCircleIcon className={`h-5 w-5 ${colors.icon}`} />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Personal Information
          </h2>
        </div>
        <div className="p-5 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="First Name"
              value={form.first_name}
              onChange={(e) => setForm((p) => ({ ...p, first_name: e.target.value }))}
              required
            />
            <Input
              label="Last Name"
              value={form.last_name}
              onChange={(e) => setForm((p) => ({ ...p, last_name: e.target.value }))}
              required
            />
          </div>
          <Input
            label="Phone Number"
            value={form.phone}
            onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
            placeholder="+1 (555) 123-4567"
          />
          <Input
            label="Email"
            value={profile?.email || ""}
            disabled
            hint="Email cannot be changed here. Use the verification section below."
          />
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

      {/* Change Password */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <KeyIcon className={`h-5 w-5 ${colors.icon}`} />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Change Password
          </h2>
        </div>
        <form onSubmit={handleChangePassword} className="p-5 space-y-4">
          <Input
            label="Current Password"
            type="password"
            value={pwdForm.old_password}
            onChange={(e) => setPwdForm((p) => ({ ...p, old_password: e.target.value }))}
            error={pwdErrors.old_password}
            required
          />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="New Password"
              type="password"
              value={pwdForm.new_password}
              onChange={(e) => setPwdForm((p) => ({ ...p, new_password: e.target.value }))}
              error={pwdErrors.new_password}
              hint="At least 8 characters"
              required
            />
            <Input
              label="Confirm New Password"
              type="password"
              value={pwdForm.confirm_password}
              onChange={(e) => setPwdForm((p) => ({ ...p, confirm_password: e.target.value }))}
              error={pwdErrors.confirm_password}
              required
            />
          </div>
          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              loading={changePassword.isPending}
              leftIcon={<CheckCircleIcon className="h-4 w-4" />}
            >
              Update Password
            </Button>
          </div>
        </form>
      </div>

      {/* Notification Preferences */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <BellIcon className={`h-5 w-5 ${colors.icon}`} />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Notification Preferences
          </h2>
        </div>
        <div className="p-5 space-y-4">
          {[
            {
              key: "notify_email" as const,
              label: "Email Notifications",
              desc: "Receive updates via email about grades, attendance, and school announcements",
            },
            {
              key: "notify_sms" as const,
              label: "SMS Notifications",
              desc: "Receive text messages for urgent announcements and fee reminders",
            },
            {
              key: "notify_push" as const,
              label: "Push Notifications",
              desc: "Receive in-app notifications when logged into the portal",
            },
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
                  onChange={(e) => setNotifPrefs((p) => ({ ...p, [key]: e.target.checked }))}
                  className="peer sr-only"
                />
                <span className="absolute inset-0 rounded-full bg-slate-300 transition-colors peer-checked:bg-slate-800 dark:peer-checked:bg-indigo-500 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-indigo-500" />
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
          <ShieldCheckIcon className={`h-5 w-5 ${colors.icon}`} />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">Security</h2>
        </div>
        <div className="p-5 space-y-3">
          <div className="flex items-center justify-between py-2">
            <div>
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                Email Verification
              </p>
              <p className="text-xs text-slate-500 mt-0.5">
                {profile?.email_verified
                  ? "Your email is verified"
                  : "Verify your email to access all features"}
              </p>
            </div>
            <Button
              variant={profile?.email_verified ? "secondary" : "primary"}
              size="sm"
              onClick={() => navigate(`${basePath}/verify-email`)}
            >
              {profile?.email_verified ? "Resend Verification" : "Verify Now"}
            </Button>
          </div>
          <div className="flex items-center justify-between py-2">
            <div>
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                Two-Factor Authentication
              </p>
              <p className="text-xs text-slate-500 mt-0.5">
                {profile?.two_factor_enabled
                  ? "2FA is enabled — extra security for your account"
                  : "Add an extra layer of security to your account"}
              </p>
            </div>
            <Button
              variant={profile?.two_factor_enabled ? "secondary" : "primary"}
              size="sm"
              onClick={() => navigate(`${basePath}/setup-2fa`)}
            >
              {profile?.two_factor_enabled ? "Manage 2FA" : "Enable 2FA"}
            </Button>
          </div>
        </div>
      </div>

      {/* Sign out */}
      <div className="flex justify-end">
        <Button
          variant="danger"
          size="sm"
          onClick={() => {
            authLogout();
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
