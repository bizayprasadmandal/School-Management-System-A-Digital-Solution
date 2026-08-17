/**
 * SidebarNav — renders sidebar navigation as collapsible module groups.
 * Each module header toggles its sub-module links open/closed.
 * The module containing the active route auto-expands on navigation.
 */

import React, { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { ChevronDownIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";

export interface SidebarNavItem {
  label: string;
  to: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

export interface SidebarNavGroup {
  title: string;
  icon?: React.ComponentType<{ className?: string }>;
  items: SidebarNavItem[];
}

export type SidebarNavSection = SidebarNavItem | SidebarNavGroup;

interface SidebarNavProps {
  sections: SidebarNavSection[];
  /** Called after a link is clicked (e.g. to close the mobile drawer). */
  onNavigate?: () => void;
}

function isGroup(section: SidebarNavSection): section is SidebarNavGroup {
  return "items" in section;
}

export function flattenSections(sections: SidebarNavSection[]): SidebarNavItem[] {
  return sections.flatMap((section) => (isGroup(section) ? section.items : [section]));
}

export default function SidebarNav({ sections, onNavigate }: SidebarNavProps) {
  const { pathname } = useLocation();

  const [openGroups, setOpenGroups] = useState<Set<string>>(() => {
    const initial = new Set<string>();
    for (const section of sections) {
      if (isGroup(section) && section.items.some((item) => pathname.startsWith(item.to))) {
        initial.add(section.title);
      }
    }
    return initial;
  });

  // Auto-expand the module containing the active route.
  useEffect(() => {
    setOpenGroups((prev) => {
      const next = new Set(prev);
      for (const section of sections) {
        if (isGroup(section) && section.items.some((item) => pathname.startsWith(item.to))) {
          next.add(section.title);
        }
      }
      return next;
    });
  }, [pathname, sections]);

  const toggle = (title: string) =>
    setOpenGroups((prev) => {
      const next = new Set(prev);
      if (next.has(title)) {
        next.delete(title);
      } else {
        next.add(title);
      }
      return next;
    });

  const renderLink = (item: SidebarNavItem, compact = false) => {
    const Icon = item.icon;
    return (
      <NavLink
        key={item.to}
        to={item.to}
        end={item.to.split("/").length === 2}
        onClick={onNavigate}
        className={({ isActive }) =>
          clsx(
            "flex items-center gap-3 rounded-lg text-sm font-medium transition-colors",
            compact ? "px-3 py-2" : "px-3 py-2.5",
            isActive
              ? "bg-white/10 text-white"
              : "text-white/60 hover:bg-white/10 hover:text-white",
          )
        }
      >
        <Icon className={clsx("flex-shrink-0", compact ? "h-4 w-4" : "h-5 w-5")} />
        <span className="flex-1 truncate">{item.label}</span>
        {item.badge ? (
          <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-white/20 px-1.5 text-[10px] font-bold text-white">
            {item.badge}
          </span>
        ) : null}
      </NavLink>
    );
  };

  return (
    <div className="space-y-0.5">
      {sections.map((section) =>
        isGroup(section) ? (
          <div key={section.title}>
            <button
              type="button"
              onClick={() => toggle(section.title)}
              aria-expanded={openGroups.has(section.title)}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-white/70 hover:bg-white/10 hover:text-white transition-colors"
            >
              {section.icon ? <section.icon className="h-5 w-5 flex-shrink-0" /> : null}
              <span className="flex-1 truncate text-left">{section.title}</span>
              <ChevronDownIcon
                className={clsx(
                  "h-4 w-4 flex-shrink-0 transition-transform duration-200",
                  openGroups.has(section.title) && "rotate-180",
                )}
              />
            </button>
            {openGroups.has(section.title) && (
              <div className="mt-0.5 ml-4 space-y-0.5 border-l border-white/10 pl-3 pb-0.5">
                {section.items.map((item) => renderLink(item, true))}
              </div>
            )}
          </div>
        ) : (
          renderLink(section)
        ),
      )}
    </div>
  );
}
