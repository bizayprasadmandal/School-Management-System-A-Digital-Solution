/**
 * Access Control — Admin page for role-based access control: school roles,
 * the global permission catalog, role-permission grants, and user-role
 * assignments.
 */
import React, { useState, useMemo, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  UserGroupIcon,
  ShieldCheckIcon,
  LockClosedIcon,
  KeyIcon,
  IdentificationIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  AdjustmentsHorizontalIcon,
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
import { useUserRole } from "../../store/authStore";
import { toCsv, downloadCsv } from "../../utils";

// ─── Types ───────────────────────────────────────────────────────────────────

interface Role {
  id: string;
  name: string;
  description: string;
  parent_role: string | null;
  level: number;
  is_active: boolean;
  is_system_role: boolean;
  permission_count: number;
  created_at: string;
  updated_at: string;
}

interface Permission {
  id: string;
  name: string;
  codename: string;
  description: string;
  permission_type: "module" | "action" | "data" | "report";
  permission_type_display: string;
  module: string;
  is_active: boolean;
  created_at: string;
}

interface RolePermission {
  id: string;
  role: string;
  role_name: string;
  permission: string;
  permission_name: string;
  permission_codename: string;
  permission_module: string;
  permission_type_display: string;
  granted: boolean;
  granted_at: string;
  granted_by_name: string | null;
}

interface UserRole {
  id: string;
  user: string;
  user_name: string | null;
  user_email: string;
  role: string;
  role_name: string;
  scope: Record<string, unknown>;
  is_active: boolean;
  assigned_date: string;
  expiry_date: string | null;
  assigned_by_name: string | null;
}

interface DirectoryUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string;
  is_active: boolean;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  inactive: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  granted: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  denied: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

const PERMISSION_TYPE_COLORS: Record<string, string> = {
  module: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300",
  action: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  data: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  report: "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
};

const PERMISSION_TYPES: readonly (readonly [string, string])[] = [
  ["module", "Module Access"],
  ["action", "Action Permission"],
  ["data", "Data Permission"],
  ["report", "Report Permission"],
];

const ROLE_LEVELS: readonly (readonly [string, string])[] = [
  ["0", "0 — Lowest"],
  ["10", "10"],
  ["20", "20"],
  ["30", "30"],
  ["40", "40"],
  ["50", "50"],
  ["60", "60"],
  ["70", "70"],
  ["80", "80"],
  ["90", "90"],
  ["100", "100 — Highest"],
];

// ─── Tabs config ─────────────────────────────────────────────────────────────

type TabType = "roles" | "permissions" | "grants" | "assignments";

const TABS: {
  key: TabType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  { key: "roles", label: "Roles", icon: UserGroupIcon },
  { key: "permissions", label: "Permission Catalog", icon: ShieldCheckIcon },
  { key: "grants", label: "Role Permissions", icon: LockClosedIcon },
  { key: "assignments", label: "User Roles", icon: IdentificationIcon },
];

const TAB_LABELS: Record<TabType, { singular: string; plural: string }> = {
  roles: { singular: "role", plural: "roles" },
  permissions: { singular: "permission", plural: "permissions" },
  grants: { singular: "grant", plural: "role permissions" },
  assignments: { singular: "assignment", plural: "user roles" },
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

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function AccessControlPage() {
  useTitle("Access Control");
  const qc = useQueryClient();
  const userRole = useUserRole();
  const isSuperAdmin = userRole === "super_admin";

  const [activeTab, setActiveTab] = useState<TabType>("roles");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const searchRef = useRef<HTMLInputElement>(null);

  // Modals
  const [showRoleForm, setShowRoleForm] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [showPermissionForm, setShowPermissionForm] = useState(false);
  const [editingPermission, setEditingPermission] = useState<Permission | null>(null);
  const [showGrantForm, setShowGrantForm] = useState(false);
  const [editingGrant, setEditingGrant] = useState<RolePermission | null>(null);
  const [showAssignmentForm, setShowAssignmentForm] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState<UserRole | null>(null);

  // ── Data fetching ───────────────────────────────────────────────────────

  const { data: roles = [], isLoading: rolesLoading } = useQuery({
    queryKey: ["auth-roles"],
    queryFn: async () => {
      const res = await api.get<{ results: Role[] }>("/auth/role/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: permissions = [], isLoading: permissionsLoading } = useQuery({
    queryKey: ["auth-permissions"],
    queryFn: async () => {
      const res = await api.get<{ results: Permission[] }>("/auth/permission/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: grants = [], isLoading: grantsLoading } = useQuery({
    queryKey: ["auth-grants"],
    queryFn: async () => {
      const res = await api.get<{ results: RolePermission[] }>("/auth/role-permission/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const { data: assignments = [], isLoading: assignmentsLoading } = useQuery({
    queryKey: ["auth-assignments"],
    queryFn: async () => {
      const res = await api.get<{ results: UserRole[] }>("/auth/user-role/", {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  // ── Mutations ───────────────────────────────────────────────────────────

  const deleteRole = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/role/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["auth-roles"] });
      qc.invalidateQueries({ queryKey: ["auth-grants"] });
      toast.success("Role deleted");
    },
  });

  const deletePermission = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/permission/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["auth-permissions"] });
      qc.invalidateQueries({ queryKey: ["auth-grants"] });
      toast.success("Permission deleted");
    },
  });

  const deleteGrant = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/role-permission/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["auth-grants"] });
      toast.success("Grant removed");
    },
  });

  const deleteAssignment = useMutation({
    mutationFn: (id: string) => api.delete(`/auth/user-role/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["auth-assignments"] });
      toast.success("Assignment removed");
    },
  });

  const toggleRole = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      api.patch(`/auth/role/${id}/`, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["auth-roles"] }),
  });

  // ── Filtering ───────────────────────────────────────────────────────────

  const filteredRoles = useMemo(() => {
    if (!search.trim()) return roles;
    const q = search.toLowerCase();
    return roles.filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        r.description.toLowerCase().includes(q) ||
        String(r.level).includes(q),
    );
  }, [roles, search]);

  const filteredPermissions = useMemo(() => {
    if (!search.trim()) return permissions;
    const q = search.toLowerCase();
    return permissions.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.codename.toLowerCase().includes(q) ||
        p.module.toLowerCase().includes(q) ||
        p.permission_type_display.toLowerCase().includes(q),
    );
  }, [permissions, search]);

  const filteredGrants = useMemo(() => {
    if (!search.trim()) return grants;
    const q = search.toLowerCase();
    return grants.filter(
      (g) =>
        g.role_name.toLowerCase().includes(q) ||
        g.permission_name.toLowerCase().includes(q) ||
        g.permission_codename.toLowerCase().includes(q) ||
        g.permission_module.toLowerCase().includes(q),
    );
  }, [grants, search]);

  const filteredAssignments = useMemo(() => {
    if (!search.trim()) return assignments;
    const q = search.toLowerCase();
    return assignments.filter(
      (a) =>
        (a.user_name ?? "").toLowerCase().includes(q) ||
        a.user_email.toLowerCase().includes(q) ||
        a.role_name.toLowerCase().includes(q),
    );
  }, [assignments, search]);

  const allFiltered =
    activeTab === "roles"
      ? filteredRoles
      : activeTab === "permissions"
        ? filteredPermissions
        : activeTab === "grants"
          ? filteredGrants
          : filteredAssignments;

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
    deleteRole.isPending ||
    deletePermission.isPending ||
    deleteGrant.isPending ||
    deleteAssignment.isPending;

  const handleBulkDelete = async () => {
    if (bulk.selectedCount === 0) return;
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(
        bulk.selectedArray.map((id) => {
          if (activeTab === "roles") return deleteRole.mutateAsync(id);
          if (activeTab === "permissions") return deletePermission.mutateAsync(id);
          if (activeTab === "grants") return deleteGrant.mutateAsync(id);
          return deleteAssignment.mutateAsync(id);
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
    if (activeTab === "roles") {
      downloadCsv(
        toCsv(filteredRoles as unknown as Record<string, unknown>[], [
          { key: "name", label: "Name" },
          { key: "description", label: "Description" },
          { key: "level", label: "Level" },
          { key: "permission_count", label: "Permissions" },
          { key: "is_active", label: "Active" },
          { key: "is_system_role", label: "System" },
        ]),
        `auth-roles-${now}.csv`,
      );
    } else if (activeTab === "permissions") {
      downloadCsv(
        toCsv(filteredPermissions as unknown as Record<string, unknown>[], [
          { key: "name", label: "Name" },
          { key: "codename", label: "Codename" },
          { key: "module", label: "Module" },
          { key: "permission_type_display", label: "Type" },
          { key: "is_active", label: "Active" },
        ]),
        `auth-permissions-${now}.csv`,
      );
    } else if (activeTab === "grants") {
      downloadCsv(
        toCsv(filteredGrants as unknown as Record<string, unknown>[], [
          { key: "role_name", label: "Role" },
          { key: "permission_name", label: "Permission" },
          { key: "permission_codename", label: "Codename" },
          { key: "permission_module", label: "Module" },
          { key: "granted", label: "Granted" },
        ]),
        `auth-role-permissions-${now}.csv`,
      );
    } else {
      downloadCsv(
        toCsv(filteredAssignments as unknown as Record<string, unknown>[], [
          { key: "user_name", label: "User" },
          { key: "user_email", label: "Email" },
          { key: "role_name", label: "Role" },
          { key: "is_active", label: "Active" },
          { key: "assigned_date", label: "Assigned" },
          { key: "expiry_date", label: "Expires" },
        ]),
        `auth-user-roles-${now}.csv`,
      );
    }
  };

  const handleBulkExport = () => {
    const cols = [{ key: "id", label: "ID" }];
    downloadCsv(
      toCsv(
        bulk.selectedItems.map((i) => ({ id: i.id })),
        cols,
      ),
      `auth-bulk-${dayjs().format("YYYY-MM-DD")}.csv`,
    );
  };

  // ── Keyboard shortcuts ──────────────────────────────────────────────────

  const { open: helpOpen, setOpen: setHelpOpen } = useShortcutHelp();
  useKeyboardShortcuts({
    onCreate: () => {
      if (activeTab === "roles") {
        setEditingRole(null);
        setShowRoleForm(true);
      } else if (activeTab === "permissions") {
        if (!isSuperAdmin) return;
        setEditingPermission(null);
        setShowPermissionForm(true);
      } else if (activeTab === "grants") {
        setEditingGrant(null);
        setShowGrantForm(true);
      } else {
        setEditingAssignment(null);
        setShowAssignmentForm(true);
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
    activeTab === "roles"
      ? rolesLoading
      : activeTab === "permissions"
        ? permissionsLoading
        : activeTab === "grants"
          ? grantsLoading
          : assignmentsLoading;

  const createButton =
    activeTab === "roles"
      ? {
          label: "Add Role",
          action: () => {
            setEditingRole(null);
            setShowRoleForm(true);
          },
        }
      : activeTab === "permissions"
        ? {
            label: "Add Permission",
            action: () => {
              setEditingPermission(null);
              setShowPermissionForm(true);
            },
          }
        : activeTab === "grants"
          ? {
              label: "Add Grant",
              action: () => {
                setEditingGrant(null);
                setShowGrantForm(true);
              },
            }
          : {
              label: "Assign Role",
              action: () => {
                setEditingAssignment(null);
                setShowAssignmentForm(true);
              },
            };

  const canCreate = activeTab !== "permissions" || isSuperAdmin;

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Access Control</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Roles, permissions, and role-based access for your school
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
        {canCreate && (
          <Button onClick={createButton.action}>
            <PlusIcon className="mr-1.5 h-4 w-4" />
            {createButton.label}
          </Button>
        )}
      </div>

      {/* Tabs */}
      <div className="flex w-fit gap-1 overflow-x-auto rounded-lg bg-slate-100 p-1 dark:bg-slate-800">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const counts: Record<TabType, number> = {
            roles: roles.length,
            permissions: permissions.length,
            grants: grants.length,
            assignments: assignments.length,
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
            activeTab === "roles"
              ? UserGroupIcon
              : activeTab === "permissions"
                ? ShieldCheckIcon
                : activeTab === "grants"
                  ? LockClosedIcon
                  : IdentificationIcon
          }
          title={`No ${TAB_LABELS[activeTab].plural}`}
          description={`Add your first ${TAB_LABELS[activeTab].singular} to get started`}
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
                  canWrite={canCreate}
                  onEdit={() => {
                    if (activeTab === "roles") {
                      setEditingRole(item as Role);
                      setShowRoleForm(true);
                    } else if (activeTab === "permissions") {
                      setEditingPermission(item as Permission);
                      setShowPermissionForm(true);
                    } else if (activeTab === "grants") {
                      setEditingGrant(item as RolePermission);
                      setShowGrantForm(true);
                    } else {
                      setEditingAssignment(item as UserRole);
                      setShowAssignmentForm(true);
                    }
                  }}
                  onDelete={() => {
                    if (!confirm("Delete this item?")) return;
                    if (activeTab === "roles") deleteRole.mutate(item.id);
                    else if (activeTab === "permissions") deletePermission.mutate(item.id);
                    else if (activeTab === "grants") deleteGrant.mutate(item.id);
                    else deleteAssignment.mutate(item.id);
                  }}
                  onToggleActive={
                    activeTab === "roles"
                      ? () =>
                          toggleRole.mutate({
                            id: item.id,
                            is_active: !(item as Role).is_active,
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
                  canWrite={canCreate}
                  onEdit={() => {
                    if (activeTab === "roles") {
                      setEditingRole(item as Role);
                      setShowRoleForm(true);
                    } else if (activeTab === "permissions") {
                      setEditingPermission(item as Permission);
                      setShowPermissionForm(true);
                    } else if (activeTab === "grants") {
                      setEditingGrant(item as RolePermission);
                      setShowGrantForm(true);
                    } else {
                      setEditingAssignment(item as UserRole);
                      setShowAssignmentForm(true);
                    }
                  }}
                  onDelete={() => {
                    if (!confirm("Delete this item?")) return;
                    if (activeTab === "roles") deleteRole.mutate(item.id);
                    else if (activeTab === "permissions") deletePermission.mutate(item.id);
                    else if (activeTab === "grants") deleteGrant.mutate(item.id);
                    else deleteAssignment.mutate(item.id);
                  }}
                  onToggleActive={
                    activeTab === "roles"
                      ? () =>
                          toggleRole.mutate({
                            id: item.id,
                            is_active: !(item as Role).is_active,
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
      {activeTab === "roles" && (
        <RoleFormModal
          open={showRoleForm}
          onClose={() => {
            setShowRoleForm(false);
            setEditingRole(null);
          }}
          role={editingRole}
          roles={roles}
          onSaved={() => {
            setShowRoleForm(false);
            setEditingRole(null);
            qc.invalidateQueries({ queryKey: ["auth-roles"] });
          }}
        />
      )}
      {activeTab === "permissions" && (
        <PermissionFormModal
          open={showPermissionForm}
          onClose={() => {
            setShowPermissionForm(false);
            setEditingPermission(null);
          }}
          permission={editingPermission}
          onSaved={() => {
            setShowPermissionForm(false);
            setEditingPermission(null);
            qc.invalidateQueries({ queryKey: ["auth-permissions"] });
          }}
        />
      )}
      {activeTab === "grants" && (
        <GrantFormModal
          open={showGrantForm}
          onClose={() => {
            setShowGrantForm(false);
            setEditingGrant(null);
          }}
          grant={editingGrant}
          roles={roles}
          permissions={permissions}
          onSaved={() => {
            setShowGrantForm(false);
            setEditingGrant(null);
            qc.invalidateQueries({ queryKey: ["auth-grants"] });
          }}
        />
      )}
      {activeTab === "assignments" && (
        <AssignmentFormModal
          open={showAssignmentForm}
          onClose={() => {
            setShowAssignmentForm(false);
            setEditingAssignment(null);
          }}
          assignment={editingAssignment}
          roles={roles}
          onSaved={() => {
            setShowAssignmentForm(false);
            setEditingAssignment(null);
            qc.invalidateQueries({ queryKey: ["auth-assignments"] });
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
  canWrite,
}: {
  tab: TabType;
  item: { id: string };
  selected: boolean;
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
  onToggleActive?: () => void;
  canWrite: boolean;
}) {
  const checkboxCls =
    "h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600";
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
          {tab === "roles" && <RoleCard item={item as Role} />}
          {tab === "permissions" && <PermissionCard item={item as Permission} />}
          {tab === "grants" && <GrantCard item={item as RolePermission} />}
          {tab === "assignments" && <AssignmentCard item={item as UserRole} />}
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
          {canWrite && (
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

function RoleCard({ item }: { item: Role }) {
  return (
    <>
      <div className="flex items-center gap-2">
        <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
          {item.name}
        </p>
        {item.is_system_role && (
          <span className="inline-flex items-center rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-500 dark:bg-slate-700 dark:text-slate-300">
            System
          </span>
        )}
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.is_active ? "active" : "inactive"} colors={STATUS_COLORS} />
        <span className="rounded-full bg-indigo-50 px-2 py-0.5 font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">
          Lv {item.level}
        </span>
        <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-600 dark:bg-slate-700 dark:text-slate-300">
          {item.permission_count} permissions
        </span>
      </div>
      {item.description && (
        <p className="mt-1 truncate text-xs text-slate-400">{item.description}</p>
      )}
    </>
  );
}

function PermissionCard({ item }: { item: Permission }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.name}
      </p>
      <p className="truncate font-mono text-xs text-slate-400">{item.codename}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <span
          className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
            PERMISSION_TYPE_COLORS[item.permission_type] ??
            "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
          }`}
        >
          {item.permission_type_display}
        </span>
        {item.module && (
          <span className="rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-600 dark:bg-slate-700 dark:text-slate-300">
            {item.module}
          </span>
        )}
        <Badge value={item.is_active ? "active" : "inactive"} colors={STATUS_COLORS} />
      </div>
      {item.description && (
        <p className="mt-1 truncate text-xs text-slate-400">{item.description}</p>
      )}
    </>
  );
}

