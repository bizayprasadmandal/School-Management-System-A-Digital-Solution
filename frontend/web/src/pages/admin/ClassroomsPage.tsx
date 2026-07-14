import React, { useState, useEffect } from "react";
import { PlusIcon, BuildingLibraryIcon, TrashIcon } from "@heroicons/react/24/outline";
import { useClassrooms, useGradeLevels, useCurrentAcademicYear } from "../../api/hooks";
import { Button, Badge, DataTable, Select, Spinner, EmptyState, SkeletonTable, Modal, Input } from "../../components/common";
import { useTitle } from "../../hooks";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import toast from "react-hot-toast";

function CreateClassroomModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const { data: gradesData } = useGradeLevels();
  const { data: currentYear } = useCurrentAcademicYear();
  const [name, setName] = useState("");
  const [gradeId, setGradeId] = useState<number | "">("");
  const [capacity, setCapacity] = useState(40);
  const [roomNumber, setRoomNumber] = useState("");

  const { mutate, isPending } = useMutation({
    mutationFn: () => api.post("/students/classrooms/", {
      name, grade: gradeId, capacity, room_number: roomNumber,
      academic_year: currentYear?.id,
    }),
    onSuccess: () => { toast.success("Classroom created!"); qc.invalidateQueries({ queryKey: ["classrooms"] }); onClose(); },
    onError: (err: any) => toast.error(err?.message ?? "Failed to create classroom"),
  });

  const grades = gradesData?.results ?? [];
  return (
    <Modal open onClose={onClose} title="Add Classroom" size="md"
      footer={<><Button variant="secondary" onClick={onClose}>Cancel</Button><Button onClick={() => mutate()} loading={isPending} disabled={!name || !gradeId}>Create Classroom</Button></>}>
      <div className="space-y-4">
        <Input label="Section Name" value={name} onChange={e => setName(e.target.value)} placeholder="e.g. 3A, 5B" required />
        <Select label="Grade" value={gradeId} onChange={e => setGradeId(Number(e.target.value))}
          options={grades.map(g => ({ value: g.id, label: g.name }))} placeholder="Select grade" />
        <Input label="Capacity" type="number" value={capacity} onChange={e => setCapacity(Number(e.target.value))} min={1} />
        <Input label="Room Number" value={roomNumber} onChange={e => setRoomNumber(e.target.value)} placeholder="e.g. 201" />
      </div>
    </Modal>
  );
}

export default function ClassroomsPage() {
  useTitle("Classrooms");
  const [gradeFilter, setGradeFilter] = useState<number|undefined>();
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const qc = useQueryClient();
  const { data: classroomsData, isLoading } = useClassrooms(gradeFilter, page);
  const { data: gradesData } = useGradeLevels();
  const classrooms = classroomsData?.results ?? [];
  const grades = gradesData?.results ?? [];
  useEffect(() => { setPage(1); }, [gradeFilter]);

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/students/classrooms/${id}/`),
    onSuccess: () => { toast.success("Classroom deleted"); qc.invalidateQueries({ queryKey: ["classrooms"] }); },
  });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold text-slate-900">Classrooms</h1><p className="text-sm text-slate-500 mt-0.5">{classrooms.length} sections configured</p></div>
        <Button variant="primary" leftIcon={<PlusIcon className="h-4 w-4"/>} onClick={() => setShowCreate(true)}>Add Classroom</Button>
      </div>
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
                { key:"actions", header:"", render: r => (
                  <button onClick={() => { if(window.confirm("Delete this classroom?")) deleteMutation.mutate(r.id); }}
                    className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 transition-colors" title="Delete">
                    <TrashIcon className="h-4 w-4" />
                  </button>
                )},
              ]}
              data={classrooms} rowKey={r=>r.id}
              page={page} total={classroomsData?.count ?? 0} pageSize={25} onPageChange={setPage}
            />
        }
      </div>
      {showCreate && <CreateClassroomModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
