/**
 * EntitySection — config-driven CRUD section for admin entity management.
 *
 * Renders a card grid for one backend entity (list endpoint) with the shared
 * feature set: search filtering, pagination/infinite-scroll toggle, CSV export,
 * bulk select + delete, create/edit modal, status badges, and delete/toggle
 * per-card actions. Used by the module hub pages (Communication, Attendance…).
 */
import React, { useState, useEffect, useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import toast from "react-hot-toast";
import { api } from "../../api/client";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import { InfiniteScroll } from "./InfiniteScroll";
import { Modal } from "./index";
import { Button } from "./index";
import { toCsv, downloadCsv } from "../../utils";
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentArrowDownIcon,
  AdjustmentsHorizontalIcon,
} from "@heroicons/react/24/outline";

// ─── Spec types ──────────────────────────────────────────────────────────────

export type FieldType = "text" | "number" | "date" | "datetime" | "select" | "textarea" | "bool";

export interface FieldSpec {
  key: string;
  label: string;
  type?: FieldType;
  options?: [string, string][];
  card?: boolean; // show as meta row on card
  badge?: boolean; // render as colored badge
  main?: boolean; // card title
  subtitle?: boolean; // card subtitle
  skipForm?: boolean; // display-only, exclude from form
  full?: boolean; // full-width in form
}

export interface EntityAction {
  label: string;
  url: (id: string | number) => string;
  confirm?: string;
  kind: "approve" | "reject" | "info";
  /** Optional predicate — show the button only on rows where it returns true. */
  visibleIf?: (row: Record<string, unknown>) => boolean;
}

export interface EntityConfig {
  key: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  endpoint: string;
  titleField: string;
  subtitleField?: string;
  fields: FieldSpec[];
  toggleField?: string;
  actions?: EntityAction[];
  readOnly?: boolean;
  searchKeys?: string[];
}

export const BADGE_COLORS: Record<string, string> = {
  P: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  present: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  approved: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  active: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  sent: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  delivered: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  read: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  accepted: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  attended: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  paid: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  verified: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  low: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  A: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  absent: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  rejected: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  cancelled: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  overdue: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  blocked: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  declined: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  bounced: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  urgent: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  L: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  late: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  pending: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  sending: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  queued: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  in_progress: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  warning: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
  E: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  excused: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  planned: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  scheduled: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  invited: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  fingerprint: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  info: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  H: "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
  draft: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
};

export const inputCls =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200";
export const labelCls = "mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300";

// ─── Small presentational helpers ────────────────────────────────────────────

