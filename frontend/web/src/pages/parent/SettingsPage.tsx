/**
 * Parent Settings Page — profile editing, preferences, and parent-specific fields
 */
import React, { useState, useEffect } from "react";
import ProfileSettingsSection from "../../components/common/ProfileSettingsSection";
import { Button, Input, SkeletonCard } from "../../components/common";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import toast from "react-hot-toast";
import { useTitle } from "../../hooks";
import { HeartIcon } from "@heroicons/react/24/outline";

interface ParentProfile {
  occupation: string;
  alternate_phone: string;
  address: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  bio: string;
}

export default function ParentSettingsPage() {
  useTitle("Settings");
  const qc = useQueryClient();
  const [loadingProfile, setLoadingProfile] = useState(true);

  const [form, setForm] = useState({
    occupation: "",
    alternate_phone: "",
    address: "",
    emergency_contact_name: "",
    emergency_contact_phone: "",
    bio: "",
  });

  useEffect(() => {
    api.get("/students/parent-profile/")
      .then((data: any) => {
        setForm({
          occupation: data.occupation || "",
          alternate_phone: data.alternate_phone || "",
          address: data.address || "",
          emergency_contact_name: data.emergency_contact_name || "",
          emergency_contact_phone: data.emergency_contact_phone || "",
          bio: data.bio || "",
        });
      })
      .catch(() => {})
      .finally(() => setLoadingProfile(false));
  }, []);

  const updateProfile = useMutation({
    mutationFn: (data: typeof form) => api.patch("/students/parent-profile/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["parent-profile"] });
      toast.success("Profile updated successfully!");
    },
    onError: () => toast.error("Failed to update profile."),
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage your profile and preferences</p>
      </div>

      {/* Shared profile section (avatar, personal info, password, notifications, security) */}
      <ProfileSettingsSection basePath="/parent" accent="violet" />

      {/* Parent-specific fields */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <HeartIcon className="h-5 w-5 text-violet-600" />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Parent Details
          </h2>
        </div>
        {loadingProfile ? (
          <div className="p-5"><SkeletonCard /></div>
        ) : (
          <div className="p-5 space-y-4">
            <Input
              label="Occupation"
              value={form.occupation}
              onChange={(e) => setForm((p) => ({ ...p, occupation: e.target.value }))}
              placeholder="e.g. Engineer, Doctor, Teacher"
            />
            <Input
              label="Alternate Phone"
              value={form.alternate_phone}
              onChange={(e) => setForm((p) => ({ ...p, alternate_phone: e.target.value }))}
              placeholder="+1 (555) 987-6543"
            />
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Address
              </label>
              <textarea
                value={form.address}
                onChange={(e) => setForm((p) => ({ ...p, address: e.target.value }))}
                rows={2}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
                placeholder="Your residential address"
              />
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Emergency Contact Name"
                value={form.emergency_contact_name}
                onChange={(e) => setForm((p) => ({ ...p, emergency_contact_name: e.target.value }))}
                placeholder="Name of emergency contact"
              />
              <Input
                label="Emergency Contact Phone"
                value={form.emergency_contact_phone}
                onChange={(e) => setForm((p) => ({ ...p, emergency_contact_phone: e.target.value }))}
                placeholder="+1 (555) 111-2222"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                About Me
              </label>
              <textarea
                value={form.bio}
                onChange={(e) => setForm((p) => ({ ...p, bio: e.target.value }))}
                rows={2}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
                placeholder="A short bio about yourself..."
              />
            </div>
            <div className="flex justify-end">
              <Button
                variant="primary"
                onClick={() => updateProfile.mutate(form)}
                loading={updateProfile.isPending}
              >
                Save Parent Details
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
