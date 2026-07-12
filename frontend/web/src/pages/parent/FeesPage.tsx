/**
 * Parent Fees Page — view and track fee invoices for children
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Badge, DataTable, EmptyState, SkeletonCard } from "../../components/common";
import { currency, FEE_STATUS, fmt } from "../../utils";
import { useTitle } from "../../hooks";
import type { StudentListItem, FeeInvoice, PaginatedResponse } from "../../types";
import { BanknotesIcon, CheckCircleIcon, ClockIcon } from "@heroicons/react/24/outline";
import dayjs from "dayjs";

export default function ParentFeesPage() {
  useTitle("Fee Management");
  const [childIdx, setChildIdx] = useState(0);

  const { data: children, isLoading: childrenLoading } = useQuery({ queryKey: ["parent-children-fees"], queryFn: () => api.get<PaginatedResponse<StudentListItem>>("/students/") });
  const childList = children?.results ?? [];
  const child = childList[childIdx];

  const { data: invData, isLoading: invLoading } = useQuery({
    queryKey: ["parent-child-inv", child?.id],
    queryFn: () => api.get<PaginatedResponse<FeeInvoice>>(`/fees/invoices/?student=${child.id}`),
    enabled: !!child?.id,
  });
  const invoices = invData?.results ?? [];
  const totalDue = invoices.filter((i: FeeInvoice)=>["unpaid","overdue","partial"].includes(i.status)).reduce((s: number, i: FeeInvoice)=>s+Number(i.outstanding_amount),0);
  const totalPaid = invoices.reduce((s: number, i: FeeInvoice)=>s+Number(i.paid_amount),0);

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold text-slate-900">Fee Management</h1><p className="text-sm text-slate-500 mt-1">Track fee invoices and payment history</p></div>

      {childList.length > 1 && (
        <div className="card p-4 flex gap-2 overflow-x-auto">
          {childList.map((c: StudentListItem, i: number) => (
            <button key={c.id} onClick={()=>setChildIdx(i)}
              className={`flex-shrink-0 rounded-xl px-4 py-2 text-sm font-semibold transition-colors ${i===childIdx?"bg-violet-600 text-white":"bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>
              {c.full_name}
            </button>
          ))}
        </div>
      )}

      {childrenLoading || invLoading ? <div className="p-4"><SkeletonCard /></div>
        : (
          <>
            <div className="grid grid-cols-3 gap-4">
              {[
                { label:"Total Paid", value:currency(totalPaid), icon:CheckCircleIcon, color:"text-green-600 bg-green-50" },
                { label:"Outstanding", value:currency(totalDue), icon:ClockIcon, color:totalDue>0?"text-red-600 bg-red-50":"text-slate-500 bg-slate-50" },
                { label:"Invoices", value:invoices.length, icon:BanknotesIcon, color:"text-indigo-600 bg-indigo-50" },
              ].map(({label,value,icon:Icon,color})=>(
                <div key={label} className="card p-4 flex items-center gap-3">
                  <div className={`h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 ${color.split(" ")[1]}`}><Icon className={`h-5 w-5 ${color.split(" ")[0]}`}/></div>
                  <div><p className={`text-xl font-bold ${color.split(" ")[0]}`}>{value}</p><p className="text-xs text-slate-500">{label}</p></div>
                </div>
              ))}
            </div>

            {totalDue > 0 && (
              <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
                <p className="text-sm font-semibold text-amber-800">Payment Required</p>
                <p className="text-xs text-amber-700 mt-0.5">{currency(totalDue)} outstanding. Please pay promptly to avoid late penalty fees.</p>
              </div>
            )}

            <div className="card">
              <div className="card-header"><h2 className="text-base font-semibold">Invoice History</h2></div>
              {invoices.length === 0
                ? <div className="p-8"><EmptyState icon={BanknotesIcon} title="No invoices yet" description="Fee invoices for your child appear here." /></div>
                : <DataTable
                    columns={[
                      { key:"invoice_number", header:"Invoice", render:r=><span className="font-mono text-xs">{r.invoice_number}</span> },
                      { key:"due_date", header:"Due", render:r=>{const od=dayjs(r.due_date).isBefore(dayjs())&&r.status!=="paid";return<span className={od?"text-red-600 font-medium":""}>{fmt.date(r.due_date)}</span>;} },
                      { key:"total_amount", header:"Total", render:r=>currency(r.total_amount) },
                      { key:"paid_amount", header:"Paid", render:r=><span className="text-green-600">{currency(r.paid_amount)}</span> },
                      { key:"outstanding_amount", header:"Outstanding", render:r=><span className={Number(r.outstanding_amount)>0?"text-red-600 font-semibold":"text-slate-400"}>{currency(r.outstanding_amount)}</span> },
                      { key:"status", header:"Status", render:r=>{const s=FEE_STATUS[r.status];return<Badge color={s?.color??"slate"}>{s?.label??r.status}</Badge>;} },
                    ]}
                    data={invoices} rowKey={r=>r.id}
                  />
              }
            </div>
          </>
        )
      }
    </div>
  );
}
