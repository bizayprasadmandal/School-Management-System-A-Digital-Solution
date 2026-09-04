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
  ChatBubbleLeftRightIcon,
  UsersIcon,
  ListBulletIcon,
  ShieldExclamationIcon,
  BeakerIcon,
  DocumentCheckIcon,
  LifebuoyIcon,
  DocumentChartBarIcon,
  BugAntIcon,
  SparklesIcon,
  StarIcon,
  ClipboardDocumentListIcon,
  BellAlertIcon,
  SunIcon,
  CloudIcon,
  MapIcon,
  ComputerDesktopIcon,
  CurrencyDollarIcon,
  WrenchIcon,
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

interface WorkOrderComment {
  id: string;
  work_order: string;
  work_order_title?: string;
  author_name?: string;
  comment: string;
  created_at: string;
}

interface AssetAssignment {
  id: string;
  asset: string;
  asset_name?: string;
  asset_tag?: string;
  assigned_to_name?: string;
  room: string | null;
  room_name?: string;
  department: string;
  assigned_date: string | null;
  returned_date: string | null;
  status: string;
  status_display?: string;
  condition_at_assignment: string;
  condition_at_return: string;
  notes: string;
}

interface AssetLifecycle {
  id: string;
  asset: string;
  asset_name?: string;
  asset_tag?: string;
  event: string;
  event_display?: string;
  event_date: string | null;
  description: string;
  cost: string | number | null;
  performed_by_name?: string;
  notes: string;
}

interface WarrantyClaim {
  id: string;
  asset: string;
  asset_name?: string;
  asset_tag?: string;
  claim_number: string;
  issue_description: string;
  claim_date: string | null;
  warranty_provider: string;
  contact_person: string;
  contact_phone: string;
  contact_email: string;
  status: string;
  status_display?: string;
  resolution_date: string | null;
  resolution_notes: string;
  cost_covered: string | number | null;
  cost_customer: string | number | null;
}

interface UtilityRecord {
  id: string;
  building: string;
  building_name?: string;
  utility_type: string;
  utility_type_display?: string;
  reading_date: string | null;
  reading_value: string | number | null;
  units: string;
  cost: string | number | null;
  previous_reading: string | number | null;
  consumption: string | number | null;
  notes: string;
  recorded_by_name?: string;
}

interface ComplianceRecord {
  id: string;
  title: string;
  compliance_type: string;
  compliance_type_display?: string;
  description: string;
  regulation_reference: string;
  status: string;
  status_display?: string;
  last_audit_date: string | null;
  next_audit_date: string | null;
  expiry_date: string | null;
  responsible_person_name?: string;
  document_url: string;
}

interface EmergencyPlan {
  id: string;
  title: string;
  plan_type: string;
  plan_type_display?: string;
  description: string;
  procedures: string;
  assembly_points: string;
  emergency_contacts: string;
  last_drill_date: string | null;
  next_drill_date: string | null;
  last_review_date: string | null;
  is_active: boolean;
  reviewed_by_name?: string;
}

interface InfraReport {
  id: string;
  title: string;
  report_type: string;
  report_type_display?: string;
  description: string;
  date_from: string | null;
  date_to: string | null;
  summary: string;
  generated_by_name?: string;
  file_url: string;
}

interface PestInspection {
  id: string;
  building: string;
  building_name?: string;
  room: string | null;
  room_name?: string;
  inspection_type: string;
  inspection_type_display?: string;
  status: string;
  status_display?: string;
  scheduled_date: string | null;
  completed_date: string | null;
  inspector_name: string;
  pests_found: string;
  treatment_applied: string;
  follow_up_required: boolean;
  treatment_cost: string | number | null;
}

interface PestTreatment {
  id: string;
  building: string;
  building_name?: string;
  treatment_date: string | null;
  treatment_type: string;
  pest_target: string;
  chemical_name: string;
  safety_re_entry_hours: number;
  cost: string | number | null;
  notes: string;
}

interface GreenInitiative {
  id: string;
  building: string | null;
  building_name?: string;
  title: string;
  description: string;
  initiative_type: string;
  initiative_type_display?: string;
  status: string;
  status_display?: string;
  estimated_cost: string | number | null;
  estimated_savings: string | number | null;
  carbon_reduction_kg: string | number | null;
  start_date: string | null;
  target_end_date: string | null;
  proposed_by_name?: string;
}

interface WaterUsage {
  id: string;
  building: string;
  building_name?: string;
  record_date: string | null;
  usage_gallons: string | number | null;
  cost: string | number | null;
  leak_detected: boolean;
  notes: string;
}

interface VendorRating {
  id: string;
  vendor_contract: string;
  vendor_contract_name?: string;
  service_type: string;
  service_type_display?: string;
  evaluation_date: string | null;
  evaluator_name?: string;
  quality_rating: number;
  timeliness_rating: number;
  communication_rating: number;
  value_rating: number;
  comments: string;
  would_rehire: boolean | null;
}

interface BuildingInspection {
  id: string;
  building: string;
  building_name?: string;
  inspection_type: string;
  inspection_type_display?: string;
  inspection_date: string | null;
  inspector_name: string;
  result: string;
  result_display?: string;
  findings: string;
  violations: string;
  follow_up_required: boolean;
  follow_up_date: string | null;
  corrective_actions: string;
  recorded_by_name?: string;
}

interface InfraAlert {
  id: string;
  building: string | null;
  building_name?: string;
  room: string | null;
  room_name?: string;
  alert_type: string;
  alert_type_display?: string;
  severity: string;
  severity_display?: string;
  status: string;
  status_display?: string;
  title: string;
  description: string;
  reported_by_name?: string;
  assigned_to_name?: string;
}

interface FloorPlan {
  id: string;
  building: string;
  building_name?: string;
  floor_number: number;
  floor_name: string;
  plan_file: string;
  total_rooms: number;
  total_area_sqft: string | number | null;
  description: string;
  is_current: boolean;
  uploaded_by_name?: string;
}

interface RoomEquipment {
  id: string;
  room: string;
  room_name?: string;
  equipment_type: string;
  equipment_type_display?: string;
  name: string;
  asset_tag: string;
  brand: string;
  status: string;
  status_display?: string;
  purchase_date: string | null;
  warranty_expiry: string | null;
  last_maintenance: string | null;
  notes: string;
}

interface CostRecord {
  id: string;
  building: string | null;
  building_name?: string;
  work_order: string | null;
  work_order_title?: string;
  cost_category: string;
  cost_category_display?: string;
  amount: string | number | null;
  vendor: string;
  cost_date: string | null;
  is_approved: boolean;
  approved_by_name?: string;
  notes: string;
}

interface MaintRequest {
  id: string;
  building: string | null;
  building_name?: string;
  room: string | null;
  room_name?: string;
  requested_by_name?: string;
  title: string;
  description: string;
  priority: string;
  priority_display?: string;
  status: string;
  status_display?: string;
  assigned_to_name?: string;
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

const ASSIGNMENT_STATUSES = [
  ["active", "Active"],
  ["returned", "Returned"],
  ["lost", "Lost"],
  ["damaged", "Damaged"],
] as const;

const LIFECYCLE_EVENTS = [
  ["purchased", "Purchased"],
  ["received", "Received"],
  ["assigned", "Assigned"],
  ["maintenance", "Maintenance"],
  ["repaired", "Repaired"],
  ["transferred", "Transferred"],
  ["inspected", "Inspected"],
  ["written_off", "Written Off"],
  ["disposed", "Disposed"],
] as const;

const WARRANTY_STATUSES = [
  ["open", "Open"],
  ["submitted", "Submitted"],
  ["approved", "Approved"],
  ["denied", "Denied"],
  ["resolved", "Resolved"],
] as const;

const UTILITY_TYPES = [
  ["electricity", "Electricity"],
  ["water", "Water"],
  ["gas", "Gas"],
  ["internet", "Internet"],
  ["phone", "Phone"],
  ["other", "Other"],
] as const;

const COMPLIANCE_TYPES = [
  ["fire_safety", "Fire Safety"],
  ["building_code", "Building Code"],
  ["accessibility", "Accessibility (ADA)"],
  ["environmental", "Environmental"],
  ["health", "Health & Safety"],
  ["data_privacy", "Data Privacy"],
  ["employment", "Employment Law"],
  ["food_safety", "Food Safety"],
] as const;

const COMPLIANCE_STATUSES = [
  ["compliant", "Compliant"],
  ["non_compliant", "Non-Compliant"],
  ["in_progress", "In Progress"],
  ["exempt", "Exempt"],
] as const;

const PLAN_TYPES = [
  ["fire", "Fire Emergency"],
  ["lockdown", "Lockdown"],
  ["evacuation", "Evacuation"],
  ["medical", "Medical Emergency"],
  ["natural_disaster", "Natural Disaster"],
  ["chemical_spill", "Chemical Spill"],
  ["power_outage", "Power Outage"],
  ["active_threat", "Active Threat"],
] as const;

const REPORT_TYPES = [
  ["work_order_summary", "Work Order Summary"],
  ["asset_summary", "Asset Summary"],
  ["utilization", "Room Utilization"],
  ["utility_usage", "Utility Usage"],
  ["safety_compliance", "Safety & Compliance"],
  ["maintenance_cost", "Maintenance Cost"],
  ["asset_depreciation", "Asset Depreciation"],
  ["general", "General Report"],
] as const;

const PEST_INSPECTION_TYPES = [
  ["routine", "Routine"],
  ["requested", "Requested"],
  ["follow_up", "Follow-up"],
] as const;

const PEST_STATUSES = [
  ["scheduled", "Scheduled"],
  ["completed", "Completed"],
] as const;

const INITIATIVE_TYPES = [
  ["solar", "Solar Energy"],
  ["rainwater", "Rainwater Harvesting"],
  ["waste", "Waste Reduction"],
  ["tree", "Tree Plantation"],
  ["audit", "Energy Audit"],
  ["other", "Other"],
] as const;

const INITIATIVE_STATUSES = [
  ["proposed", "Proposed"],
  ["approved", "Approved"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
] as const;

const BUILDING_INSPECTION_TYPES = [
  ["fire", "Fire Safety"],
  ["structural", "Structural"],
  ["electrical", "Electrical Safety"],
  ["plumbing", "Plumbing"],
  ["accessibility", "Accessibility"],
  ["general", "General"],
] as const;

const BUILDING_INSPECTION_RESULTS = [
  ["pass", "Pass"],
  ["conditional", "Conditional"],
  ["fail", "Fail"],
  ["pending", "Pending"],
] as const;

const INFRA_ALERT_TYPES = [
  ["power", "Power Outage"],
  ["water", "Water Leak"],
  ["hvac", "HVAC Failure"],
  ["structural", "Structural Issue"],
  ["flooding", "Flooding"],
  ["fire", "Fire"],
  ["gas", "Gas Leak"],
  ["other", "Other"],
] as const;

const INFRA_ALERT_SEVERITIES = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
  ["critical", "Critical"],
] as const;

const INFRA_ALERT_STATUSES = [
  ["active", "Active"],
  ["in_progress", "In Progress"],
  ["resolved", "Resolved"],
] as const;

const EQUIPMENT_TYPES = [
  ["projector", "Projector"],
  ["whiteboard", "Whiteboard"],
  ["computer", "Computer"],
  ["ac", "Air Conditioning"],
  ["smartboard", "Smart Board"],
  ["other", "Other"],
] as const;

const EQUIPMENT_STATUSES = [
  ["working", "Working"],
  ["maintenance", "Under Maintenance"],
  ["broken", "Broken"],
] as const;

const COST_CATEGORIES = [
  ["electrical", "Electrical"],
  ["plumbing", "Plumbing"],
  ["hvac", "HVAC"],
  ["roofing", "Roofing"],
  ["painting", "Painting"],
  ["landscaping", "Landscaping"],
  ["cleaning", "Cleaning"],
  ["general", "General"],
] as const;

const REQUEST_PRIORITIES = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
  ["emergency", "Emergency"],
] as const;

