/**
 * Infrastructure — Admin page for buildings, rooms, work orders, and assets.
 * Full feature set: dark mode, search, pagination/infinite scroll, CSV export,
 * bulk actions, keyboard shortcuts, shimmer skeletons, CRUD modals.
 */
import React, { useState, useMemo, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  BuildingOffice2Icon,
  Square2StackIcon,
  WrenchScrewdriverIcon,
  ArchiveBoxIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  CalendarDaysIcon,
  ClipboardDocumentCheckIcon,
  BoltIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
  MapPinIcon,
  KeyIcon,
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon,
  VideoCameraIcon,
  LockClosedIcon,
  ArrowPathIcon,
  LightBulbIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, Pagination } from "../../components/common";
import { BulkActionBar } from "../../components/common/BulkActionBar";
import { InfiniteScroll } from "../../components/common/InfiniteScroll";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import { useKeyboardShortcuts } from "../../hooks/useKeyboardShortcuts";
import { useTitle } from "../../hooks";
import { toCsv, downloadCsv } from "../../utils";

// ─── Types ───────────────────────────────────────────────────────────────────

interface Building {
  id: string;
  name: string;
  code: string;
  description: string;
  floors: number;
  year_built: number | null;
  total_area_sqft: number | null;
  address: string;
  status: string;
  status_display?: string;
  is_active: boolean;
  created_at: string;
}

interface Room {
  id: string;
  building: string;
  building_name?: string;
  name: string;
  room_number: string;
  floor: number;
  room_type: string;
  room_type_display?: string;
  status: string;
  status_display?: string;
  capacity: number;
  area_sqft: number | null;
  has_projector: boolean;
  has_smartboard: boolean;
  has_ac: boolean;
  has_wifi: boolean;
  has_computers: boolean;
  computer_count: number;
}

interface WorkOrder {
  id: string;
  title: string;
  description: string;
  category: string;
  priority: string;
  priority_display?: string;
  status: string;
  status_display?: string;
  building: string | null;
  building_name?: string;
  room: string | null;
  room_name?: string;
  reported_by_name?: string;
  assigned_to_name?: string;
  created_at: string;
}

interface Asset {
  id: string;
  asset_tag: string;
  name: string;
  description: string;
  asset_type: string;
  asset_type_display?: string;
  condition: string;
  condition_display?: string;
  status: string;
  status_display?: string;
  building: string | null;
  building_name?: string;
  room: string | null;
  room_name?: string;
  purchase_date: string | null;
  purchase_cost: number | null;
  created_at: string;
}

interface RoomAllocation {
  id: string;
  room: string;
  room_name?: string;
  room_building_name?: string;
  allocation_type: string;
  allocation_type_display?: string;
  classroom: string | null;
  teacher: string | null;
  teacher_name?: string;
  department: string;
  event_name: string;
  effective_from: string | null;
  effective_to: string | null;
  notes: string;
}

interface PreventiveMaintenance {
  id: string;
  title: string;
  description: string;
  category: string;
  building: string | null;
  building_name?: string;
  room: string | null;
  room_name?: string;
  frequency: string;
  frequency_display?: string;
  status: string;
  status_display?: string;
  assigned_to_name?: string;
  last_completed: string | null;
  next_due: string | null;
}

interface SpaceReservation {
  id: string;
  room: string;
  room_name?: string;
  room_building_name?: string;
  title: string;
  purpose: string;
  purpose_display?: string;
  reserved_by_name?: string;
  date: string | null;
  start_time: string | null;
  end_time: string | null;
  attendees_count: number;
  status: string;
  status_display?: string;
  requires_av: boolean;
  requires_refreshments: boolean;
  notes: string;
}

interface EnergyMeter {
  id: string;
  building: string;
  building_name?: string;
  room: string | null;
  room_name?: string;
  meter_number: string;
  meter_type: string;
  meter_type_display?: string;
  installation_date: string | null;
  last_reading_date: string | null;
  last_reading_value: string | number | null;
  is_active: boolean;
  notes: string;
}

interface SafetyInspection {
  id: string;
  title: string;
  inspection_type: string;
  inspection_type_display?: string;
  building: string | null;
  building_name?: string;
  room: string | null;
  room_name?: string;
  scheduled_date: string | null;
  completed_date: string | null;
  inspector_name: string;
  inspector_organization: string;
  status: string;
  status_display?: string;
  overall_severity: string;
  severity_display?: string;
  findings: string;
  recommendations: string;
  corrective_actions: string;
  next_inspection_date: string | null;
}

interface VendorContract {
  id: string;
  vendor_name: string;
  contract_type: string;
  contract_type_display?: string;
  title: string;
  description: string;
  contract_number: string;
  start_date: string | null;
  end_date: string | null;
  renewal_date: string | null;
  auto_renew: boolean;
  value: string | number | null;
  payment_frequency: string;
  contact_person: string;
  contact_phone: string;
  contact_email: string;
  sla_description: string;
  status: string;
  status_display?: string;
  created_by_name?: string;
}

interface ParkingLot {
  id: string;
  name: string;
  total_spots: number;
  available_spots: number;
  is_covered: boolean;
  is_active: boolean;
}

interface ParkingAssignment {
  id: string;
  parking_lot: string;
  parking_lot_name?: string;
  assigned_to_name?: string;
  spot_number: string;
  spot_type: string;
  spot_type_display?: string;
  vehicle_plate: string;
  is_active: boolean;
  start_date: string | null;
  end_date: string | null;
}

interface EnergyReading {
  id: string;
  meter: string;
  meter_number?: string;
  reading_date: string | null;
  reading_value: string | number | null;
  units: string;
  cost: string | number | null;
  recorded_by_name?: string;
  notes: string;
}

interface EnergyAlert {
  id: string;
  building: string;
  building_name?: string;
  meter: string | null;
  meter_number?: string;
  alert_type: string;
  alert_type_display?: string;
  severity: string;
  severity_display?: string;
  status: string;
  status_display?: string;
  description: string;
  threshold_value: string | number | null;
  actual_value: string | number | null;
  resolution_notes: string;
  created_at: string;
}

interface CCTVCamera {
  id: string;
  building: string;
  building_name?: string;
  room: string | null;
  room_name?: string;
  camera_name: string;
  camera_id: string;
  location_description: string;
  stream_url: string;
  recording_enabled: boolean;
  storage_days: number;
  status: string;
  status_display?: string;
  installation_date: string | null;
  last_maintenance: string | null;
  notes: string;
}

interface AccessControlPoint {
  id: string;
  building: string;
  building_name?: string;
  room: string | null;
  room_name?: string;
  point_name: string;
  access_type: string;
  access_type_display?: string;
  status: string;
  status_display?: string;
  access_start_time: string | null;
  access_end_time: string | null;
  restricted_access: boolean;
  installation_date: string | null;
  last_maintenance: string | null;
  notes: string;
}

interface WasteSchedule {
  id: string;
  building: string;
  building_name?: string;
  waste_type: string;
  waste_type_display?: string;
  frequency: string;
  frequency_display?: string;
  collection_day: string;
  collection_time: string | null;
  vendor_name: string;
  is_active: boolean;
}

interface LightingSchedule {
  id: string;
  building: string;
  building_name?: string;
  room: string | null;
  room_name?: string;
  zone_name: string;
  day_of_week: string;
  on_time: string | null;
  off_time: string | null;
  brightness_level: number;
  is_active: boolean;
}

// ─── Choice options (mirror backend TextChoices) ─────────────────────────────

const BUILDING_STATUSES = [
  ["active", "Active"],
  ["under_maintenance", "Under Maintenance"],
  ["closed", "Closed"],
  ["demolished", "Demolished"],
] as const;

const ROOM_TYPES = [
  ["classroom", "Classroom"],
  ["lab", "Laboratory"],
  ["library", "Library"],
  ["office", "Office"],
  ["gym", "Gymnasium"],
  ["auditorium", "Auditorium"],
] as const;

const ROOM_STATUSES = [
  ["available", "Available"],
  ["occupied", "Occupied"],
  ["under_maintenance", "Under Maintenance"],
  ["reserved", "Reserved"],
  ["unavailable", "Unavailable"],
] as const;

const WORK_ORDER_PRIORITIES = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
  ["urgent", "Urgent"],
  ["emergency", "Emergency"],
] as const;

