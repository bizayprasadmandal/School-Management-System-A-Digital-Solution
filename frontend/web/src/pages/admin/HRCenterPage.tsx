/**
 * HR Center — full-surface admin page for the hr module.
 *
 * 37 entity tabs (config-driven via EntitySection). Employees, payroll, leave, performance, recruitment, time tracking, benefits, training and compliance.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import PayrollRunsPanel from "./PayrollRunsPanel";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { BanknotesIcon, MagnifyingGlassIcon, UsersIcon } from "@heroicons/react/24/outline";

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  // ===== hr =====
  "accountant-profiles": {
    key: "accountant-profiles",
    icon: UsersIcon,
    label: "Accountant Profile",
    endpoint: "accountant-profiles",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User Name" },
      { key: "qualification", label: "Qualification" },
      { key: "specialization", label: "Specialization" },
      { key: "experience_years", label: "Experience Years" },
      { key: "certifications", label: "Certifications" },
      { key: "bio", label: "Bio" },
    ],
  },
  applicants: {
    key: "applicants",
    icon: UsersIcon,
    label: "Applicant",
    endpoint: "applicants",
    titleField: "job_posting",
    subtitleField: "status",
    fields: [
      { key: "job_posting", label: "Job Posting" },
      { key: "job_title", label: "Job Title" },
      { key: "first_name", label: "First Name" },
      { key: "last_name", label: "Last Name" },
      { key: "full_name", label: "Full Name" },
      { key: "email", label: "Email" },
      { key: "phone", label: "Phone" },
      { key: "resume_url", label: "Resume Url" },
      { key: "cover_letter", label: "Cover Letter" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["new", "New"],
          ["screening", "Screening"],
          ["interview", "Interview"],
          ["offer", "Offer"],
          ["hired", "Hired"],
          ["rejected", "Rejected"],
          ["withdrawn", "Withdrawn"],
        ],
      },
      { key: "source", label: "Source" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "rejection_reason", label: "Rejection Reason" },
      { key: "reviewed_by", label: "Reviewed By" },
      { key: "reviewed_by_name", label: "Reviewed By Name" },
    ],
  },
  "audit-logs": {
    key: "audit-logs",
    icon: UsersIcon,
    label: "H R Audit Log",
    endpoint: "audit-logs",
    titleField: "action_type",
    fields: [
      {
        key: "action_type",
        label: "Action Type",
        type: "select",
        options: [
          ["create", "Create"],
          ["update", "Update"],
          ["delete", "Delete"],
          ["approve", "Approve"],
          ["reject", "Reject"],
          ["export", "Export"],
        ],
      },
      { key: "model_name", label: "Model Name" },
      { key: "object_id", label: "Object Id" },
      { key: "object_repr", label: "Object Repr" },
      { key: "old_values", label: "Old Values" },
      { key: "new_values", label: "New Values" },
      { key: "performed_by", label: "Performed By" },
      { key: "performed_by_name", label: "Performed By Name" },
      { key: "ip_address", label: "Ip Address" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "benefit-plans": {
    key: "benefit-plans",
    icon: UsersIcon,
    label: "Benefit Plan",
    endpoint: "benefit-plans",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "benefit_type",
        label: "Benefit Type",
        type: "select",
        options: [
          ["health", "Health"],
          ["dental", "Dental"],
          ["vision", "Vision"],
          ["life", "Life"],
          ["retirement", "Retirement"],
          ["disability", "Disability"],
          ["other", "Other"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "provider", label: "Provider" },
      { key: "employee_contribution", label: "Employee Contribution" },
      { key: "employer_contribution", label: "Employer Contribution" },
      { key: "total_contribution", label: "Total Contribution" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "enrollment_start", label: "Enrollment Start" },
      { key: "enrollment_end", label: "Enrollment End" },
      { key: "enrollment_count", label: "Enrollment Count" },
    ],
  },
  certifications: {
    key: "certifications",
    icon: UsersIcon,
    label: "Certification",
    endpoint: "certifications",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "name", label: "Name" },
      { key: "issuing_organization", label: "Issuing Organization" },
      { key: "credential_id", label: "Credential Id" },
      { key: "issue_date", label: "Issue Date", type: "date" },
      { key: "expiry_date", label: "Expiry Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["expired", "Expired"],
          ["pending_renewal", "Pending Renewal"],
        ],
      },
      { key: "document_url", label: "Document Url" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "is_expired", label: "Is Expired" },
      { key: "days_until_expiry", label: "Days Until Expiry" },
    ],
  },
  "data-retention-policies": {
    key: "data-retention-policies",
    icon: UsersIcon,
    label: "Data Retention Policy",
    endpoint: "data-retention-policies",
    titleField: "model_name",
    fields: [
      { key: "model_name", label: "Model Name" },
      { key: "retention_days", label: "Retention Days" },
      { key: "auto_delete", label: "Auto Delete" },
      { key: "last_purge_date", label: "Last Purge Date", type: "date" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  departments: {
    key: "departments",
    icon: UsersIcon,
    label: "Department",
    endpoint: "departments",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "code", label: "Code" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "head", label: "Head" },
      { key: "head_name", label: "Head Name" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "employee_count", label: "Employee Count" },
    ],
  },
  "employee-benefits": {
    key: "employee-benefits",
    icon: UsersIcon,
    label: "Employee Benefit",
    endpoint: "employee-benefits",
    titleField: "employee",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "plan", label: "Plan" },
      { key: "plan_name", label: "Plan Name" },
      { key: "plan_type", label: "Plan Type" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["enrolled", "Enrolled"],
          ["pending", "Pending"],
          ["cancelled", "Cancelled"],
          ["expired", "Expired"],
        ],
      },
      { key: "enrollment_date", label: "Enrollment Date", type: "date" },
      { key: "effective_from", label: "Effective From" },
      { key: "effective_to", label: "Effective To" },
      { key: "dependents_count", label: "Dependents Count" },
      { key: "employee_contribution", label: "Employee Contribution" },
      { key: "employer_contribution", label: "Employer Contribution" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "employee-documents": {
    key: "employee-documents",
    icon: UsersIcon,
    label: "Employee Document",
    endpoint: "employee-documents",
    titleField: "title",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      {
        key: "document_type",
        label: "Document Type",
        type: "select",
        options: [
          ["contract", "Contract"],
          ["id_proof", "Id Proof"],
          ["address_proof", "Address Proof"],
          ["education", "Education"],
          ["experience", "Experience"],
          ["offer_letter", "Offer Letter"],
          ["appraisal", "Appraisal"],
          ["salary_slip", "Salary Slip"],
          ["other", "Other"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "file_url", label: "File Url" },
      { key: "uploaded_by", label: "Uploaded By" },
      { key: "uploaded_by_name", label: "Uploaded By Name" },
      { key: "expiry_date", label: "Expiry Date", type: "date" },
      { key: "is_verified", label: "Is Verified" },
      { key: "verified_by", label: "Verified By" },
      { key: "verified_by_name", label: "Verified By Name" },
      { key: "is_expired", label: "Is Expired" },
    ],
  },
  "employee-salaries": {
    key: "employee-salaries",
    icon: UsersIcon,
    label: "Employee Salary",
    endpoint: "employee-salaries",
    titleField: "employee",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "structure", label: "Structure" },
      { key: "structure_name", label: "Structure Name" },
      { key: "basic_salary", label: "Basic Salary" },
      { key: "housing_allowance", label: "Housing Allowance" },
      { key: "transport_allowance", label: "Transport Allowance" },
      { key: "medical_allowance", label: "Medical Allowance" },
      { key: "other_allowances", label: "Other Allowances" },
      { key: "tax_deduction", label: "Tax Deduction" },
      { key: "pension_deduction", label: "Pension Deduction" },
      { key: "other_deductions", label: "Other Deductions" },
      { key: "effective_from", label: "Effective From" },
      { key: "effective_to", label: "Effective To" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  employees: {
    key: "employees",
    icon: UsersIcon,
    label: "Employee",
    endpoint: "employees",
    titleField: "user_name",
    subtitleField: "status",
    fields: [
      { key: "user_name", label: "User Name" },
      { key: "user_email", label: "User Email" },
      { key: "employee_id", label: "Employee Id" },
      { key: "department", label: "Department" },
      { key: "department_name", label: "Department Name" },
      { key: "designation", label: "Designation" },
      {
        key: "employment_type",
        label: "Employment Type",
        type: "select",
        options: [
          ["full_time", "Full Time"],
          ["part_time", "Part Time"],
          ["contract", "Contract"],
          ["intern", "Intern"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["on_leave", "On Leave"],
          ["terminated", "Terminated"],
          ["resigned", "Resigned"],
        ],
      },
      { key: "joining_date", label: "Joining Date", type: "date" },
      { key: "exit_date", label: "Exit Date", type: "date" },
      { key: "phone", label: "Phone" },
      { key: "address", label: "Address" },
      { key: "emergency_contact_name", label: "Emergency Contact Name" },
      { key: "emergency_contact_phone", label: "Emergency Contact Phone" },
      { key: "bank_name", label: "Bank Name" },
      { key: "bank_account_number", label: "Bank Account Number" },
      { key: "bank_routing_number", label: "Bank Routing Number" },
      { key: "current_salary", label: "Current Salary" },
    ],
  },
  // NOTE: a duplicate `hr-dashboard` tab used to live here pointing at
  // `GET /hr/hr-dashboard/`, which does not exist (that viewset only exposes
  // `hr-dashboard/metrics/`) — the tab always rendered a 404/empty state.
  // `hr-dashboard-metrics` below is the real, list-capable endpoint.
  "hr-dashboard-metrics": {
    key: "hr-dashboard-metrics",
    icon: UsersIcon,
    label: "H R Dashboard Metrics",
    endpoint: "hr-dashboard-metrics",
    titleField: "total_employees",
    fields: [
      { key: "total_employees", label: "Total Employees" },
      { key: "active_employees", label: "Active Employees" },
      { key: "new_hires_this_month", label: "New Hires This Month" },
      { key: "separations_this_month", label: "Separations This Month" },
      { key: "turnover_rate", label: "Turnover Rate" },
      { key: "average_tenure_months", label: "Average Tenure Months" },
      { key: "total_payroll_this_month", label: "Total Payroll This Month" },
      { key: "pending_leave_requests", label: "Pending Leave Requests" },
      { key: "pending_overtime_requests", label: "Pending Overtime Requests" },
      { key: "expiring_certifications", label: "Expiring Certifications" },
      { key: "active_trainings", label: "Active Trainings" },
      { key: "department_breakdown", label: "Department Breakdown" },
      { key: "employment_type_breakdown", label: "Employment Type Breakdown" },
      { key: "calculated_at", label: "Calculated At", type: "date" },
    ],
  },
  "hr-leave-balances": {
    key: "hr-leave-balances",
    icon: UsersIcon,
    label: "Leave Balance H R",
    endpoint: "hr-leave-balances",
    titleField: "employee",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      {
        key: "leave_type",
        label: "Leave Type",
        type: "select",
        options: [
          ["annual", "Annual"],
          ["sick", "Sick"],
          ["personal", "Personal"],
          ["maternity", "Maternity"],
          ["paternity", "Paternity"],
          ["unpaid", "Unpaid"],
        ],
      },
      { key: "year", label: "Year" },
      { key: "total_days", label: "Total Days" },
      { key: "used_days", label: "Used Days" },
      { key: "carried_over", label: "Carried Over" },
      { key: "remaining_days", label: "Remaining Days" },
    ],
  },
  interviews: {
    key: "interviews",
    icon: UsersIcon,
    label: "Interview Schedule",
    endpoint: "interviews",
    titleField: "applicant",
    subtitleField: "status",
    fields: [
      { key: "applicant", label: "Applicant" },
      { key: "applicant_name", label: "Applicant Name" },
      { key: "interviewer", label: "Interviewer" },
      { key: "interviewer_name", label: "Interviewer Name" },
      {
        key: "interview_type",
        label: "Interview Type",
        type: "select",
        options: [
          ["phone", "Phone"],
          ["video", "Video"],
          ["in_person", "In Person"],
          ["panel", "Panel"],
          ["technical", "Technical"],
        ],
      },
      { key: "scheduled_date", label: "Scheduled Date", type: "date" },
      { key: "scheduled_time", label: "Scheduled Time" },
      { key: "duration_minutes", label: "Duration Minutes" },
      { key: "location", label: "Location" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
          ["no_show", "No Show"],
        ],
      },
      { key: "rating", label: "Rating" },
      { key: "feedback", label: "Feedback" },
      {
        key: "recommendation",
        label: "Recommendation",
        type: "select",
        options: [
          ["hire", "Hire"],
          ["maybe", "Maybe"],
          ["no_hire", "No Hire"],
        ],
      },
    ],
  },
  "job-postings": {
    key: "job-postings",
    icon: UsersIcon,
    label: "Job Posting",
    endpoint: "job-postings",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "department", label: "Department" },
      { key: "department_name", label: "Department Name" },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "requirements", label: "Requirements" },
      { key: "responsibilities", label: "Responsibilities" },
      {
        key: "employment_type",
        label: "Employment Type",
        type: "select",
        options: [
          ["full_time", "Full Time"],
          ["part_time", "Part Time"],
          ["contract", "Contract"],
          ["intern", "Intern"],
        ],
      },
      { key: "designation", label: "Designation" },
      { key: "salary_range_min", label: "Salary Range Min" },
      { key: "salary_range_max", label: "Salary Range Max" },
      { key: "location", label: "Location" },
      { key: "positions_count", label: "Positions Count" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["open", "Open"],
          ["closed", "Closed"],
          ["filled", "Filled"],
        ],
      },
      { key: "posted_date", label: "Posted Date", type: "date" },
      { key: "closing_date", label: "Closing Date", type: "date" },
      { key: "posted_by", label: "Posted By" },
      { key: "applicant_count", label: "Applicant Count" },
    ],
  },
  "leave-requests": {
    key: "leave-requests",
    icon: UsersIcon,
    label: "Leave Request",
    endpoint: "leave-requests",
    titleField: "employee",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "employee_id_number", label: "Employee Id Number" },
      {
        key: "leave_type",
        label: "Leave Type",
        type: "select",
        options: [
          ["annual", "Annual"],
          ["sick", "Sick"],
          ["personal", "Personal"],
          ["maternity", "Maternity"],
          ["paternity", "Paternity"],
          ["unpaid", "Unpaid"],
          ["other", "Other"],
        ],
      },
      { key: "from_date", label: "From Date", type: "date" },
      { key: "to_date", label: "To Date", type: "date" },
      { key: "total_days", label: "Total Days" },
      { key: "reason", label: "Reason" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["rejected", "Rejected"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "reviewed_by", label: "Reviewed By" },
      { key: "reviewed_by_name", label: "Reviewed By Name" },
      { key: "review_notes", label: "Review Notes" },
      { key: "reviewed_at", label: "Reviewed At", type: "date" },
    ],
  },
  "onboarding-checklists": {
    key: "onboarding-checklists",
    icon: UsersIcon,
    label: "Onboarding Checklist",
    endpoint: "onboarding-checklists",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "department", label: "Department" },
      { key: "department_name", label: "Department Name" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "task_count", label: "Task Count" },
    ],
  },
  "onboarding-progress": {
    key: "onboarding-progress",
    icon: UsersIcon,
    label: "Onboarding Progress",
    endpoint: "onboarding-progress",
    titleField: "employee",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "task", label: "Task" },
      { key: "task_title", label: "Task Title" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["in_progress", "In Progress"],
          ["completed", "Completed"],
        ],
      },
      { key: "completed_at", label: "Completed At", type: "date" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "onboarding-tasks": {
    key: "onboarding-tasks",
    icon: UsersIcon,
    label: "Onboarding Task",
    endpoint: "onboarding-tasks",
    titleField: "title",
    fields: [
      { key: "checklist", label: "Checklist" },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "assigned_to", label: "Assigned To" },
      { key: "assigned_to_name", label: "Assigned To Name" },
      { key: "order", label: "Order" },
      { key: "due_days_after_joining", label: "Due Days After Joining" },
      { key: "is_mandatory", label: "Is Mandatory" },
    ],
  },
  "overtime-requests": {
    key: "overtime-requests",
    icon: UsersIcon,
    label: "Overtime Request",
    endpoint: "overtime-requests",
    titleField: "employee",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "date", label: "Date", type: "date" },
      { key: "hours", label: "Hours" },
      { key: "reason", label: "Reason" },
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
      { key: "reviewed_by_name", label: "Reviewed By Name" },
      { key: "review_notes", label: "Review Notes" },
    ],
  },
  "payslip-view-logs": {
    key: "payslip-view-logs",
    icon: UsersIcon,
    label: "Payslip View Log",
    endpoint: "payslip-view-logs",
    titleField: "employee",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "payslip", label: "Payslip" },
      { key: "viewed_at", label: "Viewed At", type: "date" },
    ],
  },
  payslips: {
    key: "payslips",
    icon: UsersIcon,
    label: "Payslip",
    endpoint: "payslips",
    titleField: "employee",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "employee_id_number", label: "Employee Id Number" },
      { key: "department_name", label: "Department Name" },
      { key: "period_start", label: "Period Start" },
      { key: "period_end", label: "Period End" },
      { key: "basic_salary", label: "Basic Salary" },
      { key: "housing_allowance", label: "Housing Allowance" },
      { key: "transport_allowance", label: "Transport Allowance" },
      { key: "medical_allowance", label: "Medical Allowance" },
      { key: "other_allowances", label: "Other Allowances" },
      { key: "tax_deduction", label: "Tax Deduction" },
      { key: "pension_deduction", label: "Pension Deduction" },
      { key: "other_deductions", label: "Other Deductions" },
      { key: "gross_pay", label: "Gross Pay" },
      { key: "total_deductions", label: "Total Deductions" },
      { key: "net_pay", label: "Net Pay" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["approved", "Approved"],
          ["paid", "Paid"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "payment_date", label: "Payment Date", type: "date" },
      { key: "payment_method", label: "Payment Method" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "generated_by", label: "Generated By" },
    ],
  },
  "peer-feedbacks": {
    key: "peer-feedbacks",
    icon: UsersIcon,
    label: "Peer Feedback",
    endpoint: "peer-feedbacks",
    titleField: "review",
    fields: [
      { key: "review", label: "Review" },
      { key: "employee_name", label: "Employee Name" },
      { key: "reviewer", label: "Reviewer" },
      { key: "reviewer_name", label: "Reviewer Name" },
      {
        key: "feedback_type",
        label: "Feedback Type",
        type: "select",
        options: [
          ["peer", "Peer"],
          ["subordinate", "Subordinate"],
          ["self", "Self"],
          ["customer", "Customer"],
        ],
      },
      { key: "strengths", label: "Strengths", type: "textarea" },
      { key: "improvements", label: "Improvements" },
      { key: "collaboration_score", label: "Collaboration Score" },
      { key: "communication_score", label: "Communication Score" },
      { key: "overall_score", label: "Overall Score" },
      { key: "comments", label: "Comments" },
      { key: "is_anonymous", label: "Is Anonymous" },
      { key: "submitted_at", label: "Submitted At", type: "date" },
    ],
  },
  "performance-goals": {
    key: "performance-goals",
    icon: UsersIcon,
    label: "Performance Goal",
    endpoint: "performance-goals",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "cycle", label: "Cycle" },
      { key: "cycle_name", label: "Cycle Name" },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "category", label: "Category" },
      {
        key: "priority",
        label: "Priority",
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
          ["not_started", "Not Started"],
          ["in_progress", "In Progress"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "target_value", label: "Target Value", type: "number" },
      { key: "current_value", label: "Current Value" },
      { key: "unit", label: "Unit" },
      { key: "progress_pct", label: "Progress Pct" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "target_date", label: "Target Date", type: "date" },
      { key: "completed_date", label: "Completed Date", type: "date" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "performance-reviews": {
    key: "performance-reviews",
    icon: UsersIcon,
    label: "Performance Review",
    endpoint: "performance-reviews",
    titleField: "employee",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "cycle", label: "Cycle" },
      { key: "cycle_name", label: "Cycle Name" },
      { key: "reviewer", label: "Reviewer" },
      { key: "reviewer_name", label: "Reviewer Name" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["self_review", "Self Review"],
          ["manager_review", "Manager Review"],
          ["hr_review", "Hr Review"],
          ["completed", "Completed"],
          ["appealed", "Appealed"],
        ],
      },
      {
        key: "overall_rating",
        label: "Overall Rating",
        type: "select",
        options: [
          ["5", "5"],
          ["4", "4"],
          ["3", "3"],
          ["2", "2"],
          ["1", "1"],
        ],
      },
      { key: "rating_display", label: "Rating Display" },
      { key: "strengths", label: "Strengths", type: "textarea" },
      {
        key: "areas_for_improvement",
        label: "Areas For Improvement",
        type: "textarea",
      },
      { key: "goals_summary", label: "Goals Summary" },
      { key: "development_plan", label: "Development Plan" },
      { key: "self_comments", label: "Self Comments" },
      { key: "manager_comments", label: "Manager Comments" },
      { key: "hr_comments", label: "Hr Comments" },
      { key: "next_review_date", label: "Next Review Date", type: "date" },
      { key: "promotion_recommended", label: "Promotion Recommended" },
      { key: "salary_revision_pct", label: "Salary Revision Pct" },
      { key: "goals", label: "Goals" },
    ],
  },
  policies: {
    key: "policies",
    icon: UsersIcon,
    label: "Policy Document",
    endpoint: "policies",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "content", label: "Content" },
      { key: "document_type", label: "Document Type" },
      { key: "version", label: "Version" },
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
      { key: "effective_date", label: "Effective Date", type: "date" },
      { key: "requires_acknowledgment", label: "Requires Acknowledgment" },
      { key: "uploaded_by", label: "Uploaded By" },
      { key: "uploaded_by_name", label: "Uploaded By Name" },
      { key: "acknowledgment_count", label: "Acknowledgment Count" },
    ],
  },
  "policy-acknowledgments": {
    key: "policy-acknowledgments",
    icon: UsersIcon,
    label: "Policy Acknowledgment",
    endpoint: "policy-acknowledgments",
    titleField: "policy",
    fields: [
      { key: "policy", label: "Policy" },
      { key: "policy_title", label: "Policy Title" },
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "acknowledged_at", label: "Acknowledged At", type: "date" },
      { key: "ip_address", label: "Ip Address" },
    ],
  },
  "profile-updates": {
    key: "profile-updates",
    icon: UsersIcon,
    label: "Employee Profile Update",
    endpoint: "profile-updates",
    titleField: "employee",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "field_name", label: "Field Name" },
      { key: "old_value", label: "Old Value" },
      { key: "new_value", label: "New Value" },
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
      { key: "reviewed_by_name", label: "Reviewed By Name" },
      { key: "review_notes", label: "Review Notes" },
    ],
  },
  "review-cycles": {
    key: "review-cycles",
    icon: UsersIcon,
    label: "Performance Review Cycle",
    endpoint: "review-cycles",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["planning", "Planning"],
          ["active", "Active"],
          ["completed", "Completed"],
          ["archived", "Archived"],
        ],
      },
      { key: "created_by", label: "Created By" },
    ],
  },
  "salary-reports": {
    key: "salary-reports",
    icon: UsersIcon,
    label: "Salary Report",
    endpoint: "salary-reports",
    titleField: "month",
    fields: [
      { key: "month", label: "Month" },
      { key: "total_gross", label: "Total Gross" },
      { key: "total_deductions", label: "Total Deductions" },
      { key: "total_net", label: "Total Net" },
      { key: "total_tax", label: "Total Tax" },
      { key: "total_pension", label: "Total Pension" },
      { key: "average_salary", label: "Average Salary" },
      { key: "headcount", label: "Headcount" },
      { key: "department_breakdown", label: "Department Breakdown" },
    ],
  },
  "salary-structures": {
    key: "salary-structures",
    icon: UsersIcon,
    label: "Salary Structure",
    endpoint: "salary-structures",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "designation", label: "Designation" },
      { key: "department", label: "Department" },
      { key: "department_name", label: "Department Name" },
      { key: "basic_salary", label: "Basic Salary" },
      { key: "housing_allowance", label: "Housing Allowance" },
      { key: "transport_allowance", label: "Transport Allowance" },
      { key: "medical_allowance", label: "Medical Allowance" },
      { key: "other_allowances", label: "Other Allowances" },
      { key: "tax_deduction", label: "Tax Deduction" },
      { key: "pension_deduction", label: "Pension Deduction" },
      { key: "other_deductions", label: "Other Deductions" },
      { key: "total_earnings", label: "Total Earnings" },
      { key: "total_deductions", label: "Total Deductions" },
      { key: "net_salary", label: "Net Salary" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "time-entries": {
    key: "time-entries",
    icon: UsersIcon,
    label: "Time Entry",
    endpoint: "time-entries",
    titleField: "employee",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "date", label: "Date", type: "date" },
      { key: "clock_in", label: "Clock In" },
      { key: "clock_out", label: "Clock Out" },
      { key: "break_minutes", label: "Break Minutes" },
      { key: "total_hours", label: "Total Hours" },
      { key: "overtime_hours", label: "Overtime Hours" },
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
      { key: "approved_by", label: "Approved By" },
      { key: "approved_by_name", label: "Approved By Name" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  timesheets: {
    key: "timesheets",
    icon: UsersIcon,
    label: "Timesheet",
    endpoint: "timesheets",
    titleField: "employee",
    subtitleField: "status",
    fields: [
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      { key: "week_start", label: "Week Start" },
      { key: "week_end", label: "Week End" },
      { key: "total_hours", label: "Total Hours" },
      { key: "total_overtime", label: "Total Overtime" },
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
      { key: "submitted_at", label: "Submitted At", type: "date" },
      { key: "approved_by", label: "Approved By" },
      { key: "approved_by_name", label: "Approved By Name" },
      { key: "approved_at", label: "Approved At", type: "date" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "training-enrollments": {
    key: "training-enrollments",
    icon: UsersIcon,
    label: "Training Enrollment",
    endpoint: "training-enrollments",
    titleField: "program",
    subtitleField: "status",
    fields: [
      { key: "program", label: "Program" },
      { key: "program_name", label: "Program Name" },
      { key: "employee", label: "Employee" },
      { key: "employee_name", label: "Employee Name" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["enrolled", "Enrolled"],
          ["in_progress", "In Progress"],
          ["completed", "Completed"],
          ["dropped", "Dropped"],
        ],
      },
      { key: "enrolled_date", label: "Enrolled Date", type: "date" },
      { key: "completed_date", label: "Completed Date", type: "date" },
      { key: "score", label: "Score", type: "number" },
      { key: "certificate_url", label: "Certificate Url" },
      { key: "hours_attended", label: "Hours Attended" },
      { key: "feedback", label: "Feedback" },
      { key: "rating", label: "Rating" },
    ],
  },
  "training-programs": {
    key: "training-programs",
    icon: UsersIcon,
    label: "Training Program",
    endpoint: "training-programs",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "training_type",
        label: "Training Type",
        type: "select",
        options: [
          ["workshop", "Workshop"],
          ["seminar", "Seminar"],
          ["course", "Course"],
          ["certification", "Certification"],
          ["conference", "Conference"],
          ["on_job", "On Job"],
          ["other", "Other"],
        ],
      },
      { key: "provider", label: "Provider" },
      { key: "instructor", label: "Instructor" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "duration_hours", label: "Duration Hours" },
      { key: "max_participants", label: "Max Participants" },
      { key: "cost_per_participant", label: "Cost Per Participant" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["planned", "Planned"],
          ["active", "Active"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "location", label: "Location" },
      { key: "is_mandatory", label: "Is Mandatory" },
      { key: "created_by", label: "Created By" },
      { key: "created_by_name", label: "Created By Name" },
      { key: "enrollment_count", label: "Enrollment Count" },
    ],
  },
  "turnover-reports": {
    key: "turnover-reports",
    icon: UsersIcon,
    label: "Turnover Report",
    endpoint: "turnover-reports",
    titleField: "month",
    fields: [
      { key: "month", label: "Month" },
      { key: "total_employees_start", label: "Total Employees Start" },
      { key: "new_hires", label: "New Hires" },
      { key: "separations", label: "Separations" },
      { key: "turnover_rate", label: "Turnover Rate" },
      { key: "resignations", label: "Resignations" },
      { key: "terminations", label: "Terminations" },
      { key: "retirements", label: "Retirements" },
      { key: "department_breakdown", label: "Department Breakdown" },
      { key: "top_reasons", label: "Top Reasons" },
    ],
  },
};

const TABS = [
  { key: "payroll-runs", label: "Payroll Runs", icon: BanknotesIcon },
  ...Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({
    key,
    label: cfg.label,
    icon: UsersIcon,
  })),
];

export default function HRCenterPage() {
  useTitle("HR Center");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">HR Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Employees, payroll, leave, performance, recruitment, time tracking, benefits, training
            and compliance
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
            leftIcon={<UsersIcon className="h-4 w-4" />}
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
            <t.icon className="h-4 w-4" aria-hidden="true" />
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "payroll-runs" ? (
        <PayrollRunsPanel />
      ) : (
        <EntitySection
          cfg={activeCfg}
          basePath="/hr"
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
