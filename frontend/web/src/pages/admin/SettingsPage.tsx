/**
 * Admin Settings Page — school profile, academic year, user management
 */
import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuthStore } from "../../store/authStore";
import { Button, Input, Select, Badge } from "../../components/common";
import { useTitle } from "../../hooks";
import toast from "react-hot-toast";
import { api } from "../../api/client";

const schoolSchema = z.object({
  name: z.string().min(2),
  phone: z.string().min(7),
  email: z.string().email(),
  website: z.string().url().optional().or(z.literal("")),
  address: z.string().min(5),
  timezone: z.string(),
  academic_year_start_month: z.number().min(1).max(12),
});

type SchoolForm = z.infer<typeof schoolSchema>;

const TIMEZONES = ["UTC","America/New_York","America/Chicago","America/Los_Angeles","America/Toronto","Europe/London","Europe/Paris","Asia/Kolkata","Asia/Dhaka","Asia/Kathmandu","Asia/Dubai","Africa/Nairobi","Australia/Sydney"];
const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
type TabKey = "school" | "academic" | "notifications" | "integrations";
const TABS: {id: TabKey; label: string}[] = [
  {id:"school",label:"School Profile"},
  {id:"academic",label:"Academic Settings"},
  {id:"notifications",label:"Notifications"},
  {id:"integrations",label:"Integrations"},
];

export default function SettingsPage() {
  useTitle("Settings");
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<TabKey>("school");
  const [saving, setSaving] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<SchoolForm>({
    resolver: zodResolver(schoolSchema),
    defaultValues: {
      name: user?.school?.name ?? "",
      phone: user?.school?.phone ?? "",
      email: user?.school?.email ?? "",
      website: user?.school?.website ?? "",
      address: user?.school?.address ?? "",
      timezone: user?.school?.timezone ?? "UTC",
      academic_year_start_month: 9,
    },
  });

  const onSubmit = async (data: SchoolForm) => {
    setSaving(true);
    try {
      await api.patch(`/auth/schools/${user?.school?.id}/`, data);
      toast.success("School profile updated");
    } catch { toast.error("Failed to update settings"); }
    finally { setSaving(false); }
  };

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold text-slate-900">Settings</h1><p className="text-sm text-slate-500 mt-0.5">Configure your school&apos;s system preferences</p></div>
      <div className="card">
        <div className="border-b border-slate-100 px-6 flex overflow-x-auto">
          {TABS.map(t => <button key={t.id} onClick={() => setActiveTab(t.id)} className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab===t.id?"border-indigo-600 text-indigo-600":"border-transparent text-slate-500 hover:text-slate-800"}`}>{t.label}</button>)}
        </div>

        {activeTab === "school" && (
          <div className="card-body max-w-2xl">
            <h2 className="text-base font-semibold text-slate-800 mb-5">School Profile</h2>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <Input label="School Name" error={errors.name?.message} {...register("name")} />
              <div className="grid grid-cols-2 gap-4">
                <Input label="Phone" error={errors.phone?.message} {...register("phone")} />
                <Input label="Email" type="email" error={errors.email?.message} {...register("email")} />
              </div>
              <Input label="Website" error={errors.website?.message} {...register("website")} placeholder="https://yourschool.edu" />
              <Input label="Address" error={errors.address?.message} {...register("address")} />
              <Select label="Timezone" options={TIMEZONES.map(t => ({value:t,label:t}))} error={errors.timezone?.message} {...register("timezone")} />
              <div className="pt-2 flex justify-end">
                <Button type="submit" variant="primary" loading={saving}>Save Changes</Button>
              </div>
            </form>
          </div>
        )}

        {activeTab === "academic" && (
          <div className="card-body max-w-xl space-y-6">
            <h2 className="text-base font-semibold text-slate-800">Academic Year Settings</h2>
            <Select label="Academic Year Start Month" options={MONTHS.map((m,i)=>({value:i+1,label:m}))} />
            <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50">
              <div><p className="text-sm font-semibold text-slate-800">Auto-promote students</p><p className="text-xs text-slate-500">Automatically promote passing students to next grade at year end</p></div>
              <button className="h-6 w-11 rounded-full bg-indigo-500 relative flex-shrink-0"><span className="absolute right-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow" /></button>
            </div>
            <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50">
              <div><p className="text-sm font-semibold text-slate-800">Attendance lock after days</p><p className="text-xs text-slate-500">Prevent editing attendance records after this many days</p></div>
              <input type="number" defaultValue={3} className="w-20 rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-center focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            </div>
          </div>
        )}

        {activeTab === "notifications" && (
          <div className="card-body max-w-xl space-y-4">
            <h2 className="text-base font-semibold text-slate-800">Notification Channels</h2>
            {[
              { label: "Email Notifications", sub: "Send emails via SendGrid for important events", enabled: true },
              { label: "SMS Notifications", sub: "Send SMS alerts via Twilio for urgent messages", enabled: false },
              { label: "Push Notifications", sub: "Send mobile push via Firebase FCM", enabled: true },
              { label: "Absence Alerts", sub: "Notify parents immediately when student is absent", enabled: true },
              { label: "Fee Reminders", sub: "Send payment reminders 3 days before due date", enabled: true },
              { label: "Result Publications", sub: "Notify students/parents when report cards are published", enabled: true },
            ].map(({ label, sub, enabled }) => (
              <div key={label} className="flex items-center justify-between p-4 rounded-xl bg-slate-50">
                <div><p className="text-sm font-semibold text-slate-800">{label}</p><p className="text-xs text-slate-500">{sub}</p></div>
                <button className={`h-6 w-11 rounded-full relative flex-shrink-0 transition-colors ${enabled?"bg-indigo-500":"bg-slate-200"}`}>
                  <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-all ${enabled?"right-0.5":"left-0.5"}`} />
                </button>
              </div>
            ))}
          </div>
        )}

        {activeTab === "integrations" && (
          <div className="card-body max-w-xl space-y-4">
            <h2 className="text-base font-semibold text-slate-800">External Integrations</h2>
            {[
              { name: "Google Workspace", status: "connected", color: "green" as const },
              { name: "Microsoft 365", status: "disconnected", color: "slate" as const },
              { name: "Zoom", status: "connected", color: "green" as const },
              { name: "Stripe Payments", status: "connected", color: "green" as const },
              { name: "Twilio SMS", status: "disconnected", color: "slate" as const },
              { name: "Firebase Push", status: "connected", color: "green" as const },
            ].map(({ name, status, color }) => (
              <div key={name} className="flex items-center justify-between p-4 rounded-xl border border-slate-100">
                <div className="flex items-center gap-3">
                  <div className="h-9 w-9 rounded-lg bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-500">{name[0]}</div>
                  <div><p className="text-sm font-semibold text-slate-800">{name}</p><Badge color={color} dot>{status}</Badge></div>
                </div>
                <Button variant="secondary" size="sm">{status === "connected" ? "Configure" : "Connect"}</Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
