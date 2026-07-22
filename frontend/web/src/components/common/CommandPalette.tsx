/**
 * CommandPalette — Ctrl+K / Cmd+K global quick-jump search.
 * Renders a searchable overlay of navigation items so users can jump
 * to any page from anywhere in the app.
 */

import React, { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface CommandItem {
  label: string;
  to: string;
  icon: React.ComponentType<{ className?: string }>;
}

type AccentColor = "indigo" | "emerald" | "blue" | "amber" | "teal" | "pink" | "violet";

interface CommandPaletteProps {
  items: CommandItem[];
  /** Accent color for the active highlight (matches sidebar theme). */
  accent?: AccentColor;
}

// ─── Color map (avoids Tailwind dynamic class interpolation) ──────────────────

interface HighlightStyle {
  bg: string;
  text: string;
  icon: string;
  border: string;
}

const HIGHLIGHT: Record<AccentColor, HighlightStyle> = {
  indigo: {
    bg: "bg-indigo-50 dark:bg-indigo-900/25",
    text: "text-indigo-700 dark:text-indigo-300",
    icon: "text-indigo-500 dark:text-indigo-400",
    border: "border-l-indigo-500",
  },
  emerald: {
    bg: "bg-emerald-50 dark:bg-emerald-900/25",
    text: "text-emerald-700 dark:text-emerald-300",
    icon: "text-emerald-500 dark:text-emerald-400",
    border: "border-l-emerald-500",
  },
  blue: {
    bg: "bg-blue-50 dark:bg-blue-900/25",
    text: "text-blue-700 dark:text-blue-300",
    icon: "text-blue-500 dark:text-blue-400",
    border: "border-l-blue-500",
  },
  amber: {
    bg: "bg-amber-50 dark:bg-amber-900/25",
    text: "text-amber-700 dark:text-amber-300",
    icon: "text-amber-500 dark:text-amber-400",
    border: "border-l-amber-500",
  },
  teal: {
    bg: "bg-teal-50 dark:bg-teal-900/25",
    text: "text-teal-700 dark:text-teal-300",
    icon: "text-teal-500 dark:text-teal-400",
    border: "border-l-teal-500",
  },
  pink: {
    bg: "bg-pink-50 dark:bg-pink-900/25",
    text: "text-pink-700 dark:text-pink-300",
    icon: "text-pink-500 dark:text-pink-400",
    border: "border-l-pink-500",
  },
  violet: {
    bg: "bg-violet-50 dark:bg-violet-900/25",
    text: "text-violet-700 dark:text-violet-300",
    icon: "text-violet-500 dark:text-violet-400",
    border: "border-l-violet-500",
  },
};

// ─── Icon background map ──────────────────────────────────────────────────────

const ICON_BG: Record<AccentColor, string> = {
  indigo: "bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400",
  emerald: "bg-emerald-100 dark:bg-emerald-900/40 text-emerald-600 dark:text-emerald-400",
  blue: "bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400",
  amber: "bg-amber-100 dark:bg-amber-900/40 text-amber-600 dark:text-amber-400",
  teal: "bg-teal-100 dark:bg-teal-900/40 text-teal-600 dark:text-teal-400",
  pink: "bg-pink-100 dark:bg-pink-900/40 text-pink-600 dark:text-pink-400",
  violet: "bg-violet-100 dark:bg-violet-900/40 text-violet-600 dark:text-violet-400",
};

// ─── Platform detection (computed once, not per render) ─────────────────────

const IS_MAC =
  typeof navigator !== "undefined" &&
  /Mac|iPod|iPhone|iPad/.test(navigator.platform ?? "");

const SHORTCUT_LABEL = IS_MAC ? "⌘K" : "Ctrl+K";
const MODIFIER_LABEL = IS_MAC ? "Cmd" : "Ctrl";

// ─── Component ────────────────────────────────────────────────────────────────

export default function CommandPalette({ items, accent = "indigo" }: CommandPaletteProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);

  // Filter items by label
  const filtered = useMemo(() => {
    if (!query.trim()) return items;
    const q = query.toLowerCase();
    return items.filter((item) => item.label.toLowerCase().includes(q));
  }, [items, query]);

  // Global keyboard shortcut: Ctrl+K / Cmd+K to toggle, Escape to close
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        setOpen(false);
        setQuery("");
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  // Focus input when opening
  useEffect(() => {
    if (open) {
      const id = setTimeout(() => inputRef.current?.focus(), 50);
      return () => clearTimeout(id);
    }
  }, [open]);

  const handleClose = useCallback(() => {
    setOpen(false);
    setQuery("");
  }, []);

  const handleSelect = useCallback(
    (item: CommandItem) => {
      navigate(item.to);
      handleClose();
    },
    [navigate, handleClose]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((i) => Math.min(i + 1, filtered.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter" && filtered[selectedIndex]) {
        e.preventDefault();
        handleSelect(filtered[selectedIndex]);
      }
    },
    [filtered, selectedIndex, handleSelect]
  );

  const hl = HIGHLIGHT[accent] ?? HIGHLIGHT.indigo;
  const iBg = ICON_BG[accent] ?? ICON_BG.indigo;

  return (
    <>
      {/* ── Trigger button ─────────────────────────────────────────────── */}
      <button
        onClick={() => {
          setOpen(true);
          setQuery("");
          setSelectedIndex(0);
        }}
        title={`Search pages (${MODIFIER_LABEL}+K)`}
        className={clsx(
          "flex items-center gap-1.5 rounded-lg px-2 py-2",
          "text-slate-500 dark:text-slate-400",
          "hover:bg-slate-100 dark:hover:bg-slate-700",
          "hover:text-slate-900 dark:hover:text-white",
          "transition-all duration-200",
          "group"
        )}
      >
        <MagnifyingGlassIcon className="h-5 w-5" />
        {/* Always-visible keyboard shortcut badge */}
        <kbd
          aria-hidden="true"
          className={clsx(
            "hidden sm:inline-flex items-center rounded-md",
            "border border-slate-300 dark:border-slate-600",
            "bg-slate-100 dark:bg-slate-700",
            "px-1.5 py-0.5 text-[10px] font-medium leading-none",
            "text-slate-400 dark:text-slate-500",
            "transition-colors duration-200",
            "group-hover:border-slate-400 dark:group-hover:border-slate-500",
            "group-hover:text-slate-500 dark:group-hover:text-slate-400"
          )}
        >
          {SHORTCUT_LABEL}
        </kbd>
      </button>

      {/* ── Overlay ────────────────────────────────────────────────────── */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[12vh] sm:pt-[15vh]">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-in fade-in duration-150"
            onClick={handleClose}
          />

          {/* Dialog */}
          <div
            className={clsx(
              "relative w-[95vw] max-w-lg",
              "bg-white dark:bg-slate-800",
              "rounded-2xl shadow-2xl shadow-black/10 dark:shadow-black/40",
              "border border-slate-200 dark:border-slate-700",
              "overflow-hidden",
              "animate-in fade-in zoom-in-95 slide-in-from-top-3 duration-200 ease-out"
            )}
          >
            {/* Gradient top accent bar */}
            <div
              className={clsx(
                "h-1 w-full",
                accent === "indigo" && "bg-gradient-to-r from-indigo-500 to-indigo-400",
                accent === "emerald" && "bg-gradient-to-r from-emerald-500 to-emerald-400",
                accent === "blue" && "bg-gradient-to-r from-blue-500 to-blue-400",
                accent === "amber" && "bg-gradient-to-r from-amber-500 to-amber-400",
                accent === "teal" && "bg-gradient-to-r from-teal-500 to-teal-400",
                accent === "pink" && "bg-gradient-to-r from-pink-500 to-pink-400",
                accent === "violet" && "bg-gradient-to-r from-violet-500 to-violet-400"
              )}
            />

            {/* Search row */}
            <div className="flex items-center gap-3 px-4 border-b border-slate-100 dark:border-slate-700/70">
              <MagnifyingGlassIcon className="h-5 w-5 text-slate-400 flex-shrink-0" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setSelectedIndex(0);
                }}
                onKeyDown={handleKeyDown}
                placeholder="Search pages…"
                className="w-full py-3.5 text-sm bg-transparent text-slate-900 dark:text-slate-100 placeholder:text-slate-400 outline-none border-none"
              />

              {/* Item count badge */}
              {query.trim() && (
                <span className="hidden sm:inline-flex items-center rounded-full bg-slate-100 dark:bg-slate-700 px-2 py-0.5 text-[10px] font-medium text-slate-500 dark:text-slate-400 tabular-nums">
                  {filtered.length} / {items.length}
                </span>
              )}

              {/* ESC badge */}
              <kbd className="hidden sm:inline-flex items-center gap-0.5 rounded-md border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 px-1.5 py-0.5 text-[10px] font-medium text-slate-400 dark:text-slate-500">
                ESC
              </kbd>
            </div>

            {/* Results */}
            <div className="max-h-72 overflow-y-auto p-2">
              {filtered.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-10 text-center">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-700 mb-3">
                    <MagnifyingGlassIcon className="h-5 w-5 text-slate-400" />
                  </div>
                  <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                    No pages found
                  </p>
                  <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
                    Try a different search term
                  </p>
                </div>
              ) : (
                <ul className="space-y-0.5" role="listbox">
                  {filtered.map((item, index) => {
                    const Icon = item.icon;
                    const isSelected = index === selectedIndex;
                    return (
                      <li key={item.to} role="option" aria-selected={isSelected}>
                        <button
                          onClick={() => handleSelect(item)}
                          onMouseEnter={() => setSelectedIndex(index)}
                          className={clsx(
                            "w-full flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-left transition-all duration-150",
                            "border-l-2",
                            isSelected
                              ? clsx(hl.bg, hl.text, hl.border, "shadow-sm")
                              : "border-l-transparent text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50 hover:border-l-slate-200 dark:hover:border-l-slate-600"
                          )}
                        >
                          {/* Icon container */}
                          <span
                            className={clsx(
                              "flex h-7 w-7 items-center justify-center rounded-lg flex-shrink-0 transition-colors duration-150",
                              isSelected ? iBg : "bg-slate-100 dark:bg-slate-700 text-slate-400 dark:text-slate-500"
                            )}
                          >
                            <Icon className="h-3.5 w-3.5" />
                          </span>

                          <span className="flex-1 truncate">{item.label}</span>

                          {/* Arrow indicator on hover/selected */}
                          <span
                            className={clsx(
                              "flex-shrink-0 transition-all duration-150",
                              isSelected
                                ? "opacity-100 translate-x-0"
                                : "opacity-0 -translate-x-1"
                            )}
                          >
                            <svg
                              className={clsx("h-3.5 w-3.5", hl.icon)}
                              fill="none"
                              viewBox="0 0 24 24"
                              strokeWidth={2}
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"
                              />
                            </svg>
                          </span>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>

            {/* Footer hints */}
            <div className="flex items-center gap-4 border-t border-slate-100 dark:border-slate-700/70 px-4 py-2 bg-slate-50/50 dark:bg-slate-800/50">
              <div className="flex items-center gap-1.5 text-[10px] text-slate-400 dark:text-slate-500">
                <kbd className="inline-flex items-center rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-1 py-0 text-[9px] font-medium">
                  ↑
                </kbd>
                <kbd className="inline-flex items-center rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-1 py-0 text-[9px] font-medium">
                  ↓
                </kbd>
                <span>navigate</span>
              </div>
              <div className="flex items-center gap-1.5 text-[10px] text-slate-400 dark:text-slate-500">
                <kbd className="inline-flex items-center rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-1 py-0 text-[9px] font-medium">
                  ↵
                </kbd>
                <span>select</span>
              </div>
              <div className="flex items-center gap-1.5 text-[10px] text-slate-400 dark:text-slate-500">
                <kbd className="inline-flex items-center rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 px-1 py-0 text-[9px] font-medium">
                  esc
                </kbd>
                <span>close</span>
              </div>
              <div className="flex-1" />
              <span className="text-[10px] text-slate-400 dark:text-slate-500">
                {SHORTCUT_LABEL} to open
              </span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
