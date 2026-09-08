/**
 * Reporting Center — full-surface admin page for the reporting module.
 *
 * 38 entity tabs (config-driven via EntitySection). Dashboards, custom reports, KPIs, schedules, exports, insights and analytics.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, ChartBarIcon } from "@heroicons/react/24/outline";

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  "academic-performance": {
    key: "academic-performance",
    icon: ChartBarIcon,
    label: "Academic Performance Report",
    endpoint: "academic-performance",
    titleField: "title",
    fields: [
      { key: "title", label: "Title" },
      { key: "academic_year", label: "Academic Year" },
      { key: "grade", label: "Grade" },
      { key: "classroom", label: "Classroom" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "report_data", label: "Report Data", type: "textarea" },
      { key: "summary", label: "Summary", type: "textarea" },
      { key: "average_score", label: "Average Score", type: "number" },
    ],
  },
  "analytics-snapshot": {
    key: "analytics-snapshot",
    icon: ChartBarIcon,
    label: "Analytics Snapshot",
    endpoint: "analytics-snapshot",
    titleField: "snapshot_type",
    fields: [
      {
        key: "snapshot_type",
        label: "Snapshot Type",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["monthly", "Monthly"],
          ["term", "Term"],
          ["yearly", "Yearly"],
        ],
      },
      { key: "snapshot_date", label: "Snapshot Date", type: "date" },
      { key: "data", label: "Data", type: "textarea" },
      { key: "total_students", label: "Total Students", type: "number" },
      { key: "total_staff", label: "Total Staff", type: "number" },
      { key: "avg_attendance", label: "Avg Attendance", type: "number" },
      { key: "avg_gpa", label: "Avg Gpa", type: "number" },
      { key: "pass_rate", label: "Pass Rate", type: "number" },
      { key: "total_revenue", label: "Total Revenue", type: "number" },
      { key: "total_expenses", label: "Total Expenses", type: "number" },
      { key: "new_enrollments", label: "New Enrollments", type: "number" },
      { key: "dropouts", label: "Dropouts", type: "number" },
    ],
  },
  "chart-configuration": {
    key: "chart-configuration",
    icon: ChartBarIcon,
    label: "Chart Configuration",
    endpoint: "chart-configuration",
    titleField: "name",
    subtitleField: "chart_type",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "chart_type",
        label: "Chart Type",
        type: "select",
        options: [
          ["bar", "Bar"],
          ["line", "Line"],
          ["pie", "Pie"],
          ["doughnut", "Doughnut"],
          ["scatter", "Scatter"],
          ["area", "Area"],
          ["heatmap", "Heatmap"],
          ["table", "Table"],
        ],
      },
      { key: "data_source", label: "Data Source", type: "textarea" },
      { key: "query", label: "Query", type: "textarea" },
      { key: "colors", label: "Colors" },
      { key: "config", label: "Config", type: "textarea" },
      { key: "created_by", label: "Created By" },
      { key: "is_public", label: "Is Public", type: "bool" },
      { key: "total_views", label: "Total Views", type: "number" },
    ],
  },
  compliance: {
    key: "compliance",
    icon: ChartBarIcon,
    label: "Compliance Report",
    endpoint: "compliance",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "title", label: "Title" },
      {
        key: "compliance_type",
        label: "Compliance Type",
        type: "select",
        options: [
          ["government", "Government"],
          ["accreditation", "Accreditation"],
          ["insurance", "Insurance"],
          ["financial", "Financial"],
          ["safety", "Safety"],
          ["other", "Other"],
        ],
      },
      { key: "academic_year", label: "Academic Year" },
      { key: "submission_date", label: "Submission Date", type: "date" },
      { key: "due_date", label: "Due Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["submitted", "Submitted"],
          ["approved", "Approved"],
          ["rejected", "Rejected"],
        ],
      },
      { key: "report_data", label: "Report Data", type: "textarea" },
      { key: "summary", label: "Summary", type: "textarea" },
      { key: "submitted_to", label: "Submitted To" },
      { key: "reference_number", label: "Reference Number" },
      { key: "generated_by", label: "Generated By" },
    ],
  },
  "custom-report": {
    key: "custom-report",
    icon: ChartBarIcon,
    label: "Custom Report",
    endpoint: "custom-report",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["active", "Active"],
          ["archived", "Archived"],
        ],
      },
      { key: "data_sources", label: "Data Sources", type: "textarea" },
      { key: "default_filters", label: "Default Filters", type: "textarea" },
      {
        key: "available_filters",
        label: "Available Filters",
        type: "textarea",
      },
      { key: "columns", label: "Columns", type: "textarea" },
      { key: "default_sort", label: "Default Sort", type: "textarea" },
      { key: "group_by", label: "Group By", type: "textarea" },
      { key: "aggregations", label: "Aggregations", type: "textarea" },
      { key: "chart_config", label: "Chart Config", type: "textarea" },
      { key: "created_by", label: "Created By" },
    ],
  },
  "custom-report-execution": {
    key: "custom-report-execution",
    icon: ChartBarIcon,
    label: "Custom Report Execution",
    endpoint: "custom-report-execution",
    titleField: "report",
    subtitleField: "status",
    fields: [
      { key: "report", label: "Report" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["running", "Running"],
          ["completed", "Completed"],
          ["failed", "Failed"],
        ],
      },
      { key: "parameters", label: "Parameters", type: "textarea" },
      { key: "result_file", label: "Result File", type: "textarea" },
      { key: "record_count", label: "Record Count", type: "number" },
      { key: "started_at", label: "Started At", type: "date" },
      { key: "completed_at", label: "Completed At", type: "date" },
      { key: "duration_seconds", label: "Duration Seconds", type: "number" },
      { key: "error_message", label: "Error Message", type: "textarea" },
      { key: "executed_by", label: "Executed By" },
    ],
  },
  "dashboard-configuration": {
    key: "dashboard-configuration",
    icon: ChartBarIcon,
    label: "Dashboard Configuration",
    endpoint: "dashboard-configuration",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "is_default", label: "Is Default", type: "bool" },
      { key: "is_public", label: "Is Public", type: "bool" },
      { key: "columns", label: "Columns", type: "textarea" },
      { key: "theme", label: "Theme" },
    ],
  },
  "dashboard-widget": {
    key: "dashboard-widget",
    icon: ChartBarIcon,
    label: "Dashboard Widget",
    endpoint: "dashboard-widget",
    titleField: "name",
    subtitleField: "widget_type",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "widget_type",
        label: "Widget Type",
        type: "select",
        options: [
          ["chart", "Chart"],
          ["table", "Table"],
          ["kpi", "Kpi"],
          ["map", "Map"],
          ["list", "List"],
          ["calendar", "Calendar"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "data_source", label: "Data Source", type: "textarea" },
      { key: "config", label: "Config", type: "textarea" },
      {
        key: "refresh_interval_seconds",
        label: "Refresh Interval Seconds",
        type: "number",
      },
      { key: "position_x", label: "Position X", type: "number" },
      { key: "position_y", label: "Position Y", type: "number" },
      { key: "width", label: "Width", type: "number" },
      { key: "height", label: "Height", type: "number" },
      { key: "is_default", label: "Is Default", type: "bool" },
      { key: "visible_to_roles", label: "Visible To Roles", type: "textarea" },
    ],
  },
  department: {
    key: "department",
    icon: ChartBarIcon,
    label: "Department Report",
    endpoint: "department",
    titleField: "title",
    fields: [
      { key: "title", label: "Title" },
      { key: "department", label: "Department" },
      { key: "academic_year", label: "Academic Year" },
      { key: "report_data", label: "Report Data", type: "textarea" },
      { key: "summary", label: "Summary", type: "textarea" },
      { key: "total_students", label: "Total Students", type: "number" },
      { key: "total_teachers", label: "Total Teachers" },
      { key: "average_score", label: "Average Score", type: "number" },
      { key: "generated_by", label: "Generated By" },
      { key: "file_url", label: "File Url" },
    ],
  },
  "grade-trends": {
    key: "grade-trends",
    icon: ChartBarIcon,
    label: "Grade Trend Report",
    endpoint: "grade-trends",
    titleField: "title",
    subtitleField: "trend_type",
    fields: [
      { key: "title", label: "Title" },
      {
        key: "trend_type",
        label: "Trend Type",
        type: "select",
        options: [
          ["over_time", "Over Time"],
          ["by_subject", "By Subject"],
          ["by_class", "By Class"],
          ["by_student", "By Student"],
          ["comparison", "Comparison"],
        ],
      },
      { key: "academic_year", label: "Academic Year" },
      { key: "grade", label: "Grade" },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "date_from", label: "Date From", type: "date" },
      { key: "date_to", label: "Date To", type: "date" },
      { key: "report_data", label: "Report Data", type: "textarea" },
      { key: "summary", label: "Summary", type: "textarea" },
    ],
  },
  "k-p-i-definition": {
    key: "k-p-i-definition",
    icon: ChartBarIcon,
    label: "K P I Definition",
    endpoint: "k-p-i-definition",
    titleField: "name",
    subtitleField: "category",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: [
          ["academic", "Academic"],
          ["financial", "Financial"],
          ["operations", "Operations"],
          ["student_life", "Student Life"],
          ["staff", "Staff"],
        ],
      },
      {
        key: "data_type",
        label: "Data Type",
        type: "select",
        options: [
          ["number", "Number"],
          ["percentage", "Percentage"],
          ["currency", "Currency"],
          ["ratio", "Ratio"],
        ],
      },
      { key: "target_value", label: "Target Value", type: "number" },
      { key: "min_value", label: "Min Value", type: "number" },
      { key: "max_value", label: "Max Value", type: "number" },
      { key: "warning_threshold", label: "Warning Threshold", type: "number" },
      {
        key: "critical_threshold",
        label: "Critical Threshold",
        type: "number",
      },
      { key: "formula", label: "Formula" },
      { key: "data_source", label: "Data Source", type: "textarea" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "k-p-i-value": {
    key: "k-p-i-value",
    icon: ChartBarIcon,
    label: "K P I Value",
    endpoint: "k-p-i-value",
    titleField: "kpi",
    fields: [
      { key: "kpi", label: "Kpi" },
      { key: "date", label: "Date", type: "date" },
      { key: "value", label: "Value", type: "number" },
      { key: "target_met", label: "Target Met", type: "bool" },
      { key: "trend", label: "Trend" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "report-access-control": {
    key: "report-access-control",
    icon: ChartBarIcon,
    label: "Report Access Control",
    endpoint: "report-access-control",
    titleField: "report_type",
    subtitleField: "access_level",
    fields: [
      { key: "report_type", label: "Report Type" },
      { key: "role", label: "Role" },
      {
        key: "access_level",
        label: "Access Level",
        type: "select",
        options: [
          ["view", "View"],
          ["edit", "Edit"],
          ["admin", "Admin"],
        ],
      },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "expires_at", label: "Expires At", type: "date" },
      { key: "granted_by", label: "Granted By" },
    ],
  },
  "report-access-log": {
    key: "report-access-log",
    icon: ChartBarIcon,
    label: "Report Access Log",
    endpoint: "report-access-log",
    titleField: "report_history",
    fields: [
      { key: "report_history", label: "Report History" },
      {
        key: "access_type",
        label: "Access Type",
        type: "select",
        options: [
          ["view", "View"],
          ["download", "Download"],
          ["share", "Share"],
          ["export", "Export"],
        ],
      },
      { key: "ip_address", label: "Ip Address" },
      { key: "accessed_at", label: "Accessed At", type: "date" },
    ],
  },
  "report-alert": {
    key: "report-alert",
    icon: ChartBarIcon,
    label: "Report Alert",
    endpoint: "report-alert",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "alert_type",
        label: "Alert Type",
        type: "select",
        options: [
          ["threshold", "Threshold"],
          ["trend", "Trend"],
          ["anomaly", "Anomaly"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["triggered", "Triggered"],
          ["acknowledged", "Acknowledged"],
        ],
      },
      { key: "metric", label: "Metric" },
      { key: "threshold_value", label: "Threshold Value", type: "number" },
      { key: "notify_users", label: "Notify Users" },
      { key: "last_triggered_at", label: "Last Triggered At", type: "date" },
      { key: "trigger_count", label: "Trigger Count", type: "number" },
    ],
  },
  "report-analytics": {
    key: "report-analytics",
    icon: ChartBarIcon,
    label: "Report Analytics",
    endpoint: "report-analytics",
    titleField: "date",
    fields: [
      { key: "date", label: "Date", type: "date" },
      {
        key: "total_reports_generated",
        label: "Total Reports Generated",
        type: "number",
      },
      {
        key: "total_reports_viewed",
        label: "Total Reports Viewed",
        type: "number",
      },
      {
        key: "total_reports_exported",
        label: "Total Reports Exported",
        type: "number",
      },
      {
        key: "by_type_breakdown",
        label: "By Type Breakdown",
        type: "textarea",
      },
      { key: "top_reports", label: "Top Reports", type: "textarea" },
      { key: "active_users", label: "Active Users", type: "number" },
      {
        key: "avg_generation_time",
        label: "Avg Generation Time",
        type: "number",
      },
    ],
  },
  "report-bookmark": {
    key: "report-bookmark",
    icon: ChartBarIcon,
    label: "Report Bookmark",
    endpoint: "report-bookmark",
    titleField: "name",
    subtitleField: "report_type",
    fields: [
      { key: "report_type", label: "Report Type" },
      { key: "report_id", label: "Report Id" },
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "saved_filters", label: "Saved Filters", type: "textarea" },
      { key: "sort_order", label: "Sort Order", type: "number" },
    ],
  },
  "report-comment": {
    key: "report-comment",
    icon: ChartBarIcon,
    label: "Report Comment",
    endpoint: "report-comment",
    titleField: "report_history",
    fields: [
      { key: "report_history", label: "Report History" },
      { key: "comment", label: "Comment" },
      { key: "parent", label: "Parent" },
    ],
  },
  "report-comparison": {
    key: "report-comparison",
    icon: ChartBarIcon,
    label: "Report Comparison",
    endpoint: "report-comparison",
    titleField: "name",
    subtitleField: "report_type",
    fields: [
      { key: "name", label: "Name" },
      { key: "report_type", label: "Report Type" },
      { key: "period_a_start", label: "Period A Start" },
      { key: "period_a_end", label: "Period A End" },
      { key: "period_b_start", label: "Period B Start" },
      { key: "period_b_end", label: "Period B End" },
      { key: "comparison_data", label: "Comparison Data", type: "textarea" },
      { key: "highlights", label: "Highlights", type: "textarea" },
      { key: "created_by", label: "Created By" },
    ],
  },
  "report-data-cache": {
    key: "report-data-cache",
    icon: ChartBarIcon,
    label: "Report Data Cache",
    endpoint: "report-data-cache",
    titleField: "report_type",
    subtitleField: "cache_key",
    fields: [
      { key: "cache_key", label: "Cache Key" },
      { key: "report_type", label: "Report Type" },
      { key: "data", label: "Data", type: "textarea" },
      { key: "data_hash", label: "Data Hash" },
      { key: "expires_at", label: "Expires At", type: "date" },
      { key: "hit_count", label: "Hit Count", type: "number" },
      { key: "last_hit_at", label: "Last Hit At", type: "date" },
    ],
  },
  "report-data-source": {
    key: "report-data-source",
    icon: ChartBarIcon,
    label: "Report Data Source",
    endpoint: "report-data-source",
    titleField: "name",
    subtitleField: "source_type",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "source_type",
        label: "Source Type",
        type: "select",
        options: [
          ["model", "Model"],
          ["view", "View"],
          ["api", "Api"],
          ["sql", "Sql"],
        ],
      },
      { key: "model_path", label: "Model Path" },
      { key: "view_name", label: "View Name" },
      { key: "api_url", label: "Api Url" },
      { key: "sql_query", label: "Sql Query", type: "textarea" },
      { key: "fields", label: "Fields", type: "textarea" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "last_synced_at", label: "Last Synced At", type: "date" },
    ],
  },
  "report-email-delivery": {
    key: "report-email-delivery",
    icon: ChartBarIcon,
    label: "Report Email Delivery",
    endpoint: "report-email-delivery",
    titleField: "subject",
    subtitleField: "status",
    fields: [
      { key: "report_history", label: "Report History" },
      { key: "recipient", label: "Recipient" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["sent", "Sent"],
          ["delivered", "Delivered"],
          ["failed", "Failed"],
          ["bounced", "Bounced"],
        ],
      },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "message", label: "Message", type: "textarea" },
      { key: "sent_at", label: "Sent At", type: "date" },
      { key: "delivered_at", label: "Delivered At", type: "date" },
      { key: "error_message", label: "Error Message", type: "textarea" },
    ],
  },
  "report-export": {
    key: "report-export",
    icon: ChartBarIcon,
    label: "Report Export",
    endpoint: "report-export",
    titleField: "report_type",
    subtitleField: "status",
    fields: [
      { key: "report_type", label: "Report Type" },
      {
        key: "format",
        label: "Format",
        type: "select",
        options: [
          ["pdf", "Pdf"],
          ["csv", "Csv"],
          ["excel", "Excel"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["generating", "Generating"],
          ["completed", "Completed"],
          ["failed", "Failed"],
        ],
      },
      { key: "filters", label: "Filters", type: "textarea" },
      { key: "date_from", label: "Date From", type: "date" },
      { key: "date_to", label: "Date To", type: "date" },
      { key: "file", label: "File" },
      { key: "record_count", label: "Record Count", type: "number" },
      { key: "requested_by", label: "Requested By" },
      { key: "requested_at", label: "Requested At", type: "date" },
      { key: "completed_at", label: "Completed At", type: "date" },
    ],
  },
  "report-favorite": {
    key: "report-favorite",
    icon: ChartBarIcon,
    label: "Report Favorite",
    endpoint: "report-favorite",
    titleField: "report_type",
    fields: [
      { key: "report_type", label: "Report Type" },
      { key: "report_name", label: "Report Name" },
      { key: "report_config", label: "Report Config" },
    ],
  },
  "report-folder": {
    key: "report-folder",
    icon: ChartBarIcon,
    label: "Report Folder",
    endpoint: "report-folder",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "parent", label: "Parent" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "owner", label: "Owner" },
      { key: "is_shared", label: "Is Shared", type: "bool" },
    ],
  },
  "report-folder-item": {
    key: "report-folder-item",
    icon: ChartBarIcon,
    label: "Report Folder Item",
    endpoint: "report-folder-item",
    titleField: "name",
    subtitleField: "item_type",
    fields: [
      { key: "folder", label: "Folder" },
      {
        key: "item_type",
        label: "Item Type",
        type: "select",
        options: [
          ["report", "Report"],
          ["folder", "Folder"],
          ["bookmark", "Bookmark"],
        ],
      },
      { key: "item_id", label: "Item Id" },
      { key: "name", label: "Name" },
      { key: "sort_order", label: "Sort Order", type: "number" },
      { key: "added_at", label: "Added At", type: "date" },
    ],
  },
  "report-history": {
    key: "report-history",
    icon: ChartBarIcon,
    label: "Report History",
    endpoint: "report-history",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "report_type", label: "Report Type" },
      { key: "title", label: "Title" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["generating", "Generating"],
          ["completed", "Completed"],
          ["failed", "Failed"],
        ],
      },
      { key: "file", label: "File" },
      { key: "file_size_bytes", label: "File Size Bytes", type: "number" },
      { key: "format", label: "Format" },
      { key: "filters_applied", label: "Filters Applied", type: "textarea" },
      { key: "date_from", label: "Date From", type: "date" },
      { key: "date_to", label: "Date To", type: "date" },
      { key: "record_count", label: "Record Count", type: "number" },
      { key: "generated_by", label: "Generated By" },
    ],
  },
  "report-insight": {
    key: "report-insight",
    icon: ChartBarIcon,
    label: "Report Insight",
    endpoint: "report-insight",
    titleField: "title",
    subtitleField: "insight_type",
    fields: [
      {
        key: "insight_type",
        label: "Insight Type",
        type: "select",
        options: [
          ["trend", "Trend"],
          ["anomaly", "Anomaly"],
          ["recommendation", "Recommendation"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "metric", label: "Metric" },
      { key: "value", label: "Value", type: "number" },
      { key: "change_percentage", label: "Change Percentage" },
      { key: "priority", label: "Priority" },
      { key: "is_read", label: "Is Read", type: "bool" },
      { key: "generated_at", label: "Generated At", type: "date" },
    ],
  },
  "report-schedule": {
    key: "report-schedule",
    icon: ChartBarIcon,
    label: "Report Schedule",
    endpoint: "report-schedule",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      { key: "report_type", label: "Report Type" },
      {
        key: "frequency",
        label: "Frequency",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["monthly", "Monthly"],
          ["quarterly", "Quarterly"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["paused", "Paused"],
          ["disabled", "Disabled"],
        ],
      },
      { key: "day_of_week", label: "Day Of Week" },
      { key: "day_of_month", label: "Day Of Month" },
      { key: "time_of_day", label: "Time Of Day" },
      { key: "recipients", label: "Recipients", type: "textarea" },
      { key: "email_delivery", label: "Email Delivery", type: "bool" },
      {
        key: "format",
        label: "Format",
        type: "select",
        options: [
          ["pdf", "Pdf"],
          ["csv", "Csv"],
          ["excel", "Excel"],
        ],
      },
      { key: "filters", label: "Filters", type: "textarea" },
      { key: "last_generated", label: "Last Generated", type: "date" },
    ],
  },
  "report-schedule-delivery": {
    key: "report-schedule-delivery",
    icon: ChartBarIcon,
    label: "Report Schedule Delivery",
    endpoint: "report-schedule-delivery",
    titleField: "schedule",
    subtitleField: "status",
    fields: [
      { key: "schedule", label: "Schedule" },
      { key: "report_history", label: "Report History" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["sent", "Sent"],
          ["failed", "Failed"],
        ],
      },
      { key: "recipient_count", label: "Recipient Count", type: "number" },
      { key: "sent_at", label: "Sent At", type: "date" },
      { key: "error_message", label: "Error Message", type: "textarea" },
    ],
  },
  "report-subscription": {
    key: "report-subscription",
    icon: ChartBarIcon,
    label: "Report Subscription",
    endpoint: "report-subscription",
    titleField: "report_type",
    subtitleField: "update_type",
    fields: [
      { key: "report_type", label: "Report Type" },
      {
        key: "update_type",
        label: "Update Type",
        type: "select",
        options: [
          ["new_data", "New Data"],
          ["threshold", "Threshold"],
          ["scheduled", "Scheduled"],
        ],
      },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "last_notified_at", label: "Last Notified At", type: "date" },
    ],
  },
  "report-version": {
    key: "report-version",
    icon: ChartBarIcon,
    label: "Report Version",
    endpoint: "report-version",
    titleField: "template",
    subtitleField: "version_number",
    fields: [
      { key: "template", label: "Template" },
      { key: "version_number", label: "Version Number", type: "number" },
      { key: "config_snapshot", label: "Config Snapshot", type: "textarea" },
      { key: "is_current", label: "Is Current", type: "bool" },
      { key: "created_by", label: "Created By" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  scheduled: {
    key: "scheduled",
    icon: ChartBarIcon,
    label: "Scheduled Report",
    endpoint: "scheduled",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "title", label: "Title" },
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: [
          ["academic", "Academic"],
          ["attendance", "Attendance"],
          ["fee", "Fee"],
          ["enrollment", "Enrollment"],
          ["discipline", "Discipline"],
          ["health", "Health"],
          ["custom", "Custom"],
        ],
      },
      {
        key: "frequency",
        label: "Frequency",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["biweekly", "Biweekly"],
          ["monthly", "Monthly"],
          ["quarterly", "Quarterly"],
          ["semi_annual", "Semi Annual"],
          ["annual", "Annual"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["paused", "Paused"],
          ["completed", "Completed"],
        ],
      },
      {
        key: "delivery_method",
        label: "Delivery Method",
        type: "select",
        options: [
          ["email", "Email"],
          ["dashboard", "Dashboard"],
          ["both", "Both"],
        ],
      },
      { key: "recipients", label: "Recipients", type: "textarea" },
      { key: "config", label: "Config", type: "textarea" },
      { key: "last_generated", label: "Last Generated", type: "date" },
      { key: "next_generation", label: "Next Generation", type: "date" },
      { key: "created_by", label: "Created By" },
    ],
  },
  shares: {
    key: "shares",
    icon: ChartBarIcon,
    label: "Report Share",
    endpoint: "shares",
    titleField: "title",
    subtitleField: "access_level",
    fields: [
      { key: "title", label: "Title" },
      {
        key: "share_type",
        label: "Share Type",
        type: "select",
        options: [
          ["student", "Student"],
          ["parent", "Parent"],
          ["teacher", "Teacher"],
          ["admin", "Admin"],
          ["external", "External"],
        ],
      },
      {
        key: "access_level",
        label: "Access Level",
        type: "select",
        options: [
          ["view", "View"],
          ["download", "Download"],
          ["edit", "Edit"],
        ],
      },
      { key: "report_url", label: "Report Url" },
      { key: "report_data", label: "Report Data", type: "textarea" },
      { key: "shared_with", label: "Shared With", type: "textarea" },
      { key: "expires_at", label: "Expires At", type: "date" },
      { key: "password_protected", label: "Password Protected", type: "bool" },
      { key: "access_password", label: "Access Password" },
      { key: "view_count", label: "View Count", type: "number" },
      { key: "shared_by", label: "Shared By" },
    ],
  },
  "student-progress": {
    key: "student-progress",
    icon: ChartBarIcon,
    label: "Student Progress Tracking",
    endpoint: "student-progress",
    titleField: "title",
    subtitleField: "progress_type",
    fields: [
      { key: "student", label: "Student" },
      { key: "title", label: "Title" },
      {
        key: "progress_type",
        label: "Progress Type",
        type: "select",
        options: [
          ["academic", "Academic"],
          ["behavioral", "Behavioral"],
          ["attendance", "Attendance"],
          ["overall", "Overall"],
        ],
      },
      { key: "academic_year", label: "Academic Year" },
      { key: "date_from", label: "Date From", type: "date" },
      { key: "date_to", label: "Date To", type: "date" },
      { key: "report_data", label: "Report Data", type: "textarea" },
      { key: "summary", label: "Summary", type: "textarea" },
      { key: "strengths", label: "Strengths", type: "textarea" },
      {
        key: "areas_for_improvement",
        label: "Areas For Improvement",
        type: "textarea",
      },
    ],
  },
  "teacher-performance": {
    key: "teacher-performance",
    icon: ChartBarIcon,
    label: "Teacher Performance Report",
    endpoint: "teacher-performance",
    titleField: "title",
    fields: [
      { key: "title", label: "Title" },
      { key: "academic_year", label: "Academic Year" },
      { key: "teacher", label: "Teacher" },
      { key: "report_data", label: "Report Data", type: "textarea" },
      { key: "summary", label: "Summary", type: "textarea" },
      {
        key: "average_class_score",
        label: "Average Class Score",
        type: "number",
      },
      { key: "student_satisfaction", label: "Student Satisfaction" },
      { key: "attendance_rate", label: "Attendance Rate", type: "number" },
      { key: "classes_taught", label: "Classes Taught" },
      { key: "generated_by", label: "Generated By" },
    ],
  },
  templates: {
    key: "templates",
    icon: ChartBarIcon,
    label: "Report Template",
    endpoint: "templates",
    titleField: "name",
    subtitleField: "report_type",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: [
          ["academic", "Academic"],
          ["attendance", "Attendance"],
          ["fee", "Fee"],
          ["enrollment", "Enrollment"],
          ["discipline", "Discipline"],
          ["health", "Health"],
          ["custom", "Custom"],
        ],
      },
      { key: "config", label: "Config", type: "textarea" },
      { key: "columns", label: "Columns", type: "textarea" },
      { key: "filters", label: "Filters", type: "textarea" },
      { key: "is_public", label: "Is Public", type: "bool" },
      { key: "created_by", label: "Created By" },
    ],
  },
  "year-over-year": {
    key: "year-over-year",
    icon: ChartBarIcon,
    label: "Year Over Year Report",
    endpoint: "year-over-year",
    titleField: "title",
    fields: [
      { key: "title", label: "Title" },
      { key: "academic_year_from", label: "Academic Year From" },
      { key: "academic_year_to", label: "Academic Year To" },
      { key: "report_data", label: "Report Data", type: "textarea" },
      { key: "summary", label: "Summary", type: "textarea" },
      { key: "enrollment_change", label: "Enrollment Change", type: "number" },
      {
        key: "performance_change",
        label: "Performance Change",
        type: "number",
      },
      { key: "attendance_change", label: "Attendance Change", type: "number" },
      { key: "generated_by", label: "Generated By" },
    ],
  },
};

const TABS = Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({
  key,
  label: cfg.label,
  icon: ChartBarIcon,
}));

export default function ReportingCenterPage() {
  useTitle("Reporting Center");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Reporting Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Dashboards, custom reports, KPIs, schedules, exports, insights and analytics
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
            leftIcon={<ChartBarIcon className="h-4 w-4" />}
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
        basePath="/reporting"
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
