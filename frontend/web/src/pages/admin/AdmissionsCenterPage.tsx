/**
 * Admissions Center — full-surface admin page for the admissions module.
 *
 * 40 entity tabs (config-driven via EntitySection). Applications, intakes, decisions, documents, interviews, scholarships, waitlists and analytics.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, DocumentTextIcon } from "@heroicons/react/24/outline";

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  // ===== admissions =====
  "admission-agreement": {
    key: "admission-agreement",
    icon: DocumentTextIcon,
    label: "Admission Agreement",
    endpoint: "admission-agreement",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "content", label: "Content" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["active", "Active"],
          ["expired", "Expired"],
        ],
      },
      { key: "version", label: "Version" },
      { key: "effective_date", label: "Effective Date", type: "date" },
      { key: "expiry_date", label: "Expiry Date", type: "date" },
      { key: "requires_parent_signature", label: "Requires Parent Signature" },
      {
        key: "requires_student_signature",
        label: "Requires Student Signature",
      },
      { key: "created_by", label: "Created By" },
    ],
  },
  "admission-communication-log": {
    key: "admission-communication-log",
    icon: DocumentTextIcon,
    label: "Admission Communication Log",
    endpoint: "admission-communication-log",
    titleField: "subject",
    fields: [
      { key: "application", label: "Application" },
      {
        key: "channel",
        label: "Channel",
        type: "select",
        options: [
          ["email", "Email"],
          ["sms", "Sms"],
          ["phone", "Phone"],
          ["in_person", "In Person"],
          ["mail", "Mail"],
          ["other", "Other"],
        ],
      },
      {
        key: "direction",
        label: "Direction",
        type: "select",
        options: [
          ["inbound", "Inbound"],
          ["outbound", "Outbound"],
        ],
      },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "content", label: "Content" },
      { key: "sent_by", label: "Sent By" },
      { key: "sent_to_name", label: "Sent To Name" },
      { key: "sent_to_email", label: "Sent To Email" },
      { key: "delivered", label: "Delivered" },
      { key: "opened", label: "Opened" },
    ],
  },
  "admission-decision": {
    key: "admission-decision",
    icon: DocumentTextIcon,
    label: "Admission Decision",
    endpoint: "admission-decision",
    titleField: "application",
    fields: [
      { key: "application", label: "Application" },
      {
        key: "decision",
        label: "Decision",
        type: "select",
        options: [
          ["admitted", "Admitted"],
          ["rejected", "Rejected"],
          ["waitlisted", "Waitlisted"],
          ["deferred", "Deferred"],
          ["conditional", "Conditional"],
        ],
      },
      {
        key: "decision_reason",
        label: "Decision Reason",
        type: "select",
        options: [
          ["capacity", "Capacity"],
          ["academic", "Academic"],
          ["behavior", "Behavior"],
          ["documents", "Documents"],
          ["eligibility", "Eligibility"],
          ["other", "Other"],
        ],
      },
      { key: "rationale", label: "Rationale" },
      { key: "conditions", label: "Conditions" },
      { key: "recommended_grade", label: "Recommended Grade" },
      { key: "recommended_class", label: "Recommended Class" },
      { key: "scholarship_amount", label: "Scholarship Amount" },
      { key: "financial_aid_amount", label: "Financial Aid Amount" },
      { key: "decided_by", label: "Decided By" },
      { key: "decided_at", label: "Decided At", type: "date" },
      { key: "parent_notified", label: "Parent Notified" },
    ],
  },
  "admission-document-checklist": {
    key: "admission-document-checklist",
    icon: DocumentTextIcon,
    label: "Admission Document Checklist",
    endpoint: "admission-document-checklist",
    titleField: "intake",
    fields: [
      { key: "intake", label: "Intake" },
      { key: "grade_level", label: "Grade Level" },
      { key: "document_name", label: "Document Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "is_mandatory", label: "Is Mandatory" },
      { key: "accepted_formats", label: "Accepted Formats" },
      { key: "max_file_size_mb", label: "Max File Size Mb" },
      { key: "sort_order", label: "Sort Order", type: "number" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "admission-document-verification": {
    key: "admission-document-verification",
    icon: DocumentTextIcon,
    label: "Admission Document Verification",
    endpoint: "admission-document-verification",
    titleField: "application",
    subtitleField: "status",
    fields: [
      { key: "application", label: "Application" },
      { key: "checklist_item", label: "Checklist Item" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["verified", "Verified"],
          ["rejected", "Rejected"],
          ["expired", "Expired"],
        ],
      },
      { key: "file", label: "File" },
      { key: "original_filename", label: "Original Filename" },
      { key: "file_size", label: "File Size" },
      { key: "verified_by", label: "Verified By" },
      { key: "verified_at", label: "Verified At", type: "date" },
      { key: "rejection_reason", label: "Rejection Reason" },
      { key: "uploaded_at", label: "Uploaded At", type: "date" },
    ],
  },
  "admission-funnel-snapshot": {
    key: "admission-funnel-snapshot",
    icon: DocumentTextIcon,
    label: "Admission Funnel Snapshot",
    endpoint: "admission-funnel-snapshot",
    titleField: "intake",
    fields: [
      { key: "intake", label: "Intake" },
      { key: "snapshot_date", label: "Snapshot Date", type: "date" },
      { key: "inquiries", label: "Inquiries" },
      { key: "campus_visits", label: "Campus Visits" },
      { key: "applications_started", label: "Applications Started" },
      { key: "applications_submitted", label: "Applications Submitted" },
      { key: "documents_complete", label: "Documents Complete" },
      { key: "under_review", label: "Under Review" },
      { key: "interviews_scheduled", label: "Interviews Scheduled" },
      { key: "interviews_completed", label: "Interviews Completed" },
      { key: "decisions_made", label: "Decisions Made" },
      { key: "admitted", label: "Admitted" },
      { key: "enrolled", label: "Enrolled" },
    ],
  },
  "admission-marketing-source": {
    key: "admission-marketing-source",
    icon: DocumentTextIcon,
    label: "Admission Marketing Source",
    endpoint: "admission-marketing-source",
    titleField: "name",
    subtitleField: "source_type",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "source_type",
        label: "Source Type",
        type: "select",
        options: [
          ["website", "Website"],
          ["social", "Social"],
          ["referral", "Referral"],
          ["ad", "Ad"],
          ["event", "Event"],
          ["agent", "Agent"],
          ["other", "Other"],
        ],
      },
      { key: "total_inquiries", label: "Total Inquiries" },
      { key: "total_applications", label: "Total Applications" },
      { key: "total_enrolled", label: "Total Enrolled" },
      { key: "conversion_rate", label: "Conversion Rate" },
      { key: "cost", label: "Cost" },
      { key: "cost_per_enrollment", label: "Cost Per Enrollment" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "admission-policy": {
    key: "admission-policy",
    icon: DocumentTextIcon,
    label: "Admission Policy",
    endpoint: "admission-policy",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "policy_type",
        label: "Policy Type",
        type: "select",
        options: [
          ["age", "Age"],
          ["capacity", "Capacity"],
          ["priority", "Priority"],
          ["residence", "Residence"],
          ["sibling", "Sibling"],
          ["employee", "Employee"],
          ["disability", "Disability"],
          ["other", "Other"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "min_age_years", label: "Min Age Years" },
      { key: "max_age_years", label: "Max Age Years" },
      { key: "priority_weight", label: "Priority Weight" },
      { key: "max_students_per_grade", label: "Max Students Per Grade" },
      { key: "effective_date", label: "Effective Date", type: "date" },
      { key: "expiry_date", label: "Expiry Date", type: "date" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "policy_document", label: "Policy Document" },
      { key: "created_by", label: "Created By" },
    ],
  },
  "admission-prediction-model": {
    key: "admission-prediction-model",
    icon: DocumentTextIcon,
    label: "Admission Prediction Model",
    endpoint: "admission-prediction-model",
    titleField: "intake",
    fields: [
      { key: "intake", label: "Intake" },
      {
        key: "prediction_type",
        label: "Prediction Type",
        type: "select",
        options: [
          ["enrollment", "Enrollment"],
          ["yield", "Yield"],
          ["deposit", "Deposit"],
          ["retention", "Retention"],
        ],
      },
      { key: "prediction_date", label: "Prediction Date", type: "date" },
      { key: "predicted_value", label: "Predicted Value" },
      { key: "confidence_score", label: "Confidence Score" },
      { key: "factors", label: "Factors" },
      { key: "model_version", label: "Model Version" },
    ],
  },
  "admission-reminder": {
    key: "admission-reminder",
    icon: DocumentTextIcon,
    label: "Admission Reminder",
    endpoint: "admission-reminder",
    titleField: "subject",
    subtitleField: "status",
    fields: [
      { key: "application", label: "Application" },
      {
        key: "reminder_type",
        label: "Reminder Type",
        type: "select",
        options: [
          ["document", "Document"],
          ["deadline", "Deadline"],
          ["payment", "Payment"],
          ["interview", "Interview"],
          ["follow_up", "Follow Up"],
          ["custom", "Custom"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["sent", "Sent"],
          ["cancelled", "Cancelled"],
          ["failed", "Failed"],
        ],
      },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "message", label: "Message", type: "textarea" },
      { key: "scheduled_date", label: "Scheduled Date", type: "date" },
      { key: "sent_date", label: "Sent Date", type: "date" },
      {
        key: "channel",
        label: "Channel",
        type: "select",
        options: [
          ["email", "Email"],
          ["sms", "Sms"],
          ["phone", "Phone"],
          ["in_person", "In Person"],
          ["mail", "Mail"],
          ["other", "Other"],
        ],
      },
      { key: "created_by", label: "Created By" },
    ],
  },
  "admission-trend-analysis": {
    key: "admission-trend-analysis",
    icon: DocumentTextIcon,
    label: "Admission Trend Analysis",
    endpoint: "admission-trend-analysis",
    titleField: "academic_year",
    fields: [
      { key: "academic_year", label: "Academic Year" },
      { key: "intake", label: "Intake" },
      { key: "total_applications", label: "Total Applications" },
      { key: "applications_male", label: "Applications Male" },
      { key: "applications_female", label: "Applications Female" },
      { key: "total_enrolled", label: "Total Enrolled" },
      { key: "enrollment_male", label: "Enrollment Male" },
      { key: "enrollment_female", label: "Enrollment Female" },
      { key: "yield_rate", label: "Yield Rate" },
      { key: "total_tuition_revenue", label: "Total Tuition Revenue" },
      {
        key: "total_scholarships_awarded",
        label: "Total Scholarships Awarded",
      },
    ],
  },
  "agreement-signature": {
    key: "agreement-signature",
    icon: DocumentTextIcon,
    label: "Agreement Signature",
    endpoint: "agreement-signature",
    titleField: "agreement",
    fields: [
      { key: "agreement", label: "Agreement" },
      { key: "application", label: "Application" },
      {
        key: "signer_type",
        label: "Signer Type",
        type: "select",
        options: [
          ["parent", "Parent"],
          ["student", "Student"],
          ["admin", "Admin"],
        ],
      },
      { key: "signer_name", label: "Signer Name" },
      { key: "signature", label: "Signature" },
      { key: "signed_at", label: "Signed At", type: "date" },
      { key: "ip_address", label: "Ip Address" },
    ],
  },
  "application-timeline-event": {
    key: "application-timeline-event",
    icon: DocumentTextIcon,
    label: "Application Timeline Event",
    endpoint: "application-timeline-event",
    titleField: "application",
    fields: [
      { key: "application", label: "Application" },
      {
        key: "stage",
        label: "Stage",
        type: "select",
        options: [
          ["created", "Created"],
          ["submitted", "Submitted"],
          ["tour_scheduled", "Tour Scheduled"],
          ["tour_completed", "Tour Completed"],
          ["offer_sent", "Offer Sent"],
          ["offer_accepted", "Offer Accepted"],
          ["enrolled", "Enrolled"],
          ["status_changed", "Status Changed"],
        ],
      },
      { key: "note", label: "Note" },
      { key: "created_by", label: "Created By" },
    ],
  },
  applications: {
    key: "applications",
    icon: DocumentTextIcon,
    label: "Application",
    endpoint: "applications",
    titleField: "intake",
    subtitleField: "status",
    fields: [
      { key: "intake", label: "Intake" },
      { key: "application_number", label: "Application Number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["submitted", "Submitted"],
          ["under_review", "Under Review"],
          ["shortlisted", "Shortlisted"],
          ["accepted", "Accepted"],
          ["rejected", "Rejected"],
          ["waitlisted", "Waitlisted"],
          ["enrolled", "Enrolled"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "first_name", label: "First Name" },
      { key: "last_name", label: "Last Name" },
      { key: "middle_name", label: "Middle Name" },
      { key: "date_of_birth", label: "Date Of Birth" },
      {
        key: "gender",
        label: "Gender",
        type: "select",
        options: [
          ["male", "Male"],
          ["female", "Female"],
          ["other", "Other"],
        ],
      },
      { key: "nationality", label: "Nationality" },
      { key: "email", label: "Email" },
      { key: "phone", label: "Phone" },
      { key: "submitted_at", label: "Submitted At", type: "date" },
      { key: "reviewed_by", label: "Reviewed By" },
      { key: "review_notes", label: "Review Notes" },
      { key: "tour_date", label: "Tour Date", type: "date" },
      { key: "toured_at", label: "Toured At", type: "date" },
      { key: "offer_sent_at", label: "Offer Sent At", type: "date" },
      { key: "offer_deadline", label: "Offer Deadline" },
      { key: "offer_accepted_at", label: "Offer Accepted At", type: "date" },
      { key: "linked_student", label: "Linked Student" },
      { key: "timeline", label: "Timeline" },
    ],
  },
  "bulk-imports": {
    key: "bulk-imports",
    icon: DocumentTextIcon,
    label: "Bulk Application Import",
    endpoint: "bulk-imports",
    titleField: "batch_name",
    subtitleField: "status",
    fields: [
      { key: "batch_name", label: "Batch Name" },
      { key: "description", label: "Description", type: "textarea" },
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
      { key: "total_rows", label: "Total Rows" },
      { key: "imported_count", label: "Imported Count" },
      { key: "failed_count", label: "Failed Count" },
      { key: "errors", label: "Errors" },
      { key: "error_file_url", label: "Error File Url" },
      { key: "initiated_by", label: "Initiated By" },
      { key: "initiated_at", label: "Initiated At", type: "date" },
      { key: "completed_at", label: "Completed At", type: "date" },
    ],
  },
  "campus-visit": {
    key: "campus-visit",
    icon: DocumentTextIcon,
    label: "Campus Visit",
    endpoint: "campus-visit",
    titleField: "visitor_name",
    subtitleField: "status",
    fields: [
      { key: "visitor_name", label: "Visitor Name" },
      { key: "visitor_email", label: "Visitor Email" },
      { key: "visitor_phone", label: "Visitor Phone" },
      { key: "prospective_student", label: "Prospective Student" },
      {
        key: "visit_type",
        label: "Visit Type",
        type: "select",
        options: [
          ["individual", "Individual"],
          ["group", "Group"],
          ["open_house", "Open House"],
          ["shadow", "Shadow"],
          ["virtual", "Virtual"],
        ],
      },
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
      { key: "scheduled_date", label: "Scheduled Date", type: "date" },
      { key: "scheduled_time", label: "Scheduled Time" },
      { key: "duration_minutes", label: "Duration Minutes" },
      { key: "tour_guide", label: "Tour Guide" },
    ],
  },
  documents: {
    key: "documents",
    icon: DocumentTextIcon,
    label: "Application Document",
    endpoint: "documents",
    titleField: "application",
    fields: [
      { key: "application", label: "Application" },
      {
        key: "document_type",
        label: "Document Type",
        type: "select",
        options: [
          ["birth_cert", "Birth Cert"],
          ["passport", "Passport"],
          ["transcript", "Transcript"],
          ["recommendation", "Recommendation"],
          ["report_card", "Report Card"],
          ["medical", "Medical"],
          ["photo", "Photo"],
          ["other", "Other"],
        ],
      },
      { key: "file_url", label: "File Url" },
      { key: "file_name", label: "File Name" },
      { key: "uploaded_at", label: "Uploaded At", type: "date" },
      { key: "is_verified", label: "Is Verified" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "email-notifications": {
    key: "email-notifications",
    icon: DocumentTextIcon,
    label: "Admissions Email Notification",
    endpoint: "email-notifications",
    titleField: "subject",
    subtitleField: "status",
    fields: [
      { key: "application", label: "Application" },
      {
        key: "notification_type",
        label: "Notification Type",
        type: "select",
        options: [
          ["received", "Received"],
          ["review", "Review"],
          ["interview", "Interview"],
          ["document", "Document"],
          ["decision", "Decision"],
          ["acceptance", "Acceptance"],
          ["rejection", "Rejection"],
          ["waitlist", "Waitlist"],
          ["enrollment", "Enrollment"],
          ["fee", "Fee"],
          ["welcome", "Welcome"],
          ["other", "Other"],
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
          ["opened", "Opened"],
          ["failed", "Failed"],
        ],
      },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "message", label: "Message", type: "textarea" },
      { key: "recipient_email", label: "Recipient Email" },
      { key: "recipient_name", label: "Recipient Name" },
      { key: "sent_at", label: "Sent At", type: "date" },
      { key: "opened_at", label: "Opened At", type: "date" },
    ],
  },
  "enrollment-confirmations": {
    key: "enrollment-confirmations",
    icon: DocumentTextIcon,
    label: "Enrollment Confirmation",
    endpoint: "enrollment-confirmations",
    titleField: "application",
    subtitleField: "status",
    fields: [
      { key: "application", label: "Application" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["confirmed", "Confirmed"],
          ["declined", "Declined"],
          ["expired", "Expired"],
          ["cancelled", "Cancelled"],
        ],
      },
      {
        key: "confirmation_sent_at",
        label: "Confirmation Sent At",
        type: "date",
      },
      { key: "confirmation_deadline", label: "Confirmation Deadline" },
      { key: "confirmed_at", label: "Confirmed At", type: "date" },
      { key: "declined_at", label: "Declined At", type: "date" },
      { key: "deposit_amount", label: "Deposit Amount" },
      {
        key: "payment_status",
        label: "Payment Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["paid", "Paid"],
          ["waived", "Waived"],
          ["refunded", "Refunded"],
        ],
      },
      { key: "deposit_paid_at", label: "Deposit Paid At", type: "date" },
      { key: "deposit_transaction_id", label: "Deposit Transaction Id" },
      { key: "decline_reason", label: "Decline Reason" },
      { key: "enrollment_documents", label: "Enrollment Documents" },
      { key: "documents_completed", label: "Documents Completed" },
    ],
  },
  "entrance-assessment": {
    key: "entrance-assessment",
    icon: DocumentTextIcon,
    label: "Entrance Assessment",
    endpoint: "entrance-assessment",
    titleField: "application",
    subtitleField: "status",
    fields: [
      { key: "application", label: "Application" },
      { key: "assessment_type", label: "Assessment Type" },
      { key: "scheduled_date", label: "Scheduled Date", type: "date" },
      { key: "completed_date", label: "Completed Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "score", label: "Score", type: "number" },
      { key: "max_score", label: "Max Score" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "assessor_name", label: "Assessor Name" },
    ],
  },
  fees: {
    key: "fees",
    icon: DocumentTextIcon,
    label: "Application Fee",
    endpoint: "fees",
    titleField: "application",
    subtitleField: "status",
    fields: [
      { key: "application", label: "Application" },
      { key: "amount", label: "Amount", type: "number" },
      { key: "currency", label: "Currency" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["paid", "Paid"],
          ["waived", "Waived"],
          ["refunded", "Refunded"],
          ["failed", "Failed"],
        ],
      },
      {
        key: "payment_method",
        label: "Payment Method",
        type: "select",
        options: [
          ["cash", "Cash"],
          ["bank_transfer", "Bank Transfer"],
          ["card", "Card"],
          ["online", "Online"],
          ["mobile", "Mobile"],
        ],
      },
      { key: "transaction_id", label: "Transaction Id" },
      { key: "payment_date", label: "Payment Date", type: "date" },
      { key: "receipt_number", label: "Receipt Number" },
      { key: "waiver_reason", label: "Waiver Reason" },
      { key: "waived_by", label: "Waived By" },
      { key: "gateway_response", label: "Gateway Response" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "grade-level-capacity": {
    key: "grade-level-capacity",
    icon: DocumentTextIcon,
    label: "Grade Level Capacity",
    endpoint: "grade-level-capacity",
    titleField: "intake",
    fields: [
      { key: "intake", label: "Intake" },
      { key: "grade_level", label: "Grade Level" },
      { key: "max_capacity", label: "Max Capacity" },
      { key: "current_enrollment", label: "Current Enrollment" },
      { key: "waitlist_count", label: "Waitlist Count" },
      { key: "boys_count", label: "Boys Count" },
      { key: "girls_count", label: "Girls Count" },
      { key: "tuition_fee", label: "Tuition Fee" },
      { key: "registration_fee", label: "Registration Fee" },
      { key: "is_accepting", label: "Is Accepting" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  intakes: {
    key: "intakes",
    icon: DocumentTextIcon,
    label: "Enrollment Intake",
    endpoint: "intakes",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      { key: "academic_year", label: "Academic Year" },
      { key: "application_start", label: "Application Start" },
      { key: "application_end", label: "Application End" },
      { key: "enrollment_date", label: "Enrollment Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["open", "Open"],
          ["closed", "Closed"],
          ["upcoming", "Upcoming"],
        ],
      },
      { key: "max_applications", label: "Max Applications" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "application_count", label: "Application Count" },
    ],
  },
  interviews: {
    key: "interviews",
    icon: DocumentTextIcon,
    label: "Interview Schedule",
    endpoint: "interviews",
    titleField: "application",
    subtitleField: "status",
    fields: [
      { key: "application", label: "Application" },
      {
        key: "interview_type",
        label: "Interview Type",
        type: "select",
        options: [
          ["in_person", "In Person"],
          ["video", "Video"],
          ["phone", "Phone"],
          ["panel", "Panel"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
          ["no_show", "No Show"],
          ["rescheduled", "Rescheduled"],
        ],
      },
      { key: "scheduled_date", label: "Scheduled Date", type: "date" },
      { key: "scheduled_time", label: "Scheduled Time" },
      { key: "duration_minutes", label: "Duration Minutes" },
      { key: "location", label: "Location" },
      { key: "meeting_link", label: "Meeting Link" },
      { key: "meeting_id", label: "Meeting Id" },
      { key: "interviewer", label: "Interviewer" },
      { key: "panel_members", label: "Panel Members" },
      { key: "feedback", label: "Feedback" },
    ],
  },
  "merit-entries": {
    key: "merit-entries",
    icon: DocumentTextIcon,
    label: "Merit List Entry",
    endpoint: "merit-entries",
    titleField: "merit_list",
    subtitleField: "status",
    fields: [
      { key: "merit_list", label: "Merit List" },
      { key: "application", label: "Application" },
      { key: "rank", label: "Rank" },
      { key: "total_score", label: "Total Score" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["selected", "Selected"],
          ["waitlisted", "Waitlisted"],
          ["rejected", "Rejected"],
          ["declined", "Declined"],
        ],
      },
      { key: "academic_score", label: "Academic Score" },
      { key: "assessment_score", label: "Assessment Score" },
      { key: "interview_score", label: "Interview Score" },
      { key: "extracurricular_score", label: "Extracurricular Score" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "merit-lists": {
    key: "merit-lists",
    icon: DocumentTextIcon,
    label: "Merit List",
    endpoint: "merit-lists",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "intake", label: "Intake" },
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "grade", label: "Grade" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["published", "Published"],
          ["archived", "Archived"],
        ],
      },
      { key: "total_applicants", label: "Total Applicants" },
      { key: "total_selected", label: "Total Selected" },
      { key: "total_waitlisted", label: "Total Waitlisted" },
      { key: "published_at", label: "Published At", type: "date" },
      { key: "published_by", label: "Published By" },
    ],
  },
  "open-house-event": {
    key: "open-house-event",
    icon: DocumentTextIcon,
    label: "Open House Event",
    endpoint: "open-house-event",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
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
      { key: "event_date", label: "Event Date", type: "date" },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      { key: "location", label: "Location" },
      { key: "max_attendees", label: "Max Attendees" },
      { key: "current_attendees", label: "Current Attendees" },
      { key: "registration_required", label: "Registration Required" },
      { key: "registration_deadline", label: "Registration Deadline" },
      { key: "registration_url", label: "Registration Url" },
    ],
  },
  "open-house-registration": {
    key: "open-house-registration",
    icon: DocumentTextIcon,
    label: "Open House Registration",
    endpoint: "open-house-registration",
    titleField: "event",
    subtitleField: "status",
    fields: [
      { key: "event", label: "Event" },
      { key: "registrant_name", label: "Registrant Name" },
      { key: "registrant_email", label: "Registrant Email" },
      { key: "registrant_phone", label: "Registrant Phone" },
      { key: "child_name", label: "Child Name" },
      { key: "child_dob", label: "Child Dob" },
      { key: "current_grade", label: "Current Grade" },
      { key: "current_school", label: "Current School" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["registered", "Registered"],
          ["confirmed", "Confirmed"],
          ["attended", "Attended"],
          ["cancelled", "Cancelled"],
          ["no_show", "No Show"],
        ],
      },
      { key: "num_attendees", label: "Num Attendees" },
      { key: "application_created", label: "Application Created" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "registered_at", label: "Registered At", type: "date" },
    ],
  },
  pipeline: {
    key: "pipeline",
    icon: DocumentTextIcon,
    label: "Admissions Pipeline",
    endpoint: "pipeline",
    titleField: "application",
    fields: [
      { key: "application", label: "Application" },
      {
        key: "current_stage",
        label: "Current Stage",
        type: "select",
        options: [
          ["inquiry", "Inquiry"],
          ["application", "Application"],
          ["documentation", "Documentation"],
          ["assessment", "Assessment"],
          ["interview", "Interview"],
          ["review", "Review"],
          ["decision", "Decision"],
          ["enrollment", "Enrollment"],
          ["onboarded", "Onboarded"],
        ],
      },
      { key: "inquiry_date", label: "Inquiry Date", type: "date" },
      { key: "application_date", label: "Application Date", type: "date" },
      { key: "documentation_date", label: "Documentation Date", type: "date" },
      { key: "assessment_date", label: "Assessment Date", type: "date" },
      { key: "interview_date", label: "Interview Date", type: "date" },
      { key: "review_date", label: "Review Date", type: "date" },
      { key: "decision_date", label: "Decision Date", type: "date" },
      { key: "enrollment_date", label: "Enrollment Date", type: "date" },
      { key: "onboarded_date", label: "Onboarded Date", type: "date" },
    ],
  },
  "re-enrollments": {
    key: "re-enrollments",
    icon: DocumentTextIcon,
    label: "Re Enrollment",
    endpoint: "re-enrollments",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "intake", label: "Intake" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["invited", "Invited"],
          ["started", "Started"],
          ["completed", "Completed"],
          ["declined", "Declined"],
          ["expired", "Expired"],
        ],
      },
      { key: "current_grade", label: "Current Grade" },
      { key: "next_grade", label: "Next Grade" },
      { key: "invited_at", label: "Invited At", type: "date" },
      { key: "deadline", label: "Deadline" },
      { key: "started_at", label: "Started At", type: "date" },
      { key: "completed_at", label: "Completed At", type: "date" },
      { key: "decline_reason", label: "Decline Reason" },
    ],
  },
  reports: {
    key: "reports",
    icon: DocumentTextIcon,
    label: "Admissions Report",
    endpoint: "reports",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "intake", label: "Intake" },
      { key: "title", label: "Title" },
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: [
          ["summary", "Summary"],
          ["pipeline", "Pipeline"],
          ["conversion", "Conversion"],
          ["demographic", "Demographic"],
          ["financial", "Financial"],
          ["grade", "Grade"],
          ["source", "Source"],
          ["timeline", "Timeline"],
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
      { key: "total_applications", label: "Total Applications" },
      { key: "total_enrolled", label: "Total Enrolled" },
    ],
  },
  reviews: {
    key: "reviews",
    icon: DocumentTextIcon,
    label: "Application Review",
    endpoint: "reviews",
    titleField: "application",
    fields: [
      { key: "application", label: "Application" },
      { key: "reviewer", label: "Reviewer" },
      { key: "reviewer_name", label: "Reviewer Name" },
      { key: "score", label: "Score", type: "number" },
      { key: "strengths", label: "Strengths", type: "textarea" },
      { key: "weaknesses", label: "Weaknesses" },
      { key: "recommendation", label: "Recommendation" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  scholarship: {
    key: "scholarship",
    icon: DocumentTextIcon,
    label: "Scholarship",
    endpoint: "scholarship",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "scholarship_type",
        label: "Scholarship Type",
        type: "select",
        options: [
          ["merit", "Merit"],
          ["need", "Need"],
          ["athletic", "Athletic"],
          ["arts", "Arts"],
          ["sibling", "Sibling"],
          ["employee", "Employee"],
          ["custom", "Custom"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["inactive", "Inactive"],
          ["expired", "Expired"],
        ],
      },
      { key: "amount_type", label: "Amount Type" },
      { key: "amount_fixed", label: "Amount Fixed" },
      { key: "amount_percentage", label: "Amount Percentage" },
      { key: "max_recipients", label: "Max Recipients" },
      { key: "current_recipients", label: "Current Recipients" },
      { key: "min_gpa", label: "Min Gpa" },
      { key: "eligible_grades", label: "Eligible Grades" },
      { key: "eligible_intakes", label: "Eligible Intakes" },
    ],
  },
  "scholarship-application": {
    key: "scholarship-application",
    icon: DocumentTextIcon,
    label: "Scholarship Application",
    endpoint: "scholarship-application",
    titleField: "scholarship",
    subtitleField: "status",
    fields: [
      { key: "scholarship", label: "Scholarship" },
      { key: "application", label: "Application" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["submitted", "Submitted"],
          ["review", "Review"],
          ["approved", "Approved"],
          ["denied", "Denied"],
          ["waitlisted", "Waitlisted"],
        ],
      },
      { key: "essay", label: "Essay" },
      { key: "recommendation_letter", label: "Recommendation Letter" },
      { key: "transcript", label: "Transcript" },
      { key: "family_income", label: "Family Income" },
      { key: "financial_need_score", label: "Financial Need Score" },
      { key: "merit_score", label: "Merit Score" },
      { key: "gpa_at_application", label: "Gpa At Application" },
      { key: "decision_notes", label: "Decision Notes" },
      { key: "amount_awarded", label: "Amount Awarded" },
    ],
  },
  "sibling-group": {
    key: "sibling-group",
    icon: DocumentTextIcon,
    label: "Sibling Group",
    endpoint: "sibling-group",
    titleField: "family_name",
    fields: [
      { key: "family_name", label: "Family Name" },
      { key: "parent_name", label: "Parent Name" },
      { key: "parent_email", label: "Parent Email" },
      { key: "parent_phone", label: "Parent Phone" },
      { key: "total_siblings", label: "Total Siblings" },
      { key: "currently_enrolled", label: "Currently Enrolled" },
      { key: "sibling_priority", label: "Sibling Priority" },
    ],
  },
  "sibling-record": {
    key: "sibling-record",
    icon: DocumentTextIcon,
    label: "Sibling Record",
    endpoint: "sibling-record",
    titleField: "sibling_group",
    fields: [
      { key: "sibling_group", label: "Sibling Group" },
      { key: "student", label: "Student" },
      { key: "application", label: "Application" },
      { key: "is_currently_enrolled", label: "Is Currently Enrolled" },
      { key: "grade_level", label: "Grade Level" },
      { key: "enrollment_date", label: "Enrollment Date", type: "date" },
    ],
  },
  "sms-notifications": {
    key: "sms-notifications",
    icon: DocumentTextIcon,
    label: "Admissions S M S Notification",
    endpoint: "sms-notifications",
    titleField: "application",
    subtitleField: "status",
    fields: [
      { key: "application", label: "Application" },
      {
        key: "notification_type",
        label: "Notification Type",
        type: "select",
        options: [
          ["received", "Received"],
          ["interview", "Interview"],
          ["decision", "Decision"],
          ["enrollment", "Enrollment"],
          ["fee", "Fee"],
          ["general", "General"],
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
      { key: "message", label: "Message", type: "textarea" },
      { key: "phone_number", label: "Phone Number" },
      { key: "sent_at", label: "Sent At", type: "date" },
      { key: "delivered_at", label: "Delivered At", type: "date" },
    ],
  },
  templates: {
    key: "templates",
    icon: DocumentTextIcon,
    label: "Application Template",
    endpoint: "templates",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "intake", label: "Intake" },
      { key: "required_fields", label: "Required Fields" },
      { key: "optional_fields", label: "Optional Fields" },
      { key: "required_documents", label: "Required Documents" },
      { key: "application_fee", label: "Application Fee" },
      { key: "currency", label: "Currency" },
      { key: "allow_late_applications", label: "Allow Late Applications" },
      { key: "late_fee_deadline_days", label: "Late Fee Deadline Days" },
      {
        key: "max_applications_per_student",
        label: "Max Applications Per Student",
      },
    ],
  },
  "transfer-student": {
    key: "transfer-student",
    icon: DocumentTextIcon,
    label: "Transfer Student",
    endpoint: "transfer-student",
    titleField: "application",
    fields: [
      { key: "application", label: "Application" },
      { key: "previous_school_name", label: "Previous School Name" },
      { key: "previous_school_address", label: "Previous School Address" },
      { key: "previous_school_phone", label: "Previous School Phone" },
      { key: "previous_school_email", label: "Previous School Email" },
      { key: "previous_school_type", label: "Previous School Type" },
      { key: "years_attended", label: "Years Attended" },
      { key: "last_grade_completed", label: "Last Grade Completed" },
      { key: "graduation_date", label: "Graduation Date", type: "date" },
      { key: "previous_gpa", label: "Previous Gpa" },
      { key: "class_rank", label: "Class Rank" },
    ],
  },
  waitlist: {
    key: "waitlist",
    icon: DocumentTextIcon,
    label: "Waitlist Management",
    endpoint: "waitlist",
    titleField: "application",
    subtitleField: "status",
    fields: [
      { key: "application", label: "Application" },
      { key: "position", label: "Position", type: "number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["waiting", "Waiting"],
          ["offered", "Offered"],
          ["accepted", "Accepted"],
          ["declined", "Declined"],
          ["expired", "Expired"],
          ["removed", "Removed"],
        ],
      },
      { key: "offer_extended_at", label: "Offer Extended At", type: "date" },
      { key: "offer_expires_at", label: "Offer Expires At", type: "date" },
      { key: "offer_accepted_at", label: "Offer Accepted At", type: "date" },
      { key: "offer_declined_at", label: "Offer Declined At", type: "date" },
      { key: "decline_reason", label: "Decline Reason" },
      { key: "last_notified_at", label: "Last Notified At", type: "date" },
      { key: "notification_count", label: "Notification Count" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },

  // ===== admissions_map =====
};

const TABS = Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({
  key,
  label: cfg.label,
  icon: DocumentTextIcon,
}));

export default function AdmissionsCenterPage() {
  useTitle("Admissions Center");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Admissions Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Applications, intakes, decisions, documents, interviews, scholarships, waitlists and
            analytics
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
            leftIcon={<DocumentTextIcon className="h-4 w-4" />}
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
        basePath="/admissions"
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
