/**
 * Counselor Settings Page — profile editing, preferences, and counselor-specific fields
 */
import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import ProfileSettingsSection from "../../components/common/ProfileSettingsSection";
import { api } from "../../api/client";
import { Button, SkeletonCard } from "../../components/common";
import { useTitle } from "../../hooks";
import { AcademicCapIcon } from "@heroicons/react/24/outline";

interface CounselorProfileData {
  id: string;
  specialties: string;
  certifications: string;
  office_hours: string;
  bio: string;
}

export default function CounselorSettingsPage() {
  useTitle("Settings");
  const qc = useQueryClient();

  const { data: counselorProfile, isLoading: profileLoading } = useQuery<CounselorProfileData>({
    queryKey: ["counselor-profile"],
    queryFn: () => api.get("/counseling/profile/"),
    staleTime: 30 * 60 * 1000,
  });

  const [form, setForm] = useState({
    specialties: "",
    certifications: "",
    office_hours: "",
    bio: "",
  });

  useEffect(() => {
    if (counselorProfile) {
      setForm({
        specialties: counselorProfile.specialties || "",
        certifications: counselorProfile.certifications || "",
        office_hours: counselorProfile.office_hours || "",
        bio: counselorProfile.bio || "",
      });
    }
  }, [counselorProfile]);

  const updateCounselorProfile = useMutation({
    mutationFn: (data: Partial<CounselorProfileData>) =>
      api.patch("/counseling/profile/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["counselor-profile"] });
      toast.success("Counselor profile updated!");
    },
    onError: () => toast.error("Failed to update counselor profile."),
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage your profile and preferences</p>
      </div>

      {/* Personal Info & Notifications (shared) */}
      <ProfileSettingsSection basePath="/counselor" accent="pink" />

      {/* Counselor-Specific Profile */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <AcademicCapIcon className="h-5 w-5 text-pink-600" />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Counseling Profile
          </h2>
        </div>

        {profileLoading ? (
          <div className="p-5"><SkeletonCard /></div>
        ) : (
          <div className="p-5 space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Specialties
              </label>
              <textarea
                value={form.specialties}
                onChange={(e) => setForm((p) => ({ ...p, specialties: e.target.value }))}
                rows={3}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-pink-400"
                placeholder="e.g. Academic counseling, Career guidance, Mental health support, College prep..."
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Certifications &amp; Licenses
              </label>
              <textarea
                value={form.certifications}
                onChange={(e) => setForm((p) => ({ ...p, certifications: e.target.value }))}
                rows={3}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-pink-400"
                placeholder="e.g. Licensed Professional Counselor (LPC), National Board Certified Counselor (NBCC)..."
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Office Hours &amp; Availability
              </label>
              <textarea
                value={form.office_hours}
                onChange={(e) => setForm((p) => ({ ...p, office_hours: e.target.value }))}
                rows={3}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-pink-400"
                placeholder="e.g. Monday–Friday 8:00 AM – 4:00 PM, Room 204, or by appointment..."
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Professional Bio
              </label>
              <textarea
                value={form.bio}
                onChange={(e) => setForm((p) => ({ ...p, bio: e.target.value }))}
                rows={4}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-pink-400"
                placeholder="Write a brief professional bio highlighting your counseling approach and experience..."
              />
            </div>

            <div className="flex justify-end pt-2">
              <Button
                variant="primary"
                onClick={() =>
                  updateCounselorProfile.mutate({
                    specialties: form.specialties,
                    certifications: form.certifications,
                    office_hours: form.office_hours,
                    bio: form.bio,
                  })
                }
                loading={updateCounselorProfile.isPending}
              >
                Save Counseling Profile
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
