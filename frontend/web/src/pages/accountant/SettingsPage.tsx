/**
 * Accountant Settings Page — profile editing and preferences
 */
import React from "react";
import ProfileSettingsSection from "../../components/common/ProfileSettingsSection";
import { useTitle } from "../../hooks";

export default function AccountantSettingsPage() {
  useTitle("Settings");
  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Settings</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage your profile and preferences</p>
      </div>
      <ProfileSettingsSection basePath="/accountant" accent="amber" />
    </div>
  );
}
