/**
 * Access & Security Center — full-surface admin page for the auth module.
 *
 * 41 entity tabs (config-driven via EntitySection). Sessions, devices, roles, policies, API keys, webhooks, SSO, compliance and audit.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, ShieldCheckIcon } from "@heroicons/react/24/outline";

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  "a-p-i-key": {
    key: "a-p-i-key",
    icon: ShieldCheckIcon,
    label: "A P I Key",
    endpoint: "a-p-i-key",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "user_name", label: "User Name" },
      { key: "user_email", label: "User Email" },
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "key_prefix", label: "Key Prefix" },
      { key: "key_hash", label: "Key Hash" },
      { key: "scopes", label: "Scopes" },
      { key: "rate_limit", label: "Rate Limit" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["revoked", "Revoked"],
          ["expired", "Expired"],
        ],
      },
      { key: "status_display", label: "Status Display" },
      { key: "expires_at", label: "Expires At", type: "date" },
      { key: "last_used_at", label: "Last Used At", type: "date" },
      { key: "last_used_ip", label: "Last Used Ip" },
    ],
  },
  "a-p-i-usage-log": {
    key: "a-p-i-usage-log",
    icon: ShieldCheckIcon,
    label: "A P I Usage Log",
    endpoint: "a-p-i-usage-log",
    titleField: "api_key",
    fields: [
      { key: "api_key", label: "Api Key" },
      { key: "api_key_name", label: "Api Key Name" },
      { key: "endpoint", label: "Endpoint" },
      { key: "method", label: "Method" },
      { key: "status_code", label: "Status Code" },
      { key: "response_time_ms", label: "Response Time Ms" },
      { key: "request_size_bytes", label: "Request Size Bytes" },
      { key: "response_size_bytes", label: "Response Size Bytes" },
      { key: "ip_address", label: "Ip Address" },
      { key: "user_agent", label: "User Agent" },
      { key: "error_message", label: "Error Message", type: "textarea" },
      { key: "timestamp", label: "Timestamp" },
    ],
  },
  "audit-log": {
    key: "audit-log",
    icon: ShieldCheckIcon,
    label: "Audit Log",
    endpoint: "audit-log",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User Name" },
      { key: "user_email", label: "User Email" },
      { key: "action", label: "Action" },
      { key: "resource_type", label: "Resource Type" },
      { key: "resource_id", label: "Resource Id" },
      { key: "changes", label: "Changes" },
      { key: "ip_address", label: "Ip Address" },
      { key: "user_agent", label: "User Agent" },
      { key: "timestamp", label: "Timestamp" },
    ],
  },
  "audit-logs": {
    key: "audit-logs",
    icon: ShieldCheckIcon,
    label: "Audit Log",
    endpoint: "audit-logs",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User Name" },
      { key: "user_email", label: "User Email" },
      { key: "action", label: "Action" },
      { key: "resource_type", label: "Resource Type" },
      { key: "resource_id", label: "Resource Id" },
      { key: "changes", label: "Changes" },
      { key: "ip_address", label: "Ip Address" },
      { key: "user_agent", label: "User Agent" },
      { key: "timestamp", label: "Timestamp" },
    ],
  },
  "audit-report-schedule": {
    key: "audit-report-schedule",
    icon: ShieldCheckIcon,
    label: "Audit Report Schedule",
    endpoint: "audit-report-schedule",
    titleField: "name",
    subtitleField: "report_type",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: [
          ["login", "Login"],
          ["security", "Security"],
          ["api", "Api"],
          ["activity", "Activity"],
          ["compliance", "Compliance"],
        ],
      },
      {
        key: "frequency",
        label: "Frequency",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["monthly", "Monthly"],
          ["quarterly", "Quarterly"],
        ],
      },
      { key: "day_of_week", label: "Day Of Week" },
      { key: "day_of_month", label: "Day Of Month" },
      { key: "time_of_day", label: "Time Of Day" },
      { key: "recipients", label: "Recipients", type: "textarea" },
      { key: "email_delivery", label: "Email Delivery", type: "bool" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "last_generated", label: "Last Generated", type: "date" },
      { key: "next_generation", label: "Next Generation", type: "date" },
    ],
  },
  "auth-webhook": {
    key: "auth-webhook",
    icon: ShieldCheckIcon,
    label: "Auth Webhook",
    endpoint: "auth-webhook",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      { key: "url", label: "Url" },
      { key: "secret", label: "Secret" },
      {
        key: "event_type",
        label: "Event Type",
        type: "select",
        options: [
          ["login", "Login"],
          ["logout", "Logout"],
          ["password", "Password"],
          ["mfa_setup", "Mfa Setup"],
          ["user_create", "User Create"],
          ["user_deactivate", "User Deactivate"],
          ["role", "Role"],
          ["suspicious", "Suspicious"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["paused", "Paused"],
          ["disabled", "Disabled"],
        ],
      },
      { key: "headers", label: "Headers" },
      { key: "max_retries", label: "Max Retries" },
      { key: "retry_interval_seconds", label: "Retry Interval Seconds" },
      { key: "total_deliveries", label: "Total Deliveries" },
      { key: "successful_deliveries", label: "Successful Deliveries" },
      { key: "failed_deliveries", label: "Failed Deliveries" },
      { key: "last_triggered_at", label: "Last Triggered At", type: "date" },
    ],
  },
  "compliance-record": {
    key: "compliance-record",
    icon: ShieldCheckIcon,
    label: "Compliance Record",
    endpoint: "compliance-record",
    titleField: "compliance_type",
    subtitleField: "status",
    fields: [
      {
        key: "compliance_type",
        label: "Compliance Type",
        type: "select",
        options: [
          ["gdpr", "Gdpr"],
          ["ferpa", "Ferpa"],
          ["hipaa", "Hipaa"],
          ["soc2", "Soc2"],
          ["iso27001", "Iso27001"],
          ["custom", "Custom"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["compliant", "Compliant"],
          ["non_compliant", "Non Compliant"],
          ["in_progress", "In Progress"],
          ["exempt", "Exempt"],
        ],
      },
      { key: "requirement", label: "Requirement" },
      { key: "current_state", label: "Current State" },
      { key: "gap_analysis", label: "Gap Analysis" },
      { key: "remediation_plan", label: "Remediation Plan" },
      { key: "assessment_date", label: "Assessment Date", type: "date" },
      {
        key: "next_assessment_date",
        label: "Next Assessment Date",
        type: "date",
      },
      {
        key: "last_compliant_date",
        label: "Last Compliant Date",
        type: "date",
      },
      { key: "responsible_person", label: "Responsible Person" },
      { key: "evidence_file", label: "Evidence File" },
    ],
  },
  "consent-record": {
    key: "consent-record",
    icon: ShieldCheckIcon,
    label: "Consent Record",
    endpoint: "consent-record",
    titleField: "consent_type",
    subtitleField: "status",
    fields: [
      {
        key: "consent_type",
        label: "Consent Type",
        type: "select",
        options: [
          ["terms", "Terms"],
          ["privacy", "Privacy"],
          ["cookie", "Cookie"],
          ["data", "Data"],
          ["marketing", "Marketing"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["granted", "Granted"],
          ["denied", "Denied"],
          ["withdrawn", "Withdrawn"],
          ["pending", "Pending"],
        ],
      },
      { key: "policy_version", label: "Policy Version" },
      { key: "policy_url", label: "Policy Url" },
      { key: "consented_at", label: "Consented At", type: "date" },
      { key: "withdrawn_at", label: "Withdrawn At", type: "date" },
      { key: "ip_address", label: "Ip Address" },
      { key: "user_agent", label: "User Agent" },
    ],
  },
  "data-deletion-request": {
    key: "data-deletion-request",
    icon: ShieldCheckIcon,
    label: "Data Deletion Request",
    endpoint: "data-deletion-request",
    titleField: "status",
    fields: [
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["reviewing", "Reviewing"],
          ["processing", "Processing"],
          ["completed", "Completed"],
          ["denied", "Denied"],
        ],
      },
      { key: "reason", label: "Reason" },
      { key: "data_scope", label: "Data Scope" },
      { key: "reviewed_by", label: "Reviewed By" },
      { key: "review_notes", label: "Review Notes" },
      { key: "requested_at", label: "Requested At", type: "date" },
      { key: "reviewed_at", label: "Reviewed At", type: "date" },
      { key: "completed_at", label: "Completed At", type: "date" },
      { key: "denial_reason", label: "Denial Reason" },
    ],
  },
  "data-export-request": {
    key: "data-export-request",
    icon: ShieldCheckIcon,
    label: "Data Export Request",
    endpoint: "data-export-request",
    titleField: "data_type",
    subtitleField: "status",
    fields: [
      {
        key: "data_type",
        label: "Data Type",
        type: "select",
        options: [
          ["all", "All"],
          ["profile", "Profile"],
          ["activity", "Activity"],
          ["academic", "Academic"],
          ["financial", "Financial"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["processing", "Processing"],
          ["completed", "Completed"],
          ["failed", "Failed"],
        ],
      },
      { key: "requested_at", label: "Requested At", type: "date" },
      { key: "completed_at", label: "Completed At", type: "date" },
      { key: "export_file", label: "Export File" },
      { key: "file_size_bytes", label: "File Size Bytes", type: "number" },
      { key: "expires_at", label: "Expires At", type: "date" },
      { key: "error_message", label: "Error Message", type: "textarea" },
      { key: "processed_by", label: "Processed By" },
    ],
  },
  "device-management": {
    key: "device-management",
    icon: ShieldCheckIcon,
    label: "Device Management",
    endpoint: "device-management",
    titleField: "user_name",
    subtitleField: "status",
    fields: [
      { key: "user_name", label: "User Name" },
      { key: "user_email", label: "User Email" },
      { key: "device_name", label: "Device Name" },
      { key: "device_type", label: "Device Type" },
      { key: "device_type_display", label: "Device Type Display" },
      { key: "device_id", label: "Device Id" },
      { key: "fingerprint", label: "Fingerprint" },
      { key: "ip_address", label: "Ip Address" },
      { key: "location", label: "Location" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["trusted", "Trusted"],
          ["pending", "Pending"],
          ["blocked", "Blocked"],
        ],
      },
      { key: "status_display", label: "Status Display" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "last_seen", label: "Last Seen", type: "date" },
      { key: "trusted_at", label: "Trusted At", type: "date" },
      { key: "blocked_at", label: "Blocked At", type: "date" },
    ],
  },
  "domain-verification": {
    key: "domain-verification",
    icon: ShieldCheckIcon,
    label: "Domain Verification",
    endpoint: "domain-verification",
    titleField: "domain",
    subtitleField: "status",
    fields: [
      { key: "domain", label: "Domain" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["verified", "Verified"],
          ["failed", "Failed"],
          ["expired", "Expired"],
        ],
      },
      { key: "verification_token", label: "Verification Token" },
      { key: "verification_method", label: "Verification Method" },
      { key: "txt_record_name", label: "Txt Record Name" },
      { key: "txt_record_value", label: "Txt Record Value" },
      { key: "verified_at", label: "Verified At", type: "date" },
      { key: "expires_at", label: "Expires At", type: "date" },
    ],
  },
  "email-verification-token": {
    key: "email-verification-token",
    icon: ShieldCheckIcon,
    label: "Email Verification Token",
    endpoint: "email-verification-token",
    titleField: "email",
    fields: [
      { key: "email", label: "Email" },
      { key: "token", label: "Token" },
      { key: "expires_at", label: "Expires At", type: "date" },
      { key: "used", label: "Used" },
    ],
  },
  "i-p-geolocation-cache": {
    key: "i-p-geolocation-cache",
    icon: ShieldCheckIcon,
    label: "I P Geolocation Cache",
    endpoint: "i-p-geolocation-cache",
    titleField: "ip_address",
    fields: [
      { key: "ip_address", label: "Ip Address" },
      { key: "country", label: "Country" },
      { key: "region", label: "Region" },
      { key: "city", label: "City" },
      { key: "latitude", label: "Latitude" },
      { key: "longitude", label: "Longitude" },
      { key: "timezone", label: "Timezone" },
      { key: "isp", label: "Isp" },
      { key: "is_vpn", label: "Is Vpn" },
      { key: "is_proxy", label: "Is Proxy" },
      { key: "fetched_at", label: "Fetched At", type: "date" },
      { key: "expires_at", label: "Expires At", type: "date" },
    ],
  },
  "i-p-whitelist": {
    key: "i-p-whitelist",
    icon: ShieldCheckIcon,
    label: "I P Whitelist",
    endpoint: "i-p-whitelist",
    titleField: "ip_address",
    subtitleField: "access_level",
    fields: [
      { key: "ip_address", label: "Ip Address" },
      { key: "ip_range", label: "Ip Range" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "access_level",
        label: "Access Level",
        type: "select",
        options: [
          ["admin", "Admin"],
          ["staff", "Staff"],
          ["all", "All"],
          ["api", "Api"],
        ],
      },
      { key: "access_level_display", label: "Access Level Display" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "login-attempt": {
    key: "login-attempt",
    icon: ShieldCheckIcon,
    label: "Login Attempt",
    endpoint: "login-attempt",
    titleField: "username",
    subtitleField: "status",
    fields: [
      { key: "username", label: "Username" },
      { key: "email", label: "Email" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["success", "Success"],
          ["failed", "Failed"],
          ["locked", "Locked"],
          ["blocked", "Blocked"],
        ],
      },
      { key: "failure_reason", label: "Failure Reason" },
      { key: "ip_address", label: "Ip Address" },
      { key: "user_agent", label: "User Agent" },
      { key: "device_info", label: "Device Info" },
      { key: "city", label: "City" },
      { key: "country", label: "Country" },
      { key: "attempted_at", label: "Attempted At", type: "date" },
    ],
  },
  "login-history": {
    key: "login-history",
    icon: ShieldCheckIcon,
    label: "Login History",
    endpoint: "login-history",
    titleField: "user_name",
    subtitleField: "status",
    fields: [
      { key: "user_name", label: "User Name" },
      { key: "email", label: "Email" },
      {
        key: "login_type",
        label: "Login Type",
        type: "select",
        options: [
          ["password", "Password"],
          ["two_factor", "Two Factor"],
          ["oauth", "Oauth"],
          ["sso", "Sso"],
          ["magic_link", "Magic Link"],
          ["passkey", "Passkey"],
        ],
      },
      { key: "login_type_display", label: "Login Type Display" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["success", "Success"],
          ["failed", "Failed"],
          ["blocked", "Blocked"],
          ["pending_2fa", "Pending 2Fa"],
        ],
      },
      { key: "status_display", label: "Status Display" },
      { key: "ip_address", label: "Ip Address" },
      { key: "user_agent", label: "User Agent" },
      { key: "device_info", label: "Device Info" },
      { key: "location", label: "Location" },
      { key: "country", label: "Country" },
      { key: "city", label: "City" },
      { key: "failure_reason", label: "Failure Reason" },
      { key: "session_id", label: "Session Id" },
    ],
  },
  "m-f-a-method": {
    key: "m-f-a-method",
    icon: ShieldCheckIcon,
    label: "M F A Method",
    endpoint: "m-f-a-method",
    titleField: "method_type",
    subtitleField: "status",
    fields: [
      {
        key: "method_type",
        label: "Method Type",
        type: "select",
        options: [
          ["totp", "Totp"],
          ["sms", "Sms"],
          ["email", "Email"],
          ["hardware", "Hardware"],
          ["backup", "Backup"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["pending", "Pending"],
          ["disabled", "Disabled"],
        ],
      },
      { key: "totp_secret", label: "Totp Secret" },
      { key: "phone_number", label: "Phone Number" },
      { key: "email_address", label: "Email Address" },
      { key: "hardware_key_id", label: "Hardware Key Id" },
      { key: "public_key", label: "Public Key" },
      { key: "backup_codes", label: "Backup Codes" },
      { key: "last_used_at", label: "Last Used At", type: "date" },
      { key: "use_count", label: "Use Count" },
    ],
  },
  "m-f-a-verification": {
    key: "m-f-a-verification",
    icon: ShieldCheckIcon,
    label: "M F A Verification",
    endpoint: "m-f-a-verification",
    titleField: "mfa_method",
    subtitleField: "status",
    fields: [
      { key: "mfa_method", label: "Mfa Method" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["success", "Success"],
          ["failed", "Failed"],
          ["expired", "Expired"],
        ],
      },
      { key: "ip_address", label: "Ip Address" },
      { key: "user_agent", label: "User Agent" },
      { key: "attempted_at", label: "Attempted At", type: "date" },
    ],
  },
  "o-auth-provider": {
    key: "o-auth-provider",
    icon: ShieldCheckIcon,
    label: "O Auth Provider",
    endpoint: "o-auth-provider",
    titleField: "name",
    fields: [
      {
        key: "provider_type",
        label: "Provider Type",
        type: "select",
        options: [
          ["google", "Google"],
          ["microsoft", "Microsoft"],
          ["github", "Github"],
          ["apple", "Apple"],
          ["facebook", "Facebook"],
          ["other", "Other"],
        ],
      },
      { key: "name", label: "Name" },
      { key: "client_id", label: "Client Id" },
      { key: "client_secret", label: "Client Secret" },
      { key: "redirect_uri", label: "Redirect Uri" },
      { key: "scopes", label: "Scopes" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "o-auth-token": {
    key: "o-auth-token",
    icon: ShieldCheckIcon,
    label: "O Auth Token",
    endpoint: "o-auth-token",
    titleField: "provider",
    subtitleField: "status",
    fields: [
      { key: "provider", label: "Provider" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["expired", "Expired"],
          ["revoked", "Revoked"],
        ],
      },
      { key: "access_token", label: "Access Token" },
      { key: "refresh_token", label: "Refresh Token" },
      { key: "token_type", label: "Token Type" },
      { key: "provider_user_id", label: "Provider User Id" },
      { key: "provider_username", label: "Provider Username" },
      { key: "provider_email", label: "Provider Email" },
      { key: "expires_at", label: "Expires At", type: "date" },
      { key: "scopes", label: "Scopes" },
    ],
  },
  "password-history": {
    key: "password-history",
    icon: ShieldCheckIcon,
    label: "Password History",
    endpoint: "password-history",
    titleField: "password_hash",
    fields: [
      { key: "password_hash", label: "Password Hash" },
      { key: "changed_at", label: "Changed At", type: "date" },
      { key: "changed_by", label: "Changed By" },
      { key: "change_reason", label: "Change Reason" },
    ],
  },
  "password-policy": {
    key: "password-policy",
    icon: ShieldCheckIcon,
    label: "Password Policy",
    endpoint: "password-policy",
    titleField: "min_length",
    fields: [
      { key: "min_length", label: "Min Length" },
      { key: "max_length", label: "Max Length" },
      { key: "require_uppercase", label: "Require Uppercase" },
      { key: "require_lowercase", label: "Require Lowercase" },
      { key: "require_digit", label: "Require Digit" },
      { key: "require_special_char", label: "Require Special Char" },
      { key: "special_chars", label: "Special Chars" },
      { key: "prevent_REUSE", label: "Prevent  R E U S E" },
      { key: "max_age_days", label: "Max Age Days" },
      { key: "lockout_attempts", label: "Lockout Attempts" },
      { key: "lockout_duration_minutes", label: "Lockout Duration Minutes" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "password-reset-token": {
    key: "password-reset-token",
    icon: ShieldCheckIcon,
    label: "Password Reset Token",
    endpoint: "password-reset-token",
    titleField: "token",
    fields: [
      { key: "token", label: "Token" },
      { key: "expires_at", label: "Expires At", type: "date" },
      { key: "used", label: "Used" },
    ],
  },
  permission: {
    key: "permission",
    icon: ShieldCheckIcon,
    label: "Permission",
    endpoint: "permission",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "codename", label: "Codename" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "permission_type",
        label: "Permission Type",
        type: "select",
        options: [
          ["module", "Module"],
          ["action", "Action"],
          ["data", "Data"],
          ["report", "Report"],
        ],
      },
      { key: "permission_type_display", label: "Permission Type Display" },
      { key: "module", label: "Module" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  role: {
    key: "role",
    icon: ShieldCheckIcon,
    label: "Role",
    endpoint: "role",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "parent_role", label: "Parent Role" },
      { key: "level", label: "Level" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "is_system_role", label: "Is System Role" },
      { key: "permission_count", label: "Permission Count" },
    ],
  },
  "role-permission": {
    key: "role-permission",
    icon: ShieldCheckIcon,
    label: "Role Permission",
    endpoint: "role-permission",
    titleField: "role",
    fields: [
      { key: "role", label: "Role" },
      { key: "role_name", label: "Role Name" },
      { key: "permission", label: "Permission" },
      { key: "permission_name", label: "Permission Name" },
      { key: "permission_codename", label: "Permission Codename" },
      { key: "permission_module", label: "Permission Module" },
      { key: "permission_type_display", label: "Permission Type Display" },
      { key: "granted", label: "Granted" },
      { key: "conditions", label: "Conditions" },
      { key: "granted_at", label: "Granted At", type: "date" },
      { key: "granted_by", label: "Granted By" },
      { key: "granted_by_name", label: "Granted By Name" },
    ],
  },
  "s-s-o-configuration": {
    key: "s-s-o-configuration",
    icon: ShieldCheckIcon,
    label: "S S O Configuration",
    endpoint: "s-s-o-configuration",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "provider",
        label: "Provider",
        type: "select",
        options: [
          ["saml", "Saml"],
          ["oidc", "Oidc"],
          ["cas", "Cas"],
          ["azure", "Azure"],
          ["google", "Google"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["configuring", "Configuring"],
          ["disabled", "Disabled"],
        ],
      },
      { key: "entity_id", label: "Entity Id" },
      { key: "sso_url", label: "Sso Url" },
      { key: "slo_url", label: "Slo Url" },
      { key: "x509_cert", label: "X509 Cert" },
      { key: "client_id", label: "Client Id" },
      { key: "client_secret", label: "Client Secret" },
      { key: "discovery_url", label: "Discovery Url" },
      { key: "attribute_mapping", label: "Attribute Mapping" },
      { key: "is_default", label: "Is Default", type: "bool" },
    ],
  },
  "school-feature-flag": {
    key: "school-feature-flag",
    icon: ShieldCheckIcon,
    label: "School Feature Flag",
    endpoint: "school-feature-flag",
    titleField: "feature_name",
    subtitleField: "category",
    fields: [
      { key: "feature_name", label: "Feature Name" },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: [
          ["auth", "Auth"],
          ["enrollment", "Enrollment"],
          ["billing", "Billing"],
          ["reporting", "Reporting"],
          ["integration", "Integration"],
          ["ui", "Ui"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "is_enabled", label: "Is Enabled" },
      { key: "rollout_percentage", label: "Rollout Percentage" },
      { key: "conditions", label: "Conditions" },
    ],
  },
  schools: {
    key: "schools",
    icon: ShieldCheckIcon,
    label: "School",
    endpoint: "schools",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "code", label: "Code" },
      { key: "subdomain", label: "Subdomain" },
      { key: "logo", label: "Logo" },
      { key: "address", label: "Address" },
      { key: "phone", label: "Phone" },
      { key: "email", label: "Email" },
      { key: "website", label: "Website" },
      { key: "timezone", label: "Timezone" },
      { key: "academic_year_start_month", label: "Academic Year Start Month" },
      { key: "is_active", label: "Is Active", type: "bool" },
      {
        key: "subscription_tier",
        label: "Subscription Tier",
        type: "select",
        options: [
          ["basic", "Basic"],
          ["standard", "Standard"],
          ["premium", "Premium"],
        ],
      },
    ],
  },
  "security-policy": {
    key: "security-policy",
    icon: ShieldCheckIcon,
    label: "Security Policy",
    endpoint: "security-policy",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "policy_type",
        label: "Policy Type",
        type: "select",
        options: [
          ["password", "Password"],
          ["session", "Session"],
          ["login", "Login"],
          ["mfa", "Mfa"],
          ["api", "Api"],
          ["ip", "Ip"],
        ],
      },
      { key: "policy_type_display", label: "Policy Type Display" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "settings", label: "Settings" },
      { key: "min_length", label: "Min Length" },
      { key: "require_uppercase", label: "Require Uppercase" },
      { key: "require_lowercase", label: "Require Lowercase" },
      { key: "require_numbers", label: "Require Numbers" },
      { key: "require_special", label: "Require Special" },
      { key: "max_age_days", label: "Max Age Days" },
      { key: "history_count", label: "History Count" },
      { key: "session_timeout_minutes", label: "Session Timeout Minutes" },
    ],
  },
  "session-policy": {
    key: "session-policy",
    icon: ShieldCheckIcon,
    label: "Session Policy",
    endpoint: "session-policy",
    titleField: "session_timeout_minutes",
    fields: [
      { key: "session_timeout_minutes", label: "Session Timeout Minutes" },
      { key: "absolute_timeout_hours", label: "Absolute Timeout Hours" },
      { key: "idle_timeout_minutes", label: "Idle Timeout Minutes" },
      { key: "max_concurrent_sessions", label: "Max Concurrent Sessions" },
      { key: "enforce_single_session", label: "Enforce Single Session" },
      { key: "require_reauthentication", label: "Require Reauthentication" },
      {
        key: "reauthentication_interval_minutes",
        label: "Reauthentication Interval Minutes",
      },
      { key: "remember_me_days", label: "Remember Me Days" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "session-token": {
    key: "session-token",
    icon: ShieldCheckIcon,
    label: "Session Token",
    endpoint: "session-token",
    titleField: "user_name",
    subtitleField: "status",
    fields: [
      { key: "user_name", label: "User Name" },
      { key: "user_email", label: "User Email" },
      {
        key: "token_type",
        label: "Token Type",
        type: "select",
        options: [
          ["access", "Access"],
          ["refresh", "Refresh"],
          ["reset", "Reset"],
          ["verify", "Verify"],
          ["api", "Api"],
        ],
      },
      { key: "token_type_display", label: "Token Type Display" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["expired", "Expired"],
          ["revoked", "Revoked"],
          ["blacklisted", "Blacklisted"],
        ],
      },
      { key: "status_display", label: "Status Display" },
      { key: "token_hash", label: "Token Hash" },
      { key: "issued_at", label: "Issued At", type: "date" },
      { key: "expires_at", label: "Expires At", type: "date" },
      { key: "last_used_at", label: "Last Used At", type: "date" },
      { key: "device_info", label: "Device Info" },
      { key: "ip_address", label: "Ip Address" },
      { key: "revoked_at", label: "Revoked At", type: "date" },
      { key: "revocation_reason", label: "Revocation Reason" },
    ],
  },
  "two-factor-backup-code": {
    key: "two-factor-backup-code",
    icon: ShieldCheckIcon,
    label: "Two Factor Backup Code",
    endpoint: "two-factor-backup-code",
    titleField: "hashed_code",
    fields: [
      { key: "hashed_code", label: "Hashed Code" },
      { key: "used", label: "Used" },
    ],
  },
  "user-activity": {
    key: "user-activity",
    icon: ShieldCheckIcon,
    label: "User Activity",
    endpoint: "user-activity",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User Name" },
      { key: "user_email", label: "User Email" },
      {
        key: "activity_type",
        label: "Activity Type",
        type: "select",
        options: [
          ["login", "Login"],
          ["logout", "Logout"],
          ["password_change", "Password Change"],
          ["profile_update", "Profile Update"],
          ["settings_change", "Settings Change"],
          ["data_export", "Data Export"],
          ["data_import", "Data Import"],
          ["file_upload", "File Upload"],
          ["file_download", "File Download"],
          ["report_view", "Report View"],
          ["other", "Other"],
        ],
      },
      { key: "activity_type_display", label: "Activity Type Display" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "resource_type", label: "Resource Type" },
      { key: "resource_id", label: "Resource Id" },
      { key: "ip_address", label: "Ip Address" },
      { key: "user_agent", label: "User Agent" },
      { key: "metadata", label: "Metadata" },
    ],
  },
  "user-directory": {
    key: "user-directory",
    icon: ShieldCheckIcon,
    label: "User Directory",
    endpoint: "user-directory",
    titleField: "email",
    fields: [
      { key: "email", label: "Email" },
      { key: "first_name", label: "First Name" },
      { key: "last_name", label: "Last Name" },
      { key: "full_name", label: "Full Name" },
      { key: "role", label: "Role" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "avatar", label: "Avatar" },
    ],
  },
  "user-role": {
    key: "user-role",
    icon: ShieldCheckIcon,
    label: "User Role",
    endpoint: "user-role",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User Name" },
      { key: "user_email", label: "User Email" },
      { key: "role", label: "Role" },
      { key: "role_name", label: "Role Name" },
      { key: "scope", label: "Scope" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "assigned_date", label: "Assigned Date", type: "date" },
      { key: "expiry_date", label: "Expiry Date", type: "date" },
      { key: "assigned_by", label: "Assigned By" },
      { key: "assigned_by_name", label: "Assigned By Name" },
    ],
  },
  "user-session": {
    key: "user-session",
    icon: ShieldCheckIcon,
    label: "User Session",
    endpoint: "user-session",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User Name" },
      { key: "user_email", label: "User Email" },
      { key: "refresh_token_jti", label: "Refresh Token Jti" },
      { key: "device_info", label: "Device Info" },
      { key: "ip_address", label: "Ip Address" },
      { key: "last_used", label: "Last Used" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "user-session-history": {
    key: "user-session-history",
    icon: ShieldCheckIcon,
    label: "User Session History",
    endpoint: "user-session-history",
    titleField: "session_id",
    subtitleField: "device_type",
    fields: [
      { key: "session_id", label: "Session Id" },
      { key: "device_type", label: "Device Type" },
      { key: "device_name", label: "Device Name" },
      { key: "os", label: "Os" },
      { key: "browser", label: "Browser" },
      { key: "ip_address", label: "Ip Address" },
      { key: "city", label: "City" },
      { key: "country", label: "Country" },
      { key: "login_at", label: "Login At", type: "date" },
      { key: "last_active_at", label: "Last Active At", type: "date" },
      { key: "logout_at", label: "Logout At", type: "date" },
      { key: "duration_minutes", label: "Duration Minutes" },
    ],
  },
  "user-trust-score": {
    key: "user-trust-score",
    icon: ShieldCheckIcon,
    label: "User Trust Score",
    endpoint: "user-trust-score",
    titleField: "trust_score",
    fields: [
      { key: "trust_score", label: "Trust Score" },
      { key: "risk_level", label: "Risk Level" },
      { key: "account_age_days", label: "Account Age Days" },
      { key: "successful_logins", label: "Successful Logins" },
      { key: "failed_logins", label: "Failed Logins" },
      { key: "suspicious_activities", label: "Suspicious Activities" },
      { key: "devices_used", label: "Devices Used" },
      { key: "locations_used", label: "Locations Used" },
      { key: "mfa_enabled", label: "Mfa Enabled" },
      { key: "mfa_methods_count", label: "Mfa Methods Count" },
      { key: "last_login", label: "Last Login", type: "date" },
      { key: "last_password_change", label: "Last Password Change" },
    ],
  },
  "webhook-delivery": {
    key: "webhook-delivery",
    icon: ShieldCheckIcon,
    label: "Webhook Delivery",
    endpoint: "webhook-delivery",
    titleField: "webhook",
    subtitleField: "status",
    fields: [
      { key: "webhook", label: "Webhook" },
      { key: "payload", label: "Payload" },
      { key: "headers", label: "Headers" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["success", "Success"],
          ["failed", "Failed"],
          ["retrying", "Retrying"],
          ["pending", "Pending"],
        ],
      },
      { key: "response_status_code", label: "Response Status Code" },
      { key: "response_body", label: "Response Body" },
      { key: "error_message", label: "Error Message", type: "textarea" },
      { key: "attempt_number", label: "Attempt Number" },
      { key: "max_attempts", label: "Max Attempts" },
      { key: "next_retry_at", label: "Next Retry At", type: "date" },
      { key: "sent_at", label: "Sent At", type: "date" },
      { key: "completed_at", label: "Completed At", type: "date" },
      { key: "response_time_ms", label: "Response Time Ms" },
    ],
  },
};

const TABS = Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({
  key,
  label: cfg.label,
  icon: ShieldCheckIcon,
}));

export default function AuthCenterPage() {
  useTitle("Access & Security Center");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Access & Security Center
          </h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Sessions, devices, roles, policies, API keys, webhooks, SSO, compliance and audit
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
            leftIcon={<ShieldCheckIcon className="h-4 w-4" />}
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
        basePath="/auth"
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
