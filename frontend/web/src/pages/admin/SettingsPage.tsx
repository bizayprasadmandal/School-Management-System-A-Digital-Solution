/**
 * Admin Settings Page — school profile, academic year, user management
 */
import React, { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useAuthStore } from "../../store/authStore";
import { Button, Input, Select, Badge } from "../../components/common";
import { useTitle } from "../../hooks";
import EmailVerificationActions from "../../components/common/EmailVerificationActions";
import toast from "react-hot-toast";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
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

// ─── Integrations Tab ──────────────────────────────────────────────────────────

function ToggleSwitch({
  enabled,
  onChange,
  loading,
}: {
  enabled: boolean;
  onChange: (v: boolean) => void;
  loading: boolean;
}) {
  return (
    <button
      type="button"
      onClick={() => !loading && onChange(!enabled)}
      disabled={loading}
      className={`h-6 w-11 rounded-full relative flex-shrink-0 transition-colors ${
        loading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"
      } ${enabled ? "bg-indigo-500" : "bg-slate-300"}`}
    >
      <span
        className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-all ${
          enabled ? "right-0.5" : "left-0.5"
        }`}
      />
    </button>
  );
}

function PaymentGatewaysSection() {
  const qc = useQueryClient();

  const { data: gatewayConfig, isLoading } = useQuery<{
    stripe_enabled: boolean;
    khalti_enabled: boolean;
    esewa_enabled: boolean;
  }>({
    queryKey: ["gateway-config"],
    queryFn: () => api.get("/fees/gateway-config/"),
    staleTime: 30_000,
  });

  const updateConfig = useMutation({
    mutationFn: (data: Record<string, boolean>) =>
      api.post("/fees/gateway-config/", data),
    onSuccess: () => {
      toast.success("Payment gateway settings updated");
      qc.invalidateQueries({ queryKey: ["gateway-config"] });
      qc.invalidateQueries({ queryKey: ["enabled-gateways"] });
    },
    onError: () => toast.error("Failed to update gateway settings"),
  });

  const gateways = [
    {
      key: "stripe_enabled" as const,
      name: "Stripe",
      icon: "💳",
      description: "Accept international credit/debit card payments (Visa, Mastercard, Amex)",
      enabled: gatewayConfig?.stripe_enabled ?? true,
    },
    {
      key: "khalti_enabled" as const,
      name: "Khalti",
      icon: "💰",
      description: "Accept payments via Khalti wallet, Mobile Banking, and cards",
      enabled: gatewayConfig?.khalti_enabled ?? false,
    },
    {
      key: "esewa_enabled" as const,
      name: "eSewa",
      icon: "🏦",
      description: "Accept payments via eSewa wallet and connected bank accounts",
      enabled: gatewayConfig?.esewa_enabled ?? false,
    },
  ];

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
          Payment Gateways
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
          Enable or disable online payment methods for students and parents.
        </p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-4">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
        </div>
      ) : (
        <div className="space-y-3">
          {gateways.map(({ key, name, icon, description, enabled }) => (
            <div
              key={key}
              className="flex items-center justify-between p-4 rounded-xl border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800"
            >
              <div className="flex items-start gap-3 flex-1 min-w-0">
                <span className="text-xl flex-shrink-0 mt-0.5">{icon}</span>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                    {name}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    {description}
                  </p>
                </div>
              </div>
              <ToggleSwitch
                enabled={enabled}
                onChange={(v) => updateConfig.mutate({ [key]: v })}
                loading={updateConfig.isPending}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function IntegrationsTab() {
  const navigate = useNavigate();

  // Dynamically check Zoom connection status
  const { data: zoomStatus } = useQuery<{ status: string; detail: string }>({
    queryKey: ["zoom-connection-status"],
    queryFn: () => api.get("/conferences/zoom/connection/"),
    staleTime: 30_000,
    retry: 1,
  });

  const zoomConnected = zoomStatus?.status === "connected";

  const integrations = [
    { name: "Google Workspace", status: "connected" as const, color: "green" as const, description: "Email & calendar sync" },
    { name: "Microsoft 365", status: "disconnected" as const, color: "slate" as const, description: "Office integration" },
    {
      name: "Zoom",
      status: zoomConnected ? ("connected" as const) : ("disconnected" as const),
      color: zoomConnected ? ("green" as const) : ("slate" as const),
      description: "Video conferencing (Server-to-Server OAuth)",
      configPath: "/admin/zoom-integration",
    },
    { name: "Twilio", status: "disconnected" as const, color: "slate" as const, description: "SMS notifications" },
    { name: "Firebase", status: "disconnected" as const, color: "slate" as const, description: "Push notifications" },
  ];

  return (
    <div className="p-5 max-w-xl space-y-8">
      {/* External Integrations */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">External Integrations</h2>
        {integrations.map(({ name, status, color, description, configPath }) => (
          <div key={name} className="flex items-center justify-between p-4 rounded-xl border border-slate-100 dark:border-slate-700">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-500 dark:text-slate-400">
                {name[0]}
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{name}</p>
                <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{description}</p>
                <Badge color={color} dot>{status}</Badge>
              </div>
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => configPath && navigate(configPath)}
            >
              {configPath ? "Configure" : status === "connected" ? "Configure" : "Connect"}
            </Button>
          </div>
        ))}
      </div>

      {/* Separator */}
      <hr className="border-slate-200 dark:border-slate-700" />

      {/* Payment Gateways */}
      <PaymentGatewaysSection />
    </div>
  );
}

const TIMEZONES = ["UTC","America/New_York","America/Chicago","America/Los_Angeles","America/Toronto","Europe/London","Europe/Paris","Asia/Kolkata","Asia/Dhaka","Asia/Kathmandu","Asia/Dubai","Africa/Nairobi","Australia/Sydney"];
const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
type TabKey = "school" | "academic" | "notifications" | "integrations" | "security";
const TABS: {id: TabKey; label: string}[] = [
  {id:"school",label:"School Profile"},
  {id:"academic",label:"Academic Settings"},
  {id:"notifications",label:"Notifications"},
  {id:"integrations",label:"Integrations"},
  {id:"security",label:"Security"},
];

export default function SettingsPage() {
  useTitle("Settings");
  const { user } = useAuthStore();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabKey>(() => {
    // Support ?tab=security for deep-linking from sidebar verification dot
    const tabParam = searchParams.get("tab");
    if (tabParam && TABS.some((t) => t.id === tabParam)) {
      return tabParam as TabKey;
    }
    return "school";
  });
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
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
        <div className="border-b border-slate-100 px-6 flex overflow-x-auto">
          {TABS.map(t => <button key={t.id} onClick={() => setActiveTab(t.id)} className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab===t.id?"border-indigo-600 text-indigo-600":"border-transparent text-slate-500 hover:text-slate-800"}`}>{t.label}</button>)}
        </div>

        {activeTab === "school" && (
          <div className="p-5 max-w-2xl">
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
          <div className="p-5 max-w-xl space-y-6">
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
          <div className="p-5 max-w-xl space-y-4">
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

        {activeTab === "security" && (
          <div className="p-5 max-w-xl space-y-6">
            <h2 className="text-base font-semibold text-slate-800">Account Security</h2>

            {/* Email Verification */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-700 p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2.5 mb-1">
                    <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                      Email Verification
                    </h3>
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                        user?.email_verified
                          ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                          : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                      }`}
                    >
                      <span
                        className={`inline-block h-1.5 w-1.5 rounded-full ${
                          user?.email_verified ? "bg-green-500" : "bg-amber-500"
                        }`}
                      />
                      {user?.email_verified ? "Verified" : "Not Verified"}
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {user?.email}
                  </p>
                  {!user?.email_verified && (
                    <p className="text-xs text-amber-600 dark:text-amber-400 mt-2">
                      Verify your email to unlock all features and receive
                      important notifications.
                    </p>
                  )}
                  {user?.email_verified && (
                    <p className="text-xs text-green-600 dark:text-green-400 mt-2">
                      Your email is verified. You have full access to all
                      features.
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div className="shrink-0">
                  <EmailVerificationActions />
                </div>
              </div>
            </div>

            {/* Account Info */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-700 p-5">
              <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-3">
                Account Information
              </h3>
              <dl className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-slate-500 dark:text-slate-400">Email</dt>
                  <dd className="text-slate-800 dark:text-slate-200 font-medium">{user?.email}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500 dark:text-slate-400">Role</dt>
                  <dd className="text-slate-800 dark:text-slate-200 font-medium capitalize">
                    {user?.role?.replace("_", " ")}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500 dark:text-slate-400">Joined</dt>
                  <dd className="text-slate-800 dark:text-slate-200 font-medium">
                    {user?.date_joined
                      ? new Date(user.date_joined).toLocaleDateString()
                      : "—"}
                  </dd>
                </div>
                <div className="flex justify-between items-center">
                  <dt className="text-slate-500 dark:text-slate-400">Two-Factor Auth</dt>
                  <dd className="flex items-center gap-2">
                    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                      user?.two_factor_enabled
                        ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                        : "bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-400"
                    }`}>
                      <span className={`inline-block h-1.5 w-1.5 rounded-full ${
                        user?.two_factor_enabled ? "bg-green-500" : "bg-slate-400"
                      }`} />
                      {user?.two_factor_enabled ? "Enabled" : "Not configured"}
                    </span>
                    <button
                      type="button"
                      onClick={() => navigate("../setup-2fa", { relative: "path" })}
                      className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
                    >
                      {user?.two_factor_enabled ? "Manage" : "Configure"}
                    </button>
                  </dd>
                </div>
                {user?.two_factor_enabled && user?.backup_codes_remaining !== null && (
                  <div className="flex justify-between items-center mt-2 pt-2 border-t border-slate-100 dark:border-slate-700">
                    <dt className="text-slate-500 dark:text-slate-400 text-sm">Backup codes remaining</dt>
                    <dd className="flex items-center gap-2">
                      <span
                        className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                          user.backup_codes_remaining <= 2
                            ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                            : user.backup_codes_remaining <= 5
                              ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                              : "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                        }`}
                      >
                        <span
                          className={`inline-block h-1.5 w-1.5 rounded-full ${
                            user.backup_codes_remaining <= 2
                              ? "bg-red-500"
                              : user.backup_codes_remaining <= 5
                                ? "bg-amber-500"
                                : "bg-green-500"
                          }`}
                        />
                        {user.backup_codes_remaining} / 8
                      </span>
                      <button
                        type="button"
                        onClick={() => navigate("../setup-2fa", { relative: "path" })}
                        className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
                      >
                        Regenerate
                      </button>
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          </div>
        )}

        {activeTab === "integrations" && (
          <IntegrationsTab />
        )}
      </div>
    </div>
  );
}
