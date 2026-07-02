import React, { useState } from "react";
import { PlusIcon, BuildingLibraryIcon } from "@heroicons/react/24/outline";
import { useClassrooms, useGradeLevels } from "../../api/hooks";
import { Button, Badge, DataTable, Select, Spinner, EmptyState } from "../../components/common";
import { useTitle } from "../../hooks";

export default function ClassroomsPage() {
  useTitle("Classrooms");
  const [gradeFilter, setGradeFilter] = useState<number|undefined>();
  const { data: classroomsData, isLoading } = useClassrooms(gradeFilter);
  const { data: gradesData } = useGradeLevels();
  const classrooms = classroomsData?.results ?? [];
  const grades = gradesData?.results ?? [];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-slate-900">Classrooms</h1><p className="text-sm text-slate-500 mt-0.5">{classrooms.length} sections configured</p></div><Button variant="primary" leftIcon={<PlusIcon className="h-4 w-4"/>}>Add Classroom</Button></div>
      <div className="card p-4 flex gap-4">
        <Select placeholder="All Grades" options={grades.map(g=>({value:g.id,label:g.name}))} value={gradeFilter??""} onChange={e=>setGradeFilter(Number(e.target.value)||undefined)} className="w-48" />
      </div>
      <div className="card">
        {isLoading ? <div className="flex justify-center py-16"><Spinner size="lg"/></div>
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
            />
        }
      </div>
    </div>
  );
}
