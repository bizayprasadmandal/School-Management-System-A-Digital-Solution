"""Inventory / Store Management â€” Items, categories, suppliers, stock movements, purchase orders."""

import uuid

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
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
    """Every change to inventory stock â€” inbound, outbound, adjustment, return."""

    class MovementType(models.TextChoices):
        PURCHASE = "purchase", "Purchase (Inbound)"
        ISSUE = "issue", "Issue (Outbound)"
        ADJUSTMENT = "adjustment", "Adjustment"
        RETURN = "return", "Return (Inbound)"
        TRANSFER = "transfer", "Transfer"
        DAMAGE = "damage", "Damage / Write-off"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="movements",
    )
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity = models.IntegerField(help_text="Positive for inbound, negative for outbound")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    reference_number = models.CharField(max_length=50, blank=True, help_text="PO #, invoice #, etc.")
    reference_type = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="purchase_order_items",
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


# =============================================================================
# Warehouse & Location Management
# =============================================================================


class Warehouse(models.Model):
    """Warehouse or storage facility."""

    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_warehouses")
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)
    capacity = models.IntegerField(default=0)
    manager = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_warehouses"

    def __str__(self):
        return f"{self.name} ({self.code})"


class WarehouseZone(models.Model):
    """Zone within a warehouse."""

    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="zones")
    name = models.CharField(max_length=200)
    zone_type = models.CharField(
        max_length=20,
        choices=[("storage", "Storage"), ("shipping", "Shipping"), ("receiving", "Receiving"), ("staging", "Staging")],
    )
    capacity = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_warehouse_zones"

    def __str__(self):
        return f"{self.warehouse.name} - {self.name}"


class WarehouseLocation(models.Model):
    """Specific shelf/bin location in a warehouse zone."""

    zone = models.ForeignKey(WarehouseZone, on_delete=models.CASCADE, related_name="locations")
    aisle = models.CharField(max_length=20, blank=True)
    shelf = models.CharField(max_length=20, blank=True)
    bin_label = models.CharField(max_length=20, blank=True)
    item = models.ForeignKey(
        InventoryItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="warehouse_locations"
    )
    max_capacity = models.IntegerField(default=0)
    current_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_warehouse_locations"

    def __str__(self):
        return f"{self.zone.warehouse.name} / {self.aisle}-{self.shelf}-{self.bin_label}"


class StockLevel(models.Model):
    """Current stock level per warehouse."""

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="stock_levels")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stock_levels")
    quantity = models.IntegerField(default=0)
    reserved = models.IntegerField(default=0)
    available = models.IntegerField(default=0)
    reorder_point = models.IntegerField(default=0)
    last_counted = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inv_stock_levels"
        unique_together = [("item", "warehouse")]

    def __str__(self):
        return f"{self.item.name} @ {self.warehouse.name}: {self.quantity}"


class StockAdjustment(models.Model):
    """Record of stock count adjustments."""

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="stock_adjustments")
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="stock_adjustments", null=True, blank=True
    )
    adjustment_type = models.CharField(
        max_length=20, choices=[("addition", "Addition"), ("subtraction", "Subtraction"), ("correction", "Correction")]
    )
    quantity = models.IntegerField()
    reason = models.TextField(blank=True)
    adjusted_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_stock_adjustments"

    def __str__(self):
        return f"{self.get_adjustment_type_display()}: {self.item.name} ({self.quantity})"


class StockCountSchedule(models.Model):
    """Scheduled cycle counts."""

    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="inventory_count_schedules"
    )
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="count_schedules", null=True, blank=True
    )
    name = models.CharField(max_length=200)
    frequency = models.CharField(
        max_length=20,
        choices=[
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
        ],
    )
    next_count_date = models.DateField()
    last_count_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_count_schedules"

    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"