const REQUEST_STATUSES = [
  ["open", "Open"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
] as const;

const SERVICE_TYPES = [
  ["cleaning", "Cleaning"],
  ["electrical", "Electrical"],
  ["plumbing", "Plumbing"],
  ["hvac", "HVAC"],
  ["pest", "Pest Control"],
  ["other", "Other"],
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
  returned: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  submitted: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  approved: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  denied: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  lost: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  working: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  broken: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  compliant: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  non_compliant: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  exempt: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  proposed: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  conditional: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  pending: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  pass: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  fail: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

const SEVERITY_COLORS: Record<string, string> = {
  none: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  low: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

const TAB_LABELS: Record<string, { plural: string; singular: string }> = {
  buildings: { plural: "buildings", singular: "building" },
  rooms: { plural: "rooms", singular: "room" },
  workorders: { plural: "work orders", singular: "work order" },
  assets: { plural: "assets", singular: "asset" },
  allocations: { plural: "room allocations", singular: "room allocation" },
  maintenance: { plural: "maintenance tasks", singular: "maintenance task" },
  reservations: { plural: "reservations", singular: "reservation" },
  energy: { plural: "energy meters", singular: "energy meter" },
  readings: { plural: "energy readings", singular: "energy reading" },
  alerts: { plural: "energy alerts", singular: "energy alert" },
  inspections: { plural: "inspections", singular: "inspection" },
  vendors: { plural: "vendor contracts", singular: "vendor contract" },
  cameras: { plural: "cameras", singular: "camera" },
  access: { plural: "access points", singular: "access point" },
  waste: { plural: "waste schedules", singular: "waste schedule" },
  lighting: { plural: "lighting schedules", singular: "lighting schedule" },
  parking: { plural: "parking lots", singular: "parking lot" },
  spots: { plural: "spot assignments", singular: "spot assignment" },
  comments: { plural: "comments", singular: "comment" },
  assignments: { plural: "asset assignments", singular: "asset assignment" },
  lifecycle: { plural: "lifecycle events", singular: "lifecycle event" },
  warranty: { plural: "warranty claims", singular: "warranty claim" },
  utilities: { plural: "utility records", singular: "utility record" },
  compliance: { plural: "compliance records", singular: "compliance record" },
  emergency: { plural: "emergency plans", singular: "emergency plan" },
  reports: { plural: "reports", singular: "report" },
  pestinsp: { plural: "pest inspections", singular: "pest inspection" },
  pesttreat: { plural: "pest treatments", singular: "pest treatment" },
  green: { plural: "green initiatives", singular: "green initiative" },
  water: { plural: "water usage records", singular: "water usage record" },
  vendorperf: { plural: "vendor ratings", singular: "vendor rating" },
  buildinginsp: { plural: "building inspections", singular: "building inspection" },
  infraalerts: { plural: "infrastructure alerts", singular: "infrastructure alert" },
  floorplans: { plural: "floor plans", singular: "floor plan" },
  equipment: { plural: "equipment items", singular: "equipment item" },
  costs: { plural: "maintenance costs", singular: "cost record" },
  requests: { plural: "maintenance requests", singular: "maintenance request" },
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
  | "lighting"
  | "comments"
  | "assignments"
  | "lifecycle"
  | "warranty"
  | "utilities"
  | "compliance"
  | "emergency"
  | "reports"
  | "pestinsp"
  | "pesttreat"
  | "green"
  | "water"
  | "vendorperf"
  | "buildinginsp"
  | "infraalerts"
  | "floorplans"
  | "equipment"
  | "costs"
  | "requests";

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
  { key: "comments", label: "Comments", icon: ChatBubbleLeftRightIcon },
  { key: "assignments", label: "Asset Assignments", icon: UsersIcon },
  { key: "lifecycle", label: "Lifecycle", icon: ListBulletIcon },
  { key: "warranty", label: "Warranty", icon: ShieldExclamationIcon },
  { key: "utilities", label: "Utilities", icon: BeakerIcon },
  { key: "compliance", label: "Compliance", icon: DocumentCheckIcon },
  { key: "emergency", label: "Emergency", icon: LifebuoyIcon },
  { key: "reports", label: "Reports", icon: DocumentChartBarIcon },
  { key: "pestinsp", label: "Pest Inspections", icon: BugAntIcon },
  { key: "pesttreat", label: "Pest Treatments", icon: SparklesIcon },
  { key: "green", label: "Green", icon: SunIcon },
  { key: "water", label: "Water", icon: CloudIcon },
  { key: "vendorperf", label: "Vendor Ratings", icon: StarIcon },
  { key: "buildinginsp", label: "Building Inspections", icon: ClipboardDocumentListIcon },
  { key: "infraalerts", label: "Infra Alerts", icon: BellAlertIcon },
  { key: "floorplans", label: "Floor Plans", icon: MapIcon },
  { key: "equipment", label: "Room Equipment", icon: ComputerDesktopIcon },
  { key: "costs", label: "Maintenance Costs", icon: CurrencyDollarIcon },
  { key: "requests", label: "Maintenance Requests", icon: WrenchIcon },
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
  const [showCommentForm, setShowCommentForm] = useState(false);
  const [editingComment, setEditingComment] = useState<WorkOrderComment | null>(null);
  const [showAssignmentForm, setShowAssignmentForm] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState<AssetAssignment | null>(null);
  const [showLifecycleForm, setShowLifecycleForm] = useState(false);
  const [editingLifecycle, setEditingLifecycle] = useState<AssetLifecycle | null>(null);
  const [showWarrantyForm, setShowWarrantyForm] = useState(false);
  const [editingWarranty, setEditingWarranty] = useState<WarrantyClaim | null>(null);
  const [showUtilityForm, setShowUtilityForm] = useState(false);
  const [editingUtility, setEditingUtility] = useState<UtilityRecord | null>(null);
  const [showComplianceForm, setShowComplianceForm] = useState(false);
  const [editingCompliance, setEditingCompliance] = useState<ComplianceRecord | null>(null);
  const [showEmergencyForm, setShowEmergencyForm] = useState(false);
  const [editingEmergency, setEditingEmergency] = useState<EmergencyPlan | null>(null);
  const [showReportForm, setShowReportForm] = useState(false);
  const [editingReport, setEditingReport] = useState<InfraReport | null>(null);
  const [showPestInspForm, setShowPestInspForm] = useState(false);
  const [editingPestInsp, setEditingPestInsp] = useState<PestInspection | null>(null);
  const [showPestTreatForm, setShowPestTreatForm] = useState(false);
  const [editingPestTreat, setEditingPestTreat] = useState<PestTreatment | null>(null);
  const [showGreenForm, setShowGreenForm] = useState(false);
  const [editingGreen, setEditingGreen] = useState<GreenInitiative | null>(null);
  const [showWaterForm, setShowWaterForm] = useState(false);
  const [editingWater, setEditingWater] = useState<WaterUsage | null>(null);
  const [showVendorPerfForm, setShowVendorPerfForm] = useState(false);
  const [editingVendorPerf, setEditingVendorPerf] = useState<VendorRating | null>(null);
  const [showBuildingInspForm, setShowBuildingInspForm] = useState(false);
  const [editingBuildingInsp, setEditingBuildingInsp] = useState<BuildingInspection | null>(null);
  const [showInfraAlertForm, setShowInfraAlertForm] = useState(false);
  const [editingInfraAlert, setEditingInfraAlert] = useState<InfraAlert | null>(null);
  const [showFloorPlanForm, setShowFloorPlanForm] = useState(false);
  const [editingFloorPlan, setEditingFloorPlan] = useState<FloorPlan | null>(null);
  const [showEquipmentForm, setShowEquipmentForm] = useState(false);
  const [editingEquipment, setEditingEquipment] = useState<RoomEquipment | null>(null);
  const [showCostForm, setShowCostForm] = useState(false);
  const [editingCost, setEditingCost] = useState<CostRecord | null>(null);
  const [showRequestForm, setShowRequestForm] = useState(false);
  const [editingRequest, setEditingRequest] = useState<MaintRequest | null>(null);

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

  const { data: comments = [], isLoading: commentsLoading } = useQuery({
    queryKey: ["infra-comments"],
    queryFn: async () => {
      const res = await api.get<{ results: WorkOrderComment[] }>(
        "/infrastructure/work-order-comments/",
      );
      return res.results ?? [];
    },
  });

  const { data: assignments = [], isLoading: assignmentsLoading } = useQuery({
    queryKey: ["infra-assignments"],
    queryFn: async () => {
      const res = await api.get<{ results: AssetAssignment[] }>(
        "/infrastructure/asset-assignments/",
      );
      return res.results ?? [];
    },
  });

  const { data: lifecycle = [], isLoading: lifecycleLoading } = useQuery({
    queryKey: ["infra-lifecycle"],
    queryFn: async () => {
      const res = await api.get<{ results: AssetLifecycle[] }>("/infrastructure/asset-lifecycle/");
      return res.results ?? [];
    },
  });

  const { data: warrantyClaims = [], isLoading: warrantyLoading } = useQuery({
    queryKey: ["infra-warranty"],
    queryFn: async () => {
      const res = await api.get<{ results: WarrantyClaim[] }>("/infrastructure/warranty-claims/");
      return res.results ?? [];
    },
  });

  const { data: utilities = [], isLoading: utilitiesLoading } = useQuery({
    queryKey: ["infra-utilities"],
    queryFn: async () => {
      const res = await api.get<{ results: UtilityRecord[] }>("/infrastructure/utility-tracker/");
      return res.results ?? [];
    },
  });

  const { data: complianceRecords = [], isLoading: complianceLoading } = useQuery({
    queryKey: ["infra-compliance"],
    queryFn: async () => {
      const res = await api.get<{ results: ComplianceRecord[] }>(
        "/infrastructure/compliance-records/",
      );
      return res.results ?? [];
    },
  });

  const { data: emergencyPlans = [], isLoading: emergencyLoading } = useQuery({
    queryKey: ["infra-emergency"],
    queryFn: async () => {
      const res = await api.get<{ results: EmergencyPlan[] }>("/infrastructure/emergency-plans/");
      return res.results ?? [];
    },
  });

  const { data: reports = [], isLoading: reportsLoading } = useQuery({
    queryKey: ["infra-reports"],
    queryFn: async () => {
      const res = await api.get<{ results: InfraReport[] }>("/infrastructure/reports/");
      return res.results ?? [];
    },
  });

  const { data: pestInspections = [], isLoading: pestInspLoading } = useQuery({
    queryKey: ["infra-pestinsp"],
    queryFn: async () => {
      const res = await api.get<{ results: PestInspection[] }>(
        "/infrastructure/pest-control-inspection/",
      );
      return res.results ?? [];
    },
  });

  const { data: pestTreatments = [], isLoading: pestTreatLoading } = useQuery({
    queryKey: ["infra-pesttreat"],
    queryFn: async () => {
      const res = await api.get<{ results: PestTreatment[] }>("/infrastructure/pest-treatment/");
      return res.results ?? [];
    },
  });

  const { data: greenInitiatives = [], isLoading: greenLoading } = useQuery({
    queryKey: ["infra-green"],
    queryFn: async () => {
      const res = await api.get<{ results: GreenInitiative[] }>(
        "/infrastructure/green-initiative/",
      );
      return res.results ?? [];
    },
  });

  const { data: waterUsage = [], isLoading: waterLoading } = useQuery({
    queryKey: ["infra-water"],
    queryFn: async () => {
      const res = await api.get<{ results: WaterUsage[] }>("/infrastructure/water-usage-record/");
      return res.results ?? [];
    },
  });

  const { data: vendorRatings = [], isLoading: vendorPerfLoading } = useQuery({
    queryKey: ["infra-vendorperf"],
    queryFn: async () => {
      const res = await api.get<{ results: VendorRating[] }>("/infrastructure/vendor-performance/");
      return res.results ?? [];
    },
  });

  const { data: buildingInspections = [], isLoading: buildingInspLoading } = useQuery({
    queryKey: ["infra-buildinginsp"],
    queryFn: async () => {
      const res = await api.get<{ results: BuildingInspection[] }>(
        "/infrastructure/building-inspection/",
      );
      return res.results ?? [];
    },
  });

  const { data: infraAlerts = [], isLoading: infraAlertsLoading } = useQuery({
    queryKey: ["infra-infraalerts"],
    queryFn: async () => {
      const res = await api.get<{ results: InfraAlert[] }>("/infrastructure/infrastructure-alert/");
      return res.results ?? [];
    },
  });

  const { data: floorPlans = [], isLoading: floorPlansLoading } = useQuery({
    queryKey: ["infra-floorplans"],
    queryFn: async () => {
      const res = await api.get<{ results: FloorPlan[] }>("/infrastructure/floor-plan/");
      return res.results ?? [];
    },
  });

  const { data: roomEquipment = [], isLoading: equipmentLoading } = useQuery({
    queryKey: ["infra-equipment"],
    queryFn: async () => {
      const res = await api.get<{ results: RoomEquipment[] }>("/infrastructure/room-equipment/");
      return res.results ?? [];
    },
  });

  const { data: costRecords = [], isLoading: costsLoading } = useQuery({
    queryKey: ["infra-costs"],
    queryFn: async () => {
      const res = await api.get<{ results: CostRecord[] }>(
        "/infrastructure/maintenance-cost-tracking/",
      );
      return res.results ?? [];
    },
  });

  const { data: maintRequests = [], isLoading: requestsLoading } = useQuery({
    queryKey: ["infra-requests"],
    queryFn: async () => {
      const res = await api.get<{ results: MaintRequest[] }>(
        "/infrastructure/infrastructure-maintenance-request/",
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
  const deleteComment = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/work-order-comments/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-comments"] });
      toast.success("Comment deleted");
    },
  });
  const deleteAssignment = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/asset-assignments/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-assignments"] });
      toast.success("Assignment deleted");
    },
  });
  const deleteLifecycle = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/asset-lifecycle/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-lifecycle"] });
      toast.success("Lifecycle event deleted");
    },
  });
  const deleteWarranty = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/warranty-claims/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-warranty"] });
      toast.success("Warranty claim deleted");
    },
  });
  const deleteUtility = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/utility-tracker/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-utilities"] });
      toast.success("Utility record deleted");
    },
  });
  const deleteCompliance = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/compliance-records/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-compliance"] });
      toast.success("Compliance record deleted");
    },
  });
  const deleteEmergency = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/emergency-plans/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-emergency"] });
      toast.success("Emergency plan deleted");
    },
  });
  const deleteReport = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/reports/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-reports"] });
      toast.success("Report deleted");
    },
  });
  const deletePestInsp = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/pest-control-inspection/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-pestinsp"] });
      toast.success("Pest inspection deleted");
    },
  });
  const deletePestTreat = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/pest-treatment/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-pesttreat"] });
      toast.success("Pest treatment deleted");
    },
  });
  const deleteGreen = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/green-initiative/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-green"] });
      toast.success("Green initiative deleted");
    },
  });
  const deleteWater = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/water-usage-record/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-water"] });
      toast.success("Water record deleted");
    },
  });
  const deleteVendorPerf = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/vendor-performance/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-vendorperf"] });
      toast.success("Vendor rating deleted");
    },
  });
  const deleteBuildingInsp = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/building-inspection/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-buildinginsp"] });
      toast.success("Building inspection deleted");
    },
  });
  const deleteInfraAlert = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/infrastructure-alert/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-infraalerts"] });
      toast.success("Alert deleted");
    },
  });
  const deleteFloorPlan = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/floor-plan/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-floorplans"] });
      toast.success("Floor plan deleted");
    },
  });
  const deleteEquipment = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/room-equipment/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-equipment"] });
      toast.success("Equipment deleted");
    },
  });
  const deleteCost = useMutation({
    mutationFn: (id: string) => api.delete(`/infrastructure/maintenance-cost-tracking/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-costs"] });
      toast.success("Cost record deleted");
    },
  });
  const deleteRequest = useMutation({
    mutationFn: (id: string) =>
      api.delete(`/infrastructure/infrastructure-maintenance-request/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["infra-requests"] });
      toast.success("Maintenance request deleted");
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

  const filteredComments = useMemo(() => {
    if (!search.trim()) return comments;
    const q = search.toLowerCase();
    return comments.filter(
      (c) =>
        c.comment.toLowerCase().includes(q) || (c.work_order_title || "").toLowerCase().includes(q),
    );
  }, [comments, search]);

  const filteredAssignments = useMemo(() => {
    if (!search.trim()) return assignments;
    const q = search.toLowerCase();
    return assignments.filter(
      (a) =>
        (a.asset_name || "").toLowerCase().includes(q) ||
        a.department.toLowerCase().includes(q) ||
        a.status.toLowerCase().includes(q),
    );
  }, [assignments, search]);

  const filteredLifecycle = useMemo(() => {
    if (!search.trim()) return lifecycle;
    const q = search.toLowerCase();
    return lifecycle.filter(
      (l) =>
        (l.asset_name || "").toLowerCase().includes(q) ||
        l.event.toLowerCase().includes(q) ||
        l.description.toLowerCase().includes(q),
    );
  }, [lifecycle, search]);

  const filteredWarranty = useMemo(() => {
    if (!search.trim()) return warrantyClaims;
    const q = search.toLowerCase();
    return warrantyClaims.filter(
      (w) =>
        (w.asset_name || "").toLowerCase().includes(q) ||
        w.claim_number.toLowerCase().includes(q) ||
        w.warranty_provider.toLowerCase().includes(q),
    );
  }, [warrantyClaims, search]);

  const filteredUtilities = useMemo(() => {
    if (!search.trim()) return utilities;
    const q = search.toLowerCase();
    return utilities.filter(
      (u) =>
        u.utility_type.toLowerCase().includes(q) ||
        (u.building_name || "").toLowerCase().includes(q) ||
        u.notes.toLowerCase().includes(q),
    );
  }, [utilities, search]);

  const filteredCompliance = useMemo(() => {
    if (!search.trim()) return complianceRecords;
    const q = search.toLowerCase();
    return complianceRecords.filter(
      (c) =>
        c.title.toLowerCase().includes(q) ||
        c.compliance_type.toLowerCase().includes(q) ||
        c.regulation_reference.toLowerCase().includes(q),
    );
  }, [complianceRecords, search]);

  const filteredEmergency = useMemo(() => {
    if (!search.trim()) return emergencyPlans;
    const q = search.toLowerCase();
    return emergencyPlans.filter(
      (e) => e.title.toLowerCase().includes(q) || e.plan_type.toLowerCase().includes(q),
    );
  }, [emergencyPlans, search]);

  const filteredReports = useMemo(() => {
    if (!search.trim()) return reports;
    const q = search.toLowerCase();
    return reports.filter(
      (r) => r.title.toLowerCase().includes(q) || r.report_type.toLowerCase().includes(q),
    );
  }, [reports, search]);

  const filteredPestInsp = useMemo(() => {
    if (!search.trim()) return pestInspections;
    const q = search.toLowerCase();
    return pestInspections.filter(
      (p) =>
        p.inspection_type.toLowerCase().includes(q) ||
        p.inspector_name.toLowerCase().includes(q) ||
        (p.building_name || "").toLowerCase().includes(q),
    );
  }, [pestInspections, search]);

  const filteredPestTreat = useMemo(() => {
    if (!search.trim()) return pestTreatments;
    const q = search.toLowerCase();
    return pestTreatments.filter(
      (t) =>
        t.treatment_type.toLowerCase().includes(q) ||
        t.pest_target.toLowerCase().includes(q) ||
        (t.building_name || "").toLowerCase().includes(q),
    );
  }, [pestTreatments, search]);

  const filteredGreen = useMemo(() => {
    if (!search.trim()) return greenInitiatives;
    const q = search.toLowerCase();
    return greenInitiatives.filter(
      (g) =>
        g.title.toLowerCase().includes(q) ||
        g.initiative_type.toLowerCase().includes(q) ||
        (g.building_name || "").toLowerCase().includes(q),
    );
  }, [greenInitiatives, search]);

  const filteredWater = useMemo(() => {
    if (!search.trim()) return waterUsage;
    const q = search.toLowerCase();
    return waterUsage.filter(
      (w) => w.notes.toLowerCase().includes(q) || (w.building_name || "").toLowerCase().includes(q),
    );
  }, [waterUsage, search]);

  const filteredVendorPerf = useMemo(() => {
    if (!search.trim()) return vendorRatings;
    const q = search.toLowerCase();
    return vendorRatings.filter(
      (v) =>
        (v.vendor_contract_name || "").toLowerCase().includes(q) ||
        v.service_type.toLowerCase().includes(q),
    );
  }, [vendorRatings, search]);

  const filteredBuildingInsp = useMemo(() => {
    if (!search.trim()) return buildingInspections;
    const q = search.toLowerCase();
    return buildingInspections.filter(
      (b) =>
        b.inspection_type.toLowerCase().includes(q) ||
        b.inspector_name.toLowerCase().includes(q) ||
        (b.building_name || "").toLowerCase().includes(q),
    );
  }, [buildingInspections, search]);

  const filteredInfraAlerts = useMemo(() => {
    if (!search.trim()) return infraAlerts;
    const q = search.toLowerCase();
    return infraAlerts.filter(
      (a) =>
        a.title.toLowerCase().includes(q) ||
        a.alert_type.toLowerCase().includes(q) ||
        (a.building_name || "").toLowerCase().includes(q),
    );
  }, [infraAlerts, search]);

  const filteredFloorPlans = useMemo(() => {
    if (!search.trim()) return floorPlans;
    const q = search.toLowerCase();
    return floorPlans.filter(
      (f) =>
        (f.building_name || "").toLowerCase().includes(q) ||
        f.floor_name.toLowerCase().includes(q) ||
        f.description.toLowerCase().includes(q),
    );
  }, [floorPlans, search]);

  const filteredEquipment = useMemo(() => {
    if (!search.trim()) return roomEquipment;
    const q = search.toLowerCase();
    return roomEquipment.filter(
      (e) =>
        e.name.toLowerCase().includes(q) ||
        e.equipment_type.toLowerCase().includes(q) ||
        e.brand.toLowerCase().includes(q),
    );
  }, [roomEquipment, search]);

  const filteredCosts = useMemo(() => {
    if (!search.trim()) return costRecords;
    const q = search.toLowerCase();
    return costRecords.filter(
      (c) =>
        c.cost_category.toLowerCase().includes(q) ||
        c.vendor.toLowerCase().includes(q) ||
        (c.building_name || "").toLowerCase().includes(q),
    );
  }, [costRecords, search]);

  const filteredRequests = useMemo(() => {
    if (!search.trim()) return maintRequests;
    const q = search.toLowerCase();
    return maintRequests.filter(
      (r) =>
        r.title.toLowerCase().includes(q) ||
        r.status.toLowerCase().includes(q) ||
        (r.building_name || "").toLowerCase().includes(q),
    );
  }, [maintRequests, search]);

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
                                      : activeTab === "spots"
                                        ? filteredSpots
                                        : activeTab === "comments"
                                          ? filteredComments
                                          : activeTab === "assignments"
                                            ? filteredAssignments
                                            : activeTab === "lifecycle"
                                              ? filteredLifecycle
                                              : activeTab === "warranty"
                                                ? filteredWarranty
                                                : activeTab === "utilities"
                                                  ? filteredUtilities
                                                  : activeTab === "compliance"
                                                    ? filteredCompliance
                                                    : activeTab === "emergency"
                                                      ? filteredEmergency
                                                      : activeTab === "reports"
                                                        ? filteredReports
                                                        : activeTab === "pestinsp"
                                                          ? filteredPestInsp
                                                          : activeTab === "pesttreat"
                                                            ? filteredPestTreat
                                                            : activeTab === "green"
                                                              ? filteredGreen
                                                              : activeTab === "water"
                                                                ? filteredWater
                                                                : activeTab === "vendorperf"
                                                                  ? filteredVendorPerf
                                                                  : activeTab === "buildinginsp"
                                                                    ? filteredBuildingInsp
                                                                    : activeTab === "infraalerts"
                                                                      ? filteredInfraAlerts
                                                                      : activeTab === "floorplans"
                                                                        ? filteredFloorPlans
                                                                        : activeTab === "equipment"
                                                                          ? filteredEquipment
                                                                          : activeTab === "costs"
                                                                            ? filteredCosts
                                                                            : filteredRequests;

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
    deleteLighting.isPending ||
    deleteComment.isPending ||
    deleteAssignment.isPending ||
    deleteLifecycle.isPending ||
    deleteWarranty.isPending ||
    deleteUtility.isPending ||
    deleteCompliance.isPending ||
    deleteEmergency.isPending ||
    deleteReport.isPending ||
    deletePestInsp.isPending ||
    deletePestTreat.isPending ||
    deleteGreen.isPending ||
    deleteWater.isPending ||
    deleteVendorPerf.isPending ||
    deleteBuildingInsp.isPending ||
    deleteInfraAlert.isPending ||
    deleteFloorPlan.isPending ||
    deleteEquipment.isPending ||
    deleteCost.isPending ||
    deleteRequest.isPending;

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
                                              : activeTab === "lighting"
                                                ? "/infrastructure/lighting-schedule/"
                                                : activeTab === "comments"
                                                  ? "/infrastructure/work-order-comments/"
                                                  : activeTab === "assignments"
                                                    ? "/infrastructure/asset-assignments/"
                                                    : activeTab === "lifecycle"
                                                      ? "/infrastructure/asset-lifecycle/"
                                                      : activeTab === "warranty"
                                                        ? "/infrastructure/warranty-claims/"
                                                        : activeTab === "utilities"
                                                          ? "/infrastructure/utility-tracker/"
                                                          : activeTab === "compliance"
                                                            ? "/infrastructure/compliance-records/"
                                                            : activeTab === "emergency"
                                                              ? "/infrastructure/emergency-plans/"
                                                              : activeTab === "reports"
                                                                ? "/infrastructure/reports/"
                                                                : activeTab === "pestinsp"
                                                                  ? "/infrastructure/pest-control-inspection/"
                                                                  : activeTab === "pesttreat"
                                                                    ? "/infrastructure/pest-treatment/"
                                                                    : activeTab === "green"
                                                                      ? "/infrastructure/green-initiative/"
                                                                      : activeTab === "water"
                                                                        ? "/infrastructure/water-usage-record/"
                                                                        : activeTab === "vendorperf"
                                                                          ? "/infrastructure/vendor-performance/"
                                                                          : activeTab ===
                                                                              "buildinginsp"
                                                                            ? "/infrastructure/building-inspection/"
                                                                            : activeTab ===
                                                                                "infraalerts"
                                                                              ? "/infrastructure/infrastructure-alert/"
                                                                              : activeTab ===
                                                                                  "floorplans"
                                                                                ? "/infrastructure/floor-plan/"
                                                                                : activeTab ===
                                                                                    "equipment"
                                                                                  ? "/infrastructure/room-equipment/"
                                                                                  : activeTab ===
                                                                                      "costs"
                                                                                    ? "/infrastructure/maintenance-cost-tracking/"
                                                                                    : "/infrastructure/infrastructure-maintenance-request/";
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
                                          : activeTab === "comments"
                                            ? filteredComments.map((c) => ({
                                                work_order: c.work_order_title ?? "",
                                                comment: c.comment,
                                                author: c.author_name ?? "",
                                              }))
                                            : activeTab === "assignments"
                                              ? filteredAssignments.map((a) => ({
                                                  asset: a.asset_name ?? "",
                                                  status: a.status,
                                                  department: a.department,
                                                  assigned_date: a.assigned_date ?? "",
                                                }))
                                              : activeTab === "lifecycle"
                                                ? filteredLifecycle.map((l) => ({
                                                    asset: l.asset_name ?? "",
                                                    event: l.event,
                                                    event_date: l.event_date ?? "",
                                                    cost: l.cost ?? 0,
                                                  }))
                                                : activeTab === "warranty"
                                                  ? filteredWarranty.map((w) => ({
                                                      asset: w.asset_name ?? "",
                                                      claim_number: w.claim_number,
                                                      warranty_provider: w.warranty_provider,
                                                      status: w.status,
                                                      claim_date: w.claim_date ?? "",
                                                    }))
                                                  : activeTab === "utilities"
                                                    ? filteredUtilities.map((u) => ({
                                                        building: u.building_name ?? "",
                                                        utility_type: u.utility_type,
                                                        reading_date: u.reading_date ?? "",
                                                        reading_value: u.reading_value ?? 0,
                                                        cost: u.cost ?? "",
                                                      }))
                                                    : activeTab === "compliance"
                                                      ? filteredCompliance.map((c) => ({
                                                          title: c.title,
                                                          compliance_type: c.compliance_type,
                                                          status: c.status,
                                                          next_audit_date: c.next_audit_date ?? "",
                                                        }))
                                                      : activeTab === "emergency"
                                                        ? filteredEmergency.map((e) => ({
                                                            title: e.title,
                                                            plan_type: e.plan_type,
                                                            next_drill_date:
                                                              e.next_drill_date ?? "",
                                                            is_active: e.is_active,
                                                          }))
                                                        : activeTab === "reports"
                                                          ? filteredReports.map((r) => ({
                                                              title: r.title,
                                                              report_type: r.report_type,
                                                              date_from: r.date_from ?? "",
                                                              date_to: r.date_to ?? "",
                                                            }))
                                                          : activeTab === "pestinsp"
                                                            ? filteredPestInsp.map((p) => ({
                                                                building: p.building_name ?? "",
                                                                inspection_type: p.inspection_type,
                                                                status: p.status,
                                                                scheduled_date:
                                                                  p.scheduled_date ?? "",
                                                              }))
                                                            : activeTab === "pesttreat"
                                                              ? filteredPestTreat.map((t) => ({
                                                                  building: t.building_name ?? "",
                                                                  treatment_date:
                                                                    t.treatment_date ?? "",
                                                                  treatment_type: t.treatment_type,
                                                                  pest_target: t.pest_target,
                                                                  cost: t.cost ?? 0,
                                                                }))
                                                              : activeTab === "green"
                                                                ? filteredGreen.map((g) => ({
                                                                    title: g.title,
                                                                    initiative_type:
                                                                      g.initiative_type,
                                                                    status: g.status,
                                                                    estimated_savings:
                                                                      g.estimated_savings ?? 0,
                                                                  }))
                                                                : activeTab === "water"
                                                                  ? filteredWater.map((w) => ({
                                                                      building:
                                                                        w.building_name ?? "",
                                                                      record_date:
                                                                        w.record_date ?? "",
                                                                      usage_gallons:
                                                                        w.usage_gallons ?? 0,
                                                                      leak_detected:
                                                                        w.leak_detected,
                                                                    }))
                                                                  : activeTab === "vendorperf"
                                                                    ? filteredVendorPerf.map(
                                                                        (v) => ({
                                                                          vendor:
                                                                            v.vendor_contract_name ??
                                                                            "",
                                                                          service_type:
                                                                            v.service_type,
                                                                          evaluation_date:
                                                                            v.evaluation_date ?? "",
                                                                          quality_rating:
                                                                            v.quality_rating,
                                                                        }),
                                                                      )
                                                                    : activeTab === "buildinginsp"
                                                                      ? filteredBuildingInsp.map(
                                                                          (b) => ({
                                                                            building:
                                                                              b.building_name ?? "",
                                                                            inspection_type:
                                                                              b.inspection_type,
                                                                            result: b.result,
                                                                            inspection_date:
                                                                              b.inspection_date ??
                                                                              "",
                                                                          }),
                                                                        )
                                                                      : activeTab === "infraalerts"
                                                                        ? filteredInfraAlerts.map(
                                                                            (a) => ({
                                                                              title: a.title,
                                                                              alert_type:
                                                                                a.alert_type,
                                                                              severity: a.severity,
                                                                              status: a.status,
                                                                              building:
                                                                                a.building_name ??
                                                                                "",
                                                                            }),
                                                                          )
                                                                        : activeTab === "floorplans"
                                                                          ? filteredFloorPlans.map(
                                                                              (f) => ({
                                                                                building:
                                                                                  f.building_name ??
                                                                                  "",
                                                                                floor_number:
                                                                                  f.floor_number,
                                                                                floor_name:
                                                                                  f.floor_name,
                                                                                is_current:
                                                                                  f.is_current,
                                                                              }),
                                                                            )
                                                                          : activeTab ===
                                                                              "equipment"
                                                                            ? filteredEquipment.map(
                                                                                (e) => ({
                                                                                  name: e.name,
                                                                                  room:
                                                                                    e.room_name ??
                                                                                    "",
                                                                                  equipment_type:
                                                                                    e.equipment_type,
                                                                                  status: e.status,
                                                                                  brand: e.brand,
                                                                                }),
                                                                              )
                                                                            : activeTab === "costs"
                                                                              ? filteredCosts.map(
                                                                                  (c) => ({
                                                                                    cost_category:
                                                                                      c.cost_category,
                                                                                    amount:
                                                                                      c.amount ?? 0,
                                                                                    vendor:
                                                                                      c.vendor,
                                                                                    cost_date:
                                                                                      c.cost_date ??
                                                                                      "",
                                                                                    building:
                                                                                      c.building_name ??
                                                                                      "",
                                                                                  }),
                                                                                )
                                                                              : filteredRequests.map(
                                                                                  (r) => ({
                                                                                    title: r.title,
                                                                                    priority:
                                                                                      r.priority,
                                                                                    status:
                                                                                      r.status,
                                                                                    building:
                                                                                      r.building_name ??
                                                                                      "",
                                                                                  }),
                                                                                );
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
      else if (activeTab === "lighting") setShowLightingForm(true);
      else if (activeTab === "comments") setShowCommentForm(true);
      else if (activeTab === "assignments") setShowAssignmentForm(true);
      else if (activeTab === "lifecycle") setShowLifecycleForm(true);
      else if (activeTab === "warranty") setShowWarrantyForm(true);
      else if (activeTab === "utilities") setShowUtilityForm(true);
      else if (activeTab === "compliance") setShowComplianceForm(true);
      else if (activeTab === "emergency") setShowEmergencyForm(true);
      else if (activeTab === "reports") setShowReportForm(true);
      else if (activeTab === "pestinsp") setShowPestInspForm(true);
      else if (activeTab === "pesttreat") setShowPestTreatForm(true);
      else if (activeTab === "green") setShowGreenForm(true);
      else if (activeTab === "water") setShowWaterForm(true);
      else if (activeTab === "vendorperf") setShowVendorPerfForm(true);
      else if (activeTab === "buildinginsp") setShowBuildingInspForm(true);
      else if (activeTab === "infraalerts") setShowInfraAlertForm(true);
      else if (activeTab === "floorplans") setShowFloorPlanForm(true);
      else if (activeTab === "equipment") setShowEquipmentForm(true);
      else if (activeTab === "costs") setShowCostForm(true);
      else setShowRequestForm(true);
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
                                      : activeTab === "lighting"
                                        ? lightingLoading
                                        : activeTab === "comments"
                                          ? commentsLoading
                                          : activeTab === "assignments"
                                            ? assignmentsLoading
                                            : activeTab === "lifecycle"
                                              ? lifecycleLoading
                                              : activeTab === "warranty"
                                                ? warrantyLoading
                                                : activeTab === "utilities"
                                                  ? utilitiesLoading
                                                  : activeTab === "compliance"
                                                    ? complianceLoading
                                                    : activeTab === "emergency"
                                                      ? emergencyLoading
                                                      : activeTab === "reports"
                                                        ? reportsLoading
                                                        : activeTab === "pestinsp"
                                                          ? pestInspLoading
                                                          : activeTab === "pesttreat"
                                                            ? pestTreatLoading
                                                            : activeTab === "green"
                                                              ? greenLoading
                                                              : activeTab === "water"
                                                                ? waterLoading
                                                                : activeTab === "vendorperf"
                                                                  ? vendorPerfLoading
                                                                  : activeTab === "buildinginsp"
                                                                    ? buildingInspLoading
                                                                    : activeTab === "infraalerts"
                                                                      ? infraAlertsLoading
                                                                      : activeTab === "floorplans"
                                                                        ? floorPlansLoading
                                                                        : activeTab === "equipment"
                                                                          ? equipmentLoading
                                                                          : activeTab === "costs"
                                                                            ? costsLoading
                                                                            : requestsLoading;

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
                                      : activeTab === "lighting"
                                        ? {
                                            label: "Add Lighting Schedule",
                                            action: () => {
                                              setEditingLighting(null);
                                              setShowLightingForm(true);
                                            },
                                          }
                                        : activeTab === "comments"
                                          ? {
                                              label: "Add Comment",
                                              action: () => {
                                                setEditingComment(null);
                                                setShowCommentForm(true);
                                              },
                                            }
                                          : activeTab === "assignments"
                                            ? {
                                                label: "Assign Asset",
                                                action: () => {
                                                  setEditingAssignment(null);
                                                  setShowAssignmentForm(true);
                                                },
                                              }
                                            : activeTab === "lifecycle"
                                              ? {
                                                  label: "Log Event",
                                                  action: () => {
                                                    setEditingLifecycle(null);
                                                    setShowLifecycleForm(true);
                                                  },
                                                }
                                              : activeTab === "warranty"
                                                ? {
                                                    label: "New Claim",
                                                    action: () => {
                                                      setEditingWarranty(null);
                                                      setShowWarrantyForm(true);
                                                    },
                                                  }
                                                : activeTab === "utilities"
                                                  ? {
                                                      label: "Log Reading",
                                                      action: () => {
                                                        setEditingUtility(null);
                                                        setShowUtilityForm(true);
                                                      },
                                                    }
                                                  : activeTab === "compliance"
                                                    ? {
                                                        label: "Add Record",
                                                        action: () => {
                                                          setEditingCompliance(null);
                                                          setShowComplianceForm(true);
                                                        },
                                                      }
                                                    : activeTab === "emergency"
                                                      ? {
                                                          label: "Add Plan",
                                                          action: () => {
                                                            setEditingEmergency(null);
                                                            setShowEmergencyForm(true);
                                                          },
                                                        }
                                                      : activeTab === "reports"
                                                        ? {
                                                            label: "New Report",
                                                            action: () => {
                                                              setEditingReport(null);
                                                              setShowReportForm(true);
                                                            },
                                                          }
                                                        : activeTab === "pestinsp"
                                                          ? {
                                                              label: "New Inspection",
                                                              action: () => {
                                                                setEditingPestInsp(null);
                                                                setShowPestInspForm(true);
                                                              },
                                                            }
                                                          : activeTab === "pesttreat"
                                                            ? {
                                                                label: "Log Treatment",
                                                                action: () => {
                                                                  setEditingPestTreat(null);
                                                                  setShowPestTreatForm(true);
                                                                },
                                                              }
                                                            : activeTab === "green"
                                                              ? {
                                                                  label: "New Initiative",
                                                                  action: () => {
                                                                    setEditingGreen(null);
                                                                    setShowGreenForm(true);
                                                                  },
                                                                }
                                                              : activeTab === "water"
                                                                ? {
                                                                    label: "Log Usage",
                                                                    action: () => {
                                                                      setEditingWater(null);
                                                                      setShowWaterForm(true);
                                                                    },
                                                                  }
                                                                : activeTab === "vendorperf"
                                                                  ? {
                                                                      label: "Rate Vendor",
                                                                      action: () => {
                                                                        setEditingVendorPerf(null);
                                                                        setShowVendorPerfForm(true);
                                                                      },
                                                                    }
                                                                  : activeTab === "buildinginsp"
                                                                    ? {
                                                                        label: "New Inspection",
                                                                        action: () => {
                                                                          setEditingBuildingInsp(
                                                                            null,
                                                                          );
                                                                          setShowBuildingInspForm(
                                                                            true,
                                                                          );
                                                                        },
                                                                      }
                                                                    : activeTab === "infraalerts"
                                                                      ? {
                                                                          label: "Raise Alert",
                                                                          action: () => {
                                                                            setEditingInfraAlert(
                                                                              null,
                                                                            );
                                                                            setShowInfraAlertForm(
                                                                              true,
                                                                            );
                                                                          },
                                                                        }
                                                                      : activeTab === "floorplans"
                                                                        ? {
                                                                            label: "Add Floor Plan",
                                                                            action: () => {
                                                                              setEditingFloorPlan(
                                                                                null,
                                                                              );
                                                                              setShowFloorPlanForm(
                                                                                true,
                                                                              );
                                                                            },
                                                                          }
                                                                        : activeTab === "equipment"
                                                                          ? {
                                                                              label:
                                                                                "Add Equipment",
                                                                              action: () => {
                                                                                setEditingEquipment(
                                                                                  null,
                                                                                );
                                                                                setShowEquipmentForm(
                                                                                  true,
                                                                                );
                                                                              },
                                                                            }
                                                                          : activeTab === "costs"
                                                                            ? {
                                                                                label: "Add Cost",
                                                                                action: () => {
                                                                                  setEditingCost(
                                                                                    null,
                                                                                  );
                                                                                  setShowCostForm(
                                                                                    true,
                                                                                  );
                                                                                },
                                                                              }
                                                                            : {
                                                                                label:
                                                                                  "New Request",
                                                                                action: () => {
                                                                                  setEditingRequest(
                                                                                    null,
                                                                                  );
                                                                                  setShowRequestForm(
                                                                                    true,
                                                                                  );
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
          title={`No ${TAB_LABELS[activeTab]?.plural ?? activeTab}`}
          description={`Add your first ${TAB_LABELS[activeTab]?.singular ?? "item"} to get started`}
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
                    } else if (activeTab === "lighting") {
                      setEditingLighting(item as LightingSchedule);
                      setShowLightingForm(true);
                    } else if (activeTab === "comments") {
                      setEditingComment(item as WorkOrderComment);
                      setShowCommentForm(true);
                    } else if (activeTab === "assignments") {
                      setEditingAssignment(item as AssetAssignment);
                      setShowAssignmentForm(true);
                    } else if (activeTab === "lifecycle") {
                      setEditingLifecycle(item as AssetLifecycle);
                      setShowLifecycleForm(true);
                    } else if (activeTab === "warranty") {
                      setEditingWarranty(item as WarrantyClaim);
                      setShowWarrantyForm(true);
                    } else if (activeTab === "utilities") {
                      setEditingUtility(item as UtilityRecord);
                      setShowUtilityForm(true);
                    } else if (activeTab === "compliance") {
                      setEditingCompliance(item as ComplianceRecord);
                      setShowComplianceForm(true);
                    } else if (activeTab === "emergency") {
                      setEditingEmergency(item as EmergencyPlan);
                      setShowEmergencyForm(true);
                    } else if (activeTab === "reports") {
                      setEditingReport(item as InfraReport);
                      setShowReportForm(true);
                    } else if (activeTab === "pestinsp") {
                      setEditingPestInsp(item as PestInspection);
                      setShowPestInspForm(true);
                    } else if (activeTab === "pesttreat") {
                      setEditingPestTreat(item as PestTreatment);
                      setShowPestTreatForm(true);
                    } else if (activeTab === "green") {
                      setEditingGreen(item as GreenInitiative);
                      setShowGreenForm(true);
                    } else if (activeTab === "water") {
                      setEditingWater(item as WaterUsage);
                      setShowWaterForm(true);
                    } else if (activeTab === "vendorperf") {
                      setEditingVendorPerf(item as VendorRating);
                      setShowVendorPerfForm(true);
                    } else if (activeTab === "buildinginsp") {
                      setEditingBuildingInsp(item as BuildingInspection);
                      setShowBuildingInspForm(true);
                    } else if (activeTab === "infraalerts") {
                      setEditingInfraAlert(item as InfraAlert);
                      setShowInfraAlertForm(true);
                    } else if (activeTab === "floorplans") {
                      setEditingFloorPlan(item as FloorPlan);
                      setShowFloorPlanForm(true);
                    } else if (activeTab === "equipment") {
                      setEditingEquipment(item as RoomEquipment);
                      setShowEquipmentForm(true);
                    } else if (activeTab === "costs") {
                      setEditingCost(item as CostRecord);
                      setShowCostForm(true);
                    } else {
                      setEditingRequest(item as MaintRequest);
                      setShowRequestForm(true);
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
                    else if (activeTab === "lighting") deleteLighting.mutate(item.id);
                    else if (activeTab === "comments") deleteComment.mutate(item.id);
                    else if (activeTab === "assignments") deleteAssignment.mutate(item.id);
                    else if (activeTab === "lifecycle") deleteLifecycle.mutate(item.id);
                    else if (activeTab === "warranty") deleteWarranty.mutate(item.id);
                    else if (activeTab === "utilities") deleteUtility.mutate(item.id);
                    else if (activeTab === "compliance") deleteCompliance.mutate(item.id);
                    else if (activeTab === "emergency") deleteEmergency.mutate(item.id);
                    else if (activeTab === "reports") deleteReport.mutate(item.id);
                    else if (activeTab === "pestinsp") deletePestInsp.mutate(item.id);
                    else if (activeTab === "pesttreat") deletePestTreat.mutate(item.id);
                    else if (activeTab === "green") deleteGreen.mutate(item.id);
                    else if (activeTab === "water") deleteWater.mutate(item.id);
                    else if (activeTab === "vendorperf") deleteVendorPerf.mutate(item.id);
                    else if (activeTab === "buildinginsp") deleteBuildingInsp.mutate(item.id);
                    else if (activeTab === "infraalerts") deleteInfraAlert.mutate(item.id);
                    else if (activeTab === "floorplans") deleteFloorPlan.mutate(item.id);
                    else if (activeTab === "equipment") deleteEquipment.mutate(item.id);
                    else if (activeTab === "costs") deleteCost.mutate(item.id);
                    else deleteRequest.mutate(item.id);
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
                    } else if (activeTab === "lighting") {
                      setEditingLighting(item as LightingSchedule);
                      setShowLightingForm(true);
                    } else if (activeTab === "comments") {
                      setEditingComment(item as WorkOrderComment);
                      setShowCommentForm(true);
                    } else if (activeTab === "assignments") {
                      setEditingAssignment(item as AssetAssignment);
                      setShowAssignmentForm(true);
                    } else if (activeTab === "lifecycle") {
                      setEditingLifecycle(item as AssetLifecycle);
                      setShowLifecycleForm(true);
                    } else if (activeTab === "warranty") {
                      setEditingWarranty(item as WarrantyClaim);
                      setShowWarrantyForm(true);
                    } else if (activeTab === "utilities") {
                      setEditingUtility(item as UtilityRecord);
                      setShowUtilityForm(true);
                    } else if (activeTab === "compliance") {
                      setEditingCompliance(item as ComplianceRecord);
                      setShowComplianceForm(true);
                    } else if (activeTab === "emergency") {
                      setEditingEmergency(item as EmergencyPlan);
                      setShowEmergencyForm(true);
                    } else if (activeTab === "reports") {
                      setEditingReport(item as InfraReport);
                      setShowReportForm(true);
                    } else if (activeTab === "pestinsp") {
                      setEditingPestInsp(item as PestInspection);
                      setShowPestInspForm(true);
                    } else if (activeTab === "pesttreat") {
                      setEditingPestTreat(item as PestTreatment);
                      setShowPestTreatForm(true);
                    } else if (activeTab === "green") {
                      setEditingGreen(item as GreenInitiative);
                      setShowGreenForm(true);
                    } else if (activeTab === "water") {
                      setEditingWater(item as WaterUsage);
                      setShowWaterForm(true);
                    } else if (activeTab === "vendorperf") {
                      setEditingVendorPerf(item as VendorRating);
                      setShowVendorPerfForm(true);
                    } else if (activeTab === "buildinginsp") {
                      setEditingBuildingInsp(item as BuildingInspection);
                      setShowBuildingInspForm(true);
                    } else if (activeTab === "infraalerts") {
                      setEditingInfraAlert(item as InfraAlert);
                      setShowInfraAlertForm(true);
                    } else if (activeTab === "floorplans") {
                      setEditingFloorPlan(item as FloorPlan);
                      setShowFloorPlanForm(true);
                    } else if (activeTab === "equipment") {
                      setEditingEquipment(item as RoomEquipment);
                      setShowEquipmentForm(true);
                    } else if (activeTab === "costs") {
                      setEditingCost(item as CostRecord);
                      setShowCostForm(true);
                    } else {
                      setEditingRequest(item as MaintRequest);
                      setShowRequestForm(true);
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
                    else if (activeTab === "lighting") deleteLighting.mutate(item.id);
                    else if (activeTab === "comments") deleteComment.mutate(item.id);
                    else if (activeTab === "assignments") deleteAssignment.mutate(item.id);
                    else if (activeTab === "lifecycle") deleteLifecycle.mutate(item.id);
                    else if (activeTab === "warranty") deleteWarranty.mutate(item.id);
                    else if (activeTab === "utilities") deleteUtility.mutate(item.id);
                    else if (activeTab === "compliance") deleteCompliance.mutate(item.id);
                    else if (activeTab === "emergency") deleteEmergency.mutate(item.id);
                    else if (activeTab === "reports") deleteReport.mutate(item.id);
                    else if (activeTab === "pestinsp") deletePestInsp.mutate(item.id);
                    else if (activeTab === "pesttreat") deletePestTreat.mutate(item.id);
                    else if (activeTab === "green") deleteGreen.mutate(item.id);
                    else if (activeTab === "water") deleteWater.mutate(item.id);
                    else if (activeTab === "vendorperf") deleteVendorPerf.mutate(item.id);
                    else if (activeTab === "buildinginsp") deleteBuildingInsp.mutate(item.id);
                    else if (activeTab === "infraalerts") deleteInfraAlert.mutate(item.id);
                    else if (activeTab === "floorplans") deleteFloorPlan.mutate(item.id);
                    else if (activeTab === "equipment") deleteEquipment.mutate(item.id);
                    else if (activeTab === "costs") deleteCost.mutate(item.id);
                    else deleteRequest.mutate(item.id);
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
      {activeTab === "comments" && (
        <CommentFormModal
          open={showCommentForm}
          onClose={() => {
            setShowCommentForm(false);
            setEditingComment(null);
          }}
          comment={editingComment}
          workOrders={workOrders}
          onSaved={() => {
            setShowCommentForm(false);
            setEditingComment(null);
            qc.invalidateQueries({ queryKey: ["infra-comments"] });
          }}
        />
      )}
      {activeTab === "assignments" && (
        <AssignmentFormModal
          open={showAssignmentForm}
          onClose={() => {
            setShowAssignmentForm(false);
            setEditingAssignment(null);
          }}
          assignment={editingAssignment}
          assets={assets}
          onSaved={() => {
            setShowAssignmentForm(false);
            setEditingAssignment(null);
            qc.invalidateQueries({ queryKey: ["infra-assignments"] });
          }}
        />
      )}
      {activeTab === "lifecycle" && (
        <LifecycleFormModal
          open={showLifecycleForm}
          onClose={() => {
            setShowLifecycleForm(false);
            setEditingLifecycle(null);
          }}
          event={editingLifecycle}
          assets={assets}
          onSaved={() => {
            setShowLifecycleForm(false);
            setEditingLifecycle(null);
            qc.invalidateQueries({ queryKey: ["infra-lifecycle"] });
          }}
        />
      )}
      {activeTab === "warranty" && (
        <WarrantyFormModal
          open={showWarrantyForm}
          onClose={() => {
            setShowWarrantyForm(false);
            setEditingWarranty(null);
          }}
          claim={editingWarranty}
          assets={assets}
          onSaved={() => {
            setShowWarrantyForm(false);
            setEditingWarranty(null);
            qc.invalidateQueries({ queryKey: ["infra-warranty"] });
          }}
        />
      )}
      {activeTab === "utilities" && (
        <UtilityFormModal
          open={showUtilityForm}
          onClose={() => {
            setShowUtilityForm(false);
            setEditingUtility(null);
          }}
          record={editingUtility}
          buildings={buildings}
          onSaved={() => {
            setShowUtilityForm(false);
            setEditingUtility(null);
            qc.invalidateQueries({ queryKey: ["infra-utilities"] });
          }}
        />
      )}
      {activeTab === "compliance" && (
        <ComplianceFormModal
          open={showComplianceForm}
          onClose={() => {
            setShowComplianceForm(false);
            setEditingCompliance(null);
          }}
          record={editingCompliance}
          onSaved={() => {
            setShowComplianceForm(false);
            setEditingCompliance(null);
            qc.invalidateQueries({ queryKey: ["infra-compliance"] });
          }}
        />
      )}
      {activeTab === "emergency" && (
        <EmergencyFormModal
          open={showEmergencyForm}
          onClose={() => {
            setShowEmergencyForm(false);
            setEditingEmergency(null);
          }}
          plan={editingEmergency}
          onSaved={() => {
            setShowEmergencyForm(false);
            setEditingEmergency(null);
            qc.invalidateQueries({ queryKey: ["infra-emergency"] });
          }}
        />
      )}
      {activeTab === "reports" && (
        <ReportFormModal
          open={showReportForm}
          onClose={() => {
            setShowReportForm(false);
            setEditingReport(null);
          }}
          report={editingReport}
          onSaved={() => {
            setShowReportForm(false);
            setEditingReport(null);
            qc.invalidateQueries({ queryKey: ["infra-reports"] });
          }}
        />
      )}
      {activeTab === "pestinsp" && (
        <PestInspFormModal
          open={showPestInspForm}
          onClose={() => {
            setShowPestInspForm(false);
            setEditingPestInsp(null);
          }}
          inspection={editingPestInsp}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowPestInspForm(false);
            setEditingPestInsp(null);
            qc.invalidateQueries({ queryKey: ["infra-pestinsp"] });
          }}
        />
      )}
      {activeTab === "pesttreat" && (
        <PestTreatFormModal
          open={showPestTreatForm}
          onClose={() => {
            setShowPestTreatForm(false);
            setEditingPestTreat(null);
          }}
          treatment={editingPestTreat}
          buildings={buildings}
          onSaved={() => {
            setShowPestTreatForm(false);
            setEditingPestTreat(null);
            qc.invalidateQueries({ queryKey: ["infra-pesttreat"] });
          }}
        />
      )}
      {activeTab === "green" && (
        <GreenFormModal
          open={showGreenForm}
          onClose={() => {
            setShowGreenForm(false);
            setEditingGreen(null);
          }}
          initiative={editingGreen}
          buildings={buildings}
          onSaved={() => {
            setShowGreenForm(false);
            setEditingGreen(null);
            qc.invalidateQueries({ queryKey: ["infra-green"] });
          }}
        />
      )}
      {activeTab === "water" && (
        <WaterFormModal
          open={showWaterForm}
          onClose={() => {
            setShowWaterForm(false);
            setEditingWater(null);
          }}
          record={editingWater}
          buildings={buildings}
          onSaved={() => {
            setShowWaterForm(false);
            setEditingWater(null);
            qc.invalidateQueries({ queryKey: ["infra-water"] });
          }}
        />
      )}
      {activeTab === "vendorperf" && (
        <VendorPerfFormModal
          open={showVendorPerfForm}
          onClose={() => {
            setShowVendorPerfForm(false);
            setEditingVendorPerf(null);
          }}
          rating={editingVendorPerf}
          vendors={vendors}
          onSaved={() => {
            setShowVendorPerfForm(false);
            setEditingVendorPerf(null);
            qc.invalidateQueries({ queryKey: ["infra-vendorperf"] });
          }}
        />
      )}
      {activeTab === "buildinginsp" && (
        <BuildingInspFormModal
          open={showBuildingInspForm}
          onClose={() => {
            setShowBuildingInspForm(false);
            setEditingBuildingInsp(null);
          }}
          inspection={editingBuildingInsp}
          buildings={buildings}
          onSaved={() => {
            setShowBuildingInspForm(false);
            setEditingBuildingInsp(null);
            qc.invalidateQueries({ queryKey: ["infra-buildinginsp"] });
          }}
        />
      )}
      {activeTab === "infraalerts" && (
        <InfraAlertFormModal
          open={showInfraAlertForm}
          onClose={() => {
            setShowInfraAlertForm(false);
            setEditingInfraAlert(null);
          }}
          alert={editingInfraAlert}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowInfraAlertForm(false);
            setEditingInfraAlert(null);
            qc.invalidateQueries({ queryKey: ["infra-infraalerts"] });
          }}
        />
      )}
      {activeTab === "floorplans" && (
        <FloorPlanFormModal
          open={showFloorPlanForm}
          onClose={() => {
            setShowFloorPlanForm(false);
            setEditingFloorPlan(null);
          }}
          plan={editingFloorPlan}
          buildings={buildings}
          onSaved={() => {
            setShowFloorPlanForm(false);
            setEditingFloorPlan(null);
            qc.invalidateQueries({ queryKey: ["infra-floorplans"] });
          }}
        />
      )}
      {activeTab === "equipment" && (
        <EquipmentFormModal
          open={showEquipmentForm}
          onClose={() => {
            setShowEquipmentForm(false);
            setEditingEquipment(null);
          }}
          equipment={editingEquipment}
          rooms={rooms}
          onSaved={() => {
            setShowEquipmentForm(false);
            setEditingEquipment(null);
            qc.invalidateQueries({ queryKey: ["infra-equipment"] });
          }}
        />
      )}
      {activeTab === "costs" && (
        <CostFormModal
          open={showCostForm}
          onClose={() => {
            setShowCostForm(false);
            setEditingCost(null);
          }}
          record={editingCost}
          buildings={buildings}
          workOrders={workOrders}
          onSaved={() => {
            setShowCostForm(false);
            setEditingCost(null);
            qc.invalidateQueries({ queryKey: ["infra-costs"] });
          }}
        />
      )}
      {activeTab === "requests" && (
        <RequestFormModal
          open={showRequestForm}
          onClose={() => {
            setShowRequestForm(false);
            setEditingRequest(null);
          }}
          request={editingRequest}
          buildings={buildings}
          rooms={rooms}
          onSaved={() => {
            setShowRequestForm(false);
            setEditingRequest(null);
            qc.invalidateQueries({ queryKey: ["infra-requests"] });
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
          {tab === "comments" && <CommentCard item={item as WorkOrderComment} />}
          {tab === "assignments" && <AssignmentCard item={item as AssetAssignment} />}
          {tab === "lifecycle" && <LifecycleCard item={item as AssetLifecycle} />}
          {tab === "warranty" && <WarrantyCard item={item as WarrantyClaim} />}
          {tab === "utilities" && <UtilityCard item={item as UtilityRecord} />}
          {tab === "compliance" && <ComplianceCard item={item as ComplianceRecord} />}
          {tab === "emergency" && <EmergencyCard item={item as EmergencyPlan} />}
          {tab === "reports" && <ReportCard item={item as InfraReport} />}
          {tab === "pestinsp" && <PestInspCard item={item as PestInspection} />}
          {tab === "pesttreat" && <PestTreatCard item={item as PestTreatment} />}
          {tab === "green" && <GreenCard item={item as GreenInitiative} />}
          {tab === "water" && <WaterCard item={item as WaterUsage} />}
          {tab === "vendorperf" && <VendorPerfCard item={item as VendorRating} />}
          {tab === "buildinginsp" && <BuildingInspCard item={item as BuildingInspection} />}
          {tab === "infraalerts" && <InfraAlertCard item={item as InfraAlert} />}
          {tab === "floorplans" && <FloorPlanCard item={item as FloorPlan} />}
          {tab === "equipment" && <EquipmentCard item={item as RoomEquipment} />}
          {tab === "costs" && <CostCard item={item as CostRecord} />}
          {tab === "requests" && <RequestCard item={item as MaintRequest} />}
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

// ─── Comment Card ────────────────────────────────────────────────────────────

function CommentCard({ item }: { item: WorkOrderComment }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.work_order_title || "Comment"}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.author_name ?? "—"}
        {item.created_at && ` · ${new Date(item.created_at).toLocaleDateString()}`}
      </p>
      <p className="mt-2 line-clamp-2 text-xs text-slate-500 dark:text-slate-400">{item.comment}</p>
    </>
  );
}

// ─── Assignment Card ─────────────────────────────────────────────────────────

function AssignmentCard({ item }: { item: AssetAssignment }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.asset_name || "Asset assignment"}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.assigned_to_name ?? "—"}
        {item.room_name && ` · ${item.room_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.status && <Badge value={item.status_display ?? item.status} colors={STATUS_COLORS} />}
        {item.asset_tag && (
          <span className="rounded-full bg-slate-100 px-2 py-0.5 font-mono text-xs text-slate-500 dark:bg-slate-800 dark:text-slate-400">
            {item.asset_tag}
          </span>
        )}
      </div>
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-400">
        {item.assigned_date && <span>📅 {item.assigned_date}</span>}
        {item.department && <span>🏢 {item.department}</span>}
      </div>
    </>
  );
}

// ─── Lifecycle Card ──────────────────────────────────────────────────────────

function LifecycleCard({ item }: { item: AssetLifecycle }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.asset_name || "Lifecycle event"}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.event_display ?? item.event}
        {item.event_date && ` · ${item.event_date}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.event && <Badge value={item.event_display ?? item.event} colors={STATUS_COLORS} />}
        {item.cost != null && item.cost !== "" && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 font-medium text-green-700 dark:bg-green-900/40 dark:text-green-300">
            ${Number(item.cost).toLocaleString()}
          </span>
        )}
      </div>
      {item.description && (
        <p className="mt-1 line-clamp-2 text-xs text-slate-500 dark:text-slate-400">
          {item.description}
        </p>
      )}
    </>
  );
}

