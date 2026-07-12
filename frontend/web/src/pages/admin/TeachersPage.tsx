import React, { useState } from "react";
import { MagnifyingGlassIcon, PlusIcon, AcademicCapIcon } from "@heroicons/react/24/outline";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Button, Avatar, Badge, DataTable, SkeletonTable, EmptyState } from "../../components/common";
import { useTitle, useDebounce } from "../../hooks";

export default function TeachersPage() {
  useTitle("Teachers");
  const [search, setSearch] = useState("");
  const dSearch = useDebounce(search);
  const { data, isLoading } = useQuery({
    queryKey: ["teacher-profiles", dSearch],
    queryFn: () => api.get<any>("/academics/teacher-profiles/", { search: dSearch||undefined }),
  });
  const teachers = data?.results ?? [];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-slate-900">Teachers</h1><p className="text-sm text-slate-500 mt-0.5">{data?.count ?? 0} staff members</p></div><Button variant="primary" leftIcon={<PlusIcon className="h-4 w-4"/>}>Add Teacher</Button></div>
      <div className="card p-4">
        <div className="relative"><MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400"/><input className="input pl-9" placeholder="Search by name, employee ID, department…" value={search} onChange={e=>setSearch(e.target.value)}/></div>
      </div>
      <div className="card">
        {isLoading ? <SkeletonTable rows={6} cols={5} className="m-4" />
          : teachers.length === 0
          ? <div className="p-8"><EmptyState icon={AcademicCapIcon} title="No teachers found" description="Adjust search or add new teachers." /></div>
          : <DataTable
              columns={[
                { key:"full_name", header:"Teacher", render:r=><div className="flex items-center gap-3"><Avatar name={r.full_name} src={r.avatar} size="sm"/><div><p className="text-sm font-medium text-slate-900">{r.full_name}</p><p className="text-xs text-slate-400">{r.email}</p></div></div> },
                { key:"employee_id", header:"Emp. ID", render:r=><span className="font-mono text-xs">{r.employee_id}</span> },
                { key:"department", header:"Department", render:r=>r.department||"—" },
                { key:"qualification", header:"Qualification", render:r=><span className="capitalize">{r.qualification}</span> },
                { key:"experience_years", header:"Experience", render:r=>`${r.experience_years} yrs` },
                { key:"is_active", header:"Status", render:r=><Badge color={r.is_active?"green":"slate"} dot>{r.is_active?"Active":"Inactive"}</Badge> },
              ]}
              data={teachers as any[]} rowKey={r=>r.id}
            />
        }
      </div>
    </div>
  );
}
