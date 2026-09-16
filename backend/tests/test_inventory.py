"""Tests for Inventory Service — Category, Supplier, InventoryItem, StockMovement, PurchaseOrder."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

INVENTORY_CATEGORIES = f"{API_PREFIX}/inventory/categories/"
INVENTORY_SUPPLIERS = f"{API_PREFIX}/inventory/suppliers/"
INVENTORY_ITEMS = f"{API_PREFIX}/inventory/items/"
INVENTORY_MOVEMENTS = f"{API_PREFIX}/inventory/stock-movements/"
INVENTORY_PURCHASE_ORDERS = f"{API_PREFIX}/inventory/purchase-orders/"


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    from tests.factories import AdminUserFactory

    return AdminUserFactory(school=school)


@pytest.fixture
def teacher(db, school):
    from tests.factories import TeacherUserFactory

    return TeacherUserFactory(school=school)


@pytest.fixture
def admin_client(db, admin):
    c = APIClient()
    c.force_authenticate(user=admin)
    return c


@pytest.fixture
def teacher_client(db, teacher):
    c = APIClient()
    c.force_authenticate(user=teacher)
    return c


@pytest.mark.django_db
class TestInventoryCategories:

    def test_create_category(self, admin_client, school):
        payload = {"name": "Stationery", "description": "Office and school supplies"}
        r = admin_client.post(INVENTORY_CATEGORIES, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Stationery"

    def test_teacher_cannot_create_category(self, teacher_client):
        payload = {"name": "Test Category"}
        r = teacher_client.post(INVENTORY_CATEGORIES, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_list_categories(self, admin_client, school):
        from services.inventory.models import Category

        Category.objects.create(school=school, name="Electronics")
        r = admin_client.get(INVENTORY_CATEGORIES)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_tenant_isolation_category(self, db):
        from tests.factories import AdminUserFactory, SchoolFactory

        school_a = SchoolFactory(code="INVA")
        school_b = SchoolFactory(code="INVB")
        admin_a = AdminUserFactory(school=school_a)
        from services.inventory.models import Category

        Category.objects.create(school=school_b, name="Secret Cat")
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(INVENTORY_CATEGORIES)
        names = [c["name"] for c in r.data["results"]]
        assert "Secret Cat" not in names


@pytest.mark.django_db
class TestSuppliers:

    def test_create_supplier(self, admin_client, school):
        payload = {
            "name": "Acme Supplies",
            "contact_person": "John Smith",
            "email": "john@acme.com",
            "phone": "+1234567890",
            "address": "123 Main St",
        }
        r = admin_client.post(INVENTORY_SUPPLIERS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["name"] == "Acme Supplies"

    def test_search_suppliers(self, admin_client, school):
        from services.inventory.models import Supplier

        Supplier.objects.create(
            school=school,
            name="Best Suppliers",
            contact_person="Jane Doe",
            email="jane@best.com",
        )
        r = admin_client.get(f"{INVENTORY_SUPPLIERS}?search=Best")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1


@pytest.mark.django_db
class TestInventoryItems:

    def test_create_item(self, admin_client, school):
        from services.inventory.models import Category, Supplier

        cat = Category.objects.create(school=school, name="Furniture")
        supplier = Supplier.objects.create(
            school=school,
            name="FurniSupplier",
            contact_person="Bob",
            email="bob@furni.com",
        )
        payload = {
            "category": cat.id,
            "supplier": supplier.id,
            "name": "Desk Chair",
            "sku": "CHR-001",
            "quantity": 50,
            "unit_price": "150.00",
            "reorder_level": 10,
            "location": "Warehouse A",
        }
        r = admin_client.post(INVENTORY_ITEMS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["sku"] == "CHR-001"

    def test_item_list_and_search(self, admin_client, school):
        from services.inventory.models import Category, InventoryItem

        cat = Category.objects.create(school=school, name="IT Equipment")
        InventoryItem.objects.create(
            school=school,
            category=cat,
            name="Laptop",
            sku="LAP-001",
            current_stock=20,
            unit_price=Decimal("999.99"),
            minimum_stock=5,
        )
        r = admin_client.get(f"{INVENTORY_ITEMS}?search=Laptop")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_low_stock_filter(self, admin_client, school):
        from services.inventory.models import Category, InventoryItem

        cat = Category.objects.create(school=school, name="Consumables")
        InventoryItem.objects.create(
            school=school,
            category=cat,
            name="Paper",
            sku="PAP-001",
            current_stock=3,
            unit_price=Decimal("5.00"),
            minimum_stock=10,
        )
        r = admin_client.get(f"{INVENTORY_ITEMS}?low_stock=true")
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data["results"]) >= 1

    def test_adjust_stock(self, admin_client, school):
        from services.inventory.models import Category, InventoryItem

        cat = Category.objects.create(school=school, name="Office")
        item = InventoryItem.objects.create(
            school=school,
            category=cat,
            name="Whiteboard Markers",
            sku="MRK-001",
            current_stock=20,
            unit_price=Decimal("2.50"),
            minimum_stock=5,
        )
        r = admin_client.post(
            f"{INVENTORY_ITEMS}{item.id}/adjust-stock/",
            {"quantity": 5, "movement_type": "adjustment", "notes": "Restock"},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        item.refresh_from_db()
        assert item.current_stock == 25


@pytest.mark.django_db
class TestStockMovements:

    def test_record_movement(self, admin_client, school):
        from services.inventory.models import Category, InventoryItem

        cat = Category.objects.create(school=school, name="Lab")
        item = InventoryItem.objects.create(
            school=school,
            category=cat,
            name="Beaker Set",
            sku="BEK-001",
            current_stock=50,
            unit_price=Decimal("30.00"),
            minimum_stock=5,
        )
        payload = {
            "item": item.id,
            "movement_type": "issue",
            "quantity": -5,
            "notes": "Issued to Science Lab",
        }
        r = admin_client.post(INVENTORY_MOVEMENTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        item.refresh_from_db()
        assert item.current_stock == 45


@pytest.mark.django_db
class TestPurchaseOrders:

    def test_create_purchase_order(self, admin_client, school):
        from services.inventory.models import Category, InventoryItem, Supplier

        cat = Category.objects.create(school=school, name="Lab Equipment")
        supplier = Supplier.objects.create(
            school=school,
            name="LabSupplier",
            contact_person="Tom",
            email="tom@lab.com",
        )
        item = InventoryItem.objects.create(
            school=school,
            category=cat,
            name="Microscope",
            sku="MIC-001",
            current_stock=5,
            unit_price=Decimal("500.00"),
            minimum_stock=1,
        )
        payload = {
            "supplier": supplier.id,
            "order_date": date.today().isoformat(),
            "expected_date": (date.today() + timedelta(days=14)).isoformat(),
            "items_data": [{"item": item.id, "quantity_ordered": 3, "unit_price": "480.00"}],
        }
        r = admin_client.post(INVENTORY_PURCHASE_ORDERS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["status"] == "draft"

    def test_receive_purchase_order(self, admin_client, school):
        from services.inventory.models import Category, InventoryItem, PurchaseOrder, PurchaseOrderItem, Supplier

        cat = Category.objects.create(school=school, name="Books")
        supplier = Supplier.objects.create(
            school=school,
            name="BookSupplier",
            contact_person="Sue",
            email="sue@books.com",
        )
        item = InventoryItem.objects.create(
            school=school,
            category=cat,
            name="Textbook",
            sku="TXT-001",
            current_stock=10,
            unit_price=Decimal("50.00"),
            minimum_stock=2,
        )
        po = PurchaseOrder.objects.create(
            school=school,
            supplier=supplier,
            order_date=date.today(),
            status="confirmed",
        )
        PurchaseOrderItem.objects.create(
            purchase_order=po,
            item=item,
            quantity_ordered=5,
            unit_price=Decimal("50.00"),
            total_price=Decimal("250.00"),
        )
        r = admin_client.post(
            f"{INVENTORY_PURCHASE_ORDERS}{po.id}/receive/",
            {"items": [{"item_id": str(item.id), "quantity_received": 5}]},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        po.refresh_from_db()
        assert po.status == "received"
        item.refresh_from_db()
        assert item.current_stock == 15


@pytest.mark.django_db
class TestPurchaseOrderApprovalWorkflow:
    """submit -> approve: confirm the PO and post debit/credit accounting entries."""

    def _make_po(self, school, total="1200.00"):
        from services.inventory.models import PurchaseOrder

        return PurchaseOrder.objects.create(
            school=school,
            order_date=date.today(),
            status=PurchaseOrder.Status.SUBMITTED,
            subtotal=Decimal(total),
            total_amount=Decimal(total),
        )

    def test_submit_draft_po(self, admin_client, school):
        from services.inventory.models import Category, InventoryItem, Supplier

        cat = Category.objects.create(school=school, name="WF-Cat")
        supplier = Supplier.objects.create(school=school, name="WF-Supplier")
        InventoryItem.objects.create(
            school=school,
            category=cat,
            name="WF-Item",
            sku="WF-001",
            current_stock=0,
            minimum_stock=0,
        )
        payload = {
            "supplier": supplier.id,
            "order_date": date.today().isoformat(),
            "items_data": [
                {
                    "item": InventoryItem.objects.get(sku="WF-001").id,
                    "quantity_ordered": 2,
                }
            ],
        }
        r = admin_client.post(INVENTORY_PURCHASE_ORDERS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        po_id = r.data["id"]

        r = admin_client.post(f"{INVENTORY_PURCHASE_ORDERS}{po_id}/submit/")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["status"] == "submitted"

    def test_submit_rejected_for_non_draft(self, admin_client, school):
        po = self._make_po(school)
        r = admin_client.post(f"{INVENTORY_PURCHASE_ORDERS}{po.id}/submit/")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_submit_rejected_without_line_items(self, admin_client, school):
        from services.inventory.models import PurchaseOrder

        po = PurchaseOrder.objects.create(school=school, order_date=date.today(), status=PurchaseOrder.Status.DRAFT)
        r = admin_client.post(f"{INVENTORY_PURCHASE_ORDERS}{po.id}/submit/")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_approve_posts_balanced_accounting_entries_once(self, admin_client, school):
        from services.fees.models import AccountingEntry
        from services.fees.models import TransactionLog as FeeTransactionLog

        po = self._make_po(school, total="800.00")
        url = f"{INVENTORY_PURCHASE_ORDERS}{po.id}/approve/"

        r = admin_client.post(url)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["status"] == "confirmed"

        entries = AccountingEntry.objects.filter(reference_type="purchase_order", reference_id=str(po.id))
        assert entries.count() == 2
        debit = entries.get(entry_type="debit")
        credit = entries.get(entry_type="credit")
        assert debit.account_code == "5000" and debit.amount == Decimal("800.00")
        assert credit.account_code == "2000" and credit.amount == Decimal("800.00")

        # Idempotent: a second approval attempt is rejected and never double-posts.
        r2 = admin_client.post(url)
        assert r2.status_code == status.HTTP_400_BAD_REQUEST
        assert entries.count() == 2

        log = FeeTransactionLog.objects.get(transaction_id=f"PO-{po.id}-APPROVAL")
        assert log.amount == Decimal("800.00")

    def test_approve_rejected_for_non_submitted(self, admin_client, school):
        from services.inventory.models import PurchaseOrder

        po = PurchaseOrder.objects.create(school=school, order_date=date.today(), status=PurchaseOrder.Status.DRAFT)
        r = admin_client.post(f"{INVENTORY_PURCHASE_ORDERS}{po.id}/approve/")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_approve_tenant_isolation(self, db):
        from services.inventory.models import PurchaseOrder
        from tests.factories import AdminUserFactory, SchoolFactory

        school_a = SchoolFactory(code="POA1")
        school_b = SchoolFactory(code="POB1")
        po_b = PurchaseOrder.objects.create(
            school=school_b,
            order_date=date.today(),
            status=PurchaseOrder.Status.SUBMITTED,
        )
        admin_a = AdminUserFactory(school=school_a)
        c = APIClient()
        c.force_authenticate(user=admin_a)
        r = c.post(f"{INVENTORY_PURCHASE_ORDERS}{po_b.id}/approve/")
        assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_teacher_cannot_approve(self, teacher_client, school):
        from services.inventory.models import PurchaseOrder

        po = PurchaseOrder.objects.create(
            school=school,
            order_date=date.today(),
            status=PurchaseOrder.Status.SUBMITTED,
        )
        r = teacher_client.post(f"{INVENTORY_PURCHASE_ORDERS}{po.id}/approve/")
        assert r.status_code == status.HTTP_403_FORBIDDEN