const WORK_ORDER_STATUSES = [
  ["open", "Open"],
  ["in_progress", "In Progress"],
  ["on_hold", "On Hold"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as const;

const WORK_ORDER_CATEGORIES = [
  ["plumbing", "Plumbing"],
  ["electrical", "Electrical"],
  ["hvac", "HVAC / Climate"],
  ["carpentry", "Carpentry"],
  ["painting", "Painting"],
  ["roofing", "Roofing"],
  ["general", "General"],
] as const;

const ASSET_TYPES = [
  ["furniture", "Furniture"],
  ["electronics", "Electronics"],
  ["it_device", "IT Device"],
  ["projector", "Projector / Display"],
  ["network", "Network Equipment"],
  ["safety", "Safety Equipment"],
  ["other", "Other"],
] as const;

const ASSET_CONDITIONS = [
  ["new", "New"],
  ["good", "Good"],
  ["fair", "Fair"],
  ["poor", "Poor"],
  ["damaged", "Damaged"],
  ["written_off", "Written Off"],
] as const;

const ASSET_STATUSES = [
  ["in_stock", "In Stock"],
  ["in_use", "In Use"],
  ["under_repair", "Under Repair"],
  ["retired", "Retired"],
  ["disposed", "Disposed"],
] as const;

const ALLOCATION_TYPES = [
  ["class", "Class Room"],
  ["teacher", "Teacher Office"],
  ["department", "Department"],
  ["event", "Event"],
] as const;

const PM_FREQUENCIES = [
  ["daily", "Daily"],
  ["weekly", "Weekly"],
  ["biweekly", "Bi-weekly"],
  ["monthly", "Monthly"],
  ["quarterly", "Quarterly"],
  ["semi_annual", "Semi-Annual"],
  ["annual", "Annual"],
] as const;

const PM_STATUSES = [
  ["active", "Active"],
  ["paused", "Paused"],
  ["completed", "Completed"],
] as const;

const RESERVATION_STATUSES = [
  ["pending", "Pending"],
  ["confirmed", "Confirmed"],
  ["cancelled", "Cancelled"],
  ["completed", "Completed"],
] as const;

const RESERVATION_PURPOSES = [
  ["meeting", "Meeting"],
  ["event", "Event"],
  ["exam", "Examination"],
  ["training", "Training"],
  ["interview", "Interview"],
  ["other", "Other"],
] as const;

const METER_TYPES = [
  ["electric", "Electric"],
  ["water", "Water"],
  ["gas", "Gas"],
  ["solar", "Solar"],
] as const;

const INSPECTION_TYPES = [
  ["fire", "Fire Safety"],
  ["structural", "Structural"],
  ["electrical", "Electrical Safety"],
  ["plumbing", "Plumbing Safety"],
  ["hvac", "HVAC Safety"],
  ["accessibility", "Accessibility"],
  ["environmental", "Environmental"],
  ["general", "General Safety"],
] as const;

const INSPECTION_STATUSES = [
  ["scheduled", "Scheduled"],
  ["in_progress", "In Progress"],
  ["passed", "Passed"],
  ["failed", "Failed"],
  ["follow_up", "Follow-up Required"],
] as const;

const INSPECTION_SEVERITIES = [
  ["none", "None"],
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
  ["critical", "Critical"],
] as const;

const CONTRACT_TYPES = [
  ["maintenance", "Maintenance"],
  ["cleaning", "Cleaning"],
  ["security", "Security"],
  ["landscaping", "Landscaping"],
  ["it_support", "IT Support"],
  ["hvac", "HVAC Service"],
  ["pest_control", "Pest Control"],
  ["electrical", "Electrical"],
  ["plumbing", "Plumbing"],
  ["other", "Other"],
] as const;

const CONTRACT_STATUSES = [
  ["draft", "Draft"],
  ["active", "Active"],
  ["expired", "Expired"],
  ["terminated", "Terminated"],
  ["renewed", "Renewed"],
] as const;

const SPOT_TYPES = [
  ["regular", "Regular"],
  ["reserved", "Reserved"],
  ["handicap", "Handicap"],
  ["visitor", "Visitor"],
] as const;

const ALERT_TYPES = [
  ["high", "High Consumption"],
  ["spike", "Sudden Spike"],
  ["leak", "Suspected Leak"],
  ["fault", "Meter Fault"],
] as const;

const ALERT_STATUSES = [
  ["active", "Active"],
  ["acknowledged", "Acknowledged"],
  ["resolved", "Resolved"],
] as const;

const CAMERA_STATUSES = [
  ["online", "Online"],
  ["offline", "Offline"],
  ["maintenance", "Under Maintenance"],
] as const;

const ACCESS_TYPES = [
  ["card", "Card Reader"],
  ["biometric", "Biometric"],
  ["pin", "PIN Pad"],
  ["manual", "Manual Lock"],
] as const;

const ACCESS_STATUSES = [
  ["active", "Active"],
  ["disabled", "Disabled"],
  ["maintenance", "Under Maintenance"],
] as const;

const WASTE_TYPES = [
  ["general", "General Waste"],
  ["recyclable", "Recyclable"],
  ["organic", "Organic"],
  ["hazardous", "Hazardous"],
  ["e_waste", "Electronic Waste"],
] as const;

const WASTE_FREQUENCIES = [
  ["daily", "Daily"],
  ["weekly", "Weekly"],
  ["monthly", "Monthly"],
] as const;

const ALERT_SEVERITIES = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
] as const;

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  available: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  in_use: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  in_stock: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  passed: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  renewed: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  occupied: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  reserved: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  in_progress: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  scheduled: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  open: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  under_maintenance: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  under_repair: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  on_hold: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  follow_up: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  draft: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  expired: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  closed: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  cancelled: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  retired: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  disposed: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  demolished: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  unavailable: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  terminated: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  poor: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  damaged: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  written_off: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  online: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  resolved: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  acknowledged: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  maintenance: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  disabled: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  offline: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

const SEVERITY_COLORS: Record<string, string> = {
  none: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  low: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

const PRIORITY_COLORS: Record<string, string> = {
  low: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  medium: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  high: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  urgent: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
  emergency: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

const CONDITION_COLORS: Record<string, string> = {
  new: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  good: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
  fair: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  poor: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
  damaged: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  written_off: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

// ─── Tabs ────────────────────────────────────────────────────────────────────

type TabType =
  | "buildings"
  | "rooms"
  | "workorders"
  | "assets"
  | "allocations"
  | "maintenance"
  | "reservations"
  | "energy"
  | "inspections"
  | "vendors"
  | "parking"
  | "spots"
  | "readings"
  | "alerts"
  | "cameras"
  | "access"
  | "waste"
  | "lighting";

const TABS: { key: TabType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "buildings", label: "Buildings", icon: BuildingOffice2Icon },
  { key: "rooms", label: "Rooms", icon: Square2StackIcon },
  { key: "workorders", label: "Work Orders", icon: WrenchScrewdriverIcon },
  { key: "assets", label: "Assets", icon: ArchiveBoxIcon },
  { key: "allocations", label: "Room Allocations", icon: ClipboardDocumentCheckIcon },
  { key: "maintenance", label: "Maintenance", icon: WrenchScrewdriverIcon },
  { key: "reservations", label: "Reservations", icon: CalendarDaysIcon },
  { key: "energy", label: "Energy", icon: BoltIcon },
  { key: "readings", label: "Readings", icon: ArrowTrendingUpIcon },
  { key: "alerts", label: "Energy Alerts", icon: ExclamationTriangleIcon },
  { key: "inspections", label: "Inspections", icon: ShieldCheckIcon },
  { key: "vendors", label: "Vendors", icon: DocumentTextIcon },
  { key: "cameras", label: "Cameras", icon: VideoCameraIcon },
  { key: "access", label: "Access", icon: LockClosedIcon },
  { key: "waste", label: "Waste", icon: ArrowPathIcon },
  { key: "lighting", label: "Lighting", icon: LightBulbIcon },
  { key: "parking", label: "Parking Lots", icon: MapPinIcon },
  { key: "spots", label: "Spot Assignments", icon: KeyIcon },
];

// ─── Skeleton ────────────────────────────────────────────────────────────────

function CardSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div
          key={i}
          className="h-32 relative overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
        >
          <div
            className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-slate-200/50 to-transparent dark:via-slate-600/30"
            style={{ backgroundSize: "200% 100%" }}
          />
        </div>
      ))}
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function InfrastructurePage() {
  useTitle("Infrastructure");
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>("buildings");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const searchRef = useRef<HTMLInputElement>(null);

  // Modals
  const [showBuildingForm, setShowBuildingForm] = useState(false);
  const [editingBuilding, setEditingBuilding] = useState<Building | null>(null);
  const [showRoomForm, setShowRoomForm] = useState(false);
  const [editingRoom, setEditingRoom] = useState<Room | null>(null);
  const [showWorkOrderForm, setShowWorkOrderForm] = useState(false);
  const [editingWorkOrder, setEditingWorkOrder] = useState<WorkOrder | null>(null);
  const [showAssetForm, setShowAssetForm] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [showAllocationForm, setShowAllocationForm] = useState(false);
  const [editingAllocation, setEditingAllocation] = useState<RoomAllocation | null>(null);
  const [showMaintenanceForm, setShowMaintenanceForm] = useState(false);
  const [editingMaintenance, setEditingMaintenance] = useState<PreventiveMaintenance | null>(null);
  const [showReservationForm, setShowReservationForm] = useState(false);
  const [editingReservation, setEditingReservation] = useState<SpaceReservation | null>(null);
  const [showMeterForm, setShowMeterForm] = useState(false);
  const [editingMeter, setEditingMeter] = useState<EnergyMeter | null>(null);
  const [showInspectionForm, setShowInspectionForm] = useState(false);
  const [editingInspection, setEditingInspection] = useState<SafetyInspection | null>(null);
  const [showVendorForm, setShowVendorForm] = useState(false);
  const [editingVendor, setEditingVendor] = useState<VendorContract | null>(null);
  const [showParkingLotForm, setShowParkingLotForm] = useState(false);
  const [editingParkingLot, setEditingParkingLot] = useState<ParkingLot | null>(null);
  const [showSpotForm, setShowSpotForm] = useState(false);
  const [editingSpot, setEditingSpot] = useState<ParkingAssignment | null>(null);
  const [showReadingForm, setShowReadingForm] = useState(false);
  const [editingReading, setEditingReading] = useState<EnergyReading | null>(null);
  const [showAlertForm, setShowAlertForm] = useState(false);
  const [editingAlert, setEditingAlert] = useState<EnergyAlert | null>(null);
  const [showCameraForm, setShowCameraForm] = useState(false);
  const [editingCamera, setEditingCamera] = useState<CCTVCamera | null>(null);
  const [showAccessForm, setShowAccessForm] = useState(false);
  const [editingAccess, setEditingAccess] = useState<AccessControlPoint | null>(null);
  const [showWasteForm, setShowWasteForm] = useState(false);
  const [editingWaste, setEditingWaste] = useState<WasteSchedule | null>(null);
  const [showLightingForm, setShowLightingForm] = useState(false);
  const [editingLighting, setEditingLighting] = useState<LightingSchedule | null>(null);

  // ── Data fetching ───────────────────────────────────────────────────────

  const { data: buildings = [], isLoading: buildingsLoading } = useQuery({
    queryKey: ["infra-buildings"],
    queryFn: async () => {
      const res = await api.get<{ results: Building[] }>("/infrastructure/buildings/");
      return res.results ?? [];
    },
  });

  const { data: rooms = [], isLoading: roomsLoading } = useQuery({
    queryKey: ["infra-rooms"],
    queryFn: async () => {
      const res = await api.get<{ results: Room[] }>("/infrastructure/rooms/");
      return res.results ?? [];
    },
  });

  const { data: workOrders = [], isLoading: workOrdersLoading } = useQuery({
    queryKey: ["infra-workorders"],
    queryFn: async () => {
      const res = await api.get<{ results: WorkOrder[] }>("/infrastructure/work-orders/");
      return res.results ?? [];
    },
  });

  const { data: assets = [], isLoading: assetsLoading } = useQuery({
    queryKey: ["infra-assets"],
    queryFn: async () => {
      const res = await api.get<{ results: Asset[] }>("/infrastructure/assets/");
      return res.results ?? [];
    },
  });

  const { data: allocations = [], isLoading: allocationsLoading } = useQuery({
    queryKey: ["infra-allocations"],
    queryFn: async () => {
      const res = await api.get<{ results: RoomAllocation[] }>("/infrastructure/room-allocations/");
      return res.results ?? [];
    },
  });

  const { data: maintenance = [], isLoading: maintenanceLoading } = useQuery({
    queryKey: ["infra-maintenance"],
    queryFn: async () => {
      const res = await api.get<{ results: PreventiveMaintenance[] }>(
        "/infrastructure/preventive-maintenance/",
      );
      return res.results ?? [];
    },
  });

  const { data: reservations = [], isLoading: reservationsLoading } = useQuery({
    queryKey: ["infra-reservations"],
    queryFn: async () => {
      const res = await api.get<{ results: SpaceReservation[] }>(
        "/infrastructure/space-reservations/",
      );
      return res.results ?? [];
    },
  });

  const { data: energyMeters = [], isLoading: energyLoading } = useQuery({
    queryKey: ["infra-energy"],
    queryFn: async () => {
      const res = await api.get<{ results: EnergyMeter[] }>("/infrastructure/energy-meter/");
      return res.results ?? [];
    },
  });

  const { data: inspections = [], isLoading: inspectionsLoading } = useQuery({
    queryKey: ["infra-inspections"],
    queryFn: async () => {
      const res = await api.get<{ results: SafetyInspection[] }>(
        "/infrastructure/safety-inspections/",
      );
      return res.results ?? [];
    },
  });

  const { data: vendors = [], isLoading: vendorsLoading } = useQuery({
    queryKey: ["infra-vendors"],
    queryFn: async () => {
      const res = await api.get<{ results: VendorContract[] }>("/infrastructure/vendor-contracts/");
      return res.results ?? [];
    },
  });

  const { data: parkingLots = [], isLoading: parkingLoading } = useQuery({
    queryKey: ["infra-parking"],
    queryFn: async () => {
      const res = await api.get<{ results: ParkingLot[] }>("/infrastructure/parking-lot/");
      return res.results ?? [];
    },
  });

  const { data: spotAssignments = [], isLoading: spotsLoading } = useQuery({
    queryKey: ["infra-spots"],
    queryFn: async () => {
      const res = await api.get<{ results: ParkingAssignment[] }>(
        "/infrastructure/parking-assignment/",
      );
      return res.results ?? [];
    },
  });

  const { data: readings = [], isLoading: readingsLoading } = useQuery({
    queryKey: ["infra-readings"],
    queryFn: async () => {
      const res = await api.get<{ results: EnergyReading[] }>("/infrastructure/energy-reading/");
      return res.results ?? [];
    },
  });

  const { data: alerts = [], isLoading: alertsLoading } = useQuery({
    queryKey: ["infra-alerts"],
    queryFn: async () => {
      const res = await api.get<{ results: EnergyAlert[] }>("/infrastructure/energy-alert/");
      return res.results ?? [];
    },
  });

  const { data: cameras = [], isLoading: camerasLoading } = useQuery({
    queryKey: ["infra-cameras"],
    queryFn: async () => {
      const res = await api.get<{ results: CCTVCamera[] }>("/infrastructure/c-c-t-v-camera/");
      return res.results ?? [];
    },
  });

  const { data: accessPoints = [], isLoading: accessLoading } = useQuery({
    queryKey: ["infra-access"],
    queryFn: async () => {
      const res = await api.get<{ results: AccessControlPoint[] }>(
        "/infrastructure/access-control-point/",
      );
      return res.results ?? [];
    },
  });

  const { data: wasteSchedules = [], isLoading: wasteLoading } = useQuery({
    queryKey: ["infra-waste"],
    queryFn: async () => {
      const res = await api.get<{ results: WasteSchedule[] }>(
        "/infrastructure/waste-collection-schedule/",
      );
      return res.results ?? [];
    },
  });

  const { data: lightingSchedules = [], isLoading: lightingLoading } = useQuery({
    queryKey: ["infra-lighting"],
    queryFn: async () => {
      const res = await api.get<{ results: LightingSchedule[] }>(
        "/infrastructure/lighting-schedule/",
      );
      return res.results ?? [];
    },
  });

  // ── Mutations ───────────────────────────────────────────────────────────

  const deleteBuilding = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/buildings/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-buildings"] });
      toast.success("Building deleted");
    },
  });
  const deleteRoom = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/rooms/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-rooms"] });
      toast.success("Room deleted");
    },
  });
  const deleteWorkOrder = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/work-orders/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-workorders"] });
      toast.success("Work order deleted");
    },
  });
  const deleteAsset = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/assets/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-assets"] });
      toast.success("Asset deleted");
    },
  });
  const deleteAllocation = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/room-allocations/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-allocations"] });
      toast.success("Allocation deleted");
    },
  });
  const deleteMaintenance = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/preventive-maintenance/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-maintenance"] });
      toast.success("Maintenance task deleted");
    },
  });
  const deleteReservation = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/space-reservations/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-reservations"] });
      toast.success("Reservation deleted");
    },
  });
  const deleteMeter = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/energy-meter/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-energy"] });
      toast.success("Meter deleted");
    },
  });
  const deleteInspection = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/safety-inspections/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-inspections"] });
      toast.success("Inspection deleted");
    },
  });
  const deleteVendor = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/vendor-contracts/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-vendors"] });
      toast.success("Contract deleted");
    },
  });
  const deleteParkingLot = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/parking-lot/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-parking"] });
      toast.success("Parking lot deleted");
    },
  });
  const deleteSpot = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/parking-assignment/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-spots"] });
      toast.success("Assignment deleted");
    },
  });
  const deleteReading = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/energy-reading/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-readings"] });
      toast.success("Reading deleted");
    },
  });
  const deleteAlert = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/energy-alert/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-alerts"] });
      toast.success("Alert deleted");
    },
  });
  const deleteCamera = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/c-c-t-v-camera/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-cameras"] });
      toast.success("Camera deleted");
    },
  });
  const deleteAccess = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/access-control-point/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-access"] });
      toast.success("Access point deleted");
    },
  });
  const deleteWaste = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/waste-collection-schedule/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-waste"] });
      toast.success("Schedule deleted");
    },
  });
  const deleteLighting = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/lighting-schedule/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-lighting"] });
      toast.success("Lighting schedule deleted");
    },
  });

  // ── Filtering ───────────────────────────────────────────────────────────

  const filteredBuildings = useMemo(() => {
    if (!search.trim()) return buildings;
    const q = search.toLowerCase();
    return buildings.filter(
      (b) =>
        b.name.toLowerCase().includes(q) ||
        b.code.toLowerCase().includes(q) ||
        b.address?.toLowerCase().includes(q),
    );
  }, [buildings, search]);

  const filteredRooms = useMemo(() => {
    if (!search.trim()) return rooms;
    const q = search.toLowerCase();
    return rooms.filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        r.room_number.toLowerCase().includes(q) ||
        (r.building_name || "").toLowerCase().includes(q),
    );
  }, [rooms, search]);

  const filteredWorkOrders = useMemo(() => {
    if (!search.trim()) return workOrders;
    const q = search.toLowerCase();
    return workOrders.filter(
      (w) =>
        w.title.toLowerCase().includes(q) ||
        w.category.toLowerCase().includes(q) ||
        (w.building_name || "").toLowerCase().includes(q),
    );
  }, [workOrders, search]);

  const filteredAssets = useMemo(() => {
    if (!search.trim()) return assets;
    const q = search.toLowerCase();
    return assets.filter(
      (a) =>
        a.name.toLowerCase().includes(q) ||
        a.asset_tag.toLowerCase().includes(q) ||
        (a.building_name || "").toLowerCase().includes(q),
    );
  }, [assets, search]);

  const filteredAllocations = useMemo(() => {
    if (!search.trim()) return allocations;
    const q = search.toLowerCase();
    return allocations.filter(
      (al) =>
        al.department.toLowerCase().includes(q) ||
        al.event_name.toLowerCase().includes(q) ||
        (al.room_name || "").toLowerCase().includes(q),
    );
  }, [allocations, search]);

  const filteredMaintenance = useMemo(() => {
    if (!search.trim()) return maintenance;
    const q = search.toLowerCase();
    return maintenance.filter(
      (m) =>
        m.title.toLowerCase().includes(q) ||
        m.category.toLowerCase().includes(q) ||
        (m.building_name || "").toLowerCase().includes(q),
    );
  }, [maintenance, search]);

  const filteredReservations = useMemo(() => {
    if (!search.trim()) return reservations;
    const q = search.toLowerCase();
    return reservations.filter(
      (r) =>
        r.title.toLowerCase().includes(q) ||
        r.purpose.toLowerCase().includes(q) ||
        (r.room_name || "").toLowerCase().includes(q),
    );
  }, [reservations, search]);

  const filteredEnergy = useMemo(() => {
    if (!search.trim()) return energyMeters;
    const q = search.toLowerCase();
    return energyMeters.filter(
      (m) =>
        m.meter_number.toLowerCase().includes(q) ||
        m.meter_type.toLowerCase().includes(q) ||
        (m.building_name || "").toLowerCase().includes(q),
    );
  }, [energyMeters, search]);

  const filteredInspections = useMemo(() => {
    if (!search.trim()) return inspections;
    const q = search.toLowerCase();
    return inspections.filter(
      (i) =>
        i.title.toLowerCase().includes(q) ||
        i.inspection_type.toLowerCase().includes(q) ||
        (i.building_name || "").toLowerCase().includes(q) ||
        i.inspector_name.toLowerCase().includes(q),
    );
  }, [inspections, search]);

  const filteredVendors = useMemo(() => {
    if (!search.trim()) return vendors;
    const q = search.toLowerCase();
    return vendors.filter(
      (v) =>
        v.vendor_name.toLowerCase().includes(q) ||
        v.title.toLowerCase().includes(q) ||
        v.contract_type.toLowerCase().includes(q) ||
        v.contract_number.toLowerCase().includes(q),
    );
  }, [vendors, search]);

  const filteredParkingLots = useMemo(() => {
    if (!search.trim()) return parkingLots;
    const q = search.toLowerCase();
    return parkingLots.filter((l) => l.name.toLowerCase().includes(q));
  }, [parkingLots, search]);

  const filteredSpots = useMemo(() => {
    if (!search.trim()) return spotAssignments;
    const q = search.toLowerCase();
    return spotAssignments.filter(
      (s) =>
        s.spot_number.toLowerCase().includes(q) ||
        s.vehicle_plate.toLowerCase().includes(q) ||
        (s.parking_lot_name || "").toLowerCase().includes(q),
    );
  }, [spotAssignments, search]);

  const filteredReadings = useMemo(() => {
    if (!search.trim()) return readings;
    const q = search.toLowerCase();
    return readings.filter(
      (r) =>
        (r.meter_number || "").toLowerCase().includes(q) ||
        r.units.toLowerCase().includes(q) ||
        r.notes.toLowerCase().includes(q),
    );
  }, [readings, search]);

  const filteredAlerts = useMemo(() => {
    if (!search.trim()) return alerts;
    const q = search.toLowerCase();
    return alerts.filter(
      (a) =>
        a.alert_type.toLowerCase().includes(q) ||
        a.status.toLowerCase().includes(q) ||
        (a.building_name || "").toLowerCase().includes(q) ||
        a.description.toLowerCase().includes(q),
    );
  }, [alerts, search]);

  const filteredCameras = useMemo(() => {
    if (!search.trim()) return cameras;
    const q = search.toLowerCase();
    return cameras.filter(
      (c) =>
        c.camera_name.toLowerCase().includes(q) ||
        c.camera_id.toLowerCase().includes(q) ||
        (c.building_name || "").toLowerCase().includes(q),
    );
  }, [cameras, search]);

  const filteredAccess = useMemo(() => {
    if (!search.trim()) return accessPoints;
    const q = search.toLowerCase();
    return accessPoints.filter(
      (p) =>
        p.point_name.toLowerCase().includes(q) ||
        p.access_type.toLowerCase().includes(q) ||
        (p.building_name || "").toLowerCase().includes(q),
    );
  }, [accessPoints, search]);

  const filteredWaste = useMemo(() => {
    if (!search.trim()) return wasteSchedules;
    const q = search.toLowerCase();
    return wasteSchedules.filter(
      (w) =>
        w.waste_type.toLowerCase().includes(q) ||
        w.vendor_name.toLowerCase().includes(q) ||
        (w.building_name || "").toLowerCase().includes(q),
    );
  }, [wasteSchedules, search]);

  const filteredLighting = useMemo(() => {
    if (!search.trim()) return lightingSchedules;
    const q = search.toLowerCase();
    return lightingSchedules.filter(
      (l) =>
        l.zone_name.toLowerCase().includes(q) ||
        l.day_of_week.toLowerCase().includes(q) ||
        (l.building_name || "").toLowerCase().includes(q),
    );
  }, [lightingSchedules, search]);

  const allFiltered =
    activeTab === "buildings"
      ? filteredBuildings
      : activeTab === "rooms"
        ? filteredRooms
        : activeTab === "workorders"
          ? filteredWorkOrders
          : activeTab === "assets"
            ? filteredAssets
            : activeTab === "allocations"
              ? filteredAllocations
              : activeTab === "maintenance"
                ? filteredMaintenance
                : activeTab === "reservations"
                  ? filteredReservations
                  : activeTab === "energy"
                    ? filteredEnergy
                    : activeTab === "readings"
                      ? filteredReadings
                      : activeTab === "alerts"
                        ? filteredAlerts
                        : activeTab === "inspections"
                          ? filteredInspections
                          : activeTab === "vendors"
                            ? filteredVendors
                            : activeTab === "cameras"
                              ? filteredCameras
                              : activeTab === "access"
                                ? filteredAccess
                                : activeTab === "waste"
                                  ? filteredWaste
                                  : activeTab === "lighting"
                                    ? filteredLighting
                                    : activeTab === "parking"
                                      ? filteredParkingLots
                                      : filteredSpots;

  const PAGE_SIZE = 12;
  const totalPages = Math.max(1, Math.ceil(allFiltered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const paginated = allFiltered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);
  const [infinitePage, setInfinitePage] = useState(1);
  const infiniteItems: { id: string }[] = allFiltered.slice(0, infinitePage * PAGE_SIZE);
  const infiniteHasMore = infiniteItems.length < allFiltered.length;

  const visibleItems = viewMode === "pagination" ? paginated : infiniteItems;

  // ── Bulk selection ──────────────────────────────────────────────────────

  const bulk = useBulkSelect<{ id: string }>(allFiltered);
  const activeDelete =
    deleteBuilding.isPending ||
    deleteRoom.isPending ||
    deleteWorkOrder.isPending ||
    deleteAsset.isPending ||
    deleteAllocation.isPending ||
    deleteMaintenance.isPending ||
    deleteReservation.isPending ||
    deleteMeter.isPending ||
    deleteInspection.isPending ||
    deleteVendor.isPending ||
    deleteParkingLot.isPending ||
    deleteSpot.isPending ||
    deleteReading.isPending ||
    deleteAlert.isPending ||
    deleteCamera.isPending ||
    deleteAccess.isPending ||
    deleteWaste.isPending ||
    deleteLighting.isPending;

  const handleBulkDelete = async () => {
    if (bulk.selectedCount === 0) return;
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(
        bulk.selectedArray.map((id) => {
          const base =
            activeTab === "buildings"
              ? "/infrastructure/buildings/"
              : activeTab === "rooms"
                ? "/infrastructure/rooms/"
                : activeTab === "workorders"
                  ? "/infrastructure/work-orders/"
                  : activeTab === "assets"
                    ? "/infrastructure/assets/"
                    : activeTab === "allocations"
                      ? "/infrastructure/room-allocations/"
                      : activeTab === "maintenance"
                        ? "/infrastructure/preventive-maintenance/"
                        : activeTab === "reservations"
                          ? "/infrastructure/space-reservations/"
                          : activeTab === "energy"
                            ? "/infrastructure/energy-meter/"
                            : activeTab === "inspections"
                              ? "/infrastructure/safety-inspections/"
                              : activeTab === "vendors"
                                ? "/infrastructure/vendor-contracts/"
                                : activeTab === "parking"
                                  ? "/infrastructure/parking-lot/"
                                  : activeTab === "spots"
                                    ? "/infrastructure/parking-assignment/"
                                    : activeTab === "readings"
                                      ? "/infrastructure/energy-reading/"
                                      : activeTab === "alerts"
                                        ? "/infrastructure/energy-alert/"
                                        : activeTab === "cameras"
                                          ? "/infrastructure/c-c-t-v-camera/"
                                          : activeTab === "access"
                                            ? "/infrastructure/access-control-point/"
                                            : activeTab === "waste"
                                              ? "/infrastructure/waste-collection-schedule/"
                                              : "/infrastructure/lighting-schedule/";
          return api.delete(`${base}${id}/`);
        }),
      );
      toast.success(`${bulk.selectedCount} items deleted`);
      bulk.clear();
      qc.invalidateQueries();
    } catch {
      toast.error("Failed to delete items");
    }
  };

  // ── CSV export ──────────────────────────────────────────────────────────

  const handleExport = () => {
    const rows =
      activeTab === "buildings"
        ? filteredBuildings.map((b) => ({
            name: b.name,
            code: b.code,
            floors: b.floors,
            address: b.address,
            status: b.status,
          }))
        : activeTab === "rooms"
          ? filteredRooms.map((r) => ({
              name: r.name,
              room_number: r.room_number,
              building: r.building_name ?? "",
              room_type: r.room_type,
              capacity: r.capacity,
              status: r.status,
            }))
          : activeTab === "workorders"
            ? filteredWorkOrders.map((w) => ({
                title: w.title,
                category: w.category,
                priority: w.priority,
                status: w.status,
                building: w.building_name ?? "",
              }))
            : activeTab === "assets"
              ? filteredAssets.map((a) => ({
                  name: a.name,
                  asset_tag: a.asset_tag,
                  asset_type: a.asset_type,
                  condition: a.condition,
                  status: a.status,
                  building: a.building_name ?? "",
                }))
              : activeTab === "allocations"
                ? filteredAllocations.map((al) => ({
                    room: al.room_name ?? "",
                    allocation_type: al.allocation_type,
                    department: al.department,
                    event_name: al.event_name,
                    effective_from: al.effective_from ?? "",
                  }))
                : activeTab === "maintenance"
                  ? filteredMaintenance.map((m) => ({
                      title: m.title,
                      category: m.category,
                      frequency: m.frequency,
                      status: m.status,
                      building: m.building_name ?? "",
                      next_due: m.next_due ?? "",
                    }))
                  : activeTab === "reservations"
                    ? filteredReservations.map((r) => ({
                        title: r.title,
                        purpose: r.purpose,
                        room: r.room_name ?? "",
                        date: r.date ?? "",
                        status: r.status,
                        attendees: r.attendees_count,
                      }))
                    : activeTab === "energy"
                      ? filteredEnergy.map((m) => ({
                          meter_number: m.meter_number,
                          meter_type: m.meter_type,
                          building: m.building_name ?? "",
                          is_active: m.is_active,
                        }))
                      : activeTab === "inspections"
                        ? filteredInspections.map((i) => ({
                            title: i.title,
                            inspection_type: i.inspection_type,
                            status: i.status,
                            building: i.building_name ?? "",
                            scheduled_date: i.scheduled_date ?? "",
                          }))
                        : activeTab === "vendors"
                          ? filteredVendors.map((v) => ({
                              vendor_name: v.vendor_name,
                              title: v.title,
                              contract_type: v.contract_type,
                              status: v.status,
                              value: v.value ?? 0,
                            }))
                          : activeTab === "parking"
                            ? filteredParkingLots.map((l) => ({
                                name: l.name,
                                total_spots: l.total_spots,
                                available_spots: l.available_spots,
                                is_covered: l.is_covered,
                                is_active: l.is_active,
                              }))
                            : activeTab === "spots"
                              ? filteredSpots.map((s) => ({
                                  spot_number: s.spot_number,
                                  lot: s.parking_lot_name ?? "",
                                  spot_type: s.spot_type,
                                  vehicle_plate: s.vehicle_plate,
                                  is_active: s.is_active,
                                }))
                              : activeTab === "readings"
                                ? filteredReadings.map((r) => ({
                                    meter: r.meter_number ?? "",
                                    reading_date: r.reading_date ?? "",
                                    reading_value: r.reading_value ?? 0,
                                    units: r.units,
                                    cost: r.cost ?? "",
                                  }))
                                : activeTab === "alerts"
                                  ? filteredAlerts.map((a) => ({
                                      alert_type: a.alert_type,
                                      severity: a.severity,
                                      status: a.status,
                                      building: a.building_name ?? "",
                                      description: a.description,
                                    }))
                                  : activeTab === "cameras"
                                    ? filteredCameras.map((c) => ({
                                        camera_name: c.camera_name,
                                        camera_id: c.camera_id,
                                        building: c.building_name ?? "",
                                        status: c.status,
                                        recording_enabled: c.recording_enabled,
                                      }))
                                    : activeTab === "access"
                                      ? filteredAccess.map((p) => ({
                                          point_name: p.point_name,
                                          access_type: p.access_type,
                                          status: p.status,
                                          building: p.building_name ?? "",
                                          restricted_access: p.restricted_access,
                                        }))
                                      : activeTab === "waste"
                                        ? filteredWaste.map((w) => ({
                                            waste_type: w.waste_type,
                                            frequency: w.frequency,
                                            building: w.building_name ?? "",
                                            collection_day: w.collection_day,
                                            vendor: w.vendor_name,
                                          }))
                                        : activeTab === "lighting"
                                          ? filteredLighting.map((l) => ({
                                              zone_name: l.zone_name,
                                              building: l.building_name ?? "",
                                              day_of_week: l.day_of_week,
                                              on_time: l.on_time ?? "",
                                              off_time: l.off_time ?? "",
                                              brightness: l.brightness_level,
                                            }))
                                          : [];
    const cols = Object.keys(rows[0] ?? {}).map((k) => ({ key: k, label: k }));
    downloadCsv(
      toCsv(rows, cols),
      `infrastructure-${activeTab}-${dayjs().format("YYYY-MM-DD")}.csv`,
    );
  };

  const handleBulkExport = () => {
    const cols = [{ key: "id", label: "ID" }];
    downloadCsv(
      toCsv(
        bulk.selectedItems.map((i) => ({ id: i.id })),
        cols,
      ),
      `infrastructure-bulk-${dayjs().format("YYYY-MM-DD")}.csv`,
    );
  };

  // ── Keyboard shortcuts ──────────────────────────────────────────────────

  const { open: helpOpen, setOpen: setHelpOpen } = useShortcutHelp();
  useKeyboardShortcuts({
    onCreate: () => {
      if (activeTab === "buildings") setShowBuildingForm(true);
      else if (activeTab === "rooms") setShowRoomForm(true);
      else if (activeTab === "workorders") setShowWorkOrderForm(true);
      else if (activeTab === "assets") setShowAssetForm(true);
      else if (activeTab === "allocations") setShowAllocationForm(true);
      else if (activeTab === "maintenance") setShowMaintenanceForm(true);
      else if (activeTab === "reservations") setShowReservationForm(true);
      else if (activeTab === "energy") setShowMeterForm(true);
      else if (activeTab === "inspections") setShowInspectionForm(true);
      else if (activeTab === "vendors") setShowVendorForm(true);
      else if (activeTab === "parking") setShowParkingLotForm(true);
      else if (activeTab === "spots") setShowSpotForm(true);
      else if (activeTab === "readings") setShowReadingForm(true);
      else if (activeTab === "alerts") setShowAlertForm(true);
      else if (activeTab === "cameras") setShowCameraForm(true);
      else if (activeTab === "access") setShowAccessForm(true);
      else if (activeTab === "waste") setShowWasteForm(true);
      else setShowLightingForm(true);
    },
    onSearch: () => searchRef.current?.focus(),
    onExport: handleExport,
    onEscape: () => bulk.clear(),
    onDelete: () => {
      if (bulk.selectedCount > 0) handleBulkDelete();
    },
    onSelectAll: () => bulk.toggleAll(),
  });

  const isLoading =
    activeTab === "buildings"
      ? buildingsLoading
      : activeTab === "rooms"
        ? roomsLoading
        : activeTab === "workorders"
          ? workOrdersLoading
          : activeTab === "assets"
            ? assetsLoading
            : activeTab === "allocations"
              ? allocationsLoading
              : activeTab === "maintenance"
                ? maintenanceLoading
                : activeTab === "reservations"
                  ? reservationsLoading
                  : activeTab === "energy"
                    ? energyLoading
                    : activeTab === "inspections"
                      ? inspectionsLoading
                      : activeTab === "vendors"
                        ? vendorsLoading
                        : activeTab === "parking"
                          ? parkingLoading
                          : activeTab === "spots"
                            ? spotsLoading
                            : activeTab === "readings"
                              ? readingsLoading
                              : activeTab === "alerts"
                                ? alertsLoading
                                : activeTab === "cameras"
                                  ? camerasLoading
                                  : activeTab === "access"
                                    ? accessLoading
                                    : activeTab === "waste"
                                      ? wasteLoading
                                      : lightingLoading;

  const createButton =
    activeTab === "buildings"
      ? {
          label: "Add Building",
          action: () => {
            setEditingBuilding(null);
            setShowBuildingForm(true);
          },
        }
      : activeTab === "rooms"
        ? {
            label: "Add Room",
            action: () => {
              setEditingRoom(null);
              setShowRoomForm(true);
            },
          }
        : activeTab === "workorders"
          ? {
              label: "New Work Order",
              action: () => {
                setEditingWorkOrder(null);
                setShowWorkOrderForm(true);
              },
            }
          : activeTab === "assets"
            ? {
                label: "Add Asset",
                action: () => {
                  setEditingAsset(null);
                  setShowAssetForm(true);
                },
              }
            : activeTab === "allocations"
              ? {
                  label: "New Allocation",
                  action: () => {
                    setEditingAllocation(null);
                    setShowAllocationForm(true);
                  },
                }
              : activeTab === "maintenance"
                ? {
                    label: "New Maintenance Task",
                    action: () => {
                      setEditingMaintenance(null);
                      setShowMaintenanceForm(true);
                    },
                  }
                : activeTab === "reservations"
                  ? {
                      label: "New Reservation",
                      action: () => {
                        setEditingReservation(null);
                        setShowReservationForm(true);
                      },
                    }
                  : activeTab === "energy"
                    ? {
                        label: "Add Meter",
                        action: () => {
                          setEditingMeter(null);
                          setShowMeterForm(true);
                        },
                      }
                    : activeTab === "inspections"
                      ? {
                          label: "New Inspection",
                          action: () => {
                            setEditingInspection(null);
                            setShowInspectionForm(true);
                          },
                        }
                      : activeTab === "vendors"
                        ? {
                            label: "New Contract",
                            action: () => {
                              setEditingVendor(null);
                              setShowVendorForm(true);
                            },
                          }
                        : activeTab === "parking"
                          ? {
                              label: "Add Parking Lot",
                              action: () => {
                                setEditingParkingLot(null);
                                setShowParkingLotForm(true);
                              },
                            }
                          : activeTab === "spots"
                            ? {
                                label: "Assign Spot",
                                action: () => {
                                  setEditingSpot(null);
                                  setShowSpotForm(true);
                                },
                              }
                            : activeTab === "readings"
                              ? {
                                  label: "Add Reading",
                                  action: () => {
                                    setEditingReading(null);
                                    setShowReadingForm(true);
                                  },
                                }
                              : activeTab === "alerts"
                                ? {
                                    label: "Raise Alert",
                                    action: () => {
                                      setEditingAlert(null);
                                      setShowAlertForm(true);
                                    },
                                  }
                                : activeTab === "cameras"
                                  ? {
                                      label: "Add Camera",
                                      action: () => {
                                        setEditingCamera(null);
                                        setShowCameraForm(true);
                                      },
                                    }
                                  : activeTab === "access"
                                    ? {
                                        label: "Add Access Point",
                                        action: () => {
                                          setEditingAccess(null);
                                          setShowAccessForm(true);
                                        },
                                      }
                                    : activeTab === "waste"
                                      ? {
                                          label: "Add Schedule",
                                          action: () => {
                                            setEditingWaste(null);
                                            setShowWasteForm(true);
                                          },
                                        }
                                      : {
                                          label: "Add Lighting Schedule",
                                          action: () => {
                                            setEditingLighting(null);
                                            setShowLightingForm(true);
                                          },
                                        };

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Infrastructure</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Buildings, rooms, work orders, assets, energy, safety, vendors, parking, CCTV and more
          </p>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={bulk.allSelected}
              ref={(el) => {
                if (el) el.indeterminate = bulk.someSelected;
              }}
              onChange={bulk.toggleAll}
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
            />
            <span className="text-sm text-slate-500 dark:text-slate-400">Select all</span>
          </label>
          <div className="flex items-center gap-1 rounded-lg border border-slate-200 p-0.5 dark:border-slate-700">
            <button
              onClick={() => setViewMode("pagination")}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                viewMode === "pagination"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
              }`}
            >
              Pages
            </button>
            <button
              onClick={() => setViewMode("infinite")}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                viewMode === "infinite"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-400"
                  : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300"
              }`}
            >
              Scroll
            </button>
          </div>
          <Button
            variant="secondary"
            leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
            onClick={handleExport}
          >
            Export CSV
          </Button>
          <Button onClick={createButton.action}>
            <PlusIcon className="mr-1.5 h-4 w-4" />
            {createButton.label}
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 overflow-x-auto rounded-lg bg-slate-100 p-1 w-fit dark:bg-slate-800">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => {
                setActiveTab(tab.key);
                setPage(1);
                setInfinitePage(1);
              }}
              className={`inline-flex items-center gap-2 whitespace-nowrap rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? "bg-white text-slate-900 shadow-sm dark:bg-slate-700 dark:text-white"
                  : "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-200"
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
              <span className="rounded-full bg-slate-200 px-1.5 py-0.5 text-xs dark:bg-slate-600">
                {activeTab === tab.key ? allFiltered.length : ""}
              </span>
            </button>
          );
        })}
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          ref={searchRef}
          type="search"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
          placeholder={`Search ${activeTab === "workorders" ? "work orders" : activeTab}...`}
          className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:placeholder-slate-400"
        />
      </div>

      {/* Content */}
      {isLoading ? (
        <CardSkeleton />
      ) : allFiltered.length === 0 ? (
        <EmptyState
          icon={
            activeTab === "buildings"
              ? BuildingOffice2Icon
              : activeTab === "rooms"
                ? Square2StackIcon
                : activeTab === "workorders"
                  ? WrenchScrewdriverIcon
                  : activeTab === "assets"
                    ? ArchiveBoxIcon
                    : activeTab === "allocations"
                      ? ClipboardDocumentCheckIcon
                      : activeTab === "maintenance"
                        ? WrenchScrewdriverIcon
                        : activeTab === "reservations"
                          ? CalendarDaysIcon
                          : activeTab === "energy"
                            ? BoltIcon
                            : activeTab === "inspections"
                              ? ShieldCheckIcon
                              : activeTab === "vendors"
                                ? DocumentTextIcon
                                : activeTab === "parking"
                                  ? MapPinIcon
                                  : KeyIcon
          }
          title={`No ${
            activeTab === "workorders"
              ? "work orders"
              : activeTab === "maintenance"
                ? "maintenance tasks"
                : activeTab === "allocations"
                  ? "room allocations"
                  : activeTab === "reservations"
                    ? "reservations"
                    : activeTab === "energy"
                      ? "energy meters"
                      : activeTab === "readings"
                        ? "energy readings"
                        : activeTab === "alerts"
                          ? "energy alerts"
                          : activeTab === "inspections"
                            ? "inspections"
                            : activeTab === "vendors"
                              ? "vendor contracts"
                              : activeTab === "cameras"
                                ? "cameras"
                                : activeTab === "access"
                                  ? "access points"
                                  : activeTab === "waste"
                                    ? "waste schedules"
                                    : activeTab === "lighting"
                                      ? "lighting schedules"
                                      : activeTab === "parking"
                                        ? "parking lots"
                                        : "spot assignments"
          }`}
          description={`Add your first ${
            activeTab === "workorders"
              ? "work order"
              : activeTab === "maintenance"
                ? "maintenance task"
                : activeTab === "allocations"
                  ? "room allocation"
                  : activeTab === "energy"
                    ? "energy meter"
                    : activeTab === "readings"
                      ? "energy reading"
                      : activeTab === "alerts"
                        ? "energy alert"
                        : activeTab === "inspections"
                          ? "inspection"
                          : activeTab === "vendors"
                            ? "vendor contract"
                            : activeTab === "cameras"
                              ? "camera"
                              : activeTab === "access"
                                ? "access point"
                                : activeTab === "waste"
                                  ? "waste schedule"
                                  : activeTab === "lighting"
                                    ? "lighting schedule"
                                    : activeTab === "parking"
                                      ? "parking lot"
                                      : activeTab === "spots"
                                        ? "spot assignment"
                                        : activeTab.slice(0, -1)
          } to get started`}
        />
      ) : (
        <>
          {viewMode === "pagination" ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {visibleItems.map((item) => (
                <Card
                  key={item.id}
                  tab={activeTab}
                  item={item}
                  selected={bulk.isSelected(item.id)}
                  onToggle={() => bulk.toggle(item.id)}
                  onEdit={() => {
                    if (activeTab === "buildings") {
                      setEditingBuilding(item as Building);
                      setShowBuildingForm(true);
                    } else if (activeTab === "rooms") {
                      setEditingRoom(item as Room);
                      setShowRoomForm(true);
                    } else if (activeTab === "workorders") {
                      setEditingWorkOrder(item as WorkOrder);
                      setShowWorkOrderForm(true);
                    } else if (activeTab === "assets") {
                      setEditingAsset(item as Asset);
                      setShowAssetForm(true);
                    } else if (activeTab === "allocations") {
                      setEditingAllocation(item as RoomAllocation);
                      setShowAllocationForm(true);
                    } else if (activeTab === "maintenance") {
                      setEditingMaintenance(item as PreventiveMaintenance);
                      setShowMaintenanceForm(true);
                    } else if (activeTab === "reservations") {
                      setEditingReservation(item as SpaceReservation);
                      setShowReservationForm(true);
                    } else if (activeTab === "energy") {
                      setEditingMeter(item as EnergyMeter);
                      setShowMeterForm(true);
                    } else if (activeTab === "inspections") {
                      setEditingInspection(item as SafetyInspection);
                      setShowInspectionForm(true);
                    } else if (activeTab === "vendors") {
                      setEditingVendor(item as VendorContract);
                      setShowVendorForm(true);
                    } else if (activeTab === "parking") {
                      setEditingParkingLot(item as ParkingLot);
                      setShowParkingLotForm(true);
                    } else if (activeTab === "spots") {
                      setEditingSpot(item as ParkingAssignment);
                      setShowSpotForm(true);
                    } else if (activeTab === "readings") {
                      setEditingReading(item as EnergyReading);
                      setShowReadingForm(true);
                    } else if (activeTab === "alerts") {
                      setEditingAlert(item as EnergyAlert);
                      setShowAlertForm(true);
                    } else if (activeTab === "cameras") {
                      setEditingCamera(item as CCTVCamera);
                      setShowCameraForm(true);
                    } else if (activeTab === "access") {
                      setEditingAccess(item as AccessControlPoint);
                      setShowAccessForm(true);
                    } else if (activeTab === "waste") {
                      setEditingWaste(item as WasteSchedule);
                      setShowWasteForm(true);
                    } else {
                      setEditingLighting(item as LightingSchedule);
                      setShowLightingForm(true);
                    }
                  }}
                  onDelete={() => {
                    if (!confirm("Delete this item?")) return;
                    if (activeTab === "buildings") deleteBuilding.mutate(item.id);
                    else if (activeTab === "rooms") deleteRoom.mutate(item.id);
                    else if (activeTab === "workorders") deleteWorkOrder.mutate(item.id);
                    else if (activeTab === "assets") deleteAsset.mutate(item.id);
                    else if (activeTab === "allocations") deleteAllocation.mutate(item.id);
                    else if (activeTab === "maintenance") deleteMaintenance.mutate(item.id);
                    else if (activeTab === "reservations") deleteReservation.mutate(item.id);
                    else if (activeTab === "energy") deleteMeter.mutate(item.id);
                    else if (activeTab === "inspections") deleteInspection.mutate(item.id);
                    else if (activeTab === "vendors") deleteVendor.mutate(item.id);
                    else if (activeTab === "parking") deleteParkingLot.mutate(item.id);
                    else if (activeTab === "spots") deleteSpot.mutate(item.id);
                    else if (activeTab === "readings") deleteReading.mutate(item.id);
                    else if (activeTab === "alerts") deleteAlert.mutate(item.id);
                    else if (activeTab === "cameras") deleteCamera.mutate(item.id);
                    else if (activeTab === "access") deleteAccess.mutate(item.id);
                    else if (activeTab === "waste") deleteWaste.mutate(item.id);
                    else deleteLighting.mutate(item.id);
                  }}
                />
              ))}
            </div>
          ) : (
            <InfiniteScroll
              items={infiniteItems}
              hasMore={infiniteHasMore}
              isLoading={false}
              isFetchingNext={false}
              onLoadMore={() => setInfinitePage((p) => p + 1)}
              renderItem={(item) => (
                <Card
                  key={item.id}
                  tab={activeTab}
                  item={item}
                  selected={bulk.isSelected(item.id)}
                  onToggle={() => bulk.toggle(item.id)}
                  onEdit={() => {
                    if (activeTab === "buildings") {
                      setEditingBuilding(item as Building);
                      setShowBuildingForm(true);
                    } else if (activeTab === "rooms") {
                      setEditingRoom(item as Room);
                      setShowRoomForm(true);
                    } else if (activeTab === "workorders") {
                      setEditingWorkOrder(item as WorkOrder);
                      setShowWorkOrderForm(true);
                    } else if (activeTab === "assets") {
                      setEditingAsset(item as Asset);
                      setShowAssetForm(true);
                    } else if (activeTab === "allocations") {
                      setEditingAllocation(item as RoomAllocation);
                      setShowAllocationForm(true);
                    } else if (activeTab === "maintenance") {
                      setEditingMaintenance(item as PreventiveMaintenance);
                      setShowMaintenanceForm(true);
                    } else if (activeTab === "reservations") {
                      setEditingReservation(item as SpaceReservation);
                      setShowReservationForm(true);
                    } else if (activeTab === "energy") {
                      setEditingMeter(item as EnergyMeter);
                      setShowMeterForm(true);
                    } else if (activeTab === "inspections") {
                      setEditingInspection(item as SafetyInspection);
                      setShowInspectionForm(true);
                    } else if (activeTab === "vendors") {
                      setEditingVendor(item as VendorContract);
                      setShowVendorForm(true);
                    } else if (activeTab === "parking") {
                      setEditingParkingLot(item as ParkingLot);
                      setShowParkingLotForm(true);
                    } else if (activeTab === "spots") {
                      setEditingSpot(item as ParkingAssignment);
                      setShowSpotForm(true);
                    } else if (activeTab === "readings") {
                      setEditingReading(item as EnergyReading);
                      setShowReadingForm(true);
                    } else if (activeTab === "alerts") {
                      setEditingAlert(item as EnergyAlert);
                      setShowAlertForm(true);
                    } else if (activeTab === "cameras") {
                      setEditingCamera(item as CCTVCamera);
                      setShowCameraForm(true);
                    } else if (activeTab === "access") {
                      setEditingAccess(item as AccessControlPoint);
                      setShowAccessForm(true);
                    } else if (activeTab === "waste") {
                      setEditingWaste(item as WasteSchedule);
                      setShowWasteForm(true);
                    } else {
                      setEditingLighting(item as LightingSchedule);
                      setShowLightingForm(true);
                    }
                  }}
                  onDelete={() => {
                    if (!confirm("Delete this item?")) return;
                    if (activeTab === "buildings") deleteBuilding.mutate(item.id);
                    else if (activeTab === "rooms") deleteRoom.mutate(item.id);
                    else if (activeTab === "workorders") deleteWorkOrder.mutate(item.id);
                    else if (activeTab === "assets") deleteAsset.mutate(item.id);
                    else if (activeTab === "allocations") deleteAllocation.mutate(item.id);
                    else if (activeTab === "maintenance") deleteMaintenance.mutate(item.id);
                    else if (activeTab === "reservations") deleteReservation.mutate(item.id);
                    else if (activeTab === "energy") deleteMeter.mutate(item.id);
                    else if (activeTab === "inspections") deleteInspection.mutate(item.id);
                    else if (activeTab === "vendors") deleteVendor.mutate(item.id);
                    else if (activeTab === "parking") deleteParkingLot.mutate(item.id);
                    else if (activeTab === "spots") deleteSpot.mutate(item.id);
                    else if (activeTab === "readings") deleteReading.mutate(item.id);
                    else if (activeTab === "alerts") deleteAlert.mutate(item.id);
                    else if (activeTab === "cameras") deleteCamera.mutate(item.id);
                    else if (activeTab === "access") deleteAccess.mutate(item.id);
                    else if (activeTab === "waste") deleteWaste.mutate(item.id);
                    else deleteLighting.mutate(item.id);
                  }}
                />
              )}
            />
          )}

          {viewMode === "pagination" && totalPages > 1 && (
            <Pagination
              page={safePage}
              total={allFiltered.length}
              pageSize={PAGE_SIZE}
              onChange={setPage}
            />
          )}
        </>
      )}

      {/* Bulk action bar */}
      <BulkActionBar
        selectedCount={bulk.selectedCount}
        onClear={bulk.clear}
        onDelete={handleBulkDelete}
        onExport={handleBulkExport}
        deleteLabel={`Delete ${bulk.selectedCount} selected`}
      />

      {/* Modals */}
      {activeTab === "buildings" && (
        <BuildingFormModal
          open={showBuildingForm}
          onClose={() => {
            setShowBuildingForm(false);
            setEditingBuilding(null);
          }}
          building={editingBuilding}
          onSaved={() => {
            setShowBuildingForm(false);
            setEditingBuilding(null);
            qc.invalidateQueries({ queryKey: ["infra-buildings"] });
          }}
        />
      )}
      {activeTab === "rooms" && (
        <RoomFormModal
          open={showRoomForm}
          onClose={() => {
            setShowRoomForm(false);
            setEditingRoom(null);
          }}
          room={editingRoom}
          buildings={buildings}
          onSaved={() => {
            setShowRoomForm(false);
            setEditingRoom(null);
            qc.invalidateQueries({ queryKey: ["infra-rooms"] });
          }}
        />
      )}
      {activeTab === "workorders" && (
        <WorkOrderFormModal
          open={showWorkOrderForm}
          onClose={() => {
            setShowWorkOrderForm(false);
            setEditingWorkOrder(null);
          }}
          workOrder={editingWorkOrder}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowWorkOrderForm(false);
            setEditingWorkOrder(null);
            qc.invalidateQueries({ queryKey: ["infra-workorders"] });
          }}
        />
      )}
      {activeTab === "assets" && (
        <AssetFormModal
          open={showAssetForm}
          onClose={() => {
            setShowAssetForm(false);
            setEditingAsset(null);
          }}
          asset={editingAsset}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowAssetForm(false);
            setEditingAsset(null);
            qc.invalidateQueries({ queryKey: ["infra-assets"] });
          }}
        />
      )}
      {activeTab === "allocations" && (
        <AllocationFormModal
          open={showAllocationForm}
          onClose={() => {
            setShowAllocationForm(false);
            setEditingAllocation(null);
          }}
          allocation={editingAllocation}
          rooms={rooms}
          onSaved={() => {
            setShowAllocationForm(false);
            setEditingAllocation(null);
            qc.invalidateQueries({ queryKey: ["infra-allocations"] });
          }}
        />
      )}
      {activeTab === "maintenance" && (
        <MaintenanceFormModal
          open={showMaintenanceForm}
          onClose={() => {
            setShowMaintenanceForm(false);
            setEditingMaintenance(null);
          }}
          task={editingMaintenance}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowMaintenanceForm(false);
            setEditingMaintenance(null);
            qc.invalidateQueries({ queryKey: ["infra-maintenance"] });
          }}
        />
      )}
      {activeTab === "reservations" && (
        <ReservationFormModal
          open={showReservationForm}
          onClose={() => {
            setShowReservationForm(false);
            setEditingReservation(null);
          }}
          reservation={editingReservation}
          rooms={rooms}
          onSaved={() => {
            setShowReservationForm(false);
            setEditingReservation(null);
            qc.invalidateQueries({ queryKey: ["infra-reservations"] });
          }}
        />
      )}
      {activeTab === "energy" && (
        <MeterFormModal
          open={showMeterForm}
          onClose={() => {
            setShowMeterForm(false);
            setEditingMeter(null);
          }}
          meter={editingMeter}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowMeterForm(false);
            setEditingMeter(null);
            qc.invalidateQueries({ queryKey: ["infra-energy"] });
          }}
        />
      )}
      {activeTab === "inspections" && (
        <InspectionFormModal
          open={showInspectionForm}
          onClose={() => {
            setShowInspectionForm(false);
            setEditingInspection(null);
          }}
          inspection={editingInspection}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowInspectionForm(false);
            setEditingInspection(null);
            qc.invalidateQueries({ queryKey: ["infra-inspections"] });
          }}
        />
      )}
      {activeTab === "vendors" && (
        <VendorFormModal
          open={showVendorForm}
          onClose={() => {
            setShowVendorForm(false);
            setEditingVendor(null);
          }}
          contract={editingVendor}
          onSaved={() => {
            setShowVendorForm(false);
            setEditingVendor(null);
            qc.invalidateQueries({ queryKey: ["infra-vendors"] });
          }}
        />
      )}
      {activeTab === "parking" && (
        <ParkingLotFormModal
          open={showParkingLotForm}
          onClose={() => {
            setShowParkingLotForm(false);
            setEditingParkingLot(null);
          }}
          lot={editingParkingLot}
          onSaved={() => {
            setShowParkingLotForm(false);
            setEditingParkingLot(null);
            qc.invalidateQueries({ queryKey: ["infra-parking"] });
          }}
        />
      )}
      {activeTab === "spots" && (
        <SpotFormModal
          open={showSpotForm}
          onClose={() => {
            setShowSpotForm(false);
            setEditingSpot(null);
          }}
          assignment={editingSpot}
          lots={parkingLots}
          onSaved={() => {
            setShowSpotForm(false);
            setEditingSpot(null);
            qc.invalidateQueries({ queryKey: ["infra-spots"] });
          }}
        />
      )}
      {activeTab === "readings" && (
        <ReadingFormModal
          open={showReadingForm}
          onClose={() => {
            setShowReadingForm(false);
            setEditingReading(null);
          }}
          reading={editingReading}
          meters={energyMeters}
          onSaved={() => {
            setShowReadingForm(false);
            setEditingReading(null);
            qc.invalidateQueries({ queryKey: ["infra-readings"] });
          }}
        />
      )}
      {activeTab === "alerts" && (
        <AlertFormModal
          open={showAlertForm}
          onClose={() => {
            setShowAlertForm(false);
            setEditingAlert(null);
          }}
          alert={editingAlert}
          buildings={buildings}
          meters={energyMeters}
          onSaved={() => {
            setShowAlertForm(false);
            setEditingAlert(null);
            qc.invalidateQueries({ queryKey: ["infra-alerts"] });
          }}
        />
      )}
      {activeTab === "cameras" && (
        <CameraFormModal
          open={showCameraForm}
          onClose={() => {
            setShowCameraForm(false);
            setEditingCamera(null);
          }}
          camera={editingCamera}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowCameraForm(false);
            setEditingCamera(null);
            qc.invalidateQueries({ queryKey: ["infra-cameras"] });
          }}
        />
      )}
      {activeTab === "access" && (
        <AccessFormModal
          open={showAccessForm}
          onClose={() => {
            setShowAccessForm(false);
            setEditingAccess(null);
          }}
          access={editingAccess}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowAccessForm(false);
            setEditingAccess(null);
            qc.invalidateQueries({ queryKey: ["infra-access"] });
          }}
        />
      )}
      {activeTab === "waste" && (
        <WasteFormModal
          open={showWasteForm}
          onClose={() => {
            setShowWasteForm(false);
            setEditingWaste(null);
          }}
          schedule={editingWaste}
          buildings={buildings}
          onSaved={() => {
            setShowWasteForm(false);
            setEditingWaste(null);
            qc.invalidateQueries({ queryKey: ["infra-waste"] });
          }}
        />
      )}
      {activeTab === "lighting" && (
        <LightingFormModal
          open={showLightingForm}
          onClose={() => {
            setShowLightingForm(false);
            setEditingLighting(null);
          }}
          schedule={editingLighting}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowLightingForm(false);
            setEditingLighting(null);
            qc.invalidateQueries({ queryKey: ["infra-lighting"] });
          }}
        />
      )}

      {/* Shortcut help */}
      <KeyboardShortcutHelp open={helpOpen} onClose={() => setHelpOpen(false)} />
    </div>
  );
}

// ─── Card ────────────────────────────────────────────────────────────────────

function Card({
  tab,
  item,
  selected,
  onToggle,
  onEdit,
  onDelete,
}: {
  tab: TabType;
  item: { id: string };
  selected: boolean;
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const inputCls =
    "h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600";
  return (
    <div
      className={`group rounded-xl border bg-white p-4 transition-all hover:shadow-md dark:bg-slate-800 ${
        selected
          ? "border-indigo-400 ring-1 ring-indigo-400 dark:border-indigo-500"
          : "border-slate-200 dark:border-slate-700"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <input
          type="checkbox"
          checked={selected}
          onChange={onToggle}
          className={inputCls}
          aria-label="Select item"
        />
        <div className="flex-1 min-w-0">
          {tab === "buildings" && <BuildingCard item={item as Building} />}
          {tab === "rooms" && <RoomCard item={item as Room} />}
          {tab === "workorders" && <WorkOrderCard item={item as WorkOrder} />}
          {tab === "assets" && <AssetCard item={item as Asset} />}
          {tab === "allocations" && <AllocationCard item={item as RoomAllocation} />}
          {tab === "maintenance" && <MaintenanceCard item={item as PreventiveMaintenance} />}
          {tab === "reservations" && <ReservationCard item={item as SpaceReservation} />}
          {tab === "energy" && <MeterCard item={item as EnergyMeter} />}
          {tab === "readings" && <ReadingCard item={item as EnergyReading} />}
          {tab === "alerts" && <AlertCard item={item as EnergyAlert} />}
          {tab === "inspections" && <InspectionCard item={item as SafetyInspection} />}
          {tab === "vendors" && <VendorCard item={item as VendorContract} />}
          {tab === "cameras" && <CameraCard item={item as CCTVCamera} />}
          {tab === "access" && <AccessCard item={item as AccessControlPoint} />}
          {tab === "waste" && <WasteCard item={item as WasteSchedule} />}
          {tab === "lighting" && <LightingCard item={item as LightingSchedule} />}
          {tab === "parking" && <ParkingLotCard item={item as ParkingLot} />}
          {tab === "spots" && <SpotCard item={item as ParkingAssignment} />}
        </div>
        <div className="flex gap-1">
          <button
            onClick={onEdit}
            className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
            aria-label="Edit"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
          <button
            onClick={onDelete}
            className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
            aria-label="Delete"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

function Badge({ value, colors }: { value: string; colors: Record<string, string> }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
        colors[value] ?? "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
      }`}
    >
      {value.replace(/_/g, " ")}
    </span>
  );
}

function BuildingCard({ item }: { item: Building }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.name}
      </p>
      <p className="font-mono text-xs text-slate-400">{item.code}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <Badge value={item.status} colors={STATUS_COLORS} />
        {item.floors > 0 && <span>🏢 {item.floors} floors</span>}
        {item.total_area_sqft && (
          <span>📐 {Number(item.total_area_sqft).toLocaleString()} sqft</span>
        )}
      </div>
      {item.address && <p className="mt-1 truncate text-xs text-slate-400">📍 {item.address}</p>}
    </>
  );
}

function RoomCard({ item }: { item: Room }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.name}
      </p>
      <p className="text-xs text-slate-400">
        {item.room_number}
        {item.building_name && ` · ${item.building_name}`}
        {item.floor != null && ` · Floor ${item.floor}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <Badge value={item.room_type} colors={{}} />
        <Badge value={item.status} colors={STATUS_COLORS} />
        {item.capacity > 0 && <span>👥 {item.capacity}</span>}
      </div>
      <div className="mt-1 flex flex-wrap gap-1.5 text-xs text-slate-400">
        {item.has_projector && <span>🖥</span>}
        {item.has_smartboard && <span>🪄</span>}
        {item.has_ac && <span>❄️</span>}
        {item.has_wifi && <span>📶</span>}
        {item.has_computers && <span>💻 {item.computer_count}</span>}
      </div>
    </>
  );
}

