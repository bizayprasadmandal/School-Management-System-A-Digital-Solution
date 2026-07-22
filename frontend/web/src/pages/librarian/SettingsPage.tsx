/**
 * Librarian Settings Page — profile editing, preferences, and librarian-specific fields
 */
import React, { useState, useEffect } from "react";
import ProfileSettingsSection from "../../components/common/ProfileSettingsSection";
import { Button, Input, Select, SkeletonCard } from "../../components/common";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import toast from "react-hot-toast";
import { useTitle } from "../../hooks";
import { BookOpenIcon } from "@heroicons/react/24/outline";

interface LibrarianProfile {
  library_section: string;
  qualification: string;
  experience_years: number;
  certifications: string;
  bio: string;
}

const LIBRARY_SECTIONS = [
  { value: "circulation", label: "Circulation" },
  { value: "reference", label: "Reference" },
  { value: "cataloging", label: "Cataloging" },
  { value: "periodicals", label: "Periodicals" },
  { value: "digital", label: "Digital Library" },
  { value: "archives", label: "Archives" },
  { value: "children", label: "Children\'s Section" },
  { value: "general", label: "General" },
];

export default function LibrarianSettingsPage() {
  useTitle("Settings");
  const qc = useQueryClient();
  const [loadingProfile, setLoadingProfile] = useState(true);

  const [form, setForm] = useState({
    library_section: "",
    qualification: "",
    experience_years: 0,
    certifications: "",
    bio: "",
  });

  useEffect(() => {
    api.get("/library/profile/")
      .then((data: any) => {
        setForm({
          library_section: data.library_section || "",
          qualification: data.qualification || "",
          experience_years: data.experience_years || 0,
          certifications: data.certifications || "",
          bio: data.bio || "",
        });
      })
      .catch(() => {})
      .finally(() => setLoadingProfile(false));
  }, []);

  const updateProfile = useMutation({
    mutationFn: (data: typeof form) => api.patch("/library/profile/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["librarian-profile"] });
      toast.success("Librarian profile updated successfully!");
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
      <ProfileSettingsSection basePath="/librarian" accent="teal" />

      {/* Librarian-specific fields */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <BookOpenIcon className="h-5 w-5 text-teal-600" />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Library Profile
          </h2>
        </div>
        {loadingProfile ? (
          <div className="p-5"><SkeletonCard /></div>
        ) : (
          <div className="p-5 space-y-4">
            <Select
              label="Primary Library Section"
              value={form.library_section}
              onChange={(e) => setForm((p) => ({ ...p, library_section: e.target.value }))}
              options={LIBRARY_SECTIONS}
              placeholder="Select section..."
            />
            <Input
              label="Qualification"
              value={form.qualification}
              onChange={(e) => setForm((p) => ({ ...p, qualification: e.target.value }))}
              placeholder="e.g. Bachelor of Library Science"
            />
            <Input
              label="Experience (Years)"
              type="number"
              min={0}
              value={String(form.experience_years)}
              onChange={(e) => setForm((p) => ({ ...p, experience_years: Number(e.target.value) }))}
            />
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Certifications
              </label>
              <textarea
                value={form.certifications}
                onChange={(e) => setForm((p) => ({ ...p, certifications: e.target.value }))}
                rows={3}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400"
                placeholder="List your library science certifications..."
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
                placeholder="Tell us about your library experience..."
              />
            </div>
            <div className="flex justify-end">
              <Button
                variant="primary"
                onClick={() => updateProfile.mutate(form)}
                loading={updateProfile.isPending}
              >
                Save Library Profile
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