// ─── Warranty Card ───────────────────────────────────────────────────────────

function WarrantyCard({ item }: { item: WarrantyClaim }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.claim_number || item.asset_name || "Warranty claim"}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.warranty_provider ?? "—"}
        {item.claim_date && ` · ${item.claim_date}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.status && <Badge value={item.status_display ?? item.status} colors={STATUS_COLORS} />}
        {item.asset_tag && (
          <span className="rounded-full bg-slate-100 px-2 py-0.5 font-mono text-xs text-slate-500 dark:bg-slate-800 dark:text-slate-400">
            {item.asset_tag}
          </span>
        )}
      </div>
      {item.issue_description && (
        <p className="mt-1 line-clamp-2 text-xs text-slate-500 dark:text-slate-400">
          {item.issue_description}
        </p>
      )}
    </>
  );
}

// ─── Utility Card ────────────────────────────────────────────────────────────

function UtilityCard({ item }: { item: UtilityRecord }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.utility_type_display ?? item.utility_type}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name ?? "—"}
        {item.reading_date && ` · ${item.reading_date}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.reading_value != null && item.reading_value !== "" && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 font-medium text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
            {Number(item.reading_value).toLocaleString()} {item.units}
          </span>
        )}
        {item.consumption != null && item.consumption !== "" && (
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            Δ {Number(item.consumption).toLocaleString()}
          </span>
        )}
        {item.cost != null && item.cost !== "" && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 font-medium text-green-700 dark:bg-green-900/40 dark:text-green-300">
            ${Number(item.cost).toLocaleString()}
          </span>
        )}
      </div>
    </>
  );
}

