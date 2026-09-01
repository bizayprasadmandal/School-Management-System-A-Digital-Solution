"""Inventory / Store Management URL Configuration."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssetTagViewSet,
    BarcodeViewSet,
    CategoryViewSet,
    InventoryAlertViewSet,
    InventoryAnalyticsViewSet,
    InventoryBudgetViewSet,
    InventoryCatalogExtendedViewSet,
    InventoryCatalogItemViewSet,
    InventoryCatalogViewSet,
    InventoryCompositeItemViewSet,
    InventoryItemViewSet,
    InventoryLeaseAgreementExtendedViewSet,
    InventoryLeaseAgreementViewSet,
    InventoryPartsViewSet,
    InventoryPricingHistoryViewSet,
    InventoryReportViewSet,
    InventorySettingsViewSet,
    InventorySubscriptionPlanViewSet,
    InventorySubscriptionViewSet,
    InventorySupplierPerformanceViewSet,
    InventoryTransferRouteViewSet,
    InvoicePaymentViewSet,
    InvoiceViewSet,
    PurchaseOrderItemViewSet,
    PurchaseOrderViewSet,
    PurchaseRequisitionItemViewSet,
    PurchaseRequisitionViewSet,
    ReturnRequestViewSet,
    StockAdjustmentViewSet,
    StockCountScheduleViewSet,
    StockLevelViewSet,
    StockMovementViewSet,
    StockTransferItemViewSet,
    StockTransferViewSet,
    SupplierRatingViewSet,
    SupplierViewSet,
    WarehouseLocationViewSet,
    WarehouseViewSet,
    WarehouseZoneViewSet,
    WarrantyClaimExtendedViewSet,
)

app_name = "inventory_v1"

router = DefaultRouter()

router.register(r"category", CategoryViewSet, basename="category")
router.register(r"supplier", SupplierViewSet, basename="supplier")
router.register(r"inventory-item", InventoryItemViewSet, basename="inventory-item")
router.register(r"stock-movement", StockMovementViewSet, basename="stock-movement")
router.register(r"purchase-order", PurchaseOrderViewSet, basename="purchase-order")
router.register(r"purchase-order-item", PurchaseOrderItemViewSet, basename="purchase-order-item")
router.register(r"warehouse", WarehouseViewSet, basename="warehouse")
router.register(r"warehouse-zone", WarehouseZoneViewSet, basename="warehouse-zone")
router.register(r"warehouse-location", WarehouseLocationViewSet, basename="warehouse-location")
router.register(r"stock-level", StockLevelViewSet, basename="stock-level")
router.register(r"stock-adjustment", StockAdjustmentViewSet, basename="stock-adjustment")
router.register(r"stock-count-schedule", StockCountScheduleViewSet, basename="stock-count-schedule")
router.register(r"stock-transfer", StockTransferViewSet, basename="stock-transfer")
router.register(r"stock-transfer-item", StockTransferItemViewSet, basename="stock-transfer-item")
router.register(r"purchase-requisition", PurchaseRequisitionViewSet, basename="purchase-requisition")
router.register(r"purchase-requisition-item", PurchaseRequisitionItemViewSet, basename="purchase-requisition-item")
router.register(r"invoice", InvoiceViewSet, basename="invoice")
router.register(r"invoice-payment", InvoicePaymentViewSet, basename="invoice-payment")
router.register(r"return-request", ReturnRequestViewSet, basename="return-request")
router.register(r"warranty-claim-extended", WarrantyClaimExtendedViewSet, basename="warranty-claim-extended")
router.register(r"barcode", BarcodeViewSet, basename="barcode")
router.register(r"asset-tag", AssetTagViewSet, basename="asset-tag")
router.register(r"supplier-rating", SupplierRatingViewSet, basename="supplier-rating")
router.register(r"inventory-alert", InventoryAlertViewSet, basename="inventory-alert")
router.register(r"inventory-report", InventoryReportViewSet, basename="inventory-report")
router.register(r"inventory-analytics", InventoryAnalyticsViewSet, basename="inventory-analytics")
router.register(r"inventory-settings", InventorySettingsViewSet, basename="inventory-settings")
router.register(
    r"inventory-subscription-plan", InventorySubscriptionPlanViewSet, basename="inventory-subscription-plan"
)
router.register(r"inventory-subscription", InventorySubscriptionViewSet, basename="inventory-subscription")
router.register(r"inventory-budget", InventoryBudgetViewSet, basename="inventory-budget")
router.register(r"inventory-lease-agreement", InventoryLeaseAgreementViewSet, basename="inventory-lease-agreement")
router.register(
    r"inventory-supplier-performance", InventorySupplierPerformanceViewSet, basename="inventory-supplier-performance"
)
router.register(r"inventory-catalog", InventoryCatalogViewSet, basename="inventory-catalog")
router.register(r"inventory-catalog-item", InventoryCatalogItemViewSet, basename="inventory-catalog-item")
router.register(r"inventory-parts", InventoryPartsViewSet, basename="inventory-parts")
router.register(r"inventory-composite-item", InventoryCompositeItemViewSet, basename="inventory-composite-item")
router.register(r"inventory-transfer-route", InventoryTransferRouteViewSet, basename="inventory-transfer-route")
router.register(
    r"inventory-lease-agreement-extended",
    InventoryLeaseAgreementExtendedViewSet,
    basename="inventory-lease-agreement-extended",
)
router.register(r"inventory-catalog-extended", InventoryCatalogExtendedViewSet, basename="inventory-catalog-extended")
router.register(r"inventory-pricing-history", InventoryPricingHistoryViewSet, basename="inventory-pricing-history")

urlpatterns = [
    path("", include(router.urls)),
]