class StockTransfer(models.Model):
    """Transfer items between warehouses."""

    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="inventory_stock_transfers"
    )
    transfer_number = models.CharField(max_length=50, unique=True)
    source_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="transfers_out")
    dest_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="transfers_in")
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("in_transit", "In Transit"),
            ("received", "Received"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
    )
    requested_by = models.ForeignKey(
        "auth_service.User", on_delete=models.SET_NULL, null=True, related_name="inventory_transfers_requested"
    )
    approved_by = models.ForeignKey(
        "auth_service.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_transfers_approved",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "inv_stock_transfers"

    def __str__(self):
        return f"Transfer {self.transfer_number}: {self.source_warehouse.name} â†’ {self.dest_warehouse.name}"


class StockTransferItem(models.Model):
    """Line items in a stock transfer."""

    transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity_requested = models.IntegerField()
    quantity_sent = models.IntegerField(default=0)
    quantity_received = models.IntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "inv_stock_transfer_items"

    def __str__(self):
        return f"{self.item.name}: {self.quantity_requested} units"


# =============================================================================
# Purchase Requisition
# =============================================================================


class PurchaseRequisition(models.Model):
    """Internal purchase requisition."""

    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="purchase_requisitions")
    requisition_number = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("ordered", "Ordered"),
        ],
        default="draft",
    )
    requested_by = models.ForeignKey(
        "auth_service.User", on_delete=models.SET_NULL, null=True, related_name="purchase_requisitions_requested"
    )
    approved_by = models.ForeignKey(
        "auth_service.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_requisitions_approved",
    )
    priority = models.CharField(
        max_length=20,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("urgent", "Urgent")],
        default="medium",
    )
    justification = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inv_purchase_requisitions"

    def __str__(self):
        return f"PR {self.requisition_number} ({self.get_status_display()})"


class PurchaseRequisitionItem(models.Model):
    """Line items in a purchase requisition."""

    requisition = models.ForeignKey(PurchaseRequisition, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_purchase_requisition_items"

    def __str__(self):
        return f"{self.item.name} ({self.quantity} units)"


# =============================================================================
# Invoicing & Payments
# =============================================================================


class Invoice(models.Model):
    """Supplier invoices."""

    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_invoices")
    purchase_order = models.ForeignKey(
        "PurchaseOrder", on_delete=models.CASCADE, related_name="invoices", null=True, blank=True
    )
    invoice_number = models.CharField(max_length=100)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="invoices")
    invoice_date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("partial", "Partial"),
            ("paid", "Paid"),
            ("overdue", "Overdue"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_invoices"

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.supplier.name}"


class InvoicePayment(models.Model):
    """Payments made against invoices."""

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ("cash", "Cash"),
            ("cheque", "Cheque"),
            ("bank_transfer", "Bank Transfer"),
            ("online", "Online"),
            ("card", "Card"),
        ],
    )
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_invoice_payments"

    def __str__(self):
        return f"Payment {self.amount} for {self.invoice.invoice_number}"


class ReturnRequest(models.Model):
    """Return requests to suppliers."""

    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="inventory_return_requests"
    )
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="return_requests")
    purchase_order = models.ForeignKey(
        "PurchaseOrder", on_delete=models.SET_NULL, null=True, blank=True, related_name="returns"
    )
    quantity = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("shipped", "Shipped"),
            ("received", "Received"),
            ("rejected", "Rejected"),
        ],
        default="draft",
    )
    requested_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True)
    approved_by = models.ForeignKey(
        "auth_service.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="inventory_returns_approved"
    )
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inv_return_requests"

    def __str__(self):
        return f"Return {self.item.name} ({self.quantity} units)"


class WarrantyClaimExtended(models.Model):
    """Extended warranty tracking."""

    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="inventory_warranty_claims_ext"
    )
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="warranty_claims_ext")
    claim_number = models.CharField(max_length=50, unique=True)
    issue_description = models.TextField()
    date_filed = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("filed", "Filed"), ("in_progress", "In Progress"), ("resolved", "Resolved"), ("denied", "Denied")],
        default="filed",
    )
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_warranty_claims_ext"

    def __str__(self):
        return f"Claim {self.claim_number} - {self.item.name}"


# =============================================================================
# Barcode & Tagging
# =============================================================================


class Barcode(models.Model):
    """Barcodes / QR codes for inventory items."""

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="barcodes")
    barcode_type = models.CharField(
        max_length=20, choices=[("qr", "QR Code"), ("ean13", "EAN-13"), ("code128", "Code 128"), ("upc", "UPC")]
    )
    code_value = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_barcodes"

    def __str__(self):
        return f"{self.get_barcode_type_display()}: {self.code_value}"


