/**
 * Health Center — full-surface admin page for the health_clinic module.
 *
 * 42 entity tabs (config-driven via EntitySection): health records & nurse
 * visits, immunizations & medications, forms & screenings & compliance,
 * allergies & chronic conditions & emergency plans, growth charts & vitals
 * & dental/vision/lab records, alerts & incidents & referrals, mental health,
 * education & campaigns, notifications, telehealth, reports, equipment,
 * staff training and audits.
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
  DocumentTextIcon,
  ClockIcon,
  ShieldCheckIcon,
  BeakerIcon,
  ClipboardDocumentListIcon,
  InboxIcon,
  ClipboardDocumentCheckIcon,
  CheckBadgeIcon,
  ExclamationTriangleIcon,
  UserGroupIcon,
  LifebuoyIcon,
  PhoneIcon,
  BanknotesIcon,
  QueueListIcon,
  IdentificationIcon,
  ScaleIcon,
  SparklesIcon,
  ChartBarIcon,
  TicketIcon,
  EyeIcon,
  CalendarDaysIcon,
  BellAlertIcon,
  AcademicCapIcon,
  CloudIcon,
  VideoCameraIcon,
  WrenchScrewdriverIcon,
  CubeIcon,
  ArrowPathIcon,
  GiftIcon,
  FireIcon,
  EnvelopeIcon,
  MapPinIcon,
  TagIcon,
  GlobeAltIcon,
  BuildingOffice2Icon,
  SignalIcon,
} from "@heroicons/react/24/outline";

// ─── Shared option sets ──────────────────────────────────────────────────────

const BLOOD_TYPES = [
  ["A+", "A+"],
  ["A-", "A-"],
  ["B+", "B+"],
  ["B-", "B-"],
  ["AB+", "AB+"],
  ["AB-", "AB-"],
  ["O+", "O+"],
  ["O-", "O-"],
  ["unknown", "Unknown"],
] as [string, string][];

const VISIT_TYPES = [
  ["sick", "Sick"],
  ["injury", "Injury"],
  ["medication", "Medication"],
  ["checkup", "Checkup"],
  ["followup", "Follow-up"],
  ["other", "Other"],
] as [string, string][];

const VISIT_STATUS = [
  ["treated", "Treated"],
  ["referred", "Referred"],
  ["medication_given", "Medication Given"],
  ["observation", "Observation"],
] as [string, string][];

const FORM_TYPES = [
  ["health_history", "Health History"],
  ["immunization_record", "Immunization Record"],
  ["medication_auth", "Medication Auth"],
  ["allergy_plan", "Allergy Plan"],
  ["asthma_plan", "Asthma Plan"],
  ["diabetes_mgmt", "Diabetes Mgmt"],
  ["emergency_contact", "Emergency Contact"],
  ["physical_exam", "Physical Exam"],
  ["consent", "Consent"],
  ["waiver", "Waiver"],
  ["other", "Other"],
] as [string, string][];

const FORM_STATUS = [
  ["draft", "Draft"],
  ["active", "Active"],
  ["inactive", "Inactive"],
] as [string, string][];

const SUBMISSION_STATUS = [
  ["pending", "Pending"],
  ["submitted", "Submitted"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["needs_revision", "Needs Revision"],
] as [string, string][];

const ALLERGY_TYPES = [
  ["food", "Food"],
  ["medication", "Medication"],
  ["environmental", "Environmental"],
  ["insect", "Insect"],
  ["latex", "Latex"],
  ["other", "Other"],
] as [string, string][];

const SEVERITY = [
  ["mild", "Mild"],
  ["moderate", "Moderate"],
  ["severe", "Severe"],
] as [string, string][];

const ALLERGY_SEVERITY = [
  ["mild", "Mild"],
  ["moderate", "Moderate"],
  ["severe", "Severe"],
  ["life_threatening", "Life-Threatening"],
] as [string, string][];

const CONDITION_TYPES = [
  ["diabetes", "Diabetes"],
  ["asthma", "Asthma"],
  ["epilepsy", "Epilepsy"],
  ["allergies", "Allergies"],
  ["heart", "Heart"],
  ["sickle_cell", "Sickle Cell"],
  ["cystic_fibrosis", "Cystic Fibrosis"],
  ["autism", "Autism"],
  ["adhd", "ADHD"],
  ["other", "Other"],
] as [string, string][];

const PLAN_TYPES = [
  ["medical", "Medical"],
  ["allergic", "Allergic"],
  ["seizure", "Seizure"],
  ["diabetic", "Diabetic"],
  ["asthma", "Asthma"],
  ["injury", "Injury"],
  ["mental_health", "Mental Health"],
  ["general", "General"],
] as [string, string][];

const PLAN_STATUS = [
  ["active", "Active"],
  ["under_review", "Under Review"],
  ["inactive", "Inactive"],
] as [string, string][];

const RELATIONSHIPS = [
  ["parent", "Parent"],
  ["guardian", "Guardian"],
  ["grandparent", "Grandparent"],
  ["sibling", "Sibling"],
  ["other_family", "Other Family"],
  ["other", "Other"],
] as [string, string][];

const SCREENING_TYPES = [
  ["vision", "Vision"],
  ["hearing", "Hearing"],
  ["scoliosis", "Scoliosis"],
  ["bmi", "BMI"],
  ["dental", "Dental"],
  ["bp", "Blood Pressure"],
  ["tb", "TB"],
  ["other", "Other"],
] as [string, string][];

const SCREENING_STATUS = [
  ["scheduled", "Scheduled"],
  ["completed", "Completed"],
  ["referred", "Referred"],
  ["follow_up", "Follow-Up"],
] as [string, string][];

const MED_CATEGORIES = [
  ["pain", "Pain"],
  ["antihistamine", "Antihistamine"],
  ["respiratory", "Respiratory"],
  ["gastro", "Gastro"],
  ["topical", "Topical"],
  ["emergency", "Emergency"],
  ["other", "Other"],
] as [string, string][];

const PRESCRIPTION_STATUS = [
  ["pending", "Pending"],
  ["active", "Active"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
  ["expired", "Expired"],
] as [string, string][];

const NOTIF_TYPES = [
  ["medication", "Medication"],
  ["clinic", "Clinic"],
  ["fever", "Fever"],
  ["injury", "Injury"],
  ["illness", "Illness"],
  ["allergy", "Allergy"],
  ["screening", "Screening"],
  ["immunization", "Immunization"],
  ["form", "Form"],
  ["emergency", "Emergency"],
  ["other", "Other"],
] as [string, string][];

const DELIVERY_METHODS = [
  ["email", "Email"],
  ["sms", "SMS"],
  ["push", "Push"],
  ["in_app", "In-App"],
] as [string, string][];

const NOTIF_STATUS = [
  ["pending", "Pending"],
  ["sent", "Sent"],
  ["delivered", "Delivered"],
  ["read", "Read"],
  ["failed", "Failed"],
] as [string, string][];

const COMPLIANCE_TYPES = [
  ["immunization", "Immunization"],
  ["physical", "Physical"],
  ["dental", "Dental"],
  ["tb", "TB"],
  ["vision", "Vision"],
  ["hearing", "Hearing"],
  ["form", "Form"],
  ["med_auth", "Med Auth"],
  ["other", "Other"],
] as [string, string][];

const COMPLIANCE_STATUS = [
  ["compliant", "Compliant"],
  ["non_compliant", "Non-Compliant"],
  ["pending", "Pending"],
  ["exempted", "Exempted"],
  ["overdue", "Overdue"],
] as [string, string][];

const SHIFTS = [
  ["morning", "Morning"],
  ["afternoon", "Afternoon"],
  ["full_day", "Full Day"],
  ["on_call", "On Call"],
] as [string, string][];

const INCIDENT_TYPES = [
  ["injury", "Injury"],
  ["illness", "Illness"],
  ["allergy", "Allergy"],
  ["seizure", "Seizure"],
  ["fainting", "Fainting"],
  ["breathing", "Breathing"],
  ["headache", "Headache"],
  ["blood", "Blood"],
  ["other", "Other"],
] as [string, string][];

const INCIDENT_SEVERITY = [
  ["minor", "Minor"],
  ["moderate", "Moderate"],
  ["severe", "Severe"],
  ["critical", "Critical"],
] as [string, string][];

const ACTIONS_TAKEN = [
  ["none", "None"],
  ["first_aid", "First Aid"],
  ["medication", "Medication"],
  ["referral", "Referral"],
  ["ems", "EMS"],
  ["parent", "Parent"],
] as [string, string][];

const REFERRAL_REASONS = [
  ["specialist", "Specialist"],
  ["hospital", "Hospital"],
  ["testing", "Testing"],
  ["treatment", "Treatment"],
  ["emergency", "Emergency"],
  ["mental_health", "Mental Health"],
  ["dental", "Dental"],
  ["vision", "Vision"],
  ["other", "Other"],
] as [string, string][];

const REFERRAL_STATUS = [
  ["pending", "Pending"],
  ["confirmed", "Confirmed"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
  ["no_show", "No Show"],
] as [string, string][];

const REPORT_TYPES = [
  ["immunization", "Immunization"],
  ["clinic", "Clinic"],
  ["medication", "Medication"],
  ["allergy", "Allergy"],
  ["incident", "Incident"],
  ["screening", "Screening"],
  ["compliance", "Compliance"],
  ["chronic", "Chronic"],
  ["general", "General"],
] as [string, string][];

const REPORT_STATUS = [
  ["draft", "Draft"],
  ["generated", "Generated"],
  ["sent", "Sent"],
] as [string, string][];

const ALERT_TYPES = [
  ["epi_pen", "EpiPen"],
  ["inhaler", "Inhaler"],
  ["diabetic", "Diabetic"],
  ["seizure", "Seizure"],
  ["allergy", "Allergy"],
  ["other", "Other"],
] as [string, string][];

const RESOURCE_TYPES = [
  ["document", "Document"],
  ["video", "Video"],
  ["link", "Link"],
  ["handout", "Handout"],
  ["presentation", "Presentation"],
  ["other", "Other"],
] as [string, string][];

const TOPIC_CATEGORIES = [
  ["nutrition", "Nutrition"],
  ["hygiene", "Hygiene"],
  ["mental_health", "Mental Health"],
  ["substance", "Substance"],
  ["sex_ed", "Sex Ed"],
  ["first_aid", "First Aid"],
  ["exercise", "Exercise"],
  ["sleep", "Sleep"],
  ["general", "General"],
  ["other", "Other"],
] as [string, string][];

const TELEHEALTH_TYPES = [
  ["consultation", "Consultation"],
  ["follow_up", "Follow-Up"],
  ["mental_health", "Mental Health"],
  ["specialist", "Specialist"],
  ["emergency", "Emergency"],
  ["other", "Other"],
] as [string, string][];

const TELEHEALTH_STATUS = [
  ["scheduled", "Scheduled"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
  ["no_show", "No Show"],
] as [string, string][];

const DENTAL_STATUS = [
  ["scheduled", "Scheduled"],
  ["completed", "Completed"],
  ["follow_up", "Follow-Up"],
] as [string, string][];

const VISION_RESULTS = [
  ["normal", "Normal"],
  ["needs_correction", "Needs Correction"],
  ["referred", "Referred"],
] as [string, string][];

const LAB_STATUS = [
  ["pending", "Pending"],
  ["completed", "Completed"],
  ["reviewed", "Reviewed"],
] as [string, string][];

const HISTORY_TYPES = [
  ["condition", "Condition"],
  ["surgery", "Surgery"],
  ["hospitalization", "Hospitalization"],
  ["injury", "Injury"],
  ["other", "Other"],
] as [string, string][];

const INSURANCE_TYPES = [
  ["health", "Health"],
  ["dental", "Dental"],
  ["vision", "Vision"],
  ["other", "Other"],
] as [string, string][];

const VACC_STATUS = [
  ["due", "Due"],
  ["completed", "Completed"],
  ["overdue", "Overdue"],
  ["exempted", "Exempted"],
] as [string, string][];

const ASSESSMENT_TYPES = [
  ["annual", "Annual"],
  ["sports", "Sports"],
  ["pre_enrollment", "Pre-Enrollment"],
  ["follow_up", "Follow-Up"],
  ["other", "Other"],
] as [string, string][];

const RISK_LEVELS = [
  ["low", "Low"],
  ["moderate", "Moderate"],
  ["high", "High"],
  ["critical", "Critical"],
] as [string, string][];

const SESSION_TYPES = [
  ["counseling", "Counseling"],
  ["therapy", "Therapy"],
  ["assessment", "Assessment"],
  ["crisis", "Crisis"],
  ["other", "Other"],
] as [string, string][];

const MATERIAL_TYPES = [
  ["brochure", "Brochure"],
  ["video", "Video"],
  ["article", "Article"],
  ["poster", "Poster"],
  ["other", "Other"],
] as [string, string][];

const CAMPAIGN_STATUS = [
  ["planned", "Planned"],
  ["active", "Active"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const SURVEY_STATUS = [
  ["draft", "Draft"],
  ["active", "Active"],
  ["closed", "Closed"],
] as [string, string][];

const EQUIPMENT_STATUS = [
  ["operational", "Operational"],
  ["maintenance", "Maintenance"],
  ["retired", "Retired"],
  ["out_of_service", "Out of Service"],
] as [string, string][];

const MAINTENANCE_TYPES = [
  ["calibration", "Calibration"],
  ["repair", "Repair"],
  ["preventive", "Preventive"],
  ["other", "Other"],
] as [string, string][];

const AUDIT_TYPES = [
  ["compliance", "Compliance"],
  ["quality", "Quality"],
  ["safety", "Safety"],
  ["other", "Other"],
] as [string, string][];

const AUDIT_STATUS = [
  ["scheduled", "Scheduled"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
] as [string, string][];

// ─── Entity configurations (42 tabs) ─────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  records: {
    key: "records",
    label: "Health Records",
    icon: DocumentTextIcon,
    endpoint: "records",
    titleField: "student_name",
    subtitleField: "doctor_name",
    searchKeys: ["student_name", "blood_type", "doctor_name"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "blood_type",
        label: "Blood Type",
        type: "select",
        options: BLOOD_TYPES,
        badge: true,
      },
      { key: "height_cm", label: "Height (cm)", type: "number" },
      { key: "weight_kg", label: "Weight (kg)", type: "number" },
      { key: "allergies", label: "Allergies", full: true },
      { key: "chronic_conditions", label: "Chronic Conditions", full: true },
      { key: "medications", label: "Medications", full: true },
      { key: "emergency_contact_name", label: "Emergency Contact", card: true },
      { key: "emergency_contact_phone", label: "Emergency Phone" },
      { key: "doctor_name", label: "Doctor", card: true },
      { key: "doctor_phone", label: "Doctor Phone" },
    ],
  },
  visits: {
    key: "visits",
    label: "Nurse Visits",
    icon: ClockIcon,
    endpoint: "visits",
    titleField: "student_name",
    subtitleField: "visit_type",
    searchKeys: ["student_name", "visit_type", "status", "diagnosis"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "visit_type",
        label: "Visit Type",
        type: "select",
        options: VISIT_TYPES,
        badge: true,
      },
      { key: "visit_date", label: "Visit Date", type: "datetime", card: true },
      { key: "symptoms", label: "Symptoms", type: "textarea", full: true },
      { key: "diagnosis", label: "Diagnosis", type: "textarea", full: true },
      { key: "treatment", label: "Treatment", type: "textarea", full: true },
      { key: "medication_given", label: "Medication Given" },
      { key: "temperature_c", label: "Temperature (°C)", type: "number" },
      { key: "blood_pressure", label: "Blood Pressure" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: VISIT_STATUS,
        badge: true,
      },
      { key: "treated_by", label: "Treated By (User ID)" },
      { key: "treated_by_name", label: "Treated By", skipForm: true },
    ],
  },
  immunizations: {
    key: "immunizations",
    label: "Immunizations",
    icon: ShieldCheckIcon,
    endpoint: "immunizations",
    titleField: "vaccine_name",
    subtitleField: "student_name",
    searchKeys: ["vaccine_name", "student_name", "facility", "batch_number"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "vaccine_name", label: "Vaccine", main: true },
      { key: "dose_number", label: "Dose Number", type: "number" },
      {
        key: "date_administered",
        label: "Date Administered",
        type: "datetime",
        card: true,
      },
      { key: "administered_by", label: "Administered By" },
      { key: "facility", label: "Facility", card: true },
      { key: "batch_number", label: "Batch Number" },
      { key: "next_due_date", label: "Next Due", type: "date" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "medication-logs": {
    key: "medication-logs",
    label: "Medication Logs",
    icon: BeakerIcon,
    endpoint: "medication-logs",
    titleField: "medication_name",
    subtitleField: "student_name",
    searchKeys: ["medication_name", "student_name", "administered_by_name"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "medication_name", label: "Medication", main: true },
      { key: "dosage", label: "Dosage", card: true },
      { key: "route", label: "Route" },
      { key: "time_administered", label: "Time", type: "datetime", card: true },
      { key: "administered_by", label: "Administered By (User ID)" },
      { key: "administered_by_name", label: "Administered By", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  forms: {
    key: "forms",
    label: "Health Forms",
    icon: ClipboardDocumentListIcon,
    endpoint: "forms",
    titleField: "title",
    subtitleField: "form_type",
    searchKeys: ["title", "form_type", "status", "created_by_name"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "form_type",
        label: "Form Type",
        type: "select",
        options: FORM_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: FORM_STATUS,
        badge: true,
      },
      {
        key: "form_fields",
        label: "Form Fields (JSON)",
        type: "textarea",
        full: true,
      },
      {
        key: "instructions",
        label: "Instructions",
        type: "textarea",
        full: true,
      },
      { key: "is_required", label: "Required", type: "bool" },
      { key: "due_date", label: "Due Date", type: "date", card: true },
      { key: "created_by", label: "Created By (User ID)", skipForm: true },
      { key: "created_by_name", label: "Created By", skipForm: true },
    ],
  },
  "form-submissions": {
    key: "form-submissions",
    label: "Form Submissions",
    icon: InboxIcon,
    endpoint: "form-submissions",
    titleField: "form_title",
    subtitleField: "student_name",
    searchKeys: ["form_title", "student_name", "status", "submitted_by_name"],
    fields: [
      { key: "form", label: "Form (ID)", full: true },
      { key: "form_title", label: "Form", skipForm: true },
      { key: "student", label: "Student (ID)" },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "submitted_by", label: "Submitted By (User ID)" },
      { key: "submitted_by_name", label: "Submitted By", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: SUBMISSION_STATUS,
        badge: true,
      },
      {
        key: "form_data",
        label: "Form Data (JSON)",
        type: "textarea",
        full: true,
      },
      { key: "attachments", label: "Attachments" },
      { key: "reviewed_by", label: "Reviewed By (User ID)" },
      { key: "reviewed_by_name", label: "Reviewed By", skipForm: true },
      { key: "reviewed_at", label: "Reviewed At", type: "datetime" },
      {
        key: "review_notes",
        label: "Review Notes",
        type: "textarea",
        full: true,
      },
      { key: "signature_data", label: "Signature Data", skipForm: true },
    ],
  },
  screenings: {
    key: "screenings",
    label: "Screenings",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "screenings",
    titleField: "student_name",
    subtitleField: "screening_type",
    searchKeys: ["student_name", "screening_type", "status", "screened_by_name"],
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
      { key: "screening_date", label: "Date", type: "date", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: SCREENING_STATUS,
        badge: true,
      },
      {
        key: "result_summary",
        label: "Result Summary",
        type: "textarea",
        full: true,
      },
      { key: "is_normal", label: "Normal", type: "bool" },
      { key: "referral_needed", label: "Referral Needed", type: "bool" },
      {
        key: "referral_notes",
        label: "Referral Notes",
        type: "textarea",
        full: true,
      },
      { key: "referred_to", label: "Referred To" },
      { key: "screened_by", label: "Screened By (User ID)" },
      { key: "screened_by_name", label: "Screened By", skipForm: true },
    ],
  },
  "screening-results": {
    key: "screening-results",
    label: "Screening Results",
    icon: CheckBadgeIcon,
    endpoint: "screening-results",
    titleField: "metric_name",
    subtitleField: "screening_label",
    searchKeys: ["metric_name", "screening_label"],
    fields: [
      { key: "screening", label: "Screening (ID)", full: true },
      { key: "screening_label", label: "Screening", skipForm: true },
      { key: "metric_name", label: "Metric", main: true },
      { key: "metric_value", label: "Value", card: true },
      { key: "normal_range", label: "Normal Range" },
      { key: "is_abnormal", label: "Abnormal", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  compliance: {
    key: "compliance",
    label: "Compliance",
    icon: CheckBadgeIcon,
    endpoint: "compliance",
    titleField: "student_name",
    subtitleField: "compliance_type",
    searchKeys: ["student_name", "compliance_type", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "compliance_type",
        label: "Type",
        type: "select",
        options: COMPLIANCE_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: COMPLIANCE_STATUS,
        badge: true,
      },
      { key: "due_date", label: "Due Date", type: "date", card: true },
      { key: "completed_date", label: "Completed", type: "date" },
      { key: "expiration_date", label: "Expires", type: "date" },
      { key: "requirement", label: "Requirement", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      { key: "document_url", label: "Document URL", full: true },
      { key: "verified_by", label: "Verified By (User ID)" },
      { key: "verified_by_name", label: "Verified By", skipForm: true },
    ],
  },
  "health-audit": {
    key: "health-audit",
    label: "Health Audits",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "health-audit",
    titleField: "title",
    subtitleField: "audit_type",
    searchKeys: ["title", "audit_type", "status", "auditor_name"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "audit_type",
        label: "Type",
        type: "select",
        options: AUDIT_TYPES,
        badge: true,
      },
      { key: "audit_date", label: "Audit Date", type: "date", card: true },
      { key: "auditor", label: "Auditor (User ID)" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: AUDIT_STATUS,
        badge: true,
      },
      { key: "findings", label: "Findings", type: "textarea", full: true },
      {
        key: "recommendations",
        label: "Recommendations",
        type: "textarea",
        full: true,
      },
      {
        key: "corrective_actions",
        label: "Corrective Actions",
        type: "textarea",
        full: true,
      },
      {
        key: "compliance_score",
        label: "Compliance Score",
        type: "number",
        card: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      { key: "report_url", label: "Report URL", full: true },
    ],
  },
  allergies: {
    key: "allergies",
    label: "Allergies",
    icon: ExclamationTriangleIcon,
    endpoint: "allergies",
    titleField: "allergen_name",
    subtitleField: "student_name",
    searchKeys: ["allergen_name", "student_name", "allergy_type", "severity"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "allergen_name", label: "Allergen", main: true },
      {
        key: "allergy_type",
        label: "Type",
        type: "select",
        options: ALLERGY_TYPES,
        badge: true,
      },
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: ALLERGY_SEVERITY,
        badge: true,
      },
      { key: "symptoms", label: "Symptoms", type: "textarea", full: true },
      {
        key: "reaction_description",
        label: "Reaction Description",
        type: "textarea",
        full: true,
      },
      {
        key: "treatment_protocol",
        label: "Treatment Protocol",
        type: "textarea",
        full: true,
      },
      {
        key: "emergency_medication",
        label: "Emergency Medication",
        card: true,
      },
      { key: "medication_location", label: "Medication Location" },
      { key: "diagnosis_date", label: "Diagnosed", type: "date" },
      { key: "diagnosed_by", label: "Diagnosed By" },
    ],
  },
  "chronic-conditions": {
    key: "chronic-conditions",
    label: "Chronic Conditions",
    icon: FireIcon,
    endpoint: "chronic-conditions",
    titleField: "condition_name",
    subtitleField: "student_name",
    searchKeys: ["condition_name", "student_name", "condition_type", "severity"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "condition_type",
        label: "Type",
        type: "select",
        options: CONDITION_TYPES,
        badge: true,
      },
      { key: "condition_name", label: "Condition", main: true },
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: SEVERITY,
        badge: true,
      },
      { key: "diagnosed_date", label: "Diagnosed", type: "date", card: true },
      { key: "diagnosed_by", label: "Diagnosed By" },
      {
        key: "management_plan",
        label: "Management Plan",
        type: "textarea",
        full: true,
      },
      {
        key: "medication_schedule",
        label: "Medication Schedule",
        type: "textarea",
        full: true,
      },
      {
        key: "dietary_restrictions",
        label: "Dietary Restrictions",
        type: "textarea",
        full: true,
      },
      {
        key: "activity_restrictions",
        label: "Activity Restrictions",
        type: "textarea",
        full: true,
      },
      {
        key: "emergency_protocol",
        label: "Emergency Protocol",
        type: "textarea",
        full: true,
      },
    ],
  },
  "emergency-plans": {
    key: "emergency-plans",
    label: "Emergency Plans",
    icon: LifebuoyIcon,
    endpoint: "emergency-plans",
    titleField: "title",
    subtitleField: "plan_type",
    searchKeys: ["title", "plan_type", "status", "created_by_name"],
    fields: [
      { key: "title", label: "Title", main: true },
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
      { key: "procedures", label: "Procedures", type: "textarea", full: true },
      { key: "responsible_staff", label: "Responsible Staff", full: true },
      { key: "contact_numbers", label: "Contact Numbers", full: true },
      { key: "required_equipment", label: "Required Equipment", full: true },
      { key: "equipment_location", label: "Equipment Location", card: true },
      { key: "last_training_date", label: "Last Training", type: "date" },
      {
        key: "training_notes",
        label: "Training Notes",
        type: "textarea",
        full: true,
      },
      { key: "effective_date", label: "Effective Date", type: "date" },
      { key: "created_by", label: "Created By (User ID)", skipForm: true },
      { key: "created_by_name", label: "Created By", skipForm: true },
    ],
  },
  "emergency-contacts": {
    key: "emergency-contacts",
    label: "Emergency Contacts",
    icon: PhoneIcon,
    endpoint: "emergency-contacts",
    titleField: "contact_name",
    subtitleField: "student_name",
    toggleField: "is_primary",
    searchKeys: ["contact_name", "student_name", "relationship"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "contact_name", label: "Contact Name", main: true },
      {
        key: "relationship",
        label: "Relationship",
        type: "select",
        options: RELATIONSHIPS,
        badge: true,
      },
      { key: "phone_primary", label: "Primary Phone", card: true },
      { key: "phone_secondary", label: "Secondary Phone" },
      { key: "email", label: "Email" },
      { key: "address", label: "Address", full: true },
      { key: "is_primary", label: "Primary", type: "bool" },
      { key: "can_pickup", label: "Can Pick Up", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "medical-history": {
    key: "medical-history",
    label: "Medical History",
    icon: IdentificationIcon,
    endpoint: "medical-history",
    titleField: "condition_name",
    subtitleField: "student_name",
    searchKeys: ["condition_name", "student_name", "history_type", "treating_physician"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "history_type",
        label: "Type",
        type: "select",
        options: HISTORY_TYPES,
        badge: true,
      },
      { key: "condition_name", label: "Condition", main: true },
      { key: "diagnosis_date", label: "Diagnosed", type: "date", card: true },
      { key: "treating_physician", label: "Treating Physician", card: true },
      { key: "treatment", label: "Treatment", type: "textarea", full: true },
      { key: "outcome", label: "Outcome", type: "textarea", full: true },
      { key: "is_chronic", label: "Chronic", type: "bool" },
      { key: "is_resolved", label: "Resolved", type: "bool" },
      { key: "resolved_date", label: "Resolved Date", type: "date" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "medication-inventory": {
    key: "medication-inventory",
    label: "Medication Inventory",
    icon: BanknotesIcon,
    endpoint: "medication-inventory",
    titleField: "medication_name",
    subtitleField: "category",
    searchKeys: ["medication_name", "generic_name", "category", "supplier"],
    fields: [
      { key: "medication_name", label: "Medication", main: true },
      { key: "generic_name", label: "Generic Name", card: true },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: MED_CATEGORIES,
        badge: true,
      },
      {
        key: "quantity_on_hand",
        label: "Quantity",
        type: "number",
        card: true,
      },
      { key: "unit_of_measure", label: "Unit" },
      { key: "reorder_threshold", label: "Reorder Threshold", type: "number" },
      { key: "storage_location", label: "Storage Location" },
      { key: "requires_refrigeration", label: "Refrigerated", type: "bool" },
      { key: "expiration_date", label: "Expires", type: "date", card: true },
      { key: "lot_number", label: "Lot Number" },
      { key: "supplier", label: "Supplier" },
      { key: "last_reorder_date", label: "Last Reorder", type: "date" },
    ],
  },
  prescriptions: {
    key: "prescriptions",
    label: "Prescriptions",
    icon: TagIcon,
    endpoint: "prescriptions",
    titleField: "medication_name",
    subtitleField: "student_name",
    searchKeys: ["medication_name", "student_name", "status", "prescribed_by"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "medication_name", label: "Medication", main: true },
      { key: "dosage", label: "Dosage", card: true },
      { key: "frequency", label: "Frequency" },
      { key: "route", label: "Route" },
      { key: "start_date", label: "Start Date", type: "date", card: true },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "times_per_day", label: "Times Per Day", type: "number" },
      { key: "administration_times", label: "Administration Times" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: PRESCRIPTION_STATUS,
        badge: true,
      },
      { key: "prescribed_by", label: "Prescribed By", card: true },
      { key: "prescriber_phone", label: "Prescriber Phone" },
    ],
  },
  "family-medical-history": {
    key: "family-medical-history",
    label: "Family History",
    icon: UserGroupIcon,
    endpoint: "family-medical-history",
    titleField: "condition_name",
    subtitleField: "student_name",
    searchKeys: ["condition_name", "student_name", "relationship"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "relationship",
        label: "Relationship",
        type: "select",
        options: RELATIONSHIPS,
        badge: true,
      },
      { key: "condition_name", label: "Condition", main: true },
      { key: "age_at_diagnosis", label: "Age at Diagnosis", type: "number" },
      { key: "is_hereditary", label: "Hereditary", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "health-insurance-record": {
    key: "health-insurance-record",
    label: "Insurance Records",
    icon: ScaleIcon,
    endpoint: "health-insurance-record",
    titleField: "provider_name",
    subtitleField: "student_name",
    searchKeys: ["provider_name", "student_name", "policy_number", "insurance_type"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "insurance_type",
        label: "Type",
        type: "select",
        options: INSURANCE_TYPES,
        badge: true,
      },
      { key: "provider_name", label: "Provider", main: true },
      { key: "policy_number", label: "Policy Number", card: true },
      { key: "group_number", label: "Group Number" },
      { key: "subscriber_name", label: "Subscriber", card: true },
      { key: "subscriber_relationship", label: "Subscriber Relationship" },
      { key: "effective_date", label: "Effective", type: "date" },
      { key: "expiry_date", label: "Expiry", type: "date" },
      { key: "coverage_amount", label: "Coverage Amount", type: "number" },
      { key: "copay_amount", label: "Copay", type: "number" },
    ],
  },
  "growth-chart": {
    key: "growth-chart",
    label: "Growth Charts",
    icon: ChartBarIcon,
    endpoint: "growth-chart",
    titleField: "student_name",
    subtitleField: "recorded_date",
    searchKeys: ["student_name", "recorded_by_name"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "recorded_date",
        label: "Recorded Date",
        type: "date",
        card: true,
      },
      { key: "height_cm", label: "Height (cm)", type: "number", card: true },
      { key: "weight_kg", label: "Weight (kg)", type: "number", card: true },
      { key: "bmi", label: "BMI", type: "number" },
      {
        key: "head_circumference_cm",
        label: "Head Circ. (cm)",
        type: "number",
      },
      { key: "blood_pressure_systolic", label: "BP Systolic", type: "number" },
      {
        key: "blood_pressure_diastolic",
        label: "BP Diastolic",
        type: "number",
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      { key: "recorded_by", label: "Recorded By (User ID)" },
      { key: "recorded_by_name", label: "Recorded By", skipForm: true },
    ],
  },
  "vital-signs": {
    key: "vital-signs",
    label: "Vital Signs",
    icon: SignalIcon,
    endpoint: "vital-signs",
    titleField: "student_name",
    subtitleField: "recorded_date",
    searchKeys: ["student_name", "recorded_by_name"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "recorded_date", label: "Date", type: "date", card: true },
      { key: "recorded_time", label: "Time" },
      { key: "temperature", label: "Temperature", type: "number", card: true },
      { key: "heart_rate", label: "Heart Rate", type: "number", card: true },
      { key: "respiratory_rate", label: "Respiratory Rate", type: "number" },
      { key: "blood_pressure_systolic", label: "BP Systolic", type: "number" },
      {
        key: "blood_pressure_diastolic",
        label: "BP Diastolic",
        type: "number",
      },
      { key: "oxygen_saturation", label: "O₂ Saturation", type: "number" },
      { key: "blood_glucose", label: "Blood Glucose", type: "number" },
      { key: "pain_scale", label: "Pain Scale", type: "number" },
      { key: "recorded_by", label: "Recorded By (User ID)" },
      { key: "recorded_by_name", label: "Recorded By", skipForm: true },
    ],
  },
  "dental-record": {
    key: "dental-record",
    label: "Dental Records",
    icon: SparklesIcon,
    endpoint: "dental-record",
    titleField: "student_name",
    subtitleField: "dentist_name",
    searchKeys: ["student_name", "dentist_name", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "visit_date", label: "Visit Date", type: "date", card: true },
      { key: "dentist_name", label: "Dentist", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: DENTAL_STATUS,
        badge: true,
      },
      {
        key: "examination_findings",
        label: "Findings",
        type: "textarea",
        full: true,
      },
      { key: "cavities_count", label: "Cavities", type: "number" },
      { key: "gum_health", label: "Gum Health" },
      {
        key: "treatment_provided",
        label: "Treatment",
        type: "textarea",
        full: true,
      },
      {
        key: "prescriptions",
        label: "Prescriptions",
        type: "textarea",
        full: true,
      },
      { key: "next_checkup_date", label: "Next Checkup", type: "date" },
      { key: "xray_url", label: "X-Ray URL", full: true },
    ],
  },
  "vision-record": {
    key: "vision-record",
    label: "Vision Records",
    icon: EyeIcon,
    endpoint: "vision-record",
    titleField: "student_name",
    subtitleField: "result",
    searchKeys: ["student_name", "result"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "screening_date",
        label: "Screening Date",
        type: "date",
        card: true,
      },
      {
        key: "result",
        label: "Result",
        type: "select",
        options: VISION_RESULTS,
        badge: true,
      },
      { key: "left_eye_vision", label: "Left Eye", card: true },
      { key: "right_eye_vision", label: "Right Eye", card: true },
      { key: "color_blindness", label: "Color Blindness", type: "bool" },
      { key: "glasses_prescribed", label: "Glasses Prescribed", type: "bool" },
      {
        key: "prescription_details",
        label: "Prescription Details",
        type: "textarea",
        full: true,
      },
      {
        key: "specialist_referral",
        label: "Specialist Referral",
        type: "bool",
      },
      {
        key: "referral_details",
        label: "Referral Details",
        type: "textarea",
        full: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "lab-result": {
    key: "lab-result",
    label: "Lab Results",
    icon: BeakerIcon,
    endpoint: "lab-result",
    titleField: "test_name",
    subtitleField: "student_name",
    searchKeys: ["test_name", "student_name", "status", "lab_name"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "test_name", label: "Test", main: true },
      { key: "test_date", label: "Test Date", type: "date", card: true },
      { key: "result_date", label: "Result Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: LAB_STATUS,
        badge: true,
      },
      { key: "result_value", label: "Result Value", card: true },
      { key: "normal_range", label: "Normal Range" },
      { key: "is_abnormal", label: "Abnormal", type: "bool" },
      { key: "lab_name", label: "Lab" },
      { key: "ordered_by", label: "Ordered By (User ID)" },
      { key: "ordered_by_name", label: "Ordered By", skipForm: true },
    ],
  },
  alerts: {
    key: "alerts",
    label: "Health Alerts",
    icon: BellAlertIcon,
    endpoint: "alerts",
    titleField: "student_name",
    subtitleField: "alert_type",
    toggleField: "is_active",
    searchKeys: ["student_name", "alert_type", "alert_message"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "alert_type",
        label: "Alert Type",
        type: "select",
        options: ALERT_TYPES,
        badge: true,
      },
      { key: "urgency_level", label: "Urgency", badge: true, skipForm: true },
      { key: "alert_message", label: "Message", type: "textarea", full: true },
      {
        key: "emergency_instructions",
        label: "Emergency Instructions",
        type: "textarea",
        full: true,
      },
      { key: "medication_name", label: "Medication", card: true },
      { key: "medication_location", label: "Medication Location" },
      { key: "emergency_contact_name", label: "Emergency Contact", card: true },
      { key: "emergency_contact_phone", label: "Emergency Phone" },
      { key: "is_active", label: "Active", type: "bool" },
    ],
  },
  incidents: {
    key: "incidents",
    label: "Incidents",
    icon: ExclamationTriangleIcon,
    endpoint: "incidents",
    titleField: "student_name",
    subtitleField: "incident_type",
    searchKeys: ["student_name", "incident_type", "severity", "location"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "incident_type",
        label: "Type",
        type: "select",
        options: INCIDENT_TYPES,
        badge: true,
      },
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: INCIDENT_SEVERITY,
        badge: true,
      },
      { key: "incident_date", label: "Date", type: "datetime", card: true },
      { key: "location", label: "Location", card: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "action_taken",
        label: "Action Taken",
        type: "select",
        options: ACTIONS_TAKEN,
      },
      {
        key: "action_details",
        label: "Action Details",
        type: "textarea",
        full: true,
      },
      { key: "reported_by", label: "Reported By (User ID)" },
      { key: "reported_by_name", label: "Reported By", skipForm: true },
      { key: "witnessed_by", label: "Witnessed By" },
    ],
  },
  referrals: {
    key: "referrals",
    label: "Medical Referrals",
    icon: TicketIcon,
    endpoint: "referrals",
    titleField: "student_name",
    subtitleField: "referral_reason",
    searchKeys: ["student_name", "referral_reason", "status", "provider_name"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "referral_reason",
        label: "Reason",
        type: "select",
        options: REFERRAL_REASONS,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: REFERRAL_STATUS,
        badge: true,
      },
      { key: "provider_name", label: "Provider", card: true },
      { key: "provider_phone", label: "Provider Phone" },
      { key: "provider_address", label: "Provider Address", full: true },
      {
        key: "reason_for_referral",
        label: "Reason Details",
        type: "textarea",
        full: true,
      },
      { key: "urgency", label: "Urgency" },
      { key: "referral_date", label: "Referred", type: "date" },
      {
        key: "appointment_date",
        label: "Appointment",
        type: "date",
        card: true,
      },
      { key: "completed_date", label: "Completed", type: "date" },
    ],
  },
  "mental-health-record": {
    key: "mental-health-record",
    label: "Mental Health",
    icon: CloudIcon,
    endpoint: "mental-health-record",
    titleField: "student_name",
    subtitleField: "session_type",
    searchKeys: ["student_name", "session_type", "provider_name"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "session_type",
        label: "Session Type",
        type: "select",
        options: SESSION_TYPES,
        badge: true,
      },
      { key: "session_date", label: "Session Date", type: "date", card: true },
      { key: "provider", label: "Provider (User ID)" },
      { key: "provider_name", label: "Provider", skipForm: true },
      {
        key: "presenting_issue",
        label: "Presenting Issue",
        type: "textarea",
        full: true,
      },
      {
        key: "assessment_findings",
        label: "Assessment Findings",
        type: "textarea",
        full: true,
      },
      { key: "diagnosis", label: "Diagnosis", type: "textarea", full: true },
      {
        key: "treatment_plan",
        label: "Treatment Plan",
        type: "textarea",
        full: true,
      },
      {
        key: "interventions",
        label: "Interventions",
        type: "textarea",
        full: true,
      },
      {
        key: "progress_notes",
        label: "Progress Notes",
        type: "textarea",
        full: true,
      },
    ],
  },
  education: {
    key: "education",
    label: "Health Education",
    icon: AcademicCapIcon,
    endpoint: "education",
    titleField: "title",
    subtitleField: "resource_type",
    searchKeys: ["title", "resource_type", "topic_category", "created_by_name"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "resource_type",
        label: "Resource Type",
        type: "select",
        options: RESOURCE_TYPES,
        badge: true,
      },
      {
        key: "topic_category",
        label: "Topic",
        type: "select",
        options: TOPIC_CATEGORIES,
      },
      { key: "content_url", label: "Content URL", full: true },
      { key: "file_url", label: "File URL", full: true },
      { key: "content_text", label: "Content", type: "textarea", full: true },
      { key: "target_grades", label: "Target Grades", card: true },
      { key: "is_required", label: "Required", type: "bool" },
      { key: "created_by", label: "Created By (User ID)", skipForm: true },
      { key: "created_by_name", label: "Created By", skipForm: true },
    ],
  },
  "health-education-material": {
    key: "health-education-material",
    label: "Education Materials",
    icon: QueueListIcon,
    endpoint: "health-education-material",
    titleField: "title",
    subtitleField: "material_type",
    toggleField: "is_active",
    searchKeys: ["title", "material_type", "topic", "target_audience"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "material_type",
        label: "Type",
        type: "select",
        options: MATERIAL_TYPES,
        badge: true,
      },
      { key: "topic", label: "Topic", card: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "content", label: "Content", type: "textarea", full: true },
      { key: "file_url", label: "File URL", full: true },
      { key: "target_audience", label: "Target Audience", card: true },
      { key: "is_active", label: "Active", type: "bool" },
    ],
  },
  "health-campaign": {
    key: "health-campaign",
    label: "Health Campaigns",
    icon: GiftIcon,
    endpoint: "health-campaign",
    titleField: "name",
    subtitleField: "status",
    searchKeys: ["name", "campaign_type", "status", "target_audience"],
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "campaign_type", label: "Campaign Type" },
      { key: "start_date", label: "Start Date", type: "date", card: true },
      { key: "end_date", label: "End Date", type: "date", card: true },
      { key: "target_audience", label: "Target Audience" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CAMPAIGN_STATUS,
        badge: true,
      },
      { key: "budget", label: "Budget", type: "number" },
      {
        key: "participants_count",
        label: "Participants",
        skipForm: true,
        card: true,
      },
      { key: "materials", label: "Materials", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "health-survey": {
    key: "health-survey",
    label: "Health Surveys",
    icon: EnvelopeIcon,
    endpoint: "health-survey",
    titleField: "title",
    subtitleField: "status",
    searchKeys: ["title", "status", "target_audience"],
    fields: [
      { key: "title", label: "Title", main: true },
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
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: SURVEY_STATUS,
        badge: true,
      },
      { key: "is_anonymous", label: "Anonymous", type: "bool" },
      { key: "response_count", label: "Responses", skipForm: true, card: true },
    ],
  },
  notifications: {
    key: "notifications",
    label: "Parent Notifications",
    icon: BellAlertIcon,
    endpoint: "notifications",
    titleField: "subject",
    subtitleField: "student_name",
    searchKeys: ["subject", "student_name", "notification_type", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "notification_type",
        label: "Type",
        type: "select",
        options: NOTIF_TYPES,
        badge: true,
      },
      {
        key: "delivery_method",
        label: "Delivery",
        type: "select",
        options: DELIVERY_METHODS,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: NOTIF_STATUS,
        badge: true,
      },
      { key: "subject", label: "Subject", main: true },
      { key: "message", label: "Message", type: "textarea", full: true },
      { key: "nurse_visit", label: "Nurse Visit (ID)" },
      { key: "medication_log", label: "Medication Log (ID)" },
      {
        key: "sent_at",
        label: "Sent At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "nurse-schedule": {
    key: "nurse-schedule",
    label: "Nurse Schedules",
    icon: CalendarDaysIcon,
    endpoint: "nurse-schedule",
    titleField: "nurse_name",
    subtitleField: "shift_type",
    toggleField: "is_available",
    searchKeys: ["nurse_name", "shift_type", "location"],
    fields: [
      { key: "nurse", label: "Nurse (User ID)", full: true },
      { key: "nurse_name", label: "Nurse", skipForm: true },
      { key: "day_of_week", label: "Day (0-6)", type: "number", card: true },
      {
        key: "shift_type",
        label: "Shift",
        type: "select",
        options: SHIFTS,
        badge: true,
      },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      { key: "is_available", label: "Available", type: "bool" },
      { key: "location", label: "Location", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      { key: "is_recurring", label: "Recurring", type: "bool" },
      { key: "effective_from", label: "Effective From", type: "date" },
      { key: "effective_until", label: "Effective Until", type: "date" },
    ],
  },
  telehealth: {
    key: "telehealth",
    label: "Telehealth",
    icon: VideoCameraIcon,
    endpoint: "telehealth",
    titleField: "student_name",
    subtitleField: "session_type",
    searchKeys: ["student_name", "session_type", "status", "healthcare_provider"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "session_type",
        label: "Type",
        type: "select",
        options: TELEHEALTH_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: TELEHEALTH_STATUS,
        badge: true,
      },
      { key: "scheduled_date", label: "Date", type: "date", card: true },
      { key: "scheduled_time", label: "Time" },
      { key: "duration_minutes", label: "Duration (min)", type: "number" },
      { key: "meeting_link", label: "Meeting Link", full: true },
      { key: "meeting_id", label: "Meeting ID" },
      { key: "meeting_password", label: "Meeting Password" },
      { key: "healthcare_provider", label: "Provider", card: true },
    ],
  },
  reports: {
    key: "reports",
    label: "Health Reports",
    icon: MapPinIcon,
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
        options: REPORT_STATUS,
        badge: true,
      },
      { key: "period_start", label: "Period Start", type: "date", card: true },
      { key: "period_end", label: "Period End", type: "date", card: true },
      { key: "summary", label: "Summary", type: "textarea", full: true },
      { key: "findings", label: "Findings", type: "textarea", full: true },
      {
        key: "recommendations",
        label: "Recommendations",
        type: "textarea",
        full: true,
      },
      { key: "total_students", label: "Students", type: "number" },
      { key: "total_visits", label: "Visits", type: "number" },
      { key: "total_incidents", label: "Incidents", type: "number" },
      { key: "generated_by", label: "Generated By (User ID)", skipForm: true },
      { key: "generated_by_name", label: "Generated By", skipForm: true },
    ],
  },
  "vaccination-schedule": {
    key: "vaccination-schedule",
    label: "Vaccination Schedule",
    icon: ArrowPathIcon,
    endpoint: "vaccination-schedule",
    titleField: "vaccine_name",
    subtitleField: "student_name",
    searchKeys: ["vaccine_name", "student_name", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "vaccine_name", label: "Vaccine", main: true },
      { key: "dose_number", label: "Dose Number", type: "number" },
      { key: "due_date", label: "Due Date", type: "date", card: true },
      { key: "completed_date", label: "Completed", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: VACC_STATUS,
        badge: true,
      },
      { key: "administered_by", label: "Administered By" },
      { key: "batch_number", label: "Batch Number" },
      { key: "site_of_administration", label: "Site" },
      { key: "reactions", label: "Reactions", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "health-assessment": {
    key: "health-assessment",
    label: "Health Assessments",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "health-assessment",
    titleField: "student_name",
    subtitleField: "assessment_type",
    searchKeys: ["student_name", "assessment_type", "assessed_by_name"],
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
      { key: "assessment_date", label: "Date", type: "date", card: true },
      { key: "assessed_by", label: "Assessed By (User ID)" },
      { key: "assessed_by_name", label: "Assessed By", skipForm: true },
      { key: "general_health", label: "General Health" },
      {
        key: "immunizations_current",
        label: "Immunizations Current",
        type: "bool",
      },
      { key: "allergies_checked", label: "Allergies Checked", type: "bool" },
      {
        key: "medications_checked",
        label: "Medications Checked",
        type: "bool",
      },
      { key: "vision_screened", label: "Vision Screened", type: "bool" },
      { key: "hearing_screened", label: "Hearing Screened", type: "bool" },
    ],
  },
  "health-risk-assessment": {
    key: "health-risk-assessment",
    label: "Risk Assessments",
    icon: GlobeAltIcon,
    endpoint: "health-risk-assessment",
    titleField: "student_name",
    subtitleField: "risk_level",
    searchKeys: ["student_name", "risk_level", "assessed_by_name"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "assessment_date", label: "Date", type: "date", card: true },
      {
        key: "risk_level",
        label: "Risk Level",
        type: "select",
        options: RISK_LEVELS,
        badge: true,
      },
      {
        key: "risk_factors",
        label: "Risk Factors",
        type: "textarea",
        full: true,
      },
      {
        key: "chronic_conditions",
        label: "Chronic Conditions",
        type: "textarea",
        full: true,
      },
      {
        key: "family_history_risks",
        label: "Family History Risks",
        type: "textarea",
        full: true,
      },
      {
        key: "lifestyle_factors",
        label: "Lifestyle Factors",
        type: "textarea",
        full: true,
      },
      {
        key: "environmental_factors",
        label: "Environmental Factors",
        type: "textarea",
        full: true,
      },
      {
        key: "mitigation_plan",
        label: "Mitigation Plan",
        type: "textarea",
        full: true,
      },
      { key: "assessed_by", label: "Assessed By (User ID)" },
      { key: "assessed_by_name", label: "Assessed By", skipForm: true },
    ],
  },
  "medical-equipment": {
    key: "medical-equipment",
    label: "Medical Equipment",
    icon: CubeIcon,
    endpoint: "medical-equipment",
    titleField: "name",
    subtitleField: "equipment_type",
    searchKeys: ["name", "equipment_type", "model_name", "serial_number", "status", "location"],
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "equipment_type", label: "Type", card: true },
      { key: "model_name", label: "Model" },
      { key: "serial_number", label: "Serial Number", card: true },
      { key: "purchase_date", label: "Purchased", type: "date" },
      { key: "purchase_cost", label: "Cost", type: "number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: EQUIPMENT_STATUS,
        badge: true,
      },
      { key: "location", label: "Location" },
      { key: "last_calibration_date", label: "Last Calibration", type: "date" },
      { key: "next_calibration_date", label: "Next Calibration", type: "date" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "equipment-maintenance": {
    key: "equipment-maintenance",
    label: "Equipment Maintenance",
    icon: WrenchScrewdriverIcon,
    endpoint: "equipment-maintenance",
    titleField: "equipment_name",
    subtitleField: "maintenance_type",
    searchKeys: ["equipment_name", "maintenance_type", "performed_by"],
    fields: [
      { key: "equipment", label: "Equipment (ID)", full: true },
      { key: "equipment_name", label: "Equipment", skipForm: true },
      {
        key: "maintenance_type",
        label: "Type",
        type: "select",
        options: MAINTENANCE_TYPES,
        badge: true,
      },
      { key: "maintenance_date", label: "Date", type: "date", card: true },
      { key: "next_due_date", label: "Next Due", type: "date", card: true },
      { key: "cost", label: "Cost", type: "number" },
      { key: "performed_by", label: "Performed By" },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "health-staff-training": {
    key: "health-staff-training",
    label: "Staff Training",
    icon: BuildingOffice2Icon,
    endpoint: "health-staff-training",
    titleField: "training_name",
    subtitleField: "staff_member_name",
    toggleField: "is_completed",
    searchKeys: ["training_name", "staff_member_name", "training_type", "provider"],
    fields: [
      { key: "staff_member", label: "Staff Member (User ID)", full: true },
      { key: "staff_member_name", label: "Staff Member", skipForm: true },
      { key: "training_name", label: "Training", main: true },
      { key: "training_type", label: "Type", card: true },
      { key: "provider", label: "Provider", card: true },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "hours", label: "Hours", type: "number" },
      { key: "certificate_url", label: "Certificate URL", full: true },
      { key: "expiry_date", label: "Expires", type: "date" },
      { key: "is_completed", label: "Completed", type: "bool" },
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

export default function HealthPage() {
  useTitle("Health Center");
  const [activeTab, setActiveTab] = useState("records");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Health Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Records, visits, screenings, medications, alerts, telehealth, compliance and audits
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
        basePath="/health"
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
          {
            keys: ["P"],
            label: "View Mode",
            description: "Toggle pagination / infinite scroll",
          },
          {
            keys: ["?"],
            label: "Help",
            description: "Show this shortcut help",
          },
        ]}
      />
    </div>
  );
}
