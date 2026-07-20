/**
 * Alumni Management — Full CRUD with form modals.
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  PlusIcon, UsersIcon, CalendarDaysIcon, CurrencyDollarIcon, GlobeAltIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState } from "../../components/common";
import { useTitle } from "../../hooks";

interface Profile {
  id: string; user: string; user_name: string; user_email: string;
  graduation_year: number; occupation: string; employer: string;
  employment_status: string; city: string; country: string;
}
interface AlumniEvent {
  id: string; title: string; event_date: string; end_date: string | null;
  location: string; status: string; status_display: string; fee_amount: number;
}
interface Donation {
  id: string; alumni: string; alumni_name: string; amount: number;
  fund_type: string; fund_type_display: string; donation_date: string; is_recurring: boolean;
}
interface Chapter {
  id: string; name: string; city: string; country: string;
  president_name: string | null; is_active: boolean;
}

type Tab = "profiles" | "events" | "donations" | "chapters";

const TABS: { key: Tab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "profiles", label: "Alumni", icon: UsersIcon },
  { key: "events", label: "Events", icon: CalendarDaysIcon },
  { key: "donations", label: "Donations", icon: CurrencyDollarIcon },
  { key: "chapters", label: "Chapters", icon: GlobeAltIcon },
];

function ProfilesTab({
  profiles, onEdit, onDelete, search, setSearch,
}: {
  profiles: Profile[]; onEdit: (p: Profile) => void; onDelete: (id: string) => void;
  search: string; setSearch: (v: string) => void;
}) {
  const filtered = search.trim()
    ? profiles.filter(p =>
        p.user_name.toLowerCase().includes(search.toLowerCase()) ||
        (p.occupation && p.occupation.toLowerCase().includes(search.toLowerCase()))
      )
    : profiles;

  return (
    <div className="space-y-4">
      {profiles.length > 5 && (
        <div className="relative max-w-sm">
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-3 pr-3 py-2 rounded-lg border border-slate-300 bg-white dark:bg-slate-800 text-sm"
            placeholder="Search alumni..."
          />
        </div>
      )}
      {!profiles.length ? (
        <EmptyState icon={UsersIcon} title="No alumni profiles" />
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map(p => (
            <div
              key={p.id}
              onClick={() => onEdit(p)}
              className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{p.user_name}</p>
                  <p className="text-xs text-slate-400">
                    {p.graduation_year}
                    {p.occupation ? "  ·  " + p.occupation : ""}
                    {p.employer ? " at " + p.employer : ""}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    {p.city}
                    {p.country ? ", " + p.country : ""}
                  </p>
                </div>
                <div className="flex gap-1 ml-4 flex-shrink-0" onClick={e => e.stopPropagation()}>
                  <button
                    onClick={() => onEdit(p)}
                    className="text-xs text-indigo-600 font-medium hover:text-indigo-800"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => { if (confirm("Delete this profile?")) onDelete(p.id); }}
                    className="text-xs text-red-500 font-medium hover:text-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function EventsTab({ events, onDelete }: { events: AlumniEvent[]; onDelete: (id: string) => void }) {
  return (
    <div className="space-y-2">
      {!events.length ? (
        <EmptyState icon={CalendarDaysIcon} title="No alumni events" />
      ) : (
        events.map(e => (
          <div
            key={e.id}
            className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="font-semibold text-slate-900 dark:text-white">{e.title}</p>
                <p className="text-xs text-slate-400">
                  {dayjs(e.event_date).format("MMM D, YYYY")}
                  {e.location ? "  ·  " + e.location : ""}
                  {e.fee_amount > 0 ? "  ·  $" + Number(e.fee_amount) : ""}
                </p>
              </div>
              <div className="flex gap-1 ml-4 flex-shrink-0">
                <span className="text-xs font-medium px-2 py-0.5 rounded bg-blue-100 text-blue-700">
                  {e.status_display}
                </span>
                <button
                  onClick={() => { if (confirm("Delete this event?")) onDelete(e.id); }}
                  className="text-xs text-red-500 font-medium hover:text-red-700 ml-2"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function DonationsTab({ donations, onDelete }: { donations: Donation[]; onDelete: (id: string) => void }) {
  return (
    <div className="space-y-2">
      {!donations.length ? (
        <EmptyState icon={CurrencyDollarIcon} title="No donations" />
      ) : (
        donations.map(d => (
          <div
            key={d.id}
            className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="font-semibold text-slate-900 dark:text-white">{d.alumni_name}</p>
                <p className="text-xs text-slate-400">
                  {d.fund_type_display}
                  {d.is_recurring ? "  ·  Recurring" : ""}
                </p>
              </div>
              <div className="flex flex-col items-end gap-1 ml-4 flex-shrink-0">
                <p className="text-lg font-bold text-green-600">
                  {"$" + Number(d.amount).toLocaleString()}
                </p>
                <button
                  onClick={() => { if (confirm("Delete this donation?")) onDelete(d.id); }}
                  className="text-xs text-red-500 font-medium hover:text-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

function ChaptersTab({
  chapters, onEdit, onDelete,
}: {
  chapters: Chapter[]; onEdit: (c: Chapter) => void; onDelete: (id: string) => void;
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {!chapters.length ? (
        <EmptyState icon={GlobeAltIcon} title="No chapters" />
      ) : (
        chapters.map(c => (
          <div
            key={c.id}
            onClick={() => onEdit(c)}
            className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{c.name}</p>
                <p className="text-xs text-slate-400">
                  {c.city}
                  {c.country ? ", " + c.country : ""}
                  {c.president_name ? "  ·  Head: " + c.president_name : ""}
                </p>
              </div>
              <div className="flex gap-1 ml-4 flex-shrink-0" onClick={e => e.stopPropagation()}>
                <span
                  className={
                    "text-xs font-medium px-2 py-0.5 rounded " +
                    (c.is_active
                      ? "bg-green-100 text-green-700"
                      : "bg-slate-100 text-slate-500")
                  }
                >
                  {c.is_active ? "Active" : "Inactive"}
                </span>
                <button
                  onClick={() => onEdit(c)}
                  className="text-xs text-indigo-600 font-medium hover:text-indigo-800 ml-2"
                >
                  Edit
                </button>
                <button
                  onClick={() => { if (confirm("Delete this chapter?")) onDelete(c.id); }}
                  className="text-xs text-red-500 font-medium hover:text-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

// ── Form Modals ────────────────────────────────────────────────────────────────

function ProfileFormModal({
  open, onClose, profile, onSaved,
}: {
  open: boolean; onClose: () => void; profile: Profile | null; onSaved: () => void;
}) {
  const [f, setF] = useState({
    user: profile?.user ?? "",
    graduation_year: profile?.graduation_year ?? 2026,
    occupation: profile?.occupation ?? "",
    employer: profile?.employer ?? "",
    city: profile?.city ?? "",
    country: profile?.country ?? "",
  });
  const isEdit = !!profile;
  const create = useMutation({
    mutationFn: (d: typeof f) => api.post("/alumni/profiles/", d),
    onSuccess: () => { toast.success("Profile created"); onSaved(); },
  });
  const update = useMutation({
    mutationFn: (d: typeof f) => api.patch("/alumni/profiles/" + profile!.id + "/", d),
    onSuccess: () => { toast.success("Profile updated"); onSaved(); },
  });
  const saving = create.isPending || update.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isEdit) update.mutate(f);
    else create.mutate(f);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Profile" : "Add Alumni Profile"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">User ID *</label>
            <input
              value={f.user} onChange={e => setF(p => ({ ...p, user: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
              placeholder="User UUID"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Graduation Year</label>
            <input
              type="number" min={1950} max={2030}
              value={f.graduation_year}
              onChange={e => setF(p => ({ ...p, graduation_year: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Occupation</label>
            <input
              value={f.occupation} onChange={e => setF(p => ({ ...p, occupation: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Employer</label>
            <input
              value={f.employer} onChange={e => setF(p => ({ ...p, employer: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">City</label>
            <input
              value={f.city} onChange={e => setF(p => ({ ...p, city: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Country</label>
            <input
              value={f.country} onChange={e => setF(p => ({ ...p, country: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>Cancel</Button>
          <Button type="submit" loading={saving}>{isEdit ? "Update" : "Create"} Profile</Button>
        </div>
      </form>
    </Modal>
  );
}

function AlumniEventFormModal({
  open, onClose, event, onSaved,
}: {
  open: boolean; onClose: () => void; event: AlumniEvent | null; onSaved: () => void;
}) {
  const [f, setF] = useState({
    title: event?.title ?? "",
    event_date: event?.event_date ?? dayjs().format("YYYY-MM-DDTHH:mm"),
    location: event?.location ?? "",
    fee_amount: event?.fee_amount ?? 0,
    status: event?.status ?? "draft",
  });
  const isEdit = !!event;
  const create = useMutation({
    mutationFn: (d: typeof f) => api.post("/alumni/events/", d),
    onSuccess: () => { toast.success("Event created"); onSaved(); },
  });
  const update = useMutation({
    mutationFn: (d: typeof f) => api.patch("/alumni/events/" + event!.id + "/", d),
    onSuccess: () => { toast.success("Event updated"); onSaved(); },
  });
  const saving = create.isPending || update.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.title.trim()) return toast.error("Title required");
    if (isEdit) update.mutate(f);
    else create.mutate(f);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Event" : "Add Event"}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Title *</label>
          <input
            value={f.title} onChange={e => setF(p => ({ ...p, title: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Date/Time</label>
            <input
              type="datetime-local"
              value={f.event_date}
              onChange={e => setF(p => ({ ...p, event_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Location</label>
            <input
              value={f.location} onChange={e => setF(p => ({ ...p, location: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Fee Amount</label>
            <input
              type="number" min={0}
              value={f.fee_amount}
              onChange={e => setF(p => ({ ...p, fee_amount: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Status</label>
            <select
              value={f.status}
              onChange={e => setF(p => ({ ...p, status: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            >
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>Cancel</Button>
          <Button type="submit" loading={saving}>{isEdit ? "Update" : "Create"} Event</Button>
        </div>
      </form>
    </Modal>
  );
}

function DonationFormModal({
  open, onClose, profiles, onSaved,
}: {
  open: boolean; onClose: () => void; profiles: Profile[]; onSaved: () => void;
}) {
  const [f, setF] = useState({ alumni: "", amount: 0, fund_type: "general", is_recurring: false });
  const create = useMutation({
    mutationFn: (d: typeof f) => api.post("/alumni/donations/", d),
    onSuccess: () => { toast.success("Donation recorded"); onSaved(); },
  });
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.alumni || f.amount <= 0) return toast.error("Select alumni and enter amount");
    create.mutate(f);
  };
  return (
    <Modal open={open} onClose={onClose} title="Record Donation">
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Alumni *</label>
            <select
              value={f.alumni}
              onChange={e => setF(p => ({ ...p, alumni: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            >
              <option value="">Select...</option>
              {profiles.map(p => (
                <option key={p.id} value={p.id}>{p.user_name} ({p.graduation_year})</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Fund Type</label>
            <select
              value={f.fund_type}
              onChange={e => setF(p => ({ ...p, fund_type: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            >
              <option value="general">General Fund</option>
              <option value="scholarship">Scholarship Fund</option>
              <option value="infrastructure">Infrastructure</option>
              <option value="sports">Sports Fund</option>
              <option value="library">Library Fund</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Amount *</label>
            <input
              type="number" min={0}
              value={f.amount}
              onChange={e => setF(p => ({ ...p, amount: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
          <div className="flex items-end pb-2">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={f.is_recurring}
                onChange={e => setF(p => ({ ...p, is_recurring: e.target.checked }))}
              />
              Recurring
            </label>
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={create.isPending}>Cancel</Button>
          <Button type="submit" loading={create.isPending}>Record Donation</Button>
        </div>
      </form>
    </Modal>
  );
}

function ChapterFormModal({
  open, onClose, chapter, onSaved,
}: {
  open: boolean; onClose: () => void; chapter: Chapter | null; onSaved: () => void;
}) {
  const [f, setF] = useState({
    name: chapter?.name ?? "",
    city: chapter?.city ?? "",
    country: chapter?.country ?? "",
  });
  const isEdit = !!chapter;
  const create = useMutation({
    mutationFn: (d: typeof f) => api.post("/alumni/chapters/", d),
    onSuccess: () => { toast.success("Chapter created"); onSaved(); },
  });
  const update = useMutation({
    mutationFn: (d: typeof f) => api.patch("/alumni/chapters/" + chapter!.id + "/", d),
    onSuccess: () => { toast.success("Chapter updated"); onSaved(); },
  });
  const saving = create.isPending || update.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Name required");
    if (isEdit) update.mutate(f);
    else create.mutate(f);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Chapter" : "Add Chapter"}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Name *</label>
          <input
            value={f.name} onChange={e => setF(p => ({ ...p, name: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">City</label>
            <input
              value={f.city} onChange={e => setF(p => ({ ...p, city: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Country</label>
            <input
              value={f.country} onChange={e => setF(p => ({ ...p, country: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 bg-white dark:bg-slate-800 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>Cancel</Button>
          <Button type="submit" loading={saving}>{isEdit ? "Update" : "Create"} Chapter</Button>
        </div>
      </form>
    </Modal>
  );
}

// ── Main Component ─────────────────────────────────────────────────────────────

export default function AlumniPage() {
  useTitle("Alumni Management");
  const qc = useQueryClient();
  const [tab, setTab] = useState<Tab>("profiles");
  const [search, setSearch] = useState("");

  const [showProfileForm, setShowProfileForm] = useState(false);
  const [editingProfile, setEditingProfile] = useState<Profile | null>(null);

  const [showEventForm, setShowEventForm] = useState(false);
  const [editingEvent, setEditingEvent] = useState<AlumniEvent | null>(null);

  const [showDonationForm, setShowDonationForm] = useState(false);

  const [showChapterForm, setShowChapterForm] = useState(false);
  const [editingChapter, setEditingChapter] = useState<Chapter | null>(null);

  const { data: profiles = [] } = useQuery({
    queryKey: ["alumni-profiles"],
    queryFn: async () => { const r = await api.get<{ results: Profile[] }>("/alumni/profiles/"); return r.results ?? []; },
  });
  const { data: events = [] } = useQuery({
    queryKey: ["alumni-events"],
    queryFn: async () => { const r = await api.get<{ results: AlumniEvent[] }>("/alumni/events/"); return r.results ?? []; },
  });
  const { data: donations = [] } = useQuery({
    queryKey: ["alumni-donations"],
    queryFn: async () => { const r = await api.get<{ results: Donation[] }>("/alumni/donations/"); return r.results ?? []; },
  });
  const { data: chapters = [] } = useQuery({
    queryKey: ["alumni-chapters"],
    queryFn: async () => { const r = await api.get<{ results: Chapter[] }>("/alumni/chapters/"); return r.results ?? []; },
  });

  const delProfile = useMutation({
    mutationFn: (id: string) => api.delete("/alumni/profiles/" + id + "/"),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["alumni-profiles"] }); toast.success("Deleted"); },
  });
  const delEvent = useMutation({
    mutationFn: (id: string) => api.delete("/alumni/events/" + id + "/"),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["alumni-events"] }); toast.success("Deleted"); },
  });
  const delDonation = useMutation({
    mutationFn: (id: string) => api.delete("/alumni/donations/" + id + "/"),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["alumni-donations"] }); toast.success("Deleted"); },
  });
  const delChapter = useMutation({
    mutationFn: (id: string) => api.delete("/alumni/chapters/" + id + "/"),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["alumni-chapters"] }); toast.success("Deleted"); },
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Alumni Management</h1>
          <p className="text-sm text-slate-500 mt-1">
            Manage alumni profiles, events, donations, and chapters
          </p>
        </div>
        <div className="flex gap-2">
          {tab === "profiles" && (
            <Button onClick={() => { setEditingProfile(null); setShowProfileForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" />
              Add Profile
            </Button>
          )}
          {tab === "events" && (
            <Button onClick={() => { setEditingEvent(null); setShowEventForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" />
              Add Event
            </Button>
          )}
          {tab === "donations" && (
            <Button onClick={() => setShowDonationForm(true)}>
              <PlusIcon className="h-4 w-4 mr-1.5" />
              Record Donation
            </Button>
          )}
          {tab === "chapters" && (
            <Button onClick={() => { setEditingChapter(null); setShowChapterForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" />
              Add Chapter
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
        {TABS.map(t => {
          const I = t.icon;
          return (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={
                "inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap " +
                (tab === t.key
                  ? "bg-white dark:bg-slate-700 shadow-sm"
                  : "text-slate-600 hover:text-slate-900")
              }
            >
              <I className="h-4 w-4" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {tab === "profiles" && (
        <ProfilesTab
          profiles={profiles}
          search={search}
          setSearch={setSearch}
          onEdit={(p) => { setEditingProfile(p); setShowProfileForm(true); }}
          onDelete={(id) => delProfile.mutate(id)}
        />
      )}
      {tab === "events" && (
        <EventsTab
          events={events}
          onDelete={(id) => delEvent.mutate(id)}
        />
      )}
      {tab === "donations" && (
        <DonationsTab
          donations={donations}
          onDelete={(id) => delDonation.mutate(id)}
        />
      )}
      {tab === "chapters" && (
        <ChaptersTab
          chapters={chapters}
          onEdit={(c) => { setEditingChapter(c); setShowChapterForm(true); }}
          onDelete={(id) => delChapter.mutate(id)}
        />
      )}

      {/* Form Modals */}
      <ProfileFormModal
        open={showProfileForm}
        onClose={() => { setShowProfileForm(false); setEditingProfile(null); }}
        profile={editingProfile}
        onSaved={() => {
          setShowProfileForm(false);
          setEditingProfile(null);
          qc.invalidateQueries({ queryKey: ["alumni-profiles"] });
        }}
      />
      <AlumniEventFormModal
        open={showEventForm}
        onClose={() => { setShowEventForm(false); setEditingEvent(null); }}
        event={editingEvent}
        onSaved={() => {
          setShowEventForm(false);
          setEditingEvent(null);
          qc.invalidateQueries({ queryKey: ["alumni-events"] });
        }}
      />
      <DonationFormModal
        open={showDonationForm}
        onClose={() => setShowDonationForm(false)}
        profiles={profiles}
        onSaved={() => {
          setShowDonationForm(false);
          qc.invalidateQueries({ queryKey: ["alumni-donations"] });
        }}
      />
      <ChapterFormModal
        open={showChapterForm}
        onClose={() => { setShowChapterForm(false); setEditingChapter(null); }}
        chapter={editingChapter}
        onSaved={() => {
          setShowChapterForm(false);
          setEditingChapter(null);
          qc.invalidateQueries({ queryKey: ["alumni-chapters"] });
        }}
      />
    </div>
  );
}