class AssetTag(models.Model):
    """Asset tags for institutional equipment."""

    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_asset_tags")
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="asset_tags")
    tag_number = models.CharField(max_length=50, unique=True)
    qr_code = models.ImageField(upload_to="inventory/asset_tags/", blank=True, null=True)
    assigned_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("retired", "Retired"), ("lost", "Lost"), ("stolen", "Stolen")],
        default="active",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_asset_tags"

    def __str__(self):
        return f"Tag {self.tag_number} - {self.item.name}"


# =============================================================================
# Supplier Rating & Feedback
# =============================================================================


class SupplierRating(models.Model):
    """Ratings and feedback for suppliers."""

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="ratings")
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="supplier_ratings")
    quality_rating = models.DecimalField(max_digits=3, decimal_places=1)
    delivery_rating = models.DecimalField(max_digits=3, decimal_places=1)
    price_rating = models.DecimalField(max_digits=3, decimal_places=1)
    overall_rating = models.DecimalField(max_digits=3, decimal_places=1)
    comments = models.TextField(blank=True)
    rated_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_supplier_ratings"

    def __str__(self):
        return f"{self.supplier.name}: {self.overall_rating}/10"


# =============================================================================
# Alerts & Notifications
# =============================================================================


class InventoryAlert(models.Model):
    """Automated inventory alerts."""

    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_alerts")
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="alerts")
    alert_type = models.CharField(
        max_length=20,
        choices=[
            ("low_stock", "Low Stock"),
            ("expiring", "Expiring Soon"),
            ("overstocked", "Overstocked"),
            ("price_change", "Price Change"),
        ],
    )
    threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_alerts"

    def __str__(self):
        return f"{self.get_alert_type_display()}: {self.item.name}"


# =============================================================================
# Reports & Analytics
# =============================================================================


class InventoryReport(models.Model):
    """Generated inventory reports."""

    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_reports")
    report_type = models.CharField(
        max_length=30,
        choices=[
            ("stock_summary", "Stock Summary"),
            ("valuation", "Valuation"),
            ("movement", "Movement"),
            ("supplier", "Supplier Analysis"),
            ("obsolescence", "Obsolescence"),
            ("turnover", "Turnover"),
        ],
    )
    title = models.CharField(max_length=200)
    date_from = models.DateField()
    date_to = models.DateField()
    generated_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to="inventory/reports/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_reports"

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"


class InventoryAnalytics(models.Model):
    """Inventory analytics and KPIs."""

    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_analytics")
    period = models.CharField(max_length=20)
    total_items = models.IntegerField(default=0)
    total_value = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    turnover_rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stockout_count = models.IntegerField(default=0)
    overstock_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_analytics"

    def __str__(self):
        return f"Analytics {self.period}: {self.total_items} items"


# =============================================================================
# Settings
# =============================================================================


class InventorySettings(models.Model):
    """Inventory module configuration."""

    school = models.OneToOneField("auth_service.School", on_delete=models.CASCADE, related_name="inventory_settings")
    default_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.SET_NULL, null=True, blank=True, related_name="default_for_settings"
    )
    low_stock_threshold = models.IntegerField(default=10)
    auto_reorder = models.BooleanField(default=False)
    enable_barcode = models.BooleanField(default=True)
    enable_serial_tracking = models.BooleanField(default=False)
    fiscal_year_start_month = models.IntegerField(default=1)
    currency = models.CharField(max_length=3, default="USD")
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inv_settings"

    def __str__(self):
        return f"Inventory Settings - {self.school.name}"


# =============================================================================
# Subscriptions & Budgets
# =============================================================================


class InventorySubscriptionPlan(models.Model):
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="inventory_subscription_plans"
    )
    name = models.CharField(max_length=200)
    plan_type = models.CharField(
        max_length=20, choices=[("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual")]
    )
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    items_included = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_subscription_plans"

    def __str__(self):
        return f"{self.name} ({self.get_plan_type_display()})"


