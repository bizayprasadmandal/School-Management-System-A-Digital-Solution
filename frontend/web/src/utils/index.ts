/**
 * Utility helpers — formatters, validators, constants used across the app
 */

import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import duration from "dayjs/plugin/duration";

dayjs.extend(relativeTime);
dayjs.extend(duration);

// ─── Date & Time ─────────────────────────────────────────────────────────────

export const fmt = {
  date:       (d: string | Date) => dayjs(d).format("MMM D, YYYY"),
  dateShort:  (d: string | Date) => dayjs(d).format("MMM D"),
  dateInput:  (d: string | Date) => dayjs(d).format("YYYY-MM-DD"),
  time:       (t: string) => dayjs(`2000-01-01T${t}`).format("h:mm A"),
  datetime:   (d: string | Date) => dayjs(d).format("MMM D, YYYY h:mm A"),
  fromNow:    (d: string | Date) => dayjs(d).fromNow(),
  month:      (d: string | Date) => dayjs(d).format("MMMM YYYY"),
  dayOfWeek:  (d: string | Date) => dayjs(d).format("dddd"),
  iso:        (d: Date) => dayjs(d).toISOString(),
};

export const DAYS_OF_WEEK = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
export const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];

// ─── Currency & Numbers ───────────────────────────────────────────────────────

