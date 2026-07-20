/**
 * HR & Payroll — Admin page for employee management, salary structures,
 * payslip processing, and leave request management.
 */
import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  PlusIcon, FunnelIcon, MagnifyingGlassIcon,
  UsersIcon, BuildingOfficeIcon, CurrencyDollarIcon,
  CalendarDaysIcon, CheckCircleIcon, XCircleIcon,
  ClockIcon, PencilIcon, BanknotesIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

// ─── Types ───────────────────────────────────────────────────────────────────

interface Department {
  id: number;
  name: string;
  code: string;
  description: string;
  head_name: string | null;
  is_active: boolean;
  employee_count: number;
}

interface Employee {
  id: string;
  user: string;
  user_name: string;
  user_email: string;
  employee_id: string;
  department: number | null;
  department_name: string | null;
  designation: string;
  employment_type: "full_time" | "part_time" | "contract" | "intern";
  status: "active" | "on_leave" | "terminated" | "resigned";
  joining_date: string;
  phone: string;
  current_salary: {
    basic_salary: number;
    housing_allowance: number;
    net_salary: number;
  } | null;
}

interface SalaryStructure {
  id: number;
  name: string;
  designation: string;
  department: number | null;
  department_name: string | null;
  basic_salary: number;
  housing_allowance: number;
  transport_allowance: number;
  medical_allowance: number;
  other_allowances: number;
  tax_deduction: number;
  pension_deduction: number;
  other_deductions: number;
  net_salary: number;
  is_active: boolean;
}

interface Payslip {
  id: string;
  employee: string;
  employee_name: string;
  employee_id_number: string;
  department_name: string | null;
  period_start: string;
  period_end: string;
  gross_pay: number;
  net_pay: number;
  status: "draft" | "approved" | "paid" | "cancelled";
  payment_date: string | null;
}

interface LeaveRequest {
  id: string;
  employee: string;
  employee_name: string;
  employee_id_number: string;
  leave_type: string;
  from_date: string;
  to_date: string;
  total_days: number;
  reason: string;
  status: "pending" | "approved" | "rejected" | "cancelled";
  reviewed_by_name: string | null;
  review_notes: string;
  created_at: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const EMPLOYMENT_LABELS: Record<string, string> = {
  full_time: "Full-Time",
  part_time: "Part-Time",
  contract: "Contract",
  intern: "Intern",
};

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  on_leave: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  terminated: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  resigned: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300",
  approved: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  rejected: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  cancelled: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  draft: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  paid: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
};

const LEAVE_TYPE_LABELS: Record<string, string> = {
  annual: "Annual Leave",
  sick: "Sick Leave",
  personal: "Personal Leave",
  maternity: "Maternity Leave",
  paternity: "Paternity Leave",
  unpaid: "Unpaid Leave",
  other: "Other",
};

// ─── Tabs config ─────────────────────────────────────────────────────────────

