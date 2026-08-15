/**
 * Admin Students Page — searchable, filterable, paginated student list
 */

import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  MagnifyingGlassIcon,
  PlusIcon,
  FunnelIcon,
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
  EyeIcon,
  PencilIcon,
} from "@heroicons/react/24/outline";
import { useStudents, useGradeLevels } from "../../api/hooks";
import { downloadFromUrl } from "../../utils";
import { useAuthStore } from "../../store/authStore";
import toast from "react-hot-toast";
import type { StudentListItem } from "../../types";
import { Button, Badge, Input, Select, Avatar, DataTable } from "../../components/common";
import type { Column } from "../../components/common";
import ImportCsvModal from "../../components/common/ImportCsvModal";

const GENDER_LABELS: Record<string, string> = { M: "Male", F: "Female", O: "Other" };

export default function StudentsPage() {
  const navigate = useNavigate();
  const { tokens } = useAuthStore();
  const [search, setSearch] = useState("");
  const [gender, setGender] = useState("");
  const [isActive, setIsActive] = useState<boolean | undefined>(true);
  const [page, setPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [showImport, setShowImport] = useState(false);

  const { data: gradesData } = useGradeLevels();
  const [grade, setGrade] = useState<number | undefined>();

  const { data, isLoading } = useStudents({
    search: search || undefined,
    gender: gender || undefined,
    is_active: isActive,
    classroom: grade,
    page,
  });

  const students = data?.results ?? [];
  const total = data?.count ?? 0;

  const handleExport = async () => {
    try {
      await downloadFromUrl(
        `${
          process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1"
        }/reporting/export/students-csv/`,
        "students.csv",
        tokens?.access ?? "",
      );
    } catch {
      toast.error("Export failed. Please try again.");
    }
  };

  const columns: Column<StudentListItem>[] = [
    {
      key: "full_name",
      header: "Student",
      render: (student) => (
        <div className="flex items-center gap-3">
          <Avatar name={student.full_name} src={student.avatar} size="sm" />
          <div>
            <p className="text-sm font-medium text-slate-900">{student.full_name}</p>
            <p className="text-xs text-slate-400">{student.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: "admission_number",
      header: "Admission No.",
      render: (student) => (
        <span className="font-mono text-slate-600">{student.admission_number}</span>
      ),
    },
    {
      key: "gender",
      header: "Gender",
      render: (student) => (
        <span className="text-sm text-slate-600">{GENDER_LABELS[student.gender] ?? "—"}</span>
      ),
    },
    {
      key: "current_class",
      header: "Class",
      render: (student) => (
        <span className="text-sm text-slate-600">{student.current_class ?? "—"}</span>
      ),
    },
    {
      key: "is_active",
      header: "Status",
      render: (student) => (
        <Badge color={student.is_active ? "green" : "slate"} dot>
          {student.is_active ? "Active" : "Inactive"}
        </Badge>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (student) => (
        <div className="flex items-center gap-1">
          <button
            onClick={() => navigate(`/admin/students/${student.id}`)}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
            title="View profile"
          >
            <EyeIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => navigate(`/admin/students/${student.id}`)}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-amber-50 hover:text-amber-600 transition-colors"
            title="Edit student"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Students</h1>
          <p className="text-sm text-slate-500 mt-0.5">{total.toLocaleString()} total students</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="md"
            leftIcon={<ArrowUpTrayIcon className="h-4 w-4" />}
            onClick={() => setShowImport(true)}
          >
            Import CSV
          </Button>
          <Button
            variant="secondary"
            size="md"
            leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
            onClick={handleExport}
          >
            Export CSV
          </Button>
          <Link
            to="/admin/students/new"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-all duration-150 hover:bg-indigo-700 active:bg-indigo-800"
          >
            <PlusIcon className="h-4 w-4" />
            Add Student
          </Link>
        </div>
      </div>

      {/* Search + filters bar */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 space-y-3">
        <div className="flex gap-3">
          <Input
            className="flex-1"
            leftAddon={<MagnifyingGlassIcon className="h-4 w-4 text-slate-400" />}
            type="search"
            placeholder="Search by name or admission number…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
          <Button
            variant={showFilters ? "primary" : "secondary"}
            size="md"
            leftIcon={<FunnelIcon className="h-4 w-4" />}
            onClick={() => setShowFilters((v) => !v)}
          >
            Filters
          </Button>
        </div>

        {showFilters && (
          <div className="flex flex-wrap items-end gap-3 pt-3 border-t border-slate-100">
            <Select
              label="Gender"
              value={gender}
              onChange={(e) => {
                setGender(e.target.value);
                setPage(1);
              }}
              placeholder="All Genders"
              options={[
                { value: "M", label: "Male" },
                { value: "F", label: "Female" },
                { value: "O", label: "Other" },
              ]}
            />
            <Select
              label="Status"
              value={isActive === undefined ? "" : String(isActive)}
              onChange={(e) => {
                setIsActive(e.target.value === "" ? undefined : e.target.value === "true");
                setPage(1);
              }}
              options={[
                { value: "true", label: "Active" },
                { value: "false", label: "Inactive" },
                { value: "", label: "All" },
              ]}
            />
            <Select
              label="Class"
              value={grade ?? ""}
              onChange={(e) => {
                setGrade(Number(e.target.value) || undefined);
                setPage(1);
              }}
              placeholder="All Grades"
              options={(gradesData?.results ?? []).map((g) => ({ value: g.id, label: g.name }))}
            />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSearch("");
                setGender("");
                setIsActive(true);
                setGrade(undefined);
                setPage(1);
              }}
              className="mt-0.5"
            >
              Clear filters
            </Button>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="rounded-xl bg-white shadow-sm border border-slate-100 overflow-hidden">
        <DataTable<StudentListItem>
          columns={columns}
          data={students}
          loading={isLoading}
          emptyMessage="No students found. Try adjusting your search or filters"
          rowKey={(s) => s.id}
          onRowClick={(s) => navigate(`/admin/students/${s.id}`)}
          page={page}
          total={total}
          pageSize={25}
          onPageChange={setPage}
        />
      </div>

      <ImportCsvModal
        open={showImport}
        onClose={() => setShowImport(false)}
        endpoint="/students/import-csv/"
        invalidateQueries={[["students"]]}
        helpText={`first_name,last_name,email,admission_number,date_of_birth,gender,classroom_name,address,city,state,country,password
John,Doe,john@example.com,ADM001,2010-05-15,M,Grade 5 A,123 Main St,New York,NY,USA
(password column is optional — a secure random password is auto-generated and shown in the result)`}
      />
    </div>
  );
}