// ─── Compliance Card ─────────────────────────────────────────────────────────

function ComplianceCard({ item }: { item: ComplianceRecord }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.compliance_type_display ?? item.compliance_type}
        {item.regulation_reference && ` · ${item.regulation_reference}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.status && <Badge value={item.status_display ?? item.status} colors={STATUS_COLORS} />}
        {item.next_audit_date && <span>🔎 Next audit: {item.next_audit_date}</span>}
      </div>
    </>
  );
}

// ─── Emergency Card ──────────────────────────────────────────────────────────

function EmergencyCard({ item }: { item: EmergencyPlan }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.plan_type_display ?? item.plan_type}
        {item.next_drill_date && ` · Drill: ${item.next_drill_date}`}
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
        {item.last_drill_date && <span>🪖 Last drill: {item.last_drill_date}</span>}
      </div>
      {item.assembly_points && (
        <p className="mt-1 line-clamp-1 text-xs text-slate-500 dark:text-slate-400">
          📍 {item.assembly_points}
        </p>
      )}
    </>
  );
}

// ─── Report Card ─────────────────────────────────────────────────────────────

function ReportCard({ item }: { item: InfraReport }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.report_type_display ?? item.report_type}
        {item.generated_by_name && ` · ${item.generated_by_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.date_from && item.date_to && (
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            📅 {item.date_from} → {item.date_to}
          </span>
        )}
        {item.file_url && (
          <a
            href={item.file_url}
            target="_blank"
            rel="noreferrer"
            className="rounded-full bg-indigo-100 px-2 py-0.5 font-medium text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
          >
            ⬇ File
          </a>
        )}
      </div>
      {item.summary && (
        <p className="mt-1 line-clamp-2 text-xs text-slate-500 dark:text-slate-400">
          {item.summary}
        </p>
      )}
    </>
  );
}

