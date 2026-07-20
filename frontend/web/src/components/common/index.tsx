/**
 * Common UI Components — reusable across all role dashboards
 */

import React from "react";
import { XMarkIcon, ExclamationTriangleIcon, ArrowPathIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";

// ─── Button ───────────────────────────────────────────────────────────────────

export type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.memo(function Button({
  variant = "primary", size = "md", loading, leftIcon, rightIcon,
  children, className, disabled, ...props
}: ButtonProps) {
  const base = "inline-flex items-center justify-center gap-2 font-semibold rounded-xl transition-all duration-150 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-50 disabled:cursor-not-allowed select-none";
  const variants = {
    primary:   "bg-indigo-600 text-white shadow-sm hover:bg-indigo-700 active:bg-indigo-800 focus-visible:outline-indigo-600",
    secondary: "bg-white text-slate-700 border border-slate-200 shadow-sm hover:bg-slate-50 active:bg-slate-100",
    danger:    "bg-red-600 text-white shadow-sm hover:bg-red-700 active:bg-red-800",
    ghost:     "text-slate-600 hover:bg-slate-100 active:bg-slate-200",
  };
  const sizes = { sm: "px-3 py-1.5 text-xs", md: "px-4 py-2.5 text-sm", lg: "px-6 py-3 text-base" };
  return (
    <button
      className={clsx(base, variants[variant], sizes[size], className)}
      disabled={disabled || loading}
      {...props}
    >
      {loading
        ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        : leftIcon}
      {children}
      {!loading && rightIcon}
    </button>
  );
});

// ─── Input ────────────────────────────────────────────────────────────────────

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftAddon?: React.ReactNode;
  rightAddon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(function Input({
  label, error, hint, leftAddon, rightAddon, className, id, ...props
}, ref) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, "-");
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label htmlFor={inputId} className="text-xs font-semibold text-slate-700">{label}</label>}
      <div className="relative flex items-center">
        {leftAddon && <div className="absolute left-3 text-slate-400">{leftAddon}</div>}
        <input
          ref={ref}
          id={inputId}
          className={clsx(
            "w-full rounded-xl border bg-white px-4 py-2.5 text-sm placeholder:text-slate-400 text-slate-900",
            "transition focus:outline-none focus:ring-2 disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed",
            error ? "border-red-300 focus:ring-red-400 focus:border-red-400" : "border-slate-200 focus:ring-indigo-500 focus:border-indigo-400",
            leftAddon && "pl-9",
            rightAddon && "pr-9",
            className
          )}
          {...props}
        />
        {rightAddon && <div className="absolute right-3 text-slate-400">{rightAddon}</div>}
      </div>
      {error && <p className="text-xs text-red-600">{error}</p>}
      {hint && !error && <p className="text-xs text-slate-500">{hint}</p>}
    </div>
  );
});

// ─── Select ───────────────────────────────────────────────────────────────────

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: { value: string | number; label: string }[];
  placeholder?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(function Select({
  label, error, options, placeholder, className, id, ...props
}, ref) {
  const selectId = id ?? label?.toLowerCase().replace(/\s+/g, "-");
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label htmlFor={selectId} className="text-xs font-semibold text-slate-700">{label}</label>}
      <select
        ref={ref}
        id={selectId}
        className={clsx(
          "w-full rounded-xl border bg-white px-4 py-2.5 text-sm text-slate-900 appearance-none cursor-pointer",
          "transition focus:outline-none focus:ring-2 disabled:bg-slate-50 disabled:cursor-not-allowed",
          error ? "border-red-300 focus:ring-red-400" : "border-slate-200 focus:ring-indigo-500",
          className
        )}
        {...props}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
});

// ─── Badge ────────────────────────────────────────────────────────────────────

export type BadgeColor = "green" | "red" | "amber" | "blue" | "purple" | "slate" | "indigo";
interface BadgeProps { color?: BadgeColor; children: React.ReactNode; dot?: boolean; className?: string; }

