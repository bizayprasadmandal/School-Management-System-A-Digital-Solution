/**
 * Admissions & Enrollment — Full CRUD with CRM pipeline actions
 * (schedule tour → complete tour → send offer → accept offer → enroll).
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  PlusIcon,
  DocumentTextIcon,
  CalendarDaysIcon,
  ClipboardDocumentCheckIcon,
  ChevronDownIcon,
  MapPinIcon,
  PaperAirplaneIcon,
  CheckBadgeIcon,
  AcademicCapIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState } from "../../components/common";
import { useClassrooms } from "../../api/hooks";
import { useTitle } from "../../hooks";

interface TimelineEvent {
  id: string;
  stage: string;
  stage_display: string;
  note: string;
  created_by_name: string;
  created_at: string;
}
interface Application {
  id: string;
  application_number: string;
  full_name: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  date_of_birth: string;
  gender: string;
  applying_for_grade: string;
  status: string;
  status_display: string;
  intake: string;
  intake_name: string;
  submitted_at: string | null;
  tour_date: string | null;
  toured_at: string | null;
  offer_sent_at: string | null;
  offer_accepted_at: string | null;
  linked_student: string | null;
  timeline: TimelineEvent[];
}
interface Intake {
  id: string;
  name: string;
  academic_year: string;
  application_start: string;
  application_end: string;
  status: string;
  status_display: string;
  application_count: number;
  max_applications: number;
}
interface Review {
  id: string;
  application: string;
  reviewer_name: string;
  score: number | null;
  recommendation: string;
  notes: string;
}

const SC: Record<string, string> = {
  draft: "bg-slate-100 text-slate-600",
  submitted: "bg-blue-100 text-blue-700",
  under_review: "bg-amber-100 text-amber-700",
  shortlisted: "bg-indigo-100 text-indigo-700",
  accepted: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  waitlisted: "bg-yellow-100 text-yellow-700",
  enrolled: "bg-green-100 text-green-700",
  cancelled: "bg-slate-100 text-slate-500",
};

const STAGE_META: Record<string, { label: string; color: string }> = {
  created: { label: "Created", color: "bg-slate-400" },
  submitted: { label: "Submitted", color: "bg-blue-500" },
  tour_scheduled: { label: "Tour", color: "bg-violet-500" },
  tour_completed: { label: "Toured", color: "bg-violet-600" },
  offer_sent: { label: "Offer", color: "bg-amber-500" },
  offer_accepted: { label: "Offer Accepted", color: "bg-emerald-500" },
  enrolled: { label: "Enrolled", color: "bg-green-600" },
};

/** Ordered pipeline steps shown as a progress trail on each application. */
const PIPELINE_STEPS = ["created", "submitted", "tour", "offer", "enrolled"] as const;
function stageIndex(a: Application): number {
  if (a.status === "enrolled") return 4;
  if (a.offer_sent_at || a.offer_accepted_at) return 3;
  if (a.toured_at) return 2;
  if (a.tour_date) return 2;
  if (a.status !== "draft") return 1;
  return 0;
}

type Tab = "applications" | "intakes" | "reviews";
const TABS: { key: Tab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "applications", label: "Applications", icon: DocumentTextIcon },
  { key: "intakes", label: "Intake Periods", icon: CalendarDaysIcon },
  { key: "reviews", label: "Reviews", icon: ClipboardDocumentCheckIcon },
];