type TabType = "employees" | "departments" | "payroll" | "leaves";
const TABS: { key: TabType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "employees", label: "Employees", icon: UsersIcon },
  { key: "departments", label: "Departments", icon: BuildingOfficeIcon },
  { key: "payroll", label: "Payroll", icon: CurrencyDollarIcon },
  { key: "leaves", label: "Leave Requests", icon: CalendarDaysIcon },
];

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function HRPage() {
  useTitle("HR & Payroll");
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>("employees");
  const [search, setSearch] = useState("");

  // Modals
  const [showEmployeeForm, setShowEmployeeForm] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<Employee | null>(null);
  const [showDeptForm, setShowDeptForm] = useState(false);
  const [editingDept, setEditingDept] = useState<Department | null>(null);
  const [showSalaryForm, setShowSalaryForm] = useState(false);
  const [editingSalary, setEditingSalary] = useState<SalaryStructure | null>(null);
  const [showLeaveForm, setShowLeaveForm] = useState(false);
  const [selectedPayslip, setSelectedPayslip] = useState<Payslip | null>(null);

  // ── Data fetching ───────────────────────────────────────────────────────

  const { data: employees = [], isLoading: empLoading } = useQuery({
    queryKey: ["hr-employees"],
    queryFn: async () => {
      const res = await api.get<{ results: Employee[] }>("/hr/employees/");
      return res.results ?? [];
    },
  });

  const { data: departments = [] } = useQuery({
    queryKey: ["hr-departments"],
    queryFn: async () => {
      const res = await api.get<{ results: Department[] }>("/hr/departments/");
      return res.results ?? [];
    },
  });

  const { data: salaries = [] } = useQuery({
    queryKey: ["hr-salary-structures"],
    queryFn: async () => {
      const res = await api.get<{ results: SalaryStructure[] }>("/hr/salary-structures/");
      return res.results ?? [];
    },
  });

  const { data: payslips = [], isLoading: payslipLoading } = useQuery({
    queryKey: ["hr-payslips"],
    queryFn: async () => {
      const res = await api.get<{ results: Payslip[] }>("/hr/payslips/");
      return res.results ?? [];
    },
  });

  const { data: leaves = [], isLoading: leaveLoading } = useQuery({
    queryKey: ["hr-leave-requests"],
    queryFn: async () => {
      const res = await api.get<{ results: LeaveRequest[] }>("/hr/leave-requests/");
      return res.results ?? [];
    },
  });

  // ── Mutations ───────────────────────────────────────────────────────────

  const deleteDept = useMutation({
    mutationFn: (id: number) => api.delete(`/hr/departments/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["hr-departments"] }); toast.success("Department deleted"); },
  });

  const deleteEmp = useMutation({
    mutationFn: (id: string) => api.delete(`/hr/employees/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["hr-employees"] }); toast.success("Employee deleted"); },
  });

  const approveLeave = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes: string }) => api.post(`/hr/leave-requests/${id}/approve/`, { review_notes: notes }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["hr-leave-requests"] }); toast.success("Leave approved"); },
  });

  const rejectLeave = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes: string }) => api.post(`/hr/leave-requests/${id}/reject/`, { review_notes: notes }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["hr-leave-requests"] }); toast.success("Leave rejected"); },
  });

  const approvePayslip = useMutation({
    mutationFn: (id: string) => api.post(`/hr/payslips/${id}/approve/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["hr-payslips"] }); toast.success("Payslip approved"); },
  });

  const markPaid = useMutation({
    mutationFn: (id: string) => api.post(`/hr/payslips/${id}/mark-paid/`, { payment_date: dayjs().format("YYYY-MM-DD") }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["hr-payslips"] }); toast.success("Payslip marked as paid"); },
  });

  // ── Filtering ───────────────────────────────────────────────────────────

  const filteredEmployees = useMemo(() => {
    if (!search.trim()) return employees;
    const q = search.toLowerCase();
    return employees.filter((e) =>
      e.user_name?.toLowerCase().includes(q) ||
      e.employee_id?.toLowerCase().includes(q) ||
      e.designation?.toLowerCase().includes(q)
    );
  }, [employees, search]);

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">HR & Payroll</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Employee management, salary structures, and leave tracking</p>
        </div>
        <div className="flex gap-2">
          {activeTab === "employees" && (
            <Button onClick={() => { setEditingEmployee(null); setShowEmployeeForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Employee
            </Button>
          )}
          {activeTab === "departments" && (
            <Button onClick={() => { setEditingDept(null); setShowDeptForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Department
            </Button>
          )}
          {activeTab === "payroll" && (
            <Button onClick={() => { setEditingSalary(null); setShowSalaryForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Structure
            </Button>
          )}
          {activeTab === "leaves" && (
            <Button onClick={() => setShowLeaveForm(true)}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> New Request
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const counts: Record<TabType, number> = {
            employees: employees.length,
            departments: departments.length,
            payroll: payslips.length,
            leaves: leaves.filter((l) => l.status === "pending").length,
          };
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
              {tab.key === "leaves" && counts.leaves > 0 && (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
                  {counts.leaves}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* ── Employees Tab ────────────────────────────────────────────────── */}
      {activeTab === "employees" && (
        <>
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-sm">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input value={search} onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm dark:text-slate-200"
                placeholder="Search employees..." />
            </div>
          </div>
          {empLoading ? (
            <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-20 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : filteredEmployees.length === 0 ? (
            <EmptyState icon={UsersIcon} title="No employees found" description="Add your first employee to get started" />
          ) : (
            <div className="grid gap-3">
              {filteredEmployees.map((emp) => (
                <div key={emp.id}
                  onClick={() => { setEditingEmployee(emp); setShowEmployeeForm(true); }}
                  className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[emp.status]}`}>{emp.status}</span>
                        <span className="text-xs text-slate-400">{emp.employee_id}</span>
                        <span className="text-xs text-slate-400">{EMPLOYMENT_LABELS[emp.employment_type]}</span>
                      </div>
                      <p className="font-medium text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{emp.user_name}</p>
                      <p className="text-sm text-slate-500 dark:text-slate-400">{emp.designation} {emp.department_name ? `· ${emp.department_name}` : ""}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-slate-400">
                        <span>📅 Joined {dayjs(emp.joining_date).format("MMM D, YYYY")}</span>
                        {emp.current_salary && <span>💰 ${Number(emp.current_salary.net_salary).toLocaleString()}/mo</span>}
                      </div>
                    </div>
                    <div className="flex gap-1 ml-4" onClick={e => e.stopPropagation()}>
                      <button onClick={() => { setEditingEmployee(emp); setShowEmployeeForm(true); }}
                        className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700">
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button onClick={() => { if (confirm("Delete this employee?")) deleteEmp.mutate(emp.id); }}
                        className="p-2 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30">
                        <XCircleIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Departments Tab ──────────────────────────────────────────────── */}
      {activeTab === "departments" && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {departments.length === 0 ? (
            <div className="sm:col-span-2 lg:col-span-3">
              <EmptyState icon={BuildingOfficeIcon} title="No departments" description="Create your first department" />
            </div>
          ) : (
            departments.map((dept) => (
              <div key={dept.id}
                onClick={() => { setEditingDept(dept); setShowDeptForm(true); }}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{dept.name}</p>
                    {dept.code && <p className="text-xs text-slate-400 font-mono">{dept.code}</p>}
                  </div>
                  <span className={`text-xs font-medium px-2 py-0.5 rounded ${dept.is_active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>
                    {dept.is_active ? "Active" : "Inactive"}
                  </span>
                </div>
                {dept.description && <p className="text-sm text-slate-500 dark:text-slate-400 mb-2 line-clamp-2">{dept.description}</p>}
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>{dept.employee_count} employees</span>
                  <span>Head: {dept.head_name || "—"}</span>
                </div>
                <div className="flex gap-2 mt-3 pt-3 border-t border-slate-100 dark:border-slate-700" onClick={e => e.stopPropagation()}>
                  <button onClick={() => { setEditingDept(dept); setShowDeptForm(true); }}
                    className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
                  <button onClick={() => { if (confirm("Delete department?")) deleteDept.mutate(dept.id); }}
                    className="text-xs text-red-500 hover:text-red-600 font-medium">Delete</button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* ── Payroll Tab ──────────────────────────────────────────────────── */}
      {activeTab === "payroll" && (
        <div className="space-y-6">
          {/* Salary Structures */}
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
            <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <h2 className="text-base font-semibold text-slate-800 dark:text-white">Salary Structures</h2>
              <Badge color="indigo">{salaries.length} structures</Badge>
            </div>
            <div className="p-5">
              {salaries.length === 0 ? (
                <p className="text-sm text-slate-400 text-center py-8">No salary structures created yet</p>
              ) : (
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {salaries.map((s) => (
                    <div key={s.id} className="rounded-lg border border-slate-100 dark:border-slate-700 p-3">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-semibold text-slate-800 dark:text-white">{s.name}</p>
                        <span className={`text-xs font-medium px-2 py-0.5 rounded ${s.is_active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>
                          {s.is_active ? "Active" : "Inactive"}
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 space-y-1">
                        <p>Basic: ${Number(s.basic_salary).toLocaleString()}</p>
                        <p>Net: <span className="font-semibold text-slate-700 dark:text-slate-300">${Number(s.net_salary).toLocaleString()}</span></p>
                        {s.department_name && <p>Dept: {s.department_name}</p>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Payslips */}
          <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
            <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <h2 className="text-base font-semibold text-slate-800 dark:text-white">Payslips</h2>
            </div>
            <div className="p-5">
              {payslipLoading ? (
                <div className="space-y-2">{[1,2,3].map(i => <div key={i} className="h-12 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
              ) : payslips.length === 0 ? (
                <p className="text-sm text-slate-400 text-center py-8">No payslips generated yet</p>
              ) : (
                <div className="space-y-2">
                  {payslips.map((p) => (
                    <div key={p.id} className="flex items-center justify-between rounded-lg border border-slate-100 dark:border-slate-700 p-3 hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-800 dark:text-white truncate">{p.employee_name}</p>
                        <p className="text-xs text-slate-400">
                          {dayjs(p.period_start).format("MMM D")} - {dayjs(p.period_end).format("MMM D, YYYY")}
                          {p.department_name && ` · ${p.department_name}`}
                        </p>
                      </div>
                      <div className="text-right mr-4">
                        <p className="text-sm font-semibold text-slate-800 dark:text-white">${Number(p.net_pay).toLocaleString()}</p>
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[p.status]}`}>{p.status}</span>
                      </div>
                      <div className="flex gap-1">
                        {p.status === "draft" && (
                          <Button size="sm" variant="secondary" onClick={() => approvePayslip.mutate(p.id)} loading={approvePayslip.isPending}>
                            <CheckCircleIcon className="h-3.5 w-3.5 mr-1" /> Approve
                          </Button>
                        )}
                        {p.status === "approved" && (
                          <Button size="sm" variant="primary" onClick={() => markPaid.mutate(p.id)} loading={markPaid.isPending}>
                            <BanknotesIcon className="h-3.5 w-3.5 mr-1" /> Mark Paid
                          </Button>
                        )}
                        <Button size="sm" variant="ghost" onClick={() => setSelectedPayslip(p)}>
                          View
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Leave Requests Tab ───────────────────────────────────────────── */}
      {activeTab === "leaves" && (
        <>
          {leaveLoading ? (
            <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-20 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : leaves.length === 0 ? (
            <EmptyState icon={CalendarDaysIcon} title="No leave requests" description="Leave requests from employees will appear here" />
          ) : (
            <div className="space-y-3">
              {leaves.map((l) => (
                <div key={l.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[l.status]}`}>{l.status}</span>
                        <span className="text-xs text-slate-400">{LEAVE_TYPE_LABELS[l.leave_type] || l.leave_type}</span>
                        <span className="text-xs text-slate-400">{l.total_days} day{l.total_days !== 1 ? "s" : ""}</span>
                      </div>
                      <p className="font-medium text-slate-900 dark:text-white">{l.employee_name}</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                        {dayjs(l.from_date).format("MMM D")} - {dayjs(l.to_date).format("MMM D, YYYY")}
                      </p>
                      <p className="text-sm text-slate-600 dark:text-slate-300 mt-1">{l.reason}</p>
                      {l.review_notes && <p className="text-xs text-slate-400 mt-1">Review notes: {l.review_notes}</p>}
                    </div>
                    <div className="flex gap-2 ml-4">
                      {l.status === "pending" && (
                        <>
                          <Button size="sm" variant="primary" onClick={() => approveLeave.mutate({ id: l.id, notes: "" })} loading={approveLeave.isPending}>
                            <CheckCircleIcon className="h-3.5 w-3.5 mr-1" /> Approve
                          </Button>
                          <Button size="sm" variant="danger" onClick={() => rejectLeave.mutate({ id: l.id, notes: "" })} loading={rejectLeave.isPending}>
                            <XCircleIcon className="h-3.5 w-3.5 mr-1" /> Reject
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Employee Form Modal ──────────────────────────────────────────── */}
      <EmployeeFormModal
        open={showEmployeeForm}
        onClose={() => { setShowEmployeeForm(false); setEditingEmployee(null); }}
        employee={editingEmployee}
        departments={departments}
        onSaved={() => { setShowEmployeeForm(false); setEditingEmployee(null); qc.invalidateQueries({ queryKey: ["hr-employees"] }); }}
      />

      {/* ── Department Form Modal ────────────────────────────────────────── */}
      <DepartmentFormModal
        open={showDeptForm}
        onClose={() => { setShowDeptForm(false); setEditingDept(null); }}
        department={editingDept}
        onSaved={() => { setShowDeptForm(false); setEditingDept(null); qc.invalidateQueries({ queryKey: ["hr-departments"] }); }}
      />

      {/* ── Salary Structure Form Modal ──────────────────────────────────── */}
      <SalaryStructureFormModal
        open={showSalaryForm}
        onClose={() => { setShowSalaryForm(false); setEditingSalary(null); }}
        structure={editingSalary}
        departments={departments}
        onSaved={() => { setShowSalaryForm(false); setEditingSalary(null); qc.invalidateQueries({ queryKey: ["hr-salary-structures"] }); }}
      />

      {/* ── Leave Request Form Modal ────────────────────────────────────── */}
      <LeaveRequestFormModal
        open={showLeaveForm}
        onClose={() => { setShowLeaveForm(false); }}
        employees={employees}
        onSaved={() => { setShowLeaveForm(false); qc.invalidateQueries({ queryKey: ["hr-leave-requests"] }); }}
      />

      {/* ── Payslip Detail Modal ─────────────────────────────────────────── */}
      <PayslipDetailModal
        payslip={selectedPayslip}
        onClose={() => setSelectedPayslip(null)}
      />
    </div>
  );
}

// ─── Employee Form Modal ────────────────────────────────────────────────────

function EmployeeFormModal({
  open, onClose, employee, departments, onSaved,
}: {
  open: boolean; onClose: () => void; employee?: Employee | null;
  departments: Department[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    user_email: employee?.user_email ?? "",
    employee_id: employee?.employee_id ?? "",
    department: employee?.department ?? ("" as number | ""),
    designation: employee?.designation ?? "",
    employment_type: employee?.employment_type ?? "full_time",
    joining_date: employee?.joining_date ?? dayjs().format("YYYY-MM-DD"),
    phone: employee?.phone ?? "",
  });

  const isEdit = !!employee;
  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/hr/employees/", data),
    onSuccess: () => { toast.success("Employee created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/hr/employees/${employee!.id}/`, data),
    onSuccess: () => { toast.success("Employee updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.user_email.trim()) return toast.error("Email is required");
    if (!form.employee_id.trim()) return toast.error("Employee ID is required");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Employee" : "Add Employee"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Email *</label>
          <input value={form.user_email} onChange={(e) => setForm((p) => ({ ...p, user_email: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
            placeholder="employee@school.edu" disabled={isEdit} required />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Employee ID *</label>
            <input value={form.employee_id} onChange={(e) => setForm((p) => ({ ...p, employee_id: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" disabled={isEdit} required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Designation *</label>
            <input value={form.designation} onChange={(e) => setForm((p) => ({ ...p, designation: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
              placeholder="e.g. Senior Teacher" required />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Department</label>
            <select value={form.department} onChange={(e) => setForm((p) => ({ ...p, department: e.target.value ? Number(e.target.value) : "" }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">None</option>
              {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Employment Type</label>                          <select value={form.employment_type} onChange={(e) => setForm((p) => ({ ...p, employment_type: e.target.value as "full_time" | "part_time" | "contract" | "intern" }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="full_time">Full-Time</option>
              <option value="part_time">Part-Time</option>
              <option value="contract">Contract</option>
              <option value="intern">Intern</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Joining Date *</label>
            <input type="date" value={form.joining_date} onChange={(e) => setForm((p) => ({ ...p, joining_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Phone</label>
            <input value={form.phone} onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Employee</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Department Form Modal ──────────────────────────────────────────────────

function DepartmentFormModal({
  open, onClose, department, onSaved,
}: {
  open: boolean; onClose: () => void; department?: Department | null; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: department?.name ?? "",
    code: department?.code ?? "",
    description: department?.description ?? "",
  });

  const isEdit = !!department;
  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/hr/departments/", data),
    onSuccess: () => { toast.success("Department created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/hr/departments/${department!.id}/`, data),
    onSuccess: () => { toast.success("Department updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return toast.error("Name is required");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Department" : "Add Department"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Name *</label>
            <input value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Code</label>
            <input value={form.code} onChange={(e) => setForm((p) => ({ ...p, code: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
          <textarea value={form.description} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))} rows={3}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Department</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Salary Structure Form Modal ────────────────────────────────────────────

function SalaryStructureFormModal({
  open, onClose, structure, departments, onSaved,
}: {
  open: boolean; onClose: () => void; structure?: SalaryStructure | null;
  departments: Department[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: structure?.name ?? "",
    designation: structure?.designation ?? "",
    department: structure?.department ?? ("" as number | ""),
    basic_salary: structure?.basic_salary ?? 0,
    housing_allowance: structure?.housing_allowance ?? 0,
    transport_allowance: structure?.transport_allowance ?? 0,
    medical_allowance: structure?.medical_allowance ?? 0,
    tax_deduction: structure?.tax_deduction ?? 0,
    pension_deduction: structure?.pension_deduction ?? 0,
  });

  const isEdit = !!structure;
  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/hr/salary-structures/", data),
    onSuccess: () => { toast.success("Structure created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/hr/salary-structures/${structure!.id}/`, data),
    onSuccess: () => { toast.success("Structure updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return toast.error("Name is required");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Salary Structure" : "Add Salary Structure"}>
      <form onSubmit={handleSubmit} className="space-y-4 max-h-[60vh] overflow-y-auto">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Name *</label>
            <input value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Designation</label>
            <input value={form.designation} onChange={(e) => setForm((p) => ({ ...p, designation: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Department</label>
          <select value={form.department} onChange={(e) => setForm((p) => ({ ...p, department: e.target.value ? Number(e.target.value) : "" }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
            <option value="">None</option>
            {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Basic Salary</label>
            <input type="number" min={0} value={form.basic_salary} onChange={(e) => setForm((p) => ({ ...p, basic_salary: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Housing Allowance</label>
            <input type="number" min={0} value={form.housing_allowance} onChange={(e) => setForm((p) => ({ ...p, housing_allowance: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Transport Allowance</label>
            <input type="number" min={0} value={form.transport_allowance} onChange={(e) => setForm((p) => ({ ...p, transport_allowance: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Medical Allowance</label>
            <input type="number" min={0} value={form.medical_allowance} onChange={(e) => setForm((p) => ({ ...p, medical_allowance: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="border-t border-slate-100 dark:border-slate-700 pt-4">
          <p className="text-xs font-semibold text-slate-500 uppercase mb-3">Deductions</p>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Tax Deduction</label>
              <input type="number" min={0} value={form.tax_deduction} onChange={(e) => setForm((p) => ({ ...p, tax_deduction: Number(e.target.value) }))}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Pension Deduction</label>
              <input type="number" min={0} value={form.pension_deduction} onChange={(e) => setForm((p) => ({ ...p, pension_deduction: Number(e.target.value) }))}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Structure</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Leave Request Form Modal ──────────────────────────────────────────────

function LeaveRequestFormModal({
  open, onClose, employees, onSaved,
}: {
  open: boolean; onClose: () => void; employees: Employee[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    employee: "" as string,
    leave_type: "annual",
    from_date: dayjs().format("YYYY-MM-DD"),
    to_date: dayjs().add(1, "day").format("YYYY-MM-DD"),
    reason: "",
  });

  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/hr/leave-requests/", data),
    onSuccess: () => { toast.success("Leave request created"); onSaved(); },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Failed to create"),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.employee) return toast.error("Select an employee");
    if (!form.reason.trim()) return toast.error("Reason is required");
    createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title="New Leave Request">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Employee *</label>
          <select value={form.employee} onChange={(e) => setForm((p) => ({ ...p, employee: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required>
            <option value="">Select employee...</option>
            {employees.map((e) => <option key={e.id} value={e.id}>{e.user_name} ({e.employee_id})</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Leave Type</label>
          <select value={form.leave_type} onChange={(e) => setForm((p) => ({ ...p, leave_type: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
            <option value="annual">Annual Leave</option>
            <option value="sick">Sick Leave</option>
            <option value="personal">Personal Leave</option>
            <option value="maternity">Maternity Leave</option>
            <option value="paternity">Paternity Leave</option>
            <option value="unpaid">Unpaid Leave</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">From Date</label>
            <input type="date" value={form.from_date} onChange={(e) => setForm((p) => ({ ...p, from_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">To Date</label>
            <input type="date" value={form.to_date} onChange={(e) => setForm((p) => ({ ...p, to_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <p className="text-xs text-slate-400">
          Duration: {Math.max(1, Math.ceil((new Date(form.to_date).getTime() - new Date(form.from_date).getTime()) / (1000 * 60 * 60 * 24)) + 1)} day(s)
        </p>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Reason *</label>
          <textarea value={form.reason} onChange={(e) => setForm((p) => ({ ...p, reason: e.target.value }))} rows={3}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={createMut.isPending}>Cancel</Button>
          <Button type="submit" loading={createMut.isPending}>Submit Request</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Payslip Detail Modal ────────────────────────────────────────────────────

function PayslipDetailModal({
  payslip, onClose,
}: {
  payslip: Payslip | null; onClose: () => void;
}) {
  if (!payslip) return null;
  const fields = [
    { label: "Employee", value: payslip.employee_name },
    { label: "Employee ID", value: payslip.employee_id_number },
    { label: "Period", value: `${dayjs(payslip.period_start).format("MMM D")} - ${dayjs(payslip.period_end).format("MMM D, YYYY")}` },
    { label: "Gross Pay", value: `$${Number(payslip.gross_pay).toLocaleString()}` },
    { label: "Net Pay", value: `$${Number(payslip.net_pay).toLocaleString()}` },
    { label: "Status", value: payslip.status },
  ];

  return (
    <Modal open={!!payslip} onClose={onClose} title="Payslip Details">
      <div className="space-y-3">
        {fields.map((f) => (
          <div key={f.label} className="flex justify-between py-2 border-b border-slate-100 dark:border-slate-700 last:border-0">
            <span className="text-sm text-slate-500 dark:text-slate-400">{f.label}</span>
            <span className="text-sm font-medium text-slate-800 dark:text-white">{f.value}</span>
          </div>
        ))}
      </div>
    </Modal>
  );
}
