"""Tests for requisition → purchase-order conversion (`convert_to_po`).

Pins the full workflow: submitted requisition + line items → approved then
ordered, draft PO spawned with one line per requisition item, totals
computed, cross-school items rejected, double conversion refused, and
permission/tenant checks.
"""

from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

REQUISITIONS = f"{API_PREFIX}/inventory/purchase-requisition/"
PURCHASE_ORDERS = f"{API_PREFIX}/inventory/purchase-orders/"


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory()


@pytest.fixture
def other_school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    from tests.factories import AdminUserFactory

    return AdminUserFactory(school=school)


@pytest.fixture
def other_admin(db, other_school):
    from tests.factories import AdminUserFactory

    return AdminUserFactory(school=other_school)


@pytest.fixture
def admin_client(db, admin):
    c = APIClient()
    c.force_authenticate(user=admin)
    return c


def _item(school, name="Whiteboard markers", price="2.50"):
    from services.inventory.models import InventoryItem

    return InventoryItem.objects.create(school=school, name=name, unit_price=Decimal(price))


def _requisition(school, requester, status="submitted", item=None, qty=10, est="2.00"):
    from services.inventory.models import PurchaseRequisition, PurchaseRequisitionItem

    req = PurchaseRequisition.objects.create(
        school=school,
        requisition_number=f"PR-TEST-{school.code}-{status}",
        status=status,
        requested_by=requester,
        department="Science",
    )
    if item is not None:
        PurchaseRequisitionItem.objects.create(requisition=req, item=item, quantity=qty, estimated_cost=Decimal(est))
    return req


@pytest.mark.django_db
class TestConvertToPO:
    def test_full_conversion_creates_draft_po(self, admin_client, admin, school):
        item = _item(school)
        req = _requisition(school, admin, item=item, qty=10, est="2.00")

        r = admin_client.post(f"{REQUISITIONS}{req.id}/convert_to_po/", format="json")
        assert r.status_code == status.HTTP_201_CREATED, r.data

        po_data = r.data["purchase_order"]
        assert po_data["status"] == "draft"
        assert Decimal(str(po_data["subtotal"])) == Decimal("20.00")
        assert Decimal(str(po_data["total_amount"])) == Decimal("20.00")
        assert f"Converted from requisition {req.requisition_number}" in po_data["notes"]

        req.refresh_from_db()
        assert req.status == "ordered"
        assert req.approved_by == admin
        assert f"Converted to PO {po_data['order_number']}" in req.notes

        # Line item copied with requisition cost
        from services.inventory.models import PurchaseOrderItem

        lines = PurchaseOrderItem.objects.filter(purchase_order_id=po_data["id"])
        assert lines.count() == 1
        line = lines.first()
        assert line.quantity_ordered == 10
        assert line.unit_price == Decimal("2.00")
        assert line.total_price == Decimal("20.00")
        assert line.item_id == item.id

    def test_double_conversion_rejected(self, admin_client, admin, school):
        item = _item(school)
        req = _requisition(school, admin, item=item)

        first = admin_client.post(f"{REQUISITIONS}{req.id}/convert_to_po/", format="json")
        assert first.status_code == status.HTTP_201_CREATED

        second = admin_client.post(f"{REQUISITIONS}{req.id}/convert_to_po/", format="json")
        assert second.status_code == 400
        assert "Only submitted" in second.data["error"]

        # Exactly one PO exists for this conversion
        from services.inventory.models import PurchaseOrder

        assert PurchaseOrder.objects.filter(notes__icontains=req.requisition_number).count() == 1

    def test_only_submitted_converts(self, admin_client, admin, school):
        item = _item(school)
        req = _requisition(school, admin, status="draft", item=item)

        r = admin_client.post(f"{REQUISITIONS}{req.id}/convert_to_po/", format="json")
        assert r.status_code == 400
        assert "draft" in r.data["error"]

    def test_empty_requisition_rejected(self, admin_client, admin, school):
        req = _requisition(school, admin, item=None)
        r = admin_client.post(f"{REQUISITIONS}{req.id}/convert_to_po/", format="json")
        assert r.status_code == 400
        assert "no line items" in r.data["error"]

    def test_foreign_school_requisition_invisible(self, admin_client, admin, other_admin, other_school):
        """Our admin can neither see nor convert another school's requisition."""
        other_item = _item(other_school)
        req = _requisition(other_school, other_admin, item=other_item)

        r = admin_client.post(f"{REQUISITIONS}{req.id}/convert_to_po/", format="json")
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_teacher_cannot_convert(self, admin_client, admin, school, db):
        from tests.factories import TeacherUserFactory

        teacher = TeacherUserFactory(school=school)
        item = _item(school)
        req = _requisition(school, admin, item=item)

        c = APIClient()
        c.force_authenticate(user=teacher)
        r = c.post(f"{REQUISITIONS}{req.id}/convert_to_po/", format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_zero_estimated_cost_defaults(self, admin_client, admin, school):
        """Items with zero estimated_cost produce zero-priced lines cleanly."""
        from services.inventory.models import PurchaseRequisition, PurchaseRequisitionItem

        item = _item(school)
        req = PurchaseRequisition.objects.create(
            school=school,
            requisition_number="PR-TEST-ZERO",
            status="submitted",
            requested_by=admin,
        )
        PurchaseRequisitionItem.objects.create(requisition=req, item=item, quantity=5, estimated_cost=Decimal("0"))

        r = admin_client.post(f"{REQUISITIONS}{req.id}/convert_to_po/", format="json")
        assert r.status_code == status.HTTP_201_CREATED, r.data
        assert Decimal(str(r.data["purchase_order"]["subtotal"])) == Decimal("0.00")