function WorkOrderCard({ item }: { item: WorkOrder }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name || "—"}
        {item.room_name && ` · ${item.room_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.priority} colors={PRIORITY_COLORS} />
        <Badge value={item.status} colors={STATUS_COLORS} />
        {item.category && <span className="text-slate-400">{item.category}</span>}
      </div>
      {item.assigned_to_name && (
        <p className="mt-1 truncate text-xs text-slate-400">👷 {item.assigned_to_name}</p>
      )}
    </>
  );
}

function AssetCard({ item }: { item: Asset }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.name}
      </p>
      <p className="font-mono text-xs text-slate-400">{item.asset_tag}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.asset_type} colors={{}} />
        <Badge value={item.condition} colors={CONDITION_COLORS} />
        <Badge value={item.status} colors={STATUS_COLORS} />
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.building_name && <span>📍 {item.building_name}</span>}
        {item.purchase_cost != null && <span>💲{Number(item.purchase_cost).toLocaleString()}</span>}
      </div>
    </>
  );
}

function AllocationCard({ item }: { item: RoomAllocation }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.room_name ?? item.room}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.room_building_name || ""}
        {item.allocation_type && ` · ${item.allocation_type.replace(/_/g, " ")}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <Badge value={item.allocation_type} colors={{}} />
        {item.department && <span>🏛 {item.department}</span>}
        {item.event_name && <span>🎪 {item.event_name}</span>}
        {item.teacher_name && <span>👩‍🏫 {item.teacher_name}</span>}
      </div>
      {item.effective_from && (
        <p className="mt-1 truncate text-xs text-slate-400">
          📅 {item.effective_from}
          {item.effective_to ? ` → ${item.effective_to}` : " → ongoing"}
        </p>
      )}
    </>
  );
}

