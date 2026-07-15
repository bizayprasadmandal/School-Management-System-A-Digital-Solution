/**
 * Transportation Management — Admin page for vehicles, routes, student
 * assignments, and vehicle maintenance tracking.
 */
import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  PlusIcon, MagnifyingGlassIcon,
  TruckIcon, MapPinIcon, UsersIcon, WrenchScrewdriverIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Badge } from "../../components/common";
import { useTitle } from "../../hooks";

// ─── Types ───────────────────────────────────────────────────────────────────

interface Vehicle {
  id: string;
  plate_number: string;
  vehicle_type: string;
  vehicle_type_display: string;
  model_name: string;
  year: number | null;
  capacity: number;
  color: string;
  chassis_number: string;
  engine_number: string;
  status: string;
  status_display: string;
  insurance_number: string;
  insurance_expiry: string | null;
  fitness_expiry: string | null;
  notes: string;
  is_active: boolean;
  route_count: number;
  maintenance_count: number;
}

interface Driver {
  id: string;
  full_name: string;
  phone_number: string;
  email: string;
  license_number: string;
  license_expiry: string | null;
  status: string;
  status_display: string;
  employee_name: string | null;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  notes: string;
}

interface RouteStop {
  id: string;
  name: string;
  address: string;
  stop_order: number;
  stop_type: string;
  stop_type_display: string;
  pickup_time: string | null;
  dropoff_time: string | null;
}

interface Route {
  id: string;
  name: string;
  description: string;
  vehicle: string | null;
  vehicle_plate: string | null;
  driver: string | null;
  driver_name: string | null;
  origin: string;
  destination: string;
  estimated_duration_minutes: number;
  operating_days: string;
  is_active: boolean;
  stops: RouteStop[];
  student_count: number;
}

interface StudentRoute {
  id: string;
  route: string;
  route_name: string;
  student: string;
  student_name: string;
  pickup_stop: string | null;
  pickup_stop_name: string | null;
  dropoff_stop: string | null;
  dropoff_stop_name: string | null;
  service_type: string;
  fee_amount: number;
  is_active: boolean;
}

interface MaintenanceRecord {
  id: string;
  vehicle: string;
  vehicle_plate: string;
  maintenance_type: string;
  maintenance_type_display: string;
  status: string;
  status_display: string;
  scheduled_date: string;
  completed_date: string | null;
  cost: number;
  vendor_name: string;
  invoice_number: string;
  description: string;
  notes: string;
  performed_by_name: string | null;
  next_service_date: string | null;
}

interface Student {
  id: string;
  user_name: string;
  admission_number: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const VEHICLE_TYPE_LABELS: Record<string, string> = {
  bus: "Bus", mini_bus: "Mini Bus", van: "Van", suv: "SUV", sedan: "Sedan", other: "Other",
};

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  in_maintenance: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  retired: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  out_of_service: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  pending: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300",
  approved: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  rejected: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  scheduled: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  in_progress: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  cancelled: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  on_leave: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  inactive: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
};

const MAINTENANCE_TYPE_LABELS: Record<string, string> = {
  routine: "Routine Service",
  repair: "Repair",
  inspection: "Inspection",
  tire: "Tire Change",
  engine: "Engine Service",
  body: "Body Work",
  other: "Other",
};

// ─── Tabs ────────────────────────────────────────────────────────────────────

