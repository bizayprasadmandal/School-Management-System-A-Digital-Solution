/**
 * Alumni Center — full-surface admin page for the alumni module.
 *
 * 48 entity tabs (config-driven via EntitySection): profiles & verification,
 * events & RSVPs, donations/receipts/recurring, chapters, mentorships,
 * job postings & applications, discussions, newsletters, campaigns, badges,
 * activity feed, groups, volunteering, polls, success stories, referrals,
 * messaging, calendar, media galleries, directory, podcasts and awards.
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
  CalendarDaysIcon,
  CurrencyDollarIcon,
  GlobeAltIcon,
  ShieldCheckIcon,
  TicketIcon,
  ReceiptPercentIcon,
  ArrowPathIcon,
  BriefcaseIcon,
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  ChatBubbleOvalLeftIcon,
  MegaphoneIcon,
  SparklesIcon,
  TrophyIcon,
  PhotoIcon,
  VideoCameraIcon,
  NewspaperIcon,
  HeartIcon,
  UserGroupIcon,
  HandRaisedIcon,
  StarIcon,
  QueueListIcon,
  EyeIcon,
  FolderOpenIcon,
  TagIcon,
  AcademicCapIcon,
  PaperAirplaneIcon,
  InboxIcon,
  MicrophoneIcon,
  BellAlertIcon,
  ArrowTrendingUpIcon,
  CheckBadgeIcon,
  FunnelIcon,
  GiftIcon,
  ClipboardDocumentCheckIcon,
  ListBulletIcon,
  BanknotesIcon,
} from "@heroicons/react/24/outline";

// ─── Shared option sets ──────────────────────────────────────────────────────

const EMPLOYMENT_STATUS = [
  ["employed", "Employed"],
  ["self_employed", "Self-Employed"],
  ["student", "Student"],
  ["unemployed", "Unemployed"],
  ["retired", "Retired"],
] as [string, string][];

const VERIFY_STATUS = [
  ["pending", "Pending"],
  ["verified", "Verified"],
  ["rejected", "Rejected"],
  ["expired", "Expired"],
] as [string, string][];

const VERIFY_METHOD = [
  ["degree", "Degree"],
  ["student_id", "Student ID"],
  ["admin_approval", "Admin Approval"],
  ["email_verification", "Email Verification"],
  ["manual", "Manual"],
] as [string, string][];

const EVENT_STATUS = [
  ["draft", "Draft"],
  ["published", "Published"],
  ["ongoing", "Ongoing"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const RSVP_STATUS = [
  ["registered", "Registered"],
  ["confirmed", "Confirmed"],
  ["attended", "Attended"],
  ["cancelled", "Cancelled"],
  ["no_show", "No Show"],
] as [string, string][];

const FUND_TYPES = [
  ["general", "General"],
  ["scholarship", "Scholarship"],
  ["infrastructure", "Infrastructure"],
  ["sports", "Sports"],
  ["library", "Library"],
  ["other", "Other"],
] as [string, string][];

const PAYMENT_METHODS = [
  ["cash", "Cash"],
  ["check", "Check"],
  ["bank_transfer", "Bank Transfer"],
  ["online", "Online"],
  ["other", "Other"],
] as [string, string][];

const RECEIPT_STATUS = [
  ["pending", "Pending"],
  ["generated", "Generated"],
  ["sent", "Sent"],
  ["failed", "Failed"],
] as [string, string][];

const RECUR_FREQUENCY = [
  ["weekly", "Weekly"],
  ["biweekly", "Biweekly"],
  ["monthly", "Monthly"],
  ["quarterly", "Quarterly"],
  ["yearly", "Yearly"],
] as [string, string][];

const RECUR_STATUS = [
  ["active", "Active"],
  ["paused", "Paused"],
  ["cancelled", "Cancelled"],
  ["failed", "Failed"],
] as [string, string][];

const CHAPTER_ROLES = [
  ["president", "President"],
  ["vice_president", "Vice President"],
  ["secretary", "Secretary"],
  ["treasurer", "Treasurer"],
  ["member", "Member"],
] as [string, string][];

const MENTOR_FOCUS = [
  ["career", "Career"],
  ["industry", "Industry"],
  ["academic", "Academic"],
  ["personal", "Personal"],
  ["entrepreneurship", "Entrepreneurship"],
  ["other", "Other"],
] as [string, string][];

const MENTOR_STATUS = [
  ["pending", "Pending"],
  ["active", "Active"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const MEETING_FREQ = [
  ["weekly", "Weekly"],
  ["biweekly", "Biweekly"],
  ["monthly", "Monthly"],
] as [string, string][];

const JOB_TYPES = [
  ["full_time", "Full Time"],
  ["part_time", "Part Time"],
  ["contract", "Contract"],
  ["internship", "Internship"],
  ["freelance", "Freelance"],
] as [string, string][];

const EXPERIENCE_LEVELS = [
  ["entry", "Entry"],
  ["mid", "Mid"],
  ["senior", "Senior"],
  ["executive", "Executive"],
] as [string, string][];

const JOB_STATUS = [
  ["draft", "Draft"],
  ["published", "Published"],
  ["closed", "Closed"],
  ["expired", "Expired"],
] as [string, string][];

const APPLICATION_STATUS = [
  ["pending", "Pending"],
  ["reviewed", "Reviewed"],
  ["shortlisted", "Shortlisted"],
  ["rejected", "Rejected"],
  ["hired", "Hired"],
] as [string, string][];

const DISCUSSION_CATEGORIES = [
  ["general", "General"],
  ["career", "Career"],
  ["industry", "Industry"],
  ["events", "Events"],
  ["networking", "Networking"],
  ["mentorship", "Mentorship"],
  ["announcements", "Announcements"],
] as [string, string][];

const DISCUSSION_STATUS = [
  ["open", "Open"],
  ["closed", "Closed"],
  ["pinned", "Pinned"],
  ["archived", "Archived"],
] as [string, string][];

const NEWSLETTER_STATUS = [
  ["draft", "Draft"],
  ["scheduled", "Scheduled"],
  ["sending", "Sending"],
  ["sent", "Sent"],
  ["failed", "Failed"],
] as [string, string][];

const CAMPAIGN_TYPES = [
  ["general", "General"],
  ["scholarship", "Scholarship"],
  ["infrastructure", "Infrastructure"],
  ["emergency", "Emergency"],
  ["annual", "Annual"],
  ["class_gift", "Class Gift"],
  ["other", "Other"],
] as [string, string][];

const CAMPAIGN_STATUS = [
  ["draft", "Draft"],
  ["active", "Active"],
  ["paused", "Paused"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const BADGE_TYPES = [
  ["milestone", "Milestone"],
  ["donation", "Donation"],
  ["engagement", "Engagement"],
  ["mentorship", "Mentorship"],
  ["event", "Event"],
  ["volunteer", "Volunteer"],
  ["referral", "Referral"],
  ["special", "Special"],
] as [string, string][];

const ACTIVITY_TYPES = [
  ["profile_update", "Profile Update"],
  ["event_registered", "Event Registered"],
  ["event_attended", "Event Attended"],
  ["donation_made", "Donation Made"],
  ["badge_earned", "Badge Earned"],
  ["mentorship_started", "Mentorship Started"],
  ["job_posted", "Job Posted"],
  ["discussion_created", "Discussion Created"],
  ["chapter_joined", "Chapter Joined"],
  ["volunteered", "Volunteered"],
  ["referral_made", "Referral Made"],
  ["other", "Other"],
] as [string, string][];

const GROUP_TYPES = [
  ["interest", "Interest"],
  ["batch", "Batch"],
  ["sports", "Sports"],
  ["club", "Club"],
  ["industry", "Industry"],
  ["regional", "Regional"],
  ["other", "Other"],
] as [string, string][];

const GROUP_MEMBER_ROLES = [
  ["admin", "Admin"],
  ["moderator", "Moderator"],
  ["member", "Member"],
] as [string, string][];

const GROUP_MEMBER_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["banned", "Banned"],
] as [string, string][];

const TIME_COMMITMENTS = [
  ["one_time", "One Time"],
  ["weekly", "Weekly"],
  ["monthly", "Monthly"],
  ["flexible", "Flexible"],
] as [string, string][];

const VOLUNTEER_STATUS = [
  ["draft", "Draft"],
  ["open", "Open"],
  ["full", "Full"],
  ["closed", "Closed"],
  ["completed", "Completed"],
] as [string, string][];

const VOLUNTEER_SIGNUP_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["completed", "Completed"],
] as [string, string][];

const POLL_TYPES = [
  ["poll", "Poll"],
  ["survey", "Survey"],
  ["feedback", "Feedback"],
  ["election", "Election"],
] as [string, string][];

const POLL_STATUS = [
  ["draft", "Draft"],
  ["active", "Active"],
  ["closed", "Closed"],
] as [string, string][];

const STORY_TYPES = [
  ["career", "Career"],
  ["entrepreneurship", "Entrepreneurship"],
  ["social_impact", "Social Impact"],
  ["academic", "Academic"],
  ["sports", "Sports"],
  ["arts", "Arts"],
  ["other", "Other"],
] as [string, string][];

const STORY_STATUS = [
  ["draft", "Draft"],
  ["pending", "Pending"],
  ["published", "Published"],
  ["rejected", "Rejected"],
] as [string, string][];

const REFERRAL_TYPES = [
  ["admission", "Admission"],
  ["job", "Job"],
  ["event", "Event"],
  ["other", "Other"],
] as [string, string][];

const REFERRAL_STATUS = [
  ["pending", "Pending"],
  ["contacted", "Contacted"],
  ["converted", "Converted"],
  ["expired", "Expired"],
] as [string, string][];

const MESSAGE_TYPES = [
  ["text", "Text"],
  ["image", "Image"],
  ["file", "File"],
  ["link", "Link"],
  ["system", "System"],
] as [string, string][];

const CALENDAR_EVENT_TYPES = [
  ["reunion", "Reunion"],
  ["networking", "Networking"],
  ["gala", "Gala"],
  ["workshop", "Workshop"],
  ["webinar", "Webinar"],
  ["sports", "Sports"],
  ["cultural", "Cultural"],
  ["career", "Career"],
  ["other", "Other"],
] as [string, string][];

const RECURRENCE_TYPES = [
  ["none", "None"],
  ["daily", "Daily"],
  ["weekly", "Weekly"],
  ["monthly", "Monthly"],
  ["yearly", "Yearly"],
] as [string, string][];

const CAL_RSVP_STATUS = [
  ["accepted", "Accepted"],
  ["tentative", "Tentative"],
  ["declined", "Declined"],
] as [string, string][];

const VIDEO_TYPES = [
  ["event_recording", "Event Recording"],
  ["testimonial", "Testimonial"],
  ["interview", "Interview"],
  ["tutorial", "Tutorial"],
  ["highlights", "Highlights"],
  ["other", "Other"],
] as [string, string][];

const EMAIL_EVENT_TYPES = [
  ["sent", "Sent"],
  ["delivered", "Delivered"],
  ["opened", "Opened"],
  ["clicked", "Clicked"],
  ["bounced", "Bounced"],
  ["unsubscribed", "Unsubscribed"],
  ["spam_report", "Spam Report"],
] as [string, string][];

const PODCAST_EPISODE_TYPES = [
  ["interview", "Interview"],
  ["panel", "Panel"],
  ["solo", "Solo"],
  ["q_and_a", "Q&A"],
  ["other", "Other"],
] as [string, string][];

const PODCAST_STATUS = [
  ["draft", "Draft"],
  ["published", "Published"],
  ["archived", "Archived"],
] as [string, string][];

const AWARD_STATUS = [
  ["nominations_open", "Nominations Open"],
  ["nominations_closed", "Nominations Closed"],
  ["judging", "Judging"],
  ["winners_announced", "Winners Announced"],
  ["completed", "Completed"],
] as [string, string][];

const NOMINATION_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["winner", "Winner"],
  ["runner_up", "Runner Up"],
] as [string, string][];

// ─── Entity configurations (48 tabs) ─────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  profiles: {
    key: "profiles",
    label: "Alumni Profiles",
    icon: UsersIcon,
    endpoint: "profiles",
    titleField: "user_name",
    subtitleField: "user_email",
    toggleField: "is_visible_to_public",
    searchKeys: ["user_name", "user_email", "occupation", "employer", "city", "country"],
    fields: [
      { key: "user", label: "User (ID)", full: true },
      { key: "graduation_year", label: "Graduation Year", type: "number" },
      { key: "student_id", label: "Student ID" },
      { key: "occupation", label: "Occupation", card: true },
      { key: "employer", label: "Employer", card: true },
      {
        key: "employment_status",
        label: "Employment Status",
        type: "select",
        options: EMPLOYMENT_STATUS,
        badge: true,
      },
      { key: "phone", label: "Phone" },
      { key: "city", label: "City", card: true },
      { key: "country", label: "Country", card: true },
      { key: "address", label: "Address", full: true },
      { key: "linkedin_url", label: "LinkedIn URL", full: true },
      { key: "facebook_url", label: "Facebook URL", full: true },
      { key: "twitter_handle", label: "Twitter Handle" },
      { key: "bio", label: "Bio", type: "textarea", full: true },
      { key: "skills", label: "Skills", full: true },
      { key: "interests", label: "Interests", full: true },
      {
        key: "is_newsletter_subscribed",
        label: "Newsletter Subscribed",
        type: "bool",
      },
      { key: "is_visible_to_public", label: "Visible To Public", type: "bool" },
      {
        key: "engagement_score",
        label: "Engagement Score",
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
  },
  verifications: {
    key: "verifications",
    label: "Verifications",
    icon: ShieldCheckIcon,
    endpoint: "verifications",
    titleField: "alumni_name",
    subtitleField: "verification_method_display",
    searchKeys: ["alumni_name", "status", "verification_method_display"],
    fields: [
      { key: "alumni", label: "Alumni (Profile ID)", full: true },
      {
        key: "verification_method",
        label: "Method",
        type: "select",
        options: VERIFY_METHOD,
      },
      { key: "verification_method_display", label: "Method", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: VERIFY_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "document_url", label: "Document URL", full: true },
      { key: "verified_by", label: "Verified By (User ID)" },
      { key: "verified_by_name", label: "Verified By", skipForm: true },
      {
        key: "rejection_reason",
        label: "Rejection Reason",
        type: "textarea",
        full: true,
      },
      { key: "expires_at", label: "Expires At", type: "datetime" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      {
        key: "verified_at",
        label: "Verified At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  events: {
    key: "events",
    label: "Events",
    icon: CalendarDaysIcon,
    endpoint: "events",
    titleField: "title",
    subtitleField: "location",
    searchKeys: ["title", "location", "venue", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "event_date", label: "Event Date", type: "datetime", card: true },
      { key: "end_date", label: "End Date", type: "datetime" },
      { key: "location", label: "Location" },
      { key: "venue", label: "Venue" },
      { key: "max_attendees", label: "Max Attendees", type: "number" },
      {
        key: "registration_deadline",
        label: "Registration Deadline",
        type: "datetime",
      },
      { key: "fee_amount", label: "Fee Amount", type: "number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: EVENT_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "organizer", label: "Organizer (User ID)" },
      { key: "organizer_name", label: "Organizer", skipForm: true },
      { key: "cover_image_url", label: "Cover Image URL", full: true },
      { key: "rsvp_count", label: "RSVPs", skipForm: true, card: true },
    ],
  },
  rsvps: {
    key: "rsvps",
    label: "Event RSVPs",
    icon: TicketIcon,
    endpoint: "rsvps",
    titleField: "event_title",
    subtitleField: "alumni_name",
    searchKeys: ["event_title", "alumni_name", "status"],
    fields: [
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
      { key: "alumni", label: "Alumni (Profile ID)" },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: RSVP_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      {
        key: "registered_at",
        label: "Registered At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      {
        key: "checked_in_at",
        label: "Checked In At",
        type: "datetime",
        skipForm: true,
      },
    ],
  },
  donations: {
    key: "donations",
    label: "Donations",
    icon: CurrencyDollarIcon,
    endpoint: "donations",
    titleField: "alumni_name",
    subtitleField: "amount",
    searchKeys: ["alumni_name", "fund_type_display", "transaction_id"],
    fields: [
      { key: "alumni", label: "Alumni (Profile ID)", full: true },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      { key: "amount", label: "Amount", type: "number", card: true },
      {
        key: "fund_type",
        label: "Fund Type",
        type: "select",
        options: FUND_TYPES,
        badge: true,
      },
      { key: "fund_type_display", label: "Fund Type", skipForm: true },
      {
        key: "payment_method",
        label: "Payment Method",
        type: "select",
        options: PAYMENT_METHODS,
      },
      { key: "transaction_id", label: "Transaction ID" },
      {
        key: "donation_date",
        label: "Donation Date",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      { key: "is_anonymous", label: "Anonymous", type: "bool" },
      { key: "is_recurring", label: "Recurring", type: "bool" },
      {
        key: "recurring_frequency",
        label: "Recurring Frequency",
        type: "select",
        options: RECUR_FREQUENCY,
      },
      { key: "message", label: "Message", type: "textarea", full: true },
    ],
  },
  receipts: {
    key: "receipts",
    label: "Donation Receipts",
    icon: ReceiptPercentIcon,
    endpoint: "receipts",
    titleField: "receipt_number",
    subtitleField: "alumni_name",
    searchKeys: ["receipt_number", "alumni_name", "status"],
    fields: [
      { key: "donation", label: "Donation (ID)", full: true },
      {
        key: "donation_amount",
        label: "Amount",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      { key: "receipt_number", label: "Receipt #", skipForm: true },
      {
        key: "receipt_date",
        label: "Receipt Date",
        type: "datetime",
        skipForm: true,
      },
      {
        key: "tax_deductible_amount",
        label: "Tax-Deductible Amount",
        type: "number",
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: RECEIPT_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "pdf_url", label: "PDF URL", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "recurring-donations": {
    key: "recurring-donations",
    label: "Recurring Donations",
    icon: ArrowPathIcon,
    endpoint: "recurring-donations",
    titleField: "alumni_name",
    subtitleField: "amount",
    searchKeys: ["alumni_name", "fund_type_display", "status"],
    fields: [
      { key: "alumni", label: "Alumni (Profile ID)", full: true },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      {
        key: "fund_type",
        label: "Fund Type",
        type: "select",
        options: FUND_TYPES,
        badge: true,
      },
      { key: "fund_type_display", label: "Fund Type", skipForm: true },
      { key: "amount", label: "Amount", type: "number", card: true },
      {
        key: "frequency",
        label: "Frequency",
        type: "select",
        options: RECUR_FREQUENCY,
      },
      { key: "frequency_display", label: "Frequency", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: RECUR_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "start_date", label: "Start Date", type: "date" },
      {
        key: "next_payment_date",
        label: "Next Payment",
        type: "date",
        card: true,
      },
      {
        key: "last_payment_date",
        label: "Last Payment",
        type: "date",
        skipForm: true,
      },
      { key: "end_date", label: "End Date", type: "date" },
      {
        key: "payment_method",
        label: "Payment Method",
        type: "select",
        options: PAYMENT_METHODS,
      },
      { key: "total_paid", label: "Total Paid", skipForm: true, card: true },
      { key: "total_payments", label: "Total Payments", skipForm: true },
      { key: "failed_payments", label: "Failed Payments", skipForm: true },
      { key: "is_anonymous", label: "Anonymous", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  chapters: {
    key: "chapters",
    label: "Chapters",
    icon: GlobeAltIcon,
    endpoint: "chapters",
    titleField: "name",
    subtitleField: "city",
    toggleField: "is_active",
    searchKeys: ["name", "city", "country", "president_name"],
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "city", label: "City", card: true },
      { key: "country", label: "Country", card: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "president", label: "President (Profile ID)" },
      { key: "president_name", label: "President", skipForm: true },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "member_count", label: "Members", skipForm: true, card: true },
    ],
  },
  "chapter-members": {
    key: "chapter-members",
    label: "Chapter Members",
    icon: UserGroupIcon,
    endpoint: "chapter-members",
    titleField: "alumni_name",
    subtitleField: "chapter_name",
    searchKeys: ["alumni_name", "chapter_name", "role_display"],
    fields: [
      { key: "chapter", label: "Chapter (ID)", full: true },
      { key: "chapter_name", label: "Chapter", skipForm: true },
      { key: "alumni", label: "Alumni (Profile ID)" },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      {
        key: "role",
        label: "Role",
        type: "select",
        options: CHAPTER_ROLES,
        badge: true,
      },
      { key: "role_display", label: "Role", skipForm: true },
      { key: "is_active", label: "Active", type: "bool" },
      {
        key: "joined_at",
        label: "Joined At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  mentorships: {
    key: "mentorships",
    label: "Mentorships",
    icon: AcademicCapIcon,
    endpoint: "mentorships",
    titleField: "mentor_name",
    subtitleField: "mentee_name",
    searchKeys: ["mentor_name", "mentee_name", "focus_area_display", "status"],
    fields: [
      { key: "mentor", label: "Mentor (Profile ID)", full: true },
      { key: "mentor_name", label: "Mentor", skipForm: true },
      { key: "mentee", label: "Mentee (Profile ID)" },
      { key: "mentee_name", label: "Mentee", skipForm: true },
      {
        key: "focus_area",
        label: "Focus Area",
        type: "select",
        options: MENTOR_FOCUS,
        badge: true,
      },
      { key: "focus_area_display", label: "Focus Area", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: MENTOR_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "start_date", label: "Start Date", type: "date", card: true },
      { key: "end_date", label: "End Date", type: "date" },
      {
        key: "meeting_frequency",
        label: "Meeting Frequency",
        type: "select",
        options: MEETING_FREQ,
      },
      { key: "goals", label: "Goals", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  "job-postings": {
    key: "job-postings",
    label: "Job Postings",
    icon: BriefcaseIcon,
    endpoint: "job-postings",
    titleField: "title",
    subtitleField: "company",
    searchKeys: ["title", "company", "location", "status", "posted_by_name"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "company", label: "Company", card: true },
      { key: "posted_by", label: "Posted By (Profile ID)" },
      { key: "posted_by_name", label: "Posted By", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "location", label: "Location", card: true },
      { key: "is_remote", label: "Remote", type: "bool" },
      {
        key: "job_type",
        label: "Job Type",
        type: "select",
        options: JOB_TYPES,
        badge: true,
      },
      { key: "job_type_display", label: "Job Type", skipForm: true },
      {
        key: "experience_level",
        label: "Experience Level",
        type: "select",
        options: EXPERIENCE_LEVELS,
      },
      { key: "experience_level_display", label: "Experience", skipForm: true },
      { key: "salary_min", label: "Salary Min", type: "number" },
      { key: "salary_max", label: "Salary Max", type: "number" },
      { key: "application_url", label: "Application URL", full: true },
      { key: "application_email", label: "Application Email" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: JOB_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "expires_at", label: "Expires At", type: "datetime" },
      {
        key: "application_count",
        label: "Applications",
        skipForm: true,
        card: true,
      },
    ],
  },
  "job-applications": {
    key: "job-applications",
    label: "Job Applications",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "job-applications",
    titleField: "job_title",
    subtitleField: "applicant_name",
    searchKeys: ["job_title", "applicant_name", "status"],
    fields: [
      { key: "job", label: "Job (ID)", full: true },
      { key: "job_title", label: "Job", skipForm: true },
      { key: "company_name", label: "Company", skipForm: true, card: true },
      { key: "applicant", label: "Applicant (Profile ID)" },
      { key: "applicant_name", label: "Applicant", skipForm: true },
      { key: "resume_url", label: "Resume URL", full: true },
      {
        key: "cover_letter",
        label: "Cover Letter",
        type: "textarea",
        full: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: APPLICATION_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      {
        key: "applied_at",
        label: "Applied At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  discussions: {
    key: "discussions",
    label: "Discussions",
    icon: ChatBubbleLeftRightIcon,
    endpoint: "discussions",
    titleField: "title",
    subtitleField: "author_name",
    searchKeys: ["title", "author_name", "category_display", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "author", label: "Author (Profile ID)" },
      { key: "author_name", label: "Author", skipForm: true },
      { key: "content", label: "Content", type: "textarea", full: true },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: DISCUSSION_CATEGORIES,
        badge: true,
      },
      { key: "category_display", label: "Category", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: DISCUSSION_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "is_anonymous", label: "Anonymous", type: "bool" },
      { key: "views_count", label: "Views", skipForm: true, card: true },
      { key: "likes_count", label: "Likes", skipForm: true },
      { key: "reply_count", label: "Replies", skipForm: true, card: true },
    ],
  },
  "discussion-replies": {
    key: "discussion-replies",
    label: "Discussion Replies",
    icon: ChatBubbleOvalLeftIcon,
    endpoint: "discussion-replies",
    titleField: "author_name",
    subtitleField: "discussion",
    searchKeys: ["author_name", "content"],
    fields: [
      { key: "discussion", label: "Discussion (ID)", full: true },
      { key: "author", label: "Author (Profile ID)" },
      { key: "author_name", label: "Author", skipForm: true },
      { key: "content", label: "Content", type: "textarea", full: true },
      { key: "parent", label: "Parent Reply (ID)" },
      { key: "is_anonymous", label: "Anonymous", type: "bool" },
      { key: "likes_count", label: "Likes", skipForm: true, card: true },
      { key: "children_count", label: "Replies", skipForm: true },
    ],
  },
  "discussion-likes": {
    key: "discussion-likes",
    label: "Discussion Likes",
    icon: HeartIcon,
    endpoint: "discussion-likes",
    titleField: "alumni_name",
    subtitleField: "target_type",
    searchKeys: ["alumni_name", "target_type"],
    fields: [
      { key: "alumni", label: "Alumni (Profile ID)", full: true },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      {
        key: "target_type",
        label: "Target Type",
        type: "select",
        options: [
          ["discussion", "Discussion"],
          ["reply", "Reply"],
        ],
        badge: true,
      },
      { key: "discussion", label: "Discussion (ID)" },
      { key: "reply", label: "Reply (ID)" },
      {
        key: "created_at",
        label: "Liked At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  newsletters: {
    key: "newsletters",
    label: "Newsletters",
    icon: NewspaperIcon,
    endpoint: "newsletters",
    titleField: "title",
    subtitleField: "subject",
    searchKeys: ["title", "subject", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "subject", label: "Subject", card: true },
      { key: "content", label: "Content", type: "textarea", full: true },
      { key: "plain_text", label: "Plain Text", type: "textarea", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: NEWSLETTER_STATUS,
        badge: true,
      },
      { key: "scheduled_at", label: "Scheduled At", type: "datetime" },
      { key: "target_graduation_years", label: "Target Grad Years" },
      { key: "target_cities", label: "Target Cities" },
      { key: "total_sent", label: "Sent", skipForm: true, card: true },
      { key: "total_opened", label: "Opened", skipForm: true },
      { key: "total_clicked", label: "Clicked", skipForm: true },
      { key: "total_bounced", label: "Bounced", skipForm: true },
      { key: "total_unsubscribed", label: "Unsubscribed", skipForm: true },
      { key: "open_rate", label: "Open Rate", skipForm: true, card: true },
      { key: "click_rate", label: "Click Rate", skipForm: true },
      { key: "created_by", label: "Created By (User ID)", skipForm: true },
      { key: "created_by_name", label: "Created By", skipForm: true },
    ],
  },
  campaigns: {
    key: "campaigns",
    label: "Fundraising Campaigns",
    icon: MegaphoneIcon,
    endpoint: "campaigns",
    titleField: "title",
    subtitleField: "campaign_type_display",
    searchKeys: ["title", "campaign_type_display", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "campaign_type",
        label: "Type",
        type: "select",
        options: CAMPAIGN_TYPES,
        badge: true,
      },
      { key: "campaign_type_display", label: "Type", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CAMPAIGN_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "goal_amount", label: "Goal Amount", type: "number", card: true },
      { key: "raised_amount", label: "Raised", skipForm: true, card: true },
      { key: "donor_count", label: "Donors", skipForm: true },
      {
        key: "progress_percentage",
        label: "Progress %",
        skipForm: true,
        card: true,
      },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "has_matching", label: "Has Matching", type: "bool" },
      {
        key: "matching_multiplier",
        label: "Matching Multiplier",
        type: "number",
      },
      { key: "matching_deadline", label: "Matching Deadline", type: "date" },
      { key: "cover_image_url", label: "Cover Image URL", full: true },
      { key: "video_url", label: "Video URL", full: true },
      { key: "is_anonymous_allowed", label: "Anonymous Allowed", type: "bool" },
      { key: "is_recurring_allowed", label: "Recurring Allowed", type: "bool" },
      { key: "created_by", label: "Created By (User ID)", skipForm: true },
      { key: "created_by_name", label: "Created By", skipForm: true },
    ],
  },
  "campaign-donations": {
    key: "campaign-donations",
    label: "Campaign Donations",
    icon: BanknotesIcon,
    endpoint: "campaign-donations",
    titleField: "campaign_title",
    subtitleField: "donation_amount",
    searchKeys: ["campaign_title", "donation_amount"],
    fields: [
      { key: "campaign", label: "Campaign (ID)", full: true },
      { key: "campaign_title", label: "Campaign", skipForm: true },
      { key: "donation", label: "Donation (ID)" },
      {
        key: "donation_amount",
        label: "Amount",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "is_matching", label: "Matching", type: "bool" },
      {
        key: "created_at",
        label: "Created At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  badges: {
    key: "badges",
    label: "Badges",
    icon: SparklesIcon,
    endpoint: "badges",
    titleField: "name",
    subtitleField: "badge_type_display",
    toggleField: "is_active",
    searchKeys: ["name", "badge_type_display", "description"],
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "badge_type",
        label: "Type",
        type: "select",
        options: BADGE_TYPES,
        badge: true,
      },
      { key: "badge_type_display", label: "Type", skipForm: true },
      { key: "icon_url", label: "Icon URL", full: true },
      { key: "color", label: "Color" },
      {
        key: "criteria_description",
        label: "Criteria Description",
        type: "textarea",
        full: true,
      },
      { key: "criteria_value", label: "Criteria Value", type: "number" },
      { key: "total_awarded", label: "Awarded", skipForm: true, card: true },
      { key: "is_active", label: "Active", type: "bool" },
    ],
  },
  "badge-awards": {
    key: "badge-awards",
    label: "Badge Awards",
    icon: CheckBadgeIcon,
    endpoint: "badge-awards",
    titleField: "badge_name",
    subtitleField: "alumni_name",
    searchKeys: ["badge_name", "alumni_name", "awarded_by_name"],
    fields: [
      { key: "badge", label: "Badge (ID)", full: true },
      { key: "badge_name", label: "Badge", skipForm: true },
      { key: "alumni", label: "Alumni (Profile ID)" },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      { key: "awarded_by", label: "Awarded By (User ID)" },
      { key: "awarded_by_name", label: "Awarded By", skipForm: true },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      { key: "is_public", label: "Public", type: "bool" },
      {
        key: "awarded_at",
        label: "Awarded At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "activity-feed": {
    key: "activity-feed",
    label: "Activity Feed",
    icon: QueueListIcon,
    endpoint: "activity-feed",
    titleField: "title",
    subtitleField: "alumni_name",
    readOnly: true,
    searchKeys: ["title", "alumni_name", "activity_type_display"],
    fields: [
      { key: "alumni", label: "Alumni (Profile ID)", full: true },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      {
        key: "activity_type",
        label: "Activity Type",
        type: "select",
        options: ACTIVITY_TYPES,
        badge: true,
      },
      { key: "activity_type_display", label: "Activity", skipForm: true },
      { key: "title", label: "Title", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "reference_id", label: "Reference ID" },
      { key: "reference_model", label: "Reference Model" },
      { key: "is_visible", label: "Visible", type: "bool" },
      {
        key: "created_at",
        label: "Created At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  groups: {
    key: "groups",
    label: "Groups",
    icon: UserGroupIcon,
    endpoint: "groups",
    titleField: "name",
    subtitleField: "group_type_display",
    searchKeys: ["name", "group_type_display", "admin_name"],
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "group_type",
        label: "Type",
        type: "select",
        options: GROUP_TYPES,
        badge: true,
      },
      { key: "group_type_display", label: "Type", skipForm: true },
      { key: "admin", label: "Admin (Profile ID)" },
      { key: "admin_name", label: "Admin", skipForm: true },
      { key: "is_private", label: "Private", type: "bool" },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "max_members", label: "Max Members", type: "number" },
      { key: "member_count", label: "Members", skipForm: true, card: true },
      { key: "cover_image_url", label: "Cover Image URL", full: true },
      { key: "logo_url", label: "Logo URL", full: true },
    ],
  },
  "group-members": {
    key: "group-members",
    label: "Group Members",
    icon: UsersIcon,
    endpoint: "group-members",
    titleField: "alumni_name",
    subtitleField: "group_name",
    toggleField: "is_muted",
    searchKeys: ["alumni_name", "group_name", "role_display", "status"],
    fields: [
      { key: "group", label: "Group (ID)", full: true },
      { key: "group_name", label: "Group", skipForm: true },
      { key: "alumni", label: "Alumni (Profile ID)" },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      {
        key: "role",
        label: "Role",
        type: "select",
        options: GROUP_MEMBER_ROLES,
        badge: true,
      },
      { key: "role_display", label: "Role", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: GROUP_MEMBER_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "is_muted", label: "Muted", type: "bool" },
      {
        key: "joined_at",
        label: "Joined At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "group-posts": {
    key: "group-posts",
    label: "Group Posts",
    icon: DocumentTextIcon,
    endpoint: "group-posts",
    titleField: "title",
    subtitleField: "author_name",
    toggleField: "is_pinned",
    searchKeys: ["title", "author_name", "group_name"],
    fields: [
      { key: "group", label: "Group (ID)", full: true },
      { key: "group_name", label: "Group", skipForm: true },
      { key: "author", label: "Author (Profile ID)" },
      { key: "author_name", label: "Author", skipForm: true },
      { key: "title", label: "Title", main: true },
      { key: "content", label: "Content", type: "textarea", full: true },
      { key: "attachment_url", label: "Attachment URL", full: true },
      { key: "is_pinned", label: "Pinned", type: "bool" },
      { key: "likes_count", label: "Likes", skipForm: true, card: true },
      { key: "comments_count", label: "Comments", skipForm: true },
    ],
  },
  "volunteer-opportunities": {
    key: "volunteer-opportunities",
    label: "Volunteer Opportunities",
    icon: HandRaisedIcon,
    endpoint: "volunteer-opportunities",
    titleField: "title",
    subtitleField: "location",
    searchKeys: ["title", "location", "status", "organizer_name"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "skills_required", label: "Skills Required", full: true },
      { key: "max_volunteers", label: "Max Volunteers", type: "number" },
      {
        key: "current_volunteers",
        label: "Current Volunteers",
        skipForm: true,
        card: true,
      },
      { key: "start_date", label: "Start Date", type: "date", card: true },
      { key: "end_date", label: "End Date", type: "date" },
      {
        key: "time_commitment",
        label: "Time Commitment",
        type: "select",
        options: TIME_COMMITMENTS,
      },
      {
        key: "time_commitment_display",
        label: "Time Commitment",
        skipForm: true,
      },
      { key: "estimated_hours", label: "Estimated Hours", type: "number" },
      { key: "location", label: "Location", card: true },
      { key: "is_remote", label: "Remote", type: "bool" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: VOLUNTEER_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "organizer", label: "Organizer (User ID)" },
      { key: "organizer_name", label: "Organizer", skipForm: true },
    ],
  },
  "volunteer-signups": {
    key: "volunteer-signups",
    label: "Volunteer Signups",
    icon: GiftIcon,
    endpoint: "volunteer-signups",
    titleField: "opportunity_title",
    subtitleField: "alumni_name",
    searchKeys: ["opportunity_title", "alumni_name", "status"],
    fields: [
      { key: "opportunity", label: "Opportunity (ID)", full: true },
      { key: "opportunity_title", label: "Opportunity", skipForm: true },
      { key: "alumni", label: "Alumni (Profile ID)" },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: VOLUNTEER_SIGNUP_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      {
        key: "hours_logged",
        label: "Hours Logged",
        type: "number",
        card: true,
      },
      { key: "feedback", label: "Feedback", type: "textarea", full: true },
      { key: "rating", label: "Rating", type: "number" },
      {
        key: "signed_up_at",
        label: "Signed Up At",
        type: "datetime",
        skipForm: true,
      },
      {
        key: "completed_at",
        label: "Completed At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  polls: {
    key: "polls",
    label: "Polls & Surveys",
    icon: ListBulletIcon,
    endpoint: "polls",
    titleField: "title",
    subtitleField: "poll_type_display",
    searchKeys: ["title", "poll_type_display", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "poll_type",
        label: "Type",
        type: "select",
        options: POLL_TYPES,
        badge: true,
      },
      { key: "poll_type_display", label: "Type", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: POLL_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "is_anonymous", label: "Anonymous", type: "bool" },
      {
        key: "allow_multiple_answers",
        label: "Multiple Answers",
        type: "bool",
      },
      { key: "start_date", label: "Start Date", type: "datetime", card: true },
      { key: "end_date", label: "End Date", type: "datetime" },
      {
        key: "total_responses",
        label: "Responses",
        skipForm: true,
        card: true,
      },
      { key: "created_by", label: "Created By (User ID)", skipForm: true },
      { key: "created_by_name", label: "Created By", skipForm: true },
    ],
  },
  "poll-options": {
    key: "poll-options",
    label: "Poll Options",
    icon: TagIcon,
    endpoint: "poll-options",
    titleField: "text",
    subtitleField: "poll_title",
    searchKeys: ["text", "poll_title"],
    fields: [
      { key: "poll", label: "Poll (ID)", full: true },
      { key: "poll_title", label: "Poll", skipForm: true },
      { key: "text", label: "Option Text", main: true },
      { key: "order", label: "Order", type: "number" },
      { key: "vote_count", label: "Votes", skipForm: true, card: true },
    ],
  },
  "poll-responses": {
    key: "poll-responses",
    label: "Poll Responses",
    icon: CheckBadgeIcon,
    endpoint: "poll-responses",
    titleField: "alumni_name",
    subtitleField: "poll",
    searchKeys: ["alumni_name", "option_text"],
    fields: [
      { key: "poll", label: "Poll (ID)", full: true },
      { key: "alumni", label: "Alumni (Profile ID)" },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      { key: "option", label: "Option (ID)" },
      { key: "option_text", label: "Option", card: true, skipForm: true },
      {
        key: "text_response",
        label: "Text Response",
        type: "textarea",
        full: true,
      },
      {
        key: "responded_at",
        label: "Responded At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "success-stories": {
    key: "success-stories",
    label: "Success Stories",
    icon: StarIcon,
    endpoint: "success-stories",
    titleField: "title",
    subtitleField: "alumni_name",
    searchKeys: ["title", "alumni_name", "story_type_display", "status"],
    fields: [
      { key: "alumni", label: "Alumni (Profile ID)", full: true },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      { key: "title", label: "Title", main: true },
      { key: "content", label: "Content", type: "textarea", full: true },
      {
        key: "story_type",
        label: "Story Type",
        type: "select",
        options: STORY_TYPES,
        badge: true,
      },
      { key: "story_type_display", label: "Story Type", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: STORY_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "cover_image_url", label: "Cover Image URL", full: true },
      { key: "video_url", label: "Video URL", full: true },
      { key: "featured", label: "Featured", type: "bool" },
      { key: "slug", label: "Slug" },
      {
        key: "meta_description",
        label: "Meta Description",
        type: "textarea",
        full: true,
      },
      { key: "views_count", label: "Views", skipForm: true, card: true },
      { key: "likes_count", label: "Likes", skipForm: true },
      {
        key: "published_at",
        label: "Published At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  referrals: {
    key: "referrals",
    label: "Referrals",
    icon: PaperAirplaneIcon,
    endpoint: "referrals",
    titleField: "referred_name",
    subtitleField: "referrer_name",
    searchKeys: ["referred_name", "referrer_name", "referral_type_display", "status"],
    fields: [
      { key: "referrer", label: "Referrer (Profile ID)", full: true },
      { key: "referrer_name", label: "Referrer", skipForm: true },
      { key: "referred_name", label: "Referred Name", main: true },
      { key: "referred_email", label: "Referred Email" },
      { key: "referred_phone", label: "Referred Phone" },
      {
        key: "referral_type",
        label: "Type",
        type: "select",
        options: REFERRAL_TYPES,
        badge: true,
      },
      { key: "referral_type_display", label: "Type", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: REFERRAL_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
      { key: "job_posting", label: "Job Posting (ID)" },
      { key: "job_title", label: "Job Title", skipForm: true },
      {
        key: "reward_points",
        label: "Reward Points",
        type: "number",
        card: true,
      },
      { key: "reward_description", label: "Reward Description", full: true },
      {
        key: "referred_at",
        label: "Referred At",
        type: "datetime",
        skipForm: true,
      },
      {
        key: "contacted_at",
        label: "Contacted At",
        type: "datetime",
        skipForm: true,
      },
      {
        key: "converted_at",
        label: "Converted At",
        type: "datetime",
        skipForm: true,
      },
    ],
  },
  messages: {
    key: "messages",
    label: "Direct Messages",
    icon: ChatBubbleOvalLeftIcon,
    endpoint: "messages",
    titleField: "sender_name",
    subtitleField: "receiver_name",
    searchKeys: ["sender_name", "receiver_name", "message_type_display", "content"],
    fields: [
      { key: "sender", label: "Sender (Profile ID)", full: true },
      { key: "sender_name", label: "Sender", skipForm: true },
      { key: "receiver", label: "Receiver (Profile ID)" },
      { key: "receiver_name", label: "Receiver", skipForm: true },
      {
        key: "message_type",
        label: "Type",
        type: "select",
        options: MESSAGE_TYPES,
        badge: true,
      },
      { key: "message_type_display", label: "Type", skipForm: true },
      { key: "content", label: "Content", type: "textarea", full: true },
      { key: "attachment_url", label: "Attachment URL", full: true },
      { key: "is_read", label: "Read", type: "bool" },
      { key: "read_at", label: "Read At", type: "datetime", skipForm: true },
      {
        key: "created_at",
        label: "Sent At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  conversations: {
    key: "conversations",
    label: "Conversations",
    icon: ChatBubbleLeftRightIcon,
    endpoint: "conversations",
    titleField: "participant1_name",
    subtitleField: "participant2_name",
    searchKeys: ["participant1_name", "participant2_name"],
    fields: [
      { key: "participant1", label: "Participant 1 (Profile ID)", full: true },
      { key: "participant1_name", label: "Participant 1", skipForm: true },
      { key: "participant2", label: "Participant 2 (Profile ID)" },
      { key: "participant2_name", label: "Participant 2", skipForm: true },
      { key: "last_message", label: "Last Message (ID)", skipForm: true },
      {
        key: "last_message_content",
        label: "Last Message",
        skipForm: true,
        card: true,
      },
      {
        key: "last_message_at",
        label: "Last Message At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      { key: "is_archived_by_p1", label: "Archived By P1", type: "bool" },
      { key: "is_archived_by_p2", label: "Archived By P2", type: "bool" },
    ],
  },
  "calendar-events": {
    key: "calendar-events",
    label: "Calendar Events",
    icon: CalendarDaysIcon,
    endpoint: "calendar-events",
    titleField: "title",
    subtitleField: "event_type_display",
    searchKeys: ["title", "event_type_display", "location", "organizer_name"],
    fields: [
      { key: "title", label: "Title", main: true },
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
        options: CALENDAR_EVENT_TYPES,
        badge: true,
      },
      { key: "event_type_display", label: "Type", skipForm: true },
      { key: "start_datetime", label: "Start", type: "datetime", card: true },
      { key: "end_datetime", label: "End", type: "datetime" },
      { key: "all_day", label: "All Day", type: "bool" },
      { key: "timezone", label: "Timezone" },
      {
        key: "recurrence_type",
        label: "Recurrence",
        type: "select",
        options: RECURRENCE_TYPES,
      },
      { key: "recurrence_type_display", label: "Recurrence", skipForm: true },
      { key: "recurrence_end_date", label: "Recurrence End", type: "date" },
      { key: "location", label: "Location", card: true },
      { key: "venue", label: "Venue" },
      { key: "is_virtual", label: "Virtual", type: "bool" },
      { key: "virtual_link", label: "Virtual Link", full: true },
      { key: "max_attendees", label: "Max Attendees", type: "number" },
      {
        key: "requires_registration",
        label: "Requires Registration",
        type: "bool",
      },
      {
        key: "registration_deadline",
        label: "Registration Deadline",
        type: "datetime",
      },
      { key: "organizer", label: "Organizer (User ID)" },
      { key: "organizer_name", label: "Organizer", skipForm: true },
      { key: "is_published", label: "Published", type: "bool" },
      { key: "ical_uid", label: "iCal UID", skipForm: true },
    ],
  },
  "calendar-rsvps": {
    key: "calendar-rsvps",
    label: "Calendar RSVPs",
    icon: TicketIcon,
    endpoint: "calendar-rsvps",
    titleField: "event_title",
    subtitleField: "alumni_name",
    searchKeys: ["event_title", "alumni_name", "status"],
    fields: [
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
      { key: "alumni", label: "Alumni (Profile ID)" },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CAL_RSVP_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      {
        key: "responded_at",
        label: "Responded At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "photo-albums": {
    key: "photo-albums",
    label: "Photo Albums",
    icon: FolderOpenIcon,
    endpoint: "photo-albums",
    titleField: "title",
    subtitleField: "event",
    toggleField: "is_public",
    searchKeys: ["title", "description", "created_by_name"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "event", label: "Event (ID)" },
      { key: "cover_photo_url", label: "Cover Photo URL", full: true },
      { key: "is_public", label: "Public", type: "bool" },
      { key: "photo_count", label: "Photos", skipForm: true, card: true },
      { key: "created_by", label: "Created By (User ID)", skipForm: true },
      { key: "created_by_name", label: "Created By", skipForm: true },
    ],
  },
  photos: {
    key: "photos",
    label: "Photos",
    icon: PhotoIcon,
    endpoint: "photos",
    titleField: "caption",
    subtitleField: "album_title",
    toggleField: "is_featured",
    searchKeys: ["caption", "album_title", "uploaded_by_name"],
    fields: [
      { key: "album", label: "Album (ID)", full: true },
      { key: "album_title", label: "Album", skipForm: true },
      { key: "photo_url", label: "Photo URL", full: true },
      { key: "thumbnail_url", label: "Thumbnail URL", full: true },
      { key: "caption", label: "Caption", main: true },
      { key: "uploaded_by", label: "Uploaded By (User ID)" },
      { key: "uploaded_by_name", label: "Uploaded By", skipForm: true },
      { key: "is_featured", label: "Featured", type: "bool" },
      { key: "likes_count", label: "Likes", skipForm: true, card: true },
      { key: "comments_count", label: "Comments", skipForm: true },
      {
        key: "uploaded_at",
        label: "Uploaded At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "photo-comments": {
    key: "photo-comments",
    label: "Photo Comments",
    icon: ChatBubbleOvalLeftIcon,
    endpoint: "photo-comments",
    titleField: "author_name",
    subtitleField: "content",
    searchKeys: ["author_name", "content"],
    fields: [
      { key: "photo", label: "Photo (ID)", full: true },
      { key: "author", label: "Author (Profile ID)" },
      { key: "author_name", label: "Author", skipForm: true },
      { key: "content", label: "Comment", type: "textarea", full: true },
      {
        key: "created_at",
        label: "Created At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  videos: {
    key: "videos",
    label: "Video Gallery",
    icon: VideoCameraIcon,
    endpoint: "videos",
    titleField: "title",
    subtitleField: "video_type_display",
    toggleField: "is_featured",
    searchKeys: ["title", "video_type_display", "uploaded_by_name", "tags"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "video_type",
        label: "Type",
        type: "select",
        options: VIDEO_TYPES,
        badge: true,
      },
      { key: "video_type_display", label: "Type", skipForm: true },
      { key: "video_url", label: "Video URL", full: true },
      { key: "thumbnail_url", label: "Thumbnail URL", full: true },
      { key: "duration_seconds", label: "Duration (s)", type: "number" },
      {
        key: "duration_formatted",
        label: "Duration",
        skipForm: true,
        card: true,
      },
      { key: "view_count", label: "Views", skipForm: true, card: true },
      { key: "like_count", label: "Likes", skipForm: true },
      { key: "event", label: "Event (ID)" },
      { key: "uploaded_by", label: "Uploaded By (User ID)" },
      { key: "uploaded_by_name", label: "Uploaded By", skipForm: true },
      { key: "is_featured", label: "Featured", type: "bool" },
      { key: "tags", label: "Tags", full: true },
      {
        key: "uploaded_at",
        label: "Uploaded At",
        type: "datetime",
        skipForm: true,
      },
    ],
  },
  "directory-filters": {
    key: "directory-filters",
    label: "Directory Filters",
    icon: FunnelIcon,
    endpoint: "directory-filters",
    titleField: "name",
    subtitleField: "alumni_name",
    toggleField: "is_public",
    searchKeys: ["name", "alumni_name"],
    fields: [
      { key: "alumni", label: "Alumni (Profile ID)", full: true },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      { key: "name", label: "Name", main: true },
      { key: "graduation_year_min", label: "Grad Year Min", type: "number" },
      { key: "graduation_year_max", label: "Grad Year Max", type: "number" },
      { key: "cities", label: "Cities", full: true },
      { key: "countries", label: "Countries", full: true },
      { key: "industries", label: "Industries", full: true },
      { key: "companies", label: "Companies", full: true },
      { key: "skills", label: "Skills", full: true },
      {
        key: "employment_status",
        label: "Employment Status",
        type: "select",
        options: EMPLOYMENT_STATUS,
      },
      { key: "is_public", label: "Public", type: "bool" },
    ],
  },
  "profile-views": {
    key: "profile-views",
    label: "Profile Views",
    icon: EyeIcon,
    endpoint: "profile-views",
    titleField: "viewer_name",
    subtitleField: "viewed_name",
    readOnly: true,
    searchKeys: ["viewer_name", "viewed_name"],
    fields: [
      { key: "viewer", label: "Viewer (Profile ID)", full: true },
      { key: "viewer_name", label: "Viewer", skipForm: true },
      { key: "viewed", label: "Viewed (Profile ID)" },
      { key: "viewed_name", label: "Viewed", skipForm: true },
      {
        key: "viewed_at",
        label: "Viewed At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "profile-completeness": {
    key: "profile-completeness",
    label: "Profile Completeness",
    icon: ArrowTrendingUpIcon,
    endpoint: "profile-completeness",
    titleField: "alumni_name",
    subtitleField: "completion_percentage",
    readOnly: true,
    searchKeys: ["alumni_name"],
    fields: [
      { key: "alumni", label: "Alumni (Profile ID)", full: true },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      { key: "has_photo", label: "Has Photo", type: "bool" },
      { key: "has_bio", label: "Has Bio", type: "bool" },
      { key: "has_occupation", label: "Has Occupation", type: "bool" },
      { key: "has_employer", label: "Has Employer", type: "bool" },
      { key: "has_phone", label: "Has Phone", type: "bool" },
      { key: "has_address", label: "Has Address", type: "bool" },
      { key: "has_linkedin", label: "Has LinkedIn", type: "bool" },
      { key: "has_skills", label: "Has Skills", type: "bool" },
      { key: "has_interests", label: "Has Interests", type: "bool" },
      { key: "has_graduation_year", label: "Has Grad Year", type: "bool" },
      {
        key: "completion_percentage",
        label: "Completion %",
        card: true,
        skipForm: true,
      },
      {
        key: "last_calculated_at",
        label: "Calculated At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "email-analytics": {
    key: "email-analytics",
    label: "Email Analytics",
    icon: InboxIcon,
    endpoint: "email-analytics",
    titleField: "newsletter_title",
    subtitleField: "event_type_display",
    readOnly: true,
    searchKeys: ["newsletter_title", "alumni_name", "event_type_display"],
    fields: [
      { key: "newsletter", label: "Newsletter (ID)", full: true },
      { key: "newsletter_title", label: "Newsletter", skipForm: true },
      { key: "alumni", label: "Alumni (Profile ID)" },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      {
        key: "event_type",
        label: "Event Type",
        type: "select",
        options: EMAIL_EVENT_TYPES,
        badge: true,
      },
      { key: "event_type_display", label: "Event", skipForm: true },
      { key: "ip_address", label: "IP Address", card: true },
      { key: "user_agent", label: "User Agent", full: true },
      { key: "link_url", label: "Link URL", full: true },
      {
        key: "bounce_reason",
        label: "Bounce Reason",
        type: "textarea",
        full: true,
      },
      {
        key: "event_at",
        label: "Event At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "podcast-episodes": {
    key: "podcast-episodes",
    label: "Podcast Episodes",
    icon: MicrophoneIcon,
    endpoint: "podcast-episodes",
    titleField: "title",
    subtitleField: "episode_type_display",
    searchKeys: ["title", "episode_type_display", "status", "host_name", "tags"],
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "episode_type",
        label: "Type",
        type: "select",
        options: PODCAST_EPISODE_TYPES,
        badge: true,
      },
      { key: "episode_type_display", label: "Type", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: PODCAST_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "audio_url", label: "Audio URL", full: true },
      { key: "thumbnail_url", label: "Thumbnail URL", full: true },
      { key: "duration_seconds", label: "Duration (s)", type: "number" },
      {
        key: "duration_formatted",
        label: "Duration",
        skipForm: true,
        card: true,
      },
      { key: "host", label: "Host (Profile ID)" },
      { key: "host_name", label: "Host", skipForm: true },
      { key: "guests", label: "Guests (Profile IDs)", full: true },
      { key: "guest_names", label: "Guest Names", full: true },
      { key: "play_count", label: "Plays", skipForm: true, card: true },
      { key: "like_count", label: "Likes", skipForm: true },
      { key: "download_count", label: "Downloads", skipForm: true },
      { key: "episode_number", label: "Episode #", type: "number" },
      { key: "season_number", label: "Season #", type: "number" },
      { key: "tags", label: "Tags", full: true },
      {
        key: "published_at",
        label: "Published At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "podcast-subscriptions": {
    key: "podcast-subscriptions",
    label: "Podcast Subscriptions",
    icon: BellAlertIcon,
    endpoint: "podcast-subscriptions",
    titleField: "alumni_name",
    toggleField: "is_active",
    searchKeys: ["alumni_name"],
    fields: [
      { key: "alumni", label: "Alumni (Profile ID)", full: true },
      { key: "alumni_name", label: "Alumni", skipForm: true },
      { key: "is_active", label: "Active", type: "bool" },
      {
        key: "subscribed_at",
        label: "Subscribed At",
        type: "datetime",
        card: true,
        skipForm: true,
      },
    ],
  },
  "award-categories": {
    key: "award-categories",
    label: "Award Categories",
    icon: TagIcon,
    endpoint: "award-categories",
    titleField: "name",
    toggleField: "is_active",
    searchKeys: ["name", "description"],
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "icon_url", label: "Icon URL", full: true },
      { key: "is_active", label: "Active", type: "bool" },
    ],
  },
  awards: {
    key: "awards",
    label: "Awards",
    icon: TrophyIcon,
    endpoint: "awards",
    titleField: "title",
    subtitleField: "category_name",
    searchKeys: ["title", "category_name", "status", "year"],
    fields: [
      { key: "category", label: "Category (ID)", full: true },
      { key: "category_name", label: "Category", skipForm: true },
      { key: "title", label: "Title", main: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "year", label: "Year", type: "number", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: AWARD_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      {
        key: "nominations_start",
        label: "Nominations Start",
        type: "datetime",
      },
      { key: "nominations_end", label: "Nominations End", type: "datetime" },
      { key: "judging_end", label: "Judging End", type: "datetime" },
      {
        key: "announcement_date",
        label: "Announcement Date",
        type: "datetime",
        card: true,
      },
      { key: "ceremony_date", label: "Ceremony Date", type: "datetime" },
      {
        key: "max_nominations_per_person",
        label: "Max Nominations/Person",
        type: "number",
      },
      {
        key: "requires_nomination_statement",
        label: "Requires Statement",
        type: "bool",
      },
      {
        key: "total_nominations",
        label: "Nominations",
        skipForm: true,
        card: true,
      },
      { key: "created_by", label: "Created By (User ID)", skipForm: true },
    ],
  },
  "award-nominations": {
    key: "award-nominations",
    label: "Award Nominations",
    icon: StarIcon,
    endpoint: "award-nominations",
    titleField: "award_title",
    subtitleField: "nominee_name",
    searchKeys: ["award_title", "nominee_name", "nominated_by_name", "status"],
    fields: [
      { key: "award", label: "Award (ID)", full: true },
      { key: "award_title", label: "Award", skipForm: true },
      { key: "nominee", label: "Nominee (Profile ID)" },
      { key: "nominee_name", label: "Nominee", skipForm: true },
      { key: "nominated_by", label: "Nominated By (Profile ID)" },
      { key: "nominated_by_name", label: "Nominated By", skipForm: true },
      { key: "statement", label: "Statement", type: "textarea", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: NOMINATION_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status Label", skipForm: true },
      { key: "evidence_urls", label: "Evidence URLs", full: true },
      { key: "score", label: "Score", type: "number", card: true },
      {
        key: "judge_notes",
        label: "Judge Notes",
        type: "textarea",
        full: true,
      },
      {
        key: "nominated_at",
        label: "Nominated At",
        type: "datetime",
        skipForm: true,
      },
      {
        key: "reviewed_at",
        label: "Reviewed At",
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

export default function AlumniPage() {
  useTitle("Alumni Center");
  const [activeTab, setActiveTab] = useState("profiles");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Alumni Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Profiles, events, donations, chapters, mentorships, jobs, groups, media and awards
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
        basePath="/alumni"
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
