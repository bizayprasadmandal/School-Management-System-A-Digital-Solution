/**
 * Account Security — Admin page for sessions, tokens, devices, security
 * policies, API keys/usage, and audit & activity monitoring.
 */
import React, { useState, useMemo, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  ServerStackIcon,
  KeyIcon,
  DevicePhoneMobileIcon,
  ShieldCheckIcon,
  LockClosedIcon,
  FingerPrintIcon,
  GlobeAltIcon,
  ChartBarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  UserCircleIcon,
  CodeBracketIcon,
  AdjustmentsHorizontalIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Pagination } from "../../components/common";
import { BulkActionBar } from "../../components/common/BulkActionBar";
import { InfiniteScroll } from "../../components/common/InfiniteScroll";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import { useKeyboardShortcuts } from "../../hooks/useKeyboardShortcuts";
import { useTitle } from "../../hooks";
import { toCsv, downloadCsv } from "../../utils";

// ─── Types ───────────────────────────────────────────────────────────────────

interface UserSession {
  id: string;
  user: string;
  user_name: string | null;
  user_email: string;
  refresh_token_jti: string;
  device_info: Record<string, unknown>;
  ip_address: string | null;
  created_at: string;
  last_used: string;
  is_active: boolean;
}

interface SessionToken {
  id: string;
  user: string;
  user_name: string | null;
  user_email: string;
  token_type: string;
  token_type_display: string;
  status: string;
  status_display: string;
  token_hash: string;
  issued_at: string;
  expires_at: string;
  last_used_at: string | null;
  device_info: Record<string, unknown>;
  ip_address: string | null;
  revoked_at: string | null;
  revocation_reason: string;
  created_at: string;
}

interface Device {
  id: string;
  user: string;
  user_name: string | null;
  user_email: string;
  device_name: string;
  device_type: string;
  device_type_display: string;
  device_id: string;
  fingerprint: string;
  ip_address: string | null;
  location: string;
  status: string;
  status_display: string;
  is_active: boolean;
  last_seen: string;
  created_at: string;
  trusted_at: string | null;
  blocked_at: string | null;
}

interface SecurityPolicy {
  id: string;
  school: string;
  name: string;
  policy_type: string;
  policy_type_display: string;
  description: string;
  settings: Record<string, unknown>;
  min_length: number | null;
  require_uppercase: boolean;
  require_lowercase: boolean;
  require_numbers: boolean;
  require_special: boolean;
  max_age_days: number | null;
  history_count: number | null;
  session_timeout_minutes: number | null;
}

interface PasswordPolicy {
  id: string;
  school: string;
  min_length: number;
  max_length: number;
  require_uppercase: boolean;
  require_lowercase: boolean;
  require_digit: boolean;
  require_special_char: boolean;
  special_chars: string;
  prevent_REUSE: number;
  max_age_days: number;
  lockout_attempts: number;
  lockout_duration_minutes: number;
  is_active: boolean;
}

interface SessionPolicy {
  id: string;
  school: string;
  session_timeout_minutes: number;
  absolute_timeout_hours: number;
  idle_timeout_minutes: number;
  max_concurrent_sessions: number;
  enforce_single_session: boolean;
  require_reauthentication: boolean;
  reauthentication_interval_minutes: number;
  remember_me_days: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface IPWhitelistEntry {
  id: string;
  school: string;
  ip_address: string;
  ip_range: string;
  description: string;
  access_level: string;
  access_level_display: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface APIKey {
  id: string;
  school: string;
  user: string;
  user_name: string | null;
  user_email: string;
  name: string;
  description: string;
  key_prefix: string;
  key_hash: string;
  scopes: string[];
  rate_limit: number;
  status: string;
  status_display: string;
  expires_at: string | null;
  last_used_at: string | null;
  last_used_ip: string | null;
}

interface APIUsageLog {
  id: string;
  api_key: string;
  api_key_name: string;
  endpoint: string;
  method: string;
  status_code: number;
  response_time_ms: number;
  request_size_bytes: number;
  response_size_bytes: number;
  ip_address: string | null;
  user_agent: string;
  error_message: string;
  timestamp: string;
}

interface AuditLog {
  id: string;
  school: string | null;
  user: string | null;
  user_name: string | null;
  user_email: string | null;
  action: string;
  resource_type: string;
  resource_id: string;
  changes: Record<string, unknown>;
  ip_address: string | null;
  user_agent: string;
  timestamp: string;
}

interface LoginHistory {
  id: string;
  user: string | null;
  user_name: string | null;
  email: string;
  login_type: string;
  login_type_display: string;
  status: string;
  status_display: string;
  ip_address: string | null;
  user_agent: string;
  device_info: Record<string, unknown>;
  location: string;
  country: string;
  city: string;
  failure_reason: string;
  session_id: string;
  created_at: string;
}

interface LoginAttempt {
  id: string;
  school: string;
  username: string;
  email: string;
  status: string;
  failure_reason: string;
  ip_address: string | null;
  user_agent: string;
  device_info: Record<string, unknown>;
  city: string;
  country: string;
  attempted_at: string;
  user: string | null;
}

interface UserActivity {
  id: string;
  user: string;
  user_name: string | null;
  user_email: string;
  activity_type: string;
  activity_type_display: string;
  description: string;
  resource_type: string;
  resource_id: string;
  ip_address: string | null;
  user_agent: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  inactive: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  trusted: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  pending: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  blocked: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  success: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  locked: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  expired: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  revoked: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  blacklisted: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  pending_2fa: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
};

const POLICY_TYPE_OPTIONS: readonly (readonly [string, string])[] = [
  ["password", "Password Policy"],
  ["session", "Session Policy"],
  ["login", "Login Policy"],
  ["mfa", "Multi-Factor Authentication"],
  ["api", "API Access Policy"],
  ["ip", "IP Policy"],
];

const ACCESS_LEVEL_OPTIONS: readonly (readonly [string, string])[] = [
  ["admin", "Admin Only"],
  ["staff", "Staff Only"],
  ["all", "All Users"],
  ["api", "API Access"],
];

const API_KEY_STATUS_OPTIONS: readonly (readonly [string, string])[] = [
  ["active", "Active"],
  ["revoked", "Revoked"],
  ["expired", "Expired"],
];

// ─── Tabs config ─────────────────────────────────────────────────────────────

type TabType =
  | "sessions"
  | "tokens"
  | "devices"
  | "security"
  | "password"
  | "sessionpol"
  | "whitelist"
  | "apikeys"
  | "usage"
  | "audit"
  | "logins"
  | "attempts"
  | "activity";

const TABS: {
  key: TabType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  { key: "sessions", label: "Sessions", icon: ServerStackIcon },
  { key: "tokens", label: "Session Tokens", icon: KeyIcon },
  { key: "devices", label: "Devices", icon: DevicePhoneMobileIcon },
  { key: "security", label: "Security Policy", icon: ShieldCheckIcon },
  { key: "password", label: "Password Policy", icon: LockClosedIcon },
  { key: "sessionpol", label: "Session Policy", icon: ClockIcon },
  { key: "whitelist", label: "IP Whitelist", icon: GlobeAltIcon },
  { key: "apikeys", label: "API Keys", icon: CodeBracketIcon },
  { key: "usage", label: "API Usage", icon: ChartBarIcon },
  { key: "audit", label: "Audit Log", icon: AdjustmentsHorizontalIcon },
  { key: "logins", label: "Login History", icon: UserCircleIcon },
  { key: "attempts", label: "Login Attempts", icon: ExclamationTriangleIcon },
  { key: "activity", label: "User Activity", icon: FingerPrintIcon },
];

const TAB_LABELS: Record<TabType, { singular: string; plural: string }> = {
  sessions: { singular: "session", plural: "sessions" },
  tokens: { singular: "token", plural: "tokens" },
  devices: { singular: "device", plural: "devices" },
  security: { singular: "security policy", plural: "security policies" },
  password: { singular: "password policy", plural: "password policies" },
  sessionpol: { singular: "session policy", plural: "session policies" },
  whitelist: { singular: "whitelist entry", plural: "whitelist entries" },
  apikeys: { singular: "API key", plural: "API keys" },
  usage: { singular: "usage log", plural: "usage logs" },
  audit: { singular: "audit entry", plural: "audit entries" },
  logins: { singular: "login", plural: "logins" },
  attempts: { singular: "attempt", plural: "attempts" },
  activity: { singular: "activity", plural: "activities" },
};

// ─── Skeleton ────────────────────────────────────────────────────────────────

function CardSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div
          key={i}
          className="relative h-32 overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
        >
          <div
            className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-slate-200/50 to-transparent dark:via-slate-600/30"
            style={{ backgroundSize: "200% 100%" }}
          />
        </div>
      ))}
    </div>
  );
}

