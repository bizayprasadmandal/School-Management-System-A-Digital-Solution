/**
 * Setup2FAPage
 *
 * Two-factor authentication setup page with backup codes support.
 * States: idle, loading, setup (QR + backup codes), verifying, enabled, error
 *
 * Users are prompted to save their backup codes during setup. Backup codes
 * can be regenerated from the enabled state.
 */

import React, { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import {
  KeyIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  EyeIcon,
  EyeSlashIcon,
  DocumentArrowDownIcon,
  PrinterIcon,
  ClipboardIcon,
  CheckIcon,
} from "@heroicons/react/24/outline";
import { QRCodeSVG } from "qrcode.react";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { trackEvent } from "../../utils/analytics";
import toast from "react-hot-toast";
import clsx from "clsx";

// ─── Types ────────────────────────────────────────────────────────────────────

type PageState = "idle" | "loading" | "setup" | "verifying" | "enabled" | "error";

interface SetupData {
  secret: string;
  provisioning_uri: string;
  backup_codes?: string[];
}

interface VerifyResponse {
  detail: string;
  backup_codes?: string[];
}

interface RegenerateResponse {
  backup_codes: string[];
  detail: string;
}

// ─── Component ────────────────────────────────────────────────────────────────

export default function Setup2FAPage() {
  const user = useAuthStore((s) => s.user);
  const setUser = useAuthStore((s) => s.setUser);
  const isEnabled = user?.two_factor_enabled ?? false;

  const [state, setState] = useState<PageState>(isEnabled ? "enabled" : "idle");
  const [setupData, setSetupData] = useState<SetupData | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [backupCodesSaved, setBackupCodesSaved] = useState(false);
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [errorMsg, setErrorMsg] = useState("");
  const [showSecret, setShowSecret] = useState(false);
  const [disablePassword, setDisablePassword] = useState("");
  const [disabling, setDisabling] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [codesCopied, setCodesCopied] = useState(false);

  const codeInputRefs = Array.from({ length: 6 }, () => React.createRef<HTMLInputElement>());

  // ── Fetch new secret ──────────────────────────────────────────────────────

  const fetchSetup = useCallback(async () => {
    setState("loading");
    setErrorMsg("");
    setBackupCodesSaved(false);
    try {
      const data = await api.post<SetupData>("/auth/setup-2fa/");
      setSetupData(data);
      setBackupCodes(data.backup_codes ?? []);
      setState("setup");
      trackEvent("2fa_setup_initiated", {});
    } catch (err: unknown) {
      const error = err as { message?: string };
      const msg = error?.message ?? "Failed to initiate 2FA setup.";
      setErrorMsg(msg);
      setState("error");
      toast.error(msg);
    }
  }, []);

  // ── Verify TOTP code ─────────────────────────────────────────────────────

  const handleVerify = useCallback(async () => {
    const fullCode = code.join("");
    if (fullCode.length !== 6) {
      toast.error("Please enter the complete 6-digit code.");
      return;
    }

    setState("verifying");
    setErrorMsg("");
    try {
      const response = await api.post<VerifyResponse>("/auth/verify-2fa/", { code: fullCode });

      // Update local user state
      if (user) {
        setUser({ ...user, two_factor_enabled: true });
      }

      // Backup codes may be returned if they weren't generated during setup
      if (response.backup_codes && response.backup_codes.length > 0) {
        setBackupCodes(response.backup_codes);
        setBackupCodesSaved(false);
      }

      setState("enabled");
      trackEvent("2fa_enabled", {});
      toast.success("Two-factor authentication enabled!");
    } catch (err: unknown) {
      const error = err as { message?: string };
      const msg = error?.message ?? "Invalid code. Please try again.";
      setErrorMsg(msg);
      setState("setup");
      setCode(["", "", "", "", "", ""]);
      codeInputRefs[0].current?.focus();
      toast.error(msg);
    }
  }, [code, user, setUser, codeInputRefs]);

  // ── Regenerate backup codes ──────────────────────────────────────────────

  const handleRegenerate = useCallback(async () => {
    setRegenerating(true);
    try {
      const response = await api.post<RegenerateResponse>("/auth/regenerate-backup-codes/", {
        password: disablePassword || prompt("Enter your password to regenerate backup codes:"),
      });
      setBackupCodes(response.backup_codes);
      setBackupCodesSaved(false);
      setCodesCopied(false);
      trackEvent("2fa_backup_codes_regenerated", {});
      toast.success("New backup codes generated!");
    } catch (err: unknown) {
      const error = err as { message?: string };
      toast.error(error?.message ?? "Failed to regenerate backup codes.");
    } finally {
      setRegenerating(false);
    }
  }, [disablePassword]);

  // ── Copy backup codes ────────────────────────────────────────────────────

  const handleCopyCodes = useCallback(() => {
    navigator.clipboard.writeText(backupCodes.join("\n")).then(() => {
      setCodesCopied(true);
      toast.success("Backup codes copied to clipboard!");
      setTimeout(() => setCodesCopied(false), 3000);
    });
  }, [backupCodes]);

  // ── Download backup codes as text file ───────────────────────────────────

  const handleDownloadCodes = useCallback(() => {
    const text = [
      "EduSphere SMS — Two-Factor Authentication Backup Codes",
      "========================================================",
      "",
      "Account: " + (user?.email ?? ""),
      "Generated: " + new Date().toLocaleDateString(),
      "",
      "Each code can be used ONCE to sign in if you lose access",
      "to your authenticator app. Keep these safe and private.",
      "",
      ...backupCodes.map((c, i) => `${i + 1}.  ${c}`),
      "",
      "========================================================",
      "If you lose these codes, regenerate new ones from your",
      "security settings. Previous codes will be invalidated.",
    ].join("\n");

    const blob = new Blob([text], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `edusphere-2fa-backup-codes-${user?.email ?? "account"}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    setBackupCodesSaved(true);
    trackEvent("2fa_backup_codes_downloaded", {});
    toast.success("Backup codes downloaded!");
  }, [backupCodes, user]);

  // ── Print backup codes ──────────────────────────────────────────────────

  const handlePrintCodes = useCallback(() => {
    const printWindow = window.open("", "_blank");
    if (!printWindow) {
      toast.error("Please allow pop-ups to print backup codes.");
      return;
    }
    printWindow.document.write(`
      <html>
        <head><title>2FA Backup Codes — ${user?.email ?? ""}</title>
        <style>
          body { font-family: monospace; padding: 40px; max-width: 600px; margin: auto; }
          h1 { font-size: 20px; margin-bottom: 4px; }
          p { color: #666; font-size: 14px; }
          .codes { margin: 24px 0; }
          .code { font-size: 18px; letter-spacing: 2px; padding: 8px 0; border-bottom: 1px solid #eee; }
          .warning { background: #fff3cd; padding: 12px; border-radius: 8px; font-size: 13px; }
        </style></head>
        <body>
          <h1>Two-Factor Authentication Backup Codes</h1>
          <p>Account: ${user?.email ?? ""}</p>
          <p>Each code can be used <strong>once</strong> to sign in.</p>
          <div class="codes">
            ${backupCodes.map((c) => `<div class="code">${c}</div>`).join("")}
          </div>
          <div class="warning">
            ⚠ Keep these codes safe and private. If you lose them,
            generate new ones from your account security settings.
          </div>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
    setBackupCodesSaved(true);
    trackEvent("2fa_backup_codes_printed", {});
  }, [backupCodes, user]);

  // ── Disable 2FA ─────────────────────────────────────────────────────────

  const handleDisable = useCallback(async () => {
    if (!disablePassword) {
      toast.error("Please enter your password to disable 2FA.");
      return;
    }

    setDisabling(true);
    try {
      await api.post<{ detail: string }>("/auth/disable-2fa/", {
        password: disablePassword,
      });

      if (user) {
        setUser({ ...user, two_factor_enabled: false });
      }

      setState("idle");
      setSetupData(null);
      setBackupCodes([]);
      setDisablePassword("");
      setCode(["", "", "", "", "", ""]);
      trackEvent("2fa_disabled", {});
      toast.success("Two-factor authentication disabled.");
    } catch (err: unknown) {
      const error = err as { message?: string };
      toast.error(error?.message ?? "Failed to disable 2FA.");
    } finally {
      setDisabling(false);
    }
  }, [disablePassword, user, setUser]);

  // ── Code input handlers ──────────────────────────────────────────────────

  const handleCodeChange = (index: number, value: string) => {
    if (value && !/^\d$/.test(value)) return;
    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);
    if (value && index < 5) {
      codeInputRefs[index + 1].current?.focus();
    }
  };

  const handleCodeKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !code[index] && index > 0) {
      codeInputRefs[index - 1].current?.focus();
    }
    if (e.key === "Enter") {
      handleVerify();
    }
  };

  const handleCodePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    const newCode = pasted.split("").concat(Array(6).fill("")).slice(0, 6);
    setCode(newCode);
    const nextEmpty = newCode.findIndex((c) => !c);
    codeInputRefs[nextEmpty >= 0 ? nextEmpty : 5].current?.focus();
  };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Two-Factor Authentication
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Add an extra layer of security to your account
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800 shadow-sm">
        {/* ── Idle ──────────────────────────────────────────── */}
        {state === "idle" && (
          <div className="p-8 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-100 dark:bg-indigo-900/30 mb-4">
              <ShieldCheckIcon className="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
            </div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Enhance your account security
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto mb-6">
              Two-factor authentication adds an extra layer of protection.
              After setup, you&apos;ll need both your password and a one-time code
              from your authenticator app to sign in.
            </p>
            <button
              type="button"
              onClick={fetchSetup}
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 active:bg-indigo-700 transition-all duration-150"
            >
              <KeyIcon className="h-4 w-4" />
              Set up two-factor authentication
            </button>
          </div>
        )}

        {/* ── Loading ───────────────────────────────────────── */}
        {state === "loading" && (
          <div className="flex flex-col items-center py-12 text-center">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent mb-4" />
            <p className="text-sm font-medium text-slate-600 dark:text-slate-400">
              Generating your 2FA secret and backup codes…
            </p>
          </div>
        )}

        {/* ── Setup — QR code + backup codes + TOTP input ───── */}
        {(state === "setup" || state === "verifying") && setupData && (
          <div>
            {/* QR Code Section */}
            <div className="p-6 pb-0">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-100 dark:bg-indigo-900/30">
                  <KeyIcon className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-slate-900 dark:text-white">
                    Step 1: Scan this QR code
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Use your authenticator app (Google Authenticator, Authy, etc.)
                  </p>
                </div>
              </div>
            </div>

            <div className="flex justify-center py-4">
              <div className="rounded-2xl border-2 border-slate-100 dark:border-slate-700 bg-white p-4 shadow-sm">
                <QRCodeSVG value={setupData.provisioning_uri} size={200} level="M" includeMargin />
              </div>
            </div>

            {/* Manual entry */}
            <div className="px-6 pb-2">
              <div className="rounded-xl bg-slate-50 dark:bg-slate-900/50 px-4 py-3">
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                    Or enter this key manually
                  </label>
                  <button
                    type="button"
                    onClick={() => setShowSecret((v) => !v)}
                    className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
                    title={showSecret ? "Hide secret" : "Show secret"}
                  >
                    {showSecret ? <EyeSlashIcon className="h-4 w-4" /> : <EyeIcon className="h-4 w-4" />}
                  </button>
                </div>
                <p className="font-mono text-sm text-slate-800 dark:text-slate-200 break-all select-all">
                  {showSecret
                    ? setupData.secret
                    : `${setupData.secret.slice(0, 4)}...${setupData.secret.slice(-4)}`}
                </p>
              </div>
            </div>

            {/* ── Backup Codes Display ──────────────────────────── */}
            {backupCodes.length > 0 && (
              <div className="px-6 pt-4">
                <div className="rounded-xl border-2 border-amber-200 dark:border-amber-700/50 bg-amber-50 dark:bg-amber-900/20 p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <ExclamationTriangleIcon className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0" />
                    <h3 className="text-sm font-bold text-amber-800 dark:text-amber-300">
                      Step 2: Save your backup codes
                    </h3>
                  </div>
                  <p className="text-xs text-amber-700 dark:text-amber-400 mb-3">
                    Each code can be used <strong>once</strong> to sign in if you lose access to
                    your authenticator app. Save them somewhere safe.
                  </p>

                  {/* Code list */}
                  <div className="bg-white dark:bg-slate-800 rounded-lg p-3 mb-3 font-mono text-sm space-y-1.5">
                    {backupCodes.map((c, i) => (
                      <div key={i} className="flex items-center gap-3 text-slate-800 dark:text-slate-200">
                        <span className="w-5 text-right text-xs text-slate-400 dark:text-slate-500">
                          {i + 1}.
                        </span>
                        <span className="tracking-wider font-bold">{c}</span>
                      </div>
                    ))}
                  </div>

                  {/* Action buttons */}
                  <div className="flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={handleCopyCodes}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-amber-100 dark:bg-amber-800/40 px-3 py-1.5 text-xs font-semibold text-amber-800 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-700/50 transition-colors"
                    >
                      {codesCopied ? (
                        <CheckIcon className="h-3.5 w-3.5" />
                      ) : (
                        <ClipboardIcon className="h-3.5 w-3.5" />
                      )}
                      {codesCopied ? "Copied!" : "Copy"}
                    </button>
                    <button
                      type="button"
                      onClick={handleDownloadCodes}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-amber-100 dark:bg-amber-800/40 px-3 py-1.5 text-xs font-semibold text-amber-800 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-700/50 transition-colors"
                    >
                      <DocumentArrowDownIcon className="h-3.5 w-3.5" />
                      Download
                    </button>
                    <button
                      type="button"
                      onClick={handlePrintCodes}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-amber-100 dark:bg-amber-800/40 px-3 py-1.5 text-xs font-semibold text-amber-800 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-700/50 transition-colors"
                    >
                      <PrinterIcon className="h-3.5 w-3.5" />
                      Print
                    </button>
                    {!backupCodesSaved && (
                      <button
                        type="button"
                        onClick={() => setBackupCodesSaved(true)}
                        className="text-xs font-medium text-amber-700 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-300 underline underline-offset-2 transition-colors"
                      >                         I&apos;ve saved them
                      </button>
                    )}
                    {backupCodesSaved && (
                      <span className="inline-flex items-center gap-1 text-xs font-medium text-green-600 dark:text-green-400">
                        <CheckIcon className="h-3.5 w-3.5" />
                        Saved
                      </span>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* TOTP Code Input */}
            <div className="p-6">
              <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
                Step 3: Enter the 6-digit code from your authenticator app
              </label>
              <div className="flex items-center justify-center gap-2">
                {code.map((digit, i) => (
                  <input
                    key={i}
                    ref={codeInputRefs[i]}
                    type="text"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleCodeChange(i, e.target.value)}
                    onKeyDown={(e) => handleCodeKeyDown(i, e)}
                    onPaste={i === 0 ? handleCodePaste : undefined}
                    disabled={state === "verifying"}
                    className={clsx(
                      "h-12 w-10 rounded-lg border text-center text-lg font-bold transition-all duration-100 focus:outline-none focus:ring-2",
                      errorMsg
                        ? "border-red-300 focus:ring-red-400"
                        : "border-slate-300 dark:border-slate-600 focus:ring-indigo-500 focus:border-indigo-400",
                      digit ? "border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20" : ""
                    )}
                    aria-label={`Digit ${i + 1}`}
                  />
                ))}
              </div>

              {errorMsg && (
                <p className="mt-3 text-center text-xs text-red-600 dark:text-red-400 flex items-center justify-center gap-1">
                  <ExclamationTriangleIcon className="h-3.5 w-3.5" />
                  {errorMsg}
                </p>
              )}

              <div className="mt-5 flex flex-col sm:flex-row items-center justify-center gap-3">
                <button
                  type="button"
                  disabled={state === "verifying"}
                  onClick={handleVerify}
                  className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 active:bg-indigo-700 transition-all duration-150 disabled:opacity-50"
                >
                  {state === "verifying" ? (
                    <>
                      <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Verifying…
                    </>
                  ) : (
                    <>
                      <ShieldCheckIcon className="h-4 w-4" />
                      Verify &amp; Enable
                    </>
                  )}
                </button>
                <button
                  type="button"
                  disabled={state === "verifying"}
                  onClick={fetchSetup}
                  className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-600 px-5 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors disabled:opacity-50"
                >
                  <ArrowPathIcon className="h-4 w-4" />
                  Generate new code
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── Enabled ────────────────────────────────────────── */}
        {state === "enabled" && (
          <div className="p-8">
            {/* Success header */}
            <div className="text-center mb-6">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-green-100 dark:bg-green-900/30 mb-4">
                <ShieldCheckIcon className="h-8 w-8 text-green-600 dark:text-green-400" />
              </div>
              <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
                Two-factor authentication is active
              </h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto">
                Your account is protected with an additional layer of security.
              </p>
            </div>

            {/* Backup codes section */}
            {backupCodes.length > 0 && (
              <div className="mb-6 rounded-xl border-2 border-amber-200 dark:border-amber-700/50 bg-amber-50 dark:bg-amber-900/20 p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <ExclamationTriangleIcon className="h-5 w-5 text-amber-600 dark:text-amber-400 shrink-0" />
                    <h3 className="text-sm font-bold text-amber-800 dark:text-amber-300">
                      Your backup codes
                    </h3>
                  </div>
                  <button
                    type="button"
                    disabled={regenerating}
                    onClick={handleRegenerate}
                    className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-xs font-semibold text-amber-700 dark:text-amber-400 hover:bg-amber-100 dark:hover:bg-amber-800/30 transition-colors disabled:opacity-50"
                  >
                    <ArrowPathIcon className={clsx("h-3.5 w-3.5", regenerating && "animate-spin")} />
                    Regenerate
                  </button>
                </div>

                <div className="bg-white dark:bg-slate-800 rounded-lg p-3 mb-3 font-mono text-sm space-y-1.5">
                  {backupCodes.map((c, i) => (
                    <div key={i} className="flex items-center gap-3 text-slate-800 dark:text-slate-200">
                      <span className="w-5 text-right text-xs text-slate-400 dark:text-slate-500">{i + 1}.</span>
                      <span className="tracking-wider font-bold">{c}</span>
                    </div>
                  ))}
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <button type="button" onClick={handleCopyCodes} className="inline-flex items-center gap-1.5 rounded-lg bg-amber-100 dark:bg-amber-800/40 px-3 py-1.5 text-xs font-semibold text-amber-800 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-700/50 transition-colors">
                    {codesCopied ? <CheckIcon className="h-3.5 w-3.5" /> : <ClipboardIcon className="h-3.5 w-3.5" />}
                    {codesCopied ? "Copied!" : "Copy"}
                  </button>
                  <button type="button" onClick={handleDownloadCodes} className="inline-flex items-center gap-1.5 rounded-lg bg-amber-100 dark:bg-amber-800/40 px-3 py-1.5 text-xs font-semibold text-amber-800 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-700/50 transition-colors">
                    <DocumentArrowDownIcon className="h-3.5 w-3.5" />
                    Download
                  </button>
                  <button type="button" onClick={handlePrintCodes} className="inline-flex items-center gap-1.5 rounded-lg bg-amber-100 dark:bg-amber-800/40 px-3 py-1.5 text-xs font-semibold text-amber-800 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-700/50 transition-colors">
                    <PrinterIcon className="h-3.5 w-3.5" />
                    Print
                  </button>
                </div>
              </div>
            )}

            {/* Disable section */}
            <details className="group">
              <summary className="cursor-pointer text-sm font-medium text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 transition-colors list-none inline-flex items-center gap-1.5">
                <ExclamationTriangleIcon className="h-4 w-4" />
                Disable two-factor authentication
              </summary>
              <div className="mt-4 rounded-xl border border-red-200 dark:border-red-800/40 bg-red-50 dark:bg-red-900/10 p-5 text-left">
                <p className="text-xs font-medium text-red-700 dark:text-red-400 mb-3">
                  Enter your password to disable 2FA:
                </p>
                <input
                  type="password"
                  value={disablePassword}
                  onChange={(e) => setDisablePassword(e.target.value)}
                  placeholder="Your current password"
                  className="w-full rounded-lg border border-slate-300 dark:border-slate-600 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-400 mb-3"
                  onKeyDown={(e) => e.key === "Enter" && handleDisable()}
                />
                <button
                  type="button"
                  disabled={disabling}
                  onClick={handleDisable}
                  className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-500 active:bg-red-700 transition-colors disabled:opacity-50"
                >
                  {disabling ? (
                    <>
                      <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Disabling…
                    </>
                  ) : (
                    <>
                      <ExclamationTriangleIcon className="h-4 w-4" />
                      Disable 2FA
                    </>
                  )}
                </button>
              </div>
            </details>
          </div>
        )}

        {/* ── Error ──────────────────────────────────────────── */}
        {state === "error" && (
          <div className="p-8 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-red-100 dark:bg-red-900/30 mb-4">
              <ExclamationTriangleIcon className="h-8 w-8 text-red-600 dark:text-red-400" />
            </div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
              Something went wrong
            </h2>
            <p className="text-sm text-red-600 dark:text-red-400 mb-6">{errorMsg}</p>
            <button
              type="button"
              onClick={fetchSetup}
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors"
            >
              <ArrowPathIcon className="h-4 w-4" />
              Try again
            </button>
          </div>
        )}
      </div>

      {/* ── Info cards ──────────────────────────────────────────── */}
      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800 p-5 shadow-sm">
          <div className="flex items-center gap-2.5 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/30">
              <svg className="h-4 w-4 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">How it works</h3>
          </div>
          <ol className="space-y-2 text-xs text-slate-500 dark:text-slate-400 list-decimal list-inside">
            <li>Scan the QR code with your authenticator app</li>
            <li>The app generates a 6-digit code that refreshes every 30 seconds</li>
            <li>Save your backup codes — you&apos;ll need them if you lose your phone</li>
            <li>Enter the current code to confirm setup</li>
          </ol>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800 p-5 shadow-sm">
          <div className="flex items-center gap-2.5 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/30">
              <svg className="h-4 w-4 text-amber-600 dark:text-amber-400" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Backup codes</h3>
          </div>
          <ul className="space-y-1.5 text-xs text-slate-500 dark:text-slate-400">
            <li className="flex items-start gap-1.5">
              <span className="mt-0.5 text-amber-500">⚠</span>
              Each backup code can be used <strong>once</strong> to sign in
            </li>
            <li className="flex items-start gap-1.5">
              <span className="mt-0.5 text-amber-500">⚠</span>
              Store them securely — treat them like passwords
            </li>
            <li className="flex items-start gap-1.5">
              <span className="mt-0.5 text-green-500">✓</span>
              You can regenerate codes at any time from this page
            </li>
            <li className="flex items-start gap-1.5">
              <span className="mt-0.5 text-green-500">✓</span>
              Previous codes are invalidated when you regenerate
            </li>
          </ul>
        </div>
      </div>

      <div className="mt-6 text-center">
        <Link
          to=".."
          className="text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 transition-colors"
        >
          ← Back to settings
        </Link>
      </div>
    </div>
  );
}