class InventorySubscription(models.Model):
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_subscriptions")
    plan = models.ForeignKey(InventorySubscriptionPlan, on_delete=models.CASCADE, related_name="subscriptions")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="subscriptions")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("cancelled", "Cancelled"), ("expired", "Expired")],
        default="active",
    )
    auto_renew = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_subscriptions"

    def __str__(self):
        return f"{self.plan.name} - {self.supplier.name}"


class InventoryBudget(models.Model):
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_budgets")
    department_name = models.CharField(max_length=200, blank=True)
    fiscal_year = models.IntegerField()
    total_budget = models.DecimalField(max_digits=14, decimal_places=2)
    spent = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_budgets"

    def __str__(self):
        return f"{self.department_name or 'Overall'} Budget FY{self.fiscal_year}"


# =============================================================================
# Leasing & Rentals
# =============================================================================


class InventoryLeaseAgreement(models.Model):
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="inventory_lease_agreements"
    )
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="lease_agreements")
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="lease_agreements", null=True, blank=True
    )
    lease_start = models.DateField()
    lease_end = models.DateField()
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    terms = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("active", "Active"), ("expired", "Expired"), ("terminated", "Terminated")],
        default="active",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_lease_agreements"

    def __str__(self):
        return f"Lease: {self.item.name} ({self.lease_start} to {self.lease_end})"


class InventorySupplierPerformance(models.Model):
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="inventory_supplier_performances"
    )
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="performances")
    evaluation_period = models.CharField(max_length=20)
    quality_score = models.DecimalField(max_digits=3, decimal_places=1)
    delivery_score = models.DecimalField(max_digits=3, decimal_places=1)
    price_score = models.DecimalField(max_digits=3, decimal_places=1)
    overall_score = models.DecimalField(max_digits=3, decimal_places=1)
    comments = models.TextField(blank=True)
    evaluated_by = models.ForeignKey("auth_service.User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_supplier_performances"

    def __str__(self):
        return f"{self.supplier.name} - {self.evaluation_period}: {self.overall_score}/10"


class InventoryCatalog(models.Model):
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_catalogs")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=20, default="1.0")
    effective_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_catalogs"

    def __str__(self):
        return f"{self.name} v{self.version}"


class InventoryCatalogItem(models.Model):
    catalog = models.ForeignKey(InventoryCatalog, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="catalog_entries")
    catalog_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "inv_catalog_items"

    def __str__(self):
        return f"{self.item.name} - {self.catalog.name}"


# =============================================================================
# Parts & Composites
# =============================================================================


class InventoryParts(models.Model):
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_parts")
    name = models.CharField(max_length=200)
    part_number = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="parts")
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_parts"

    def __str__(self):
        return f"{self.name} ({self.part_number})"


class InventoryCompositeItem(models.Model):
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="inventory_composite_items"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_composite_items"

    def __str__(self):
        return self.name


class InventoryTransferRoute(models.Model):
    school = models.ForeignKey(
        "auth_service.School", on_delete=models.CASCADE, related_name="inventory_transfer_routes"
    )
    name = models.CharField(max_length=200)
    origin_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="routes_origin", null=True, blank=True
    )
    dest_warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="routes_destination", null=True, blank=True
    )
    estimated_time_minutes = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_transfer_routes"

    def __str__(self):
        return self.name


class InventoryLeaseAgreementExtended(models.Model):
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_lease_ext")
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="lease_ext")
    supplier_name = models.CharField(max_length=200, blank=True)
    lease_start = models.DateField()
    lease_end = models.DateField()
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[("active", "Active"), ("expired", "Expired")], default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_lease_ext"

    def __str__(self):
        return f"Lease: {self.item.name}"


class InventoryCatalogExtended(models.Model):
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inventory_catalog_ext")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=20, default="1.0")
    effective_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_catalog_ext"

    def __str__(self):
        return f"{self.name} v{self.version}"


class InventoryPricingHistory(models.Model):
    school = models.ForeignKey("auth_service.School", on_delete=models.CASCADE, related_name="inv_pricing_history")
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="pricing_history")
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="pricing_history"
    )
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inv_pricing_history"

    def __str__(self):
        return f"{self.item.name}: {self.unit_price} ({self.effective_date})"