// ─── Form helpers ────────────────────────────────────────────────────────────

const inputCls =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200";
const labelCls = "mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300";

function SelectField({
  label,
  value,
  options,
  onChange,
  required,
}: {
  label: string;
  value: string;
  options: readonly (readonly [string, string])[];
  onChange: (v: string) => void;
  required?: boolean;
}) {
  return (
    <div>
      <label className={labelCls}>
        {label}
        {required && " *"}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={inputCls}
        required={required}
      >
        {options.map(([v, l]) => (
          <option key={v} value={v}>
            {l}
          </option>
        ))}
      </select>
    </div>
  );
}

function Badge({ value, colors }: { value: string; colors: Record<string, string> }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
        colors[value] ?? "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
      }`}
    >
      {value.replace(/_/g, " ")}
    </span>
  );
}

function Toggle({ checked, onChange }: { checked: boolean; onChange: () => void }) {
  return (
    <button
      type="button"
      onClick={onChange}
      className={`relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors ${
        checked ? "bg-indigo-600" : "bg-slate-300 dark:bg-slate-600"
      }`}
      aria-label={checked ? "Active" : "Inactive"}
    >
      <span
        className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
          checked ? "translate-x-[18px]" : "translate-x-[3px]"
        }`}
      />
    </button>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function AccountSecurityPage() {
  useTitle("Account Security");
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>("sessions");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const searchRef = useRef<HTMLInputElement>(null);

  // Modals
  const [showSecurityForm, setShowSecurityForm] = useState(false);
  const [editingSecurity, setEditingSecurity] = useState<SecurityPolicy | null>(null);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [editingPassword, setEditingPassword] = useState<PasswordPolicy | null>(null);
  const [showSessionPolForm, setShowSessionPolForm] = useState(false);
  const [editingSessionPol, setEditingSessionPol] = useState<SessionPolicy | null>(null);
  const [showWhitelistForm, setShowWhitelistForm] = useState(false);
  const [editingWhitelist, setEditingWhitelist] = useState<IPWhitelistEntry | null>(null);
  const [showAPIKeyForm, setShowAPIKeyForm] = useState(false);
  const [editingAPIKey, setEditingAPIKey] = useState<APIKey | null>(null);

  // ── Data fetching ───────────────────────────────────────────────────────

  const { data: sessions = [], isLoading: sessionsLoading } = useQuery({
    queryKey: ["auth-sessions"],
    queryFn: async () => {
      const res = await api.get<{ results: UserSession[] }>("/auth/user-session/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: tokens = [], isLoading: tokensLoading } = useQuery({
    queryKey: ["auth-tokens"],
    queryFn: async () => {
      const res = await api.get<{ results: SessionToken[] }>("/auth/session-token/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: devices = [], isLoading: devicesLoading } = useQuery({
    queryKey: ["auth-devices"],
    queryFn: async () => {
      const res = await api.get<{ results: Device[] }>("/auth/device-management/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: securityPolicies = [], isLoading: securityLoading } = useQuery({
    queryKey: ["auth-security"],
    queryFn: async () => {
      const res = await api.get<{ results: SecurityPolicy[] }>("/auth/security-policy/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: passwordPolicies = [], isLoading: passwordLoading } = useQuery({
    queryKey: ["auth-password"],
    queryFn: async () => {
      const res = await api.get<{ results: PasswordPolicy[] }>("/auth/password-policy/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: sessionPolicies = [], isLoading: sessionPolLoading } = useQuery({
    queryKey: ["auth-sessionpol"],
    queryFn: async () => {
      const res = await api.get<{ results: SessionPolicy[] }>("/auth/session-policy/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: whitelist = [], isLoading: whitelistLoading } = useQuery({
    queryKey: ["auth-whitelist"],
    queryFn: async () => {
      const res = await api.get<{ results: IPWhitelistEntry[] }>("/auth/i-p-whitelist/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: apiKeys = [], isLoading: apiKeysLoading } = useQuery({
    queryKey: ["auth-apikeys"],
    queryFn: async () => {
      const res = await api.get<{ results: APIKey[] }>("/auth/a-p-i-key/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: usageLogs = [], isLoading: usageLoading } = useQuery({
    queryKey: ["auth-usage"],
    queryFn: async () => {
      const res = await api.get<{ results: APIUsageLog[] }>("/auth/a-p-i-usage-log/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: auditLogs = [], isLoading: auditLoading } = useQuery({
    queryKey: ["auth-audit"],
    queryFn: async () => {
      const res = await api.get<{ results: AuditLog[] }>("/auth/audit-log/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: loginHistory = [], isLoading: loginsLoading } = useQuery({
    queryKey: ["auth-logins"],
    queryFn: async () => {
      const res = await api.get<{ results: LoginHistory[] }>("/auth/login-history/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: loginAttempts = [], isLoading: attemptsLoading } = useQuery({
    queryKey: ["auth-attempts"],
    queryFn: async () => {
      const res = await api.get<{ results: LoginAttempt[] }>("/auth/login-attempt/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: activities = [], isLoading: activityLoading } = useQuery({
    queryKey: ["auth-activity"],
    queryFn: async () => {
      const res = await api.get<{ results: UserActivity[] }>("/auth/user-activity/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  // ── Mutations ───────────────────────────────────────────────────────────

  const deleteSession = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/user-session/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["auth-sessions"] });
      toast.success("Session revoked");
    },
  });

  const toggleSession = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      api.patch(`/auth/user-session/${id}/`, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["auth-sessions"] }),
  });

  const deleteToken = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/session-token/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["auth-tokens"] });
      toast.success("Token revoked");
    },
  });

  const deleteDevice = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/device-management/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["auth-devices"] });
      toast.success("Device removed");
    },
  });

  const toggleDevice = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      api.patch(`/auth/device-management/${id}/`, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["auth-devices"] }),
  });

  const deleteWhitelist = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/i-p-whitelist/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["auth-whitelist"] });
      toast.success("Whitelist entry removed");
    },
  });

  const deleteAPIKey = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/a-p-i-key/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["auth-apikeys"] });
      toast.success("API key revoked");
    },
  });

  const toggleAPIKey = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.patch(`/auth/a-p-i-key/${id}/`, { status }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["auth-apikeys"] }),
  });

  const deleteUsage = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/a-p-i-usage-log/${id}/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["auth-usage"] }),
  });

  const deleteAudit = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/audit-log/${id}/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["auth-audit"] }),
  });

  const deleteLogin = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/login-history/${id}/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["auth-logins"] }),
  });

  const deleteAttempt = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/login-attempt/${id}/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["auth-attempts"] }),
  });

  const deleteActivity = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/user-activity/${id}/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["auth-activity"] }),
  });

  // ── Filtering ───────────────────────────────────────────────────────────

  const filteredSessions = useMemo(() => {
    if (!search.trim()) return sessions;
    const q = search.toLowerCase();
    return sessions.filter(
      (s) =>
        (s.user_name ?? "").toLowerCase().includes(q) ||
        s.user_email.toLowerCase().includes(q) ||
        (s.ip_address ?? "").toLowerCase().includes(q),
    );
  }, [sessions, search]);

  const filteredTokens = useMemo(() => {
    if (!search.trim()) return tokens;
    const q = search.toLowerCase();
    return tokens.filter(
      (t) =>
        (t.user_name ?? "").toLowerCase().includes(q) ||
        t.user_email.toLowerCase().includes(q) ||
        t.token_type_display.toLowerCase().includes(q) ||
        t.status_display.toLowerCase().includes(q),
    );
  }, [tokens, search]);

  const filteredDevices = useMemo(() => {
    if (!search.trim()) return devices;
    const q = search.toLowerCase();
    return devices.filter(
      (d) =>
        d.device_name.toLowerCase().includes(q) ||
        d.device_type.toLowerCase().includes(q) ||
        (d.user_name ?? "").toLowerCase().includes(q) ||
        d.user_email.toLowerCase().includes(q) ||
        d.location.toLowerCase().includes(q),
    );
  }, [devices, search]);

  const filteredSecurity = useMemo(() => {
    if (!search.trim()) return securityPolicies;
    const q = search.toLowerCase();
    return securityPolicies.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.policy_type_display.toLowerCase().includes(q) ||
        p.description.toLowerCase().includes(q),
    );
  }, [securityPolicies, search]);

  const filteredPassword = useMemo(() => {
    if (!search.trim()) return passwordPolicies;
    return passwordPolicies;
  }, [passwordPolicies, search]);

  const filteredSessionPol = useMemo(() => {
    if (!search.trim()) return sessionPolicies;
    return sessionPolicies;
  }, [sessionPolicies, search]);

  const filteredWhitelist = useMemo(() => {
    if (!search.trim()) return whitelist;
    const q = search.toLowerCase();
    return whitelist.filter(
      (w) =>
        w.ip_address.toLowerCase().includes(q) ||
        w.ip_range.toLowerCase().includes(q) ||
        w.description.toLowerCase().includes(q) ||
        w.access_level_display.toLowerCase().includes(q),
    );
  }, [whitelist, search]);

  const filteredAPIKeys = useMemo(() => {
    if (!search.trim()) return apiKeys;
    const q = search.toLowerCase();
    return apiKeys.filter(
      (k) =>
        k.name.toLowerCase().includes(q) ||
        k.description.toLowerCase().includes(q) ||
        k.key_prefix.toLowerCase().includes(q) ||
        (k.user_name ?? "").toLowerCase().includes(q),
    );
  }, [apiKeys, search]);

  const filteredUsage = useMemo(() => {
    if (!search.trim()) return usageLogs;
    const q = search.toLowerCase();
    return usageLogs.filter(
      (u) =>
        u.endpoint.toLowerCase().includes(q) ||
        u.method.toLowerCase().includes(q) ||
        u.api_key_name.toLowerCase().includes(q) ||
        String(u.status_code).includes(q),
    );
  }, [usageLogs, search]);

  const filteredAudit = useMemo(() => {
    if (!search.trim()) return auditLogs;
    const q = search.toLowerCase();
    return auditLogs.filter(
      (a) =>
        a.action.toLowerCase().includes(q) ||
        a.resource_type.toLowerCase().includes(q) ||
        (a.user_name ?? "").toLowerCase().includes(q) ||
        (a.user_email ?? "").toLowerCase().includes(q) ||
        (a.ip_address ?? "").toLowerCase().includes(q),
    );
  }, [auditLogs, search]);

  const filteredLogins = useMemo(() => {
    if (!search.trim()) return loginHistory;
    const q = search.toLowerCase();
    return loginHistory.filter(
      (l) =>
        l.email.toLowerCase().includes(q) ||
        (l.user_name ?? "").toLowerCase().includes(q) ||
        l.login_type_display.toLowerCase().includes(q) ||
        (l.ip_address ?? "").toLowerCase().includes(q) ||
        l.city.toLowerCase().includes(q),
    );
  }, [loginHistory, search]);

  const filteredAttempts = useMemo(() => {
    if (!search.trim()) return loginAttempts;
    const q = search.toLowerCase();
    return loginAttempts.filter(
      (a) =>
        a.username.toLowerCase().includes(q) ||
        a.email.toLowerCase().includes(q) ||
        a.status.toLowerCase().includes(q) ||
        (a.ip_address ?? "").toLowerCase().includes(q),
    );
  }, [loginAttempts, search]);

  const filteredActivity = useMemo(() => {
    if (!search.trim()) return activities;
    const q = search.toLowerCase();
    return activities.filter(
      (a) =>
        a.activity_type_display.toLowerCase().includes(q) ||
        a.description.toLowerCase().includes(q) ||
        (a.user_name ?? "").toLowerCase().includes(q) ||
        a.user_email.toLowerCase().includes(q),
    );
  }, [activities, search]);

  const allFiltered =
    activeTab === "sessions"
      ? filteredSessions
      : activeTab === "tokens"
        ? filteredTokens
        : activeTab === "devices"
          ? filteredDevices
          : activeTab === "security"
            ? filteredSecurity
            : activeTab === "password"
              ? filteredPassword
              : activeTab === "sessionpol"
                ? filteredSessionPol
                : activeTab === "whitelist"
                  ? filteredWhitelist
                  : activeTab === "apikeys"
                    ? filteredAPIKeys
                    : activeTab === "usage"
                      ? filteredUsage
                      : activeTab === "audit"
                        ? filteredAudit
                        : activeTab === "logins"
                          ? filteredLogins
                          : activeTab === "attempts"
                            ? filteredAttempts
                            : filteredActivity;

  const PAGE_SIZE = 12;
  const totalPages = Math.max(1, Math.ceil(allFiltered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const paginated = allFiltered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);
  const [infinitePage, setInfinitePage] = useState(1);
  const infiniteItems: { id: string }[] = allFiltered.slice(0, infinitePage * PAGE_SIZE);
  const infiniteHasMore = infiniteItems.length < allFiltered.length;

  const visibleItems = viewMode === "pagination" ? paginated : infiniteItems;

  // ── Bulk selection ──────────────────────────────────────────────────────

  const bulk = useBulkSelect<{ id: string }>(allFiltered);
  const activeDelete =
    deleteSession.isPending ||
    deleteToken.isPending ||
    deleteDevice.isPending ||
    deleteWhitelist.isPending ||
    deleteAPIKey.isPending ||
    deleteUsage.isPending ||
    deleteAudit.isPending ||
    deleteLogin.isPending ||
    deleteAttempt.isPending ||
    deleteActivity.isPending;

  const handleBulkDelete = async () => {
    if (bulk.selectedCount === 0) return;
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(
        bulk.selectedArray.map((id) => {
          if (activeTab === "sessions") return deleteSession.mutateAsync(id);
          if (activeTab === "tokens") return deleteToken.mutateAsync(id);
          if (activeTab === "devices") return deleteDevice.mutateAsync(id);
          if (activeTab === "whitelist") return deleteWhitelist.mutateAsync(id);
          if (activeTab === "apikeys") return deleteAPIKey.mutateAsync(id);
          if (activeTab === "usage") return deleteUsage.mutateAsync(id);
          if (activeTab === "audit") return deleteAudit.mutateAsync(id);
          if (activeTab === "logins") return deleteLogin.mutateAsync(id);
          if (activeTab === "attempts") return deleteAttempt.mutateAsync(id);
          return deleteActivity.mutateAsync(id);
        }),
      );
      bulk.clear();
      toast.success("Selected items deleted");
    } catch {
      toast.error("Some deletions failed");
    }
  };

  // ── Export ──────────────────────────────────────────────────────────────

  const handleExport = () => {
    const now = dayjs().format("YYYY-MM-DD");
    if (activeTab === "sessions") {
      downloadCsv(
        toCsv(filteredSessions as unknown as Record<string, unknown>[], [
          { key: "user_email", label: "User" },
          { key: "ip_address", label: "IP" },
          { key: "created_at", label: "Created" },
          { key: "last_used", label: "Last Used" },
          { key: "is_active", label: "Active" },
        ]),
        `auth-sessions-${now}.csv`,
      );
    } else if (activeTab === "tokens") {
      downloadCsv(
        toCsv(filteredTokens as unknown as Record<string, unknown>[], [
          { key: "user_email", label: "User" },
          { key: "token_type_display", label: "Type" },
          { key: "status_display", label: "Status" },
          { key: "expires_at", label: "Expires" },
        ]),
        `auth-tokens-${now}.csv`,
      );
    } else if (activeTab === "devices") {
      downloadCsv(
        toCsv(filteredDevices as unknown as Record<string, unknown>[], [
          { key: "user_email", label: "User" },
          { key: "device_name", label: "Device" },
          { key: "device_type", label: "Type" },
          { key: "status_display", label: "Status" },
          { key: "last_seen", label: "Last Seen" },
        ]),
        `auth-devices-${now}.csv`,
      );
    } else if (activeTab === "security") {
      downloadCsv(
        toCsv(filteredSecurity as unknown as Record<string, unknown>[], [
          { key: "name", label: "Name" },
          { key: "policy_type_display", label: "Type" },
          { key: "min_length", label: "Min Length" },
          { key: "max_age_days", label: "Max Age Days" },
        ]),
        `auth-security-${now}.csv`,
      );
    } else if (activeTab === "password") {
      downloadCsv(
        toCsv(filteredPassword as unknown as Record<string, unknown>[], [
          { key: "min_length", label: "Min Length" },
          { key: "max_length", label: "Max Length" },
          { key: "require_uppercase", label: "Uppercase" },
          { key: "require_digit", label: "Digit" },
          { key: "max_age_days", label: "Max Age Days" },
          { key: "lockout_attempts", label: "Lockout Attempts" },
        ]),
        `auth-password-policy-${now}.csv`,
      );
    } else if (activeTab === "sessionpol") {
      downloadCsv(
        toCsv(filteredSessionPol as unknown as Record<string, unknown>[], [
          { key: "session_timeout_minutes", label: "Timeout (min)" },
          { key: "absolute_timeout_hours", label: "Absolute (hrs)" },
          { key: "max_concurrent_sessions", label: "Max Concurrent" },
          { key: "enforce_single_session", label: "Single Session" },
          { key: "is_active", label: "Active" },
        ]),
        `auth-session-policy-${now}.csv`,
      );
    } else if (activeTab === "whitelist") {
      downloadCsv(
        toCsv(filteredWhitelist as unknown as Record<string, unknown>[], [
          { key: "ip_address", label: "IP" },
          { key: "ip_range", label: "Range" },
          { key: "description", label: "Description" },
          { key: "access_level_display", label: "Access" },
          { key: "is_active", label: "Active" },
        ]),
        `auth-whitelist-${now}.csv`,
      );
    } else if (activeTab === "apikeys") {
      downloadCsv(
        toCsv(filteredAPIKeys as unknown as Record<string, unknown>[], [
          { key: "name", label: "Name" },
          { key: "key_prefix", label: "Prefix" },
          { key: "status_display", label: "Status" },
          { key: "rate_limit", label: "Rate Limit" },
          { key: "last_used_at", label: "Last Used" },
        ]),
        `auth-apikeys-${now}.csv`,
      );
    } else if (activeTab === "usage") {
      downloadCsv(
        toCsv(filteredUsage as unknown as Record<string, unknown>[], [
          { key: "method", label: "Method" },
          { key: "endpoint", label: "Endpoint" },
          { key: "status_code", label: "Status" },
          { key: "response_time_ms", label: "Time (ms)" },
          { key: "api_key_name", label: "API Key" },
          { key: "timestamp", label: "Time" },
        ]),
        `auth-usage-${now}.csv`,
      );
    } else if (activeTab === "audit") {
      downloadCsv(
        toCsv(filteredAudit as unknown as Record<string, unknown>[], [
          { key: "user_email", label: "User" },
          { key: "action", label: "Action" },
          { key: "resource_type", label: "Resource" },
          { key: "ip_address", label: "IP" },
          { key: "timestamp", label: "Time" },
        ]),
        `auth-audit-${now}.csv`,
      );
    } else if (activeTab === "logins") {
      downloadCsv(
        toCsv(filteredLogins as unknown as Record<string, unknown>[], [
          { key: "email", label: "Email" },
          { key: "login_type_display", label: "Type" },
          { key: "status_display", label: "Status" },
          { key: "ip_address", label: "IP" },
          { key: "created_at", label: "Time" },
        ]),
        `auth-logins-${now}.csv`,
      );
    } else if (activeTab === "attempts") {
      downloadCsv(
        toCsv(filteredAttempts as unknown as Record<string, unknown>[], [
          { key: "username", label: "Username" },
          { key: "email", label: "Email" },
          { key: "status", label: "Status" },
          { key: "ip_address", label: "IP" },
          { key: "attempted_at", label: "Time" },
        ]),
        `auth-attempts-${now}.csv`,
      );
    } else {
      downloadCsv(
        toCsv(filteredActivity as unknown as Record<string, unknown>[], [
          { key: "user_email", label: "User" },
          { key: "activity_type_display", label: "Type" },
          { key: "description", label: "Description" },
          { key: "created_at", label: "Time" },
        ]),
        `auth-activity-${now}.csv`,
      );
    }
  };

  const handleBulkExport = () => {
    downloadCsv(
      toCsv(
        bulk.selectedItems.map((i) => ({ id: i.id })),
        [{ key: "id", label: "ID" }],
      ),
      `auth-bulk-${dayjs().format("YYYY-MM-DD")}.csv`,
    );
  };

  // ── Keyboard shortcuts ──────────────────────────────────────────────────

  const { open: helpOpen, setOpen: setHelpOpen } = useShortcutHelp();
  useKeyboardShortcuts({
    onCreate: () => {
      if (activeTab === "security") {
        setEditingSecurity(null);
        setShowSecurityForm(true);
      } else if (activeTab === "password") {
        setEditingPassword(null);
        setShowPasswordForm(true);
      } else if (activeTab === "sessionpol") {
        setEditingSessionPol(null);
        setShowSessionPolForm(true);
      } else if (activeTab === "whitelist") {
        setEditingWhitelist(null);
        setShowWhitelistForm(true);
      } else if (activeTab === "apikeys") {
        setEditingAPIKey(null);
        setShowAPIKeyForm(true);
      }
    },
    onSearch: () => searchRef.current?.focus(),
    onExport: handleExport,
    onEscape: () => bulk.clear(),
    onDelete: () => {
      if (bulk.selectedCount > 0) handleBulkDelete();
    },
    onSelectAll: () => bulk.toggleAll(),
  });

  const isLoading =
    activeTab === "sessions"
      ? sessionsLoading
      : activeTab === "tokens"
        ? tokensLoading
        : activeTab === "devices"
          ? devicesLoading
          : activeTab === "security"
            ? securityLoading
            : activeTab === "password"
              ? passwordLoading
              : activeTab === "sessionpol"
                ? sessionPolLoading
                : activeTab === "whitelist"
                  ? whitelistLoading
                  : activeTab === "apikeys"
                    ? apiKeysLoading
                    : activeTab === "usage"
                      ? usageLoading
                      : activeTab === "audit"
                        ? auditLoading
                        : activeTab === "logins"
                          ? loginsLoading
                          : activeTab === "attempts"
                            ? attemptsLoading
                            : activityLoading;

  const createButton =
    activeTab === "security"
      ? {
          label: "Add Policy",
          action: () => {
            setEditingSecurity(null);
            setShowSecurityForm(true);
          },
        }
      : activeTab === "password"
        ? {
            label: "Add Policy",
            action: () => {
              setEditingPassword(null);
              setShowPasswordForm(true);
            },
          }
        : activeTab === "sessionpol"
          ? {
              label: "Add Policy",
              action: () => {
                setEditingSessionPol(null);
                setShowSessionPolForm(true);
              },
            }
          : activeTab === "whitelist"
            ? {
                label: "Add Entry",
                action: () => {
                  setEditingWhitelist(null);
                  setShowWhitelistForm(true);
                },
              }
            : activeTab === "apikeys"
              ? {
                  label: "Create Key",
                  action: () => {
                    setEditingAPIKey(null);
                    setShowAPIKeyForm(true);
                  },
                }
              : null;

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Account Security</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Sessions, devices, policies, API keys, and audit activity
          </p>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
            <input
              type="checkbox"
              checked={bulk.allSelected && allFiltered.length > 0}
              onChange={bulk.toggleAll}
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
              aria-label="Select all"
            />
            <span className="text-sm text-slate-500 dark:text-slate-400">Select all</span>
          </label>
          <div className="flex items-center gap-1 rounded-lg border border-slate-200 p-0.5 dark:border-slate-700">
            <button
              onClick={() => setViewMode("pagination")}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                viewMode === "pagination"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
              }`}
            >
              Pages
            </button>
            <button
              onClick={() => setViewMode("infinite")}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                viewMode === "infinite"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
              }`}
            >
              Scroll
            </button>
          </div>
          <Button
            variant="secondary"
            leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
            onClick={handleExport}
          >
            Export CSV
          </Button>
        </div>
        {createButton && (
          <Button onClick={createButton.action}>
            <PlusIcon className="mr-1.5 h-4 w-4" />
            {createButton.label}
          </Button>
        )}
      </div>

      {/* Tabs */}
      <div className="flex w-fit max-w-full gap-1 overflow-x-auto rounded-lg bg-slate-100 p-1 dark:bg-slate-800">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const counts: Record<TabType, number> = {
            sessions: sessions.length,
            tokens: tokens.length,
            devices: devices.length,
            security: securityPolicies.length,
            password: passwordPolicies.length,
            sessionpol: sessionPolicies.length,
            whitelist: whitelist.length,
            apikeys: apiKeys.length,
            usage: usageLogs.length,
            audit: auditLogs.length,
            logins: loginHistory.length,
            attempts: loginAttempts.length,
            activity: activities.length,
          };
          return (
            <button
              key={tab.key}
              onClick={() => {
                setActiveTab(tab.key);
                setPage(1);
                setInfinitePage(1);
              }}
              className={`inline-flex items-center gap-2 whitespace-nowrap rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? "bg-white text-slate-900 shadow-sm dark:bg-slate-700 dark:text-white"
                  : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
              <span className="rounded-full bg-slate-200 px-1.5 py-0.5 text-xs dark:bg-slate-600">
                {counts[tab.key]}
              </span>
            </button>
          );
        })}
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          ref={searchRef}
          type="search"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          placeholder={`Search ${TAB_LABELS[activeTab].plural}...`}
          className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:placeholder-slate-400"
        />
      </div>

      {/* Content */}
      {isLoading ? (
        <CardSkeleton />
      ) : allFiltered.length === 0 ? (
        <EmptyState
          icon={
            activeTab === "sessions"
              ? ServerStackIcon
              : activeTab === "tokens"
                ? KeyIcon
                : activeTab === "devices"
                  ? DevicePhoneMobileIcon
                  : activeTab === "security"
                    ? ShieldCheckIcon
                    : activeTab === "password"
                      ? LockClosedIcon
                      : activeTab === "sessionpol"
                        ? ClockIcon
                        : activeTab === "whitelist"
                          ? GlobeAltIcon
                          : activeTab === "apikeys"
                            ? CodeBracketIcon
                            : activeTab === "usage"
                              ? ChartBarIcon
                              : activeTab === "audit"
                                ? AdjustmentsHorizontalIcon
                                : activeTab === "logins"
                                  ? UserCircleIcon
                                  : activeTab === "attempts"
                                    ? ExclamationTriangleIcon
                                    : FingerPrintIcon
          }
          title={`No ${TAB_LABELS[activeTab].plural}`}
          description={`No ${TAB_LABELS[activeTab].singular} found`}
        />
      ) : (
        <>
          {viewMode === "pagination" ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {visibleItems.map((item) => (
                <Card
                  key={item.id}
                  tab={activeTab}
                  item={item}
                  selected={bulk.isSelected(item.id)}
                  onToggle={() => bulk.toggle(item.id)}
                  onEdit={() => {
                    if (activeTab === "security") {
                      setEditingSecurity(item as SecurityPolicy);
                      setShowSecurityForm(true);
                    } else if (activeTab === "password") {
                      setEditingPassword(item as PasswordPolicy);
                      setShowPasswordForm(true);
                    } else if (activeTab === "sessionpol") {
                      setEditingSessionPol(item as SessionPolicy);
                      setShowSessionPolForm(true);
                    } else if (activeTab === "whitelist") {
                      setEditingWhitelist(item as IPWhitelistEntry);
                      setShowWhitelistForm(true);
                    } else if (activeTab === "apikeys") {
                      setEditingAPIKey(item as APIKey);
                      setShowAPIKeyForm(true);
                    }
                  }}
                  onDelete={() => {
                    if (!confirm("Delete this item?")) return;
                    if (activeTab === "sessions") deleteSession.mutate(item.id);
                    else if (activeTab === "tokens") deleteToken.mutate(item.id);
                    else if (activeTab === "devices") deleteDevice.mutate(item.id);
                    else if (activeTab === "whitelist") deleteWhitelist.mutate(item.id);
                    else if (activeTab === "apikeys") deleteAPIKey.mutate(item.id);
                    else if (activeTab === "usage") deleteUsage.mutate(item.id);
                    else if (activeTab === "audit") deleteAudit.mutate(item.id);
                    else if (activeTab === "logins") deleteLogin.mutate(item.id);
                    else if (activeTab === "attempts") deleteAttempt.mutate(item.id);
                    else deleteActivity.mutate(item.id);
                  }}
                  onToggleActive={
                    activeTab === "sessions"
                      ? () =>
                          toggleSession.mutate({
                            id: item.id,
                            is_active: !(item as UserSession).is_active,
                          })
                      : activeTab === "devices"
                        ? () =>
                            toggleDevice.mutate({
                              id: item.id,
                              is_active: !(item as Device).is_active,
                            })
                        : activeTab === "apikeys"
                          ? () =>
                              toggleAPIKey.mutate({
                                id: item.id,
                                status: (item as APIKey).status === "active" ? "revoked" : "active",
                              })
                          : undefined
                  }
                />
              ))}
            </div>
          ) : (
            <InfiniteScroll
              items={infiniteItems}
              hasMore={infiniteHasMore}
              isLoading={false}
              isFetchingNext={false}
              onLoadMore={() => setInfinitePage((p) => p + 1)}
              renderItem={(item) => (
                <Card
                  key={item.id}
                  tab={activeTab}
                  item={item}
                  selected={bulk.isSelected(item.id)}
                  onToggle={() => bulk.toggle(item.id)}
                  onEdit={() => {
                    if (activeTab === "security") {
                      setEditingSecurity(item as SecurityPolicy);
                      setShowSecurityForm(true);
                    } else if (activeTab === "password") {
                      setEditingPassword(item as PasswordPolicy);
                      setShowPasswordForm(true);
                    } else if (activeTab === "sessionpol") {
                      setEditingSessionPol(item as SessionPolicy);
                      setShowSessionPolForm(true);
                    } else if (activeTab === "whitelist") {
                      setEditingWhitelist(item as IPWhitelistEntry);
                      setShowWhitelistForm(true);
                    } else if (activeTab === "apikeys") {
                      setEditingAPIKey(item as APIKey);
                      setShowAPIKeyForm(true);
                    }
                  }}
                  onDelete={() => {
                    if (!confirm("Delete this item?")) return;
                    if (activeTab === "sessions") deleteSession.mutate(item.id);
                    else if (activeTab === "tokens") deleteToken.mutate(item.id);
                    else if (activeTab === "devices") deleteDevice.mutate(item.id);
                    else if (activeTab === "whitelist") deleteWhitelist.mutate(item.id);
                    else if (activeTab === "apikeys") deleteAPIKey.mutate(item.id);
                    else if (activeTab === "usage") deleteUsage.mutate(item.id);
                    else if (activeTab === "audit") deleteAudit.mutate(item.id);
                    else if (activeTab === "logins") deleteLogin.mutate(item.id);
                    else if (activeTab === "attempts") deleteAttempt.mutate(item.id);
                    else deleteActivity.mutate(item.id);
                  }}
                  onToggleActive={
                    activeTab === "sessions"
                      ? () =>
                          toggleSession.mutate({
                            id: item.id,
                            is_active: !(item as UserSession).is_active,
                          })
                      : activeTab === "devices"
                        ? () =>
                            toggleDevice.mutate({
                              id: item.id,
                              is_active: !(item as Device).is_active,
                            })
                        : activeTab === "apikeys"
                          ? () =>
                              toggleAPIKey.mutate({
                                id: item.id,
                                status: (item as APIKey).status === "active" ? "revoked" : "active",
                              })
                          : undefined
                  }
                />
              )}
            />
          )}

          {viewMode === "pagination" && totalPages > 1 && (
            <Pagination
              page={safePage}
              total={allFiltered.length}
              pageSize={PAGE_SIZE}
              onChange={setPage}
            />
          )}
        </>
      )}

      {/* Bulk action bar */}
      <BulkActionBar
        selectedCount={bulk.selectedCount}
        onClear={bulk.clear}
        onDelete={activeDelete ? undefined : handleBulkDelete}
        onExport={handleBulkExport}
        deleteLabel={`Delete ${bulk.selectedCount} selected`}
      />

      {/* Modals */}
      {activeTab === "security" && (
        <SecurityPolicyFormModal
          open={showSecurityForm}
          onClose={() => {
            setShowSecurityForm(false);
            setEditingSecurity(null);
          }}
          policy={editingSecurity}
          onSaved={() => {
            setShowSecurityForm(false);
            setEditingSecurity(null);
            qc.invalidateQueries({ queryKey: ["auth-security"] });
          }}
        />
      )}
      {activeTab === "password" && (
        <PasswordPolicyFormModal
          open={showPasswordForm}
          onClose={() => {
            setShowPasswordForm(false);
            setEditingPassword(null);
          }}
          policy={editingPassword}
          onSaved={() => {
            setShowPasswordForm(false);
            setEditingPassword(null);
            qc.invalidateQueries({ queryKey: ["auth-password"] });
          }}
        />
      )}
      {activeTab === "sessionpol" && (
        <SessionPolicyFormModal
          open={showSessionPolForm}
          onClose={() => {
            setShowSessionPolForm(false);
            setEditingSessionPol(null);
          }}
          policy={editingSessionPol}
          onSaved={() => {
            setShowSessionPolForm(false);
            setEditingSessionPol(null);
            qc.invalidateQueries({ queryKey: ["auth-sessionpol"] });
          }}
        />
      )}
      {activeTab === "whitelist" && (
        <WhitelistFormModal
          open={showWhitelistForm}
          onClose={() => {
            setShowWhitelistForm(false);
            setEditingWhitelist(null);
          }}
          entry={editingWhitelist}
          onSaved={() => {
            setShowWhitelistForm(false);
            setEditingWhitelist(null);
            qc.invalidateQueries({ queryKey: ["auth-whitelist"] });
          }}
        />
      )}
      {activeTab === "apikeys" && (
        <APIKeyFormModal
          open={showAPIKeyForm}
          onClose={() => {
            setShowAPIKeyForm(false);
            setEditingAPIKey(null);
          }}
          apiKey={editingAPIKey}
          onSaved={() => {
            setShowAPIKeyForm(false);
            setEditingAPIKey(null);
            qc.invalidateQueries({ queryKey: ["auth-apikeys"] });
          }}
        />
      )}

      {/* Shortcut help */}
      <KeyboardShortcutHelp open={helpOpen} onClose={() => setHelpOpen(false)} />
    </div>
  );
}

// ─── Card ────────────────────────────────────────────────────────────────────

function Card({
  tab,
  item,
  selected,
  onToggle,
  onEdit,
  onDelete,
  onToggleActive,
}: {
  tab: TabType;
  item: { id: string };
  selected: boolean;
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onToggleActive?: () => void;
}) {
  const checkboxCls =
    "h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600";
  const editable = ["security", "password", "sessionpol", "whitelist", "apikeys"].includes(tab);
  return (
    <div
      className={`group rounded-xl border bg-white p-4 transition-all hover:shadow-md dark:bg-slate-800 ${
        selected
          ? "border-indigo-400 ring-1 ring-indigo-400 dark:border-indigo-500"
          : "border-slate-200 dark:border-slate-700"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggle}
          className={checkboxCls}
          aria-label="Select item"
        />
        <div className="min-w-0 flex-1">
          {tab === "sessions" && <SessionCard item={item as UserSession} />}
          {tab === "tokens" && <TokenCard item={item as SessionToken} />}
          {tab === "devices" && <DeviceCard item={item as Device} />}
          {tab === "security" && <SecurityCard item={item as SecurityPolicy} />}
          {tab === "password" && <PasswordCard item={item as PasswordPolicy} />}
          {tab === "sessionpol" && <SessionPolCard item={item as SessionPolicy} />}
          {tab === "whitelist" && <WhitelistCard item={item as IPWhitelistEntry} />}
          {tab === "apikeys" && <APIKeyCard item={item as APIKey} />}
          {tab === "usage" && <UsageCard item={item as APIUsageLog} />}
          {tab === "audit" && <AuditCard item={item as AuditLog} />}
          {tab === "logins" && <LoginCard item={item as LoginHistory} />}
          {tab === "attempts" && <AttemptCard item={item as LoginAttempt} />}
          {tab === "activity" && <ActivityCard item={item as UserActivity} />}
        </div>
        <div className="flex gap-1">
          {onToggleActive && (
            <button
              onClick={onToggleActive}
              className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
              aria-label="Toggle active"
              title="Toggle active"
            >
              <ArrowPathIcon className="h-4 w-4" />
            </button>
          )}
          {editable && (
            <>
              <button
                onClick={onEdit}
                className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                aria-label="Edit"
              >
                <PencilIcon className="h-4 w-4" />
              </button>
              <button
                onClick={onDelete}
                className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                aria-label="Delete"
              >
                <TrashIcon className="h-4 w-4" />
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function SessionCard({ item }: { item: UserSession }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.user_name ?? item.user_email}
      </p>
      <p className="truncate text-xs text-slate-400">{item.user_email}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.is_active ? "active" : "inactive"} colors={STATUS_COLORS} />
        {item.ip_address && <span className="font-mono text-slate-400">{item.ip_address}</span>}
      </div>
      <p className="mt-1 text-xs text-slate-400">
        Last used {dayjs(item.last_used).format("MMM D, YYYY · h:mm A")}
      </p>
    </>
  );
}

function TokenCard({ item }: { item: SessionToken }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.token_type_display}
      </p>
      <p className="truncate text-xs text-slate-400">{item.user_name ?? item.user_email}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.status} colors={STATUS_COLORS} />
        {item.ip_address && <span className="font-mono text-slate-400">{item.ip_address}</span>}
      </div>
      <p className="mt-1 text-xs text-slate-400">
        {item.status === "active"
          ? `Expires ${dayjs(item.expires_at).format("MMM D, YYYY")}`
          : item.revoked_at
            ? `Revoked ${dayjs(item.revoked_at).format("MMM D, YYYY")}`
            : `Issued ${dayjs(item.issued_at).format("MMM D, YYYY")}`}
      </p>
    </>
  );
}

