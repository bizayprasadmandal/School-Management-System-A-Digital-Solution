/**
 * Conferences Center — full-surface admin page for the conferences module.
 *
 * 33 entity tabs (config-driven via EntitySection). Slots, bookings, availability, locations, approvals, surveys, no-shows and analytics.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, VideoCameraIcon } from "@heroicons/react/24/outline";

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  availability: {
    key: "availability",
    icon: VideoCameraIcon,
    label: "Conference Availability",
    endpoint: "availability",
    titleField: "teacher",
    fields: [
      { key: "teacher", label: "Teacher" },
      {
        key: "day_of_week",
        label: "Day Of Week",
        type: "select",
        options: [
          ["0", "0"],
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
          ["6", "6"],
        ],
      },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      {
        key: "availability_type",
        label: "Availability Type",
        type: "select",
        options: [
          ["available", "Available"],
          ["unavailable", "Unavailable"],
          ["tentative", "Tentative"],
        ],
      },
      { key: "location", label: "Location" },
      { key: "is_virtual_available", label: "Is Virtual Available" },
      { key: "effective_from", label: "Effective From" },
      { key: "effective_until", label: "Effective Until" },
      { key: "is_recurring", label: "Is Recurring" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  bookings: {
    key: "bookings",
    icon: VideoCameraIcon,
    label: "Conference Booking",
    endpoint: "bookings",
    titleField: "slot",
    subtitleField: "status",
    fields: [
      { key: "slot", label: "Slot" },
      { key: "booking_type", label: "Booking Type" },
      { key: "parent", label: "Parent" },
      { key: "student", label: "Student" },
      { key: "teacher", label: "Teacher" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["confirmed", "Confirmed"],
          ["cancelled", "Cancelled"],
          ["completed", "Completed"],
          ["no_show", "No Show"],
          ["rescheduled", "Rescheduled"],
        ],
      },
      { key: "is_virtual", label: "Is Virtual" },
      { key: "meeting_link", label: "Meeting Link" },
      { key: "meeting_id", label: "Meeting Id" },
    ],
  },
  "conference-analytics": {
    key: "conference-analytics",
    icon: VideoCameraIcon,
    label: "Conference Analytics",
    endpoint: "conference-analytics",
    titleField: "date",
    fields: [
      { key: "date", label: "Date", type: "date" },
      { key: "total_scheduled", label: "Total Scheduled" },
      { key: "total_completed", label: "Total Completed" },
      { key: "total_no_show", label: "Total No Show" },
      { key: "total_cancelled", label: "Total Cancelled" },
      { key: "total_parents", label: "Total Parents" },
      { key: "total_teachers", label: "Total Teachers" },
      { key: "parent_participation_rate", label: "Parent Participation Rate" },
      { key: "avg_duration_minutes", label: "Avg Duration Minutes" },
      { key: "avg_satisfaction_rating", label: "Avg Satisfaction Rating" },
      {
        key: "by_type_breakdown",
        label: "By Type Breakdown",
        type: "textarea",
      },
    ],
  },
  "conference-approval": {
    key: "conference-approval",
    icon: VideoCameraIcon,
    label: "Conference Approval",
    endpoint: "conference-approval",
    titleField: "booking",
    subtitleField: "status",
    fields: [
      { key: "booking", label: "Booking" },
      { key: "approver", label: "Approver" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["denied", "Denied"],
        ],
      },
      { key: "comments", label: "Comments" },
      { key: "decided_at", label: "Decided At", type: "date" },
    ],
  },
  "conference-blocked-slot": {
    key: "conference-blocked-slot",
    icon: VideoCameraIcon,
    label: "Conference Blocked Slot",
    endpoint: "conference-blocked-slot",
    titleField: "title",
    fields: [
      { key: "teacher", label: "Teacher" },
      { key: "title", label: "Title" },
      { key: "date", label: "Date", type: "date" },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      { key: "reason", label: "Reason" },
      { key: "is_recurring", label: "Is Recurring" },
    ],
  },
  "conference-booking-rule": {
    key: "conference-booking-rule",
    icon: VideoCameraIcon,
    label: "Conference Booking Rule",
    endpoint: "conference-booking-rule",
    titleField: "name",
    subtitleField: "priority",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "rule_type",
        label: "Rule Type",
        type: "select",
        options: [
          ["time_slot", "Time Slot"],
          ["grade", "Grade"],
          ["teacher_limit", "Teacher Limit"],
          ["parent_limit", "Parent Limit"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "parameters", label: "Parameters", type: "textarea" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "priority", label: "Priority" },
    ],
  },
  "conference-calendar-sync": {
    key: "conference-calendar-sync",
    icon: VideoCameraIcon,
    label: "Conference Calendar Sync",
    endpoint: "conference-calendar-sync",
    titleField: "calendar_type",
    subtitleField: "status",
    fields: [
      {
        key: "calendar_type",
        label: "Calendar Type",
        type: "select",
        options: [
          ["google", "Google"],
          ["outlook", "Outlook"],
          ["ics", "Ics"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["error", "Error"],
          ["disabled", "Disabled"],
        ],
      },
      { key: "calendar_id", label: "Calendar Id" },
      { key: "ical_url", label: "Ical Url" },
      { key: "auto_sync", label: "Auto Sync" },
      { key: "last_synced_at", label: "Last Synced At", type: "date" },
      { key: "last_error", label: "Last Error" },
    ],
  },
  "conference-conference-type": {
    key: "conference-conference-type",
    icon: VideoCameraIcon,
    label: "Conference Conference Type",
    endpoint: "conference-conference-type",
    titleField: "conference_type",
    fields: [
      { key: "conference_type", label: "Conference Type" },
      { key: "requires_parent_consent", label: "Requires Parent Consent" },
      { key: "requires_student_consent", label: "Requires Student Consent" },
      { key: "auto_generate_notes", label: "Auto Generate Notes" },
      { key: "default_location", label: "Default Location" },
      { key: "max_duration_minutes", label: "Max Duration Minutes" },
      { key: "allow_virtual", label: "Allow Virtual" },
      { key: "allow_walk_in", label: "Allow Walk In" },
      { key: "fee", label: "Fee" },
    ],
  },
  "conference-export": {
    key: "conference-export",
    icon: VideoCameraIcon,
    label: "Conference Export",
    endpoint: "conference-export",
    titleField: "export_type",
    subtitleField: "status",
    fields: [
      {
        key: "export_type",
        label: "Export Type",
        type: "select",
        options: [
          ["schedule", "Schedule"],
          ["attendance", "Attendance"],
          ["feedback", "Feedback"],
          ["all", "All"],
        ],
      },
      {
        key: "format",
        label: "Format",
        type: "select",
        options: [
          ["csv", "Csv"],
          ["pdf", "Pdf"],
          ["excel", "Excel"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["processing", "Processing"],
          ["completed", "Completed"],
          ["failed", "Failed"],
        ],
      },
      { key: "date_from", label: "Date From", type: "date" },
      { key: "date_to", label: "Date To", type: "date" },
      { key: "file", label: "File" },
      { key: "record_count", label: "Record Count", type: "number" },
      { key: "requested_by", label: "Requested By" },
      { key: "requested_at", label: "Requested At", type: "date" },
      { key: "completed_at", label: "Completed At", type: "date" },
    ],
  },
  "conference-follow-up": {
    key: "conference-follow-up",
    icon: VideoCameraIcon,
    label: "Conference Follow Up",
    endpoint: "conference-follow-up",
    titleField: "booking",
    subtitleField: "status",
    fields: [
      { key: "booking", label: "Booking" },
      { key: "assigned_to", label: "Assigned To" },
      { key: "action_required", label: "Action Required" },
      { key: "due_date", label: "Due Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["in_progress", "In Progress"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "completed_at", label: "Completed At", type: "date" },
    ],
  },
  "conference-history-detail": {
    key: "conference-history-detail",
    icon: VideoCameraIcon,
    label: "Conference History Detail",
    endpoint: "conference-history-detail",
    titleField: "booking",
    fields: [
      { key: "booking", label: "Booking" },
      { key: "student", label: "Student" },
      { key: "conference_date", label: "Conference Date", type: "date" },
      { key: "conference_type", label: "Conference Type" },
      { key: "topics_discussed", label: "Topics Discussed" },
      { key: "outcome", label: "Outcome" },
      { key: "follow_up_needed", label: "Follow Up Needed" },
      { key: "recommendations", label: "Recommendations" },
      { key: "recorded_by", label: "Recorded By" },
    ],
  },
  "conference-location": {
    key: "conference-location",
    icon: VideoCameraIcon,
    label: "Conference Location",
    endpoint: "conference-location",
    titleField: "name",
    subtitleField: "location_type",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "location_type",
        label: "Location Type",
        type: "select",
        options: [
          ["in_person", "In Person"],
          ["virtual", "Virtual"],
          ["hybrid", "Hybrid"],
        ],
      },
      { key: "building", label: "Building" },
      { key: "room", label: "Room" },
      { key: "capacity", label: "Capacity" },
      { key: "virtual_link", label: "Virtual Link" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "conference-no-show": {
    key: "conference-no-show",
    icon: VideoCameraIcon,
    label: "Conference No Show",
    endpoint: "conference-no-show",
    titleField: "booking",
    fields: [
      { key: "booking", label: "Booking" },
      { key: "rescheduled", label: "Rescheduled" },
      { key: "rescheduled_to", label: "Rescheduled To" },
      { key: "reason", label: "Reason" },
    ],
  },
  "conference-note-template": {
    key: "conference-note-template",
    icon: VideoCameraIcon,
    label: "Conference Note Template",
    endpoint: "conference-note-template",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "sections", label: "Sections" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "is_default", label: "Is Default", type: "bool" },
    ],
  },
  "conference-resource": {
    key: "conference-resource",
    icon: VideoCameraIcon,
    label: "Conference Resource",
    endpoint: "conference-resource",
    titleField: "name",
    fields: [
      { key: "booking", label: "Booking" },
      {
        key: "resource_type",
        label: "Resource Type",
        type: "select",
        options: [
          ["room", "Room"],
          ["equipment", "Equipment"],
          ["document", "Document"],
          ["translator", "Translator"],
        ],
      },
      { key: "name", label: "Name" },
      { key: "quantity", label: "Quantity" },
      { key: "is_reserved", label: "Is Reserved" },
      { key: "cost", label: "Cost" },
    ],
  },
  "conference-room-booking": {
    key: "conference-room-booking",
    icon: VideoCameraIcon,
    label: "Conference Room Booking",
    endpoint: "conference-room-booking",
    titleField: "location",
    subtitleField: "status",
    fields: [
      { key: "location", label: "Location" },
      { key: "booking", label: "Booking" },
      { key: "date", label: "Date", type: "date" },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["confirmed", "Confirmed"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "booked_by", label: "Booked By" },
    ],
  },
  "conference-settings": {
    key: "conference-settings",
    icon: VideoCameraIcon,
    label: "Conference Settings",
    endpoint: "conference-settings",
    titleField: "booking_window_days",
    fields: [
      { key: "booking_window_days", label: "Booking Window Days" },
      { key: "cancellation_window_hours", label: "Cancellation Window Hours" },
      { key: "buffer_between_minutes", label: "Buffer Between Minutes" },
      { key: "max_conferences_per_day", label: "Max Conferences Per Day" },
      { key: "send_confirmation_email", label: "Send Confirmation Email" },
      { key: "send_reminder_email", label: "Send Reminder Email" },
      { key: "reminder_hours_before", label: "Reminder Hours Before" },
      { key: "collect_feedback", label: "Collect Feedback" },
      { key: "feedback_deadline_days", label: "Feedback Deadline Days" },
    ],
  },
  "conference-slots": {
    key: "conference-slots",
    icon: VideoCameraIcon,
    label: "Conference Slot",
    endpoint: "conference-slots",
    titleField: "teacher",
    fields: [
      { key: "teacher", label: "Teacher" },
      { key: "student", label: "Student" },
      { key: "date", label: "Date", type: "date" },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      { key: "is_booked", label: "Is Booked" },
      { key: "booked_by", label: "Booked By" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "zoom_meeting_id", label: "Zoom Meeting Id" },
      { key: "zoom_join_url", label: "Zoom Join Url" },
    ],
  },
  "conference-survey": {
    key: "conference-survey",
    icon: VideoCameraIcon,
    label: "Conference Survey",
    endpoint: "conference-survey",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "title", label: "Title" },
      { key: "questions", label: "Questions" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["active", "Active"],
          ["closed", "Closed"],
        ],
      },
      { key: "total_responses", label: "Total Responses" },
    ],
  },
  "conference-survey-response": {
    key: "conference-survey-response",
    icon: VideoCameraIcon,
    label: "Conference Survey Response",
    endpoint: "conference-survey-response",
    titleField: "survey",
    fields: [
      { key: "survey", label: "Survey" },
      { key: "respondent", label: "Respondent" },
      { key: "answers", label: "Answers" },
      { key: "overall_rating", label: "Overall Rating" },
      { key: "comments", label: "Comments" },
      { key: "submitted_at", label: "Submitted At", type: "date" },
    ],
  },
  "conference-time-slot": {
    key: "conference-time-slot",
    icon: VideoCameraIcon,
    label: "Conference Time Slot",
    endpoint: "conference-time-slot",
    titleField: "teacher",
    subtitleField: "status",
    fields: [
      { key: "teacher", label: "Teacher" },
      { key: "date", label: "Date", type: "date" },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["available", "Available"],
          ["booked", "Booked"],
          ["blocked", "Blocked"],
        ],
      },
      { key: "booking", label: "Booking" },
      { key: "location", label: "Location" },
    ],
  },
  "conference-types": {
    key: "conference-types",
    icon: VideoCameraIcon,
    label: "Conference Type",
    endpoint: "conference-types",
    titleField: "name",
    subtitleField: "category",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: [
          ["ptc", "Ptc"],
          ["student_led", "Student Led"],
          ["three_way", "Three Way"],
          ["iep", "Iep"],
          ["planning", "Planning"],
          ["progress", "Progress"],
          ["discipline", "Discipline"],
          ["orientation", "Orientation"],
          ["other", "Other"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "default_duration_minutes", label: "Default Duration Minutes" },
      { key: "max_participants", label: "Max Participants" },
      { key: "allow_virtual", label: "Allow Virtual" },
      { key: "allow_notes", label: "Allow Notes" },
      { key: "require_student", label: "Require Student" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "conference-waiting-list": {
    key: "conference-waiting-list",
    icon: VideoCameraIcon,
    label: "Conference Waiting List",
    endpoint: "conference-waiting-list",
    titleField: "parent",
    subtitleField: "status",
    fields: [
      { key: "parent", label: "Parent" },
      { key: "student", label: "Student" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["waiting", "Waiting"],
          ["contacted", "Contacted"],
          ["scheduled", "Scheduled"],
          ["expired", "Expired"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "position", label: "Position", type: "number" },
      { key: "preferred_dates", label: "Preferred Dates" },
      { key: "preferred_times", label: "Preferred Times" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  feedback: {
    key: "feedback",
    icon: VideoCameraIcon,
    label: "Conference Feedback",
    endpoint: "feedback",
    titleField: "booking",
    fields: [
      { key: "booking", label: "Booking" },
      { key: "submitted_by", label: "Submitted By" },
      {
        key: "feedback_for",
        label: "Feedback For",
        type: "select",
        options: [
          ["teacher", "Teacher"],
          ["conference", "Conference"],
          ["school", "School"],
          ["other", "Other"],
        ],
      },
      {
        key: "overall_rating",
        label: "Overall Rating",
        type: "select",
        options: [
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
        ],
      },
      {
        key: "communication_rating",
        label: "Communication Rating",
        type: "select",
        options: [
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
        ],
      },
      {
        key: "preparedness_rating",
        label: "Preparedness Rating",
        type: "select",
        options: [
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
        ],
      },
      {
        key: "helpfulness_rating",
        label: "Helpfulness Rating",
        type: "select",
        options: [
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
        ],
      },
      { key: "positive_feedback", label: "Positive Feedback" },
      { key: "suggestions", label: "Suggestions" },
      { key: "additional_comments", label: "Additional Comments" },
      { key: "submitted_at", label: "Submitted At", type: "date" },
    ],
  },
  "follow-ups": {
    key: "follow-ups",
    icon: VideoCameraIcon,
    label: "Follow Up Tracking",
    endpoint: "follow-ups",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "booking", label: "Booking" },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "priority",
        label: "Priority",
        type: "select",
        options: [
          ["low", "Low"],
          ["medium", "Medium"],
          ["high", "High"],
          ["urgent", "Urgent"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["in_progress", "In Progress"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
          ["overdue", "Overdue"],
        ],
      },
      { key: "assigned_to", label: "Assigned To" },
      { key: "due_date", label: "Due Date", type: "date" },
      { key: "completed_date", label: "Completed Date", type: "date" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  history: {
    key: "history",
    icon: VideoCameraIcon,
    label: "Conference History",
    endpoint: "history",
    titleField: "booking",
    fields: [
      { key: "booking", label: "Booking" },
      { key: "teacher", label: "Teacher" },
      { key: "parent", label: "Parent" },
      { key: "student", label: "Student" },
      { key: "conference_date", label: "Conference Date", type: "date" },
      { key: "conference_type", label: "Conference Type" },
      { key: "was_virtual", label: "Was Virtual" },
    ],
  },
  notes: {
    key: "notes",
    icon: VideoCameraIcon,
    label: "Conference Notes",
    endpoint: "notes",
    titleField: "title",
    fields: [
      { key: "booking", label: "Booking" },
      {
        key: "note_type",
        label: "Note Type",
        type: "select",
        options: [
          ["general", "General"],
          ["academic", "Academic"],
          ["behavior", "Behavior"],
          ["action", "Action"],
          ["follow_up", "Follow Up"],
          ["recommendations", "Recommendations"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "content", label: "Content" },
      { key: "has_action_items", label: "Has Action Items" },
      { key: "action_items", label: "Action Items" },
      { key: "action_items_completed", label: "Action Items Completed" },
      { key: "follow_up_needed", label: "Follow Up Needed" },
      { key: "follow_up_date", label: "Follow Up Date", type: "date" },
      { key: "follow_up_notes", label: "Follow Up Notes" },
      { key: "created_by", label: "Created By" },
      { key: "shared_with_parent", label: "Shared With Parent" },
    ],
  },
  "recurring-conference": {
    key: "recurring-conference",
    icon: VideoCameraIcon,
    label: "Recurring Conference",
    endpoint: "recurring-conference",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "frequency",
        label: "Frequency",
        type: "select",
        options: [
          ["weekly", "Weekly"],
          ["biweekly", "Biweekly"],
          ["monthly", "Monthly"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["paused", "Paused"],
          ["ended", "Ended"],
        ],
      },
      { key: "day_of_week", label: "Day Of Week" },
      { key: "time_of_day", label: "Time Of Day" },
      { key: "duration_minutes", label: "Duration Minutes" },
      { key: "teacher", label: "Teacher" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "last_occurrence", label: "Last Occurrence" },
    ],
  },
  reminders: {
    key: "reminders",
    icon: VideoCameraIcon,
    label: "Conference Reminder",
    endpoint: "reminders",
    titleField: "subject",
    subtitleField: "status",
    fields: [
      { key: "booking", label: "Booking" },
      {
        key: "reminder_type",
        label: "Reminder Type",
        type: "select",
        options: [
          ["email", "Email"],
          ["sms", "Sms"],
          ["push", "Push"],
          ["in_app", "In App"],
        ],
      },
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
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "message", label: "Message", type: "textarea" },
      { key: "send_before_minutes", label: "Send Before Minutes" },
      { key: "sent_at", label: "Sent At", type: "date" },
    ],
  },
  reports: {
    key: "reports",
    icon: VideoCameraIcon,
    label: "Conference Report",
    endpoint: "reports",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "title", label: "Title" },
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: [
          ["attendance", "Attendance"],
          ["summary", "Summary"],
          ["teacher", "Teacher"],
          ["grade", "Grade"],
          ["follow_up", "Follow Up"],
          ["feedback", "Feedback"],
          ["custom", "Custom"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["generated", "Generated"],
          ["sent", "Sent"],
        ],
      },
      { key: "period_start", label: "Period Start" },
      { key: "period_end", label: "Period End" },
      { key: "summary", label: "Summary", type: "textarea" },
      { key: "findings", label: "Findings" },
      { key: "recommendations", label: "Recommendations" },
      { key: "total_conferences", label: "Total Conferences" },
      { key: "total_attended", label: "Total Attended" },
      { key: "total_no_show", label: "Total No Show" },
      { key: "attendance_rate", label: "Attendance Rate", type: "number" },
    ],
  },
  templates: {
    key: "templates",
    icon: VideoCameraIcon,
    label: "Conference Template",
    endpoint: "templates",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "conference_type", label: "Conference Type" },
      { key: "default_duration_minutes", label: "Default Duration Minutes" },
      { key: "agenda_items", label: "Agenda Items" },
      { key: "discussion_topics", label: "Discussion Topics" },
      { key: "questions_to_ask", label: "Questions To Ask" },
      { key: "require_notes", label: "Require Notes" },
      { key: "require_feedback", label: "Require Feedback" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "created_by", label: "Created By" },
    ],
  },
  virtual: {
    key: "virtual",
    icon: VideoCameraIcon,
    label: "Virtual Conference",
    endpoint: "virtual",
    titleField: "booking",
    subtitleField: "status",
    fields: [
      { key: "booking", label: "Booking" },
      {
        key: "platform",
        label: "Platform",
        type: "select",
        options: [
          ["zoom", "Zoom"],
          ["meet", "Meet"],
          ["teams", "Teams"],
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
      { key: "meeting_id", label: "Meeting Id" },
      { key: "meeting_url", label: "Meeting Url" },
      { key: "meeting_password", label: "Meeting Password" },
      { key: "host_url", label: "Host Url" },
      { key: "recording_url", label: "Recording Url" },
      { key: "has_recording", label: "Has Recording" },
      { key: "participants_joined", label: "Participants Joined" },
      { key: "scheduled_duration", label: "Scheduled Duration" },
      { key: "actual_duration", label: "Actual Duration" },
      { key: "had_technical_issues", label: "Had Technical Issues" },
    ],
  },
  waitlist: {
    key: "waitlist",
    icon: VideoCameraIcon,
    label: "Waitlist Management",
    endpoint: "waitlist",
    titleField: "slot",
    subtitleField: "status",
    fields: [
      { key: "slot", label: "Slot" },
      { key: "parent", label: "Parent" },
      { key: "student", label: "Student" },
      { key: "position", label: "Position", type: "number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["waiting", "Waiting"],
          ["offered", "Offered"],
          ["booked", "Booked"],
          ["expired", "Expired"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "offered_at", label: "Offered At", type: "date" },
      { key: "offer_expires_at", label: "Offer Expires At", type: "date" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "joined_at", label: "Joined At", type: "date" },
    ],
  },
};

const TABS = Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({
  key,
  label: cfg.label,
  icon: VideoCameraIcon,
}));

export default function ConferencesCenterPage() {
  useTitle("Conferences Center");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Conferences Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Slots, bookings, availability, locations, approvals, surveys, no-shows and analytics
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
            leftIcon={<VideoCameraIcon className="h-4 w-4" />}
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
        basePath="/conferences"
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