// ─── Pest Inspection Card ────────────────────────────────────────────────────

function PestInspCard({ item }: { item: PestInspection }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.inspection_type_display ?? item.inspection_type}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name ?? "—"}
        {item.room_name && ` · ${item.room_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.status && <Badge value={item.status_display ?? item.status} colors={STATUS_COLORS} />}
        {item.scheduled_date && <span>📅 {item.scheduled_date}</span>}
        {item.follow_up_required && (
          <span className="rounded-full bg-amber-100 px-2 py-0.5 font-medium text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
            Follow-up needed
          </span>
        )}
      </div>
      {item.pests_found && (
        <p className="mt-1 line-clamp-1 text-xs text-slate-500 dark:text-slate-400">
          🐜 {item.pests_found}
        </p>
      )}
    </>
  );
}

// ─── Pest Treatment Card ─────────────────────────────────────────────────────

function PestTreatCard({ item }: { item: PestTreatment }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.treatment_type || "Pest treatment"}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name ?? "—"}
        {item.treatment_date && ` · ${item.treatment_date}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.pest_target && (
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            🐛 {item.pest_target}
          </span>
        )}
        {item.cost != null && item.cost !== "" && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 font-medium text-green-700 dark:bg-green-900/40 dark:text-green-300">
            ${Number(item.cost).toLocaleString()}
          </span>
        )}
        {item.safety_re_entry_hours > 0 && (
          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
            ⏳ Re-entry {item.safety_re_entry_hours}h
          </span>
        )}
      </div>
    </>
  );
}

// ─── Green Initiative Card ───────────────────────────────────────────────────

function GreenCard({ item }: { item: GreenInitiative }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.initiative_type_display ?? item.initiative_type}
        {item.building_name && ` · ${item.building_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.status && <Badge value={item.status_display ?? item.status} colors={STATUS_COLORS} />}
        {item.carbon_reduction_kg != null && item.carbon_reduction_kg !== "" && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 font-medium text-green-700 dark:bg-green-900/40 dark:text-green-300">
            🌱 {Number(item.carbon_reduction_kg).toLocaleString()} kg CO₂
          </span>
        )}
      </div>
      {item.estimated_savings != null && item.estimated_savings !== "" && (
        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
          💰 Est. savings ${Number(item.estimated_savings).toLocaleString()}
        </p>
      )}
    </>
  );
}

// ─── Water Usage Card ────────────────────────────────────────────────────────

function WaterCard({ item }: { item: WaterUsage }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.building_name || "Water usage"}
      </p>
      <p className="truncate text-xs text-slate-400">{item.record_date ?? "—"}</p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.usage_gallons != null && item.usage_gallons !== "" && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 font-medium text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
            💧 {Number(item.usage_gallons).toLocaleString()} gal
          </span>
        )}
        {item.cost != null && item.cost !== "" && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 font-medium text-green-700 dark:bg-green-900/40 dark:text-green-300">
            ${Number(item.cost).toLocaleString()}
          </span>
        )}
        {item.leak_detected && (
          <span className="rounded-full bg-red-100 px-2 py-0.5 font-medium text-red-700 dark:bg-red-900/40 dark:text-red-300">
            🚨 Leak detected
          </span>
        )}
      </div>
    </>
  );
}

// ─── Vendor Performance Card ─────────────────────────────────────────────────

function VendorPerfCard({ item }: { item: VendorRating }) {
  const avg =
    (item.quality_rating + item.timeliness_rating + item.communication_rating + item.value_rating) /
    4;
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.vendor_contract_name || "Vendor rating"}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.service_type_display ?? item.service_type}
        {item.evaluation_date && ` · ${item.evaluation_date}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        <span className="rounded-full bg-amber-100 px-2 py-0.5 font-medium text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
          ⭐ {avg.toFixed(1)}/5
        </span>
        {item.would_rehire !== null && item.would_rehire !== undefined && (
          <span
            className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
              item.would_rehire
                ? "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300"
                : "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300"
            }`}
          >
            {item.would_rehire ? "Would rehire" : "Would not rehire"}
          </span>
        )}
      </div>
      {item.comments && (
        <p className="mt-1 line-clamp-2 text-xs text-slate-500 dark:text-slate-400">
          {item.comments}
        </p>
      )}
    </>
  );
}

// ─── Building Inspection Card ────────────────────────────────────────────────

function BuildingInspCard({ item }: { item: BuildingInspection }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.inspection_type_display ?? item.inspection_type}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name ?? "—"}
        {item.inspection_date && ` · ${item.inspection_date}`}
        {item.inspector_name && ` · ${item.inspector_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.result && <Badge value={item.result_display ?? item.result} colors={STATUS_COLORS} />}
        {item.follow_up_required && (
          <span className="rounded-full bg-amber-100 px-2 py-0.5 font-medium text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
            Follow-up required
          </span>
        )}
      </div>
      {item.violations && (
        <p className="mt-1 line-clamp-1 text-xs text-red-500 dark:text-red-400">
          ⚠ {item.violations}
        </p>
      )}
    </>
  );
}

