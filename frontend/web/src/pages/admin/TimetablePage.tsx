/**
 * Timetable Center — full-surface admin page for the timetable module.
 *
 * Overview tab (weekly class grid) + 40 entity tabs (config-driven via
 * EntitySection): periods, slots, events, exams, calendars, bookings,
 * templates, preferences, approvals, changes, closures, class groups,
 * lesson plans, validation, resources, analytics and more.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button, Select, SkeletonCard } from "../../components/common";
import { useTitle } from "../../hooks";
import { useClassrooms, useCurrentAcademicYear } from "../../api/hooks";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { MagnifyingGlassIcon, ShieldExclamationIcon } from "@heroicons/react/24/outline";
import {
  CalendarDaysIcon,
  ClockIcon,
  BookOpenIcon,
  AcademicCapIcon,
  BuildingOfficeIcon,
  ChartBarIcon,
  ClipboardDocumentCheckIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  PresentationChartBarIcon,
  ReceiptPercentIcon,
  ShieldCheckIcon,
  TableCellsIcon,
  TicketIcon,
  UsersIcon,
  WrenchScrewdriverIcon,
  BellAlertIcon,
  LockClosedIcon,
  PuzzlePieceIcon,
  QueueListIcon,
  ScaleIcon,
  ServerIcon,
  StarIcon,
  ArrowPathIcon,
  CircleStackIcon,
  IdentificationIcon,
  Square2StackIcon,
  TrophyIcon,
  UserGroupIcon,
} from "@heroicons/react/24/outline";

// ─── Shared option sets ──────────────────────────────────────────────────────

const DAYS = [
  ["0", "Monday"],
  ["1", "Tuesday"],
  ["2", "Wednesday"],
  ["3", "Thursday"],
  ["4", "Friday"],
  ["5", "Saturday"],
] as [string, string][];

const EVENT_TYPES = [
  ["holiday", "Holiday"],
  ["exam", "Exam"],
  ["sports", "Sports"],
  ["cultural", "Cultural"],
  ["ptm", "PTM"],
  ["trip", "Trip"],
  ["other", "Other"],
] as [string, string][];

const STATUS_PCC = [
  ["pending", "Pending"],
  ["confirmed", "Confirmed"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const CONFLICT_TYPES = [
  ["teacher_double_book", "Teacher Double Book"],
  ["room_double_book", "Room Double Book"],
  ["student_double_book", "Student Double Book"],
  ["teacher_unavailable", "Teacher Unavailable"],
  ["room_unavailable", "Room Unavailable"],
  ["other", "Other"],
] as [string, string][];

const CONFLICT_STATUS = [
  ["open", "Open"],
  ["resolved", "Resolved"],
  ["ignored", "Ignored"],
] as [string, string][];

const EXAM_TYPES = [
  ["midterm", "Midterm"],
  ["final", "Final"],
  ["quiz", "Quiz"],
  ["practical", "Practical"],
  ["oral", "Oral"],
  ["other", "Other"],
] as [string, string][];

const EXAM_STATUS = [
  ["draft", "Draft"],
  ["published", "Published"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const CALENDAR_TYPES = [
  ["term_start", "Term Start"],
  ["term_end", "Term End"],
  ["holiday", "Holiday"],
  ["vacation", "Vacation"],
  ["exam_period", "Exam Period"],
  ["registration", "Registration"],
  ["orientation", "Orientation"],
  ["graduation", "Graduation"],
  ["other", "Other"],
] as [string, string][];

const BOOKING_TYPES = [
  ["class", "Class"],
  ["exam", "Exam"],
  ["event", "Event"],
  ["meeting", "Meeting"],
  ["training", "Training"],
  ["other", "Other"],
] as [string, string][];

const PREFERENCE_TYPES = [
  ["preferred", "Preferred"],
  ["unavailable", "Unavailable"],
  ["preferred_day", "Preferred Day"],
  ["preferred_time", "Preferred Time"],
] as [string, string][];

const APPROVAL_STATUS = [
  ["draft", "Draft"],
  ["pending_approval", "Pending Approval"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["published", "Published"],
] as [string, string][];

const CHANGE_TYPES = [
  ["room_change", "Room Change"],
  ["time_change", "Time Change"],
  ["teacher_change", "Teacher Change"],
  ["cancellation", "Cancellation"],
  ["rescheduling", "Rescheduling"],
  ["other", "Other"],
] as [string, string][];

const ACTIVITY_TYPES = [
  ["sports", "Sports"],
  ["arts", "Arts"],
  ["music", "Music"],
  ["drama", "Drama"],
  ["debate", "Debate"],
  ["club", "Club"],
  ["other", "Other"],
] as [string, string][];

const REPORT_TYPES = [
  ["teacher_load", "Teacher Load"],
  ["room_utilization", "Room Utilization"],
  ["subject_distribution", "Subject Distribution"],
  ["conflict_summary", "Conflict Summary"],
  ["general", "General"],
] as [string, string][];

const CLOSURE_TYPES = [
  ["public_holiday", "Public Holiday"],
  ["school_holiday", "School Holiday"],
  ["weather", "Weather"],
  ["emergency", "Emergency"],
  ["maintenance", "Maintenance"],
  ["other", "Other"],
] as [string, string][];

const DAY_TYPES = [
  ["regular", "Regular"],
  ["early", "Early"],
  ["late", "Late"],
  ["special", "Special"],
] as [string, string][];

const EXAM_ATT_STATUS = [
  ["present", "Present"],
  ["absent", "Absent"],
  ["late", "Late"],
  ["excused", "Excused"],
] as [string, string][];

const SESSION_STATUS = [
  ["upcoming", "Upcoming"],
  ["active", "Active"],
  ["completed", "Completed"],
] as [string, string][];

const SUB_STATUS = [
  ["scheduled", "Scheduled"],
  ["confirmed", "Confirmed"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const RULE_TYPES = [
  ["teacher_load", "Teacher Load"],
  ["room_capacity", "Room Capacity"],
  ["spacing", "Subject Spacing"],
  ["consecutive", "Consecutive Periods"],
  ["break", "Break Required"],
  ["grade_conflict", "Grade Conflict"],
  ["teacher_conflict", "Teacher Conflict"],
  ["custom", "Custom"],
] as [string, string][];

const SEVERITIES = [
  ["error", "Error"],
  ["warning", "Warning"],
  ["info", "Info"],
] as [string, string][];

const RESOURCE_TYPES = [
  ["projector", "Projector"],
  ["lab", "Lab"],
  ["computer", "Computer"],
  ["library", "Library"],
  ["auditorium", "Auditorium"],
  ["sports", "Sports"],
  ["other", "Other"],
] as [string, string][];

const RESOURCE_BOOKING_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["denied", "Denied"],
  ["cancelled", "Cancelled"],
  ["completed", "Completed"],
] as [string, string][];

const CHANGE_REQUEST_TYPES = [
  ["swap", "Swap"],
  ["room", "Room Change"],
  ["time", "Time Change"],
  ["teacher", "Teacher Change"],
  ["cancel", "Cancellation"],
  ["extra", "Extra Class"],
] as [string, string][];

const CHANGE_REQUEST_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["denied", "Denied"],
  ["implemented", "Implemented"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const SUB_STATUS_SHORT = [
  ["pending", "Pending"],
  ["confirmed", "Confirmed"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

// ─── Entity configs (40 tabs) ────────────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  periods: {
    key: "periods",
    label: "Period",
    icon: ClockIcon,
    endpoint: "periods",
    titleField: "name",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "period_number", label: "Period #", type: "number", subtitle: true },
      { key: "start_time", label: "Start", card: true },
      { key: "end_time", label: "End", card: true },
      { key: "is_break", label: "Break", type: "bool", badge: true },
    ],
    searchKeys: ["name", "period_number"],
  },
  slots: {
    key: "slots",
    label: "Timetable Slot",
    icon: TableCellsIcon,
    endpoint: "slots",
    titleField: "subject_name",
    subtitleField: "classroom_name",
    fields: [
      { key: "subject_name", label: "Subject", main: true, skipForm: true },
      { key: "classroom_name", label: "Classroom", subtitle: true, skipForm: true },
      { key: "classroom", label: "Classroom ID", skipForm: true },
      { key: "assignment", label: "Assignment ID", skipForm: true },
      { key: "period_name", label: "Period", card: true, skipForm: true },
      { key: "period", label: "Period ID", card: true },
      { key: "day_of_week", label: "Day", type: "select", options: DAYS, badge: true },
      { key: "teacher_name", label: "Teacher", card: true, skipForm: true },
      { key: "room", label: "Room", card: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "effective_from", label: "Effective From", type: "date", card: true },
      { key: "effective_to", label: "Effective To", type: "date", card: true },
    ],
    searchKeys: ["subject_name", "classroom_name", "teacher_name", "room", "period_name"],
  },
  events: {
    key: "events",
    label: "School Event",
    icon: CalendarDaysIcon,
    endpoint: "events",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "event_type", label: "Type", type: "select", options: EVENT_TYPES, badge: true },
      { key: "start_date", label: "Start Date", type: "date", card: true },
      { key: "end_date", label: "End Date", type: "date", card: true },
      { key: "start_time", label: "Start Time", card: true },
      { key: "end_time", label: "End Time", card: true },
      { key: "venue", label: "Venue", card: true },
      { key: "is_school_wide", label: "School-wide", type: "bool", card: true },
      { key: "target_grades", label: "Target Grades", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
    ],
    searchKeys: ["title", "event_type", "venue"],
  },
  "teacher-timetables": {
    key: "teacher-timetables",
    label: "Teacher Timetable",
    icon: UserGroupIcon,
    endpoint: "teacher-timetables",
    titleField: "teacher_name",
    subtitleField: "classroom_name",
    fields: [
      { key: "teacher_name", label: "Teacher", main: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", skipForm: true },
      { key: "classroom_name", label: "Classroom", subtitle: true, skipForm: true },
      { key: "classroom", label: "Classroom ID", skipForm: true },
      { key: "subject_name", label: "Subject", card: true, skipForm: true },
      { key: "subject", label: "Subject ID", card: true },
      { key: "period_name", label: "Period", card: true, skipForm: true },
      { key: "period", label: "Period ID", card: true },
      { key: "day_of_week", label: "Day", type: "select", options: DAYS, badge: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "total_hours_per_week", label: "Hours/Week", type: "number", card: true },
      { key: "slot", label: "Slot ID", card: true },
    ],
    searchKeys: ["teacher_name", "classroom_name", "subject_name"],
  },
  substitutes: {
    key: "substitutes",
    label: "Substitute Teacher",
    icon: ArrowPathIcon,
    endpoint: "substitutes",
    titleField: "substitute_teacher",
    subtitleField: "date",
    fields: [
      { key: "substitute_teacher", label: "Substitute", main: true },
      { key: "original_teacher", label: "Original Teacher", card: true },
      { key: "date", label: "Date", type: "date", subtitle: true },
      { key: "period_name", label: "Period", card: true, skipForm: true },
      { key: "period", label: "Period ID", card: true },
      { key: "slot", label: "Slot ID", card: true },
      { key: "status", label: "Status", type: "select", options: SUB_STATUS, badge: true },
      { key: "reason", label: "Reason", type: "textarea", full: true, card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["substitute_teacher", "original_teacher", "reason", "status"],
  },
  conflicts: {
    key: "conflicts",
    label: "Conflict",
    icon: ExclamationTriangleIcon,
    endpoint: "conflicts",
    titleField: "conflict_type",
    subtitleField: "description",
    fields: [
      {
        key: "conflict_type",
        label: "Type",
        type: "select",
        options: CONFLICT_TYPES,
        main: true,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        subtitle: true,
        type: "textarea",
        full: true,
        card: true,
      },
      { key: "slot1", label: "Slot 1", card: true },
      { key: "slot2", label: "Slot 2", card: true },
      { key: "status", label: "Status", type: "select", options: CONFLICT_STATUS, badge: true },
      {
        key: "resolution_notes",
        label: "Resolution Notes",
        type: "textarea",
        full: true,
        card: true,
      },
      { key: "resolved_by_name", label: "Resolved By", card: true, skipForm: true },
      { key: "resolved_by", label: "Resolved By ID", skipForm: true },
      { key: "resolved_at", label: "Resolved At", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["conflict_type", "description", "status"],
  },
  "exam-schedules": {
    key: "exam-schedules",
    label: "Exam Schedule",
    icon: ReceiptPercentIcon,
    endpoint: "exam-schedules",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "exam_type", label: "Exam Type", type: "select", options: EXAM_TYPES, badge: true },
      { key: "status", label: "Status", type: "select", options: EXAM_STATUS, badge: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "start_date", label: "Start Date", type: "date", card: true },
      { key: "end_date", label: "End Date", type: "date", card: true },
      { key: "instructions", label: "Instructions", type: "textarea", full: true, card: true },
      { key: "published_at", label: "Published", type: "datetime", card: true, skipForm: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
    ],
    searchKeys: ["title", "exam_type", "status"],
  },
  "exam-entries": {
    key: "exam-entries",
    label: "Exam Entry",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "exam-entries",
    titleField: "subject_name",
    subtitleField: "classroom_name",
    fields: [
      { key: "subject_name", label: "Subject", main: true, skipForm: true },
      { key: "classroom_name", label: "Classroom", subtitle: true, skipForm: true },
      { key: "exam_schedule_title", label: "Schedule", card: true, skipForm: true },
      { key: "exam_schedule", label: "Schedule ID", card: true },
      { key: "classroom", label: "Classroom ID", skipForm: true },
      { key: "subject", label: "Subject ID", skipForm: true },
      { key: "exam_date", label: "Exam Date", type: "date", card: true },
      { key: "start_time", label: "Start", card: true },
      { key: "end_time", label: "End", card: true },
      { key: "room", label: "Room", card: true },
      { key: "invigilator_name", label: "Invigilator", card: true, skipForm: true },
      { key: "invigilator", label: "Invigilator ID", card: true },
      { key: "total_marks", label: "Total Marks", type: "number", card: true },
      { key: "passing_marks", label: "Passing Marks", type: "number", card: true },
    ],
    searchKeys: ["subject_name", "classroom_name", "exam_schedule_title", "room"],
  },
  "academic-calendar": {
    key: "academic-calendar",
    label: "Academic Calendar",
    icon: CalendarDaysIcon,
    endpoint: "academic-calendar",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "calendar_type", label: "Type", type: "select", options: CALENDAR_TYPES, badge: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "start_date", label: "Start Date", type: "date", card: true },
      { key: "end_date", label: "End Date", type: "date", card: true },
      { key: "is_school_wide", label: "School-wide", type: "bool", card: true },
      { key: "target_grades", label: "Target Grades", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["title", "calendar_type", "description"],
  },
  "room-bookings": {
    key: "room-bookings",
    label: "Room Booking",
    icon: BuildingOfficeIcon,
    endpoint: "room-bookings",
    titleField: "room_name",
    subtitleField: "purpose",
    fields: [
      { key: "room_name", label: "Room", main: true, skipForm: true },
      { key: "room", label: "Room ID", skipForm: true },
      {
        key: "purpose",
        label: "Purpose",
        subtitle: true,
        type: "textarea",
        full: true,
        card: true,
      },
      { key: "booking_type", label: "Type", type: "select", options: BOOKING_TYPES, badge: true },
      { key: "status", label: "Status", type: "select", options: STATUS_PCC, badge: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "start_time", label: "Start", card: true },
      { key: "end_time", label: "End", card: true },
      { key: "attendees_count", label: "Attendees", type: "number", card: true },
      { key: "booked_by_name", label: "Booked By", card: true, skipForm: true },
      { key: "booked_by", label: "Booked By ID", card: true },
      { key: "approved_by_name", label: "Approved By", card: true, skipForm: true },
      { key: "approved_by", label: "Approved By ID", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["room_name", "purpose", "booking_type", "status"],
  },
  templates: {
    key: "templates",
    label: "Timetable Template",
    icon: PuzzlePieceIcon,
    endpoint: "templates",
    titleField: "name",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "description",
        label: "Description",
        subtitle: true,
        type: "textarea",
        full: true,
        card: true,
      },
      { key: "grade", label: "Grade", card: true },
      { key: "periods_per_day", label: "Periods/Day", type: "number", card: true },
      { key: "working_days", label: "Working Days", type: "number", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
    ],
    searchKeys: ["name", "description", "grade"],
  },
  "template-slots": {
    key: "template-slots",
    label: "Template Slot",
    icon: Square2StackIcon,
    endpoint: "template-slots",
    titleField: "subject_name",
    subtitleField: "day_name",
    fields: [
      { key: "subject_name", label: "Subject", main: true, skipForm: true },
      { key: "subject", label: "Subject ID", skipForm: true },
      { key: "day_name", label: "Day", subtitle: true, skipForm: true },
      { key: "day_of_week", label: "Day #", type: "select", options: DAYS, card: true },
      { key: "period_name", label: "Period", card: true, skipForm: true },
      { key: "period", label: "Period ID", card: true },
      { key: "template", label: "Template ID", card: true },
      { key: "room", label: "Room", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["subject_name", "day_name", "room"],
  },
  preferences: {
    key: "preferences",
    label: "Teacher Preference",
    icon: StarIcon,
    endpoint: "preferences",
    titleField: "teacher_name",
    fields: [
      { key: "teacher_name", label: "Teacher", main: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", skipForm: true },
      {
        key: "preference_type",
        label: "Type",
        type: "select",
        options: PREFERENCE_TYPES,
        badge: true,
      },
      { key: "day_of_week", label: "Day", type: "select", options: DAYS, card: true },
      { key: "period_name", label: "Period", card: true, skipForm: true },
      { key: "period", label: "Period ID", card: true },
      { key: "is_recurring", label: "Recurring", type: "bool", card: true },
      { key: "effective_from", label: "Effective From", type: "date", card: true },
      { key: "effective_to", label: "Effective To", type: "date", card: true },
      { key: "reason", label: "Reason", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["teacher_name", "preference_type", "reason"],
  },
  approvals: {
    key: "approvals",
    label: "Timetable Approval",
    icon: ShieldCheckIcon,
    endpoint: "approvals",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "status", label: "Status", type: "select", options: APPROVAL_STATUS, badge: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "grade", label: "Grade", card: true },
      { key: "submitted_by", label: "Submitted By", card: true },
      { key: "submitted_at", label: "Submitted At", type: "datetime", card: true, skipForm: true },
      { key: "approved_by_name", label: "Approved By", card: true, skipForm: true },
      { key: "approved_by", label: "Approved By ID", card: true },
      { key: "approved_at", label: "Approved At", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["title", "status", "approved_by_name"],
  },
  changes: {
    key: "changes",
    label: "Timetable Change",
    icon: WrenchScrewdriverIcon,
    endpoint: "changes",
    titleField: "change_type",
    subtitleField: "reason",
    fields: [
      {
        key: "change_type",
        label: "Type",
        type: "select",
        options: CHANGE_TYPES,
        main: true,
        badge: true,
      },
      { key: "reason", label: "Reason", subtitle: true, type: "textarea", full: true, card: true },
      { key: "slot", label: "Slot ID", card: true },
      { key: "old_value", label: "Old Value", card: true },
      { key: "new_value", label: "New Value", card: true },
      { key: "effective_date", label: "Effective Date", type: "date", card: true },
      { key: "changed_by", label: "Changed By", card: true },
      { key: "notified", label: "Notified", type: "bool", badge: true },
    ],
    searchKeys: ["change_type", "reason", "old_value", "new_value"],
  },
  "co-curricular": {
    key: "co-curricular",
    label: "Co-Curricular",
    icon: TrophyIcon,
    endpoint: "co-curricular",
    titleField: "activity_name",
    fields: [
      { key: "activity_name", label: "Activity", main: true },
      { key: "activity_type", label: "Type", type: "select", options: ACTIVITY_TYPES, badge: true },
      { key: "instructor", label: "Instructor", card: true },
      { key: "day_of_week", label: "Day", type: "select", options: DAYS, card: true },
      { key: "start_time", label: "Start", card: true },
      { key: "end_time", label: "End", card: true },
      { key: "venue", label: "Venue", card: true },
      { key: "max_participants", label: "Max Participants", type: "number", card: true },
      { key: "target_grades", label: "Target Grades", card: true },
      { key: "is_mandatory", label: "Mandatory", type: "bool", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
    ],
    searchKeys: ["activity_name", "activity_type", "instructor", "venue"],
  },
  reports: {
    key: "reports",
    label: "Timetable Report",
    icon: PresentationChartBarIcon,
    endpoint: "reports",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "report_type", label: "Type", type: "select", options: REPORT_TYPES, badge: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "date_from", label: "From", type: "date", card: true },
      { key: "date_to", label: "To", type: "date", card: true },
      { key: "summary", label: "Summary", type: "textarea", full: true, card: true },
      { key: "generated_by", label: "Generated By", card: true },
      { key: "file_url", label: "File", card: true },
    ],
    searchKeys: ["title", "report_type", "summary"],
  },
  closures: {
    key: "closures",
    label: "School Closure",
    icon: LockClosedIcon,
    endpoint: "closures",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "closure_type", label: "Type", type: "select", options: CLOSURE_TYPES, badge: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "affects_all", label: "Affects All", type: "bool", card: true },
      { key: "target_grades", label: "Target Grades", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "notified", label: "Notified", type: "bool", badge: true },
    ],
    searchKeys: ["title", "closure_type", "description"],
  },
  "bell-schedule": {
    key: "bell-schedule",
    label: "Bell Schedule",
    icon: BellAlertIcon,
    endpoint: "bell-schedule",
    titleField: "name",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "day_type", label: "Day Type", type: "select", options: DAY_TYPES, badge: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "effective_from", label: "Effective From", type: "date", card: true },
      { key: "effective_until", label: "Effective Until", type: "date", card: true },
    ],
    searchKeys: ["name", "day_type"],
  },
  "bell-schedule-entry": {
    key: "bell-schedule-entry",
    label: "Bell Entry",
    icon: QueueListIcon,
    endpoint: "bell-schedule-entry",
    titleField: "bell_schedule_name",
    subtitleField: "period_name",
    fields: [
      { key: "bell_schedule_name", label: "Schedule", main: true, skipForm: true },
      { key: "bell_schedule", label: "Schedule ID", skipForm: true },
      { key: "period_name", label: "Period", subtitle: true, skipForm: true },
      { key: "period", label: "Period ID", card: true },
      { key: "start_time", label: "Start", card: true },
      { key: "end_time", label: "End", card: true },
      { key: "is_break", label: "Break", type: "bool", badge: true },
      { key: "break_name", label: "Break Name", card: true },
      { key: "sort_order", label: "Sort Order", type: "number", card: true },
    ],
    searchKeys: ["bell_schedule_name", "period_name", "break_name"],
  },
  "class-group": {
    key: "class-group",
    label: "Class Group",
    icon: UsersIcon,
    endpoint: "class-group",
    titleField: "grade_level",
    subtitleField: "section_name",
    toggleField: "is_active",
    fields: [
      { key: "grade_level", label: "Grade", main: true },
      { key: "section_name", label: "Section", subtitle: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "max_students", label: "Max Students", type: "number", card: true },
      { key: "current_students", label: "Current Students", type: "number", card: true },
      { key: "class_teacher_name", label: "Class Teacher", card: true, skipForm: true },
      { key: "class_teacher", label: "Class Teacher ID", card: true },
      { key: "homeroom", label: "Homeroom", card: true },
      { key: "subjects", label: "Subjects", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
    ],
    searchKeys: ["grade_level", "section_name", "class_teacher_name", "homeroom"],
  },
  "class-group-enrollment": {
    key: "class-group-enrollment",
    label: "Enrollment",
    icon: IdentificationIcon,
    endpoint: "class-group-enrollment",
    titleField: "student_name",
    subtitleField: "class_group_label",
    toggleField: "is_active",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "class_group_label", label: "Class Group", subtitle: true, skipForm: true },
      { key: "class_group", label: "Class Group ID", card: true },
      { key: "enrolled_date", label: "Enrolled", type: "date", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
    ],
    searchKeys: ["student_name", "class_group_label"],
  },
  "subject-teacher-assignment": {
    key: "subject-teacher-assignment",
    label: "Subject Assignment",
    icon: BookOpenIcon,
    endpoint: "subject-teacher-assignment",
    titleField: "subject_name",
    subtitleField: "class_group_label",
    toggleField: "is_active",
    fields: [
      { key: "subject_name", label: "Subject", main: true, skipForm: true },
      { key: "subject", label: "Subject ID", skipForm: true },
      { key: "class_group_label", label: "Class Group", subtitle: true, skipForm: true },
      { key: "class_group", label: "Class Group ID", card: true },
      { key: "teacher_name", label: "Teacher", card: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", card: true },
      { key: "subject_code", label: "Subject Code", card: true },
      { key: "periods_per_week", label: "Periods/Week", type: "number", card: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "semester", label: "Semester", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
    ],
    searchKeys: ["subject_name", "class_group_label", "teacher_name", "subject_code"],
  },
  "lesson-plan": {
    key: "lesson-plan",
    label: "Lesson Plan",
    icon: DocumentTextIcon,
    endpoint: "lesson-plan",
    titleField: "topic",
    subtitleField: "teacher_name",
    fields: [
      { key: "topic", label: "Topic", main: true },
      { key: "teacher_name", label: "Teacher", subtitle: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", skipForm: true },
      { key: "class_group_label", label: "Class Group", card: true, skipForm: true },
      { key: "class_group", label: "Class Group ID", card: true },
      { key: "subject_name", label: "Subject", card: true, skipForm: true },
      { key: "subject", label: "Subject ID", card: true },
      { key: "plan_date", label: "Date", type: "date", card: true },
      { key: "period_name", label: "Period", card: true, skipForm: true },
      { key: "period", label: "Period ID", card: true },
      { key: "timetable_slot", label: "Slot ID", card: true },
      {
        key: "learning_objectives",
        label: "Learning Objectives",
        type: "textarea",
        full: true,
        card: true,
      },
    ],
    searchKeys: ["topic", "teacher_name", "class_group_label", "subject_name"],
  },
  "exam-room-allocation": {
    key: "exam-room-allocation",
    label: "Exam Room Allocation",
    icon: BuildingOfficeIcon,
    endpoint: "exam-room-allocation",
    titleField: "room_name",
    subtitleField: "exam_schedule_title",
    fields: [
      { key: "room_name", label: "Room", main: true, skipForm: true },
      { key: "room", label: "Room ID", skipForm: true },
      { key: "exam_schedule_title", label: "Schedule", subtitle: true, skipForm: true },
      { key: "exam_schedule", label: "Schedule ID", card: true },
      { key: "seating_capacity", label: "Capacity", type: "number", card: true },
      { key: "students_allocated", label: "Students", type: "number", card: true },
      { key: "invigilator_name", label: "Invigilator", card: true, skipForm: true },
      { key: "invigilator", label: "Invigilator ID", card: true },
      { key: "co_invigilator_name", label: "Co-Invigilator", card: true, skipForm: true },
      { key: "co_invigilator", label: "Co-Invigilator ID", card: true },
      { key: "equipment_needed", label: "Equipment", card: true },
      { key: "seating_arrangement", label: "Seating Arrangement", type: "textarea", full: true },
    ],
    searchKeys: ["room_name", "exam_schedule_title", "invigilator_name"],
  },
  "seating-arrangement": {
    key: "seating-arrangement",
    label: "Seating Arrangement",
    icon: TableCellsIcon,
    endpoint: "seating-arrangement",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "room_allocation", label: "Room Allocation", card: true },
      { key: "seat_number", label: "Seat #", type: "number", card: true },
      { key: "row", label: "Row", type: "number", card: true },
      { key: "column", label: "Column", type: "number", card: true },
    ],
    searchKeys: ["student_name", "seat_number"],
  },
  "exam-attendance": {
    key: "exam-attendance",
    label: "Exam Attendance",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "exam-attendance",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "exam_entry", label: "Exam Entry", card: true },
      { key: "status", label: "Status", type: "select", options: EXAM_ATT_STATUS, badge: true },
      { key: "arrival_time", label: "Arrival", type: "datetime", card: true },
      { key: "departure_time", label: "Departure", type: "datetime", card: true },
      { key: "minutes_late", label: "Minutes Late", type: "number", card: true },
      { key: "seating", label: "Seating", card: true },
      { key: "invigilator_notes", label: "Notes", type: "textarea", full: true, card: true },
      { key: "recorded_by_name", label: "Recorded By", card: true, skipForm: true },
      { key: "recorded_by", label: "Recorded By ID", card: true },
    ],
    searchKeys: ["student_name", "status"],
  },
  "academic-session": {
    key: "academic-session",
    label: "Academic Session",
    icon: AcademicCapIcon,
    endpoint: "academic-session",
    titleField: "name",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "status", label: "Status", type: "select", options: SESSION_STATUS, badge: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "semester", label: "Semester", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "enrollment_start", label: "Enrollment Start", type: "date", card: true },
      { key: "enrollment_end", label: "Enrollment End", type: "date", card: true },
      { key: "exam_start_date", label: "Exam Start", type: "date", card: true },
      { key: "exam_end_date", label: "Exam End", type: "date", card: true },
      { key: "results_date", label: "Results", type: "date", card: true },
    ],
    searchKeys: ["name", "status", "semester"],
  },
  "substitute-schedule": {
    key: "substitute-schedule",
    label: "Substitute Schedule",
    icon: ArrowPathIcon,
    endpoint: "substitute-schedule",
    titleField: "class_group_label",
    subtitleField: "subject_name",
    fields: [
      { key: "class_group_label", label: "Class Group", main: true, skipForm: true },
      { key: "class_group", label: "Class Group ID", skipForm: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      { key: "subject", label: "Subject ID", card: true },
      { key: "substitute_teacher", label: "Substitute", card: true },
      { key: "original_teacher", label: "Original Teacher", card: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "timetable_slot", label: "Slot ID", card: true },
      { key: "status", label: "Status", type: "select", options: SUB_STATUS_SHORT, badge: true },
      { key: "lesson_plan", label: "Lesson Plan", card: true },
    ],
    searchKeys: ["class_group_label", "subject_name", "status"],
  },
  "room-utilization": {
    key: "room-utilization",
    label: "Room Utilization",
    icon: ChartBarIcon,
    endpoint: "room-utilization",
    titleField: "room_name",
    subtitleField: "date",
    fields: [
      { key: "room_name", label: "Room", main: true, skipForm: true },
      { key: "room", label: "Room ID", skipForm: true },
      { key: "date", label: "Date", type: "date", subtitle: true, card: true },
      { key: "total_hours_available", label: "Available", type: "number", card: true },
      { key: "total_hours_used", label: "Used", type: "number", card: true },
      {
        key: "utilization_percentage",
        label: "Utilization %",
        type: "number",
        card: true,
        badge: true,
      },
      { key: "teaching_hours", label: "Teaching", type: "number", card: true },
      { key: "exam_hours", label: "Exams", type: "number", card: true },
      { key: "meeting_hours", label: "Meetings", type: "number", card: true },
      { key: "event_hours", label: "Events", type: "number", card: true },
      { key: "conflicts_detected", label: "Conflicts", type: "number", card: true },
    ],
    searchKeys: ["room_name", "utilization_percentage"],
  },
  "timetable-validation-rule": {
    key: "timetable-validation-rule",
    label: "Validation Rule",
    icon: ScaleIcon,
    endpoint: "timetable-validation-rule",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "rule_type", label: "Type", type: "select", options: RULE_TYPES, badge: true },
      {
        key: "description",
        label: "Description",
        subtitle: true,
        type: "textarea",
        full: true,
        card: true,
      },
      { key: "max_value", label: "Max Value", type: "number", card: true },
      { key: "min_value", label: "Min Value", type: "number", card: true },
      { key: "priority", label: "Priority", type: "number", card: true },
      { key: "is_hard_constraint", label: "Hard Constraint", type: "bool", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "parameters", label: "Parameters", type: "textarea", full: true },
    ],
    searchKeys: ["name", "rule_type", "description"],
  },
  "timetable-validation-error": {
    key: "timetable-validation-error",
    label: "Validation Error",
    icon: ExclamationTriangleIcon,
    endpoint: "timetable-validation-error",
    titleField: "rule_name",
    subtitleField: "message",
    fields: [
      { key: "rule_name", label: "Rule", main: true, skipForm: true },
      { key: "rule", label: "Rule ID", skipForm: true },
      {
        key: "message",
        label: "Message",
        subtitle: true,
        type: "textarea",
        full: true,
        card: true,
      },
      { key: "severity", label: "Severity", type: "select", options: SEVERITIES, badge: true },
      { key: "timetable_slot", label: "Slot ID", card: true },
      { key: "details", label: "Details", type: "textarea", full: true, card: true },
      { key: "resolved", label: "Resolved", type: "bool", badge: true },
      { key: "resolved_by_name", label: "Resolved By", card: true, skipForm: true },
      { key: "resolved_by", label: "Resolved By ID", card: true },
      { key: "resolved_at", label: "Resolved At", type: "datetime", card: true, skipForm: true },
      { key: "resolution_notes", label: "Resolution Notes", type: "textarea", full: true },
    ],
    searchKeys: ["rule_name", "message", "severity"],
  },
  "timetable-resource": {
    key: "timetable-resource",
    label: "Timetable Resource",
    icon: ServerIcon,
    endpoint: "timetable-resource",
    titleField: "name",
    toggleField: "is_available",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "resource_type", label: "Type", type: "select", options: RESOURCE_TYPES, badge: true },
      { key: "room_name", label: "Room", card: true, skipForm: true },
      { key: "room", label: "Room ID", card: true },
      { key: "capacity", label: "Capacity", type: "number", card: true },
      { key: "hourly_cost", label: "Hourly Cost", type: "number", card: true },
      { key: "is_available", label: "Available", type: "bool", badge: true },
      { key: "notes", label: "Notes", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["name", "resource_type", "room_name"],
  },
  "timetable-resource-booking": {
    key: "timetable-resource-booking",
    label: "Resource Booking",
    icon: TicketIcon,
    endpoint: "timetable-resource-booking",
    titleField: "resource_name",
    subtitleField: "purpose",
    fields: [
      { key: "resource_name", label: "Resource", main: true, skipForm: true },
      { key: "resource", label: "Resource ID", skipForm: true },
      {
        key: "purpose",
        label: "Purpose",
        subtitle: true,
        type: "textarea",
        full: true,
        card: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: RESOURCE_BOOKING_STATUS,
        badge: true,
      },
      { key: "booking_date", label: "Date", type: "date", card: true },
      { key: "start_time", label: "Start", card: true },
      { key: "end_time", label: "End", card: true },
      { key: "class_group_label", label: "Class Group", card: true, skipForm: true },
      { key: "class_group", label: "Class Group ID", card: true },
      { key: "event_title", label: "Event", card: true, skipForm: true },
      { key: "event", label: "Event ID", card: true },
      { key: "booked_by_name", label: "Booked By", card: true, skipForm: true },
      { key: "booked_by", label: "Booked By ID", card: true },
      { key: "approved_by_name", label: "Approved By", card: true, skipForm: true },
      { key: "approved_by", label: "Approved By ID", card: true },
    ],
    searchKeys: ["resource_name", "purpose", "status"],
  },
  "timetable-analytics": {
    key: "timetable-analytics",
    label: "Analytics",
    icon: ChartBarIcon,
    endpoint: "timetable-analytics",
    titleField: "academic_year",
    subtitleField: "semester",
    fields: [
      { key: "academic_year", label: "Academic Year", main: true },
      { key: "semester", label: "Semester", subtitle: true, card: true },
      { key: "generation_date", label: "Generated", type: "datetime", card: true, skipForm: true },
      { key: "total_classes", label: "Classes", type: "number", card: true },
      { key: "total_slots", label: "Slots", type: "number", card: true },
      { key: "total_teachers", label: "Teachers", type: "number", card: true },
      { key: "total_rooms", label: "Rooms", type: "number", card: true },
      { key: "conflicts_found", label: "Conflicts Found", type: "number", card: true },
      { key: "conflicts_resolved", label: "Conflicts Resolved", type: "number", card: true },
      {
        key: "validation_score",
        label: "Validation Score",
        type: "number",
        card: true,
        badge: true,
      },
      { key: "avg_teacher_load", label: "Avg Teacher Load", type: "number", card: true },
      { key: "max_teacher_load", label: "Max Teacher Load", type: "number", card: true },
    ],
    searchKeys: ["academic_year", "semester", "validation_score"],
  },
  "timetable-change-request": {
    key: "timetable-change-request",
    label: "Change Request",
    icon: WrenchScrewdriverIcon,
    endpoint: "timetable-change-request",
    titleField: "request_type",
    subtitleField: "description",
    fields: [
      {
        key: "request_type",
        label: "Type",
        type: "select",
        options: CHANGE_REQUEST_TYPES,
        main: true,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        subtitle: true,
        type: "textarea",
        full: true,
        card: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CHANGE_REQUEST_STATUS,
        badge: true,
      },
      { key: "requested_by", label: "Requested By", card: true },
      { key: "original_slot", label: "Original Slot", card: true },
      { key: "requested_slot", label: "Requested Slot", card: true },
      { key: "approved_by_name", label: "Approved By", card: true, skipForm: true },
      { key: "approved_by", label: "Approved By ID", card: true },
      { key: "approval_notes", label: "Approval Notes", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["request_type", "description", "status"],
  },
  "daily-schedule": {
    key: "daily-schedule",
    label: "Daily Schedule",
    icon: CalendarDaysIcon,
    endpoint: "daily-schedule",
    titleField: "date",
    fields: [
      { key: "date", label: "Date", type: "date", main: true },
      {
        key: "day_of_week",
        label: "Day",
        type: "select",
        options: DAYS,
        subtitle: true,
        card: true,
      },
      { key: "total_classes_scheduled", label: "Scheduled", type: "number", card: true },
      { key: "total_classes_conducted", label: "Conducted", type: "number", card: true },
      { key: "total_classes_cancelled", label: "Cancelled", type: "number", card: true },
      { key: "total_substitutes", label: "Substitutes", type: "number", card: true },
      { key: "is_holiday", label: "Holiday", type: "bool", badge: true },
      { key: "holiday_name", label: "Holiday Name", card: true },
      { key: "is_special_schedule", label: "Special Schedule", type: "bool", badge: true },
      { key: "special_schedule_name", label: "Special Name", card: true },
    ],
    searchKeys: ["date", "holiday_name", "special_schedule_name"],
  },
  "teacher-workload": {
    key: "teacher-workload",
    label: "Teacher Workload",
    icon: ChartBarIcon,
    endpoint: "teacher-workload",
    titleField: "teacher_name",
    subtitleField: "workload_percentage",
    fields: [
      { key: "teacher_name", label: "Teacher", main: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", skipForm: true },
      {
        key: "workload_percentage",
        label: "Workload %",
        subtitle: true,
        type: "number",
        card: true,
        badge: true,
      },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "semester", label: "Semester", card: true },
      { key: "total_periods_per_week", label: "Periods/Week", type: "number", card: true },
      { key: "total_classes", label: "Classes", type: "number", card: true },
      { key: "total_students", label: "Students", type: "number", card: true },
      { key: "subjects_taught", label: "Subjects", type: "number", card: true },
      { key: "classes_taught", label: "Classes Taught", type: "number", card: true },
      { key: "max_periods_per_week", label: "Max Periods/Week", type: "number", card: true },
      { key: "duty_hours_per_week", label: "Duty Hours/Week", type: "number", card: true },
    ],
    searchKeys: ["teacher_name", "workload_percentage"],
  },
  "class-schedule": {
    key: "class-schedule",
    label: "Class Schedule",
    icon: TableCellsIcon,
    endpoint: "class-schedule",
    titleField: "class_group_label",
    fields: [
      { key: "class_group_label", label: "Class Group", main: true, skipForm: true },
      { key: "class_group", label: "Class Group ID", skipForm: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "total_weekly_periods", label: "Weekly Periods", type: "number", card: true },
      { key: "subjects_scheduled", label: "Subjects Scheduled", card: true },
      { key: "is_finalized", label: "Finalized", type: "bool", badge: true },
      { key: "finalized_at", label: "Finalized At", type: "datetime", card: true, skipForm: true },
      { key: "finalized_by_name", label: "Finalized By", card: true, skipForm: true },
      { key: "finalized_by", label: "Finalized By ID", card: true },
    ],
    searchKeys: ["class_group_label", "subjects_scheduled"],
  },
  "timetable-version": {
    key: "timetable-version",
    label: "Timetable Version",
    icon: CircleStackIcon,
    endpoint: "timetable-version",
    titleField: "name",
    subtitleField: "version_number",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "version_number", label: "Version", subtitle: true, type: "number", card: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "semester", label: "Semester", card: true },
      { key: "is_current", label: "Current", type: "bool", badge: true },
      { key: "is_published", label: "Published", type: "bool", badge: true },
      { key: "published_at", label: "Published At", type: "datetime", card: true, skipForm: true },
      { key: "changes_from_previous", label: "Changes", type: "textarea", full: true, card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", card: true },
    ],
    searchKeys: ["name", "version_number", "description"],
  },
};

const TABS: { key: string; label: string; icon: React.ComponentType<{ className?: string }> }[] =
  Object.values(ENTITY_CONFIGS).map((c) => ({ key: c.key, label: c.label, icon: c.icon }));

// ─── Overview tab (weekly grid) ──────────────────────────────────────────────

const WEEK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const COLORS = [
  "bg-indigo-100 text-indigo-800",
  "bg-emerald-100 text-emerald-800",
  "bg-amber-100 text-amber-800",
  "bg-violet-100 text-violet-800",
  "bg-rose-100 text-rose-800",
  "bg-teal-100 text-teal-800",
  "bg-orange-100 text-orange-800",
  "bg-cyan-100 text-cyan-800",
];

interface WeeklySlot {
  subject_name: string;
  period_name: string;
  start_time: string;
  end_time: string;
  teacher_name: string;
  classroom_name: string;
  room: string;
}

function OverviewTab() {
  const [classroomId, setClassroomId] = useState<number | null>(null);
  const { data: classroomsData } = useClassrooms();
  const { data: academicYear } = useCurrentAcademicYear();
  const classrooms = classroomsData?.results ?? [];

  const { data: weekly, isLoading } = useQuery({
    queryKey: ["admin-timetable", classroomId, academicYear?.id],
    queryFn: () =>
      api.get<Record<string, WeeklySlot[]>>(
        `/timetable/slots/weekly/?classroom_id=${classroomId}&academic_year_id=${academicYear?.id}`,
      ),
    enabled: !!classroomId && !!academicYear?.id,
  });

  const colorMap: Record<string, string> = {};
  let ci = 0;
  if (weekly)
    Object.values(weekly)
      .flat()
      .forEach((s) => {
        if (!colorMap[s.subject_name]) colorMap[s.subject_name] = COLORS[ci++ % COLORS.length];
      });

  return (
    <div className="space-y-5">
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4 flex flex-wrap gap-4">
        <div className="flex-1 min-w-48">
          <Select
            label="Select Classroom"
            placeholder="Choose a class…"
            value={classroomId ?? ""}
            onChange={(e) => setClassroomId(Number(e.target.value) || null)}
            options={classrooms.map((c) => ({ value: c.id, label: `${c.grade_name} ${c.name}` }))}
          />
        </div>
      </div>
      {isLoading && <SkeletonCard className="max-w-md mx-auto" />}
      {weekly && !isLoading && (
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-700/50">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase border-b border-slate-100 dark:border-slate-700 w-24">
                    Period
                  </th>
                  {WEEK_DAYS.map((d) => (
                    <th
                      key={d}
                      className="px-3 py-3 text-left text-xs font-semibold text-slate-500 uppercase border-b border-l border-slate-100 dark:border-slate-700 min-w-36"
                    >
                      {d}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Array.from(
                  new Set(
                    Object.values(weekly)
                      .flat()
                      .map((s) => s.period_name),
                  ),
                ).map((period, pi) => (
                  <tr
                    key={String(period)}
                    className={
                      pi % 2 === 0
                        ? "bg-white dark:bg-slate-800"
                        : "bg-slate-50/40 dark:bg-slate-700/30"
                    }
                  >
                    <td className="px-4 py-3 border-b border-slate-100 dark:border-slate-700">
                      <p className="text-xs font-semibold text-slate-700 dark:text-slate-200">
                        {String(period)}
                      </p>
                      <p className="text-[10px] text-slate-400">
                        {
                          Object.values(weekly)
                            .flat()
                            .find((s) => s.period_name === period)?.start_time
                        }
                      </p>
                    </td>
                    {WEEK_DAYS.map((day) => {
                      const slot = (weekly[day] ?? []).find((s) => s.period_name === period);
                      return (
                        <td
                          key={day}
                          className="px-2 py-2 border-b border-l border-slate-100 dark:border-slate-700"
                        >
                          {slot ? (
                            <div
                              className={`rounded-lg p-2 text-xs ${
                                colorMap[slot.subject_name] ?? COLORS[0]
                              }`}
                            >
                              <p className="font-semibold truncate">{slot.subject_name}</p>
                              <p className="opacity-70 truncate mt-0.5">{slot.teacher_name}</p>
                            </div>
                          ) : (
                            <div className="h-10" />
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {!classroomId && !isLoading && (
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-16 text-center text-slate-400">
          <p>Select a classroom to view its timetable</p>
        </div>
      )}
    </div>
  );
}

// ─── Main page ───────────────────────────────────────────────────────────────

export default function TimetablePage() {
  useTitle("Timetable Center");
  const [activeTab, setActiveTab] = useState("overview");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const searchRef = useRef<HTMLInputElement>(null);
  const actionRef = useRef<{ add?: () => void; export?: () => void }>({});
  const { open: helpOpen, setOpen: setHelpOpen } = useShortcutHelp();

  useEffect(() => {
    setPage(1);
  }, [activeTab]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.tagName === "SELECT" ||
        target.isContentEditable
      ) {
        return;
      }
      if (e.key === "/") {
        e.preventDefault();
        searchRef.current?.focus();
      }
      if (e.key.toLowerCase() === "n") {
        e.preventDefault();
        actionRef.current?.add?.();
      }
      if (e.key.toLowerCase() === "e") {
        e.preventDefault();
        actionRef.current?.export?.();
      }
      if (e.key.toLowerCase() === "p") {
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Timetable Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Weekly schedules, periods, events, exams, bookings, substitutions and analytics
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
            leftIcon={<ShieldExclamationIcon className="h-4 w-4" />}
          >
            Shortcuts
          </Button>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        <button
          onClick={() => setActiveTab("overview")}
          className={`flex shrink-0 items-center gap-1.5 rounded-xl px-3.5 py-2 text-sm font-medium transition ${
            activeTab === "overview"
              ? "bg-indigo-600 text-white shadow-sm"
              : "bg-white text-slate-600 hover:bg-slate-50 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
          }`}
        >
          <CalendarDaysIcon className="h-4 w-4" />
          Overview
        </button>
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

      {activeTab === "overview" ? (
        <OverviewTab />
      ) : (
        <EntitySection
          cfg={activeCfg}
          basePath="/timetable"
          search={search}
          page={page}
          setPage={setPage}
          viewMode={viewMode}
          registerActions={(h) => {
            actionRef.current = h;
          }}
        />
      )}

      <KeyboardShortcutHelp
        open={helpOpen}
        onClose={() => setHelpOpen(false)}
        shortcuts={[
          { keys: ["N"], label: "New", description: "Open create form" },
          { keys: ["/"], label: "Search", description: "Focus search input" },
          { keys: ["E"], label: "Export", description: "Export data to CSV" },
          { keys: ["P"], label: "View Mode", description: "Toggle pagination / infinite scroll" },
          { keys: ["?"], label: "Help", description: "Show this shortcut help" },
        ]}
      />
    </div>
  );
}
