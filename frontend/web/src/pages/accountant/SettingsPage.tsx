/**
 * Accountant Settings Page — profile editing, preferences, and accountant-specific fields
 */
import React, { useState, useEffect } from "react";
import ProfileSettingsSection from "../../components/common/ProfileSettingsSection";
import { Button, Input, SkeletonCard } from "../../components/common";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import toast from "react-hot-toast";
import { useTitle } from "../../hooks";
import { BriefcaseIcon } from "@heroicons/react/24/outline";

export default function AccountantSettingsPage() {
  useTitle("Settings");
  const qc = useQueryClient();
  const [loadingProfile, setLoadingProfile] = useState(true);

  const [form, setForm] = useState({
    qualification: "",
    specialization: "",
    experience_years: 0,
    certifications: "",
    bio: "",
  });

  useEffect(() => {
    api.get("/hr/profile/")
      .then((data: any) => {
        setForm({
          qualification: data.qualification || "",
          specialization: data.specialization || "",
          experience_years: data.experience_years || 0,
          certifications: data.certifications || "",
          bio: data.bio || "",
        });
      })
      .catch(() => {})
      .finally(() => setLoadingProfile(false));
  }, []);

  const updateProfile = useMutation({
    mutationFn: (data: typeof form) => api.patch("/hr/profile/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accountant-profile"] });
      toast.success("Accountant profile updated successfully!");
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
      <ProfileSettingsSection basePath="/accountant" accent="amber" />

      {/* Accountant-specific fields */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <BriefcaseIcon className="h-5 w-5 text-amber-600" />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Accounting Profile
          </h2>
        </div>
        {loadingProfile ? (
          <div className="p-5"><SkeletonCard /></div>
        ) : (
          <div className="p-5 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Qualification"
                value={form.qualification}
                onChange={(e) => setForm((p) => ({ ...p, qualification: e.target.value }))}
                placeholder="e.g. ACCA, CPA, MBA Finance"
              />
              <Input
                label="Specialization"
                value={form.specialization}
                onChange={(e) => setForm((p) => ({ ...p, specialization: e.target.value }))}
                placeholder="e.g. Taxation, Audit"
              />
            </div>
            <Input
              label="Experience (Years)"
              type="number"
              min={0}
              value={String(form.experience_years)}
              onChange={(e) => setForm((p) => ({ ...p, experience_years: Number(e.target.value) }))}
            />
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Certifications & Licenses
              </label>
              <textarea
                value={form.certifications}
                onChange={(e) => setForm((p) => ({ ...p, certifications: e.target.value }))}
                rows={3}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
                placeholder="List your professional certifications..."
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Professional Bio
              </label>
              <textarea
                value={form.bio}
                onChange={(e) => setForm((p) => ({ ...p, bio: e.target.value }))}
                rows={3}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
                placeholder="Tell us about your professional background..."
              />
            </div>
            <div className="flex justify-end">
              <Button
                variant="primary"
                onClick={() => updateProfile.mutate(form)}
                loading={updateProfile.isPending}
              >
                Save Accounting Profile
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
