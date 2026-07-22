/**
 * Student Settings Page — profile editing, preferences, and student-specific fields
 */
import React, { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import ProfileSettingsSection from "../../components/common/ProfileSettingsSection";
import { api } from "../../api/client";
import { Button, SkeletonCard } from "../../components/common";
import { useTitle } from "../../hooks";
import { AcademicCapIcon } from "@heroicons/react/24/outline";

interface StudentProfileData {
  id: string;
  bio: string;
  interests: string;
  learning_goals: string;
}

export default function StudentSettingsPage() {
  useTitle("Settings");
  const qc = useQueryClient();

  const { data: studentProfile, isLoading: profileLoading } = useQuery<StudentProfileData>({
    queryKey: ["student-me"],
    queryFn: () => api.get("/students/me/"),
    staleTime: 30 * 60 * 1000,
  });

  const [form, setForm] = useState({
    bio: "",
    interests: "",
    learning_goals: "",
  });

  useEffect(() => {
    if (studentProfile) {
      setForm({
        bio: studentProfile.bio || "",
        interests: studentProfile.interests || "",
        learning_goals: studentProfile.learning_goals || "",
      });
    }
  }, [studentProfile]);

  const updateStudentProfile = useMutation({
    mutationFn: (data: Partial<StudentProfileData>) =>
      api.patch("/students/me/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["student-me"] });
      toast.success("Student profile updated!");
    },
    onError: () => toast.error("Failed to update student profile."),
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage your profile and preferences</p>
      </div>

      {/* Personal Info & Notifications (shared) */}
      <ProfileSettingsSection basePath="/student" accent="blue" />

      {/* Student-Specific Profile */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
          <AcademicCapIcon className="h-5 w-5 text-blue-600" />
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
            Student Profile
          </h2>
        </div>

        {profileLoading ? (
          <div className="p-5"><SkeletonCard /></div>
        ) : (
          <div className="p-5 space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                About Me / Bio
              </label>
              <textarea
                value={form.bio}
                onChange={(e) => setForm((p) => ({ ...p, bio: e.target.value }))}
                rows={3}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400"
                placeholder="Write a short bio about yourself..."
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Interests &amp; Hobbies
              </label>
              <textarea
                value={form.interests}
                onChange={(e) => setForm((p) => ({ ...p, interests: e.target.value }))}
                rows={3}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400"
                placeholder="e.g. sports, music, coding, art, debate club..."
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1.5">
                Learning Goals &amp; Aspirations
              </label>
              <textarea
                value={form.learning_goals}
                onChange={(e) => setForm((p) => ({ ...p, learning_goals: e.target.value }))}
                rows={3}
                className="w-full rounded-xl border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-400"
                placeholder="What do you want to achieve this year? Any career aspirations?"
              />
            </div>

            <div className="flex justify-end pt-2">
              <Button
                variant="primary"
                onClick={() =>
                  updateStudentProfile.mutate({
                    bio: form.bio,
                    interests: form.interests,
                    learning_goals: form.learning_goals,
                  })
                }
                loading={updateStudentProfile.isPending}
              >
                Save Student Profile
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