function DeviceCard({ item }: { item: Device }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.device_name || "Unnamed device"}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.user_email}
        {item.location && ` · 📍 ${item.location}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.status} colors={STATUS_COLORS} />
        <Badge value={item.is_active ? "active" : "inactive"} colors={STATUS_COLORS} />
        {item.device_type && <span className="text-slate-400">🖥 {item.device_type}</span>}
      </div>
      <p className="mt-1 text-xs text-slate-400">
        Last seen {dayjs(item.last_seen).format("MMM D, YYYY · h:mm A")}
      </p>
    </>
  );
}

function SecurityCard({ item }: { item: SecurityPolicy }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.name}
      </p>
      <p className="truncate text-xs text-slate-400">{item.description}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <span className="inline-flex items-center rounded-full bg-indigo-50 px-2 py-0.5 font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">
          {item.policy_type_display}
        </span>
        {item.min_length != null && (
          <span className="text-slate-400">🔒 min {item.min_length}</span>
        )}
        {item.session_timeout_minutes != null && (
          <span className="text-slate-400">⏱ {item.session_timeout_minutes}m</span>
        )}
        {item.max_age_days != null && (
          <span className="text-slate-400">📅 {item.max_age_days}d</span>
        )}
      </div>
    </>
  );
}

function PasswordCard({ item }: { item: PasswordPolicy }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        Password Policy
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.is_active ? "active" : "inactive"} colors={STATUS_COLORS} />
        <span className="text-slate-400">
          🔒 {item.min_length}–{item.max_length} chars
        </span>
      </div>
      <div className="mt-1 flex flex-wrap gap-1.5 text-xs text-slate-400">
        {item.require_uppercase && <span>🔠 Upper</span>}
        {item.require_lowercase && <span>🔡 Lower</span>}
        {item.require_digit && <span>🔢 Digit</span>}
        {item.require_special_char && <span>✨ Special</span>}
      </div>
      <p className="mt-1 text-xs text-slate-400">
        ⏳ max age {item.max_age_days}d · 🔁 {item.lockout_attempts} attempts lockout
      </p>
    </>
  );
}

function SessionPolCard({ item }: { item: SessionPolicy }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        Session Policy
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.is_active ? "active" : "inactive"} colors={STATUS_COLORS} />
        <span className="text-slate-400">⏱ {item.session_timeout_minutes} min</span>
        <span className="text-slate-400">🔄 {item.max_concurrent_sessions} concurrent</span>
      </div>
      <div className="mt-1 flex flex-wrap gap-1.5 text-xs text-slate-400">
        {item.enforce_single_session && <span>🔐 Single session</span>}
        {item.require_reauthentication && (
          <span>🔁 Re-auth {item.reauthentication_interval_minutes}m</span>
        )}
        {item.absolute_timeout_hours > 0 && <span>📅 {item.absolute_timeout_hours}h absolute</span>}
      </div>
    </>
  );
}

function WhitelistCard({ item }: { item: IPWhitelistEntry }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.ip_address}
      </p>
      <p className="truncate text-xs text-slate-400">{item.description || item.ip_range || "—"}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-0.5 font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
          {item.access_level_display}
        </span>
        <Badge value={item.is_active ? "active" : "inactive"} colors={STATUS_COLORS} />
        {item.ip_range && <span className="font-mono text-slate-400">{item.ip_range}</span>}
      </div>
    </>
  );
}

function APIKeyCard({ item }: { item: APIKey }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.name}
      </p>
      <p className="truncate font-mono text-xs text-slate-400">{item.key_prefix}••••••••</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.status} colors={STATUS_COLORS} />
        <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-600 dark:bg-slate-700 dark:text-slate-300">
          {item.rate_limit}/hr
        </span>
        {item.scopes.length > 0 && (
          <span className="truncate text-slate-400">{item.scopes.join(", ")}</span>
        )}
      </div>
      <p className="mt-1 text-xs text-slate-400">
        {item.last_used_at
          ? `Last used ${dayjs(item.last_used_at).format("MMM D, YYYY")}`
          : "Never used"}
      </p>
    </>
  );
}

function UsageCard({ item }: { item: APIUsageLog }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        <span className="font-mono">{item.method}</span> {item.endpoint}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.api_key_name || "No key"} · {item.ip_address ?? "—"}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <span
          className={`inline-flex items-center rounded-full px-2 py-0.5 font-medium ${
            item.status_code < 400
              ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
              : "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300"
          }`}
        >
          {item.status_code}
        </span>
        <span className="text-slate-400">⚡ {item.response_time_ms}ms</span>
        {item.error_message && (
          <span className="truncate text-slate-400">⚠ {item.error_message}</span>
        )}
      </div>
      <p className="mt-1 text-xs text-slate-400">
        {dayjs(item.timestamp).format("MMM D, YYYY · h:mm A")}
      </p>
    </>
  );
}

function AuditCard({ item }: { item: AuditLog }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.action.replace(/_/g, " ")}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.user_name ?? item.user_email ?? "system"}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-600 dark:bg-slate-700 dark:text-slate-300">
          {item.resource_type.replace(/_/g, " ")}
        </span>
        {item.ip_address && <span className="font-mono text-slate-400">{item.ip_address}</span>}
      </div>
      <p className="mt-1 text-xs text-slate-400">
        {dayjs(item.timestamp).format("MMM D, YYYY · h:mm A")}
      </p>
    </>
  );
}

function LoginCard({ item }: { item: LoginHistory }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.user_name ?? item.email}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.email}
        {item.city && ` · 📍 ${item.city}${item.country ? `, ${item.country}` : ""}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.status} colors={STATUS_COLORS} />
        <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-600 dark:bg-slate-700 dark:text-slate-300">
          {item.login_type_display}
        </span>
        {item.ip_address && <span className="font-mono text-slate-400">{item.ip_address}</span>}
      </div>
      <p className="mt-1 text-xs text-slate-400">
        {dayjs(item.created_at).format("MMM D, YYYY · h:mm A")}
      </p>
    </>
  );
}

