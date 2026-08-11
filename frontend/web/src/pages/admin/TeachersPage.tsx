import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  MagnifyingGlassIcon,
  PlusIcon,
  AcademicCapIcon,
  TrashIcon,
  ArrowUpTrayIcon,
} from "@heroicons/react/24/outline";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import {
  Button,
  Avatar,
  Badge,
  DataTable,
  SkeletonTable,
  EmptyState,
  Modal,
  Input,
  Select,
} from "../../components/common";
import ImportCsvModal from "../../components/common/ImportCsvModal";
import { useTitle, useDebounce } from "../../hooks";
import toast from "react-hot-toast";

function CreateTeacherModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [form, setForm] = useState({
    employee_id: "",
    date_of_birth: "",
    gender: "M",
    qualification: "bachelor",
    specialization: "",
    joining_date: "",
    experience_years: 0,
    department: "",
    address: "",
  });

  const { mutate, isPending } = useMutation({
    mutationFn: () =>
      api.post("/academics/teacher-profiles/", {
        employee_id: form.employee_id,
        date_of_birth: form.date_of_birth || undefined,
        gender: form.gender,
        qualification: form.qualification,
        specialization: form.specialization,
        joining_date: form.joining_date || undefined,
        experience_years: form.experience_years,
        department: form.department,
        address: form.address,
      }),
    onSuccess: () => {
      toast.success("Teacher profile created!");
      qc.invalidateQueries({ queryKey: ["teacher-profiles"] });
      onClose();
    },
    onError: (err: any) =>
      toast.error(
        err?.message ??
          "Failed to create teacher. Ensure the teacher user exists first (create via Django admin).",
      ),
  });

  const set = <K extends keyof typeof form>(k: K, v: (typeof form)[K]) =>
    setForm((f) => ({ ...f, [k]: v }));

  return (
    <Modal
      open
      onClose={onClose}
      title="Add Teacher"
      size="lg"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={() => mutate()} loading={isPending} disabled={!form.employee_id}>
            Create Teacher
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <div className="rounded-lg bg-amber-50 border border-amber-200 p-3 text-xs text-amber-800">
          Note: Teacher user account must exist first. Create the user with role=teacher via the
          Django admin panel before adding their profile here.
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Employee ID"
            value={form.employee_id}
            onChange={(e) => set("employee_id", e.target.value)}
            required
          />
          <Input
            label="Date of Birth"
            type="date"
            value={form.date_of_birth}
            onChange={(e) => set("date_of_birth", e.target.value)}
          />
          <Select
            label="Gender"
            value={form.gender}
            onChange={(e) => set("gender", e.target.value)}
            options={[
              { value: "M", label: "Male" },
              { value: "F", label: "Female" },
              { value: "O", label: "Other" },
            ]}
          />
          <Select
            label="Qualification"
            value={form.qualification}
            onChange={(e) => set("qualification", e.target.value)}
            options={[
              { value: "diploma", label: "Diploma" },
              { value: "bachelor", label: "Bachelor" },
              { value: "master", label: "Master" },
              { value: "phd", label: "PhD" },
            ]}
          />
          <Input
            label="Specialization"
            value={form.specialization}
            onChange={(e) => set("specialization", e.target.value)}
          />
          <Input
            label="Joining Date"
            type="date"
            value={form.joining_date}
            onChange={(e) => set("joining_date", e.target.value)}
          />
          <Input
            label="Experience (years)"
            type="number"
            value={form.experience_years}
            onChange={(e) => set("experience_years", Number(e.target.value))}
          />
          <Input
            label="Department"
            value={form.department}
            onChange={(e) => set("department", e.target.value)}
          />
        </div>
        <Input
          label="Address"
          value={form.address}
          onChange={(e) => set("address", e.target.value)}
        />
      </div>
    </Modal>
  );
}