export default function AdmissionsPage() {
  useTitle("Admissions & Enrollment");
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>("applications");
  const [search, setSearch] = useState("");
  const [showAppForm, setShowAppForm] = useState(false);
  const [editingApp, setEditingApp] = useState<Application | null>(null);
  const [showIntakeForm, setShowIntakeForm] = useState(false);
  const [editingIntake, setEditingIntake] = useState<Intake | null>(null);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [appStatus, setAppStatus] = useState<Record<string, string>>({});
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [tourTarget, setTourTarget] = useState<Application | null>(null);
  const [enrollTarget, setEnrollTarget] = useState<Application | null>(null);

  const { data: apps = [], isLoading: aLoading } = useQuery({
    queryKey: ["admissions-apps"],
    queryFn: async () => {
      const r = await api.get<{ results: Application[] }>("/admissions/applications/");
      return r.results ?? [];
    },
  });
  const { data: intakes = [], isLoading: iLoading } = useQuery({
    queryKey: ["admissions-intakes"],
    queryFn: async () => {
      const r = await api.get<{ results: Intake[] }>("/admissions/intakes/");
      return r.results ?? [];
    },
  });
  const { data: reviews = [] } = useQuery({
    queryKey: ["admissions-reviews"],
    queryFn: async () => {
      const r = await api.get<{ results: Review[] }>("/admissions/reviews/");
      return r.results ?? [];
    },
  });

  const submitApp = useMutation({
    mutationFn: (id: string) => api.post(`/admissions/applications/${id}/submit/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admissions-apps"] });
      toast.success("Submitted");
    },
  });
  const updateStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      api.post(`/admissions/applications/${id}/update-status/`, { status }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admissions-apps"] });
      toast.success("Status updated");
    },
  });
  const delApp = useMutation({
    mutationFn: (id: string) => api.delete(`/admissions/applications/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admissions-apps"] });
      toast.success("Deleted");
    },
  });
  const delIntake = useMutation({
    mutationFn: (id: string) => api.delete(`/admissions/intakes/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admissions-intakes"] });
      toast.success("Deleted");
    },
  });

  const invalidateApps = () => qc.invalidateQueries({ queryKey: ["admissions-apps"] });
  const scheduleTour = useMutation({
    mutationFn: ({ id, tour_date }: { id: string; tour_date: string }) =>
      api.post(`/admissions/applications/${id}/schedule-tour/`, { tour_date }),
    onSuccess: () => {
      invalidateApps();
      toast.success("Tour scheduled");
    },
  });
  const completeTour = useMutation({
    mutationFn: (id: string) => api.post(`/admissions/applications/${id}/complete-tour/`, {}),
    onSuccess: () => {
      invalidateApps();
      toast.success("Tour completed");
    },
  });
  const sendOffer = useMutation({
    mutationFn: (id: string) => api.post(`/admissions/applications/${id}/send-offer/`, {}),
    onSuccess: () => {
      invalidateApps();
      toast.success("Offer sent");
    },
  });
  const acceptOffer = useMutation({
    mutationFn: (id: string) => api.post(`/admissions/applications/${id}/accept-offer/`, {}),
    onSuccess: () => {
      invalidateApps();
      toast.success("Offer accepted");
    },
  });
  const enrollApp = useMutation({
    mutationFn: ({ id, classroom_id }: { id: string; classroom_id: string }) =>
      api.post<{ generated_password?: string }>(`/admissions/applications/${id}/enroll/`, {
        classroom_id,
      }),
    onSuccess: (data) => {
      invalidateApps();
      setEnrollTarget(null);
      toast.success(
        data?.generated_password
          ? `Enrolled — temp password: ${data.generated_password}`
          : "Enrolled",
      );
    },
  });

  const filtered = search.trim()
    ? apps.filter(
        (a) =>
          a.full_name?.toLowerCase().includes(search.toLowerCase()) ||
          a.application_number.toLowerCase().includes(search.toLowerCase()),
      )
    : apps;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Admissions & Enrollment
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage applications, intake periods, and admission reviews
          </p>
        </div>
        <div className="flex gap-2">
          {tab === "applications" && (
            <Button
              onClick={() => {
                setEditingApp(null);
                setShowAppForm(true);
              }}
            >
              <PlusIcon className="h-4 w-4 mr-1.5" />
              Add Application
            </Button>
          )}
          {tab === "intakes" && (
            <Button
              onClick={() => {
                setEditingIntake(null);
                setShowIntakeForm(true);
              }}
            >
              <PlusIcon className="h-4 w-4 mr-1.5" />
              Add Intake
            </Button>
          )}
          {tab === "reviews" && (
            <Button onClick={() => setShowReviewForm(true)}>
              <PlusIcon className="h-4 w-4 mr-1.5" />
              Add Review
            </Button>
          )}
        </div>
      </div>
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
        {TABS.map((t) => {
          const I = t.icon;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap ${
                tab === t.key
                  ? "bg-white dark:bg-slate-700 shadow-sm"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              <I className="h-4 w-4" />
              {t.label}
            </button>
          );
        })}
      </div>
      {tab === "applications" && (
        <>
          {apps.length > 5 && (
            <div className="relative max-w-sm">
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-3 pr-3 py-2 rounded-lg border border-slate-300 bg-white dark:bg-slate-800 text-sm"
                placeholder="Search applications..."
              />
            </div>
          )}
          {aLoading ? (
            <div className="space-y-2">
              {[1, 2, 3].map((i) => (
                <div
                  key={i}
                  className="h-20 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
                />
              ))}
            </div>
          ) : !filtered.length ? (
            <EmptyState icon={DocumentTextIcon} title="No applications" />
          ) : (
            <div className="space-y-2">
              {filtered.map((a) => {
                const step = stageIndex(a);
                return (
                  <div
                    key={a.id}
                    className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 hover:shadow-md transition-shadow"
                  >
                    <div className="p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <button
                              onClick={() => setExpanded((p) => ({ ...p, [a.id]: !p[a.id] }))}
                              className="font-semibold text-slate-900 dark:text-white hover:text-indigo-600 dark:hover:text-indigo-400 text-left flex items-center gap-1 transition-colors"
                            >
                              {a.full_name || a.application_number}
                              <ChevronDownIcon
                                className={`h-4 w-4 text-slate-400 transition-transform ${
                                  expanded[a.id] ? "rotate-180" : ""
                                }`}
                              />
                            </button>
                            <span
                              className={`text-xs font-medium px-2 py-0.5 rounded ${
                                SC[a.status] || "bg-slate-100"
                              }`}
                            >
                              {a.status_display}
                            </span>
                          </div>
                          <p className="text-xs text-slate-400 truncate">
                            {a.application_number} · Grade {a.applying_for_grade}
                            {a.intake_name ? ` · ${a.intake_name}` : ""}
                          </p>
                          <p className="text-xs text-slate-400 truncate">
                            {a.email}
                            {a.submitted_at
                              ? ` · Submitted ${dayjs(a.submitted_at).format("MMM D")}`
                              : ""}
                            {a.tour_date ? ` · Tour ${dayjs(a.tour_date).format("MMM D")}` : ""}
                            {a.offer_sent_at
                              ? ` · Offer ${dayjs(a.offer_sent_at).format("MMM D")}`
                              : ""}
                          </p>
                        </div>
                        <div className="flex gap-2 ml-4 items-start shrink-0">
                          {a.status === "draft" && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => submitApp.mutate(a.id)}
                            >
                              Submit
                            </Button>
                          )}
                          {a.status === "shortlisted" && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => sendOffer.mutate(a.id)}
                              disabled={sendOffer.isPending}
                            >
                              <PaperAirplaneIcon className="h-3.5 w-3.5 mr-1" />
                              Send Offer
                            </Button>
                          )}
                          {a.status === "accepted" && !a.offer_sent_at && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => sendOffer.mutate(a.id)}
                              disabled={sendOffer.isPending}
                            >
                              <PaperAirplaneIcon className="h-3.5 w-3.5 mr-1" />
                              Send Offer
                            </Button>
                          )}
                          {a.offer_sent_at && !a.offer_accepted_at && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => acceptOffer.mutate(a.id)}
                              disabled={acceptOffer.isPending}
                            >
                              <CheckBadgeIcon className="h-3.5 w-3.5 mr-1" />
                              Accept Offer
                            </Button>
                          )}
                          {a.offer_sent_at && a.status !== "enrolled" && (
                            <Button size="sm" onClick={() => setEnrollTarget(a)}>
                              <AcademicCapIcon className="h-3.5 w-3.5 mr-1" />
                              Enroll
                            </Button>
                          )}
                          {["submitted", "under_review", "shortlisted", "accepted"].includes(
                            a.status,
                          ) && (
                            <select
                              value={appStatus[a.id] || ""}
                              onChange={(e) => {
                                const v = e.target.value;
                                if (v) {
                                  updateStatus.mutate({ id: a.id, status: v });
                                  setAppStatus((p) => ({ ...p, [a.id]: v }));
                                }
                              }}
                              className="text-xs rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-2 py-1"
                            >
                              <option value="">Change...</option>
                              <option value="under_review">Under Review</option>
                              <option value="shortlisted">Shortlisted</option>
                              <option value="accepted">Accepted</option>
                              <option value="rejected">Rejected</option>
                              <option value="waitlisted">Waitlisted</option>
                            </select>
                          )}
                          <button
                            onClick={() => {
                              if (confirm("Delete?")) delApp.mutate(a.id);
                            }}
                            className="text-xs text-red-500 font-medium"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                    {/* ── Pipeline trail ── */}
                    <div className="px-4 pb-3 flex items-center gap-1">
                      {PIPELINE_STEPS.map((s, i) => {
                        const active = i < step;
                        return (
                          <div key={s} className="flex items-center gap-1 flex-1 last:flex-none">
                            <div
                              className={`h-1.5 rounded-full flex-1 ${
                                active ? "bg-indigo-500" : "bg-slate-200 dark:bg-slate-700"
                              }`}
                            />
                            {i === PIPELINE_STEPS.length - 1 && (
                              <span
                                className={`text-[10px] font-medium ${
                                  active ? "text-indigo-600" : "text-slate-400"
                                }`}
                              >
                                Enrolled
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                    {expanded[a.id] && (
                      <div className="px-4 pb-4 pt-1 border-t border-slate-100 dark:border-slate-700">
                        <div className="flex flex-wrap gap-2 mb-3">
                          <Button size="sm" variant="secondary" onClick={() => setTourTarget(a)}>
                            <MapPinIcon className="h-3.5 w-3.5 mr-1" />
                            {a.tour_date ? "Reschedule Tour" : "Schedule Tour"}
                          </Button>
                          {a.tour_date && !a.toured_at && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => completeTour.mutate(a.id)}
                              disabled={completeTour.isPending}
                            >
                              Complete Tour
                            </Button>
                          )}
                          {a.linked_student && (
                            <span className="inline-flex items-center gap-1 text-xs font-medium text-green-600 dark:text-green-400">
                              <AcademicCapIcon className="h-4 w-4" />
                              Linked to student {a.linked_student}
                            </span>
                          )}
                        </div>
                        {!a.timeline || !a.timeline.length ? (
                          <p className="text-xs text-slate-400">No pipeline activity yet.</p>
                        ) : (
                          <ol className="space-y-2">
                            {a.timeline.map((t) => {
                              const meta = STAGE_META[t.stage];
                              return (
                                <li key={t.id} className="flex items-start gap-2">
                                  <span
                                    className={`mt-1 h-2 w-2 rounded-full shrink-0 ${
                                      meta?.color || "bg-slate-400"
                                    }`}
                                  />
                                  <div className="flex-1">
                                    <div className="flex items-center justify-between">
                                      <p className="text-xs font-medium text-slate-800 dark:text-slate-200">
                                        {t.stage_display || t.stage}
                                      </p>
                                      <span className="text-[10px] text-slate-400">
                                        {dayjs(t.created_at).format("MMM D, h:mm A")}
                                      </span>
                                    </div>
                                    {t.note && <p className="text-xs text-slate-500">{t.note}</p>}
                                    <p className="text-[10px] text-slate-400">
                                      {t.created_by_name || "System"}
                                    </p>
                                  </div>
                                </li>
                              );
                            })}
                          </ol>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
      {tab === "intakes" &&
        (iLoading ? (
          <div className="grid gap-3 sm:grid-cols-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="h-24 animate-pulse bg-slate-100 dark:bg-slate-800 rounded-lg"
              />
            ))}
          </div>
        ) : !intakes.length ? (
          <EmptyState icon={CalendarDaysIcon} title="No intake periods" />
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {intakes.map((i) => (
              <div
                key={i.id}
                onClick={() => {
                  setEditingIntake(i);
                  setShowIntakeForm(true);
                }}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                      {i.name}
                    </p>
                    <p className="text-xs text-slate-400">
                      {i.academic_year} · {dayjs(i.application_start).format("MMM D")} -{" "}
                      {dayjs(i.application_end).format("MMM D, YYYY")}
                    </p>
                  </div>
                  <div className="text-right">
                    <span
                      className={`text-xs font-medium px-2 py-0.5 rounded ${
                        i.status === "open"
                          ? "bg-green-100 text-green-700"
                          : i.status === "upcoming"
                            ? "bg-blue-100 text-blue-700"
                            : "bg-slate-100 text-slate-500"
                      }`}
                    >
                      {i.status_display}
                    </span>
                    <p className="text-xs text-slate-400 mt-1">
                      {i.application_count} applicant{i.application_count !== 1 ? "s" : ""}
                    </p>
                  </div>
                </div>
                <div
                  className="flex gap-2 mt-2 pt-2 border-t border-slate-100"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    onClick={() => {
                      setEditingIntake(i);
                      setShowIntakeForm(true);
                    }}
                    className="text-xs text-indigo-600 font-medium"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete?")) delIntake.mutate(i.id);
                    }}
                    className="text-xs text-red-500 font-medium"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        ))}
      {tab === "reviews" &&
        (!reviews.length ? (
          <EmptyState icon={ClipboardDocumentCheckIcon} title="No reviews" />
        ) : (
          <div className="space-y-2">
            {reviews.map((r) => (
              <div
                key={r.id}
                className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-slate-900 dark:text-white">
                      Application Review
                    </p>
                    <p className="text-xs text-slate-400">
                      Reviewer: {r.reviewer_name}
                      {r.score ? ` · Score: ${r.score}/100` : ""}
                      {r.recommendation ? ` · ${r.recommendation}` : ""}
                    </p>
                    {r.notes && <p className="text-xs text-slate-500 mt-1">{r.notes}</p>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ))}
      <AppFormModal
        open={showAppForm}
        onClose={() => {
          setShowAppForm(false);
          setEditingApp(null);
        }}
        application={editingApp}
        intakes={intakes}
        onSaved={() => {
          setShowAppForm(false);
          setEditingApp(null);
          qc.invalidateQueries({ queryKey: ["admissions-apps"] });
        }}
      />
      <IntakeFormModal
        open={showIntakeForm}
        onClose={() => {
          setShowIntakeForm(false);
          setEditingIntake(null);
        }}
        intake={editingIntake}
        onSaved={() => {
          setShowIntakeForm(false);
          setEditingIntake(null);
          qc.invalidateQueries({ queryKey: ["admissions-intakes"] });
        }}
      />
      <ReviewFormModal
        open={showReviewForm}
        onClose={() => setShowReviewForm(false)}
        apps={apps}
        onSaved={() => {
          setShowReviewForm(false);
          qc.invalidateQueries({ queryKey: ["admissions-reviews"] });
        }}
      />
      <TourModal
        open={!!tourTarget}
        onClose={() => setTourTarget(null)}
        application={tourTarget}
        onSave={({ id, tour_date }) => {
          scheduleTour.mutate({ id, tour_date });
          setTourTarget(null);
        }}
      />
      <EnrollModal
        open={!!enrollTarget}
        onClose={() => setEnrollTarget(null)}
        application={enrollTarget}
        onSave={(d) => enrollApp.mutate(d)}
      />
    </div>
  );
}

function AppFormModal({
  open,
  onClose,
  application,
  intakes,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  application?: Application | null;
  intakes: Intake[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    intake: application?.intake ?? "",
    first_name: application?.first_name ?? "",
    last_name: application?.last_name ?? "",
    email: application?.email ?? "",
    phone: application?.phone ?? "",
    date_of_birth: application?.date_of_birth ?? "",
    gender: application?.gender ?? "",
    applying_for_grade: application?.applying_for_grade ?? "",
  });
  const create = useMutation({
    mutationFn: (d: typeof f) => api.post("/admissions/applications/", d),
    onSuccess: () => {
      toast.success("Application created");
      onSaved();
    },
  });
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.first_name.trim() || !f.last_name.trim()) return toast.error("Name required");
    if (!f.date_of_birth) return toast.error("Date of birth is required");
    if (!f.gender) return toast.error("Gender is required");
    create.mutate(f);
  };
  return (
    <Modal open={open} onClose={onClose} title="Add Application">
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Intake</label>
            <select
              value={f.intake}
              onChange={(e) => setF((p) => ({ ...p, intake: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            >
              <option value="">Select...</option>
              {intakes.map((i) => (
                <option key={i.id} value={i.id}>
                  {i.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Grade Applying For</label>
            <input
              value={f.applying_for_grade}
              onChange={(e) => setF((p) => ({ ...p, applying_for_grade: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
              placeholder="e.g. Grade 9"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">First Name *</label>
            <input
              value={f.first_name}
              onChange={(e) => setF((p) => ({ ...p, first_name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Last Name *</label>
            <input
              value={f.last_name}
              onChange={(e) => setF((p) => ({ ...p, last_name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
              required
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              value={f.email}
              onChange={(e) => setF((p) => ({ ...p, email: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Phone</label>
            <input
              value={f.phone}
              onChange={(e) => setF((p) => ({ ...p, phone: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Date of Birth *</label>
            <input
              type="date"
              value={f.date_of_birth}
              onChange={(e) => setF((p) => ({ ...p, date_of_birth: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Gender *</label>
            <select
              value={f.gender}
              onChange={(e) => setF((p) => ({ ...p, gender: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
              required
            >
              <option value="">Select...</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={create.isPending}>
            Cancel
          </Button>
          <Button type="submit" loading={create.isPending}>
            Create Application
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function IntakeFormModal({
  open,
  onClose,
  intake,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  intake?: Intake | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    name: intake?.name ?? "",
    academic_year: intake?.academic_year ?? "",
    application_start: intake?.application_start ?? dayjs().format("YYYY-MM-DD"),
    application_end: intake?.application_end ?? dayjs().add(60, "day").format("YYYY-MM-DD"),
    status: intake?.status ?? "upcoming",
    max_applications: intake?.max_applications ?? 0,
  });
  const isEdit = !!intake;
  const create = useMutation({
    mutationFn: (d: typeof f) => api.post("/admissions/intakes/", d),
    onSuccess: () => {
      toast.success("Intake created");
      onSaved();
    },
  });
  const update = useMutation({
    mutationFn: (d: typeof f) => api.patch(`/admissions/intakes/${intake!.id}/`, d),
    onSuccess: () => {
      toast.success("Intake updated");
      onSaved();
    },
  });
  const saving = create.isPending || update.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Name required");
    if (isEdit) update.mutate(f);
    else create.mutate(f);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Intake" : "Add Intake Period"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
              placeholder="e.g. Fall 2026 Intake"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Academic Year</label>
            <input
              value={f.academic_year}
              onChange={(e) => setF((p) => ({ ...p, academic_year: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Start Date</label>
            <input
              type="date"
              value={f.application_start}
              onChange={(e) => setF((p) => ({ ...p, application_start: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">End Date</label>
            <input
              type="date"
              value={f.application_end}
              onChange={(e) => setF((p) => ({ ...p, application_end: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Status</label>
            <select
              value={f.status}
              onChange={(e) => setF((p) => ({ ...p, status: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            >
              <option value="upcoming">Upcoming</option>
              <option value="open">Open</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Max Applications</label>
            <input
              type="number"
              min={0}
              value={f.max_applications}
              onChange={(e) => setF((p) => ({ ...p, max_applications: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
              placeholder="0 = unlimited"
            />
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"} Intake
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function ReviewFormModal({
  open,
  onClose,
  apps,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  apps: Application[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({ application: "", score: "", recommendation: "", notes: "" });
  const create = useMutation({
    mutationFn: (d: {
      application: string;
      score: number | null;
      recommendation: string;
      notes: string;
    }) => api.post("/admissions/reviews/", { ...d, score: d.score ? Number(d.score) : null }),
    onSuccess: () => {
      toast.success("Review added");
      onSaved();
    },
  });
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.application) return toast.error("Select application");
    create.mutate({ ...f, score: f.score ? Number(f.score) : null });
  };
  return (
    <Modal open={open} onClose={onClose} title="Add Review">
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Application *</label>
            <select
              value={f.application}
              onChange={(e) => setF((p) => ({ ...p, application: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
              required
            >
              <option value="">Select...</option>
              {apps.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.full_name || a.application_number}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Score (0-100)</label>
            <input
              type="number"
              min={0}
              max={100}
              value={f.score}
              onChange={(e) => setF((p) => ({ ...p, score: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Recommendation</label>
          <select
            value={f.recommendation}
            onChange={(e) => setF((p) => ({ ...p, recommendation: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
          >
            <option value="">Select...</option>
            <option value="Strongly Recommend">Strongly Recommend</option>
            <option value="Recommend">Recommend</option>
            <option value="Consider">Consider</option>
            <option value="Not Recommended">Not Recommended</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Notes</label>
          <textarea
            value={f.notes}
            onChange={(e) => setF((p) => ({ ...p, notes: e.target.value }))}
            rows={2}
            className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={create.isPending}>
            Cancel
          </Button>
          <Button type="submit" loading={create.isPending}>
            Add Review
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function TourModal({
  open,
  onClose,
  application,
  onSave,
}: {
  open: boolean;
  onClose: () => void;
  application: Application | null;
  onSave: (d: { id: string; tour_date: string }) => void;
}) {
  const [date, setDate] = useState("");
  if (!open) return null;
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Schedule Tour — ${application?.full_name || ""}`}
      description="Pick the campus tour date for this applicant."
    >
      <div className="space-y-4">
        <div>
          <label htmlFor="tour-date" className="block text-sm font-medium mb-1">
            Tour Date *
          </label>
          <input
            id="tour-date"
            type="date"
            value={date}
            min={dayjs().format("YYYY-MM-DD")}
            onChange={(e) => setDate(e.target.value)}
            className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            disabled={!date || !application}
            onClick={() => {
              if (application && date) onSave({ id: application.id, tour_date: date });
            }}
          >
            Schedule Tour
          </Button>
        </div>
      </div>
    </Modal>
  );
}

function EnrollModal({
  open,
  onClose,
  application,
  onSave,
}: {
  open: boolean;
  onClose: () => void;
  application: Application | null;
  onSave: (d: { id: string; classroom_id: string }) => void;
}) {
  const [classroomId, setClassroomId] = useState("");
  const { data: classrooms, isLoading } = useClassrooms();
  if (!open) return null;
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={`Enroll — ${application?.full_name || ""}`}
      description="Create the student profile and assign to a classroom. A temporary password is generated for the new student account."
    >
      <div className="space-y-4">
        <div>
          <label htmlFor="enroll-classroom" className="block text-sm font-medium mb-1">
            Classroom *
          </label>
          {isLoading ? (
            <p className="text-sm text-slate-400">Loading classrooms...</p>
          ) : (
            <select
              id="enroll-classroom"
              value={classroomId}
              onChange={(e) => setClassroomId(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            >
              <option value="">Select...</option>
              {(classrooms?.results ?? []).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.grade_name ? `${c.grade_name} ${c.name}` : c.name}
                </option>
              ))}
            </select>
          )}
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            disabled={!classroomId || !application}
            onClick={() => {
              if (application && classroomId)
                onSave({ id: application.id, classroom_id: classroomId });
            }}
          >
            Enroll Student
          </Button>
        </div>
      </div>
    </Modal>
  );
}