export function StatusBadge({ value, colors }: { value: string; colors?: Record<string, string> }) {
  const map = colors ?? BADGE_COLORS;
  const key = String(value ?? "").toLowerCase();
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
        map[key] ?? "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
      }`}
    >
      {String(value ?? "—").replace(/_/g, " ")}
    </span>
  );
}

export function Toggle({ checked, onChange }: { checked: boolean; onChange: () => void }) {
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

export function CardSkeleton() {
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

export function formatValue(value: unknown, spec: FieldSpec): string {
  if (value === null || value === undefined || value === "") return "—";
  if (spec.type === "bool") {
    return String(value) === "true" ? "Yes" : "No";
  }
  if (spec.type === "select" && spec.options) {
    const found = spec.options.find(([v]) => v === value);
    return found ? found[1] : String(value);
  }
  if (spec.type === "date" && typeof value === "string") {
    return dayjs(value).format("MMM D, YYYY");
  }
  if (spec.type === "datetime" && typeof value === "string") {
    return dayjs(value).format("MMM D, YYYY h:mm A");
  }
  return String(value);
}

function FormField({
  spec,
  value,
  onChange,
}: {
  spec: FieldSpec;
  value: unknown;
  onChange: (v: unknown) => void;
}) {
  const type = spec.type ?? "text";
  if (type === "select") {
    return (
      <div className={spec.full ? "sm:col-span-2" : undefined}>
        <label className={labelCls}>{spec.label}</label>
        <select
          className={inputCls}
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="">— Select —</option>
          {(spec.options ?? []).map(([v, l]) => (
            <option key={v} value={v}>
              {l}
            </option>
          ))}
        </select>
      </div>
    );
  }
  if (type === "bool") {
    return (
      <div className={spec.full ? "sm:col-span-2" : undefined}>
        <label className={labelCls}>{spec.label}</label>
        <select
          className={inputCls}
          value={value ? "true" : "false"}
          onChange={(e) => onChange(e.target.value === "true")}
        >
          <option value="true">Yes</option>
          <option value="false">No</option>
        </select>
      </div>
    );
  }
  if (type === "textarea") {
    return (
      <div className={spec.full ? "sm:col-span-2" : undefined}>
        <label className={labelCls}>{spec.label}</label>
        <textarea
          className={inputCls}
          rows={3}
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
        />
      </div>
    );
  }
  return (
    <div className={spec.full ? "sm:col-span-2" : undefined}>
      <label className={labelCls}>{spec.label}</label>
      <input
        type={type === "datetime" ? "datetime-local" : type === "number" ? "number" : "text"}
        className={inputCls}
        value={value === null || value === undefined ? "" : String(value)}
        onChange={(e) => onChange(type === "number" ? Number(e.target.value) : e.target.value)}
      />
    </div>
  );
}

// ─── Main section ────────────────────────────────────────────────────────────

export function EntitySection({
  cfg,
  basePath,
  search,
  page,
  setPage,
  viewMode,
  registerActions,
}: {
  cfg: EntityConfig;
  basePath: string;
  search: string;
  page: number;
  setPage: (p: number) => void;
  viewMode: "pagination" | "infinite";
  registerActions?: (h: { add?: () => void; export?: () => void }) => void;
}) {
  const qc = useQueryClient();
  const queryKey = [basePath, cfg.endpoint];
  const { data: rows = [], isLoading } = useQuery({
    queryKey,
    queryFn: async () => {
      const res = await api.get<{ results: any[] }>(`${basePath}/${cfg.endpoint}/`, {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const searchKeys = useMemo(
    () =>
      cfg.searchKeys ??
      cfg.fields.filter((f) => f.main || f.subtitle || f.badge || f.card).map((f) => f.key),
    [cfg],
  );

  const filtered = useMemo(() => {
    if (!search.trim()) return rows;
    const q = search.toLowerCase();
    return rows.filter((r: any) =>
      searchKeys.some((k: string) =>
        String(r[k] ?? "")
          .toLowerCase()
          .includes(q),
      ),
    );
  }, [rows, search, searchKeys]);

  const PAGE_SIZE = 12;
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const paginated = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);
  const [infiniteCount, setInfiniteCount] = useState(PAGE_SIZE);
  useEffect(() => {
    setInfiniteCount(PAGE_SIZE);
  }, [cfg.key, search]);
  const infiniteItems = filtered.slice(0, infiniteCount);
  const visible = viewMode === "pagination" ? paginated : infiniteItems;
  const hasMore = infiniteItems.length < filtered.length;

  const bulk = useBulkSelect<{ id: string }>(filtered as unknown as { id: string }[]);

  const save = useMutation({
    mutationFn: ({ id, payload }: { id?: string | number; payload: Record<string, unknown> }) =>
      id !== undefined && id !== null
        ? api.patch(`${basePath}/${cfg.endpoint}/${id}/`, payload)
        : api.post(`${basePath}/${cfg.endpoint}/`, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey });
      setModalOpen(false);
      toast.success("Saved");
    },
    onError: (e: any) => toast.error(e?.message ?? "Save failed"),
  });

  const del = useMutation({
    mutationFn: (id: string | number) => api.delete(`${basePath}/${cfg.endpoint}/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey });
      toast.success("Deleted");
    },
  });

  const toggle = useMutation({
    mutationFn: ({ id, value }: { id: string | number; value: boolean }) =>
      api.patch(`${basePath}/${cfg.endpoint}/${id}/`, { [cfg.toggleField as string]: value }),
    onSuccess: () => qc.invalidateQueries({ queryKey }),
  });

  const runAction = useMutation({
    mutationFn: (url: string) => api.post(url),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey });
      toast.success("Done");
    },
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<any>(null);
  const [form, setForm] = useState<Record<string, unknown>>({});

  const formFields = cfg.fields.filter((f) => !f.skipForm);

  const openCreate = () => {
    setEditing(null);
    const f: Record<string, unknown> = {};
    formFields.forEach((x) => (f[x.key] = x.type === "bool" ? false : ""));
    setForm(f);
    setModalOpen(true);
  };

  const openEdit = (row: any) => {
    setEditing(row);
    const f: Record<string, unknown> = {};
    formFields.forEach((x) => {
      const v = row[x.key];
      f[x.key] = v === null || v === undefined ? (x.type === "bool" ? false : "") : v;
    });
    setForm(f);
    setModalOpen(true);
  };

  const submit = (ev: React.FormEvent) => {
    ev.preventDefault();
    save.mutateAsync({ id: editing?.id, payload: form }).catch(() => undefined);
  };

  const handleBulkDelete = async () => {
    if (bulk.selectedCount === 0) return;
    if (!confirm(`Delete ${bulk.selectedCount} ${cfg.label.toLowerCase()}?`)) return;
    try {
      await Promise.all(bulk.selectedArray.map((id) => del.mutateAsync(id)));
      bulk.clear();
      toast.success("Selected items deleted");
    } catch {
      toast.error("Some deletions failed");
    }
  };

  const handleExport = () => {
    const cols = cfg.fields
      .filter((f) => f.main || f.subtitle || f.badge || f.card)
      .map((f) => ({ key: f.key, label: f.label }));
    downloadCsv(
      toCsv(filtered as unknown as Record<string, unknown>[], cols),
      `${cfg.endpoint}-${dayjs().format("YYYY-MM-DD")}.csv`,
    );
  };

  useEffect(() => {
    registerActions?.({ add: cfg.readOnly ? undefined : openCreate, export: handleExport });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cfg, filtered]);

  if (isLoading) return <CardSkeleton />;

  const metaFields = cfg.fields.filter((f) => f.card && !f.main && !f.subtitle && !f.badge);
  const badgeFields = cfg.fields.filter((f) => f.badge);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <p className="text-sm text-slate-500 dark:text-slate-400">
          {filtered.length} {cfg.label.toLowerCase()}
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleExport}
            leftIcon={<DocumentArrowDownIcon className="h-4 w-4" />}
          >
            Export CSV
          </Button>
          {!cfg.readOnly && (
            <Button size="sm" onClick={openCreate} leftIcon={<PlusIcon className="h-4 w-4" />}>
              Add {cfg.label}
            </Button>
          )}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 p-10 text-center text-slate-400 dark:border-slate-600">
          <p className="text-sm">No {cfg.label.toLowerCase()} found</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {visible.map((row: any) => {
            const title = row[cfg.titleField];
            const sub = cfg.subtitleField ? row[cfg.subtitleField] : undefined;
            return (
              <div
                key={row.id}
                className="relative rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex min-w-0 items-start gap-3">
                    <input
                      type="checkbox"
                      checked={bulk.isSelected(String(row.id))}
                      onChange={() => bulk.toggle(String(row.id))}
                      aria-label={`Select ${title ?? row.id}`}
                      className="mt-1 h-4 w-4 shrink-0 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
                    />
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-slate-900 dark:text-slate-100">
                        {title ?? "—"}
                      </p>
                      {sub !== undefined && sub !== null && sub !== "" && (
                        <p className="truncate text-sm text-slate-500 dark:text-slate-400">{sub}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex shrink-0 items-center gap-1.5">
                    {cfg.toggleField && (
                      <Toggle
                        checked={!!row[cfg.toggleField as string]}
                        onChange={() =>
                          toggle.mutate({ id: row.id, value: !row[cfg.toggleField as string] })
                        }
                      />
                    )}
                    {(cfg.actions ?? [])
                      .filter((a) => !a.visibleIf || a.visibleIf(row as Record<string, unknown>))
                      .map((a) => {
                        const Icon =
                          a.kind === "approve"
                            ? CheckCircleIcon
                            : a.kind === "reject"
                              ? XCircleIcon
                              : AdjustmentsHorizontalIcon;
                        return (
                          <button
                            key={a.label}
                            type="button"
                            title={a.label}
                            onClick={() => {
                              if (a.confirm && !confirm(a.confirm)) return;
                              runAction.mutate(a.url(row.id));
                            }}
                            className={`rounded-md p-1.5 ${
                              a.kind === "approve"
                                ? "text-green-600 hover:bg-green-50 dark:hover:bg-green-900/30"
                                : a.kind === "reject"
                                  ? "text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30"
                                  : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700"
                            }`}
                          >
                            <Icon className="h-4 w-4" />
                          </button>
                        );
                      })}
                    {!cfg.readOnly && (
                      <>
                        <button
                          type="button"
                          title="Edit"
                          onClick={() => openEdit(row)}
                          className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700"
                        >
                          <PencilSquareIcon className="h-4 w-4" />
                        </button>
                        <button
                          type="button"
                          title="Delete"
                          onClick={() => del.mutate(row.id)}
                          className="rounded-md p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </>
                    )}
                  </div>
                </div>
                {badgeFields.length > 0 && (
                  <div className="mt-2.5 flex flex-wrap gap-1.5">
                    {badgeFields.map((f) => (
                      <StatusBadge key={f.key} value={String(row[f.key] ?? "—")} />
                    ))}
                  </div>
                )}
                {metaFields.length > 0 && (
                  <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-1.5 text-sm">
                    {metaFields.map((f) => (
                      <div key={f.key}>
                        <dt className="text-xs text-slate-400 dark:text-slate-500">{f.label}</dt>
                        <dd className="truncate text-slate-700 dark:text-slate-200">
                          {formatValue(row[f.key], f)}
                        </dd>
                      </div>
                    ))}
                  </dl>
                )}
              </div>
            );
          })}
        </div>
      )}

      {bulk.selectedCount > 0 && (
        <div className="fixed bottom-6 left-1/2 z-40 flex -translate-x-1/2 items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-2.5 shadow-xl dark:border-slate-700 dark:bg-slate-800">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-200">
            {bulk.selectedCount} selected
          </span>
          {!cfg.readOnly && (
            <button
              onClick={handleBulkDelete}
              className="inline-flex items-center gap-1 rounded-lg bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700"
            >
              <TrashIcon className="h-4 w-4" /> Delete
            </button>
          )}
          <button
            onClick={bulk.clear}
            className="rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300"
          >
            Clear
          </button>
        </div>
      )}

      {viewMode === "pagination" && filtered.length > PAGE_SIZE && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Page {safePage} of {totalPages}
          </p>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage(safePage - 1)}
              disabled={safePage <= 1}
              className="rounded-lg border border-slate-200 p-1.5 text-slate-600 disabled:opacity-40 dark:border-slate-600 dark:text-slate-300"
              aria-label="Previous page"
            >
              <ChevronLeftIcon className="h-4 w-4" />
            </button>
            <button
              onClick={() => setPage(safePage + 1)}
              disabled={safePage >= totalPages}
              className="rounded-lg border border-slate-200 p-1.5 text-slate-600 disabled:opacity-40 dark:border-slate-600 dark:text-slate-300"
              aria-label="Next page"
            >
              <ChevronRightIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {viewMode === "infinite" && hasMore && (
        <InfiniteScroll
          items={[]}
          totalCount={filtered.length}
          hasMore={hasMore}
          isLoading={isLoading}
          isFetchingNext={false}
          onLoadMore={() => setInfiniteCount((c) => c + PAGE_SIZE)}
          renderItem={() => null}
          endMessage="End of list"
        />
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? `Edit ${cfg.label}` : `Add ${cfg.label}`}
      >
        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {formFields.map((f) => (
              <FormField
                key={f.key}
                spec={f}
                value={form[f.key]}
                onChange={(v) => setForm((prev) => ({ ...prev, [f.key]: v }))}
              />
            ))}
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="secondary" type="button" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={save.isPending}>
              {editing ? "Save Changes" : "Create"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
