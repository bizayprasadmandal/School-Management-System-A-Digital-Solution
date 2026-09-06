/**
 * Library Center — full-surface admin page for the library module.
 *
 * 33 entity tabs (config-driven via EntitySection): books, checkouts,
 * categories, reservations, reading lists & challenges, digital resources,
 * inventory audits & barcodes, fines & payments, analytics, events, reviews,
 * inter-library loans, recommendations, notifications, copies, repairs,
 * donations, purchases, cards, acquisitions, clubs and feedback.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, BuildingLibraryIcon } from "@heroicons/react/24/outline";
import {
  BookOpenIcon,
  ArrowsRightLeftIcon,
  TagIcon,
  BookmarkIcon,
  ListBulletIcon,
  GlobeAltIcon,
  CloudIcon,
  ClipboardDocumentCheckIcon,
  QrCodeIcon,
  CurrencyDollarIcon,
  ReceiptPercentIcon,
  ChartBarIcon,
  CalendarDaysIcon,
  TicketIcon,
  StarIcon,
  SparklesIcon,
  BellAlertIcon,
  UserIcon,
  CubeIcon,
  WrenchScrewdriverIcon,
  ShoppingBagIcon,
  CreditCardIcon,
  GiftIcon,
  ClipboardDocumentListIcon,
  UserGroupIcon,
  QueueListIcon,
  CheckBadgeIcon,
  ChatBubbleLeftRightIcon,
  ArchiveBoxIcon,
  EyeIcon,
} from "@heroicons/react/24/outline";

// ─── Shared option sets ──────────────────────────────────────────────────────

const CONDITIONS = [
  ["new", "New"],
  ["good", "Good"],
  ["fair", "Fair"],
  ["poor", "Poor"],
  ["damaged", "Damaged"],
  ["lost", "Lost"],
] as [string, string][];

const AUDIT_CONDITIONS = [
  ["good", "Good"],
  ["fair", "Fair"],
  ["poor", "Poor"],
  ["damaged", "Damaged"],
  ["lost", "Lost"],
] as [string, string][];

const RESERVATION_STATUS = [
  ["pending", "Pending"],
  ["fulfilled", "Fulfilled"],
  ["cancelled", "Cancelled"],
  ["expired", "Expired"],
] as [string, string][];

const READING_LIST_STATUS = [
  ["active", "Active"],
  ["archived", "Archived"],
] as [string, string][];

const RESOURCE_TYPES = [
  ["ebook", "E-Book"],
  ["audiobook", "Audiobook"],
  ["video", "Video"],
  ["article", "Article"],
  ["database", "Database"],
  ["podcast", "Podcast"],
  ["interactive", "Interactive"],
  ["other", "Other"],
] as [string, string][];

const AUDIT_TYPES = [
  ["full", "Full"],
  ["partial", "Partial"],
  ["spot_check", "Spot Check"],
  ["annual", "Annual"],
] as [string, string][];

const AUDIT_STATUS = [
  ["scheduled", "Scheduled"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const TRACKING_TYPES = [
  ["barcode", "Barcode"],
  ["rfid", "RFID"],
  ["qr_code", "QR Code"],
] as [string, string][];

const BARCODE_STATUS = [
  ["active", "Active"],
  ["damaged", "Damaged"],
  ["lost", "Lost"],
  ["deactivated", "Deactivated"],
] as [string, string][];

const FINE_TYPES = [
  ["overdue", "Overdue"],
  ["lost_book", "Lost Book"],
  ["damaged_book", "Damaged Book"],
  ["late_return", "Late Return"],
] as [string, string][];

const FINE_STATUS = [
  ["pending", "Pending"],
  ["partial", "Partially Paid"],
  ["paid", "Paid"],
  ["waived", "Waived"],
] as [string, string][];

const PAYMENT_METHODS = [
  ["cash", "Cash"],
  ["card", "Card"],
  ["online", "Online"],
  ["check", "Check"],
  ["waived", "Waived"],
] as [string, string][];

const REPORT_TYPES = [
  ["daily", "Daily"],
  ["weekly", "Weekly"],
  ["monthly", "Monthly"],
  ["term", "Term"],
  ["annual", "Annual"],
] as [string, string][];

const EVENT_TYPES = [
  ["book_fair", "Book Fair"],
  ["author_visit", "Author Visit"],
  ["reading_program", "Reading Program"],
  ["story_time", "Story Time"],
  ["book_club", "Book Club"],
  ["workshop", "Workshop"],
  ["exhibition", "Exhibition"],
  ["other", "Other"],
] as [string, string][];

const EVENT_STATUS = [
  ["upcoming", "Upcoming"],
  ["ongoing", "Ongoing"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const REG_STATUS = [
  ["registered", "Registered"],
  ["attended", "Attended"],
  ["cancelled", "Cancelled"],
  ["waitlisted", "Waitlisted"],
] as [string, string][];

const REC_TYPES = [
  ["popular", "Popular"],
  ["similar", "Similar"],
  ["curated", "Curated"],
  ["trending", "Trending"],
  ["new_arrival", "New Arrival"],
] as [string, string][];

const NOTIF_TYPES = [
  ["overdue_reminder", "Overdue Reminder"],
  ["book_due_soon", "Book Due Soon"],
  ["book_available", "Book Available"],
  ["new_arrival", "New Arrival"],
  ["fine_notice", "Fine Notice"],
  ["event_reminder", "Event Reminder"],
  ["recommendation", "Recommendation"],
] as [string, string][];

const CHANNELS = [
  ["email", "Email"],
  ["sms", "SMS"],
  ["push", "Push"],
  ["in_app", "In-App"],
] as [string, string][];

const LIBRARY_SECTIONS = [
  ["circulation", "Circulation"],
  ["reference", "Reference"],
  ["cataloging", "Cataloging"],
  ["periodicals", "Periodicals"],
  ["digital", "Digital"],
  ["archives", "Archives"],
  ["children", "Children"],
  ["general", "General"],
] as [string, string][];

const DONATION_STATUS = [
  ["pending", "Pending"],
  ["received", "Received"],
  ["cataloged", "Cataloged"],
  ["rejected", "Rejected"],
] as [string, string][];

const PURCHASE_STATUS = [
  ["pending", "Pending"],
  ["ordered", "Ordered"],
  ["received", "Received"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const CARD_STATUS = [
  ["active", "Active"],
  ["expired", "Expired"],
  ["lost", "Lost"],
  ["blocked", "Blocked"],
] as [string, string][];

const ACQ_PRIORITY = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
] as [string, string][];

const ACQ_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["ordered", "Ordered"],
  ["rejected", "Rejected"],
] as [string, string][];

const CLUB_ROLES = [
  ["member", "Member"],
  ["president", "President"],
  ["secretary", "Secretary"],
] as [string, string][];

const CHALLENGE_STATUS = [
  ["upcoming", "Upcoming"],
  ["active", "Active"],
  ["completed", "Completed"],
] as [string, string][];

const ILLO_STATUS = [
  ["requested", "Requested"],
  ["approved", "Approved"],
  ["in_transit", "In Transit"],
  ["received", "Received"],
  ["returned", "Returned"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const FEEDBACK_TYPES = [
  ["service", "Service"],
  ["collection", "Collection"],
  ["facility", "Facility"],
  ["staff", "Staff"],
  ["general", "General"],
] as [string, string][];

// ─── Entity configurations (33 tabs) ─────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  books: {
    key: "books",
    label: "Books",
    icon: BookOpenIcon,
    endpoint: "books",
    titleField: "title",
    subtitleField: "author",
    toggleField: "is_active",
    searchKeys: ["title", "author", "isbn", "publisher"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "author", label: "Author", card: true },
      { key: "isbn", label: "ISBN", card: true },
      { key: "publisher", label: "Publisher" },
      { key: "category", label: "Category (ID)" },
      { key: "shelf_location", label: "Shelf Location", card: true },
      { key: "total_copies", label: "Total Copies", type: "number" },
      {
        key: "available_copies",
        label: "Available",
        skipForm: true,
        card: true,
      },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "created_at", label: "Added", type: "datetime", skipForm: true },
    ],
  },
  checkouts: {
    key: "checkouts",
    label: "Checkouts",
    icon: ArrowsRightLeftIcon,
    endpoint: "checkouts",
    titleField: "book_title",
    subtitleField: "student_name",
    searchKeys: ["book_title", "student_name", "checked_out_by_name"],
    fields: [
      { key: "book", label: "Book (ID)", full: true },
      { key: "book_title", label: "Book", skipForm: true },
      { key: "student", label: "Student (ID)" },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "checked_out_by", label: "Checked Out By (User ID)" },
      { key: "checked_out_by_name", label: "Checked Out By", skipForm: true },
      {
        key: "checked_out_at",
        label: "Checked Out At",
        type: "datetime",
        card: true,
      },
      { key: "due_date", label: "Due Date", type: "date", card: true },
      { key: "returned_at", label: "Returned At", type: "datetime" },
      { key: "fine_amount", label: "Fine Amount", type: "number" },
      { key: "fine_paid", label: "Fine Paid", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      { key: "is_overdue", label: "Overdue", badge: true, skipForm: true },
      { key: "days_overdue", label: "Days Overdue", skipForm: true },
    ],
  },
  categories: {
    key: "categories",
    label: "Categories",
    icon: TagIcon,
    endpoint: "categories",
    titleField: "name",
    toggleField: "is_active",
    searchKeys: ["name", "dewey_code", "description"],
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "parent_category", label: "Parent Category (ID)" },
      { key: "dewey_code", label: "Dewey Code", card: true },
      { key: "is_active", label: "Active", type: "bool" },
    ],
  },
  reservations: {
    key: "reservations",
    label: "Reservations",
    icon: BookmarkIcon,
    endpoint: "reservations",
    titleField: "book_title",
    subtitleField: "student_name",
    searchKeys: ["book_title", "student_name", "status"],
    fields: [
      { key: "book", label: "Book (ID)", full: true },
      { key: "book_title", label: "Book", skipForm: true },
      { key: "student", label: "Student (ID)" },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: RESERVATION_STATUS,
        badge: true,
      },
      {
        key: "reserved_at",
        label: "Reserved At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      { key: "expires_at", label: "Expires At", type: "datetime" },
      { key: "notified", label: "Notified", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "reading-lists": {
    key: "reading-lists",
    label: "Reading Lists",
    icon: ListBulletIcon,
    endpoint: "reading-lists",
    titleField: "name",
    subtitleField: "created_by_name",
    searchKeys: ["name", "created_by_name", "subject", "grade", "status"],
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "created_by", label: "Created By (User ID)" },
      { key: "created_by_name", label: "Created By", skipForm: true },
      { key: "grade", label: "Grade", card: true },
      { key: "subject", label: "Subject", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: READING_LIST_STATUS,
        badge: true,
      },
      { key: "is_mandatory", label: "Mandatory", type: "bool" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
    ],
  },
  "reading-list-items": {
    key: "reading-list-items",
    label: "Reading List Items",
    icon: QueueListIcon,
    endpoint: "reading-list-items",
    titleField: "book_title",
    subtitleField: "reading_list_name",
    searchKeys: ["book_title", "reading_list_name"],
    fields: [
      { key: "reading_list", label: "Reading List (ID)", full: true },
      { key: "reading_list_name", label: "Reading List", skipForm: true },
      { key: "book", label: "Book (ID)" },
      { key: "book_title", label: "Book", skipForm: true },
      { key: "order", label: "Order", type: "number" },
      { key: "is_required", label: "Required", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      {
        key: "added_at",
        label: "Added At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "digital-resources": {
    key: "digital-resources",
    label: "Digital Resources",
    icon: CloudIcon,
    endpoint: "digital-resources",
    titleField: "title",
    subtitleField: "author",
    searchKeys: ["title", "author", "resource_type", "publisher"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "author", label: "Author", card: true },
      {
        key: "resource_type",
        label: "Type",
        type: "select",
        options: RESOURCE_TYPES,
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "url", label: "URL", full: true },
      { key: "file", label: "File" },
      { key: "category", label: "Category" },
      { key: "isbn", label: "ISBN" },
      { key: "publisher", label: "Publisher" },
      { key: "publication_date", label: "Publication Date", type: "date" },
      { key: "duration_minutes", label: "Duration (min)", type: "number" },
    ],
  },
  "inventory-audits": {
    key: "inventory-audits",
    label: "Inventory Audits",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "inventory-audits",
    titleField: "name",
    subtitleField: "audit_type",
    searchKeys: ["name", "audit_type", "status", "conducted_by_name"],
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "audit_type",
        label: "Audit Type",
        type: "select",
        options: AUDIT_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: AUDIT_STATUS,
        badge: true,
      },
      {
        key: "scheduled_date",
        label: "Scheduled Date",
        type: "date",
        card: true,
      },
      { key: "completed_date", label: "Completed Date", type: "date" },
      { key: "conducted_by", label: "Conducted By (User ID)" },
      { key: "conducted_by_name", label: "Conducted By", skipForm: true },
      { key: "total_books_expected", label: "Expected", type: "number" },
      { key: "total_books_found", label: "Found", type: "number" },
      { key: "total_missing", label: "Missing", skipForm: true, card: true },
      { key: "total_damaged", label: "Damaged", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "inventory-items": {
    key: "inventory-items",
    label: "Audit Items",
    icon: CubeIcon,
    endpoint: "inventory-items",
    titleField: "book_title",
    subtitleField: "audit_name",
    searchKeys: ["book_title", "audit_name", "shelf_location"],
    fields: [
      { key: "audit", label: "Audit (ID)", full: true },
      { key: "audit_name", label: "Audit", skipForm: true },
      { key: "book", label: "Book (ID)" },
      { key: "book_title", label: "Book", skipForm: true },
      { key: "expected_copies", label: "Expected Copies", type: "number" },
      { key: "found_copies", label: "Found Copies", type: "number" },
      {
        key: "condition",
        label: "Condition",
        type: "select",
        options: AUDIT_CONDITIONS,
        badge: true,
      },
      { key: "shelf_location", label: "Shelf Location", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      {
        key: "checked_at",
        label: "Checked At",
        type: "datetime",
        skipForm: true,
      },
    ],
  },
  barcodes: {
    key: "barcodes",
    label: "Barcode Tracking",
    icon: QrCodeIcon,
    endpoint: "barcodes",
    titleField: "barcode_value",
    subtitleField: "book_title",
    searchKeys: ["barcode_value", "book_title", "status"],
    fields: [
      { key: "book", label: "Book (ID)", full: true },
      { key: "book_title", label: "Book", skipForm: true },
      {
        key: "tracking_type",
        label: "Tracking Type",
        type: "select",
        options: TRACKING_TYPES,
        badge: true,
      },
      { key: "barcode_value", label: "Barcode Value", main: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: BARCODE_STATUS,
        badge: true,
      },
      { key: "copy_number", label: "Copy Number", card: true },
      { key: "assigned_at", label: "Assigned At", type: "datetime" },
      {
        key: "last_scanned_at",
        label: "Last Scanned",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  fines: {
    key: "fines",
    label: "Fines",
    icon: CurrencyDollarIcon,
    endpoint: "fines",
    titleField: "student_name",
    subtitleField: "book_title",
    searchKeys: ["student_name", "book_title", "fine_type", "status"],
    actions: [
      {
        label: "Waive Fine",
        url: (id) => `/library/fines/${id}/waive/`,
        confirm: "Waive this fine?",
        kind: "info",
      },
    ],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "checkout", label: "Checkout (ID)" },
      { key: "book", label: "Book (ID)" },
      { key: "book_title", label: "Book", skipForm: true },
      {
        key: "fine_type",
        label: "Fine Type",
        type: "select",
        options: FINE_TYPES,
        badge: true,
      },
      { key: "amount", label: "Amount", type: "number", card: true },
      { key: "amount_paid", label: "Amount Paid", type: "number", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: FINE_STATUS,
        badge: true,
      },
      { key: "days_overdue", label: "Days Overdue", type: "number" },
      { key: "reason", label: "Reason", type: "textarea", full: true },
    ],
  },
  "fine-payments": {
    key: "fine-payments",
    label: "Fine Payments",
    icon: ReceiptPercentIcon,
    endpoint: "fine-payments",
    titleField: "fine_reference",
    subtitleField: "received_by_name",
    searchKeys: ["fine_reference", "received_by_name", "payment_method"],
    fields: [
      { key: "fine", label: "Fine (ID)", full: true },
      { key: "fine_reference", label: "Fine", skipForm: true },
      { key: "amount", label: "Amount", type: "number", card: true },
      {
        key: "payment_method",
        label: "Payment Method",
        type: "select",
        options: PAYMENT_METHODS,
        badge: true,
      },
      { key: "received_by", label: "Received By (User ID)" },
      { key: "received_by_name", label: "Received By", skipForm: true },
      { key: "reference_number", label: "Reference Number", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      { key: "paid_at", label: "Paid At", type: "datetime", skipForm: true },
    ],
  },
  analytics: {
    key: "analytics",
    label: "Analytics Reports",
    icon: ChartBarIcon,
    endpoint: "analytics",
    titleField: "report_type",
    subtitleField: "period_start",
    searchKeys: ["report_type"],
    fields: [
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: REPORT_TYPES,
        badge: true,
      },
      { key: "period_start", label: "Period Start", type: "date", card: true },
      { key: "period_end", label: "Period End", type: "date", card: true },
      { key: "total_checkouts", label: "Checkouts", type: "number" },
      { key: "total_returns", label: "Returns", type: "number" },
      { key: "total_renewals", label: "Renewals", type: "number" },
      { key: "total_reservations", label: "Reservations", type: "number" },
      { key: "total_books", label: "Total Books", type: "number" },
      { key: "new_books_added", label: "New Books", type: "number" },
      { key: "books_lost", label: "Books Lost", type: "number" },
      { key: "books_damaged", label: "Books Damaged", type: "number" },
      {
        key: "active_users",
        label: "Active Users",
        type: "number",
        card: true,
      },
    ],
  },
  events: {
    key: "events",
    label: "Library Events",
    icon: CalendarDaysIcon,
    endpoint: "events",
    titleField: "name",
    subtitleField: "location",
    searchKeys: ["name", "event_type", "status", "location", "organizer_name"],
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "event_type",
        label: "Type",
        type: "select",
        options: EVENT_TYPES,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: EVENT_STATUS,
        badge: true,
      },
      { key: "location", label: "Location", card: true },
      { key: "start_date", label: "Start Date", type: "datetime", card: true },
      { key: "end_date", label: "End Date", type: "datetime" },
      { key: "max_participants", label: "Max Participants", type: "number" },
      {
        key: "current_participants",
        label: "Participants",
        skipForm: true,
        card: true,
      },
      { key: "organizer", label: "Organizer (User ID)" },
      { key: "organizer_name", label: "Organizer", skipForm: true },
      { key: "is_mandatory", label: "Mandatory", type: "bool" },
    ],
  },
  "event-registrations": {
    key: "event-registrations",
    label: "Event Registrations",
    icon: TicketIcon,
    endpoint: "event-registrations",
    titleField: "event_name",
    subtitleField: "student_name",
    searchKeys: ["event_name", "student_name", "status"],
    fields: [
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_name", label: "Event", skipForm: true },
      { key: "student", label: "Student (ID)" },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: REG_STATUS,
        badge: true,
      },
      {
        key: "registered_at",
        label: "Registered At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      { key: "attended_at", label: "Attended At", type: "datetime" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  reviews: {
    key: "reviews",
    label: "Book Reviews",
    icon: StarIcon,
    endpoint: "reviews",
    titleField: "title",
    subtitleField: "book_title",
    toggleField: "is_approved",
    searchKeys: ["title", "book_title", "student_name"],
    fields: [
      { key: "book", label: "Book (ID)", full: true },
      { key: "book_title", label: "Book", skipForm: true },
      { key: "student", label: "Student (ID)" },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "title", label: "Review Title", main: true },
      { key: "review_text", label: "Review", type: "textarea", full: true },
      { key: "rating", label: "Rating", type: "number", card: true },
      { key: "is_anonymous", label: "Anonymous", type: "bool" },
      { key: "is_approved", label: "Approved", type: "bool" },
      {
        key: "helpful_count",
        label: "Helpful Votes",
        skipForm: true,
        card: true,
      },
    ],
  },
  "inter-library-loans": {
    key: "inter-library-loans",
    label: "Inter-Library Loans",
    icon: GlobeAltIcon,
    endpoint: "inter-library-loans",
    titleField: "book_title",
    subtitleField: "requesting_student_name",
    searchKeys: ["book_title", "book_author", "lending_library", "status"],
    fields: [
      {
        key: "requesting_student",
        label: "Requesting Student (ID)",
        full: true,
      },
      { key: "requesting_student_name", label: "Student", skipForm: true },
      { key: "book_title", label: "Book Title", main: true },
      { key: "book_author", label: "Author", card: true },
      { key: "isbn", label: "ISBN" },
      { key: "lending_library", label: "Lending Library", card: true },
      { key: "lending_library_contact", label: "Library Contact", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ILLO_STATUS,
        badge: true,
      },
      { key: "requested_date", label: "Requested", type: "date" },
      { key: "expected_arrival", label: "Expected Arrival", type: "date" },
      { key: "actual_arrival", label: "Actual Arrival", type: "date" },
      { key: "due_date", label: "Due Date", type: "date" },
    ],
  },
  recommendations: {
    key: "recommendations",
    label: "Recommendations",
    icon: SparklesIcon,
    endpoint: "recommendations",
    titleField: "book_title",
    subtitleField: "student_name",
    searchKeys: ["book_title", "student_name", "recommendation_type"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "book", label: "Book (ID)" },
      { key: "book_title", label: "Book", skipForm: true },
      {
        key: "recommendation_type",
        label: "Type",
        type: "select",
        options: REC_TYPES,
        badge: true,
      },
      { key: "score", label: "Score", type: "number", card: true },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      { key: "is_dismissed", label: "Dismissed", type: "bool" },
      { key: "is_read", label: "Read", type: "bool" },
    ],
  },
  notifications: {
    key: "notifications",
    label: "Notifications",
    icon: BellAlertIcon,
    endpoint: "notifications",
    titleField: "title",
    subtitleField: "student_name",
    searchKeys: ["title", "student_name", "notification_type", "channel"],
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
      { key: "channel", label: "Channel", type: "select", options: CHANNELS },
      { key: "title", label: "Title", main: true },
      { key: "message", label: "Message", type: "textarea", full: true },
      { key: "book", label: "Book (ID)" },
      { key: "checkout", label: "Checkout (ID)" },
      { key: "event", label: "Event (ID)" },
    ],
  },
  "librarian-profile": {
    key: "librarian-profile",
    label: "Librarian Profiles",
    icon: UserIcon,
    endpoint: "librarian-profile",
    titleField: "user_name",
    subtitleField: "library_section",
    searchKeys: ["user_name", "library_section", "qualification"],
    fields: [
      { key: "user", label: "User (ID)", full: true },
      { key: "user_name", label: "User", skipForm: true },
      {
        key: "library_section",
        label: "Section",
        type: "select",
        options: LIBRARY_SECTIONS,
        badge: true,
      },
      { key: "qualification", label: "Qualification", card: true },
      { key: "experience_years", label: "Experience (years)", type: "number" },
      { key: "certifications", label: "Certifications", full: true },
      { key: "bio", label: "Bio", type: "textarea", full: true },
    ],
  },
  "book-copy": {
    key: "book-copy",
    label: "Book Copies",
    icon: ArchiveBoxIcon,
    endpoint: "book-copy",
    titleField: "book_title",
    subtitleField: "copy_number",
    toggleField: "is_available",
    searchKeys: ["book_title", "barcode", "location", "condition"],
    fields: [
      { key: "book", label: "Book (ID)", full: true },
      { key: "book_title", label: "Book", skipForm: true },
      { key: "copy_number", label: "Copy Number", card: true },
      { key: "barcode", label: "Barcode", card: true },
      {
        key: "condition",
        label: "Condition",
        type: "select",
        options: CONDITIONS,
        badge: true,
      },
      { key: "location", label: "Location" },
      { key: "shelf_number", label: "Shelf Number" },
      { key: "is_available", label: "Available", type: "bool" },
      { key: "is_reference_only", label: "Reference Only", type: "bool" },
      { key: "purchase_date", label: "Purchase Date", type: "date" },
      { key: "purchase_price", label: "Purchase Price", type: "number" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "book-condition-log": {
    key: "book-condition-log",
    label: "Condition Logs",
    icon: ClipboardDocumentListIcon,
    endpoint: "book-condition-log",
    titleField: "copy_label",
    subtitleField: "new_condition",
    searchKeys: ["copy_label", "reported_by_name", "reason"],
    fields: [
      { key: "book_copy", label: "Book Copy (ID)", full: true },
      { key: "copy_label", label: "Copy", skipForm: true },
      {
        key: "previous_condition",
        label: "Previous Condition",
        type: "select",
        options: CONDITIONS,
      },
      {
        key: "new_condition",
        label: "New Condition",
        type: "select",
        options: CONDITIONS,
        badge: true,
      },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      { key: "reported_by", label: "Reported By (User ID)" },
      { key: "reported_by_name", label: "Reported By", skipForm: true },
      {
        key: "created_at",
        label: "Logged At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "book-repair": {
    key: "book-repair",
    label: "Book Repairs",
    icon: WrenchScrewdriverIcon,
    endpoint: "book-repair",
    titleField: "copy_label",
    subtitleField: "issue",
    searchKeys: ["copy_label", "issue", "vendor", "status"],
    fields: [
      { key: "book_copy", label: "Book Copy (ID)", full: true },
      { key: "copy_label", label: "Copy", skipForm: true },
      { key: "issue", label: "Issue", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: AUDIT_STATUS,
        badge: true,
      },
      { key: "cost", label: "Cost", type: "number", card: true },
      { key: "vendor", label: "Vendor", card: true },
      { key: "scheduled_date", label: "Scheduled Date", type: "date" },
      { key: "completed_date", label: "Completed Date", type: "date" },
      { key: "reported_by", label: "Reported By (User ID)" },
      { key: "reported_by_name", label: "Reported By", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "book-donation": {
    key: "book-donation",
    label: "Book Donations",
    icon: GiftIcon,
    endpoint: "book-donation",
    titleField: "donor_name",
    subtitleField: "book_title",
    searchKeys: ["donor_name", "book_title", "status"],
    fields: [
      { key: "donor_name", label: "Donor Name", main: true },
      { key: "donor_email", label: "Donor Email", card: true },
      { key: "donor_phone", label: "Donor Phone" },
      { key: "book_title", label: "Book Title", card: true },
      { key: "author", label: "Author" },
      { key: "isbn", label: "ISBN" },
      { key: "quantity", label: "Quantity", type: "number" },
      {
        key: "condition",
        label: "Condition",
        type: "select",
        options: CONDITIONS,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: DONATION_STATUS,
        badge: true,
      },
      { key: "received_date", label: "Received Date", type: "date" },
      { key: "received_by", label: "Received By (User ID)" },
      { key: "received_by_name", label: "Received By", skipForm: true },
    ],
  },
  "book-purchase": {
    key: "book-purchase",
    label: "Book Purchases",
    icon: ShoppingBagIcon,
    endpoint: "book-purchase",
    titleField: "title",
    subtitleField: "vendor",
    searchKeys: ["title", "author", "vendor", "status"],
    fields: [
      { key: "book", label: "Book (ID)" },
      { key: "book_title", label: "Catalog Book", skipForm: true },
      { key: "title", label: "Title", main: true },
      { key: "author", label: "Author", card: true },
      { key: "isbn", label: "ISBN" },
      { key: "quantity", label: "Quantity", type: "number" },
      { key: "unit_price", label: "Unit Price", type: "number" },
      { key: "total_cost", label: "Total Cost", type: "number", card: true },
      { key: "vendor", label: "Vendor" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: PURCHASE_STATUS,
        badge: true,
      },
      { key: "order_date", label: "Order Date", type: "date" },
      { key: "expected_date", label: "Expected Date", type: "date" },
      { key: "received_date", label: "Received Date", type: "date" },
    ],
  },
  "library-card": {
    key: "library-card",
    label: "Library Cards",
    icon: CreditCardIcon,
    endpoint: "library-card",
    titleField: "card_number",
    subtitleField: "student_name",
    searchKeys: ["card_number", "student_name", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "card_number", label: "Card Number", main: true },
      { key: "issue_date", label: "Issue Date", type: "date", card: true },
      { key: "expiry_date", label: "Expiry Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CARD_STATUS,
        badge: true,
      },
      { key: "max_checkouts", label: "Max Checkouts", type: "number" },
      {
        key: "current_checkouts",
        label: "Current Checkouts",
        skipForm: true,
        card: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "acquisition-request": {
    key: "acquisition-request",
    label: "Acquisition Requests",
    icon: CheckBadgeIcon,
    endpoint: "acquisition-request",
    titleField: "title",
    subtitleField: "requested_by_name",
    searchKeys: ["title", "author", "requested_by_name", "status", "priority"],
    fields: [
      { key: "requested_by", label: "Requested By (User ID)" },
      { key: "requested_by_name", label: "Requested By", skipForm: true },
      { key: "title", label: "Title", main: true },
      { key: "author", label: "Author", card: true },
      { key: "isbn", label: "ISBN" },
      { key: "publisher", label: "Publisher" },
      { key: "quantity", label: "Quantity", type: "number" },
      {
        key: "estimated_cost",
        label: "Estimated Cost",
        type: "number",
        card: true,
      },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      {
        key: "priority",
        label: "Priority",
        type: "select",
        options: ACQ_PRIORITY,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ACQ_STATUS,
        badge: true,
      },
      { key: "approved_by", label: "Approved By (User ID)" },
      { key: "approved_by_name", label: "Approved By", skipForm: true },
    ],
  },
  "book-club": {
    key: "book-club",
    label: "Book Clubs",
    icon: UserGroupIcon,
    endpoint: "book-club",
    titleField: "name",
    subtitleField: "meeting_day",
    toggleField: "is_active",
    searchKeys: ["name", "advisor_name", "meeting_location"],
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "advisor", label: "Advisor (User ID)" },
      { key: "advisor_name", label: "Advisor", skipForm: true },
      { key: "meeting_day", label: "Meeting Day", card: true },
      { key: "meeting_time", label: "Meeting Time", card: true },
      { key: "meeting_location", label: "Meeting Location" },
      { key: "max_members", label: "Max Members", type: "number" },
      { key: "current_book", label: "Current Book (ID)" },
      { key: "current_book_title", label: "Current Book", skipForm: true },
      { key: "is_active", label: "Active", type: "bool" },
    ],
  },
  "book-club-membership": {
    key: "book-club-membership",
    label: "Club Memberships",
    icon: UserGroupIcon,
    endpoint: "book-club-membership",
    titleField: "student_name",
    subtitleField: "club_name",
    toggleField: "is_active",
    searchKeys: ["student_name", "club_name", "role"],
    fields: [
      { key: "book_club", label: "Book Club (ID)", full: true },
      { key: "club_name", label: "Club", skipForm: true },
      { key: "student", label: "Student (ID)" },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "role",
        label: "Role",
        type: "select",
        options: CLUB_ROLES,
        badge: true,
      },
      { key: "join_date", label: "Join Date", type: "date", card: true },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "is_active", label: "Active", type: "bool" },
    ],
  },
  "student-reading-log": {
    key: "student-reading-log",
    label: "Reading Logs",
    icon: BookOpenIcon,
    endpoint: "student-reading-log",
    titleField: "book_title",
    subtitleField: "student_name",
    searchKeys: ["book_title", "student_name", "author"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "book", label: "Book (ID)" },
      { key: "book_title", label: "Book Title", main: true },
      { key: "author", label: "Author", card: true },
      { key: "pages_read", label: "Pages Read", type: "number", card: true },
      { key: "total_pages", label: "Total Pages", type: "number" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "rating", label: "Rating", type: "number" },
      { key: "review", label: "Review", type: "textarea", full: true },
    ],
  },
  "reading-challenge": {
    key: "reading-challenge",
    label: "Reading Challenges",
    icon: SparklesIcon,
    endpoint: "reading-challenge",
    titleField: "name",
    subtitleField: "status",
    searchKeys: ["name", "status", "prize"],
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "start_date", label: "Start Date", type: "date", card: true },
      { key: "end_date", label: "End Date", type: "date", card: true },
      { key: "goal_books", label: "Goal (Books)", type: "number" },
      { key: "goal_pages", label: "Goal (Pages)", type: "number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CHALLENGE_STATUS,
        badge: true,
      },
      { key: "prize", label: "Prize", full: true },
      {
        key: "participants_count",
        label: "Participants",
        skipForm: true,
        card: true,
      },
    ],
  },
  "reading-challenge-progress": {
    key: "reading-challenge-progress",
    label: "Challenge Progress",
    icon: EyeIcon,
    endpoint: "reading-challenge-progress",
    titleField: "student_name",
    subtitleField: "challenge_name",
    toggleField: "is_completed",
    searchKeys: ["student_name", "challenge_name"],
    fields: [
      { key: "challenge", label: "Challenge (ID)", full: true },
      { key: "challenge_name", label: "Challenge", skipForm: true },
      { key: "student", label: "Student (ID)" },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "books_read", label: "Books Read", type: "number", card: true },
      { key: "pages_read", label: "Pages Read", type: "number", card: true },
      { key: "is_completed", label: "Completed", type: "bool" },
      {
        key: "completed_date",
        label: "Completed Date",
        type: "date",
        skipForm: true,
      },
    ],
  },
  "library-feedback": {
    key: "library-feedback",
    label: "Feedback",
    icon: ChatBubbleLeftRightIcon,
    endpoint: "library-feedback",
    titleField: "student_name",
    subtitleField: "feedback_type",
    searchKeys: ["student_name", "feedback_type", "comments"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "feedback_type",
        label: "Feedback Type",
        type: "select",
        options: FEEDBACK_TYPES,
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
      { key: "responded_by", label: "Responded By (User ID)" },
      { key: "responded_by_name", label: "Responded By", skipForm: true },
      {
        key: "responded_at",
        label: "Responded At",
        type: "datetime",
        skipForm: true,
      },
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

export default function LibraryPage() {
  useTitle("Library Center");
  const [activeTab, setActiveTab] = useState("books");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Library Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Catalog, circulation, reservations, fines, events, clubs, inventory and analytics
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
            leftIcon={<BuildingLibraryIcon className="h-4 w-4" />}
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
        basePath="/library"
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
