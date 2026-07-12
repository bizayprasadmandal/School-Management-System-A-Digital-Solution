/**
 * Admin Students Page — searchable, filterable, paginated student list
 */

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  MagnifyingGlassIcon, PlusIcon, FunnelIcon,
  ArrowDownTrayIcon, EyeIcon, PencilIcon,
} from "@heroicons/react/24/outline";
import { useStudents, useGradeLevels } from "../../api/hooks";
import { downloadFromUrl } from "../../utils";
import { useAuthStore } from "../../store/authStore";
import toast from "react-hot-toast";
import type { StudentListItem } from "../../types";
import { SkeletonTable } from "../../components/common";

const GENDER_LABELS: Record<string, string> = { M: "Male", F: "Female", O: "Other" };

function StatusBadge({ active }: { active: boolean }) {
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
      active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"
    }`}>
      <span className={`h-1.5 w-1.5 rounded-full ${active ? "bg-green-500" : "bg-slate-400"}`} />
      {active ? "Active" : "Inactive"}
    </span>
  );
}

function Avatar({ student }: { student: StudentListItem }) {
  if (student.avatar) {
    return <img src={student.avatar} alt="" className="h-8 w-8 rounded-full object-cover" />;
  }
  const initials = student.full_name.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase();
  return (
    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 text-xs font-semibold">
      {initials}
    </div>
  );
}

export default function StudentsPage() {
  const navigate = useNavigate();
  const { tokens } = useAuthStore();
  const [search, setSearch] = useState("");
  const [gender, setGender] = useState("");
  const [isActive, setIsActive] = useState<boolean | undefined>(true);
  const [page, setPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);

  const { data: gradesData } = useGradeLevels();
  const [grade, setGrade] = useState<number | undefined>();

  const { data, isLoading, isFetching } = useStudents({
    search: search || undefined,
    gender: gender || undefined,
    is_active: isActive,
    classroom: grade,
    page,
  });

  const students = data?.results ?? [];
  const total = data?.count ?? 0;
  const totalPages = Math.ceil(total / 25);

  const handleExport = async () => {
    try {
      await downloadFromUrl(
        `${process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1"}/reporting/export/students-csv/`,
        "students.csv",
        tokens?.access ?? ""
      );
    } catch {
      toast.error("Export failed. Please try again.");
    }
  };

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Students</h1>
          <p className="text-sm text-slate-500 mt-0.5">{total.toLocaleString()} total students</p>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handleExport}
            className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors">
            <ArrowDownTrayIcon className="h-4 w-4" />
            Export CSV
          </button>
          <Link to="/admin/students/new"
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 transition-colors shadow-sm">
            <PlusIcon className="h-4 w-4" />
            Add Student
          </Link>
        </div>
      </div>

      {/* Search + filters bar */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 space-y-3">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="search"
              placeholder="Search by name or admission number…"
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1); }}
              className="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <button
            onClick={() => setShowFilters(v => !v)}
            className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
              showFilters ? "border-indigo-300 bg-indigo-50 text-indigo-700" : "border-slate-200 text-slate-700 hover:bg-slate-50"
            }`}>
            <FunnelIcon className="h-4 w-4" />
            Filters
          </button>
        </div>

        {showFilters && (
          <div className="flex flex-wrap gap-3 pt-1 border-t border-slate-100">
            <select value={gender} onChange={e => { setGender(e.target.value); setPage(1); }}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="">All Genders</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
            <select
              value={isActive === undefined ? "" : String(isActive)}
              onChange={e => {
                setIsActive(e.target.value === "" ? undefined : e.target.value === "true");
                setPage(1);
              }}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="true">Active</option>
              <option value="false">Inactive</option>
              <option value="">All</option>
            </select>
            <select value={grade ?? ""} onChange={e => { setGrade(Number(e.target.value) || undefined); setPage(1); }}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="">All Grades</option>
              {gradesData?.results.map(g => (
                <option key={g.id} value={g.id}>{g.name}</option>
              ))}
            </select>
            <button onClick={() => { setSearch(""); setGender(""); setIsActive(true); setGrade(undefined); setPage(1); }}
              className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">
              Clear filters
            </button>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="rounded-xl bg-white shadow-sm border border-slate-100 overflow-hidden">
        {isLoading ? (
          <SkeletonTable rows={6} cols={6} />
        ) : students.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400">
            <p className="text-base font-medium">No students found</p>
            <p className="text-sm mt-1">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-100">
              <thead className="bg-slate-50">
                <tr>
                  {["Student", "Admission No.", "Gender", "Class", "Status", "Actions"].map(h => (
                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {students.map(student => (
                  <tr key={student.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <Avatar student={student} />
                        <div>
                          <p className="text-sm font-medium text-slate-900">{student.full_name}</p>
                          <p className="text-xs text-slate-400">{student.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600 font-mono">{student.admission_number}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{GENDER_LABELS[student.gender] ?? "—"}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{student.current_class ?? "—"}</td>
                    <td className="px-4 py-3"><StatusBadge active={student.is_active} /></td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button onClick={() => navigate(`/admin/students/${student.id}`)}
                          className="rounded-lg p-1.5 text-slate-400 hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
                          title="View profile">
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button onClick={() => navigate(`/admin/students/${student.id}/edit`)}
                          className="rounded-lg p-1.5 text-slate-400 hover:bg-amber-50 hover:text-amber-600 transition-colors"
                          title="Edit student">
                          <PencilIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-slate-100 px-4 py-3">
            <p className="text-sm text-slate-500">
              Showing {((page - 1) * 25) + 1}–{Math.min(page * 25, total)} of {total.toLocaleString()}
            </p>
            <div className="flex items-center gap-2">
              <button disabled={page === 1} onClick={() => setPage(p => p - 1)}
                className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
                Previous
              </button>
              <span className="text-sm text-slate-600">Page {page} of {totalPages}</span>
              <button disabled={page === totalPages} onClick={() => setPage(p => p + 1)}
                className="rounded-lg border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors">
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
