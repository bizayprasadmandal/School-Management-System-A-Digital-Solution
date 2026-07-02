/**
 * Common UI Components — reusable across all role dashboards
 */

import React, { Fragment } from "react";
import { XMarkIcon } from "@heroicons/react/24/outline";
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

export function Button({
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
}

// ─── Input ────────────────────────────────────────────────────────────────────

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
  leftAddon?: React.ReactNode;
  rightAddon?: React.ReactNode;
}

export function Input({ label, error, hint, leftAddon, rightAddon, className, id, ...props }: InputProps) {
  const inputId = id ?? label?.toLowerCase().replace(/\s+/g, "-");
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label htmlFor={inputId} className="text-xs font-semibold text-slate-700">{label}</label>}
      <div className="relative flex items-center">
        {leftAddon && <div className="absolute left-3 text-slate-400">{leftAddon}</div>}
        <input
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
}

// ─── Select ───────────────────────────────────────────────────────────────────

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: { value: string | number; label: string }[];
  placeholder?: string;
}

export function Select({ label, error, options, placeholder, className, id, ...props }: SelectProps) {
  const selectId = id ?? label?.toLowerCase().replace(/\s+/g, "-");
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label htmlFor={selectId} className="text-xs font-semibold text-slate-700">{label}</label>}
      <select
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
}

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

export function Badge({ color = "slate", dot, children, className }: BadgeProps) {
  return (
    <span className={clsx("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold", BADGE_COLORS[color], className)}>
      {dot && <span className={clsx("h-1.5 w-1.5 rounded-full", DOT_COLORS[color])} />}
      {children}
    </span>
  );
}

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

export function PageLoader({ text = "Loading…" }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 text-slate-400">
      <Spinner size="lg" />
      <p className="text-sm">{text}</p>
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
}

export function DataTable<T>({ columns, data, loading, emptyMessage = "No data found", rowKey, onRowClick }: DataTableProps<T>) {
  if (loading) return <PageLoader />;
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
    </div>
  );
}

// ─── Pagination ───────────────────────────────────────────────────────────────

interface PaginationProps {
  page: number;
  total: number;
  pageSize?: number;
  onChange: (page: number) => void;
}

export function Pagination({ page, total, pageSize = 25, onChange }: PaginationProps) {
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

export function Avatar({ name, src, size = "md", className }: {
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
}
