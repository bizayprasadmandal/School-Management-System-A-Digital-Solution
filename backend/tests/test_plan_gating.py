"""
Plan feature gating — tier enforcement on premium endpoints.

Pins the contract between ``School.subscription_tier`` and the gated
surfaces:

- **Registry semantics** — unknown keys fail closed; premium unlocks
  everything; standard unlocks only the deliberately-shared features.
- **Enforcement** — a standard school gets 403 with ``plan_required`` in
  the error payload on gated endpoints (ledger depth, deep analytics,
  live transport tracking) while its untiered endpoints keep working.
- **Discovery** — ``/auth/me/`` carries ``plan_features`` so the UI can
  badge and upsell without a second request.
"""

import pytest
from core.plan_features import ENDPOINT_FEATURE_MAP, PREMIUM_FEATURES, plan_features_for_tier, school_has_feature
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import AdminUserFactory, SchoolFactory, UserFactory

# Premium-only (standard does NOT unlock these).
PREMIUM_ONLY_ENDPOINTS = [
    "/api/v1/fees/accounting-entry/monthly_summary/",
    "/api/v1/fees/accounting-entry/monthly_trend/",
    "/api/v1/reporting/at-risk-students/",
    "/api/v1/reporting/enrollment-funnel/",
    "/api/v1/reporting/fee-forecast/",
    "/api/v1/transport/bus-tracking/",
    "/api/v1/transport/stop-e-t-a/",
    "/api/v1/transport/geofence-zone/",
]

# Standard ALSO unlocks these (shared tier features).
STANDARD_OK_ENDPOINTS = [
    "/api/v1/reporting/finance-ops/",
]

GATED_ENDPOINTS = PREMIUM_ONLY_ENDPOINTS + STANDARD_OK_ENDPOINTS


