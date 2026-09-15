"""Tests for the budget-vs-actual variance report.

Pins: expense-driven actuals for categorized line items (approved/paid
only, within the academic year), manual actual_amount fallback, variance
sign conventions, summary rollups, and tenant isolation.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from services.fees.models import BudgetLineItem, BudgetPlan, ExpenseTracking
from services.students.models import AcademicYear
from tests.factories import AcademicYearFactory, AdminUserFactory, FeeCategoryFactory, SchoolFactory, StudentFactory


def _make_plan(school, total=Decimal("10000.00")):
    student = StudentFactory(school=school)  # ensure school fixture exists
    _ = student
    year = AcademicYearFactory(school=school)
    plan = BudgetPlan.objects.create(
        school=school,
        academic_year=year,
        title="FY Budget",
        total_budget=total,
        status=BudgetPlan.Status.ACTIVE,
    )
    return plan, year


def _add_line(plan, description, budgeted, category=None, manual_actual=Decimal("0")):
    return BudgetLineItem.objects.create(
        budget_plan=plan,
        category=category,
        description=description,
        budgeted_amount=budgeted,
        actual_amount=manual_actual,
    )


def _add_expense(school, category, amount, status="paid", days_ago=30):
    year = AcademicYear.objects.filter(school=school).first()
    expense_date = date.today() - timedelta(days=days_ago)
    # Clamp inside the plan's academic year regardless of today's date.
    if year and year.start_date and expense_date < year.start_date:
        expense_date = year.start_date + timedelta(days=5)
    return ExpenseTracking.objects.create(
        school=school,
        expense_type="supplies",
        description=f"Spend on {category.name}",
        amount=amount,
        expense_date=expense_date,
        category=category,
        status=status,
    )


def _get_variance(admin, plan):
    client = APIClient()
    client.force_authenticate(user=admin)
    return client.get(f"/api/v1/fees/budget-plan/{plan.id}/variance/")


@pytest.mark.django_db
class TestBudgetVariance:
    def test_expense_driven_actual_and_variance(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        plan, _ = _make_plan(school)
        cat = FeeCategoryFactory(school=school)
        line = _add_line(plan, "Lab supplies", Decimal("1000.00"), category=cat)
        _add_expense(school, cat, Decimal("400.00"), status="paid")

        resp = _get_variance(admin, plan)

        assert resp.status_code == 200, resp.content
        body = resp.json()
        li = next(item for item in body["line_items"] if item["id"] == str(line.id))
        assert li["actual_amount"] == "400.00"
        assert li["variance"] == "600.00"  # under budget → positive
        assert li["over_budget"] is False
        assert li["source"] == "expenses"
        assert body["summary"]["total_variance"] == "600.00"

    def test_pending_expenses_not_counted(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        plan, _ = _make_plan(school)
        cat = FeeCategoryFactory(school=school)
        _add_line(plan, "Library", Decimal("500.00"), category=cat)
        _add_expense(school, cat, Decimal("200.00"), status="pending")

        resp = _get_variance(admin, plan)

        li = resp.json()["line_items"][0]
        assert li["actual_amount"] == "0.00"  # pending ≠ spent

    def test_uncategorized_line_uses_manual_actual(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        plan, _ = _make_plan(school)
        _add_line(plan, "Misc", Decimal("300.00"), manual_actual=Decimal("350.00"))

        resp = _get_variance(admin, plan)

        li = resp.json()["line_items"][0]
        assert li["source"] == "manual"
        assert li["variance"] == "-50.00"
        assert li["over_budget"] is True
        assert resp.json()["summary"]["over_budget_lines"] == 1

    def test_summary_rollup(self):
        school = SchoolFactory()
        admin = AdminUserFactory(school=school, is_staff=True)
        plan, _ = _make_plan(school)
        cat = FeeCategoryFactory(school=school)
        _add_line(plan, "A", Decimal("1000.00"), category=cat)
        _add_expense(school, cat, Decimal("400.00"))
        _add_line(plan, "B", Decimal("500.00"), manual_actual=Decimal("600.00"))

        resp = _get_variance(admin, plan)

        summary = resp.json()["summary"]
        assert summary["total_budgeted"] == "1500.00"
        assert summary["total_actual"] == "1000.00"
        assert summary["total_variance"] == "500.00"
        assert summary["line_count"] == 2
        assert summary["over_budget_lines"] == 1

    def test_cross_tenant_variance_rejected(self):
        school = SchoolFactory()
        other = SchoolFactory()
        admin = AdminUserFactory(school=other, is_staff=True)
        plan, _ = _make_plan(school)

        resp = _get_variance(admin, plan)

        assert resp.status_code == 404  # queryset scoping hides foreign plans
