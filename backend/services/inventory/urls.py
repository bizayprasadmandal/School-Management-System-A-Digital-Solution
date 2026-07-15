"""Inventory / Store Management URL Configuration."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, SupplierViewSet, InventoryItemViewSet,
    StockMovementViewSet, PurchaseOrderViewSet,
)

app_name = "inventory_v1"

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(r"items", InventoryItemViewSet, basename="item")
router.register(r"stock-movements", StockMovementViewSet, basename="stock-movement")
router.register(r"purchase-orders", PurchaseOrderViewSet, basename="purchase-order")

urlpatterns = [
    path("", include(router.urls)),
]
