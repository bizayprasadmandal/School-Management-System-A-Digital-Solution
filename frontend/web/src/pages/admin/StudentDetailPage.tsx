/**
 * Admin Student Detail Page — full profile, enrollments, grades, attendance, fees
 */
import React, { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeftIcon, PencilIcon } from "@heroicons/react/24/outline";
import { useStudent, useStudentAttendanceSummary, useStudentInvoices, useReportCards } from "../../api/hooks";
import { Button, Badge, Avatar, Spinner, DataTable, SkeletonCard } from "../../components/common";
import { fmt, currency, percent, attendanceColor, FEE_STATUS } from "../../utils";
import { useTitle } from "../../hooks";

type Tab = "overview" | "attendance" | "grades" | "fees";

export default function StudentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<Tab>("overview");
  const { data: student, isLoading } = useStudent(id!);
  const { data: attendance } = useStudentAttendanceSummary(id!);
  const { data: invoicesData } = useStudentInvoices(id!);
  const { data: reportCardsData } = useReportCards(id!);
  useTitle(student?.full_name ?? "Student Profile");

  if (isLoading) return <SkeletonCard className="max-w-2xl mx-auto mt-6" />;
  if (!student) return <div className="text-center py-32 text-slate-400"><p className="text-lg font-semibold">Student not found</p><Link to="/admin/students" className="text-indigo-600 text-sm mt-2 inline-block">Back to students</Link></div>;

  const invoices = invoicesData?.results ?? [];
  const reportCards = reportCardsData?.results ?? [];
  const totalFeesDue = invoices.filter(i => ["unpaid","overdue","partial"].includes(i.status)).reduce((s,i) => s + Number(i.outstanding_amount), 0);
  const TABS: {id: Tab; label: string}[] = [{id:"overview",label:"Overview"},{id:"attendance",label:"Attendance"},{id:"grades",label:"Grades"},{id:"fees",label:"Fees"}];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-800"><ArrowLeftIcon className="h-4 w-4" /> Back</button>
        <Button variant="primary" leftIcon={<PencilIcon className="h-4 w-4" />} onClick={() => navigate(`/admin/students/${id}/edit`)}>Edit Student</Button>
      </div>
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
        <div className="p-6 flex flex-col sm:flex-row gap-5">
          <Avatar name={student.full_name} src={student.avatar} className="h-20 w-20 text-2xl flex-shrink-0" />
          <div className="flex-1">
            <div className="flex items-center gap-3"><h1 className="text-2xl font-bold text-slate-900">{student.full_name}</h1><Badge color={student.is_active?"green":"slate"} dot>{student.is_active?"Active":"Inactive"}</Badge></div>
            <p className="text-slate-500 text-sm mt-1">{student.email}</p>
            <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-600">
              <span><b className="text-slate-800">Adm #</b> {student.admission_number}</span>
              <span><b className="text-slate-800">Class</b> {student.enrollments?.[0]?.classroom_name ?? "—"}</span>
              <span><b className="text-slate-800">DOB</b> {fmt.date(student.date_of_birth)}</span>
              <span><b className="text-slate-800">Age</b> {student.age} yrs</span>
            </div>
          </div>
          <div className="flex gap-3">
            <div className="text-center px-4 py-2 rounded-xl bg-indigo-50"><p className={`text-xl font-bold ${attendanceColor(attendance?.attendance_percentage ?? 0)}`}>{percent(attendance?.attendance_percentage ?? 0)}</p><p className="text-xs text-slate-500">Attendance</p></div>
            {totalFeesDue > 0 && <div className="text-center px-4 py-2 rounded-xl bg-red-50"><p className="text-xl font-bold text-red-600">{currency(totalFeesDue)}</p><p className="text-xs text-slate-500">Fees Due</p></div>}
          </div>
        </div>
        <div className="border-t border-slate-100 px-6 flex overflow-x-auto">
          {TABS.map(t => <button key={t.id} onClick={() => setActiveTab(t.id)} className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab===t.id?"border-indigo-600 text-indigo-600":"border-transparent text-slate-500 hover:text-slate-800"}`}>{t.label}</button>)}
        </div>
      </div>
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none"><div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700"><h2 className="text-base font-semibold">Personal Information</h2></div><div className="p-5 space-y-3">{[["Nationality",student.nationality],["Phone",student.phone||"—"],["Address",`${student.address}, ${student.city}`],["Admission Date",fmt.date(student.admission_date)]].map(([l,v])=><div key={l} className="flex justify-between text-sm"><span className="text-slate-500 font-medium">{l}</span><span className="text-slate-800">{v}</span></div>)}</div></div>
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none"><div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700"><h2 className="text-base font-semibold">Guardians</h2></div><div className="p-5 space-y-3">{student.guardians?.length===0?<p className="text-sm text-slate-400 text-center py-6">No guardians</p>:student.guardians?.map((sg,i)=><div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-slate-50"><Avatar name={sg.guardian.full_name} size="sm" /><div><p className="text-sm font-semibold">{sg.guardian.full_name}</p><p className="text-xs text-slate-500">{sg.guardian.email}</p></div>{sg.is_primary_contact&&<Badge color="indigo" dot>Primary</Badge>}</div>)}</div></div>
        </div>
      )}
      {activeTab === "attendance" && (
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none"><div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700"><h2 className="text-base font-semibold">Attendance</h2></div><div className="p-5"><div className="grid grid-cols-2 sm:grid-cols-4 gap-4">{[["Total",attendance?.total_days??0,"text-slate-800"],["Present",attendance?.present??0,"text-green-600"],["Absent",attendance?.absent??0,"text-red-600"],["Late",attendance?.late??0,"text-amber-600"]].map(([l,v,c])=><div key={String(l)} className="rounded-xl bg-slate-50 p-4 text-center"><p className={`text-2xl font-bold ${c}`}>{v}</p><p className="text-xs text-slate-500 mt-1">{l}</p></div>)}</div><div className="mt-4 rounded-full bg-slate-100 h-3 overflow-hidden"><div className="h-full bg-indigo-500 rounded-full" style={{width:`${attendance?.attendance_percentage??0}%`}}/></div><p className="text-xs text-right text-slate-500 mt-1">{percent(attendance?.attendance_percentage??0)} overall</p></div></div>
      )}
      {activeTab === "grades" && (
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none"><div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700"><h2 className="text-base font-semibold">Report Cards</h2></div><DataTable columns={[{key:"exam_name",header:"Exam"},{key:"percentage",header:"Score",render:r=><span className={`font-semibold ${Number(r.percentage)>=75?"text-green-600":Number(r.percentage)>=50?"text-amber-600":"text-red-600"}`}>{percent(Number(r.percentage))}</span>},{key:"grade_letter",header:"Grade",render:r=><Badge color="indigo">{r.grade_letter}</Badge>},{key:"rank_in_class",header:"Rank",render:r=>r.rank_in_class?`#${r.rank_in_class}`:"—"},{key:"status",header:"Status",render:r=><Badge color={r.status==="published"?"green":"slate"}>{r.status}</Badge>}]} data={reportCards} rowKey={r=>r.id} emptyMessage="No report cards yet" /></div>
      )}
      {activeTab === "fees" && (
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none"><div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700"><h2 className="text-base font-semibold">Invoices</h2>{totalFeesDue>0&&<Badge color="red" dot>Due: {currency(totalFeesDue)}</Badge>}</div><DataTable columns={[{key:"invoice_number",header:"Invoice #",render:r=><span className="font-mono text-xs">{r.invoice_number}</span>},{key:"due_date",header:"Due",render:r=>fmt.date(r.due_date)},{key:"total_amount",header:"Total",render:r=>currency(r.total_amount)},{key:"paid_amount",header:"Paid",render:r=><span className="text-green-600">{currency(r.paid_amount)}</span>},{key:"outstanding_amount",header:"Outstanding",render:r=><span className={Number(r.outstanding_amount)>0?"text-red-600 font-semibold":"text-slate-400"}>{currency(r.outstanding_amount)}</span>},{key:"status",header:"Status",render:r=>{const s=FEE_STATUS[r.status];return<Badge color={s?.color??"slate"}>{s?.label??r.status}</Badge>;}}]} data={invoices} rowKey={r=>r.id} emptyMessage="No invoices" /></div>
      )}
    </div>
  );
}
