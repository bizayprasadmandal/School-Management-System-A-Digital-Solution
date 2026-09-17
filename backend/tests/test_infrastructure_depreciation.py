"""Tests for infrastructure asset-depreciation and PM→WorkOrder tasks.

Pins:
- depreciation math (straight line, floor at zero, month counting, skip rules)
- bookkeeping: Dr 5100 / Cr 1900 posted per school, idempotent by month key
- school scoping (school_id arg) and tenant isolation
- PM→WorkOrder: creation on due, dedupe while a [PM] WO is open, next_due
  advance by frequency, school scoping
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from tests.url_helpers import API_PREFIX  # noqa: F401


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory(code="DEP1")


@pytest.fixture
def other_school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory(code="DEP2")


def _asset(school, **kw):
    from services.infrastructure.models import Asset

    defaults = dict(
        school=school,
        asset_tag=f"AT-{kw.pop('tag', 'x')}",
        name="Projector",
        asset_type=Asset.AssetType.PROJECTOR,
        purchase_date=timezone.now().date() - timedelta(days=400),
        purchase_cost=Decimal("12000.00"),
        current_value=Decimal("12000.00"),
    )
    defaults.update(kw)
    return Asset.objects.create(**defaults)


# ── Depreciation math ───────────────────────────────────────────────────────


@pytest.mark.django_db
class TestDepreciationEngine:
    def test_depreciates_value_and_posts_balanced_entries(self, school):
        from services.infrastructure.tasks import run_monthly_depreciation

        asset = _asset(school, tag="p1")  # projector: 5y life → 200/month
        # 400 days ≈ 13 months elapsed
        result = run_monthly_depreciation.apply(args=[school.id]).get()
        asset.refresh_from_db()

        assert asset.current_value < asset.purchase_cost
        assert result["assets_updated"] >= 1
        assert result["schools"] == 1
        assert result["expense_posted"] > 0

        from services.fees.models import AccountingEntry

        entries = AccountingEntry.objects.filter(
            school=school, reference_type="depreciation", reference_id=result["month"] + f"-{school.id}"
        )
        debit = entries.filter(entry_type=AccountingEntry.EntryType.DEBIT).first()
        credit = entries.filter(entry_type=AccountingEntry.EntryType.CREDIT).first()
        assert debit and credit
        assert debit.account_code == "5100"
        assert credit.account_code == "1900"
        assert debit.amount == credit.amount == Decimal(str(result["expense_posted"]))

    def test_idempotent_rerun_never_double_posts(self, school):
        from services.fees.models import AccountingEntry
        from services.infrastructure.tasks import run_monthly_depreciation

        _asset(school, tag="p2")
        run_monthly_depreciation.apply(args=[school.id]).get()
        run_monthly_depreciation.apply(args=[school.id]).get()

        count = AccountingEntry.objects.filter(school=school, reference_type="depreciation").count()
        assert count == 2  # one debit + one credit, not four

    def test_zero_cost_and_retired_assets_skipped(self, school):
        from services.fees.models import AccountingEntry
        from services.infrastructure.tasks import run_monthly_depreciation

        _asset(school, tag="z", purchase_cost=Decimal("0"))
        _asset(
            school,
            tag="r",
            status="retired",
        )
        result = run_monthly_depreciation.apply(args=[school.id]).get()

        assert result["expense_posted"] == 0
        assert AccountingEntry.objects.filter(school=school, reference_type="depreciation").count() == 0

    def test_recently_purchased_no_expense(self, school):
        from services.fees.models import AccountingEntry
        from services.infrastructure.tasks import run_monthly_depreciation

        _asset(school, tag="new", purchase_date=timezone.now().date() - timedelta(days=5))
        result = run_monthly_depreciation.apply(args=[school.id]).get()

        assert result["expense_posted"] == 0
        assert AccountingEntry.objects.filter(school=school, reference_type="depreciation").count() == 0

    def test_school_scoping_isolation(self, school, other_school):
        from services.fees.models import AccountingEntry
        from services.infrastructure.tasks import run_monthly_depreciation

        _asset(school, tag="own")
        _asset(other_school, tag="foreign")

        run_monthly_depreciation.apply(args=[school.id]).get()

        # Only the target school gets entries; other school untouched
        assert AccountingEntry.objects.filter(school=school, reference_type="depreciation").count() == 2
        assert AccountingEntry.objects.filter(school=other_school, reference_type="depreciation").count() == 0

    def test_value_floors_at_zero(self, school):
        from services.infrastructure.models import Asset
        from services.infrastructure.tasks import _months_elapsed, run_monthly_depreciation

        # it_device: 3y life = 36 months. Purchased 40 months ago → fully depreciated
        asset = _asset(
            school,
            tag="old",
            asset_type=Asset.AssetType.IT_DEVICE,
            purchase_cost=Decimal("3600.00"),
            current_value=Decimal("3600.00"),
            purchase_date=timezone.now().date() - timedelta(days=40 * 31),
        )
        assert _months_elapsed(timezone.now().date(), asset.purchase_date) >= 40

        run_monthly_depreciation.apply(args=[school.id]).get()
        asset.refresh_from_db()
        assert asset.current_value == Decimal("0.00")


# ── PM → WorkOrder ──────────────────────────────────────────────────────────


def _pm(school, **kw):
    from services.infrastructure.models import PreventiveMaintenance

    defaults = dict(
        school=school,
        title="AC filter service",
        frequency=PreventiveMaintenance.Frequency.MONTHLY,
        next_due=timezone.now().date() - timedelta(days=1),
    )
    defaults.update(kw)
    return PreventiveMaintenance.objects.create(**defaults)


@pytest.mark.django_db
class TestGenerateDuePMWorkOrders:
    def test_creates_wo_and_advances_next_due(self, school):
        from services.infrastructure.models import WorkOrder
        from services.infrastructure.tasks import PM_FREQUENCY_DAYS, generate_due_pm_work_orders

        pm = _pm(school)
        result = generate_due_pm_work_orders.apply(args=[school.id]).get()
        pm.refresh_from_db()

        assert result["work_orders_created"] == 1
        wo = WorkOrder.objects.get(school=school, title="[PM] AC filter service")
        assert wo.scheduled_date == pm.next_due - timedelta(days=PM_FREQUENCY_DAYS["monthly"])
        assert wo.status == WorkOrder.Status.OPEN
        assert pm.next_due > timezone.now().date()

    def test_no_duplicate_while_open_wo_exists(self, school):
        from services.infrastructure.tasks import generate_due_pm_work_orders

        _pm(school)
        first = generate_due_pm_work_orders.apply(args=[school.id]).get()
        # next_due advanced past today, but force another due run to prove dedupe
        from services.infrastructure.models import PreventiveMaintenance

        PreventiveMaintenance.objects.update(next_due=timezone.now().date() - timedelta(days=1))
        second = generate_due_pm_work_orders.apply(args=[school.id]).get()

        assert first["work_orders_created"] == 1
        assert second["work_orders_created"] == 0

    def test_future_schedule_skipped(self, school):
        from services.infrastructure.tasks import generate_due_pm_work_orders

        _pm(school, next_due=timezone.now().date() + timedelta(days=10))
        result = generate_due_pm_work_orders.apply(args=[school.id]).get()
        assert result["work_orders_created"] == 0

    def test_paused_schedule_skipped(self, school):
        from services.infrastructure.tasks import generate_due_pm_work_orders

        _pm(school, status="paused")
        result = generate_due_pm_work_orders.apply(args=[school.id]).get()
        assert result["work_orders_created"] == 0

    def test_school_scoping(self, school, other_school):
        from services.infrastructure.models import WorkOrder
        from services.infrastructure.tasks import generate_due_pm_work_orders

        _pm(school)
        _pm(other_school)

        generate_due_pm_work_orders.apply(args=[school.id]).get()

        assert WorkOrder.objects.filter(school=school, title__startswith="[PM]").count() == 1
        assert WorkOrder.objects.filter(school=other_school, title__startswith="[PM]").count() == 0

    def test_completed_wo_does_not_block_new_cycle(self, school):
        from services.infrastructure.models import WorkOrder
        from services.infrastructure.tasks import generate_due_pm_work_orders

        pm = _pm(school)
        # A previously completed [PM] WO from the last cycle
        WorkOrder.objects.create(
            school=school,
            title="[PM] AC filter service",
            description="old cycle",
            status=WorkOrder.Status.COMPLETED,
        )
        result = generate_due_pm_work_orders.apply(args=[school.id]).get()
        pm.refresh_from_db()

        assert result["work_orders_created"] == 1
        assert WorkOrder.objects.filter(school=school, title="[PM] AC filter service").count() == 2