function MaintenanceCard({ item }: { item: PreventiveMaintenance }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name || "—"}
        {item.room_name && ` · ${item.room_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.frequency} colors={{}} />
        <Badge value={item.status} colors={STATUS_COLORS} />
        {item.category && <span className="text-slate-400">{item.category}</span>}
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.next_due && <span>⏳ due {item.next_due}</span>}
        {item.assigned_to_name && <span>👷 {item.assigned_to_name}</span>}
      </div>
    </>
  );
}

function ReservationCard({ item }: { item: SpaceReservation }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.room_name || item.room}
        {item.room_building_name && ` · ${item.room_building_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.purpose} colors={{}} />
        <Badge value={item.status} colors={STATUS_COLORS} />
        {item.attendees_count > 0 && (
          <span className="text-slate-400">👥 {item.attendees_count}</span>
        )}
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.date && (
          <span>
            📅 {item.date}
            {item.start_time && ` ${item.start_time.slice(0, 5)}–${item.end_time?.slice(0, 5)}`}
          </span>
        )}
        {item.requires_av && <span>🎤</span>}
        {item.requires_refreshments && <span>☕</span>}
      </div>
    </>
  );
}

function MeterCard({ item }: { item: EnergyMeter }) {
  const lastReading = item.last_reading_value != null ? Number(item.last_reading_value) : null;
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.meter_number}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name || "—"}
        {item.room_name && ` · ${item.room_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.meter_type} colors={{}} />
        <span
          className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
            item.is_active
              ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
              : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
          }`}
        >
          {item.is_active ? "Active" : "Inactive"}
        </span>
      </div>
      <p className="mt-1 truncate text-xs text-slate-400">
        {item.last_reading_date
          ? `📊 last reading ${item.last_reading_date}${
              lastReading != null ? ` · ${lastReading.toLocaleString()}` : ""
            }`
          : "📊 no readings yet"}
      </p>
    </>
  );
}

