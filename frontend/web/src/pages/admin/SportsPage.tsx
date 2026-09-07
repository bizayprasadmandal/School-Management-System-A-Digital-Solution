/**
 * Sports Center — full-surface admin page for the sports module.
 *
 * 51 entity tabs (config-driven via EntitySection): sports, teams, members,
 * events, achievements, registrations, attendance, practices, statistics,
 * rosters, lineups, injuries, medical clearances, equipment, uniform orders,
 * league standings, communications, photos, fundraising, sponsorships,
 * travel, volunteers, analytics, referees, facility bookings, live scores,
 * video analysis, wearables, development plans, tryouts, season passes,
 * schedule conflicts, refunds, compliance, weather alerts, live streams,
 * suspensions, tournaments, merchandise, insurance, eligibility, transfers,
 * season archives, badges, and leaderboards.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, TrophyIcon } from "@heroicons/react/24/outline";
import {
  UsersIcon,
  CalendarDaysIcon,
  ClipboardDocumentCheckIcon,
  ClipboardDocumentListIcon,
  UserGroupIcon,
  StarIcon,
  HeartIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
  ChartBarIcon,
  PhotoIcon,
  CurrencyDollarIcon,
  HandRaisedIcon,
  MapPinIcon,
  VideoCameraIcon,
  SignalIcon,
  ClockIcon,
  GlobeAltIcon,
  TicketIcon,
  ArrowsRightLeftIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon,
  ShoppingBagIcon,
  ShoppingCartIcon,
  BanknotesIcon,
  ScaleIcon,
  CloudIcon,
  AcademicCapIcon,
  FireIcon,
  BeakerIcon,
  PlayCircleIcon,
  FlagIcon,
  IdentificationIcon,
  InboxIcon,
  QueueListIcon,
  SparklesIcon,
  CheckBadgeIcon,
  PresentationChartLineIcon,
  WrenchScrewdriverIcon,
  ComputerDesktopIcon,
  WifiIcon,
  TruckIcon,
  ChatBubbleLeftRightIcon,
  BellAlertIcon,
  CheckCircleIcon,
  ArchiveBoxIcon,
  ListBulletIcon,
  Squares2X2Icon,
  UserPlusIcon,
  BuildingStorefrontIcon,
  ReceiptPercentIcon,
  LifebuoyIcon,
  TagIcon,
} from "@heroicons/react/24/outline";

// ─── Shared option sets ──────────────────────────────────────────────────────

const SPORT_CATEGORY = [
  ["sport", "Sport"],
  ["academic", "Academic"],
  ["arts", "Arts"],
  ["club", "Club"],
  ["other", "Other"],
] as [string, string][];

const GENDER = [
  ["boys", "Boys"],
  ["girls", "Girls"],
  ["mixed", "Mixed"],
] as [string, string][];

const TEAM_ROLE = [
  ["captain", "Captain"],
  ["vice_captain", "Vice Captain"],
  ["member", "Member"],
] as [string, string][];

const MEMBER_STATUS = [
  ["active", "Active"],
  ["inactive", "Inactive"],
  ["dropped", "Dropped"],
] as [string, string][];

const EVENT_STATUS = [
  ["scheduled", "Scheduled"],
  ["ongoing", "Ongoing"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const APPROVAL_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["waitlisted", "Waitlisted"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const PAY_STATUS = [
  ["unpaid", "Unpaid"],
  ["paid", "Paid"],
  ["waived", "Waived"],
  ["refunded", "Refunded"],
] as [string, string][];

const ATTENDANCE_STATUS = [
  ["present", "Present"],
  ["absent", "Absent"],
  ["tardy", "Tardy"],
  ["excused", "Excused"],
  ["injured", "Injured"],
] as [string, string][];

const SESSION_TYPE = [
  ["practice", "Practice"],
  ["game", "Game"],
  ["tryout", "Tryout"],
  ["conditioning", "Conditioning"],
  ["other", "Other"],
] as [string, string][];

const PRACTICE_TYPE = [
  ["regular", "Regular"],
  ["conditioning", "Conditioning"],
  ["scrimmage", "Scrimmage"],
  ["film", "Film"],
  ["meeting", "Meeting"],
  ["other", "Other"],
] as [string, string][];

const DAY_OF_WEEK = [
  ["monday", "Monday"],
  ["tuesday", "Tuesday"],
  ["wednesday", "Wednesday"],
  ["thursday", "Thursday"],
  ["friday", "Friday"],
  ["saturday", "Saturday"],
  ["sunday", "Sunday"],
] as [string, string][];

const EQUIPMENT_TYPE = [
  ["ball", "Ball"],
  ["uniform", "Uniform"],
  ["protective", "Protective"],
  ["training", "Training"],
  ["maintenance", "Maintenance"],
  ["other", "Other"],
] as [string, string][];

const CONDITION = [
  ["new", "New"],
  ["good", "Good"],
  ["fair", "Fair"],
  ["poor", "Poor"],
  ["retired", "Retired"],
] as [string, string][];

const INJURY_TYPE = [
  ["sprain", "Sprain"],
  ["strain", "Strain"],
  ["fracture", "Fracture"],
  ["concussion", "Concussion"],
  ["bruise", "Bruise"],
  ["cut", "Cut"],
  ["other", "Other"],
] as [string, string][];

const SEVERITY = [
  ["minor", "Minor"],
  ["moderate", "Moderate"],
  ["severe", "Severe"],
  ["critical", "Critical"],
] as [string, string][];

const INJURY_STATUS = [
  ["active", "Active"],
  ["recovering", "Recovering"],
  ["cleared", "Cleared"],
  ["chronic", "Chronic"],
] as [string, string][];

const CLEARANCE_TYPE = [
  ["physical", "Physical"],
  ["concussion", "Concussion"],
  ["cardiac", "Cardiac"],
  ["allergy", "Allergy"],
  ["other", "Other"],
] as [string, string][];

const CLEARANCE_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["expired", "Expired"],
  ["denied", "Denied"],
] as [string, string][];

const UNIFORM_STATUS = [
  ["pending", "Pending"],
  ["sizing", "Sizing"],
  ["ordered", "Ordered"],
  ["shipped", "Shipped"],
  ["delivered", "Delivered"],
  ["completed", "Completed"],
] as [string, string][];

const ROSTER_TYPE = [
  ["varsity", "Varsity"],
  ["jv", "JV"],
  ["freshman", "Freshman"],
  ["club", "Club"],
] as [string, string][];

const MESSAGE_TYPE = [
  ["announcement", "Announcement"],
  ["message", "Message"],
  ["reminder", "Reminder"],
  ["alert", "Alert"],
] as [string, string][];

const AUDIENCE = [
  ["all", "All"],
  ["players", "Players"],
  ["coaches", "Coaches"],
  ["parents", "Parents"],
] as [string, string][];

const PHOTO_TYPE = [
  ["team", "Team"],
  ["game", "Game"],
  ["practice", "Practice"],
  ["award", "Award"],
  ["event", "Event"],
  ["other", "Other"],
] as [string, string][];

const CAMPAIGN_TYPE = [
  ["equipment", "Equipment"],
  ["travel", "Travel"],
  ["fees", "Fees"],
  ["facility", "Facility"],
  ["other", "Other"],
] as [string, string][];

const CAMPAIGN_STATUS = [
  ["planning", "Planning"],
  ["active", "Active"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const SPONSOR_LEVEL = [
  ["platinum", "Platinum"],
  ["gold", "Gold"],
  ["silver", "Silver"],
  ["bronze", "Bronze"],
  ["custom", "Custom"],
] as [string, string][];

const SPONSOR_STATUS = [
  ["pending", "Pending"],
  ["active", "Active"],
  ["expired", "Expired"],
  ["renewed", "Renewed"],
] as [string, string][];

const TRAVEL_TYPE = [
  ["bus", "Bus"],
  ["van", "Van"],
  ["carpool", "Carpool"],
  ["flight", "Flight"],
  ["other", "Other"],
] as [string, string][];

const TRAVEL_STATUS = [
  ["planned", "Planned"],
  ["confirmed", "Confirmed"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const VOLUNTEER_TYPE = [
  ["coach", "Coach"],
  ["assistant", "Assistant"],
  ["scorekeeper", "Scorekeeper"],
  ["timer", "Timer"],
  ["chaperone", "Chaperone"],
  ["fundraiser", "Fundraiser"],
  ["other", "Other"],
] as [string, string][];

const VOLUNTEER_STATUS = [
  ["interested", "Interested"],
  ["approved", "Approved"],
  ["active", "Active"],
  ["inactive", "Inactive"],
] as [string, string][];

const ANALYTICS_TYPE = [
  ["team_performance", "Team Performance"],
  ["player_stats", "Player Stats"],
  ["win_loss", "Win/Loss"],
  ["scoring_trends", "Scoring Trends"],
  ["attendance", "Attendance"],
  ["injury", "Injury"],
  ["opponent", "Opponent"],
] as [string, string][];

const REFEREE_TYPE = [
  ["referee", "Referee"],
  ["umpire", "Umpire"],
  ["line_judge", "Line Judge"],
  ["official", "Official"],
  ["other", "Other"],
] as [string, string][];

const CERT_LEVEL = [
  ["entry", "Entry"],
  ["intermediate", "Intermediate"],
  ["advanced", "Advanced"],
  ["elite", "Elite"],
] as [string, string][];

const REFEREE_STATUS = [
  ["active", "Active"],
  ["inactive", "Inactive"],
  ["suspended", "Suspended"],
] as [string, string][];

const ASSIGN_STATUS = [
  ["pending", "Pending"],
  ["confirmed", "Confirmed"],
  ["declined", "Declined"],
  ["completed", "Completed"],
] as [string, string][];

const FACILITY_TYPE = [
  ["field", "Field"],
  ["court", "Court"],
  ["gym", "Gym"],
  ["pool", "Pool"],
  ["track", "Track"],
  ["other", "Other"],
] as [string, string][];

const BOOKING_STATUS = [
  ["pending", "Pending"],
  ["confirmed", "Confirmed"],
  ["cancelled", "Cancelled"],
  ["completed", "Completed"],
] as [string, string][];

const LIVE_STATUS = [
  ["pre_game", "Pre-Game"],
  ["live", "Live"],
  ["halftime", "Halftime"],
  ["final", "Final"],
  ["postponed", "Postponed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const VIDEO_TYPE = [
  ["game", "Game"],
  ["practice", "Practice"],
  ["highlight", "Highlight"],
  ["breakdown", "Breakdown"],
  ["other", "Other"],
] as [string, string][];

const VIDEO_STATUS = [
  ["uploading", "Uploading"],
  ["processing", "Processing"],
  ["ready", "Ready"],
  ["failed", "Failed"],
] as [string, string][];

const DEVICE_TYPE = [
  ["apple_watch", "Apple Watch"],
  ["fitbit", "Fitbit"],
  ["garmin", "Garmin"],
  ["whoop", "Whoop"],
  ["catapult", "Catapult"],
  ["other", "Other"],
] as [string, string][];

const SYNC_STATUS = [
  ["connected", "Connected"],
  ["disconnected", "Disconnected"],
  ["syncing", "Syncing"],
  ["error", "Error"],
] as [string, string][];

const DEV_PHASE = [
  ["fundamentals", "Fundamentals"],
  ["skill_development", "Skill Development"],
  ["competitive", "Competitive"],
  ["elite", "Elite"],
  ["maintenance", "Maintenance"],
] as [string, string][];

const DEV_STATUS = [
  ["active", "Active"],
  ["completed", "Completed"],
  ["on_hold", "On Hold"],
] as [string, string][];

const TRYOUT_STATUS = [
  ["scheduled", "Scheduled"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const SELECTION_STATUS = [
  ["pending", "Pending"],
  ["selected", "Selected"],
  ["alternate", "Alternate"],
  ["not_selected", "Not Selected"],
] as [string, string][];

const MEMBERSHIP_TYPE = [
  ["player", "Player"],
  ["family", "Family"],
  ["coach", "Coach"],
  ["supporter", "Supporter"],
  ["lifetime", "Lifetime"],
] as [string, string][];

const PASS_STATUS = [
  ["active", "Active"],
  ["expired", "Expired"],
  ["cancelled", "Cancelled"],
  ["suspended", "Suspended"],
] as [string, string][];

const CONFLICT_TYPE = [
  ["venue", "Venue"],
  ["player", "Player"],
  ["coach", "Coach"],
  ["facility", "Facility"],
  ["other", "Other"],
] as [string, string][];

const CONFLICT_STATUS = [
  ["detected", "Detected"],
  ["resolved", "Resolved"],
  ["ignored", "Ignored"],
] as [string, string][];

const REFUND_REASON = [
  ["injury", "Injury"],
  ["schedule", "Schedule"],
  ["dissatisfaction", "Dissatisfaction"],
  ["duplicate", "Duplicate"],
  ["other", "Other"],
] as [string, string][];

const REFUND_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["denied", "Denied"],
  ["processed", "Processed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const COMPLIANCE_TYPE = [
  ["background_check", "Background Check"],
  ["first_aid", "First Aid"],
  ["cpr", "CPR"],
  ["safeguarding", "Safeguarding"],
  ["concussion", "Concussion"],
  ["fire_safety", "Fire Safety"],
  ["other", "Other"],
] as [string, string][];

const COMPLIANCE_STATUS = [
  ["valid", "Valid"],
  ["expired", "Expired"],
  ["pending", "Pending"],
  ["suspended", "Suspended"],
] as [string, string][];

const WEATHER = [
  ["clear", "Clear"],
  ["rain", "Rain"],
  ["heavy_rain", "Heavy Rain"],
  ["snow", "Snow"],
  ["storm", "Storm"],
  ["extreme_heat", "Extreme Heat"],
  ["wind", "Wind"],
  ["fog", "Fog"],
  ["other", "Other"],
] as [string, string][];

const WEATHER_ACTION = [
  ["none", "None"],
  ["delayed", "Delayed"],
  ["rescheduled", "Rescheduled"],
  ["cancelled", "Cancelled"],
  ["moved_indoors", "Moved Indoors"],
] as [string, string][];

const STREAM_STATUS = [
  ["scheduled", "Scheduled"],
  ["live", "Live"],
  ["ended", "Ended"],
  ["failed", "Failed"],
] as [string, string][];

const QUALITY = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
  ["auto", "Auto"],
] as [string, string][];

const SUSPENSION_TYPE = [
  ["game", "Game"],
  ["practice", "Practice"],
  ["season", "Season"],
  ["indefinite", "Indefinite"],
  ["other", "Other"],
] as [string, string][];

const SUSPENSION_STATUS = [
  ["active", "Active"],
  ["appealed", "Appealed"],
  ["lifted", "Lifted"],
  ["expired", "Expired"],
] as [string, string][];

const BRACKET_TYPE = [
  ["single", "Single Elimination"],
  ["double", "Double Elimination"],
  ["round_robin", "Round Robin"],
  ["swiss", "Swiss"],
  ["other", "Other"],
] as [string, string][];

const BRACKET_STATUS = [
  ["draft", "Draft"],
  ["published", "Published"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
] as [string, string][];

const MATCH_STATUS = [
  ["scheduled", "Scheduled"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
  ["bye", "Bye"],
  ["forfeit", "Forfeit"],
] as [string, string][];

const PRODUCT_TYPE = [
  ["jersey", "Jersey"],
  ["shorts", "Shorts"],
  ["jacket", "Jacket"],
  ["cap", "Cap"],
  ["bag", "Bag"],
  ["accessory", "Accessory"],
  ["other", "Other"],
] as [string, string][];

const STORE_STATUS = [
  ["active", "Active"],
  ["out_of_stock", "Out of Stock"],
  ["discontinued", "Discontinued"],
] as [string, string][];

const ORDER_STATUS = [
  ["pending", "Pending"],
  ["confirmed", "Confirmed"],
  ["shipped", "Shipped"],
  ["delivered", "Delivered"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const ORDER_PAY = [
  ["unpaid", "Unpaid"],
  ["paid", "Paid"],
  ["refunded", "Refunded"],
] as [string, string][];

const INSURANCE_TYPE = [
  ["personal", "Personal"],
  ["school", "School"],
  ["athletic", "Athletic"],
  ["other", "Other"],
] as [string, string][];

const INSURANCE_STATUS = [
  ["active", "Active"],
  ["expired", "Expired"],
  ["pending", "Pending"],
  ["denied", "Denied"],
] as [string, string][];

const RULE_TYPE = [
  ["academic", "Academic"],
  ["age", "Age"],
  ["grade", "Grade"],
  ["attendance", "Attendance"],
  ["other", "Other"],
] as [string, string][];

const RULE_STATUS = [
  ["active", "Active"],
  ["inactive", "Inactive"],
] as [string, string][];

const ELIGIBILITY_STATUS = [
  ["eligible", "Eligible"],
  ["ineligible", "Ineligible"],
  ["probation", "Probation"],
  ["pending", "Pending"],
] as [string, string][];

const TRANSFER_TYPE = [
  ["internal", "Internal"],
  ["external", "External"],
  ["loan", "Loan"],
  ["other", "Other"],
] as [string, string][];

const TRANSFER_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const BADGE_TYPE = [
  ["participation", "Participation"],
  ["achievement", "Achievement"],
  ["milestone", "Milestone"],
  ["special", "Special"],
  ["team", "Team"],
] as [string, string][];

const LEADERBOARD_TYPE = [
  ["points", "Points"],
  ["wins", "Wins"],
  ["goals", "Goals"],
  ["attendance", "Attendance"],
  ["academic", "Academic"],
  ["overall", "Overall"],
] as [string, string][];

const FK_ID = (key: string) => ({
  key,
  label: `${key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, " ")} (ID)`,
  full: true,
});

// ─── Entity configs ──────────────────────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  sports: {
    key: "sports",
    label: "Sports",
    icon: TrophyIcon,
    endpoint: "sports",
    titleField: "name",
    subtitleField: "category_display",
    searchKeys: ["name", "description"],
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: SPORT_CATEGORY,
        badge: true,
      },
      { key: "category_display", label: "Category", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "min_players", label: "Min Players", type: "number" },
      { key: "max_players", label: "Max Players", type: "number" },
      { key: "team_count", label: "Teams", skipForm: true },
      { key: "is_active", label: "Active", type: "bool" },
    ],
  },
  teams: {
    key: "teams",
    label: "Teams",
    icon: UsersIcon,
    endpoint: "teams",
    titleField: "name",
    subtitleField: "sport_name",
    searchKeys: ["name", "sport_name", "coach_name"],
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "sport", label: "Sport (ID)", full: true },
      { key: "sport_name", label: "Sport", skipForm: true },
      {
        key: "gender",
        label: "Gender",
        type: "select",
        options: GENDER,
        badge: true,
      },
      { key: "gender_display", label: "Gender", skipForm: true },
      { key: "coach", label: "Coach (ID)", full: true },
      { key: "coach_name", label: "Coach", skipForm: true },
      { key: "assistant_coach", label: "Assistant Coach (ID)", full: true },
      { key: "member_count", label: "Members", skipForm: true },
      { key: "is_active", label: "Active", type: "bool" },
    ],
  },
  teamMembers: {
    key: "teamMembers",
    label: "Team Members",
    icon: UserGroupIcon,
    endpoint: "team-members",
    titleField: "student_name",
    subtitleField: "role_display",
    searchKeys: ["student_name", "role", "status"],
    fields: [
      FK_ID("team"),
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "role",
        label: "Role",
        type: "select",
        options: TEAM_ROLE,
        badge: true,
      },
      { key: "role_display", label: "Role", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: MEMBER_STATUS,
        badge: true,
      },
      { key: "joined_date", label: "Joined", type: "date", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  events: {
    key: "events",
    label: "Events",
    icon: CalendarDaysIcon,
    endpoint: "events",
    titleField: "title",
    subtitleField: "sport_name",
    searchKeys: ["title", "opponent", "location", "team_name"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "sport", label: "Sport (ID)", full: true },
      { key: "sport_name", label: "Sport", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "event_type", label: "Event Type" },
      { key: "opponent", label: "Opponent", card: true },
      { key: "location", label: "Location", card: true },
      { key: "event_date", label: "Date", type: "date", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: EVENT_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "home_score", label: "Home Score", type: "number" },
      { key: "opponent_score", label: "Opponent Score", type: "number" },
      { key: "result", label: "Result" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  achievements: {
    key: "achievements",
    label: "Achievements",
    icon: StarIcon,
    endpoint: "achievements",
    titleField: "title",
    subtitleField: "student_name",
    searchKeys: ["title", "student_name", "team_name", "level"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "position", label: "Position", card: true },
      { key: "level", label: "Level", card: true },
      { key: "awarded_date", label: "Awarded", type: "date", card: true },
      { key: "certificate_url", label: "Certificate URL", full: true },
    ],
  },
  registrations: {
    key: "registrations",
    label: "Registrations",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "registrations",
    titleField: "student_name",
    subtitleField: "sport_name",
    searchKeys: ["student_name", "sport_name", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "sport", label: "Sport (ID)", full: true },
      { key: "sport_name", label: "Sport", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "registration_type",
        label: "Type",
        type: "select",
        options: [
          ["individual", "Individual"],
          ["team", "Team"],
          ["season", "Season"],
          ["tryout", "Tryout"],
        ] as [string, string][],
        badge: true,
      },
      { key: "registration_type_display", label: "Type", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: APPROVAL_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "season", label: "Season", card: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "fee_amount", label: "Fee", type: "number" },
      {
        key: "payment_status",
        label: "Payment",
        type: "select",
        options: PAY_STATUS,
        badge: true,
      },
      { key: "emergency_contact", label: "Emergency Contact" },
      { key: "emergency_phone", label: "Emergency Phone" },
      { key: "parent_name", label: "Parent Name" },
      { key: "parent_email", label: "Parent Email" },
      { key: "parent_phone", label: "Parent Phone" },
      { key: "parent_consent", label: "Parent Consent", type: "bool" },
      { key: "consent_form_signed", label: "Consent Signed", type: "bool" },
      { key: "physical_exam_date", label: "Physical Exam Date", type: "date" },
      { key: "physical_exam_expiry", label: "Physical Expiry", type: "date" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  attendance: {
    key: "attendance",
    label: "Attendance",
    icon: ClipboardDocumentListIcon,
    endpoint: "attendance",
    titleField: "student_name",
    subtitleField: "session_type_display",
    searchKeys: ["student_name", "status", "date"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "session_type",
        label: "Session Type",
        type: "select",
        options: SESSION_TYPE,
        badge: true,
      },
      { key: "session_type_display", label: "Session Type", skipForm: true },
      { key: "practice", label: "Practice (ID)", full: true },
      { key: "event", label: "Event (ID)", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ATTENDANCE_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "minutes_late", label: "Minutes Late", type: "number" },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  practices: {
    key: "practices",
    label: "Practices",
    icon: ClockIcon,
    endpoint: "practices",
    titleField: "team_name",
    subtitleField: "practice_type_display",
    searchKeys: ["team_name", "location", "day_of_week"],
    toggleField: "is_active",
    fields: [
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "practice_type",
        label: "Type",
        type: "select",
        options: PRACTICE_TYPE,
        badge: true,
      },
      { key: "practice_type_display", label: "Type", skipForm: true },
      {
        key: "day_of_week",
        label: "Day",
        type: "select",
        options: DAY_OF_WEEK,
        badge: true,
      },
      { key: "day_of_week_display", label: "Day", skipForm: true },
      { key: "start_time", label: "Start Time", card: true },
      { key: "end_time", label: "End Time", card: true },
      { key: "location", label: "Location", card: true },
      { key: "field_court", label: "Field/Court" },
      { key: "is_recurring", label: "Recurring", type: "bool" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "required", label: "Required", type: "bool" },
      { key: "min_attendance", label: "Min Attendance", type: "number" },
      { key: "coach", label: "Coach (ID)", full: true },
      { key: "coach_name", label: "Coach", skipForm: true },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  statistics: {
    key: "statistics",
    label: "Player Stats",
    icon: ChartBarIcon,
    endpoint: "statistics",
    titleField: "student_name",
    subtitleField: "academic_year",
    searchKeys: ["student_name", "team_name", "season"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
      { key: "games_played", label: "GP", type: "number", card: true },
      { key: "games_started", label: "GS", type: "number" },
      { key: "minutes_played", label: "Minutes", type: "number" },
      { key: "goals", label: "Goals", type: "number", card: true },
      { key: "assists", label: "Assists", type: "number", card: true },
      { key: "points", label: "Points", type: "number", card: true },
      { key: "rebounds", label: "Rebounds", type: "number" },
      { key: "steals", label: "Steals", type: "number" },
      { key: "blocks", label: "Blocks", type: "number" },
      { key: "turnovers", label: "Turnovers", type: "number" },
      { key: "fouls", label: "Fouls", type: "number" },
      { key: "rating", label: "Rating", type: "number" },
      { key: "season", label: "Season" },
      { key: "academic_year", label: "Academic Year" },
      { key: "stats", label: "Stats (JSON)", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  rosters: {
    key: "rosters",
    label: "Rosters",
    icon: ListBulletIcon,
    endpoint: "rosters",
    titleField: "team_name",
    subtitleField: "roster_type_display",
    searchKeys: ["team_name", "season", "roster_type"],
    fields: [
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "roster_type",
        label: "Type",
        type: "select",
        options: ROSTER_TYPE,
        badge: true,
      },
      { key: "roster_type_display", label: "Type", skipForm: true },
      { key: "season", label: "Season", card: true },
      { key: "academic_year", label: "Academic Year", card: true },
      {
        key: "roster_data",
        label: "Roster Data (JSON)",
        type: "textarea",
        full: true,
      },
      {
        key: "total_players",
        label: "Players",
        type: "number",
        skipForm: true,
      },
      { key: "max_roster_size", label: "Max Size", type: "number" },
      { key: "is_published", label: "Published", type: "bool" },
      { key: "published_at", label: "Published At", type: "datetime" },
    ],
  },
  lineups: {
    key: "lineups",
    label: "Lineups",
    icon: Squares2X2Icon,
    endpoint: "lineups",
    titleField: "student_name",
    subtitleField: "lineup_type_display",
    searchKeys: ["student_name", "event_title", "position"],
    fields: [
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "lineup_type",
        label: "Lineup Type",
        type: "select",
        options: [
          ["starting", "Starting"],
          ["bench", "Bench"],
          ["substitute", "Substitute"],
          ["injured", "Injured"],
          ["scratched", "Scratched"],
        ] as [string, string][],
        badge: true,
      },
      { key: "lineup_type_display", label: "Lineup Type", skipForm: true },
      { key: "position", label: "Position", card: true },
      { key: "jersey_number", label: "Jersey #", type: "number", card: true },
      { key: "subbed_in_at", label: "Subbed In", type: "datetime" },
      { key: "subbed_out_at", label: "Subbed Out", type: "datetime" },
      { key: "substitution_reason", label: "Sub Reason", full: true },
      { key: "minutes_played", label: "Minutes", type: "number" },
      {
        key: "stats_snapshot",
        label: "Stats Snapshot (JSON)",
        type: "textarea",
        full: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  injuries: {
    key: "injuries",
    label: "Injuries",
    icon: HeartIcon,
    endpoint: "injuries",
    titleField: "student_name",
    subtitleField: "injury_type_display",
    searchKeys: ["student_name", "injury_type", "status", "body_part"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "injury_type",
        label: "Type",
        type: "select",
        options: INJURY_TYPE,
        badge: true,
      },
      { key: "injury_type_display", label: "Type", skipForm: true },
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: SEVERITY,
        badge: true,
      },
      { key: "severity_display", label: "Severity", skipForm: true },
      { key: "body_part", label: "Body Part", card: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "injury_date", label: "Injury Date", type: "date", card: true },
      { key: "reported_date", label: "Reported", type: "date" },
      { key: "expected_return", label: "Expected Return", type: "date" },
      { key: "actual_return", label: "Actual Return", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: INJURY_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      {
        key: "treatment_notes",
        label: "Treatment Notes",
        type: "textarea",
        full: true,
      },
      { key: "doctor_name", label: "Doctor Name" },
      { key: "doctor_contact", label: "Doctor Contact" },
      { key: "cleared_by", label: "Cleared By (ID)", full: true },
      { key: "cleared_by_name", label: "Cleared By", skipForm: true },
      { key: "cleared_date", label: "Cleared Date", type: "date" },
      {
        key: "activity_restriction",
        label: "Activity Restriction",
        full: true,
      },
      { key: "medical_report_url", label: "Medical Report URL", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  medicalClearances: {
    key: "medicalClearances",
    label: "Medical Clearances",
    icon: ShieldCheckIcon,
    endpoint: "medical-clearances",
    titleField: "student_name",
    subtitleField: "clearance_type_display",
    searchKeys: ["student_name", "clearance_type", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "clearance_type",
        label: "Type",
        type: "select",
        options: CLEARANCE_TYPE,
        badge: true,
      },
      { key: "clearance_type_display", label: "Type", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CLEARANCE_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "physician_name", label: "Physician", card: true },
      { key: "physician_contact", label: "Physician Contact" },
      { key: "exam_date", label: "Exam Date", type: "date", card: true },
      { key: "expiry_date", label: "Expiry", type: "date" },
      { key: "document_url", label: "Document URL", full: true },
      {
        key: "restrictions",
        label: "Restrictions",
        type: "textarea",
        full: true,
      },
      { key: "cleared_for", label: "Cleared For", full: true },
      { key: "reviewed_by", label: "Reviewed By (ID)", full: true },
      { key: "reviewed_by_name", label: "Reviewed By", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  equipment: {
    key: "equipment",
    label: "Equipment",
    icon: ArchiveBoxIcon,
    endpoint: "equipment",
    titleField: "name",
    subtitleField: "equipment_type_display",
    searchKeys: ["name", "team_name", "vendor", "storage_location"],
    toggleField: "is_available",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "equipment_type",
        label: "Type",
        type: "select",
        options: EQUIPMENT_TYPE,
        badge: true,
      },
      { key: "equipment_type_display", label: "Type", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "quantity", label: "Quantity", type: "number", card: true },
      {
        key: "condition",
        label: "Condition",
        type: "select",
        options: CONDITION,
        badge: true,
      },
      { key: "condition_display", label: "Condition", skipForm: true },
      { key: "purchase_date", label: "Purchased", type: "date" },
      { key: "purchase_price", label: "Price", type: "number" },
      { key: "vendor", label: "Vendor" },
      { key: "last_maintenance", label: "Last Maintenance", type: "date" },
      { key: "next_maintenance", label: "Next Maintenance", type: "date" },
      {
        key: "maintenance_notes",
        label: "Maintenance Notes",
        type: "textarea",
        full: true,
      },
      { key: "storage_location", label: "Storage", card: true },
      { key: "is_available", label: "Available", type: "bool" },
      { key: "assigned_to", label: "Assigned To (ID)", full: true },
      { key: "assigned_to_name", label: "Assigned To", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  uniformOrders: {
    key: "uniformOrders",
    label: "Uniform Orders",
    icon: TagIcon,
    endpoint: "uniform-orders",
    titleField: "student_name",
    subtitleField: "status_display",
    searchKeys: ["student_name", "team_name", "order_number", "vendor"],
    fields: [
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "uniform_type", label: "Uniform Type" },
      { key: "size", label: "Size", card: true },
      { key: "jersey_number", label: "Jersey #", type: "number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: UNIFORM_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "quantity", label: "Quantity", type: "number" },
      { key: "cost", label: "Cost", type: "number" },
      {
        key: "payment_status",
        label: "Payment",
        type: "select",
        options: PAY_STATUS,
        badge: true,
      },
      { key: "ordered_date", label: "Ordered", type: "date" },
      { key: "expected_delivery", label: "Expected Delivery", type: "date" },
      { key: "delivered_date", label: "Delivered", type: "date" },
      { key: "vendor", label: "Vendor" },
      { key: "order_number", label: "Order #", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  leagueStandings: {
    key: "leagueStandings",
    label: "League Standings",
    icon: PresentationChartLineIcon,
    endpoint: "league-standings",
    titleField: "team_name",
    subtitleField: "league_name",
    searchKeys: ["team_name", "league_name", "division", "season"],
    fields: [
      { key: "sport", label: "Sport (ID)", full: true },
      { key: "sport_name", label: "Sport", skipForm: true },
      { key: "league_name", label: "League", main: true },
      { key: "season", label: "Season", card: true },
      { key: "division", label: "Division", card: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "games_played", label: "GP", type: "number" },
      { key: "wins", label: "W", type: "number" },
      { key: "losses", label: "L", type: "number" },
      { key: "ties", label: "T", type: "number" },
      { key: "points_for", label: "PF", type: "number" },
      { key: "points_against", label: "PA", type: "number" },
      { key: "rank", label: "Rank", type: "number", card: true },
      { key: "streak", label: "Streak", card: true },
      { key: "win_percentage", label: "Win %", skipForm: true },
      { key: "point_differential", label: "Diff", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  communications: {
    key: "communications",
    label: "Communications",
    icon: ChatBubbleLeftRightIcon,
    endpoint: "communications",
    titleField: "subject",
    subtitleField: "message_type_display",
    searchKeys: ["subject", "content", "team_name"],
    fields: [
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "message_type",
        label: "Type",
        type: "select",
        options: MESSAGE_TYPE,
        badge: true,
      },
      { key: "message_type_display", label: "Type", skipForm: true },
      {
        key: "target_audience",
        label: "Audience",
        type: "select",
        options: AUDIENCE,
        badge: true,
      },
      { key: "target_audience_display", label: "Audience", skipForm: true },
      { key: "subject", label: "Subject", main: true },
      { key: "content", label: "Content", type: "textarea", full: true },
      { key: "attachment_url", label: "Attachment URL", full: true },
      { key: "is_pinned", label: "Pinned", type: "bool" },
      { key: "send_immediately", label: "Send Immediately", type: "bool" },
      { key: "scheduled_at", label: "Scheduled At", type: "datetime" },
      { key: "sent_at", label: "Sent At", type: "datetime", skipForm: true },
    ],
  },
  photos: {
    key: "photos",
    label: "Photo Gallery",
    icon: PhotoIcon,
    endpoint: "photos",
    titleField: "title",
    subtitleField: "photo_type_display",
    searchKeys: ["title", "team_name", "photographer", "tags"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "photo_type",
        label: "Type",
        type: "select",
        options: PHOTO_TYPE,
        badge: true,
      },
      { key: "photo_type_display", label: "Type", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "photo_url", label: "Photo URL", full: true },
      { key: "thumbnail_url", label: "Thumbnail URL", full: true },
      { key: "photographer", label: "Photographer", card: true },
      { key: "event", label: "Event (ID)", full: true },
      { key: "taken_date", label: "Taken", type: "date" },
      { key: "tags", label: "Tags" },
      { key: "likes_count", label: "Likes", type: "number", skipForm: true },
      {
        key: "comments_count",
        label: "Comments",
        type: "number",
        skipForm: true,
      },
      { key: "is_featured", label: "Featured", type: "bool" },
      { key: "is_public", label: "Public", type: "bool" },
    ],
  },
  fundraising: {
    key: "fundraising",
    label: "Fundraising",
    icon: CurrencyDollarIcon,
    endpoint: "fundraising",
    titleField: "title",
    subtitleField: "campaign_type_display",
    searchKeys: ["title", "team_name", "campaign_type", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "campaign_type",
        label: "Type",
        type: "select",
        options: CAMPAIGN_TYPE,
        badge: true,
      },
      { key: "campaign_type_display", label: "Type", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "goal_amount", label: "Goal", type: "number", card: true },
      { key: "raised_amount", label: "Raised", type: "number", card: true },
      { key: "progress_percentage", label: "Progress %", skipForm: true },
      { key: "start_date", label: "Start", type: "date" },
      { key: "end_date", label: "End", type: "date" },
      { key: "donor_count", label: "Donors", type: "number", skipForm: true },
      { key: "is_online", label: "Online", type: "bool" },
      { key: "online_donation_url", label: "Donation URL", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: CAMPAIGN_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
    ],
  },
  sponsorships: {
    key: "sponsorships",
    label: "Sponsorships",
    icon: HandRaisedIcon,
    endpoint: "sponsorships",
    titleField: "sponsor_name",
    subtitleField: "sponsorship_level_display",
    searchKeys: ["sponsor_name", "contact_name", "status"],
    fields: [
      { key: "sponsor_name", label: "Sponsor", main: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "contact_name", label: "Contact Name", card: true },
      { key: "contact_email", label: "Contact Email" },
      { key: "contact_phone", label: "Contact Phone" },
      { key: "website", label: "Website", full: true },
      {
        key: "sponsorship_level",
        label: "Level",
        type: "select",
        options: SPONSOR_LEVEL,
        badge: true,
      },
      { key: "sponsorship_level_display", label: "Level", skipForm: true },
      { key: "amount", label: "Amount", type: "number" },
      { key: "in_kind_value", label: "In-Kind Value", type: "number" },
      { key: "total_value", label: "Total Value", skipForm: true },
      { key: "start_date", label: "Start", type: "date" },
      { key: "end_date", label: "End", type: "date" },
      { key: "is_recurring", label: "Recurring", type: "bool" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: SPONSOR_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  travel: {
    key: "travel",
    label: "Travel",
    icon: TruckIcon,
    endpoint: "travel",
    titleField: "team_name",
    subtitleField: "travel_type_display",
    searchKeys: ["team_name", "event_title", "hotel_name", "status"],
    fields: [
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
      {
        key: "travel_type",
        label: "Type",
        type: "select",
        options: TRAVEL_TYPE,
        badge: true,
      },
      { key: "travel_type_display", label: "Type", skipForm: true },
      { key: "departure_date", label: "Departure", type: "date", card: true },
      { key: "return_date", label: "Return", type: "date", card: true },
      { key: "vehicle_info", label: "Vehicle" },
      { key: "driver_name", label: "Driver" },
      { key: "driver_contact", label: "Driver Contact" },
      { key: "hotel_name", label: "Hotel", card: true },
      { key: "hotel_address", label: "Hotel Address", full: true },
      { key: "hotel_confirmation", label: "Hotel Confirmation" },
      { key: "meal_plan", label: "Meal Plan" },
      { key: "estimated_cost", label: "Est. Cost", type: "number" },
      { key: "actual_cost", label: "Actual Cost", type: "number" },
      {
        key: "travelers",
        label: "Travelers (JSON)",
        type: "textarea",
        full: true,
      },
      { key: "itinerary_url", label: "Itinerary URL", full: true },
      { key: "emergency_contact", label: "Emergency Contact" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: TRAVEL_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  volunteers: {
    key: "volunteers",
    label: "Volunteers",
    icon: UserPlusIcon,
    endpoint: "volunteers",
    titleField: "parent_name",
    subtitleField: "volunteer_type_display",
    searchKeys: ["parent_name", "student_name", "skills", "status"],
    fields: [
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "parent_name", label: "Parent Name", main: true },
      { key: "parent_email", label: "Email" },
      { key: "parent_phone", label: "Phone" },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "volunteer_type",
        label: "Type",
        type: "select",
        options: VOLUNTEER_TYPE,
        badge: true,
      },
      { key: "volunteer_type_display", label: "Type", skipForm: true },
      { key: "availability", label: "Availability", full: true },
      {
        key: "background_check_complete",
        label: "Background Check",
        type: "bool",
      },
      { key: "background_check_date", label: "Check Date", type: "date" },
      { key: "total_hours", label: "Hours", type: "number", card: true },
      { key: "skills", label: "Skills" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: VOLUNTEER_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  analytics: {
    key: "analytics",
    label: "Analytics",
    icon: ChartBarIcon,
    endpoint: "analytics",
    titleField: "title",
    subtitleField: "analytics_type_display",
    searchKeys: ["title", "team_name", "analytics_type"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "analytics_type",
        label: "Type",
        type: "select",
        options: ANALYTICS_TYPE,
        badge: true,
      },
      { key: "analytics_type_display", label: "Type", skipForm: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      {
        key: "analytics_data",
        label: "Data (JSON)",
        type: "textarea",
        full: true,
      },
      { key: "insights", label: "Insights", type: "textarea", full: true },
      {
        key: "recommendations",
        label: "Recommendations",
        type: "textarea",
        full: true,
      },
      { key: "chart_type", label: "Chart Type" },
      {
        key: "chart_data",
        label: "Chart Data (JSON)",
        type: "textarea",
        full: true,
      },
      {
        key: "key_metrics",
        label: "Key Metrics (JSON)",
        type: "textarea",
        full: true,
      },
      { key: "is_shared", label: "Shared", type: "bool" },
    ],
  },
  referees: {
    key: "referees",
    label: "Referees",
    icon: FlagIcon,
    endpoint: "referees",
    titleField: "full_name",
    subtitleField: "referee_type_display",
    searchKeys: ["first_name", "last_name", "email", "status"],
    fields: [
      { key: "first_name", label: "First Name" },
      { key: "last_name", label: "Last Name" },
      { key: "full_name", label: "Name", main: true, skipForm: true },
      { key: "email", label: "Email", card: true },
      { key: "phone", label: "Phone", card: true },
      {
        key: "referee_type",
        label: "Type",
        type: "select",
        options: REFEREE_TYPE,
        badge: true,
      },
      { key: "referee_type_display", label: "Type", skipForm: true },
      {
        key: "certification_level",
        label: "Cert Level",
        type: "select",
        options: CERT_LEVEL,
        badge: true,
      },
      {
        key: "certification_level_display",
        label: "Cert Level",
        skipForm: true,
      },
      { key: "certification_number", label: "Cert Number" },
      { key: "certification_expiry", label: "Cert Expiry", type: "date" },
      { key: "availability", label: "Availability" },
      { key: "games_officiated", label: "Games", type: "number" },
      { key: "average_rating", label: "Rating", type: "number", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: REFEREE_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  refereeAssignments: {
    key: "refereeAssignments",
    label: "Referee Assignments",
    icon: IdentificationIcon,
    endpoint: "referee-assignments",
    titleField: "referee_name",
    subtitleField: "event_title",
    searchKeys: ["referee_name", "event_title", "role", "status"],
    fields: [
      { key: "referee", label: "Referee (ID)", full: true },
      { key: "referee_name", label: "Referee", skipForm: true },
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
      { key: "role", label: "Role", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ASSIGN_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "fee_amount", label: "Fee", type: "number" },
      {
        key: "payment_status",
        label: "Payment",
        type: "select",
        options: PAY_STATUS,
        badge: true,
      },
      { key: "rating", label: "Rating", type: "number" },
      { key: "comments", label: "Comments", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  facilityBookings: {
    key: "facilityBookings",
    label: "Facility Bookings",
    icon: MapPinIcon,
    endpoint: "facility-bookings",
    titleField: "facility_name",
    subtitleField: "facility_type_display",
    searchKeys: ["facility_name", "location", "team_name", "status"],
    fields: [
      { key: "facility_name", label: "Facility", main: true },
      {
        key: "facility_type",
        label: "Type",
        type: "select",
        options: FACILITY_TYPE,
        badge: true,
      },
      { key: "facility_type_display", label: "Type", skipForm: true },
      { key: "location", label: "Location", card: true },
      { key: "booked_by", label: "Booked By (ID)", full: true },
      { key: "booked_by_name", label: "Booked By", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "start_time", label: "Start Time", card: true },
      { key: "end_time", label: "End Time", card: true },
      { key: "is_recurring", label: "Recurring", type: "bool" },
      { key: "recurrence_pattern", label: "Recurrence" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: BOOKING_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "rental_cost", label: "Rental Cost", type: "number" },
      {
        key: "payment_status",
        label: "Payment",
        type: "select",
        options: PAY_STATUS,
        badge: true,
      },
      { key: "equipment_needed", label: "Equipment Needed", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  liveScores: {
    key: "liveScores",
    label: "Live Scores",
    icon: SignalIcon,
    endpoint: "live-scores",
    titleField: "event_title",
    subtitleField: "status_display",
    searchKeys: ["event_title", "status", "possession"],
    fields: [
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
      { key: "home_score", label: "Home Score", type: "number", card: true },
      { key: "away_score", label: "Away Score", type: "number", card: true },
      { key: "current_period", label: "Period" },
      { key: "period_time", label: "Period Time" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: LIVE_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "possession", label: "Possession" },
      { key: "shots_on_target", label: "Shots on Target", type: "number" },
      { key: "score_diff", label: "Diff", skipForm: true },
      { key: "commentary", label: "Commentary", type: "textarea", full: true },
      { key: "is_public", label: "Public", type: "bool" },
      { key: "auto_update", label: "Auto Update", type: "bool" },
    ],
  },
  videos: {
    key: "videos",
    label: "Video Analysis",
    icon: VideoCameraIcon,
    endpoint: "videos",
    titleField: "title",
    subtitleField: "video_type_display",
    searchKeys: ["title", "team_name", "event_title", "tags"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
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
        options: VIDEO_TYPE,
        badge: true,
      },
      { key: "video_type_display", label: "Type", skipForm: true },
      { key: "video_url", label: "Video URL", full: true },
      { key: "thumbnail_url", label: "Thumbnail URL", full: true },
      { key: "duration_seconds", label: "Duration (s)", type: "number" },
      { key: "duration_formatted", label: "Duration", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: VIDEO_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      {
        key: "analysis_notes",
        label: "Analysis Notes",
        type: "textarea",
        full: true,
      },
      {
        key: "key_moments",
        label: "Key Moments (JSON)",
        type: "textarea",
        full: true,
      },
      { key: "tags", label: "Tags" },
      { key: "is_public", label: "Public", type: "bool" },
    ],
  },
  wearables: {
    key: "wearables",
    label: "Wearables",
    icon: WifiIcon,
    endpoint: "wearables",
    titleField: "student_name",
    subtitleField: "device_type_display",
    searchKeys: ["student_name", "device_type", "device_id"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "device_type",
        label: "Device",
        type: "select",
        options: DEVICE_TYPE,
        badge: true,
      },
      { key: "device_type_display", label: "Device", skipForm: true },
      { key: "device_id", label: "Device ID", card: true },
      {
        key: "sync_status",
        label: "Sync",
        type: "select",
        options: SYNC_STATUS,
        badge: true,
      },
      { key: "sync_status_display", label: "Sync", skipForm: true },
      { key: "last_sync", label: "Last Sync", type: "datetime", card: true },
      { key: "auto_sync", label: "Auto Sync", type: "bool" },
      { key: "share_with_coach", label: "Share with Coach", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  developmentPlans: {
    key: "developmentPlans",
    label: "Development Plans",
    icon: AcademicCapIcon,
    endpoint: "development-plans",
    titleField: "title",
    subtitleField: "student_name",
    searchKeys: ["title", "student_name", "team_name", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "phase",
        label: "Phase",
        type: "select",
        options: DEV_PHASE,
        badge: true,
      },
      { key: "phase_display", label: "Phase", skipForm: true },
      {
        key: "short_term_goals",
        label: "Short-term Goals",
        type: "textarea",
        full: true,
      },
      {
        key: "long_term_goals",
        label: "Long-term Goals",
        type: "textarea",
        full: true,
      },
      {
        key: "baseline_metrics",
        label: "Baseline (JSON)",
        type: "textarea",
        full: true,
      },
      {
        key: "current_metrics",
        label: "Current (JSON)",
        type: "textarea",
        full: true,
      },
      {
        key: "target_metrics",
        label: "Target (JSON)",
        type: "textarea",
        full: true,
      },
      {
        key: "progress_percentage",
        label: "Progress %",
        type: "number",
        card: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: DEV_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "start_date", label: "Start", type: "date" },
      { key: "target_date", label: "Target", type: "date" },
      { key: "review_date", label: "Review", type: "date" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  tryouts: {
    key: "tryouts",
    label: "Tryouts",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "tryouts",
    titleField: "title",
    subtitleField: "sport_name",
    searchKeys: ["title", "sport_name", "team_name", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "sport", label: "Sport (ID)", full: true },
      { key: "sport_name", label: "Sport", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "tryout_date", label: "Date", type: "date", card: true },
      { key: "location", label: "Location", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: TRYOUT_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "max_score", label: "Max Score", type: "number" },
      { key: "passing_score", label: "Passing Score", type: "number" },
      { key: "max_participants", label: "Max Participants", type: "number" },
      { key: "current_participants", label: "Participants", type: "number" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  tryoutScores: {
    key: "tryoutScores",
    label: "Tryout Scores",
    icon: QueueListIcon,
    endpoint: "tryout-scores",
    titleField: "student_name",
    subtitleField: "selection_status_display",
    searchKeys: ["student_name", "tryout_title", "selection_status"],
    fields: [
      { key: "tryout", label: "Tryout (ID)", full: true },
      { key: "tryout_title", label: "Tryout", skipForm: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "total_score", label: "Score", type: "number", card: true },
      {
        key: "category_scores",
        label: "Category Scores (JSON)",
        type: "textarea",
        full: true,
      },
      {
        key: "selection_status",
        label: "Selection",
        type: "select",
        options: SELECTION_STATUS,
        badge: true,
      },
      { key: "selection_status_display", label: "Selection", skipForm: true },
      {
        key: "evaluator_notes",
        label: "Evaluator Notes",
        type: "textarea",
        full: true,
      },
      { key: "strengths", label: "Strengths", type: "textarea", full: true },
      {
        key: "areas_for_improvement",
        label: "Areas for Improvement",
        type: "textarea",
        full: true,
      },
    ],
  },
  seasonPasses: {
    key: "seasonPasses",
    label: "Season Passes",
    icon: TicketIcon,
    endpoint: "season-passes",
    titleField: "student_name",
    subtitleField: "membership_type_display",
    searchKeys: ["student_name", "membership_type", "season", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "membership_type",
        label: "Type",
        type: "select",
        options: MEMBERSHIP_TYPE,
        badge: true,
      },
      { key: "membership_type_display", label: "Type", skipForm: true },
      { key: "season", label: "Season", card: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "amount", label: "Amount", type: "number" },
      { key: "discount_amount", label: "Discount", type: "number" },
      { key: "final_amount", label: "Final Amount", skipForm: true },
      { key: "start_date", label: "Start", type: "date" },
      { key: "end_date", label: "End", type: "date" },
      { key: "auto_renew", label: "Auto Renew", type: "bool" },
      { key: "renewal_date", label: "Renewal Date", type: "date" },
      {
        key: "payment_status",
        label: "Payment",
        type: "select",
        options: ORDER_PAY,
        badge: true,
      },
      { key: "transaction_id", label: "Transaction ID" },
      { key: "benefits", label: "Benefits", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: PASS_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  scheduleConflicts: {
    key: "scheduleConflicts",
    label: "Schedule Conflicts",
    icon: ExclamationTriangleIcon,
    endpoint: "schedule-conflicts",
    titleField: "event_1_title",
    subtitleField: "conflict_type_display",
    searchKeys: ["event_1_title", "event_2_title", "conflict_type", "status"],
    fields: [
      { key: "event_1", label: "Event 1 (ID)", full: true },
      { key: "event_1_title", label: "Event 1", skipForm: true },
      { key: "event_2", label: "Event 2 (ID)", full: true },
      { key: "event_2_title", label: "Event 2", skipForm: true },
      {
        key: "conflict_type",
        label: "Type",
        type: "select",
        options: CONFLICT_TYPE,
        badge: true,
      },
      { key: "conflict_type_display", label: "Type", skipForm: true },
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
        options: CONFLICT_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      {
        key: "resolution_notes",
        label: "Resolution Notes",
        type: "textarea",
        full: true,
      },
      { key: "resolved_by", label: "Resolved By (ID)", full: true },
      { key: "resolved_by_name", label: "Resolved By", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  refunds: {
    key: "refunds",
    label: "Refunds",
    icon: ReceiptPercentIcon,
    endpoint: "refunds",
    titleField: "student_name",
    subtitleField: "status_display",
    searchKeys: ["student_name", "refund_reason", "status"],
    fields: [
      { key: "requested_by", label: "Requested By (ID)", full: true },
      { key: "requested_by_name", label: "Requested By", skipForm: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "registration", label: "Registration (ID)", full: true },
      { key: "original_amount", label: "Original", type: "number" },
      { key: "refund_amount", label: "Refund", type: "number", card: true },
      { key: "refund_percentage", label: "Refund %", type: "number" },
      {
        key: "refund_reason",
        label: "Reason",
        type: "select",
        options: REFUND_REASON,
        badge: true,
      },
      { key: "refund_reason_display", label: "Reason", skipForm: true },
      { key: "reason_details", label: "Details", type: "textarea", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: REFUND_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "reviewed_by", label: "Reviewed By (ID)", full: true },
      { key: "reviewed_by_name", label: "Reviewed By", skipForm: true },
      {
        key: "approval_notes",
        label: "Approval Notes",
        type: "textarea",
        full: true,
      },
      { key: "transaction_id", label: "Transaction ID" },
      { key: "within_policy", label: "Within Policy", type: "bool" },
      { key: "policy_exception", label: "Policy Exception", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  compliance: {
    key: "compliance",
    label: "Compliance",
    icon: ShieldCheckIcon,
    endpoint: "compliance",
    titleField: "staff_member_name",
    subtitleField: "compliance_type_display",
    searchKeys: ["staff_member_name", "compliance_type", "status"],
    fields: [
      { key: "staff_member", label: "Staff Member (ID)", full: true },
      { key: "staff_member_name", label: "Staff Member", skipForm: true },
      {
        key: "compliance_type",
        label: "Type",
        type: "select",
        options: COMPLIANCE_TYPE,
        badge: true,
      },
      { key: "compliance_type_display", label: "Type", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: COMPLIANCE_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "certification_number", label: "Cert Number", card: true },
      { key: "issuing_organization", label: "Issuing Org" },
      { key: "issue_date", label: "Issued", type: "date" },
      { key: "expiry_date", label: "Expires", type: "date", card: true },
      { key: "document_url", label: "Document URL", full: true },
      { key: "verified_by", label: "Verified By (ID)", full: true },
      { key: "verified_by_name", label: "Verified By", skipForm: true },
      { key: "is_valid", label: "Valid", type: "bool", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  weatherAlerts: {
    key: "weatherAlerts",
    label: "Weather Alerts",
    icon: CloudIcon,
    endpoint: "weather-alerts",
    titleField: "event_title",
    subtitleField: "weather_condition_display",
    searchKeys: ["event_title", "weather_condition", "action_taken"],
    fields: [
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
      {
        key: "weather_condition",
        label: "Condition",
        type: "select",
        options: WEATHER,
        badge: true,
      },
      { key: "weather_condition_display", label: "Condition", skipForm: true },
      { key: "temperature", label: "Temp (°C)", type: "number", card: true },
      { key: "humidity", label: "Humidity %", type: "number" },
      { key: "wind_speed", label: "Wind Speed", type: "number" },
      { key: "precipitation_mm", label: "Precip (mm)", type: "number" },
      {
        key: "action_taken",
        label: "Action",
        type: "select",
        options: WEATHER_ACTION,
        badge: true,
      },
      { key: "action_taken_display", label: "Action", skipForm: true },
      {
        key: "action_reason",
        label: "Action Reason",
        type: "textarea",
        full: true,
      },
      { key: "notified_coaches", label: "Notified Coaches", type: "bool" },
      { key: "notified_players", label: "Notified Players", type: "bool" },
      { key: "notified_parents", label: "Notified Parents", type: "bool" },
      { key: "decided_by", label: "Decided By (ID)", full: true },
      { key: "decided_by_name", label: "Decided By", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  liveStreams: {
    key: "liveStreams",
    label: "Live Streams",
    icon: PlayCircleIcon,
    endpoint: "live-streams",
    titleField: "title",
    subtitleField: "status_display",
    searchKeys: ["title", "event_title", "team_name", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "event", label: "Event (ID)", full: true },
      { key: "event_title", label: "Event", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "stream_url", label: "Stream URL", full: true },
      { key: "embed_code", label: "Embed Code", type: "textarea", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: STREAM_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      {
        key: "quality",
        label: "Quality",
        type: "select",
        options: QUALITY,
        badge: true,
      },
      { key: "quality_display", label: "Quality", skipForm: true },
      {
        key: "scheduled_start",
        label: "Scheduled Start",
        type: "datetime",
        card: true,
      },
      { key: "actual_start", label: "Actual Start", type: "datetime" },
      { key: "actual_end", label: "Actual End", type: "datetime" },
      {
        key: "peak_viewers",
        label: "Peak Viewers",
        type: "number",
        skipForm: true,
      },
      {
        key: "total_views",
        label: "Total Views",
        type: "number",
        skipForm: true,
      },
      { key: "is_public", label: "Public", type: "bool" },
      { key: "requires_login", label: "Requires Login", type: "bool" },
      { key: "password", label: "Password" },
      { key: "allow_chat", label: "Allow Chat", type: "bool" },
      { key: "show_scoreboard", label: "Show Scoreboard", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  suspensions: {
    key: "suspensions",
    label: "Suspensions",
    icon: BellAlertIcon,
    endpoint: "suspensions",
    titleField: "student_name",
    subtitleField: "suspension_type_display",
    searchKeys: ["student_name", "team_name", "reason", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "staff_member", label: "Staff Member (ID)", full: true },
      { key: "staff_member_name", label: "Staff Member", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "suspension_type",
        label: "Type",
        type: "select",
        options: SUSPENSION_TYPE,
        badge: true,
      },
      { key: "suspension_type_display", label: "Type", skipForm: true },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      {
        key: "incident_date",
        label: "Incident Date",
        type: "date",
        card: true,
      },
      { key: "games_missed", label: "Games Missed", type: "number" },
      { key: "start_date", label: "Start", type: "date" },
      { key: "end_date", label: "End", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: SUSPENSION_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "issued_by", label: "Issued By (ID)", full: true },
      { key: "issued_by_name", label: "Issued By", skipForm: true },
      { key: "appeal_submitted", label: "Appeal Submitted", type: "bool" },
      { key: "appeal_date", label: "Appeal Date", type: "date" },
      { key: "appeal_outcome", label: "Appeal Outcome", full: true },
      { key: "document_url", label: "Document URL", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  tournamentBrackets: {
    key: "tournamentBrackets",
    label: "Tournament Brackets",
    icon: TrophyIcon,
    endpoint: "tournament-brackets",
    titleField: "title",
    subtitleField: "bracket_type_display",
    searchKeys: ["title", "sport_name", "status"],
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "sport", label: "Sport (ID)", full: true },
      { key: "sport_name", label: "Sport", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "bracket_type",
        label: "Type",
        type: "select",
        options: BRACKET_TYPE,
        badge: true,
      },
      { key: "bracket_type_display", label: "Type", skipForm: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "max_teams", label: "Max Teams", type: "number" },
      { key: "current_round", label: "Current Round", type: "number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: BRACKET_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      {
        key: "bracket_data",
        label: "Bracket Data (JSON)",
        type: "textarea",
        full: true,
      },
      { key: "first_prize", label: "1st Prize" },
      { key: "second_prize", label: "2nd Prize" },
      { key: "third_prize", label: "3rd Prize" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  tournamentMatches: {
    key: "tournamentMatches",
    label: "Tournament Matches",
    icon: FireIcon,
    endpoint: "tournament-matches",
    titleField: "bracket_title",
    subtitleField: "status_display",
    searchKeys: ["bracket_title", "team_1_name", "team_2_name", "status"],
    fields: [
      { key: "bracket", label: "Bracket (ID)", full: true },
      { key: "bracket_title", label: "Bracket", skipForm: true },
      { key: "team_1", label: "Team 1 (ID)", full: true },
      { key: "team_1_name", label: "Team 1", skipForm: true },
      { key: "team_2", label: "Team 2 (ID)", full: true },
      { key: "team_2_name", label: "Team 2", skipForm: true },
      { key: "round_number", label: "Round", type: "number", card: true },
      { key: "match_number", label: "Match #", type: "number", card: true },
      { key: "team_1_score", label: "Team 1 Score", type: "number" },
      { key: "team_2_score", label: "Team 2 Score", type: "number" },
      { key: "winner", label: "Winner (ID)", full: true },
      { key: "winner_name", label: "Winner", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: MATCH_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "match_date", label: "Match Date", type: "date" },
      { key: "location", label: "Location", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  merchandise: {
    key: "merchandise",
    label: "Merchandise",
    icon: BuildingStorefrontIcon,
    endpoint: "merchandise",
    titleField: "name",
    subtitleField: "product_type_display",
    searchKeys: ["name", "team_name", "product_type", "status"],
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      {
        key: "product_type",
        label: "Type",
        type: "select",
        options: PRODUCT_TYPE,
        badge: true,
      },
      { key: "product_type_display", label: "Type", skipForm: true },
      { key: "price", label: "Price", type: "number", card: true },
      { key: "sale_price", label: "Sale Price", type: "number" },
      { key: "is_on_sale", label: "On Sale", type: "bool" },
      { key: "quantity_available", label: "In Stock", type: "number" },
      { key: "sizes_available", label: "Sizes" },
      { key: "colors_available", label: "Colors" },
      { key: "image_url", label: "Image URL", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: STORE_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "total_sold", label: "Sold", skipForm: true },
      { key: "total_revenue", label: "Revenue", skipForm: true },
      { key: "is_online", label: "Online", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  merchandiseOrders: {
    key: "merchandiseOrders",
    label: "Merch Orders",
    icon: ShoppingCartIcon,
    endpoint: "merchandise-orders",
    titleField: "product_name",
    subtitleField: "status_display",
    searchKeys: ["product_name", "buyer_name", "student_name", "status"],
    fields: [
      { key: "product", label: "Product (ID)", full: true },
      { key: "product_name", label: "Product", skipForm: true },
      { key: "buyer_name", label: "Buyer", card: true },
      { key: "buyer_email", label: "Buyer Email" },
      { key: "buyer_phone", label: "Buyer Phone" },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "quantity", label: "Qty", type: "number" },
      { key: "size", label: "Size" },
      { key: "color", label: "Color" },
      { key: "unit_price", label: "Unit Price", type: "number" },
      { key: "total_amount", label: "Total", type: "number", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ORDER_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      {
        key: "payment_status",
        label: "Payment",
        type: "select",
        options: ORDER_PAY,
        badge: true,
      },
      { key: "transaction_id", label: "Transaction ID" },
      {
        key: "shipping_address",
        label: "Shipping Address",
        type: "textarea",
        full: true,
      },
      { key: "tracking_number", label: "Tracking #" },
      { key: "shipped_date", label: "Shipped", type: "date" },
      { key: "delivered_date", label: "Delivered", type: "date" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  insurance: {
    key: "insurance",
    label: "Insurance",
    icon: BanknotesIcon,
    endpoint: "insurance",
    titleField: "student_name",
    subtitleField: "insurance_type_display",
    searchKeys: ["student_name", "provider", "policy_number", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "insurance_type",
        label: "Type",
        type: "select",
        options: INSURANCE_TYPE,
        badge: true,
      },
      { key: "insurance_type_display", label: "Type", skipForm: true },
      { key: "provider", label: "Provider", card: true },
      { key: "policy_number", label: "Policy #", card: true },
      { key: "group_number", label: "Group #" },
      { key: "coverage_start", label: "Coverage Start", type: "date" },
      { key: "coverage_end", label: "Coverage End", type: "date" },
      { key: "provider_phone", label: "Provider Phone" },
      { key: "provider_email", label: "Provider Email" },
      { key: "insurance_card_url", label: "Card URL", full: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: INSURANCE_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "verified", label: "Verified", type: "bool" },
      { key: "verified_by", label: "Verified By (ID)", full: true },
      { key: "verified_by_name", label: "Verified By", skipForm: true },
      { key: "is_valid", label: "Valid", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  eligibilityRules: {
    key: "eligibilityRules",
    label: "Eligibility Rules",
    icon: ScaleIcon,
    endpoint: "eligibility-rules",
    titleField: "name",
    subtitleField: "rule_type_display",
    searchKeys: ["name", "sport_name", "rule_type", "status"],
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "sport", label: "Sport (ID)", full: true },
      { key: "sport_name", label: "Sport", skipForm: true },
      {
        key: "rule_type",
        label: "Type",
        type: "select",
        options: RULE_TYPE,
        badge: true,
      },
      { key: "rule_type_display", label: "Type", skipForm: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
      { key: "min_gpa", label: "Min GPA", type: "number", card: true },
      { key: "min_age", label: "Min Age", type: "number" },
      { key: "max_age", label: "Max Age", type: "number" },
      { key: "min_grade", label: "Min Grade", type: "number" },
      { key: "max_grade", label: "Max Grade", type: "number" },
      { key: "min_attendance", label: "Min Attendance %", type: "number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: RULE_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  studentEligibility: {
    key: "studentEligibility",
    label: "Student Eligibility",
    icon: CheckBadgeIcon,
    endpoint: "student-eligibility",
    titleField: "student_name",
    subtitleField: "status_display",
    searchKeys: ["student_name", "sport_name", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "sport", label: "Sport (ID)", full: true },
      { key: "sport_name", label: "Sport", skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ELIGIBILITY_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "current_gpa", label: "GPA", type: "number", card: true },
      {
        key: "current_attendance",
        label: "Attendance %",
        type: "number",
        card: true,
      },
      { key: "last_review_date", label: "Last Review", type: "date" },
      { key: "next_review_date", label: "Next Review", type: "date" },
      { key: "reviewed_by", label: "Reviewed By (ID)", full: true },
      { key: "reviewed_by_name", label: "Reviewed By", skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  transfers: {
    key: "transfers",
    label: "Transfers",
    icon: ArrowsRightLeftIcon,
    endpoint: "transfers",
    titleField: "student_name",
    subtitleField: "transfer_type_display",
    searchKeys: ["student_name", "from_team_name", "to_team_name", "status"],
    fields: [
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      {
        key: "transfer_type",
        label: "Type",
        type: "select",
        options: TRANSFER_TYPE,
        badge: true,
      },
      { key: "transfer_type_display", label: "Type", skipForm: true },
      { key: "from_team", label: "From Team (ID)", full: true },
      { key: "from_team_name", label: "From Team", skipForm: true },
      { key: "to_team", label: "To Team (ID)", full: true },
      { key: "to_team_name", label: "To Team", skipForm: true },
      { key: "from_school", label: "From School" },
      { key: "to_school", label: "To School" },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      { key: "request_date", label: "Requested", type: "date" },
      { key: "effective_date", label: "Effective", type: "date", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: TRANSFER_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true },
      { key: "approved_by", label: "Approved By (ID)", full: true },
      { key: "approved_by_name", label: "Approved By", skipForm: true },
      { key: "approval_date", label: "Approval Date", type: "date" },
      { key: "transfer_paperwork_url", label: "Paperwork URL", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  seasonArchives: {
    key: "seasonArchives",
    label: "Season Archives",
    icon: ArchiveBoxIcon,
    endpoint: "season-archives",
    titleField: "team_name",
    subtitleField: "season",
    searchKeys: ["team_name", "season", "academic_year"],
    fields: [
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "season", label: "Season", card: true },
      { key: "academic_year", label: "Academic Year", card: true },
      { key: "games_played", label: "GP", type: "number" },
      { key: "wins", label: "W", type: "number" },
      { key: "losses", label: "L", type: "number" },
      { key: "ties", label: "T", type: "number" },
      { key: "points_scored", label: "Points Scored", type: "number" },
      { key: "points_allowed", label: "Points Allowed", type: "number" },
      { key: "win_percentage", label: "Win %", skipForm: true },
      { key: "championships", label: "Championships", full: true },
      {
        key: "tournament_appearances",
        label: "Tournament Appearances",
        type: "number",
      },
      {
        key: "roster_snapshot",
        label: "Roster Snapshot (JSON)",
        type: "textarea",
        full: true,
      },
      {
        key: "archive_data",
        label: "Archive Data (JSON)",
        type: "textarea",
        full: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  badges: {
    key: "badges",
    label: "Badges",
    icon: SparklesIcon,
    endpoint: "badges",
    titleField: "name",
    subtitleField: "badge_type_display",
    searchKeys: ["name", "criteria", "badge_type"],
    toggleField: "is_active",
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
        options: BADGE_TYPE,
        badge: true,
      },
      { key: "badge_type_display", label: "Type", skipForm: true },
      { key: "icon_url", label: "Icon URL", full: true },
      { key: "icon_color", label: "Icon Color", card: true },
      { key: "criteria", label: "Criteria", type: "textarea", full: true },
      { key: "points_value", label: "Points", type: "number", card: true },
      { key: "times_awarded", label: "Times Awarded", skipForm: true },
      { key: "is_active", label: "Active", type: "bool" },
      { key: "is_hidden", label: "Hidden", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  badgeAwards: {
    key: "badgeAwards",
    label: "Badge Awards",
    icon: CheckBadgeIcon,
    endpoint: "badge-awards",
    titleField: "badge_name",
    subtitleField: "student_name",
    searchKeys: ["badge_name", "student_name", "team_name", "reason"],
    fields: [
      { key: "badge", label: "Badge (ID)", full: true },
      { key: "badge_name", label: "Badge", skipForm: true },
      { key: "student", label: "Student (ID)", full: true },
      { key: "student_name", label: "Student", skipForm: true },
      { key: "team", label: "Team (ID)", full: true },
      { key: "team_name", label: "Team", skipForm: true },
      { key: "awarded_date", label: "Awarded", type: "date", card: true },
      { key: "awarded_by", label: "Awarded By (ID)", full: true },
      { key: "awarded_by_name", label: "Awarded By", skipForm: true },
      { key: "reason", label: "Reason", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
  },
  leaderboards: {
    key: "leaderboards",
    label: "Leaderboards",
    icon: SparklesIcon,
    endpoint: "leaderboards",
    titleField: "name",
    subtitleField: "leaderboard_type_display",
    searchKeys: ["name", "sport_name", "leaderboard_type", "season"],
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "sport", label: "Sport (ID)", full: true },
      { key: "sport_name", label: "Sport", skipForm: true },
      {
        key: "leaderboard_type",
        label: "Type",
        type: "select",
        options: LEADERBOARD_TYPE,
        badge: true,
      },
      { key: "leaderboard_type_display", label: "Type", skipForm: true },
      { key: "season", label: "Season", card: true },
      { key: "entries", label: "Entries (JSON)", type: "textarea", full: true },
      { key: "is_public", label: "Public", type: "bool" },
      { key: "is_active", label: "Active", type: "bool" },
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

export default function SportsPage() {
  useTitle("Sports Center");
  const [activeTab, setActiveTab] = useState("sports");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Sports Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Teams, events, registrations, injuries, tournaments, merchandise and analytics
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
            leftIcon={<TrophyIcon className="h-4 w-4" />}
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
        basePath="/sports"
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
