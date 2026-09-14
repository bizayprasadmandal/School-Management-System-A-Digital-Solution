/**
 * Hostel Center — full-surface admin page for the hostel module.
 *
 * 39 entity tabs (config-driven via EntitySection). Hostels, rooms, allocations, mess, visitors, events, assets, emergencies, inspections and wellness.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, BuildingOffice2Icon } from "@heroicons/react/24/outline";

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  // ===== hostel =====
  allocations: {
    key: "allocations",
    icon: BuildingOffice2Icon,
    label: "Hostel Allocation",
    endpoint: "allocations",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "room", label: "Room" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["checked_out", "Checked Out"],
          ["transferred", "Transferred"],
        ],
      },
      { key: "check_in_date", label: "Check In Date", type: "date" },
      { key: "check_out_date", label: "Check Out Date", type: "date" },
      { key: "fee_amount", label: "Fee Amount" },
      { key: "is_paid", label: "Is Paid" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "allocated_by", label: "Allocated By" },
    ],
  },
  attendance: {
    key: "attendance",
    icon: BuildingOffice2Icon,
    label: "Hostel Attendance",
    endpoint: "attendance",
    titleField: "allocation",
    subtitleField: "status",
    fields: [
      { key: "allocation", label: "Allocation" },
      { key: "date", label: "Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["present", "Present"],
          ["absent", "Absent"],
          ["late", "Late"],
          ["on_leave", "On Leave"],
        ],
      },
      { key: "check_in_time", label: "Check In Time" },
      { key: "check_out_time", label: "Check Out Time" },
      { key: "is_in_campus", label: "Is In Campus" },
      { key: "recorded_by", label: "Recorded By" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  checkouts: {
    key: "checkouts",
    icon: BuildingOffice2Icon,
    label: "Checkout Process",
    endpoint: "checkouts",
    titleField: "allocation",
    subtitleField: "status",
    fields: [
      { key: "allocation", label: "Allocation" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["in_progress", "In Progress"],
          ["completed", "Completed"],
          ["on_hold", "On Hold"],
        ],
      },
      { key: "checkout_date", label: "Checkout Date", type: "date" },
      { key: "room_inspected", label: "Room Inspected" },
      { key: "inspection_notes", label: "Inspection Notes" },
      { key: "damage_detected", label: "Damage Detected" },
      { key: "damage_description", label: "Damage Description" },
      { key: "damage_charge", label: "Damage Charge" },
      { key: "items_returned", label: "Items Returned" },
      { key: "missing_items", label: "Missing Items" },
      { key: "pending_dues", label: "Pending Dues" },
      { key: "security_deposit_refund", label: "Security Deposit Refund" },
      { key: "final_amount", label: "Final Amount" },
    ],
  },
  "common-area-booking": {
    key: "common-area-booking",
    icon: BuildingOffice2Icon,
    label: "Common Area Booking",
    endpoint: "common-area-booking",
    titleField: "hostel",
    subtitleField: "status",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "student", label: "Student" },
      {
        key: "area_type",
        label: "Area Type",
        type: "select",
        options: [
          ["study", "Study"],
          ["gym", "Gym"],
          ["tv", "Tv"],
          ["game", "Game"],
          ["library", "Library"],
          ["terrace", "Terrace"],
          ["meeting", "Meeting"],
          ["other", "Other"],
        ],
      },
      { key: "area_name", label: "Area Name" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["booked", "Booked"],
          ["active", "Active"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
          ["no_show", "No Show"],
        ],
      },
      { key: "booking_date", label: "Booking Date", type: "date" },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      { key: "group_size", label: "Group Size" },
      { key: "additional_members", label: "Additional Members" },
      { key: "purpose", label: "Purpose" },
      { key: "rules_acknowledged", label: "Rules Acknowledged" },
    ],
  },
  complaints: {
    key: "complaints",
    icon: BuildingOffice2Icon,
    label: "Complaint Management",
    endpoint: "complaints",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "allocation", label: "Allocation" },
      {
        key: "complaint_type",
        label: "Complaint Type",
        type: "select",
        options: [
          ["maintenance", "Maintenance"],
          ["cleanliness", "Cleanliness"],
          ["noise", "Noise"],
          ["security", "Security"],
          ["food", "Food"],
          ["roommate", "Roommate"],
          ["facility", "Facility"],
          ["other", "Other"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["under_review", "Under Review"],
          ["in_progress", "In Progress"],
          ["resolved", "Resolved"],
          ["closed", "Closed"],
          ["rejected", "Rejected"],
        ],
      },
      {
        key: "priority",
        label: "Priority",
        type: "select",
        options: [
          ["low", "Low"],
          ["medium", "Medium"],
          ["high", "High"],
          ["urgent", "Urgent"],
        ],
      },
      { key: "assigned_to", label: "Assigned To" },
      { key: "resolution_notes", label: "Resolution Notes" },
      { key: "resolved_at", label: "Resolved At", type: "date" },
      { key: "resolved_by", label: "Resolved By" },
    ],
  },
  "emergency-contacts": {
    key: "emergency-contacts",
    icon: BuildingOffice2Icon,
    label: "Emergency Contact",
    endpoint: "emergency-contacts",
    titleField: "name",
    fields: [
      { key: "hostel", label: "Hostel" },
      {
        key: "contact_type",
        label: "Contact Type",
        type: "select",
        options: [
          ["warden", "Warden"],
          ["assistant_warden", "Assistant Warden"],
          ["security", "Security"],
          ["medical", "Medical"],
          ["fire", "Fire"],
          ["police", "Police"],
          ["parent", "Parent"],
          ["school", "School"],
          ["other", "Other"],
        ],
      },
      { key: "name", label: "Name" },
      { key: "phone_primary", label: "Phone Primary" },
      { key: "phone_secondary", label: "Phone Secondary" },
      { key: "email", label: "Email" },
      { key: "is_available_24x7", label: "Is Available 24X7" },
      { key: "available_hours", label: "Available Hours" },
      { key: "location", label: "Location" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  feedback: {
    key: "feedback",
    icon: BuildingOffice2Icon,
    label: "Hostel Feedback",
    endpoint: "feedback",
    titleField: "title",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "allocation", label: "Allocation" },
      {
        key: "feedback_type",
        label: "Feedback Type",
        type: "select",
        options: [
          ["room", "Room"],
          ["cleanliness", "Cleanliness"],
          ["food", "Food"],
          ["security", "Security"],
          ["staff", "Staff"],
          ["facilities", "Facilities"],
          ["maintenance", "Maintenance"],
          ["general", "General"],
          ["suggestion", "Suggestion"],
          ["complaint", "Complaint"],
        ],
      },
      {
        key: "rating",
        label: "Rating",
        type: "select",
        options: [
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "comment", label: "Comment" },
      { key: "suggestion", label: "Suggestion" },
      { key: "is_anonymous", label: "Is Anonymous" },
      { key: "response", label: "Response" },
      { key: "responded_by", label: "Responded By" },
      { key: "responded_at", label: "Responded At", type: "date" },
    ],
  },
  fees: {
    key: "fees",
    icon: BuildingOffice2Icon,
    label: "Hostel Fee",
    endpoint: "fees",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "hostel", label: "Hostel" },
      {
        key: "room_type",
        label: "Room Type",
        type: "select",
        options: [
          ["single", "Single"],
          ["double", "Double"],
          ["triple", "Triple"],
          ["dormitory", "Dormitory"],
        ],
      },
      { key: "amount", label: "Amount", type: "number" },
      {
        key: "billing_cycle",
        label: "Billing Cycle",
        type: "select",
        options: [
          ["monthly", "Monthly"],
          ["quarterly", "Quarterly"],
          ["semi_annual", "Semi Annual"],
          ["annual", "Annual"],
        ],
      },
      { key: "includes_meals", label: "Includes Meals" },
      { key: "includes_laundry", label: "Includes Laundry" },
      { key: "includes_wifi", label: "Includes Wifi" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "hostel-asset": {
    key: "hostel-asset",
    icon: BuildingOffice2Icon,
    label: "Hostel Asset",
    endpoint: "hostel-asset",
    titleField: "room",
    fields: [
      { key: "room", label: "Room" },
      { key: "hostel", label: "Hostel" },
      { key: "asset_name", label: "Asset Name" },
      { key: "asset_tag", label: "Asset Tag" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "condition",
        label: "Condition",
        type: "select",
        options: [
          ["new", "New"],
          ["good", "Good"],
          ["fair", "Fair"],
          ["poor", "Poor"],
          ["damaged", "Damaged"],
          ["retired", "Retired"],
        ],
      },
      { key: "purchase_date", label: "Purchase Date", type: "date" },
      { key: "purchase_cost", label: "Purchase Cost" },
      { key: "warranty_expiry", label: "Warranty Expiry" },
      { key: "last_inspected", label: "Last Inspected" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "hostel-asset-transfer": {
    key: "hostel-asset-transfer",
    icon: BuildingOffice2Icon,
    label: "Hostel Asset Transfer",
    endpoint: "hostel-asset-transfer",
    titleField: "asset",
    fields: [
      { key: "asset", label: "Asset" },
      { key: "from_room", label: "From Room" },
      { key: "to_room", label: "To Room" },
      { key: "transferred_by", label: "Transferred By" },
      { key: "transfer_date", label: "Transfer Date", type: "date" },
      { key: "reason", label: "Reason" },
      {
        key: "condition_at_transfer",
        label: "Condition At Transfer",
        type: "select",
        options: [
          ["new", "New"],
          ["good", "Good"],
          ["fair", "Fair"],
          ["poor", "Poor"],
          ["damaged", "Damaged"],
          ["retired", "Retired"],
        ],
      },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "hostel-attendance-alert": {
    key: "hostel-attendance-alert",
    icon: BuildingOffice2Icon,
    label: "Hostel Attendance Alert",
    endpoint: "hostel-attendance-alert",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "hostel", label: "Hostel" },
      {
        key: "alert_type",
        label: "Alert Type",
        type: "select",
        options: [
          ["missing", "Missing"],
          ["no_show", "No Show"],
          ["late", "Late"],
          ["unauthorized", "Unauthorized"],
          ["leave_violation", "Leave Violation"],
        ],
      },
      {
        key: "severity",
        label: "Severity",
        type: "select",
        options: [
          ["low", "Low"],
          ["medium", "Medium"],
          ["high", "High"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["acknowledged", "Acknowledged"],
          ["resolved", "Resolved"],
          ["escalated", "Escalated"],
        ],
      },
      { key: "alert_date", label: "Alert Date", type: "date" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "related_attendance", label: "Related Attendance" },
      { key: "acknowledged_by", label: "Acknowledged By" },
    ],
  },
  "hostel-emergency-drill": {
    key: "hostel-emergency-drill",
    icon: BuildingOffice2Icon,
    label: "Hostel Emergency Drill",
    endpoint: "hostel-emergency-drill",
    titleField: "hostel",
    subtitleField: "status",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "protocol", label: "Protocol" },
      { key: "conducted_by", label: "Conducted By" },
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
      { key: "drill_date", label: "Drill Date", type: "date" },
      { key: "start_time", label: "Start Time" },
      { key: "end_time", label: "End Time" },
      { key: "participants_count", label: "Participants Count" },
      {
        key: "evaluation",
        label: "Evaluation",
        type: "select",
        options: [
          ["excellent", "Excellent"],
          ["good", "Good"],
          ["satisfactory", "Satisfactory"],
          ["needs_improvement", "Needs Improvement"],
          ["poor", "Poor"],
        ],
      },
      { key: "evacuation_time_minutes", label: "Evacuation Time Minutes" },
      { key: "issues_identified", label: "Issues Identified" },
    ],
  },
  "hostel-emergency-protocol": {
    key: "hostel-emergency-protocol",
    icon: BuildingOffice2Icon,
    label: "Hostel Emergency Protocol",
    endpoint: "hostel-emergency-protocol",
    titleField: "title",
    fields: [
      { key: "hostel", label: "Hostel" },
      {
        key: "emergency_type",
        label: "Emergency Type",
        type: "select",
        options: [
          ["fire", "Fire"],
          ["medical", "Medical"],
          ["natural", "Natural"],
          ["lockdown", "Lockdown"],
          ["evacuation", "Evacuation"],
          ["power", "Power"],
          ["other", "Other"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "procedures", label: "Procedures" },
      { key: "contacts", label: "Contacts" },
      { key: "assembly_point", label: "Assembly Point" },
      { key: "last_drill_date", label: "Last Drill Date", type: "date" },
      { key: "next_drill_date", label: "Next Drill Date", type: "date" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "document", label: "Document" },
    ],
  },
  "hostel-event": {
    key: "hostel-event",
    icon: BuildingOffice2Icon,
    label: "Hostel Event",
    endpoint: "hostel-event",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "organizer", label: "Organizer" },
      { key: "title", label: "Title" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "event_type",
        label: "Event Type",
        type: "select",
        options: [
          ["orientation", "Orientation"],
          ["social", "Social"],
          ["cleanliness", "Cleanliness"],
          ["safety", "Safety"],
          ["cultural", "Cultural"],
          ["sports", "Sports"],
          ["workshop", "Workshop"],
          ["celebration", "Celebration"],
          ["other", "Other"],
        ],
      },
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
      { key: "max_participants", label: "Max Participants" },
      { key: "current_participants", label: "Current Participants" },
    ],
  },
  "hostel-event-participant": {
    key: "hostel-event-participant",
    icon: BuildingOffice2Icon,
    label: "Hostel Event Participant",
    endpoint: "hostel-event-participant",
    titleField: "event",
    fields: [
      { key: "event", label: "Event" },
      { key: "student", label: "Student" },
      { key: "registered_at", label: "Registered At", type: "date" },
      { key: "attended", label: "Attended" },
      { key: "feedback_rating", label: "Feedback Rating" },
      { key: "feedback_comment", label: "Feedback Comment" },
    ],
  },
  "hostel-fee-payment": {
    key: "hostel-fee-payment",
    icon: BuildingOffice2Icon,
    label: "Hostel Fee Payment",
    endpoint: "hostel-fee-payment",
    titleField: "allocation",
    subtitleField: "status",
    fields: [
      { key: "allocation", label: "Allocation" },
      { key: "hostel_fee", label: "Hostel Fee" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["paid", "Paid"],
          ["partial", "Partial"],
          ["overdue", "Overdue"],
          ["waived", "Waived"],
        ],
      },
      { key: "amount_due", label: "Amount Due" },
      { key: "amount_paid", label: "Amount Paid" },
      { key: "late_fee", label: "Late Fee" },
      { key: "discount", label: "Discount" },
      {
        key: "payment_method",
        label: "Payment Method",
        type: "select",
        options: [
          ["cash", "Cash"],
          ["bank", "Bank"],
          ["online", "Online"],
          ["cheque", "Cheque"],
          ["scholarship", "Scholarship"],
        ],
      },
      { key: "transaction_id", label: "Transaction Id" },
      { key: "payment_date", label: "Payment Date", type: "date" },
    ],
  },
  "hostel-inspection-schedule": {
    key: "hostel-inspection-schedule",
    icon: BuildingOffice2Icon,
    label: "Hostel Inspection Schedule",
    endpoint: "hostel-inspection-schedule",
    titleField: "hostel",
    subtitleField: "frequency",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "inspector", label: "Inspector" },
      {
        key: "frequency",
        label: "Frequency",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["biweekly", "Biweekly"],
          ["monthly", "Monthly"],
          ["quarterly", "Quarterly"],
        ],
      },
      { key: "day_of_week", label: "Day Of Week" },
      { key: "time_of_day", label: "Time Of Day" },
      { key: "rooms_to_inspect", label: "Rooms To Inspect" },
      { key: "checklist_items", label: "Checklist Items" },
      { key: "is_active", label: "Is Active", type: "bool" },
      {
        key: "last_inspection_date",
        label: "Last Inspection Date",
        type: "date",
      },
      {
        key: "next_inspection_date",
        label: "Next Inspection Date",
        type: "date",
      },
    ],
  },
  hostels: {
    key: "hostels",
    icon: BuildingOffice2Icon,
    label: "Hostel",
    endpoint: "hostels",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      { key: "code", label: "Code" },
      {
        key: "gender",
        label: "Gender",
        type: "select",
        options: [
          ["male", "Male"],
          ["female", "Female"],
          ["coed", "Coed"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["inactive", "Inactive"],
          ["under_maintenance", "Under Maintenance"],
        ],
      },
      { key: "warden", label: "Warden" },
      { key: "assistant_warden", label: "Assistant Warden" },
      { key: "address", label: "Address" },
      { key: "phone", label: "Phone" },
      { key: "total_floors", label: "Total Floors" },
      { key: "rules", label: "Rules" },
    ],
  },
  inspections: {
    key: "inspections",
    icon: BuildingOffice2Icon,
    label: "Room Inspection",
    endpoint: "inspections",
    titleField: "room",
    subtitleField: "status",
    fields: [
      { key: "room", label: "Room" },
      {
        key: "inspection_type",
        label: "Inspection Type",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["monthly", "Monthly"],
          ["random", "Random"],
          ["checkout", "Checkout"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["in_progress", "In Progress"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "scheduled_date", label: "Scheduled Date", type: "date" },
      { key: "completed_date", label: "Completed Date", type: "date" },
      {
        key: "cleanliness_rating",
        label: "Cleanliness Rating",
        type: "select",
        options: [
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
        ],
      },
      {
        key: "orderliness_rating",
        label: "Orderliness Rating",
        type: "select",
        options: [
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
        ],
      },
      {
        key: "condition_rating",
        label: "Condition Rating",
        type: "select",
        options: [
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
        ],
      },
      { key: "inspected_by", label: "Inspected By" },
      { key: "issues_found", label: "Issues Found" },
      { key: "has_issues", label: "Has Issues" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  inventory: {
    key: "inventory",
    icon: BuildingOffice2Icon,
    label: "Inventory Management",
    endpoint: "inventory",
    titleField: "hostel",
    subtitleField: "status",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "room", label: "Room" },
      { key: "item_name", label: "Item Name" },
      {
        key: "item_category",
        label: "Item Category",
        type: "select",
        options: [
          ["furniture", "Furniture"],
          ["electronics", "Electronics"],
          ["bedding", "Bedding"],
          ["fixture", "Fixture"],
          ["appliance", "Appliance"],
          ["other", "Other"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "quantity", label: "Quantity" },
      { key: "unit_price", label: "Unit Price" },
      { key: "total_value", label: "Total Value" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["good", "Good"],
          ["fair", "Fair"],
          ["needs_repair", "Needs Repair"],
          ["damaged", "Damaged"],
          ["retired", "Retired"],
        ],
      },
      { key: "purchase_date", label: "Purchase Date", type: "date" },
      { key: "warranty_expiry", label: "Warranty Expiry" },
      { key: "supplier", label: "Supplier" },
    ],
  },
  "laundry-service": {
    key: "laundry-service",
    icon: BuildingOffice2Icon,
    label: "Laundry Service",
    endpoint: "laundry-service",
    titleField: "allocation",
    subtitleField: "status",
    fields: [
      { key: "allocation", label: "Allocation" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pickup", "Pickup"],
          ["picked_up", "Picked Up"],
          ["in_process", "In Process"],
          ["ready", "Ready"],
          ["delivered", "Delivered"],
          ["cancelled", "Cancelled"],
        ],
      },
      {
        key: "garment_type",
        label: "Garment Type",
        type: "select",
        options: [
          ["uniform", "Uniform"],
          ["bedding", "Bedding"],
          ["personal", "Personal"],
          ["other", "Other"],
        ],
      },
      { key: "quantity", label: "Quantity" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "pickup_date", label: "Pickup Date", type: "date" },
      { key: "pickup_time", label: "Pickup Time" },
      { key: "delivery_date", label: "Delivery Date", type: "date" },
      { key: "delivery_time", label: "Delivery Time" },
      { key: "total_cost", label: "Total Cost" },
      { key: "paid", label: "Paid" },
    ],
  },
  leaves: {
    key: "leaves",
    icon: BuildingOffice2Icon,
    label: "Leave Management",
    endpoint: "leaves",
    titleField: "allocation",
    subtitleField: "status",
    fields: [
      { key: "allocation", label: "Allocation" },
      {
        key: "leave_type",
        label: "Leave Type",
        type: "select",
        options: [
          ["sick", "Sick"],
          ["home", "Home"],
          ["personal", "Personal"],
          ["emergency", "Emergency"],
          ["academic", "Academic"],
          ["other", "Other"],
        ],
      },
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
      { key: "from_date", label: "From Date", type: "date" },
      { key: "to_date", label: "To Date", type: "date" },
      { key: "total_days", label: "Total Days" },
      { key: "approved_by", label: "Approved By" },
      { key: "approved_at", label: "Approved At", type: "date" },
      { key: "rejection_reason", label: "Rejection Reason" },
      { key: "parent_notified", label: "Parent Notified" },
      { key: "parent_consent", label: "Parent Consent" },
    ],
  },
  maintenance: {
    key: "maintenance",
    icon: BuildingOffice2Icon,
    label: "Room Maintenance",
    endpoint: "maintenance",
    titleField: "room",
    subtitleField: "status",
    fields: [
      { key: "room", label: "Room" },
      {
        key: "maintenance_type",
        label: "Maintenance Type",
        type: "select",
        options: [
          ["plumbing", "Plumbing"],
          ["electrical", "Electrical"],
          ["furniture", "Furniture"],
          ["cleaning", "Cleaning"],
          ["painting", "Painting"],
          ["general", "General"],
          ["emergency", "Emergency"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["in_progress", "In Progress"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
          ["on_hold", "On Hold"],
        ],
      },
      {
        key: "priority",
        label: "Priority",
        type: "select",
        options: [
          ["low", "Low"],
          ["medium", "Medium"],
          ["high", "High"],
          ["urgent", "Urgent"],
        ],
      },
      { key: "reported_by", label: "Reported By" },
      { key: "assigned_to", label: "Assigned To" },
      { key: "reported_date", label: "Reported Date", type: "date" },
      { key: "scheduled_date", label: "Scheduled Date", type: "date" },
      { key: "completed_date", label: "Completed Date", type: "date" },
      { key: "estimated_cost", label: "Estimated Cost" },
    ],
  },
  mess: {
    key: "mess",
    icon: BuildingOffice2Icon,
    label: "Mess Management",
    endpoint: "mess",
    titleField: "hostel",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "date", label: "Date", type: "date" },
      {
        key: "meal_type",
        label: "Meal Type",
        type: "select",
        options: [
          ["breakfast", "Breakfast"],
          ["lunch", "Lunch"],
          ["snack", "Snack"],
          ["dinner", "Dinner"],
        ],
      },
      { key: "menu_items", label: "Menu Items" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "is_vegetarian", label: "Is Vegetarian" },
      { key: "is_vegan", label: "Is Vegan" },
      { key: "is_halal", label: "Is Halal" },
      { key: "is_gluten_free", label: "Is Gluten Free" },
      { key: "rating", label: "Rating" },
      { key: "cost_per_meal", label: "Cost Per Meal" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "created_by", label: "Created By" },
    ],
  },
  "mess-attendance": {
    key: "mess-attendance",
    icon: BuildingOffice2Icon,
    label: "Mess Attendance",
    endpoint: "mess-attendance",
    titleField: "mess_menu",
    subtitleField: "status",
    fields: [
      { key: "mess_menu", label: "Mess Menu" },
      { key: "allocation", label: "Allocation" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["attended", "Attended"],
          ["absent", "Absent"],
          ["skipped", "Skipped"],
        ],
      },
      { key: "recorded_at", label: "Recorded At", type: "date" },
    ],
  },
  "mess-dietary-request": {
    key: "mess-dietary-request",
    icon: BuildingOffice2Icon,
    label: "Mess Dietary Request",
    endpoint: "mess-dietary-request",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "allocation", label: "Allocation" },
      {
        key: "diet_type",
        label: "Diet Type",
        type: "select",
        options: [
          ["vegetarian", "Vegetarian"],
          ["vegan", "Vegan"],
          ["gluten_free", "Gluten Free"],
          ["diabetic", "Diabetic"],
          ["low_sodium", "Low Sodium"],
          ["halal", "Halal"],
          ["kosher", "Kosher"],
          ["allergy", "Allergy"],
          ["other", "Other"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["denied", "Denied"],
          ["expired", "Expired"],
        ],
      },
      { key: "medical_reason", label: "Medical Reason" },
      { key: "doctor_note", label: "Doctor Note" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "approved_by", label: "Approved By" },
    ],
  },
  "mess-feedback": {
    key: "mess-feedback",
    icon: BuildingOffice2Icon,
    label: "Mess Feedback",
    endpoint: "mess-feedback",
    titleField: "hostel",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "student", label: "Student" },
      {
        key: "meal_type",
        label: "Meal Type",
        type: "select",
        options: [
          ["breakfast", "Breakfast"],
          ["lunch", "Lunch"],
          ["dinner", "Dinner"],
          ["snack", "Snack"],
        ],
      },
      {
        key: "rating",
        label: "Rating",
        type: "select",
        options: [
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
        ],
      },
      {
        key: "food_quality",
        label: "Food Quality",
        type: "select",
        options: [
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
        ],
      },
      { key: "portion_size", label: "Portion Size" },
      {
        key: "hygiene_rating",
        label: "Hygiene Rating",
        type: "select",
        options: [
          ["1", "1"],
          ["2", "2"],
          ["3", "3"],
          ["4", "4"],
          ["5", "5"],
        ],
      },
      { key: "liked_items", label: "Liked Items" },
      { key: "disliked_items", label: "Disliked Items" },
      { key: "suggestions", label: "Suggestions" },
      { key: "meal_date", label: "Meal Date", type: "date" },
      { key: "is_anonymous", label: "Is Anonymous" },
    ],
  },
  "mess-menu-plan": {
    key: "mess-menu-plan",
    icon: BuildingOffice2Icon,
    label: "Mess Menu Plan",
    endpoint: "mess-menu-plan",
    titleField: "hostel",
    fields: [
      { key: "hostel", label: "Hostel" },
      {
        key: "meal_type",
        label: "Meal Type",
        type: "select",
        options: [
          ["breakfast", "Breakfast"],
          ["lunch", "Lunch"],
          ["snack", "Snack"],
          ["dinner", "Dinner"],
        ],
      },
      {
        key: "day_of_week",
        label: "Day Of Week",
        type: "select",
        options: [
          ["monday", "Monday"],
          ["tuesday", "Tuesday"],
          ["wednesday", "Wednesday"],
          ["thursday", "Thursday"],
          ["friday", "Friday"],
          ["saturday", "Saturday"],
          ["sunday", "Sunday"],
        ],
      },
      { key: "week_number", label: "Week Number" },
      { key: "main_course", label: "Main Course" },
      { key: "side_dish", label: "Side Dish" },
      { key: "bread_rice", label: "Bread Rice" },
      { key: "dessert", label: "Dessert" },
      { key: "beverage", label: "Beverage" },
      { key: "is_vegetarian", label: "Is Vegetarian" },
      { key: "is_vegan", label: "Is Vegan" },
      { key: "is_gluten_free", label: "Is Gluten Free" },
      { key: "calories", label: "Calories" },
    ],
  },
  notifications: {
    key: "notifications",
    icon: BuildingOffice2Icon,
    label: "Hostel Notification",
    endpoint: "notifications",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "hostel", label: "Hostel" },
      {
        key: "notification_type",
        label: "Notification Type",
        type: "select",
        options: [
          ["general", "General"],
          ["emergency", "Emergency"],
          ["maintenance", "Maintenance"],
          ["leave", "Leave"],
          ["complaint", "Complaint"],
          ["fee", "Fee"],
          ["event", "Event"],
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
          ["read", "Read"],
          ["failed", "Failed"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "message", label: "Message", type: "textarea" },
      {
        key: "recipient_type",
        label: "Recipient Type",
        type: "select",
        options: [
          ["all", "All"],
          ["specific", "Specific"],
          ["warden", "Warden"],
          ["parent", "Parent"],
        ],
      },
      { key: "recipients", label: "Recipients", type: "textarea" },
      { key: "sent_at", label: "Sent At", type: "date" },
      { key: "read_count", label: "Read Count" },
      { key: "is_priority", label: "Is Priority" },
      { key: "created_by", label: "Created By" },
    ],
  },
  reports: {
    key: "reports",
    icon: BuildingOffice2Icon,
    label: "Hostel Report",
    endpoint: "reports",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "title", label: "Title" },
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: [
          ["occupancy", "Occupancy"],
          ["financial", "Financial"],
          ["maintenance", "Maintenance"],
          ["discipline", "Discipline"],
          ["attendance", "Attendance"],
          ["mess", "Mess"],
          ["complaint", "Complaint"],
          ["general", "General"],
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
      { key: "total_rooms", label: "Total Rooms" },
      { key: "occupied_rooms", label: "Occupied Rooms" },
      { key: "occupancy_rate", label: "Occupancy Rate" },
      { key: "total_complaints", label: "Total Complaints" },
    ],
  },
  "room-key": {
    key: "room-key",
    icon: BuildingOffice2Icon,
    label: "Room Key",
    endpoint: "room-key",
    titleField: "room",
    subtitleField: "status",
    fields: [
      { key: "room", label: "Room" },
      { key: "key_number", label: "Key Number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["assigned", "Assigned"],
          ["returned", "Returned"],
          ["lost", "Lost"],
          ["replaced", "Replaced"],
        ],
      },
      { key: "allocated_to", label: "Allocated To" },
      { key: "issued_date", label: "Issued Date", type: "date" },
      { key: "return_date", label: "Return Date", type: "date" },
      { key: "replacement_cost", label: "Replacement Cost" },
      { key: "reported_lost_date", label: "Reported Lost Date", type: "date" },
    ],
  },
  "roommate-assignment": {
    key: "roommate-assignment",
    icon: BuildingOffice2Icon,
    label: "Roommate Assignment",
    endpoint: "roommate-assignment",
    titleField: "room",
    fields: [
      { key: "room", label: "Room" },
      { key: "student", label: "Student" },
      { key: "allocation", label: "Allocation" },
      { key: "match_score", label: "Match Score" },
      { key: "assigned_date", label: "Assigned Date", type: "date" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "roommate-match-request": {
    key: "roommate-match-request",
    icon: BuildingOffice2Icon,
    label: "Roommate Match Request",
    endpoint: "roommate-match-request",
    titleField: "requester",
    subtitleField: "status",
    fields: [
      { key: "requester", label: "Requester" },
      { key: "requested", label: "Requested" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["accepted", "Accepted"],
          ["declined", "Declined"],
          ["expired", "Expired"],
        ],
      },
      { key: "message", label: "Message", type: "textarea" },
      { key: "response_message", label: "Response Message" },
      { key: "responded_at", label: "Responded At", type: "date" },
    ],
  },
  "roommate-preference": {
    key: "roommate-preference",
    icon: BuildingOffice2Icon,
    label: "Roommate Preference",
    endpoint: "roommate-preference",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "sleep_time", label: "Sleep Time" },
      { key: "wake_time", label: "Wake Time" },
      { key: "is_light_sleeper", label: "Is Light Sleeper" },
      { key: "study_habits", label: "Study Habits" },
      { key: "prefers_study_at", label: "Prefers Study At", type: "date" },
      { key: "visitor_frequency", label: "Visitor Frequency" },
      { key: "is_social", label: "Is Social" },
      { key: "smoking", label: "Smoking" },
      { key: "snoring", label: "Snoring" },
      { key: "neatness_level", label: "Neatness Level" },
    ],
  },
  rooms: {
    key: "rooms",
    icon: BuildingOffice2Icon,
    label: "Hostel Room",
    endpoint: "rooms",
    titleField: "hostel",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "room_number", label: "Room Number" },
      { key: "floor", label: "Floor" },
      {
        key: "room_type",
        label: "Room Type",
        type: "select",
        options: [
          ["single", "Single"],
          ["double", "Double"],
          ["triple", "Triple"],
          ["dormitory", "Dormitory"],
        ],
      },
      { key: "capacity", label: "Capacity" },
      { key: "is_furnished", label: "Is Furnished" },
      { key: "has_ac", label: "Has Ac" },
      { key: "has_attached_bathroom", label: "Has Attached Bathroom" },
      { key: "monthly_fee", label: "Monthly Fee" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  transfers: {
    key: "transfers",
    icon: BuildingOffice2Icon,
    label: "Room Transfer",
    endpoint: "transfers",
    titleField: "allocation",
    subtitleField: "status",
    fields: [
      { key: "allocation", label: "Allocation" },
      { key: "from_room", label: "From Room" },
      { key: "to_room", label: "To Room" },
      { key: "reason", label: "Reason" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["completed", "Completed"],
          ["rejected", "Rejected"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "approved_by", label: "Approved By" },
      { key: "approved_at", label: "Approved At", type: "date" },
      { key: "rejection_reason", label: "Rejection Reason" },
      { key: "requested_date", label: "Requested Date", type: "date" },
      { key: "transfer_date", label: "Transfer Date", type: "date" },
    ],
  },
  "visitor-pass": {
    key: "visitor-pass",
    icon: BuildingOffice2Icon,
    label: "Visitor Pass",
    endpoint: "visitor-pass",
    titleField: "hostel",
    subtitleField: "status",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "resident", label: "Resident" },
      { key: "visitor_name", label: "Visitor Name" },
      { key: "visitor_phone", label: "Visitor Phone" },
      { key: "visitor_id_number", label: "Visitor Id Number" },
      { key: "relationship", label: "Relationship" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["requested", "Requested"],
          ["approved", "Approved"],
          ["denied", "Denied"],
          ["checked_in", "Checked In"],
          ["checked_out", "Checked Out"],
          ["expired", "Expired"],
        ],
      },
      { key: "visit_date", label: "Visit Date", type: "date" },
      { key: "expected_arrival", label: "Expected Arrival" },
      { key: "expected_departure", label: "Expected Departure" },
    ],
  },
  visitors: {
    key: "visitors",
    icon: BuildingOffice2Icon,
    label: "Hostel Visitor",
    endpoint: "visitors",
    titleField: "hostel",
    fields: [
      { key: "hostel", label: "Hostel" },
      { key: "visitor_name", label: "Visitor Name" },
      { key: "phone", label: "Phone" },
      { key: "id_proof", label: "Id Proof" },
      { key: "student_visited", label: "Student Visited" },
      { key: "purpose", label: "Purpose" },
      { key: "in_time", label: "In Time" },
      { key: "out_time", label: "Out Time" },
      { key: "relationship", label: "Relationship" },
      { key: "checked_in_by", label: "Checked In By" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "wellness-check": {
    key: "wellness-check",
    icon: BuildingOffice2Icon,
    label: "Wellness Check",
    endpoint: "wellness-check",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "allocation", label: "Allocation" },
      { key: "checked_by", label: "Checked By" },
      {
        key: "check_type",
        label: "Check Type",
        type: "select",
        options: [
          ["routine", "Routine"],
          ["follow_up", "Follow Up"],
          ["welfare", "Welfare"],
          ["medical", "Medical"],
          ["mental", "Mental"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["completed", "Completed"],
          ["issue", "Issue"],
          ["escalated", "Escalated"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "check_date", label: "Check Date", type: "date" },
      { key: "physical_wellbeing", label: "Physical Wellbeing" },
      { key: "emotional_state", label: "Emotional State" },
      { key: "room_condition", label: "Room Condition" },
    ],
  },
};

const TABS = Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({
  key,
  label: cfg.label,
  icon: BuildingOffice2Icon,
}));

export default function HostelCenterPage() {
  useTitle("Hostel Center");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Hostel Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Hostels, rooms, allocations, mess, visitors, events, assets, emergencies, inspections
            and wellness
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
            leftIcon={<BuildingOffice2Icon className="h-4 w-4" />}
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
        basePath="/hostel"
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
