/**
 * Teacher Counseling Page — Refer students and view past referrals.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import { UserGroupIcon, PlusIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

interface Referral {
  id: string;
  student_name: string;
  category: string;
  priority: string;
  status: string;
  reason: string;
  created_at: string;
}
interface Student {
  id: string;
  user_name: string;
}

export default function TeacherCounselingPage() {
  useTitle("Counseling Referrals");
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);

  const { data: referrals = [], isLoading } = useQuery({
    queryKey: ["teacher-referrals"],
    queryFn: async () => {
      const r = await api.get<{ results: Referral[] }>("/counseling/referrals/my/");
      return r.results ?? [];
    },
  });
  const { data: students = [] } = useQuery({
    queryKey: ["students-short"],
    queryFn: async () => {
      const r = await api.get<{ results: Student[] }>("/students/");
      return r.results ?? [];
    },
  });

  const delRef = useMutation({
    mutationFn: (id: string) => api.delete(`/counseling/referrals/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["teacher-referrals"] });
      toast.success("Deleted");
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Counseling Referrals
          </h1>
          <p className="text-sm text-slate-500 mt-1">Refer students for counseling support</p>
        </div>
        <Button onClick={() => setShowForm(true)}>
          <PlusIcon className="h-4 w-4 mr-1.5" />
          New Referral
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg" />
          ))}
        </div>
      ) : !referrals.length ? (
        <EmptyState
          icon={UserGroupIcon}
          title="No referrals"
          description="You haven't referred any students yet"
        />
      ) : (
        <div className="space-y-2">
          {referrals.map((r) => (
            <div
              key={r.id}
              className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-slate-900 dark:text-white">{r.student_name}</p>
                  <p className="text-sm text-slate-500 mt-0.5">{r.reason}</p>
                  <p className="text-xs text-slate-400 mt-1">
                    {dayjs(r.created_at).format("MMM D, YYYY")}
                  </p>
                </div>
                <div className="flex gap-2 items-center">
                  <Badge color="indigo">{r.category}</Badge>
                  <Badge
                    color={
                      r.priority === "high" ? "red" : r.priority === "medium" ? "amber" : "blue"
                    }
                  >
                    {r.priority}
                  </Badge>
                  <Badge
                    color={
                      r.status === "closed"
                        ? "green"
                        : r.status === "in_progress"
                          ? "amber"
                          : "slate"
                    }
                  >
                    {r.status}
                  </Badge>
                  <button
                    onClick={() => {
                      if (confirm("Delete?")) delRef.mutate(r.id);
                    }}
                    className="text-xs text-red-500 font-medium"
                  >
                    Del
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <ReferralFormModal
        open={showForm}
        onClose={() => setShowForm(false)}
        students={students}
        onSaved={() => {
          setShowForm(false);
          qc.invalidateQueries({ queryKey: ["teacher-referrals"] });
        }}
      />
    </div>
  );
}

function ReferralFormModal({
  open,
  onClose,
  students,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  students: Student[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({ student: "", category: "academic", priority: "medium", reason: "" });
  const create = useMutation({
    mutationFn: (d: typeof f) => api.post("/counseling/referrals/", d),
    onSuccess: () => {
      toast.success("Referral submitted");
      onSaved();
    },
  });
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.student || !f.reason) return toast.error("Student and reason required");
    create.mutate(f);
  };
  return (
    <Modal open={open} onClose={onClose} title="New Counseling Referral">
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Student *</label>
          <select
            value={f.student}
            onChange={(e) => setF((p) => ({ ...p, student: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            required
          >
            <option value="">Select...</option>
            {students.map((s) => (
              <option key={s.id} value={s.id}>
                {s.user_name}
              </option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Category</label>
            <select
              value={f.category}
              onChange={(e) => setF((p) => ({ ...p, category: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            >
              <option value="academic">Academic</option>
              <option value="behavioral">Behavioral</option>
              <option value="social">Social</option>
              <option value="emotional">Emotional</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Priority</label>
            <select
              value={f.priority}
              onChange={(e) => setF((p) => ({ ...p, priority: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Reason *</label>
          <textarea
            value={f.reason}
            onChange={(e) => setF((p) => ({ ...p, reason: e.target.value }))}
            rows={3}
            className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            placeholder="Describe why you're referring this student..."
            required
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={create.isPending}>
            Cancel
          </Button>
          <Button type="submit" loading={create.isPending}>
            Submit Referral
          </Button>
        </div>
      </form>
    </Modal>
  );
}
