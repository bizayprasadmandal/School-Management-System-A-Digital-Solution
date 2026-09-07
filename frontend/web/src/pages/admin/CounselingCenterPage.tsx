/**
 * Counseling Center — full-surface admin page for the counseling module.
 *
 * 50 entity tabs (config-driven via EntitySection): appointments, referrals &
 * sessions, intervention plans & goals, screenings & responses, crisis
 * interventions & follow-ups, progress tracking & milestones, consent,
 * group sessions & attendance & members, case management & notes, outcomes,
 * reports, availability & absences & coverage, feedback, academic advising &
 * course recommendations, bullying reports & follow-ups, career assessments &
 * goals, college applications, contracts, goal tracking, notifications, audit
 * logs, surveys & responses, waitlist, workshops & registrations, counselor
 * profiles, external providers, referral tracking, peer mentoring,
 * restorative practice, SEL assessments & goals, session attachments and
 * special education referrals.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, HeartIcon } from "@heroicons/react/24/outline";
import {
  CalendarDaysIcon,
  ClockIcon,
  DocumentTextIcon,
  FlagIcon,
  UserGroupIcon,
  UsersIcon,
  ClipboardDocumentListIcon,
  ClipboardDocumentCheckIcon,
  CheckBadgeIcon,
  ExclamationTriangleIcon,
  LifebuoyIcon,
  ScaleIcon,
  IdentificationIcon,
  InboxIcon,
  QueueListIcon,
  TicketIcon,
  BeakerIcon,
  SparklesIcon,
  ChartBarIcon,
  PresentationChartBarIcon,
  AcademicCapIcon,
  BookOpenIcon,
  EnvelopeIcon,
  BellAlertIcon,
  ChatBubbleLeftRightIcon,
  UserCircleIcon,
  ShieldCheckIcon,
  CheckCircleIcon,
  XCircleIcon,
  EyeIcon,
  MapPinIcon,
  TrophyIcon,
  UserPlusIcon,
  HandThumbUpIcon,
  ArrowPathIcon,
  BriefcaseIcon,
  GlobeAltIcon,
  FireIcon,
  StarIcon,
  PhoneArrowUpRightIcon,
  BuildingOffice2Icon,
} from "@heroicons/react/24/outline";

// ─── Shared option sets ──────────────────────────────────────────────────────

const APPT_TYPES = [
  ["academic", "Academic"],
  ["career", "Career"],
  ["personal", "Personal"],
  ["behavioral", "Behavioral"],
  ["college", "College"],
  ["group", "Group"],
  ["other", "Other"],
] as [string, string][];

const APPT_STATUS = [
  ["scheduled", "Scheduled"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
  ["no_show", "No Show"],
] as [string, string][];

const REFERRAL_CATEGORIES = [
  ["academic", "Academic"],
  ["attendance", "Attendance"],
  ["behavior", "Behavior"],
  ["emotional", "Emotional"],
  ["family", "Family"],
  ["social", "Social"],
  ["safety", "Safety"],
  ["other", "Other"],
] as [string, string][];

const REFERRAL_STATUS = [
  ["pending", "Pending"],
  ["under_review", "Under Review"],
  ["contacted", "Contacted"],
  ["actioned", "Actioned"],
  ["closed", "Closed"],
  ["declined", "Declined"],
] as [string, string][];

const PRIORITY = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
  ["urgent", "Urgent"],
] as [string, string][];

const URGENCY = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
  ["urgent", "Urgent"],
] as [string, string][];

const SESSION_TYPES = [
  ["individual", "Individual"],
  ["group", "Group"],
  ["family", "Family"],
  ["crisis", "Crisis"],
  ["follow_up", "Follow-up"],
  ["assessment", "Assessment"],
] as [string, string][];

const PLAN_TYPES = [
  ["academic", "Academic"],
  ["behavioral", "Behavioral"],
  ["social_emotional", "Social-Emotional"],
  ["mental_health", "Mental Health"],
  ["crisis", "Crisis"],
  ["career", "Career"],
  ["other", "Other"],
] as [string, string][];

const PLAN_STATUS = [
  ["draft", "Draft"],
  ["active", "Active"],
  ["on_hold", "On Hold"],
  ["completed", "Completed"],
  ["discontinued", "Discontinued"],
] as [string, string][];

const GOAL_STATUS = [
  ["not_started", "Not Started"],
  ["in_progress", "In Progress"],
  ["achieved", "Achieved"],
  ["partially_achieved", "Partially Achieved"],
  ["not_achieved", "Not Achieved"],
] as [string, string][];

const SCREENING_TYPES = [
  ["phq9", "PHQ-9"],
  ["gad7", "GAD-7"],
  ["pss10", "PSS-10"],
  ["audit", "AUDIT"],
  ["yrbs", "YRBS"],
  ["sdq", "SDQ"],
  ["custom", "Custom"],
] as [string, string][];

const RISK_LEVELS = [
  ["low", "Low"],
  ["moderate", "Moderate"],
  ["moderately_severe", "Moderately Severe"],
  ["severe", "Severe"],
] as [string, string][];

const CRISIS_TYPES = [
  ["suicidal_ideation", "Suicidal Ideation"],
  ["self_harm", "Self Harm"],
  ["violence", "Violence"],
  ["substance_abuse", "Substance Abuse"],
  ["trauma", "Trauma"],
  ["meltdown", "Meltdown"],
  ["other", "Other"],
] as [string, string][];

const CRISIS_SEVERITY = [
  ["low", "Low"],
  ["moderate", "Moderate"],
  ["high", "High"],
  ["critical", "Critical"],
] as [string, string][];

const CRISIS_STATUS = [
  ["active", "Active"],
  ["stabilized", "Stabilized"],
  ["follow_up", "Follow-up"],
  ["resolved", "Resolved"],
  ["referred", "Referred"],
] as [string, string][];

const TRACKING_DOMAINS = [
  ["academic", "Academic"],
  ["social", "Social"],
  ["emotional", "Emotional"],
  ["behavioral", "Behavioral"],
  ["attendance", "Attendance"],
  ["career", "Career"],
  ["overall", "Overall"],
] as [string, string][];

const TRENDS = [
  ["improving", "Improving"],
  ["stable", "Stable"],
  ["declining", "Declining"],
  ["fluctuating", "Fluctuating"],
] as [string, string][];

const CONSENT_TYPES = [
  ["general", "General"],
  ["mental_health", "Mental Health"],
  ["screening", "Screening"],
  ["group", "Group"],
  ["external_referral", "External Referral"],
  ["crisis", "Crisis"],
  ["records_access", "Records Access"],
] as [string, string][];

const CONSENT_STATUS = [
  ["pending", "Pending"],
  ["granted", "Granted"],
  ["denied", "Denied"],
  ["revoked", "Revoked"],
  ["expired", "Expired"],
] as [string, string][];

const GROUP_TYPES = [
  ["social_skills", "Social Skills"],
  ["grief", "Grief"],
  ["anger_management", "Anger Management"],
  ["anxiety", "Anxiety"],
  ["depression", "Depression"],
  ["behavioral", "Behavioral"],
  ["career", "Career"],
  ["peer_mediation", "Peer Mediation"],
  ["other", "Other"],
] as [string, string][];

const SESSION_STATUS = [
  ["scheduled", "Scheduled"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const ATTENDANCE_STATUS = [
  ["present", "Present"],
  ["absent", "Absent"],
  ["excused", "Excused"],
  ["late", "Late"],
] as [string, string][];

const CASE_STATUS = [
  ["open", "Open"],
  ["active", "Active"],
  ["on_hold", "On Hold"],
  ["closed", "Closed"],
  ["referred", "Referred"],
] as [string, string][];

const OUTCOME_TYPES = [
  ["academic", "Academic"],
  ["behavioral", "Behavioral"],
  ["social_emotional", "Social-Emotional"],
  ["attendance", "Attendance"],
  ["career", "Career"],
  ["overall", "Overall"],
] as [string, string][];

const OUTCOME_RATINGS = [
  ["significant_improvement", "Significant Improvement"],
  ["moderate_improvement", "Moderate Improvement"],
  ["slight_improvement", "Slight Improvement"],
  ["no_change", "No Change"],
  ["decline", "Decline"],
] as [string, string][];

const REPORT_TYPES = [
  ["individual", "Individual"],
  ["group", "Group"],
  ["department", "Department"],
  ["school", "School"],
  ["program", "Program"],
  ["compliance", "Compliance"],
] as [string, string][];

const DAYS = [
  ["monday", "Monday"],
  ["tuesday", "Tuesday"],
  ["wednesday", "Wednesday"],
  ["thursday", "Thursday"],
  ["friday", "Friday"],
  ["saturday", "Saturday"],
  ["sunday", "Sunday"],
] as [string, string][];

const FEEDBACK_TYPES = [
  ["student", "Student"],
  ["parent", "Parent"],
  ["teacher", "Teacher"],
] as [string, string][];

const SATISFACTION = [
  ["very_satisfied", "Very Satisfied"],
  ["satisfied", "Satisfied"],
  ["neutral", "Neutral"],
  ["dissatisfied", "Dissatisfied"],
  ["very_dissatisfied", "Very Dissatisfied"],
] as [string, string][];

const ADVISING_TYPES = [
  ["course_selection", "Course Selection"],
  ["scheduling", "Scheduling"],
  ["standing", "Standing"],
  ["graduation", "Graduation"],
  ["transfer", "Transfer"],
  ["other", "Other"],
] as [string, string][];

const BULLYING_TYPES = [
  ["physical", "Physical"],
  ["verbal", "Verbal"],
  ["social", "Social"],
  ["cyber", "Cyber"],
  ["sexual", "Sexual"],
  ["racial", "Racial"],
  ["discrimination", "Discrimination"],
  ["other", "Other"],
] as [string, string][];

const SEVERITY = [
  ["low", "Low"],
  ["moderate", "Moderate"],
  ["high", "High"],
  ["severe", "Severe"],
] as [string, string][];

const BULLYING_STATUS = [
  ["reported", "Reported"],
  ["investigating", "Investigating"],
  ["confirmed", "Confirmed"],
  ["unfounded", "Unfounded"],
  ["resolved", "Resolved"],
  ["escalated", "Escalated"],
] as [string, string][];

const ASSESSMENT_TYPES = [
  ["holland_code", "Holland Code"],
  ["mbti", "MBTI"],
  ["clifton", "Clifton"],
  ["strong", "Strong"],
  ["skills", "Skills"],
  ["values", "Values"],
  ["custom", "Custom"],
] as [string, string][];

const CAREER_GOAL_STATUS = [
  ["active", "Active"],
  ["achieved", "Achieved"],
  ["changed", "Changed"],
  ["abandoned", "Abandoned"],
] as [string, string][];

const NOTE_TYPES = [
  ["session", "Session"],
  ["phone", "Phone"],
  ["email", "Email"],
  ["meeting", "Meeting"],
  ["home_visit", "Home Visit"],
  ["observation", "Observation"],
  ["other", "Other"],
] as [string, string][];

const DEGREE_TYPES = [
  ["bachelors", "Bachelors"],
  ["masters", "Masters"],
  ["associate", "Associate"],
  ["diploma", "Diploma"],
] as [string, string][];

const COLLEGE_STATUS = [
  ["researching", "Researching"],
  ["preparing", "Preparing"],
  ["submitted", "Submitted"],
  ["accepted", "Accepted"],
  ["rejected", "Rejected"],
  ["waitlisted", "Waitlisted"],
  ["enrolled", "Enrolled"],
  ["declined", "Declined"],
] as [string, string][];

const CONTRACT_TYPES = [
  ["confidentiality", "Confidentiality"],
  ["service", "Service"],
  ["consent", "Consent"],
  ["release", "Release"],
  ["safety", "Safety"],
] as [string, string][];

const CONTRACT_STATUS = [
  ["pending", "Pending"],
  ["signed", "Signed"],
  ["expired", "Expired"],
  ["revoked", "Revoked"],
] as [string, string][];

const GOAL_DOMAINS = [
  ["academic", "Academic"],
  ["social", "Social"],
  ["emotional", "Emotional"],
  ["behavioral", "Behavioral"],
  ["career", "Career"],
  ["college", "College"],
  ["wellness", "Wellness"],
] as [string, string][];

const GOAL_TRACK_STATUS = [
  ["active", "Active"],
  ["achieved", "Achieved"],
  ["partial", "Partial"],
  ["ongoing", "Ongoing"],
  ["discontinued", "Discontinued"],
] as [string, string][];

const NOTIFICATION_TYPES = [
  ["appt_reminder", "Appt Reminder"],
  ["appt_confirmed", "Appt Confirmed"],
  ["appt_cancelled", "Appt Cancelled"],
  ["follow_up", "Follow-up"],
  ["workshop", "Workshop"],
  ["waitlist", "Waitlist"],
  ["screening", "Screening"],
  ["crisis", "Crisis"],
  ["other", "Other"],
] as [string, string][];

const LOG_ACTIONS = [
  ["viewed", "Viewed"],
  ["created", "Created"],
  ["edited", "Edited"],
  ["shared", "Shared"],
  ["exported", "Exported"],
  ["deleted", "Deleted"],
] as [string, string][];

const SURVEY_TYPES = [
  ["satisfaction", "Satisfaction"],
  ["needs", "Needs"],
  ["evaluation", "Evaluation"],
  ["anonymous", "Anonymous"],
  ["pre_post", "Pre/Post"],
] as [string, string][];

const SURVEY_STATUS = [
  ["draft", "Draft"],
  ["active", "Active"],
  ["closed", "Closed"],
  ["analyzed", "Analyzed"],
] as [string, string][];

const WAITLIST_STATUS = [
  ["waiting", "Waiting"],
  ["contacted", "Contacted"],
  ["scheduled", "Scheduled"],
  ["expired", "Expired"],
  ["removed", "Removed"],
] as [string, string][];

const WORKSHOP_TYPES = [
  ["orientation", "Orientation"],
  ["parent", "Parent"],
  ["stress", "Stress Management"],
  ["bullying", "Bullying Prevention"],
  ["college_prep", "College Prep"],
  ["financial", "Financial Literacy"],
  ["mental_health", "Mental Health"],
  ["career", "Career"],
  ["other", "Other"],
] as [string, string][];

const WORKSHOP_STATUS = [
  ["planned", "Planned"],
  ["active", "Active"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const ABSENCE_TYPES = [
  ["sick", "Sick"],
  ["personal", "Personal"],
  ["pd", "PD"],
  ["conference", "Conference"],
  ["other", "Other"],
] as [string, string][];

const COVERAGE_STATUS = [
  ["pending", "Pending"],
  ["accepted", "Accepted"],
  ["declined", "Declined"],
  ["completed", "Completed"],
] as [string, string][];

const PROVIDER_TYPES = [
  ["therapist", "Therapist"],
  ["psychiatrist", "Psychiatrist"],
  ["social_worker", "Social Worker"],
  ["community", "Community"],
  ["hospital", "Hospital"],
  ["educational", "Educational"],
  ["legal", "Legal"],
  ["other", "Other"],
] as [string, string][];

const PEER_MENTOR_STATUS = [
  ["active", "Active"],
  ["inactive", "Inactive"],
  ["graduated", "Graduated"],
] as [string, string][];

const REFERRAL_TRACK_STATUS = [
  ["initiated", "Initiated"],
  ["confirmed", "Confirmed"],
  ["attended", "Attended"],
  ["ongoing", "Ongoing"],
  ["completed", "Completed"],
  ["lost", "Lost"],
] as [string, string][];

const COMMITMENT_STATUS = [
  ["pending", "Pending"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["overdue", "Overdue"],
] as [string, string][];

const RESTORATIVE_TYPES = [
  ["circle", "Circle"],
  ["conference", "Conference"],
  ["mediation", "Mediation"],
  ["dialogue", "Dialogue"],
] as [string, string][];

const RESTORATIVE_OUTCOMES = [
  ["resolution", "Resolution"],
  ["partial", "Partial"],
  ["no_resolution", "No Resolution"],
  ["referred", "Referred"],
] as [string, string][];

const SEL_DOMAINS = [
  ["self_awareness", "Self-Awareness"],
  ["self_management", "Self-Management"],
  ["social_awareness", "Social Awareness"],
  ["relationship", "Relationship Skills"],
  ["decisions", "Responsible Decision-Making"],
  ["overall", "Overall SEL"],
] as [string, string][];

const SEL_GOAL_STATUS = [
  ["active", "Active"],
  ["achieved", "Achieved"],
  ["discontinued", "Discontinued"],
] as [string, string][];

const SPECIAL_ED_TYPES = [
  ["iep", "IEP"],
  ["504", "504 Plan"],
  ["gifted", "Gifted"],
  ["ld", "Learning Disability"],
  ["adhd", "ADHD"],
  ["autism", "Autism"],
  ["emotional", "Emotional"],
  ["other", "Other"],
] as [string, string][];

const SPECIAL_ED_STATUS = [
  ["initiated", "Initiated"],
  ["eval_scheduled", "Eval Scheduled"],
  ["evaluating", "Evaluating"],
  ["eligible", "Eligible"],
  ["not_eligible", "Not Eligible"],
  ["iep_created", "IEP Created"],
  ["in_progress", "In Progress"],
  ["review", "Review"],
  ["closed", "Closed"],
] as [string, string][];

const WORKSHOP_REG_STATUS = [
  ["registered", "Registered"],
  ["attended", "Attended"],
  ["no_show", "No Show"],
  ["cancelled", "Cancelled"],
] as [string, string][];

// ─── Entity configs ──────────────────────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  appointments: {
    key: "appointments",
    label: "Appointments",
    icon: CalendarDaysIcon,
    endpoint: "appointments",
    titleField: "student_name",
    subtitleField: "counselor_name",
    searchKeys: ["student_name", "counselor_name", "appointment_type", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "counselor_name", label: "Counselor", skipForm: true },
      {
        key: "appointment_type",
        label: "Type",
        type: "select",
        options: APPT_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: APPT_STATUS,
        badge: true,
      },
      { key: "scheduled_date", label: "Date", type: "date", card: true },
      { key: "scheduled_time", label: "Time", card: true },
      { key: "duration_minutes", label: "Duration (min)", type: "number" },
      { key: "location", label: "Location", card: true },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      { key: "follow_up_needed", label: "Follow-up Needed", type: "bool" },
      { key: "follow_up_date", label: "Follow-up Date", type: "date" },
    ],
  },
  referrals: {
    key: "referrals",
    label: "Referrals",
    icon: ArrowPathIcon,
    endpoint: "referrals",
    titleField: "student_name",
    subtitleField: "referred_by_name",
    searchKeys: ["student_name", "category", "status", "reason"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "referred_by", label: "Referred By (ID)", full: true },
      { key: "referred_by_name", label: "Referred By", skipForm: true },
      { key: "assigned_to", label: "Assigned To (ID)", full: true },
      { key: "assigned_to_name", label: "Assigned To", skipForm: true },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: REFERRAL_CATEGORIES,
        badge: true,
      },
      {
        key: "priority",
        label: "Priority",
        type: "select",
        options: PRIORITY,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: REFERRAL_STATUS,
        badge: true,
      },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      { key: "outcome", label: "Outcome", type: "textarea", full: true },
      {
        key: "follow_up_date",
        label: "Follow-up Date",
        type: "date",
        card: true,
      },
      { key: "is_confidential", label: "Confidential", type: "bool" },
    ],
  },
  sessions: {
    key: "sessions",
    label: "Sessions",
    icon: ChatBubbleLeftRightIcon,
    endpoint: "sessions",
    titleField: "student_name",
    subtitleField: "session_type",
    searchKeys: ["student_name", "counselor_name", "session_type", "presenting_issue"],
    fields: [
      { key: "appointment", label: "Appointment (ID)", full: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "counselor_name", label: "Counselor", skipForm: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "session_type",
        label: "Type",
        type: "select",
        options: SESSION_TYPES,
        badge: true,
      },
      { key: "session_date", label: "Date", type: "date", card: true },
      { key: "start_time", label: "Start", card: true },
      { key: "end_time", label: "End" },
      { key: "duration_minutes", label: "Duration (min)", type: "number" },
      {
        key: "presenting_issue",
        label: "Presenting Issue",
        type: "textarea",
        full: true,
      },
      {
        key: "session_summary",
        label: "Summary",
        type: "textarea",
        full: true,
      },
      {
        key: "interventions_used",
        label: "Interventions Used",
        type: "textarea",
        full: true,
      },
      {
        key: "student_response",
        label: "Student Response",
        type: "textarea",
        full: true,
      },
      {
        key: "risk_assessment",
        label: "Risk Assessment",
        type: "textarea",
        full: true,
      },
      {
        key: "progress_notes",
        label: "Progress Notes",
        type: "textarea",
        full: true,
      },
      {
        key: "follow_up_actions",
        label: "Follow-up Actions",
        type: "textarea",
        full: true,
      },
      { key: "follow_up_date", label: "Follow-up Date", type: "date" },
      { key: "is_confidential", label: "Confidential", type: "bool" },
    ],
  },
  interventionPlans: {
    key: "interventionPlans",
    label: "Intervention Plans",
    icon: ClipboardDocumentListIcon,
    endpoint: "intervention-plans",
    titleField: "title",
    subtitleField: "student_name",
    searchKeys: ["title", "student_name", "counselor_name", "plan_type", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "counselor_name", label: "Counselor", skipForm: true },
      {
        key: "plan_type",
        label: "Plan Type",
        type: "select",
        options: PLAN_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: PLAN_STATUS,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "target_end_date", label: "Target End", type: "date" },
      { key: "actual_end_date", label: "Actual End", type: "date" },
      { key: "review_frequency", label: "Review Frequency", card: true },
      { key: "next_review_date", label: "Next Review", type: "date" },
      {
        key: "outcome_summary",
        label: "Outcome Summary",
        type: "textarea",
        full: true,
      },
      { key: "is_effective", label: "Effective", type: "bool" },
      {
        key: "completion_percentage",
        label: "Completion %",
        type: "number",
        card: true,
      },
    ],
  },
  interventionGoals: {
    key: "interventionGoals",
    label: "Intervention Goals",
    icon: CheckBadgeIcon,
    endpoint: "intervention-goals",
    titleField: "description",
    subtitleField: "plan_title",
    searchKeys: ["description", "plan_title", "status"],
    fields: [
      { key: "intervention_plan", label: "Plan (ID)", full: true },
      { key: "plan_title", label: "Plan", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "measurable_outcome",
        label: "Measurable Outcome",
        type: "textarea",
        full: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: GOAL_STATUS,
        badge: true,
      },
      { key: "target_date", label: "Target Date", type: "date", card: true },
      { key: "is_completed", label: "Completed", type: "bool" },
      { key: "completion_date", label: "Completion Date", type: "date" },
      { key: "order", label: "Order", type: "number" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  screenings: {
    key: "screenings",
    label: "Screenings",
    icon: BeakerIcon,
    endpoint: "screenings",
    titleField: "student_name",
    subtitleField: "screening_type",
    searchKeys: ["student_name", "screening_type", "risk_level"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "screening_type",
        label: "Type",
        type: "select",
        options: SCREENING_TYPES,
        badge: true,
      },
      { key: "administered_by", label: "Administered By (ID)", full: true },
      { key: "administered_by_name", label: "Administered By", skipForm: true },
      { key: "administered_date", label: "Date", type: "date", card: true },
      { key: "total_score", label: "Total Score", type: "number", card: true },
      {
        key: "risk_level",
        label: "Risk Level",
        type: "select",
        options: RISK_LEVELS,
        badge: true,
      },
      {
        key: "interpretation",
        label: "Interpretation",
        type: "textarea",
        full: true,
      },
      {
        key: "recommendations",
        label: "Recommendations",
        type: "textarea",
        full: true,
      },
      { key: "referral_needed", label: "Referral Needed", type: "bool" },
      { key: "referred_to", label: "Referred To" },
      { key: "follow_up_date", label: "Follow-up Date", type: "date" },
      { key: "follow_up_completed", label: "Follow-up Done", type: "bool" },
      { key: "consent_obtained", label: "Consent Obtained", type: "bool" },
    ],
  },
  screeningResponses: {
    key: "screeningResponses",
    label: "Screening Responses",
    icon: QueueListIcon,
    endpoint: "screening-responses",
    titleField: "screening_title",
    subtitleField: "question_text",
    searchKeys: ["screening_title", "question_text"],
    fields: [
      { key: "screening", label: "Screening (ID)", full: true },
      { key: "screening_title", label: "Screening", skipForm: true },
      {
        key: "question_number",
        label: "Question #",
        type: "number",
        card: true,
      },
      { key: "question_text", label: "Question", type: "textarea", full: true },
      { key: "response_value", label: "Response Value", type: "number" },
      { key: "response_text", label: "Response", type: "textarea", full: true },
    ],
  },
  crisis: {
    key: "crisis",
    label: "Crisis Interventions",
    icon: ExclamationTriangleIcon,
    endpoint: "crisis",
    titleField: "student_name",
    subtitleField: "crisis_type",
    searchKeys: ["student_name", "crisis_type", "severity_level", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "reported_by", label: "Reported By (ID)", full: true },
      { key: "reported_by_name", label: "Reported By", skipForm: true },
      {
        key: "crisis_type",
        label: "Type",
        type: "select",
        options: CRISIS_TYPES,
        badge: true,
      },
      {
        key: "severity_level",
        label: "Severity",
        type: "select",
        options: CRISIS_SEVERITY,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CRISIS_STATUS,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "immediate_actions",
        label: "Immediate Actions",
        type: "textarea",
        full: true,
      },
      { key: "risk_to_self", label: "Risk to Self", type: "bool" },
      { key: "risk_to_others", label: "Risk to Others", type: "bool" },
      {
        key: "responding_counselor",
        label: "Responding Counselor (ID)",
        full: true,
      },
      {
        key: "responding_counselor_name",
        label: "Responding Counselor",
        skipForm: true,
      },
      {
        key: "intervention_provided",
        label: "Intervention Provided",
        type: "textarea",
        full: true,
      },
      { key: "follow_up_needed", label: "Follow-up Needed", type: "bool" },
      { key: "follow_up_date", label: "Follow-up Date", type: "date" },
      { key: "parent_notified", label: "Parent Notified", type: "bool" },
      { key: "external_referral", label: "External Referral", type: "bool" },
      { key: "external_agency", label: "External Agency", card: true },
    ],
  },
  crisisFollowups: {
    key: "crisisFollowups",
    label: "Crisis Follow-ups",
    icon: LifebuoyIcon,
    endpoint: "crisis-followups",
    titleField: "counselor_name",
    subtitleField: "student_status",
    searchKeys: ["counselor_name", "student_status", "notes"],
    fields: [
      { key: "crisis", label: "Crisis (ID)", full: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "counselor_name", label: "Counselor", skipForm: true },
      { key: "follow_up_date", label: "Date", type: "date", card: true },
      { key: "student_status", label: "Student Status", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      {
        key: "actions_taken",
        label: "Actions Taken",
        type: "textarea",
        full: true,
      },
    ],
  },
  progress: {
    key: "progress",
    label: "Progress Tracking",
    icon: ChartBarIcon,
    endpoint: "progress",
    titleField: "student_name",
    subtitleField: "domain",
    searchKeys: ["student_name", "domain", "trend"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "counselor_name", label: "Counselor", skipForm: true },
      {
        key: "domain",
        label: "Domain",
        type: "select",
        options: TRACKING_DOMAINS,
        badge: true,
      },
      {
        key: "trend",
        label: "Trend",
        type: "select",
        options: TRENDS,
        badge: true,
      },
      { key: "assessment_date", label: "Assessed", type: "date", card: true },
      { key: "current_rating", label: "Current", type: "number", card: true },
      { key: "previous_rating", label: "Previous", type: "number" },
      { key: "target_rating", label: "Target", type: "number" },
      {
        key: "observations",
        label: "Observations",
        type: "textarea",
        full: true,
      },
      { key: "strengths", label: "Strengths", type: "textarea", full: true },
      {
        key: "areas_for_growth",
        label: "Growth Areas",
        type: "textarea",
        full: true,
      },
      {
        key: "interventions_applied",
        label: "Interventions",
        type: "textarea",
        full: true,
      },
    ],
  },
  progressMilestones: {
    key: "progressMilestones",
    label: "Progress Milestones",
    icon: FlagIcon,
    endpoint: "progress-milestones",
    titleField: "description",
    subtitleField: "progress_domain",
    searchKeys: ["description", "progress_domain"],
    fields: [
      { key: "progress", label: "Progress (ID)", full: true },
      { key: "progress_domain", label: "Domain", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "target_date", label: "Target Date", type: "date", card: true },
      { key: "achieved", label: "Achieved", type: "bool" },
      { key: "achieved_date", label: "Achieved Date", type: "date" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  consent: {
    key: "consent",
    label: "Parent Consent",
    icon: ShieldCheckIcon,
    endpoint: "consent",
    titleField: "student_name",
    subtitleField: "consent_type",
    searchKeys: ["student_name", "parent_name", "consent_type", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "parent", label: "Parent (ID)", full: true },
      { key: "parent_name", label: "Parent", skipForm: true },
      {
        key: "consent_type",
        label: "Type",
        type: "select",
        options: CONSENT_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CONSENT_STATUS,
        badge: true,
      },
      { key: "consent_given", label: "Consent Given", type: "bool" },
      { key: "consent_date", label: "Consent Date", type: "date", card: true },
      { key: "expiry_date", label: "Expires", type: "date" },
      {
        key: "scope_description",
        label: "Scope",
        type: "textarea",
        full: true,
      },
      {
        key: "restrictions",
        label: "Restrictions",
        type: "textarea",
        full: true,
      },
      { key: "withdrawal_date", label: "Withdrawn", type: "date" },
      {
        key: "withdrawal_reason",
        label: "Withdrawal Reason",
        type: "textarea",
        full: true,
      },
    ],
  },
  groupSessions: {
    key: "groupSessions",
    label: "Group Sessions",
    icon: UserGroupIcon,
    endpoint: "group-sessions",
    titleField: "title",
    subtitleField: "group_type",
    searchKeys: ["title", "counselor_name", "group_type", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "counselor_name", label: "Counselor", skipForm: true },
      {
        key: "group_type",
        label: "Type",
        type: "select",
        options: GROUP_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: SESSION_STATUS,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date" },
      { key: "meeting_time", label: "Meeting Time", card: true },
      { key: "duration_minutes", label: "Duration (min)", type: "number" },
      { key: "location", label: "Location", card: true },
      { key: "recurrence", label: "Recurrence" },
      { key: "max_participants", label: "Max Participants", type: "number" },
      {
        key: "current_participants",
        label: "Enrolled",
        type: "number",
        card: true,
      },
      { key: "goals", label: "Goals", type: "textarea", full: true },
      { key: "curriculum", label: "Curriculum", type: "textarea", full: true },
      {
        key: "materials_needed",
        label: "Materials",
        type: "textarea",
        full: true,
      },
    ],
  },
  groupAttendance: {
    key: "groupAttendance",
    label: "Group Attendance",
    icon: CheckCircleIcon,
    endpoint: "group-attendance",
    titleField: "student_name",
    subtitleField: "status",
    searchKeys: ["student_name", "status"],
    fields: [
      { key: "group_session", label: "Group Session (ID)", full: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "session_number", label: "Session #", type: "number", card: true },
      { key: "attended_date", label: "Date", type: "date", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ATTENDANCE_STATUS,
        badge: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  cases: {
    key: "cases",
    label: "Case Management",
    icon: IdentificationIcon,
    endpoint: "cases",
    titleField: "title",
    subtitleField: "student_name",
    searchKeys: ["case_number", "title", "student_name", "case_manager_name", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "case_number", label: "Case #", card: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "case_manager", label: "Case Manager (ID)", full: true },
      { key: "case_manager_name", label: "Case Manager", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CASE_STATUS,
        badge: true,
      },
      {
        key: "priority",
        label: "Priority",
        type: "select",
        options: PRIORITY,
        badge: true,
      },
      {
        key: "presenting_concerns",
        label: "Presenting Concerns",
        type: "textarea",
        full: true,
      },
      {
        key: "background_information",
        label: "Background",
        type: "textarea",
        full: true,
      },
      { key: "strengths", label: "Strengths", type: "textarea", full: true },
      {
        key: "risk_factors",
        label: "Risk Factors",
        type: "textarea",
        full: true,
      },
      { key: "opened_date", label: "Opened", type: "date", card: true },
      { key: "closed_date", label: "Closed", type: "date" },
      { key: "next_review_date", label: "Next Review", type: "date" },
      {
        key: "outcome_summary",
        label: "Outcome",
        type: "textarea",
        full: true,
      },
      { key: "is_successful", label: "Successful", type: "bool" },
    ],
  },
  outcomes: {
    key: "outcomes",
    label: "Outcomes",
    icon: TrophyIcon,
    endpoint: "outcomes",
    titleField: "student_name",
    subtitleField: "outcome_type",
    searchKeys: ["student_name", "outcome_type", "rating"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "counselor_name", label: "Counselor", skipForm: true },
      {
        key: "outcome_type",
        label: "Type",
        type: "select",
        options: OUTCOME_TYPES,
        badge: true,
      },
      {
        key: "rating",
        label: "Rating",
        type: "select",
        options: OUTCOME_RATINGS,
        badge: true,
      },
      { key: "assessment_date", label: "Assessed", type: "date", card: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "measurable_results",
        label: "Measurable Results",
        type: "textarea",
        full: true,
      },
      { key: "data_sources", label: "Data Sources", full: true },
      {
        key: "recommendations",
        label: "Recommendations",
        type: "textarea",
        full: true,
      },
      {
        key: "continuation_needed",
        label: "Continuation Needed",
        type: "bool",
      },
    ],
  },
  reports: {
    key: "reports",
    label: "Reports",
    icon: DocumentTextIcon,
    endpoint: "reports",
    titleField: "title",
    subtitleField: "report_type",
    searchKeys: ["title", "report_type", "status", "generated_by_name"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "report_type",
        label: "Type",
        type: "select",
        options: REPORT_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["final", "Final"],
          ["archived", "Archived"],
        ] as [string, string][],
        badge: true,
      },
      { key: "period_start", label: "Period Start", type: "date", card: true },
      { key: "period_end", label: "Period End", type: "date" },
      { key: "summary", label: "Summary", type: "textarea", full: true },
      { key: "findings", label: "Findings", type: "textarea", full: true },
      {
        key: "recommendations",
        label: "Recommendations",
        type: "textarea",
        full: true,
      },
      {
        key: "total_students_served",
        label: "Students Served",
        type: "number",
        card: true,
      },
      { key: "total_sessions", label: "Sessions", type: "number" },
      { key: "total_referrals", label: "Referrals", type: "number" },
    ],
  },
  availability: {
    key: "availability",
    label: "Availability",
    icon: ClockIcon,
    endpoint: "availability",
    titleField: "counselor_name",
    subtitleField: "day_of_week",
    searchKeys: ["counselor_name", "day_of_week", "location"],
    fields: [
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "counselor_name", label: "Counselor", skipForm: true },
      {
        key: "day_of_week",
        label: "Day",
        type: "select",
        options: DAYS,
        badge: true,
      },
      { key: "start_time", label: "Start", card: true },
      { key: "end_time", label: "End", card: true },
      { key: "is_available", label: "Available", type: "bool" },
      { key: "location", label: "Location", card: true },
      { key: "session_type", label: "Session Type" },
      { key: "max_appointments", label: "Max Appointments", type: "number" },
      { key: "effective_from", label: "Effective From", type: "date" },
      { key: "effective_until", label: "Effective Until", type: "date" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  feedback: {
    key: "feedback",
    label: "Feedback",
    icon: HandThumbUpIcon,
    endpoint: "feedback",
    titleField: "student_name",
    subtitleField: "feedback_type",
    searchKeys: ["student_name", "counselor_name", "feedback_type", "overall_satisfaction"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "counselor_name", label: "Counselor", skipForm: true },
      {
        key: "feedback_type",
        label: "From",
        type: "select",
        options: FEEDBACK_TYPES,
        badge: true,
      },
      {
        key: "overall_satisfaction",
        label: "Satisfaction",
        type: "select",
        options: SATISFACTION,
        badge: true,
      },
      {
        key: "helpfulness_rating",
        label: "Helpfulness (1-5)",
        type: "number",
        card: true,
      },
      {
        key: "communication_rating",
        label: "Communication (1-5)",
        type: "number",
      },
      {
        key: "professionalism_rating",
        label: "Professionalism (1-5)",
        type: "number",
      },
      {
        key: "what_went_well",
        label: "What Went Well",
        type: "textarea",
        full: true,
      },
      {
        key: "areas_for_improvement",
        label: "To Improve",
        type: "textarea",
        full: true,
      },
      {
        key: "additional_comments",
        label: "Comments",
        type: "textarea",
        full: true,
      },
      { key: "would_recommend", label: "Would Recommend", type: "bool" },
      { key: "is_anonymous", label: "Anonymous", type: "bool" },
    ],
  },
  academicAdvising: {
    key: "academicAdvising",
    label: "Academic Advising",
    icon: AcademicCapIcon,
    endpoint: "academic-advising",
    titleField: "student_name",
    subtitleField: "advisor_name",
    searchKeys: ["student_name", "advisor_name", "advising_type", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "advisor", label: "Advisor (ID)", full: true },
      { key: "advisor_name", label: "Advisor", skipForm: true },
      {
        key: "advising_type",
        label: "Type",
        type: "select",
        options: ADVISING_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["completed", "Completed"],
          ["follow_up", "Follow-up"],
        ] as [string, string][],
        badge: true,
      },
      { key: "scheduled_date", label: "Scheduled", type: "date", card: true },
      { key: "completed_date", label: "Completed", type: "date" },
      {
        key: "topics_discussed",
        label: "Topics",
        type: "textarea",
        full: true,
      },
      {
        key: "recommendations",
        label: "Recommendations",
        type: "textarea",
        full: true,
      },
      { key: "current_gpa", label: "Current GPA", type: "number", card: true },
      { key: "credits_earned", label: "Credits Earned", type: "number" },
      { key: "credits_required", label: "Credits Required", type: "number" },
      { key: "standing", label: "Standing", card: true },
      { key: "follow_up_date", label: "Follow-up", type: "date" },
    ],
  },
  bullyingFollowups: {
    key: "bullyingFollowups",
    label: "Bullying Follow-ups",
    icon: ArrowPathIcon,
    endpoint: "bullying-followups",
    titleField: "report_type",
    subtitleField: "outcome",
    searchKeys: ["report_type", "outcome", "notes"],
    fields: [
      { key: "report", label: "Report (ID)", full: true },
      { key: "report_type", label: "Report Type", skipForm: true },
      { key: "conducted_by", label: "Conducted By (ID)", full: true },
      { key: "participant", label: "Participant", card: true },
      { key: "follow_up_date", label: "Date", type: "date", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      { key: "outcome", label: "Outcome", type: "textarea", full: true },
      { key: "victim_status", label: "Victim Status", card: true },
    ],
  },
  bullyingReports: {
    key: "bullyingReports",
    label: "Bullying Reports",
    icon: ExclamationTriangleIcon,
    endpoint: "bullying-reports",
    titleField: "victim_name",
    subtitleField: "report_type",
    searchKeys: ["victim_name", "report_type", "severity", "status", "location"],
    fields: [
      { key: "victim", label: "Victim (ID)", full: true },
      { key: "victim_name", label: "Victim", skipForm: true },
      { key: "reporter", label: "Reporter (ID)", full: true },
      {
        key: "alleged_perpetrator",
        label: "Alleged Perpetrator (ID)",
        full: true,
      },
      {
        key: "report_type",
        label: "Type",
        type: "select",
        options: BULLYING_TYPES,
        badge: true,
      },
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: SEVERITY,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: BULLYING_STATUS,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "location", label: "Location", card: true },
      {
        key: "date_of_incident",
        label: "Incident Date",
        type: "date",
        card: true,
      },
      { key: "witnesses", label: "Witnesses", full: true },
      { key: "evidence", label: "Evidence", type: "textarea", full: true },
      {
        key: "investigation_notes",
        label: "Investigation Notes",
        type: "textarea",
        full: true,
      },
      { key: "investigator", label: "Investigator (ID)", full: true },
      { key: "resolution", label: "Resolution", type: "textarea", full: true },
      {
        key: "actions_taken",
        label: "Actions Taken",
        type: "textarea",
        full: true,
      },
      { key: "counselor_assigned", label: "Counselor (ID)", full: true },
      {
        key: "victim_parent_notified",
        label: "Victim Parent Notified",
        type: "bool",
      },
      {
        key: "perpetrator_parent_notified",
        label: "Perp Parent Notified",
        type: "bool",
      },
    ],
  },
  careerAssessments: {
    key: "careerAssessments",
    label: "Career Assessments",
    icon: BriefcaseIcon,
    endpoint: "career-assessments",
    titleField: "student_name",
    subtitleField: "assessment_type",
    searchKeys: ["student_name", "assessment_type"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "assessment_type",
        label: "Type",
        type: "select",
        options: ASSESSMENT_TYPES,
        badge: true,
      },
      { key: "administered_by", label: "Administered By (ID)", full: true },
      { key: "administered_date", label: "Date", type: "date", card: true },
      {
        key: "result_summary",
        label: "Result Summary",
        type: "textarea",
        full: true,
      },
      { key: "recommended_careers", label: "Recommended Careers", full: true },
      { key: "recommended_fields", label: "Recommended Fields", full: true },
      {
        key: "recommendations",
        label: "Recommendations",
        type: "textarea",
        full: true,
      },
      {
        key: "counselor_notes",
        label: "Counselor Notes",
        type: "textarea",
        full: true,
      },
    ],
  },
  careerGoals: {
    key: "careerGoals",
    label: "Career Goals",
    icon: StarIcon,
    endpoint: "career-goals",
    titleField: "title",
    subtitleField: "student_name",
    searchKeys: ["title", "student_name", "target_field", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "target_field", label: "Target Field", card: true },
      { key: "target_university", label: "Target University", card: true },
      { key: "target_program", label: "Target Program" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CAREER_GOAL_STATUS,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "action_steps",
        label: "Action Steps",
        type: "textarea",
        full: true,
      },
      {
        key: "resources_needed",
        label: "Resources Needed",
        type: "textarea",
        full: true,
      },
      { key: "timeline", label: "Timeline", card: true },
      {
        key: "progress_notes",
        label: "Progress Notes",
        type: "textarea",
        full: true,
      },
    ],
  },
  caseNotes: {
    key: "caseNotes",
    label: "Case Notes",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "case-notes",
    titleField: "author_name",
    subtitleField: "note_type",
    searchKeys: ["author_name", "note_type", "content"],
    fields: [
      { key: "case", label: "Case (ID)", full: true },
      { key: "author", label: "Author (ID)", full: true },
      { key: "author_name", label: "Author", skipForm: true },
      {
        key: "note_type",
        label: "Type",
        type: "select",
        options: NOTE_TYPES,
        badge: true,
      },
      { key: "content", label: "Content", type: "textarea", full: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "time", label: "Time", card: true },
      { key: "is_confidential", label: "Confidential", type: "bool" },
    ],
  },
  collegeApplications: {
    key: "collegeApplications",
    label: "College Applications",
    icon: BuildingOffice2Icon,
    endpoint: "college-applications",
    titleField: "university_name",
    subtitleField: "student_name",
    searchKeys: ["university_name", "student_name", "program_name", "status"],
    fields: [
      { key: "university_name", label: "University", main: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "program_name", label: "Program", card: true },
      {
        key: "degree_type",
        label: "Degree",
        type: "select",
        options: DEGREE_TYPES,
        badge: true,
      },
      { key: "location", label: "Location", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: COLLEGE_STATUS,
        badge: true,
      },
      {
        key: "application_deadline",
        label: "Deadline",
        type: "date",
        card: true,
      },
      { key: "application_submitted_date", label: "Submitted", type: "date" },
      { key: "decision_date", label: "Decision", type: "date" },
      {
        key: "enrollment_deadline",
        label: "Enrollment Deadline",
        type: "date",
      },
      { key: "estimated_cost", label: "Est. Cost", type: "number" },
      { key: "scholarship_offered", label: "Scholarship", type: "bool" },
      { key: "financial_aid_amount", label: "Financial Aid", type: "number" },
      { key: "sat_score", label: "SAT", type: "number" },
      { key: "act_score", label: "ACT", type: "number" },
      { key: "essays_completed", label: "Essays Done", type: "bool" },
      { key: "letters_of_rec_sent", label: "Rec Letters Sent", type: "bool" },
      {
        key: "counselor_recommendation",
        label: "Counselor Rec",
        type: "textarea",
        full: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  contracts: {
    key: "contracts",
    label: "Contracts",
    icon: ScaleIcon,
    endpoint: "contracts",
    titleField: "title",
    subtitleField: "student_name",
    searchKeys: ["title", "student_name", "contract_type", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "parent", label: "Parent (ID)", full: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      {
        key: "contract_type",
        label: "Type",
        type: "select",
        options: CONTRACT_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CONTRACT_STATUS,
        badge: true,
      },
      { key: "content", label: "Content", type: "textarea", full: true },
      { key: "student_signed", label: "Student Signed", type: "bool" },
      { key: "parent_signed", label: "Parent Signed", type: "bool" },
      { key: "counselor_signed", label: "Counselor Signed", type: "bool" },
      { key: "effective_date", label: "Effective", type: "date", card: true },
      { key: "expiry_date", label: "Expires", type: "date" },
    ],
  },
  goalTracking: {
    key: "goalTracking",
    label: "Goal Tracking",
    icon: CheckBadgeIcon,
    endpoint: "goal-tracking",
    titleField: "goal",
    subtitleField: "student_name",
    searchKeys: ["goal", "student_name", "domain", "status"],
    fields: [
      { key: "goal", label: "Goal", main: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      {
        key: "domain",
        label: "Domain",
        type: "select",
        options: GOAL_DOMAINS,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: GOAL_TRACK_STATUS,
        badge: true,
      },
      {
        key: "priority",
        label: "Priority",
        type: "select",
        options: PRIORITY,
        badge: true,
      },
      {
        key: "measurable_criteria",
        label: "Measurable Criteria",
        type: "textarea",
        full: true,
      },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "target_date", label: "Target", type: "date" },
      { key: "achieved_date", label: "Achieved", type: "date" },
      {
        key: "progress_percentage",
        label: "Progress %",
        type: "number",
        card: true,
      },
      {
        key: "progress_notes",
        label: "Progress Notes",
        type: "textarea",
        full: true,
      },
      { key: "barriers", label: "Barriers", type: "textarea", full: true },
      {
        key: "support_strategies",
        label: "Support Strategies",
        type: "textarea",
        full: true,
      },
    ],
  },
  notifications: {
    key: "notifications",
    label: "Notifications",
    icon: BellAlertIcon,
    endpoint: "notifications",
    titleField: "title",
    subtitleField: "recipient_name",
    searchKeys: ["title", "recipient_name", "notification_type", "message"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "recipient", label: "Recipient (ID)", full: true },
      { key: "recipient_name", label: "Recipient", skipForm: true },
      { key: "student", label: "Student (ID)", full: true },
      {
        key: "notification_type",
        label: "Type",
        type: "select",
        options: NOTIFICATION_TYPES,
        badge: true,
      },
      { key: "message", label: "Message", type: "textarea", full: true },
      { key: "is_read", label: "Read", type: "bool" },
      { key: "is_sent", label: "Sent", type: "bool" },
      { key: "sent_via", label: "Sent Via", card: true },
      { key: "sent_at", label: "Sent At", type: "datetime" },
    ],
  },
  sessionLogs: {
    key: "sessionLogs",
    label: "Audit Logs",
    icon: EyeIcon,
    endpoint: "session-logs",
    titleField: "user_name",
    subtitleField: "action",
    searchKeys: ["user_name", "action", "target_type", "description"],
    fields: [
      { key: "user", label: "User (ID)", full: true },
      { key: "user_name", label: "User", skipForm: true },
      {
        key: "action",
        label: "Action",
        type: "select",
        options: LOG_ACTIONS,
        badge: true,
      },
      { key: "target_type", label: "Target Type", card: true },
      { key: "target_id", label: "Target ID", card: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "ip_address", label: "IP Address", card: true },
      { key: "timestamp", label: "Timestamp", type: "datetime" },
    ],
  },
  surveys: {
    key: "surveys",
    label: "Surveys",
    icon: ClipboardDocumentListIcon,
    endpoint: "surveys",
    titleField: "title",
    subtitleField: "survey_type",
    searchKeys: ["title", "survey_type", "status", "target_audience"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "survey_type",
        label: "Type",
        type: "select",
        options: SURVEY_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: SURVEY_STATUS,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "questions",
        label: "Questions (JSON)",
        type: "textarea",
        full: true,
      },
      { key: "target_audience", label: "Target Audience", card: true },
      { key: "is_anonymous", label: "Anonymous", type: "bool" },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date" },
      {
        key: "total_responses",
        label: "Responses",
        type: "number",
        card: true,
      },
    ],
  },
  surveyResponses: {
    key: "surveyResponses",
    label: "Survey Responses",
    icon: QueueListIcon,
    endpoint: "survey-responses",
    titleField: "respondent_type",
    subtitleField: "comments",
    searchKeys: ["respondent_type", "comments"],
    fields: [
      { key: "survey", label: "Survey (ID)", full: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "parent", label: "Parent (ID)", full: true },
      { key: "respondent_type", label: "Respondent", badge: true },
      { key: "answers", label: "Answers (JSON)", type: "textarea", full: true },
      {
        key: "overall_rating",
        label: "Overall Rating",
        type: "number",
        card: true,
      },
      { key: "comments", label: "Comments", type: "textarea", full: true },
      { key: "submitted_at", label: "Submitted", type: "datetime" },
    ],
  },
  waitlist: {
    key: "waitlist",
    label: "Waitlist",
    icon: QueueListIcon,
    endpoint: "waitlist",
    titleField: "student_name",
    subtitleField: "reason",
    searchKeys: ["student_name", "reason", "priority", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "preferred_counselor",
        label: "Preferred Counselor (ID)",
        full: true,
      },
      {
        key: "scheduled_appointment",
        label: "Scheduled Appt (ID)",
        full: true,
      },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      {
        key: "priority",
        label: "Priority",
        type: "select",
        options: PRIORITY,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: WAITLIST_STATUS,
        badge: true,
      },
      { key: "position", label: "Position", type: "number", card: true },
      { key: "added_date", label: "Added", type: "date", card: true },
      { key: "contact_date", label: "Contacted", type: "date" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  workshops: {
    key: "workshops",
    label: "Workshops",
    icon: PresentationChartBarIcon,
    endpoint: "workshops",
    titleField: "title",
    subtitleField: "workshop_type",
    searchKeys: ["title", "workshop_type", "status", "speaker_name"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "organizer", label: "Organizer (ID)", full: true },
      {
        key: "workshop_type",
        label: "Type",
        type: "select",
        options: WORKSHOP_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: WORKSHOP_STATUS,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "start_date", label: "Start Date", type: "date", card: true },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "start_time", label: "Start Time", card: true },
      { key: "end_time", label: "End Time" },
      { key: "location", label: "Location", card: true },
      { key: "max_participants", label: "Max Participants", type: "number" },
      { key: "current_participants", label: "Enrolled", type: "number" },
      { key: "target_grades", label: "Target Grades" },
      { key: "target_audience", label: "Target Audience" },
      { key: "objectives", label: "Objectives", type: "textarea", full: true },
      { key: "materials", label: "Materials", type: "textarea", full: true },
      { key: "speaker_name", label: "Speaker", card: true },
      { key: "speaker_org", label: "Speaker Org" },
    ],
  },
  workshopRegistrations: {
    key: "workshopRegistrations",
    label: "Workshop Registrations",
    icon: TicketIcon,
    endpoint: "workshop-registrations",
    titleField: "workshop_title",
    subtitleField: "student_name",
    searchKeys: ["workshop_title", "student_name", "status"],
    fields: [
      { key: "workshop", label: "Workshop (ID)", full: true },
      { key: "workshop_title", label: "Workshop", skipForm: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: WORKSHOP_REG_STATUS,
        badge: true,
      },
      {
        key: "registered_at",
        label: "Registered",
        type: "datetime",
        card: true,
      },
      { key: "attended_at", label: "Attended", type: "datetime" },
      {
        key: "feedback_rating",
        label: "Feedback Rating",
        type: "number",
        card: true,
      },
      {
        key: "feedback_comments",
        label: "Feedback",
        type: "textarea",
        full: true,
      },
    ],
  },
  absences: {
    key: "absences",
    label: "Counselor Absences",
    icon: XCircleIcon,
    endpoint: "absences",
    titleField: "counselor_name",
    subtitleField: "absence_type",
    searchKeys: ["counselor_name", "absence_type", "reason"],
    fields: [
      { key: "counselor", label: "Counselor (ID)", full: true },
      { key: "counselor_name", label: "Counselor", skipForm: true },
      {
        key: "absence_type",
        label: "Type",
        type: "select",
        options: ABSENCE_TYPES,
        badge: true,
      },
      { key: "start_date", label: "From", type: "date", card: true },
      { key: "end_date", label: "To", type: "date" },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      { key: "approved_by", label: "Approved By (ID)", full: true },
      { key: "approved_by_name", label: "Approved By", skipForm: true },
      {
        key: "appointments_affected",
        label: "Appts Affected",
        type: "number",
        card: true,
      },
      { key: "students_notified", label: "Students Notified", type: "number" },
    ],
  },
  coverage: {
    key: "coverage",
    label: "Coverage",
    icon: UserGroupIcon,
    endpoint: "coverage",
    titleField: "absent_counselor_name",
    subtitleField: "covering_counselor_name",
    searchKeys: ["absent_counselor_name", "covering_counselor_name", "status"],
    fields: [
      { key: "absent_counselor", label: "Absent Counselor (ID)", full: true },
      {
        key: "absent_counselor_name",
        label: "Absent Counselor",
        skipForm: true,
      },
      {
        key: "covering_counselor",
        label: "Covering Counselor (ID)",
        full: true,
      },
      {
        key: "covering_counselor_name",
        label: "Covering Counselor",
        skipForm: true,
      },
      { key: "absence", label: "Absence (ID)", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: COVERAGE_STATUS,
        badge: true,
      },
      { key: "coverage_date", label: "Date", type: "date", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  counselorProfiles: {
    key: "counselorProfiles",
    label: "Counselor Profiles",
    icon: UserCircleIcon,
    endpoint: "counselor-profiles",
    titleField: "full_name",
    subtitleField: "email",
    searchKeys: ["full_name", "email", "specialties"],
    fields: [
      { key: "user", label: "User (ID)", full: true },
      { key: "full_name", label: "Name", main: true },
      { key: "email", label: "Email", card: true },
      { key: "specialties", label: "Specialties", full: true },
      { key: "certifications", label: "Certifications", full: true },
      { key: "office_hours", label: "Office Hours", card: true },
      { key: "bio", label: "Bio", type: "textarea", full: true },
    ],
  },
  courseRecommendations: {
    key: "courseRecommendations",
    label: "Course Recommendations",
    icon: BookOpenIcon,
    endpoint: "course-recommendations",
    titleField: "course_name",
    subtitleField: "course_code",
    searchKeys: ["course_name", "course_code", "semester", "reason"],
    fields: [
      { key: "advising", label: "Advising (ID)", full: true },
      { key: "course_code", label: "Course Code", card: true },
      { key: "course_name", label: "Course Name", main: true },
      { key: "semester", label: "Semester", card: true },
      {
        key: "priority",
        label: "Priority",
        type: "select",
        options: PRIORITY,
        badge: true,
      },
      { key: "reason", label: "Reason", type: "textarea", full: true },
    ],
  },
  providers: {
    key: "providers",
    label: "External Providers",
    icon: PhoneArrowUpRightIcon,
    endpoint: "providers",
    titleField: "name",
    toggleField: "is_active",
    subtitleField: "provider_type",
    searchKeys: ["name", "provider_type", "organization", "contact_person"],
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "provider_type",
        label: "Type",
        type: "select",
        options: PROVIDER_TYPES,
        badge: true,
      },
      { key: "organization", label: "Organization", card: true },
      { key: "contact_person", label: "Contact Person", card: true },
      { key: "phone", label: "Phone", card: true },
      { key: "email", label: "Email" },
      { key: "address", label: "Address", full: true },
      { key: "specialties", label: "Specialties", full: true },
      { key: "insurance_accepted", label: "Insurance Accepted", full: true },
      {
        key: "referral_process",
        label: "Referral Process",
        type: "textarea",
        full: true,
      },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "rating", label: "Rating", type: "number" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  groupMembers: {
    key: "groupMembers",
    label: "Group Members",
    icon: UsersIcon,
    endpoint: "group-members",
    titleField: "student_name",
    toggleField: "is_active",
    subtitleField: "enrolled_at",
    searchKeys: ["student_name", "notes"],
    fields: [
      { key: "group_session", label: "Group Session (ID)", full: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "enrolled_at", label: "Enrolled", type: "datetime", card: true },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  peerMentors: {
    key: "peerMentors",
    label: "Peer Mentors",
    icon: UserPlusIcon,
    endpoint: "peer-mentors",
    titleField: "student_name",
    subtitleField: "status",
    searchKeys: ["student_name", "status", "specialties"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "supervisor", label: "Supervisor (ID)", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: PEER_MENTOR_STATUS,
        badge: true,
      },
      { key: "training_completed", label: "Trained", type: "bool" },
      { key: "training_date", label: "Training Date", type: "date" },
      { key: "specialties", label: "Specialties", full: true },
      { key: "max_mentees", label: "Max Mentees", type: "number" },
      {
        key: "current_mentees",
        label: "Current Mentees",
        type: "number",
        card: true,
      },
      {
        key: "total_sessions",
        label: "Total Sessions",
        type: "number",
        card: true,
      },
      { key: "avg_rating", label: "Avg Rating", type: "number" },
    ],
  },
  peerMentoringSessions: {
    key: "peerMentoringSessions",
    label: "Mentoring Sessions",
    icon: ChatBubbleLeftRightIcon,
    endpoint: "peer-mentoring-sessions",
    titleField: "mentor_name",
    subtitleField: "mentee_name",
    searchKeys: ["mentor_name", "mentee_name", "status", "topics_covered"],
    fields: [
      { key: "mentor", label: "Mentor (ID)", full: true },
      { key: "mentor_name", label: "Mentor", skipForm: true },
      { key: "mentee", label: "Mentee (ID)", full: true },
      { key: "mentee_name", label: "Mentee", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
          ["no_show", "No Show"],
        ] as [string, string][],
        badge: true,
      },
      { key: "session_date", label: "Date", type: "date", card: true },
      { key: "session_time", label: "Time", card: true },
      { key: "duration_minutes", label: "Duration (min)", type: "number" },
      { key: "location", label: "Location", card: true },
      { key: "topics_covered", label: "Topics", type: "textarea", full: true },
      {
        key: "mentor_notes",
        label: "Mentor Notes",
        type: "textarea",
        full: true,
      },
      {
        key: "mentee_feedback",
        label: "Mentee Feedback",
        type: "textarea",
        full: true,
      },
      { key: "rating", label: "Rating", type: "number" },
    ],
  },
  referralTracking: {
    key: "referralTracking",
    label: "Referral Tracking",
    icon: ArrowPathIcon,
    endpoint: "referral-tracking",
    titleField: "student_name",
    subtitleField: "provider_name",
    searchKeys: ["student_name", "provider_name", "status", "urgency"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "provider", label: "Provider (ID)", full: true },
      { key: "provider_name", label: "Provider", skipForm: true },
      { key: "referred_by", label: "Referred By (ID)", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: REFERRAL_TRACK_STATUS,
        badge: true,
      },
      {
        key: "urgency",
        label: "Urgency",
        type: "select",
        options: URGENCY,
        badge: true,
      },
      {
        key: "referral_date",
        label: "Referral Date",
        type: "date",
        card: true,
      },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      { key: "appointment_date", label: "Appointment", type: "date" },
      { key: "follow_up_date", label: "Follow-up", type: "date" },
      { key: "outcome_notes", label: "Outcome", type: "textarea", full: true },
      { key: "parent_consent", label: "Parent Consent", type: "bool" },
      { key: "parent_contacted", label: "Parent Contacted", type: "bool" },
    ],
  },
  restorativeCommitments: {
    key: "restorativeCommitments",
    label: "Restorative Commitments",
    icon: CheckCircleIcon,
    endpoint: "restorative-commitments",
    titleField: "commitment",
    subtitleField: "student_name",
    searchKeys: ["commitment", "student_name", "status"],
    fields: [
      { key: "session", label: "Session (ID)", full: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "verified_by", label: "Verified By (ID)", full: true },
      { key: "commitment", label: "Commitment", type: "textarea", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: COMMITMENT_STATUS,
        badge: true,
      },
      { key: "due_date", label: "Due", type: "date", card: true },
      { key: "completed_date", label: "Completed", type: "date" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  restorativeSessions: {
    key: "restorativeSessions",
    label: "Restorative Sessions",
    icon: UserGroupIcon,
    endpoint: "restorative-sessions",
    titleField: "session_type",
    subtitleField: "scheduled_date",
    searchKeys: ["session_type", "status", "incident_description", "outcome"],
    fields: [
      { key: "facilitator", label: "Facilitator (ID)", full: true },
      {
        key: "session_type",
        label: "Type",
        type: "select",
        options: RESTORATIVE_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: SESSION_STATUS,
        badge: true,
      },
      { key: "scheduled_date", label: "Date", type: "date", card: true },
      { key: "scheduled_time", label: "Time", card: true },
      { key: "location", label: "Location", card: true },
      { key: "participant_count", label: "Participants", type: "number" },
      {
        key: "incident_description",
        label: "Incident",
        type: "textarea",
        full: true,
      },
      {
        key: "harm_caused",
        label: "Harm Caused",
        type: "textarea",
        full: true,
      },
      {
        key: "needs_identified",
        label: "Needs Identified",
        type: "textarea",
        full: true,
      },
      { key: "agreements", label: "Agreements", type: "textarea", full: true },
      {
        key: "outcome",
        label: "Outcome",
        type: "select",
        options: RESTORATIVE_OUTCOMES,
        badge: true,
      },
      {
        key: "outcome_notes",
        label: "Outcome Notes",
        type: "textarea",
        full: true,
      },
      { key: "agreements_met", label: "Agreements Met", type: "bool" },
      { key: "follow_up_date", label: "Follow-up", type: "date" },
    ],
  },
  selAssessments: {
    key: "selAssessments",
    label: "SEL Assessments",
    icon: SparklesIcon,
    endpoint: "sel-assessments",
    titleField: "student_name",
    subtitleField: "domain",
    searchKeys: ["student_name", "domain"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "assessor", label: "Assessor (ID)", full: true },
      {
        key: "domain",
        label: "Domain",
        type: "select",
        options: SEL_DOMAINS,
        badge: true,
      },
      { key: "assessment_date", label: "Date", type: "date", card: true },
      { key: "score", label: "Score", type: "number", card: true },
      { key: "max_score", label: "Max Score", type: "number" },
      {
        key: "strength_areas",
        label: "Strength Areas",
        type: "textarea",
        full: true,
      },
      {
        key: "growth_areas",
        label: "Growth Areas",
        type: "textarea",
        full: true,
      },
      {
        key: "recommendations",
        label: "Recommendations",
        type: "textarea",
        full: true,
      },
      {
        key: "intervention_suggested",
        label: "Intervention Suggested",
        type: "bool",
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  selGoals: {
    key: "selGoals",
    label: "SEL Goals",
    icon: FireIcon,
    endpoint: "sel-goals",
    titleField: "goal_description",
    subtitleField: "student_name",
    searchKeys: ["goal_description", "student_name", "domain", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "counselor", label: "Counselor (ID)", full: true },
      {
        key: "domain",
        label: "Domain",
        type: "select",
        options: SEL_DOMAINS,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: SEL_GOAL_STATUS,
        badge: true,
      },
      { key: "goal_description", label: "Goal", type: "textarea", full: true },
      {
        key: "measurable_outcome",
        label: "Measurable Outcome",
        type: "textarea",
        full: true,
      },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "target_date", label: "Target", type: "date" },
      { key: "achieved_date", label: "Achieved", type: "date" },
      { key: "strategies", label: "Strategies", type: "textarea", full: true },
      {
        key: "progress_notes",
        label: "Progress Notes",
        type: "textarea",
        full: true,
      },
    ],
  },
  sessionAttachments: {
    key: "sessionAttachments",
    label: "Session Attachments",
    icon: InboxIcon,
    endpoint: "session-attachments",
    titleField: "file_name",
    subtitleField: "uploaded_by_name",
    searchKeys: ["file_name", "description", "uploaded_by_name"],
    fields: [
      { key: "session", label: "Session (ID)", full: true },
      { key: "file", label: "File", full: true },
      { key: "file_name", label: "File Name", main: true },
      { key: "uploaded_by", label: "Uploaded By (ID)", full: true },
      { key: "uploaded_by_name", label: "Uploaded By", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
    ],
  },
  specialEducationReferrals: {
    key: "specialEducationReferrals",
    label: "Special Ed Referrals",
    icon: AcademicCapIcon,
    endpoint: "special-education-referrals",
    titleField: "student_name",
    subtitleField: "referral_type",
    searchKeys: ["student_name", "referral_type", "status", "reason"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "referred_by", label: "Referred By (ID)", full: true },
      { key: "evaluator", label: "Evaluator (ID)", full: true },
      {
        key: "referral_type",
        label: "Type",
        type: "select",
        options: SPECIAL_ED_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: SPECIAL_ED_STATUS,
        badge: true,
      },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      {
        key: "supporting_data",
        label: "Supporting Data",
        type: "textarea",
        full: true,
      },
      { key: "evaluation_date", label: "Eval Date", type: "date", card: true },
      {
        key: "evaluation_results",
        label: "Eval Results",
        type: "textarea",
        full: true,
      },
      { key: "plan_type", label: "Plan Type", card: true },
      { key: "plan_review_date", label: "Plan Review", type: "date" },
      { key: "parent_consent", label: "Parent Consent", type: "bool" },
      { key: "parent_notified", label: "Parent Notified", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
};

const TABS: {
  key: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = Object.values(ENTITY_CONFIGS).map((c) => ({
  key: c.key,
  label: c.label,
  icon: c.icon,
}));

// ─── Main page ───────────────────────────────────────────────────────────────

export default function CounselingCenterPage() {
  useTitle("Counseling Center");
  const [activeTab, setActiveTab] = useState("appointments");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Counseling Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Appointments, referrals, crisis response, SEL, cases, college &amp; career, workshops
            and restorative practice
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
            leftIcon={<HeartIcon className="h-4 w-4" />}
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
        basePath="/counseling"
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