function InspectionCard({ item }: { item: SafetyInspection }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.inspection_type.replace(/_/g, " ")}
        {item.building_name && ` · ${item.building_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.status} colors={STATUS_COLORS} />
        <Badge value={item.overall_severity} colors={SEVERITY_COLORS} />
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.scheduled_date && <span>📅 {item.scheduled_date}</span>}
        {item.inspector_name && <span>👷 {item.inspector_name}</span>}
      </div>
    </>
  );
}

function VendorCard({ item }: { item: VendorContract }) {
  const value = item.value != null ? Number(item.value) : null;
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.vendor_name}
        {item.contract_number && ` · ${item.contract_number}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.contract_type} colors={{}} />
        <Badge value={item.status} colors={STATUS_COLORS} />
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.start_date && (
          <span>
            🗓 {item.start_date}
            {item.end_date ? ` → ${item.end_date}` : ""}
          </span>
        )}
        {value != null && value > 0 && (
          <span>💲{value.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>
        )}
        {item.auto_renew && <span>🔄 auto-renew</span>}
      </div>
    </>
  );
}

function ParkingLotCard({ item }: { item: ParkingLot }) {
  const occupied = Math.max(0, item.total_spots - item.available_spots);
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.name}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <span
          className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
            item.is_active
              ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
              : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
          }`}
        >
          {item.is_active ? "Active" : "Inactive"}
        </span>
        {item.is_covered && (
          <span className="inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
            Covered
          </span>
        )}
      </div>
      <p className="mt-1 text-xs text-slate-400">
        🅿️ {item.available_spots}/{item.total_spots} spots free
        {occupied > 0 ? ` (${occupied} used)` : ""}
      </p>
    </>
  );
}

function SpotCard({ item }: { item: ParkingAssignment }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.spot_number}
      </p>
      <p className="truncate text-xs text-slate-400">{item.parking_lot_name || item.parking_lot}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.spot_type} colors={{}} />
        <span
          className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
            item.is_active
              ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
              : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
          }`}
        >
          {item.is_active ? "Active" : "Inactive"}
        </span>
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.vehicle_plate && <span>🚗 {item.vehicle_plate}</span>}
        {item.assigned_to_name && <span>👤 {item.assigned_to_name}</span>}
      </div>
    </>
  );
}