// ─── Infra Alert Card ────────────────────────────────────────────────────────

function InfraAlertCard({ item }: { item: InfraAlert }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.alert_type_display ?? item.alert_type}
        {item.building_name && ` · ${item.building_name}`}
        {item.room_name && ` · ${item.room_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.severity && (
          <Badge value={item.severity_display ?? item.severity} colors={STATUS_COLORS} />
        )}
        {item.status && <Badge value={item.status_display ?? item.status} colors={STATUS_COLORS} />}
      </div>
      {item.description && (
        <p className="mt-1 line-clamp-2 text-xs text-slate-500 dark:text-slate-400">
          {item.description}
        </p>
      )}
    </>
  );
}

// ─── Floor Plan Card ─────────────────────────────────────────────────────────

function FloorPlanCard({ item }: { item: FloorPlan }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.floor_name || `Floor ${item.floor_number}`}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name ?? "—"}
        {item.floor_number > 0 && ` · Floor ${item.floor_number}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.total_rooms > 0 && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 font-medium text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
            🚪 {item.total_rooms} rooms
          </span>
        )}
        {item.total_area_sqft != null && item.total_area_sqft !== "" && (
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-slate-600 dark:bg-slate-800 dark:text-slate-300">
            📐 {Number(item.total_area_sqft).toLocaleString()} sqft
          </span>
        )}
        {item.is_current && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 font-medium text-green-700 dark:bg-green-900/40 dark:text-green-300">
            Current
          </span>
        )}
      </div>
      {item.plan_file && (
        <a
          href={item.plan_file}
          target="_blank"
          rel="noreferrer"
          className="mt-1 inline-block text-xs font-medium text-indigo-600 dark:text-indigo-400"
        >
          🗺 View plan
        </a>
      )}
    </>
  );
}

// ─── Room Equipment Card ─────────────────────────────────────────────────────

function EquipmentCard({ item }: { item: RoomEquipment }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.name || item.equipment_type_display || item.equipment_type}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.room_name ?? "—"}
        {item.brand && ` · ${item.brand}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.status && <Badge value={item.status_display ?? item.status} colors={STATUS_COLORS} />}
        {item.asset_tag && (
          <span className="rounded-full bg-slate-100 px-2 py-0.5 font-mono text-xs text-slate-500 dark:bg-slate-800 dark:text-slate-400">
            {item.asset_tag}
          </span>
        )}
        {item.warranty_expiry && <span>🛡 {item.warranty_expiry}</span>}
      </div>
    </>
  );
}

// ─── Maintenance Cost Card ───────────────────────────────────────────────────

function CostCard({ item }: { item: CostRecord }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.cost_category_display ?? item.cost_category}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name ?? item.work_order_title ?? "—"}
        {item.cost_date && ` · ${item.cost_date}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.amount != null && item.amount !== "" && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 font-medium text-green-700 dark:bg-green-900/40 dark:text-green-300">
            ${Number(item.amount).toLocaleString()}
          </span>
        )}
        {item.is_approved ? (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-green-700 dark:bg-green-900/40 dark:text-green-300">
            ✓ Approved
          </span>
        ) : (
          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
            Pending approval
          </span>
        )}
      </div>
    </>
  );
}

// ─── Maintenance Request Card ────────────────────────────────────────────────

function RequestCard({ item }: { item: MaintRequest }) {
  return (
    <>
      <p className="truncate font-semibold text-slate-900 group-hover:text-indigo-600 dark:text-white dark:group-hover:text-indigo-400">
        {item.title}
      </p>
      <p className="truncate text-xs text-slate-400">
        {item.building_name ?? "—"}
        {item.room_name && ` · ${item.room_name}`}
        {item.requested_by_name && ` · ${item.requested_by_name}`}
      </p>
      <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
        {item.priority && (
          <Badge value={item.priority_display ?? item.priority} colors={STATUS_COLORS} />
        )}
        {item.status && <Badge value={item.status_display ?? item.status} colors={STATUS_COLORS} />}
        {item.assigned_to_name && <span>🔧 {item.assigned_to_name}</span>}
      </div>
      {item.description && (
        <p className="mt-1 line-clamp-2 text-xs text-slate-500 dark:text-slate-400">
          {item.description}
        </p>
      )}
    </>
  );
}

// ─── Comment Form Modal ──────────────────────────────────────────────────────

