"""Inventory / Store Management — Items, categories, suppliers, stock movements, purchase orders."""

import uuid
from decimal import Decimal
from django.db import models
from services.auth.models import School, User


class Category(models.Model):
    """Item categories (e.g., Stationery, Uniforms, Sports Equipment, Cleaning)."""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="inventory_categories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_categories"
        unique_together = [("school", "name")]
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Vendors who supply inventory items to the school."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        DISCONTINUED = "discontinued", "Discontinued"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="suppliers")
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=254, blank=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(max_length=100, blank=True, help_text="e.g. Net 30")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inv_suppliers"
        ordering = ["name"]

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    """Individual stock-keeping items in the school store."""

    class Unit(models.TextChoices):
        PIECE = "piece", "Piece"
        PACK = "pack", "Pack"
        BOX = "box", "Box"
        SET = "set", "Set"
        LITER = "liter", "Liter"
        KILOGRAM = "kilogram", "Kilogram"
        METER = "meter", "Meter"
        ROLL = "roll", "Roll"
        PAIR = "pair", "Pair"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="inventory_items")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="items",
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="supplied_items",
    )
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, blank=True, help_text="Stock Keeping Unit / internal code")
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_stock = models.PositiveIntegerField(default=0, help_text="Current quantity on hand")
    minimum_stock = models.PositiveIntegerField(default=0, help_text="Low-stock alert threshold")
    maximum_stock = models.PositiveIntegerField(default=0, help_text="Maximum desired stock level")
    location = models.CharField(max_length=100, blank=True, help_text="Shelf/room location in store")
    barcode = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inv_items"
        unique_together = [("school", "sku")]
        ordering = ["name"]

    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock if self.minimum_stock > 0 else False

    @property
    def stock_value(self):
        return self.current_stock * self.unit_price

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"


class StockMovement(models.Model):
    """Every change to inventory stock — inbound, outbound, adjustment, return."""

    class MovementType(models.TextChoices):
        PURCHASE = "purchase", "Purchase (Inbound)"
        ISSUE = "issue", "Issue (Outbound)"
        ADJUSTMENT = "adjustment", "Adjustment"
        RETURN = "return", "Return (Inbound)"
        TRANSFER = "transfer", "Transfer"
        DAMAGE = "damage", "Damage / Write-off"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name="movements",
    )
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity = models.IntegerField(help_text="Positive for inbound, negative for outbound")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    reference_number = models.CharField(max_length=50, blank=True, help_text="PO #, invoice #, etc.")
    reference_type = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="stock_movements",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_stock_movements"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.item.name} ({self.movement_type}: {self.quantity})"


class PurchaseOrder(models.Model):
    """Purchase orders sent to suppliers."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        CONFIRMED = "confirmed", "Confirmed"
        PARTIALLY_RECEIVED = "partially_received", "Partially Received"
        RECEIVED = "received", "Fully Received"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="purchase_orders")
    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="purchase_orders",
    )
    order_date = models.DateField()
    expected_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=25, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    ordered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="ordered_purchase_orders",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inv_purchase_orders"
        ordering = ["-order_date"]

    def __str__(self):
        return self.order_number


class PurchaseOrderItem(models.Model):
    """Line items within a purchase order."""
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items",
    )
    item = models.ForeignKey(
        InventoryItem, on_delete=models.CASCADE, related_name="purchase_order_items",
    )
    quantity_ordered = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=14, decimal_places=2)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "inv_purchase_order_items"
        unique_together = [("purchase_order", "item")]

    def __str__(self):
        return f"{self.item.name} ({self.quantity_ordered} x ${self.unit_price})"