function ReadingCard({ item }: { item: EnergyReading }) {
  const value = item.reading_value != null ? Number(item.reading_value) : null;
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.meter_number ?? item.meter}
      </p>
      <p className="text-xs text-slate-400">{item.reading_date ?? "—"}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
        <span className="rounded-full bg-blue-100 px-2 py-0.5 font-medium text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
          {value != null ? value.toLocaleString() : "—"} {item.units}
        </span>
        {item.cost != null && Number(item.cost) > 0 && (
          <span>💲{Number(item.cost).toLocaleString()}</span>
        )}
      </div>
      {item.recorded_by_name && (
        <p className="mt-1 truncate text-xs text-slate-400">👤 {item.recorded_by_name}</p>
      )}
    </>
  );
}

function AlertCard({ item }: { item: EnergyAlert }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.alert_type.replace(/_/g, " ")}
        {item.meter_number ? ` · ${item.meter_number}` : ""}
      </p>
      <p className="truncate text-xs text-slate-400">{item.building_name ?? "—"}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.severity} colors={SEVERITY_COLORS} />
        <Badge value={item.status} colors={STATUS_COLORS} />
      </div>
      <p className="mt-1 line-clamp-2 text-xs text-slate-400">{item.description}</p>
      {item.threshold_value != null && item.actual_value != null && (
        <p className="mt-1 text-xs text-slate-400">
          ⚡ {Number(item.actual_value).toLocaleString()} vs threshold{" "}
          {Number(item.threshold_value).toLocaleString()}
        </p>
      )}
    </>
  );
}

function CameraCard({ item }: { item: CCTVCamera }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.camera_name}
      </p>
      <p className="font-mono text-xs text-slate-400">{item.camera_id}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.status} colors={STATUS_COLORS} />
        {item.building_name && <span className="text-slate-400">📍 {item.building_name}</span>}
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.recording_enabled && <span>⏺ recording</span>}
        {item.storage_days > 0 && <span>💾 {item.storage_days}d retention</span>}
        {item.location_description && (
          <span className="truncate">🗺 {item.location_description}</span>
        )}
      </div>
    </>
  );
}

function AccessCard({ item }: { item: AccessControlPoint }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.point_name}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name ?? "—"}
        {item.room_name && ` · ${item.room_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.access_type} colors={{}} />
        <Badge value={item.status} colors={STATUS_COLORS} />
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.restricted_access && <span>🔒 restricted</span>}
        {item.access_start_time && (
          <span>
            🕐 {item.access_start_time.slice(0, 5)}–{item.access_end_time?.slice(0, 5)}
          </span>
        )}
      </div>
    </>
  );
}

function WasteCard({ item }: { item: WasteSchedule }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.waste_type.replace(/_/g, " ")}
      </p>
      <p className="truncate text-xs text-slate-400">{item.building_name ?? "—"}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <Badge value={item.frequency} colors={{}} />
        <span
          className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
            item.is_active
              ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
              : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
          }`}
        >
          {item.is_active ? "Active" : "Inactive"}
        </span>
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.collection_day && (
          <span>
            🗓 {item.collection_day}
            {item.collection_time ? ` ${item.collection_time.slice(0, 5)}` : ""}
          </span>
        )}
        {item.vendor_name && <span>🚛 {item.vendor_name}</span>}
      </div>
    </>
  );
}

function LightingCard({ item }: { item: LightingSchedule }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.zone_name || item.building_name || "Lighting schedule"}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name ?? "—"}
        {item.room_name && ` · ${item.room_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <span className="rounded-full bg-amber-100 px-2 py-0.5 font-medium text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
          💡 {item.on_time?.slice(0, 5)}–{item.off_time?.slice(0, 5)}
        </span>
        <span
          className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
            item.is_active
              ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
              : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
          }`}
        >
          {item.is_active ? "Active" : "Inactive"}
        </span>
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.day_of_week && <span>📅 {item.day_of_week}</span>}
        {item.brightness_level > 0 && <span>🔆 {item.brightness_level}%</span>}
      </div>
    </>
  );
}

// ─── Form helpers ────────────────────────────────────────────────────────────

const inputCls =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200";
const labelCls = "mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300";

function SelectField({
  label,
  value,
  options,
  onChange,
  required,
}: {
  label: string;
  value: string;
  options: readonly (readonly [string, string])[];
  onChange: (v: string) => void;
  required?: boolean;
}) {
  return (
    <div>
      <label className={labelCls}>
        {label}
        {required && " *"}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={inputCls}
        required={required}
      >
        {options.map(([v, l]) => (
          <option key={v} value={v}>
            {l}
          </option>
        ))}
      </select>
    </div>
  );
}

// ─── Building Form Modal ─────────────────────────────────────────────────────

