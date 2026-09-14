"""Generate the four center pages: config bodies + a shared shell template."""

import json
import re

MODULES = {
    "transportation": {
        "title": "Transportation Center",
        "desc": "Vehicles, drivers, routes, stops, tracking, GPS, geofences, fees, incidents, maintenance and analytics",
        "icon": "TruckIcon",
        "component": "TransportationCenterPage",
    },
    "hostel": {
        "title": "Hostel Center",
        "desc": "Hostels, rooms, allocations, mess, visitors, events, assets, emergencies, inspections and wellness",
        "icon": "BuildingOffice2Icon",
        "component": "HostelCenterPage",
    },
    "gradebook": {
        "title": "Gradebook Center",
        "desc": "Exams, grades, rubrics, standards, transcripts, report cards, history and analytics",
        "icon": "AcademicCapIcon",
        "component": "GradebookCenterPage",
    },
    "hr": {
        "title": "HR Center",
        "desc": "Employees, payroll, leave, performance, recruitment, time tracking, benefits, training and compliance",
        "icon": "UsersIcon",
        "component": "HRCenterPage",
    },
    "reporting": {
        "title": "Reporting Center",
        "desc": "Dashboards, custom reports, KPIs, schedules, exports, insights and analytics",
        "icon": "ChartBarIcon",
        "component": "ReportingCenterPage",
    },
    "conferences": {
        "title": "Conferences Center",
        "desc": "Slots, bookings, availability, locations, approvals, surveys, no-shows and analytics",
        "icon": "VideoCameraIcon",
        "component": "ConferencesCenterPage",
    },
    "auth": {
        "title": "Access & Security Center",
        "desc": "Sessions, devices, roles, policies, API keys, webhooks, SSO, compliance and audit",
        "icon": "ShieldCheckIcon",
        "component": "AuthCenterPage",
    },
    "fees": {
        "title": "Finance Center",
        "desc": "Invoices, payments, budgets, expenses, refunds, reconciliations, templates and audits",
        "icon": "BanknotesIcon",
        "component": "FeesCenterPage",
    },
    "inventory": {
        "title": "Inventory Center",
        "desc": "Items, warehouses, stock, transfers, purchases, suppliers, catalogs, leases and analytics",
        "icon": "CubeIcon",
        "component": "InventoryCenterPage",
    },
    "admissions": {
        "title": "Admissions Center",
        "desc": "Applications, intakes, decisions, documents, interviews, scholarships, waitlists and analytics",
        "icon": "DocumentTextIcon",
        "component": "AdmissionsCenterPage",
    },
    "attendance": {
        "title": "Attendance Center",
        "desc": "Records, period attendance, leaves, tardies, corrections, biometric, GPS, analytics and alerts",
        "icon": "ClipboardDocumentCheckIcon",
        "component": "AttendanceCenterPage",
    },
}

