import React from "react";
import { TrashIcon, ArrowDownTrayIcon, XMarkIcon } from "@heroicons/react/24/outline";

interface BulkActionBarProps {
  selectedCount: number;
  onClear: () => void;
  onDelete?: () => void;
  onExport?: () => void;
  deleteLabel?: string;
}

/**
 * Floating bulk action bar that appears when items are selected.
 * Shows count, delete, export, and clear buttons.
 */
export function BulkActionBar({
  selectedCount,
  onClear,
  onDelete,
  onExport,
  deleteLabel = "Delete selected",
}: BulkActionBarProps) {
  if (selectedCount === 0) return null;

  return (
    <div className="fixed bottom-6 left-1/2 z-50 -translate-x-1/2 animate-slide-up">
      <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-5 py-3 shadow-lg dark:border-slate-700 dark:bg-slate-800">
        <span className="text-sm font-medium text-slate-700 dark:text-slate-200">
          {selectedCount} selected
        </span>

        {onExport && (
          <button
            onClick={onExport}
            className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-1.5 text-sm font-medium text-indigo-700 transition-colors hover:bg-indigo-100 dark:bg-indigo-900/30 dark:text-indigo-400 dark:hover:bg-indigo-900/50"
          >
            <ArrowDownTrayIcon className="h-4 w-4" />
            Export
          </button>
        )}

        {onDelete && (
          <button
            onClick={onDelete}
            className="inline-flex items-center gap-1.5 rounded-lg bg-red-50 px-3 py-1.5 text-sm font-medium text-red-700 transition-colors hover:bg-red-100 dark:bg-red-900/30 dark:text-red-400 dark:hover:bg-red-900/50"
          >
            <TrashIcon className="h-4 w-4" />
            {deleteLabel}
          </button>
        )}

        <button
          onClick={onClear}
          className="ml-1 rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-700 dark:hover:text-slate-300"
        >
          <XMarkIcon className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
