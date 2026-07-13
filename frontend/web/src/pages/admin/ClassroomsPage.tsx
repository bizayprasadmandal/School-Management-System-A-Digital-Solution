import React, { useState, useEffect } from "react";
import { PlusIcon, BuildingLibraryIcon } from "@heroicons/react/24/outline";
import { useClassrooms, useGradeLevels } from "../../api/hooks";
import { Button, Badge, DataTable, Select, Spinner, EmptyState, SkeletonTable } from "../../components/common";
import { useTitle } from "../../hooks";

export default function ClassroomsPage() {
  useTitle("Classrooms");
  const [gradeFilter, setGradeFilter] = useState<number|undefined>();
  const [page, setPage] = useState(1);
  const { data: classroomsData, isLoading } = useClassrooms(gradeFilter, page);
  const { data: gradesData } = useGradeLevels();
  const classrooms = classroomsData?.results ?? [];
  const grades = gradesData?.results ?? [];
  // Reset to page 1 when grade filter changes
  useEffect(() => { setPage(1); }, [gradeFilter]);

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-slate-900">Classrooms</h1><p className="text-sm text-slate-500 mt-0.5">{classrooms.length} sections configured</p></div><Button variant="primary" leftIcon={<PlusIcon className="h-4 w-4"/>}>Add Classroom</Button></div>
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4 flex gap-4">
        <Select placeholder="All Grades" options={grades.map(g=>({value:g.id,label:g.name}))} value={gradeFilter??""} onChange={e=>setGradeFilter(Number(e.target.value)||undefined)} className="w-48" />
      </div>
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
        {isLoading ? <div className="m-4"><SkeletonTable rows={5} cols={4} /></div>
          : classrooms.length === 0
          ? <div className="p-8"><EmptyState icon={BuildingLibraryIcon} title="No classrooms" description="Add classrooms to get started." /></div>
          : <DataTable
              columns={[
                { key:"name", header:"Section", render:r=><span className="font-semibold">{r.grade_name} {r.name}</span> },
                { key:"capacity", header:"Capacity" },
                { key:"student_count", header:"Students", render:r=><Badge color={r.student_count>=r.capacity?"red":"green"}>{r.student_count}/{r.capacity}</Badge> },
                { key:"teacher_name", header:"Class Teacher", render:r=>r.teacher_name??<span className="text-slate-400">Unassigned</span> },
                { key:"room_number", header:"Room", render:r=>r.room_number||"—" },
              ]}
              data={classrooms} rowKey={r=>r.id}
              page={page} total={classroomsData?.count ?? 0} pageSize={25} onPageChange={setPage}
            />
        }
      </div>
    </div>
  );
}
