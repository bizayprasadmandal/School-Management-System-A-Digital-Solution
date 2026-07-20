/**
 * Hostel / Accommodation Management — Admin page for hostels, rooms,
 * student allocations, fee structures, and visitor logs.
 */
import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  PlusIcon, MagnifyingGlassIcon,
  BuildingOffice2Icon, KeyIcon, UsersIcon,
  CurrencyDollarIcon, ClipboardDocumentListIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

// ─── Types ───────────────────────────────────────────────────────────────────

interface Hostel {
  id: string;
  name: string;
  code: string;
  gender: string;
  gender_display: string;
  status: string;
  status_display: string;
  warden_name: string | null;
  assistant_warden_name: string | null;
  address: string;
  phone: string;
  total_floors: number;
  rules: string;
  amenities: string;
  notes: string;
  total_rooms: number;
  total_beds: number;
  occupied_beds: number;
  available_beds: number;
}

interface HostelRoom {
  id: string;
  hostel: string;
  hostel_name: string;
  room_number: string;
  floor: number;
  room_type: string;
  room_type_display: string;
  capacity: number;
  is_furnished: boolean;
  has_ac: boolean;
  has_attached_bathroom: boolean;
  monthly_fee: number;
  occupied_beds: number;
  available_beds: number;
  is_active: boolean;
}

interface HostelAllocation {
  id: string;
  student: string;
  student_name: string;
  room: string;
  hostel_name: string;
  room_number: string;
  status: string;
  check_in_date: string;
  check_out_date: string | null;
  fee_amount: number;
  is_paid: boolean;
  notes: string;
  allocated_by_name: string | null;
}

interface HostelFee {
  id: string;
  name: string;
  hostel: string;
  hostel_name: string;
  room_type: string;
  amount: number;
  billing_cycle: string;
  billing_cycle_display: string;
  includes_meals: boolean;
  includes_laundry: boolean;
  includes_wifi: boolean;
  is_active: boolean;
}

interface HostelVisitor {
  id: string;
  hostel: string;
  hostel_name: string;
  visitor_name: string;
  phone: string;
  id_proof: string;
  student_visited: string;
  student_name: string;
  purpose: string;
  in_time: string;
  out_time: string | null;
  relationship: string;
  checked_in_by_name: string | null;
}

interface Student {
  id: string;
  user_name: string;
  admission_number: string;
}

// ─── Colors ──────────────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  inactive: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  under_maintenance: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  checked_out: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  transferred: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
};

// ─── Tabs ────────────────────────────────────────────────────────────────────

