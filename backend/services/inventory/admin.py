"""Inventory / Store Management — Django Admin registrations."""

from django.contrib import admin
from .models import Category, Supplier, InventoryItem, StockMovement, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ["item", "quantity_ordered", "quantity_received", "unit_price", "total_price"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active"]
    list_filter = ["is_active", "school"]
    search_fields = ["name"]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_person", "phone", "email", "status"]
    list_filter = ["status", "school"]
    search_fields = ["name", "contact_person"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "category", "current_stock", "minimum_stock", "unit_price"]
    list_filter = ["category", "is_active", "school"]
    search_fields = ["name", "sku", "barcode"]
    readonly_fields = ["id", "current_stock", "created_at", "updated_at"]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["item", "movement_type", "quantity", "total_amount", "created_at"]
    list_filter = ["movement_type"]
    search_fields = ["item__name", "reference_number"]
    readonly_fields = ["id", "created_at"]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "supplier", "order_date", "total_amount", "status"]
    list_filter = ["status", "school"]
    search_fields = ["order_number", "supplier__name"]
    inlines = [PurchaseOrderItemInline]
    readonly_fields = ["id", "created_at", "updated_at"]