const BADGE_COLORS: Record<BadgeColor, string> = {
  green:  "bg-green-100 text-green-700",
  red:    "bg-red-100 text-red-700",
  amber:  "bg-amber-100 text-amber-700",
  blue:   "bg-blue-100 text-blue-700",
  purple: "bg-purple-100 text-purple-700",
  slate:  "bg-slate-100 text-slate-600",
  indigo: "bg-indigo-100 text-indigo-700",
};
const DOT_COLORS: Record<BadgeColor, string> = {
  green: "bg-green-500", red: "bg-red-500", amber: "bg-amber-500",
  blue: "bg-blue-500", purple: "bg-purple-500", slate: "bg-slate-400", indigo: "bg-indigo-500",
};

export const Badge = React.memo(function Badge({ color = "slate", dot, children, className }: BadgeProps) {
  return (
    <span className={clsx("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold", BADGE_COLORS[color], className)}>
      {dot && <span className={clsx("h-1.5 w-1.5 rounded-full", DOT_COLORS[color])} />}
      {children}
    </span>
  );
});

// ─── Modal ────────────────────────────────────────────────────────────────────

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
  footer?: React.ReactNode;
}

const MODAL_SIZES = { sm: "max-w-sm", md: "max-w-md", lg: "max-w-lg", xl: "max-w-2xl" };

export function Modal({ open, onClose, title, description, children, size = "md", footer }: ModalProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className={clsx("relative w-full bg-white rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]", MODAL_SIZES[size])}>
        {title && (
          <div className="flex items-start justify-between p-6 border-b border-slate-100">
            <div>
              <h2 className="text-lg font-bold text-slate-900">{title}</h2>
              {description && <p className="text-sm text-slate-500 mt-0.5">{description}</p>}
            </div>
            <button onClick={onClose} className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors ml-4">
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        )}
        <div className="flex-1 overflow-y-auto p-6">{children}</div>
        {footer && <div className="border-t border-slate-100 px-6 py-4 flex items-center justify-end gap-3">{footer}</div>}
      </div>
    </div>
  );
}

// ─── Spinner / Loading ────────────────────────────────────────────────────────

export function Spinner({ size = "md", className }: { size?: "sm" | "md" | "lg"; className?: string }) {
  const sizes = { sm: "h-4 w-4 border-2", md: "h-7 w-7 border-4", lg: "h-10 w-10 border-4" };
  return <div className={clsx("animate-spin rounded-full border-indigo-500 border-t-transparent", sizes[size], className)} />;
}

// ─── Skeleton Loaders ─────────────────────────────────────────────────────────

/** Base skeleton pulse block */
function Skeleton({ className }: { className?: string }) {
  return <div className={clsx("animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700", className)} />;
}

/** Skeleton that mimics a card with title + 2 text lines */
export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={clsx("rounded-xl bg-white dark:bg-slate-800 p-5 border border-slate-100 dark:border-slate-700", className)}>
      <Skeleton className="h-4 w-1/3 mb-4" />
      <Skeleton className="h-8 w-2/3 mb-3" />
      <Skeleton className="h-3 w-full mb-2" />
      <Skeleton className="h-3 w-4/5" />
    </div>
  );
}

/** Skeleton that mimics a table with header + rows */
export function SkeletonTable({ rows = 5, cols = 4, className }: { rows?: number; cols?: number; className?: string }) {
  return (
    <div className={clsx("rounded-xl border border-slate-100 dark:border-slate-700 overflow-hidden", className)}>
      {/* Header */}
      <div className="bg-slate-50 dark:bg-slate-800/50 px-4 py-3 flex gap-4">
        {Array.from({ length: cols }, (_, i) => (
          <Skeleton key={i} className="h-3 flex-1" />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }, (_, r) => (
        <div key={r} className="flex gap-4 px-4 py-3 border-t border-slate-50 dark:border-slate-700/50">
          {Array.from({ length: cols }, (_, c) => (
            <Skeleton key={c} className={`h-4 ${c === 0 ? "flex-[2]" : "flex-1"}`} />
          ))}
        </div>
      ))}
    </div>
  );
}

