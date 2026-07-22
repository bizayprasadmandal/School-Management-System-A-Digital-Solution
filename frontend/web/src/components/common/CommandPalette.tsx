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

const HIGHLIGHT: Record<AccentColor, { bg: string; text: string; icon: string }> = {
  indigo: {
    bg: "bg-indigo-50 dark:bg-indigo-900/20",
    text: "text-indigo-700 dark:text-indigo-300",
    icon: "text-indigo-500",
  },
  emerald: {
    bg: "bg-emerald-50 dark:bg-emerald-900/20",
    text: "text-emerald-700 dark:text-emerald-300",
    icon: "text-emerald-500",
  },
  blue: {
    bg: "bg-blue-50 dark:bg-blue-900/20",
    text: "text-blue-700 dark:text-blue-300",
    icon: "text-blue-500",
  },
  amber: {
    bg: "bg-amber-50 dark:bg-amber-900/20",
    text: "text-amber-700 dark:text-amber-300",
    icon: "text-amber-500",
  },
  teal: {
    bg: "bg-teal-50 dark:bg-teal-900/20",
    text: "text-teal-700 dark:text-teal-300",
    icon: "text-teal-500",
  },
  pink: {
    bg: "bg-pink-50 dark:bg-pink-900/20",
    text: "text-pink-700 dark:text-pink-300",
    icon: "text-pink-500",
  },
  violet: {
    bg: "bg-violet-50 dark:bg-violet-900/20",
    text: "text-violet-700 dark:text-violet-300",
    icon: "text-violet-500",
  },
};

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
      // Short timeout to let the DOM render the input first
      const id = setTimeout(() => inputRef.current?.focus(), 30);
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

  return (
    <>
      {/* ── Trigger button ─────────────────────────────────────────────── */}
      <button
        onClick={() => {
          setOpen(true);
          setQuery("");
          setSelectedIndex(0);
        }}
        title="Search pages (Ctrl+K)"
        className="rounded-lg p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white transition-all duration-200"
      >
        <MagnifyingGlassIcon className="h-5 w-5" />
      </button>

      {/* ── Overlay ────────────────────────────────────────────────────── */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={handleClose}
          />

          {/* Dialog */}
          <div
            className={clsx(
              "relative w-full max-w-lg bg-white dark:bg-slate-800 rounded-2xl shadow-2xl",
              "border border-slate-200 dark:border-slate-700 overflow-hidden",
              "animate-in fade-in slide-in-from-top-2 duration-200"
            )}
          >
            {/* Search row */}
            <div className="flex items-center gap-3 px-4 border-b border-slate-200 dark:border-slate-700">
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
                className="w-full py-4 text-sm bg-transparent text-slate-900 dark:text-slate-100 placeholder:text-slate-400 outline-none border-none"
              />
              <kbd className="hidden sm:inline-flex items-center gap-0.5 rounded-md border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 px-1.5 py-0.5 text-[10px] font-medium text-slate-400 dark:text-slate-500">
                ESC
              </kbd>
            </div>

            {/* Results */}
            <div className="max-h-80 overflow-y-auto p-2">
              {filtered.length === 0 ? (
                <p className="text-center py-8 text-sm text-slate-400">
                  No pages found
                </p>
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
                            "w-full flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-left transition-colors",
                            isSelected
                              ? clsx(hl.bg, hl.text)
                              : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50"
                          )}
                        >
                          <Icon
                            className={clsx(
                              "h-4 w-4 flex-shrink-0",
                              isSelected ? hl.icon : "text-slate-400"
                            )}
                          />
                          <span>{item.label}</span>
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
