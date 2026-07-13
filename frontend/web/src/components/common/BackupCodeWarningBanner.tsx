/**
 * BackupCodeWarningBanner
 *
 * Shows a prominent warning banner on dashboard pages when the authenticated
 * user has 2FA enabled and their remaining backup codes drop to 2 or fewer.
 *
 * - 0 remaining: red critical banner urging immediate regeneration
 * - 1–2 remaining: amber warning banner suggesting regeneration
 *
 * The banner can be dismissed by the user and won't reappear until the page
 * is reloaded or they navigate to a different route.
 */

import React from "react";
import { useNavigate } from "react-router-dom";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";
import { useAuthStore } from "../../store/authStore";
import { useUIStore } from "../../store/uiStore";
import clsx from "clsx";

interface Props {
  /** Path to the 2FA setup/manage page (e.g. "../setup-2fa"). */
  managePath?: string;
}

export default function BackupCodeWarningBanner({ managePath = "../setup-2fa" }: Props) {
  const user = useAuthStore((s) => s.user);
  const dismissed = useUIStore((s) => s.backupBannerDismissed);
  const dismissBanner = useUIStore((s) => s.dismissBackupBanner);
  const navigate = useNavigate();

  // Don't render if user hasn't loaded, 2FA is not enabled, no codes info,
  // or enough codes remain, or banner was dismissed
  if (!user || !user.two_factor_enabled || user.backup_codes_remaining === null) {
    return null;
  }

  if (user.backup_codes_remaining > 2) return null;
  if (dismissed) return null;

  const isCritical = user.backup_codes_remaining === 0;

  return (
    <div
      className={clsx(
        "mb-6 rounded-xl border px-4 py-3",
        isCritical
          ? "border-red-200 bg-red-50 dark:border-red-800/40 dark:bg-red-900/20"
          : "border-amber-200 bg-amber-50 dark:border-amber-800/40 dark:bg-amber-900/20"
      )}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <ExclamationTriangleIcon
          className={clsx(
            "mt-0.5 h-5 w-5 shrink-0",
            isCritical
              ? "text-red-500 dark:text-red-400"
              : "text-amber-500 dark:text-amber-400"
          )}
        />

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <p
              className={clsx(
                "text-sm font-semibold",
                isCritical
                  ? "text-red-800 dark:text-red-300"
                  : "text-amber-800 dark:text-amber-300"
              )}
            >
              {isCritical
                ? "No backup codes remaining"
                : `Only ${user.backup_codes_remaining} backup code${user.backup_codes_remaining === 1 ? "" : "s"} remaining`}
            </p>
            <button
              type="button"
              onClick={() => dismissBanner()}
              className={clsx(
                "shrink-0 rounded p-0.5 transition-colors",
                isCritical
                  ? "text-red-400 hover:text-red-600 dark:hover:text-red-200"
                  : "text-amber-400 hover:text-amber-600 dark:hover:text-amber-200"
              )}
              aria-label="Dismiss"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p
            className={clsx(
              "text-xs mt-0.5",
              isCritical
                ? "text-red-700 dark:text-red-400"
                : "text-amber-700 dark:text-amber-400"
            )}
          >
            {isCritical
              ? "You have used all your backup codes. Generate new ones immediately to avoid being locked out of your account."
              : "Consider generating new backup codes from your security settings to ensure you always have a recovery option available."}
          </p>

          {/* Actions */}
          <div className="mt-2.5 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => navigate(managePath)}
              className={clsx(
                "inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors",
                isCritical
                  ? "bg-red-100 dark:bg-red-800/40 text-red-800 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-700/50"
                  : "bg-amber-100 dark:bg-amber-800/40 text-amber-800 dark:text-amber-300 hover:bg-amber-200 dark:hover:bg-amber-700/50"
              )}
            >
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
              </svg>
              {isCritical ? "Generate codes now" : "Manage backup codes"}
            </button>
            <button
              type="button"
              onClick={() => dismissBanner()}
              className={clsx(
                "text-xs underline underline-offset-2",
                isCritical
                  ? "text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                  : "text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300"
              )}
            >
              {isCritical ? "I'll do it later" : "Remind me later"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