/** Skeleton that mimics a KPI stat card */
export function SkeletonStatCard({ className }: { className?: string }) {
  return (
    <div className={clsx("rounded-xl bg-white dark:bg-slate-800 p-5 border border-slate-100 dark:border-slate-700", className)}>
      <Skeleton className="h-3 w-1/2 mb-3" />
      <Skeleton className="h-8 w-1/3 mb-3" />
      <Skeleton className="h-3 w-2/3" />
    </div>
  );
}

/** Skeleton that mimics a chart/visualization area */
export function SkeletonChart({ className }: { className?: string }) {
  return (
    <div className={clsx("rounded-xl bg-white dark:bg-slate-800 p-5 border border-slate-100 dark:border-slate-700", className)}>
      <Skeleton className="h-3 w-1/4 mb-6" />
      <div className="flex items-end gap-2 h-40">
        <Skeleton className="flex-1 h-3/4" />
        <Skeleton className="flex-1 h-1/2" />
        <Skeleton className="flex-1 h-4/5" />
        <Skeleton className="flex-1 h-1/3" />
        <Skeleton className="flex-1 h-2/3" />
        <Skeleton className="flex-1 h-5/6" />
      </div>
    </div>
  );
}

/** Skeleton that mimics a list of text lines */
export function SkeletonText({ lines = 3, className }: { lines?: number; className?: string }) {
  return (
    <div className={clsx("space-y-2", className)}>
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton key={i} className={`h-3 ${i === lines - 1 ? "w-3/5" : "w-full"}`} />
      ))}
    </div>
  );
}

