/**
 * Academics Hub — full-surface admin page for the academics module.
 *
 * 30 entity tabs (config-driven via EntitySection): subjects, assignments,
 * lesson plans, curriculum, syllabi, evaluations, transcripts, academic
 * calendar, homework, exams, analytics, versioning and course catalog.
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
  BookOpenIcon,
  AcademicCapIcon,
  ChartBarIcon,
  ClipboardDocumentCheckIcon,
  CalendarDaysIcon,
  DocumentTextIcon,
  WrenchScrewdriverIcon,
  BellAlertIcon,
  QueueListIcon,
  ScaleIcon,
  StarIcon,
  CircleStackIcon,
  IdentificationIcon,
  TrophyIcon,
  UserGroupIcon,
  ClipboardDocumentListIcon,
  DocumentChartBarIcon,
  CheckBadgeIcon,
  LinkIcon,
  SunIcon,
} from "@heroicons/react/24/outline";

// ─── Shared option sets ──────────────────────────────────────────────────────

const QUALIFICATIONS = [
  ["diploma", "Diploma"],
  ["bachelor", "Bachelor"],
  ["master", "Master"],
  ["phd", "PhD"],
] as [string, string][];

const ENROLLMENT_STATUS = [
  ["active", "Active"],
  ["dropped", "Dropped"],
  ["transferred", "Transferred"],
  ["completed", "Completed"],
] as [string, string][];

const FRAMEWORKS = [
  ["common_core", "Common Core"],
  ["ngss", "NGSS"],
  ["cbse", "CBSE"],
  ["ncert", "NCERT"],
  ["national_uk", "National UK"],
  ["ib", "IB"],
  ["custom", "Custom"],
] as [string, string][];

const COVERAGE_LEVELS = [
  ["full", "Full"],
  ["partial", "Partial"],
  ["introduced", "Introduced"],
  ["not_covered", "Not Covered"],
] as [string, string][];

const REVIEW_STATUS = [
  ["draft", "Draft"],
  ["under_review", "Under Review"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["completed", "Completed"],
] as [string, string][];

const TOPIC_STATUS = [
  ["not_started", "Not Started"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["skipped", "Skipped"],
] as [string, string][];

const CRITERIA_CATEGORIES = [
  ["planning", "Planning"],
  ["instruction", "Instruction"],
  ["classroom", "Classroom"],
  ["assessment", "Assessment"],
  ["professional", "Professional"],
  ["communication", "Communication"],
  ["student", "Student"],
  ["other", "Other"],
] as [string, string][];

const EVAL_TYPES = [
  ["observation", "Observation"],
  ["self", "Self"],
  ["peer", "Peer"],
  ["student_feedback", "Student Feedback"],
  ["performance", "Performance"],
  ["probationary", "Probationary"],
] as [string, string][];

const EVAL_STATUS = [
  ["draft", "Draft"],
  ["self_review", "Self Review"],
  ["peer_review", "Peer Review"],
  ["admin_review", "Admin Review"],
  ["completed", "Completed"],
  ["archived", "Archived"],
] as [string, string][];

const TRANSCRIPT_STATUS = [
  ["draft", "Draft"],
  ["generated", "Generated"],
  ["verified", "Verified"],
  ["archived", "Archived"],
] as [string, string][];

const EVENT_TYPES = [
  ["exam", "Exam"],
  ["ptm", "Parent-Teacher"],
  ["holiday", "Holiday"],
  ["milestone", "Milestone"],
  ["enrollment", "Enrollment"],
  ["report_card", "Report Card"],
  ["orientation", "Orientation"],
  ["field_trip", "Field Trip"],
  ["cultural", "Cultural"],
  ["sports", "Sports"],
  ["other", "Other"],
] as [string, string][];

const ASSIGNMENT_TYPES = [
  ["homework", "Homework"],
  ["classwork", "Classwork"],
  ["project", "Project"],
  ["quiz", "Quiz"],
  ["lab", "Lab"],
  ["reading", "Reading"],
  ["other", "Other"],
] as [string, string][];

const ASSIGNMENT_STATUS = [
  ["draft", "Draft"],
  ["published", "Published"],
  ["closed", "Closed"],
  ["archived", "Archived"],
] as [string, string][];

const SUBMISSION_STATUS = [
  ["submitted", "Submitted"],
  ["late", "Late"],
  ["graded", "Graded"],
  ["returned", "Returned"],
  ["resubmitted", "Resubmitted"],
] as [string, string][];

const QUESTION_TYPES = [
  ["mcq", "MCQ"],
  ["tf", "True/False"],
  ["short", "Short Answer"],
  ["long", "Long Answer"],
  ["fill", "Fill in Blank"],
  ["match", "Matching"],
  ["essay", "Essay"],
  ["numerical", "Numerical"],
] as [string, string][];

const DIFFICULTIES = [
  ["easy", "Easy"],
  ["medium", "Medium"],
  ["hard", "Hard"],
] as [string, string][];

const PAPER_STATUS = [
  ["draft", "Draft"],
  ["finalized", "Finalized"],
  ["used", "Used"],
] as [string, string][];

const NOTIFICATION_TYPES = [
  ["lesson_plan_approved", "Lesson Plan Approved"],
  ["lesson_plan_rejected", "Lesson Plan Rejected"],
  ["assignment_posted", "Assignment Posted"],
  ["assignment_graded", "Assignment Graded"],
  ["assignment_due_soon", "Assignment Due Soon"],
  ["grade_published", "Grade Published"],
  ["transcript_ready", "Transcript Ready"],
  ["evaluation_status", "Evaluation Status"],
  ["exam_scheduled", "Exam Scheduled"],
  ["term_start", "Term Start"],
  ["enrollment_deadline", "Enrollment Deadline"],
  ["attendance_alert", "Attendance Alert"],
  ["general", "General"],
] as [string, string][];

const PRIORITIES = [
  ["low", "Low"],
  ["normal", "Normal"],
  ["high", "High"],
  ["urgent", "Urgent"],
] as [string, string][];

const TRENDS = [
  ["improving", "Improving"],
  ["stable", "Stable"],
  ["declining", "Declining"],
  ["insufficient", "Insufficient"],
] as [string, string][];

const DIFFICULTY_LEVELS = [
  ["beginner", "Beginner"],
  ["intermediate", "Intermediate"],
  ["advanced", "Advanced"],
  ["all", "All Levels"],
] as [string, string][];

const INTENT_STATUS = [
  ["interested", "Interested"],
  ["waitlisted", "Waitlisted"],
  ["enrolled", "Enrolled"],
  ["declined", "Declined"],
] as [string, string][];

// ─── Entity configs (30 tabs) ────────────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  subjects: {
    key: "subjects",
    label: "Subject",
    icon: BookOpenIcon,
    endpoint: "subjects",
    titleField: "name",
    subtitleField: "code",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "code", label: "Code", subtitle: true },
      { key: "grade_name", label: "Grade", card: true, skipForm: true },
      { key: "grade", label: "Grade ID", card: true },
      { key: "is_core", label: "Core", type: "bool", badge: true },
      { key: "is_elective", label: "Elective", type: "bool", badge: true },
      { key: "max_marks", label: "Max Marks", type: "number", card: true },
      { key: "pass_marks", label: "Pass Marks", type: "number", card: true },
      { key: "credit_hours", label: "Credit Hours", type: "number", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["name", "code", "grade_name", "description"],
  },
  assignments: {
    key: "assignments",
    label: "Teacher Assignment",
    icon: UserGroupIcon,
    endpoint: "assignments",
    titleField: "subject_name",
    subtitleField: "teacher_name",
    fields: [
      { key: "subject_name", label: "Subject", main: true, skipForm: true },
      { key: "subject", label: "Subject ID", skipForm: true },
      { key: "teacher_name", label: "Teacher", subtitle: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", card: true },
      { key: "classroom_name", label: "Classroom", card: true, skipForm: true },
      { key: "classroom", label: "Classroom ID", card: true },
      { key: "academic_year_name", label: "Academic Year", card: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      { key: "is_primary", label: "Primary", type: "bool", badge: true },
    ],
    searchKeys: ["subject_name", "teacher_name", "classroom_name"],
  },
  "teacher-profiles": {
    key: "teacher-profiles",
    label: "Teacher Profile",
    icon: AcademicCapIcon,
    endpoint: "teacher-profiles",
    titleField: "full_name",
    subtitleField: "specialization",
    toggleField: "is_active",
    fields: [
      { key: "full_name", label: "Name", main: true, skipForm: true },
      { key: "user", label: "User ID", skipForm: true },
      { key: "specialization", label: "Specialization", subtitle: true, card: true },
      { key: "email", label: "Email", card: true, skipForm: true },
      { key: "phone", label: "Phone", card: true },
      { key: "employee_id", label: "Employee ID", card: true },
      {
        key: "qualification",
        label: "Qualification",
        type: "select",
        options: QUALIFICATIONS,
        badge: true,
      },
      { key: "department", label: "Department", card: true },
      { key: "experience_years", label: "Experience (yrs)", type: "number", card: true },
      { key: "joining_date", label: "Joining Date", type: "date", card: true },
      { key: "date_of_birth", label: "DOB", type: "date", card: true },
      { key: "gender", label: "Gender", card: true },
      { key: "address", label: "Address", type: "textarea", full: true },
      { key: "bio", label: "Bio", type: "textarea", full: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
    ],
    searchKeys: ["full_name", "specialization", "email", "department", "employee_id"],
  },
  "lesson-plans": {
    key: "lesson-plans",
    label: "Lesson Plan",
    icon: DocumentTextIcon,
    endpoint: "lesson-plans",
    titleField: "title",
    subtitleField: "subject_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      { key: "assignment", label: "Assignment ID", card: true },
      { key: "teacher_name", label: "Teacher", card: true, skipForm: true },
      { key: "classroom_name", label: "Classroom", card: true, skipForm: true },
      { key: "topic", label: "Topic", card: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "duration_minutes", label: "Duration (min)", type: "number", card: true },
      { key: "status", label: "Status", type: "select", options: REVIEW_STATUS, badge: true },
      { key: "objectives", label: "Objectives", type: "textarea", full: true, card: true },
      { key: "content", label: "Content", type: "textarea", full: true },
      { key: "resources", label: "Resources", type: "textarea", full: true },
    ],
    searchKeys: ["title", "topic", "subject_name", "teacher_name"],
  },
  "student-subject-enrollments": {
    key: "student-subject-enrollments",
    label: "Subject Enrollment",
    icon: IdentificationIcon,
    endpoint: "student-subject-enrollments",
    titleField: "student_name",
    subtitleField: "subject_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      { key: "subject", label: "Subject ID", card: true },
      { key: "admission_number", label: "Admission #", card: true, skipForm: true },
      { key: "grade_name", label: "Grade", card: true, skipForm: true },
      { key: "academic_year_name", label: "Academic Year", card: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      { key: "enrolled_date", label: "Enrolled", type: "date", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: ENROLLMENT_STATUS, badge: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "subject_name", "admission_number", "status"],
  },
  "curriculum-standards": {
    key: "curriculum-standards",
    label: "Curriculum Standard",
    icon: ScaleIcon,
    endpoint: "curriculum-standards",
    titleField: "name",
    subtitleField: "code",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "code", label: "Code", subtitle: true },
      { key: "framework", label: "Framework", type: "select", options: FRAMEWORKS, badge: true },
      { key: "grade_name", label: "Grade", card: true, skipForm: true },
      { key: "grade", label: "Grade ID", card: true },
      { key: "subject_name", label: "Subject", card: true, skipForm: true },
      { key: "subject", label: "Subject ID", card: true },
      { key: "domain", label: "Domain", card: true },
      { key: "cluster", label: "Cluster", card: true },
      { key: "mappings_count", label: "Mappings", type: "number", card: true, skipForm: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["name", "code", "framework", "domain"],
  },
  "subject-standard-mappings": {
    key: "subject-standard-mappings",
    label: "Standard Mapping",
    icon: LinkIcon,
    endpoint: "subject-standard-mappings",
    titleField: "subject_name",
    subtitleField: "standard_name",
    fields: [
      { key: "subject_name", label: "Subject", main: true, skipForm: true },
      { key: "subject", label: "Subject ID", skipForm: true },
      { key: "standard_name", label: "Standard", subtitle: true, skipForm: true },
      { key: "standard", label: "Standard ID", card: true },
      { key: "standard_code", label: "Standard Code", card: true, skipForm: true },
      { key: "standard_framework", label: "Framework", card: true, skipForm: true },
      { key: "academic_year_name", label: "Academic Year", card: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      {
        key: "coverage_level",
        label: "Coverage",
        type: "select",
        options: COVERAGE_LEVELS,
        badge: true,
      },
      { key: "mapped_by_name", label: "Mapped By", card: true, skipForm: true },
      { key: "mapped_by", label: "Mapped By ID", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["subject_name", "standard_name", "standard_code", "coverage_level"],
  },
  syllabi: {
    key: "syllabi",
    label: "Syllabus",
    icon: BookOpenIcon,
    endpoint: "syllabi",
    titleField: "title",
    subtitleField: "subject_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      { key: "subject", label: "Subject ID", skipForm: true },
      { key: "grade_name", label: "Grade", card: true, skipForm: true },
      { key: "academic_year_name", label: "Academic Year", card: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      { key: "term", label: "Term", card: true },
      { key: "total_hours", label: "Total Hours", type: "number", card: true },
      { key: "status", label: "Status", type: "select", options: REVIEW_STATUS, badge: true },
      { key: "topic_count", label: "Topics", type: "number", card: true, skipForm: true },
      {
        key: "completed_topic_count",
        label: "Completed",
        type: "number",
        card: true,
        skipForm: true,
      },
      {
        key: "progress_percentage",
        label: "Progress %",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", card: true },
      { key: "approved_by_name", label: "Approved By", card: true, skipForm: true },
      { key: "approved_by", label: "Approved By ID", card: true },
      { key: "approved_at", label: "Approved At", type: "datetime", card: true, skipForm: true },
      { key: "rejection_reason", label: "Rejection Reason", type: "textarea", full: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "learning_objectives", label: "Learning Objectives", type: "textarea", full: true },
      { key: "resources", label: "Resources", type: "textarea", full: true },
      { key: "assessment_criteria", label: "Assessment Criteria", type: "textarea", full: true },
    ],
    searchKeys: ["title", "subject_name", "status"],
  },
  "workload-config": {
    key: "workload-config",
    label: "Workload Config",
    icon: WrenchScrewdriverIcon,
    endpoint: "workload-config",
    titleField: "max_periods_per_week",
    subtitleField: "warning_threshold_pct",
    toggleField: "is_active",
    fields: [
      { key: "max_periods_per_week", label: "Max Periods/Week", main: true, type: "number" },
      {
        key: "warning_threshold_pct",
        label: "Warning Threshold %",
        subtitle: true,
        type: "number",
      },
      { key: "max_periods_per_day", label: "Max Periods/Day", type: "number", card: true },
      { key: "max_subjects", label: "Max Subjects", type: "number", card: true },
      { key: "max_classes", label: "Max Classes", type: "number", card: true },
      { key: "min_periods_per_week", label: "Min Periods/Week", type: "number", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
    ],
    searchKeys: ["max_periods_per_week", "warning_threshold_pct"],
  },
  "evaluation-criteria": {
    key: "evaluation-criteria",
    label: "Evaluation Criterion",
    icon: CheckBadgeIcon,
    endpoint: "evaluation-criteria",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: CRITERIA_CATEGORIES,
        badge: true,
      },
      { key: "max_score", label: "Max Score", type: "number", card: true },
      { key: "weight", label: "Weight %", type: "number", card: true },
      { key: "order", label: "Order", type: "number", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["name", "category", "description"],
  },
  "evaluation-templates": {
    key: "evaluation-templates",
    label: "Evaluation Template",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "evaluation-templates",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "eval_type", label: "Type", type: "select", options: EVAL_TYPES, badge: true },
      { key: "criteria_ids", label: "Criteria IDs", type: "textarea", full: true, card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["name", "eval_type", "description"],
  },
  evaluations: {
    key: "evaluations",
    label: "Teacher Evaluation",
    icon: StarIcon,
    endpoint: "evaluations",
    titleField: "title",
    subtitleField: "teacher_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "teacher_name", label: "Teacher", subtitle: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", skipForm: true },
      { key: "template_name", label: "Template", card: true, skipForm: true },
      { key: "template", label: "Template ID", card: true },
      { key: "academic_year_name", label: "Academic Year", card: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      { key: "evaluation_period", label: "Period", card: true },
      { key: "status", label: "Status", type: "select", options: EVAL_STATUS, badge: true },
      { key: "overall_score", label: "Score", type: "number", card: true, skipForm: true },
      { key: "score_percentage", label: "Score %", type: "number", card: true, skipForm: true },
      { key: "score_display", label: "Grade", card: true, skipForm: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "strength", label: "Strengths", type: "textarea", full: true },
      { key: "areas_for_growth", label: "Areas for Growth", type: "textarea", full: true },
      { key: "action_plan", label: "Action Plan", type: "textarea", full: true },
      { key: "evaluator_notes", label: "Evaluator Notes", type: "textarea", full: true },
      { key: "teacher_comments", label: "Teacher Comments", type: "textarea", full: true },
    ],
    searchKeys: ["title", "teacher_name", "status"],
  },
  transcripts: {
    key: "transcripts",
    label: "Transcript",
    icon: DocumentChartBarIcon,
    endpoint: "transcripts",
    titleField: "student_name",
    subtitleField: "transcript_number",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "transcript_number", label: "Transcript #", subtitle: true, skipForm: true },
      { key: "admission_number", label: "Admission #", card: true, skipForm: true },
      { key: "grade_name", label: "Grade", card: true, skipForm: true },
      { key: "classroom_name", label: "Classroom", card: true, skipForm: true },
      { key: "academic_year_name", label: "Academic Year", card: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      { key: "status", label: "Status", type: "select", options: TRANSCRIPT_STATUS, badge: true },
      { key: "total_marks", label: "Total Marks", type: "number", card: true, skipForm: true },
      { key: "obtained_marks", label: "Obtained", type: "number", card: true, skipForm: true },
      { key: "percentage", label: "Percentage", type: "number", card: true, skipForm: true },
      { key: "gpa", label: "GPA", card: true, skipForm: true },
      { key: "grade_letter", label: "Grade", card: true, skipForm: true },
      { key: "rank_in_class", label: "Class Rank", card: true, skipForm: true },
      { key: "rank_in_grade", label: "Grade Rank", card: true, skipForm: true },
      {
        key: "attendance_percentage",
        label: "Attendance %",
        type: "number",
        card: true,
        skipForm: true,
      },
    ],
    searchKeys: ["student_name", "transcript_number", "status"],
  },
  terms: {
    key: "terms",
    label: "Academic Term",
    icon: CalendarDaysIcon,
    endpoint: "terms",
    titleField: "name",
    subtitleField: "academic_year_name",
    toggleField: "is_current",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "academic_year_name", label: "Academic Year", subtitle: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      { key: "term_type", label: "Term Type", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "report_card_date", label: "Report Cards", type: "date", card: true },
      { key: "parent_teacher_date", label: "Parent-Teacher", type: "date", card: true },
      { key: "enrollment_deadline", label: "Enrollment Deadline", type: "date", card: true },
      { key: "is_current", label: "Current", type: "bool", badge: true },
      {
        key: "duration_days",
        label: "Duration (days)",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "events_count", label: "Events", type: "number", card: true, skipForm: true },
    ],
    searchKeys: ["name", "academic_year_name", "term_type"],
  },
  events: {
    key: "events",
    label: "Academic Event",
    icon: CalendarDaysIcon,
    endpoint: "events",
    titleField: "title",
    subtitleField: "event_type_display",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "event_type",
        label: "Type",
        type: "select",
        options: EVENT_TYPES,
        subtitle: true,
        badge: true,
      },
      { key: "academic_year_name", label: "Academic Year", card: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      { key: "term_name", label: "Term", card: true, skipForm: true },
      { key: "term", label: "Term ID", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "start_time", label: "Start Time", card: true },
      { key: "end_time", label: "End Time", card: true },
      { key: "is_all_day", label: "All Day", type: "bool", card: true },
      { key: "location", label: "Location", card: true },
      { key: "is_recurring", label: "Recurring", type: "bool", card: true },
      { key: "recurrence_rule", label: "Recurrence", card: true },
      { key: "affected_grades", label: "Affected Grades", card: true },
      { key: "affected_subjects", label: "Affected Subjects", card: true },
      { key: "is_published", label: "Published", type: "bool", badge: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["title", "event_type", "location"],
  },
  holidays: {
    key: "holidays",
    label: "Academic Holiday",
    icon: SunIcon,
    endpoint: "holidays",
    titleField: "name",
    subtitleField: "date",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "date", label: "Date", type: "date", subtitle: true, card: true },
      { key: "end_date", label: "End Date", type: "date", card: true },
      { key: "holiday_type", label: "Type", card: true },
      { key: "academic_year", label: "Academic Year", card: true },
      {
        key: "duration_days",
        label: "Duration (days)",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["name", "holiday_type", "description"],
  },
  "homework-assignments": {
    key: "homework-assignments",
    label: "Homework Assignment",
    icon: DocumentTextIcon,
    endpoint: "homework-assignments",
    titleField: "title",
    subtitleField: "subject_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      {
        key: "assignment_type",
        label: "Type",
        type: "select",
        options: ASSIGNMENT_TYPES,
        badge: true,
      },
      { key: "status", label: "Status", type: "select", options: ASSIGNMENT_STATUS, badge: true },
      { key: "teacher_name", label: "Teacher", card: true, skipForm: true },
      { key: "classroom_name", label: "Classroom", card: true, skipForm: true },
      { key: "due_date", label: "Due Date", type: "date", card: true },
      { key: "due_time", label: "Due Time", card: true },
      { key: "max_score", label: "Max Score", type: "number", card: true },
      { key: "weight_percentage", label: "Weight %", type: "number", card: true },
      { key: "allow_late_submissions", label: "Allow Late", type: "bool", card: true },
      { key: "late_penalty_per_day", label: "Late Penalty/Day", type: "number", card: true },
      { key: "is_overdue", label: "Overdue", type: "bool", badge: true, skipForm: true },
      { key: "submission_count", label: "Submissions", type: "number", card: true, skipForm: true },
      { key: "average_score", label: "Avg Score", type: "number", card: true, skipForm: true },
      { key: "published_at", label: "Published", type: "datetime", card: true, skipForm: true },
      { key: "created_by", label: "Created By", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "attachments", label: "Attachments", type: "textarea", full: true },
    ],
    searchKeys: ["title", "subject_name", "teacher_name", "status"],
  },
  submissions: {
    key: "submissions",
    label: "Submission",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "submissions",
    titleField: "student_name",
    subtitleField: "assignment_title",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "assignment_title", label: "Assignment", subtitle: true, skipForm: true },
      { key: "assignment", label: "Assignment ID", card: true },
      { key: "status", label: "Status", type: "select", options: SUBMISSION_STATUS, badge: true },
      { key: "is_late", label: "Late", type: "bool", badge: true, skipForm: true },
      { key: "submitted_at", label: "Submitted", type: "datetime", card: true, skipForm: true },
      { key: "score", label: "Score", type: "number", card: true },
      { key: "score_percentage", label: "Score %", type: "number", card: true, skipForm: true },
      { key: "grade_letter", label: "Grade", card: true, skipForm: true },
      { key: "graded_by_name", label: "Graded By", card: true, skipForm: true },
      { key: "graded_by", label: "Graded By ID", card: true },
      { key: "graded_at", label: "Graded At", type: "datetime", card: true, skipForm: true },
      {
        key: "submission_number",
        label: "Submission #",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "content", label: "Content", type: "textarea", full: true, card: true },
      { key: "attachments", label: "Attachments", type: "textarea", full: true },
      { key: "feedback", label: "Feedback", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "assignment_title", "status"],
  },
  "homework-tracker": {
    key: "homework-tracker",
    label: "Homework Tracker",
    icon: ClipboardDocumentListIcon,
    endpoint: "homework-tracker",
    titleField: "classroom_name",
    subtitleField: "subject_name",
    fields: [
      { key: "classroom_name", label: "Classroom", main: true, skipForm: true },
      { key: "classroom", label: "Classroom ID", skipForm: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      { key: "subject", label: "Subject ID", card: true },
      { key: "teacher_name", label: "Teacher", card: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", card: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "due_date", label: "Due", type: "date", card: true },
      { key: "is_completed", label: "Completed", type: "bool", badge: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["classroom_name", "subject_name", "teacher_name"],
  },
  "question-bank": {
    key: "question-bank",
    label: "Question Bank",
    icon: QueueListIcon,
    endpoint: "question-bank",
    titleField: "question_text",
    subtitleField: "subject_name",
    toggleField: "is_active",
    fields: [
      { key: "question_text", label: "Question", main: true, type: "textarea", full: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      { key: "subject", label: "Subject ID", card: true },
      { key: "question_type", label: "Type", type: "select", options: QUESTION_TYPES, badge: true },
      {
        key: "difficulty",
        label: "Difficulty",
        type: "select",
        options: DIFFICULTIES,
        badge: true,
      },
      { key: "marks", label: "Marks", type: "number", card: true },
      { key: "usage_count", label: "Usage", type: "number", card: true, skipForm: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "options", label: "Options", type: "textarea", full: true, card: true },
      { key: "correct_answer", label: "Correct Answer", type: "textarea", full: true },
      { key: "explanation", label: "Explanation", type: "textarea", full: true },
      { key: "tags", label: "Tags", card: true },
    ],
    searchKeys: ["question_text", "subject_name", "question_type", "difficulty", "tags"],
  },
  "exam-papers": {
    key: "exam-papers",
    label: "Exam Paper",
    icon: ClipboardDocumentListIcon,
    endpoint: "exam-papers",
    titleField: "title",
    subtitleField: "subject_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      { key: "subject", label: "Subject ID", card: true },
      { key: "status", label: "Status", type: "select", options: PAPER_STATUS, badge: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "total_marks", label: "Total Marks", type: "number", card: true },
      { key: "duration_minutes", label: "Duration (min)", type: "number", card: true },
      { key: "question_count", label: "Questions", type: "number", card: true, skipForm: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
      { key: "created_by", label: "Created By ID", card: true },
      { key: "questions", label: "Questions", type: "textarea", full: true, card: true },
      { key: "question_distribution", label: "Distribution", type: "textarea", full: true },
    ],
    searchKeys: ["title", "subject_name", "status"],
  },
  notifications: {
    key: "notifications",
    label: "Academic Notification",
    icon: BellAlertIcon,
    endpoint: "notifications",
    titleField: "title",
    subtitleField: "recipient_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "recipient_name", label: "Recipient", subtitle: true, skipForm: true },
      { key: "recipient", label: "Recipient ID", card: true },
      {
        key: "notification_type",
        label: "Type",
        type: "select",
        options: NOTIFICATION_TYPES,
        badge: true,
      },
      { key: "priority", label: "Priority", type: "select", options: PRIORITIES, badge: true },
      { key: "is_read", label: "Read", type: "bool", badge: true },
      { key: "is_emailed", label: "Emailed", type: "bool", card: true, skipForm: true },
      { key: "read_at", label: "Read At", type: "datetime", card: true, skipForm: true },
      { key: "action_url", label: "Action URL", card: true },
      { key: "message", label: "Message", type: "textarea", full: true, card: true },
      { key: "metadata", label: "Metadata", type: "textarea", full: true },
    ],
    searchKeys: ["title", "recipient_name", "notification_type", "priority"],
  },
  "subject-performance": {
    key: "subject-performance",
    label: "Subject Performance",
    icon: ChartBarIcon,
    endpoint: "subject-performance",
    titleField: "subject_name",
    subtitleField: "term_name",
    fields: [
      { key: "subject_name", label: "Subject", main: true, skipForm: true },
      { key: "subject", label: "Subject ID", skipForm: true },
      { key: "term_name", label: "Term", subtitle: true, skipForm: true },
      { key: "term", label: "Term ID", card: true },
      { key: "academic_year_name", label: "Academic Year", card: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      { key: "total_students", label: "Students", type: "number", card: true },
      { key: "average_score", label: "Average", type: "number", card: true },
      { key: "median_score", label: "Median", type: "number", card: true },
      { key: "highest_score", label: "Highest", type: "number", card: true },
      { key: "lowest_score", label: "Lowest", type: "number", card: true },
      { key: "pass_rate", label: "Pass Rate %", type: "number", card: true, badge: true },
      { key: "calculated_at", label: "Calculated", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["subject_name", "term_name"],
  },
  "student-progress": {
    key: "student-progress",
    label: "Student Progress",
    icon: ChartBarIcon,
    endpoint: "student-progress",
    titleField: "student_name",
    subtitleField: "subject_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      { key: "subject", label: "Subject ID", card: true },
      { key: "term_name", label: "Term", card: true, skipForm: true },
      { key: "term", label: "Term ID", card: true },
      { key: "academic_year_name", label: "Academic Year", card: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      { key: "current_score", label: "Current Score", type: "number", card: true },
      { key: "previous_score", label: "Previous Score", type: "number", card: true },
      { key: "score_change", label: "Change", type: "number", card: true, skipForm: true },
      { key: "trend", label: "Trend", type: "select", options: TRENDS, badge: true },
      { key: "attendance_rate", label: "Attendance %", type: "number", card: true },
      { key: "assignment_completion_rate", label: "Completion %", type: "number", card: true },
      { key: "calculated_at", label: "Calculated", type: "datetime", card: true, skipForm: true },
      {
        key: "teacher_remarks",
        label: "Teacher Remarks",
        type: "textarea",
        full: true,
        card: true,
      },
      { key: "strengths", label: "Strengths", type: "textarea", full: true },
      { key: "areas_for_improvement", label: "Areas to Improve", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "subject_name", "trend"],
  },
  "teacher-effectiveness": {
    key: "teacher-effectiveness",
    label: "Teacher Effectiveness",
    icon: TrophyIcon,
    endpoint: "teacher-effectiveness",
    titleField: "teacher_name",
    subtitleField: "subject_name",
    fields: [
      { key: "teacher_name", label: "Teacher", main: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", skipForm: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      { key: "subject", label: "Subject ID", card: true },
      { key: "term_name", label: "Term", card: true, skipForm: true },
      { key: "term", label: "Term ID", card: true },
      { key: "academic_year_name", label: "Academic Year", card: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      {
        key: "effectiveness_score",
        label: "Effectiveness",
        type: "number",
        card: true,
        badge: true,
      },
      { key: "average_student_score", label: "Avg Student Score", type: "number", card: true },
      { key: "pass_rate", label: "Pass Rate %", type: "number", card: true },
      { key: "evaluation_score", label: "Evaluation", type: "number", card: true },
      { key: "lesson_completion_rate", label: "Lessons %", type: "number", card: true },
      { key: "assignment_count", label: "Assignments", type: "number", card: true },
      { key: "average_assignment_score", label: "Avg Assignment", type: "number", card: true },
      { key: "attendance_rate", label: "Attendance %", type: "number", card: true },
      { key: "total_students", label: "Students", type: "number", card: true },
      { key: "calculated_at", label: "Calculated", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["teacher_name", "subject_name", "term_name"],
  },
  "subject-versions": {
    key: "subject-versions",
    label: "Subject Version",
    icon: CircleStackIcon,
    endpoint: "subject-versions",
    titleField: "name",
    subtitleField: "subject_name",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      { key: "subject", label: "Subject ID", card: true },
      { key: "version_number", label: "Version", type: "number", card: true, skipForm: true },
      { key: "code", label: "Code", card: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "max_marks", label: "Max Marks", type: "number", card: true },
      { key: "pass_marks", label: "Pass Marks", type: "number", card: true },
      { key: "credit_hours", label: "Credit Hours", type: "number", card: true },
      { key: "is_core", label: "Core", type: "bool", badge: true },
      { key: "is_elective", label: "Elective", type: "bool", badge: true },
      { key: "changed_by_name", label: "Changed By", card: true, skipForm: true },
      { key: "changed_by", label: "Changed By ID", card: true },
      { key: "change_summary", label: "Change Summary", type: "textarea", full: true, card: true },
      { key: "description", label: "Description", type: "textarea", full: true },
    ],
    searchKeys: ["name", "subject_name", "code"],
  },
  "lesson-plan-versions": {
    key: "lesson-plan-versions",
    label: "Lesson Plan Version",
    icon: CircleStackIcon,
    endpoint: "lesson-plan-versions",
    titleField: "title",
    subtitleField: "version_number",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "version_number",
        label: "Version",
        subtitle: true,
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "lesson_plan", label: "Lesson Plan ID", card: true },
      { key: "topic", label: "Topic", card: true },
      { key: "duration_minutes", label: "Duration (min)", type: "number", card: true },
      { key: "changed_by_name", label: "Changed By", card: true, skipForm: true },
      { key: "changed_by", label: "Changed By ID", card: true },
      { key: "objectives", label: "Objectives", type: "textarea", full: true, card: true },
      { key: "content", label: "Content", type: "textarea", full: true },
      { key: "resources", label: "Resources", type: "textarea", full: true },
      { key: "change_summary", label: "Change Summary", type: "textarea", full: true },
    ],
    searchKeys: ["title", "topic", "change_summary"],
  },
  "assignment-versions": {
    key: "assignment-versions",
    label: "Assignment Version",
    icon: CircleStackIcon,
    endpoint: "assignment-versions",
    titleField: "title",
    subtitleField: "version_number",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "version_number",
        label: "Version",
        subtitle: true,
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "assignment", label: "Assignment ID", card: true },
      {
        key: "assignment_type",
        label: "Type",
        type: "select",
        options: ASSIGNMENT_TYPES,
        badge: true,
      },
      { key: "due_date", label: "Due Date", type: "date", card: true },
      { key: "due_time", label: "Due Time", card: true },
      { key: "max_score", label: "Max Score", type: "number", card: true },
      { key: "changed_by_name", label: "Changed By", card: true, skipForm: true },
      { key: "changed_by", label: "Changed By ID", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "change_summary", label: "Change Summary", type: "textarea", full: true },
    ],
    searchKeys: ["title", "assignment_type", "change_summary"],
  },
  catalog: {
    key: "catalog",
    label: "Course Catalog",
    icon: BookOpenIcon,
    endpoint: "catalog",
    titleField: "subject_name",
    subtitleField: "grade_name",
    toggleField: "is_published",
    fields: [
      { key: "subject_name", label: "Subject", main: true, skipForm: true },
      { key: "subject", label: "Subject ID", skipForm: true },
      { key: "grade_name", label: "Grade", subtitle: true, skipForm: true },
      { key: "subject_code", label: "Code", card: true, skipForm: true },
      {
        key: "difficulty_level",
        label: "Difficulty",
        type: "select",
        options: DIFFICULTY_LEVELS,
        badge: true,
      },
      { key: "estimated_hours_per_week", label: "Hours/Week", type: "number", card: true },
      { key: "enrollment_cap", label: "Enrollment Cap", type: "number", card: true },
      { key: "available_terms", label: "Available Terms", card: true },
      { key: "view_count", label: "Views", type: "number", card: true, skipForm: true },
      { key: "interested_count", label: "Interested", type: "number", card: true, skipForm: true },
      { key: "is_published", label: "Published", type: "bool", badge: true },
      { key: "prerequisite_names", label: "Prerequisites", card: true, skipForm: true },
      { key: "prerequisites", label: "Prerequisite IDs", card: true },
      { key: "co_requisite_names", label: "Co-requisites", card: true, skipForm: true },
      { key: "co_requisites", label: "Co-requisite IDs", card: true },
      { key: "tags", label: "Tags", card: true },
      { key: "image_url", label: "Image URL", card: true },
      {
        key: "catalog_description",
        label: "Description",
        type: "textarea",
        full: true,
        card: true,
      },
      { key: "learning_outcomes", label: "Learning Outcomes", type: "textarea", full: true },
      { key: "syllabus_summary", label: "Syllabus Summary", type: "textarea", full: true },
      { key: "assessment_method", label: "Assessment", type: "textarea", full: true },
      {
        key: "recommended_resources",
        label: "Recommended Resources",
        type: "textarea",
        full: true,
      },
    ],
    searchKeys: ["subject_name", "grade_name", "difficulty_level", "tags"],
  },
  "enrollment-intents": {
    key: "enrollment-intents",
    label: "Enrollment Intent",
    icon: IdentificationIcon,
    endpoint: "enrollment-intents",
    titleField: "student_name",
    subtitleField: "subject_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "subject_name", label: "Subject", subtitle: true, skipForm: true },
      { key: "catalog_entry", label: "Catalog Entry", card: true },
      { key: "academic_year_name", label: "Academic Year", card: true, skipForm: true },
      { key: "academic_year", label: "Academic Year ID", card: true },
      { key: "status", label: "Status", type: "select", options: INTENT_STATUS, badge: true },
      { key: "notes", label: "Notes", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["student_name", "subject_name", "status"],
  },
};

const TABS: { key: string; label: string; icon: React.ComponentType<{ className?: string }> }[] =
  Object.values(ENTITY_CONFIGS).map((c) => ({ key: c.key, label: c.label, icon: c.icon }));

// ─── Main page ───────────────────────────────────────────────────────────────

export default function AcademicsPage() {
  useTitle("Academics Hub");
  const [activeTab, setActiveTab] = useState("subjects");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Academics Hub</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Subjects, lesson plans, curriculum, syllabi, evaluations, homework, exams and analytics
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
        basePath="/academics"
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