function GrantCard({ item }: { item: RolePermission }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.permission_name}
      </p>
      <p className="truncate font-mono text-xs text-slate-400">{item.permission_codename}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 font-medium text-slate-600 dark:bg-slate-700 dark:text-slate-300">
          <UserGroupIcon className="h-3 w-3" />
          {item.role_name}
        </span>
        <Badge value={item.granted ? "granted" : "denied"} colors={STATUS_COLORS} />
        {item.permission_module && (
          <span className="text-slate-400">📦 {item.permission_module}</span>
        )}
      </div>
      {item.granted_by_name && (
        <p className="mt-1 text-xs text-slate-400">
          Granted by {item.granted_by_name} · {dayjs(item.granted_at).format("MMM D, YYYY")}
        </p>
      )}
    </>
  );
}

function AssignmentCard({ item }: { item: UserRole }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.user_name ?? item.user_email}
      </p>
      <p className="truncate text-xs text-slate-400">{item.user_email}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <span className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-0.5 font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300">
          <KeyIcon className="h-3 w-3" />
          {item.role_name}
        </span>
        <Badge value={item.is_active ? "active" : "inactive"} colors={STATUS_COLORS} />
      </div>
      <p className="mt-1 text-xs text-slate-400">
        Assigned {dayjs(item.assigned_date).format("MMM D, YYYY")}
        {item.expiry_date && ` · expires ${dayjs(item.expiry_date).format("MMM D, YYYY")}`}
      </p>
    </>
  );
}