function CommentFormModal({
  open,
  onClose,
  comment,
  workOrders,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  comment?: WorkOrderComment | null;
  workOrders: WorkOrder[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    work_order: comment?.work_order ?? "",
    comment: comment?.comment ?? "",
  });
  const isEdit = !!comment;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/work-order-comments/", data),
    onSuccess: () => {
      toast.success("Comment added");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/work-order-comments/${comment!.id}/`, data),
    onSuccess: () => {
      toast.success("Comment updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.work_order) return toast.error("Select a work order");
    if (!f.comment.trim()) return toast.error("Comment is required");
    if (isEdit) updateMut.mutate(f);
    else createMut.mutate(f);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Comment" : "Add Comment"}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>Work Order *</label>
          <select
            value={f.work_order}
            onChange={(e) => setF((p) => ({ ...p, work_order: e.target.value }))}
            className={inputCls}
            required
          >
            <option value="">Select work order...</option>
            {workOrders.map((wo) => (
              <option key={wo.id} value={wo.id}>
                {wo.title}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelCls}>Comment *</label>
          <textarea
            value={f.comment}
            onChange={(e) => setF((p) => ({ ...p, comment: e.target.value }))}
            rows={3}
            className={inputCls}
            required
            placeholder="Progress update, notes..."
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

// ─── Assignment Form Modal ───────────────────────────────────────────────────

function AssignmentFormModal({
  open,
  onClose,
  assignment,
  assets,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  assignment?: AssetAssignment | null;
  assets: Asset[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    asset: assignment?.asset ?? "",
    department: assignment?.department ?? "",
    assigned_date: assignment?.assigned_date ?? "",
    returned_date: assignment?.returned_date ?? "",
    status: assignment?.status ?? "active",
    condition_at_assignment: assignment?.condition_at_assignment ?? "",
    condition_at_return: assignment?.condition_at_return ?? "",
    notes: assignment?.notes ?? "",
  });
  const isEdit = !!assignment;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/asset-assignments/", data),
    onSuccess: () => {
      toast.success("Assignment created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/asset-assignments/${assignment!.id}/`, data),
    onSuccess: () => {
      toast.success("Assignment updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.asset) return toast.error("Select an asset");
    const data = {
      ...f,
      returned_date: f.returned_date || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Assignment" : "Add Asset Assignment"}
    >
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Asset *</label>
            <select
              value={f.asset}
              onChange={(e) => setF((p) => ({ ...p, asset: e.target.value }))}
              className={inputCls}
              required
            >
              <option value="">Select asset...</option>
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.asset_tag})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Department</label>
            <input
              value={f.department}
              onChange={(e) => setF((p) => ({ ...p, department: e.target.value }))}
              className={inputCls}
              placeholder="e.g. Science"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Assigned Date</label>
            <input
              type="date"
              value={f.assigned_date}
              onChange={(e) => setF((p) => ({ ...p, assigned_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Returned Date</label>
            <input
              type="date"
              value={f.returned_date}
              onChange={(e) => setF((p) => ({ ...p, returned_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <SelectField
            label="Status"
            value={f.status}
            options={ASSIGNMENT_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Condition at Assignment</label>
            <input
              value={f.condition_at_assignment}
              onChange={(e) => setF((p) => ({ ...p, condition_at_assignment: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Condition at Return</label>
            <input
              value={f.condition_at_return}
              onChange={(e) => setF((p) => ({ ...p, condition_at_return: e.target.value }))}
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

// ─── Lifecycle Form Modal ────────────────────────────────────────────────────

function LifecycleFormModal({
  open,
  onClose,
  event,
  assets,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  event?: AssetLifecycle | null;
  assets: Asset[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    asset: event?.asset ?? "",
    event: event?.event ?? "purchased",
    event_date: event?.event_date ?? "",
    description: event?.description ?? "",
    cost: event?.cost?.toString() ?? "",
    notes: event?.notes ?? "",
  });
  const isEdit = !!event;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/asset-lifecycle/", data),
    onSuccess: () => {
      toast.success("Lifecycle event added");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/asset-lifecycle/${event!.id}/`, data),
    onSuccess: () => {
      toast.success("Lifecycle event updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.asset) return toast.error("Select an asset");
    const data = {
      ...f,
      cost: f.cost === "" ? null : Number(f.cost),
      event_date: f.event_date || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Event" : "Add Lifecycle Event"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Asset *</label>
            <select
              value={f.asset}
              onChange={(e) => setF((p) => ({ ...p, asset: e.target.value }))}
              className={inputCls}
              required
            >
              <option value="">Select asset...</option>
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.asset_tag})
                </option>
              ))}
            </select>
          </div>
          <SelectField
            label="Event"
            value={f.event}
            options={LIFECYCLE_EVENTS}
            onChange={(v) => setF((p) => ({ ...p, event: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Event Date</label>
            <input
              type="date"
              value={f.event_date}
              onChange={(e) => setF((p) => ({ ...p, event_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Cost ($)</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={f.cost}
              onChange={(e) => setF((p) => ({ ...p, cost: e.target.value }))}
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

// ─── Warranty Form Modal ─────────────────────────────────────────────────────

function WarrantyFormModal({
  open,
  onClose,
  claim,
  assets,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  claim?: WarrantyClaim | null;
  assets: Asset[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    asset: claim?.asset ?? "",
    claim_number: claim?.claim_number ?? "",
    issue_description: claim?.issue_description ?? "",
    claim_date: claim?.claim_date ?? "",
    warranty_provider: claim?.warranty_provider ?? "",
    contact_person: claim?.contact_person ?? "",
    contact_phone: claim?.contact_phone ?? "",
    contact_email: claim?.contact_email ?? "",
    status: claim?.status ?? "open",
    resolution_date: claim?.resolution_date ?? "",
    resolution_notes: claim?.resolution_notes ?? "",
    cost_covered: claim?.cost_covered?.toString() ?? "",
    cost_customer: claim?.cost_customer?.toString() ?? "",
  });
  const isEdit = !!claim;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/warranty-claims/", data),
    onSuccess: () => {
      toast.success("Warranty claim created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/warranty-claims/${claim!.id}/`, data),
    onSuccess: () => {
      toast.success("Warranty claim updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.asset) return toast.error("Select an asset");
    if (!f.claim_number.trim()) return toast.error("Claim number is required");
    const data = {
      ...f,
      claim_date: f.claim_date || null,
      resolution_date: f.resolution_date || null,
      cost_covered: f.cost_covered === "" ? null : Number(f.cost_covered),
      cost_customer: f.cost_customer === "" ? null : Number(f.cost_customer),
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Claim" : "Add Warranty Claim"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Asset *</label>
            <select
              value={f.asset}
              onChange={(e) => setF((p) => ({ ...p, asset: e.target.value }))}
              className={inputCls}
              required
            >
              <option value="">Select asset...</option>
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name} ({a.asset_tag})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Claim Number *</label>
            <input
              value={f.claim_number}
              onChange={(e) => setF((p) => ({ ...p, claim_number: e.target.value }))}
              className={inputCls}
              required
              placeholder="e.g. WC-2026-001"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Claim Date</label>
            <input
              type="date"
              value={f.claim_date}
              onChange={(e) => setF((p) => ({ ...p, claim_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Provider</label>
            <input
              value={f.warranty_provider}
              onChange={(e) => setF((p) => ({ ...p, warranty_provider: e.target.value }))}
              className={inputCls}
              placeholder="Vendor / insurer"
            />
          </div>
          <SelectField
            label="Status"
            value={f.status}
            options={WARRANTY_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div>
          <label className={labelCls}>Issue Description</label>
          <textarea
            value={f.issue_description}
            onChange={(e) => setF((p) => ({ ...p, issue_description: e.target.value }))}
            rows={2}
            className={inputCls}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Contact Person</label>
            <input
              value={f.contact_person}
              onChange={(e) => setF((p) => ({ ...p, contact_person: e.target.value }))}
              className={inputCls}
            />
          </div>
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
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Cost Covered ($)</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={f.cost_covered}
              onChange={(e) => setF((p) => ({ ...p, cost_covered: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Cost to Customer ($)</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={f.cost_customer}
              onChange={(e) => setF((p) => ({ ...p, cost_customer: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Resolution Date</label>
            <input
              type="date"
              value={f.resolution_date}
              onChange={(e) => setF((p) => ({ ...p, resolution_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Resolution Notes</label>
            <input
              value={f.resolution_notes}
              onChange={(e) => setF((p) => ({ ...p, resolution_notes: e.target.value }))}
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

// ─── Utility Form Modal ──────────────────────────────────────────────────────

function UtilityFormModal({
  open,
  onClose,
  record,
  buildings,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  record?: UtilityRecord | null;
  buildings: Building[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: record?.building ?? "",
    utility_type: record?.utility_type ?? "electricity",
    reading_date: record?.reading_date ?? "",
    reading_value: record?.reading_value?.toString() ?? "",
    units: record?.units ?? "",
    cost: record?.cost?.toString() ?? "",
    previous_reading: record?.previous_reading?.toString() ?? "",
    consumption: record?.consumption?.toString() ?? "",
    notes: record?.notes ?? "",
  });
  const isEdit = !!record;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/utility-tracker/", data),
    onSuccess: () => {
      toast.success("Utility reading saved");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/utility-tracker/${record!.id}/`, data),
    onSuccess: () => {
      toast.success("Utility reading updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    if (f.reading_value === "") return toast.error("Reading value is required");
    const data = {
      ...f,
      reading_date: f.reading_date || null,
      reading_value: Number(f.reading_value),
      cost: f.cost === "" ? null : Number(f.cost),
      previous_reading: f.previous_reading === "" ? null : Number(f.previous_reading),
      consumption: f.consumption === "" ? null : Number(f.consumption),
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Reading" : "Add Utility Reading"}>
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
          <SelectField
            label="Utility Type"
            value={f.utility_type}
            options={UTILITY_TYPES}
            onChange={(v) => setF((p) => ({ ...p, utility_type: v }))}
          />
        </div>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <label className={labelCls}>Reading Date</label>
            <input
              type="date"
              value={f.reading_date}
              onChange={(e) => setF((p) => ({ ...p, reading_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Reading Value *</label>
            <input
              type="number"
              min={0}
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
              placeholder="kWh, m³..."
            />
          </div>
          <div>
            <label className={labelCls}>Cost ($)</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={f.cost}
              onChange={(e) => setF((p) => ({ ...p, cost: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Previous Reading</label>
            <input
              type="number"
              min={0}
              value={f.previous_reading}
              onChange={(e) => setF((p) => ({ ...p, previous_reading: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Consumption</label>
            <input
              type="number"
              min={0}
              value={f.consumption}
              onChange={(e) => setF((p) => ({ ...p, consumption: e.target.value }))}
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

// ─── Compliance Form Modal ───────────────────────────────────────────────────

function ComplianceFormModal({
  open,
  onClose,
  record,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  record?: ComplianceRecord | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    title: record?.title ?? "",
    compliance_type: record?.compliance_type ?? "fire_safety",
    description: record?.description ?? "",
    regulation_reference: record?.regulation_reference ?? "",
    status: record?.status ?? "compliant",
    last_audit_date: record?.last_audit_date ?? "",
    next_audit_date: record?.next_audit_date ?? "",
    expiry_date: record?.expiry_date ?? "",
    document_url: record?.document_url ?? "",
  });
  const isEdit = !!record;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/compliance-records/", data),
    onSuccess: () => {
      toast.success("Compliance record created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/compliance-records/${record!.id}/`, data),
    onSuccess: () => {
      toast.success("Compliance record updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.title.trim()) return toast.error("Title is required");
    const data = {
      ...f,
      last_audit_date: f.last_audit_date || null,
      next_audit_date: f.next_audit_date || null,
      expiry_date: f.expiry_date || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Record" : "Add Compliance Record"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Title *</label>
            <input
              value={f.title}
              onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
              className={inputCls}
              required
              placeholder="e.g. Fire extinguisher inspection"
            />
          </div>
          <SelectField
            label="Compliance Type"
            value={f.compliance_type}
            options={COMPLIANCE_TYPES}
            onChange={(v) => setF((p) => ({ ...p, compliance_type: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Status"
            value={f.status}
            options={COMPLIANCE_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
          <div>
            <label className={labelCls}>Regulation Reference</label>
            <input
              value={f.regulation_reference}
              onChange={(e) => setF((p) => ({ ...p, regulation_reference: e.target.value }))}
              className={inputCls}
              placeholder="e.g. NFPA 10"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Last Audit Date</label>
            <input
              type="date"
              value={f.last_audit_date}
              onChange={(e) => setF((p) => ({ ...p, last_audit_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Next Audit Date</label>
            <input
              type="date"
              value={f.next_audit_date}
              onChange={(e) => setF((p) => ({ ...p, next_audit_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Expiry Date</label>
            <input
              type="date"
              value={f.expiry_date}
              onChange={(e) => setF((p) => ({ ...p, expiry_date: e.target.value }))}
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
        <div>
          <label className={labelCls}>Document URL</label>
          <input
            value={f.document_url}
            onChange={(e) => setF((p) => ({ ...p, document_url: e.target.value }))}
            className={inputCls}
            placeholder="https://..."
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

// ─── Emergency Plan Form Modal ───────────────────────────────────────────────

function EmergencyFormModal({
  open,
  onClose,
  plan,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  plan?: EmergencyPlan | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    title: plan?.title ?? "",
    plan_type: plan?.plan_type ?? "fire",
    description: plan?.description ?? "",
    procedures: plan?.procedures ?? "",
    assembly_points: plan?.assembly_points ?? "",
    emergency_contacts: plan?.emergency_contacts ?? "",
    last_drill_date: plan?.last_drill_date ?? "",
    next_drill_date: plan?.next_drill_date ?? "",
    last_review_date: plan?.last_review_date ?? "",
    is_active: plan?.is_active ?? true,
  });
  const isEdit = !!plan;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/emergency-plans/", data),
    onSuccess: () => {
      toast.success("Emergency plan created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/infrastructure/emergency-plans/${plan!.id}/`, data),
    onSuccess: () => {
      toast.success("Emergency plan updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.title.trim()) return toast.error("Title is required");
    const data = {
      ...f,
      last_drill_date: f.last_drill_date || null,
      next_drill_date: f.next_drill_date || null,
      last_review_date: f.last_review_date || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Plan" : "Add Emergency Plan"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Title *</label>
            <input
              value={f.title}
              onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
              className={inputCls}
              required
              placeholder="e.g. Fire evacuation plan"
            />
          </div>
          <SelectField
            label="Plan Type"
            value={f.plan_type}
            options={PLAN_TYPES}
            onChange={(v) => setF((p) => ({ ...p, plan_type: v }))}
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
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Procedures</label>
            <textarea
              value={f.procedures}
              onChange={(e) => setF((p) => ({ ...p, procedures: e.target.value }))}
              rows={2}
              className={inputCls}
              placeholder="Step-by-step instructions"
            />
          </div>
          <div>
            <label className={labelCls}>Assembly Points</label>
            <textarea
              value={f.assembly_points}
              onChange={(e) => setF((p) => ({ ...p, assembly_points: e.target.value }))}
              rows={2}
              className={inputCls}
              placeholder="e.g. Main field, front gate"
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>Emergency Contacts</label>
          <textarea
            value={f.emergency_contacts}
            onChange={(e) => setF((p) => ({ ...p, emergency_contacts: e.target.value }))}
            rows={2}
            className={inputCls}
            placeholder="e.g. Fire dept: 911, Campus security: ext 200"
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Last Drill Date</label>
            <input
              type="date"
              value={f.last_drill_date}
              onChange={(e) => setF((p) => ({ ...p, last_drill_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Next Drill Date</label>
            <input
              type="date"
              value={f.next_drill_date}
              onChange={(e) => setF((p) => ({ ...p, next_drill_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Last Review Date</label>
            <input
              type="date"
              value={f.last_review_date}
              onChange={(e) => setF((p) => ({ ...p, last_review_date: e.target.value }))}
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
          Plan is active
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

// ─── Report Form Modal ───────────────────────────────────────────────────────

function ReportFormModal({
  open,
  onClose,
  report,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  report?: InfraReport | null;
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    title: report?.title ?? "",
    report_type: report?.report_type ?? "general",
    description: report?.description ?? "",
    date_from: report?.date_from ?? "",
    date_to: report?.date_to ?? "",
    summary: report?.summary ?? "",
  });
  const isEdit = !!report;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/reports/", data),
    onSuccess: () => {
      toast.success("Report created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) => api.patch(`/infrastructure/reports/${report!.id}/`, data),
    onSuccess: () => {
      toast.success("Report updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.title.trim()) return toast.error("Title is required");
    const data = {
      ...f,
      date_from: f.date_from || null,
      date_to: f.date_to || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Report" : "Generate Report"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Title *</label>
            <input
              value={f.title}
              onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
              className={inputCls}
              required
              placeholder="e.g. Q3 maintenance summary"
            />
          </div>
          <SelectField
            label="Report Type"
            value={f.report_type}
            options={REPORT_TYPES}
            onChange={(v) => setF((p) => ({ ...p, report_type: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Date From</label>
            <input
              type="date"
              value={f.date_from}
              onChange={(e) => setF((p) => ({ ...p, date_from: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Date To</label>
            <input
              type="date"
              value={f.date_to}
              onChange={(e) => setF((p) => ({ ...p, date_to: e.target.value }))}
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
        <div>
          <label className={labelCls}>Summary</label>
          <textarea
            value={f.summary}
            onChange={(e) => setF((p) => ({ ...p, summary: e.target.value }))}
            rows={3}
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

// ─── Pest Inspection Form Modal ──────────────────────────────────────────────

function PestInspFormModal({
  open,
  onClose,
  inspection,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  inspection?: PestInspection | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: inspection?.building ?? "",
    room: inspection?.room ?? "",
    inspection_type: inspection?.inspection_type ?? "routine",
    status: inspection?.status ?? "scheduled",
    scheduled_date: inspection?.scheduled_date ?? "",
    completed_date: inspection?.completed_date ?? "",
    inspector_name: inspection?.inspector_name ?? "",
    pests_found: inspection?.pests_found ?? "",
    treatment_applied: inspection?.treatment_applied ?? "",
    follow_up_required: inspection?.follow_up_required ?? false,
    treatment_cost: inspection?.treatment_cost?.toString() ?? "",
  });
  const isEdit = !!inspection;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/pest-control-inspection/", data),
    onSuccess: () => {
      toast.success("Pest inspection created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/pest-control-inspection/${inspection!.id}/`, data),
    onSuccess: () => {
      toast.success("Pest inspection updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    if (!f.scheduled_date) return toast.error("Scheduled date is required");
    const data = {
      ...f,
      room: f.room || null,
      scheduled_date: f.scheduled_date || null,
      completed_date: f.completed_date || null,
      treatment_cost: f.treatment_cost === "" ? null : Number(f.treatment_cost),
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Inspection" : "Add Pest Inspection"}>
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
          <SelectField
            label="Inspection Type"
            value={f.inspection_type}
            options={PEST_INSPECTION_TYPES}
            onChange={(v) => setF((p) => ({ ...p, inspection_type: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={PEST_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
          <div>
            <label className={labelCls}>Inspector</label>
            <input
              value={f.inspector_name}
              onChange={(e) => setF((p) => ({ ...p, inspector_name: e.target.value }))}
              className={inputCls}
            />
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
            <label className={labelCls}>Treatment Cost ($)</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={f.treatment_cost}
              onChange={(e) => setF((p) => ({ ...p, treatment_cost: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Pests Found</label>
            <textarea
              value={f.pests_found}
              onChange={(e) => setF((p) => ({ ...p, pests_found: e.target.value }))}
              rows={2}
              className={inputCls}
              placeholder="e.g. ants in hallway B"
            />
          </div>
          <div>
            <label className={labelCls}>Treatment Applied</label>
            <textarea
              value={f.treatment_applied}
              onChange={(e) => setF((p) => ({ ...p, treatment_applied: e.target.value }))}
              rows={2}
              className={inputCls}
            />
          </div>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.follow_up_required}
            onChange={(e) => setF((p) => ({ ...p, follow_up_required: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
          />
          Follow-up required
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

// ─── Pest Treatment Form Modal ───────────────────────────────────────────────

function PestTreatFormModal({
  open,
  onClose,
  treatment,
  buildings,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  treatment?: PestTreatment | null;
  buildings: Building[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: treatment?.building ?? "",
    treatment_date: treatment?.treatment_date ?? "",
    treatment_type: treatment?.treatment_type ?? "",
    pest_target: treatment?.pest_target ?? "",
    chemical_name: treatment?.chemical_name ?? "",
    safety_re_entry_hours: treatment?.safety_re_entry_hours ?? 24,
    cost: treatment?.cost?.toString() ?? "",
    notes: treatment?.notes ?? "",
  });
  const isEdit = !!treatment;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/pest-treatment/", data),
    onSuccess: () => {
      toast.success("Treatment logged");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/pest-treatment/${treatment!.id}/`, data),
    onSuccess: () => {
      toast.success("Treatment updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    if (!f.treatment_date) return toast.error("Treatment date is required");
    if (!f.treatment_type.trim()) return toast.error("Treatment type is required");
    const data = {
      ...f,
      treatment_date: f.treatment_date || null,
      cost: f.cost === "" ? null : Number(f.cost),
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Treatment" : "Log Pest Treatment"}>
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
            <label className={labelCls}>Treatment Date *</label>
            <input
              type="date"
              value={f.treatment_date}
              onChange={(e) => setF((p) => ({ ...p, treatment_date: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Treatment Type *</label>
            <input
              value={f.treatment_type}
              onChange={(e) => setF((p) => ({ ...p, treatment_type: e.target.value }))}
              className={inputCls}
              required
              placeholder="e.g. baiting, spraying"
            />
          </div>
          <div>
            <label className={labelCls}>Pest Target</label>
            <input
              value={f.pest_target}
              onChange={(e) => setF((p) => ({ ...p, pest_target: e.target.value }))}
              className={inputCls}
              placeholder="e.g. rodents"
            />
          </div>
          <div>
            <label className={labelCls}>Chemical Name</label>
            <input
              value={f.chemical_name}
              onChange={(e) => setF((p) => ({ ...p, chemical_name: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Safety Re-entry (hours)</label>
            <input
              type="number"
              min={0}
              value={f.safety_re_entry_hours}
              onChange={(e) =>
                setF((p) => ({ ...p, safety_re_entry_hours: Number(e.target.value) }))
              }
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Cost ($)</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={f.cost}
              onChange={(e) => setF((p) => ({ ...p, cost: e.target.value }))}
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

// ─── Green Initiative Form Modal ─────────────────────────────────────────────

function GreenFormModal({
  open,
  onClose,
  initiative,
  buildings,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  initiative?: GreenInitiative | null;
  buildings: Building[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: initiative?.building ?? "",
    title: initiative?.title ?? "",
    description: initiative?.description ?? "",
    initiative_type: initiative?.initiative_type ?? "other",
    status: initiative?.status ?? "proposed",
    estimated_cost: initiative?.estimated_cost?.toString() ?? "",
    estimated_savings: initiative?.estimated_savings?.toString() ?? "",
    carbon_reduction_kg: initiative?.carbon_reduction_kg?.toString() ?? "",
    start_date: initiative?.start_date ?? "",
    target_end_date: initiative?.target_end_date ?? "",
  });
  const isEdit = !!initiative;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/green-initiative/", data),
    onSuccess: () => {
      toast.success("Initiative created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/green-initiative/${initiative!.id}/`, data),
    onSuccess: () => {
      toast.success("Initiative updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.title.trim()) return toast.error("Title is required");
    const data = {
      ...f,
      building: f.building || null,
      estimated_cost: f.estimated_cost === "" ? null : Number(f.estimated_cost),
      estimated_savings: f.estimated_savings === "" ? null : Number(f.estimated_savings),
      carbon_reduction_kg: f.carbon_reduction_kg === "" ? null : Number(f.carbon_reduction_kg),
      start_date: f.start_date || null,
      target_end_date: f.target_end_date || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Initiative" : "Add Green Initiative"}
    >
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Title *</label>
            <input
              value={f.title}
              onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
              className={inputCls}
              required
              placeholder="e.g. Rooftop solar panels"
            />
          </div>
          <div>
            <label className={labelCls}>Building</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value }))}
              className={inputCls}
            >
              <option value="">None (campus-wide)</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SelectField
            label="Initiative Type"
            value={f.initiative_type}
            options={INITIATIVE_TYPES}
            onChange={(v) => setF((p) => ({ ...p, initiative_type: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={INITIATIVE_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Est. Cost ($)</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={f.estimated_cost}
              onChange={(e) => setF((p) => ({ ...p, estimated_cost: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Est. Savings ($)</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={f.estimated_savings}
              onChange={(e) => setF((p) => ({ ...p, estimated_savings: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>CO₂ Reduction (kg)</label>
            <input
              type="number"
              min={0}
              value={f.carbon_reduction_kg}
              onChange={(e) => setF((p) => ({ ...p, carbon_reduction_kg: e.target.value }))}
              className={inputCls}
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
            <label className={labelCls}>Target End Date</label>
            <input
              type="date"
              value={f.target_end_date}
              onChange={(e) => setF((p) => ({ ...p, target_end_date: e.target.value }))}
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

// ─── Water Usage Form Modal ──────────────────────────────────────────────────

function WaterFormModal({
  open,
  onClose,
  record,
  buildings,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  record?: WaterUsage | null;
  buildings: Building[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: record?.building ?? "",
    record_date: record?.record_date ?? "",
    usage_gallons: record?.usage_gallons?.toString() ?? "",
    cost: record?.cost?.toString() ?? "",
    leak_detected: record?.leak_detected ?? false,
    notes: record?.notes ?? "",
  });
  const isEdit = !!record;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/water-usage-record/", data),
    onSuccess: () => {
      toast.success("Water usage saved");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/water-usage-record/${record!.id}/`, data),
    onSuccess: () => {
      toast.success("Water usage updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    if (f.usage_gallons === "") return toast.error("Usage is required");
    const data = {
      ...f,
      record_date: f.record_date || null,
      usage_gallons: Number(f.usage_gallons),
      cost: f.cost === "" ? null : Number(f.cost),
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Record" : "Add Water Usage"}>
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
            <label className={labelCls}>Record Date *</label>
            <input
              type="date"
              value={f.record_date}
              onChange={(e) => setF((p) => ({ ...p, record_date: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Usage (gallons) *</label>
            <input
              type="number"
              min={0}
              value={f.usage_gallons}
              onChange={(e) => setF((p) => ({ ...p, usage_gallons: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Cost ($)</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={f.cost}
              onChange={(e) => setF((p) => ({ ...p, cost: e.target.value }))}
              className={inputCls}
            />
          </div>
          <label className="flex items-end gap-2 pb-2 text-sm text-slate-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={f.leak_detected}
              onChange={(e) => setF((p) => ({ ...p, leak_detected: e.target.checked }))}
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
            />
            Leak detected
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

// ─── Vendor Performance Form Modal ───────────────────────────────────────────

function VendorPerfFormModal({
  open,
  onClose,
  rating,
  vendors,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  rating?: VendorRating | null;
  vendors: VendorContract[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    vendor_contract: rating?.vendor_contract ?? "",
    service_type: rating?.service_type ?? "cleaning",
    evaluation_date: rating?.evaluation_date ?? "",
    quality_rating: rating?.quality_rating ?? 5,
    timeliness_rating: rating?.timeliness_rating ?? 5,
    communication_rating: rating?.communication_rating ?? 5,
    value_rating: rating?.value_rating ?? 5,
    comments: rating?.comments ?? "",
    would_rehire: rating?.would_rehire === null ? "" : String(rating?.would_rehire ?? ""),
  });
  const isEdit = !!rating;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/vendor-performance/", data),
    onSuccess: () => {
      toast.success("Vendor rating saved");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/vendor-performance/${rating!.id}/`, data),
    onSuccess: () => {
      toast.success("Vendor rating updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.vendor_contract) return toast.error("Select a vendor contract");
    const data = {
      ...f,
      evaluation_date: f.evaluation_date || null,
      would_rehire: f.would_rehire === "" ? null : f.would_rehire === "true",
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const ratingFields: { key: keyof typeof f; label: string }[] = [
    { key: "quality_rating", label: "Quality" },
    { key: "timeliness_rating", label: "Timeliness" },
    { key: "communication_rating", label: "Communication" },
    { key: "value_rating", label: "Value" },
  ];
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Rating" : "Rate Vendor"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Vendor Contract *</label>
            <select
              value={f.vendor_contract}
              onChange={(e) => setF((p) => ({ ...p, vendor_contract: e.target.value }))}
              className={inputCls}
              required
            >
              <option value="">Select vendor...</option>
              {vendors.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.vendor_name || v.id}
                </option>
              ))}
            </select>
          </div>
          <SelectField
            label="Service Type"
            value={f.service_type}
            options={SERVICE_TYPES}
            onChange={(v) => setF((p) => ({ ...p, service_type: v }))}
          />
        </div>
        <div className="grid grid-cols-4 gap-4">
          {ratingFields.map((rf) => (
            <div key={rf.key}>
              <label className={labelCls}>{rf.label} (1-5)</label>
              <input
                type="number"
                min={1}
                max={5}
                value={f[rf.key]}
                onChange={(e) => setF((p) => ({ ...p, [rf.key]: Number(e.target.value) }))}
                className={inputCls}
                required
              />
            </div>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Evaluation Date</label>
            <input
              type="date"
              value={f.evaluation_date}
              onChange={(e) => setF((p) => ({ ...p, evaluation_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Would Rehire?</label>
            <select
              value={f.would_rehire}
              onChange={(e) => setF((p) => ({ ...p, would_rehire: e.target.value }))}
              className={inputCls}
            >
              <option value="">Not sure</option>
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          </div>
        </div>
        <div>
          <label className={labelCls}>Comments</label>
          <textarea
            value={f.comments}
            onChange={(e) => setF((p) => ({ ...p, comments: e.target.value }))}
            rows={3}
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

// ─── Building Inspection Form Modal ──────────────────────────────────────────

function BuildingInspFormModal({
  open,
  onClose,
  inspection,
  buildings,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  inspection?: BuildingInspection | null;
  buildings: Building[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: inspection?.building ?? "",
    inspection_type: inspection?.inspection_type ?? "general",
    inspection_date: inspection?.inspection_date ?? "",
    inspector_name: inspection?.inspector_name ?? "",
    result: inspection?.result ?? "pending",
    findings: inspection?.findings ?? "",
    violations: inspection?.violations ?? "",
    follow_up_required: inspection?.follow_up_required ?? false,
    follow_up_date: inspection?.follow_up_date ?? "",
    corrective_actions: inspection?.corrective_actions ?? "",
  });
  const isEdit = !!inspection;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/building-inspection/", data),
    onSuccess: () => {
      toast.success("Building inspection created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/building-inspection/${inspection!.id}/`, data),
    onSuccess: () => {
      toast.success("Building inspection updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    if (!f.inspection_date) return toast.error("Inspection date is required");
    const data = {
      ...f,
      inspection_date: f.inspection_date || null,
      follow_up_date: f.follow_up_date || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Inspection" : "Add Building Inspection"}
    >
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
          <SelectField
            label="Inspection Type"
            value={f.inspection_type}
            options={BUILDING_INSPECTION_TYPES}
            onChange={(v) => setF((p) => ({ ...p, inspection_type: v }))}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Inspection Date *</label>
            <input
              type="date"
              value={f.inspection_date}
              onChange={(e) => setF((p) => ({ ...p, inspection_date: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Inspector</label>
            <input
              value={f.inspector_name}
              onChange={(e) => setF((p) => ({ ...p, inspector_name: e.target.value }))}
              className={inputCls}
            />
          </div>
          <SelectField
            label="Result"
            value={f.result}
            options={BUILDING_INSPECTION_RESULTS}
            onChange={(v) => setF((p) => ({ ...p, result: v }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
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
            <label className={labelCls}>Violations</label>
            <textarea
              value={f.violations}
              onChange={(e) => setF((p) => ({ ...p, violations: e.target.value }))}
              rows={2}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Follow-up Date</label>
            <input
              type="date"
              value={f.follow_up_date}
              onChange={(e) => setF((p) => ({ ...p, follow_up_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Corrective Actions</label>
            <textarea
              value={f.corrective_actions}
              onChange={(e) => setF((p) => ({ ...p, corrective_actions: e.target.value }))}
              rows={2}
              className={inputCls}
            />
          </div>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.follow_up_required}
            onChange={(e) => setF((p) => ({ ...p, follow_up_required: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
          />
          Follow-up required
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

// ─── Infra Alert Form Modal ──────────────────────────────────────────────────

function InfraAlertFormModal({
  open,
  onClose,
  alert,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  alert?: InfraAlert | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: alert?.building ?? "",
    room: alert?.room ?? "",
    alert_type: alert?.alert_type ?? "other",
    severity: alert?.severity ?? "medium",
    status: alert?.status ?? "active",
    title: alert?.title ?? "",
    description: alert?.description ?? "",
  });
  const isEdit = !!alert;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/infrastructure-alert/", data),
    onSuccess: () => {
      toast.success("Alert raised");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/infrastructure-alert/${alert!.id}/`, data),
    onSuccess: () => {
      toast.success("Alert updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.title.trim()) return toast.error("Title is required");
    const data = {
      ...f,
      building: f.building || null,
      room: f.room || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Alert" : "Raise Infra Alert"}>
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>Title *</label>
          <input
            value={f.title}
            onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
            className={inputCls}
            required
            placeholder="e.g. Water leak in science block"
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
          <SelectField
            label="Alert Type"
            value={f.alert_type}
            options={INFRA_ALERT_TYPES}
            onChange={(v) => setF((p) => ({ ...p, alert_type: v }))}
          />
          <SelectField
            label="Severity"
            value={f.severity}
            options={INFRA_ALERT_SEVERITIES}
            onChange={(v) => setF((p) => ({ ...p, severity: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={INFRA_ALERT_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
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

// ─── Floor Plan Form Modal ───────────────────────────────────────────────────

function FloorPlanFormModal({
  open,
  onClose,
  plan,
  buildings,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  plan?: FloorPlan | null;
  buildings: Building[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: plan?.building ?? "",
    floor_number: plan?.floor_number ?? 1,
    floor_name: plan?.floor_name ?? "",
    total_rooms: plan?.total_rooms ?? 0,
    total_area_sqft: plan?.total_area_sqft?.toString() ?? "",
    description: plan?.description ?? "",
    is_current: plan?.is_current ?? false,
  });
  const [file, setFile] = useState<File | null>(null);
  const isEdit = !!plan;
  const createMut = useMutation({
    mutationFn: (data: FormData) => api.upload("/infrastructure/floor-plan/", data),
    onSuccess: () => {
      toast.success("Floor plan created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f | FormData) =>
      api.patch(`/infrastructure/floor-plan/${plan!.id}/`, data),
    onSuccess: () => {
      toast.success("Floor plan updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.building) return toast.error("Select a building");
    if (!file && !isEdit) return toast.error("Plan file is required");
    const body: Record<string, unknown> = {
      building: f.building,
      floor_number: Number(f.floor_number),
      floor_name: f.floor_name,
      total_rooms: Number(f.total_rooms),
      total_area_sqft: f.total_area_sqft === "" ? null : Number(f.total_area_sqft),
      description: f.description,
      is_current: f.is_current,
    };
    if (file) {
      const fd = new FormData();
      Object.entries(body).forEach(([k, v]) => {
        if (v !== null) fd.append(k, String(v));
      });
      fd.append("plan_file", file);
      if (isEdit) updateMut.mutate(fd);
      else createMut.mutate(fd);
    } else {
      if (isEdit) updateMut.mutate(body as any);
    }
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Floor Plan" : "Add Floor Plan"}>
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
            <label className={labelCls}>Floor Name</label>
            <input
              value={f.floor_name}
              onChange={(e) => setF((p) => ({ ...p, floor_name: e.target.value }))}
              className={inputCls}
              placeholder="e.g. Ground floor"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Floor Number</label>
            <input
              type="number"
              min={0}
              value={f.floor_number}
              onChange={(e) => setF((p) => ({ ...p, floor_number: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Total Rooms</label>
            <input
              type="number"
              min={0}
              value={f.total_rooms}
              onChange={(e) => setF((p) => ({ ...p, total_rooms: Number(e.target.value) }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Total Area (sqft)</label>
            <input
              type="number"
              min={0}
              value={f.total_area_sqft}
              onChange={(e) => setF((p) => ({ ...p, total_area_sqft: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div>
          <label className={labelCls}>
            Plan File {isEdit ? "(leave empty to keep current)" : "*"}
          </label>
          <input
            type="file"
            accept="image/*,.pdf"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className={inputCls}
            required={!isEdit}
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
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input
            type="checkbox"
            checked={f.is_current}
            onChange={(e) => setF((p) => ({ ...p, is_current: e.target.checked }))}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
          />
          Current plan
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

// ─── Room Equipment Form Modal ───────────────────────────────────────────────

function EquipmentFormModal({
  open,
  onClose,
  equipment,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  equipment?: RoomEquipment | null;
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    room: equipment?.room ?? "",
    equipment_type: equipment?.equipment_type ?? "other",
    name: equipment?.name ?? "",
    asset_tag: equipment?.asset_tag ?? "",
    brand: equipment?.brand ?? "",
    status: equipment?.status ?? "working",
    purchase_date: equipment?.purchase_date ?? "",
    warranty_expiry: equipment?.warranty_expiry ?? "",
    last_maintenance: equipment?.last_maintenance ?? "",
    notes: equipment?.notes ?? "",
  });
  const isEdit = !!equipment;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/room-equipment/", data),
    onSuccess: () => {
      toast.success("Equipment added");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/room-equipment/${equipment!.id}/`, data),
    onSuccess: () => {
      toast.success("Equipment updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.room) return toast.error("Select a room");
    if (!f.name.trim()) return toast.error("Name is required");
    const data = {
      ...f,
      purchase_date: f.purchase_date || null,
      warranty_expiry: f.warranty_expiry || null,
      last_maintenance: f.last_maintenance || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Equipment" : "Add Room Equipment"}>
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
            label="Equipment Type"
            value={f.equipment_type}
            options={EQUIPMENT_TYPES}
            onChange={(v) => setF((p) => ({ ...p, equipment_type: v }))}
          />
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={labelCls}>Name *</label>
            <input
              value={f.name}
              onChange={(e) => setF((p) => ({ ...p, name: e.target.value }))}
              className={inputCls}
              required
              placeholder="e.g. Epson projector"
            />
          </div>
          <div>
            <label className={labelCls}>Asset Tag</label>
            <input
              value={f.asset_tag}
              onChange={(e) => setF((p) => ({ ...p, asset_tag: e.target.value }))}
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>Brand</label>
            <input
              value={f.brand}
              onChange={(e) => setF((p) => ({ ...p, brand: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-4 gap-4">
          <SelectField
            label="Status"
            value={f.status}
            options={EQUIPMENT_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
          />
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
            <label className={labelCls}>Warranty Expiry</label>
            <input
              type="date"
              value={f.warranty_expiry}
              onChange={(e) => setF((p) => ({ ...p, warranty_expiry: e.target.value }))}
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

// ─── Maintenance Cost Form Modal ─────────────────────────────────────────────

function CostFormModal({
  open,
  onClose,
  record,
  buildings,
  workOrders,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  record?: CostRecord | null;
  buildings: Building[];
  workOrders: WorkOrder[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: record?.building ?? "",
    work_order: record?.work_order ?? "",
    cost_category: record?.cost_category ?? "general",
    amount: record?.amount?.toString() ?? "",
    vendor: record?.vendor ?? "",
    cost_date: record?.cost_date ?? "",
    is_approved: record?.is_approved ?? false,
    notes: record?.notes ?? "",
  });
  const isEdit = !!record;
  const createMut = useMutation({
    mutationFn: (data: typeof f) => api.post("/infrastructure/maintenance-cost-tracking/", data),
    onSuccess: () => {
      toast.success("Cost record saved");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/maintenance-cost-tracking/${record!.id}/`, data),
    onSuccess: () => {
      toast.success("Cost record updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (f.amount === "") return toast.error("Amount is required");
    const data = {
      ...f,
      building: f.building || null,
      work_order: f.work_order || null,
      amount: Number(f.amount),
      cost_date: f.cost_date || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Cost" : "Add Maintenance Cost"}>
      <form onSubmit={submit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Building</label>
            <select
              value={f.building}
              onChange={(e) => setF((p) => ({ ...p, building: e.target.value }))}
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
            <label className={labelCls}>Work Order</label>
            <select
              value={f.work_order}
              onChange={(e) => setF((p) => ({ ...p, work_order: e.target.value }))}
              className={inputCls}
            >
              <option value="">None</option>
              {workOrders.map((wo) => (
                <option key={wo.id} value={wo.id}>
                  {wo.title}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <SelectField
            label="Cost Category"
            value={f.cost_category}
            options={COST_CATEGORIES}
            onChange={(v) => setF((p) => ({ ...p, cost_category: v }))}
          />
          <div>
            <label className={labelCls}>Amount ($) *</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={f.amount}
              onChange={(e) => setF((p) => ({ ...p, amount: e.target.value }))}
              className={inputCls}
              required
            />
          </div>
          <div>
            <label className={labelCls}>Vendor</label>
            <input
              value={f.vendor}
              onChange={(e) => setF((p) => ({ ...p, vendor: e.target.value }))}
              className={inputCls}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>Cost Date</label>
            <input
              type="date"
              value={f.cost_date}
              onChange={(e) => setF((p) => ({ ...p, cost_date: e.target.value }))}
              className={inputCls}
            />
          </div>
          <label className="flex items-end gap-2 pb-2 text-sm text-slate-700 dark:text-slate-300">
            <input
              type="checkbox"
              checked={f.is_approved}
              onChange={(e) => setF((p) => ({ ...p, is_approved: e.target.checked }))}
              className="h-4 w-4 rounded border-slate-300 text-indigo-600 dark:border-slate-600"
            />
            Approved
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

// ─── Maintenance Request Form Modal ──────────────────────────────────────────

function RequestFormModal({
  open,
  onClose,
  request,
  buildings,
  rooms,
  onSaved,
}: {
  open: boolean;
  onClose: () => void;
  request?: MaintRequest | null;
  buildings: Building[];
  rooms: Room[];
  onSaved: () => void;
}) {
  const [f, setF] = useState({
    building: request?.building ?? "",
    room: request?.room ?? "",
    title: request?.title ?? "",
    description: request?.description ?? "",
    priority: request?.priority ?? "medium",
    status: request?.status ?? "open",
  });
  const isEdit = !!request;
  const createMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.post("/infrastructure/infrastructure-maintenance-request/", data),
    onSuccess: () => {
      toast.success("Maintenance request created");
      onSaved();
    },
  });
  const updateMut = useMutation({
    mutationFn: (data: typeof f) =>
      api.patch(`/infrastructure/infrastructure-maintenance-request/${request!.id}/`, data),
    onSuccess: () => {
      toast.success("Maintenance request updated");
      onSaved();
    },
  });
  const saving = createMut.isPending || updateMut.isPending;
  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!f.title.trim()) return toast.error("Title is required");
    const data = {
      ...f,
      building: f.building || null,
      room: f.room || null,
    } as any;
    if (isEdit) updateMut.mutate(data);
    else createMut.mutate(data);
  };
  const buildingRooms = rooms.filter((r) => r.building === f.building);
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={isEdit ? "Edit Request" : "Add Maintenance Request"}
    >
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className={labelCls}>Title *</label>
          <input
            value={f.title}
            onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
            className={inputCls}
            required
            placeholder="e.g. AC not cooling in lab 2"
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
          <SelectField
            label="Priority"
            value={f.priority}
            options={REQUEST_PRIORITIES}
            onChange={(v) => setF((p) => ({ ...p, priority: v }))}
          />
          <SelectField
            label="Status"
            value={f.status}
            options={REQUEST_STATUSES}
            onChange={(v) => setF((p) => ({ ...p, status: v }))}
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