export default function TeachersPage() {
  useTitle("Teachers");
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const dSearch = useDebounce(search);
  const qc = useQueryClient();
  useEffect(() => {
    setPage(1);
  }, [dSearch]);

  const { data, isLoading } = useQuery({
    queryKey: ["teacher-profiles", dSearch, page],
    queryFn: () =>
      api.get<any>("/academics/teacher-profiles/", { search: dSearch || undefined, page }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/academics/teacher-profiles/${id}/`),
    onSuccess: () => {
      toast.success("Teacher removed");
      qc.invalidateQueries({ queryKey: ["teacher-profiles"] });
    },
  });

  const teachers = data?.results ?? [];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Teachers</h1>
          <p className="text-sm text-slate-500 mt-0.5">{data?.count ?? 0} staff members</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            leftIcon={<ArrowUpTrayIcon className="h-4 w-4" />}
            onClick={() => setShowImport(true)}
          >
            Import CSV
          </Button>
          <Button
            variant="primary"
            leftIcon={<PlusIcon className="h-4 w-4" />}
            onClick={() => setShowCreate(true)}
          >
            Add Teacher
          </Button>
        </div>
      </div>
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm placeholder:text-slate-400 text-slate-900 transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-400 disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed dark:bg-slate-800 dark:border-slate-600 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:ring-indigo-400 pl-9"
            placeholder="Search by name, employee ID, department…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
        {isLoading ? (
          <SkeletonTable rows={6} cols={5} className="m-4" />
        ) : teachers.length === 0 ? (
          <div className="p-8">
            <EmptyState
              icon={AcademicCapIcon}
              title="No teachers found"
              description="Adjust search or add new teachers."
            />
          </div>
        ) : (
          <DataTable
            columns={[
              {
                key: "full_name",
                header: "Teacher",
                render: (r) => (
                  <div className="flex items-center gap-3">
                    <Avatar name={r.full_name} src={r.avatar} size="sm" />
                    <div>
                      <p className="text-sm font-medium text-slate-900">{r.full_name}</p>
                      <p className="text-xs text-slate-400">{r.email}</p>
                    </div>
                  </div>
                ),
              },
              {
                key: "employee_id",
                header: "Emp. ID",
                render: (r) => <span className="font-mono text-xs">{r.employee_id}</span>,
              },
              { key: "department", header: "Department", render: (r) => r.department || "—" },
              {
                key: "qualification",
                header: "Qualification",
                render: (r) => <span className="capitalize">{r.qualification}</span>,
              },
              {
                key: "experience_years",
                header: "Experience",
                render: (r) => `${r.experience_years} yrs`,
              },
              {
                key: "is_active",
                header: "Status",
                render: (r) => (
                  <Badge color={r.is_active ? "green" : "slate"} dot>
                    {r.is_active ? "Active" : "Inactive"}
                  </Badge>
                ),
              },
              {
                key: "actions",
                header: "",
                render: (r) => (
                  <button
                    onClick={() => {
                      if (window.confirm("Remove this teacher?")) deleteMutation.mutate(r.id);
                    }}
                    className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors"
                    title="Delete"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                ),
              },
            ]}
            data={teachers as any[]}
            rowKey={(r) => r.id}
            page={page}
            total={data?.count ?? 0}
            pageSize={25}
            onPageChange={setPage}
            onRowClick={(r) => {
              navigate(`/admin/teachers`, {
                state: { selectedTeacherId: r.id },
              });
            }}
          />
        )}
      </div>
      {showCreate && <CreateTeacherModal onClose={() => setShowCreate(false)} />}
      <ImportCsvModal
        open={showImport}
        onClose={() => setShowImport(false)}
        endpoint="/academics/teacher-profiles/import-csv/"
        invalidateQueries={[["teacher-profiles"]]}
        helpText={`email,first_name,last_name,employee_id,gender,qualification,joining_date,department,specialization,address,password
jane.doe@school.edu,Jane,Doe,EMP-101,F,bachelor,2024-01-15,Mathematics,Algebra,123 Main St
(password column is optional — a secure random password is auto-generated and shown in the result; gender is M/F/O, qualification is diploma/bachelor/master/phd)`}
      />
    </div>
  );
}
