/**
 * Inventory Center — full-surface admin page for the inventory module.
 *
 * 40 entity tabs (config-driven via EntitySection). Items, warehouses, stock, transfers, purchases, suppliers, catalogs, leases and analytics.
 */
import React, { useState, useEffect, useRef } from "react";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { EntitySection, type EntityConfig } from "../../components/common/EntitySection";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { MagnifyingGlassIcon, CubeIcon } from "@heroicons/react/24/outline";

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  // ===== inventory =====
  "asset-tag": {
    key: "asset-tag",
    icon: CubeIcon,
    label: "Asset Tag",
    endpoint: "asset-tag",
    titleField: "item",
    subtitleField: "status",
    fields: [
      { key: "item", label: "Item" },
      { key: "tag_number", label: "Tag Number" },
      { key: "qr_code", label: "Qr Code" },
      { key: "assigned_date", label: "Assigned Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["retired", "Retired"],
          ["lost", "Lost"],
          ["stolen", "Stolen"],
        ],
      },
    ],
  },
  barcode: {
    key: "barcode",
    icon: CubeIcon,
    label: "Barcode",
    endpoint: "barcode",
    titleField: "item",
    fields: [
      { key: "item", label: "Item" },
      {
        key: "barcode_type",
        label: "Barcode Type",
        type: "select",
        options: [
          ["qr", "Qr"],
          ["ean13", "Ean13"],
          ["code128", "Code128"],
          ["upc", "Upc"],
        ],
      },
      { key: "code_value", label: "Code Value" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  categories: {
    key: "categories",
    icon: CubeIcon,
    label: "Category",
    endpoint: "categories",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "inventory-alert": {
    key: "inventory-alert",
    icon: CubeIcon,
    label: "Inventory Alert",
    endpoint: "inventory-alert",
    titleField: "item",
    subtitleField: "alert_type",
    fields: [
      { key: "item", label: "Item" },
      {
        key: "alert_type",
        label: "Alert Type",
        type: "select",
        options: [
          ["low_stock", "Low Stock"],
          ["expiring", "Expiring"],
          ["overstocked", "Overstocked"],
          ["price_change", "Price Change"],
        ],
      },
      { key: "threshold", label: "Threshold" },
      { key: "current_value", label: "Current Value" },
      { key: "is_active", label: "Is Active", type: "bool" },
      { key: "notified", label: "Notified" },
    ],
  },
  "inventory-analytics": {
    key: "inventory-analytics",
    icon: CubeIcon,
    label: "Inventory Analytics",
    endpoint: "inventory-analytics",
    titleField: "period",
    fields: [
      { key: "period", label: "Period" },
      { key: "total_items", label: "Total Items" },
      { key: "total_value", label: "Total Value" },
      { key: "turnover_rate", label: "Turnover Rate" },
      { key: "average_order_value", label: "Average Order Value" },
      { key: "stockout_count", label: "Stockout Count" },
      { key: "overstock_count", label: "Overstock Count" },
    ],
  },
  "inventory-budget": {
    key: "inventory-budget",
    icon: CubeIcon,
    label: "Inventory Budget",
    endpoint: "inventory-budget",
    titleField: "department_name",
    fields: [
      { key: "department_name", label: "Department Name" },
      { key: "fiscal_year", label: "Fiscal Year" },
      { key: "total_budget", label: "Total Budget" },
      { key: "spent", label: "Spent" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "is_approved", label: "Is Approved" },
      { key: "approved_by", label: "Approved By" },
    ],
  },
  "inventory-catalog": {
    key: "inventory-catalog",
    icon: CubeIcon,
    label: "Inventory Catalog",
    endpoint: "inventory-catalog",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "version", label: "Version" },
      { key: "effective_date", label: "Effective Date", type: "date" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "inventory-catalog-extended": {
    key: "inventory-catalog-extended",
    icon: CubeIcon,
    label: "Inventory Catalog Extended",
    endpoint: "inventory-catalog-extended",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "version", label: "Version" },
      { key: "effective_date", label: "Effective Date", type: "date" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "inventory-catalog-item": {
    key: "inventory-catalog-item",
    icon: CubeIcon,
    label: "Inventory Catalog Item",
    endpoint: "inventory-catalog-item",
    titleField: "catalog",
    fields: [
      { key: "catalog", label: "Catalog" },
      { key: "item", label: "Item" },
      { key: "catalog_price", label: "Catalog Price" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "inventory-composite-item": {
    key: "inventory-composite-item",
    icon: CubeIcon,
    label: "Inventory Composite Item",
    endpoint: "inventory-composite-item",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "description", label: "Description", type: "textarea" },
      { key: "quantity", label: "Quantity" },
      { key: "unit_cost", label: "Unit Cost" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "inventory-lease-agreement": {
    key: "inventory-lease-agreement",
    icon: CubeIcon,
    label: "Inventory Lease Agreement",
    endpoint: "inventory-lease-agreement",
    titleField: "item",
    subtitleField: "status",
    fields: [
      { key: "item", label: "Item" },
      { key: "supplier", label: "Supplier" },
      { key: "lease_start", label: "Lease Start" },
      { key: "lease_end", label: "Lease End" },
      { key: "monthly_cost", label: "Monthly Cost" },
      { key: "terms", label: "Terms" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["expired", "Expired"],
          ["terminated", "Terminated"],
        ],
      },
    ],
  },
  "inventory-lease-agreement-extended": {
    key: "inventory-lease-agreement-extended",
    icon: CubeIcon,
    label: "Inventory Lease Agreement Extended",
    endpoint: "inventory-lease-agreement-extended",
    titleField: "item",
    subtitleField: "status",
    fields: [
      { key: "item", label: "Item" },
      { key: "supplier_name", label: "Supplier Name" },
      { key: "lease_start", label: "Lease Start" },
      { key: "lease_end", label: "Lease End" },
      { key: "monthly_cost", label: "Monthly Cost" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["expired", "Expired"],
        ],
      },
    ],
  },
  "inventory-parts": {
    key: "inventory-parts",
    icon: CubeIcon,
    label: "Inventory Parts",
    endpoint: "inventory-parts",
    titleField: "name",
    subtitleField: "category",
    fields: [
      { key: "name", label: "Name" },
      { key: "part_number", label: "Part Number" },
      { key: "category", label: "Category" },
      { key: "unit_cost", label: "Unit Cost" },
      { key: "quantity_in_stock", label: "Quantity In Stock" },
      { key: "reorder_level", label: "Reorder Level" },
    ],
  },
  "inventory-pricing-history": {
    key: "inventory-pricing-history",
    icon: CubeIcon,
    label: "Inventory Pricing History",
    endpoint: "inventory-pricing-history",
    titleField: "item",
    fields: [
      { key: "item", label: "Item" },
      { key: "supplier", label: "Supplier" },
      { key: "unit_price", label: "Unit Price" },
      { key: "effective_date", label: "Effective Date", type: "date" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "inventory-report": {
    key: "inventory-report",
    icon: CubeIcon,
    label: "Inventory Report",
    endpoint: "inventory-report",
    titleField: "title",
    subtitleField: "report_type",
    fields: [
      {
        key: "report_type",
        label: "Report Type",
        type: "select",
        options: [
          ["stock_summary", "Stock Summary"],
          ["valuation", "Valuation"],
          ["movement", "Movement"],
          ["supplier", "Supplier"],
          ["obsolescence", "Obsolescence"],
          ["turnover", "Turnover"],
        ],
      },
      { key: "title", label: "Title" },
      { key: "date_from", label: "Date From", type: "date" },
      { key: "date_to", label: "Date To", type: "date" },
      { key: "generated_by", label: "Generated By" },
      { key: "file", label: "File" },
    ],
  },
  "inventory-settings": {
    key: "inventory-settings",
    icon: CubeIcon,
    label: "Inventory Settings",
    endpoint: "inventory-settings",
    titleField: "default_warehouse",
    fields: [
      { key: "default_warehouse", label: "Default Warehouse" },
      { key: "low_stock_threshold", label: "Low Stock Threshold" },
      { key: "auto_reorder", label: "Auto Reorder" },
      { key: "enable_barcode", label: "Enable Barcode" },
      { key: "enable_serial_tracking", label: "Enable Serial Tracking" },
      { key: "fiscal_year_start_month", label: "Fiscal Year Start Month" },
      { key: "currency", label: "Currency" },
      { key: "tax_rate", label: "Tax Rate" },
    ],
  },
  "inventory-subscription": {
    key: "inventory-subscription",
    icon: CubeIcon,
    label: "Inventory Subscription",
    endpoint: "inventory-subscription",
    titleField: "plan",
    subtitleField: "status",
    fields: [
      { key: "plan", label: "Plan" },
      { key: "supplier", label: "Supplier" },
      { key: "start_date", label: "Start Date", type: "date" },
      { key: "end_date", label: "End Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["cancelled", "Cancelled"],
          ["expired", "Expired"],
        ],
      },
      { key: "auto_renew", label: "Auto Renew" },
    ],
  },
  "inventory-subscription-plan": {
    key: "inventory-subscription-plan",
    icon: CubeIcon,
    label: "Inventory Subscription Plan",
    endpoint: "inventory-subscription-plan",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      {
        key: "plan_type",
        label: "Plan Type",
        type: "select",
        options: [
          ["monthly", "Monthly"],
          ["quarterly", "Quarterly"],
          ["annual", "Annual"],
        ],
      },
      { key: "cost", label: "Cost" },
      { key: "items_included", label: "Items Included" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "inventory-supplier-performance": {
    key: "inventory-supplier-performance",
    icon: CubeIcon,
    label: "Inventory Supplier Performance",
    endpoint: "inventory-supplier-performance",
    titleField: "supplier",
    fields: [
      { key: "supplier", label: "Supplier" },
      { key: "evaluation_period", label: "Evaluation Period" },
      { key: "quality_score", label: "Quality Score" },
      { key: "delivery_score", label: "Delivery Score" },
      { key: "price_score", label: "Price Score" },
      { key: "overall_score", label: "Overall Score" },
      { key: "comments", label: "Comments" },
      { key: "evaluated_by", label: "Evaluated By" },
    ],
  },
  "inventory-transfer-route": {
    key: "inventory-transfer-route",
    icon: CubeIcon,
    label: "Inventory Transfer Route",
    endpoint: "inventory-transfer-route",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "origin_warehouse", label: "Origin Warehouse" },
      { key: "dest_warehouse", label: "Dest Warehouse" },
      { key: "estimated_time_minutes", label: "Estimated Time Minutes" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  invoice: {
    key: "invoice",
    icon: CubeIcon,
    label: "Invoice",
    endpoint: "invoice",
    titleField: "purchase_order",
    subtitleField: "status",
    fields: [
      { key: "purchase_order", label: "Purchase Order" },
      { key: "invoice_number", label: "Invoice Number" },
      { key: "supplier", label: "Supplier" },
      { key: "invoice_date", label: "Invoice Date", type: "date" },
      { key: "due_date", label: "Due Date", type: "date" },
      { key: "subtotal", label: "Subtotal" },
      { key: "tax", label: "Tax" },
      { key: "total", label: "Total" },
      { key: "amount_paid", label: "Amount Paid" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["partial", "Partial"],
          ["paid", "Paid"],
          ["overdue", "Overdue"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "invoice-payment": {
    key: "invoice-payment",
    icon: CubeIcon,
    label: "Invoice Payment",
    endpoint: "invoice-payment",
    titleField: "invoice",
    fields: [
      { key: "invoice", label: "Invoice" },
      { key: "payment_date", label: "Payment Date", type: "date" },
      { key: "amount", label: "Amount", type: "number" },
      {
        key: "payment_method",
        label: "Payment Method",
        type: "select",
        options: [
          ["cash", "Cash"],
          ["cheque", "Cheque"],
          ["bank_transfer", "Bank Transfer"],
          ["online", "Online"],
          ["card", "Card"],
        ],
      },
      { key: "reference_number", label: "Reference Number" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "created_by", label: "Created By" },
    ],
  },
  items: {
    key: "items",
    icon: CubeIcon,
    label: "Inventory Item",
    endpoint: "items",
    titleField: "name",
    subtitleField: "category",
    fields: [
      { key: "category", label: "Category" },
      { key: "supplier", label: "Supplier" },
      { key: "name", label: "Name" },
      { key: "sku", label: "Sku" },
      { key: "description", label: "Description", type: "textarea" },
      {
        key: "unit",
        label: "Unit",
        type: "select",
        options: [
          ["piece", "Piece"],
          ["pack", "Pack"],
          ["box", "Box"],
          ["set", "Set"],
          ["liter", "Liter"],
          ["kilogram", "Kilogram"],
          ["meter", "Meter"],
          ["roll", "Roll"],
          ["pair", "Pair"],
          ["other", "Other"],
        ],
      },
      { key: "unit_price", label: "Unit Price" },
      { key: "current_stock", label: "Current Stock" },
      { key: "minimum_stock", label: "Minimum Stock" },
      { key: "maximum_stock", label: "Maximum Stock" },
    ],
  },
  "purchase-order-item": {
    key: "purchase-order-item",
    icon: CubeIcon,
    label: "Purchase Order Item",
    endpoint: "purchase-order-item",
    titleField: "purchase_order",
    fields: [
      { key: "purchase_order", label: "Purchase Order" },
      { key: "item", label: "Item" },
      { key: "quantity_ordered", label: "Quantity Ordered" },
      { key: "quantity_received", label: "Quantity Received" },
      { key: "unit_price", label: "Unit Price" },
      { key: "total_price", label: "Total Price" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "purchase-orders": {
    key: "purchase-orders",
    icon: CubeIcon,
    label: "Purchase Order",
    endpoint: "purchase-orders",
    titleField: "order_number",
    subtitleField: "status",
    fields: [
      { key: "order_number", label: "Order Number" },
      { key: "supplier", label: "Supplier" },
      { key: "order_date", label: "Order Date", type: "date" },
      { key: "expected_date", label: "Expected Date", type: "date" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["submitted", "Submitted"],
          ["confirmed", "Confirmed"],
          ["partially_received", "Partially Received"],
          ["received", "Received"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "subtotal", label: "Subtotal" },
      { key: "tax_amount", label: "Tax Amount" },
      { key: "shipping_cost", label: "Shipping Cost" },
      { key: "total_amount", label: "Total Amount", type: "number" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "ordered_by", label: "Ordered By" },
    ],
  },
  "purchase-requisition": {
    key: "purchase-requisition",
    icon: CubeIcon,
    label: "Purchase Requisition",
    endpoint: "purchase-requisition",
    titleField: "requisition_number",
    subtitleField: "status",
    fields: [
      { key: "requisition_number", label: "Requisition Number" },
      { key: "department", label: "Department" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["submitted", "Submitted"],
          ["approved", "Approved"],
          ["rejected", "Rejected"],
          ["ordered", "Ordered"],
        ],
      },
      { key: "requested_by", label: "Requested By" },
      { key: "approved_by", label: "Approved By" },
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
      { key: "justification", label: "Justification" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "purchase-requisition-item": {
    key: "purchase-requisition-item",
    icon: CubeIcon,
    label: "Purchase Requisition Item",
    endpoint: "purchase-requisition-item",
    titleField: "requisition",
    fields: [
      { key: "requisition", label: "Requisition" },
      { key: "item", label: "Item" },
      { key: "quantity", label: "Quantity" },
      { key: "estimated_cost", label: "Estimated Cost" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "return-request": {
    key: "return-request",
    icon: CubeIcon,
    label: "Return Request",
    endpoint: "return-request",
    titleField: "item",
    subtitleField: "status",
    fields: [
      { key: "item", label: "Item" },
      { key: "purchase_order", label: "Purchase Order" },
      { key: "quantity", label: "Quantity" },
      { key: "reason", label: "Reason" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["submitted", "Submitted"],
          ["approved", "Approved"],
          ["shipped", "Shipped"],
          ["received", "Received"],
          ["rejected", "Rejected"],
        ],
      },
      { key: "requested_by", label: "Requested By" },
      { key: "approved_by", label: "Approved By" },
      { key: "refund_amount", label: "Refund Amount" },
    ],
  },
  "stock-adjustment": {
    key: "stock-adjustment",
    icon: CubeIcon,
    label: "Stock Adjustment",
    endpoint: "stock-adjustment",
    titleField: "item",
    fields: [
      { key: "item", label: "Item" },
      { key: "warehouse", label: "Warehouse" },
      {
        key: "adjustment_type",
        label: "Adjustment Type",
        type: "select",
        options: [
          ["addition", "Addition"],
          ["subtraction", "Subtraction"],
          ["correction", "Correction"],
        ],
      },
      { key: "quantity", label: "Quantity" },
      { key: "reason", label: "Reason" },
      { key: "adjusted_by", label: "Adjusted By" },
    ],
  },
  "stock-count-schedule": {
    key: "stock-count-schedule",
    icon: CubeIcon,
    label: "Stock Count Schedule",
    endpoint: "stock-count-schedule",
    titleField: "name",
    subtitleField: "frequency",
    fields: [
      { key: "warehouse", label: "Warehouse" },
      { key: "name", label: "Name" },
      {
        key: "frequency",
        label: "Frequency",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["monthly", "Monthly"],
          ["quarterly", "Quarterly"],
          ["annual", "Annual"],
        ],
      },
      { key: "next_count_date", label: "Next Count Date", type: "date" },
      { key: "last_count_date", label: "Last Count Date", type: "date" },
      { key: "assigned_to", label: "Assigned To" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "stock-level": {
    key: "stock-level",
    icon: CubeIcon,
    label: "Stock Level",
    endpoint: "stock-level",
    titleField: "item",
    fields: [
      { key: "item", label: "Item" },
      { key: "warehouse", label: "Warehouse" },
      { key: "quantity", label: "Quantity" },
      { key: "reserved", label: "Reserved" },
      { key: "available", label: "Available" },
      { key: "reorder_point", label: "Reorder Point" },
      { key: "last_counted", label: "Last Counted" },
    ],
  },
  "stock-movements": {
    key: "stock-movements",
    icon: CubeIcon,
    label: "Stock Movement",
    endpoint: "stock-movements",
    titleField: "item",
    fields: [
      { key: "item", label: "Item" },
      {
        key: "movement_type",
        label: "Movement Type",
        type: "select",
        options: [
          ["purchase", "Purchase"],
          ["issue", "Issue"],
          ["adjustment", "Adjustment"],
          ["return", "Return"],
          ["transfer", "Transfer"],
          ["damage", "Damage"],
        ],
      },
      { key: "quantity", label: "Quantity" },
      { key: "unit_price", label: "Unit Price" },
      { key: "total_amount", label: "Total Amount", type: "number" },
      { key: "reference_number", label: "Reference Number" },
      { key: "reference_type", label: "Reference Type" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "performed_by", label: "Performed By" },
    ],
  },
  "stock-transfer": {
    key: "stock-transfer",
    icon: CubeIcon,
    label: "Stock Transfer",
    endpoint: "stock-transfer",
    titleField: "transfer_number",
    subtitleField: "status",
    fields: [
      { key: "transfer_number", label: "Transfer Number" },
      { key: "source_warehouse", label: "Source Warehouse" },
      { key: "dest_warehouse", label: "Dest Warehouse" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["in_transit", "In Transit"],
          ["received", "Received"],
          ["cancelled", "Cancelled"],
        ],
      },
      { key: "requested_by", label: "Requested By" },
      { key: "approved_by", label: "Approved By" },
      { key: "notes", label: "Notes", type: "textarea" },
      { key: "received_at", label: "Received At", type: "date" },
    ],
  },
  "stock-transfer-item": {
    key: "stock-transfer-item",
    icon: CubeIcon,
    label: "Stock Transfer Item",
    endpoint: "stock-transfer-item",
    titleField: "transfer",
    fields: [
      { key: "transfer", label: "Transfer" },
      { key: "item", label: "Item" },
      { key: "quantity_requested", label: "Quantity Requested" },
      { key: "quantity_sent", label: "Quantity Sent" },
      { key: "quantity_received", label: "Quantity Received" },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  "supplier-rating": {
    key: "supplier-rating",
    icon: CubeIcon,
    label: "Supplier Rating",
    endpoint: "supplier-rating",
    titleField: "supplier",
    fields: [
      { key: "supplier", label: "Supplier" },
      { key: "quality_rating", label: "Quality Rating" },
      { key: "delivery_rating", label: "Delivery Rating" },
      { key: "price_rating", label: "Price Rating" },
      { key: "overall_rating", label: "Overall Rating" },
      { key: "comments", label: "Comments" },
      { key: "rated_by", label: "Rated By" },
    ],
  },
  suppliers: {
    key: "suppliers",
    icon: CubeIcon,
    label: "Supplier",
    endpoint: "suppliers",
    titleField: "name",
    subtitleField: "status",
    fields: [
      { key: "name", label: "Name" },
      { key: "contact_person", label: "Contact Person" },
      { key: "email", label: "Email" },
      { key: "phone", label: "Phone" },
      { key: "address", label: "Address" },
      { key: "tax_id", label: "Tax Id" },
      { key: "payment_terms", label: "Payment Terms" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["active", "Active"],
          ["inactive", "Inactive"],
          ["discontinued", "Discontinued"],
        ],
      },
      { key: "notes", label: "Notes", type: "textarea" },
    ],
  },
  warehouse: {
    key: "warehouse",
    icon: CubeIcon,
    label: "Warehouse",
    endpoint: "warehouse",
    titleField: "name",
    fields: [
      { key: "name", label: "Name" },
      { key: "code", label: "Code" },
      { key: "address", label: "Address" },
      { key: "capacity", label: "Capacity" },
      { key: "manager", label: "Manager" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "warehouse-location": {
    key: "warehouse-location",
    icon: CubeIcon,
    label: "Warehouse Location",
    endpoint: "warehouse-location",
    titleField: "zone",
    fields: [
      { key: "zone", label: "Zone" },
      { key: "aisle", label: "Aisle" },
      { key: "shelf", label: "Shelf" },
      { key: "bin_label", label: "Bin Label" },
      { key: "item", label: "Item" },
      { key: "max_capacity", label: "Max Capacity" },
      { key: "current_quantity", label: "Current Quantity" },
    ],
  },
  "warehouse-zone": {
    key: "warehouse-zone",
    icon: CubeIcon,
    label: "Warehouse Zone",
    endpoint: "warehouse-zone",
    titleField: "name",
    fields: [
      { key: "warehouse", label: "Warehouse" },
      { key: "name", label: "Name" },
      {
        key: "zone_type",
        label: "Zone Type",
        type: "select",
        options: [
          ["storage", "Storage"],
          ["shipping", "Shipping"],
          ["receiving", "Receiving"],
          ["staging", "Staging"],
        ],
      },
      { key: "capacity", label: "Capacity" },
      { key: "is_active", label: "Is Active", type: "bool" },
    ],
  },
  "warranty-claim-extended": {
    key: "warranty-claim-extended",
    icon: CubeIcon,
    label: "Warranty Claim Extended",
    endpoint: "warranty-claim-extended",
    titleField: "item",
    subtitleField: "status",
    fields: [
      { key: "item", label: "Item" },
      { key: "claim_number", label: "Claim Number" },
      { key: "issue_description", label: "Issue Description" },
      { key: "date_filed", label: "Date Filed" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["filed", "Filed"],
          ["in_progress", "In Progress"],
          ["resolved", "Resolved"],
          ["denied", "Denied"],
        ],
      },
      { key: "resolution_notes", label: "Resolution Notes" },
    ],
  },

  // ===== inventory_map =====
};

const TABS = Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({
  key,
  label: cfg.label,
  icon: CubeIcon,
}));

export default function InventoryCenterPage() {
  useTitle("Inventory Center");
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
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Inventory Center</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            Items, warehouses, stock, transfers, purchases, suppliers, catalogs, leases and
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
            leftIcon={<CubeIcon className="h-4 w-4" />}
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
        basePath="/inventory"
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
