/**
 * Attendance Center — full-surface admin page for the attendance module.
 *
 * 41 entity tabs (config-driven via EntitySection). Records, period attendance, leaves, tardies, corrections, biometric, GPS, analytics and alerts.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, ClipboardDocumentCheckIcon } from "@heroicons/react/24/outline";

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  // ===== attendance =====
  archives: {
    key: "archives",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Data Archive",
    endpoint: "archives",
    titleField: "academic_year",
    fields: [
      { key: "academic_year", label: "Academic Year" },
      {
        key: "archive_type",
        label: "Archive Type",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["period", "Period"],
        ],
      },
      { key: "data", label: "Data", type: "textarea" },
      { key: "record_count", label: "Record Count", type: "number" },
      { key: "date_from", label: "Date From", type: "date" },
      { key: "date_to", label: "Date To", type: "date" },
      { key: "archived_at", label: "Archived At", type: "date" },
      { key: "is_purged", label: "Is Purged" },
      { key: "academic_year_name", label: "Academic Year Name" },
    ],
  },
  "attendance-alert-config": {
    key: "attendance-alert-config",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Alert Config",
    endpoint: "attendance-alert-config",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "absence_threshold", label: "Absence Threshold" },
      { key: "tardy_threshold", label: "Tardy Threshold" },
      { key: "lookback_days", label: "Lookback Days" },
      { key: "consecutive_absences", label: "Consecutive Absences" },
      { key: "consecutive_count", label: "Consecutive Count" },
      { key: "notify_parent", label: "Notify Parent" },
      { key: "notify_counselor", label: "Notify Counselor" },
      { key: "notify_admin", label: "Notify Admin" },
      { key: "notify_teacher", label: "Notify Teacher" },
      { key: "email_template", label: "Email Template" },
    ],
  },
  "attendance-audit-entry": {
    key: "attendance-audit-entry",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Audit Entry",
    endpoint: "attendance-audit-entry",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      {
        key: "change_type",
        label: "Change Type",
        type: "select",
        options: [
          ["check_in", "Check In"],
          ["check_out", "Check Out"],
          ["status_change", "Status Change"],
          ["manual_override", "Manual Override"],
          ["bulk_import", "Bulk Import"],
          ["correction", "Correction"],
        ],
      },
      { key: "old_status", label: "Old Status" },
      { key: "new_status", label: "New Status" },
      { key: "old_time", label: "Old Time" },
      { key: "new_time", label: "New Time" },
      { key: "changed_by", label: "Changed By" },
      { key: "reason", label: "Reason" },
      { key: "change_date", label: "Change Date", type: "date" },
      { key: "change_timestamp", label: "Change Timestamp" },
      { key: "student_name", label: "Student Name" },
      { key: "changed_by_name", label: "Changed By Name" },
    ],
  },
  "attendance-comment": {
    key: "attendance-comment",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Comment",
    endpoint: "attendance-comment",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "author", label: "Author" },
      {
        key: "comment_type",
        label: "Comment Type",
        type: "select",
        options: [
          ["positive", "Positive"],
          ["concern", "Concern"],
          ["intervention", "Intervention"],
          ["parent_comm", "Parent Comm"],
          ["general", "General"],
        ],
      },
      { key: "comment", label: "Comment" },
      { key: "comment_date", label: "Comment Date", type: "date" },
      { key: "related_date", label: "Related Date", type: "date" },
      { key: "is_visible_to_parent", label: "Is Visible To Parent" },
      { key: "is_visible_to_student", label: "Is Visible To Student" },
      { key: "student_name", label: "Student Name" },
    ],
  },
  "attendance-configuration": {
    key: "attendance-configuration",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Configuration",
    endpoint: "attendance-configuration",
    titleField: "attendance_mode",
    fields: [
      {
        key: "attendance_mode",
        label: "Attendance Mode",
        type: "select",
        options: [
          ["class_period", "Class Period"],
          ["daily", "Daily"],
          ["both", "Both"],
        ],
      },
      {
        key: "check_in_method",
        label: "Check In Method",
        type: "select",
        options: [
          ["manual", "Manual"],
          ["qr", "Qr"],
          ["biometric", "Biometric"],
          ["rfid", "Rfid"],
          ["gps", "Gps"],
          ["app", "App"],
        ],
      },
      { key: "grace_period_minutes", label: "Grace Period Minutes" },
      { key: "tardy_threshold_minutes", label: "Tardy Threshold Minutes" },
      { key: "absent_threshold_minutes", label: "Absent Threshold Minutes" },
      {
        key: "early_departure_threshold_minutes",
        label: "Early Departure Threshold Minutes",
      },
      { key: "auto_notify_absent", label: "Auto Notify Absent" },
      { key: "auto_notify_tardy", label: "Auto Notify Tardy" },
      { key: "notify_after_minutes", label: "Notify After Minutes" },
      { key: "parent_portal_enabled", label: "Parent Portal Enabled" },
      { key: "parent_real_time_view", label: "Parent Real Time View" },
      { key: "auto_apply_holidays", label: "Auto Apply Holidays" },
    ],
  },
  "attendance-escalation": {
    key: "attendance-escalation",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Escalation",
    endpoint: "attendance-escalation",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      {
        key: "escalation_level",
        label: "Escalation Level",
        type: "select",
        options: [
          ["level_1", "Level 1"],
          ["level_2", "Level 2"],
          ["level_3", "Level 3"],
          ["level_4", "Level 4"],
          ["level_5", "Level 5"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["triggered", "Triggered"],
          ["resolved", "Resolved"],
          ["escalated", "Escalated"],
        ],
      },
      { key: "trigger_reason", label: "Trigger Reason" },
      { key: "absences_count", label: "Absences Count" },
      { key: "tardies_count", label: "Tardies Count" },
      { key: "actions_taken", label: "Actions Taken" },
      { key: "assigned_to", label: "Assigned To" },
      { key: "meeting_date", label: "Meeting Date", type: "date" },
      { key: "meeting_notes", label: "Meeting Notes" },
      { key: "student_name", label: "Student Name" },
      { key: "assigned_to_name", label: "Assigned To Name" },
    ],
  },
  "attendance-incentive": {
    key: "attendance-incentive",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Incentive",
    endpoint: "attendance-incentive",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "incentive_type",
        label: "Incentive Type",
        type: "select",
        options: [
          ["points", "Points"],
          ["badge", "Badge"],
          ["certificate", "Certificate"],
          ["prize", "Prize"],
          ["recognition", "Recognition"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "required_streak_days", label: "Required Streak Days" },
      { key: "required_percentage", label: "Required Percentage" },
      { key: "points_value", label: "Points Value" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "total_available", label: "Total Available" },
      { key: "total_awarded", label: "Total Awarded" },
    ],
  },
  "attendance-incentive-award": {
    key: "attendance-incentive-award",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Incentive Award",
    endpoint: "attendance-incentive-award",
    titleField: "incentive",
    fields: [
      { key: "incentive", label: "Incentive" },
      { key: "student", label: "Student" },
      { key: "awarded_date", label: "Awarded Date", type: "date" },
      { key: "awarded_by", label: "Awarded By" },
      { key: "streak_days", label: "Streak Days" },
      { key: "attendance_percentage", label: "Attendance Percentage" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "points_earned", label: "Points Earned" },
      { key: "total_points", label: "Total Points" },
      { key: "incentive_name", label: "Incentive Name" },
      { key: "student_name", label: "Student Name" },
      { key: "awarded_by_name", label: "Awarded By Name" },
    ],
  },
  "attendance-lockout": {
    key: "attendance-lockout",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Lockout",
    endpoint: "attendance-lockout",
    titleField: "lock_date",
    fields: [
      { key: "lock_date", label: "Lock Date", type: "date" },
      { key: "period", label: "Period" },
      { key: "locked_by", label: "Locked By" },
      { key: "lock_reason", label: "Lock Reason" },
      { key: "is_locked", label: "Is Locked" },
      { key: "locked_at", label: "Locked At", type: "date" },
      { key: "unlocked_by", label: "Unlocked By" },
      { key: "unlocked_at", label: "Unlocked At", type: "date" },
      { key: "unlock_reason", label: "Unlock Reason" },
    ],
  },
  "attendance-make-up": {
    key: "attendance-make-up",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Make Up",
    endpoint: "attendance-make-up",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "original_absence", label: "Original Absence" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["completed", "Completed"],
          ["excused", "Excused"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "make_up_date", label: "Make Up Date", type: "date" },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      { key: "location", label: "Location" },
      { key: "supervised_by", label: "Supervised By" },
      { key: "reason", label: "Reason" },
      { key: "student_name", label: "Student Name" },
    ],
  },
  "attendance-prediction": {
    key: "attendance-prediction",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Prediction",
    endpoint: "attendance-prediction",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      {
        key: "prediction_type",
        label: "Prediction Type",
        type: "select",
        options: [
          ["absence", "Absence"],
          ["chronic", "Chronic"],
          ["late", "Late"],
          ["drop", "Drop"],
        ],
      },
      { key: "risk_score", label: "Risk Score" },
      { key: "prediction_date", label: "Prediction Date", type: "date" },
      { key: "predicted_period_start", label: "Predicted Period Start" },
      { key: "predicted_period_end", label: "Predicted Period End" },
      { key: "risk_factors", label: "Risk Factors" },
      { key: "historical_pattern", label: "Historical Pattern" },
      { key: "recommended_action", label: "Recommended Action" },
      {
        key: "priority_level",
        label: "Priority Level",
        type: "select",
        options: [
          ["low", "Low"],
          ["medium", "Medium"],
          ["high", "High"],
        ],
      },
      { key: "reviewed", label: "Reviewed" },
      { key: "student_name", label: "Student Name" },
    ],
  },
  "attendance-record": {
    key: "attendance-record",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Record",
    endpoint: "attendance-record",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "classroom", label: "Classroom" },
      { key: "academic_year", label: "Academic Year" },
      { key: "date", label: "Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["P", "P"],
          ["A", "A"],
          ["L", "L"],
          ["E", "E"],
          ["H", "H"],
        ],
      },
      { key: "recorded_by", label: "Recorded By" },
      { key: "recorded_at", label: "Recorded At", type: "date" },
      { key: "updated_by", label: "Updated By" },
      { key: "remarks", label: "Remarks" },
      { key: "student_name", label: "Student Name" },
      { key: "classroom_name", label: "Classroom Name" },
      { key: "academic_year_name", label: "Academic Year Name" },
      { key: "recorded_by_name", label: "Recorded By Name" },
      { key: "updated_by_name", label: "Updated By Name" },
    ],
  },
  biometric: {
    key: "biometric",
    icon: ClipboardDocumentCheckIcon,
    label: "Biometric Checkin",
    endpoint: "biometric",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      {
        key: "biometric_type",
        label: "Biometric Type",
        type: "select",
        options: [
          ["fingerprint", "Fingerprint"],
          ["face", "Face"],
          ["iris", "Iris"],
          ["other", "Other"],
        ],
      },
      { key: "device_id", label: "Device Id" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["success", "Success"],
          ["failed", "Failed"],
          ["denied", "Denied"],
        ],
      },
      { key: "confidence_score", label: "Confidence Score" },
      { key: "latitude", label: "Latitude" },
      { key: "longitude", label: "Longitude" },
      { key: "checkin_time", label: "Checkin Time" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "student_name", label: "Student Name" },
    ],
  },
  "bulk-import": {
    key: "bulk-import",
    icon: ClipboardDocumentCheckIcon,
    label: "Bulk Attendance Import",
    endpoint: "bulk-import",
    titleField: "file_name",
    subtitleField: "status",
    fields: [
      { key: "file_name", label: "File Name" },
      { key: "file_url", label: "File Url" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["processing", "Processing"],
          ["completed", "Completed"],
          ["failed", "Failed"],
          ["partial", "Partial"],
        ],
      },
      { key: "total_records", label: "Total Records" },
      { key: "successful_records", label: "Successful Records" },
      { key: "failed_records", label: "Failed Records" },
      { key: "error_log", label: "Error Log" },
      { key: "date_column", label: "Date Column" },
      { key: "student_column", label: "Student Column" },
      { key: "status_column", label: "Status Column" },
      { key: "overwrite_existing", label: "Overwrite Existing" },
      { key: "imported_by", label: "Imported By" },
      { key: "imported_by_name", label: "Imported By Name" },
    ],
  },
  changelogs: {
    key: "changelogs",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Change Log",
    endpoint: "changelogs",
    titleField: "attendance_type",
    fields: [
      {
        key: "attendance_type",
        label: "Attendance Type",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["period", "Period"],
        ],
      },
      { key: "attendance_id", label: "Attendance Id" },
      {
        key: "change_type",
        label: "Change Type",
        type: "select",
        options: [
          ["create", "Create"],
          ["update", "Update"],
          ["delete", "Delete"],
          ["bulk_import", "Bulk Import"],
        ],
      },
      { key: "old_values", label: "Old Values" },
      { key: "new_values", label: "New Values" },
      { key: "changed_by", label: "Changed By" },
      { key: "changed_at", label: "Changed At", type: "date" },
      { key: "reason", label: "Reason" },
      { key: "changed_by_name", label: "Changed By Name" },
    ],
  },
  "chronic-absence": {
    key: "chronic-absence",
    icon: ClipboardDocumentCheckIcon,
    label: "Chronic Absence Tracking",
    endpoint: "chronic-absence",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "academic_year", label: "Academic Year" },
      { key: "term", label: "Term" },
      { key: "total_days", label: "Total Days" },
      { key: "days_present", label: "Days Present" },
      { key: "days_absent", label: "Days Absent" },
      { key: "days_late", label: "Days Late" },
      { key: "attendance_percentage", label: "Attendance Percentage" },
      { key: "absence_percentage", label: "Absence Percentage" },
      { key: "student_name", label: "Student Name" },
      { key: "academic_year_name", label: "Academic Year Name" },
    ],
  },
  corrections: {
    key: "corrections",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Correction Workflow",
    endpoint: "corrections",
    titleField: "correction_type",
    subtitleField: "status",
    fields: [
      {
        key: "correction_type",
        label: "Correction Type",
        type: "select",
        options: [
          ["status_change", "Status Change"],
          ["time_change", "Time Change"],
          ["add_record", "Add Record"],
          ["delete_record", "Delete Record"],
          ["bulk_update", "Bulk Update"],
        ],
      },
      { key: "attendance_record", label: "Attendance Record" },
      { key: "period_attendance", label: "Period Attendance" },
      { key: "old_status", label: "Old Status" },
      { key: "new_status", label: "New Status" },
      { key: "old_time", label: "Old Time" },
      { key: "new_time", label: "New Time" },
      { key: "reason", label: "Reason" },
      { key: "supporting_document", label: "Supporting Document" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["rejected", "Rejected"],
          ["auto_approved", "Auto Approved"],
        ],
      },
    ],
  },
  dashboard: {
    key: "dashboard",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Dashboard",
    endpoint: "dashboard",
    titleField: "title",
    fields: [
      {
        key: "dashboard_type",
        label: "Dashboard Type",
        type: "select",
        options: [
          ["school", "School"],
          ["grade", "Grade"],
          ["classroom", "Classroom"],
          ["student", "Student"],
          ["teacher", "Teacher"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "total_students", label: "Total Students", type: "number" },
      { key: "average_attendance", label: "Average Attendance" },
      { key: "present_count", label: "Present Count" },
      { key: "absent_count", label: "Absent Count" },
      { key: "late_count", label: "Late Count" },
      { key: "excused_count", label: "Excused Count" },
      { key: "attendance_trend", label: "Attendance Trend" },
      { key: "daily_breakdown", label: "Daily Breakdown" },
    ],
  },
  "early-dismissal": {
    key: "early-dismissal",
    icon: ClipboardDocumentCheckIcon,
    label: "Early Dismissal",
    endpoint: "early-dismissal",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "requested_by", label: "Requested By" },
      {
        key: "reason_type",
        label: "Reason Type",
        type: "select",
        options: [
          ["medical", "Medical"],
          ["dental", "Dental"],
          ["family", "Family"],
          ["religious", "Religious"],
          ["personal", "Personal"],
          ["bus", "Bus"],
          ["other", "Other"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["denied", "Denied"],
          ["completed", "Completed"],
        ],
      },
      { key: "dismissal_date", label: "Dismissal Date", type: "date" },
      { key: "requested_departure_time", label: "Requested Departure Time" },
      { key: "actual_departure_time", label: "Actual Departure Time" },
      { key: "reason_detail", label: "Reason Detail" },
      { key: "pickup_person", label: "Pickup Person" },
      { key: "pickup_id_verified", label: "Pickup Id Verified" },
      { key: "student_name", label: "Student Name" },
      { key: "requested_by_name", label: "Requested By Name" },
    ],
  },
  "field-trip": {
    key: "field-trip",
    icon: ClipboardDocumentCheckIcon,
    label: "Field Trip",
    endpoint: "field-trip",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "destination", label: "Destination" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["planned", "Planned"],
          ["approved", "Approved"],
          ["active", "Active"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "departure_date", label: "Departure Date", type: "date" },
      { key: "departure_time", label: "Departure Time" },
      { key: "return_date", label: "Return Date", type: "date" },
      { key: "return_time", label: "Return Time" },
      { key: "organizer", label: "Organizer" },
      { key: "chaperones", label: "Chaperones" },
      { key: "eligible_grades", label: "Eligible Grades" },
      { key: "organizer_name", label: "Organizer Name" },
    ],
  },
  "field-trip-participant": {
    key: "field-trip-participant",
    icon: ClipboardDocumentCheckIcon,
    label: "Field Trip Participant",
    endpoint: "field-trip-participant",
    titleField: "field_trip",
    fields: [
      { key: "field_trip", label: "Field Trip" },
      { key: "student", label: "Student" },
      {
        key: "consent_status",
        label: "Consent Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["granted", "Granted"],
          ["denied", "Denied"],
        ],
      },
      {
        key: "attendance_status",
        label: "Attendance Status",
        type: "select",
        options: [
          ["enrolled", "Enrolled"],
          ["attended", "Attended"],
          ["absent", "Absent"],
          ["excused", "Excused"],
        ],
      },
      { key: "parent_contacted", label: "Parent Contacted" },
      { key: "payment_status", label: "Payment Status" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "enrolled_at", label: "Enrolled At", type: "date" },
      { key: "field_trip_title", label: "Field Trip Title" },
      { key: "student_name", label: "Student Name" },
    ],
  },
  gps: {
    key: "gps",
    icon: ClipboardDocumentCheckIcon,
    label: "G P S Attendance",
    endpoint: "gps",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "latitude", label: "Latitude" },
      { key: "longitude", label: "Longitude" },
      { key: "accuracy_meters", label: "Accuracy Meters" },
      { key: "geofence_name", label: "Geofence Name" },
      { key: "geofence_radius", label: "Geofence Radius" },
      { key: "distance_from_school", label: "Distance From School" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["verified", "Verified"],
          ["out_of_range", "Out Of Range"],
          ["pending", "Pending"],
          ["denied", "Denied"],
        ],
      },
      { key: "device_id", label: "Device Id" },
      { key: "device_type", label: "Device Type" },
      { key: "checkin_time", label: "Checkin Time" },
      { key: "student_name", label: "Student Name" },
    ],
  },
  history: {
    key: "history",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance History View",
    endpoint: "history",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "academic_year", label: "Academic Year" },
      { key: "term", label: "Term" },
      { key: "total_days", label: "Total Days" },
      { key: "days_present", label: "Days Present" },
      { key: "days_absent", label: "Days Absent" },
      { key: "days_late", label: "Days Late" },
      { key: "days_excused", label: "Days Excused" },
      { key: "attendance_percentage", label: "Attendance Percentage" },
      { key: "timeline_data", label: "Timeline Data" },
      { key: "monthly_trend", label: "Monthly Trend" },
      { key: "student_name", label: "Student Name" },
      { key: "academic_year_name", label: "Academic Year Name" },
    ],
  },
  holidays: {
    key: "holidays",
    icon: ClipboardDocumentCheckIcon,
    label: "Holiday",
    endpoint: "holidays",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "date", label: "Date", type: "date" },
      {
        key: "holiday_type",
        label: "Holiday Type",
        type: "select",
        options: [
          ["public", "Public"],
          ["school", "School"],
          ["exam", "Exam"],
          ["vacation", "Vacation"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "academic_year", label: "Academic Year" },
    ],
  },
  "leave-approval-level": {
    key: "leave-approval-level",
    icon: ClipboardDocumentCheckIcon,
    label: "Leave Approval Level",
    endpoint: "leave-approval-level",
    titleField: "leave",
    subtitleField: "status",
    fields: [
      { key: "leave", label: "Leave" },
      { key: "level", label: "Level" },
      { key: "approver", label: "Approver" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["rejected", "Rejected"],
          ["skipped", "Skipped"],
        ],
      },
      { key: "remarks", label: "Remarks" },
      { key: "decided_at", label: "Decided At", type: "date" },
    ],
  },
  "leave-balances": {
    key: "leave-balances",
    icon: ClipboardDocumentCheckIcon,
    label: "Leave Balance",
    endpoint: "leave-balances",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "academic_year", label: "Academic Year" },
      { key: "sick_leave_total", label: "Sick Leave Total" },
      { key: "sick_leave_used", label: "Sick Leave Used" },
      { key: "casual_leave_total", label: "Casual Leave Total" },
      { key: "casual_leave_used", label: "Casual Leave Used" },
      { key: "other_leave_total", label: "Other Leave Total" },
      { key: "other_leave_used", label: "Other Leave Used" },
      { key: "student_name", label: "Student Name" },
      { key: "academic_year_name", label: "Academic Year Name" },
    ],
  },
  leaves: {
    key: "leaves",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Leave",
    endpoint: "leaves",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      {
        key: "leave_type",
        label: "Leave Type",
        type: "select",
        options: [
          ["sick", "Sick"],
          ["family", "Family"],
          ["official", "Official"],
          ["other", "Other"],
        ],
      },
      { key: "from_date", label: "From Date", type: "date" },
      { key: "to_date", label: "To Date", type: "date" },
      { key: "reason", label: "Reason" },
      { key: "supporting_document", label: "Supporting Document" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["rejected", "Rejected"],
        ],
      },
      { key: "reviewed_by", label: "Reviewed By" },
      { key: "review_remarks", label: "Review Remarks" },
      { key: "requested_at", label: "Requested At", type: "date" },
      { key: "reviewed_at", label: "Reviewed At", type: "date" },
      { key: "student_name", label: "Student Name" },
      { key: "reviewed_by_name", label: "Reviewed By Name" },
    ],
  },
  "parent-notifications": {
    key: "parent-notifications",
    icon: ClipboardDocumentCheckIcon,
    label: "Parent Notification",
    endpoint: "parent-notifications",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      {
        key: "notification_type",
        label: "Notification Type",
        type: "select",
        options: [
          ["absence", "Absence"],
          ["late", "Late"],
          ["early_departure", "Early Departure"],
          ["chronic", "Chronic"],
          ["pattern", "Pattern"],
          ["other", "Other"],
        ],
      },
      {
        key: "channel",
        label: "Channel",
        type: "select",
        options: [
          ["sms", "Sms"],
          ["email", "Email"],
          ["push", "Push"],
          ["all", "All"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "message", label: "Message", type: "textarea" },
      { key: "parent_email", label: "Parent Email" },
      { key: "parent_phone", label: "Parent Phone" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["sent", "Sent"],
          ["delivered", "Delivered"],
          ["failed", "Failed"],
          ["read", "Read"],
        ],
      },
      { key: "sent_at", label: "Sent At", type: "date" },
      { key: "delivered_at", label: "Delivered At", type: "date" },
      { key: "read_at", label: "Read At", type: "date" },
      { key: "student_name", label: "Student Name" },
    ],
  },
  patterns: {
    key: "patterns",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Patterns",
    endpoint: "patterns",
    titleField: "student",
    subtitleField: "frequency",
    fields: [
      { key: "student", label: "Student" },
      { key: "academic_year", label: "Academic Year" },
      {
        key: "pattern_type",
        label: "Pattern Type",
        type: "select",
        options: [
          ["weekday", "Weekday"],
          ["monthly", "Monthly"],
          ["seasonal", "Seasonal"],
          ["consecutive", "Consecutive"],
          ["before_after_break", "Before After Break"],
        ],
      },
      { key: "pattern_name", label: "Pattern Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "frequency", label: "Frequency" },
      { key: "percentage", label: "Percentage", type: "number" },
      {
        key: "risk_level",
        label: "Risk Level",
        type: "select",
        options: [
          ["low", "Low"],
          ["medium", "Medium"],
          ["high", "High"],
          ["critical", "Critical"],
        ],
      },
      { key: "pattern_data", label: "Pattern Data" },
      { key: "affected_dates", label: "Affected Dates" },
      { key: "student_name", label: "Student Name" },
      { key: "academic_year_name", label: "Academic Year Name" },
    ],
  },
  periods: {
    key: "periods",
    icon: ClipboardDocumentCheckIcon,
    label: "Period Attendance",
    endpoint: "periods",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "assignment", label: "Assignment" },
      { key: "date", label: "Date", type: "date" },
      { key: "period_number", label: "Period Number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["P", "P"],
          ["A", "A"],
          ["L", "L"],
        ],
      },
      { key: "recorded_by", label: "Recorded By" },
      { key: "recorded_at", label: "Recorded At", type: "date" },
      { key: "updated_by", label: "Updated By" },
      { key: "student_name", label: "Student Name" },
      { key: "assignment_label", label: "Assignment Label" },
      { key: "recorded_by_name", label: "Recorded By Name" },
      { key: "updated_by_name", label: "Updated By Name" },
    ],
  },
  policies: {
    key: "policies",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Policy",
    endpoint: "policies",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "min_attendance_pct", label: "Min Attendance Pct" },
      { key: "auto_fail_below", label: "Auto Fail Below" },
      { key: "notify_parent_below_pct", label: "Notify Parent Below Pct" },
      { key: "notify_admin_below_pct", label: "Notify Admin Below Pct" },
      { key: "edit_window_days", label: "Edit Window Days" },
      { key: "reminder_time", label: "Reminder Time" },
      { key: "escalation_enabled", label: "Escalation Enabled" },
      { key: "escalation_after_minutes", label: "Escalation After Minutes" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "q-r-code-checkin": {
    key: "q-r-code-checkin",
    icon: ClipboardDocumentCheckIcon,
    label: "Q R Code Checkin",
    endpoint: "q-r-code-checkin",
    titleField: "session",
    fields: [
      { key: "session", label: "Session" },
      { key: "student", label: "Student" },
      { key: "checked_in_at", label: "Checked In At", type: "date" },
      { key: "ip_address", label: "Ip Address" },
      { key: "device_info", label: "Device Info" },
    ],
  },
  "qr-sessions": {
    key: "qr-sessions",
    icon: ClipboardDocumentCheckIcon,
    label: "Q R Code Session",
    endpoint: "qr-sessions",
    titleField: "classroom",
    fields: [
      { key: "classroom", label: "Classroom" },
      { key: "teacher", label: "Teacher" },
      { key: "date", label: "Date", type: "date" },
      { key: "period_number", label: "Period Number" },
      { key: "qr_code", label: "Qr Code" },
      { key: "secret_key", label: "Secret Key" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "expires_at", label: "Expires At", type: "date" },
      { key: "classroom_name", label: "Classroom Name" },
      { key: "teacher_name", label: "Teacher Name" },
    ],
  },
  realtime: {
    key: "realtime",
    icon: ClipboardDocumentCheckIcon,
    label: "Real Time Dashboard",
    endpoint: "realtime",
    titleField: "scope",
    fields: [
      {
        key: "scope",
        label: "Scope",
        type: "select",
        options: [
          ["school", "School"],
          ["grade", "Grade"],
          ["classroom", "Classroom"],
          ["bus", "Bus"],
          ["dormitory", "Dormitory"],
        ],
      },
      { key: "scope_id", label: "Scope Id" },
      { key: "total_expected", label: "Total Expected" },
      { key: "total_present", label: "Total Present" },
      { key: "total_absent", label: "Total Absent" },
      { key: "total_late", label: "Total Late" },
      { key: "total_excused", label: "Total Excused" },
      { key: "total_early_departure", label: "Total Early Departure" },
      { key: "attendance_percentage", label: "Attendance Percentage" },
      { key: "live_checkins", label: "Live Checkins" },
      { key: "recent_alerts", label: "Recent Alerts" },
      { key: "last_refreshed", label: "Last Refreshed" },
    ],
  },
  records: {
    key: "records",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Record",
    endpoint: "records",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "classroom", label: "Classroom" },
      { key: "academic_year", label: "Academic Year" },
      { key: "date", label: "Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["P", "P"],
          ["A", "A"],
          ["L", "L"],
          ["E", "E"],
          ["H", "H"],
        ],
      },
      { key: "recorded_by", label: "Recorded By" },
      { key: "recorded_at", label: "Recorded At", type: "date" },
      { key: "updated_by", label: "Updated By" },
      { key: "remarks", label: "Remarks" },
      { key: "student_name", label: "Student Name" },
      { key: "classroom_name", label: "Classroom Name" },
      { key: "academic_year_name", label: "Academic Year Name" },
      { key: "recorded_by_name", label: "Recorded By Name" },
      { key: "updated_by_name", label: "Updated By Name" },
    ],
  },
  reports: {
    key: "reports",
    icon: ClipboardDocumentCheckIcon,
    label: "Attendance Report",
    endpoint: "reports",
    titleField: "title",
    subtitleField: "report_type",
    fields: [
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["monthly", "Monthly"],
          ["term", "Term"],
          ["annual", "Annual"],
          ["custom", "Custom"],
          ["student", "Student"],
          ["class", "Class"],
          ["chronic", "Chronic"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "classroom", label: "Classroom" },
      { key: "student", label: "Student" },
      { key: "grade", label: "Grade" },
      { key: "total_students", label: "Total Students", type: "number" },
      { key: "classroom_name", label: "Classroom Name" },
      { key: "student_name", label: "Student Name" },
    ],
  },
  rfid: {
    key: "rfid",
    icon: ClipboardDocumentCheckIcon,
    label: "R F I D Checkin",
    endpoint: "rfid",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "card_number", label: "Card Number" },
      { key: "reader_id", label: "Reader Id" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["success", "Success"],
          ["failed", "Failed"],
          ["denied", "Denied"],
          ["lost", "Lost"],
        ],
      },
      { key: "location", label: "Location" },
      { key: "latitude", label: "Latitude" },
      { key: "longitude", label: "Longitude" },
      { key: "checkin_time", label: "Checkin Time" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "student_name", label: "Student Name" },
    ],
  },
  "student-attendance-summary": {
    key: "student-attendance-summary",
    icon: ClipboardDocumentCheckIcon,
    label: "Student Attendance Summary",
    endpoint: "student-attendance-summary",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "academic_year", label: "Academic Year" },
      { key: "semester", label: "Semester" },
      { key: "total_school_days", label: "Total School Days" },
      { key: "days_present", label: "Days Present" },
      { key: "days_absent", label: "Days Absent" },
      { key: "days_late", label: "Days Late" },
      { key: "days_excused", label: "Days Excused" },
      { key: "days_early_departure", label: "Days Early Departure" },
      { key: "attendance_percentage", label: "Attendance Percentage" },
      { key: "tardiness_rate", label: "Tardiness Rate" },
      { key: "student_name", label: "Student Name" },
      { key: "academic_year_name", label: "Academic Year Name" },
    ],
  },
  substitutes: {
    key: "substitutes",
    icon: ClipboardDocumentCheckIcon,
    label: "Substitute Teacher",
    endpoint: "substitutes",
    titleField: "subject",
    fields: [
      { key: "original_teacher", label: "Original Teacher" },
      { key: "substitute_teacher", label: "Substitute Teacher" },
      { key: "date", label: "Date", type: "date" },
      { key: "period_number", label: "Period Number" },
      { key: "classroom", label: "Classroom" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "reason", label: "Reason" },
      { key: "is_auto_assigned", label: "Is Auto Assigned" },
      { key: "classroom_name", label: "Classroom Name" },
    ],
  },
  "tardy-policy": {
    key: "tardy-policy",
    icon: ClipboardDocumentCheckIcon,
    label: "Tardy Policy",
    endpoint: "tardy-policy",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "tardy_count", label: "Tardy Count" },
      { key: "consequence", label: "Consequence" },
      { key: "notify_parent", label: "Notify Parent" },
      { key: "detention_minutes", label: "Detention Minutes" },
      { key: "in_school_suspension", label: "In School Suspension" },
      { key: "warning_only", label: "Warning Only" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "tardy-record": {
    key: "tardy-record",
    icon: ClipboardDocumentCheckIcon,
    label: "Tardy Record",
    endpoint: "tardy-record",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "attendance_record", label: "Attendance Record" },
      { key: "tardy_date", label: "Tardy Date", type: "date" },
      { key: "arrival_time", label: "Arrival Time" },
      { key: "minutes_late", label: "Minutes Late" },
      { key: "reason", label: "Reason" },
      { key: "excuse", label: "Excuse" },
      { key: "policy_applied", label: "Policy Applied" },
      { key: "consequence", label: "Consequence" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["recorded", "Recorded"],
          ["notified", "Notified"],
          ["consequence", "Consequence"],
          ["resolved", "Resolved"],
        ],
      },
      { key: "parent_notified", label: "Parent Notified" },
      { key: "student_name", label: "Student Name" },
      { key: "policy_name", label: "Policy Name" },
    ],
  },

  // ===== attendance_map =====
};

const TABS = Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({
  key,
  label: cfg.label,
  icon: ClipboardDocumentCheckIcon,
}));

export default function AttendanceCenterPage() {
  useTitle("Attendance Center");
  useShortcutHelp();
  const [activeTab, setActiveTab] = useState(TABS[0]?.key ?? "");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Attendance Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Records, period attendance, leaves, tardies, corrections, biometric, GPS, analytics and
            alerts
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
            leftIcon={<ClipboardDocumentCheckIcon className="h-4 w-4" />}
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
        basePath="/attendance"
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
