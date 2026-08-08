/**
 * ImportCsvModal — Reusable modal for CSV file import.
 * Supports file upload (drag & drop or click) and manual paste.
 * Uses the existing POST endpoint for CSV import.
 */

import React, { useState, useRef, useCallback } from "react";
import {
  ArrowUpTrayIcon,
  DocumentTextIcon,
  XMarkIcon,
  ClipboardDocumentIcon,
} from "@heroicons/react/24/outline";
import { Modal, Button } from "./";
import { api } from "../../api/client";
import toast from "react-hot-toast";
import { useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";

interface ImportCsvModalProps {
  open: boolean;
  onClose: () => void;
  endpoint: string;
  invalidateQueries?: string[][];
  /** Optional helper text shown below the upload area */
  helpText?: string;
}

export default function ImportCsvModal({
  open,
  onClose,
  endpoint,
  invalidateQueries,
  helpText,
}: ImportCsvModalProps) {
  const qc = useQueryClient();
  const [csvText, setCsvText] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [mode, setMode] = useState<"upload" | "paste">("upload");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isPending, setIsPending] = useState(false);
  const [results, setResults] = useState<{
    imported: number;
    errors: string[];
    generated_passwords?: Record<string, string>;
  } | null>(null);

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) readFile(file);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) readFile(file);
  };

  const readFile = (file: File) => {
    setFileName(file.name);
    setResults(null);
    const reader = new FileReader();
    reader.onload = (ev) => setCsvText((ev.target?.result as string) ?? "");
    reader.readAsText(file);
  };

  const handleSubmit = async () => {
    if (!csvText.trim()) return;
    setIsPending(true);
    setResults(null);
    try {
      const res = await api.post<{
        imported: number;
        errors: string[];
        generated_passwords?: Record<string, string>;
      }>(endpoint, { csv_data: csvText });
      setResults(res);
      if (res.errors && res.errors.length > 0) {
        toast.error(`Imported ${res.imported} records with ${res.errors.length} errors`);
      } else {
        toast.success(`Successfully imported ${res.imported} records!`);
      }
      if (invalidateQueries) {
        invalidateQueries.forEach((qk) => qc.invalidateQueries({ queryKey: qk }));
      }
    } catch (err: any) {
      toast.error(err?.detail || err?.message || "Import failed");
    } finally {
      setIsPending(false);
    }
  };

  const reset = () => {
    setCsvText("");
    setFileName(null);
    setResults(null);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Import CSV"
      description="Upload a CSV file or paste the data directly"
      size="lg"
      footer={
        results ? (
          <Button onClick={handleClose}>Done</Button>
        ) : (
          <>
            <Button variant="secondary" onClick={handleClose}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} loading={isPending} disabled={!csvText.trim()}>
              Import Data
            </Button>
          </>
        )
      }
    >
      <div className="space-y-4">
        {/* Results summary */}
        {results && (
          <div
            className={clsx(
              "rounded-xl border p-4 space-y-2",
              results.errors.length > 0
                ? "bg-amber-50 border-amber-200"
                : "bg-green-50 border-green-200",
            )}
          >
            <p className="text-sm font-semibold text-slate-800">
              {results.imported} records imported successfully
            </p>
            {results.errors.length > 0 && (
              <div className="space-y-1">
                <p className="text-xs font-medium text-red-700">{results.errors.length} errors:</p>
                <ul className="text-xs text-red-600 max-h-32 overflow-y-auto space-y-0.5 list-disc list-inside">
                  {results.errors.map((err, i) => (
                    <li key={i}>{err}</li>
                  ))}
                </ul>
              </div>
            )}
            {results.generated_passwords && Object.keys(results.generated_passwords).length > 0 && (
              <div className="rounded-lg border border-indigo-100 bg-indigo-50 p-3">
                <p className="text-xs font-medium text-indigo-700 mb-1.5">
                  Auto-generated passwords — share these with students:
                </p>
                <div className="max-h-40 overflow-y-auto space-y-1">
                  {Object.entries(results.generated_passwords).map(([email, pw]) => (
                    <p key={email} className="text-xs font-mono text-indigo-600 break-all">
                      <span className="font-semibold">{email}</span>: {pw}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Mode toggle */}
        {!results && (
          <div className="flex gap-2">
            <button
              onClick={() => setMode("upload")}
              className={clsx(
                "flex-1 rounded-lg py-2 text-sm font-medium transition-colors",
                mode === "upload"
                  ? "bg-indigo-100 text-indigo-700"
                  : "bg-slate-100 text-slate-500 hover:bg-slate-200",
              )}
            >
              Upload File
            </button>
            <button
              onClick={() => setMode("paste")}
              className={clsx(
                "flex-1 rounded-lg py-2 text-sm font-medium transition-colors",
                mode === "paste"
                  ? "bg-indigo-100 text-indigo-700"
                  : "bg-slate-100 text-slate-500 hover:bg-slate-200",
              )}
            >
              Paste Data
            </button>
          </div>
        )}

        {/* Upload area */}
        {!results && mode === "upload" && (
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleFileDrop}
            onClick={() => fileInputRef.current?.click()}
            className={clsx(
              "relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 cursor-pointer transition-colors",
              isDragging
                ? "border-indigo-500 bg-indigo-50"
                : "border-slate-200 hover:border-indigo-300 hover:bg-slate-50",
            )}
          >
            {fileName ? (
              <>
                <DocumentTextIcon className="h-10 w-10 text-indigo-500 mb-2" />
                <p className="text-sm font-medium text-slate-700">{fileName}</p>
                <p className="text-xs text-slate-400 mt-1">
                  {csvText.length.toLocaleString()} characters
                </p>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    reset();
                  }}
                  className="mt-2 text-xs text-red-500 hover:text-red-700"
                >
                  Remove file
                </button>
              </>
            ) : (
              <>
                <ArrowUpTrayIcon className="h-10 w-10 text-slate-300 mb-2" />
                <p className="text-sm font-medium text-slate-600">
                  Drop CSV file here or click to browse
                </p>
                <p className="text-xs text-slate-400 mt-1">Supports .csv files</p>
              </>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={handleFileSelect}
            />
          </div>
        )}

        {/* Paste area */}
        {!results && mode === "paste" && (
          <div className="space-y-2">
            <div className="relative">
              <textarea
                value={csvText}
                onChange={(e) => setCsvText(e.target.value)}
                placeholder="Paste CSV data here (include header row)..."
                rows={10}
                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-mono text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-400 resize-y"
              />
              {csvText && (
                <button
                  onClick={() => setCsvText("")}
                  className="absolute top-3 right-3 p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              )}
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <ClipboardDocumentIcon className="h-3.5 w-3.5" />
              {csvText ? `${csvText.split("\n").length} lines` : "Paste your CSV data above"}
            </div>
          </div>
        )}

        {/* Help text */}
        {helpText && !results && (
          <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-500 leading-relaxed">
            <p className="font-medium text-slate-700 mb-1">CSV Format:</p>
            <pre className="whitespace-pre-wrap font-mono text-slate-500">{helpText}</pre>
          </div>
        )}
      </div>
    </Modal>
  );
}
