/**
 * Plan & Billing — current subscription tier, the tiered feature matrix,
 * and an upgrade/downgrade CTA for school admins.
 *
 * Data comes from GET /auth/plan/ (matrix + current tier); tier changes go
 * through POST /auth/plan/change-tier/ (school admins only — the backend
 * enforces this and the UI hides the CTA for other roles).
 */
import React, { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckIcon, MinusIcon, SparklesIcon, ArrowPathIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, SkeletonCard, SkeletonStatCard } from "../../components/common";
import { useAuthStore } from "../../store/authStore";
import { useTitle } from "../../hooks";
import { npr } from "../../utils";
import toast from "react-hot-toast";

interface MatrixRow {
  key: string;
  label: string;
  basic: boolean;
  standard: boolean;
  premium: boolean;
}

interface TierPricing {
  currency: string;
  per_student_month: number;
  per_student_year: number;
}

interface PlanOverview {
  plan: "basic" | "standard" | "premium";
  is_premium: boolean;
  school_name: string | null;
  features: string[];
  matrix: MatrixRow[];
  can_manage: boolean;
  pricing: Record<string, TierPricing>;
}

const TIER_ORDER: Record<string, number> = { basic: 0, standard: 1, premium: 2 };

const TIER_META: Record<string, { label: string; blurb: string; badge: string }> = {
  basic: {
    label: "Basic",
    blurb: "The bare student information system — records, attendance, and the essentials.",
    badge: "bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-200",
  },
  standard: {
    label: "Standard",
    blurb: "Everything a school needs to run end-to-end, plus the finance overview.",
    badge: "bg-sky-100 text-sky-700 dark:bg-sky-900/50 dark:text-sky-200",
  },
  premium: {
    label: "Premium",
    blurb: "Deeper accounting, advanced analytics, live transport tracking, and more.",
    badge: "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-200",
  },
};

function Cell({ ok }: { ok: boolean }) {
  return ok ? (
    <CheckIcon className="h-5 w-5 text-emerald-500" aria-label="Included" />
  ) : (
    <MinusIcon className="h-5 w-5 text-slate-300 dark:text-slate-600" aria-label="Not included" />
  );
}

