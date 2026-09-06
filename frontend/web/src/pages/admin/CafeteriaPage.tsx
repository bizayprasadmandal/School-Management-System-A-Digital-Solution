/**
 * Cafeteria Center — full-surface admin page for the cafeteria module.
 *
 * 40 entity tabs (config-driven via EntitySection): menus, plans, bookings,
 * dietary, POS/payments/accounts, inventory/vendors, allergen/nutrition,
 * production/waste, online ordering, food safety, staff/feedback,
 * reservations/alerts, subscriptions and analytics.
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
  CalendarDaysIcon,
  ChartBarIcon,
  ClipboardDocumentCheckIcon,
  ClipboardDocumentListIcon,
  DocumentChartBarIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  IdentificationIcon,
  KeyIcon,
  QueueListIcon,
  ScaleIcon,
  ServerIcon,
  StarIcon,
  SunIcon,
  TagIcon,
  TicketIcon,
  TrophyIcon,
  UserGroupIcon,
  UsersIcon,
  WrenchScrewdriverIcon,
  ArrowPathIcon,
  BanknotesIcon,
  BellAlertIcon,
  BuildingOfficeIcon,
  CheckBadgeIcon,
  CircleStackIcon,
  ClockIcon,
  Cog6ToothIcon,
  CreditCardIcon,
  CubeIcon,
  DocumentCheckIcon,
  FireIcon,
  GiftIcon,
  HomeModernIcon,
  InboxIcon,
  LightBulbIcon,
  LockClosedIcon,
  NewspaperIcon,
  NoSymbolIcon,
  PaperClipIcon,
  PhoneIcon,
  ReceiptPercentIcon,
  ShieldCheckIcon,
  ShoppingBagIcon,
  SparklesIcon,
  Square2StackIcon,
  TrashIcon,
  TruckIcon,
  WalletIcon,
} from "@heroicons/react/24/outline";

// ─── Shared option sets ──────────────────────────────────────────────────────

const MEAL_TYPES = [
  ["breakfast", "Breakfast"],
  ["lunch", "Lunch"],
  ["dinner", "Dinner"],
  ["snack", "Snack"],
] as [string, string][];

const PLAN_STATUS = [
  ["active", "Active"],
  ["expired", "Expired"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const BOOKING_STATUS = [
  ["confirmed", "Confirmed"],
  ["attended", "Attended"],
  ["cancelled", "Cancelled"],
  ["no_show", "No Show"],
] as [string, string][];

const PAYMENT_METHODS = [
  ["pin", "PIN"],
  ["barcode", "Barcode"],
  ["biometric", "Biometric"],
  ["card", "Card"],
  ["cash", "Cash"],
] as [string, string][];

const PAYMENT_TXN_METHODS = [
  ["credit_card", "Credit Card"],
  ["debit_card", "Debit Card"],
  ["ach", "ACH"],
  ["check", "Check"],
  ["cash", "Cash"],
  ["other", "Other"],
] as [string, string][];

const PAYMENT_STATUS = [
  ["pending", "Pending"],
  ["completed", "Completed"],
  ["failed", "Failed"],
  ["refunded", "Refunded"],
] as [string, string][];

const ELIGIBILITY = [
  ["free", "Free"],
  ["reduced", "Reduced"],
  ["paid", "Paid"],
] as [string, string][];

const ELIGIBILITY_STATUS = [
  ["active", "Active"],
  ["expired", "Expired"],
  ["pending", "Pending"],
  ["denied", "Denied"],
] as [string, string][];

const INVENTORY_CATEGORIES = [
  ["produce", "Produce"],
  ["dairy", "Dairy"],
  ["meat", "Meat"],
  ["grains", "Grains"],
  ["beverages", "Beverages"],
  ["frozen", "Frozen"],
  ["dry_goods", "Dry Goods"],
  ["condiments", "Condiments"],
  ["other", "Other"],
] as [string, string][];

const UNITS = [
  ["kg", "kg"],
  ["g", "grams"],
  ["l", "liters"],
  ["ml", "ml"],
  ["pcs", "pieces"],
  ["boxes", "boxes"],
  ["bags", "bags"],
] as [string, string][];

const REPORT_TYPES = [
  ["daily", "Daily"],
  ["monthly", "Monthly"],
  ["quarterly", "Quarterly"],
  ["annual", "Annual"],
] as [string, string][];

const REPORT_STATUS = [
  ["draft", "Draft"],
  ["submitted", "Submitted"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
] as [string, string][];

const PREORDER_STATUS = [
  ["pending", "Pending"],
  ["confirmed", "Confirmed"],
  ["cancelled", "Cancelled"],
  ["fulfilled", "Fulfilled"],
] as [string, string][];

const ACCOUNT_STATUS = [
  ["active", "Active"],
  ["suspended", "Suspended"],
  ["closed", "Closed"],
] as [string, string][];

const SEVERITIES = [
  ["mild", "Mild"],
  ["moderate", "Moderate"],
  ["severe", "Severe"],
  ["life_threatening", "Life Threatening"],
] as [string, string][];

const ALLERGEN_STATUS = [
  ["active", "Active"],
  ["inactive", "Inactive"],
  ["suspended", "Suspended"],
] as [string, string][];

const VENDOR_STATUS = [
  ["active", "Active"],
  ["inactive", "Inactive"],
  ["suspended", "Suspended"],
] as [string, string][];

const VENDOR_ORDER_STATUS = [
  ["draft", "Draft"],
  ["submitted", "Submitted"],
  ["confirmed", "Confirmed"],
  ["delivered", "Delivered"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const PRODUCTION_STATUS = [
  ["planned", "Planned"],
  ["in_progress", "In Progress"],
  ["completed", "Completed"],
] as [string, string][];

const WASTE_TYPES = [
  ["prep", "Prep"],
  ["plate", "Plate"],
  ["spoiled", "Spoiled"],
  ["other", "Other"],
] as [string, string][];

const ONLINE_ORDER_STATUS = [
  ["pending", "Pending"],
  ["confirmed", "Confirmed"],
  ["preparing", "Preparing"],
  ["ready", "Ready"],
  ["delivered", "Delivered"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const DELIVERY_STATUS = [
  ["scheduled", "Scheduled"],
  ["in_transit", "In Transit"],
  ["delivered", "Delivered"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const CHECK_TYPES = [
  ["temperature", "Temperature"],
  ["cleanliness", "Cleanliness"],
  ["storage", "Storage"],
  ["hygiene", "Personal Hygiene"],
  ["equipment", "Equipment"],
  ["waste", "Waste"],
] as [string, string][];

const CHECK_STATUS = [
  ["pass", "Pass"],
  ["fail", "Fail"],
  ["conditional", "Conditional"],
  ["pending", "Pending"],
] as [string, string][];

const INCIDENT_SEVERITY = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
  ["critical", "Critical"],
] as [string, string][];

const INCIDENT_STATUS = [
  ["reported", "Reported"],
  ["investigating", "Investigating"],
  ["resolved", "Resolved"],
  ["closed", "Closed"],
] as [string, string][];

const STAFF_ROLES = [
  ["cook", "Cook"],
  ["assistant", "Assistant"],
  ["cashier", "Cashier"],
  ["manager", "Manager"],
  ["cleaner", "Cleaner"],
  ["delivery", "Delivery"],
  ["supervisor", "Supervisor"],
] as [string, string][];

const FEEDBACK_TYPES = [
  ["food", "Food Quality"],
  ["service", "Service"],
  ["cleanliness", "Cleanliness"],
  ["price", "Price"],
  ["wait", "Wait Time"],
  ["general", "General"],
] as [string, string][];

const PREORDER_MEAL_STATUS = [
  ["pending", "Pending"],
  ["confirmed", "Confirmed"],
  ["preparing", "Preparing"],
  ["ready", "Ready"],
  ["collected", "Collected"],
  ["cancelled", "Cancelled"],
] as [string, string][];

const EQUIPMENT_TYPES = [
  ["oven", "Oven"],
  ["fridge", "Refrigerator"],
  ["freezer", "Freezer"],
  ["dishwasher", "Dishwasher"],
  ["mixer", "Mixer"],
  ["fryer", "Fryer"],
  ["steamer", "Steamer"],
  ["warmer", "Warmer"],
  ["other", "Other"],
] as [string, string][];

const EQUIPMENT_STATUS = [
  ["working", "Working"],
  ["maintenance", "Maintenance"],
  ["broken", "Broken"],
  ["retired", "Retired"],
] as [string, string][];

const RESERVATION_TYPES = [
  ["event", "Event"],
  ["meeting", "Meeting"],
  ["celebration", "Celebration"],
  ["lunch_meeting", "Meeting Lunch"],
] as [string, string][];

const RESERVATION_STATUS = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["denied", "Denied"],
  ["cancelled", "Cancelled"],
  ["completed", "Completed"],
] as [string, string][];

const ALERT_TYPES = [
  ["inventory", "Low Inventory"],
  ["equipment", "Equipment Failure"],
  ["safety", "Safety Issue"],
  ["waste", "Food Waste"],
  ["budget", "Overbudget"],
  ["staff", "Staff Shortage"],
] as [string, string][];

const ALERT_SEVERITY = [
  ["low", "Low"],
  ["medium", "Medium"],
  ["high", "High"],
] as [string, string][];

const ALERT_STATUS = [
  ["active", "Active"],
  ["acknowledged", "Acknowledged"],
  ["resolved", "Resolved"],
] as [string, string][];

const SUBSCRIPTION_PLANS = [
  ["weekly", "Weekly"],
  ["monthly", "Monthly"],
  ["quarterly", "Quarterly"],
  ["yearly", "Yearly"],
] as [string, string][];

const SUBSCRIPTION_STATUS = [
  ["active", "Active"],
  ["paused", "Paused"],
  ["cancelled", "Cancelled"],
  ["expired", "Expired"],
] as [string, string][];

const INVENTORY_ALERT_TYPES = [
  ["low_stock", "Low Stock"],
  ["expiring", "Expiring"],
  ["out_of_stock", "Out of Stock"],
  ["price", "Price Change"],
] as [string, string][];

const INVENTORY_ALERT_STATUS = [
  ["active", "Active"],
  ["acknowledged", "Acknowledged"],
  ["resolved", "Resolved"],
] as [string, string][];

// ─── Entity configs (40 tabs) ────────────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  menus: {
    key: "menus",
    label: "Menu",
    icon: BookOpenIcon,
    endpoint: "menus",
    titleField: "name",
    subtitleField: "meal_type",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "meal_type",
        label: "Meal Type",
        type: "select",
        options: MEAL_TYPES,
        subtitle: true,
        badge: true,
      },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "calories", label: "Calories", type: "number", card: true },
      { key: "price", label: "Price", type: "number", card: true },
      { key: "is_vegetarian", label: "Vegetarian", type: "bool", badge: true },
      { key: "is_vegan", label: "Vegan", type: "bool", badge: true },
      { key: "is_gluten_free", label: "Gluten Free", type: "bool", badge: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "items", label: "Items", type: "textarea", full: true, card: true },
      { key: "description", label: "Description", type: "textarea", full: true },
    ],
    searchKeys: ["name", "meal_type", "items", "description"],
  },
  plans: {
    key: "plans",
    label: "Meal Plan",
    icon: CalendarDaysIcon,
    endpoint: "plans",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "meals_included", label: "Meals Included", type: "number", card: true },
      { key: "price_per_period", label: "Price/Period", type: "number", card: true },
      { key: "period_days", label: "Period (days)", type: "number", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["name", "description"],
  },
  bookings: {
    key: "bookings",
    label: "Meal Booking",
    icon: TicketIcon,
    endpoint: "bookings",
    titleField: "user_name",
    subtitleField: "menu_name",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      { key: "menu_name", label: "Menu", subtitle: true, skipForm: true },
      { key: "menu", label: "Menu ID", card: true },
      { key: "meal_plan_name", label: "Plan", card: true, skipForm: true },
      { key: "meal_plan", label: "Plan ID", card: true },
      { key: "booking_date", label: "Booking Date", type: "date", card: true },
      { key: "meal_type", label: "Meal Type", type: "select", options: MEAL_TYPES, badge: true },
      { key: "status", label: "Status", type: "select", options: BOOKING_STATUS, badge: true },
      { key: "cancelled_at", label: "Cancelled", type: "datetime", card: true, skipForm: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["user_name", "menu_name", "meal_plan_name", "status"],
  },
  dietary: {
    key: "dietary",
    label: "Dietary Restriction",
    icon: NoSymbolIcon,
    endpoint: "dietary",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      { key: "restriction_type", label: "Type", card: true },
      { key: "severity", label: "Severity", type: "select", options: SEVERITIES, badge: true },
      { key: "notes", label: "Notes", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["user_name", "restriction_type", "severity"],
  },
  pos: {
    key: "pos",
    label: "Point of Sale",
    icon: CreditCardIcon,
    endpoint: "pos",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      {
        key: "transaction_type",
        label: "Type",
        type: "select",
        options: [
          ["meal", "Meal"],
          ["snack", "Snack"],
          ["drink", "Drink"],
          ["other", "Other"],
        ] as [string, string][],
        badge: true,
      },
      { key: "transaction_type_display", label: "Type", skipForm: true, card: true },
      { key: "amount", label: "Amount", type: "number", card: true },
      {
        key: "payment_method",
        label: "Method",
        type: "select",
        options: PAYMENT_METHODS,
        badge: true,
      },
      { key: "payment_method_display", label: "Method", skipForm: true, card: true },
      { key: "menu_name", label: "Menu", card: true, skipForm: true },
      { key: "menu", label: "Menu ID", card: true },
      {
        key: "balance_before",
        label: "Balance Before",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "balance_after", label: "Balance After", type: "number", card: true, skipForm: true },
      { key: "is_successful", label: "Successful", type: "bool", badge: true },
      { key: "meal_benefit_applied", label: "Meal Benefit", type: "bool", card: true },
      { key: "benefit_type", label: "Benefit Type", card: true },
    ],
    searchKeys: ["user_name", "transaction_type", "payment_method", "menu_name"],
  },
  payments: {
    key: "payments",
    label: "Payment",
    icon: BanknotesIcon,
    endpoint: "payments",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      {
        key: "transaction_type",
        label: "Type",
        type: "select",
        options: [
          ["deposit", "Deposit"],
          ["meal_purchase", "Meal Purchase"],
          ["plan_purchase", "Plan Purchase"],
          ["refund", "Refund"],
          ["other", "Other"],
        ] as [string, string][],
        badge: true,
      },
      { key: "transaction_type_display", label: "Type", skipForm: true, card: true },
      { key: "amount", label: "Amount", type: "number", card: true },
      {
        key: "payment_method",
        label: "Method",
        type: "select",
        options: PAYMENT_TXN_METHODS,
        badge: true,
      },
      { key: "payment_method_display", label: "Method", skipForm: true, card: true },
      { key: "status", label: "Status", type: "select", options: PAYMENT_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "transaction_id", label: "Transaction ID", card: true },
      { key: "receipt_number", label: "Receipt #", card: true },
      { key: "meal_plan_name", label: "Plan", card: true, skipForm: true },
      { key: "meal_plan", label: "Plan ID", card: true },
      {
        key: "account_balance_before",
        label: "Balance Before",
        type: "number",
        card: true,
        skipForm: true,
      },
      {
        key: "account_balance_after",
        label: "Balance After",
        type: "number",
        card: true,
        skipForm: true,
      },
    ],
    searchKeys: ["user_name", "transaction_type", "status", "receipt_number"],
  },
  accounts: {
    key: "accounts",
    label: "Student Account",
    icon: WalletIcon,
    endpoint: "accounts",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      { key: "balance", label: "Balance", type: "number", card: true },
      { key: "status", label: "Status", type: "select", options: ACCOUNT_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "low_balance_threshold", label: "Low Balance Threshold", type: "number", card: true },
      { key: "auto_replenish_enabled", label: "Auto Replenish", type: "bool", card: true },
      { key: "replenish_threshold", label: "Replenish Threshold", type: "number", card: true },
      { key: "replenish_amount", label: "Replenish Amount", type: "number", card: true },
      { key: "daily_spending_limit", label: "Daily Limit", type: "number", card: true },
      { key: "total_spent", label: "Total Spent", type: "number", card: true, skipForm: true },
      {
        key: "total_deposited",
        label: "Total Deposited",
        type: "number",
        card: true,
        skipForm: true,
      },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["user_name", "status"],
  },
  "free-reduced": {
    key: "free-reduced",
    label: "Free/Reduced Lunch",
    icon: GiftIcon,
    endpoint: "free-reduced",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", card: true },
      {
        key: "eligibility_type",
        label: "Eligibility",
        type: "select",
        options: ELIGIBILITY,
        badge: true,
      },
      { key: "eligibility_type_display", label: "Eligibility", skipForm: true, card: true },
      { key: "status", label: "Status", type: "select", options: ELIGIBILITY_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "application_date", label: "Applied", type: "date", card: true },
      { key: "approval_date", label: "Approved", type: "date", card: true },
      { key: "expiry_date", label: "Expires", type: "date", card: true },
      { key: "application_number", label: "Application #", card: true },
      { key: "household_size", label: "Household Size", type: "number", card: true },
      { key: "household_income", label: "Household Income", type: "number", card: true },
      { key: "reviewed_by", label: "Reviewed By", card: true },
      { key: "document_url", label: "Document", card: true },
    ],
    searchKeys: ["student_name", "eligibility_type", "status", "application_number"],
  },
  inventory: {
    key: "inventory",
    label: "Inventory Item",
    icon: CubeIcon,
    endpoint: "inventory",
    titleField: "name",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "category",
        label: "Category",
        type: "select",
        options: INVENTORY_CATEGORIES,
        badge: true,
      },
      { key: "quantity", label: "Quantity", type: "number", card: true },
      { key: "unit", label: "Unit", type: "select", options: UNITS, card: true },
      { key: "minimum_stock", label: "Min Stock", type: "number", card: true },
      { key: "unit_cost", label: "Unit Cost", type: "number", card: true },
      { key: "total_value", label: "Total Value", type: "number", card: true, skipForm: true },
      { key: "supplier", label: "Supplier", card: true },
      { key: "storage_location", label: "Storage", card: true },
      { key: "temperature_requirement", label: "Temp Req", card: true },
      { key: "description", label: "Description", type: "textarea", full: true },
    ],
    searchKeys: ["name", "category", "supplier", "storage_location"],
  },
  vendors: {
    key: "vendors",
    label: "Vendor",
    icon: TruckIcon,
    endpoint: "vendors",
    titleField: "name",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "status", label: "Status", type: "select", options: VENDOR_STATUS, badge: true },
      { key: "contact_name", label: "Contact", card: true },
      { key: "email", label: "Email", card: true },
      { key: "phone", label: "Phone", card: true },
      { key: "address", label: "Address", card: true },
      { key: "minimum_order", label: "Min Order", type: "number", card: true },
      { key: "rating", label: "Rating", type: "number", card: true },
      { key: "total_orders", label: "Orders", type: "number", card: true, skipForm: true },
      { key: "products_offered", label: "Products", type: "textarea", full: true, card: true },
      { key: "payment_terms", label: "Payment Terms", type: "textarea", full: true },
      { key: "delivery_schedule", label: "Delivery Schedule", type: "textarea", full: true },
    ],
    searchKeys: ["name", "contact_name", "email", "status"],
  },
  "vendor-orders": {
    key: "vendor-orders",
    label: "Vendor Order",
    icon: ShoppingBagIcon,
    endpoint: "vendor-orders",
    titleField: "order_number",
    subtitleField: "vendor_name",
    fields: [
      { key: "order_number", label: "Order #", main: true },
      { key: "vendor_name", label: "Vendor", subtitle: true, skipForm: true },
      { key: "vendor", label: "Vendor ID", card: true },
      { key: "total_amount", label: "Total", type: "number", card: true },
      { key: "status", label: "Status", type: "select", options: VENDOR_ORDER_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      {
        key: "payment_status",
        label: "Payment",
        type: "select",
        options: PAYMENT_STATUS,
        badge: true,
      },
      { key: "payment_status_display", label: "Payment", skipForm: true, card: true },
      { key: "order_date", label: "Ordered", type: "date", card: true },
      { key: "expected_delivery", label: "Expected", type: "date", card: true },
      { key: "actual_delivery", label: "Delivered", type: "date", card: true },
      { key: "created_by", label: "Created By", card: true },
      { key: "items", label: "Items", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["order_number", "vendor_name", "status"],
  },
  allergens: {
    key: "allergens",
    label: "Allergen",
    icon: ExclamationTriangleIcon,
    endpoint: "allergens",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "severity", label: "Severity", type: "select", options: SEVERITIES, badge: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "symptoms", label: "Symptoms", type: "textarea", full: true, card: true },
      { key: "treatment_notes", label: "Treatment", type: "textarea", full: true, card: true },
      { key: "description", label: "Description", type: "textarea", full: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["name", "severity", "symptoms"],
  },
  "menu-allergens": {
    key: "menu-allergens",
    label: "Menu Allergen",
    icon: ExclamationTriangleIcon,
    endpoint: "menu-allergens",
    titleField: "menu_name",
    subtitleField: "allergen_name",
    fields: [
      { key: "menu_name", label: "Menu", main: true, skipForm: true },
      { key: "menu", label: "Menu ID", card: true },
      { key: "allergen_name", label: "Allergen", subtitle: true, skipForm: true },
      { key: "allergen", label: "Allergen ID", card: true },
      { key: "contains", label: "Contains", type: "bool", badge: true },
      { key: "may_contain", label: "May Contain", type: "bool", badge: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["menu_name", "allergen_name"],
  },
  nutrition: {
    key: "nutrition",
    label: "Nutrition Tracking",
    icon: ScaleIcon,
    endpoint: "nutrition",
    titleField: "user_name",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "calories", label: "Calories", type: "number", card: true },
      { key: "protein", label: "Protein", type: "number", card: true },
      { key: "carbohydrates", label: "Carbs", type: "number", card: true },
      { key: "fat", label: "Fat", type: "number", card: true },
      { key: "fiber", label: "Fiber", type: "number", card: true },
      { key: "vitamins", label: "Vitamins", card: true },
      { key: "minerals", label: "Minerals", card: true },
      { key: "meals", label: "Meals", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["user_name", "meals"],
  },
  "pre-orders": {
    key: "pre-orders",
    label: "Pre-Order",
    icon: QueueListIcon,
    endpoint: "pre-orders",
    titleField: "user_name",
    subtitleField: "menu_name",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      { key: "menu_name", label: "Menu", subtitle: true, skipForm: true },
      { key: "menu", label: "Menu ID", card: true },
      { key: "quantity", label: "Quantity", type: "number", card: true },
      { key: "unit_price", label: "Unit Price", type: "number", card: true },
      { key: "total_price", label: "Total", type: "number", card: true, skipForm: true },
      { key: "status", label: "Status", type: "select", options: PREORDER_STATUS, badge: true },
      {
        key: "payment_status",
        label: "Payment",
        type: "select",
        options: PAYMENT_STATUS,
        badge: true,
      },
      { key: "transaction", label: "Transaction", card: true },
      { key: "special_requests", label: "Special Requests", type: "textarea", full: true },
    ],
    searchKeys: ["user_name", "menu_name", "status"],
  },
  production: {
    key: "production",
    label: "Production Plan",
    icon: Cog6ToothIcon,
    endpoint: "production",
    titleField: "menu_name",
    fields: [
      { key: "menu_name", label: "Menu", main: true, skipForm: true },
      { key: "menu", label: "Menu ID", card: true },
      { key: "status", label: "Status", type: "select", options: PRODUCTION_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "planned_quantity", label: "Planned", type: "number", card: true },
      { key: "actual_quantity", label: "Actual", type: "number", card: true },
      { key: "pre_order_count", label: "Pre-Orders", type: "number", card: true, skipForm: true },
      { key: "expected_walk_in", label: "Expected Walk-in", type: "number", card: true },
      { key: "assigned_to", label: "Assigned To", card: true },
      { key: "prep_start_time", label: "Prep Start", card: true },
      { key: "prep_end_time", label: "Prep End", card: true },
      { key: "serve_time", label: "Serve Time", card: true },
    ],
    searchKeys: ["menu_name", "status", "assigned_to"],
  },
  "usda-reports": {
    key: "usda-reports",
    label: "USDA Report",
    icon: DocumentChartBarIcon,
    endpoint: "usda-reports",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "report_type", label: "Type", type: "select", options: REPORT_TYPES, badge: true },
      { key: "report_type_display", label: "Type", skipForm: true, card: true },
      { key: "status", label: "Status", type: "select", options: REPORT_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "total_meals_served", label: "Meals Served", type: "number", card: true },
      { key: "free_meals", label: "Free", type: "number", card: true },
      { key: "reduced_meals", label: "Reduced", type: "number", card: true },
      { key: "paid_meals", label: "Paid", type: "number", card: true },
      { key: "total_reimbursement", label: "Reimbursement", type: "number", card: true },
      { key: "per_meal_rate", label: "Per-Meal Rate", type: "number", card: true },
      { key: "submitted_by", label: "Submitted By", card: true },
    ],
    searchKeys: ["title", "report_type", "status"],
  },
  waste: {
    key: "waste",
    label: "Waste Record",
    icon: TrashIcon,
    endpoint: "waste",
    titleField: "item_name",
    subtitleField: "menu_name",
    fields: [
      { key: "item_name", label: "Item", main: true },
      { key: "menu_name", label: "Menu", subtitle: true, skipForm: true },
      { key: "menu", label: "Menu ID", card: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "waste_type", label: "Type", type: "select", options: WASTE_TYPES, badge: true },
      { key: "waste_type_display", label: "Type", skipForm: true, card: true },
      { key: "quantity_wasted", label: "Quantity", type: "number", card: true },
      { key: "unit", label: "Unit", type: "select", options: UNITS, card: true },
      { key: "estimated_cost", label: "Cost", type: "number", card: true },
      { key: "recorded_by_name", label: "Recorded By", card: true, skipForm: true },
      { key: "recorded_by", label: "Recorded By ID", card: true },
      { key: "reason", label: "Reason", type: "textarea", full: true, card: true },
      { key: "prevention_notes", label: "Prevention", type: "textarea", full: true },
    ],
    searchKeys: ["item_name", "menu_name", "waste_type", "reason"],
  },
  "online-order": {
    key: "online-order",
    label: "Online Order",
    icon: ShoppingBagIcon,
    endpoint: "online-order",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", card: true },
      { key: "status", label: "Status", type: "select", options: ONLINE_ORDER_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "total_amount", label: "Total", type: "number", card: true },
      {
        key: "payment_method",
        label: "Method",
        type: "select",
        options: PAYMENT_METHODS,
        badge: true,
      },
      { key: "payment_method_display", label: "Method", skipForm: true, card: true },
      { key: "paid", label: "Paid", type: "bool", badge: true },
      { key: "delivery_required", label: "Delivery", type: "bool", card: true },
      { key: "pickup_time", label: "Pickup", type: "datetime", card: true },
      { key: "delivery_location", label: "Delivery Location", card: true },
      { key: "ordered_at", label: "Ordered", type: "datetime", card: true, skipForm: true },
      { key: "items", label: "Items", type: "textarea", full: true, card: true },
      { key: "special_instructions", label: "Instructions", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "status", "delivery_location"],
  },
  "online-order-item": {
    key: "online-order-item",
    label: "Order Item",
    icon: ShoppingBagIcon,
    endpoint: "online-order-item",
    titleField: "item_name",
    subtitleField: "menu_item_name",
    fields: [
      { key: "item_name", label: "Item", main: true },
      { key: "menu_item_name", label: "Menu Item", subtitle: true, skipForm: true },
      { key: "menu_item", label: "Menu Item ID", card: true },
      { key: "order", label: "Order ID", card: true },
      { key: "order_status", label: "Order Status", card: true, skipForm: true },
      { key: "quantity", label: "Quantity", type: "number", card: true },
      { key: "unit_price", label: "Unit Price", type: "number", card: true },
      { key: "total_price", label: "Total", type: "number", card: true, skipForm: true },
      { key: "special_requests", label: "Requests", type: "textarea", full: true },
    ],
    searchKeys: ["item_name", "menu_item_name", "order_status"],
  },
  "meal-delivery": {
    key: "meal-delivery",
    label: "Meal Delivery",
    icon: TruckIcon,
    endpoint: "meal-delivery",
    titleField: "delivery_location",
    fields: [
      { key: "delivery_location", label: "Location", main: true },
      { key: "status", label: "Status", type: "select", options: DELIVERY_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "delivery_date", label: "Date", type: "date", card: true },
      { key: "delivery_time", label: "Time", card: true },
      { key: "class_group_name", label: "Class Group", card: true, skipForm: true },
      { key: "class_group", label: "Class Group ID", card: true },
      { key: "meals_ordered", label: "Ordered", type: "number", card: true },
      { key: "meals_delivered", label: "Delivered", type: "number", card: true },
      { key: "meals_returned", label: "Returned", type: "number", card: true },
      { key: "delivered_by_name", label: "Delivered By", card: true, skipForm: true },
      { key: "delivered_by", label: "Delivered By ID", card: true },
      { key: "completed_at", label: "Completed", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["delivery_location", "status", "class_group_name"],
  },
  "cash-register": {
    key: "cash-register",
    label: "Cash Register",
    icon: BanknotesIcon,
    endpoint: "cash-register",
    titleField: "register_name",
    fields: [
      { key: "register_name", label: "Name", main: true },
      { key: "location", label: "Location", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "is_open", label: "Open", type: "bool", badge: true },
      { key: "opening_amount", label: "Opening", type: "number", card: true },
      { key: "closing_amount", label: "Closing", type: "number", card: true },
      { key: "expected_amount", label: "Expected", type: "number", card: true, skipForm: true },
      { key: "variance", label: "Variance", type: "number", card: true, skipForm: true },
      { key: "opened_by_name", label: "Opened By", card: true, skipForm: true },
      { key: "opened_by", label: "Opened By ID", card: true },
      { key: "opened_at", label: "Opened At", type: "datetime", card: true, skipForm: true },
      { key: "closed_by_name", label: "Closed By", card: true, skipForm: true },
      { key: "closed_by", label: "Closed By ID", card: true },
    ],
    searchKeys: ["register_name", "location"],
  },
  "daily-sales-summary": {
    key: "daily-sales-summary",
    label: "Daily Sales",
    icon: ChartBarIcon,
    endpoint: "daily-sales-summary",
    titleField: "date",
    fields: [
      { key: "date", label: "Date", type: "date", main: true },
      { key: "total_sales", label: "Total Sales", type: "number", card: true },
      { key: "total_transactions", label: "Transactions", type: "number", card: true },
      { key: "total_items_sold", label: "Items Sold", type: "number", card: true },
      { key: "avg_transaction_value", label: "Avg Value", type: "number", card: true },
      { key: "cash_sales", label: "Cash", type: "number", card: true },
      { key: "card_sales", label: "Card", type: "number", card: true },
      { key: "account_sales", label: "Account", type: "number", card: true },
      { key: "free_meal_sales", label: "Free Meals", type: "number", card: true },
      { key: "breakfast_sales", label: "Breakfast", type: "number", card: true },
      { key: "lunch_sales", label: "Lunch", type: "number", card: true },
      { key: "snack_sales", label: "Snack", type: "number", card: true },
    ],
    searchKeys: ["date"],
  },
  "food-safety-check": {
    key: "food-safety-check",
    label: "Safety Check",
    icon: ShieldCheckIcon,
    endpoint: "food-safety-check",
    titleField: "check_type",
    subtitleField: "location",
    fields: [
      {
        key: "check_type",
        label: "Type",
        type: "select",
        options: CHECK_TYPES,
        main: true,
        badge: true,
      },
      { key: "check_type_display", label: "Type", skipForm: true, card: true },
      { key: "location", label: "Location", subtitle: true, card: true },
      { key: "check_date", label: "Date", type: "date", card: true },
      { key: "status", label: "Status", type: "select", options: CHECK_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "temperature_reading", label: "Temp", type: "number", card: true },
      { key: "checked_by_name", label: "Checked By", card: true, skipForm: true },
      { key: "checked_by", label: "Checked By ID", card: true },
      { key: "findings", label: "Findings", type: "textarea", full: true, card: true },
      { key: "corrective_actions", label: "Corrective Actions", type: "textarea", full: true },
      { key: "compliance_notes", label: "Compliance", type: "textarea", full: true },
      { key: "photo", label: "Photo", card: true },
    ],
    searchKeys: ["check_type", "location", "status"],
  },
  "food-safety-incident": {
    key: "food-safety-incident",
    label: "Safety Incident",
    icon: ExclamationTriangleIcon,
    endpoint: "food-safety-incident",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: INCIDENT_SEVERITY,
        badge: true,
      },
      { key: "severity_display", label: "Severity", skipForm: true, card: true },
      { key: "status", label: "Status", type: "select", options: INCIDENT_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "people_affected", label: "Affected", type: "number", card: true },
      { key: "reported_by_name", label: "Reported By", card: true, skipForm: true },
      { key: "reported_by", label: "Reported By ID", card: true },
      { key: "resolved_at", label: "Resolved", type: "datetime", card: true, skipForm: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "root_cause", label: "Root Cause", type: "textarea", full: true },
      { key: "investigation_notes", label: "Investigation", type: "textarea", full: true },
      { key: "corrective_actions", label: "Corrective Actions", type: "textarea", full: true },
      { key: "preventive_measures", label: "Prevention", type: "textarea", full: true },
    ],
    searchKeys: ["title", "severity", "status"],
  },
  "cafeteria-staff": {
    key: "cafeteria-staff",
    label: "Staff Member",
    icon: UserGroupIcon,
    endpoint: "cafeteria-staff",
    titleField: "user_name",
    toggleField: "is_active",
    fields: [
      { key: "user_name", label: "User", main: true, skipForm: true },
      { key: "user", label: "User ID", card: true },
      { key: "role", label: "Role", type: "select", options: STAFF_ROLES, badge: true },
      { key: "role_display", label: "Role", skipForm: true, card: true },
      { key: "shift_start", label: "Shift Start", card: true },
      { key: "shift_end", label: "Shift End", card: true },
      { key: "days_of_week", label: "Days", card: true },
      { key: "is_active", label: "Active", type: "bool", badge: true },
      { key: "is_certified", label: "Certified", type: "bool", card: true },
      { key: "certification_expiry", label: "Cert Expiry", type: "date", card: true },
      { key: "performance_rating", label: "Rating", type: "number", card: true },
    ],
    searchKeys: ["user_name", "role"],
  },
  "cafeteria-feedback": {
    key: "cafeteria-feedback",
    label: "Feedback",
    icon: StarIcon,
    endpoint: "cafeteria-feedback",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", card: true },
      { key: "feedback_type", label: "Type", type: "select", options: FEEDBACK_TYPES, badge: true },
      { key: "feedback_type_display", label: "Type", skipForm: true, card: true },
      { key: "rating", label: "Rating", type: "number", card: true },
      { key: "date_of_experience", label: "Date", type: "date", card: true },
      { key: "staff_member_name", label: "Staff", card: true, skipForm: true },
      { key: "staff_member", label: "Staff ID", card: true },
      { key: "meal_rated", label: "Meal", card: true },
      { key: "responded_by_name", label: "Responded By", card: true, skipForm: true },
      { key: "responded_by", label: "Responded By ID", card: true },
      { key: "comment", label: "Comment", type: "textarea", full: true, card: true },
      { key: "response", label: "Response", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "feedback_type", "comment"],
  },
  "meal-pre-order": {
    key: "meal-pre-order",
    label: "Meal Pre-Order",
    icon: QueueListIcon,
    endpoint: "meal-pre-order",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", card: true },
      { key: "meal_date", label: "Date", type: "date", card: true },
      { key: "meal_type", label: "Meal", type: "select", options: MEAL_TYPES, badge: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: PREORDER_MEAL_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "total_amount", label: "Total", type: "number", card: true },
      { key: "paid", label: "Paid", type: "bool", badge: true },
      { key: "paid_via", label: "Paid Via", card: true },
      { key: "pickup_time", label: "Pickup", type: "datetime", card: true },
      { key: "pickup_location", label: "Pickup Location", card: true },
      { key: "collected_at", label: "Collected", type: "datetime", card: true, skipForm: true },
      { key: "menu_items", label: "Menu Items", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["student_name", "meal_type", "status"],
  },
  "nutrition-analysis": {
    key: "nutrition-analysis",
    label: "Nutrition Analysis",
    icon: ScaleIcon,
    endpoint: "nutrition-analysis",
    titleField: "menu_item_name",
    fields: [
      { key: "menu_item_name", label: "Menu Item", main: true, skipForm: true },
      { key: "menu_item", label: "Menu Item ID", card: true },
      { key: "calories", label: "Calories", type: "number", card: true },
      { key: "health_score", label: "Health Score", type: "number", card: true, badge: true },
      { key: "is_healthy_choice", label: "Healthy Choice", type: "bool", badge: true },
      { key: "protein_g", label: "Protein (g)", type: "number", card: true },
      { key: "carbohydrates_g", label: "Carbs (g)", type: "number", card: true },
      { key: "fat_g", label: "Fat (g)", type: "number", card: true },
      { key: "fiber_g", label: "Fiber (g)", type: "number", card: true },
      { key: "sugar_g", label: "Sugar (g)", type: "number", card: true },
      { key: "sodium_mg", label: "Sodium (mg)", type: "number", card: true },
      { key: "vitamin_a", label: "Vitamin A", type: "number", card: true },
      { key: "vitamin_c", label: "Vitamin C", type: "number", card: true },
      { key: "calcium", label: "Calcium", type: "number", card: true },
      { key: "iron", label: "Iron", type: "number", card: true },
      { key: "analyzed_by_name", label: "Analyzed By", card: true, skipForm: true },
    ],
    searchKeys: ["menu_item_name", "health_score"],
  },
  "cafeteria-equipment": {
    key: "cafeteria-equipment",
    label: "Equipment",
    icon: Cog6ToothIcon,
    endpoint: "cafeteria-equipment",
    titleField: "name",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "equipment_type",
        label: "Type",
        type: "select",
        options: EQUIPMENT_TYPES,
        badge: true,
      },
      { key: "equipment_type_display", label: "Type", skipForm: true, card: true },
      { key: "status", label: "Status", type: "select", options: EQUIPMENT_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "asset_tag", label: "Asset Tag", card: true },
      { key: "brand", label: "Brand", card: true },
      { key: "model_number", label: "Model", card: true },
      { key: "purchase_date", label: "Purchased", type: "date", card: true },
      { key: "purchase_cost", label: "Cost", type: "number", card: true },
      { key: "warranty_expiry", label: "Warranty", type: "date", card: true },
      { key: "last_maintenance", label: "Last Maintenance", type: "date", card: true },
      { key: "next_maintenance", label: "Next Maintenance", type: "date", card: true },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["name", "equipment_type", "status", "asset_tag"],
  },
  "cafeteria-reservation": {
    key: "cafeteria-reservation",
    label: "Reservation",
    icon: CalendarDaysIcon,
    endpoint: "cafeteria-reservation",
    titleField: "title",
    subtitleField: "requested_by_name",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "requested_by_name", label: "Requested By", subtitle: true, skipForm: true },
      { key: "requested_by", label: "Requested By ID", card: true },
      {
        key: "reservation_type",
        label: "Type",
        type: "select",
        options: RESERVATION_TYPES,
        badge: true,
      },
      { key: "reservation_type_display", label: "Type", skipForm: true, card: true },
      { key: "status", label: "Status", type: "select", options: RESERVATION_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "reservation_date", label: "Date", type: "date", card: true },
      { key: "start_time", label: "Start", card: true },
      { key: "end_time", label: "End", card: true },
      { key: "expected_guests", label: "Guests", type: "number", card: true },
      { key: "approved_by_name", label: "Approved By", card: true, skipForm: true },
      { key: "approved_by", label: "Approved By ID", card: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["title", "requested_by_name", "reservation_type", "status"],
  },
  "cafeteria-alert": {
    key: "cafeteria-alert",
    label: "Alert",
    icon: BellAlertIcon,
    endpoint: "cafeteria-alert",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "alert_type", label: "Type", type: "select", options: ALERT_TYPES, badge: true },
      { key: "alert_type_display", label: "Type", skipForm: true, card: true },
      { key: "severity", label: "Severity", type: "select", options: ALERT_SEVERITY, badge: true },
      { key: "severity_display", label: "Severity", skipForm: true, card: true },
      { key: "status", label: "Status", type: "select", options: ALERT_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "acknowledged_by_name", label: "Acknowledged By", card: true, skipForm: true },
      { key: "acknowledged_by", label: "Acknowledged By ID", card: true },
      { key: "resolved_by_name", label: "Resolved By", card: true, skipForm: true },
      { key: "resolved_by", label: "Resolved By ID", card: true },
      { key: "resolved_at", label: "Resolved", type: "datetime", card: true, skipForm: true },
      { key: "description", label: "Description", type: "textarea", full: true, card: true },
      { key: "resolution_notes", label: "Resolution Notes", type: "textarea", full: true },
    ],
    searchKeys: ["title", "alert_type", "severity", "status"],
  },
  "meal-subscription": {
    key: "meal-subscription",
    label: "Meal Subscription",
    icon: SparklesIcon,
    endpoint: "meal-subscription",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", card: true },
      { key: "plan_type", label: "Plan", type: "select", options: SUBSCRIPTION_PLANS, badge: true },
      { key: "plan_type_display", label: "Plan", skipForm: true, card: true },
      { key: "status", label: "Status", type: "select", options: SUBSCRIPTION_STATUS, badge: true },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "meals_included", label: "Meals Included", type: "number", card: true },
      { key: "meals_per_week", label: "Meals/Week", type: "number", card: true },
      { key: "price_per_meal", label: "Price/Meal", type: "number", card: true },
      { key: "total_price", label: "Total", type: "number", card: true },
      { key: "discount_percentage", label: "Discount %", type: "number", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "next_billing_date", label: "Next Billing", type: "date", card: true },
    ],
    searchKeys: ["student_name", "plan_type", "status"],
  },
  "subscription-usage": {
    key: "subscription-usage",
    label: "Subscription Usage",
    icon: SparklesIcon,
    endpoint: "subscription-usage",
    titleField: "subscription_label",
    fields: [
      { key: "subscription_label", label: "Subscription", main: true, skipForm: true },
      { key: "subscription", label: "Subscription ID", card: true },
      { key: "meal_date", label: "Date", type: "date", card: true },
      { key: "meal_type", label: "Meal", type: "select", options: MEAL_TYPES, badge: true },
      { key: "meal_type_display", label: "Meal", skipForm: true, card: true },
      { key: "menu_item_name", label: "Menu Item", card: true, skipForm: true },
      { key: "menu_item", label: "Menu Item ID", card: true },
      { key: "used", label: "Used", type: "bool", badge: true },
      { key: "skipped", label: "Skipped", type: "bool", badge: true },
      { key: "recorded_at", label: "Recorded", type: "datetime", card: true, skipForm: true },
    ],
    searchKeys: ["subscription_label", "meal_type"],
  },
  "cafeteria-analytics": {
    key: "cafeteria-analytics",
    label: "Analytics",
    icon: ChartBarIcon,
    endpoint: "cafeteria-analytics",
    titleField: "date",
    fields: [
      { key: "date", label: "Date", type: "date", main: true },
      { key: "total_visitors", label: "Visitors", type: "number", card: true },
      { key: "unique_visitors", label: "Unique", type: "number", card: true },
      { key: "total_meals_served", label: "Meals Served", type: "number", card: true },
      { key: "avg_wait_time_minutes", label: "Avg Wait", type: "number", card: true },
      { key: "peak_hour", label: "Peak Hour", card: true },
      { key: "total_waste_kg", label: "Waste (kg)", type: "number", card: true },
      { key: "waste_percentage", label: "Waste %", type: "number", card: true },
      { key: "total_revenue", label: "Revenue", type: "number", card: true },
      { key: "meals_by_type", label: "Meals by Type", type: "textarea", full: true, card: true },
      { key: "top_items", label: "Top Items", type: "textarea", full: true },
      { key: "least_popular", label: "Least Popular", type: "textarea", full: true },
    ],
    searchKeys: ["date", "peak_hour"],
  },
  "cafeteria-capacity": {
    key: "cafeteria-capacity",
    label: "Seating Capacity",
    icon: UsersIcon,
    endpoint: "cafeteria-capacity",
    titleField: "seating_area",
    fields: [
      { key: "seating_area", label: "Area", main: true },
      { key: "total_seats", label: "Total Seats", type: "number", card: true },
      { key: "available_seats", label: "Available", type: "number", card: true },
      { key: "meal_type", label: "Meal", type: "select", options: MEAL_TYPES, badge: true },
      { key: "meal_type_display", label: "Meal", skipForm: true, card: true },
      { key: "time_slot_start", label: "Slot Start", card: true },
      { key: "time_slot_end", label: "Slot End", card: true },
      { key: "is_full", label: "Full", type: "bool", badge: true },
      { key: "reservation_required", label: "Reservation Required", type: "bool", card: true },
    ],
    searchKeys: ["seating_area", "meal_type"],
  },
  "menu-item-rating": {
    key: "menu-item-rating",
    label: "Menu Rating",
    icon: StarIcon,
    endpoint: "menu-item-rating",
    titleField: "menu_item_name",
    fields: [
      { key: "menu_item_name", label: "Menu Item", main: true, skipForm: true },
      { key: "menu_item", label: "Menu Item ID", card: true },
      { key: "student_name", label: "Student", card: true, skipForm: true },
      { key: "student", label: "Student ID", card: true },
      { key: "rating", label: "Rating", type: "number", card: true, badge: true },
      { key: "would_order_again", label: "Would Order Again", type: "bool", badge: true },
      { key: "date_rated", label: "Rated", type: "date", card: true, skipForm: true },
      { key: "review", label: "Review", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["menu_item_name", "student_name", "rating"],
  },
  "cafeteria-holiday-schedule": {
    key: "cafeteria-holiday-schedule",
    label: "Holiday Schedule",
    icon: SunIcon,
    endpoint: "cafeteria-holiday-schedule",
    titleField: "date",
    fields: [
      { key: "date", label: "Date", type: "date", main: true },
      { key: "is_closed", label: "Closed", type: "bool", badge: true },
      { key: "special_hours", label: "Special Hours", type: "bool", card: true },
      { key: "opening_time", label: "Opens", card: true },
      { key: "closing_time", label: "Closes", card: true },
      { key: "reason", label: "Reason", card: true },
      { key: "special_menu", label: "Special Menu", card: true },
    ],
    searchKeys: ["date", "reason"],
  },
  "cafeteria-monthly-report": {
    key: "cafeteria-monthly-report",
    label: "Monthly Report",
    icon: DocumentChartBarIcon,
    endpoint: "cafeteria-monthly-report",
    titleField: "month",
    subtitleField: "year",
    fields: [
      { key: "month", label: "Month", main: true },
      { key: "year", label: "Year", subtitle: true, type: "number", card: true },
      { key: "total_revenue", label: "Revenue", type: "number", card: true },
      { key: "total_cost", label: "Cost", type: "number", card: true },
      { key: "net_profit", label: "Net Profit", type: "number", card: true, badge: true },
      { key: "total_meals_served", label: "Meals Served", type: "number", card: true },
      { key: "total_operational_days", label: "Days", type: "number", card: true },
      { key: "avg_daily_revenue", label: "Avg Daily Revenue", type: "number", card: true },
      { key: "avg_food_rating", label: "Food Rating", type: "number", card: true },
      { key: "avg_service_rating", label: "Service Rating", type: "number", card: true },
      { key: "total_complaints", label: "Complaints", type: "number", card: true },
      { key: "complaints_resolved", label: "Resolved", type: "number", card: true },
    ],
    searchKeys: ["month", "year"],
  },
  "cafeteria-inventory-alert": {
    key: "cafeteria-inventory-alert",
    label: "Inventory Alert",
    icon: BellAlertIcon,
    endpoint: "cafeteria-inventory-alert",
    titleField: "item_name",
    fields: [
      { key: "item_name", label: "Item", main: true, skipForm: true },
      { key: "item", label: "Item ID", card: true },
      {
        key: "alert_type",
        label: "Type",
        type: "select",
        options: INVENTORY_ALERT_TYPES,
        badge: true,
      },
      { key: "alert_type_display", label: "Type", skipForm: true, card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: INVENTORY_ALERT_STATUS,
        badge: true,
      },
      { key: "status_display", label: "Status", skipForm: true, card: true },
      { key: "current_quantity", label: "Current", type: "number", card: true },
      { key: "reorder_quantity", label: "Reorder At", type: "number", card: true },
      { key: "acknowledged_by", label: "Acknowledged By", card: true },
      { key: "resolved_at", label: "Resolved", type: "datetime", card: true, skipForm: true },
      { key: "message", label: "Message", type: "textarea", full: true, card: true },
    ],
    searchKeys: ["item_name", "alert_type", "status"],
  },
};

const TABS: { key: string; label: string; icon: React.ComponentType<{ className?: string }> }[] =
  Object.values(ENTITY_CONFIGS).map((c) => ({ key: c.key, label: c.label, icon: c.icon }));

// ─── Main page ───────────────────────────────────────────────────────────────

export default function CafeteriaPage() {
  useTitle("Cafeteria Center");
  const [activeTab, setActiveTab] = useState("menus");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Cafeteria Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Menus, meal plans, POS, accounts, inventory, vendors, nutrition, food safety and
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
        basePath="/cafeteria"
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
