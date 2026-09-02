import { useEffect, useCallback } from "react";

interface KeyboardShortcutHandlers {
  /** Open create/new form */
  onCreate?: () => void;
  /** Focus the search input */
  onSearch?: () => void;
  /** Export data to CSV */
  onExport?: () => void;
  /** Close open modal or clear selection */
  onEscape?: () => void;
  /** Bulk delete selected items */
  onDelete?: () => void;
  /** Select all items */
  onSelectAll?: () => void;
  /** Toggle reorder mode */
  onToggleReorder?: () => void;
}

/**
 * Reusable keyboard shortcuts hook for list/card pages.
 *
 * Shortcuts:
 *   N         → Open create form
 *   /         → Focus search input
 *   E         → Export CSV
 *   Escape    → Close modal / clear selection
 *   Delete    → Bulk delete (when items selected)
 *   Ctrl+A    → Select all
 *   R         → Toggle reorder mode
 */
export function useKeyboardShortcuts(handlers: KeyboardShortcutHandlers) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Don't trigger shortcuts when typing in inputs
      const target = e.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.tagName === "SELECT" ||
        target.isContentEditable
      ) {
        // Allow Escape in inputs
        if (e.key === "Escape" && handlers.onEscape) {
          handlers.onEscape();
        }
        return;
      }

      // Escape → close/clear
      if (e.key === "Escape" && handlers.onEscape) {
        e.preventDefault();
        handlers.onEscape();
        return;
      }

      // Ctrl+A → select all
      if (e.key === "a" && (e.ctrlKey || e.metaKey) && handlers.onSelectAll) {
        e.preventDefault();
        handlers.onSelectAll();
        return;
      }

      // N → new/create
      if (e.key === "n" && !e.ctrlKey && !e.metaKey && handlers.onCreate) {
        e.preventDefault();
        handlers.onCreate();
        return;
      }

      // / → focus search
      if (e.key === "/" && !e.ctrlKey && !e.metaKey && handlers.onSearch) {
        e.preventDefault();
        handlers.onSearch();
        return;
      }

      // E → export
      if (e.key === "e" && !e.ctrlKey && !e.metaKey && handlers.onExport) {
        e.preventDefault();
        handlers.onExport();
        return;
      }

      // Delete → bulk delete
      if (e.key === "Delete" && handlers.onDelete) {
        e.preventDefault();
        handlers.onDelete();
        return;
      }

      // R → toggle reorder
      if (e.key === "r" && !e.ctrlKey && !e.metaKey && handlers.onToggleReorder) {
        e.preventDefault();
        handlers.onToggleReorder();
        return;
      }
    },
    [handlers],
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);
}
