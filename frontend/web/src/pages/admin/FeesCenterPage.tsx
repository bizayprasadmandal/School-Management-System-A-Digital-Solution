/**
 * Finance Center — full-surface admin page for the fees module.
 *
 * 39 entity tabs (config-driven via EntitySection). Invoices, payments, budgets, expenses, refunds, reconciliations, templates and audits.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import {
  MagnifyingGlassIcon,
  BanknotesIcon,
  DocumentTextIcon,
  CurrencyDollarIcon,
  CalculatorIcon,
  ChartBarIcon,
  ClipboardDocumentListIcon,
  ReceiptPercentIcon,
  TicketIcon,
  GiftIcon,
  ArrowUturnLeftIcon,
  NoSymbolIcon,
  CheckBadgeIcon,
  BuildingLibraryIcon,
  AcademicCapIcon,
  CalendarDaysIcon,
  CreditCardIcon,
  CurrencyRupeeIcon,
  DocumentDuplicateIcon,
  EnvelopeIcon,
  ExclamationTriangleIcon,
  FolderOpenIcon,
  HandRaisedIcon,
  KeyIcon,
  ListBulletIcon,
  MagnifyingGlassCircleIcon,
  PencilSquareIcon,
  QueueListIcon,
  ShieldCheckIcon,
  SwatchIcon,
  TagIcon,
  TrophyIcon,
  WalletIcon,
} from "@heroicons/react/24/outline";

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  "accounting-entry": {
    key: "accounting-entry",
    icon: CalculatorIcon,
    label: "Accounting Entry",
    endpoint: "accounting-entry",
    titleField: "entry_type",
    fields: [
      {
        key: "entry_type",
        label: "Entry Type",
        type: "select",
        options: [
          ["debit", "Debit"],
          ["credit", "Credit"],
        ],
      },
      { key: "account_code", label: "Account Code" },
      { key: "account_name", label: "Account Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "amount", label: "Amount", type: "number" },
      { key: "reference_type", label: "Reference Type" },
      { key: "reference_id", label: "Reference Id" },
      { key: "entry_date", label: "Entry Date", type: "date" },
      { key: "created_by", label: "Created By" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  adjustments: {
    key: "adjustments",
    icon: CurrencyRupeeIcon,
    label: "Fee Adjustment",
    endpoint: "adjustments",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "invoice", label: "Invoice" },
      {
        key: "adjustment_type",
        label: "Adjustment Type",
        type: "select",
        options: [
          ["discount", "Discount"],
          ["surcharge", "Surcharge"],
          ["waiver", "Waiver"],
          ["penalty", "Penalty"],
          ["credit", "Credit"],
          ["other", "Other"],
        ],
      },
      { key: "amount", label: "Amount", type: "number" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "approved_by", label: "Approved By" },
      { key: "approved_at", label: "Approved At", type: "date" },
      { key: "adjustment_date", label: "Adjustment Date", type: "date" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "advance-payments": {
    key: "advance-payments",
    icon: WalletIcon,
    label: "Advance Payment",
    endpoint: "advance-payments",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "amount", label: "Amount", type: "number" },
      { key: "payment", label: "Payment" },
      { key: "applied_to_invoice", label: "Applied To Invoice" },
      { key: "applied_amount", label: "Applied Amount" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["applied", "Applied"],
          ["refunded", "Refunded"],
          ["expired", "Expired"],
        ],
      },
      { key: "payment_date", label: "Payment Date", type: "date" },
      { key: "applied_date", label: "Applied Date", type: "date" },
      { key: "expiry_date", label: "Expiry Date", type: "date" },
    ],
  },
  "bank-reconciliation": {
    key: "bank-reconciliation",
    icon: BuildingLibraryIcon,
    label: "Bank Reconciliation",
    endpoint: "bank-reconciliation",
    titleField: "bank_statement_date",
    subtitleField: "status",
    fields: [
      {
        key: "bank_statement_date",
        label: "Bank Statement Date",
        type: "date",
      },
      { key: "statement_balance", label: "Statement Balance" },
      { key: "book_balance", label: "Book Balance" },
      { key: "difference", label: "Difference" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["matched", "Matched"],
          ["unmatched", "Unmatched"],
          ["adjusted", "Adjusted"],
        ],
      },
      { key: "matched_transactions", label: "Matched Transactions" },
      { key: "unmatched_transactions", label: "Unmatched Transactions" },
      { key: "adjustments", label: "Adjustments" },
      { key: "reconciled_by", label: "Reconciled By" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "budget-line-item": {
    key: "budget-line-item",
    icon: ClipboardDocumentListIcon,
    label: "Budget Line Item",
    endpoint: "budget-line-item",
    titleField: "budget_plan",
    subtitleField: "category",
    fields: [
      { key: "budget_plan", label: "Budget Plan" },
      { key: "category", label: "Category" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "budgeted_amount", label: "Budgeted Amount" },
      { key: "actual_amount", label: "Actual Amount" },
      { key: "variance", label: "Variance" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "budget-plan": {
    key: "budget-plan",
    icon: ChartBarIcon,
    label: "Budget Plan",
    endpoint: "budget-plan",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "academic_year", label: "Academic Year" },
      { key: "title", label: "Title" },
      { key: "total_budget", label: "Total Budget" },
      { key: "allocated", label: "Allocated" },
      { key: "spent", label: "Spent" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["approved", "Approved"],
          ["active", "Active"],
          ["closed", "Closed"],
        ],
      },
      { key: "approved_by", label: "Approved By" },
      { key: "approved_date", label: "Approved Date", type: "date" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "bulk-invoices": {
    key: "bulk-invoices",
    icon: DocumentDuplicateIcon,
    label: "Bulk Invoice Generation",
    endpoint: "bulk-invoices",
    titleField: "batch_name",
    subtitleField: "status",
    fields: [
      { key: "batch_name", label: "Batch Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "academic_year", label: "Academic Year" },
      { key: "grades", label: "Grades" },
      { key: "fee_categories", label: "Fee Categories" },
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
      { key: "total_students", label: "Total Students", type: "number" },
      { key: "total_invoices_generated", label: "Total Invoices Generated" },
      { key: "total_amount", label: "Total Amount", type: "number" },
      { key: "errors", label: "Errors" },
      { key: "initiated_by", label: "Initiated By" },
    ],
  },
  categories: {
    key: "categories",
    icon: TagIcon,
    label: "Fee Category",
    endpoint: "categories",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "is_mandatory", label: "Is Mandatory" },
      { key: "is_recurring", label: "Is Recurring" },
      {
        key: "recurrence",
        label: "Recurrence",
        type: "select",
        options: [
          ["monthly", "Monthly"],
          ["quarterly", "Quarterly"],
          ["annual", "Annual"],
          ["one_time", "One Time"],
        ],
      },
    ],
  },
  concessions: {
    key: "concessions",
    icon: GiftIcon,
    label: "Fee Concession",
    endpoint: "concessions",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "academic_year", label: "Academic Year" },
      {
        key: "concession_type",
        label: "Concession Type",
        type: "select",
        options: [
          ["sibling", "Sibling"],
          ["staff_ward", "Staff Ward"],
          ["merit", "Merit"],
          ["need_based", "Need Based"],
          ["government", "Government"],
          ["sports", "Sports"],
          ["cultural", "Cultural"],
          ["other", "Other"],
        ],
      },
      { key: "name", label: "Name" },
      {
        key: "discount_type",
        label: "Discount Type",
        type: "select",
        options: [
          ["percent", "Percent"],
          ["fixed", "Fixed"],
        ],
      },
      { key: "discount_value", label: "Discount Value" },
      { key: "applies_to_categories", label: "Applies To Categories" },
      { key: "max_amount", label: "Max Amount" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["rejected", "Rejected"],
          ["expired", "Expired"],
        ],
      },
      { key: "approved_by", label: "Approved By" },
    ],
  },
  "credit-note": {
    key: "credit-note",
    icon: ArrowUturnLeftIcon,
    label: "Credit Note",
    endpoint: "credit-note",
    titleField: "note_number",
    subtitleField: "status",
    fields: [
      { key: "note_number", label: "Note Number" },
      { key: "student", label: "Student" },
      { key: "invoice", label: "Invoice" },
      { key: "amount", label: "Amount", type: "number" },
      { key: "reason", label: "Reason" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["issued", "Issued"],
          ["applied", "Applied"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "issued_date", label: "Issued Date", type: "date" },
      { key: "applied_date", label: "Applied Date", type: "date" },
      { key: "issued_by", label: "Issued By" },
    ],
    actions: [
      {
        label: "Apply to invoice",
        url: (id) => `/fees/credit-note/${id}/apply/`,
        confirm:
          "Apply this credit note to its invoice? This reduces the invoice total and cannot be undone.",
        kind: "approve",
        visibleIf: (row) =>
          (row["status"] === "draft" || row["status"] === "issued") && !!row["invoice"],
      },
    ],
  },
  dashboard: {
    key: "dashboard",
    icon: SwatchIcon,
    label: "Fee Collection Dashboard",
    endpoint: "dashboard",
    titleField: "total_expected",
    fields: [
      { key: "total_expected", label: "Total Expected" },
      { key: "total_collected", label: "Total Collected" },
      { key: "total_outstanding", label: "Total Outstanding" },
      { key: "collection_percentage", label: "Collection Percentage" },
      { key: "collected_by_category", label: "Collected By Category" },
      { key: "outstanding_by_category", label: "Outstanding By Category" },
      { key: "collected_by_grade", label: "Collected By Grade" },
      { key: "outstanding_by_grade", label: "Outstanding By Grade" },
      { key: "collected_by_method", label: "Collected By Method" },
      { key: "daily_collection", label: "Daily Collection" },
      { key: "monthly_collection", label: "Monthly Collection" },
      { key: "total_defaulters", label: "Total Defaulters" },
    ],
  },
  "debit-note": {
    key: "debit-note",
    icon: ExclamationTriangleIcon,
    label: "Debit Note",
    endpoint: "debit-note",
    titleField: "note_number",
    subtitleField: "status",
    fields: [
      { key: "note_number", label: "Note Number" },
      { key: "student", label: "Student" },
      { key: "invoice", label: "Invoice" },
      { key: "amount", label: "Amount", type: "number" },
      { key: "reason", label: "Reason" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["issued", "Issued"],
          ["applied", "Applied"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "issued_date", label: "Issued Date", type: "date" },
      { key: "applied_date", label: "Applied Date", type: "date" },
      { key: "issued_by", label: "Issued By" },
    ],
    actions: [
      {
        label: "Apply to invoice",
        url: (id) => `/fees/debit-note/${id}/apply/`,
        confirm:
          "Apply this debit note to its invoice? This increases the invoice total and cannot be undone.",
        kind: "info",
        visibleIf: (row) =>
          (row["status"] === "draft" || row["status"] === "issued") && !!row["invoice"],
      },
    ],
  },
  "expense-tracking": {
    key: "expense-tracking",
    icon: ReceiptPercentIcon,
    label: "Expense Tracking",
    endpoint: "expense-tracking",
    titleField: "expense_type",
    subtitleField: "status",
    fields: [
      {
        key: "expense_type",
        label: "Expense Type",
        type: "select",
        options: [
          ["salary", "Salary"],
          ["utility", "Utility"],
          ["maintenance", "Maintenance"],
          ["supplies", "Supplies"],
          ["transport", "Transport"],
          ["event", "Event"],
          ["other", "Other"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "amount", label: "Amount", type: "number" },
      { key: "vendor", label: "Vendor" },
      { key: "invoice_number", label: "Invoice Number" },
      { key: "expense_date", label: "Expense Date", type: "date" },
      { key: "category", label: "Category" },
      { key: "approved_by", label: "Approved By" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["paid", "Paid"],
        ],
      },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "fee-discount": {
    key: "fee-discount",
    icon: TicketIcon,
    label: "Fee Discount",
    endpoint: "fee-discount",
    titleField: "name",
    subtitleField: "category",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "discount_type",
        label: "Discount Type",
        type: "select",
        options: [
          ["percentage", "Percentage"],
          ["fixed", "Fixed"],
        ],
      },
      { key: "value", label: "Value", type: "number" },
      {
        key: "applies_to",
        label: "Applies To",
        type: "select",
        options: [
          ["all", "All"],
          ["category", "Category"],
          ["grade", "Grade"],
        ],
      },
      { key: "grade", label: "Grade" },
      { key: "category", label: "Category" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "fee-exemption": {
    key: "fee-exemption",
    icon: NoSymbolIcon,
    label: "Fee Exemption",
    endpoint: "fee-exemption",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "fee_structure", label: "Fee Structure" },
      { key: "reason", label: "Reason" },
      {
        key: "exemption_type",
        label: "Exemption Type",
        type: "select",
        options: [
          ["full", "Full"],
          ["partial", "Partial"],
        ],
      },
      { key: "percentage", label: "Percentage", type: "number" },
      { key: "approved_by", label: "Approved By" },
      { key: "approved_date", label: "Approved Date", type: "date" },
      { key: "valid_from", label: "Valid From" },
      { key: "valid_to", label: "Valid To" },
    ],
  },
  "fee-waiver-approval": {
    key: "fee-waiver-approval",
    icon: CheckBadgeIcon,
    label: "Fee Waiver Approval",
    endpoint: "fee-waiver-approval",
    titleField: "waiver",
    subtitleField: "status",
    fields: [
      { key: "waiver", label: "Waiver" },
      { key: "approver", label: "Approver" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["rejected", "Rejected"],
        ],
      },
      { key: "comments", label: "Comments" },
      { key: "approved_date", label: "Approved Date", type: "date" },
    ],
  },
  "financial-audit": {
    key: "financial-audit",
    icon: ShieldCheckIcon,
    label: "Financial Audit",
    endpoint: "financial-audit",
    titleField: "title",
    subtitleField: "status",
    fields: [
      {
        key: "audit_type",
        label: "Audit Type",
        type: "select",
        options: [
          ["internal", "Internal"],
          ["external", "External"],
          ["tax", "Tax"],
          ["other", "Other"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "audit_period_start", label: "Audit Period Start" },
      { key: "audit_period_end", label: "Audit Period End" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["scheduled", "Scheduled"],
          ["in_progress", "In Progress"],
          ["completed", "Completed"],
          ["findings", "Findings"],
        ],
      },
      { key: "auditor_name", label: "Auditor Name" },
      { key: "auditor_organization", label: "Auditor Organization" },
      { key: "findings", label: "Findings" },
      { key: "recommendations", label: "Recommendations" },
      { key: "total_revenue", label: "Total Revenue", type: "number" },
      { key: "total_expenses", label: "Total Expenses", type: "number" },
      { key: "net_income", label: "Net Income" },
    ],
  },
  "financial-year": {
    key: "financial-year",
    icon: CalendarDaysIcon,
    label: "Financial Year",
    endpoint: "financial-year",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      { key: "is_current", label: "Is Current", type: "bool" },
      { key: "is_closed", label: "Is Closed" },
      { key: "closed_by", label: "Closed By" },
      { key: "closed_date", label: "Closed Date", type: "date" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
    actions: [
      {
        label: "Close financial year",
        url: (id) => `/fees/financial-year/${id}/close/`,
        confirm:
          "Close this financial year? Outstanding balances are rolled forward and the year is locked permanently.",
        kind: "approve",
        visibleIf: (row) => !row["is_closed"],
      },
    ],
  },
  "installment-payments": {
    key: "installment-payments",
    icon: CreditCardIcon,
    label: "Installment Payment",
    endpoint: "installment-payments",
    titleField: "installment_plan",
    subtitleField: "status",
    fields: [
      { key: "installment_plan", label: "Installment Plan" },
      { key: "installment_number", label: "Installment Number" },
      { key: "amount", label: "Amount", type: "number" },
      { key: "due_date", label: "Due Date", type: "date" },
      { key: "paid_date", label: "Paid Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["paid", "Paid"],
          ["overdue", "Overdue"],
          ["waived", "Waived"],
        ],
      },
      { key: "late_fee", label: "Late Fee" },
      { key: "payment", label: "Payment" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "installment-plans": {
    key: "installment-plans",
    icon: ListBulletIcon,
    label: "Installment Plan",
    endpoint: "installment-plans",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "invoice", label: "Invoice" },
      { key: "total_amount", label: "Total Amount", type: "number" },
      { key: "number_of_installments", label: "Number Of Installments" },
      { key: "installment_amount", label: "Installment Amount" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
          ["defaulted", "Defaulted"],
        ],
      },
      { key: "late_fee_per_installment", label: "Late Fee Per Installment" },
      { key: "grace_period_days", label: "Grace Period Days" },
    ],
  },
  "invoice-template": {
    key: "invoice-template",
    icon: DocumentTextIcon,
    label: "Invoice Template",
    endpoint: "invoice-template",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "header_text", label: "Header Text" },
      { key: "footer_text", label: "Footer Text" },
      { key: "terms_and_conditions", label: "Terms And Conditions" },
      { key: "logo_url", label: "Logo Url" },
      { key: "is_default", label: "Is Default", type: "bool" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  invoices: {
    key: "invoices",
    icon: BanknotesIcon,
    label: "Fee Invoice",
    endpoint: "invoices",
    titleField: "invoice_number",
    subtitleField: "status",
    fields: [
      { key: "invoice_number", label: "Invoice Number" },
      { key: "student", label: "Student" },
      { key: "academic_year", label: "Academic Year" },
      { key: "fee_structure", label: "Fee Structure" },
      { key: "due_date", label: "Due Date", type: "date" },
      { key: "base_amount", label: "Base Amount" },
      { key: "discount_amount", label: "Discount Amount" },
      { key: "late_fee", label: "Late Fee" },
      { key: "total_amount", label: "Total Amount", type: "number" },
      { key: "paid_amount", label: "Paid Amount", type: "number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["unpaid", "Unpaid"],
          ["partial", "Partial"],
          ["paid", "Paid"],
          ["overdue", "Overdue"],
          ["waived", "Waived"],
          ["cancelled", "Cancelled"],
        ],
      },
    ],
  },
  "late-fee-rule": {
    key: "late-fee-rule",
    icon: PencilSquareIcon,
    label: "Late Fee Rule",
    endpoint: "late-fee-rule",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "days_after_due", label: "Days After Due" },
      { key: "fee_amount", label: "Fee Amount" },
      {
        key: "fee_type",
        label: "Fee Type",
        type: "select",
        options: [
          ["fixed", "Fixed"],
          ["percentage", "Percentage"],
        ],
      },
      { key: "percentage", label: "Percentage", type: "number" },
      { key: "max_late_fee", label: "Max Late Fee" },
      {
        key: "applies_to",
        label: "Applies To",
        type: "select",
        options: [
          ["all", "All"],
          ["specific", "Specific"],
        ],
      },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  ledger: {
    key: "ledger",
    icon: FolderOpenIcon,
    label: "Student Ledger",
    endpoint: "ledger",
    titleField: "student",
    fields: [
      { key: "student", label: "Student" },
      { key: "academic_year", label: "Academic Year" },
      {
        key: "transaction_type",
        label: "Transaction Type",
        type: "select",
        options: [
          ["invoice", "Invoice"],
          ["payment", "Payment"],
          ["adjustment", "Adjustment"],
          ["scholarship", "Scholarship"],
          ["concession", "Concession"],
          ["waiver", "Waiver"],
          ["refund", "Refund"],
          ["late_fee", "Late Fee"],
          ["other", "Other"],
        ],
      },
      { key: "amount", label: "Amount", type: "number" },
      { key: "balance_after", label: "Balance After" },
      { key: "invoice", label: "Invoice" },
      { key: "payment", label: "Payment" },
      { key: "description", label: "Description", type: "textarea" },
    ],
  },
  "parent-account": {
    key: "parent-account",
    icon: AcademicCapIcon,
    label: "Parent Account",
    endpoint: "parent-account",
    titleField: "parent",
    fields: [
      { key: "parent", label: "Parent" },
      { key: "balance", label: "Balance" },
      { key: "total_paid", label: "Total Paid" },
      { key: "total_outstanding", label: "Total Outstanding" },
      { key: "payment_method", label: "Payment Method" },
      { key: "auto_pay_enabled", label: "Auto Pay Enabled" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "payment-gateway-config": {
    key: "payment-gateway-config",
    icon: KeyIcon,
    label: "Payment Gateway Config",
    endpoint: "payment-gateway-config",
    titleField: "stripe_enabled",
    fields: [
      { key: "stripe_enabled", label: "Stripe Enabled", type: "bool" },
      { key: "khalti_enabled", label: "Khalti Enabled", type: "bool" },
      { key: "esewa_enabled", label: "Esewa Enabled", type: "bool" },
    ],
  },
  "payment-method": {
    key: "payment-method",
    icon: CurrencyDollarIcon,
    label: "Payment Method",
    endpoint: "payment-method",
    titleField: "name",
    subtitleField: "method_type",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "method_type",
        label: "Method Type",
        type: "select",
        options: [
          ["cash", "Cash"],
          ["cheque", "Cheque"],
          ["bank_transfer", "Bank Transfer"],
          ["online", "Online"],
          ["card", "Card"],
          ["mobile", "Mobile"],
          ["other", "Other"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "processing_fee_percentage", label: "Processing Fee Percentage" },
      { key: "processing_fee_fixed", label: "Processing Fee Fixed" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "payment-reminders": {
    key: "payment-reminders",
    icon: EnvelopeIcon,
    label: "Payment Reminder",
    endpoint: "payment-reminders",
    titleField: "subject",
    subtitleField: "status",
    fields: [
      { key: "invoice", label: "Invoice" },
      { key: "student", label: "Student" },
      {
        key: "reminder_type",
        label: "Reminder Type",
        type: "select",
        options: [
          ["email", "Email"],
          ["sms", "Sms"],
          ["push", "Push"],
          ["in_app", "In App"],
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
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "subject", label: "Subject", type: "textarea" },
      { key: "message", label: "Message", type: "textarea" },
      { key: "scheduled_date", label: "Scheduled Date", type: "date" },
      { key: "scheduled_time", label: "Scheduled Time" },
      { key: "sent_at", label: "Sent At", type: "date" },
    ],
  },
  payments: {
    key: "payments",
    icon: QueueListIcon,
    label: "Payment",
    endpoint: "payments",
    titleField: "invoice",
    subtitleField: "status",
    fields: [
      { key: "invoice", label: "Invoice" },
      { key: "amount", label: "Amount", type: "number" },
      {
        key: "payment_method",
        label: "Payment Method",
        type: "select",
        options: [
          ["cash", "Cash"],
          ["bank_transfer", "Bank Transfer"],
          ["card", "Card"],
          ["cheque", "Cheque"],
          ["online", "Online"],
          ["mobile", "Mobile"],
          ["khalti", "Khalti"],
          ["esewa", "Esewa"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["successful", "Successful"],
          ["failed", "Failed"],
          ["refunded", "Refunded"],
        ],
      },
      { key: "transaction_id", label: "Transaction Id" },
      { key: "gateway_response", label: "Gateway Response" },
      { key: "receipt_number", label: "Receipt Number" },
      { key: "paid_at", label: "Paid At", type: "date" },
      { key: "receipt_sent_at", label: "Receipt Sent At", type: "date" },
      { key: "collected_by", label: "Collected By" },
      { key: "refunded_by", label: "Refunded By" },
    ],
  },
  "receipt-template": {
    key: "receipt-template",
    icon: HandRaisedIcon,
    label: "Receipt Template",
    endpoint: "receipt-template",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "header_text", label: "Header Text" },
      { key: "footer_text", label: "Footer Text" },
      { key: "is_default", label: "Is Default", type: "bool" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  reconciliation: {
    key: "reconciliation",
    icon: MagnifyingGlassCircleIcon,
    label: "Payment Reconciliation",
    endpoint: "reconciliation",
    titleField: "reconciliation_type",
    subtitleField: "status",
    fields: [
      {
        key: "reconciliation_type",
        label: "Reconciliation Type",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["monthly", "Monthly"],
          ["manual", "Manual"],
        ],
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["in_progress", "In Progress"],
          ["completed", "Completed"],
          ["failed", "Failed"],
          ["discrepancies", "Discrepancies"],
        ],
      },
      { key: "period_start", label: "Period Start" },
      { key: "period_end", label: "Period End" },
      { key: "total_expected", label: "Total Expected" },
      { key: "total_matched", label: "Total Matched" },
      { key: "total_unmatched", label: "Total Unmatched" },
      { key: "match_percentage", label: "Match Percentage" },
      { key: "discrepancies", label: "Discrepancies" },
      { key: "discrepancy_count", label: "Discrepancy Count" },
      { key: "initiated_by", label: "Initiated By" },
    ],
  },
  "refund-record": {
    key: "refund-record",
    icon: ArrowUturnLeftIcon,
    label: "Refund Record",
    endpoint: "refund-record",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "payment", label: "Payment" },
      { key: "invoice", label: "Invoice" },
      { key: "amount", label: "Amount", type: "number" },
      { key: "reason", label: "Reason" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["processed", "Processed"],
          ["rejected", "Rejected"],
        ],
      },
      { key: "processed_date", label: "Processed Date", type: "date" },
      { key: "refund_method", label: "Refund Method" },
      { key: "approved_by", label: "Approved By" },
    ],
  },
  "revenue-reports": {
    key: "revenue-reports",
    icon: ChartBarIcon,
    label: "Revenue Report",
    endpoint: "revenue-reports",
    titleField: "title",
    subtitleField: "status",
    fields: [
      { key: "title", label: "Title" },
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["monthly", "Monthly"],
          ["quarterly", "Quarterly"],
          ["annual", "Annual"],
          ["category", "Category"],
          ["grade", "Grade"],
          ["outstanding", "Outstanding"],
          ["defaulters", "Defaulters"],
          ["scholarship", "Scholarship"],
          ["refund", "Refund"],
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
          ["archived", "Archived"],
        ],
      },
      { key: "period_start", label: "Period Start" },
      { key: "period_end", label: "Period End" },
      { key: "summary", label: "Summary", type: "textarea" },
      { key: "findings", label: "Findings" },
      { key: "recommendations", label: "Recommendations" },
      { key: "total_collected", label: "Total Collected" },
      { key: "total_outstanding", label: "Total Outstanding" },
      { key: "total_refunded", label: "Total Refunded" },
      { key: "total_scholarships", label: "Total Scholarships" },
    ],
  },
  scholarships: {
    key: "scholarships",
    icon: TrophyIcon,
    label: "Scholarship",
    endpoint: "scholarships",
    titleField: "name",
    fields: [
      { key: "student", label: "Student" },
      { key: "academic_year", label: "Academic Year" },
      { key: "name", label: "Name" },
      {
        key: "discount_type",
        label: "Discount Type",
        type: "select",
        options: [
          ["percent", "Percent"],
          ["fixed", "Fixed"],
        ],
      },
      { key: "discount_value", label: "Discount Value" },
      { key: "applies_to_categories", label: "Applies To Categories" },
      { key: "reason", label: "Reason" },
      { key: "approved_by", label: "Approved By" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "sibling-discounts": {
    key: "sibling-discounts",
    icon: TagIcon,
    label: "Sibling Discount",
    endpoint: "sibling-discounts",
    titleField: "name",
    subtitleField: "priority",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "discount_type",
        label: "Discount Type",
        type: "select",
        options: [
          ["percent", "Percent"],
          ["fixed", "Fixed"],
        ],
      },
      { key: "discount_value", label: "Discount Value" },
      { key: "min_siblings", label: "Min Siblings" },
      { key: "applies_to_categories", label: "Applies To Categories" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "priority", label: "Priority" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  structures: {
    key: "structures",
    icon: DocumentTextIcon,
    label: "Fee Structure",
    endpoint: "structures",
    titleField: "academic_year",
    fields: [
      { key: "academic_year", label: "Academic Year" },
      { key: "grade", label: "Grade" },
      { key: "fee_category", label: "Fee Category" },
      { key: "amount", label: "Amount", type: "number" },
      { key: "due_day", label: "Due Day" },
      { key: "late_fee_per_day", label: "Late Fee Per Day" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  templates: {
    key: "templates",
    icon: ClipboardDocumentListIcon,
    label: "Fee Template",
    endpoint: "templates",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "template_type",
        label: "Template Type",
        type: "select",
        options: [
          ["tuition", "Tuition"],
          ["transport", "Transport"],
          ["hostel", "Hostel"],
          ["lab", "Lab"],
          ["library", "Library"],
          ["sports", "Sports"],
          ["exam", "Exam"],
          ["other", "Other"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "default_amount", label: "Default Amount" },
      { key: "is_recurring", label: "Is Recurring" },
      {
        key: "recurrence",
        label: "Recurrence",
        type: "select",
        options: [
          ["monthly", "Monthly"],
          ["quarterly", "Quarterly"],
          ["annual", "Annual"],
          ["one_time", "One Time"],
        ],
      },
      { key: "is_mandatory", label: "Is Mandatory" },
      { key: "late_fee_per_day", label: "Late Fee Per Day" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "created_by", label: "Created By" },
    ],
  },
  "transaction-log": {
    key: "transaction-log",
    icon: ListBulletIcon,
    label: "Transaction Log",
    endpoint: "transaction-log",
    titleField: "transaction_type",
    subtitleField: "status",
    fields: [
      {
        key: "transaction_type",
        label: "Transaction Type",
        type: "select",
        options: [
          ["payment", "Payment"],
          ["refund", "Refund"],
          ["adjustment", "Adjustment"],
          ["late_fee", "Late Fee"],
          ["waiver", "Waiver"],
          ["other", "Other"],
        ],
      },
      { key: "transaction_id", label: "Transaction Id" },
      { key: "student", label: "Student" },
      { key: "amount", label: "Amount", type: "number" },
      { key: "payment_method", label: "Payment Method" },
      { key: "reference_number", label: "Reference Number" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["success", "Success"],
          ["failed", "Failed"],
          ["pending", "Pending"],
        ],
      },
      { key: "description", label: "Description", type: "textarea" },
      { key: "metadata", label: "Metadata" },
    ],
  },
  waivers: {
    key: "waivers",
    icon: HandRaisedIcon,
    label: "Fee Waiver",
    endpoint: "waivers",
    titleField: "student",
    subtitleField: "status",
    fields: [
      { key: "student", label: "Student" },
      { key: "academic_year", label: "Academic Year" },
      {
        key: "waiver_type",
        label: "Waiver Type",
        type: "select",
        options: [
          ["full", "Full"],
          ["partial", "Partial"],
          ["category", "Category"],
        ],
      },
      { key: "amount", label: "Amount", type: "number" },
      { key: "applies_to_categories", label: "Applies To Categories" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["rejected", "Rejected"],
          ["applied", "Applied"],
        ],
      },
      { key: "approved_by", label: "Approved By" },
      { key: "approved_at", label: "Approved At", type: "date" },
      { key: "rejection_reason", label: "Rejection Reason" },
    ],
  },
};

const TABS = Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({
  key,
  label: cfg.label,
  icon: BanknotesIcon,
}));

export default function FeesCenterPage() {
  useTitle("Finance Center");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Finance Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Invoices, payments, budgets, expenses, refunds, reconciliations, templates and audits
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
            leftIcon={<BanknotesIcon className="h-4 w-4" />}
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
        basePath="/fees"
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
