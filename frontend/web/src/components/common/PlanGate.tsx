/**
 * Plan gating UI — badges and upgrade prompts for tiered features.
 *
 * Reads the plan entitlements the backend reports on /auth/me/
 * (plan_features) via the auth store. Surfaces:
 *
 * - <PlanBadge />        — sidebar/header chip showing current plan
 * - <PremiumGate>        — wraps gated content; renders an upgrade panel
 *                          in place of children when the feature is locked
 * - <FeatureLockNotice/> — inline variant for cards/tabs
 */

import React from "react";
import { Link } from "react-router-dom";
import { LockClosedIcon, SparklesIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";

import { useHasFeature, usePlanFeatures, useFeatureLocked } from "../../store/authStore";

const PLAN_STYLES: Record<string, string> = {
  premium: "bg-gradient-to-r from-amber-400 to-amber-500 text-amber-950",
  standard: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300",
  basic: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
};

/** Current plan chip (sidebar/header). */
export function PlanBadge({ className }: { className?: string }) {
  const planFeatures = usePlanFeatures();
  const plan = planFeatures?.plan ?? "basic";
  return (
    <span
      title={`Current plan: ${plan}`}
      className={clsx(
        "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
        PLAN_STYLES[plan] ?? PLAN_STYLES.basic,
        className,
      )}
    >
      {plan === "premium" && <SparklesIcon className="h-3 w-3" aria-hidden="true" />}
      {plan}
    </span>
  );
}

const FEATURE_LABELS: Record<string, string> = {
  accounting_ledger: "the accounting ledger (monthly summary & trend)",
  advanced_analytics: "advanced analytics (at-risk students, enrollment funnel, fee forecast)",
  finance_overview: "the finance & operations overview",
  live_transport_tracking: "live transport tracking (bus tracking, stop ETAs, geofences)",
};

/** Inline notice for a locked card/tab. */
export function FeatureLockNotice({
  featureKey,
  compact = false,
}: {
  featureKey: string;
  compact?: boolean;
}) {
  const planFeatures = usePlanFeatures();
  const what = FEATURE_LABELS[featureKey] ?? "this feature";
  return (
    <div
      role="status"
      aria-label={`Premium feature locked: ${what}`}
      className={clsx(
        "rounded-xl border border-amber-200 bg-amber-50 dark:border-amber-800/60 dark:bg-amber-900/20",
        compact ? "px-3 py-2" : "px-4 py-6 text-center",
      )}
    >
      <div className={clsx("flex items-center gap-2", !compact && "flex-col justify-center")}>
        <LockClosedIcon className="h-5 w-5 text-amber-500" aria-hidden="true" />
        <p
          className={clsx(
            "font-medium text-amber-800 dark:text-amber-200",
            compact ? "text-xs" : "text-sm",
          )}
        >
          {what.charAt(0).toUpperCase() + what.slice(1)} requires a plan upgrade.
        </p>
        {!compact && (
          <p className="mt-1 max-w-md text-xs text-amber-700 dark:text-amber-300">
            Your current plan is <strong>{planFeatures?.plan ?? "basic"}</strong>. Upgrade to
            Premium to unlock {what}, plus the double-entry ledger, advanced analytics, and live
            transport tracking.
          </p>
        )}
        <Link
          to="/admin/settings"
          className={clsx(
            "inline-flex items-center gap-1 rounded-lg bg-amber-500 px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition hover:bg-amber-600",
            !compact && "mt-3",
          )}
        >
          <SparklesIcon className="h-3.5 w-3.5" aria-hidden="true" />
          Upgrade plan
        </Link>
      </div>
    </div>
  );
}

/**
 * Renders children when the school's plan unlocks `featureKey`; otherwise
 * renders the upgrade panel in place. Super admins always see content.
 */
export function PremiumGate({
  featureKey,
  children,
  fallback,
}: {
  featureKey: string;
  children: React.ReactNode;
  /** Custom locked render (defaults to FeatureLockNotice). */
  fallback?: React.ReactNode;
}) {
  const unlocked = useHasFeature(featureKey);
  if (unlocked) return <>{children}</>;
  return <>{fallback ?? <FeatureLockNotice featureKey={featureKey} />}</>;
}

/**
 * Soft gate for existing surfaces (entity tabs, dashboard cards): renders
 * children normally while the plan is unknown/premium (fail-open — the
 * backend's 403 is the hard enforcement), and swaps in a compact upgrade
 * banner above the content once the plan is *known* to lack the feature.
 * Pass `replace` to hide the content entirely instead of banner-above.
 */
export function PlanLockedSection({
  featureKey,
  children,
  replace = false,
}: {
  featureKey: string;
  children: React.ReactNode;
  /** When true, locked content is hidden and only the notice renders. */
  replace?: boolean;
}) {
  const locked = useFeatureLocked(featureKey);
  if (!locked) return <>{children}</>;
  if (replace) return <FeatureLockNotice featureKey={featureKey} />;
  return (
    <div className="space-y-3">
      <FeatureLockNotice featureKey={featureKey} compact />
      {children}
    </div>
  );
}