SHELL = """/**
 * {title} — full-surface admin page for the {mod} module.
 *
 * {n} entity tabs (config-driven via EntitySection). {desc}.
 */
import React, {{ useState, useEffect, useRef }} from "react";
import {{
  KeyboardShortcutHelp,
  useShortcutHelp,
}} from "../../components/common/KeyboardShortcutHelp";
import {{ EntitySection, type EntityConfig }} from "../../components/common/EntitySection";
import {{ Button }} from "../../components/common";
import {{ useTitle }} from "../../hooks";
import {{ MagnifyingGlassIcon, {icon} }} from "@heroicons/react/24/outline";

{configs}

const TABS = Object.entries(ENTITY_CONFIGS).map(([key, cfg]) => ({{
  key,
  label: cfg.label,
  icon: {icon},
}}));

export default function {component}() {{
  useTitle("{title}");
  useShortcutHelp();
  const [activeTab, setActiveTab] = useState(TABS[0]?.key ?? "");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const [helpOpen, setHelpOpen] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);
  const actionRef = useRef<{{ add?: () => void; export?: () => void }}>({{}});

  useEffect(() => {{
    setPage(1);
  }}, [activeTab]);

  useEffect(() => {{
    const handler = (e: KeyboardEvent) => {{
      const target = e.target as HTMLElement;
      if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {{
        return;
      }}
      if (e.key === "/") {{
        e.preventDefault();
        searchRef.current?.focus();
      }} else if (e.key.toLowerCase() === "n") {{
        e.preventDefault();
        actionRef.current.add?.();
      }} else if (e.key.toLowerCase() === "e") {{
        e.preventDefault();
        actionRef.current.export?.();
      }} else if (e.key.toLowerCase() === "p") {{
        e.preventDefault();
        setViewMode((v) => (v === "pagination" ? "infinite" : "pagination"));
      }}
    }};
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }}, []);

  const activeCfg = ENTITY_CONFIGS[activeTab];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{title}</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            {desc}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              ref={{searchRef}}
              type="search"
              value={{search}}
              onChange={{(e) => {{
                setSearch(e.target.value);
                setPage(1);
              }}}}
              placeholder="Search…  ( / )"
              className="w-56 rounded-xl border border-slate-200 bg-white px-4 py-2 pl-9 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
          </div>
          <div className="flex items-center gap-1 rounded-xl border border-slate-200 p-1 dark:border-slate-600">
            <button
              onClick={{() => setViewMode("pagination")}}
              className={{`rounded-lg px-3 py-1.5 text-xs font-medium transition ${{
                viewMode === "pagination"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                  : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700"
              }}`}}
            >
              Paginated
            </button>
            <button
              onClick={{() => setViewMode("infinite")}}
              className={{`rounded-lg px-3 py-1.5 text-xs font-medium transition ${{
                viewMode === "infinite"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                  : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700"
              }}`}}
            >
              Infinite
            </button>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={{() => setHelpOpen(true)}}
            leftIcon={{<{icon} className="h-4 w-4" />}}
          >
            Shortcuts
          </Button>
        </div>
      </div>

      {{/* Tab bar */}}
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {{TABS.map((t) => (
          <button
            key={{t.key}}
            onClick={{() => setActiveTab(t.key)}}
            className={{`flex shrink-0 items-center gap-1.5 rounded-xl px-3.5 py-2 text-sm font-medium transition ${{
              activeTab === t.key
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-white text-slate-600 hover:bg-slate-50 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            }}`}}
          >
            <t.icon className="h-4 w-4" />
            {{t.label}}
          </button>
        ))}}
      </div>

      <EntitySection
        cfg={{activeCfg}}
        basePath="/{mod}"
        search={{search}}
        page={{page}}
        setPage={{setPage}}
        viewMode={{viewMode}}
        registerActions={{(h) => {{
          actionRef.current = h;
        }}}}
      />

      <KeyboardShortcutHelp
        open={{helpOpen}}
        onClose={{() => setHelpOpen(false)}}
        shortcuts={{[
          {{ keys: ["N"], label: "New", description: "New record" }},
          {{ keys: ["/"], label: "Search", description: "Focus search" }},
          {{ keys: ["E"], label: "Export", description: "Export CSV" }},
          {{
            keys: ["P"],
            label: "Pages",
            description: "Toggle pagination / infinite scroll",
          }},
        ]}}
      />
    </div>
  );
}}
"""

import sys

for mod, meta in MODULES.items():
    if len(sys.argv) > 1 and mod not in sys.argv[1:]:
        continue
    body = open(f"scripts/ui_configs_{mod}.txt", encoding="utf-8").read().strip()
    # normalize: first entry brace lost its indentation from strip()
    if body.startswith("{"):
        body = "  " + body
    # convert array-style entries to Record entries:  {\n    key: "x", ->  "x": {\n    key: "x",
    body = re.sub(r'^  \{\n    key: "([\w-]+)",', r'  "\1": {\n    key: "\1",', body, flags=re.M)
    # inject icon after each key line
    body = re.sub(r'(  "[\w-]+": \{\n    key: "[\w-]+",)', r"\1\n    icon: " + meta["icon"] + ",", body)
    # count tabs
    n = body.count("key:")
    configs = f"const ENTITY_CONFIGS: Record<string, EntityConfig> = {{\n{body}\n}};"
    page = SHELL.format(
        mod=mod,
        title=meta["title"],
        desc=meta["desc"],
        icon=meta["icon"],
        component=meta["component"],
        configs=configs,
        n=n,
    )
    out = f"../frontend/web/src/pages/admin/{meta['component']}.tsx"
    open(out, "w", encoding="utf-8", newline="\n").write(page)
    print(meta["component"], n, "tabs")
