import React from "react";
import { BanknotesIcon, CheckCircleIcon, ClockIcon } from "@heroicons/react/24/outline";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { useStudentInvoices } from "../../api/hooks";
import { Badge, DataTable, EmptyState, SkeletonCard } from "../../components/common";
import { currency, FEE_STATUS, fmt } from "../../utils";
import { useTitle } from "../../hooks";
import dayjs from "dayjs";

export default function StudentFeesPage() {
  useTitle("My Fees");
  const { data: profile } = useQuery({ queryKey:["student-me-fees"], queryFn:()=>api.get<any>("/students/me/") });
  const { data: invData, isLoading } = useStudentInvoices(profile?.id ?? "");
  const invoices = invData?.results ?? [];
  const totalDue = invoices.filter(i=>["unpaid","overdue","partial"].includes(i.status)).reduce((s,i)=>s+Number(i.outstanding_amount),0);
  const totalPaid = invoices.reduce((s,i)=>s+Number(i.paid_amount),0);

  if (isLoading) return <div className="p-4"><SkeletonCard /></div>;

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-bold text-slate-900">My Fees</h1><p className="text-sm text-slate-500 mt-1">Payment history and outstanding balances</p></div>
      <div className="grid grid-cols-3 gap-4">
        {[
          { label:"Total Paid", value:currency(totalPaid), icon:CheckCircleIcon, color:"text-green-600 bg-green-50" },
          { label:"Outstanding", value:currency(totalDue), icon:ClockIcon, color:totalDue>0?"text-red-600 bg-red-50":"text-slate-600 bg-slate-50" },
          { label:"Total Invoices", value:invoices.length, icon:BanknotesIcon, color:"text-indigo-600 bg-indigo-50" },
        ].map(({label,value,icon:Icon,color})=>(
          <div key={label} className="card p-4 flex items-center gap-4">
            <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${color.split(" ")[1]}`}><Icon className={`h-5 w-5 ${color.split(" ")[0]}`}/></div>
            <div><p className={`text-xl font-bold ${color.split(" ")[0]}`}>{value}</p><p className="text-xs text-slate-500">{label}</p></div>
          </div>
        ))}
      </div>
      {totalDue > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 flex items-center justify-between">
          <div><p className="text-sm font-semibold text-amber-800">You have outstanding fees</p><p className="text-xs text-amber-600 mt-0.5">Please pay {currency(totalDue)} to avoid late penalties.</p></div>
          <span className="text-lg font-bold text-amber-800">{currency(totalDue)}</span>
        </div>
      )}
      <div className="card">
        <div className="card-header"><h2 className="text-base font-semibold">Invoice History</h2></div>
        {invoices.length === 0
          ? <div className="p-8"><EmptyState icon={BanknotesIcon} title="No invoices yet" description="Your fee invoices will appear here." /></div>
          : <DataTable
              columns={[
                { key:"invoice_number", header:"Invoice", render:r=><span className="font-mono text-xs">{r.invoice_number}</span> },
                { key:"due_date", header:"Due", render:r=>{const od=dayjs(r.due_date).isBefore(dayjs())&&r.status!=="paid"; return <span className={od?"text-red-600 font-medium":""}>{fmt.date(r.due_date)}</span>;} },
                { key:"total_amount", header:"Total", render:r=>currency(r.total_amount) },
                { key:"paid_amount", header:"Paid", render:r=><span className="text-green-600">{currency(r.paid_amount)}</span> },
                { key:"outstanding_amount", header:"Due", render:r=><span className={Number(r.outstanding_amount)>0?"text-red-600 font-semibold":"text-slate-400"}>{currency(r.outstanding_amount)}</span> },
                { key:"status", header:"Status", render:r=>{const s=FEE_STATUS[r.status];return<Badge color={s?.color??"slate"}>{s?.label??r.status}</Badge>;} },
              ]}
              data={invoices} rowKey={r=>r.id}
            />
        }
      </div>
    </div>
  );
}