function BuildingFormModal({
  open,
  onClose,
  building,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  building?: Building | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    name: building?.name ?? "",
    code: building?.code ?? "",
    description: building?.description ?? "",
    floors: building?.floors ?? 1,
    year_built: building?.year_built ?? "",
    total_area_sqft: building?.total_area_sqft ?? "",
    address: building?.address ?? "",
    status: building?.status ?? "active",
  });
  const isEdit = !!building;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/buildings/", data),
    onSuccess: () => {
      toast.success("Building created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/infrastructure/buildings/${building!.id}/`, data),
    onSuccess: () => {
      toast.success("Building updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Building name is required");
    const data = {
      ...f,
      year_built: f.year_built ? Number(f.year_built) : null,
      total_area_sqft: f.total_area_sqft ? Number(f.total_area_sqft) : null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Building" : "Add Building"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Code</label>
            <input
              value={f.code}
              onChange={(e) => setF((p) => ({ ...p, code: e.target.value }))}
              className={inputCls}
              placeholder="e.g. BLDG-A"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Floors</label>
            <input
              type="number"
              min={1}
              value={f.floors}
              onChange={(e) => setF((p) => ({ ...p, floors: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Year Built</label>
            <input
              type="number"
              min={1800}
              max={2100}
              value={f.year_built}
              onChange={(e) => setF((p) => ({ ...p, year_built: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Area (sqft)</label>
            <input
              type="number"
              min={0}
              value={f.total_area_sqft}
              onChange={(e) => setF((p) => ({ ...p, total_area_sqft: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <SelectField
          label="Status"
          value={f.status}
          options={BUILDING_STATUSES}
          onChange={(v) => setF((p) => ({ ...p, status: v }))}
        />
        <div>
          <label className={labelCls}>Address</label>
          <input
            value={f.address}
            onChange={(e) => setF((p) => ({ ...p, address: e.target.value }))}
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Room Form Modal ─────────────────────────────────────────────────────────

function RoomFormModal({
  open,
  onClose,
  room,
  buildings,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  room?: Room | null;
  buildings: Building[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: room?.building ?? "",
    name: room?.name ?? "",
    room_number: room?.room_number ?? "",
    floor: room?.floor ?? 1,
    room_type: room?.room_type ?? "classroom",
    status: room?.status ?? "available",
    capacity: room?.capacity ?? 30,
    area_sqft: room?.area_sqft ?? "",
    has_projector: room?.has_projector ?? false,
    has_smartboard: room?.has_smartboard ?? false,
    has_ac: room?.has_ac ?? false,
    has_wifi: room?.has_wifi ?? false,
    has_computers: room?.has_computers ?? false,
    computer_count: room?.computer_count ?? 0,
  });
  const isEdit = !!room;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/rooms/", data),
    onSuccess: () => {
      toast.success("Room created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/infrastructure/rooms/${room!.id}/`, data),
    onSuccess: () => {
      toast.success("Room updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Room name is required");
    if (!f.building) return toast.error("Select a building");
    const data = { ...f, area_sqft: f.area_sqft ? Number(f.area_sqft) : null } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Room" : "Add Room"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building *</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value }))}
              className={inputCls}
              required
            >
              <option value="">Select building...</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room Number</label>
            <input
              value={f.room_number}
              onChange={(e) => setF((p) => ({ ...p, room_number: e.target.value }))}
              className={inputCls}
              placeholder="e.g. A-101"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Floor</label>
            <input
              type="number"
              min={0}
              value={f.floor}
              onChange={(e) => setF((p) => ({ ...p, floor: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Capacity</label>
            <input
              type="number"
              min={0}
              value={f.capacity}
              onChange={(e) => setF((p) => ({ ...p, capacity: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Room Type"
            value={f.room_type}
            options={ROOM_TYPES}
            onChange={(v) => setF((p) => ({ ...p, room_type: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={ROOM_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div>
          <label className={labelCls}>Area (sqft)</label>
          <input
            type="number"
            min={0}
            value={f.area_sqft}
            onChange={(e) => setF((p) => ({ ...p, area_sqft: e.target.value }))}
            className={inputCls}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          {(
            [
              ["has_projector", "Projector"],
              ["has_smartboard", "Smartboard"],
              ["has_ac", "Air Conditioning"],
              ["has_wifi", "Wi-Fi"],
              ["has_computers", "Computers"],
            ] as const
          ).map(([key, label]) => (
            <label
              key={key}
              className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300"
            >
              <input
                type="checkbox"
                checked={f[key]}
                onChange={(e) => setF((p) => ({ ...p, [key]: e.target.checked }))}
                className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
              />
              {label}
            </label>
          ))}
        </div>
        {f.has_computers && (
          <div>
            <label className={labelCls}>Computer Count</label>
            <input
              type="number"
              min={0}
              value={f.computer_count}
              onChange={(e) => setF((p) => ({ ...p, computer_count: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
        )}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Work Order Form Modal ───────────────────────────────────────────────────

function WorkOrderFormModal({
  open,
  onClose,
  workOrder,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  workOrder?: WorkOrder | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    title: workOrder?.title ?? "",
    description: workOrder?.description ?? "",
    category: workOrder?.category ?? "general",
    priority: workOrder?.priority ?? "medium",
    status: workOrder?.status ?? "open",
    building: workOrder?.building ?? "",
    room: workOrder?.room ?? "",
  });
  const isEdit = !!workOrder;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/work-orders/", data),
    onSuccess: () => {
      toast.success("Work order created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/work-orders/${workOrder!.id}/`, data),
    onSuccess: () => {
      toast.success("Work order updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.title.trim()) return toast.error("Title is required");
    const data = { ...f, building: f.building || null, room: f.room || null } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Work Order" : "New Work Order"}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>Title *</label>
          <input
            value={f.title}
            onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
            className={inputCls}
            required
          />
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            rows={3}
            className={inputCls}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <SelectField
            label="Category"
            value={f.category}
            options={WORK_ORDER_CATEGORIES}
            onChange={(v) => setF((p) => ({ ...p, category: v }))}
          />
          <SelectField
            label="Priority"
            value={f.priority}
            options={WORK_ORDER_PRIORITIES}
            onChange={(v) => setF((p) => ({ ...p, priority: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={WORK_ORDER_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value, room: "" }))}
              className={inputCls}
            >
              <option value="">None</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              disabled={!f.building}
            >
              <option value="">None</option>
              {buildingRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Asset Form Modal ────────────────────────────────────────────────────────

function AssetFormModal({
  open,
  onClose,
  asset,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  asset?: Asset | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    name: asset?.name ?? "",
    asset_tag: asset?.asset_tag ?? "",
    description: asset?.description ?? "",
    asset_type: asset?.asset_type ?? "furniture",
    condition: asset?.condition ?? "good",
    status: asset?.status ?? "in_stock",
    building: asset?.building ?? "",
    room: asset?.room ?? "",
    purchase_date: asset?.purchase_date ?? "",
    purchase_cost: asset?.purchase_cost ?? "",
  });
  const isEdit = !!asset;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/assets/", data),
    onSuccess: () => {
      toast.success("Asset created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/infrastructure/assets/${asset!.id}/`, data),
    onSuccess: () => {
      toast.success("Asset updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Asset name is required");
    const data = {
      ...f,
      building: f.building || null,
      room: f.room || null,
      purchase_date: f.purchase_date || null,
      purchase_cost: f.purchase_cost ? Number(f.purchase_cost) : null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Asset" : "Add Asset"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Asset Tag</label>
            <input
              value={f.asset_tag}
              onChange={(e) => setF((p) => ({ ...p, asset_tag: e.target.value }))}
              className={`${inputCls} font-mono`}
              placeholder="e.g. AST-0001"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <SelectField
            label="Type"
            value={f.asset_type}
            options={ASSET_TYPES}
            onChange={(v) => setF((p) => ({ ...p, asset_type: v }))}
          />
          <SelectField
            label="Condition"
            value={f.condition}
            options={ASSET_CONDITIONS}
            onChange={(v) => setF((p) => ({ ...p, condition: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={ASSET_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value, room: "" }))}
              className={inputCls}
            >
              <option value="">None</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              disabled={!f.building}
            >
              <option value="">None</option>
              {buildingRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Purchase Date</label>
            <input
              type="date"
              value={f.purchase_date}
              onChange={(e) => setF((p) => ({ ...p, purchase_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Purchase Cost</label>
            <input
              type="number"
              min={0}
              step={0.01}
              value={f.purchase_cost}
              onChange={(e) => setF((p) => ({ ...p, purchase_cost: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Room Allocation Form Modal ──────────────────────────────────────────────

function AllocationFormModal({
  open,
  onClose,
  allocation,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  allocation?: RoomAllocation | null;
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    room: allocation?.room ?? "",
    allocation_type: allocation?.allocation_type ?? "class",
    department: allocation?.department ?? "",
    event_name: allocation?.event_name ?? "",
    effective_from: allocation?.effective_from ?? "",
    effective_to: allocation?.effective_to ?? "",
    notes: allocation?.notes ?? "",
  });
  const isEdit = !!allocation;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/room-allocations/", data),
    onSuccess: () => {
      toast.success("Allocation created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/room-allocations/${allocation!.id}/`, data),
    onSuccess: () => {
      toast.success("Allocation updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.room) return toast.error("Select a room");
    if (!f.effective_from) return toast.error("Effective from date is required");
    const data = { ...f, effective_to: f.effective_to || null } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Allocation" : "New Room Allocation"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Room *</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              required
            >
              <option value="">Select room...</option>
              {rooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
          <SelectField
            label="Allocation Type"
            value={f.allocation_type}
            options={ALLOCATION_TYPES}
            onChange={(v) => setF((p) => ({ ...p, allocation_type: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Department</label>
            <input
              value={f.department}
              onChange={(e) => setF((p) => ({ ...p, department: e.target.value }))}
              className={inputCls}
              placeholder="e.g. Mathematics"
            />
          </div>
          <div>
            <label className={labelCls}>Event Name</label>
            <input
              value={f.event_name}
              onChange={(e) => setF((p) => ({ ...p, event_name: e.target.value }))}
              className={inputCls}
              placeholder="e.g. Science Fair 2026"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Effective From *</label>
            <input
              type="date"
              value={f.effective_from}
              onChange={(e) => setF((p) => ({ ...p, effective_from: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Effective To</label>
            <input
              type="date"
              value={f.effective_to}
              onChange={(e) => setF((p) => ({ ...p, effective_to: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Notes</label>
          <textarea
            value={f.notes}
            onChange={(e) => setF((p) => ({ ...p, notes: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Maintenance Form Modal ──────────────────────────────────────────────────

function MaintenanceFormModal({
  open,
  onClose,
  task,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  task?: PreventiveMaintenance | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    title: task?.title ?? "",
    description: task?.description ?? "",
    category: task?.category ?? "general",
    building: task?.building ?? "",
    room: task?.room ?? "",
    frequency: task?.frequency ?? "monthly",
    status: task?.status ?? "active",
    last_completed: task?.last_completed ?? "",
    next_due: task?.next_due ?? "",
  });
  const isEdit = !!task;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/preventive-maintenance/", data),
    onSuccess: () => {
      toast.success("Maintenance task created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/preventive-maintenance/${task!.id}/`, data),
    onSuccess: () => {
      toast.success("Maintenance task updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.title.trim()) return toast.error("Title is required");
    if (!f.next_due) return toast.error("Next due date is required");
    const data = {
      ...f,
      building: f.building || null,
      room: f.room || null,
      last_completed: f.last_completed || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Maintenance Task" : "New Maintenance Task"}
    >
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>Title *</label>
          <input
            value={f.title}
            onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
            className={inputCls}
            required
          />
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <SelectField
            label="Category"
            value={f.category}
            options={WORK_ORDER_CATEGORIES}
            onChange={(v) => setF((p) => ({ ...p, category: v }))}
          />
          <SelectField
            label="Frequency"
            value={f.frequency}
            options={PM_FREQUENCIES}
            onChange={(v) => setF((p) => ({ ...p, frequency: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={PM_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value, room: "" }))}
              className={inputCls}
            >
              <option value="">None</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              disabled={!f.building}
            >
              <option value="">None</option>
              {buildingRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Next Due *</label>
            <input
              type="date"
              value={f.next_due}
              onChange={(e) => setF((p) => ({ ...p, next_due: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Last Completed</label>
            <input
              type="date"
              value={f.last_completed}
              onChange={(e) => setF((p) => ({ ...p, last_completed: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Reservation Form Modal ──────────────────────────────────────────────────

function ReservationFormModal({
  open,
  onClose,
  reservation,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  reservation?: SpaceReservation | null;
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    room: reservation?.room ?? "",
    title: reservation?.title ?? "",
    purpose: reservation?.purpose ?? "meeting",
    date: reservation?.date ?? "",
    start_time: reservation?.start_time ?? "09:00",
    end_time: reservation?.end_time ?? "10:00",
    attendees_count: reservation?.attendees_count ?? 0,
    status: reservation?.status ?? "pending",
    requires_av: reservation?.requires_av ?? false,
    requires_refreshments: reservation?.requires_refreshments ?? false,
    notes: reservation?.notes ?? "",
  });
  const isEdit = !!reservation;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/space-reservations/", data),
    onSuccess: () => {
      toast.success("Reservation created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/space-reservations/${reservation!.id}/`, data),
    onSuccess: () => {
      toast.success("Reservation updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.room) return toast.error("Select a room");
    if (!f.title.trim()) return toast.error("Title is required");
    if (!f.date) return toast.error("Date is required");
    if (!f.start_time || !f.end_time) return toast.error("Start and end times are required");
    const data = { ...f } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Reservation" : "New Reservation"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Room *</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              required
            >
              <option value="">Select room...</option>
              {rooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Title *</label>
            <input
              value={f.title}
              onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Purpose"
            value={f.purpose}
            options={RESERVATION_PURPOSES}
            onChange={(v) => setF((p) => ({ ...p, purpose: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={RESERVATION_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Date *</label>
            <input
              type="date"
              value={f.date}
              onChange={(e) => setF((p) => ({ ...p, date: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Start Time *</label>
            <input
              type="time"
              value={f.start_time}
              onChange={(e) => setF((p) => ({ ...p, start_time: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>End Time *</label>
            <input
              type="time"
              value={f.end_time}
              onChange={(e) => setF((p) => ({ ...p, end_time: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Attendees Count</label>
          <input
            type="number"
            min={0}
            value={f.attendees_count}
            onChange={(e) => setF((p) => ({ ...p, attendees_count: Number(e.target.value) }))}
            className={inputCls}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={f.requires_av}
              onChange={(e) => setF((p) => ({ ...p, requires_av: e.target.checked }))}
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
            />
            Requires AV equipment
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={f.requires_refreshments}
              onChange={(e) => setF((p) => ({ ...p, requires_refreshments: e.target.checked }))}
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
            />
            Requires refreshments
          </label>
        </div>
        <div>
          <label className={labelCls}>Notes</label>
          <textarea
            value={f.notes}
            onChange={(e) => setF((p) => ({ ...p, notes: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Energy Meter Form Modal ─────────────────────────────────────────────────

function MeterFormModal({
  open,
  onClose,
  meter,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  meter?: EnergyMeter | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: meter?.building ?? "",
    room: meter?.room ?? "",
    meter_number: meter?.meter_number ?? "",
    meter_type: meter?.meter_type ?? "electric",
    installation_date: meter?.installation_date ?? "",
    is_active: meter?.is_active ?? true,
    notes: meter?.notes ?? "",
  });
  const isEdit = !!meter;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/energy-meter/", data),
    onSuccess: () => {
      toast.success("Meter created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/infrastructure/energy-meter/${meter!.id}/`, data),
    onSuccess: () => {
      toast.success("Meter updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    if (!f.meter_number.trim()) return toast.error("Meter number is required");
    const data = {
      ...f,
      room: f.room || null,
      installation_date: f.installation_date || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Meter" : "Add Energy Meter"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building *</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value, room: "" }))}
              className={inputCls}
              required
            >
              <option value="">Select building...</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              disabled={!f.building}
            >
              <option value="">None</option>
              {buildingRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Meter Number *</label>
            <input
              value={f.meter_number}
              onChange={(e) => setF((p) => ({ ...p, meter_number: e.target.value }))}
              className={`${inputCls} font-mono`}
              placeholder="e.g. E-1001"
              required
            />
          </div>
          <SelectField
            label="Meter Type"
            value={f.meter_type}
            options={METER_TYPES}
            onChange={(v) => setF((p) => ({ ...p, meter_type: v }))}
          />
          <div>
            <label className={labelCls}>Installation Date</label>
            <input
              type="date"
              value={f.installation_date}
              onChange={(e) => setF((p) => ({ ...p, installation_date: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.is_active}
            onChange={(e) => setF((p) => ({ ...p, is_active: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
          />
          Meter is active
        </label>
        <div>
          <label className={labelCls}>Notes</label>
          <textarea
            value={f.notes}
            onChange={(e) => setF((p) => ({ ...p, notes: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Safety Inspection Form Modal ────────────────────────────────────────────

function InspectionFormModal({
  open,
  onClose,
  inspection,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  inspection?: SafetyInspection | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    title: inspection?.title ?? "",
    inspection_type: inspection?.inspection_type ?? "general",
    building: inspection?.building ?? "",
    room: inspection?.room ?? "",
    scheduled_date: inspection?.scheduled_date ?? "",
    completed_date: inspection?.completed_date ?? "",
    inspector_name: inspection?.inspector_name ?? "",
    inspector_organization: inspection?.inspector_organization ?? "",
    status: inspection?.status ?? "scheduled",
    overall_severity: inspection?.overall_severity ?? "none",
    findings: inspection?.findings ?? "",
    recommendations: inspection?.recommendations ?? "",
    corrective_actions: inspection?.corrective_actions ?? "",
    next_inspection_date: inspection?.next_inspection_date ?? "",
  });
  const isEdit = !!inspection;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/safety-inspections/", data),
    onSuccess: () => {
      toast.success("Inspection created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/safety-inspections/${inspection!.id}/`, data),
    onSuccess: () => {
      toast.success("Inspection updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.title.trim()) return toast.error("Title is required");
    if (!f.scheduled_date) return toast.error("Scheduled date is required");
    const data = {
      ...f,
      building: f.building || null,
      room: f.room || null,
      completed_date: f.completed_date || null,
      next_inspection_date: f.next_inspection_date || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Inspection" : "New Safety Inspection"}
    >
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>Title *</label>
          <input
            value={f.title}
            onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
            className={inputCls}
            required
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <SelectField
            label="Inspection Type"
            value={f.inspection_type}
            options={INSPECTION_TYPES}
            onChange={(v) => setF((p) => ({ ...p, inspection_type: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={INSPECTION_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
          <SelectField
            label="Severity"
            value={f.overall_severity}
            options={INSPECTION_SEVERITIES}
            onChange={(v) => setF((p) => ({ ...p, overall_severity: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value, room: "" }))}
              className={inputCls}
            >
              <option value="">None</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              disabled={!f.building}
            >
              <option value="">None</option>
              {buildingRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Scheduled Date *</label>
            <input
              type="date"
              value={f.scheduled_date}
              onChange={(e) => setF((p) => ({ ...p, scheduled_date: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Completed Date</label>
            <input
              type="date"
              value={f.completed_date}
              onChange={(e) => setF((p) => ({ ...p, completed_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Next Inspection</label>
            <input
              type="date"
              value={f.next_inspection_date}
              onChange={(e) => setF((p) => ({ ...p, next_inspection_date: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Inspector Name</label>
            <input
              value={f.inspector_name}
              onChange={(e) => setF((p) => ({ ...p, inspector_name: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Inspector Organization</label>
            <input
              value={f.inspector_organization}
              onChange={(e) => setF((p) => ({ ...p, inspector_organization: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Findings</label>
          <textarea
            value={f.findings}
            onChange={(e) => setF((p) => ({ ...p, findings: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls}>Recommendations</label>
          <textarea
            value={f.recommendations}
            onChange={(e) => setF((p) => ({ ...p, recommendations: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Vendor Contract Form Modal ──────────────────────────────────────────────

function VendorFormModal({
  open,
  onClose,
  contract,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  contract?: VendorContract | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    vendor_name: contract?.vendor_name ?? "",
    contract_type: contract?.contract_type ?? "other",
    title: contract?.title ?? "",
    description: contract?.description ?? "",
    contract_number: contract?.contract_number ?? "",
    start_date: contract?.start_date ?? "",
    end_date: contract?.end_date ?? "",
    renewal_date: contract?.renewal_date ?? "",
    auto_renew: contract?.auto_renew ?? false,
    value: contract?.value != null ? String(contract.value) : "",
    payment_frequency: contract?.payment_frequency ?? "",
    contact_person: contract?.contact_person ?? "",
    contact_phone: contract?.contact_phone ?? "",
    contact_email: contract?.contact_email ?? "",
    sla_description: contract?.sla_description ?? "",
    status: contract?.status ?? "draft",
  });
  const isEdit = !!contract;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/vendor-contracts/", data),
    onSuccess: () => {
      toast.success("Contract created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/vendor-contracts/${contract!.id}/`, data),
    onSuccess: () => {
      toast.success("Contract updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.vendor_name.trim()) return toast.error("Vendor name is required");
    if (!f.title.trim()) return toast.error("Title is required");
    if (!f.start_date || !f.end_date) return toast.error("Start and end dates are required");
    const data = {
      ...f,
      value: f.value ? Number(f.value) : 0,
      renewal_date: f.renewal_date || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Contract" : "New Vendor Contract"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Vendor Name *</label>
            <input
              value={f.vendor_name}
              onChange={(e) => setF((p) => ({ ...p, vendor_name: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Title *</label>
            <input
              value={f.title}
              onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <SelectField
            label="Contract Type"
            value={f.contract_type}
            options={CONTRACT_TYPES}
            onChange={(v) => setF((p) => ({ ...p, contract_type: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={CONTRACT_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
          <div>
            <label className={labelCls}>Contract #</label>
            <input
              value={f.contract_number}
              onChange={(e) => setF((p) => ({ ...p, contract_number: e.target.value }))}
              className={inputCls}
              placeholder="e.g. VC-2026-001"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Start Date *</label>
            <input
              type="date"
              value={f.start_date}
              onChange={(e) => setF((p) => ({ ...p, start_date: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>End Date *</label>
            <input
              type="date"
              value={f.end_date}
              onChange={(e) => setF((p) => ({ ...p, end_date: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Renewal Date</label>
            <input
              type="date"
              value={f.renewal_date}
              onChange={(e) => setF((p) => ({ ...p, renewal_date: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Value</label>
            <input
              type="number"
              min={0}
              step={0.01}
              value={f.value}
              onChange={(e) => setF((p) => ({ ...p, value: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Payment Frequency</label>
            <input
              value={f.payment_frequency}
              onChange={(e) => setF((p) => ({ ...p, payment_frequency: e.target.value }))}
              className={inputCls}
              placeholder="e.g. Monthly, Quarterly, Annual"
            />
          </div>
          <div>
            <label className={labelCls}>Contact Person</label>
            <input
              value={f.contact_person}
              onChange={(e) => setF((p) => ({ ...p, contact_person: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Contact Phone</label>
            <input
              value={f.contact_phone}
              onChange={(e) => setF((p) => ({ ...p, contact_phone: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Contact Email</label>
            <input
              type="email"
              value={f.contact_email}
              onChange={(e) => setF((p) => ({ ...p, contact_email: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.auto_renew}
            onChange={(e) => setF((p) => ({ ...p, auto_renew: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
          />
          Auto-renew
        </label>
        <div>
          <label className={labelCls}>SLA Description</label>
          <textarea
            value={f.sla_description}
            onChange={(e) => setF((p) => ({ ...p, sla_description: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls}>Description</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Parking Lot Form Modal ──────────────────────────────────────────────────

function ParkingLotFormModal({
  open,
  onClose,
  lot,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  lot?: ParkingLot | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    name: lot?.name ?? "",
    total_spots: lot?.total_spots ?? 0,
    available_spots: lot ? lot.available_spots : undefined,
    is_covered: lot?.is_covered ?? false,
    is_active: lot?.is_active ?? true,
  });
  const isEdit = !!lot;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/parking-lot/", data),
    onSuccess: () => {
      toast.success("Parking lot created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/infrastructure/parking-lot/${lot!.id}/`, data),
    onSuccess: () => {
      toast.success("Parking lot updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.name.trim()) return toast.error("Lot name is required");
    const data = {
      name: f.name,
      total_spots: Number(f.total_spots) || 0,
      available_spots:
        f.available_spots === undefined
          ? Number(f.total_spots) || 0
          : Number(f.available_spots) || 0,
      is_covered: f.is_covered,
      is_active: f.is_active,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Parking Lot" : "Add Parking Lot"}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>Name *</label>
          <input
            value={f.name}
            onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
            className={inputCls}
            required
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Total Spots</label>
            <input
              type="number"
              min={0}
              value={f.total_spots}
              onChange={(e) => setF((p) => ({ ...p, total_spots: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Available Spots</label>
            <input
              type="number"
              min={0}
              value={f.available_spots ?? ""}
              onChange={(e) =>
                setF((p) => ({
                  ...p,
                  available_spots: e.target.value ? Number(e.target.value) : 0,
                }))
              }
              className={inputCls}
              placeholder="Defaults to total"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={f.is_covered}
              onChange={(e) => setF((p) => ({ ...p, is_covered: e.target.checked }))}
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
            />
            Covered lot
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={f.is_active}
              onChange={(e) => setF((p) => ({ ...p, is_active: e.target.checked }))}
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
            />
            Active
          </label>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Parking Assignment Form Modal ───────────────────────────────────────────

function SpotFormModal({
  open,
  onClose,
  assignment,
  lots,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  assignment?: ParkingAssignment | null;
  lots: ParkingLot[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    parking_lot: assignment?.parking_lot ?? "",
    spot_number: assignment?.spot_number ?? "",
    spot_type: assignment?.spot_type ?? "regular",
    vehicle_plate: assignment?.vehicle_plate ?? "",
    is_active: assignment?.is_active ?? true,
    start_date: assignment?.start_date ?? "",
    end_date: assignment?.end_date ?? "",
  });
  const isEdit = !!assignment;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/parking-assignment/", data),
    onSuccess: () => {
      toast.success("Spot assigned");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/parking-assignment/${assignment!.id}/`, data),
    onSuccess: () => {
      toast.success("Assignment updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.parking_lot) return toast.error("Select a parking lot");
    if (!f.spot_number.trim()) return toast.error("Spot number is required");
    const data = {
      ...f,
      start_date: f.start_date || null,
      end_date: f.end_date || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Assignment" : "Assign Spot"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Parking Lot *</label>
            <select
              value={f.parking_lot}
              onChange={(e) => setF((p) => ({ ...p, parking_lot: e.target.value }))}
              className={inputCls}
              required
            >
              <option value="">Select lot...</option>
              {lots.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Spot Number *</label>
            <input
              value={f.spot_number}
              onChange={(e) => setF((p) => ({ ...p, spot_number: e.target.value }))}
              className={`${inputCls} font-mono`}
              placeholder="e.g. A-01"
              required
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Spot Type"
            value={f.spot_type}
            options={SPOT_TYPES}
            onChange={(v) => setF((p) => ({ ...p, spot_type: v }))}
          />
          <div>
            <label className={labelCls}>Vehicle Plate</label>
            <input
              value={f.vehicle_plate}
              onChange={(e) => setF((p) => ({ ...p, vehicle_plate: e.target.value }))}
              className={`${inputCls} font-mono`}
              placeholder="e.g. ABC-123"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Start Date</label>
            <input
              type="date"
              value={f.start_date}
              onChange={(e) => setF((p) => ({ ...p, start_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>End Date</label>
            <input
              type="date"
              value={f.end_date}
              onChange={(e) => setF((p) => ({ ...p, end_date: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.is_active}
            onChange={(e) => setF((p) => ({ ...p, is_active: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
          />
          Assignment is active
        </label>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Energy Reading Form Modal ───────────────────────────────────────────────

function ReadingFormModal({
  open,
  onClose,
  reading,
  meters,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  reading?: EnergyReading | null;
  meters: EnergyMeter[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    meter: reading?.meter ?? "",
    reading_date: reading?.reading_date ?? "",
    reading_value: reading?.reading_value != null ? String(reading.reading_value) : "",
    units: reading?.units ?? "",
    cost: reading?.cost != null ? String(reading.cost) : "",
    notes: reading?.notes ?? "",
  });
  const isEdit = !!reading;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/energy-reading/", data),
    onSuccess: () => {
      toast.success("Reading recorded");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/energy-reading/${reading!.id}/`, data),
    onSuccess: () => {
      toast.success("Reading updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.meter) return toast.error("Select a meter");
    if (!f.reading_date) return toast.error("Reading date is required");
    if (!f.reading_value) return toast.error("Reading value is required");
    const data = {
      ...f,
      reading_value: Number(f.reading_value),
      cost: f.cost ? Number(f.cost) : null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Reading" : "Record Reading"}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>Meter *</label>
          <select
            value={f.meter}
            onChange={(e) => setF((p) => ({ ...p, meter: e.target.value }))}
            className={inputCls}
            required
          >
            <option value="">Select meter...</option>
            {meters.map((m) => (
              <option key={m.id} value={m.id}>
                {m.meter_number} ({m.meter_type})
              </option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Reading Date *</label>
            <input
              type="date"
              value={f.reading_date}
              onChange={(e) => setF((p) => ({ ...p, reading_date: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Reading Value *</label>
            <input
              type="number"
              min={0}
              step={0.01}
              value={f.reading_value}
              onChange={(e) => setF((p) => ({ ...p, reading_value: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Units</label>
            <input
              value={f.units}
              onChange={(e) => setF((p) => ({ ...p, units: e.target.value }))}
              className={inputCls}
              placeholder="e.g. kWh"
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Cost</label>
          <input
            type="number"
            min={0}
            step={0.01}
            value={f.cost}
            onChange={(e) => setF((p) => ({ ...p, cost: e.target.value }))}
            className={inputCls}
          />
        </div>
        <div>
          <label className={labelCls}>Notes</label>
          <textarea
            value={f.notes}
            onChange={(e) => setF((p) => ({ ...p, notes: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Energy Alert Form Modal ─────────────────────────────────────────────────

function AlertFormModal({
  open,
  onClose,
  alert,
  buildings,
  meters,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  alert?: EnergyAlert | null;
  buildings: Building[];
  meters: EnergyMeter[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: alert?.building ?? "",
    meter: alert?.meter ?? "",
    alert_type: alert?.alert_type ?? "high",
    severity: alert?.severity ?? "medium",
    status: alert?.status ?? "active",
    description: alert?.description ?? "",
    threshold_value: alert?.threshold_value != null ? String(alert.threshold_value) : "",
    actual_value: alert?.actual_value != null ? String(alert.actual_value) : "",
    resolution_notes: alert?.resolution_notes ?? "",
  });
  const isEdit = !!alert;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/energy-alert/", data),
    onSuccess: () => {
      toast.success("Alert raised");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/infrastructure/energy-alert/${alert!.id}/`, data),
    onSuccess: () => {
      toast.success("Alert updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    if (!f.description.trim()) return toast.error("Description is required");
    const data = {
      ...f,
      meter: f.meter || null,
      threshold_value: f.threshold_value ? Number(f.threshold_value) : null,
      actual_value: f.actual_value ? Number(f.actual_value) : null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingMeters = meters.filter((m) => m.building === f.building);
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Alert" : "Raise Energy Alert"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building *</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value, meter: "" }))}
              className={inputCls}
              required
            >
              <option value="">Select building...</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Meter</label>
            <select
              value={f.meter}
              onChange={(e) => setF((p) => ({ ...p, meter: e.target.value }))}
              className={inputCls}
              disabled={!f.building}
            >
              <option value="">None</option>
              {buildingMeters.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.meter_number}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <SelectField
            label="Alert Type"
            value={f.alert_type}
            options={ALERT_TYPES}
            onChange={(v) => setF((p) => ({ ...p, alert_type: v }))}
          />
          <SelectField
            label="Severity"
            value={f.severity}
            options={ALERT_SEVERITIES}
            onChange={(v) => setF((p) => ({ ...p, severity: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={ALERT_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div>
          <label className={labelCls}>Description *</label>
          <textarea
            value={f.description}
            onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
            rows={2}
            className={inputCls}
            required
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Threshold Value</label>
            <input
              type="number"
              step={0.01}
              value={f.threshold_value}
              onChange={(e) => setF((p) => ({ ...p, threshold_value: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Actual Value</label>
            <input
              type="number"
              step={0.01}
              value={f.actual_value}
              onChange={(e) => setF((p) => ({ ...p, actual_value: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Resolution Notes</label>
          <textarea
            value={f.resolution_notes}
            onChange={(e) => setF((p) => ({ ...p, resolution_notes: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── CCTV Camera Form Modal ──────────────────────────────────────────────────

function CameraFormModal({
  open,
  onClose,
  camera,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  camera?: CCTVCamera | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: camera?.building ?? "",
    room: camera?.room ?? "",
    camera_name: camera?.camera_name ?? "",
    camera_id: camera?.camera_id ?? "",
    location_description: camera?.location_description ?? "",
    stream_url: camera?.stream_url ?? "",
    recording_enabled: camera?.recording_enabled ?? true,
    storage_days: camera?.storage_days ?? 30,
    status: camera?.status ?? "online",
    installation_date: camera?.installation_date ?? "",
    last_maintenance: camera?.last_maintenance ?? "",
    notes: camera?.notes ?? "",
  });
  const isEdit = !!camera;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/c-c-t-v-camera/", data),
    onSuccess: () => {
      toast.success("Camera added");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/c-c-t-v-camera/${camera!.id}/`, data),
    onSuccess: () => {
      toast.success("Camera updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    if (!f.camera_name.trim()) return toast.error("Camera name is required");
    if (!f.camera_id.trim()) return toast.error("Camera ID is required");
    const data = {
      ...f,
      room: f.room || null,
      installation_date: f.installation_date || null,
      last_maintenance: f.last_maintenance || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Camera" : "Add CCTV Camera"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building *</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value, room: "" }))}
              className={inputCls}
              required
            >
              <option value="">Select building...</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              disabled={!f.building}
            >
              <option value="">None</option>
              {buildingRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Camera Name *</label>
            <input
              value={f.camera_name}
              onChange={(e) => setF((p) => ({ ...p, camera_name: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Camera ID *</label>
            <input
              value={f.camera_id}
              onChange={(e) => setF((p) => ({ ...p, camera_id: e.target.value }))}
              className={`${inputCls} font-mono`}
              placeholder="e.g. CAM-001"
              required
            />
          </div>
          <SelectField
            label="Status"
            value={f.status}
            options={CAMERA_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Location Description</label>
            <input
              value={f.location_description}
              onChange={(e) => setF((p) => ({ ...p, location_description: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Storage (days)</label>
            <input
              type="number"
              min={0}
              value={f.storage_days}
              onChange={(e) => setF((p) => ({ ...p, storage_days: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Installation Date</label>
            <input
              type="date"
              value={f.installation_date}
              onChange={(e) => setF((p) => ({ ...p, installation_date: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Stream URL</label>
          <input
            type="url"
            value={f.stream_url}
            onChange={(e) => setF((p) => ({ ...p, stream_url: e.target.value }))}
            className={inputCls}
            placeholder="https://..."
          />
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.recording_enabled}
            onChange={(e) => setF((p) => ({ ...p, recording_enabled: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
          />
          Recording enabled
        </label>
        <div>
          <label className={labelCls}>Notes</label>
          <textarea
            value={f.notes}
            onChange={(e) => setF((p) => ({ ...p, notes: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Access Control Form Modal ───────────────────────────────────────────────

function AccessFormModal({
  open,
  onClose,
  access,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  access?: AccessControlPoint | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: access?.building ?? "",
    room: access?.room ?? "",
    point_name: access?.point_name ?? "",
    access_type: access?.access_type ?? "card",
    status: access?.status ?? "active",
    access_start_time: access?.access_start_time ?? "",
    access_end_time: access?.access_end_time ?? "",
    restricted_access: access?.restricted_access ?? false,
    installation_date: access?.installation_date ?? "",
    last_maintenance: access?.last_maintenance ?? "",
    notes: access?.notes ?? "",
  });
  const isEdit = !!access;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/access-control-point/", data),
    onSuccess: () => {
      toast.success("Access point created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/access-control-point/${access!.id}/`, data),
    onSuccess: () => {
      toast.success("Access point updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    if (!f.point_name.trim()) return toast.error("Point name is required");
    const data = {
      ...f,
      room: f.room || null,
      access_start_time: f.access_start_time || null,
      access_end_time: f.access_end_time || null,
      installation_date: f.installation_date || null,
      last_maintenance: f.last_maintenance || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Access Point" : "Add Access Point"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building *</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value, room: "" }))}
              className={inputCls}
              required
            >
              <option value="">Select building...</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              disabled={!f.building}
            >
              <option value="">None</option>
              {buildingRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Point Name *</label>
            <input
              value={f.point_name}
              onChange={(e) => setF((p) => ({ ...p, point_name: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <SelectField
            label="Access Type"
            value={f.access_type}
            options={ACCESS_TYPES}
            onChange={(v) => setF((p) => ({ ...p, access_type: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={ACCESS_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Access Start Time</label>
            <input
              type="time"
              value={f.access_start_time}
              onChange={(e) => setF((p) => ({ ...p, access_start_time: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Access End Time</label>
            <input
              type="time"
              value={f.access_end_time}
              onChange={(e) => setF((p) => ({ ...p, access_end_time: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.restricted_access}
            onChange={(e) => setF((p) => ({ ...p, restricted_access: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
          />
          Restricted access
        </label>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Installation Date</label>
            <input
              type="date"
              value={f.installation_date}
              onChange={(e) => setF((p) => ({ ...p, installation_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Last Maintenance</label>
            <input
              type="date"
              value={f.last_maintenance}
              onChange={(e) => setF((p) => ({ ...p, last_maintenance: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Notes</label>
          <textarea
            value={f.notes}
            onChange={(e) => setF((p) => ({ ...p, notes: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Waste Collection Form Modal ─────────────────────────────────────────────

function WasteFormModal({
  open,
  onClose,
  schedule,
  buildings,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  schedule?: WasteSchedule | null;
  buildings: Building[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: schedule?.building ?? "",
    waste_type: schedule?.waste_type ?? "general",
    frequency: schedule?.frequency ?? "weekly",
    collection_day: schedule?.collection_day ?? "",
    collection_time: schedule?.collection_time ?? "",
    vendor_name: schedule?.vendor_name ?? "",
    is_active: schedule?.is_active ?? true,
  });
  const isEdit = !!schedule;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/waste-collection-schedule/", data),
    onSuccess: () => {
      toast.success("Schedule created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/waste-collection-schedule/${schedule!.id}/`, data),
    onSuccess: () => {
      toast.success("Schedule updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    const data = { ...f, collection_time: f.collection_time || null } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Schedule" : "Add Waste Schedule"}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>Building *</label>
          <select
            value={f.building}
            onChange={(e) => setF((p) => ({ ...p, building: e.target.value }))}
            className={inputCls}
            required
          >
            <option value="">Select building...</option>
            {buildings.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <SelectField
            label="Waste Type"
            value={f.waste_type}
            options={WASTE_TYPES}
            onChange={(v) => setF((p) => ({ ...p, waste_type: v }))}
          />
          <SelectField
            label="Frequency"
            value={f.frequency}
            options={WASTE_FREQUENCIES}
            onChange={(v) => setF((p) => ({ ...p, frequency: v }))}
          />
          <div>
            <label className={labelCls}>Collection Day</label>
            <input
              value={f.collection_day}
              onChange={(e) => setF((p) => ({ ...p, collection_day: e.target.value }))}
              className={inputCls}
              placeholder="e.g. Monday"
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Collection Time</label>
            <input
              type="time"
              value={f.collection_time}
              onChange={(e) => setF((p) => ({ ...p, collection_time: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Vendor</label>
            <input
              value={f.vendor_name}
              onChange={(e) => setF((p) => ({ ...p, vendor_name: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.is_active}
            onChange={(e) => setF((p) => ({ ...p, is_active: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
          />
          Schedule is active
        </label>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// ─── Lighting Schedule Form Modal ────────────────────────────────────────────

function LightingFormModal({
  open,
  onClose,
  schedule,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  schedule?: LightingSchedule | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: schedule?.building ?? "",
    room: schedule?.room ?? "",
    zone_name: schedule?.zone_name ?? "",
    day_of_week: schedule?.day_of_week ?? "",
    on_time: schedule?.on_time ?? "",
    off_time: schedule?.off_time ?? "",
    brightness_level: schedule?.brightness_level ?? 100,
    is_active: schedule?.is_active ?? true,
  });
  const isEdit = !!schedule;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/lighting-schedule/", data),
    onSuccess: () => {
      toast.success("Lighting schedule created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/lighting-schedule/${schedule!.id}/`, data),
    onSuccess: () => {
      toast.success("Lighting schedule updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    if (!f.on_time || !f.off_time) return toast.error("On and off times are required");
    const data = {
      ...f,
      room: f.room || null,
      on_time: f.on_time || null,
      off_time: f.off_time || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Schedule" : "Add Lighting Schedule"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building *</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value, room: "" }))}
              className={inputCls}
              required
            >
              <option value="">Select building...</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Room</label>
            <select
              value={f.room}
              onChange={(e) => setF((p) => ({ ...p, room: e.target.value }))}
              className={inputCls}
              disabled={!f.building}
            >
              <option value="">None</option>
              {buildingRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_number})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Zone Name</label>
            <input
              value={f.zone_name}
              onChange={(e) => setF((p) => ({ ...p, zone_name: e.target.value }))}
              className={inputCls}
              placeholder="e.g. Hallway A"
            />
          </div>
          <div>
            <label className={labelCls}>Day of Week</label>
            <input
              value={f.day_of_week}
              onChange={(e) => setF((p) => ({ ...p, day_of_week: e.target.value }))}
              className={inputCls}
              placeholder="e.g. weekdays"
            />
          </div>
          <div>
            <label className={labelCls}>Brightness (%)</label>
            <input
              type="number"
              min={0}
              max={100}
              value={f.brightness_level}
              onChange={(e) => setF((p) => ({ ...p, brightness_level: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>On Time *</label>
            <input
              type="time"
              value={f.on_time}
              onChange={(e) => setF((p) => ({ ...p, on_time: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Off Time *</label>
            <input
              type="time"
              value={f.off_time}
              onChange={(e) => setF((p) => ({ ...p, off_time: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.is_active}
            onChange={(e) => setF((p) => ({ ...p, is_active: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
          />
          Schedule is active
        </label>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            {isEdit ? "Update" : "Create"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
