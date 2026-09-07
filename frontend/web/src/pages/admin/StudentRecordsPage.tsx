/**
 * Student Records — full-surface admin page for the students module.
 *
 * 47 entity tabs (config-driven via EntitySection): classrooms, grades,
 * academic years, guardians, contacts, medical records, custom fields,
 * photos, ID cards, status history, siblings, categories, tags, notes,
 * archive, social media, portfolio, wellness, guardian links, enrollment,
 * parent profiles, documents, learning styles, achievements, clubs,
 * activities, awards, discipline, tutoring, mentoring, career guidance,
 * parent communication, academic advising, transfers, graduation,
 * volunteering, internships, scholarships, financial aid, transport
 * assignments, meal plans, parking, ID activity and feedback.
 *
 * The core student list lives on StudentsPage (with detail navigation);
 * this page covers every supporting record type around the student.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, UsersIcon } from "@heroicons/react/24/outline";
import {
  UserGroupIcon,
  ClipboardDocumentListIcon,
  ClipboardDocumentCheckIcon,
  HeartIcon,
  AdjustmentsHorizontalIcon,
  PhotoIcon,
  IdentificationIcon,
  ArrowPathIcon,
  UserPlusIcon,
  TagIcon,
  DocumentTextIcon,
  ArchiveBoxIcon,
  GlobeAltIcon,
  BriefcaseIcon,
  ChatBubbleLeftRightIcon,
  AcademicCapIcon,
  ArrowsRightLeftIcon,
  CheckBadgeIcon,
  HandRaisedIcon,
  TruckIcon,
  MapPinIcon,
  ClockIcon,
  ReceiptPercentIcon,
  BanknotesIcon,
  ScaleIcon,
  LifebuoyIcon,
  BellAlertIcon,
  SignalIcon,
  FireIcon,
  ListBulletIcon,
  QueueListIcon,
  CalendarDaysIcon,
  ShieldCheckIcon,
  StarIcon,
  PresentationChartBarIcon,
  EnvelopeIcon,
  BeakerIcon,
  ComputerDesktopIcon,
  WrenchScrewdriverIcon,
  TrophyIcon,
  BuildingOffice2Icon,
  PencilIcon,
  BookOpenIcon,
  GiftIcon,
  KeyIcon,
  CameraIcon,
  QuestionMarkCircleIcon,
  MusicalNoteIcon,
  UserCircleIcon,
  Square3Stack3DIcon,
  CurrencyDollarIcon,
  PhoneIcon,
} from "@heroicons/react/24/outline";

// ─── Shared option sets ──────────────────────────────────────────────────────

const ENROLL_STATUS = [
  ["active", "Active"],
  ["transferred", "Transferred"],
  ["graduated", "Graduated"],
  ["withdrawn", "Withdrawn"],
  ["suspended", "Suspended"],
] as [string, string][];

const ARCHIVE_STATUS = [
  ["active", "Active"],
  ["inactive", "Inactive"],
  ["graduated", "Graduated"],
  ["withdrawn", "Withdrawn"],
  ["suspended", "Suspended"],
  ["transferred", "Transferred"],
] as [string, string][];

const STATUS_HISTORY = [
  ["active", "Active"],
  ["inactive", "Inactive"],
  ["graduated", "Graduated"],
  ["withdrawn", "Withdrawn"],
  ["suspended", "Suspended"],
  ["transferred", "Transferred"],
  ["expelled", "Expelled"],
  ["deceased", "Deceased"],
] as [string, string][];

const RELATIONSHIP = [
  ["father", "Father"],
  ["mother", "Mother"],
  ["guardian", "Guardian"],
  ["sibling", "Sibling"],
  ["other", "Other"],
] as [string, string][];

const SIBLING_REL = [
  ["sibling", "Sibling"],
  ["twin", "Twin"],
  ["step_sibling", "Step Sibling"],
] as [string, string][];

const DOC_TYPE = [
  ["birth_cert", "Birth Certificate"],
  ["id_card", "ID Card"],
  ["transfer_cert", "Transfer Certificate"],
  ["medical", "Medical"],
  ["report_card", "Report Card"],
  ["other", "Other"],
] as [string, string][];

const MED_TYPE = [
  ["allergy", "Allergy"],
  ["condition", "Condition"],
  ["medication", "Medication"],
  ["immunization", "Immunization"],
  ["visit", "Visit"],
  ["other", "Other"],
] as [string, string][];

const MED_SEVERITY = [
  ["mild", "Mild"],
  ["moderate", "Moderate"],
  ["severe", "Severe"],
  ["life_threatening", "Life-Threatening"],
] as [string, string][];

const FIELD_TYPE = [
  ["text", "Text"],
  ["number", "Number"],
  ["date", "Date"],
  ["boolean", "Boolean"],
  ["select", "Select"],
  ["multi_select", "Multi Select"],
  ["url", "URL"],
  ["email", "Email"],
] as [string, string][];

const PHOTO_TYPE = [
  ["profile", "Profile"],
  ["id_photo", "ID Photo"],
  ["class_photo", "Class Photo"],
  ["event", "Event"],
  ["other", "Other"],
] as [string, string][];

const ID_CARD_STATUS = [
  ["active", "Active"],
  ["expired", "Expired"],
  ["lost", "Lost"],
  ["replaced", "Replaced"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const ACHIEVEMENT_TYPE = [
  ["academic", "Academic"],
  ["sports", "Sports"],
  ["arts", "Arts"],
  ["leadership", "Leadership"],
  ["service", "Service"],
  ["other", "Other"],
] as [string, string][];

const ACTIVITY_TYPE = [
  ["sports", "Sports"],
  ["arts", "Arts"],
  ["music", "Music"],
  ["drama", "Drama"],
  ["debate", "Debate"],
  ["science", "Science"],
  ["coding", "Coding"],
  ["other", "Other"],
] as [string, string][];

const AWARD_LEVEL = [
  ["classroom", "Classroom"],
  ["school", "School"],
  ["district", "District"],
  ["state", "State"],
  ["national", "National"],
  ["international", "International"],
] as [string, string][];

const ACTION_TYPE = [
  ["warning", "Warning"],
  ["detention", "Detention"],
  ["suspension", "Suspension"],
  ["expulsion", "Expulsion"],
  ["counseling", "Counseling"],
  ["community_service", "Community Service"],
  ["other", "Other"],
] as [string, string][];

const SEVERITY = [
  ["minor", "Minor"],
  ["moderate", "Moderate"],
  ["major", "Major"],
  ["critical", "Critical"],
] as [string, string][];

const TUTOR_STATUS = [
  ["scheduled", "Scheduled"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const MENTOR_STATUS = [
  ["active", "Active"],
  ["completed", "Completed"],
  ["paused", "Paused"],
] as [string, string][];

const ADVISOR_STATUS = [
  ["active", "Active"],
  ["completed", "Completed"],
  ["pending", "Pending"],
] as [string, string][];

const CAREER_INTEREST = [
  ["stem", "STEM"],
  ["business", "Business"],
  ["arts", "Arts"],
  ["healthcare", "Healthcare"],
  ["education", "Education"],
  ["law", "Law"],
  ["engineering", "Engineering"],
  ["other", "Other"],
] as [string, string][];

const COMM_TYPE = [
  ["meeting", "Meeting"],
  ["phone_call", "Phone Call"],
  ["email", "Email"],
  ["note", "Note"],
  ["conference", "Conference"],
  ["other", "Other"],
] as [string, string][];

const TRANSFER_TYPE = [
  ["incoming", "Incoming"],
  ["outgoing", "Outgoing"],
  ["internal", "Internal"],
] as [string, string][];

const TRANSFER_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["completed", "Completed"],
  ["rejected", "Rejected"],
] as [string, string][];

const GRAD_STATUS = [
  ["on_track", "On Track"],
  ["at_risk", "At Risk"],
  ["graduated", "Graduated"],
  ["not_graduated", "Not Graduated"],
] as [string, string][];

const INTERNSHIP_STATUS = [
  ["planned", "Planned"],
  ["active", "Active"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const SCHOLARSHIP_STATUS = [
  ["applied", "Applied"],
  ["pending", "Pending"],
  ["awarded", "Awarded"],
  ["declined", "Declined"],
  ["expired", "Expired"],
] as [string, string][];

const AID_TYPE = [
  ["grant", "Grant"],
  ["loan", "Loan"],
  ["work_study", "Work Study"],
  ["waiver", "Waiver"],
  ["other", "Other"],
] as [string, string][];

const AID_STATUS = [
  ["applied", "Applied"],
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["denied", "Denied"],
  ["disbursed", "Disbursed"],
] as [string, string][];

const SERVICE_TYPE = [
  ["pickup", "Pickup"],
  ["dropoff", "Dropoff"],
  ["both", "Both"],
] as [string, string][];

const MEAL_TYPE = [
  ["full", "Full"],
  ["lunch", "Lunch"],
  ["breakfast", "Breakfast"],
  ["partial", "Partial"],
] as [string, string][];

const MEAL_STATUS = [
  ["active", "Active"],
  ["expired", "Expired"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const PERMIT_TYPE = [
  ["student", "Student"],
  ["staff", "Staff"],
  ["visitor", "Visitor"],
  ["handicap", "Handicap"],
] as [string, string][];

const PARKING_STATUS = [
  ["active", "Active"],
  ["expired", "Expired"],
  ["suspended", "Suspended"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const ID_ACTIVITY = [
  ["entry", "Entry"],
  ["exit", "Exit"],
  ["library", "Library"],
  ["cafeteria", "Cafeteria"],
  ["lab", "Lab"],
  ["other", "Other"],
] as [string, string][];

const FEEDBACK_TYPE = [
  ["course", "Course"],
  ["teacher", "Teacher"],
  ["facility", "Facility"],
  ["service", "Service"],
  ["general", "General"],
] as [string, string][];

const NOTE_TYPE = [
  ["general", "General"],
  ["academic", "Academic"],
  ["behavior", "Behavior"],
  ["medical", "Medical"],
  ["pastoral", "Pastoral"],
  ["confidential", "Confidential"],
] as [string, string][];

const LEARNING_STYLE = [
  ["visual", "Visual"],
  ["auditory", "Auditory"],
  ["kinesthetic", "Kinesthetic"],
  ["reading", "Reading"],
  ["multimodal", "Multimodal"],
] as [string, string][];

const WELLNESS_TYPE = [
  ["check_in", "Check-In"],
  ["assessment", "Assessment"],
  ["counseling", "Counseling"],
  ["incident", "Incident"],
  ["other", "Other"],
] as [string, string][];

const WELLNESS_STATUS = [
  ["normal", "Normal"],
  ["attention", "Attention"],
  ["concern", "Concern"],
  ["urgent", "Urgent"],
] as [string, string][];

const CLUB_ROLE = [
  ["member", "Member"],
  ["president", "President"],
  ["vice_president", "Vice President"],
  ["secretary", "Secretary"],
  ["treasurer", "Treasurer"],
  ["advisor", "Advisor"],
] as [string, string][];

const PLATFORM = [
  ["facebook", "Facebook"],
  ["twitter", "Twitter"],
  ["instagram", "Instagram"],
  ["linkedin", "LinkedIn"],
  ["youtube", "YouTube"],
  ["other", "Other"],
] as [string, string][];

const PORTFOLIO_TYPE = [
  ["academic", "Academic"],
  ["creative", "Creative"],
  ["project", "Project"],
  ["presentation", "Presentation"],
  ["certificate", "Certificate"],
  ["other", "Other"],
] as [string, string][];

const STUDENT_ID = (full = true) => ({
  key: "student",
  label: "Student (ID)",
  full,
});
const STUDENT_NAME = { key: "student_name", label: "Student", skipForm: true };

// ─── Entity configs ──────────────────────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  classrooms: {
    key: "classrooms",
    label: "Classrooms",
    icon: BuildingOffice2Icon,
    endpoint: "classrooms",
    titleField: "name",
    searchKeys: ["name", "room_number"],
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "grade", label: "Grade (ID)", full: true },
      { key: "capacity", label: "Capacity", type: "number", card: true },
      { key: "room_number", label: "Room #", card: true },
      { key: "class_teacher", label: "Class Teacher (ID)", full: true },
      { key: "academic_year", label: "Academic Year (ID)", full: true },
    ],
  },
  grades: {
    key: "grades",
    label: "Grades",
    icon: ListBulletIcon,
    endpoint: "grades",
    titleField: "name",
    subtitleField: "level",
    searchKeys: ["name", "description"],
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "level", label: "Level", type: "number", card: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
    ],
  },
  academicYears: {
    key: "academicYears",
    label: "Academic Years",
    icon: CalendarDaysIcon,
    endpoint: "academic-years",
    titleField: "name",
    searchKeys: ["name"],
    toggleField: "is_current",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "is_current", label: "Current", type: "bool" },
    ],
  },
  guardians: {
    key: "guardians",
    label: "Guardians",
    icon: UserGroupIcon,
    endpoint: "guardians",
    titleField: "first_name",
    subtitleField: "last_name",
    searchKeys: ["first_name", "last_name", "email", "phone"],
    fields: [
      { key: "first_name", label: "First Name", main: true },
      { key: "last_name", label: "Last Name", main: true },
      { key: "user", label: "User (ID)", full: true },
      { key: "email", label: "Email", card: true },
      { key: "phone", label: "Phone", card: true },
      { key: "alternate_phone", label: "Alt Phone" },
      { key: "occupation", label: "Occupation" },
      { key: "annual_income", label: "Annual Income", type: "number" },
      { key: "address", label: "Address", type: "textarea", full: true },
      { key: "is_primary", label: "Primary", type: "bool" },
    ],
  },
  contacts: {
    key: "contacts",
    label: "Contacts",
    icon: PhoneIcon,
    endpoint: "contacts",
    titleField: "student_name",
    searchKeys: ["student_name", "personal_phone", "personal_email"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "personal_phone", label: "Personal Phone", card: true },
      { key: "personal_email", label: "Personal Email", card: true },
      { key: "emergency_contact_1_name", label: "Emergency 1 Name" },
      { key: "emergency_contact_1_phone", label: "Emergency 1 Phone" },
      { key: "emergency_contact_1_relationship", label: "Emergency 1 Rel." },
      { key: "emergency_contact_2_name", label: "Emergency 2 Name" },
      { key: "emergency_contact_2_phone", label: "Emergency 2 Phone" },
      { key: "emergency_contact_2_relationship", label: "Emergency 2 Rel." },
      { key: "medical_emergency_contact", label: "Medical Emergency Contact" },
      { key: "medical_emergency_phone", label: "Medical Emergency Phone" },
      { key: "doctor_name", label: "Doctor Name" },
      { key: "doctor_phone", label: "Doctor Phone" },
    ],
  },
  medicalRecords: {
    key: "medicalRecords",
    label: "Medical Records",
    icon: HeartIcon,
    endpoint: "medical-records",
    titleField: "title",
    subtitleField: "record_type",
    searchKeys: ["title", "student_name", "doctor_name", "description"],
    fields: [
      { key: "title", label: "Title", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "record_type",
        label: "Type",
        type: "select",
        options: MED_TYPE,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: MED_SEVERITY,
        badge: true,
      },
      { key: "date_recorded", label: "Recorded", type: "date", card: true },
      { key: "date_of_visit", label: "Visit Date", type: "date" },
      { key: "doctor_name", label: "Doctor" },
      { key: "hospital_name", label: "Hospital" },
      {
        key: "treatment_notes",
        label: "Treatment Notes",
        type: "textarea",
        full: true,
      },
      {
        key: "medication_details",
        label: "Medications",
        type: "textarea",
        full: true,
      },
      { key: "document_url", label: "Document URL", full: true },
      { key: "is_ongoing", label: "Ongoing", type: "bool" },
    ],
  },
  customFields: {
    key: "customFields",
    label: "Custom Fields",
    icon: AdjustmentsHorizontalIcon,
    endpoint: "custom-fields",
    titleField: "name",
    subtitleField: "field_type",
    searchKeys: ["name", "description"],
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "field_type",
        label: "Type",
        type: "select",
        options: FIELD_TYPE,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "options", label: "Options", full: true },
      { key: "is_required", label: "Required", type: "bool" },
      { key: "is_visible", label: "Visible", type: "bool" },
      { key: "order", label: "Order", type: "number" },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  customFieldValues: {
    key: "customFieldValues",
    label: "Field Values",
    icon: QueueListIcon,
    endpoint: "custom-field-values",
    titleField: "field_name",
    subtitleField: "student_name",
    searchKeys: ["student_name", "field_name", "text_value"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "field", label: "Field (ID)", full: true },
      { key: "field_name", label: "Field", skipForm: true },
      { key: "text_value", label: "Text Value", full: true },
      { key: "number_value", label: "Number Value", type: "number" },
      { key: "date_value", label: "Date Value", type: "date" },
      { key: "boolean_value", label: "Boolean Value", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  photos: {
    key: "photos",
    label: "Photos",
    icon: PhotoIcon,
    endpoint: "photos",
    titleField: "title",
    subtitleField: "photo_type",
    searchKeys: ["title", "student_name", "photographer"],
    fields: [
      { key: "title", label: "Title", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "photo_type",
        label: "Type",
        type: "select",
        options: PHOTO_TYPE,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "photo_url", label: "Photo URL", full: true },
      { key: "thumbnail_url", label: "Thumbnail URL", full: true },
      { key: "taken_date", label: "Taken", type: "date", card: true },
      { key: "photographer", label: "Photographer" },
      { key: "is_primary", label: "Primary", type: "bool" },
      { key: "is_public", label: "Public", type: "bool" },
      { key: "uploaded_by", label: "Uploaded By (ID)", full: true },
    ],
  },
  idCards: {
    key: "idCards",
    label: "ID Cards",
    icon: IdentificationIcon,
    endpoint: "id-cards",
    titleField: "card_number",
    subtitleField: "student_name",
    searchKeys: ["card_number", "student_name", "rfid_number", "status"],
    fields: [
      { key: "card_number", label: "Card #", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "barcode", label: "Barcode" },
      { key: "rfid_number", label: "RFID #" },
      { key: "issue_date", label: "Issued", type: "date", card: true },
      { key: "expiry_date", label: "Expiry", type: "date", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ID_CARD_STATUS,
        badge: true,
      },
      { key: "photo_url", label: "Photo URL", full: true },
      { key: "access_level", label: "Access Level" },
      { key: "issued_by", label: "Issued By (ID)", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  statusHistory: {
    key: "statusHistory",
    label: "Status History",
    icon: ArrowPathIcon,
    endpoint: "status-history",
    titleField: "student_name",
    subtitleField: "status",
    searchKeys: ["student_name", "status", "previous_status", "reason"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "status",
        label: "Status",
        type: "select",
        options: STATUS_HISTORY,
        badge: true,
      },
      {
        key: "previous_status",
        label: "Previous",
        type: "select",
        options: STATUS_HISTORY,
      },
      { key: "effective_date", label: "Effective", type: "date", card: true },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      { key: "document_url", label: "Document URL", full: true },
      { key: "approved_by", label: "Approved By (ID)", full: true },
      { key: "approved_at", label: "Approved At", type: "datetime" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  siblings: {
    key: "siblings",
    label: "Siblings",
    icon: UserPlusIcon,
    endpoint: "siblings",
    titleField: "student_name",
    subtitleField: "sibling_name",
    searchKeys: ["student_name", "sibling_name", "relationship"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "sibling", label: "Sibling (ID)", full: true },
      { key: "sibling_name", label: "Sibling", skipForm: true },
      {
        key: "relationship",
        label: "Relationship",
        type: "select",
        options: SIBLING_REL,
        badge: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  categories: {
    key: "categories",
    label: "Categories",
    icon: TagIcon,
    endpoint: "categories",
    titleField: "name",
    searchKeys: ["name", "description"],
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "color", label: "Color", card: true },
      { key: "student_count", label: "Students", skipForm: true },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  categoryMemberships: {
    key: "categoryMemberships",
    label: "Category Memberships",
    icon: CheckBadgeIcon,
    endpoint: "category-memberships",
    titleField: "category_name",
    subtitleField: "student_name",
    searchKeys: ["student_name", "category_name"],
    toggleField: "is_active",
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "category", label: "Category (ID)", full: true },
      { key: "category_name", label: "Category", skipForm: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date" },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  tags: {
    key: "tags",
    label: "Tags",
    icon: TagIcon,
    endpoint: "tags",
    titleField: "name",
    subtitleField: "color",
    searchKeys: ["name"],
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "color", label: "Color", card: true },
      { key: "usage_count", label: "Uses", skipForm: true },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  tagAssignments: {
    key: "tagAssignments",
    label: "Tag Assignments",
    icon: KeyIcon,
    endpoint: "tag-assignments",
    titleField: "tag_name",
    subtitleField: "student_name",
    searchKeys: ["student_name", "tag_name"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "tag", label: "Tag (ID)", full: true },
      { key: "tag_name", label: "Tag", skipForm: true },
      { key: "assigned_by", label: "Assigned By (ID)", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  notes: {
    key: "notes",
    label: "Notes",
    icon: PencilIcon,
    endpoint: "notes",
    titleField: "title",
    subtitleField: "note_type",
    searchKeys: ["title", "content", "student_name"],
    toggleField: "is_pinned",
    fields: [
      { key: "title", label: "Title", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "note_type",
        label: "Type",
        type: "select",
        options: NOTE_TYPE,
        badge: true,
      },
      { key: "content", label: "Content", type: "textarea", full: true },
      { key: "author", label: "Author (ID)", full: true },
      { key: "is_confidential", label: "Confidential", type: "bool" },
      { key: "is_pinned", label: "Pinned", type: "bool" },
      { key: "notes", label: "Extra Notes", type: "textarea", full: true },
    ],
  },
  archive: {
    key: "archive",
    label: "Archive",
    icon: ArchiveBoxIcon,
    endpoint: "archive",
    titleField: "student_name",
    subtitleField: "status",
    searchKeys: ["student_name", "status", "academic_year"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "academic_year", label: "Academic Year (ID)", full: true },
      { key: "grade", label: "Grade (ID)", full: true },
      { key: "classroom", label: "Classroom (ID)", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ARCHIVE_STATUS,
        badge: true,
      },
      { key: "final_grade", label: "Final Grade", card: true },
      { key: "gpa", label: "GPA", type: "number", card: true },
      { key: "rank_in_class", label: "Class Rank", type: "number" },
    ],
  },
  socialMedia: {
    key: "socialMedia",
    label: "Social Media",
    icon: GlobeAltIcon,
    endpoint: "social-media",
    titleField: "username",
    subtitleField: "platform",
    searchKeys: ["username", "platform", "student_name"],
    toggleField: "is_active",
    fields: [
      { key: "username", label: "Username", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "platform",
        label: "Platform",
        type: "select",
        options: PLATFORM,
        badge: true,
      },
      { key: "profile_url", label: "Profile URL", full: true },
      { key: "is_verified", label: "Verified", type: "bool" },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  portfolio: {
    key: "portfolio",
    label: "Portfolio",
    icon: BriefcaseIcon,
    endpoint: "portfolio",
    titleField: "title",
    subtitleField: "portfolio_type",
    searchKeys: ["title", "student_name", "subject"],
    toggleField: "is_featured",
    fields: [
      { key: "title", label: "Title", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "portfolio_type",
        label: "Type",
        type: "select",
        options: PORTFOLIO_TYPE,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "file_url", label: "File URL", full: true },
      { key: "thumbnail_url", label: "Thumbnail URL", full: true },
      { key: "subject", label: "Subject", card: true },
      { key: "date_completed", label: "Completed", type: "date" },
      { key: "grade_received", label: "Grade", card: true },
      { key: "is_featured", label: "Featured", type: "bool" },
      { key: "is_public", label: "Public", type: "bool" },
    ],
  },
  wellness: {
    key: "wellness",
    label: "Wellness",
    icon: LifebuoyIcon,
    endpoint: "wellness",
    titleField: "title",
    subtitleField: "wellness_type",
    searchKeys: ["title", "student_name", "status", "description"],
    fields: [
      { key: "title", label: "Title", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "wellness_type",
        label: "Type",
        type: "select",
        options: WELLNESS_TYPE,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: WELLNESS_STATUS,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "mood_score", label: "Mood Score", type: "number", card: true },
      { key: "stress_level", label: "Stress Level", type: "number" },
      { key: "recorded_by", label: "Recorded By (ID)", full: true },
      { key: "follow_up_required", label: "Follow-Up Required", type: "bool" },
      { key: "follow_up_date", label: "Follow-Up Date", type: "date" },
    ],
  },
  studentGuardians: {
    key: "studentGuardians",
    label: "Guardian Links",
    icon: UserGroupIcon,
    endpoint: "student-guardian",
    titleField: "student_name",
    subtitleField: "guardian_name",
    searchKeys: ["student_name", "guardian_name", "relationship"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "guardian", label: "Guardian (ID)", full: true },
      { key: "guardian_name", label: "Guardian", skipForm: true },
      {
        key: "relationship",
        label: "Relationship",
        type: "select",
        options: RELATIONSHIP,
        badge: true,
      },
      { key: "is_primary_contact", label: "Primary Contact", type: "bool" },
      {
        key: "has_pickup_permission",
        label: "Pickup Permission",
        type: "bool",
      },
      { key: "portal_access", label: "Portal Access", type: "bool" },
    ],
  },
  enrollment: {
    key: "enrollment",
    label: "Enrollment",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "enrollment",
    titleField: "student_name",
    subtitleField: "classroom_name",
    searchKeys: ["student_name", "classroom_name", "status"],
    toggleField: "is_active",
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "classroom", label: "Classroom (ID)", full: true },
      { key: "classroom_name", label: "Classroom", skipForm: true },
      { key: "academic_year", label: "Academic Year (ID)", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ENROLL_STATUS,
        badge: true,
      },
      { key: "enrollment_date", label: "Enrolled", type: "date", card: true },
      { key: "promoted_from", label: "Promoted From (ID)", full: true },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  parentProfiles: {
    key: "parentProfiles",
    label: "Parent Profiles",
    icon: UserCircleIcon,
    endpoint: "parent-profile",
    titleField: "occupation",
    searchKeys: ["occupation", "emergency_contact_name"],
    fields: [
      { key: "user", label: "User (ID)", full: true },
      { key: "occupation", label: "Occupation", main: true },
      { key: "alternate_phone", label: "Alt Phone" },
      { key: "address", label: "Address", type: "textarea", full: true },
      { key: "emergency_contact_name", label: "Emergency Contact" },
      { key: "emergency_contact_phone", label: "Emergency Phone", card: true },
      { key: "bio", label: "Bio", type: "textarea", full: true },
    ],
  },
  documents: {
    key: "documents",
    label: "Documents",
    icon: DocumentTextIcon,
    endpoint: "document",
    titleField: "title",
    subtitleField: "document_type",
    searchKeys: ["title", "student_name", "document_type"],
    fields: [
      { key: "title", label: "Title", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "document_type",
        label: "Type",
        type: "select",
        options: DOC_TYPE,
        badge: true,
      },
      { key: "file", label: "File", full: true },
      { key: "uploaded_by", label: "Uploaded By (ID)", full: true },
      {
        key: "uploaded_at",
        label: "Uploaded At",
        type: "datetime",
        card: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  learningStyles: {
    key: "learningStyles",
    label: "Learning Styles",
    icon: BeakerIcon,
    endpoint: "student-learning-style",
    titleField: "student_name",
    subtitleField: "primary_style",
    searchKeys: ["student_name", "primary_style", "assessment_tool"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "primary_style",
        label: "Primary",
        type: "select",
        options: LEARNING_STYLE,
        badge: true,
      },
      {
        key: "secondary_style",
        label: "Secondary",
        type: "select",
        options: LEARNING_STYLE,
      },
      { key: "assessment_tool", label: "Assessment Tool" },
      { key: "score_visual", label: "Visual", type: "number" },
      { key: "score_auditory", label: "Auditory", type: "number" },
      { key: "score_kinesthetic", label: "Kinesthetic", type: "number" },
      { key: "score_reading", label: "Reading", type: "number" },
      {
        key: "recommendations",
        label: "Recommendations",
        type: "textarea",
        full: true,
      },
      { key: "assessed_date", label: "Assessed", type: "date", card: true },
      { key: "assessed_by", label: "Assessed By (ID)", full: true },
    ],
  },
  achievements: {
    key: "achievements",
    label: "Achievements",
    icon: TrophyIcon,
    endpoint: "student-achievement",
    titleField: "title",
    subtitleField: "achievement_type",
    searchKeys: ["title", "student_name", "achievement_type"],
    toggleField: "is_public",
    fields: [
      { key: "title", label: "Title", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "achievement_type",
        label: "Type",
        type: "select",
        options: ACHIEVEMENT_TYPE,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "date_earned", label: "Earned", type: "date", card: true },
      { key: "awarded_by", label: "Awarded By (ID)", full: true },
      { key: "certificate_url", label: "Certificate URL", full: true },
      { key: "is_public", label: "Public", type: "bool" },
    ],
  },
  clubs: {
    key: "clubs",
    label: "Clubs",
    icon: MusicalNoteIcon,
    endpoint: "student-club",
    titleField: "club_name",
    subtitleField: "student_name",
    searchKeys: ["club_name", "student_name", "role", "club_type"],
    toggleField: "is_active",
    fields: [
      { key: "club_name", label: "Club", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "club_type", label: "Club Type" },
      {
        key: "role",
        label: "Role",
        type: "select",
        options: CLUB_ROLE,
        badge: true,
      },
      { key: "join_date", label: "Joined", type: "date", card: true },
      { key: "end_date", label: "End", type: "date" },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "advisor", label: "Advisor (ID)", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  activities: {
    key: "activities",
    label: "Activities",
    icon: FireIcon,
    endpoint: "student-activity",
    titleField: "activity_name",
    subtitleField: "activity_type",
    searchKeys: ["activity_name", "student_name", "activity_type"],
    toggleField: "is_active",
    fields: [
      { key: "activity_name", label: "Activity", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "activity_type",
        label: "Type",
        type: "select",
        options: ACTIVITY_TYPE,
        badge: true,
      },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date" },
      { key: "hours_per_week", label: "Hours/Week", type: "number" },
      { key: "total_hours", label: "Total Hours", type: "number", card: true },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "instructor", label: "Instructor" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  awards: {
    key: "awards",
    label: "Awards",
    icon: StarIcon,
    endpoint: "student-award",
    titleField: "award_name",
    subtitleField: "award_level",
    searchKeys: ["award_name", "student_name", "category"],
    fields: [
      { key: "award_name", label: "Award", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "award_level",
        label: "Level",
        type: "select",
        options: AWARD_LEVEL,
        badge: true,
      },
      { key: "category", label: "Category", card: true },
      { key: "date_awarded", label: "Awarded", type: "date", card: true },
      { key: "awarded_by", label: "Awarded By (ID)", full: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "certificate_url", label: "Certificate URL", full: true },
    ],
  },
  discipline: {
    key: "discipline",
    label: "Discipline",
    icon: ScaleIcon,
    endpoint: "student-discipline",
    titleField: "action_type",
    subtitleField: "severity",
    searchKeys: ["student_name", "action_type", "severity", "description"],
    fields: [
      {
        key: "action_type",
        label: "Action",
        type: "select",
        options: ACTION_TYPE,
        badge: true,
        main: true,
      },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: SEVERITY,
        badge: true,
      },
      {
        key: "incident_date",
        label: "Incident Date",
        type: "date",
        card: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "location", label: "Location", card: true },
      { key: "witnesses", label: "Witnesses" },
      {
        key: "action_taken",
        label: "Action Taken",
        type: "textarea",
        full: true,
      },
      { key: "follow_up_required", label: "Follow-Up Required", type: "bool" },
      { key: "follow_up_date", label: "Follow-Up Date", type: "date" },
      { key: "parent_notified", label: "Parent Notified", type: "bool" },
    ],
  },
  tutoring: {
    key: "tutoring",
    label: "Tutoring",
    icon: BookOpenIcon,
    endpoint: "student-tutoring",
    titleField: "student_name",
    subtitleField: "status",
    searchKeys: ["student_name", "subject", "status"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "subject", label: "Subject", main: true },
      { key: "tutor", label: "Tutor (ID)", full: true },
      { key: "session_date", label: "Session Date", type: "date", card: true },
      { key: "start_time", label: "Start Time", card: true },
      { key: "end_time", label: "End Time", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: TUTOR_STATUS,
        badge: true,
      },
      {
        key: "topics_covered",
        label: "Topics Covered",
        type: "textarea",
        full: true,
      },
      {
        key: "homework_assigned",
        label: "Homework Assigned",
        type: "textarea",
        full: true,
      },
    ],
  },
  mentoring: {
    key: "mentoring",
    label: "Mentoring",
    icon: HandRaisedIcon,
    endpoint: "student-mentor",
    titleField: "program_name",
    subtitleField: "status",
    searchKeys: ["program_name", "student_name", "status"],
    fields: [
      { key: "program_name", label: "Program", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "mentor", label: "Mentor (ID)", full: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: MENTOR_STATUS,
        badge: true,
      },
      { key: "goals", label: "Goals", type: "textarea", full: true },
      { key: "meeting_frequency", label: "Meeting Frequency" },
      {
        key: "progress_notes",
        label: "Progress Notes",
        type: "textarea",
        full: true,
      },
      { key: "outcome", label: "Outcome", type: "textarea", full: true },
    ],
  },
  careerGuidance: {
    key: "careerGuidance",
    label: "Career Guidance",
    icon: AcademicCapIcon,
    endpoint: "student-career-guidance",
    titleField: "student_name",
    subtitleField: "career_interest",
    searchKeys: ["student_name", "career_interest", "career_goals"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "career_interest",
        label: "Interest",
        type: "select",
        options: CAREER_INTEREST,
        badge: true,
      },
      {
        key: "career_goals",
        label: "Career Goals",
        type: "textarea",
        full: true,
      },
      { key: "strengths", label: "Strengths", type: "textarea", full: true },
      {
        key: "areas_for_development",
        label: "Development Areas",
        type: "textarea",
        full: true,
      },
      {
        key: "recommended_courses",
        label: "Recommended Courses",
        type: "textarea",
        full: true,
      },
      {
        key: "recommended_activities",
        label: "Recommended Activities",
        type: "textarea",
        full: true,
      },
      { key: "college_preferences", label: "College Preferences", full: true },
      { key: "scholarship_eligibility", label: "Scholarship Eligibility" },
      {
        key: "guidance_date",
        label: "Guidance Date",
        type: "date",
        card: true,
      },
      { key: "guided_by", label: "Guided By (ID)", full: true },
    ],
  },
  parentCommunication: {
    key: "parentCommunication",
    label: "Parent Communication",
    icon: EnvelopeIcon,
    endpoint: "student-parent-communication",
    titleField: "subject",
    subtitleField: "communication_type",
    searchKeys: ["subject", "student_name", "parent_name", "description"],
    fields: [
      { key: "subject", label: "Subject", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "communication_type",
        label: "Type",
        type: "select",
        options: COMM_TYPE,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "communication_date", label: "Date", type: "date", card: true },
      { key: "parent_name", label: "Parent" },
      { key: "parent_phone", label: "Parent Phone" },
      { key: "parent_email", label: "Parent Email" },
      { key: "teacher", label: "Teacher (ID)", full: true },
      { key: "follow_up_required", label: "Follow-Up Required", type: "bool" },
    ],
  },
  academicAdvisors: {
    key: "academicAdvisors",
    label: "Academic Advisors",
    icon: PresentationChartBarIcon,
    endpoint: "student-academic-advisor",
    titleField: "student_name",
    subtitleField: "status",
    searchKeys: ["student_name", "advisor_name", "status"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "advisor", label: "Advisor (ID)", full: true },
      { key: "advisor_name", label: "Advisor", skipForm: true },
      {
        key: "advising_date",
        label: "Advising Date",
        type: "date",
        card: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ADVISOR_STATUS,
        badge: true,
      },
      {
        key: "academic_goals",
        label: "Academic Goals",
        type: "textarea",
        full: true,
      },
      {
        key: "course_recommendations",
        label: "Course Recommendations",
        type: "textarea",
        full: true,
      },
      {
        key: "academic_concerns",
        label: "Academic Concerns",
        type: "textarea",
        full: true,
      },
      {
        key: "action_items",
        label: "Action Items",
        type: "textarea",
        full: true,
      },
      { key: "next_advising_date", label: "Next Advising", type: "date" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  transfers: {
    key: "transfers",
    label: "Transfers",
    icon: ArrowsRightLeftIcon,
    endpoint: "student-transfer",
    titleField: "student_name",
    subtitleField: "transfer_type",
    searchKeys: ["student_name", "transfer_type", "from_school", "to_school", "status"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "transfer_type",
        label: "Type",
        type: "select",
        options: TRANSFER_TYPE,
        badge: true,
      },
      { key: "from_school", label: "From School" },
      { key: "to_school", label: "To School" },
      { key: "from_classroom", label: "From Classroom (ID)", full: true },
      { key: "to_classroom", label: "To Classroom (ID)", full: true },
      {
        key: "transfer_date",
        label: "Transfer Date",
        type: "date",
        card: true,
      },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: TRANSFER_STATUS,
        badge: true,
      },
    ],
  },
  graduation: {
    key: "graduation",
    label: "Graduation",
    icon: CheckBadgeIcon,
    endpoint: "student-graduation",
    titleField: "student_name",
    subtitleField: "status",
    searchKeys: ["student_name", "status", "diploma_type"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "expected_graduation_year",
        label: "Expected Year",
        type: "number",
        card: true,
      },
      { key: "actual_graduation_year", label: "Actual Year", type: "number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: GRAD_STATUS,
        badge: true,
      },
      { key: "credits_earned", label: "Credits Earned", type: "number" },
      { key: "credits_required", label: "Credits Required", type: "number" },
      { key: "gpa", label: "GPA", type: "number", card: true },
      { key: "class_rank", label: "Class Rank", type: "number" },
      { key: "diploma_type", label: "Diploma Type" },
      { key: "honors", label: "Honors", full: true },
      { key: "college_acceptance", label: "College Acceptance", full: true },
    ],
  },
  volunteering: {
    key: "volunteering",
    label: "Volunteering",
    icon: GiftIcon,
    endpoint: "student-volunteer",
    titleField: "organization",
    subtitleField: "student_name",
    searchKeys: ["organization", "student_name", "activity"],
    toggleField: "verified",
    fields: [
      { key: "organization", label: "Organization", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "activity", label: "Activity", card: true },
      { key: "hours", label: "Hours", type: "number", card: true },
      { key: "date_performed", label: "Date", type: "date" },
      { key: "supervisor_name", label: "Supervisor" },
      { key: "supervisor_phone", label: "Supervisor Phone" },
      { key: "supervisor_email", label: "Supervisor Email" },
      { key: "certificate_url", label: "Certificate URL", full: true },
      { key: "verified", label: "Verified", type: "bool" },
      { key: "verified_by", label: "Verified By (ID)", full: true },
    ],
  },
  internships: {
    key: "internships",
    label: "Internships",
    icon: BriefcaseIcon,
    endpoint: "student-internship",
    titleField: "company_name",
    subtitleField: "student_name",
    searchKeys: ["company_name", "student_name", "position", "status"],
    fields: [
      { key: "company_name", label: "Company", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "position", label: "Position", card: true },
      { key: "department", label: "Department" },
      { key: "supervisor_name", label: "Supervisor" },
      { key: "supervisor_email", label: "Supervisor Email" },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: INTERNSHIP_STATUS,
        badge: true,
      },
      { key: "hours_per_week", label: "Hours/Week", type: "number" },
      { key: "is_paid", label: "Paid", type: "bool" },
    ],
  },
  scholarships: {
    key: "scholarships",
    label: "Scholarships",
    icon: CurrencyDollarIcon,
    endpoint: "student-scholarship",
    titleField: "scholarship_name",
    subtitleField: "student_name",
    searchKeys: ["scholarship_name", "student_name", "provider", "status"],
    fields: [
      { key: "scholarship_name", label: "Scholarship", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "provider", label: "Provider", card: true },
      { key: "amount", label: "Amount", type: "number", card: true },
      { key: "scholarship_type", label: "Type" },
      { key: "application_date", label: "Applied", type: "date" },
      { key: "deadline_date", label: "Deadline", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: SCHOLARSHIP_STATUS,
        badge: true,
      },
      { key: "award_date", label: "Award Date", type: "date" },
      { key: "renewal_required", label: "Renewal Required", type: "bool" },
      { key: "renewal_date", label: "Renewal Date", type: "date" },
    ],
  },
  financialAid: {
    key: "financialAid",
    label: "Financial Aid",
    icon: BanknotesIcon,
    endpoint: "student-financial-aid",
    titleField: "aid_name",
    subtitleField: "aid_type",
    searchKeys: ["aid_name", "student_name", "provider", "status"],
    fields: [
      { key: "aid_name", label: "Aid Name", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "aid_type",
        label: "Type",
        type: "select",
        options: AID_TYPE,
        badge: true,
      },
      { key: "amount", label: "Amount", type: "number", card: true },
      { key: "provider", label: "Provider", card: true },
      { key: "application_date", label: "Applied", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: AID_STATUS,
        badge: true,
      },
      { key: "disbursement_date", label: "Disbursed", type: "date" },
      { key: "renewal_required", label: "Renewal Required", type: "bool" },
      {
        key: "academic_requirement",
        label: "Academic Requirement",
        full: true,
      },
      { key: "documents", label: "Documents", full: true },
    ],
  },
  transportAssignments: {
    key: "transportAssignments",
    label: "Transport Assignments",
    icon: TruckIcon,
    endpoint: "student-transport-assignment",
    titleField: "student_name",
    subtitleField: "service_type",
    searchKeys: ["student_name", "pickup_address", "service_type"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "route", label: "Route (ID)", full: true },
      { key: "vehicle", label: "Vehicle (ID)", full: true },
      {
        key: "service_type",
        label: "Service",
        type: "select",
        options: SERVICE_TYPE,
        badge: true,
      },
      {
        key: "pickup_address",
        label: "Pickup Address",
        type: "textarea",
        full: true,
      },
      { key: "pickup_latitude", label: "Latitude", type: "number" },
      { key: "pickup_longitude", label: "Longitude", type: "number" },
      {
        key: "effective_from",
        label: "Effective From",
        type: "date",
        card: true,
      },
      { key: "effective_to", label: "Effective To", type: "date" },
    ],
  },
  mealPlans: {
    key: "mealPlans",
    label: "Meal Plans",
    icon: Square3Stack3DIcon,
    endpoint: "student-meal-plan",
    titleField: "plan_name",
    subtitleField: "plan_type",
    searchKeys: ["plan_name", "student_name", "status"],
    fields: [
      { key: "plan_name", label: "Plan", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "plan_type",
        label: "Type",
        type: "select",
        options: MEAL_TYPE,
        badge: true,
      },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: MEAL_STATUS,
        badge: true,
      },
      { key: "meals_per_day", label: "Meals/Day", type: "number" },
      { key: "total_meals", label: "Total Meals", type: "number" },
      { key: "meals_consumed", label: "Consumed", type: "number" },
      { key: "cost", label: "Cost", type: "number" },
      {
        key: "dietary_restrictions",
        label: "Dietary Restrictions",
        full: true,
      },
    ],
  },
  parking: {
    key: "parking",
    label: "Parking",
    icon: MapPinIcon,
    endpoint: "student-parking",
    titleField: "permit_number",
    subtitleField: "student_name",
    searchKeys: ["permit_number", "student_name", "license_plate", "status"],
    fields: [
      { key: "permit_number", label: "Permit #", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "permit_type",
        label: "Type",
        type: "select",
        options: PERMIT_TYPE,
        badge: true,
      },
      { key: "vehicle_make", label: "Vehicle Make", card: true },
      { key: "vehicle_model", label: "Vehicle Model" },
      { key: "vehicle_color", label: "Vehicle Color" },
      { key: "license_plate", label: "License Plate", card: true },
      { key: "parking_zone", label: "Zone" },
      { key: "start_date", label: "Start", type: "date" },
      { key: "end_date", label: "End", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: PARKING_STATUS,
        badge: true,
      },
    ],
  },
  idActivity: {
    key: "idActivity",
    label: "ID Activity",
    icon: SignalIcon,
    endpoint: "student-i-d-activity",
    titleField: "student_name",
    subtitleField: "activity_type",
    searchKeys: ["student_name", "activity_type", "location", "device"],
    fields: [
      STUDENT_ID(),
      STUDENT_NAME,
      { key: "id_card", label: "ID Card (ID)", full: true },
      {
        key: "activity_type",
        label: "Type",
        type: "select",
        options: ID_ACTIVITY,
        badge: true,
      },
      { key: "location", label: "Location", card: true },
      { key: "timestamp", label: "Timestamp", type: "datetime", card: true },
      { key: "device", label: "Device" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  feedback: {
    key: "feedback",
    label: "Feedback",
    icon: QuestionMarkCircleIcon,
    endpoint: "student-feedback",
    titleField: "subject",
    subtitleField: "feedback_type",
    searchKeys: ["subject", "student_name", "comments", "suggestions"],
    fields: [
      { key: "subject", label: "Subject", main: true },
      STUDENT_ID(),
      STUDENT_NAME,
      {
        key: "feedback_type",
        label: "Type",
        type: "select",
        options: FEEDBACK_TYPE,
        badge: true,
      },
      { key: "rating", label: "Rating", type: "number", card: true },
      { key: "comments", label: "Comments", type: "textarea", full: true },
      {
        key: "suggestions",
        label: "Suggestions",
        type: "textarea",
        full: true,
      },
      { key: "is_anonymous", label: "Anonymous", type: "bool" },
      { key: "response", label: "Response", type: "textarea", full: true },
      { key: "responded_by", label: "Responded By (ID)", full: true },
      { key: "responded_at", label: "Responded At", type: "datetime" },
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

export default function StudentRecordsPage() {
  useTitle("Student Records");
  const [activeTab, setActiveTab] = useState("classrooms");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Student Records</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Classrooms, guardians, enrollment, medical, wellness, activities, aid and every
            supporting record around the student
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
            <t.icon className="h-4 w-4" />
            {t.label}
          </button>
        ))}
      </div>

      <EntitySection
        cfg={activeCfg}
        basePath="/students"
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