export default function PlanBillingPage() {
  useTitle("Plan & Billing");
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const [changing, setChanging] = useState(false);

  const { data: plan, isLoading } = useQuery({
    queryKey: ["plan"],
    queryFn: () => api.get<PlanOverview>("/auth/plan/"),
  });

  const changeTier = async (tier: string) => {
    if (!plan || tier === plan.plan) return;
    const direction = TIER_ORDER[tier] > TIER_ORDER[plan.plan] ? "upgrade" : "downgrade";
    if (
      !window.confirm(
        `Change the school plan from ${TIER_META[plan.plan]?.label} to ${TIER_META[tier]
          ?.label}? ` +
          (direction === "downgrade"
            ? "Features above the new tier stop working immediately."
            : "New features unlock immediately."),
      )
    ) {
      return;
    }
    setChanging(true);
    try {
      await api.post("/auth/plan/change-tier/", { tier });
      toast.success(`Plan changed to ${TIER_META[tier]?.label}`);
      // plan_features on /auth/me/ is persisted in the auth store — refresh it
      const me = await api.get<Record<string, unknown>>("/auth/me/");
      useAuthStore
        .getState()
        .setPlanFeatures((me as { plan_features?: never }).plan_features ?? null);
      await queryClient.invalidateQueries({ queryKey: ["plan"] });
    } catch {
      toast.error("Failed to change plan");
    } finally {
      setChanging(false);
    }
  };

  if (isLoading || !plan) {
    return (
      <div className="space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Plan &amp; Billing</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Your school&apos;s subscription and included features
          </p>
        </div>
        <SkeletonStatCard />
        <SkeletonCard />
      </div>
    );
  }

  const meta = TIER_META[plan.plan] ?? TIER_META.basic;
  const upgradeTargets = (["basic", "standard", "premium"] as const).filter(
    (t) => TIER_ORDER[t] > TIER_ORDER[plan.plan],
  );
  const tierPrice = (t: string) => {
    const p = plan.pricing?.[t];
    if (!p) return "";
    return p.per_student_month === 0 ? "Free" : `${npr(p.per_student_month)}/student/mo`;
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Plan &amp; Billing</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Your school&apos;s subscription and included features
        </p>
      </div>

      {/* Current tier */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                {plan.school_name ?? "School"}
              </h2>
              <span
                className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${meta.badge}`}
              >
                {plan.is_premium && <SparklesIcon className="h-3.5 w-3.5" aria-hidden />}
                {meta.label}
              </span>
            </div>
            <p className="text-sm text-slate-500 mt-1">{meta.blurb}</p>
            <p className="text-xs text-slate-400 mt-1">
              {plan.features.length} gated feature{plan.features.length === 1 ? "" : "s"} unlocked
            </p>
          </div>{" "}
          {plan.can_manage && upgradeTargets.length > 0 && (
            <div className="flex items-center gap-2">
              {upgradeTargets.map((t) => (
                <Button
                  key={t}
                  onClick={() => changeTier(t)}
                  disabled={changing}
                  variant={t === "premium" ? "primary" : "secondary"}
                >
                  {changing ? (
                    <ArrowPathIcon className="h-4 w-4 animate-spin" aria-hidden />
                  ) : t === "premium" ? (
                    <>
                      💎 Upgrade to {TIER_META[t].label} · {tierPrice(t)}
                    </>
                  ) : (
                    <>
                      Switch to {TIER_META[t].label} · {tierPrice(t)}
                    </>
                  )}
                </Button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Pricing row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {(["basic", "standard", "premium"] as const).map((t) => {
          const p = plan.pricing?.[t];
          const current = t === plan.plan;
          return (
            <div
              key={t}
              className={`rounded-2xl border p-4 shadow-sm ${
                current
                  ? "border-indigo-300 bg-indigo-50/60 dark:border-indigo-700 dark:bg-indigo-900/20"
                  : "bg-white border-slate-100 dark:bg-slate-800 dark:border-slate-700 dark:shadow-none"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">
                  {TIER_META[t].label}
                </span>
                {current && (
                  <span className="text-xs font-medium text-indigo-600 dark:text-indigo-300">
                    current
                  </span>
                )}
              </div>
              <p className="mt-1 text-lg font-bold text-slate-900 dark:text-white">
                {p && p.per_student_month > 0 ? (
                  <>
                    {npr(p.per_student_month)}
                    <span className="text-xs font-normal text-slate-500"> /student/mo</span>
                  </>
                ) : (
                  "Free"
                )}
              </p>
              <p className="text-xs text-slate-400 mt-0.5">
                {p && p.per_student_month > 0
                  ? `${npr(p.per_student_year)}/student billed yearly (2 months free)`
                  : "No cost"}
              </p>
            </div>
          );
        })}
      </div>

      {/* Feature matrix */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white">
            Feature comparison
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">What each subscription tier unlocks</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm" aria-label="Feature comparison by subscription tier">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-100 dark:border-slate-700">
                <th scope="col" className="px-5 py-3 font-medium">
                  Feature
                </th>
                <th scope="col" className="px-3 py-3 font-medium text-center">
                  Basic
                </th>
                <th scope="col" className="px-3 py-3 font-medium text-center">
                  Standard
                </th>
                <th scope="col" className="px-3 py-3 font-medium text-center">
                  Premium
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {plan.matrix.map((row) => {
                const unlocked = plan.features.includes(row.key);
                return (
                  <tr
                    key={row.key}
                    className={
                      unlocked
                        ? "bg-emerald-50/60 dark:bg-emerald-900/10"
                        : "hover:bg-slate-50 dark:hover:bg-slate-700/40"
                    }
                  >
                    <td className="px-5 py-3 text-slate-800 dark:text-slate-100">
                      {row.label}
                      {unlocked && (
                        <span className="ml-2 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                          · included in your plan
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-center">
                      <Cell ok={row.basic} />
                    </td>
                    <td className="px-3 py-3 text-center">
                      <Cell ok={row.standard} />
                    </td>
                    <td className="px-3 py-3 text-center">
                      <Cell ok={row.premium} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {!plan.can_manage && (
        <p className="text-xs text-slate-400">
          Plan changes are managed by your school&apos;s administrators
          {user?.role ? ` (${user.role} view)` : ""}.
        </p>
      )}
    </div>
  );
}