/** Skeleton that mimics the Teacher Dashboard layout — KPI cards + schedule + chart */
export function SkeletonTeacherDashboard() {
  return (
    <div className="space-y-6">
      {/* KPI cards row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SkeletonStatCard />
        <SkeletonStatCard />
        <SkeletonStatCard />
        <SkeletonStatCard />
      </div>

      {/* Schedule + chart row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <SkeletonChart />
        </div>
        <SkeletonChart />
      </div>

      {/* Attendance summaries */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <SkeletonCard />
        <SkeletonCard />
        <SkeletonCard />
      </div>
    </div>
  );
}

/** Skeleton that mimics the Student Dashboard layout — info cards + gauge + notifications */
export function SkeletonStudentDashboard() {
  return (
    <div className="space-y-6">
      {/* Metric cards row */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Skeleton className="h-24 rounded-xl" />
        <Skeleton className="h-24 rounded-xl" />
        <Skeleton className="h-24 rounded-xl" />
        <Skeleton className="h-24 rounded-xl" />
      </div>

      {/* Gauge + notifications row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <SkeletonChart />
        <div className="lg:col-span-2">
          <SkeletonCard />
        </div>
      </div>
    </div>
  );
}

// ─── SkeletonSection types ───────────────────────────────────────────────────

export type SkeletonSectionType = "card" | "stat-card" | "chart" | "table" | "text";

export interface SkeletonSection {
  type: SkeletonSectionType;
  /** Number of items to render (cards, stat-cards, or chart items) */
  count?: number;
  /** Rows for table type (default 5) */
  rows?: number;
  /** Columns for table type (default 4) */
  cols?: number;
  /** Lines for text type (default 3) */
  lines?: number;
  /** Wrapper className, e.g. "grid grid-cols-1 gap-4 sm:grid-cols-2" */
  className?: string;
}

interface SkeletonPageProps {
  /** Single layout type — shorthand for a one-section skeleton */
  layout?: SkeletonSectionType;
  /** Number of items for the shorthand layout (cards, stat-cards, etc.) */
  count?: number;
  /** Rows for table shorthand */
  rows?: number;
  /** Columns for table shorthand */
  cols?: number;
  /** Lines for text shorthand */
  lines?: number;
  /** Multi-section config for complex page layouts */
  sections?: SkeletonSection[];
  /** Optional heading skeleton shown above all sections */
  header?: boolean;
  /** Optional className on the root wrapper */
  className?: string;
}

/**
 * Flexible skeleton page — compose a loading placeholder from
 * section types (card, stat-card, chart, table, text).
 *
 * Shorthand examples:
 *   <SkeletonPage layout="card" count={3} />
 *   <SkeletonPage layout="table" rows={6} cols={5} />
 *
 * Multi-section example:
 *   <SkeletonPage header sections={[
 *     { type: "stat-card", count: 4, className: "grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4" },
 *     { type: "chart", count: 2, className: "grid grid-cols-1 gap-6 lg:grid-cols-3" },
 *   ]} />
 */
export function SkeletonPage({ layout, count = 1, rows, cols, lines, sections, header, className }: SkeletonPageProps) {
  const resolvedSections: SkeletonSection[] = sections ?? (layout ? [{ type: layout, count, rows, cols, lines }] : []);

  const renderSection = (sec: SkeletonSection, idx: number) => {
    const items = sec.count ?? 1;
    let wrapperClass = sec.className ?? "";

    // Auto-grid for cards/stat-cards when no custom className
    if (!sec.className && (sec.type === "card" || sec.type === "stat-card")) {
      if (items <= 2) wrapperClass = "grid grid-cols-1 gap-4 sm:grid-cols-2";
      else if (items <= 3) wrapperClass = "grid grid-cols-1 gap-4 sm:grid-cols-3";
      else wrapperClass = "grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4";
    }

    switch (sec.type) {
      case "card":
        return (
          <div key={idx} className={wrapperClass || undefined}>
            {Array.from({ length: items }, (_, i) => <SkeletonCard key={i} />)}
          </div>
        );
      case "stat-card":
        return (
          <div key={idx} className={wrapperClass || undefined}>
            {Array.from({ length: items }, (_, i) => <SkeletonStatCard key={i} />)}
          </div>
        );
      case "chart":
        return (
          <div key={idx} className={wrapperClass || undefined}>
            {Array.from({ length: items }, (_, i) => <SkeletonChart key={i} />)}
          </div>
        );
      case "table":
        return <SkeletonTable key={idx} rows={sec.rows ?? 5} cols={sec.cols ?? 4} className={sec.className} />;
      case "text":
        return (
          <div key={idx} className={wrapperClass || undefined}>
            {Array.from({ length: items }, (_, i) => <SkeletonText key={i} lines={sec.lines ?? 3} />)}
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className={clsx("space-y-6", className)}>
      {header && (
        <div className="space-y-2">
          <div className="h-5 w-1/3 rounded-lg bg-slate-200 dark:bg-slate-700 animate-pulse" />
          <div className="h-3 w-1/5 rounded-lg bg-slate-200 dark:bg-slate-700 animate-pulse" />
        </div>
      )}
      {resolvedSections.map(renderSection)}
    </div>
  );
}

/** Skeleton that mimics the Admin Dashboard layout — KPI cards + charts + announcements */
export function SkeletonDashboard() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <SkeletonStatCard /><SkeletonStatCard /><SkeletonStatCard /><SkeletonStatCard />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2"><SkeletonChart /></div>
        <SkeletonChart />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2"><SkeletonChart /></div>
        <SkeletonCard />
      </div>
    </div>
  );
}

// ─── Data Table ───────────────────────────────────────────────────────────────

export interface Column<T> {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyMessage?: string;
  rowKey: (row: T) => string | number;
  onRowClick?: (row: T) => void;
  /** Built-in pagination — when provided, a Pagination bar renders below the table */
  page?: number;
  total?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
}

const DataTableInner = <T,>({
  columns, data, loading, emptyMessage = "No data found",
  rowKey, onRowClick,
  page, total, pageSize, onPageChange,
}: DataTableProps<T>) => {
  if (loading) return <SkeletonTable rows={5} cols={columns.length} />;
  return (
    <div className="rounded-xl overflow-hidden border border-slate-100">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-100">
          <thead className="bg-slate-50">
            <tr>
              {columns.map(col => (
                <th key={String(col.key)} className={clsx("px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide", col.className)}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50 bg-white">
            {data.length === 0
              ? <tr><td colSpan={columns.length} className="text-center py-16 text-slate-400 text-sm">{emptyMessage}</td></tr>
              : data.map(row => (
                <tr
                  key={rowKey(row)}
                  onClick={() => onRowClick?.(row)}
                  className={clsx("hover:bg-slate-50/60 transition-colors", onRowClick && "cursor-pointer")}
                >
                  {columns.map(col => (
                    <td key={String(col.key)} className={clsx("px-4 py-3 text-sm text-slate-700", col.className)}>
                      {col.render ? col.render(row) : String((row as any)[col.key] ?? "—")}
                    </td>
                  ))}
                </tr>
              ))}
          </tbody>
        </table>
      </div>
      {page !== undefined && total !== undefined && onPageChange && (
        <Pagination page={page} total={total} pageSize={pageSize ?? 25} onChange={onPageChange} />
      )}
    </div>
  );
};

export const DataTable = React.memo(DataTableInner) as typeof DataTableInner;

// ─── Pagination ───────────────────────────────────────────────────────────────

interface PaginationProps {
  page: number;
  total: number;
  pageSize?: number;
  onChange: (page: number) => void;
}

export const Pagination = React.memo(function Pagination({ page, total, pageSize = 25, onChange }: PaginationProps) {
  const totalPages = Math.ceil(total / pageSize);
  if (totalPages <= 1) return null;
  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, total);
  return (
    <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3 bg-white">
      <p className="text-sm text-slate-500">Showing {start}–{end} of {total.toLocaleString()}</p>
      <div className="flex items-center gap-2">
        <Button variant="secondary" size="sm" disabled={page === 1} onClick={() => onChange(page - 1)}>Previous</Button>
        <span className="text-sm text-slate-600">Page {page} of {totalPages}</span>
        <Button variant="secondary" size="sm" disabled={page === totalPages} onClick={() => onChange(page + 1)}>Next</Button>
      </div>
    </div>
  );
});

// ─── Error State ──────────────────────────────────────────────────────────────

export function ErrorState({
  title,
  message,
  onRetry,
}: {
  title?: string;
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex min-h-[200px] flex-col items-center justify-center p-8 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-red-100">
        <ExclamationTriangleIcon className="h-7 w-7 text-red-600" />
      </div>
      <h3 className="mt-4 text-base font-semibold text-slate-800">
        {title ?? "Failed to load data"}
      </h3>
      {message && (
        <p className="mt-1 max-w-sm text-sm text-slate-500">{message}</p>
      )}
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 transition-colors"
        >
          <ArrowPathIcon className="h-4 w-4" />
          Try Again
        </button>
      )}
    </div>
  );
}

// ─── Empty State ──────────────────────────────────────────────────────────────

export function EmptyState({
  icon: Icon, title, description, action,
}: {
  icon?: React.ComponentType<{ className?: string }>;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {Icon && <Icon className="h-12 w-12 text-slate-300 mb-3" />}
      <h3 className="text-base font-semibold text-slate-700">{title}</h3>
      {description && <p className="text-sm text-slate-400 mt-1 max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

// ─── Confirm Dialog ───────────────────────────────────────────────────────────

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  confirmVariant?: ButtonVariant;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
}

export function ConfirmDialog({
  open, title, message, confirmLabel = "Confirm", confirmVariant = "danger",
  onConfirm, onCancel, loading,
}: ConfirmDialogProps) {
  return (
    <Modal open={open} onClose={onCancel} title={title} size="sm"
      footer={
        <>
          <Button variant="secondary" onClick={onCancel} disabled={loading}>Cancel</Button>
          <Button variant={confirmVariant} onClick={onConfirm} loading={loading}>{confirmLabel}</Button>
        </>
      }>
      <p className="text-sm text-slate-600">{message}</p>
    </Modal>
  );
}

// ─── Avatar ───────────────────────────────────────────────────────────────────

export const Avatar = React.memo(function Avatar({ name, src, size = "md", className }: {
  name: string; src?: string; size?: "sm" | "md" | "lg"; className?: string;
}) {
  const sizes = { sm: "h-7 w-7 text-xs", md: "h-9 w-9 text-sm", lg: "h-12 w-12 text-base" };
  const initials = name.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase();
  if (src) return <img src={src} alt={name} className={clsx("rounded-full object-cover flex-shrink-0", sizes[size], className)} />;
  return (
    <div className={clsx("rounded-full bg-indigo-100 text-indigo-700 font-semibold flex items-center justify-center flex-shrink-0", sizes[size], className)}>
      {initials}
    </div>
  );
});
