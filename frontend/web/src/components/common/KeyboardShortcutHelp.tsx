import React, { useState, useEffect } from "react";
import { Modal } from "./index";
import { CommandLineIcon } from "@heroicons/react/24/outline";

interface Shortcut {
  keys: string[];
  label: string;
  description: string;
}

const DEFAULT_SHORTCUTS: Shortcut[] = [
  { keys: ["N"], label: "New", description: "Open create form" },
  { keys: ["/"], label: "Search", description: "Focus search input" },
  { keys: ["E"], label: "Export", description: "Export data to CSV" },
  { keys: ["Esc"], label: "Close", description: "Close modal or clear selection" },
  { keys: ["Del"], label: "Delete", description: "Bulk delete selected items" },
  { keys: ["Ctrl", "A"], label: "Select All", description: "Select all visible items" },
  { keys: ["R"], label: "Reorder", description: "Toggle reorder mode" },
  { keys: ["?"], label: "Help", description: "Show this shortcut help" },
];

interface KeyboardShortcutHelpProps {
  open: boolean;
  onClose: () => void;
  shortcuts?: Shortcut[];
}

function ShortcutKeys({ keys }: { keys: string[] }) {
  return (
    <div className="flex items-center gap-1">
      {keys.map((key, i) => (
        <React.Fragment key={key}>
          {i > 0 && <span className="text-slate-400 text-xs">+</span>}
          <kbd className="inline-flex items-center justify-center min-w-[28px] h-7 rounded-md border border-slate-300 bg-slate-100 px-1.5 text-xs font-medium text-slate-700 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300">
            {key}
          </kbd>
        </React.Fragment>
      ))}
    </div>
  );
}

export function KeyboardShortcutHelp({
  open,
  onClose,
  shortcuts = DEFAULT_SHORTCUTS,
}: KeyboardShortcutHelpProps) {
  // Also register ? key to open this modal
  useEffect(() => {
    if (!open) {
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
        if (e.key === "?") {
          e.preventDefault();
          // We can't call onClose from here since we don't control open state
          // The parent component should register this
        }
      };
      document.addEventListener("keydown", handler);
      return () => document.removeEventListener("keydown", handler);
    }
  }, [open]);

  return (
    <Modal open={open} onClose={onClose} title="Keyboard Shortcuts">
      <div className="space-y-1">
        {shortcuts.map((shortcut) => (
          <div
            key={shortcut.label}
            className="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-slate-50 dark:hover:bg-slate-700/50"
          >
            <div className="flex items-center gap-3">
              <ShortcutKeys keys={shortcut.keys} />
              <span className="text-sm font-medium text-slate-700 dark:text-slate-200">
                {shortcut.label}
              </span>
            </div>
            <span className="text-sm text-slate-500 dark:text-slate-400">
              {shortcut.description}
            </span>
          </div>
        ))}
      </div>
      <p className="mt-4 text-center text-xs text-slate-400 dark:text-slate-500">
        Press{" "}
        <kbd className="rounded border border-slate-300 bg-slate-100 px-1 py-0.5 text-xs dark:border-slate-600 dark:bg-slate-800">
          ?
        </kbd>{" "}
        to toggle this panel
      </p>
    </Modal>
  );
}

/**
 * Hook to manage keyboard shortcut help modal state.
 * Registers the ? key to toggle the modal.
 */
export function useShortcutHelp() {
  const [open, setOpen] = useState(false);

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
      if (e.key === "?") {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
      if (e.key === "Escape" && open) {
        e.preventDefault();
        setOpen(false);
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [open]);

  return { open, setOpen };
}
