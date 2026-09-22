/**
 * Transportation Center — full-surface admin page for the transportation module.
 *
 * 37 entity tabs (config-driven via EntitySection). Vehicles, drivers, routes, stops, tracking, GPS, geofences, fees, incidents, maintenance and analytics.
 */
import React, { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, TruckIcon } from "@heroicons/react/24/outline";

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  // ===== transportation =====
  attendance: {
    key: "attendance",
    icon: TruckIcon,
    label: "Daily Transport Attendance",
    endpoint: "attendance",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "route", label: "Route" },
      { key: "vehicle", label: "Vehicle" },
      { key: "date", label: "Date", type: "date" },
      {
        key: "attendance_type",
        label: "Attendance Type",
        type: "select",
        options: [
          ["pickup", "Pickup"],
          ["dropoff", "Dropoff"],
          ["both", "Both"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["present", "Present"],
          ["absent", "Absent"],
          ["late", "Late"],
          ["excused", "Excused"],
        ],
      },
      { key: "pickup_time", label: "Pickup Time" },
      { key: "dropoff_time", label: "Dropoff Time" },
      { key: "pickup_stop", label: "Pickup Stop" },
    ],
  },
  "bus-tracking": {
    key: "bus-tracking",
    icon: TruckIcon,
    label: "Bus Tracking",
    endpoint: "bus-tracking",
    premiumFeature: "live_transport_tracking",
    titleField: "vehicle",
    subtitleField: "status",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      { key: "route", label: "Route" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["not_started", "Not Started"],
          ["on_route", "On Route"],
          ["at_stop", "At Stop"],
          ["completed", "Completed"],
        ],
      },
      { key: "scheduled_start", label: "Scheduled Start" },
      { key: "scheduled_end", label: "Scheduled End" },
      { key: "actual_start", label: "Actual Start" },
      { key: "actual_end", label: "Actual End" },
      { key: "current_stop", label: "Current Stop" },
      { key: "next_stop", label: "Next Stop" },
      { key: "estimated_arrival", label: "Estimated Arrival" },
    ],
  },
  documents: {
    key: "documents",
    icon: TruckIcon,
    label: "Vehicle Document",
    endpoint: "documents",
    titleField: "vehicle",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      {
        key: "document_type",
        label: "Document Type",
        type: "select",
        options: [
          ["registration", "Registration"],
          ["insurance", "Insurance"],
          ["permit", "Permit"],
          ["fitness", "Fitness"],
          ["pollution", "Pollution"],
          ["tax", "Tax"],
          ["other", "Other"],
        ],
      },
      { key: "document_name", label: "Document Name" },
      { key: "document_number", label: "Document Number" },
      { key: "issue_date", label: "Issue Date", type: "date" },
      { key: "expiry_date", label: "Expiry Date", type: "date" },
      { key: "issued_by", label: "Issued By" },
      { key: "document_url", label: "Document Url" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "is_valid", label: "Is Valid" },
    ],
  },
  "driver-license": {
    key: "driver-license",
    icon: TruckIcon,
    label: "Driver License",
    endpoint: "driver-license",
    titleField: "driver",
    fields: [
      { key: "driver", label: "Driver" },
      { key: "license_number", label: "License Number" },
      { key: "license_type", label: "License Type" },
      { key: "issue_date", label: "Issue Date", type: "date" },
      { key: "expiry_date", label: "Expiry Date", type: "date" },
      { key: "issuing_authority", label: "Issuing Authority" },
      { key: "endorsements", label: "Endorsements" },
      { key: "restrictions", label: "Restrictions" },
      { key: "license_image", label: "License Image" },
      { key: "is_valid", label: "Is Valid" },
      { key: "suspension_reason", label: "Suspension Reason" },
      { key: "suspension_date", label: "Suspension Date", type: "date" },
    ],
  },
  "driver-performance": {
    key: "driver-performance",
    icon: TruckIcon,
    label: "Driver Performance",
    endpoint: "driver-performance",
    titleField: "driver",
    fields: [
      { key: "driver", label: "Driver" },
      { key: "evaluation_date", label: "Evaluation Date", type: "date" },
      { key: "evaluator", label: "Evaluator" },
      { key: "safety_rating", label: "Safety Rating" },
      { key: "punctuality_rating", label: "Punctuality Rating" },
      { key: "vehicle_care_rating", label: "Vehicle Care Rating" },
      {
        key: "student_interaction_rating",
        label: "Student Interaction Rating",
      },
      { key: "overall_rating", label: "Overall Rating" },
      { key: "total_trips", label: "Total Trips" },
      { key: "accidents", label: "Accidents" },
      { key: "complaints", label: "Complaints" },
      { key: "compliments", label: "Compliments" },
    ],
  },
  drivers: {
    key: "drivers",
    icon: TruckIcon,
    label: "Driver",
    endpoint: "drivers",
    titleField: "employee",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "full_name", label: "Full Name" },
      { key: "phone_number", label: "Phone Number" },
      { key: "email", label: "Email" },
      { key: "license_number", label: "License Number" },
      { key: "license_expiry", label: "License Expiry" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["on_leave", "On Leave"],
          ["inactive", "Inactive"],
        ],
      },
      { key: "emergency_contact_name", label: "Emergency Contact Name" },
      { key: "emergency_contact_phone", label: "Emergency Contact Phone" },
    ],
  },
  fees: {
    key: "fees",
    icon: TruckIcon,
    label: "Transport Fee",
    endpoint: "fees",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "route", label: "Route" },
      {
        key: "fee_type",
        label: "Fee Type",
        type: "select",
        options: [
          ["monthly", "Monthly"],
          ["term", "Term"],
          ["annual", "Annual"],
          ["one_time", "One Time"],
          ["other", "Other"],
        ],
      },
      { key: "amount", label: "Amount", type: "number" },
      { key: "paid_amount", label: "Paid Amount", type: "number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["paid", "Paid"],
          ["overdue", "Overdue"],
          ["waived", "Waived"],
        ],
      },
      { key: "due_date", label: "Due Date", type: "date" },
      { key: "paid_date", label: "Paid Date", type: "date" },
      { key: "academic_year", label: "Academic Year" },
    ],
  },
  "fuel-logs": {
    key: "fuel-logs",
    icon: TruckIcon,
    label: "Fuel Log",
    endpoint: "fuel-logs",
    titleField: "vehicle",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      {
        key: "fuel_type",
        label: "Fuel Type",
        type: "select",
        options: [
          ["diesel", "Diesel"],
          ["petrol", "Petrol"],
          ["cng", "Cng"],
          ["electric", "Electric"],
          ["other", "Other"],
        ],
      },
      { key: "fill_date", label: "Fill Date", type: "date" },
      { key: "odometer_reading", label: "Odometer Reading" },
      { key: "liters", label: "Liters" },
      { key: "cost_per_liter", label: "Cost Per Liter" },
      { key: "total_cost", label: "Total Cost" },
      { key: "station_name", label: "Station Name" },
      { key: "invoice_number", label: "Invoice Number" },
      { key: "filled_by", label: "Filled By" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "geofence-alert": {
    key: "geofence-alert",
    icon: TruckIcon,
    label: "Geofence Alert",
    endpoint: "geofence-alert",
    premiumFeature: "live_transport_tracking",
    titleField: "vehicle",
    subtitleField: "status",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      { key: "zone", label: "Zone" },
      { key: "gps_log", label: "Gps Log" },
      {
        key: "alert_type",
        label: "Alert Type",
        type: "select",
        options: [
          ["entry", "Entry"],
          ["exit", "Exit"],
          ["speed", "Speed"],
          ["deviation", "Deviation"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["acknowledged", "Acknowledged"],
          ["resolved", "Resolved"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "speed_recorded", label: "Speed Recorded" },
      { key: "speed_limit", label: "Speed Limit" },
    ],
  },
  "geofence-zone": {
    key: "geofence-zone",
    icon: TruckIcon,
    label: "Geofence Zone",
    endpoint: "geofence-zone",
    premiumFeature: "live_transport_tracking",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "zone_type",
        label: "Zone Type",
        type: "select",
        options: [
          ["school", "School"],
          ["stop", "Stop"],
          ["restricted", "Restricted"],
          ["danger", "Danger"],
        ],
      },
      { key: "center_latitude", label: "Center Latitude" },
      { key: "center_longitude", label: "Center Longitude" },
      { key: "radius_meters", label: "Radius Meters" },
      { key: "polygon_coordinates", label: "Polygon Coordinates" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "alert_on_entry", label: "Alert On Entry" },
      { key: "alert_on_exit", label: "Alert On Exit" },
    ],
  },
  incidents: {
    key: "incidents",
    icon: TruckIcon,
    label: "Transport Incident Report",
    endpoint: "incidents",
    titleField: "incident_type",
    subtitleField: "status",
    fields: [
      {
        key: "incident_type",
        label: "Incident Type",
        type: "select",
        options: [
          ["accident", "Accident"],
          ["breakdown", "Breakdown"],
          ["medical", "Medical"],
          ["behavioral", "Behavioral"],
          ["route_delay", "Route Delay"],
          ["vehicle_damage", "Vehicle Damage"],
          ["weather", "Weather"],
          ["other", "Other"],
        ],
      },
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: [
          ["low", "Low"],
          ["medium", "Medium"],
          ["high", "High"],
          ["critical", "Critical"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["reported", "Reported"],
          ["investigating", "Investigating"],
          ["resolved", "Resolved"],
          ["closed", "Closed"],
        ],
      },
      { key: "vehicle", label: "Vehicle" },
      { key: "route", label: "Route" },
      { key: "driver", label: "Driver" },
      { key: "incident_date", label: "Incident Date", type: "date" },
      { key: "incident_time", label: "Incident Time" },
      { key: "location", label: "Location" },
    ],
  },
  inspections: {
    key: "inspections",
    icon: TruckIcon,
    label: "Vehicle Inspection",
    endpoint: "inspections",
    titleField: "vehicle",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      {
        key: "inspection_type",
        label: "Inspection Type",
        type: "select",
        options: [
          ["pre_trip", "Pre Trip"],
          ["post_trip", "Post Trip"],
          ["weekly", "Weekly"],
          ["monthly", "Monthly"],
          ["annual", "Annual"],
        ],
      },
      { key: "inspection_date", label: "Inspection Date", type: "date" },
      { key: "inspector_name", label: "Inspector Name" },
      {
        key: "result",
        label: "Result",
        type: "select",
        options: [
          ["pass", "Pass"],
          ["fail", "Fail"],
          ["needs_repair", "Needs Repair"],
        ],
      },
      { key: "odometer_reading", label: "Odometer Reading" },
      { key: "exterior_check", label: "Exterior Check" },
      { key: "interior_check", label: "Interior Check" },
      { key: "tires_check", label: "Tires Check" },
      { key: "lights_check", label: "Lights Check" },
      { key: "brakes_check", label: "Brakes Check" },
      { key: "signals_check", label: "Signals Check" },
      { key: "emergency_equipment", label: "Emergency Equipment" },
    ],
  },
  insurance: {
    key: "insurance",
    icon: TruckIcon,
    label: "Vehicle Insurance",
    endpoint: "insurance",
    titleField: "vehicle",
    subtitleField: "status",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      {
        key: "insurance_type",
        label: "Insurance Type",
        type: "select",
        options: [
          ["comprehensive", "Comprehensive"],
          ["third_party", "Third Party"],
          ["liability", "Liability"],
          ["other", "Other"],
        ],
      },
      { key: "provider", label: "Provider" },
      { key: "policy_number", label: "Policy Number" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "premium_amount", label: "Premium Amount" },
      { key: "coverage_amount", label: "Coverage Amount" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["expired", "Expired"],
          ["pending_renewal", "Pending Renewal"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "document_url", label: "Document Url" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  maintenance: {
    key: "maintenance",
    icon: TruckIcon,
    label: "Vehicle Maintenance",
    endpoint: "maintenance",
    titleField: "vehicle",
    subtitleField: "status",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      {
        key: "maintenance_type",
        label: "Maintenance Type",
        type: "select",
        options: [
          ["routine", "Routine"],
          ["repair", "Repair"],
          ["inspection", "Inspection"],
          ["tire", "Tire"],
          ["engine", "Engine"],
          ["body", "Body"],
          ["other", "Other"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["in_progress", "In Progress"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "scheduled_date", label: "Scheduled Date", type: "date" },
      { key: "completed_date", label: "Completed Date", type: "date" },
      { key: "odometer_reading", label: "Odometer Reading" },
      { key: "cost", label: "Cost" },
      { key: "vendor_name", label: "Vendor Name" },
      { key: "invoice_number", label: "Invoice Number" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "performed_by", label: "Performed By" },
    ],
  },
  notifications: {
    key: "notifications",
    icon: TruckIcon,
    label: "Transport Notification",
    endpoint: "notifications",
    titleField: "title",
    subtitleField: "status",
    fields: [
      {
        key: "notification_type",
        label: "Notification Type",
        type: "select",
        options: [
          ["delay", "Delay"],
          ["cancellation", "Cancellation"],
          ["route_change", "Route Change"],
          ["pickup_complete", "Pickup Complete"],
          ["dropoff_complete", "Dropoff Complete"],
          ["incident", "Incident"],
          ["fee_reminder", "Fee Reminder"],
          ["general", "General"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "message", label: "Message", type: "textarea" },
      { key: "route", label: "Route" },
      { key: "vehicle", label: "Vehicle" },
      { key: "recipients", label: "Recipients", type: "textarea" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["sent", "Sent"],
          ["delivered", "Delivered"],
          ["failed", "Failed"],
        ],
      },
      { key: "sent_at", label: "Sent At", type: "date" },
      { key: "sent_by", label: "Sent By" },
    ],
  },
  "parent-transport-access": {
    key: "parent-transport-access",
    icon: TruckIcon,
    label: "Parent Transport Access",
    endpoint: "parent-transport-access",
    titleField: "parent",
    fields: [
      { key: "parent", label: "Parent" },
      { key: "student", label: "Student" },
      { key: "tracking_enabled", label: "Tracking Enabled" },
      { key: "notifications_enabled", label: "Notifications Enabled" },
      { key: "email_alerts", label: "Email Alerts" },
      { key: "sms_alerts", label: "Sms Alerts" },
      { key: "alert_pickup", label: "Alert Pickup" },
      { key: "alert_dropoff", label: "Alert Dropoff" },
      { key: "alert_delay", label: "Alert Delay" },
      { key: "alert_incident", label: "Alert Incident" },
    ],
  },
  reports: {
    key: "reports",
    icon: TruckIcon,
    label: "Transport Report",
    endpoint: "reports",
    titleField: "title",
    subtitleField: "report_type",
    fields: [
      { key: "title", label: "Title" },
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: [
          ["route_summary", "Route Summary"],
          ["vehicle_status", "Vehicle Status"],
          ["fuel_consumption", "Fuel Consumption"],
          ["incident_summary", "Incident Summary"],
          ["fee_collection", "Fee Collection"],
          ["attendance_summary", "Attendance Summary"],
          ["maintenance_cost", "Maintenance Cost"],
          ["general", "General"],
        ],
      },
      { key: "date_from", label: "Date From", type: "date" },
      { key: "date_to", label: "Date To", type: "date" },
      { key: "report_data", label: "Report Data", type: "textarea" },
      { key: "summary", label: "Summary", type: "textarea" },
      { key: "generated_by", label: "Generated By" },
      { key: "file_url", label: "File Url" },
    ],
  },
  "route-optimization": {
    key: "route-optimization",
    icon: TruckIcon,
    label: "Route Optimization",
    endpoint: "route-optimization",
    titleField: "route",
    fields: [
      { key: "route", label: "Route" },
      { key: "optimization_date", label: "Optimization Date", type: "date" },
      { key: "original_distance_km", label: "Original Distance Km" },
      { key: "original_time_minutes", label: "Original Time Minutes" },
      { key: "original_fuel_cost", label: "Original Fuel Cost" },
      { key: "optimized_distance_km", label: "Optimized Distance Km" },
      { key: "optimized_time_minutes", label: "Optimized Time Minutes" },
      { key: "optimized_fuel_cost", label: "Optimized Fuel Cost" },
      { key: "distance_saved_km", label: "Distance Saved Km" },
      { key: "time_saved_minutes", label: "Time Saved Minutes" },
      { key: "fuel_saved", label: "Fuel Saved" },
    ],
  },
  "route-stops": {
    key: "route-stops",
    icon: TruckIcon,
    label: "Route Stop Detail",
    endpoint: "route-stops",
    titleField: "name",
    fields: [
      { key: "route", label: "Route" },
      { key: "name", label: "Name" },
      { key: "address", label: "Address" },
      { key: "landmark", label: "Landmark" },
      { key: "latitude", label: "Latitude" },
      { key: "longitude", label: "Longitude" },
      { key: "stop_order", label: "Stop Order" },
      { key: "stop_type", label: "Stop Type" },
      { key: "pickup_time", label: "Pickup Time" },
      { key: "dropoff_time", label: "Dropoff Time" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  routes: {
    key: "routes",
    icon: TruckIcon,
    label: "Route",
    endpoint: "routes",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "vehicle", label: "Vehicle" },
      { key: "driver", label: "Driver" },
      { key: "origin", label: "Origin" },
      { key: "destination", label: "Destination" },
      {
        key: "estimated_duration_minutes",
        label: "Estimated Duration Minutes",
      },
      { key: "operating_days", label: "Operating Days" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "stop-e-t-a": {
    key: "stop-e-t-a",
    icon: TruckIcon,
    label: "Stop E T A",
    endpoint: "stop-e-t-a",
    premiumFeature: "live_transport_tracking",
    titleField: "tracking",
    fields: [
      { key: "tracking", label: "Tracking" },
      { key: "stop", label: "Stop" },
      { key: "scheduled_time", label: "Scheduled Time" },
      { key: "estimated_time", label: "Estimated Time" },
      { key: "actual_time", label: "Actual Time" },
      { key: "students_expected", label: "Students Expected" },
      { key: "students_picked_up", label: "Students Picked Up" },
      { key: "students_dropped", label: "Students Dropped" },
      { key: "delay_minutes", label: "Delay Minutes" },
      { key: "delay_reason", label: "Delay Reason" },
    ],
  },
  "student-routes": {
    key: "student-routes",
    icon: TruckIcon,
    label: "Student Route",
    endpoint: "student-routes",
    titleField: "route",
    fields: [
      { key: "route", label: "Route" },
      { key: "student", label: "Student" },
      { key: "pickup_stop", label: "Pickup Stop" },
      { key: "dropoff_stop", label: "Dropoff Stop" },
      {
        key: "service_type",
        label: "Service Type",
        type: "select",
        options: [
          ["pickup", "Pickup"],
          ["dropoff", "Dropoff"],
          ["both", "Both"],
        ],
      },
      { key: "fee_amount", label: "Fee Amount" },
      { key: "effective_from", label: "Effective From" },
      { key: "effective_to", label: "Effective To" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "student-transport-profile": {
    key: "student-transport-profile",
    icon: TruckIcon,
    label: "Student Transport Profile",
    endpoint: "student-transport-profile",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "assigned_route", label: "Assigned Route" },
      { key: "assigned_stop", label: "Assigned Stop" },
      { key: "needs_morning", label: "Needs Morning" },
      { key: "needs_evening", label: "Needs Evening" },
      { key: "has_disability", label: "Has Disability" },
      { key: "disability_notes", label: "Disability Notes" },
      { key: "needs_wheelchair", label: "Needs Wheelchair" },
      { key: "needs_escort", label: "Needs Escort" },
    ],
  },
  "transport-alert": {
    key: "transport-alert",
    icon: TruckIcon,
    label: "Transport Alert",
    endpoint: "transport-alert",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      { key: "route", label: "Route" },
      {
        key: "alert_type",
        label: "Alert Type",
        type: "select",
        options: [
          ["delay", "Delay"],
          ["cancel", "Cancel"],
          ["breakdown", "Breakdown"],
          ["accident", "Accident"],
          ["weather", "Weather"],
          ["route_change", "Route Change"],
          ["maintenance", "Maintenance"],
        ],
      },
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: [
          ["low", "Low"],
          ["medium", "Medium"],
          ["high", "High"],
          ["critical", "Critical"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["acknowledged", "Acknowledged"],
          ["resolved", "Resolved"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "affected_students", label: "Affected Students" },
      { key: "affected_routes", label: "Affected Routes" },
      { key: "estimated_delay_minutes", label: "Estimated Delay Minutes" },
    ],
  },
  "transport-audit-log": {
    key: "transport-audit-log",
    icon: TruckIcon,
    label: "Transport Audit Log",
    endpoint: "transport-audit-log",
    titleField: "action_type",
    fields: [
      {
        key: "action_type",
        label: "Action Type",
        type: "select",
        options: [
          ["vehicle_add", "Vehicle Add"],
          ["vehicle_update", "Vehicle Update"],
          ["route_create", "Route Create"],
          ["route_modify", "Route Modify"],
          ["driver_assign", "Driver Assign"],
          ["maint_schedule", "Maint Schedule"],
          ["fee_collect", "Fee Collect"],
          ["incident", "Incident"],
          ["alert", "Alert"],
        ],
      },
      { key: "target_model", label: "Target Model" },
      { key: "target_id", label: "Target Id" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "old_values", label: "Old Values" },
      { key: "new_values", label: "New Values" },
      { key: "ip_address", label: "Ip Address" },
      { key: "timestamp", label: "Timestamp" },
    ],
  },
  "transport-budget": {
    key: "transport-budget",
    icon: TruckIcon,
    label: "Transport Budget",
    endpoint: "transport-budget",
    titleField: "academic_year",
    fields: [
      { key: "academic_year", label: "Academic Year" },
      { key: "fuel_budget", label: "Fuel Budget" },
      { key: "maintenance_budget", label: "Maintenance Budget" },
      { key: "insurance_budget", label: "Insurance Budget" },
      { key: "salary_budget", label: "Salary Budget" },
      { key: "new_vehicle_budget", label: "New Vehicle Budget" },
      { key: "miscellaneous_budget", label: "Miscellaneous Budget" },
      { key: "total_budget", label: "Total Budget" },
      { key: "fuel_spent", label: "Fuel Spent" },
      { key: "maintenance_spent", label: "Maintenance Spent" },
      { key: "insurance_spent", label: "Insurance Spent" },
      { key: "salary_spent", label: "Salary Spent" },
    ],
  },
  "transport-driver-schedule": {
    key: "transport-driver-schedule",
    icon: TruckIcon,
    label: "Transport Driver Schedule",
    endpoint: "transport-driver-schedule",
    titleField: "driver",
    fields: [
      { key: "driver", label: "Driver" },
      { key: "date", label: "Date", type: "date" },
      {
        key: "shift_type",
        label: "Shift Type",
        type: "select",
        options: [
          ["morning", "Morning"],
          ["afternoon", "Afternoon"],
          ["full_day", "Full Day"],
          ["overtime", "Overtime"],
        ],
      },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      { key: "routes_assigned", label: "Routes Assigned" },
      { key: "total_distance_km", label: "Total Distance Km" },
      { key: "total_hours", label: "Total Hours" },
      { key: "overtime_hours", label: "Overtime Hours" },
      { key: "is_available", label: "Is Available" },
      { key: "is_on_leave", label: "Is On Leave" },
    ],
  },
  "transport-fee-structure": {
    key: "transport-fee-structure",
    icon: TruckIcon,
    label: "Transport Fee Structure",
    endpoint: "transport-fee-structure",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "fee_type",
        label: "Fee Type",
        type: "select",
        options: [
          ["monthly", "Monthly"],
          ["quarterly", "Quarterly"],
          ["annual", "Annual"],
          ["per_trip", "Per Trip"],
          ["one_time", "One Time"],
        ],
      },
      { key: "amount", label: "Amount", type: "number" },
      { key: "route", label: "Route" },
      { key: "min_distance_km", label: "Min Distance Km" },
      { key: "max_distance_km", label: "Max Distance Km" },
      { key: "sibling_discount", label: "Sibling Discount" },
      { key: "early_bird_discount", label: "Early Bird Discount" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "academic_year", label: "Academic Year" },
    ],
  },
  "transport-incident": {
    key: "transport-incident",
    icon: TruckIcon,
    label: "Transport Incident",
    endpoint: "transport-incident",
    titleField: "vehicle",
    subtitleField: "status",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      { key: "route", label: "Route" },
      { key: "driver", label: "Driver" },
      {
        key: "incident_type",
        label: "Incident Type",
        type: "select",
        options: [
          ["accident", "Accident"],
          ["breakdown", "Breakdown"],
          ["delay", "Delay"],
          ["medical", "Medical"],
          ["behavioral", "Behavioral"],
          ["weather", "Weather"],
          ["other", "Other"],
        ],
      },
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: [
          ["low", "Low"],
          ["medium", "Medium"],
          ["high", "High"],
          ["critical", "Critical"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["reported", "Reported"],
          ["investigating", "Investigating"],
          ["resolved", "Resolved"],
          ["closed", "Closed"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "location", label: "Location" },
      { key: "incident_date", label: "Incident Date", type: "date" },
    ],
  },
  "transport-monthly-report": {
    key: "transport-monthly-report",
    icon: TruckIcon,
    label: "Transport Monthly Report",
    endpoint: "transport-monthly-report",
    titleField: "month",
    fields: [
      { key: "month", label: "Month" },
      { key: "year", label: "Year" },
      { key: "total_operational_days", label: "Total Operational Days" },
      { key: "total_trips", label: "Total Trips" },
      { key: "total_routes_active", label: "Total Routes Active" },
      { key: "vehicles_active", label: "Vehicles Active" },
      { key: "vehicles_maintained", label: "Vehicles Maintained" },
      { key: "avg_fleet_age_years", label: "Avg Fleet Age Years" },
      { key: "total_students_served", label: "Total Students Served" },
      { key: "avg_daily_riders", label: "Avg Daily Riders" },
      { key: "total_fuel_liters", label: "Total Fuel Liters" },
      { key: "total_fuel_cost", label: "Total Fuel Cost" },
    ],
  },
  "transport-schedule": {
    key: "transport-schedule",
    icon: TruckIcon,
    label: "Transport Schedule",
    endpoint: "transport-schedule",
    titleField: "route",
    fields: [
      { key: "route", label: "Route" },
      {
        key: "day_of_week",
        label: "Day Of Week",
        type: "select",
        options: [
          ["monday", "Monday"],
          ["tuesday", "Tuesday"],
          ["wednesday", "Wednesday"],
          ["thursday", "Thursday"],
          ["friday", "Friday"],
          ["saturday", "Saturday"],
        ],
      },
      { key: "pickup_start", label: "Pickup Start" },
      { key: "pickup_end", label: "Pickup End" },
      { key: "dropoff_start", label: "Dropoff Start" },
      { key: "dropoff_end", label: "Dropoff End" },
      { key: "vehicle", label: "Vehicle" },
      { key: "driver", label: "Driver" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  trips: {
    key: "trips",
    icon: TruckIcon,
    label: "Trip Schedule",
    endpoint: "trips",
    titleField: "title",
    fields: [
      { key: "title", label: "Title" },
      {
        key: "trip_type",
        label: "Trip Type",
        type: "select",
        options: [
          ["field_trip", "Field Trip"],
          ["sports_event", "Sports Event"],
          ["cultural_event", "Cultural Event"],
          ["examination", "Examination"],
          ["other", "Other"],
        ],
      },
      { key: "destination", label: "Destination" },
      { key: "trip_date", label: "Trip Date", type: "date" },
      { key: "departure_time", label: "Departure Time" },
      { key: "return_time", label: "Return Time" },
      { key: "vehicle", label: "Vehicle" },
      { key: "driver", label: "Driver" },
      { key: "route", label: "Route" },
    ],
  },
  "vehicle-assignment-log": {
    key: "vehicle-assignment-log",
    icon: TruckIcon,
    label: "Vehicle Assignment Log",
    endpoint: "vehicle-assignment-log",
    titleField: "vehicle",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      { key: "route", label: "Route" },
      { key: "driver", label: "Driver" },
      { key: "assignment_date", label: "Assignment Date", type: "date" },
      {
        key: "assignment_type",
        label: "Assignment Type",
        type: "select",
        options: [
          ["route", "Route"],
          ["trip", "Trip"],
          ["pool", "Pool"],
          ["maintenance", "Maintenance"],
        ],
      },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      { key: "purpose", label: "Purpose" },
      { key: "assigned_by", label: "Assigned By" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "vehicle-condition-report": {
    key: "vehicle-condition-report",
    icon: TruckIcon,
    label: "Vehicle Condition Report",
    endpoint: "vehicle-condition-report",
    titleField: "report_type",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      { key: "driver", label: "Driver" },
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: [
          ["pre_trip", "Pre Trip"],
          ["post_trip", "Post Trip"],
          ["spot_check", "Spot Check"],
        ],
      },
      { key: "report_date", label: "Report Date", type: "date" },
      {
        key: "tires_condition",
        label: "Tires Condition",
        type: "select",
        options: [
          ["excellent", "Excellent"],
          ["good", "Good"],
          ["fair", "Fair"],
          ["poor", "Poor"],
          ["not_working", "Not Working"],
        ],
      },
      {
        key: "brakes_condition",
        label: "Brakes Condition",
        type: "select",
        options: [
          ["excellent", "Excellent"],
          ["good", "Good"],
          ["fair", "Fair"],
          ["poor", "Poor"],
          ["not_working", "Not Working"],
        ],
      },
      {
        key: "lights_condition",
        label: "Lights Condition",
        type: "select",
        options: [
          ["excellent", "Excellent"],
          ["good", "Good"],
          ["fair", "Fair"],
          ["poor", "Poor"],
          ["not_working", "Not Working"],
        ],
      },
      {
        key: "mirrors_condition",
        label: "Mirrors Condition",
        type: "select",
        options: [
          ["excellent", "Excellent"],
          ["good", "Good"],
          ["fair", "Fair"],
          ["poor", "Poor"],
          ["not_working", "Not Working"],
        ],
      },
      {
        key: "body_condition",
        label: "Body Condition",
        type: "select",
        options: [
          ["excellent", "Excellent"],
          ["good", "Good"],
          ["fair", "Fair"],
          ["poor", "Poor"],
          ["not_working", "Not Working"],
        ],
      },
      {
        key: "interior_condition",
        label: "Interior Condition",
        type: "select",
        options: [
          ["excellent", "Excellent"],
          ["good", "Good"],
          ["fair", "Fair"],
          ["poor", "Poor"],
          ["not_working", "Not Working"],
        ],
      },
      { key: "fuel_level", label: "Fuel Level" },
      { key: "mileage", label: "Mileage" },
    ],
  },
  "vehicle-g-p-s-log": {
    key: "vehicle-g-p-s-log",
    icon: TruckIcon,
    label: "Vehicle G P S Log",
    endpoint: "vehicle-g-p-s-log",
    titleField: "vehicle",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      { key: "latitude", label: "Latitude" },
      { key: "longitude", label: "Longitude" },
      { key: "speed_kmh", label: "Speed Kmh" },
      { key: "heading", label: "Heading" },
      { key: "timestamp", label: "Timestamp" },
      { key: "ignition_on", label: "Ignition On" },
      { key: "battery_level", label: "Battery Level" },
    ],
  },
  "vehicle-pool": {
    key: "vehicle-pool",
    icon: TruckIcon,
    label: "Vehicle Pool",
    endpoint: "vehicle-pool",
    titleField: "vehicle",
    subtitleField: "status",
    fields: [
      { key: "vehicle", label: "Vehicle" },
      {
        key: "pool_type",
        label: "Pool Type",
        type: "select",
        options: [
          ["field_trip", "Field Trip"],
          ["staff", "Staff"],
          ["emergency", "Emergency"],
          ["replacement", "Replacement"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["available", "Available"],
          ["booked", "Booked"],
          ["in_use", "In Use"],
          ["maintenance", "Maintenance"],
        ],
      },
      { key: "booked_by", label: "Booked By" },
      { key: "purpose", label: "Purpose" },
      { key: "destination", label: "Destination" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "start_time", label: "Start Time" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "end_time", label: "End Time" },
    ],
  },
  vehicles: {
    key: "vehicles",
    icon: TruckIcon,
    label: "Vehicle",
    endpoint: "vehicles",
    titleField: "plate_number",
    subtitleField: "status",
    fields: [
      { key: "plate_number", label: "Plate Number" },
      {
        key: "vehicle_type",
        label: "Vehicle Type",
        type: "select",
        options: [
          ["bus", "Bus"],
          ["mini_bus", "Mini Bus"],
          ["van", "Van"],
          ["suv", "Suv"],
          ["sedan", "Sedan"],
          ["other", "Other"],
        ],
      },
      { key: "model_name", label: "Model Name" },
      { key: "year", label: "Year" },
      { key: "capacity", label: "Capacity" },
      { key: "color", label: "Color" },
      { key: "chassis_number", label: "Chassis Number" },
      { key: "engine_number", label: "Engine Number" },
      { key: "insurance_number", label: "Insurance Number" },
      { key: "insurance_expiry", label: "Insurance Expiry" },
      { key: "fitness_expiry", label: "Fitness Expiry" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["in_maintenance", "In Maintenance"],
          ["retired", "Retired"],
          ["out_of_service", "Out Of Service"],
        ],
      },
    ],
  },
};

const TABS = Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({
  key,
  label: cfg.label,
  icon: TruckIcon,
}));

export default function TransportationCenterPage() {
  useTitle("Transportation Center");
  useShortcutHelp();
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTab = searchParams.get("tab");
  const [activeTab, setActiveTabState] = useState(
    initialTab && ENTITY_CONFIGS[initialTab] ? initialTab : TABS[0]?.key ?? "",
  );
  // Keep ?tab= in the URL so center-page deep links work (and survive reloads).
  const setActiveTab = (key: string) => {
    setActiveTabState(key);
    setSearchParams({ tab: key }, { replace: true });
  };
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const [helpOpen, setHelpOpen] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);
  const actionRef = useRef<{ add?: () => void; export?: () => void }>({});

  useEffect(() => {
    setPage(1);
  }, [activeTab]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {
        return;
      }
      if (e.key === "/") {
        e.preventDefault();
        searchRef.current?.focus();
      } else if (e.key.toLowerCase() === "n") {
        e.preventDefault();
        actionRef.current.add?.();
      } else if (e.key.toLowerCase() === "e") {
        e.preventDefault();
        actionRef.current.export?.();
      } else if (e.key.toLowerCase() === "p") {
        e.preventDefault();
        setViewMode((v) => (v === "pagination" ? "infinite" : "pagination"));
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  const activeCfg = ENTITY_CONFIGS[activeTab];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Transportation Center
          </h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Vehicles, drivers, routes, stops, tracking, GPS, geofences, fees, incidents, maintenance
            and analytics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              ref={searchRef}
              type="search"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search…  ( / )"
              className="w-56 rounded-xl border border-slate-200 bg-white px-4 py-2 pl-9 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
          </div>
          <div className="flex items-center gap-1 rounded-xl border border-slate-200 p-1 dark:border-slate-600">
            <button
              onClick={() => setViewMode("pagination")}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                viewMode === "pagination"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                  : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700"
              }`}
            >
              Paginated
            </button>
            <button
              onClick={() => setViewMode("infinite")}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                viewMode === "infinite"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                  : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700"
              }`}
            >
              Infinite
            </button>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setHelpOpen(true)}
            leftIcon={<TruckIcon className="h-4 w-4" />}
          >
            Shortcuts
          </Button>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`flex shrink-0 items-center gap-1.5 rounded-xl px-3.5 py-2 text-sm font-medium transition ${
              activeTab === t.key
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-white text-slate-600 hover:bg-slate-50 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            }`}
          >
            <t.icon className="h-4 w-4" />
            {t.label}
          </button>
        ))}
      </div>

      <EntitySection
        cfg={activeCfg}
        basePath="/transport"
        search={search}
        page={page}
        setPage={setPage}
        viewMode={viewMode}
        registerActions={(h) => {
          actionRef.current = h;
        }}
      />

      <KeyboardShortcutHelp
        open={helpOpen}
        onClose={() => setHelpOpen(false)}
        shortcuts={[
          { keys: ["N"], label: "New", description: "New record" },
          { keys: ["/"], label: "Search", description: "Focus search" },
          { keys: ["E"], label: "Export", description: "Export CSV" },
          {
            keys: ["P"],
            label: "Pages",
            description: "Toggle pagination / infinite scroll",
          },
        ]}
      />
    </div>
  );
}