export const currency = (amount: number | string, symbol = "$") =>
  `${symbol}${Number(amount).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

export const percent = (value: number, decimals = 1) =>
  `${value.toFixed(decimals)}%`;

export const compact = (n: number) => {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)     return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
};

// ─── Attendance ───────────────────────────────────────────────────────────────

export const ATTENDANCE_STATUS: Record<string, { label: string; color: "green"|"red"|"amber"|"blue"|"slate" }> = {
  P: { label: "Present", color: "green" },
  A: { label: "Absent",  color: "red" },
  L: { label: "Late",    color: "amber" },
  E: { label: "Excused", color: "blue" },
  H: { label: "Half Day",color: "slate" },
};

export const attendanceColor = (pct: number): string => {
  if (pct >= 90) return "text-green-600";
  if (pct >= 75) return "text-amber-600";
  return "text-red-600";
};

export const attendanceBg = (pct: number): string => {
  if (pct >= 90) return "bg-green-500";
  if (pct >= 75) return "bg-amber-500";
  return "bg-red-500";
};

// ─── Fee status ───────────────────────────────────────────────────────────────

export const FEE_STATUS: Record<string, { label: string; color: "green"|"red"|"amber"|"blue"|"slate" }> = {
  paid:      { label: "Paid",       color: "green" },
  unpaid:    { label: "Unpaid",     color: "amber" },
  overdue:   { label: "Overdue",    color: "red" },
  partial:   { label: "Partial",    color: "blue" },
  waived:    { label: "Waived",     color: "slate" },
  cancelled: { label: "Cancelled",  color: "slate" },
};

// ─── Grade / GPA ─────────────────────────────────────────────────────────────

export const gradeColor = (letter: string): string => {
  if (letter.startsWith("A")) return "text-green-600";
  if (letter.startsWith("B")) return "text-blue-600";
  if (letter.startsWith("C")) return "text-amber-600";
  if (letter.startsWith("D")) return "text-orange-600";
  return "text-red-600";
};

export const gradeBg = (pct: number): string => {
  if (pct >= 90) return "bg-green-100 text-green-800";
  if (pct >= 80) return "bg-blue-100 text-blue-800";
  if (pct >= 70) return "bg-indigo-100 text-indigo-800";
  if (pct >= 60) return "bg-amber-100 text-amber-800";
  if (pct >= 50) return "bg-orange-100 text-orange-800";
  return "bg-red-100 text-red-800";
};

// ─── User roles ───────────────────────────────────────────────────────────────

export const ROLE_LABELS: Record<string, string> = {
  super_admin:  "Super Administrator",
  school_admin: "School Administrator",
  teacher:      "Teacher",
  student:      "Student",
  parent:       "Parent / Guardian",
  accountant:   "Accountant",
  librarian:    "Librarian",
  counselor:    "Counselor",
};

export const ROLE_COLORS: Record<string, string> = {
  super_admin:  "bg-purple-100 text-purple-700",
  school_admin: "bg-indigo-100 text-indigo-700",
  teacher:      "bg-emerald-100 text-emerald-700",
  student:      "bg-blue-100 text-blue-700",
  parent:       "bg-violet-100 text-violet-700",
  accountant:   "bg-amber-100 text-amber-700",
  librarian:    "bg-teal-100 text-teal-700",
  counselor:    "bg-rose-100 text-rose-700",
};

// ─── Validators ───────────────────────────────────────────────────────────────

export const validators = {
  email: (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || "Invalid email address",
  required: (label = "This field") => (v: string) => v?.trim() ? true : `${label} is required`,
  minLength: (min: number) => (v: string) => v?.length >= min || `Minimum ${min} characters required`,
  maxLength: (max: number) => (v: string) => v?.length <= max || `Maximum ${max} characters allowed`,
  phone: (v: string) => /^[+]?[\d\s()-]{7,20}$/.test(v) || "Invalid phone number",
  positiveNumber: (v: string) => (Number(v) > 0) || "Must be a positive number",
  date: (v: string) => dayjs(v).isValid() || "Invalid date",
  dateAfter: (after: string) => (v: string) =>
    dayjs(v).isAfter(dayjs(after)) || `Date must be after ${fmt.date(after)}`,
};

// ─── String helpers ───────────────────────────────────────────────────────────

export const capitalize = (s: string) =>
  s.charAt(0).toUpperCase() + s.slice(1).toLowerCase();

export const titleCase = (s: string) =>
  s.split(/[\s_-]/).map(capitalize).join(" ");

export const truncate = (s: string, len: number) =>
  s.length > len ? `${s.slice(0, len)}…` : s;

export const initials = (name: string) =>
  name.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase();

export const slugify = (s: string) =>
  s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");

// ─── File helpers ─────────────────────────────────────────────────────────────

export const fileSize = (bytes: number) => {
  if (bytes >= 1_048_576) return `${(bytes / 1_048_576).toFixed(1)} MB`;
  if (bytes >= 1_024)     return `${(bytes / 1_024).toFixed(0)} KB`;
  return `${bytes} B`;
};

export const ACCEPTED_IMAGE_TYPES = "image/jpeg,image/png,image/webp";
export const ACCEPTED_DOC_TYPES   = "application/pdf,.doc,.docx,.xls,.xlsx";

// ─── Array helpers ────────────────────────────────────────────────────────────

export const groupBy = <T>(arr: T[], key: keyof T): Record<string, T[]> =>
  arr.reduce((acc, item) => {
    const k = String(item[key]);
    return { ...acc, [k]: [...(acc[k] ?? []), item] };
  }, {} as Record<string, T[]>);

export const sortBy = <T>(arr: T[], key: keyof T, dir: "asc" | "desc" = "asc") =>
  [...arr].sort((a, b) => {
    const va = a[key], vb = b[key];
    const cmp = va < vb ? -1 : va > vb ? 1 : 0;
    return dir === "asc" ? cmp : -cmp;
  });

export const unique = <T>(arr: T[], key?: keyof T): T[] => {
  if (!key) return [...new Set(arr)];
  const seen = new Set<T[keyof T]>();
  return arr.filter(item => {
    if (seen.has(item[key])) return false;
    seen.add(item[key]);
    return true;
  });
};

// ─── Color utilities ──────────────────────────────────────────────────────────

export const CHART_COLORS = [
  "#6366f1","#22c55e","#f59e0b","#ef4444","#8b5cf6",
  "#14b8a6","#f97316","#3b82f6","#ec4899","#84cc16",
];

// ─── Download helpers ─────────────────────────────────────────────────────────

export const downloadBlob = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob);
  const a   = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

export const downloadFromUrl = async (url: string, filename: string, token: string) => {
  const res  = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  const blob = await res.blob();
  downloadBlob(blob, filename);
};
