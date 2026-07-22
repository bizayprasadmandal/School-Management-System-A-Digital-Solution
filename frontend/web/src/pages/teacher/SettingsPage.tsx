/**
 * Teacher Settings Page — profile editing, preferences, and teacher-specific fields
 */
import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import ProfileSettingsSection from "../../components/common/ProfileSettingsSection";
import { api } from "../../api/client";
import { Button, Input, Select, SkeletonCard } from "../../components/common";
import { useTitle } from "../../hooks";
import { AcademicCapIcon } from "@heroicons/react/24/outline";

interface TeacherProfileData {
  id: string;
  qualification: string;
  specialization: string;
  department: string;
  experience_years: number;
  bio: string;
}

const QUALIFICATION_OPTIONS = [
  { value: "diploma", label: "Diploma" },
  { value: "bachelor", label: "Bachelor's Degree" },
  { value: "master", label: "Master's Degree" },
  { value: "phd", label: "PhD" },
];

export default function TeacherSettingsPage() {
  useTitle("Settings");
  const qc = useQueryClient();

  const { data: teacherProfile, isLoading: profileLoading } = useQuery<TeacherProfileData>({
    queryKey: ["teacher-profile-me"],
    queryFn: () => api.get("/academics/teacher-profiles/me/"),
    staleTime: 30 * 60 * 1000,
  });

  const [form, setForm] = useState({
    qualification: "",
    specialization: "",
    department: "",
    experience_years: 0,
    bio: "",
  });

  useEffect(() => {
    if (teacherProfile) {
      setForm({
        qualification: teacherProfile.qualification || "",
        specialization: teacherProfile.specialization || "",
        department: teacherProfile.department || "",
        experience_years: teacherProfile.experience_years || 0,
        bio: teacherProfile.bio || "",
      });
    }
  }, [teacherProfile]);

  const updateTeacherProfile = useMutation({
    mutationFn: (data: Partial<TeacherProfileData>) =>
      api.patch("/academics/teacher-profiles/me/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teacher-profile-me"] });
      toast.success("Teacher profile updated!");
    },
    onError: () => toast.error("Failed to update teacher profile."),
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage your profile and preferences</p>
      </div>

      {/* Personal Info & Notifications (shared) */}
      <ProfileSettingsSection basePath="/teacher" accent="emerald" />

      {/* Teacher-Specific Profile */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <AcademicCapIcon className="h-5 w-5 text-emerald-600" />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Teaching Profile
          </h2>
        </div>

        {profileLoading ? (
          <div className="p-5"><SkeletonCard /></div>
        ) : (
          <div className="p-5 space-y-4">
            <Select
              label="Qualification"
              options={QUALIFICATION_OPTIONS}
              value={form.qualification}
              onChange={(e) => setForm((p) => ({ ...p, qualification: e.target.value }))}
            />
            <Input
              label="Specialization"
              value={form.specialization}
              onChange={(e) => setForm((p) => ({ ...p, specialization: e.target.value }))}
              placeholder="e.g. Mathematics, Physics, English Literature"
            />
            <Input
              label="Department"
              value={form.department}
              onChange={(e) => setForm((p) => ({ ...p, department: e.target.value }))}
              placeholder="e.g. Science, Humanities, Mathematics"
            />
            <Input
              label="Experience (years)"
              type="number"
              min={0}
              value={form.experience_years}
              onChange={(e) => setForm((p) => ({ ...p, experience_years: parseInt(e.target.value) || 0 }))}
            />
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Professional Bio
              </label>
              <textarea
                value={form.bio}
                onChange={(e) => setForm((p) => ({ ...p, bio: e.target.value }))}
                rows={4}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-400"
                placeholder="Write a brief professional bio highlighting your teaching experience, achievements, and areas of expertise..."
              />
            </div>
            <div className="flex justify-end pt-2">
              <Button
                variant="primary"
                onClick={() =>
                  updateTeacherProfile.mutate({
                    qualification: form.qualification,
                    specialization: form.specialization,
                    department: form.department,
                    experience_years: form.experience_years,
                    bio: form.bio,
                  })
                }
                loading={updateTeacherProfile.isPending}
              >
                Save Teaching Profile
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
