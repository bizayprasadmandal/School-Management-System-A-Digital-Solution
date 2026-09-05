/**
 * Communication Center — full-surface admin page for the communication module.
 *
 * 38 tabs (config-driven via EntitySection) covering announcements, messaging,
 * chat, conferences, integrations, surveys/polls, templates, logs and config.
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
  MegaphoneIcon,
  ChatBubbleLeftRightIcon,
  BellIcon,
  EnvelopeIcon,
  DevicePhoneMobileIcon,
  PhoneIcon,
  MicrophoneIcon,
  VideoCameraIcon,
  UsersIcon,
  PaperAirplaneIcon,
  InboxIcon,
  EyeIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  HandRaisedIcon,
  ExclamationTriangleIcon,
  LockClosedIcon,
  NoSymbolIcon,
  ClockIcon,
  TicketIcon,
  UserGroupIcon,
  AtSymbolIcon,
  WrenchScrewdriverIcon,
  DocumentChartBarIcon,
  BellAlertIcon,
  NewspaperIcon,
  SignalIcon,
  QueueListIcon,
  ComputerDesktopIcon,
  SpeakerWaveIcon,
  ArrowsRightLeftIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";

// ─── Shared option sets ──────────────────────────────────────────────────────

const AUDIENCE = [
  ["all", "All"],
  ["teachers", "Teachers"],
  ["students", "Students"],
  ["parents", "Parents"],
  ["staff", "Staff"],
] as [string, string][];

const CHANNELS = [
  ["email", "Email"],
  ["sms", "SMS"],
  ["push", "Push"],
  ["in_app", "In-App"],
] as [string, string][];

const MSG_STATUS = [
  ["pending", "Pending"],
  ["queued", "Queued"],
  ["sent", "Sent"],
  ["delivered", "Delivered"],
  ["read", "Read"],
  ["failed", "Failed"],
] as [string, string][];

const ATT_STATUS = [
  ["pending", "Pending"],
  ["sent", "Sent"],
  ["delivered", "Delivered"],
  ["failed", "Failed"],
] as [string, string][];

const PLATFORMS = [
  ["ios", "iOS"],
  ["android", "Android"],
  ["web", "Web (PWA)"],
] as [string, string][];

const SMS_PROVIDERS = [
  ["twilio", "Twilio"],
  ["africastalking", "Africa's Talking"],
  ["nexmo", "Nexmo/Vonage"],
  ["msg91", "MSG91"],
  ["custom", "Custom API"],
] as [string, string][];

const EMAIL_PROVIDERS = [
  ["sendgrid", "SendGrid"],
  ["aws_ses", "AWS SES"],
  ["mailgun", "Mailgun"],
  ["smtp", "SMTP Server"],
  ["custom", "Custom Provider"],
] as [string, string][];

// ─── Entity configs (38 tabs) ────────────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  announcements: {
    key: "announcements",
    label: "Announcement",
    icon: MegaphoneIcon,
    endpoint: "announcements",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "created_by_name", label: "By", subtitle: true, skipForm: true },
      {
        key: "priority",
        label: "Priority",
        type: "select",
        options: [
          ["low", "Low"],
          ["normal", "Normal"],
          ["high", "High"],
          ["urgent", "Urgent"],
        ],
        badge: true,
      },
      {
        key: "audience",
        label: "Audience",
        type: "select",
        options: AUDIENCE,
        badge: true,
      },
      { key: "content", label: "Content", type: "textarea", full: true, card: true },
      { key: "send_email", label: "Send Email", type: "bool", card: true },
      { key: "send_sms", label: "Send SMS", type: "bool", card: true },
      { key: "send_push", label: "Send Push", type: "bool", card: true },
      { key: "is_draft", label: "Draft", type: "bool", card: true },
      { key: "view_count", label: "Views", type: "number", card: true, skipForm: true },
      { key: "published_at", label: "Published", type: "datetime", skipForm: true },
      { key: "expires_at", label: "Expires", type: "datetime", card: true },
    ],
    searchKeys: ["title", "priority", "audience", "content"],
  },
  messages: {
    key: "messages",
    label: "Direct Message",
    icon: EnvelopeIcon,
    endpoint: "messages",
    titleField: "sender_name",
    subtitleField: "recipient_name",
    fields: [
      { key: "sender_name", label: "From", main: true, skipForm: true },
      { key: "sender", label: "Sender ID", skipForm: true },
      { key: "recipient_name", label: "To", subtitle: true, skipForm: true },
      { key: "recipient", label: "Recipient ID", card: true },
      { key: "content", label: "Message", type: "textarea", full: true, card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: MSG_STATUS,
        badge: true,
      },
      { key: "sent_at", label: "Sent", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["sender_name", "recipient_name", "content", "status"],
  },
  notifications: {
    key: "notifications",
    label: "Notification",
    icon: BellIcon,
    endpoint: "notifications",
    titleField: "title",
    readOnly: true,
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "user_name", label: "User", subtitle: true, skipForm: true },
      {
        key: "channel",
        label: "Channel",
        type: "select",
        options: CHANNELS,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: MSG_STATUS,
        badge: true,
      },
      { key: "body", label: "Body", type: "textarea", full: true, card: true },
      { key: "sent_at", label: "Sent", type: "datetime", card: true },
      { key: "read_at", label: "Read", type: "datetime", card: true },
      { key: "failure_reason", label: "Failure Reason", card: true },
    ],
    searchKeys: ["title", "user_name", "channel", "status"],
  },
  "chat-groups": {
    key: "chat-groups",
    label: "Chat Group",
    icon: UsersIcon,
    endpoint: "chat-groups",
    titleField: "name",
    toggleField: "is_archived",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "group_type",
        label: "Type",
        type: "select",
        options: [
          ["class", "Class"],
          ["subject", "Subject"],
          ["club", "Club"],
          ["department", "Department"],
          ["staff", "Staff"],
          ["parents", "Parents"],
          ["custom", "Custom"],
        ],
        badge: true,
      },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "classroom", label: "Classroom ID", type: "number", card: true },
      { key: "subject", label: "Subject ID", type: "number", card: true },
      { key: "created_by", label: "Created By ID", type: "number", skipForm: true },
      { key: "max_members", label: "Max Members", type: "number", card: true },
      { key: "is_archived", label: "Archived", type: "bool", card: true },
      { key: "is_muted", label: "Muted", type: "bool", card: true },
    ],
    searchKeys: ["name", "group_type", "description"],
  },
  "group-messages": {
    key: "group-messages",
    label: "Group Message",
    icon: ChatBubbleLeftRightIcon,
    endpoint: "group-messages",
    titleField: "group_name",
    subtitleField: "sender_name",
    fields: [
      { key: "group_name", label: "Group", main: true, skipForm: true },
      { key: "group", label: "Group ID" },
      { key: "sender_name", label: "From", subtitle: true, skipForm: true },
      { key: "sender", label: "Sender ID", skipForm: true },
      {
        key: "message_type",
        label: "Type",
        type: "select",
        options: [
          ["text", "Text"],
          ["image", "Image"],
          ["file", "File"],
          ["voice", "Voice"],
          ["video", "Video"],
          ["system", "System"],
          ["poll", "Poll"],
        ],
        badge: true,
      },
      { key: "content", label: "Message", type: "textarea", full: true, card: true },
      { key: "is_pinned", label: "Pinned", type: "bool", card: true },
      { key: "is_edited", label: "Edited", type: "bool", skipForm: true },
      { key: "is_deleted", label: "Deleted", type: "bool", skipForm: true },
      { key: "sent_at", label: "Sent", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["group_name", "sender_name", "content"],
  },
  "message-reactions": {
    key: "message-reactions",
    label: "Message Reaction",
    icon: SparklesIcon,
    endpoint: "message-reactions",
    titleField: "emoji",
    fields: [
      { key: "emoji", label: "Emoji", main: true },
      { key: "user_name", label: "User", subtitle: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      { key: "message", label: "Message ID" },
      { key: "created_at", label: "Created", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["emoji", "user_name"],
  },
  "read-receipts": {
    key: "read-receipts",
    label: "Read Receipt",
    icon: EyeIcon,
    endpoint: "read-receipts",
    titleField: "user_name",
    readOnly: true,
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "message", label: "Message ID", card: true },
      { key: "read_at", label: "Read At", type: "datetime", card: true },
    ],
    searchKeys: ["user_name"],
  },
  "typing-indicators": {
    key: "typing-indicators",
    label: "Typing Indicator",
    icon: AtSymbolIcon,
    endpoint: "typing-indicators",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      {
        key: "chat_type",
        label: "Chat Type",
        type: "select",
        options: [
          ["group", "Group"],
          ["parent_teacher", "Parent-Teacher"],
          ["direct", "Direct"],
        ],
        badge: true,
      },
      { key: "chat_id", label: "Chat ID", card: true },
      { key: "started_at", label: "Started", type: "datetime", card: true },
      { key: "expires_at", label: "Expires", type: "datetime", card: true },
    ],
    searchKeys: ["user_name", "chat_type"],
  },
  "message-threads": {
    key: "message-threads",
    label: "Message Thread",
    icon: QueueListIcon,
    endpoint: "message-threads",
    titleField: "reply_count",
    fields: [
      { key: "reply_count", label: "Replies", main: true, type: "number" },
      { key: "parent_message", label: "Parent Message ID" },
      { key: "last_reply_by_name", label: "Last Reply By", subtitle: true, skipForm: true },
      { key: "last_reply_at", label: "Last Reply", type: "datetime", card: true },
      { key: "is_closed", label: "Closed", type: "bool", card: true },
      { key: "created_at", label: "Created", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["last_reply_by_name"],
  },
  attachments: {
    key: "attachments",
    label: "File Attachment",
    icon: DocumentTextIcon,
    endpoint: "attachments",
    titleField: "file_name",
    fields: [
      { key: "file_name", label: "File", main: true },
      {
        key: "file_type",
        label: "Type",
        type: "select",
        options: [
          ["document", "Document"],
          ["image", "Image"],
          ["video", "Video"],
          ["audio", "Audio"],
          ["archive", "Archive"],
          ["other", "Other"],
        ],
        badge: true,
      },
      { key: "uploaded_by_name", label: "Uploaded By", subtitle: true, skipForm: true },
      { key: "uploaded_by", label: "Uploaded By ID", skipForm: true },
      { key: "file_size", label: "Size (bytes)", type: "number", card: true },
      { key: "mime_type", label: "MIME Type", card: true },
      { key: "reference_type", label: "Reference Type", card: true },
      { key: "reference_id", label: "Reference ID", card: true },
      { key: "is_public", label: "Public", type: "bool", card: true },
      { key: "download_count", label: "Downloads", type: "number", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["file_name", "file_type", "uploaded_by_name"],
  },
  "parent-teacher-chats": {
    key: "parent-teacher-chats",
    label: "Parent-Teacher Chat",
    icon: ChatBubbleLeftRightIcon,
    endpoint: "parent-teacher-chats",
    titleField: "subject",
    toggleField: "is_archived_by_teacher",
    fields: [
      { key: "subject", label: "Subject", main: true },
      { key: "parent_name", label: "Parent", subtitle: true, skipForm: true },
      { key: "parent", label: "Parent ID", card: true },
      { key: "teacher_name", label: "Teacher", card: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", card: true },
      { key: "student_name", label: "Student", card: true, skipForm: true },
      { key: "student", label: "Student ID", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["archived", "Archived"],
          ["blocked", "Blocked"],
        ],
        badge: true,
      },
      {
        key: "last_message_at",
        label: "Last Message",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      { key: "parent_unread_count", label: "Parent Unread", type: "number", skipForm: true },
    ],
    searchKeys: ["subject", "parent_name", "teacher_name", "status"],
  },
  "parent-teacher-messages": {
    key: "parent-teacher-messages",
    label: "Parent-Teacher Message",
    icon: ChatBubbleLeftRightIcon,
    endpoint: "parent-teacher-messages",
    titleField: "chat_subject",
    subtitleField: "sender_name",
    fields: [
      { key: "chat_subject", label: "Chat", main: true, skipForm: true },
      { key: "chat", label: "Chat ID" },
      { key: "sender_name", label: "From", subtitle: true, skipForm: true },
      { key: "sender", label: "Sender ID", skipForm: true },
      {
        key: "message_type",
        label: "Type",
        type: "select",
        options: [
          ["text", "Text"],
          ["image", "Image"],
          ["file", "File"],
          ["system", "System"],
        ],
        badge: true,
      },
      { key: "content", label: "Message", type: "textarea", full: true, card: true },
      { key: "is_read_by_parent", label: "Read (Parent)", type: "bool", card: true },
      { key: "is_read_by_teacher", label: "Read (Teacher)", type: "bool", card: true },
      { key: "sent_at", label: "Sent", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["chat_subject", "sender_name", "content"],
  },
  "video-conferences": {
    key: "video-conferences",
    label: "Video Conference",
    icon: VideoCameraIcon,
    endpoint: "video-conferences",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "host_name", label: "Host", subtitle: true, skipForm: true },
      { key: "host", label: "Host ID", skipForm: true },
      {
        key: "conference_type",
        label: "Type",
        type: "select",
        options: [
          ["meeting", "Meeting"],
          ["parent_teacher", "Parent-Teacher"],
          ["staff", "Staff Meeting"],
          ["class", "Virtual Class"],
          ["tutoring", "Tutoring"],
          ["interview", "Interview"],
        ],
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["active", "Active"],
          ["ended", "Ended"],
          ["cancelled", "Cancelled"],
        ],
        badge: true,
      },
      { key: "scheduled_at", label: "Scheduled", type: "datetime", card: true },
      { key: "duration_minutes", label: "Duration (min)", type: "number", card: true },
      { key: "max_participants", label: "Max Participants", type: "number", card: true },
      { key: "meeting_url", label: "Meeting URL", card: true },
      { key: "meeting_id", label: "Meeting ID", card: true },
      { key: "meeting_password", label: "Password", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["title", "host_name", "conference_type", "status"],
  },
  "conference-participants": {
    key: "conference-participants",
    label: "Conference Participant",
    icon: UserGroupIcon,
    endpoint: "conference-participants",
    titleField: "user_name",
    subtitleField: "conference_title",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      { key: "conference_title", label: "Conference", subtitle: true, skipForm: true },
      { key: "conference", label: "Conference ID" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["invited", "Invited"],
          ["accepted", "Accepted"],
          ["declined", "Declined"],
          ["attended", "Attended"],
          ["no_show", "No Show"],
        ],
        badge: true,
      },
      { key: "duration_minutes", label: "Duration (min)", type: "number", card: true },
      { key: "joined_at", label: "Joined", type: "datetime", card: true, skipForm: true },
      { key: "left_at", label: "Left", type: "datetime", skipForm: true },
    ],
    searchKeys: ["user_name", "conference_title", "status"],
  },
  sms: {
    key: "sms",
    label: "SMS Message",
    icon: DevicePhoneMobileIcon,
    endpoint: "sms",
    titleField: "to_number",
    fields: [
      { key: "to_number", label: "To", main: true },
      { key: "from_number", label: "From", card: true },
      {
        key: "provider",
        label: "Provider",
        type: "select",
        options: SMS_PROVIDERS,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ATT_STATUS,
        badge: true,
      },
      { key: "message", label: "Message", type: "textarea", full: true, card: true },
      { key: "cost", label: "Cost", type: "number", card: true },
      { key: "provider_message_id", label: "Provider Msg ID", card: true },
      { key: "error_message", label: "Error", card: true },
      { key: "sent_by_name", label: "Sent By", card: true, skipForm: true },
      { key: "sent_at", label: "Sent", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["to_number", "provider", "status"],
  },
  emails: {
    key: "emails",
    label: "Email Message",
    icon: EnvelopeIcon,
    endpoint: "emails",
    titleField: "subject",
    subtitleField: "to_email",
    fields: [
      { key: "subject", label: "Subject", main: true },
      { key: "to_email", label: "To", subtitle: true },
      { key: "from_email", label: "From", card: true },
      {
        key: "provider",
        label: "Provider",
        type: "select",
        options: EMAIL_PROVIDERS,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ATT_STATUS,
        badge: true,
      },
      { key: "body_text", label: "Body (Text)", type: "textarea", full: true, card: true },
      { key: "body_html", label: "Body (HTML)", type: "textarea", full: true },
      { key: "cc_emails", label: "CC", card: true },
      { key: "bcc_emails", label: "BCC", card: true },
      { key: "error_message", label: "Error", card: true },
      { key: "sent_by_name", label: "Sent By", card: true, skipForm: true },
    ],
    searchKeys: ["subject", "to_email", "provider", "status"],
  },
  "voice-messages": {
    key: "voice-messages",
    label: "Voice Message",
    icon: MicrophoneIcon,
    endpoint: "voice-messages",
    titleField: "sender_name",
    fields: [
      { key: "sender_name", label: "From", main: true, skipForm: true },
      { key: "sender", label: "Sender ID", skipForm: true },
      { key: "group", label: "Group ID", card: true },
      { key: "parent_teacher_chat", label: "Chat ID", card: true },
      { key: "duration_seconds", label: "Duration (s)", type: "number", card: true },
      { key: "file_size", label: "Size (bytes)", type: "number", card: true },
      { key: "is_transcribed", label: "Transcribed", type: "bool", card: true },
      { key: "transcription", label: "Transcription", type: "textarea", full: true, card: true },
      { key: "audio_file", label: "Audio File", card: true },
      { key: "sent_at", label: "Sent", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["sender_name", "transcription"],
  },
  broadcasts: {
    key: "broadcasts",
    label: "Broadcast",
    icon: SpeakerWaveIcon,
    endpoint: "broadcasts",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "channel",
        label: "Channel",
        type: "select",
        options: [...CHANNELS, ["all", "All Channels"]],
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["scheduled", "Scheduled"],
          ["sending", "Sending"],
          ["sent", "Sent"],
          ["partial", "Partial"],
          ["failed", "Failed"],
        ],
        badge: true,
      },
      { key: "content", label: "Content", type: "textarea", full: true, card: true },
      {
        key: "target_audience",
        label: "Audience",
        type: "select",
        options: AUDIENCE,
        card: true,
      },
      { key: "scheduled_at", label: "Scheduled", type: "datetime", card: true },
      { key: "sent_at", label: "Sent", type: "datetime", card: true, skipForm: true },
      { key: "total_recipients", label: "Recipients", type: "number", card: true, skipForm: true },
      { key: "total_sent", label: "Sent OK", type: "number", card: true, skipForm: true },
    ],
    searchKeys: ["title", "channel", "status"],
  },
  logs: {
    key: "logs",
    label: "Communication Log",
    icon: ClipboardDocumentListIcon,
    endpoint: "logs",
    titleField: "subject",
    readOnly: true,
    fields: [
      { key: "subject", label: "Subject", main: true },
      {
        key: "communication_type",
        label: "Type",
        type: "select",
        options: [
          ["sms", "SMS"],
          ["email", "Email"],
          ["push", "Push"],
          ["in_app", "In-App"],
          ["announcement", "Announcement"],
          ["broadcast", "Broadcast"],
          ["direct_message", "Direct"],
          ["group_message", "Group"],
          ["parent_teacher", "Parent-Teacher"],
          ["video_conference", "Conference"],
        ],
        badge: true,
      },
      { key: "sender", label: "Sender", card: true },
      { key: "recipient", label: "Recipient", card: true },
      { key: "recipient_group", label: "Recipient Group", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: MSG_STATUS,
        badge: true,
      },
      { key: "content_preview", label: "Preview", type: "textarea", full: true, card: true },
      { key: "cost", label: "Cost", type: "number" },
      { key: "error_message", label: "Error", card: true },
    ],
    searchKeys: ["subject", "communication_type", "recipient", "status"],
  },
  "announcement-read": {
    key: "announcement-read",
    label: "Announcement Read",
    icon: EyeIcon,
    endpoint: "announcement-read",
    titleField: "announcement_title",
    subtitleField: "user_name",
    fields: [
      { key: "announcement_title", label: "Announcement", main: true, skipForm: true },
      { key: "announcement", label: "Announcement ID" },
      { key: "user_name", label: "User", subtitle: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      { key: "read_at", label: "Read At", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["announcement_title", "user_name"],
  },
  "notification-template": {
    key: "notification-template",
    label: "Notification Template",
    icon: BellAlertIcon,
    endpoint: "notification-template",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "event_type", label: "Event Type", card: true },
      { key: "email_subject", label: "Email Subject", card: true },
      { key: "email_body", label: "Email Body", type: "textarea", full: true, card: true },
      { key: "sms_body", label: "SMS Body", type: "textarea", full: true },
      { key: "push_title", label: "Push Title", card: true },
      { key: "push_body", label: "Push Body", type: "textarea", full: true },
      { key: "is_active", label: "Active", type: "bool", card: true },
    ],
    searchKeys: ["name", "event_type"],
  },
  "device-token": {
    key: "device-token",
    label: "Device Token",
    icon: ComputerDesktopIcon,
    endpoint: "device-token",
    titleField: "device_name",
    subtitleField: "user_name",
    toggleField: "is_active",
    fields: [
      { key: "device_name", label: "Device", main: true },
      { key: "user_name", label: "User", subtitle: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      {
        key: "platform",
        label: "Platform",
        type: "select",
        options: PLATFORMS,
        badge: true,
      },
      { key: "device_id", label: "Device ID", card: true },
      { key: "token", label: "Token", card: true },
      { key: "app_version", label: "App Version", card: true },
      { key: "is_active", label: "Active", type: "bool", card: true },
      { key: "last_used_at", label: "Last Used", type: "datetime", card: true, skipForm: true },
      { key: "registered_at", label: "Registered", type: "datetime", skipForm: true },
    ],
    searchKeys: ["device_name", "user_name", "platform"],
  },
  "group-membership": {
    key: "group-membership",
    label: "Group Member",
    icon: UserGroupIcon,
    endpoint: "group-membership",
    titleField: "group_name",
    subtitleField: "user_name",
    fields: [
      { key: "group_name", label: "Group", main: true, skipForm: true },
      { key: "group", label: "Group ID" },
      { key: "user_name", label: "User", subtitle: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      {
        key: "role",
        label: "Role",
        type: "select",
        options: [
          ["owner", "Owner"],
          ["admin", "Admin"],
          ["moderator", "Moderator"],
          ["member", "Member"],
          ["viewer", "Viewer"],
        ],
        badge: true,
      },
      { key: "nickname", label: "Nickname", card: true },
      { key: "is_muted", label: "Muted", type: "bool", card: true },
      { key: "is_pinned", label: "Pinned", type: "bool", card: true },
      { key: "unread_count", label: "Unread", type: "number", skipForm: true },
      { key: "joined_at", label: "Joined", type: "datetime", card: true, skipForm: true },
      { key: "last_active_at", label: "Last Active", type: "datetime", skipForm: true },
    ],
    searchKeys: ["group_name", "user_name", "role"],
  },
  survey: {
    key: "survey",
    label: "Survey",
    icon: ClipboardDocumentListIcon,
    endpoint: "survey",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "survey_type",
        label: "Type",
        type: "select",
        options: [
          ["feedback", "Feedback"],
          ["satisfaction", "Satisfaction"],
          ["needs", "Needs Assessment"],
          ["academic", "Academic"],
          ["demographic", "Demographic"],
          ["custom", "Custom"],
        ],
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["active", "Active"],
          ["closed", "Closed"],
          ["analyzed", "Analyzed"],
        ],
        badge: true,
      },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      {
        key: "target_audience",
        label: "Audience",
        type: "select",
        options: AUDIENCE,
        card: true,
      },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "is_anonymous", label: "Anonymous", type: "bool", card: true },
      {
        key: "allow_multiple_responses",
        label: "Multi-response",
        type: "bool",
        card: true,
      },
      { key: "total_invited", label: "Invited", type: "number", card: true, skipForm: true },
      { key: "total_responses", label: "Responses", type: "number", card: true, skipForm: true },
    ],
    searchKeys: ["title", "survey_type", "status"],
  },
  "survey-response": {
    key: "survey-response",
    label: "Survey Response",
    icon: TicketIcon,
    endpoint: "survey-response",
    titleField: "survey_title",
    fields: [
      { key: "survey_title", label: "Survey", main: true, skipForm: true },
      { key: "survey", label: "Survey ID" },
      {
        key: "respondent_type",
        label: "Respondent",
        type: "select",
        options: [
          ["student", "Student"],
          ["parent", "Parent"],
          ["staff", "Staff"],
        ],
        badge: true,
      },
      { key: "student_name", label: "Student", card: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "parent_name", label: "Parent", card: true, skipForm: true },
      { key: "parent", label: "Parent ID", skipForm: true },
      { key: "staff_name", label: "Staff", card: true, skipForm: true },
      { key: "staff", label: "Staff ID", skipForm: true },
      { key: "overall_rating", label: "Rating", type: "number", card: true },
      { key: "comments", label: "Comments", type: "textarea", full: true, card: true },
      { key: "answers", label: "Answers", type: "textarea", full: true },
      { key: "submitted_at", label: "Submitted", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["survey_title", "respondent_type", "comments"],
  },
  poll: {
    key: "poll",
    label: "Poll",
    icon: HandRaisedIcon,
    endpoint: "poll",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["active", "Active"],
          ["closed", "Closed"],
        ],
        badge: true,
      },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      {
        key: "target_audience",
        label: "Audience",
        type: "select",
        options: AUDIENCE,
        card: true,
      },
      { key: "is_anonymous", label: "Anonymous", type: "bool", card: true },
      {
        key: "allow_multiple_choices",
        label: "Multi-choice",
        type: "bool",
        card: true,
      },
      { key: "max_choices", label: "Max Choices", type: "number", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "total_votes", label: "Votes", type: "number", card: true, skipForm: true },
    ],
    searchKeys: ["title", "status"],
  },
  "poll-vote": {
    key: "poll-vote",
    label: "Poll Vote",
    icon: CheckSquareFallback,
    endpoint: "poll-vote",
    titleField: "poll_title",
    fields: [
      { key: "poll_title", label: "Poll", main: true, skipForm: true },
      { key: "poll", label: "Poll ID" },
      {
        key: "voter_type",
        label: "Voter",
        type: "select",
        options: [
          ["student", "Student"],
          ["parent", "Parent"],
          ["staff", "Staff"],
        ],
        badge: true,
      },
      { key: "student_name", label: "Student", card: true, skipForm: true },
      { key: "student", label: "Student ID", skipForm: true },
      { key: "parent_name", label: "Parent", card: true, skipForm: true },
      { key: "parent", label: "Parent ID", skipForm: true },
      { key: "staff_name", label: "Staff", card: true, skipForm: true },
      { key: "staff", label: "Staff ID", skipForm: true },
      { key: "selected_options", label: "Selected", card: true },
      { key: "voted_at", label: "Voted", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["poll_title", "voter_type"],
  },
  "email-template": {
    key: "email-template",
    label: "Email Template",
    icon: EnvelopeIcon,
    endpoint: "email-template",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: [
          ["welcome", "Welcome"],
          ["fee_reminder", "Fee Reminder"],
          ["event", "Event"],
          ["report", "Report Card"],
          ["absence", "Absence Alert"],
          ["newsletter", "Newsletter"],
          ["admission", "Admission"],
          ["custom", "Custom"],
        ],
        badge: true,
      },
      { key: "subject", label: "Subject", card: true },
      { key: "body_html", label: "Body (HTML)", type: "textarea", full: true, card: true },
      { key: "body_text", label: "Body (Text)", type: "textarea", full: true },
      { key: "times_used", label: "Times Used", type: "number", card: true, skipForm: true },
      { key: "last_used_at", label: "Last Used", type: "datetime", skipForm: true },
      { key: "is_active", label: "Active", type: "bool", card: true },
    ],
    searchKeys: ["name", "category", "subject"],
  },
  "s-m-s-gateway-config": {
    key: "s-m-s-gateway-config",
    label: "SMS Gateway",
    icon: SignalIcon,
    endpoint: "s-m-s-gateway-config",
    titleField: "provider",
    toggleField: "is_active",
    fields: [
      {
        key: "provider",
        label: "Provider",
        type: "select",
        options: SMS_PROVIDERS,
        main: true,
      },
      { key: "sender_id", label: "Sender ID", card: true },
      { key: "api_key", label: "API Key", card: true },
      { key: "api_secret", label: "API Secret", card: true },
      { key: "webhook_url", label: "Webhook URL", card: true },
      { key: "total_sms_sent", label: "Total Sent", type: "number", card: true, skipForm: true },
      { key: "total_sms_cost", label: "Total Cost", type: "number", card: true, skipForm: true },
      { key: "is_active", label: "Active", type: "bool", card: true },
    ],
    searchKeys: ["provider", "sender_id"],
  },
  "s-m-s-log": {
    key: "s-m-s-log",
    label: "SMS Log",
    icon: PhoneIcon,
    endpoint: "s-m-s-log",
    titleField: "recipient_name",
    subtitleField: "recipient_phone",
    fields: [
      { key: "recipient_name", label: "Recipient", main: true },
      { key: "recipient_phone", label: "Phone", subtitle: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: ATT_STATUS,
        badge: true,
      },
      { key: "message", label: "Message", type: "textarea", full: true, card: true },
      { key: "cost", label: "Cost", type: "number", card: true },
      { key: "provider_message_id", label: "Provider Msg ID", card: true },
      { key: "error_message", label: "Error", card: true },
      { key: "reference_type", label: "Reference Type", card: true },
      { key: "reference_id", label: "Reference ID", card: true },
      { key: "sent_by_name", label: "Sent By", card: true, skipForm: true },
      { key: "sent_at", label: "Sent", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["recipient_name", "recipient_phone", "status"],
  },
  newsletter: {
    key: "newsletter",
    label: "Newsletter",
    icon: NewspaperIcon,
    endpoint: "newsletter",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "subject", label: "Subject", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["scheduled", "Scheduled"],
          ["sent", "Sent"],
          ["failed", "Failed"],
        ],
        badge: true,
      },
      {
        key: "target_audience",
        label: "Audience",
        type: "select",
        options: AUDIENCE,
        card: true,
      },
      { key: "content_html", label: "Content (HTML)", type: "textarea", full: true, card: true },
      { key: "content_text", label: "Content (Text)", type: "textarea", full: true },
      { key: "scheduled_date", label: "Scheduled", type: "datetime", card: true },
      { key: "sent_date", label: "Sent", type: "datetime", skipForm: true },
      { key: "total_recipients", label: "Recipients", type: "number", skipForm: true },
      { key: "total_opened", label: "Opened", type: "number", card: true, skipForm: true },
      { key: "total_clicked", label: "Clicked", type: "number", card: true, skipForm: true },
    ],
    searchKeys: ["title", "subject", "status"],
  },
  "emergency-alert": {
    key: "emergency-alert",
    label: "Emergency Alert",
    icon: ExclamationTriangleIcon,
    endpoint: "emergency-alert",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "alert_level",
        label: "Level",
        type: "select",
        options: [
          ["info", "Informational"],
          ["warning", "Warning"],
          ["critical", "Critical"],
          ["test", "Test"],
        ],
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["active", "Active"],
          ["resolved", "Resolved"],
          ["cancelled", "Cancelled"],
        ],
        badge: true,
      },
      { key: "message", label: "Message", type: "textarea", full: true, card: true },
      {
        key: "target_audience",
        label: "Audience",
        type: "select",
        options: AUDIENCE,
        card: true,
      },
      { key: "send_email", label: "Email", type: "bool", card: true },
      { key: "send_sms", label: "SMS", type: "bool", card: true },
      { key: "send_push", label: "Push", type: "bool", card: true },
      { key: "send_pa", label: "PA System", type: "bool", card: true },
      { key: "total_sent", label: "Sent", type: "number", skipForm: true },
      { key: "total_delivered", label: "Delivered", type: "number", skipForm: true },
      { key: "total_read", label: "Read", type: "number", skipForm: true },
      { key: "triggered_by_name", label: "Triggered By", card: true, skipForm: true },
      { key: "resolved_by_name", label: "Resolved By", card: true, skipForm: true },
      { key: "resolved_at", label: "Resolved At", type: "datetime", skipForm: true },
    ],
    searchKeys: ["title", "alert_level", "status"],
  },
  "communication-preference": {
    key: "communication-preference",
    label: "Communication Preference",
    icon: Cog6ToothIcon,
    endpoint: "communication-preference",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID" },
      { key: "email_enabled", label: "Email", type: "bool", card: true },
      { key: "sms_enabled", label: "SMS", type: "bool", card: true },
      { key: "push_enabled", label: "Push", type: "bool", card: true },
      { key: "in_app_enabled", label: "In-App", type: "bool", card: true },
      { key: "announcements", label: "Announcements", type: "bool", card: true },
      { key: "fee_notices", label: "Fee Notices", type: "bool", card: true },
      { key: "attendance_alerts", label: "Attendance Alerts", type: "bool", card: true },
      { key: "emergency_alerts", label: "Emergency Alerts", type: "bool", card: true },
      { key: "event_reminders", label: "Event Reminders", type: "bool", card: true },
      { key: "quiet_hours_start", label: "Quiet Hours Start", card: true },
    ],
    searchKeys: ["user_name"],
  },
  "message-template": {
    key: "message-template",
    label: "Message Template",
    icon: DocumentTextIcon,
    endpoint: "message-template",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "template_type",
        label: "Type",
        type: "select",
        options: [
          ["email", "Email"],
          ["sms", "SMS"],
          ["push", "Push"],
          ["in_app", "In-App"],
        ],
        badge: true,
      },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: [
          ["fee", "Fee"],
          ["attendance", "Attendance"],
          ["event", "Event"],
          ["academic", "Academic"],
          ["general", "General"],
          ["welcome", "Welcome"],
        ],
        badge: true,
      },
      { key: "subject", label: "Subject", card: true },
      { key: "body", label: "Body", type: "textarea", full: true, card: true },
      { key: "variables", label: "Variables", card: true },
      { key: "times_used", label: "Times Used", type: "number", card: true, skipForm: true },
      { key: "is_active", label: "Active", type: "bool", card: true },
      { key: "created_by_name", label: "Created By", card: true, skipForm: true },
    ],
    searchKeys: ["name", "template_type", "category"],
  },
  "message-delivery-status": {
    key: "message-delivery-status",
    label: "Delivery Status",
    icon: ArrowsRightLeftIcon,
    endpoint: "message-delivery-status",
    titleField: "recipient_name",
    fields: [
      { key: "recipient_name", label: "Recipient", main: true, skipForm: true },
      { key: "recipient", label: "Recipient ID", card: true },
      { key: "notification", label: "Notification ID", card: true },
      { key: "broadcast", label: "Broadcast ID", card: true },
      {
        key: "channel",
        label: "Channel",
        type: "select",
        options: CHANNELS,
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["sent", "Sent"],
          ["delivered", "Delivered"],
          ["read", "Read"],
          ["failed", "Failed"],
          ["bounced", "Bounced"],
        ],
        badge: true,
      },
      { key: "sent_at", label: "Sent", type: "datetime", card: true, skipForm: true },
      { key: "delivered_at", label: "Delivered", type: "datetime", card: true, skipForm: true },
      { key: "read_at", label: "Read", type: "datetime", card: true, skipForm: true },
      { key: "error_message", label: "Error", card: true },
    ],
    searchKeys: ["recipient_name", "channel", "status"],
  },
  "communication-blacklist": {
    key: "communication-blacklist",
    label: "Blacklist Entry",
    icon: NoSymbolIcon,
    endpoint: "communication-blacklist",
    titleField: "user_name",
    toggleField: "is_active",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID" },
      {
        key: "channel",
        label: "Channel",
        type: "select",
        options: CHANNELS,
        badge: true,
      },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: [
          ["marketing", "Marketing"],
          ["newsletter", "Newsletter"],
          ["fee", "Fee Reminders"],
          ["event", "Events"],
          ["all", "All"],
        ],
        badge: true,
      },
      { key: "reason", label: "Reason", type: "textarea", full: true, card: true },
      { key: "expires_at", label: "Expires", type: "datetime", card: true },
      { key: "is_active", label: "Active", type: "bool", card: true },
      { key: "blacklisted_at", label: "Blacklisted", type: "datetime", skipForm: true },
    ],
    searchKeys: ["user_name", "channel", "category"],
  },
  "communication-analytics": {
    key: "communication-analytics",
    label: "Communication Analytics",
    icon: ChartBarIcon,
    endpoint: "communication-analytics",
    titleField: "period_start",
    fields: [
      { key: "period_start", label: "Period Start", type: "date", main: true },
      { key: "period_end", label: "Period End", type: "date", subtitle: true },
      { key: "emails_sent", label: "Emails Sent", type: "number", card: true },
      { key: "emails_delivered", label: "Emails Delivered", type: "number", card: true },
      { key: "emails_opened", label: "Emails Opened", type: "number", card: true },
      { key: "emails_clicked", label: "Emails Clicked", type: "number", card: true },
      { key: "emails_bounced", label: "Emails Bounced", type: "number", card: true },
      { key: "sms_sent", label: "SMS Sent", type: "number", card: true },
      { key: "sms_delivered", label: "SMS Delivered", type: "number", card: true },
      { key: "sms_failed", label: "SMS Failed", type: "number", card: true },
      { key: "push_sent", label: "Push Sent", type: "number", card: true },
    ],
    searchKeys: [],
  },
  "notification-schedule": {
    key: "notification-schedule",
    label: "Notification Schedule",
    icon: ClockIcon,
    endpoint: "notification-schedule",
    titleField: "notification_title",
    fields: [
      { key: "notification_title", label: "Notification", main: true, skipForm: true },
      { key: "notification", label: "Notification ID", card: true },
      { key: "announcement", label: "Announcement ID", card: true },
      { key: "scheduled_at", label: "Scheduled", type: "datetime", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["sent", "Sent"],
          ["cancelled", "Cancelled"],
          ["failed", "Failed"],
        ],
        badge: true,
      },
      { key: "is_recurring", label: "Recurring", type: "bool", card: true },
      {
        key: "recurrence_pattern",
        label: "Recurrence",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["monthly", "Monthly"],
          ["termly", "Termly"],
        ],
        card: true,
      },
      { key: "recurrence_end", label: "Recurrence End", type: "datetime", card: true },
      { key: "last_executed", label: "Last Executed", type: "datetime", skipForm: true },
      { key: "next_execution", label: "Next Execution", type: "datetime", skipForm: true },
      { key: "execution_count", label: "Executions", type: "number", skipForm: true },
    ],
    searchKeys: ["notification_title", "status"],
  },
};

const TABS: { key: string; label: string; icon: React.ComponentType<{ className?: string }> }[] =
  Object.values(ENTITY_CONFIGS).map((c) => ({ key: c.key, label: c.label, icon: c.icon }));

// Fallback icon used by the poll-vote config before icons resolve (avoids an
// import-order dependency on CheckCircleIcon in EntitySection).
function CheckSquareFallback({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  );
}

// ─── Page shell ──────────────────────────────────────────────────────────────

export default function CommunicationPage() {
  useTitle("Communication Center");
  const [activeTab, setActiveTab] = useState("announcements");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Communication Center
          </h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Announcements, messaging, chat, conferences, surveys and delivery infrastructure
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
        basePath="/communication"
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