// ─── Role Form Modal ─────────────────────────────────────────────────────────

function RoleFormModal({
  open,
  onClose,
  role,
  roles,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  role?: Role | null;
  roles: Role[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    name: role?.name ?? "",
    description: role?.description ?? "",
    parent_role: role?.parent_role ?? "",
    level: role?.level != null ? String(role.level) : "50",
    is_active: role?.is_active ?? true,
  });
  const isEdit = !!role;
  const isSystem = role?.is_system_role ?? false;
  const createMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.post("/auth/role/", {
        ...data,
        parent_role: data.parent_role || null,
        level: Number(data.level),
      }),
    onSuccess: () => {
      toast.success("Role created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/auth/role/${role!.id}/`, {
        ...data,
        parent_role: data.parent_role || null,
        level: Number(data.level),
      }),
    onSuccess: () => {
      toast.success("Role updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const parentOptions = roles
    .filter((r) => r.id !== role?.id)
    .map((r) => [r.id, r.name] as [string, string]);
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Role name is required");
    const data = { ...f, name: f.name.trim() };
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Role" : "Add Role"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Role Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className={inputCls}
              placeholder="e.g. Class Teacher"
              required
            />
          </div>
          <SelectField
            label="Authority Level"
            value={f.level}
            options={ROLE_LEVELS}
            onChange={(v) => setF((p) => ({ ...p, level: v }))}
          />
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            className={`${inputCls} min-h-[70px]`}
            placeholder="What can this role do?"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Parent Role</label>
            <select
              value={f.parent_role}
              onChange={(e) => setF((p) => ({ ...p, parent_role: e.target.value }))}
              className={inputCls}
            >
              <option value="">None</option>
              {parentOptions.map(([v, l]) => (
                <option key={v} value={v}>
                  {l}
                </option>
              ))}
            </select>
          </div>
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
        {isSystem && (
          <p className="rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-500 dark:bg-slate-700/50 dark:text-slate-400">
            This is a system role — it cannot be deleted.
          </p>
        )}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"} Role
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Permission Form Modal ───────────────────────────────────────────────────

function PermissionFormModal({
  open,
  onClose,
  permission,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  permission?: Permission | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    name: permission?.name ?? "",
    codename: permission?.codename ?? "",
    description: permission?.description ?? "",
    module: permission?.module ?? "",
    permission_type: permission?.permission_type ?? "module",
    is_active: permission?.is_active ?? true,
  });
  const isEdit = !!permission;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/auth/permission/", data),
    onSuccess: () => {
      toast.success("Permission created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/auth/permission/${permission!.id}/`, data),
    onSuccess: () => {
      toast.success("Permission updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Permission name is required");
    if (!f.codename.trim()) return toast.error("Codename is required");
    const data = { ...f, name: f.name.trim(), codename: f.codename.trim() };
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Permission" : "Add Permission"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className={inputCls}
              placeholder="e.g. View Student Records"
              required
            />
          </div>
          <div>
            <label className={labelCls}>Codename *</label>
            <input
              value={f.codename}
              onChange={(e) => setF((p) => ({ ...p, codename: e.target.value }))}
              className={`${inputCls} font-mono`}
              placeholder="e.g. students.view"
              required
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Permission Type"
            value={f.permission_type}
            options={PERMISSION_TYPES}
            onChange={(v) =>
              setF((p) => ({
                ...p,
                permission_type: v as typeof f.permission_type,
              }))
            }
          />
          <div>
            <label className={labelCls}>Module</label>
            <input
              value={f.module}
              onChange={(e) => setF((p) => ({ ...p, module: e.target.value }))}
              className={inputCls}
              placeholder="e.g. students, fees, library"
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
            {isEdit ? "Update" : "Create"} Permission
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Grant Form Modal ────────────────────────────────────────────────────────

function GrantFormModal({
  open,
  onClose,
  grant,
  roles,
  permissions,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  grant?: RolePermission | null;
  roles: Role[];
  permissions: Permission[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    role: grant?.role ?? "",
    permission: grant?.permission ?? "",
    granted: grant?.granted ?? true,
  });
  const isEdit = !!grant;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/auth/role-permission/", data),
    onSuccess: () => {
      toast.success("Permission granted");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/auth/role-permission/${grant!.id}/`, data),
    onSuccess: () => {
      toast.success("Grant updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.role) return toast.error("Select a role");
    if (!f.permission) return toast.error("Select a permission");
    if (isEdit) updateMut.mutate(f);
    else createMut.mutate(f);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Grant" : "Grant Permission to Role"}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>Role *</label>
          <select
            value={f.role}
            onChange={(e) => setF((p) => ({ ...p, role: e.target.value }))}
            className={inputCls}
            disabled={isEdit}
            required
          >
            <option value="">Select a role...</option>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelCls}>Permission *</label>
          <select
            value={f.permission}
            onChange={(e) => setF((p) => ({ ...p, permission: e.target.value }))}
            className={inputCls}
            disabled={isEdit}
            required
          >
            <option value="">Select a permission...</option>
            {permissions.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.codename})
              </option>
            ))}
          </select>
        </div>
        <label className="flex cursor-pointer items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.granted}
            onChange={(e) => setF((p) => ({ ...p, granted: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
          />
          Granted (uncheck to explicitly deny)
        </label>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Grant"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Assignment Form Modal ───────────────────────────────────────────────────

function AssignmentFormModal({
  open,
  onClose,
  assignment,
  roles,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  assignment?: UserRole | null;
  roles: Role[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    role: assignment?.role ?? "",
    is_active: assignment?.is_active ?? true,
    expiry_date: assignment?.expiry_date ?? "",
  });
  const [userId, setUserId] = useState(assignment?.user ?? "");
  const [userSearch, setUserSearch] = useState(assignment?.user_email ?? "");
  const isEdit = !!assignment;

  const { data: directory = [] } = useQuery({
    queryKey: ["auth-directory", userSearch],
    queryFn: async () => {
      if (userSearch.length < 2) return [];
      const res = await api.get<{ results: DirectoryUser[] }>("/auth/user-directory/", {
        search: userSearch,
        page_size: 10,
      });
      return res.results ?? [];
    },
    enabled: userSearch.length >= 2,
  });

  const createMut = useMutation({
    mutationFn: () =>
      api.post("/auth/user-role/", {
        user: userId,
        role: f.role,
        is_active: f.is_active,
        expiry_date: f.expiry_date || null,
      }),
    onSuccess: () => {
      toast.success("Role assigned");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: () =>
      api.patch(`/auth/user-role/${assignment!.id}/`, {
        is_active: f.is_active,
        expiry_date: f.expiry_date || null,
      }),
    onSuccess: () => {
      toast.success("Assignment updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isEdit && !userId) return toast.error("Search and select a user");
    if (!f.role) return toast.error("Select a role");
    if (isEdit) updateMut.mutate();
    else createMut.mutate();
  };
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Role Assignment" : "Assign Role to User"}
    >
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>{isEdit ? "User" : "User *"}</label>
          {isEdit ? (
            <input value={userSearch} readOnly className={`${inputCls} opacity-70`} />
          ) : (
            <>
              <input
                value={userSearch}
                onChange={(e) => {
                  setUserSearch(e.target.value);
                  setUserId("");
                }}
                className={inputCls}
                placeholder="Search by name or email..."
                required
              />
              {userSearch.length >= 2 && !userId && directory.length > 0 && (
                <div className="mt-1 max-h-44 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-lg dark:border-slate-600 dark:bg-slate-800">
                  {directory.map((u) => (
                    <button
                      key={u.id}
                      type="button"
                      onClick={() => {
                        setUserId(u.id);
                        setUserSearch(u.full_name || u.email);
                      }}
                      className="flex w-full flex-col px-3 py-2 text-left text-sm hover:bg-slate-50 dark:hover:bg-slate-700 dark:text-slate-200"
                    >
                      <span className="font-medium">{u.full_name || u.email}</span>
                      <span className="text-xs text-slate-400">
                        {u.email} · {u.role.replace(/_/g, " ")}
                      </span>
                    </button>
                  ))}
                </div>
              )}
              {userSearch.length >= 2 && !userId && directory.length === 0 && (
                <p className="mt-1 text-xs text-slate-400">No matching users found</p>
              )}
            </>
          )}
        </div>
        <div>
          <label className={labelCls}>Role *</label>
          <select
            value={f.role}
            onChange={(e) => setF((p) => ({ ...p, role: e.target.value }))}
            className={inputCls}
            disabled={isEdit}
            required
          >
            <option value="">Select a role...</option>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Expiry Date</label>
            <input
              type="date"
              value={f.expiry_date}
              onChange={(e) => setF((p) => ({ ...p, expiry_date: e.target.value }))}
              className={inputCls}
            />
          </div>
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
            {isEdit ? "Update" : "Assign Role"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
