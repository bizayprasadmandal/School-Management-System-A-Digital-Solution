"""Plan feature gating — which capabilities each subscription tier unlocks.

``subscription_tier`` on ``School`` carries the plan (basic / standard /
premium); this module is the single source of truth for what each tier may
use. Enforcement is via :class:`core.permissions.IsPremiumFeature` on the
gated viewsets/actions, and the frontend discovers its plan's entitlements
through ``/api/v1/auth/me/`` (``plan_features`` on the profile payload).

Gating philosophy: Standard must be able to run a school end-to-end;
Premium sells time, insight, and reach — deeper accounting, analytics,
messaging reach, live tracking, and document generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PremiumFeature:
    """One gated capability. ``endpoints`` are DRF-style paths relative to
    ``/api/v1/`` used for both enforcement lookup and frontend discovery."""

    key: str
    label: str
    endpoints: tuple[str, ...] = field(default_factory=tuple)


PREMIUM_FEATURES: tuple[PremiumFeature, ...] = (
    PremiumFeature(
        key="accounting_ledger",
        label="Double-entry accounting ledger",
        endpoints=("fees/accounting-entry/monthly_summary", "fees/accounting-entry/monthly_trend"),
    ),
    PremiumFeature(
        key="advanced_analytics",
        label="Advanced analytics & custom reports",
        endpoints=(
            "reporting/at-risk-students",
            "reporting/enrollment-funnel",
            "reporting/fee-forecast",
        ),
    ),
    PremiumFeature(
        key="finance_overview",
        label="Finance & operations overview cards",
        endpoints=("reporting/finance-ops",),
    ),
    PremiumFeature(
        key="live_transport_tracking",
        label="Live GPS tracking, geofencing & ETAs",
        endpoints=(
            "transport/bus-tracking",
            "transport/stop-e-t-a",
            "transport/geofence-zone",
            "transport/geofence-alert",
        ),
    ),
)

# Flat endpoint -> feature key lookup for enforcement.
ENDPOINT_FEATURE_MAP: dict[str, str] = {
    endpoint: feature.key for feature in PREMIUM_FEATURES for endpoint in feature.endpoints
}

# Keys every paid plan (standard and premium) may use. Basic is the bare
# SIS tier. Premium currently unlocks everything gated; the split exists so
# future mid-tier features have a home.
STANDARD_FEATURES: frozenset[str] = frozenset({"finance_overview"})
PREMIUM_FEATURE_KEYS: frozenset[str] = frozenset(feature.key for feature in PREMIUM_FEATURES)


def school_has_feature(school, feature_key: str) -> bool:
    """Whether ``school``'s subscription tier unlocks ``feature_key``.

    Unknown feature keys resolve to False (fail closed).
    """
    if school is None:
        return False
    tier = getattr(school, "subscription_tier", "basic")
    if tier == "premium":
        return feature_key in PREMIUM_FEATURE_KEYS
    if tier == "standard":
        return feature_key in STANDARD_FEATURES
    return False


def plan_features_for_tier(tier: str) -> dict:
    """Payload fragment for ``/auth/me/`` — plan and unlocked feature keys."""
    tier = tier or "basic"
    if tier == "premium":
        unlocked = sorted(PREMIUM_FEATURE_KEYS)
    elif tier == "standard":
        unlocked = sorted(STANDARD_FEATURES)
    else:
        unlocked = []
    return {
        "plan": tier,
        "features": unlocked,
        "is_premium": tier == "premium",
    }
