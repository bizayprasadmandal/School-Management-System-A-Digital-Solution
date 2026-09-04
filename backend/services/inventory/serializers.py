"""Inventory / Store Management serializers."""

from rest_framework import serializers

from .models import (
    AssetTag,
    Barcode,
    Category,
    InventoryAlert,
    InventoryAnalytics,
    InventoryBudget,
    InventoryCatalog,
    InventoryCatalogExtended,
    InventoryCatalogItem,
    InventoryCompositeItem,
    InventoryItem,
    InventoryLeaseAgreement,
    InventoryLeaseAgreementExtended,
    InventoryParts,
    InventoryPricingHistory,
    InventoryReport,
    InventorySettings,
    InventorySubscription,
    InventorySubscriptionPlan,
    InventorySupplierPerformance,
    InventoryTransferRoute,
    Invoice,
    InvoicePayment,
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseRequisition,
    PurchaseRequisitionItem,
    ReturnRequest,
    StockAdjustment,
    StockCountSchedule,
    StockLevel,
    StockMovement,
    StockTransfer,
    StockTransferItem,
    Supplier,
    SupplierRating,
    Warehouse,
    WarehouseLocation,
    WarehouseZone,
    WarrantyClaimExtended,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "school", "name", "description", "is_active", "created_at"]
        read_only_fields = ["id", "school", "created_at"]

    def validate(self, attrs):
        # Duplicate (school, name) would hit the DB unique constraint → 500;
        # surface a clean 400 instead (DRF skips its auto validator because
        # school is read-only and never present in the input attrs).
        name = attrs.get("name")
        if name:
            user = self.context["request"].user
            if Category.objects.filter(school_id=user.school_id, name__iexact=name).exists():
                raise serializers.ValidationError({"detail": f"A category named '{name}' already exists."})
        return attrs


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id",
            "school",
            "id",
            "name",
            "contact_person",
            "email",
            "phone",
            "address",
            "tax_id",
            "payment_terms",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "school", "created_at", "updated_at"]


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "school",
            "id",
            "category",
            "supplier",
            "name",
            "sku",
            "description",
            "unit",
            "unit_price",
            "current_stock",
            "minimum_stock",
            "maximum_stock",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "school"]

    def validate(self, attrs):
        # Duplicate (school, sku) would hit the DB unique constraint → 500.
        sku = attrs.get("sku")
        if sku:
            user = self.context["request"].user
            if InventoryItem.objects.filter(school_id=user.school_id, sku__iexact=sku).exists():
                raise serializers.ValidationError({"detail": f"An item with SKU '{sku}' already exists."})
        return attrs

    def validate_category(self, value):
        # Inventory items must stay within the tenant — the category has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Category not found in your school.")
        return value

    def validate_supplier(self, value):
        # Inventory items must stay within the tenant — the supplier has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Supplier not found in your school.")
        return value


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = [
            "id",
            "id",
            "item",
            "movement_type",
            "quantity",
            "unit_price",
            "total_amount",
            "reference_number",
            "reference_type",
            "notes",
            "performed_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_item(self, value):
        # Stock movements inherit tenant scope from the item — reject items
        # from another school.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Item not found in your school.")
        return value

    def validate_performed_by(self, value):
        # Stock movements must stay within the tenant — the performing user
        # has to belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Performed-by user must be in your school.")
        return value


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "school",
            "id",
            "order_number",
            "supplier",
            "order_date",
            "expected_date",
            "status",
            "subtotal",
            "tax_amount",
            "shipping_cost",
            "total_amount",
            "notes",
            "ordered_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "school"]

    def validate_supplier(self, value):
        # Purchase orders must stay within the tenant — the supplier has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Supplier not found in your school.")
        return value


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = [
            "id",
            "purchase_order",
            "item",
            "quantity_ordered",
            "quantity_received",
            "unit_price",
            "total_price",
            "notes",
        ]
        read_only_fields = ["id"]


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ["id", "school", "name", "code", "address", "capacity", "manager", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class WarehouseZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseZone
        fields = ["id", "warehouse", "name", "zone_type", "capacity", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class WarehouseLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseLocation
        fields = ["id", "zone", "aisle", "shelf", "bin_label", "item", "max_capacity", "current_quantity", "created_at"]
        read_only_fields = ["id", "created_at"]


class StockLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockLevel
        fields = [
            "id",
            "item",
            "warehouse",
            "quantity",
            "reserved",
            "available",
            "reorder_point",
            "last_counted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StockAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAdjustment
        fields = ["id", "item", "warehouse", "adjustment_type", "quantity", "reason", "adjusted_by", "created_at"]
        read_only_fields = ["id", "created_at"]


class StockCountScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockCountSchedule
        fields = [
            "id",
            "school",
            "warehouse",
            "name",
            "frequency",
            "next_count_date",
            "last_count_date",
            "assigned_to",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StockTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransfer
        fields = [
            "id",
            "school",
            "transfer_number",
            "source_warehouse",
            "dest_warehouse",
            "status",
            "requested_by",
            "approved_by",
            "notes",
            "created_at",
            "received_at",
        ]
        read_only_fields = ["id", "created_at"]


class StockTransferItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransferItem
        fields = ["id", "transfer", "item", "quantity_requested", "quantity_sent", "quantity_received", "notes"]
        read_only_fields = ["id"]


class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequisition
        fields = [
            "id",
            "school",
            "requisition_number",
            "department",
            "status",
            "requested_by",
            "approved_by",
            "priority",
            "justification",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PurchaseRequisitionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequisitionItem
        fields = ["id", "requisition", "item", "quantity", "estimated_cost", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "school",
            "purchase_order",
            "invoice_number",
            "supplier",
            "invoice_date",
            "due_date",
            "subtotal",
            "tax",
            "total",
            "amount_paid",
            "status",
            "notes",
        ]
        read_only_fields = ["id", "created_at"]


class InvoicePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoicePayment
        fields = [
            "id",
            "invoice",
            "payment_date",
            "amount",
            "payment_method",
            "reference_number",
            "notes",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReturnRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnRequest
        fields = [
            "id",
            "school",
            "item",
            "purchase_order",
            "quantity",
            "reason",
            "status",
            "requested_by",
            "approved_by",
            "refund_amount",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WarrantyClaimExtendedSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarrantyClaimExtended
        fields = [
            "id",
            "school",
            "item",
            "claim_number",
            "issue_description",
            "date_filed",
            "status",
            "resolution_notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barcode
        fields = ["id", "item", "barcode_type", "code_value", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class AssetTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTag
        fields = ["id", "school", "item", "tag_number", "qr_code", "assigned_date", "status", "created_at"]
        read_only_fields = ["id", "created_at"]


class SupplierRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierRating
        fields = [
            "id",
            "school",
            "supplier",
            "quality_rating",
            "delivery_rating",
            "price_rating",
            "overall_rating",
            "comments",
            "rated_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAlert
        fields = [
            "id",
            "school",
            "item",
            "alert_type",
            "threshold",
            "current_value",
            "is_active",
            "notified",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryReport
        fields = ["id", "school", "report_type", "title", "date_from", "date_to", "generated_by", "file", "created_at"]
        read_only_fields = ["id", "created_at"]


class InventoryAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAnalytics
        fields = [
            "id",
            "school",
            "period",
            "total_items",
            "total_value",
            "turnover_rate",
            "average_order_value",
            "stockout_count",
            "overstock_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventorySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventorySettings
        fields = [
            "id",
            "school",
            "default_warehouse",
            "low_stock_threshold",
            "auto_reorder",
            "enable_barcode",
            "enable_serial_tracking",
            "fiscal_year_start_month",
            "currency",
            "tax_rate",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InventorySubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventorySubscriptionPlan
        fields = ["id", "school", "name", "plan_type", "cost", "items_included", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class InventorySubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventorySubscription
        fields = ["id", "school", "plan", "supplier", "start_date", "end_date", "status", "auto_renew", "created_at"]
        read_only_fields = ["id", "created_at"]


class InventoryBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryBudget
        fields = [
            "id",
            "school",
            "department_name",
            "fiscal_year",
            "total_budget",
            "spent",
            "notes",
            "is_approved",
            "approved_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryLeaseAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLeaseAgreement
        fields = [
            "id",
            "school",
            "item",
            "supplier",
            "lease_start",
            "lease_end",
            "monthly_cost",
            "terms",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventorySupplierPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventorySupplierPerformance
        fields = [
            "id",
            "school",
            "supplier",
            "evaluation_period",
            "quality_score",
            "delivery_score",
            "price_score",
            "overall_score",
            "comments",
            "evaluated_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCatalog
        fields = ["id", "school", "name", "description", "version", "effective_date", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class InventoryCatalogItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCatalogItem
        fields = ["id", "catalog", "item", "catalog_price", "notes"]
        read_only_fields = ["id"]


class InventoryPartsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryParts
        fields = [
            "id",
            "school",
            "name",
            "part_number",
            "category",
            "unit_cost",
            "quantity_in_stock",
            "reorder_level",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryCompositeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCompositeItem
        fields = ["id", "school", "name", "description", "quantity", "unit_cost", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class InventoryTransferRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransferRoute
        fields = [
            "id",
            "school",
            "name",
            "origin_warehouse",
            "dest_warehouse",
            "estimated_time_minutes",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryLeaseAgreementExtendedSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLeaseAgreementExtended
        fields = [
            "id",
            "school",
            "item",
            "supplier_name",
            "lease_start",
            "lease_end",
            "monthly_cost",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryCatalogExtendedSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCatalogExtended
        fields = ["id", "school", "name", "description", "version", "effective_date", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class InventoryPricingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryPricingHistory
        fields = ["id", "school", "item", "supplier", "unit_price", "effective_date", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]