type TabType = "vehicles" | "drivers" | "routes" | "assignments" | "maintenance";
const TABS: { key: TabType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "vehicles", label: "Vehicles", icon: TruckIcon },
  { key: "drivers", label: "Drivers", icon: UsersIcon },
  { key: "routes", label: "Routes", icon: MapPinIcon },
  { key: "assignments", label: "Assignments", icon: UsersIcon },
  { key: "maintenance", label: "Maintenance", icon: WrenchScrewdriverIcon },
];

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function TransportationPage() {
  useTitle("Transportation Management");
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>("vehicles");
  const [search, setSearch] = useState("");

  // Modals
  const [showVehicleForm, setShowVehicleForm] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null);
  const [showDriverForm, setShowDriverForm] = useState(false);
  const [editingDriver, setEditingDriver] = useState<Driver | null>(null);
  const [showRouteForm, setShowRouteForm] = useState(false);
  const [editingRoute, setEditingRoute] = useState<Route | null>(null);
  const [showStopForm, setShowStopForm] = useState(false);
  const [selectedRoute, setSelectedRoute] = useState<string | null>(null);
  const [showAssignmentForm, setShowAssignmentForm] = useState(false);
  const [showMaintenanceForm, setShowMaintenanceForm] = useState(false);
  const [editingMaintenance, setEditingMaintenance] = useState<MaintenanceRecord | null>(null);

  // ── Data fetching ───────────────────────────────────────────────────────

  const { data: vehicles = [], isLoading: vLoading } = useQuery({
    queryKey: ["transport-vehicles"],
    queryFn: async () => {
      const res = await api.get<{ results: Vehicle[] }>("/transport/vehicles/");
      return res.results ?? [];
    },
  });

  const { data: drivers = [], isLoading: dLoading } = useQuery({
    queryKey: ["transport-drivers"],
    queryFn: async () => {
      const res = await api.get<{ results: Driver[] }>("/transport/drivers/");
      return res.results ?? [];
    },
  });

  const { data: routes = [], isLoading: rLoading } = useQuery({
    queryKey: ["transport-routes"],
    queryFn: async () => {
      const res = await api.get<{ results: Route[] }>("/transport/routes/");
      return res.results ?? [];
    },
  });

  const { data: assignments = [], isLoading: aLoading } = useQuery({
    queryKey: ["transport-assignments"],
    queryFn: async () => {
      const res = await api.get<{ results: StudentRoute[] }>("/transport/student-routes/");
      return res.results ?? [];
    },
  });

  const { data: maintenance = [], isLoading: mLoading } = useQuery({
    queryKey: ["transport-maintenance"],
    queryFn: async () => {
      const res = await api.get<{ results: MaintenanceRecord[] }>("/transport/maintenance/");
      return res.results ?? [];
    },
  });

  const { data: students = [] } = useQuery({
    queryKey: ["students-short"],
    queryFn: async () => {
      const res = await api.get<{ results: Student[] }>("/students/");
      return res.results ?? [];
    },
  });

  // ── Mutations ───────────────────────────────────────────────────────────

  const deleteVehicle = useMutation({
    mutationFn: (id: string) => api.delete(`/transport/vehicles/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["transport-vehicles"] }); toast.success("Vehicle deleted"); },
  });

  const deleteDriver = useMutation({
    mutationFn: (id: string) => api.delete(`/transport/drivers/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["transport-drivers"] }); toast.success("Driver deleted"); },
  });

  const deleteRoute = useMutation({
    mutationFn: (id: string) => api.delete(`/transport/routes/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["transport-routes"] }); toast.success("Route deleted"); },
  });

  const deleteAssignment = useMutation({
    mutationFn: (id: string) => api.delete(`/transport/student-routes/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["transport-assignments"] }); toast.success("Assignment removed"); },
  });

  // ── Filtering ───────────────────────────────────────────────────────────

  const filteredVehicles = useMemo(() => {
    if (!search.trim()) return vehicles;
    const q = search.toLowerCase();
    return vehicles.filter((v) =>
      v.plate_number.toLowerCase().includes(q) ||
      v.model_name.toLowerCase().includes(q) ||
      v.vehicle_type_display.toLowerCase().includes(q)
    );
  }, [vehicles, search]);

  const filteredRoutes = useMemo(() => {
    if (!search.trim()) return routes;
    const q = search.toLowerCase();
    return routes.filter((r) =>
      r.name.toLowerCase().includes(q) ||
      r.origin.toLowerCase().includes(q) ||
      r.destination.toLowerCase().includes(q)
    );
  }, [routes, search]);

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Transportation Management</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Vehicles, routes, student assignments, and maintenance</p>
        </div>
        <div className="flex gap-2">
          {activeTab === "vehicles" && (
            <Button onClick={() => { setEditingVehicle(null); setShowVehicleForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Vehicle
            </Button>
          )}
          {activeTab === "drivers" && (
            <Button onClick={() => { setEditingDriver(null); setShowDriverForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Driver
            </Button>
          )}
          {activeTab === "routes" && (
            <Button onClick={() => { setEditingRoute(null); setShowRouteForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Add Route
            </Button>
          )}
          {activeTab === "assignments" && (
            <Button onClick={() => setShowAssignmentForm(true)}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Assign Student
            </Button>
          )}
          {activeTab === "maintenance" && (
            <Button onClick={() => { setEditingMaintenance(null); setShowMaintenanceForm(true); }}>
              <PlusIcon className="h-4 w-4 mr-1.5" /> Schedule Service
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit overflow-x-auto">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === tab.key
                  ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Search */}
      {(activeTab === "vehicles" || activeTab === "routes") && (
        <div className="relative max-w-sm">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm dark:text-slate-200"
            placeholder={activeTab === "vehicles" ? "Search vehicles..." : "Search routes..."}
          />
        </div>
      )}

      {/* ── Vehicles Tab ─────────────────────────────────────────────────── */}
      {activeTab === "vehicles" && (
        <>
          {vLoading ? (
            <div className="grid gap-3 sm:grid-cols-2">{[1,2,3].map(i => <div key={i} className="h-28 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : filteredVehicles.length === 0 ? (
            <EmptyState icon={TruckIcon} title="No vehicles" description="Add your first vehicle to get started" />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filteredVehicles.map((v) => (
                <div key={v.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-semibold text-slate-900 dark:text-white">{v.plate_number}</p>
                      <p className="text-xs text-slate-400">{v.vehicle_type_display} {v.model_name && `· ${v.model_name}`} {v.year && `(${v.year})`}</p>
                    </div>
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[v.status]}`}>
                      {v.status_display}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">Seats:</span> {v.capacity}
                      <span className="text-slate-300 dark:text-slate-600">|</span>
                      <span className="font-medium">Routes:</span> {v.route_count}
                    </div>
                    {v.insurance_expiry && (
                      <p>Insurance: {dayjs(v.insurance_expiry).format("MMM D, YYYY")}
                        {dayjs(v.insurance_expiry).isBefore(dayjs()) && (
                          <span className="text-red-500 ml-1">(Expired)</span>
                        )}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2 pt-2 border-t border-slate-100 dark:border-slate-700">
                    <button onClick={() => { setEditingVehicle(v); setShowVehicleForm(true); }}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
                    <button onClick={() => { if (confirm("Delete this vehicle?")) deleteVehicle.mutate(v.id); }}
                      className="text-xs text-red-500 hover:text-red-600 font-medium">Delete</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Drivers Tab ──────────────────────────────────────────────────── */}
      {activeTab === "drivers" && (
        <>
          {dLoading ? (
            <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-20 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : drivers.length === 0 ? (
            <EmptyState icon={UsersIcon} title="No drivers" description="Add your first driver" />
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {drivers.map((d) => (
                <div key={d.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-semibold text-slate-900 dark:text-white">{d.full_name}</p>
                      <p className="text-xs text-slate-400">{d.phone_number} {d.email && `· ${d.email}`}</p>
                    </div>
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[d.status]}`}>
                      {d.status_display}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 space-y-1">
                    {d.license_number && <p>License: {d.license_number} {d.license_expiry && `(exp: ${dayjs(d.license_expiry).format("MMM D, YYYY")})`}</p>}
                    {d.employee_name && <p>HR Link: {d.employee_name}</p>}
                  </div>
                  <div className="flex items-center gap-2 mt-3 pt-2 border-t border-slate-100 dark:border-slate-700">
                    <button onClick={() => { setEditingDriver(d); setShowDriverForm(true); }}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
                    <button onClick={() => { if (confirm("Delete this driver?")) deleteDriver.mutate(d.id); }}
                      className="text-xs text-red-500 hover:text-red-600 font-medium">Delete</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Routes Tab ───────────────────────────────────────────────────── */}
      {activeTab === "routes" && (
        <>
          {rLoading ? (
            <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-24 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : filteredRoutes.length === 0 ? (
            <EmptyState icon={MapPinIcon} title="No routes" description="Create your first route" />
          ) : (
            <div className="space-y-4">
              {filteredRoutes.map((r) => (
                <div key={r.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-semibold text-slate-900 dark:text-white">{r.name}</p>
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${r.is_active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>
                          {r.is_active ? "Active" : "Inactive"}
                        </span>
                      </div>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {r.origin} → {r.destination}
                        {r.estimated_duration_minutes && ` · ${r.estimated_duration_minutes} min`}
                      </p>
                    </div>
                    <div className="text-right text-xs text-slate-400">
                      {r.vehicle_plate && <p>🚌 {r.vehicle_plate}</p>}
                      {r.driver_name && <p>👤 {r.driver_name}</p>}
                      <p>{r.student_count} student{r.student_count !== 1 ? "s" : ""}</p>
                    </div>
                  </div>

                  {/* Stops list */}
                  {r.stops && r.stops.length > 0 && (
                    <div className="mb-3 pl-2 border-l-2 border-indigo-300 dark:border-indigo-600">
                      {r.stops.sort((a, b) => a.stop_order - b.stop_order).map((s) => (
                        <div key={s.id} className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 py-0.5">
                          <span className="inline-flex h-4 w-4 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-900 text-[10px] font-bold text-indigo-600 dark:text-indigo-300">
                            {s.stop_order}
                          </span>
                          <span>{s.name}</span>
                          {s.pickup_time && <span className="text-slate-400">⬆ {dayjs(`2000-01-01T${s.pickup_time}`).format("h:mm A")}</span>}
                          {s.dropoff_time && <span className="text-slate-400">⬇ {dayjs(`2000-01-01T${s.dropoff_time}`).format("h:mm A")}</span>}
                        </div>
                      ))}
                    </div>
                  )}

                  {r.operating_days && (
                    <p className="text-xs text-slate-400 mb-2">📅 {r.operating_days.split(",").map(d => d.trim().charAt(0).toUpperCase() + d.trim().slice(1)).join(", ")}</p>
                  )}

                  <div className="flex items-center gap-2 pt-2 border-t border-slate-100 dark:border-slate-700">
                    <button onClick={() => { setEditingRoute(r); setShowRouteForm(true); }}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Edit</button>
                    <button onClick={() => { setSelectedRoute(r.id); setShowStopForm(true); }}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium">Manage Stops</button>
                    <button onClick={() => { if (confirm("Delete this route?")) deleteRoute.mutate(r.id); }}
                      className="text-xs text-red-500 hover:text-red-600 font-medium">Delete</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Assignments Tab ──────────────────────────────────────────────── */}
      {activeTab === "assignments" && (
        <>
          {aLoading ? (
            <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : assignments.length === 0 ? (
            <EmptyState icon={UsersIcon} title="No student assignments" description="Assign students to routes" />
          ) : (
            <div className="space-y-3">
              {assignments.map((a) => (
                <div key={a.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium text-slate-900 dark:text-white">{a.student_name}</p>
                      <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${a.is_active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>
                        {a.is_active ? "Active" : "Inactive"}
                      </span>
                    </div>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      🚌 {a.route_name}
                      {a.pickup_stop_name && ` · Pickup: ${a.pickup_stop_name}`}
                      {a.dropoff_stop_name && ` · Dropoff: ${a.dropoff_stop_name}`}
                    </p>
                    {a.fee_amount > 0 && <p className="text-xs text-slate-400 mt-0.5">Fee: ${Number(a.fee_amount).toLocaleString()}</p>}
                  </div>
                  <button onClick={() => { if (confirm("Remove this assignment?")) deleteAssignment.mutate(a.id); }}
                    className="text-xs text-red-500 hover:text-red-600 font-medium ml-4">Remove</button>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Maintenance Tab ──────────────────────────────────────────────── */}
      {activeTab === "maintenance" && (
        <>
          {mLoading ? (
            <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-20 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
          ) : maintenance.length === 0 ? (
            <EmptyState icon={WrenchScrewdriverIcon} title="No maintenance records" description="Schedule a vehicle service" />
          ) : (
            <div className="space-y-3">
              {maintenance.map((m) => (
                <div key={m.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-semibold text-slate-900 dark:text-white">{m.vehicle_plate}</p>
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${STATUS_COLORS[m.status]}`}>{m.status_display}</span>
                        <span className="text-xs text-slate-400">{m.maintenance_type_display}</span>
                      </div>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        Scheduled: {dayjs(m.scheduled_date).format("MMM D, YYYY")}
                        {m.completed_date && ` · Completed: ${dayjs(m.completed_date).format("MMM D, YYYY")}`}
                        {m.cost > 0 && ` · Cost: $${Number(m.cost).toLocaleString()}`}
                      </p>
                      {m.description && <p className="text-xs text-slate-400 mt-1">{m.description}</p>}
                      {m.vendor_name && <p className="text-xs text-slate-400">Vendor: {m.vendor_name}</p>}
                    </div>
                    <button onClick={() => { setEditingMaintenance(m); setShowMaintenanceForm(true); }}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium ml-4">Edit</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* ── Vehicle Form Modal ───────────────────────────────────────────── */}
      <VehicleFormModal
        open={showVehicleForm}
        onClose={() => { setShowVehicleForm(false); setEditingVehicle(null); }}
        vehicle={editingVehicle}
        onSaved={() => { setShowVehicleForm(false); setEditingVehicle(null); qc.invalidateQueries({ queryKey: ["transport-vehicles"] }); }}
      />

      {/* ── Driver Form Modal ────────────────────────────────────────────── */}
      <DriverFormModal
        open={showDriverForm}
        onClose={() => { setShowDriverForm(false); setEditingDriver(null); }}
        driver={editingDriver}
        employees={[]}
        onSaved={() => { setShowDriverForm(false); setEditingDriver(null); qc.invalidateQueries({ queryKey: ["transport-drivers"] }); }}
      />

      {/* ── Route Form Modal ─────────────────────────────────────────────── */}
      <RouteFormModal
        open={showRouteForm}
        onClose={() => { setShowRouteForm(false); setEditingRoute(null); }}
        route={editingRoute}
        vehicles={vehicles}
        drivers={drivers}
        onSaved={() => { setShowRouteForm(false); setEditingRoute(null); qc.invalidateQueries({ queryKey: ["transport-routes"] }); }}
      />

      {/* ── Route Stop Form Modal ────────────────────────────────────────── */}
      <RouteStopFormModal
        open={showStopForm}
        onClose={() => { setShowStopForm(false); setSelectedRoute(null); }}
        routeId={selectedRoute}
        onSaved={() => { setShowStopForm(false); setSelectedRoute(null); qc.invalidateQueries({ queryKey: ["transport-routes"] }); }}
      />

      {/* ── Student Assignment Form Modal ────────────────────────────────── */}
      <AssignmentFormModal
        open={showAssignmentForm}
        onClose={() => setShowAssignmentForm(false)}
        routes={routes}
        students={students}
        onSaved={() => { setShowAssignmentForm(false); qc.invalidateQueries({ queryKey: ["transport-assignments"] }); }}
      />

      {/* ── Maintenance Form Modal ────────────────────────────────────────── */}
      <MaintenanceFormModal
        open={showMaintenanceForm}
        onClose={() => { setShowMaintenanceForm(false); setEditingMaintenance(null); }}
        maintenance={editingMaintenance}
        vehicles={vehicles}
        onSaved={() => { setShowMaintenanceForm(false); setEditingMaintenance(null); qc.invalidateQueries({ queryKey: ["transport-maintenance"] }); }}
      />
    </div>
  );
}

// ─── Vehicle Form Modal ──────────────────────────────────────────────────────

function VehicleFormModal({
  open, onClose, vehicle, onSaved,
}: {
  open: boolean; onClose: () => void; vehicle?: Vehicle | null; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    plate_number: vehicle?.plate_number ?? "",
    vehicle_type: vehicle?.vehicle_type ?? "bus",
    model_name: vehicle?.model_name ?? "",
    year: vehicle?.year ?? null as number | null,
    capacity: vehicle?.capacity ?? 40,
    color: vehicle?.color ?? "",
    chassis_number: vehicle?.chassis_number ?? "",
    insurance_number: vehicle?.insurance_number ?? "",
    insurance_expiry: vehicle?.insurance_expiry ?? "",
    fitness_expiry: vehicle?.fitness_expiry ?? "",
    notes: vehicle?.notes ?? "",
  });

  const isEdit = !!vehicle;
  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/transport/vehicles/", data),
    onSuccess: () => { toast.success("Vehicle created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/transport/vehicles/${vehicle!.id}/`, data),
    onSuccess: () => { toast.success("Vehicle updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.plate_number.trim()) return toast.error("Plate number is required");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Vehicle" : "Add Vehicle"}>
      <form onSubmit={handleSubmit} className="space-y-4 max-h-[60vh] overflow-y-auto">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Plate Number *</label>
            <input value={form.plate_number} onChange={(e) => setForm(p => ({ ...p, plate_number: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200 font-mono" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Vehicle Type</label>
            <select value={form.vehicle_type} onChange={(e) => setForm(p => ({ ...p, vehicle_type: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="bus">Bus</option>
              <option value="mini_bus">Mini Bus</option>
              <option value="van">Van</option>
              <option value="suv">SUV</option>
              <option value="sedan">Sedan</option>
              <option value="other">Other</option>
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Model</label>
            <input value={form.model_name} onChange={(e) => setForm(p => ({ ...p, model_name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Year</label>
            <input type="number" min={1990} max={2030} value={form.year ?? ""} onChange={(e) => setForm(p => ({ ...p, year: e.target.value ? Number(e.target.value) : null }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Capacity *</label>
            <input type="number" min={1} value={form.capacity} onChange={(e) => setForm(p => ({ ...p, capacity: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Color</label>
            <input value={form.color} onChange={(e) => setForm(p => ({ ...p, color: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="border-t border-slate-100 dark:border-slate-700 pt-4">
          <p className="text-xs font-semibold text-slate-500 uppercase mb-3">Insurance & Compliance</p>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Insurance #</label>
              <input value={form.insurance_number} onChange={(e) => setForm(p => ({ ...p, insurance_number: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Insurance Expiry</label>
              <input type="date" value={form.insurance_expiry} onChange={(e) => setForm(p => ({ ...p, insurance_expiry: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4 mt-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Fitness Expiry</label>
              <input type="date" value={form.fitness_expiry} onChange={(e) => setForm(p => ({ ...p, fitness_expiry: e.target.value }))}
                className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
            </div>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Notes</label>
          <textarea value={form.notes} onChange={(e) => setForm(p => ({ ...p, notes: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Vehicle</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Driver Form Modal ──────────────────────────────────────────────────────

function DriverFormModal({
  open, onClose, driver, employees, onSaved,
}: {
  open: boolean; onClose: () => void; driver?: Driver | null;
  employees: any[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    full_name: driver?.full_name ?? "",
    phone_number: driver?.phone_number ?? "",
    email: driver?.email ?? "",
    license_number: driver?.license_number ?? "",
    license_expiry: driver?.license_expiry ?? "",
    emergency_contact_name: driver?.emergency_contact_name ?? "",
    emergency_contact_phone: driver?.emergency_contact_phone ?? "",
    notes: driver?.notes ?? "",
  });

  const isEdit = !!driver;
  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/transport/drivers/", data),
    onSuccess: () => { toast.success("Driver created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/transport/drivers/${driver!.id}/`, data),
    onSuccess: () => { toast.success("Driver updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.full_name.trim()) return toast.error("Driver name is required");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Driver" : "Add Driver"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Full Name *</label>
            <input value={form.full_name} onChange={(e) => setForm(p => ({ ...p, full_name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Phone *</label>
            <input value={form.phone_number} onChange={(e) => setForm(p => ({ ...p, phone_number: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Email</label>
            <input type="email" value={form.email} onChange={(e) => setForm(p => ({ ...p, email: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">License #</label>
            <input value={form.license_number} onChange={(e) => setForm(p => ({ ...p, license_number: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">License Expiry</label>
            <input type="date" value={form.license_expiry} onChange={(e) => setForm(p => ({ ...p, license_expiry: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Emergency Contact</label>
            <input value={form.emergency_contact_name} onChange={(e) => setForm(p => ({ ...p, emergency_contact_name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Notes</label>
          <textarea value={form.notes} onChange={(e) => setForm(p => ({ ...p, notes: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Driver</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Route Form Modal ──────────────────────────────────────────────────────

function RouteFormModal({
  open, onClose, route, vehicles, drivers, onSaved,
}: {
  open: boolean; onClose: () => void; route?: Route | null;
  vehicles: Vehicle[]; drivers: Driver[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: route?.name ?? "",
    description: route?.description ?? "",
    vehicle: route?.vehicle ?? "",
    driver: route?.driver ?? "",
    origin: route?.origin ?? "",
    destination: route?.destination ?? "",
    estimated_duration_minutes: route?.estimated_duration_minutes ?? 30,
    operating_days: route?.operating_days ?? "monday,tuesday,wednesday,thursday,friday",
  });

  const isEdit = !!route;
  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/transport/routes/", data),
    onSuccess: () => { toast.success("Route created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/transport/routes/${route!.id}/`, data),
    onSuccess: () => { toast.success("Route updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return toast.error("Route name is required");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Route" : "Add Route"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Route Name *</label>
          <input value={form.name} onChange={(e) => setForm(p => ({ ...p, name: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Origin *</label>
            <input value={form.origin} onChange={(e) => setForm(p => ({ ...p, origin: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Destination *</label>
            <input value={form.destination} onChange={(e) => setForm(p => ({ ...p, destination: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Vehicle</label>
            <select value={form.vehicle} onChange={(e) => setForm(p => ({ ...p, vehicle: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">None</option>
              {vehicles.map((v) => <option key={v.id} value={v.id}>{v.plate_number} ({v.vehicle_type_display})</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Driver</label>
            <select value={form.driver} onChange={(e) => setForm(p => ({ ...p, driver: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">None</option>
              {drivers.map((d) => <option key={d.id} value={d.id}>{d.full_name}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Duration (min)</label>
            <input type="number" min={1} value={form.estimated_duration_minutes} onChange={(e) => setForm(p => ({ ...p, estimated_duration_minutes: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Operating Days</label>
            <input value={form.operating_days} onChange={(e) => setForm(p => ({ ...p, operating_days: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
              placeholder="monday,tuesday,wednesday,..." />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
          <textarea value={form.description} onChange={(e) => setForm(p => ({ ...p, description: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Route</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Route Stop Form Modal ──────────────────────────────────────────────────

function RouteStopFormModal({
  open, onClose, routeId, onSaved,
}: {
  open: boolean; onClose: () => void; routeId: string | null; onSaved: () => void;
}) {
  const [stops, setStops] = useState<{ name: string; address: string; stop_order: number; stop_type: string; pickup_time: string; dropoff_time: string }[]>([]);
  const [newStop, setNewStop] = useState({
    name: "", address: "", stop_type: "both", pickup_time: "07:00", dropoff_time: "15:00",
  });

  // Fetch existing stops for this route
  const { data: existingStops = [] } = useQuery({
    queryKey: ["route-stops", routeId],
    queryFn: async () => {
      if (!routeId) return [];
      const res = await api.get<{ results: any[] }>(`/transport/route-stops/?route=${routeId}`);
      return res.results ?? [];
    },
    enabled: !!routeId && open,
  });

  // Reset stops when modal opens
  React.useEffect(() => {
    if (open && existingStops.length > 0) {
      setStops(existingStops.map((s: any) => ({
        name: s.name,
        address: s.address || "",
        stop_order: s.stop_order,
        stop_type: s.stop_type,
        pickup_time: s.pickup_time || "07:00",
        dropoff_time: s.dropoff_time || "15:00",
      })));
    } else if (open) {
      setStops([]);
    }
  }, [open, existingStops]);

  const addStop = useMutation({
    mutationFn: () => api.post("/transport/route-stops/", {
      route: routeId,
      ...newStop,
      stop_order: stops.length + 1,
    }),
    onSuccess: () => {
      toast.success("Stop added");
      setNewStop({ name: "", address: "", stop_type: "both", pickup_time: "07:00", dropoff_time: "15:00" });
      onSaved();
    },
  });

  const removeStop = useMutation({
    mutationFn: (stop: any) => api.delete(`/transport/route-stops/${stop.id}/`),
    onSuccess: () => { toast.success("Stop removed"); onSaved(); },
  });

  return (
    <Modal open={open} onClose={onClose} title="Manage Route Stops">
      <div className="space-y-4">
        {/* Existing stops */}
        {stops.length > 0 && (
          <div className="space-y-2">
            {stops.sort((a, b) => a.stop_order - b.stop_order).map((s, i) => (
              <div key={i} className="flex items-center gap-2 p-2 rounded-lg border border-slate-100 dark:border-slate-700">
                <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-900 text-xs font-bold text-indigo-600 dark:text-indigo-300">
                  {s.stop_order}
                </span>
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-800 dark:text-white">{s.name}</p>
                  <p className="text-xs text-slate-400">{s.stop_type} · {s.pickup_time || "—"}</p>
                </div>
                <button onClick={() => removeStop.mutate(s as any)}
                  className="text-xs text-red-500 hover:text-red-600">Remove</button>
              </div>
            ))}
          </div>
        )}

        {/* Add new stop */}
        <div className="border-t border-slate-100 dark:border-slate-700 pt-4">
          <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">Add Stop</p>
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <input value={newStop.name} onChange={(e) => setNewStop(p => ({ ...p, name: e.target.value }))}
                className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
                placeholder="Stop name *" />
              <input value={newStop.address} onChange={(e) => setNewStop(p => ({ ...p, address: e.target.value }))}
                className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
                placeholder="Address" />
            </div>
            <div className="grid grid-cols-3 gap-3">
              <select value={newStop.stop_type} onChange={(e) => setNewStop(p => ({ ...p, stop_type: e.target.value }))}
                className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
                <option value="both">Both</option>
                <option value="pickup">Pickup</option>
                <option value="dropoff">Dropoff</option>
              </select>
              <div>
                <label className="block text-xs text-slate-500 mb-1">Pickup Time</label>
                <input type="time" value={newStop.pickup_time} onChange={(e) => setNewStop(p => ({ ...p, pickup_time: e.target.value }))}
                  className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
              </div>
              <div>
                <label className="block text-xs text-slate-500 mb-1">Dropoff Time</label>
                <input type="time" value={newStop.dropoff_time} onChange={(e) => setNewStop(p => ({ ...p, dropoff_time: e.target.value }))}
                  className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
              </div>
            </div>
            <Button onClick={() => addStop.mutate()} loading={addStop.isPending} disabled={!newStop.name.trim()}>
              Add Stop
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}

// ─── Student Assignment Form Modal ──────────────────────────────────────────

function AssignmentFormModal({
  open, onClose, routes, students, onSaved,
}: {
  open: boolean; onClose: () => void; routes: Route[]; students: Student[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    route: "",
    student: "",
    service_type: "both",
    fee_amount: 0,
    effective_from: dayjs().format("YYYY-MM-DD"),
    notes: "",
  });

  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/transport/student-routes/", data),
    onSuccess: () => { toast.success("Student assigned to route"); onSaved(); },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.route || !form.student) return toast.error("Select both route and student");
    createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title="Assign Student to Route">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Route *</label>
            <select value={form.route} onChange={(e) => setForm(p => ({ ...p, route: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">Select route...</option>
              {routes.filter(r => r.is_active).map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Student *</label>
            <select value={form.student} onChange={(e) => setForm(p => ({ ...p, student: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">Select student...</option>
              {students.map((s) => <option key={s.id} value={s.id}>{s.user_name}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Service Type</label>
            <select value={form.service_type} onChange={(e) => setForm(p => ({ ...p, service_type: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="both">Both Pickup & Dropoff</option>
              <option value="pickup">Pickup Only</option>
              <option value="dropoff">Dropoff Only</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Monthly Fee</label>
            <input type="number" min={0} value={form.fee_amount} onChange={(e) => setForm(p => ({ ...p, fee_amount: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Effective From</label>
          <input type="date" value={form.effective_from} onChange={(e) => setForm(p => ({ ...p, effective_from: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Notes</label>
          <textarea value={form.notes} onChange={(e) => setForm(p => ({ ...p, notes: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={createMut.isPending}>Cancel</Button>
          <Button type="submit" loading={createMut.isPending}>Assign Student</Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Maintenance Form Modal ──────────────────────────────────────────────────

function MaintenanceFormModal({
  open, onClose, maintenance, vehicles, onSaved,
}: {
  open: boolean; onClose: () => void; maintenance?: MaintenanceRecord | null;
  vehicles: Vehicle[]; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    vehicle: maintenance?.vehicle ?? "",
    maintenance_type: maintenance?.maintenance_type ?? "routine",
    scheduled_date: maintenance?.scheduled_date ?? dayjs().format("YYYY-MM-DD"),
    cost: maintenance?.cost ?? 0,
    vendor_name: maintenance?.vendor_name ?? "",
    invoice_number: maintenance?.invoice_number ?? "",
    description: maintenance?.description ?? "",
    notes: maintenance?.notes ?? "",
    next_service_date: maintenance?.next_service_date ?? "",
  });

  const isEdit = !!maintenance;
  const createMut = useMutation({
    mutationFn: (data: typeof form) => api.post("/transport/maintenance/", data),
    onSuccess: () => { toast.success("Maintenance record created"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof form) => api.patch(`/transport/maintenance/${maintenance!.id}/`, data),
    onSuccess: () => { toast.success("Maintenance updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.vehicle) return toast.error("Select a vehicle");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Maintenance Record" : "Schedule Vehicle Service"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Vehicle *</label>
            <select value={form.vehicle} onChange={(e) => setForm(p => ({ ...p, vehicle: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="">Select vehicle...</option>
              {vehicles.map((v) => <option key={v.id} value={v.id}>{v.plate_number} ({v.vehicle_type_display})</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Service Type</label>
            <select value={form.maintenance_type} onChange={(e) => setForm(p => ({ ...p, maintenance_type: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              {Object.entries(MAINTENANCE_TYPE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Scheduled Date *</label>
            <input type="date" value={form.scheduled_date} onChange={(e) => setForm(p => ({ ...p, scheduled_date: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Cost</label>
            <input type="number" min={0} value={form.cost} onChange={(e) => setForm(p => ({ ...p, cost: Number(e.target.value) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Vendor</label>
            <input value={form.vendor_name} onChange={(e) => setForm(p => ({ ...p, vendor_name: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Invoice #</label>
            <input value={form.invoice_number} onChange={(e) => setForm(p => ({ ...p, invoice_number: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
          <textarea value={form.description} onChange={(e) => setForm(p => ({ ...p, description: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Next Service Date</label>
          <input type="date" value={form.next_service_date} onChange={(e) => setForm(p => ({ ...p, next_service_date: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Schedule"} Service</Button>
        </div>
      </form>
    </Modal>
  );
}
