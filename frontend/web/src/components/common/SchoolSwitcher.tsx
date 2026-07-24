/**
 * SchoolSwitcher — Dropdown for super admin to switch between schools.
 *
 * Shows a searchable list of all schools. Selecting one sets it as the
 * active school context, which causes all subsequent API requests to
 * send the X-School-ID header, scoping all data to that school.
 */

import React, { useState, useRef, useEffect, useCallback } from "react";
import {
  BuildingOffice2Icon,
  CheckIcon,
  MagnifyingGlassIcon,
  ChevronDownIcon,
} from "@heroicons/react/24/outline";
import { usePlatformSchools } from "../../api/hooks";
import { useSchoolContextStore } from "../../store/schoolContextStore";

export default function SchoolSwitcher() {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const activeSchool = useSchoolContextStore((s) => s.activeSchool);
  const setActiveSchool = useSchoolContextStore((s) => s.setActiveSchool);

  const { data } = usePlatformSchools({ search: search || undefined });

  const schools = data?.results || [];

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Focus search input when opening
  useEffect(() => {
    if (open && inputRef.current) {
      inputRef.current.focus();
    }
  }, [open]);

  const handleSelect = useCallback(
    (school: { id: string; name: string; code: string; subdomain: string }) => {
      // If it's already selected, deselect (back to global context)
      if (activeSchool?.id === school.id) {
        setActiveSchool(null);
      } else {
        setActiveSchool({
          id: school.id,
          name: school.name,
          code: school.code,
          subdomain: school.subdomain,
        });
      }
      setOpen(false);
      setSearch("");
    },
    [activeSchool, setActiveSchool]
  );

  const handleClear = useCallback(() => {
    setActiveSchool(null);
    setOpen(false);
    setSearch("");
  }, [setActiveSchool]);

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger button */}
      <button
        onClick={() => setOpen(!open)}
        className={`inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-medium transition-all duration-200 ${
          activeSchool
            ? "border-emerald-400 bg-emerald-50 text-emerald-700 shadow-[0_0_0_1px_#34d399] dark:border-emerald-600 dark:bg-emerald-900/25 dark:text-emerald-300 dark:shadow-[0_0_0_1px_#059669]"
            : "border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700"
        }`}
        title={activeSchool ? `Managing: ${activeSchool.name}` : "All Schools (Global)"}
      >
        {/* Colored indicator dot — always visible when context is active */}
        {activeSchool && (
          <span className="relative flex h-2.5 w-2.5 flex-shrink-0">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
          </span>
        )}
        <BuildingOffice2Icon className={`h-4 w-4 flex-shrink-0 ${activeSchool ? "text-emerald-600 dark:text-emerald-400" : ""}`} />
        <span className="hidden sm:inline max-w-[140px] truncate">
          {activeSchool ? activeSchool.name : "All Schools"}
        </span>
        <ChevronDownIcon className="h-3.5 w-3.5 flex-shrink-0 text-slate-400" />
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute right-0 mt-2 w-72 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 shadow-xl z-50 overflow-hidden">
          {/* Search */}
          <div className="relative border-b border-slate-200 dark:border-slate-700">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              ref={inputRef}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search schools..."
              className="w-full bg-transparent pl-9 pr-4 py-3 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none"
            />
          </div>

          {/* "All Schools" option */}
          {activeSchool && (
            <button
              onClick={handleClear}
              className="flex w-full items-center gap-3 px-4 py-2.5 text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors text-left border-b border-slate-100 dark:border-slate-700"
            >
              <BuildingOffice2Icon className="h-4 w-4" />
              <span className="font-medium">All Schools (Global)</span>
            </button>
          )}

          {/* Schools list */}
          <div className="max-h-60 overflow-y-auto">
            {schools.length === 0 ? (
              <div className="px-4 py-8 text-center">
                <BuildingOffice2Icon className="mx-auto h-8 w-8 text-slate-300 dark:text-slate-600" />
                <p className="mt-2 text-sm text-slate-400 dark:text-slate-500">
                  {search ? "No schools match your search." : "No schools available."}
                </p>
              </div>
            ) : (
              schools.map((school) => {
                const isSelected = activeSchool?.id === school.id;
                return (
                  <button
                    key={school.id}
                    onClick={() => handleSelect(school)}
                    className={`flex w-full items-center gap-3 px-4 py-2.5 text-sm transition-colors text-left ${
                      isSelected
                        ? "bg-indigo-50 dark:bg-indigo-900/30"
                        : "hover:bg-slate-50 dark:hover:bg-slate-700/50"
                    }`}
                  >
                    <div className="flex h-7 w-7 items-center justify-center rounded-md bg-indigo-100 dark:bg-indigo-900/50 flex-shrink-0">
                      <BuildingOffice2Icon className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-slate-900 dark:text-white truncate">
                        {school.name}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {school.code} · {school.subdomain}
                      </p>
                    </div>
                    {isSelected && (
                      <CheckIcon className="h-4 w-4 flex-shrink-0 text-indigo-600 dark:text-indigo-400" />
                    )}
                  </button>
                );
              })
            )}
          </div>

          {/* Footer hint */}
          <div className="border-t border-slate-200 dark:border-slate-700 px-4 py-2 bg-slate-50 dark:bg-slate-800/50">
            <p className="text-[11px] text-slate-400 dark:text-slate-500">
              {activeSchool
                ? `All data scoped to ${activeSchool.name}`
                : "Viewing all schools (global context)"}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
