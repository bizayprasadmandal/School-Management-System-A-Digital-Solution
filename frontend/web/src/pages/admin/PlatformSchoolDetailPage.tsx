/**
 * PlatformSchoolDetailPage — Super admin view/edit individual school
 * Shows school stats, settings, and admin management.
 */

import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeftIcon,
  BuildingOffice2Icon,
  UsersIcon,
  AcademicCapIcon,
  BanknotesIcon,
  PencilIcon,
  PlusIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import {
  usePlatformSchool,
  useUpdateSchool,
  useToggleSchoolActive,
  useSchoolAdmins,
  useAddSchoolAdmin,
} from "../../api/hooks";
import type { School, SchoolAdminUser } from "../../types";

function AddAdminModal({
  schoolId,
  open,
  onClose,
}: {
  schoolId: string;
  open: boolean;
  onClose: () => void;
}) {
  const addAdmin = useAddSchoolAdmin(schoolId);
  const [form, setForm] = useState({
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    phone: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.email || !form.first_name || !form.last_name) {
      toast.error("Email, First Name, and Last Name are required.");
      return;
    }
    try {
      const result = await addAdmin.mutateAsync(
        form as Partial<SchoolAdminUser> & { password?: string },
      );
      const tempPw = (result as SchoolAdminUser & { temporary_password?: string })
        .temporary_password;
      if (tempPw) {
        toast.success(`School admin created! Temporary password: ${tempPw}`);
      } else {
        toast.success("School admin created!");
      }
      onClose();
      setForm({ email: "", first_name: "", last_name: "", password: "", phone: "" });
    } catch {
      toast.error("Failed to create admin.");
    }
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-xl bg-white dark:bg-slate-800 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-700 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Add School Admin</h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Email *
            </label>
            <input
              required
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              placeholder="admin@school.edu"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                First Name *
              </label>
              <input
                required
                value={form.first_name}
                onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                Last Name *
              </label>
              <input
                required
                value={form.last_name}
                onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Password
            </label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="Leave blank to auto-generate a secure password"
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Phone
            </label>
            <input
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-300 dark:border-slate-600 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={addAdmin.isPending}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {addAdmin.isPending ? "Creating..." : "Create Admin"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export default function PlatformSchoolDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: school, isLoading, error } = usePlatformSchool(id || "");
  const updateSchool = useUpdateSchool(id || "");
  const toggleSchool = useToggleSchoolActive();
  const { data: adminsData } = useSchoolAdmins(id || "");
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<School>>({});
  const [showAddAdmin, setShowAddAdmin] = useState(false);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
      </div>
    );
  }

  if (error || !school) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20 p-6 text-center">
        <p className="text-red-600 dark:text-red-400">School not found.</p>
        <button
          onClick={() => navigate("/admin/platform/schools")}
          className="mt-3 text-sm font-medium text-indigo-600 hover:text-indigo-700"
        >
          Back to schools
        </button>
      </div>
    );
  }

  const startEdit = () => {
    setEditForm({
      name: school.name,
      code: school.code,
      subdomain: school.subdomain,
      address: school.address,
      phone: school.phone,
      email: school.email,
      timezone: school.timezone,
      subscription_tier: school.subscription_tier,
    });
    setIsEditing(true);
  };

  const handleSave = async () => {
    try {
      await updateSchool.mutateAsync(editForm);
      toast.success("School updated!");
      setIsEditing(false);
    } catch {
      toast.error("Failed to update school.");
    }
  };

  const handleToggle = async () => {
    try {
      await toggleSchool.mutateAsync(school.id);
      toast.success(school.is_active ? "School deactivated" : "School activated");
    } catch {
      toast.error("Failed to toggle school status");
    }
  };

  return (
    <div className="space-y-6">
      {/* Back button */}
      <button
        onClick={() => navigate("/admin/platform/schools")}
        className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
      >
        <ArrowLeftIcon className="h-4 w-4" />
        Back to Schools
      </button>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-indigo-100 dark:bg-indigo-900/50">
            <BuildingOffice2Icon className="h-7 w-7 text-indigo-600 dark:text-indigo-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{school.name}</h1>
              <span
                className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  school.is_active
                    ? "bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300"
                    : "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300"
                }`}
              >
                {school.is_active ? "Active" : "Inactive"}
              </span>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {school.code} · {school.subdomain}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={startEdit}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-300 dark:border-slate-600 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          >
            <PencilIcon className="h-4 w-4" />
            Edit
          </button>
          <button
            onClick={handleToggle}
            className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white transition-colors ${
              school.is_active ? "bg-red-600 hover:bg-red-700" : "bg-green-600 hover:bg-green-700"
            }`}
          >
            {school.is_active ? "Deactivate" : "Activate"}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Users", value: school.user_count || 0, icon: UsersIcon, color: "bg-blue-500" },
          {
            label: "Students",
            value: school.student_count || 0,
            icon: AcademicCapIcon,
            color: "bg-emerald-500",
          },
          {
            label: "Teachers",
            value: school.teacher_count || 0,
            icon: UsersIcon,
            color: "bg-violet-500",
          },
          {
            label: "Revenue",
            value: formatCurrency(school.total_revenue || 0),
            icon: BanknotesIcon,
            color: "bg-amber-500",
          },
        ].map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-4"
          >
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-500 dark:text-slate-400">{stat.label}</p>
              <div className={`rounded-lg p-2 ${stat.color}`}>
                <stat.icon className="h-4 w-4 text-white" />
              </div>
            </div>
            <p className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Details + Admins */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* School Details */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4">
            School Details
          </h2>
          {isEditing ? (
            <div className="space-y-4">
              {[
                { label: "Name", key: "name" as const, required: true },
                { label: "Code", key: "code" as const, required: true },
                { label: "Subdomain", key: "subdomain" as const, required: true },
                { label: "Address", key: "address" as const },
                { label: "Phone", key: "phone" as const },
                { label: "Email", key: "email" as const, type: "email" },
                { label: "Timezone", key: "timezone" as const },
              ].map((field) => (
                <div key={field.key}>
                  <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
                    {field.label}
                  </label>
                  <input
                    required={field.required}
                    type={field.type || "text"}
                    value={(editForm as any)[field.key] || ""}
                    onChange={(e) => setEditForm({ ...editForm, [field.key]: e.target.value })}
                    className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
              ))}
              <div>
                <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
                  Subscription Tier
                </label>
                <select
                  value={editForm.subscription_tier || "standard"}
                  onChange={(e) =>
                    setEditForm({
                      ...editForm,
                      subscription_tier: e.target.value as School["subscription_tier"],
                    })
                  }
                  className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-3 py-2 text-sm text-slate-900 dark:text-white focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                >
                  <option value="basic">Basic</option>
                  <option value="standard">Standard</option>
                  <option value="premium">Premium</option>
                </select>
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setIsEditing(false)}
                  className="rounded-lg border border-slate-300 dark:border-slate-600 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  disabled={updateSchool.isPending}
                  className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                  {updateSchool.isPending ? "Saving..." : "Save"}
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {[
                { label: "Code", value: school.code },
                { label: "Subdomain", value: school.subdomain },
                { label: "Address", value: school.address },
                { label: "Phone", value: school.phone },
                { label: "Email", value: school.email },
                { label: "Website", value: school.website || "—" },
                { label: "Timezone", value: school.timezone },
                {
                  label: "Subscription",
                  value:
                    school.subscription_tier?.charAt(0).toUpperCase() +
                    school.subscription_tier?.slice(1),
                },
              ].map((field) => (
                <div key={field.label} className="flex justify-between">
                  <span className="text-sm text-slate-500 dark:text-slate-400">{field.label}</span>
                  <span className="text-sm font-medium text-slate-900 dark:text-white text-right max-w-[60%] truncate">
                    {field.value || "—"}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* School Admins */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-slate-900 dark:text-white">
              School Admins
            </h2>
            <button
              onClick={() => setShowAddAdmin(true)}
              className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 transition-colors"
            >
              <PlusIcon className="h-4 w-4" />
              Add Admin
            </button>
          </div>
          {!adminsData?.results?.length ? (
            <p className="text-sm text-slate-400 dark:text-slate-500">
              No admins assigned to this school yet.
            </p>
          ) : (
            <div className="divide-y divide-slate-100 dark:divide-slate-700">
              {adminsData.results.map((admin) => (
                <div key={admin.id} className="flex items-center justify-between py-3">
                  <div>
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                      {admin.first_name} {admin.last_name}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">{admin.email}</p>
                  </div>
                  <span
                    className={`inline-flex items-center gap-1 text-xs font-medium ${
                      admin.is_active
                        ? "text-green-600 dark:text-green-400"
                        : "text-red-600 dark:text-red-400"
                    }`}
                  >
                    {admin.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <AddAdminModal
        schoolId={school.id}
        open={showAddAdmin}
        onClose={() => setShowAddAdmin(false)}
      />
    </div>
  );
}
