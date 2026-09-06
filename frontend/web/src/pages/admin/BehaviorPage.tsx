/**
 * Behavior Center — full-surface admin page for the behavior module.
 *
 * 49 entity tabs (config-driven via EntitySection): incidents, referrals,
 * points/merits/rewards/badges, consequences/detentions/suspensions,
 * contracts, hall passes, goals/streaks, houses, SEL check-ins and surveys,
 * intervention plans, MTSS, analytics, rubrics, policies and training.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, ShieldExclamationIcon } from "@heroicons/react/24/outline";
import {
  ExclamationTriangleIcon,
  ArrowPathIcon,
  BoltIcon,
  ScaleIcon,
  CheckBadgeIcon,
  TrophyIcon,
  GiftIcon,
  StarIcon,
  CalendarDaysIcon,
  ClipboardDocumentCheckIcon,
  ClockIcon,
  FireIcon,
  FlagIcon,
  UserGroupIcon,
  UsersIcon,
  DocumentTextIcon,
  ChartBarIcon,
  PresentationChartBarIcon,
  BellAlertIcon,
  BanknotesIcon,
  SparklesIcon,
  HeartIcon,
  LifebuoyIcon,
  AcademicCapIcon,
  BookOpenIcon,
  WrenchScrewdriverIcon,
  QueueListIcon,
  TicketIcon,
  IdentificationIcon,
  CircleStackIcon,
  Cog6ToothIcon,
  ServerIcon,
  SignalIcon,
  TagIcon,
  EyeIcon,
  ChatBubbleLeftRightIcon,
  HandRaisedIcon,
  LightBulbIcon,
  LockClosedIcon,
  MegaphoneIcon,
  NewspaperIcon,
  NoSymbolIcon,
  PaperClipIcon,
  ReceiptPercentIcon,
  ShoppingBagIcon,
  ShieldCheckIcon,
  TableCellsIcon,
  EnvelopeIcon,
} from "@heroicons/react/24/outline";

// ─── Shared option sets ──────────────────────────────────────────────────────

const CATEGORY_TYPES = [
  ["positive", "Positive"],
  ["negative", "Negative"],
  ["neutral", "Neutral"],
] as [string, string][];

const SEVERITIES = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
  ["critical", "Critical"],
] as [string, string][];

const REFERRAL_STATUS = [
  ["pending", "Pending"],
  ["actioned", "Actioned"],
  ["closed", "Closed"],
] as [string, string][];

const POINT_TYPES = [
  ["earned", "Earned"],
  ["deducted", "Deducted"],
  ["adjusted", "Adjusted"],
] as [string, string][];

const CONSEQUENCE_TYPES = [
  ["verbal_warning", "Verbal Warning"],
  ["written_warning", "Written Warning"],
  ["detention", "Detention"],
  ["in_school_suspension", "In-School Suspension"],
  ["out_of_school_suspension", "Out-of-School Suspension"],
  ["expulsion", "Expulsion"],
  ["community_service", "Community Service"],
  ["parent_meeting", "Parent Meeting"],
  ["loss_of_privileges", "Loss of Privileges"],
  ["behavior_contract", "Behavior Contract"],
  ["counseling", "Counseling"],
  ["other", "Other"],
] as [string, string][];

const CONSEQUENCE_STATUS = [
  ["pending", "Pending"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["appealed", "Appealed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const MERIT_TYPES = [
  ["academic", "Academic"],
  ["citizenship", "Citizenship"],
  ["leadership", "Leadership"],
  ["service", "Service"],
  ["improvement", "Improvement"],
  ["attendance", "Attendance"],
  ["other", "Other"],
] as [string, string][];

const DETENTION_TYPES = [
  ["lunch", "Lunch"],
  ["after_school", "After School"],
  ["in_school", "In-School"],
  ["saturday", "Saturday"],
  ["other", "Other"],
] as [string, string][];

const DETENTION_STATUS = [
  ["scheduled", "Scheduled"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["missed", "Missed"],
  ["excused", "Excused"],
] as [string, string][];

const SUSPENSION_TYPES = [
  ["in_school", "In-School"],
  ["out_of_school", "Out-of-School"],
  ["expulsion", "Expulsion"],
] as [string, string][];

const SUSPENSION_STATUS = [
  ["pending", "Pending"],
  ["active", "Active"],
  ["completed", "Completed"],
  ["appealed", "Appealed"],
  ["revoked", "Revoked"],
] as [string, string][];

const CONTRACT_STATUS = [
  ["draft", "Draft"],
  ["active", "Active"],
  ["completed", "Completed"],
  ["violated", "Violated"],
  ["terminated", "Terminated"],
] as [string, string][];

const EVIDENCE_TYPES = [
  ["photo", "Photo"],
  ["video", "Video"],
  ["document", "Document"],
  ["audio", "Audio"],
  ["other", "Other"],
] as [string, string][];

const PASS_TYPES = [
  ["bathroom", "Bathroom"],
  ["nurse", "Nurse"],
  ["counselor", "Counselor"],
  ["administration", "Administration"],
  ["library", "Library"],
  ["other_class", "Other Class"],
  ["office", "Office"],
  ["other", "Other"],
] as [string, string][];

const PASS_STATUS = [
  ["active", "Active"],
  ["completed", "Completed"],
  ["expired", "Expired"],
  ["denied", "Denied"],
] as [string, string][];

const TARDY_TYPES = [
  ["excused", "Excused"],
  ["unexcused", "Unexcused"],
  ["medical", "Medical"],
  ["family", "Family"],
  ["transportation", "Transportation"],
] as [string, string][];

const TARDY_STATUS = [
  ["recorded", "Recorded"],
  ["excused", "Excused"],
  ["appealed", "Appealed"],
] as [string, string][];

const GOAL_TYPES = [
  ["reduce_incidents", "Reduce Incidents"],
  ["improve_attendance", "Improve Attendance"],
  ["earn_points", "Earn Points"],
  ["complete_consequence", "Complete Consequence"],
  ["custom", "Custom"],
] as [string, string][];

const GOAL_STATUS = [
  ["active", "Active"],
  ["achieved", "Achieved"],
  ["missed", "Missed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const STREAK_TYPES = [
  ["no_incidents", "No Incidents"],
  ["perfect_attendance", "Perfect Attendance"],
  ["on_time", "On Time"],
  ["points_earned", "Points Earned"],
  ["custom", "Custom"],
] as [string, string][];

const ALERT_TYPES = [
  ["critical_incident", "Critical Incident"],
  ["pattern_detected", "Pattern Detected"],
  ["escalation", "Escalation"],
  ["attendance", "Attendance"],
  ["parent_contact", "Parent Contact"],
  ["follow_up", "Follow Up"],
  ["other", "Other"],
] as [string, string][];

const ALERT_PRIORITIES = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
  ["urgent", "Urgent"],
] as [string, string][];

const ALERT_STATUS = [
  ["active", "Active"],
  ["acknowledged", "Acknowledged"],
  ["resolved", "Resolved"],
] as [string, string][];

const APPEAL_TYPES = [
  ["incident", "Incident"],
  ["consequence", "Consequence"],
  ["suspension", "Suspension"],
] as [string, string][];

const APPEAL_STATUS = [
  ["submitted", "Submitted"],
  ["under_review", "Under Review"],
  ["approved", "Approved"],
  ["denied", "Denied"],
  ["withdrawn", "Withdrawn"],
] as [string, string][];

const APPEAL_DECISIONS = [
  ["upheld", "Upheld"],
  ["modified", "Modified"],
  ["overturned", "Overturned"],
  ["reduced", "Reduced"],
] as [string, string][];

const NOTIFICATION_TYPES = [
  ["incident", "Incident"],
  ["consequence", "Consequence"],
  ["suspension", "Suspension"],
  ["meeting", "Meeting"],
  ["goal_update", "Goal Update"],
  ["positive", "Positive"],
  ["other", "Other"],
] as [string, string][];

const NOTIFICATION_STATUS = [
  ["pending", "Pending"],
  ["sent", "Sent"],
  ["delivered", "Delivered"],
  ["failed", "Failed"],
  ["acknowledged", "Acknowledged"],
] as [string, string][];

const DELIVERY_METHODS = [
  ["email", "Email"],
  ["sms", "SMS"],
  ["push", "Push"],
  ["phone", "Phone"],
  ["letter", "Letter"],
  ["in_app", "In-App"],
] as [string, string][];

const REPORT_TYPES = [
  ["daily", "Daily"],
  ["weekly", "Weekly"],
  ["monthly", "Monthly"],
  ["quarterly", "Quarterly"],
  ["annual", "Annual"],
  ["custom", "Custom"],
] as [string, string][];

const REWARD_TYPES = [
  ["physical", "Physical"],
  ["privilege", "Privilege"],
  ["experience", "Experience"],
  ["certificate", "Certificate"],
  ["digital", "Digital"],
  ["other", "Other"],
] as [string, string][];

const REWARD_AVAILABILITY = [
  ["always", "Always"],
  ["limited", "Limited"],
  ["seasonal", "Seasonal"],
  ["event", "Event"],
] as [string, string][];

const REDEMPTION_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["fulfilled", "Fulfilled"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const HOUSE_ROLES = [
  ["captain", "Captain"],
  ["vice_captain", "Vice Captain"],
  ["member", "Member"],
] as [string, string][];

const LEADERBOARD_TYPES = [
  ["individual", "Individual"],
  ["class", "Class"],
  ["house", "House"],
  ["grade", "Grade"],
  ["overall", "Overall"],
] as [string, string][];

const LEADERBOARD_PERIODS = [
  ["weekly", "Weekly"],
  ["monthly", "Monthly"],
  ["quarterly", "Quarterly"],
  ["semester", "Semester"],
  ["annual", "Annual"],
  ["all_time", "All Time"],
] as [string, string][];

const REPORT_PERIODS = [
  ["weekly", "Weekly"],
  ["biweekly", "Biweekly"],
  ["monthly", "Monthly"],
  ["quarterly", "Quarterly"],
  ["semester", "Semester"],
  ["annual", "Annual"],
] as [string, string][];

const REPORT_CARD_STATUS = [
  ["draft", "Draft"],
  ["generating", "Generating"],
  ["completed", "Completed"],
  ["sent", "Sent"],
] as [string, string][];

const PLAN_TYPES = [
  ["bip", "BIP"],
  ["fba", "FBA"],
  ["safety_plan", "Safety Plan"],
  ["behavior_support", "Behavior Support"],
  ["other", "Other"],
] as [string, string][];

const PLAN_STATUS = [
  ["draft", "Draft"],
  ["active", "Active"],
  ["under_review", "Under Review"],
  ["completed", "Completed"],
  ["archived", "Archived"],
] as [string, string][];

const REVIEW_FREQUENCIES = [
  ["weekly", "Weekly"],
  ["biweekly", "Biweekly"],
  ["monthly", "Monthly"],
  ["quarterly", "Quarterly"],
] as [string, string][];

const MTSS_TIERS = [
  ["tier_1", "Tier 1"],
  ["tier_2", "Tier 2"],
  ["tier_3", "Tier 3"],
] as [string, string][];

const MTSS_STATUSES = [
  ["active", "Active"],
  ["monitoring", "Monitoring"],
  ["progressing", "Progressing"],
  ["referral", "Referral"],
  ["exited", "Exited"],
] as [string, string][];

const MOODS = [
  ["great", "Great"],
  ["good", "Good"],
  ["okay", "Okay"],
  ["sad", "Sad"],
  ["angry", "Angry"],
  ["anxious", "Anxious"],
  ["sick", "Sick"],
] as [string, string][];

const CHECKIN_FREQUENCIES = [
  ["daily", "Daily"],
  ["weekly", "Weekly"],
  ["as_needed", "As Needed"],
] as [string, string][];

const BADGE_TYPES = [
  ["incident_free", "Incident Free"],
  ["points_milestone", "Points Milestone"],
  ["attendance", "Attendance"],
  ["improvement", "Improvement"],
  ["leadership", "Leadership"],
  ["service", "Service"],
  ["academic", "Academic"],
  ["custom", "Custom"],
] as [string, string][];

const SMS_ALERT_TYPES = [
  ["critical_incident", "Critical Incident"],
  ["suspension", "Suspension"],
  ["violent_incident", "Violent Incident"],
  ["substance", "Substance"],
  ["bullying", "Bullying"],
  ["other", "Other"],
] as [string, string][];

const SMS_STATUS = [
  ["pending", "Pending"],
  ["sent", "Sent"],
  ["delivered", "Delivered"],
  ["failed", "Failed"],
] as [string, string][];

const ESCALATION_TRIGGERS = [
  ["incident_count", "Incident Count"],
  ["point_threshold", "Point Threshold"],
  ["consecutive_days", "Consecutive Days"],
  ["same_type", "Same Type"],
  ["severity", "Severity"],
] as [string, string][];

const ESCALATION_ACTIONS = [
  ["warning", "Warning"],
  ["parent_contact", "Parent Contact"],
  ["detention", "Detention"],
  ["suspension", "Suspension"],
  ["meeting", "Meeting"],
  ["intervention", "Intervention"],
  ["counseling", "Counseling"],
] as [string, string][];

const LINK_TYPES = [
  ["tardy_behavior", "Tardy-Behavior"],
  ["absence_behavior", "Absence-Behavior"],
  ["attendance_reward", "Attendance Reward"],
  ["attendance_consequence", "Attendance Consequence"],
] as [string, string][];

const CORRELATION_TYPES = [
  ["gpa_impact", "GPA Impact"],
  ["grade_trend", "Grade Trend"],
  ["class_performance", "Class Performance"],
  ["assignment_completion", "Assignment Completion"],
] as [string, string][];

const CHART_TYPES = [
  ["incidents_by_type", "Incidents by Type"],
  ["incidents_by_severity", "Incidents by Severity"],
  ["incidents_by_grade", "Incidents by Grade"],
  ["incidents_by_month", "Incidents by Month"],
  ["points_distribution", "Points Distribution"],
  ["top_earners", "Top Earners"],
  ["behavior_trends", "Behavior Trends"],
  ["house_rankings", "House Rankings"],
  ["teacher_comparison", "Teacher Comparison"],
  ["student_timeline", "Student Timeline"],
] as [string, string][];

const RISK_LEVELS = [
  ["low", "Low"],
  ["moderate", "Moderate"],
  ["high", "High"],
  ["critical", "Critical"],
] as [string, string][];

const PREDICTION_TYPES = [
  ["behavior_risk", "Behavior Risk"],
  ["dropout_risk", "Dropout Risk"],
  ["academic_risk", "Academic Risk"],
  ["attendance_risk", "Attendance Risk"],
] as [string, string][];

const SURVEY_TYPES = [
  ["wellness", "Wellness"],
  ["mood", "Mood"],
  ["stress", "Stress"],
  ["belonging", "Belonging"],
  ["safety", "Safety"],
  ["support", "Support"],
  ["custom", "Custom"],
] as [string, string][];

const SURVEY_STATUS = [
  ["draft", "Draft"],
  ["active", "Active"],
  ["closed", "Closed"],
] as [string, string][];

const MATERIAL_TYPES = [
  ["document", "Document"],
  ["video", "Video"],
  ["presentation", "Presentation"],
  ["course", "Course"],
  ["workshop", "Workshop"],
  ["other", "Other"],
] as [string, string][];

const AUDIENCES = [
  ["all_staff", "All Staff"],
  ["teachers", "Teachers"],
  ["administrators", "Administrators"],
  ["counselors", "Counselors"],
  ["support_staff", "Support Staff"],
] as [string, string][];

const TRAINING_STATUS = [
  ["not_started", "Not Started"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
] as [string, string][];

const POLICY_CATEGORIES = [
  ["code_of_conduct", "Code of Conduct"],
  ["discipline", "Discipline"],
  ["bullying", "Bullying"],
  ["technology", "Technology"],
  ["attendance", "Attendance"],
  ["dress_code", "Dress Code"],
  ["other", "Other"],
] as [string, string][];

const CHALLENGE_TYPES = [
  ["incident_free", "Incident Free"],
  ["perfect_attendance", "Perfect Attendance"],
  ["on_time", "On Time"],
  ["points_earned", "Points Earned"],
  ["custom", "Custom"],
] as [string, string][];

const CHALLENGE_STATUS = [
  ["upcoming", "Upcoming"],
  ["active", "Active"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const ACCESS_LEVELS = [
  ["view_only", "View Only"],
  ["view_communicate", "View & Communicate"],
  ["full_access", "Full Access"],
] as [string, string][];

// ─── Entity configs (49 tabs) ────────────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  categories: {
    key: "categories",
    label: "Category",
    icon: TagIcon,
    endpoint: "categories",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "category_type",
        label: "Type",
        type: "select",
        options: CATEGORY_TYPES,
        subtitle: true,
        badge: true,
      },
      { key: "points_value", label: "Points", type: "number", card: true },
      { key: "requires_incident", label: "Requires Incident", type: "bool", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "color", label: "Color", card: true },
      { key: "icon", label: "Icon", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["name", "category_type", "description"],
  },
  incidents: {
    key: "incidents",
    label: "Incident",
    icon: ExclamationTriangleIcon,
    endpoint: "incidents",
    titleField: "title",
    subtitleField: "student_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "student_name", label: "Student", subtitle: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "category_name", label: "Category", card: true, skipForm: true },
      { key: "category", label: "Category ID", card: true },
      { key: "severity", label: "Severity", type: "select", options: SEVERITIES, badge: true },
      { key: "severity_display", label: "Severity", card: true, skipForm: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "incident_date", label: "Date", type: "datetime", card: true },
      { key: "location", label: "Location", card: true },
      { key: "reported_by_name", label: "Reported By", card: true, skipForm: true },
      { key: "reported_by", label: "Reported By ID", skipForm: true },
      {
        key: "parents_notified",
        label: "Parents Notified",
        type: "bool",
        card: true,
        skipForm: true,
      },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "action_taken", label: "Action Taken", type: "textarea", full: true },
    ],
    searchKeys: ["title", "student_name", "category_name", "severity", "location"],
  },
  referrals: {
    key: "referrals",
    label: "Referral",
    icon: ArrowPathIcon,
    endpoint: "referrals",
    titleField: "reason",
    subtitleField: "student_name",
    fields: [
      { key: "reason", label: "Reason", main: true },
      { key: "student_name", label: "Student", subtitle: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "referred_to_name", label: "Referred To", card: true, skipForm: true },
      { key: "referred_to", label: "Referred To ID", card: true },
      { key: "status", label: "Status", type: "select", options: REFERRAL_STATUS, badge: true },
      { key: "notes", label: "Notes", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["reason", "student_name", "referred_to_name", "status"],
  },
  points: {
    key: "points",
    label: "Behavior Point",
    icon: BoltIcon,
    endpoint: "points",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "category_name", label: "Category", card: true, skipForm: true },
      { key: "category", label: "Category ID", card: true },
      { key: "points", label: "Points", type: "number", card: true },
      { key: "point_type", label: "Type", type: "select", options: POINT_TYPES, badge: true },
      { key: "point_type_display", label: "Type", card: true, skipForm: true },
      { key: "reason", label: "Reason", type: "textarea", full: true, card: true },
      { key: "awarded_by_name", label: "Awarded By", card: true, skipForm: true },
      { key: "awarded_by", label: "Awarded By ID", skipForm: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "is_redeemed", label: "Redeemed", type: "bool", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "category_name", "reason", "point_type"],
  },
  "point-balances": {
    key: "point-balances",
    label: "Point Balance",
    icon: ScaleIcon,
    endpoint: "point-balances",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "current_balance", label: "Balance", type: "number", card: true, badge: true },
      { key: "total_earned", label: "Earned", type: "number", card: true },
      { key: "total_deducted", label: "Deducted", type: "number", card: true },
      {
        key: "lifetime_earned",
        label: "Lifetime Earned",
        type: "number",
        card: true,
        skipForm: true,
      },
      {
        key: "lifetime_deducted",
        label: "Lifetime Deducted",
        type: "number",
        card: true,
        skipForm: true,
      },
      {
        key: "last_activity_at",
        label: "Last Activity",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
    searchKeys: ["student_name"],
  },
  consequences: {
    key: "consequences",
    label: "Consequence",
    icon: ScaleIcon,
    endpoint: "consequences",
    titleField: "student_name",
    subtitleField: "description",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      {
        key: "consequence_type",
        label: "Type",
        type: "select",
        options: CONSEQUENCE_TYPES,
        badge: true,
      },
      { key: "consequence_type_display", label: "Type", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: CONSEQUENCE_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "issued_date", label: "Issued", type: "date", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "duration_hours", label: "Hours", type: "number", card: true },
      { key: "duration_days", label: "Days", type: "number", card: true },
      { key: "location", label: "Location", card: true },
      { key: "issued_by_name", label: "Issued By", card: true, skipForm: true },
      { key: "issued_by", label: "Issued By ID", skipForm: true },
      { key: "parents_notified", label: "Parents Notified", type: "bool", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "conditions", label: "Conditions", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "consequence_type", "status", "location"],
  },
  merits: {
    key: "merits",
    label: "Merit",
    icon: CheckBadgeIcon,
    endpoint: "merits",
    titleField: "title",
    subtitleField: "student_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "student_name", label: "Student", subtitle: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "merit_type", label: "Type", type: "select", options: MERIT_TYPES, badge: true },
      { key: "merit_type_display", label: "Type", card: true, skipForm: true },
      { key: "points", label: "Points", type: "number", card: true },
      { key: "awarded_by_name", label: "Awarded By", card: true, skipForm: true },
      { key: "awarded_by", label: "Awarded By ID", skipForm: true },
      { key: "awarded_date", label: "Date", type: "date", card: true },
      { key: "is_public", label: "Public", type: "bool", card: true },
      { key: "certificate_generated", label: "Certificate", type: "bool", card: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["title", "student_name", "merit_type"],
  },
  detentions: {
    key: "detentions",
    label: "Detention",
    icon: ClockIcon,
    endpoint: "detentions",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      {
        key: "detention_type",
        label: "Type",
        type: "select",
        options: DETENTION_TYPES,
        badge: true,
      },
      { key: "detention_type_display", label: "Type", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: DETENTION_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "consequence", label: "Consequence ID", card: true },
      { key: "scheduled_date", label: "Date", type: "date", card: true },
      { key: "start_time", label: "Start", card: true },
      { key: "end_time", label: "End", card: true },
      { key: "location", label: "Location", card: true },
      { key: "supervisor_name", label: "Supervisor", card: true, skipForm: true },
      { key: "supervisor", label: "Supervisor ID", card: true },
      { key: "attended", label: "Attended", type: "bool", badge: true },
      { key: "attended_at", label: "Attended At", type: "datetime", card: true, skipForm: true },
      { key: "parents_notified", label: "Parents Notified", type: "bool", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "detention_type", "status", "location"],
  },
  suspensions: {
    key: "suspensions",
    label: "Suspension",
    icon: NoSymbolIcon,
    endpoint: "suspensions",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      {
        key: "suspension_type",
        label: "Type",
        type: "select",
        options: SUSPENSION_TYPES,
        badge: true,
      },
      { key: "suspension_type_display", label: "Type", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: SUSPENSION_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "consequence", label: "Consequence ID", card: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "actual_return_date", label: "Returned", type: "date", card: true },
      { key: "duration_days_computed", label: "Days", type: "number", card: true, skipForm: true },
      { key: "issued_by_name", label: "Issued By", card: true, skipForm: true },
      { key: "issued_by", label: "Issued By ID", skipForm: true },
      { key: "meeting_required", label: "Meeting Required", type: "bool", card: true },
      { key: "meeting_date", label: "Meeting Date", type: "date", card: true },
      { key: "parent_signature_required", label: "Signature Required", type: "bool", card: true },
      { key: "parent_signature_obtained", label: "Signature Obtained", type: "bool", badge: true },
      { key: "make_up_work_required", label: "Make-up Work", type: "bool", card: true },
      {
        key: "conditions_for_return",
        label: "Conditions for Return",
        type: "textarea",
        full: true,
      },
      { key: "meeting_notes", label: "Meeting Notes", type: "textarea", full: true },
      { key: "make_up_work_notes", label: "Make-up Notes", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "suspension_type", "status"],
  },
  contracts: {
    key: "contracts",
    label: "Behavior Contract",
    icon: DocumentTextIcon,
    endpoint: "contracts",
    titleField: "title",
    subtitleField: "student_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "student_name", label: "Student", subtitle: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "status", label: "Status", type: "select", options: CONTRACT_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "review_dates", label: "Review Dates", card: true },
      { key: "student_signed", label: "Student Signed", type: "bool", badge: true },
      { key: "parent_signed", label: "Parent Signed", type: "bool", badge: true },
      { key: "administrator_signed", label: "Admin Signed", type: "bool", badge: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", skipForm: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "goals", label: "Goals", type: "textarea", full: true },
      {
        key: "consequences_for_violation",
        label: "Violation Consequences",
        type: "textarea",
        full: true,
      },
      { key: "rewards_for_compliance", label: "Compliance Rewards", type: "textarea", full: true },
      { key: "progress_notes", label: "Progress Notes", type: "textarea", full: true },
    ],
    searchKeys: ["title", "student_name", "status"],
  },
  "witness-statements": {
    key: "witness-statements",
    label: "Witness Statement",
    icon: ChatBubbleLeftRightIcon,
    endpoint: "witness-statements",
    titleField: "witness_name",
    fields: [
      { key: "witness_name", label: "Witness", main: true },
      { key: "witness_type", label: "Type", card: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "witness_student", label: "Witness Student", card: true },
      { key: "witness_contact", label: "Contact", card: true },
      { key: "statement_date", label: "Date", type: "date", card: true },
      { key: "collected_by_name", label: "Collected By", card: true, skipForm: true },
      { key: "collected_by", label: "Collected By ID", card: true },
      { key: "is_confidential", label: "Confidential", type: "bool", badge: true },
      { key: "statement", label: "Statement", type: "textarea", full: true, card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["witness_name", "witness_type", "statement"],
  },
  evidence: {
    key: "evidence",
    label: "Evidence",
    icon: PaperClipIcon,
    endpoint: "evidence",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "evidence_type", label: "Type", type: "select", options: EVIDENCE_TYPES, badge: true },
      { key: "evidence_type_display", label: "Type", card: true, skipForm: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "file_url", label: "File URL", card: true },
      { key: "file_size", label: "File Size", type: "number", card: true },
      { key: "uploaded_by_name", label: "Uploaded By", card: true, skipForm: true },
      { key: "uploaded_by", label: "Uploaded By ID", card: true },
      { key: "is_confidential", label: "Confidential", type: "bool", badge: true },
      { key: "uploaded_at", label: "Uploaded", type: "datetime", card: true, skipForm: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["title", "evidence_type", "description"],
  },
  rubrics: {
    key: "rubrics",
    label: "Rubric",
    icon: TableCellsIcon,
    endpoint: "rubrics",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "applies_to", label: "Applies To", card: true },
      { key: "min_score", label: "Min Score", type: "number", card: true },
      { key: "max_score", label: "Max Score", type: "number", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", skipForm: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["name", "applies_to", "description"],
  },
  "rubric-levels": {
    key: "rubric-levels",
    label: "Rubric Level",
    icon: TableCellsIcon,
    endpoint: "rubric-levels",
    titleField: "label",
    subtitleField: "rubric_name",
    fields: [
      { key: "label", label: "Label", main: true },
      { key: "rubric_name", label: "Rubric", subtitle: true, skipForm: true },
      { key: "rubric", label: "Rubric ID", card: true },
      { key: "score", label: "Score", type: "number", card: true },
      { key: "color", label: "Color", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["label", "rubric_name", "description"],
  },
  "hall-passes": {
    key: "hall-passes",
    label: "Hall Pass",
    icon: TicketIcon,
    endpoint: "hall-passes",
    titleField: "student_name",
    subtitleField: "to_destination",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "pass_type", label: "Type", type: "select", options: PASS_TYPES, badge: true },
      { key: "pass_type_display", label: "Type", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: PASS_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "from_class", label: "From Class", card: true },
      { key: "to_destination", label: "Destination", subtitle: true, card: true },
      { key: "approved_by_name", label: "Approved By", card: true, skipForm: true },
      { key: "approved_by", label: "Approved By ID", card: true },
      { key: "issued_at", label: "Issued", type: "datetime", card: true },
      { key: "expected_return_at", label: "Expected Return", type: "datetime", card: true },
      { key: "actual_return_at", label: "Returned", type: "datetime", card: true, skipForm: true },
      { key: "is_late", label: "Late", type: "bool", badge: true, skipForm: true },
      { key: "minutes_late", label: "Minutes Late", type: "number", card: true, skipForm: true },
      { key: "reason", label: "Reason", type: "textarea", full: true, card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "pass_type", "to_destination", "status"],
  },
  tardies: {
    key: "tardies",
    label: "Tardy",
    icon: ClockIcon,
    endpoint: "tardies",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "tardy_type", label: "Type", type: "select", options: TARDY_TYPES, badge: true },
      { key: "tardy_type_display", label: "Type", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: TARDY_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "scheduled_time", label: "Scheduled", card: true },
      { key: "arrival_time", label: "Arrival", card: true },
      { key: "minutes_late", label: "Minutes Late", type: "number", card: true },
      { key: "class_name", label: "Class", card: true },
      { key: "teacher_name", label: "Teacher", card: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", card: true },
      { key: "parent_contacted", label: "Parent Contacted", type: "bool", card: true },
      { key: "is_part_of_pattern", label: "Pattern", type: "bool", badge: true },
      { key: "reason", label: "Reason", type: "textarea", full: true, card: true },
      { key: "pattern_notes", label: "Pattern Notes", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "tardy_type", "class_name", "status"],
  },
  goals: {
    key: "goals",
    label: "Behavior Goal",
    icon: FlagIcon,
    endpoint: "goals",
    titleField: "title",
    subtitleField: "student_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "student_name", label: "Student", subtitle: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "goal_type", label: "Type", type: "select", options: GOAL_TYPES, badge: true },
      { key: "goal_type_display", label: "Type", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: GOAL_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "target_value", label: "Target", type: "number", card: true },
      { key: "current_value", label: "Current", type: "number", card: true },
      {
        key: "progress_percentage",
        label: "Progress %",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "support_plan", label: "Support Plan", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["title", "student_name", "goal_type", "status"],
  },
  streaks: {
    key: "streaks",
    label: "Streak",
    icon: FireIcon,
    endpoint: "streaks",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "streak_type", label: "Type", type: "select", options: STREAK_TYPES, badge: true },
      { key: "streak_type_display", label: "Type", card: true, skipForm: true },
      { key: "current_streak", label: "Current", type: "number", card: true },
      { key: "longest_streak", label: "Longest", type: "number", card: true },
      { key: "streak_unit", label: "Unit", card: true },
      { key: "streak_started_at", label: "Started", type: "datetime", card: true, skipForm: true },
      {
        key: "last_activity_at",
        label: "Last Activity",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      { key: "milestone_7", label: "7 Milestone", type: "bool", card: true },
      { key: "milestone_30", label: "30 Milestone", type: "bool", card: true },
      { key: "milestone_90", label: "90 Milestone", type: "bool", card: true },
      { key: "milestone_180", label: "180 Milestone", type: "bool", card: true },
      { key: "milestone_365", label: "365 Milestone", type: "bool", card: true },
      { key: "reward_earned", label: "Reward Earned", type: "bool", badge: true },
      { key: "reward_description", label: "Reward", card: true },
    ],
    searchKeys: ["student_name", "streak_type"],
  },
  alerts: {
    key: "alerts",
    label: "Alert",
    icon: BellAlertIcon,
    endpoint: "alerts",
    titleField: "title",
    subtitleField: "student_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "student_name", label: "Student", subtitle: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "alert_type", label: "Type", type: "select", options: ALERT_TYPES, badge: true },
      { key: "alert_type_display", label: "Type", card: true, skipForm: true },
      {
        key: "priority",
        label: "Priority",
        type: "select",
        options: ALERT_PRIORITIES,
        badge: true,
      },
      { key: "priority_display", label: "Priority", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: ALERT_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "acknowledged_by_name", label: "Acknowledged By", card: true, skipForm: true },
      { key: "acknowledged_by", label: "Acknowledged By ID", card: true },
      {
        key: "acknowledged_at",
        label: "Acknowledged",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      { key: "resolved_at", label: "Resolved", type: "datetime", card: true, skipForm: true },
      { key: "notification_sent", label: "Notified", type: "bool", card: true, skipForm: true },
      { key: "message", label: "Message", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["title", "student_name", "alert_type", "priority", "status"],
  },
  appeals: {
    key: "appeals",
    label: "Appeal",
    icon: ScaleIcon,
    endpoint: "appeals",
    titleField: "student_name",
    subtitleField: "reason",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "appeal_type", label: "Type", type: "select", options: APPEAL_TYPES, badge: true },
      { key: "appeal_type_display", label: "Type", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: APPEAL_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      {
        key: "decision",
        label: "Decision",
        type: "select",
        options: APPEAL_DECISIONS,
        badge: true,
      },
      { key: "decision_display", label: "Decision", card: true, skipForm: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "consequence", label: "Consequence ID", card: true },
      { key: "suspension", label: "Suspension ID", card: true },
      { key: "reviewed_by_name", label: "Reviewed By", card: true, skipForm: true },
      { key: "reviewed_by", label: "Reviewed By ID", card: true },
      { key: "reviewed_at", label: "Reviewed", type: "datetime", card: true, skipForm: true },
      { key: "hearing_date", label: "Hearing", type: "date", card: true },
      { key: "parent_notified", label: "Parent Notified", type: "bool", card: true },
      { key: "reason", label: "Reason", type: "textarea", full: true, card: true },
      { key: "supporting_evidence", label: "Supporting Evidence", type: "textarea", full: true },
      { key: "requested_outcome", label: "Requested Outcome", type: "textarea", full: true },
      { key: "decision_notes", label: "Decision Notes", type: "textarea", full: true },
      { key: "parent_statement", label: "Parent Statement", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "appeal_type", "status", "reason"],
  },
  "parent-notifications": {
    key: "parent-notifications",
    label: "Parent Notification",
    icon: EnvelopeIcon,
    endpoint: "parent-notifications",
    titleField: "student_name",
    subtitleField: "subject",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "subject", label: "Subject", subtitle: true, card: true },
      {
        key: "notification_type",
        label: "Type",
        type: "select",
        options: NOTIFICATION_TYPES,
        badge: true,
      },
      { key: "notification_type_display", label: "Type", card: true, skipForm: true },
      {
        key: "delivery_method",
        label: "Method",
        type: "select",
        options: DELIVERY_METHODS,
        badge: true,
      },
      { key: "delivery_method_display", label: "Method", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: NOTIFICATION_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "consequence", label: "Consequence ID", card: true },
      { key: "parent_email", label: "Email", card: true },
      { key: "parent_phone", label: "Phone", card: true },
      { key: "sent_at", label: "Sent", type: "datetime", card: true, skipForm: true },
      { key: "delivered_at", label: "Delivered", type: "datetime", card: true, skipForm: true },
      {
        key: "acknowledged_at",
        label: "Acknowledged",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      { key: "sent_by_name", label: "Sent By", card: true, skipForm: true },
      { key: "sent_by", label: "Sent By ID", skipForm: true },
      { key: "message", label: "Message", type: "textarea", full: true, card: true },
      { key: "parent_response", label: "Parent Response", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "subject", "notification_type", "status"],
  },
  analytics: {
    key: "analytics",
    label: "Analytics Report",
    icon: ChartBarIcon,
    endpoint: "analytics",
    titleField: "report_type",
    fields: [
      {
        key: "report_type",
        label: "Type",
        type: "select",
        options: REPORT_TYPES,
        main: true,
        badge: true,
      },
      { key: "report_type_display", label: "Type", card: true, skipForm: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "total_incidents", label: "Incidents", type: "number", card: true },
      { key: "total_points_awarded", label: "Points Awarded", type: "number", card: true },
      { key: "total_points_deducted", label: "Points Deducted", type: "number", card: true },
      { key: "total_consequences", label: "Consequences", type: "number", card: true },
      { key: "total_suspension_days", label: "Suspension Days", type: "number", card: true },
      { key: "total_detention_hours", label: "Detention Hours", type: "number", card: true },
      { key: "generated_by_name", label: "Generated By", card: true, skipForm: true },
      { key: "generated_by", label: "Generated By ID", skipForm: true },
      { key: "generated_at", label: "Generated", type: "datetime", card: true, skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["report_type", "notes"],
  },
  rewards: {
    key: "rewards",
    label: "Reward",
    icon: GiftIcon,
    endpoint: "rewards",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "reward_type",
        label: "Type",
        type: "select",
        options: REWARD_TYPES,
        subtitle: true,
        badge: true,
      },
      { key: "reward_type_display", label: "Type", card: true, skipForm: true },
      { key: "points_cost", label: "Points Cost", type: "number", card: true },
      {
        key: "availability",
        label: "Availability",
        type: "select",
        options: REWARD_AVAILABILITY,
        badge: true,
      },
      { key: "availability_display", label: "Availability", card: true, skipForm: true },
      { key: "stock_quantity", label: "Stock", type: "number", card: true },
      { key: "max_per_student", label: "Max/Student", type: "number", card: true },
      { key: "total_redeemed", label: "Redeemed", type: "number", card: true, skipForm: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "is_available", label: "Available", type: "bool", badge: true, skipForm: true },
      { key: "requires_approval", label: "Requires Approval", type: "bool", card: true },
      { key: "available_from", label: "From", type: "date", card: true },
      { key: "available_until", label: "Until", type: "date", card: true },
      { key: "image_url", label: "Image", card: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", skipForm: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["name", "reward_type", "description"],
  },
  redemptions: {
    key: "redemptions",
    label: "Redemption",
    icon: ShoppingBagIcon,
    endpoint: "redemptions",
    titleField: "student_name",
    subtitleField: "reward_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "reward_name", label: "Reward", subtitle: true, skipForm: true },
      { key: "reward", label: "Reward ID", card: true },
      { key: "points_spent", label: "Points Spent", type: "number", card: true },
      { key: "status", label: "Status", type: "select", options: REDEMPTION_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "approved_by_name", label: "Approved By", card: true, skipForm: true },
      { key: "approved_by", label: "Approved By ID", card: true },
      { key: "approved_at", label: "Approved", type: "datetime", card: true, skipForm: true },
      { key: "fulfilled_at", label: "Fulfilled", type: "datetime", card: true, skipForm: true },
      { key: "redeemed_at", label: "Redeemed", type: "datetime", card: true, skipForm: true },
      { key: "rejection_reason", label: "Rejection Reason", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "reward_name", "status"],
  },
  houses: {
    key: "houses",
    label: "House",
    icon: UserGroupIcon,
    endpoint: "houses",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "total_points", label: "Total Points", type: "number", card: true, badge: true },
      { key: "member_count", label: "Members", type: "number", card: true, skipForm: true },
      { key: "captain_name", label: "Captain", card: true, skipForm: true },
      { key: "captain", label: "Captain ID", card: true },
      { key: "vice_captain_name", label: "Vice Captain", card: true, skipForm: true },
      { key: "vice_captain", label: "Vice Captain ID", card: true },
      { key: "faculty_advisor_name", label: "Faculty Advisor", card: true, skipForm: true },
      { key: "faculty_advisor", label: "Faculty Advisor ID", card: true },
      { key: "color", label: "Color", card: true },
      { key: "mascot", label: "Mascot", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["name", "description"],
  },
  "house-members": {
    key: "house-members",
    label: "House Member",
    icon: UsersIcon,
    endpoint: "house-members",
    titleField: "student_name",
    subtitleField: "house_name",
    toggleField: "is_active",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "house_name", label: "House", subtitle: true, skipForm: true },
      { key: "house", label: "House ID", card: true },
      { key: "role", label: "Role", type: "select", options: HOUSE_ROLES, badge: true },
      { key: "role_display", label: "Role", card: true, skipForm: true },
      { key: "joined_at", label: "Joined", type: "datetime", card: true, skipForm: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
    ],
    searchKeys: ["student_name", "house_name", "role"],
  },
  leaderboards: {
    key: "leaderboards",
    label: "Leaderboard",
    icon: TrophyIcon,
    endpoint: "leaderboards",
    titleField: "name",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "leaderboard_type",
        label: "Type",
        type: "select",
        options: LEADERBOARD_TYPES,
        badge: true,
      },
      { key: "leaderboard_type_display", label: "Type", card: true, skipForm: true },
      {
        key: "time_period",
        label: "Period",
        type: "select",
        options: LEADERBOARD_PERIODS,
        badge: true,
      },
      { key: "time_period_display", label: "Period", card: true, skipForm: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "total_entries", label: "Entries", type: "number", card: true, skipForm: true },
      { key: "is_published", label: "Published", type: "bool", badge: true },
      { key: "show_on_dashboard", label: "On Dashboard", type: "bool", card: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", skipForm: true },
    ],
    searchKeys: ["name", "leaderboard_type", "time_period"],
  },
  "report-cards": {
    key: "report-cards",
    label: "Behavior Report Card",
    icon: ReceiptPercentIcon,
    endpoint: "report-cards",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      {
        key: "report_period",
        label: "Period",
        type: "select",
        options: REPORT_PERIODS,
        badge: true,
      },
      { key: "report_period_display", label: "Period", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: REPORT_CARD_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "behavior_score", label: "Score", type: "number", card: true, badge: true },
      { key: "behavior_trend", label: "Trend", card: true },
      { key: "total_incidents", label: "Incidents", type: "number", card: true, skipForm: true },
      { key: "total_merits", label: "Merits", type: "number", card: true, skipForm: true },
      { key: "net_points", label: "Net Points", type: "number", card: true, skipForm: true },
      { key: "total_detentions", label: "Detentions", type: "number", card: true, skipForm: true },
      {
        key: "total_suspensions",
        label: "Suspensions",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "total_tardies", label: "Tardies", type: "number", card: true, skipForm: true },
      { key: "sent_to_parent", label: "Sent to Parent", type: "bool", badge: true, skipForm: true },
      { key: "generated_by_name", label: "Generated By", card: true, skipForm: true },
      { key: "generated_by", label: "Generated By ID", skipForm: true },
      { key: "strengths", label: "Strengths", type: "textarea", full: true, card: true },
      { key: "areas_for_growth", label: "Areas for Growth", type: "textarea", full: true },
      { key: "teacher_comments", label: "Teacher Comments", type: "textarea", full: true },
      { key: "admin_comments", label: "Admin Comments", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "report_period", "status"],
  },
  "intervention-plans": {
    key: "intervention-plans",
    label: "Intervention Plan",
    icon: LifebuoyIcon,
    endpoint: "intervention-plans",
    titleField: "title",
    subtitleField: "student_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "student_name", label: "Student", subtitle: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "plan_type", label: "Type", type: "select", options: PLAN_TYPES, badge: true },
      { key: "plan_type_display", label: "Type", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: PLAN_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "target_behavior", label: "Target Behavior", card: true },
      { key: "case_manager_name", label: "Case Manager", card: true, skipForm: true },
      { key: "case_manager", label: "Case Manager ID", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      {
        key: "review_frequency",
        label: "Review Freq",
        type: "select",
        options: REVIEW_FREQUENCIES,
        card: true,
      },
      { key: "next_review_date", label: "Next Review", type: "date", card: true },
      { key: "goals_met", label: "Goals Met", type: "number", card: true, skipForm: true },
      {
        key: "goals_remaining",
        label: "Goals Remaining",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "parent_signature_required", label: "Signature Required", type: "bool", card: true },
      { key: "parent_signed", label: "Parent Signed", type: "bool", badge: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", skipForm: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "function_of_behavior", label: "Function of Behavior", type: "textarea", full: true },
      { key: "prevention_strategies", label: "Prevention", type: "textarea", full: true },
      { key: "teaching_strategies", label: "Teaching", type: "textarea", full: true },
      { key: "reinforcement_strategies", label: "Reinforcement", type: "textarea", full: true },
      { key: "crisis_plan", label: "Crisis Plan", type: "textarea", full: true },
      { key: "progress_notes", label: "Progress Notes", type: "textarea", full: true },
    ],
    searchKeys: ["title", "student_name", "plan_type", "status"],
  },
  mtss: {
    key: "mtss",
    label: "MTSS",
    icon: AcademicCapIcon,
    endpoint: "mtss",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "tier_level", label: "Tier", type: "select", options: MTSS_TIERS, badge: true },
      { key: "tier_level_display", label: "Tier", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: MTSS_STATUSES, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "referral_date", label: "Referral Date", type: "date", card: true },
      { key: "referred_by_name", label: "Referred By", card: true, skipForm: true },
      { key: "referred_by", label: "Referred By ID", card: true },
      { key: "case_manager_name", label: "Case Manager", card: true, skipForm: true },
      { key: "case_manager", label: "Case Manager ID", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "review_date", label: "Review", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "outcome_date", label: "Outcome Date", type: "date", card: true },
      { key: "referral_reason", label: "Reason", type: "textarea", full: true, card: true },
      { key: "interventions", label: "Interventions", type: "textarea", full: true },
      { key: "supports", label: "Supports", type: "textarea", full: true },
      { key: "goals", label: "Goals", type: "textarea", full: true },
      { key: "progress_data", label: "Progress Data", type: "textarea", full: true },
      { key: "outcome_notes", label: "Outcome Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "tier_level", "status"],
  },
  "sel-checkins": {
    key: "sel-checkins",
    label: "SEL Check-In",
    icon: HeartIcon,
    endpoint: "sel-checkins",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "mood", label: "Mood", type: "select", options: MOODS, badge: true },
      { key: "mood_display", label: "Mood", card: true, skipForm: true },
      { key: "energy_level", label: "Energy (1-5)", type: "number", card: true },
      { key: "stress_level", label: "Stress (1-5)", type: "number", card: true },
      { key: "sleep_quality", label: "Sleep (1-5)", type: "number", card: true },
      { key: "ate_breakfast", label: "Ate Breakfast", type: "bool", card: true },
      { key: "needs_help", label: "Needs Help", type: "bool", badge: true },
      { key: "help_type", label: "Help Type", card: true },
      { key: "follow_up_needed", label: "Follow-up Needed", type: "bool", badge: true },
      { key: "follow_up_completed", label: "Follow-up Done", type: "bool", card: true },
      { key: "check_in_date", label: "Date", type: "date", card: true },
      { key: "check_in_time", label: "Time", card: true },
      { key: "responded_by_name", label: "Responded By", card: true, skipForm: true },
      { key: "responded_by", label: "Responded By ID", card: true },
      { key: "responded_at", label: "Responded At", type: "datetime", card: true, skipForm: true },
      {
        key: "how_are_you_feeling",
        label: "How Are You Feeling",
        type: "textarea",
        full: true,
        card: true,
      },
      { key: "anything_else", label: "Anything Else", type: "textarea", full: true },
      { key: "staff_response", label: "Staff Response", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "mood", "help_type"],
  },
  "sel-responses": {
    key: "sel-responses",
    label: "SEL Response",
    icon: ChatBubbleLeftRightIcon,
    endpoint: "sel-responses",
    titleField: "staff_name",
    fields: [
      { key: "staff_name", label: "Staff", main: true, skipForm: true },
      { key: "staff", label: "Staff ID", skipForm: true },
      { key: "check_in", label: "Check-In ID", card: true },
      { key: "follow_up_required", label: "Follow-up Required", type: "bool", badge: true },
      { key: "follow_up_date", label: "Follow-up Date", type: "date", card: true },
      { key: "follow_up_completed", label: "Follow-up Done", type: "bool", card: true },
      { key: "created_at", label: "Created", type: "datetime", card: true, skipForm: true },
      { key: "response", label: "Response", type: "textarea", full: true, card: true },
      { key: "action_taken", label: "Action Taken", type: "textarea", full: true },
    ],
    searchKeys: ["staff_name", "response"],
  },
  "staff-dashboards": {
    key: "staff-dashboards",
    label: "Staff Dashboard",
    icon: PresentationChartBarIcon,
    endpoint: "staff-dashboards",
    titleField: "staff_name",
    fields: [
      { key: "staff_name", label: "Staff", main: true, skipForm: true },
      { key: "staff", label: "Staff ID", skipForm: true },
      { key: "incidents_today", label: "Incidents Today", type: "number", card: true },
      { key: "points_given_today", label: "Points Today", type: "number", card: true },
      { key: "referrals_received_today", label: "Referrals Today", type: "number", card: true },
      { key: "hall_passes_active", label: "Active Passes", type: "number", card: true },
      { key: "incidents_this_week", label: "Incidents Week", type: "number", card: true },
      { key: "points_given_this_week", label: "Points Week", type: "number", card: true },
      { key: "pending_alerts", label: "Pending Alerts", type: "number", card: true },
      { key: "pending_referrals", label: "Pending Referrals", type: "number", card: true },
      { key: "last_refreshed", label: "Refreshed", type: "datetime", card: true, skipForm: true },
      { key: "top_students", label: "Top Students", type: "textarea", full: true, card: true },
      { key: "students_needing_attention", label: "Needs Attention", type: "textarea", full: true },
      { key: "favorite_quick_actions", label: "Quick Actions", type: "textarea", full: true },
    ],
    searchKeys: ["staff_name"],
  },
  badges: {
    key: "badges",
    label: "Badge",
    icon: SparklesIcon,
    endpoint: "badges",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "badge_type",
        label: "Type",
        type: "select",
        options: BADGE_TYPES,
        subtitle: true,
        badge: true,
      },
      { key: "badge_type_display", label: "Type", card: true, skipForm: true },
      { key: "points_required", label: "Points Required", type: "number", card: true },
      { key: "streak_required", label: "Streak Required", type: "number", card: true },
      { key: "incidents_allowed", label: "Incidents Allowed", type: "number", card: true },
      { key: "total_earned", label: "Earned Count", type: "number", card: true, skipForm: true },
      { key: "points_value", label: "Points Value", type: "number", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "is_hidden", label: "Hidden", type: "bool", card: true },
      { key: "icon_url", label: "Icon", card: true },
      { key: "color", label: "Color", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "criteria_description", label: "Criteria", type: "textarea", full: true },
    ],
    searchKeys: ["name", "badge_type", "description"],
  },
  "badge-awards": {
    key: "badge-awards",
    label: "Badge Award",
    icon: CheckBadgeIcon,
    endpoint: "badge-awards",
    titleField: "badge_name",
    subtitleField: "student_name",
    fields: [
      { key: "badge_name", label: "Badge", main: true, skipForm: true },
      { key: "badge", label: "Badge ID", skipForm: true },
      { key: "student_name", label: "Student", subtitle: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "awarded_by_name", label: "Awarded By", card: true, skipForm: true },
      { key: "awarded_by", label: "Awarded By ID", card: true },
      { key: "awarded_at", label: "Awarded", type: "datetime", card: true, skipForm: true },
      { key: "notified", label: "Notified", type: "bool", card: true },
      { key: "is_public", label: "Public", type: "bool", card: true },
      { key: "shared_to_feed", label: "Shared", type: "bool", card: true },
      { key: "reason", label: "Reason", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["badge_name", "student_name", "reason"],
  },
  "sms-alerts": {
    key: "sms-alerts",
    label: "SMS Alert",
    icon: BellAlertIcon,
    endpoint: "sms-alerts",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "alert_type", label: "Type", type: "select", options: SMS_ALERT_TYPES, badge: true },
      { key: "alert_type_display", label: "Type", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: SMS_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "parent_phone", label: "Phone", card: true },
      { key: "parent_name", label: "Parent", card: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "sent_at", label: "Sent", type: "datetime", card: true, skipForm: true },
      { key: "delivered_at", label: "Delivered", type: "datetime", card: true, skipForm: true },
      { key: "error_message", label: "Error", card: true, skipForm: true },
      { key: "sent_by", label: "Sent By", card: true },
      { key: "message", label: "Message", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["student_name", "alert_type", "status", "parent_name"],
  },
  "auto-escalations": {
    key: "auto-escalations",
    label: "Escalation Rule",
    icon: Cog6ToothIcon,
    endpoint: "auto-escalations",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "trigger_type",
        label: "Trigger",
        type: "select",
        options: ESCALATION_TRIGGERS,
        badge: true,
      },
      { key: "trigger_type_display", label: "Trigger", card: true, skipForm: true },
      { key: "trigger_value", label: "Trigger Value", type: "number", card: true },
      { key: "trigger_window_days", label: "Window (days)", type: "number", card: true },
      {
        key: "escalation_action",
        label: "Action",
        type: "select",
        options: ESCALATION_ACTIONS,
        badge: true,
      },
      { key: "escalation_action_display", label: "Action", card: true, skipForm: true },
      { key: "priority", label: "Priority", type: "number", card: true },
      {
        key: "times_triggered",
        label: "Times Triggered",
        type: "number",
        card: true,
        skipForm: true,
      },
      {
        key: "last_triggered_at",
        label: "Last Triggered",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "action_description", label: "Action Description", type: "textarea", full: true },
    ],
    searchKeys: ["name", "trigger_type", "escalation_action"],
  },
  "escalation-logs": {
    key: "escalation-logs",
    label: "Escalation Log",
    icon: SignalIcon,
    endpoint: "escalation-logs",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "escalation_rule_name", label: "Rule", card: true, skipForm: true },
      { key: "escalation_rule", label: "Rule ID", card: true },
      { key: "triggered_at", label: "Triggered", type: "datetime", card: true, skipForm: true },
      { key: "resolved", label: "Resolved", type: "bool", badge: true },
      { key: "resolved_at", label: "Resolved At", type: "datetime", card: true, skipForm: true },
      { key: "action_taken_by_name", label: "Action By", card: true, skipForm: true },
      { key: "action_taken_by", label: "Action By ID", card: true },
      { key: "trigger_data", label: "Trigger Data", type: "textarea", full: true, card: true },
      { key: "action_taken", label: "Action Taken", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "escalation_rule_name", "action_taken"],
  },
  "attendance-links": {
    key: "attendance-links",
    label: "Attendance Link",
    icon: CalendarDaysIcon,
    endpoint: "attendance-links",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "link_type", label: "Type", type: "select", options: LINK_TYPES, badge: true },
      { key: "link_type_display", label: "Type", card: true, skipForm: true },
      { key: "attendance_date", label: "Date", type: "date", card: true },
      { key: "attendance_record_id", label: "Attendance Record", card: true },
      { key: "incident", label: "Incident ID", card: true },
      { key: "behavior_point", label: "Behavior Point", card: true },
      { key: "points_adjusted", label: "Points Adjusted", type: "number", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["student_name", "link_type", "notes"],
  },
  "academic-correlations": {
    key: "academic-correlations",
    label: "Academic Correlation",
    icon: AcademicCapIcon,
    endpoint: "academic-correlations",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      {
        key: "correlation_type",
        label: "Type",
        type: "select",
        options: CORRELATION_TYPES,
        badge: true,
      },
      { key: "correlation_type_display", label: "Type", card: true, skipForm: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "behavior_score", label: "Behavior Score", type: "number", card: true },
      { key: "gpa", label: "GPA", type: "number", card: true },
      { key: "gpa_change", label: "GPA Change", type: "number", card: true },
      { key: "grade_average", label: "Grade Avg", type: "number", card: true },
      { key: "assignment_completion_rate", label: "Completion %", type: "number", card: true },
      { key: "total_incidents", label: "Incidents", type: "number", card: true, skipForm: true },
      { key: "total_merits", label: "Merits", type: "number", card: true, skipForm: true },
      { key: "correlation_strength", label: "Strength", card: true, badge: true },
      { key: "generated_at", label: "Generated", type: "datetime", card: true, skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["student_name", "correlation_type", "correlation_strength"],
  },
  "data-visualizations": {
    key: "data-visualizations",
    label: "Visualization",
    icon: PresentationChartBarIcon,
    endpoint: "data-visualizations",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "chart_type",
        label: "Chart",
        type: "select",
        options: CHART_TYPES,
        subtitle: true,
        badge: true,
      },
      { key: "chart_type_display", label: "Chart", card: true, skipForm: true },
      { key: "date_range_start", label: "From", type: "date", card: true },
      { key: "date_range_end", label: "To", type: "date", card: true },
      { key: "grade_filter", label: "Grade Filter", card: true },
      { key: "teacher_filter", label: "Teacher Filter", card: true },
      { key: "is_public", label: "Public", type: "bool", badge: true },
      { key: "refresh_interval_hours", label: "Refresh (hrs)", type: "number", card: true },
      { key: "last_refreshed", label: "Refreshed", type: "datetime", card: true, skipForm: true },
      { key: "labels", label: "Labels", type: "textarea", full: true, skipForm: true },
      { key: "datasets", label: "Datasets", type: "textarea", full: true, skipForm: true },
      { key: "chart_data", label: "Chart Data", type: "textarea", full: true, skipForm: true },
    ],
    searchKeys: ["title", "chart_type"],
  },
  "predictive-analytics": {
    key: "predictive-analytics",
    label: "Predictive Analytics",
    icon: LightBulbIcon,
    endpoint: "predictive-analytics",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      {
        key: "prediction_type",
        label: "Type",
        type: "select",
        options: PREDICTION_TYPES,
        badge: true,
      },
      { key: "prediction_type_display", label: "Type", card: true, skipForm: true },
      { key: "risk_level", label: "Risk", type: "select", options: RISK_LEVELS, badge: true },
      { key: "risk_level_display", label: "Risk", card: true, skipForm: true },
      { key: "risk_score", label: "Risk Score", type: "number", card: true },
      { key: "confidence_level", label: "Confidence", type: "number", card: true },
      { key: "prediction_date", label: "Predicted", type: "datetime", card: true, skipForm: true },
      { key: "valid_until", label: "Valid Until", type: "date", card: true, skipForm: true },
      { key: "reviewed", label: "Reviewed", type: "bool", badge: true },
      { key: "reviewed_by_name", label: "Reviewed By", card: true, skipForm: true },
      { key: "reviewed_by", label: "Reviewed By ID", card: true },
      { key: "action_taken", label: "Action Taken", type: "textarea", full: true, card: true },
      { key: "risk_factors", label: "Risk Factors", type: "textarea", full: true },
      { key: "protective_factors", label: "Protective Factors", type: "textarea", full: true },
      { key: "predicted_outcome", label: "Predicted Outcome", type: "textarea", full: true },
      {
        key: "recommended_interventions",
        label: "Recommended Interventions",
        type: "textarea",
        full: true,
      },
      { key: "recommended_actions", label: "Recommended Actions", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "prediction_type", "risk_level"],
  },
  "sel-surveys": {
    key: "sel-surveys",
    label: "SEL Survey",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "sel-surveys",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "survey_type",
        label: "Type",
        type: "select",
        options: SURVEY_TYPES,
        subtitle: true,
        badge: true,
      },
      { key: "survey_type_display", label: "Type", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: SURVEY_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "target_grades", label: "Target Grades", card: true },
      { key: "total_responses", label: "Responses", type: "number", card: true, skipForm: true },
      { key: "average_scores", label: "Avg Scores", card: true, skipForm: true },
      { key: "is_anonymous", label: "Anonymous", type: "bool", card: true },
      {
        key: "allow_multiple_submissions",
        label: "Multiple Submissions",
        type: "bool",
        card: true,
      },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", skipForm: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "questions", label: "Questions", type: "textarea", full: true },
    ],
    searchKeys: ["title", "survey_type", "status"],
  },
  "sel-survey-responses": {
    key: "sel-survey-responses",
    label: "Survey Response",
    icon: QueueListIcon,
    endpoint: "sel-survey-responses",
    titleField: "student_name",
    subtitleField: "survey_title",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "survey_title", label: "Survey", subtitle: true, skipForm: true },
      { key: "survey", label: "Survey ID", card: true },
      { key: "overall_score", label: "Score", type: "number", card: true, badge: true },
      { key: "needs_follow_up", label: "Needs Follow-up", type: "bool", badge: true },
      { key: "follow_up_completed", label: "Follow-up Done", type: "bool", card: true },
      { key: "submitted_at", label: "Submitted", type: "datetime", card: true, skipForm: true },
      { key: "responses", label: "Responses", type: "textarea", full: true, card: true },
      { key: "follow_up_notes", label: "Follow-up Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "survey_title"],
  },
  "training-materials": {
    key: "training-materials",
    label: "Training Material",
    icon: BookOpenIcon,
    endpoint: "training-materials",
    titleField: "title",
    toggleField: "is_active",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "material_type",
        label: "Type",
        type: "select",
        options: MATERIAL_TYPES,
        subtitle: true,
        badge: true,
      },
      { key: "material_type_display", label: "Type", card: true, skipForm: true },
      { key: "audience", label: "Audience", type: "select", options: AUDIENCES, badge: true },
      { key: "audience_display", label: "Audience", card: true, skipForm: true },
      { key: "duration_minutes", label: "Duration (min)", type: "number", card: true },
      { key: "views_count", label: "Views", type: "number", card: true, skipForm: true },
      {
        key: "completions_count",
        label: "Completions",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "is_required", label: "Required", type: "bool", badge: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "due_date", label: "Due", type: "date", card: true },
      { key: "file_url", label: "File", card: true },
      { key: "external_url", label: "External URL", card: true },
      { key: "tags", label: "Tags", card: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", skipForm: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "content_text", label: "Content", type: "textarea", full: true },
    ],
    searchKeys: ["title", "material_type", "audience", "tags"],
  },
  "training-completions": {
    key: "training-completions",
    label: "Training Completion",
    icon: CheckBadgeIcon,
    endpoint: "training-completions",
    titleField: "material_title",
    subtitleField: "staff_name",
    fields: [
      { key: "material_title", label: "Material", main: true, skipForm: true },
      { key: "material", label: "Material ID", skipForm: true },
      { key: "staff_name", label: "Staff", subtitle: true, skipForm: true },
      { key: "staff", label: "Staff ID", skipForm: true },
      { key: "status", label: "Status", type: "select", options: TRAINING_STATUS, badge: true },
      { key: "score", label: "Score", type: "number", card: true },
      { key: "started_at", label: "Started", type: "datetime", card: true, skipForm: true },
      { key: "completed_at", label: "Completed", type: "datetime", card: true, skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["material_title", "staff_name", "status"],
  },
  "policy-templates": {
    key: "policy-templates",
    label: "Policy Template",
    icon: LockClosedIcon,
    endpoint: "policy-templates",
    titleField: "title",
    toggleField: "is_active",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: POLICY_CATEGORIES,
        subtitle: true,
        badge: true,
      },
      { key: "category_display", label: "Category", card: true, skipForm: true },
      { key: "version", label: "Version", card: true },
      { key: "effective_date", label: "Effective", type: "date", card: true },
      { key: "review_date", label: "Review", type: "date", card: true },
      { key: "downloads_count", label: "Downloads", type: "number", card: true, skipForm: true },
      { key: "is_template", label: "Template", type: "bool", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", skipForm: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "content", label: "Content", type: "textarea", full: true },
    ],
    searchKeys: ["title", "category", "description"],
  },
  "streak-challenges": {
    key: "streak-challenges",
    label: "Streak Challenge",
    icon: FireIcon,
    endpoint: "streak-challenges",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "challenge_type",
        label: "Type",
        type: "select",
        options: CHALLENGE_TYPES,
        subtitle: true,
        badge: true,
      },
      { key: "challenge_type_display", label: "Type", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: CHALLENGE_STATUS, badge: true },
      { key: "status_display", label: "Status", card: true, skipForm: true },
      { key: "target_streak", label: "Target Streak", type: "number", card: true },
      { key: "streak_unit", label: "Unit", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "completion_reward_points", label: "Reward Points", type: "number", card: true },
      { key: "top_reward_points", label: "Top Reward", type: "number", card: true },
      { key: "completion_reward_badge", label: "Reward Badge", card: true },
      {
        key: "total_participants",
        label: "Participants",
        type: "number",
        card: true,
        skipForm: true,
      },
      {
        key: "total_completions",
        label: "Completions",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "is_class_competition", label: "Class Competition", type: "bool", card: true },
      { key: "is_house_competition", label: "House Competition", type: "bool", card: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", skipForm: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["title", "challenge_type", "status"],
  },
  "parent-portals": {
    key: "parent-portals",
    label: "Parent Portal",
    icon: EyeIcon,
    endpoint: "parent-portals",
    titleField: "parent_name",
    subtitleField: "student_name",
    toggleField: "is_active",
    fields: [
      { key: "parent_name", label: "Parent", main: true, skipForm: true },
      { key: "parent_user", label: "Parent ID", skipForm: true },
      { key: "student_name", label: "Student", subtitle: true, skipForm: true },
      { key: "student", label: "Student ID", card: true },
      { key: "access_level", label: "Access", type: "select", options: ACCESS_LEVELS, badge: true },
      { key: "access_level_display", label: "Access", card: true, skipForm: true },
      { key: "show_incidents", label: "Show Incidents", type: "bool", card: true },
      { key: "show_points", label: "Show Points", type: "bool", card: true },
      { key: "show_consequences", label: "Show Consequences", type: "bool", card: true },
      { key: "show_report_cards", label: "Show Report Cards", type: "bool", card: true },
      { key: "show_merits", label: "Show Merits", type: "bool", card: true },
      { key: "show_streaks", label: "Show Streaks", type: "bool", card: true },
      { key: "show_goals", label: "Show Goals", type: "bool", card: true },
      { key: "email_notifications", label: "Email", type: "bool", card: true },
      { key: "sms_notifications", label: "SMS", type: "bool", card: true },
      { key: "push_notifications", label: "Push", type: "bool", card: true },
      { key: "notify_on_incident", label: "On Incident", type: "bool", card: true },
      { key: "notify_on_consequence", label: "On Consequence", type: "bool", card: true },
      { key: "notify_on_positive", label: "On Positive", type: "bool", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "last_login_at", label: "Last Login", type: "datetime", card: true, skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["parent_name", "student_name", "access_level"],
  },
};

const TABS: { key: string; label: string; icon: React.ComponentType<{ className?: string }> }[] =
  Object.values(ENTITY_CONFIGS).map((c) => ({ key: c.key, label: c.label, icon: c.icon }));

// ─── Main page ───────────────────────────────────────────────────────────────

export default function BehaviorPage() {
  useTitle("Behavior Center");
  const [activeTab, setActiveTab] = useState("incidents");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Behavior Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Incidents, points, consequences, houses, SEL, interventions and analytics
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
        basePath="/behavior"
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