type TabType = "hostels" | "rooms" | "allocations" | "fees" | "visitors";
const TABS: { key: TabType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "hostels", label: "Hostels", icon: BuildingOffice2Icon },
  { key: "rooms", label: "Rooms", icon: KeyIcon },
  { key: "allocations", label: "Allocations", icon: UsersIcon },
  { key: "fees", label: "Fee Structures", icon: CurrencyDollarIcon },
  { key: "visitors", label: "Visitor Log", icon: ClipboardDocumentListIcon },
];

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function HostelPage() {
  useTitle("Hostel Management");
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>("hostels");
  const [search, setSearch] = useState("");

  // Modals
  const [showHostelForm, setShowHostelForm] = useState(false);
  const [editingHostel, setEditingHostel] = useState<Hostel | null>(null);
  const [showRoomForm, setShowRoomForm] = useState(false);
  const [editingRoom, setEditingRoom] = useState<HostelRoom | null>(null);
  const [showAllocationForm, setShowAllocationForm] = useState(false);
  const [showFeeForm, setShowFeeForm] = useState(false);
  const [editingFee, setEditingFee] = useState<HostelFee | null>(null);
  const [showVisitorForm, setShowVisitorForm] = useState(false);

  // ── Data ─────────────────────────────────────────────────────────────────

  const { data: hostels = [], isLoading: hLoading } = useQuery({
    queryKey: ["hostel-hostels"],
    queryFn: async () => { const r = await api.get<{ results: Hostel[] }>("/hostel/hostels/"); return r.results ?? []; },
  });

  const { data: rooms = [], isLoading: rLoading } = useQuery({
    queryKey: ["hostel-rooms"],
    queryFn: async () => { const r = await api.get<{ results: HostelRoom[] }>("/hostel/rooms/"); return r.results ?? []; },
  });

  const { data: allocations = [], isLoading: aLoading } = useQuery({
    queryKey: ["hostel-allocations"],
    queryFn: async () => { const r = await api.get<{ results: HostelAllocation[] }>("/hostel/allocations/"); return r.results ?? []; },
  });

  const { data: fees = [], isLoading: fLoading } = useQuery({
    queryKey: ["hostel-fees"],
    queryFn: async () => { const r = await api.get<{ results: HostelFee[] }>("/hostel/fees/"); return r.results ?? []; },
  });

  const { data: visitors = [], isLoading: vLoading } = useQuery({
    queryKey: ["hostel-visitors"],
    queryFn: async () => { const r = await api.get<{ results: HostelVisitor[] }>("/hostel/visitors/"); return r.results ?? []; },
  });

  const { data: students = [] } = useQuery({
    queryKey: ["students-short"],
    queryFn: async () => { const r = await api.get<{ results: Student[] }>("/students/"); return r.results ?? []; },
  });

  // ── Mutations ───────────────────────────────────────────────────────────

  const deleteHostel = useMutation({
    mutationFn: (id: string) => api.delete(`/hostel/hostels/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["hostel-hostels"] }); toast.success("Hostel deleted"); },
  });

  const deleteRoom = useMutation({
    mutationFn: (id: string) => api.delete(`/hostel/rooms/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["hostel-rooms"] }); toast.success("Room deleted"); },
  });

  const checkoutAllocation = useMutation({
    mutationFn: ({ id, notes }: { id: string; notes: string }) => api.post(`/hostel/allocations/${id}/checkout/`, { notes }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["hostel-allocations"] }); toast.success("Student checked out"); },
  });

  const checkoutVisitor = useMutation({
    mutationFn: (id: string) => api.post(`/hostel/visitors/${id}/checkout/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["hostel-visitors"] }); toast.success("Visitor checked out"); },
  });

  // ── Filtering ───────────────────────────────────────────────────────────

  const filteredHostels = useMemo(() => {
    if (!search.trim()) return hostels;
    const q = search.toLowerCase();
    return hostels.filter((h) => h.name.toLowerCase().includes(q) || h.code.toLowerCase().includes(q));
  }, [hostels, search]);

  const filteredRooms = useMemo(() => {
    if (!search.trim()) return rooms;
    const q = search.toLowerCase();
    return rooms.filter((r) => r.room_number.toLowerCase().includes(q) || r.hostel_name.toLowerCase().includes(q));
  }, [rooms, search]);

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Hostel & Accommodation</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage hostels, rooms, student allocations, and visitor logs</p>
        </div>
        <div className="flex gap-2">
          {activeTab === "hostels" && (
            <Button onClick={() => { setEditingHostel(null); setShowHostelForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Hostel
            </Button>
          )}
          {activeTab === "rooms" && (
            <Button onClick={() => { setEditingRoom(null); setShowRoomForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Room
            </Button>
          )}
          {activeTab === "allocations" && (
            <Button onClick={() => setShowAllocationForm(true)}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Allocate Room
            </Button>
          )}
          {activeTab === "fees" && (
            <Button onClick={() => { setEditingFee(null); setShowFeeForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Fee Structure
            </Button>
          )}
          {activeTab === "visitors" && (
            <Button onClick={() => setShowVisitorForm(true)}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Log Visitor
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button key={tab.key} onClick={() => setActiveTab(tab.key)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.key
                  ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
              }`}
            >
              <Icon className="h-4 w-4" /> {tab.label}
            </button>
          );
        })}
      </div>

      {/* Search */}
      {(activeTab === "hostels" || activeTab === "rooms") && (
        <div className="relative max-w-sm">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm dark:text-slate-200"
            placeholder={activeTab === "hostels" ? "Search hostels..." : "Search rooms..."} />
        </div>
      )}

      {/* ── Hostels Tab ──────────────────────────────────────────────────── */}
      {activeTab === "hostels" && (
        <>
          {hLoading ? (<div className="grid gap-4 sm:grid-cols-2">{[1,2].map(i => <div key={i} className="h-36 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : filteredHostels.length === 0 ? (
            <EmptyState icon={BuildingOffice2Icon} title="No hostels" description="Add your first hostel" />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-2">
              {filteredHostels.map((h) => (
                <div key={h.id}
                  onClick={() => { setEditingHostel(h); setShowHostelForm(true); }}
                  className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{h.name}</p>
                      <p className="text-xs text-slate-400">{h.code && `${h.code} · `}{h.gender_display}</p>
                    </div>
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[h.status]}`}>{h.status_display}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-3 mb-3">
                    <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-2 text-center">
                      <p className="text-lg font-bold text-indigo-600 dark:text-indigo-400">{h.total_beds}</p>
                      <p className="text-xs text-slate-500">Total Beds</p>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-2 text-center">
                      <p className="text-lg font-bold text-green-600 dark:text-green-400">{h.available_beds}</p>
                      <p className="text-xs text-slate-500">Available</p>
                    </div>
                    <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-2 text-center">
                      <p className="text-lg font-bold text-amber-600 dark:text-amber-400">{h.occupied_beds}</p>
                      <p className="text-xs text-slate-500">Occupied</p>
                    </div>
                  </div>
                  <div className="text-xs text-slate-400 space-y-0.5 mb-2">
                    {h.warden_name && <p>Warden: {h.warden_name}</p>}
                    {h.phone && <p>📞 {h.phone}</p>}
                    {h.amenities && <p>🎯 {h.amenities}</p>}
                  </div>
                  <div className="flex gap-2 pt-2 border-t border-slate-100 dark:border-slate-700" onClick={e => e.stopPropagation()}>
                    <button onClick={() => { setEditingHostel(h); setShowHostelForm(true); }}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
                    <button onClick={() => { if (confirm("Delete hostel?")) deleteHostel.mutate(h.id); }}
                      className="text-xs text-red-500 hover:text-red-600 font-medium">Delete</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Rooms Tab ────────────────────────────────────────────────────── */}
      {activeTab === "rooms" && (
        <>
          {rLoading ? (<div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{[1,2,3].map(i => <div key={i} className="h-24 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : filteredRooms.length === 0 ? (
            <EmptyState icon={KeyIcon} title="No rooms" description="Add rooms to a hostel" />
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {filteredRooms.map((r) => (
                <div key={r.id}
                  onClick={() => { setEditingRoom(r); setShowRoomForm(true); }}
                  className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{r.room_number}</p>
                      <p className="text-xs text-slate-400">{r.hostel_name} · Floor {r.floor} · {r.room_type_display}</p>
                    </div>
                    {!r.is_active && <span className="text-xs text-slate-400">Inactive</span>}
                  </div>
                  <div className="flex items-center gap-4 text-xs text-slate-500 mb-2">
                    <span>🛏️ {r.occupied_beds}/{r.capacity} occupied</span>
                    {r.has_ac && <span>❄️ AC</span>}
                    {r.is_furnished && <span>🪑 Furnished</span>}
                  </div>
                  <div className="text-xs text-slate-400">
                    {r.monthly_fee > 0 && <p>💰 ${Number(r.monthly_fee).toLocaleString()}/mo</p>}
                  </div>
                  <div className="flex gap-2 mt-2 pt-2 border-t border-slate-100 dark:border-slate-700" onClick={e => e.stopPropagation()}>
                    <button onClick={() => { setEditingRoom(r); setShowRoomForm(true); }}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
                    <button onClick={() => { if (confirm("Delete room?")) deleteRoom.mutate(r.id); }}
                      className="text-xs text-red-500 hover:text-red-600 font-medium">Delete</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Allocations Tab ──────────────────────────────────────────────── */}
      {activeTab === "allocations" && (
        <>
          {aLoading ? (<div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : allocations.length === 0 ? (
            <EmptyState icon={UsersIcon} title="No allocations" description="Allocate rooms to students" />
          ) : (
            <div className="space-y-3">
              {allocations.map((a) => (
                <div key={a.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-semibold text-slate-900 dark:text-white">{a.student_name}</p>
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[a.status]}`}>{a.status}</span>
                        {a.is_paid ? (
                          <span className="text-xs text-green-600 font-medium">Paid</span>
                        ) : (
                          <span className="text-xs text-amber-600 font-medium">Unpaid</span>
                        )}
                      </div>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        🏠 {a.hostel_name} · Room {a.room_number}
                      </p>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Check-in: {dayjs(a.check_in_date).format("MMM D, YYYY")}
                        {a.check_out_date && ` · Check-out: ${dayjs(a.check_out_date).format("MMM D, YYYY")}`}
                        {a.fee_amount > 0 && ` · Fee: $${Number(a.fee_amount).toLocaleString()}`}
                      </p>
                    </div>
                    <div className="flex gap-2 ml-4">
                      {a.status === "active" && (
                        <Button size="sm" variant="secondary" onClick={() => checkoutAllocation.mutate({ id: a.id, notes: "" })}>
                          Check Out
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Fees Tab ──────────────────────────────────────────────────────── */}
      {activeTab === "fees" && (
        <>
          {fLoading ? (<div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : fees.length === 0 ? (
            <EmptyState icon={CurrencyDollarIcon} title="No fee structures" description="Create fee structures for hostels" />
          ) : (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {fees.map((f) => (
                <div key={f.id}
                  onClick={() => { setEditingFee(f); setShowFeeForm(true); }}
                  className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{f.name}</p>
                      <p className="text-xs text-slate-400">{f.hostel_name}</p>
                    </div>
                    <span className={`text-xs font-medium px-2 py-0.5 rounded ${f.is_active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>
                      {f.is_active ? "Active" : "Inactive"}
                    </span>
                  </div>
                  <p className="text-lg font-bold text-slate-800 dark:text-white">${Number(f.amount).toLocaleString()}<span className="text-sm font-normal text-slate-400">/{f.billing_cycle_display?.toLowerCase()}</span></p>
                  <div className="text-xs text-slate-400 mt-2 space-y-0.5">
                    {f.room_type && <p>Room type: {f.room_type}</p>}
                    <div className="flex gap-2 mt-1">
                      {f.includes_meals && <span className="text-green-600">🍽️ Meals</span>}
                      {f.includes_laundry && <span className="text-blue-600">👕 Laundry</span>}
                      {f.includes_wifi && <span className="text-indigo-600">📶 WiFi</span>}
                    </div>
                  </div>
                  <div className="flex gap-2 mt-3 pt-2 border-t border-slate-100 dark:border-slate-700" onClick={e => e.stopPropagation()}>
                    <button onClick={() => { setEditingFee(f); setShowFeeForm(true); }}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Visitors Tab ──────────────────────────────────────────────────── */}
      {activeTab === "visitors" && (
        <>
          {vLoading ? (<div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : visitors.length === 0 ? (
            <EmptyState icon={ClipboardDocumentListIcon} title="No visitors logged" description="Log your first visitor" />
          ) : (
            <div className="space-y-2">
              {visitors.map((v) => (
                <div key={v.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-semibold text-slate-900 dark:text-white">{v.visitor_name}</p>
                        {v.out_time ? (
                          <span className="text-xs text-green-600 font-medium">✓ Checked out</span>
                        ) : (
                          <span className="text-xs text-amber-600 font-medium">● In hostel</span>
                        )}
                      </div>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        Visiting {v.student_name} · {v.hostel_name}
                        {v.purpose && ` · ${v.purpose}`}
                      </p>
                      <p className="text-xs text-slate-400 mt-0.5">
                        In: {dayjs(v.in_time).format("MMM D, h:mm A")}
                        {v.out_time && ` · Out: ${dayjs(v.out_time).format("MMM D, h:mm A")}`}
                        {v.relationship && ` · ${v.relationship}`}
                      </p>
                    </div>
                    <div className="flex gap-2 ml-4">
                      {!v.out_time && (
                        <Button size="sm" variant="secondary" onClick={() => checkoutVisitor.mutate(v.id)} loading={checkoutVisitor.isPending}>
                          Check Out
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Form Modals ───────────────────────────────────────────────────── */}
      <HostelFormModal open={showHostelForm} onClose={() => { setShowHostelForm(false); setEditingHostel(null); }}
        hostel={editingHostel}
        onSaved={() => { setShowHostelForm(false); setEditingHostel(null); qc.invalidateQueries({ queryKey: ["hostel-hostels"] }); }} />

      <RoomFormModal open={showRoomForm} onClose={() => { setShowRoomForm(false); setEditingRoom(null); }}
        room={editingRoom} hostels={hostels}
        onSaved={() => { setShowRoomForm(false); setEditingRoom(null); qc.invalidateQueries({ queryKey: ["hostel-rooms"] }); qc.invalidateQueries({ queryKey: ["hostel-hostels"] }); }} />

      <AllocationFormModal open={showAllocationForm} onClose={() => setShowAllocationForm(false)}
        students={students} rooms={rooms.filter(r => r.is_active && r.available_beds > 0)}
        onSaved={() => { setShowAllocationForm(false); qc.invalidateQueries({ queryKey: ["hostel-allocations"] }); qc.invalidateQueries({ queryKey: ["hostel-rooms"] }); qc.invalidateQueries({ queryKey: ["hostel-hostels"] }); }} />

      <FeeFormModal open={showFeeForm} onClose={() => { setShowFeeForm(false); setEditingFee(null); }}
        fee={editingFee} hostels={hostels}
        onSaved={() => { setShowFeeForm(false); setEditingFee(null); qc.invalidateQueries({ queryKey: ["hostel-fees"] }); }} />

      <VisitorFormModal open={showVisitorForm} onClose={() => setShowVisitorForm(false)}
        hostels={hostels} students={students}
        onSaved={() => { setShowVisitorForm(false); qc.invalidateQueries({ queryKey: ["hostel-visitors"] }); }} />
    </div>
  );
}

// ─── Sub-components ──────────────────────────────────────────────────────────

function HostelFormModal({ open, onClose, hostel, onSaved }: {
  open: boolean; onClose: () => void; hostel?: Hostel | null; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: hostel?.name ?? "", code: hostel?.code ?? "", gender: hostel?.gender ?? "male",
    address: hostel?.address ?? "", phone: hostel?.phone ?? "",
    total_floors: hostel?.total_floors ?? 1, rules: hostel?.rules ?? "",
    amenities: hostel?.amenities ?? "", notes: hostel?.notes ?? "",
  });
  const isEdit = !!hostel;
  const createMut = useMutation({
    mutationFn: (d: typeof form) => api.post("/hostel/hostels/", d),
    onSuccess: () => { toast.success("Hostel created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (d: typeof form) => api.patch(`/hostel/hostels/${hostel!.id}/`, d),
    onSuccess: () => { toast.success("Hostel updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return toast.error("Hostel name is required");
    if (isEdit) updateMut.mutate(form); else createMut.mutate(form);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Hostel" : "Add Hostel"}>
      <form onSubmit={handleSubmit} className="space-y-4 max-h-[60vh] overflow-y-auto">
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Name *</label>
            <input value={form.name} onChange={(e) => setForm(p => ({ ...p, name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required /></div>
          <div><label className="block text-sm font-medium mb-1">Code</label>
            <input value={form.code} onChange={(e) => setForm(p => ({ ...p, code: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200 font-mono" /></div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Gender</label>
            <select value={form.gender} onChange={(e) => setForm(p => ({ ...p, gender: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="male">Male Only</option><option value="female">Female Only</option><option value="coed">Co-Educational</option>
            </select></div>
          <div><label className="block text-sm font-medium mb-1">Floors</label>
            <input type="number" min={1} value={form.total_floors} onChange={(e) => setForm(p => ({ ...p, total_floors: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Phone</label>
            <input value={form.phone} onChange={(e) => setForm(p => ({ ...p, phone: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
          <div><label className="block text-sm font-medium mb-1">Amenities</label>
            <input value={form.amenities} onChange={(e) => setForm(p => ({ ...p, amenities: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" placeholder="wifi, laundry, gym" /></div>
        </div>
        <div><label className="block text-sm font-medium mb-1">Address</label>
          <textarea value={form.address} onChange={(e) => setForm(p => ({ ...p, address: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
        <div><label className="block text-sm font-medium mb-1">Rules</label>
          <textarea value={form.rules} onChange={(e) => setForm(p => ({ ...p, rules: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Hostel</Button>
        </div>
      </form>
    </Modal>
  );
}

function RoomFormModal({ open, onClose, room, hostels, onSaved }: {
  open: boolean; onClose: () => void; room?: HostelRoom | null;
  hostels: Hostel[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    hostel: room?.hostel ?? "", room_number: room?.room_number ?? "",
    floor: room?.floor ?? 1, room_type: room?.room_type ?? "double",
    capacity: room?.capacity ?? 2, monthly_fee: room?.monthly_fee ?? 0,
    is_furnished: room?.is_furnished ?? true, has_ac: room?.has_ac ?? false,
    has_attached_bathroom: room?.has_attached_bathroom ?? true,
  });
  const isEdit = !!room;
  const createMut = useMutation({
    mutationFn: (d: typeof form) => api.post("/hostel/rooms/", d),
    onSuccess: () => { toast.success("Room created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (d: typeof form) => api.patch(`/hostel/rooms/${room!.id}/`, d),
    onSuccess: () => { toast.success("Room updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.room_number.trim()) return toast.error("Room number is required");
    if (isEdit) updateMut.mutate(form); else createMut.mutate(form);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Room" : "Add Room"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Hostel *</label>
            <select value={form.hostel} onChange={(e) => setForm(p => ({ ...p, hostel: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required>
              <option value="">Select...</option>
              {hostels.map((h) => <option key={h.id} value={h.id}>{h.name}</option>)}
            </select></div>
          <div><label className="block text-sm font-medium mb-1">Room # *</label>
            <input value={form.room_number} onChange={(e) => setForm(p => ({ ...p, room_number: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required /></div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div><label className="block text-sm font-medium mb-1">Floor</label>
            <input type="number" min={0} value={form.floor} onChange={(e) => setForm(p => ({ ...p, floor: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
          <div><label className="block text-sm font-medium mb-1">Type</label>
            <select value={form.room_type} onChange={(e) => setForm(p => ({ ...p, room_type: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="single">Single</option><option value="double">Double</option>
              <option value="triple">Triple</option><option value="dormitory">Dormitory</option>
            </select></div>
          <div><label className="block text-sm font-medium mb-1">Capacity</label>
            <input type="number" min={1} value={form.capacity} onChange={(e) => setForm(p => ({ ...p, capacity: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Monthly Fee</label>
            <input type="number" min={0} value={form.monthly_fee} onChange={(e) => setForm(p => ({ ...p, monthly_fee: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
          <div className="flex items-end gap-4 pb-2">
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.is_furnished} onChange={(e) => setForm(p => ({ ...p, is_furnished: e.target.checked }))} /> Furnished</label>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={form.has_ac} onChange={(e) => setForm(p => ({ ...p, has_ac: e.target.checked }))} /> AC</label>
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Room</Button>
        </div>
      </form>
    </Modal>
  );
}

function AllocationFormModal({ open, onClose, students, rooms, onSaved }: {
  open: boolean; onClose: () => void; students: Student[];
  rooms: HostelRoom[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    student: "", room: "", fee_amount: 0,
    check_in_date: dayjs().format("YYYY-MM-DD"), notes: "",
  });
  const createMut = useMutation({
    mutationFn: (d: typeof form) => api.post("/hostel/allocations/", d),
    onSuccess: () => { toast.success("Room allocated"); onSaved(); },
  });
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.student || !form.room) return toast.error("Select student and room");
    createMut.mutate(form);
  };
  return (
    <Modal open={open} onClose={onClose} title="Allocate Room">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Student *</label>
            <select value={form.student} onChange={(e) => setForm(p => ({ ...p, student: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required>
              <option value="">Select...</option>
              {students.map((s) => <option key={s.id} value={s.id}>{s.user_name}</option>)}
            </select></div>
          <div><label className="block text-sm font-medium mb-1">Room *</label>
            <select value={form.room} onChange={(e) => setForm(p => ({ ...p, room: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required>
              <option value="">Select...</option>
              {rooms.map((r) => <option key={r.id} value={r.id}>{r.hostel_name} - {r.room_number} ({r.available_beds} free)</option>)}
            </select></div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Check-in Date</label>
            <input type="date" value={form.check_in_date} onChange={(e) => setForm(p => ({ ...p, check_in_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
          <div><label className="block text-sm font-medium mb-1">Fee Amount</label>
            <input type="number" min={0} value={form.fee_amount} onChange={(e) => setForm(p => ({ ...p, fee_amount: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={createMut.isPending}>Cancel</Button>
          <Button type="submit" loading={createMut.isPending}>Allocate Room</Button>
        </div>
      </form>
    </Modal>
  );
}

function FeeFormModal({ open, onClose, fee, hostels, onSaved }: {
  open: boolean; onClose: () => void; fee?: HostelFee | null;
  hostels: Hostel[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: fee?.name ?? "", hostel: fee?.hostel ?? "",
    room_type: fee?.room_type ?? "", amount: fee?.amount ?? 0,
    billing_cycle: fee?.billing_cycle ?? "monthly",
    includes_meals: fee?.includes_meals ?? false,
    includes_laundry: fee?.includes_laundry ?? false,
    includes_wifi: fee?.includes_wifi ?? false,
  });
  const isEdit = !!fee;
  const createMut = useMutation({
    mutationFn: (d: typeof form) => api.post("/hostel/fees/", d),
    onSuccess: () => { toast.success("Fee structure created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (d: typeof form) => api.patch(`/hostel/fees/${fee!.id}/`, d),
    onSuccess: () => { toast.success("Fee structure updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return toast.error("Name is required");
    if (isEdit) updateMut.mutate(form); else createMut.mutate(form);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Fee Structure" : "Add Fee Structure"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Name *</label>
            <input value={form.name} onChange={(e) => setForm(p => ({ ...p, name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required /></div>
          <div><label className="block text-sm font-medium mb-1">Hostel</label>
            <select value={form.hostel} onChange={(e) => setForm(p => ({ ...p, hostel: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">All</option>
              {hostels.map((h) => <option key={h.id} value={h.id}>{h.name}</option>)}
            </select></div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Amount *</label>
            <input type="number" min={0} value={form.amount} onChange={(e) => setForm(p => ({ ...p, amount: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required /></div>
          <div><label className="block text-sm font-medium mb-1">Billing Cycle</label>
            <select value={form.billing_cycle} onChange={(e) => setForm(p => ({ ...p, billing_cycle: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="monthly">Monthly</option><option value="quarterly">Quarterly</option>
              <option value="semi_annual">Semi-Annual</option><option value="annual">Annual</option>
            </select></div>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <label className="flex items-center gap-2"><input type="checkbox" checked={form.includes_meals} onChange={(e) => setForm(p => ({ ...p, includes_meals: e.target.checked }))} /> Includes Meals</label>
          <label className="flex items-center gap-2"><input type="checkbox" checked={form.includes_laundry} onChange={(e) => setForm(p => ({ ...p, includes_laundry: e.target.checked }))} /> Laundry</label>
          <label className="flex items-center gap-2"><input type="checkbox" checked={form.includes_wifi} onChange={(e) => setForm(p => ({ ...p, includes_wifi: e.target.checked }))} /> WiFi</label>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Fee Structure</Button>
        </div>
      </form>
    </Modal>
  );
}

function VisitorFormModal({ open, onClose, hostels, students, onSaved }: {
  open: boolean; onClose: () => void; hostels: Hostel[]; students: Student[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    hostel: "", visitor_name: "", phone: "", id_proof: "",
    student_visited: "", purpose: "", relationship: "",
    in_time: dayjs().format("YYYY-MM-DDTHH:mm"),
  });
  const createMut = useMutation({
    mutationFn: (d: typeof form) => api.post("/hostel/visitors/", d),
    onSuccess: () => { toast.success("Visitor logged"); onSaved(); },
  });
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.visitor_name.trim() || !form.student_visited) return toast.error("Visitor name and student are required");
    createMut.mutate(form);
  };
  return (
    <Modal open={open} onClose={onClose} title="Log Visitor">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Visitor Name *</label>
            <input value={form.visitor_name} onChange={(e) => setForm(p => ({ ...p, visitor_name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required /></div>
          <div><label className="block text-sm font-medium mb-1">Phone</label>
            <input value={form.phone} onChange={(e) => setForm(p => ({ ...p, phone: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Hostel</label>
            <select value={form.hostel} onChange={(e) => setForm(p => ({ ...p, hostel: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">Select...</option>
              {hostels.map((h) => <option key={h.id} value={h.id}>{h.name}</option>)}
            </select></div>
          <div><label className="block text-sm font-medium mb-1">Student *</label>
            <select value={form.student_visited} onChange={(e) => setForm(p => ({ ...p, student_visited: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required>
              <option value="">Select...</option>
              {students.map((s) => <option key={s.id} value={s.id}>{s.user_name}</option>)}
            </select></div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div><label className="block text-sm font-medium mb-1">Purpose</label>
            <input value={form.purpose} onChange={(e) => setForm(p => ({ ...p, purpose: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
          <div><label className="block text-sm font-medium mb-1">Relationship</label>
            <input value={form.relationship} onChange={(e) => setForm(p => ({ ...p, relationship: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
        </div>
        <div><label className="block text-sm font-medium mb-1">In Time</label>
          <input type="datetime-local" value={form.in_time} onChange={(e) => setForm(p => ({ ...p, in_time: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" /></div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={createMut.isPending}>Cancel</Button>
          <Button type="submit" loading={createMut.isPending}>Log Visitor</Button>
        </div>
      </form>
    </Modal>
  );
}