def client_as(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# ─── Registry semantics ───────────────────────────────────────────────────────


@pytest.mark.django_db
def test_unknown_feature_fails_closed():
    school = SchoolFactory(subscription_tier="premium")
    assert school_has_feature(school, "not_a_real_feature") is False
    assert school_has_feature(None, "accounting_ledger") is False


@pytest.mark.django_db
def test_tier_matrix():
    premium = SchoolFactory(subscription_tier="premium")
    standard = SchoolFactory(subscription_tier="standard")
    basic = SchoolFactory(subscription_tier="basic")

    for feature, _label, _eps in [(f, f.label, f.endpoints) for f in PREMIUM_FEATURES]:
        key = feature.key
        assert school_has_feature(premium, key) is True
        assert school_has_feature(standard, key) == (key == "finance_overview")
        assert school_has_feature(basic, key) is False


def test_registry_paths_are_consistent():
    """Every registered endpoint maps back to its own feature key."""
    for feature in PREMIUM_FEATURES:
        for endpoint in feature.endpoints:
            assert ENDPOINT_FEATURE_MAP[endpoint] == feature.key


# ─── /auth/me/ discovery ──────────────────────────────────────────────────────


@pytest.mark.django_db
def test_me_carries_plan_features_for_premium():
    school = SchoolFactory(subscription_tier="premium")
    admin = AdminUserFactory(school=school)
    resp = client_as(admin).get("/api/v1/auth/me/")
    assert resp.status_code == 200
    pf = resp.data["plan_features"]
    assert pf["plan"] == "premium"
    assert pf["is_premium"] is True
    assert "advanced_analytics" in pf["features"]
    assert "accounting_ledger" in pf["features"]


@pytest.mark.django_db
def test_me_carries_plan_features_for_standard():
    school = SchoolFactory(subscription_tier="standard")
    admin = AdminUserFactory(school=school)
    pf = client_as(admin).get("/api/v1/auth/me/").data["plan_features"]
    assert pf["plan"] == "standard"
    assert pf["is_premium"] is False
    assert pf["features"] == ["finance_overview"]


def test_plan_features_payload_shapes():
    assert plan_features_for_tier("basic") == {"plan": "basic", "features": [], "is_premium": False}
    assert plan_features_for_tier(None)["plan"] == "basic"


# ─── Enforcement: standard school blocked on gated endpoints ──────────────────


@pytest.mark.django_db
def test_standard_school_blocked_on_premium_endpoints():
    school = SchoolFactory(subscription_tier="standard")
    admin = AdminUserFactory(school=school)
    client = client_as(admin)

    for endpoint in PREMIUM_ONLY_ENDPOINTS:
        resp = client.get(endpoint)
        assert resp.status_code == 403, f"{endpoint} should be gated for standard"
        assert (
            "plan" in str(resp.data.get("detail", "")).lower() or "upgrade" in str(resp.data.get("detail", "")).lower()
        ), f"{endpoint} error should mention the upgrade"


@pytest.mark.django_db
def test_standard_school_passes_shared_tier_features():
    """finance_overview is deliberately unlocked on Standard."""
    school = SchoolFactory(subscription_tier="standard")
    admin = AdminUserFactory(school=school)
    for endpoint in STANDARD_OK_ENDPOINTS:
        assert client_as(admin).get(endpoint).status_code == 200, f"{endpoint} should pass for standard"


@pytest.mark.django_db
def test_premium_school_passes_gated_endpoints():
    school = SchoolFactory(subscription_tier="premium")
    admin = AdminUserFactory(school=school)
    client = client_as(admin)

    for endpoint in GATED_ENDPOINTS:
        resp = client.get(endpoint)
        assert resp.status_code == 200, f"{endpoint} should pass for premium: {getattr(resp, 'data', '')}"


@pytest.mark.django_db
def test_untiered_endpoints_still_work_for_standard():
    """Standard schools keep the core SIS running — gating must not leak."""
    school = SchoolFactory(subscription_tier="standard")
    admin = AdminUserFactory(school=school)
    client = client_as(admin)

    assert client.get("/api/v1/reporting/dashboard-stats/").status_code == 200
    assert client.get("/api/v1/students/classrooms/").status_code == 200
    assert client.get("/api/v1/transport/vehicles/").status_code == 200
    assert client.get("/api/v1/fees/accounting-entry/").status_code == 200


@pytest.mark.django_db
def test_super_admin_bypasses_gating_for_any_tier():
    """Platform staff manage every tenant — never blocked by a school's plan."""
    from services.auth.models import UserRole

    school = SchoolFactory(subscription_tier="basic")
    super_admin = UserFactory(school=school, role=UserRole.SUPER_ADMIN)
    client = client_as(super_admin)

    for endpoint in GATED_ENDPOINTS[:3]:
        resp = client.get(endpoint)
        assert (
            resp.status_code != 403 or "upgrade" not in str(resp.data.get("detail", "")).lower()
        ), f"super admin should not be plan-blocked at {endpoint}"


# ─── Plan & billing page API ─────────────────────────────────────────────────


@pytest.mark.django_db
def test_plan_overview_returns_matrix_and_tier():
    """Any school member can see the current plan and the full feature matrix."""
    school = SchoolFactory(subscription_tier="standard")
    user = UserFactory(school=school, role="teacher")

    res = client_as(user).get("/api/v1/auth/plan/")

    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    assert body["plan"] == "standard"
    assert body["school_name"] == school.name
    assert body["features"] == ["finance_overview"]
    assert body["can_manage"] is False
    keys = {row["key"]: row for row in body["matrix"]}
    assert set(keys) == {f.key for f in PREMIUM_FEATURES}
    # matrix shape: premium unlocks all, basic none, standard only shared keys
    for row in keys.values():
        assert row["premium"] is True
        assert row["basic"] is False
        assert row["standard"] == (row["key"] == "finance_overview")


@pytest.mark.django_db
def test_plan_overview_includes_pricing_for_all_tiers():
    """The pricing block (per-student rates per tier) advertises upgrades."""
    from core.plan_features import TIER_PRICING

    user = UserFactory(role="teacher")
    res = client_as(user).get("/api/v1/auth/plan/")

    assert res.status_code == status.HTTP_200_OK
    pricing = res.json()["pricing"]
    assert set(pricing) == {"basic", "standard", "premium"}
    assert pricing == TIER_PRICING
    assert pricing["basic"]["per_student_month"] == 0
    assert pricing["premium"]["per_student_month"] > pricing["standard"]["per_student_month"]
    # annual = 10x monthly (two months free)
    for tier in ("standard", "premium"):
        assert pricing[tier]["per_student_year"] == pricing[tier]["per_student_month"] * 10


@pytest.mark.django_db
def test_plan_overview_admin_sees_manage_flag():
    school = SchoolFactory(subscription_tier="premium")
    user = AdminUserFactory(school=school)

    res = client_as(user).get("/api/v1/auth/plan/")

    assert res.status_code == status.HTTP_200_OK
    assert res.json()["can_manage"] is True
    assert res.json()["is_premium"] is True


@pytest.mark.django_db
def test_change_tier_upgrade_and_downgrade():
    school = SchoolFactory(subscription_tier="standard")
    user = AdminUserFactory(school=school)
    client = client_as(user)

    res = client.post("/api/v1/auth/plan/change-tier/", {"tier": "premium"}, format="json")
    assert res.status_code == status.HTTP_200_OK
    assert res.json()["plan"] == "premium"
    assert set(res.json()["plan_features"]["features"]) == {f.key for f in PREMIUM_FEATURES}
    school.refresh_from_db()
    assert school.subscription_tier == "premium"

    res = client.post("/api/v1/auth/plan/change-tier/", {"tier": "basic"}, format="json")
    assert res.status_code == status.HTTP_200_OK
    school.refresh_from_db()
    assert school.subscription_tier == "basic"


@pytest.mark.django_db
def test_change_tier_validates_input_and_idempotence():
    school = SchoolFactory(subscription_tier="standard")
    client = client_as(AdminUserFactory(school=school))

    res = client.post("/api/v1/auth/plan/change-tier/", {"tier": "ultra"}, format="json")
    assert res.status_code == status.HTTP_400_BAD_REQUEST

    res = client.post("/api/v1/auth/plan/change-tier/", {"tier": "standard"}, format="json")
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_change_tier_rejects_non_admins():
    school = SchoolFactory(subscription_tier="standard")
    teacher = UserFactory(school=school, role="teacher")

    res = client_as(teacher).post("/api/v1/auth/plan/change-tier/", {"tier": "premium"}, format="json")

    assert res.status_code == status.HTTP_403_FORBIDDEN
    school.refresh_from_db()
    assert school.subscription_tier == "standard"


# ─── Platform console: Revenue & cross-school audit ──────────────────────────


@pytest.mark.django_db
def test_platform_stats_contract_and_permissions():
    """Platform dashboard payload matches the frontend contract.

    Revenue is numeric (not a DRF decimal string) and recent-school rows
    carry the annotated ``student_count`` the dashboard renders.
    """
    from decimal import Decimal

    from tests.factories import (
        AcademicYearFactory,
        FeeCategoryFactory,
        FeeInvoiceFactory,
        FeeStructureFactory,
        GradeFactory,
        PaymentFactory,
        StudentFactory,
        StudentUserFactory,
    )

    premium_school = SchoolFactory(subscription_tier="premium")
    sa = UserFactory(role="super_admin", school=None, is_staff=True)
    admin = AdminUserFactory(school=premium_school)

    grade = GradeFactory(school=premium_school)
    category = FeeCategoryFactory(school=premium_school)
    ay = AcademicYearFactory(school=premium_school)
    fs = FeeStructureFactory(school=premium_school, academic_year=ay, grade=grade, fee_category=category)
    student = StudentFactory(user=StudentUserFactory(school=premium_school))
    invoice = FeeInvoiceFactory(student=student, academic_year=ay, fee_structure=fs)
    PaymentFactory(invoice=invoice, collected_by=sa, amount=Decimal("250.00"), status="successful")

    # School admins are locked out of the platform console.
    assert client_as(admin).get("/api/v1/auth/platform/stats/").status_code == status.HTTP_403_FORBIDDEN

    res = client_as(sa).get("/api/v1/auth/platform/stats/")

    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    assert isinstance(body["total_revenue"], (int, float))
    assert body["total_revenue"] == 250.0
    assert body["total_students"] == 1
    assert body["schools_by_tier"] == {"premium": 1}
    row = next(s for s in body["recent_schools"] if s["id"] == str(premium_school.id))
    assert row["student_count"] == 1
    assert isinstance(body["top_schools"], list)


@pytest.mark.django_db
def test_platform_revenue_aggregates_schools():
    """Super admin sees per-school tier/MRR/ARR and platform totals."""
    from decimal import Decimal

    from tests.factories import (
        AcademicYearFactory,
        FeeCategoryFactory,
        FeeInvoiceFactory,
        FeeStructureFactory,
        GradeFactory,
        PaymentFactory,
        StudentFactory,
        StudentUserFactory,
    )

    premium_school = SchoolFactory(subscription_tier="premium")
    basic_school = SchoolFactory(subscription_tier="basic")
    sa = UserFactory(role="super_admin", school=None, is_staff=True)

    # Anchor every factory dependency to the premium school so the test
    # creates exactly two schools (premium + basic), no orphans.
    grade = GradeFactory(school=premium_school)
    category = FeeCategoryFactory(school=premium_school)
    ay = AcademicYearFactory(school=premium_school)
    fs = FeeStructureFactory(school=premium_school, academic_year=ay, grade=grade, fee_category=category)
    students = [StudentFactory(user=StudentUserFactory(school=premium_school)) for _ in range(3)]
    invoice = FeeInvoiceFactory(student=students[0], academic_year=ay, fee_structure=fs)
    # collected_by=sa avoids PaymentFactory's AdminUserFactory sub-factory,
    # which would otherwise create yet another school.
    PaymentFactory(invoice=invoice, collected_by=sa, amount=Decimal("5000.00"), status="successful")

    res = client_as(sa).get("/api/v1/auth/platform/revenue/")

    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    # 3 premium students × 60 = 180; basic contributes 0
    assert body["total_mrr"] == 180
    assert body["total_arr"] == 1800
    assert body["schools_by_tier"] == {"premium": 1, "basic": 1}
    rows = {r["id"]: r for r in body["schools"]}
    assert rows[str(premium_school.id)]["mrr"] == 180
    assert rows[str(premium_school.id)]["revenue"] == 5000.0
    assert rows[str(basic_school.id)]["mrr"] == 0


@pytest.mark.django_db
def test_platform_revenue_rejects_school_admins():
    school = SchoolFactory(subscription_tier="premium")
    admin = AdminUserFactory(school=school)

    res = client_as(admin).get("/api/v1/auth/platform/revenue/")

    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_super_admin_audit_log_spans_schools():
    """Super admin reads the platform-wide audit trail; admins stay scoped."""
    from services.auth.models import AuditLog

    school_a = SchoolFactory(subscription_tier="standard")
    school_b = SchoolFactory(subscription_tier="standard")
    admin_a = AdminUserFactory(school=school_a)
    sa = UserFactory(role="super_admin", school=None, is_staff=True)
    AuditLog.objects.create(
        school=school_a,
        user=admin_a,
        action="plan_tier_change",
        resource_type="school",
        resource_id=str(school_a.id),
    )
    AuditLog.objects.create(school=school_b, user=sa, action="login", resource_type="user", resource_id=str(sa.id))

    res_sa = client_as(sa).get("/api/v1/auth/audit-log/")
    assert res_sa.status_code == status.HTTP_200_OK
    school_ids = {str(row["school"]) for row in res_sa.json()["results"]}
    assert str(school_a.id) in school_ids and str(school_b.id) in school_ids

    res_admin = client_as(admin_a).get("/api/v1/auth/audit-log/")
    school_ids_admin = {str(row["school"]) for row in res_admin.json()["results"]}
    assert school_ids_admin <= {str(school_a.id)}
