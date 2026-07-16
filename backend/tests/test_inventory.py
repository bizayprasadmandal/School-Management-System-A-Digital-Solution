"""Tests for Inventory Service — Category, Supplier, InventoryItem, StockMovement, PurchaseOrder."""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

INVENTORY_CATEGORIES = f"{API_PREFIX}/inventory/categories/"
INVENTORY_SUPPLIERS = f"{API_PREFIX}/inventory/suppliers/"
INVENTORY_ITEMS = f"{API_PREFIX}/inventory/items/"
INVENTORY_MOVEMENTS = f"{API_PREFIX}/inventory/movements/"
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
        from tests.factories import SchoolFactory, AdminUserFactory
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
            school=school, name="Best Suppliers",
            contact_person="Jane Doe", email="jane@best.com",
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
            school=school, name="FurniSupplier",
            contact_person="Bob", email="bob@furni.com",
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
            school=school, category=cat, name="Laptop",
            sku="LAP-001", quantity=20,
            unit_price=Decimal("999.99"), reorder_level=5,
        )
        r = admin_client.get(f"{INVENTORY_ITEMS}?search=Laptop")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_low_stock_filter(self, admin_client, school):
        from services.inventory.models import Category, InventoryItem
        cat = Category.objects.create(school=school, name="Consumables")
        InventoryItem.objects.create(
            school=school, category=cat, name="Paper",
            sku="PAP-001", quantity=3,
            unit_price=Decimal("5.00"), reorder_level=10,
        )
        r = admin_client.get(f"{INVENTORY_ITEMS}?low_stock=true")
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data["results"]) >= 1

    def test_adjust_stock(self, admin_client, school):
        from services.inventory.models import Category, InventoryItem
        cat = Category.objects.create(school=school, name="Office")
        item = InventoryItem.objects.create(
            school=school, category=cat, name="Whiteboard Markers",
            sku="MRK-001", quantity=20,
            unit_price=Decimal("2.50"), reorder_level=5,
        )
        r = admin_client.post(
            f"{INVENTORY_ITEMS}{item.id}/adjust-stock/",
            {"quantity": 5, "adjustment_type": "add", "reason": "Restock"},
            format="json",
        )
        assert r.status_code == status.HTTP_200_OK
        item.refresh_from_db()
        assert item.quantity == 25


@pytest.mark.django_db
class TestStockMovements:

    def test_record_movement(self, admin_client, school):
        from services.inventory.models import Category, InventoryItem
        cat = Category.objects.create(school=school, name="Lab")
        item = InventoryItem.objects.create(
            school=school, category=cat, name="Beaker Set",
            sku="BEK-001", quantity=50, unit_price=Decimal("30.00"),
            reorder_level=5,
        )
        payload = {
            "item": item.id,
            "movement_type": "out",
            "quantity": 5,
            "reason": "Issued to Science Lab",
        }
        r = admin_client.post(INVENTORY_MOVEMENTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        item.refresh_from_db()
        assert item.quantity == 45


@pytest.mark.django_db
class TestPurchaseOrders:

    def test_create_purchase_order(self, admin_client, school):
        from services.inventory.models import Category, Supplier, InventoryItem
        cat = Category.objects.create(school=school, name="Lab Equipment")
        supplier = Supplier.objects.create(
            school=school, name="LabSupplier",
            contact_person="Tom", email="tom@lab.com",
        )
        item = InventoryItem.objects.create(
            school=school, category=cat, name="Microscope",
            sku="MIC-001", quantity=5,
            unit_price=Decimal("500.00"), reorder_level=1,
        )
        payload = {
            "supplier": supplier.id,
            "order_date": date.today().isoformat(),
            "expected_delivery": (date.today() + timedelta(days=14)).isoformat(),
            "items": [{"item": item.id, "quantity": 3, "unit_price": "480.00"}],
        }
        r = admin_client.post(INVENTORY_PURCHASE_ORDERS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["status"] == "pending"

    def test_receive_purchase_order(self, admin_client, school):
        from services.inventory.models import Category, Supplier, InventoryItem, PurchaseOrder, PurchaseOrderItem
        cat = Category.objects.create(school=school, name="Books")
        supplier = Supplier.objects.create(
            school=school, name="BookSupplier",
            contact_person="Sue", email="sue@books.com",
        )
        item = InventoryItem.objects.create(
            school=school, category=cat, name="Textbook",
            sku="TXT-001", quantity=10,
            unit_price=Decimal("50.00"), reorder_level=2,
        )
        po = PurchaseOrder.objects.create(
            school=school, supplier=supplier,
            order_date=date.today(), status="approved",
        )
        PurchaseOrderItem.objects.create(
            purchase_order=po, item=item,
            quantity=5, unit_price=Decimal("50.00"),
        )
        r = admin_client.post(f"{INVENTORY_PURCHASE_ORDERS}{po.id}/receive/")
        assert r.status_code == status.HTTP_200_OK
        po.refresh_from_db()
        assert po.status == "received"
        item.refresh_from_db()
        assert item.quantity == 15