function AttemptCard({ item }: { item: LoginAttempt }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.username || item.email}
      </p>
      <p className="truncate text-xs text-slate-400">{item.email}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.status} colors={STATUS_COLORS} />
        {item.ip_address && <span className="font-mono text-slate-400">{item.ip_address}</span>}
      </div>
      <p className="mt-1 truncate text-xs text-slate-400">
        {item.failure_reason || dayjs(item.attempted_at).format("MMM D, YYYY · h:mm A")}
      </p>
    </>
  );
}

function ActivityCard({ item }: { item: UserActivity }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.activity_type_display}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.user_name ?? item.user_email}
        {item.resource_type && ` · ${item.resource_type.replace(/_/g, " ")}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.ip_address && <span className="font-mono text-slate-400">{item.ip_address}</span>}
      </div>
      <p className="mt-1 truncate text-xs text-slate-400">
        {item.description || dayjs(item.created_at).format("MMM D, YYYY · h:mm A")}
      </p>
    </>
  );
}

// ─── Security Policy Form Modal ──────────────────────────────────────────────

function SecurityPolicyFormModal({
  open,
  onClose,
  policy,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  policy?: SecurityPolicy | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    name: policy?.name ?? "",
    policy_type: policy?.policy_type ?? "login",
    description: policy?.description ?? "",
    min_length: policy?.min_length != null ? String(policy.min_length) : "",
    max_age_days: policy?.max_age_days != null ? String(policy.max_age_days) : "",
    history_count: policy?.history_count != null ? String(policy.history_count) : "",
    session_timeout_minutes:
      policy?.session_timeout_minutes != null ? String(policy.session_timeout_minutes) : "",
  });
  const isEdit = !!policy;
  const createMut = useMutation({
    mutationFn: (data: unknown) => api.post("/auth/security-policy/", data),
    onSuccess: () => {
      toast.success("Security policy created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: unknown) => api.patch(`/auth/security-policy/${policy!.id}/`, data),
    onSuccess: () => {
      toast.success("Security policy updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Policy name is required");
    const data = {
      ...f,
      name: f.name.trim(),
      min_length: f.min_length ? Number(f.min_length) : null,
      max_age_days: f.max_age_days ? Number(f.max_age_days) : null,
      history_count: f.history_count ? Number(f.history_count) : null,
      session_timeout_minutes: f.session_timeout_minutes ? Number(f.session_timeout_minutes) : null,
    };
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Security Policy" : "Add Security Policy"}
    >
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <SelectField
            label="Policy Type"
            value={f.policy_type}
            options={POLICY_TYPE_OPTIONS}
            onChange={(v) => setF((p) => ({ ...p, policy_type: v }))}
          />
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            className={`${inputCls} min-h-[60px]`}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Min Length</label>
            <input
              type="number"
              min={0}
              value={f.min_length}
              onChange={(e) => setF((p) => ({ ...p, min_length: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Max Age (days)</label>
            <input
              type="number"
              min={0}
              value={f.max_age_days}
              onChange={(e) => setF((p) => ({ ...p, max_age_days: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>History Count</label>
            <input
              type="number"
              min={0}
              value={f.history_count}
              onChange={(e) => setF((p) => ({ ...p, history_count: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Session Timeout (minutes)</label>
          <input
            type="number"
            min={0}
            value={f.session_timeout_minutes}
            onChange={(e) => setF((p) => ({ ...p, session_timeout_minutes: e.target.value }))}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Password Policy Form Modal ──────────────────────────────────────────────

function PasswordPolicyFormModal({
  open,
  onClose,
  policy,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  policy?: PasswordPolicy | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    min_length: policy?.min_length != null ? String(policy.min_length) : "8",
    max_length: policy?.max_length != null ? String(policy.max_length) : "64",
    require_uppercase: policy?.require_uppercase ?? true,
    require_lowercase: policy?.require_lowercase ?? true,
    require_digit: policy?.require_digit ?? true,
    require_special_char: policy?.require_special_char ?? false,
    max_age_days: policy?.max_age_days != null ? String(policy.max_age_days) : "90",
    lockout_attempts: policy?.lockout_attempts != null ? String(policy.lockout_attempts) : "5",
    lockout_duration_minutes:
      policy?.lockout_duration_minutes != null ? String(policy.lockout_duration_minutes) : "30",
    is_active: policy?.is_active ?? true,
  });
  const isEdit = !!policy;
  const createMut = useMutation({
    mutationFn: (data: unknown) => api.post("/auth/password-policy/", data),
    onSuccess: () => {
      toast.success("Password policy created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: unknown) => api.patch(`/auth/password-policy/${policy!.id}/`, data),
    onSuccess: () => {
      toast.success("Password policy updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      ...f,
      min_length: Number(f.min_length),
      max_length: Number(f.max_length),
      max_age_days: Number(f.max_age_days),
      lockout_attempts: Number(f.lockout_attempts),
      lockout_duration_minutes: Number(f.lockout_duration_minutes),
    };
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Password Policy" : "Add Password Policy"}
    >
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Min Length *</label>
            <input
              type="number"
              min={1}
              value={f.min_length}
              onChange={(e) => setF((p) => ({ ...p, min_length: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Max Length *</label>
            <input
              type="number"
              min={1}
              value={f.max_length}
              onChange={(e) => setF((p) => ({ ...p, max_length: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Max Age (days)</label>
            <input
              type="number"
              min={0}
              value={f.max_age_days}
              onChange={(e) => setF((p) => ({ ...p, max_age_days: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Lockout Attempts</label>
            <input
              type="number"
              min={0}
              value={f.lockout_attempts}
              onChange={(e) => setF((p) => ({ ...p, lockout_attempts: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Lockout Duration (min)</label>
            <input
              type="number"
              min={0}
              value={f.lockout_duration_minutes}
              onChange={(e) =>
                setF((p) => ({
                  ...p,
                  lockout_duration_minutes: e.target.value,
                }))
              }
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {(
            [
              ["require_uppercase", "Require uppercase"],
              ["require_lowercase", "Require lowercase"],
              ["require_digit", "Require digit"],
              ["require_special_char", "Require special char"],
            ] as const
          ).map(([key, label]) => (
            <label
              key={key}
              className="flex cursor-pointer items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300"
            >
              <input
                type="checkbox"
                checked={f[key]}
                onChange={(e) => setF((p) => ({ ...p, [key]: e.target.checked }))}
                className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
              />
              {label}
            </label>
          ))}
        </div>
        <label className="flex cursor-pointer items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.is_active}
            onChange={(e) => setF((p) => ({ ...p, is_active: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
          />
          Active
        </label>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Session Policy Form Modal ───────────────────────────────────────────────

function SessionPolicyFormModal({
  open,
  onClose,
  policy,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  policy?: SessionPolicy | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    session_timeout_minutes:
      policy?.session_timeout_minutes != null ? String(policy.session_timeout_minutes) : "30",
    absolute_timeout_hours:
      policy?.absolute_timeout_hours != null ? String(policy.absolute_timeout_hours) : "8",
    idle_timeout_minutes:
      policy?.idle_timeout_minutes != null ? String(policy.idle_timeout_minutes) : "15",
    max_concurrent_sessions:
      policy?.max_concurrent_sessions != null ? String(policy.max_concurrent_sessions) : "3",
    enforce_single_session: policy?.enforce_single_session ?? false,
    require_reauthentication: policy?.require_reauthentication ?? false,
    reauthentication_interval_minutes:
      policy?.reauthentication_interval_minutes != null
        ? String(policy.reauthentication_interval_minutes)
        : "60",
    remember_me_days: policy?.remember_me_days != null ? String(policy.remember_me_days) : "30",
    is_active: policy?.is_active ?? true,
  });
  const isEdit = !!policy;
  const createMut = useMutation({
    mutationFn: (data: unknown) => api.post("/auth/session-policy/", data),
    onSuccess: () => {
      toast.success("Session policy created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: unknown) => api.patch(`/auth/session-policy/${policy!.id}/`, data),
    onSuccess: () => {
      toast.success("Session policy updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      ...f,
      session_timeout_minutes: Number(f.session_timeout_minutes),
      absolute_timeout_hours: Number(f.absolute_timeout_hours),
      idle_timeout_minutes: Number(f.idle_timeout_minutes),
      max_concurrent_sessions: Number(f.max_concurrent_sessions),
      reauthentication_interval_minutes: Number(f.reauthentication_interval_minutes),
      remember_me_days: Number(f.remember_me_days),
    };
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Session Policy" : "Add Session Policy"}
    >
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Timeout (min) *</label>
            <input
              type="number"
              min={1}
              value={f.session_timeout_minutes}
              onChange={(e) => setF((p) => ({ ...p, session_timeout_minutes: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Absolute (hrs)</label>
            <input
              type="number"
              min={0}
              value={f.absolute_timeout_hours}
              onChange={(e) => setF((p) => ({ ...p, absolute_timeout_hours: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Idle (min)</label>
            <input
              type="number"
              min={0}
              value={f.idle_timeout_minutes}
              onChange={(e) => setF((p) => ({ ...p, idle_timeout_minutes: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Max Concurrent *</label>
            <input
              type="number"
              min={1}
              value={f.max_concurrent_sessions}
              onChange={(e) => setF((p) => ({ ...p, max_concurrent_sessions: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Re-auth Interval (min)</label>
            <input
              type="number"
              min={0}
              value={f.reauthentication_interval_minutes}
              onChange={(e) =>
                setF((p) => ({
                  ...p,
                  reauthentication_interval_minutes: e.target.value,
                }))
              }
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Remember Me (days)</label>
            <input
              type="number"
              min={0}
              value={f.remember_me_days}
              onChange={(e) => setF((p) => ({ ...p, remember_me_days: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <label className="flex cursor-pointer items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={f.enforce_single_session}
              onChange={(e) =>
                setF((p) => ({
                  ...p,
                  enforce_single_session: e.target.checked,
                }))
              }
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
            />
            Enforce single session
          </label>
          <label className="flex cursor-pointer items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={f.require_reauthentication}
              onChange={(e) =>
                setF((p) => ({
                  ...p,
                  require_reauthentication: e.target.checked,
                }))
              }
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
            />
            Require re-authentication
          </label>
        </div>
        <label className="flex cursor-pointer items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.is_active}
            onChange={(e) => setF((p) => ({ ...p, is_active: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
          />
          Active
        </label>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Whitelist Form Modal ────────────────────────────────────────────────────

function WhitelistFormModal({
  open,
  onClose,
  entry,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  entry?: IPWhitelistEntry | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    ip_address: entry?.ip_address ?? "",
    ip_range: entry?.ip_range ?? "",
    description: entry?.description ?? "",
    access_level: entry?.access_level ?? "all",
    is_active: entry?.is_active ?? true,
  });
  const isEdit = !!entry;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/auth/i-p-whitelist/", data),
    onSuccess: () => {
      toast.success("Whitelist entry added");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/auth/i-p-whitelist/${entry!.id}/`, data),
    onSuccess: () => {
      toast.success("Whitelist entry updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.ip_address.trim() && !f.ip_range.trim())
      return toast.error("IP address or range is required");
    if (isEdit) updateMut.mutate(f);
    else createMut.mutate(f);
  };
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Whitelist Entry" : "Add Whitelist Entry"}
    >
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>IP Address *</label>
            <input
              value={f.ip_address}
              onChange={(e) => setF((p) => ({ ...p, ip_address: e.target.value }))}
              className={`${inputCls} font-mono`}
              placeholder="e.g. 203.0.113.10"
            />
          </div>
          <div>
            <label className={labelCls}>IP Range (CIDR)</label>
            <input
              value={f.ip_range}
              onChange={(e) => setF((p) => ({ ...p, ip_range: e.target.value }))}
              className={`${inputCls} font-mono`}
              placeholder="e.g. 192.168.1.0/24"
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <input
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            className={inputCls}
            placeholder="e.g. Campus admin office"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Access Level"
            value={f.access_level}
            options={ACCESS_LEVEL_OPTIONS}
            onChange={(v) => setF((p) => ({ ...p, access_level: v }))}
          />
          <div className="flex items-end pb-1">
            <label className="flex cursor-pointer items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
              <input
                type="checkbox"
                checked={f.is_active}
                onChange={(e) => setF((p) => ({ ...p, is_active: e.target.checked }))}
                className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
              />
              Active
            </label>
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Add"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── API Key Form Modal ──────────────────────────────────────────────────────

function APIKeyFormModal({
  open,
  onClose,
  apiKey,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  apiKey?: APIKey | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    name: apiKey?.name ?? "",
    description: apiKey?.description ?? "",
    scopes: apiKey?.scopes.join(", ") ?? "",
    rate_limit: apiKey?.rate_limit != null ? String(apiKey.rate_limit) : "1000",
    status: apiKey?.status ?? "active",
    expires_at: apiKey?.expires_at ? apiKey.expires_at.slice(0, 10) : "",
  });
  const isEdit = !!apiKey;
  const createMut = useMutation({
    mutationFn: (data: unknown) => api.post("/auth/a-p-i-key/", data),
    onSuccess: () => {
      toast.success("API key created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: unknown) => api.patch(`/auth/a-p-i-key/${apiKey!.id}/`, data),
    onSuccess: () => {
      toast.success("API key updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Key name is required");
    const data = {
      ...f,
      name: f.name.trim(),
      scopes: f.scopes
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
      rate_limit: Number(f.rate_limit) || 1000,
      expires_at: f.expires_at || null,
    };
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit API Key" : "Create API Key"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className={inputCls}
              placeholder="e.g. SIS Integration"
              required
            />
          </div>
          <div>
            <label className={labelCls}>Rate Limit (req/hr)</label>
            <input
              type="number"
              min={1}
              value={f.rate_limit}
              onChange={(e) => setF((p) => ({ ...p, rate_limit: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            className={`${inputCls} min-h-[60px]`}
          />
        </div>
        <div>
          <label className={labelCls}>Scopes (comma-separated)</label>
          <input
            value={f.scopes}
            onChange={(e) => setF((p) => ({ ...p, scopes: e.target.value }))}
            className={`${inputCls} font-mono`}
            placeholder="students:read, fees:read"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Status"
            value={f.status}
            options={API_KEY_STATUS_OPTIONS}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
          <div>
            <label className={labelCls}>Expires At</label>
            <input
              type="date"
              value={f.expires_at}
              onChange={(e) => setF((p) => ({ ...p, expires_at: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        {!isEdit && (
          <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700 dark:bg-amber-900/30 dark:text-amber-300">
            The secret key is generated server-side — copy it from the API response after creating.
          </p>
        )}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create Key"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
