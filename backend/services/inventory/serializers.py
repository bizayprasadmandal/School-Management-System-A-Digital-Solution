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
        fields = ["id", "school", "on_delete", "name", "description", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
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
        read_only_fields = ["id", "created_at", "updated_at"]


class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "category",
            "on_delete",
            "supplier",
            "on_delete",
            "name",
            "sku",
            "description",
            "unit",
            "unit_price",
            "current_stock",
            "minimum_stock",
            "maximum_stock",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = [
            "id",
            "id",
            "item",
            "on_delete",
            "movement_type",
            "quantity",
            "unit_price",
            "total_amount",
            "reference_number",
            "reference_type",
            "notes",
            "performed_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "order_number",
            "supplier",
            "on_delete",
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
        read_only_fields = ["id", "created_at", "updated_at"]


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = [
            "id",
            "purchase_order",
            "on_delete",
            "item",
            "on_delete",
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
        fields = [
            "id",
            "school",
            "on_delete",
            "name",
            "code",
            "address",
            "capacity",
            "manager",
            "on_delete",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class WarehouseZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseZone
        fields = ["id", "warehouse", "on_delete", "name", "zone_type", "capacity", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class WarehouseLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseLocation
        fields = [
            "id",
            "zone",
            "on_delete",
            "aisle",
            "shelf",
            "bin_label",
            "item",
            "on_delete",
            "max_capacity",
            "current_quantity",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StockLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockLevel
        fields = [
            "id",
            "item",
            "on_delete",
            "warehouse",
            "on_delete",
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
        fields = [
            "id",
            "item",
            "on_delete",
            "warehouse",
            "on_delete",
            "adjustment_type",
            "quantity",
            "reason",
            "adjusted_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StockCountScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockCountSchedule
        fields = [
            "id",
            "school",
            "on_delete",
            "warehouse",
            "on_delete",
            "name",
            "frequency",
            "next_count_date",
            "last_count_date",
            "assigned_to",
            "on_delete",
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
            "on_delete",
            "transfer_number",
            "source_warehouse",
            "on_delete",
            "dest_warehouse",
            "on_delete",
            "status",
            "requested_by",
            "on_delete",
            "approved_by",
            "on_delete",
            "notes",
            "created_at",
            "received_at",
        ]
        read_only_fields = ["id", "created_at"]


class StockTransferItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockTransferItem
        fields = [
            "id",
            "transfer",
            "on_delete",
            "item",
            "on_delete",
            "quantity_requested",
            "quantity_sent",
            "quantity_received",
            "notes",
        ]
        read_only_fields = ["id"]


class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequisition
        fields = [
            "id",
            "school",
            "on_delete",
            "requisition_number",
            "department",
            "status",
            "requested_by",
            "on_delete",
            "approved_by",
            "on_delete",
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
        fields = [
            "id",
            "requisition",
            "on_delete",
            "item",
            "on_delete",
            "quantity",
            "estimated_cost",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "id",
            "school",
            "on_delete",
            "purchase_order",
            "on_delete",
            "invoice_number",
            "supplier",
            "on_delete",
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
            "on_delete",
            "payment_date",
            "amount",
            "payment_method",
            "reference_number",
            "notes",
            "created_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReturnRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnRequest
        fields = [
            "id",
            "school",
            "on_delete",
            "item",
            "on_delete",
            "purchase_order",
            "on_delete",
            "quantity",
            "reason",
            "status",
            "requested_by",
            "on_delete",
            "approved_by",
            "on_delete",
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
            "on_delete",
            "item",
            "on_delete",
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
        fields = ["id", "item", "on_delete", "barcode_type", "code_value", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class AssetTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetTag
        fields = [
            "id",
            "school",
            "on_delete",
            "item",
            "on_delete",
            "tag_number",
            "qr_code",
            "assigned_date",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SupplierRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierRating
        fields = [
            "id",
            "school",
            "supplier",
            "on_delete",
            "on_delete",
            "quality_rating",
            "delivery_rating",
            "price_rating",
            "overall_rating",
            "comments",
            "rated_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAlert
        fields = [
            "id",
            "school",
            "on_delete",
            "item",
            "on_delete",
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
        fields = [
            "id",
            "school",
            "on_delete",
            "report_type",
            "title",
            "date_from",
            "date_to",
            "generated_by",
            "on_delete",
            "file",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAnalytics
        fields = [
            "id",
            "school",
            "on_delete",
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
            "on_delete",
            "default_warehouse",
            "on_delete",
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
        fields = ["id", "school", "on_delete", "name", "plan_type", "cost", "items_included", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class InventorySubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventorySubscription
        fields = [
            "id",
            "school",
            "on_delete",
            "plan",
            "on_delete",
            "supplier",
            "on_delete",
            "start_date",
            "end_date",
            "status",
            "auto_renew",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryBudget
        fields = [
            "id",
            "school",
            "on_delete",
            "department_name",
            "fiscal_year",
            "total_budget",
            "spent",
            "notes",
            "is_approved",
            "approved_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryLeaseAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLeaseAgreement
        fields = [
            "id",
            "school",
            "on_delete",
            "item",
            "on_delete",
            "supplier",
            "on_delete",
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
            "on_delete",
            "supplier",
            "on_delete",
            "evaluation_period",
            "quality_score",
            "delivery_score",
            "price_score",
            "overall_score",
            "comments",
            "evaluated_by",
            "on_delete",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCatalog
        fields = [
            "id",
            "school",
            "on_delete",
            "name",
            "description",
            "version",
            "effective_date",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryCatalogItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCatalogItem
        fields = ["id", "catalog", "on_delete", "item", "on_delete", "catalog_price", "notes"]
        read_only_fields = ["id"]


class InventoryPartsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryParts
        fields = [
            "id",
            "school",
            "on_delete",
            "name",
            "part_number",
            "category",
            "on_delete",
            "unit_cost",
            "quantity_in_stock",
            "reorder_level",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryCompositeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCompositeItem
        fields = [
            "id",
            "school",
            "on_delete",
            "name",
            "description",
            "quantity",
            "unit_cost",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryTransferRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryTransferRoute
        fields = [
            "id",
            "school",
            "on_delete",
            "name",
            "origin_warehouse",
            "on_delete",
            "dest_warehouse",
            "on_delete",
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
            "on_delete",
            "item",
            "on_delete",
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
        fields = [
            "id",
            "school",
            "on_delete",
            "name",
            "description",
            "version",
            "effective_date",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class InventoryPricingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryPricingHistory
        fields = [
            "id",
            "school",
            "on_delete",
            "item",
            "on_delete",
            "supplier",
            "on_delete",
            "unit_price",
            "effective_date",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
