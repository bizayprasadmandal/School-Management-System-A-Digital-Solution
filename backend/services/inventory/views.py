"""Inventory / Store Management — Viewsets with school-scoped CRUD and stock actions."""

import json
import logging
from decimal import Decimal

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db import transaction as db_transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, InventoryItem, PurchaseOrder, PurchaseOrderItem, StockMovement, Supplier
from .serializers import (
    CategorySerializer,
    InventoryItemSerializer,
    PurchaseOrderSerializer,
    StockMovementSerializer,
    SupplierSerializer,
)

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        return Category.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "contact_person", "email", "phone"]
    filterset_fields = ["status"]

    def get_queryset(self):
        return Supplier.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "sku", "description", "barcode"]
    filterset_fields = ["category", "supplier", "is_active"]
    ordering_fields = ["name", "current_stock", "unit_price"]
    ordering = ["name"]

    def get_queryset(self):
        return InventoryItem.objects.filter(school=self.request.user.school).select_related("category", "supplier")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=True, methods=["post"], url_path="adjust-stock")
    def adjust_stock(self, request, pk=None):
        """Add or remove stock and record the movement."""
        item = self.get_object()
        movement_type = request.data.get("movement_type", "adjustment")
        quantity = int(request.data.get("quantity", 0))
        notes = request.data.get("notes", "")

        if quantity == 0:
            return Response({"error": "Quantity must be non-zero"}, status=400)

        with db_transaction.atomic():
            StockMovement.objects.create(
                item=item,
                movement_type=movement_type,
                quantity=quantity,
                unit_price=item.unit_price,
                total_amount=abs(quantity) * item.unit_price,
                notes=notes,
                reference_number=request.data.get("reference_number", ""),
                performed_by=request.user,
            )
            item.current_stock = max(0, item.current_stock + quantity)
            item.save(update_fields=["current_stock"])

        return Response(InventoryItemSerializer(item).data)


class StockMovementViewSet(viewsets.ModelViewSet):
    serializer_class = StockMovementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["item__name", "reference_number", "notes"]
    filterset_fields = ["item", "movement_type", "performed_by"]

    def get_queryset(self):
        return StockMovement.objects.filter(item__school=self.request.user.school).select_related(
            "item", "performed_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save()


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["order_number", "supplier__name", "notes"]
    filterset_fields = ["supplier", "status"]

    def get_queryset(self):
        return (
            PurchaseOrder.objects.filter(school=self.request.user.school)
            .select_related("supplier", "ordered_by")
            .prefetch_related("items__item")
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        raw_items = request.data.get("items_data", "[]")
        if isinstance(raw_items, str):
            try:
                items_data = json.loads(raw_items)
            except (json.JSONDecodeError, TypeError):
                items_data = []
        elif isinstance(raw_items, list):
            items_data = raw_items
        else:
            items_data = []

        # Tenant isolation: resolve every line item against THIS school's
        # inventory before writing anything, so a foreign item aborts cleanly
        # without leaving a partially-created purchase order behind.
        resolved_items = []
        seen_items = set()
        for entry in items_data:
            item_id = entry["item"]
            if item_id in seen_items:
                return Response(
                    {"error": f"Duplicate item '{item_id}' in items_data. Remove duplicates."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            seen_items.add(item_id)
            try:
                item = InventoryItem.objects.get(id=item_id, school=request.user.school)
            except InventoryItem.DoesNotExist:
                return Response(
                    {"error": f"Item '{item_id}' not found in your school."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            resolved_items.append(
                (
                    item,
                    int(entry["quantity_ordered"]),
                    Decimal(str(entry.get("unit_price", item.unit_price))),
                )
            )

        with db_transaction.atomic():
            po = serializer.save(school=request.user.school, ordered_by=request.user)
            subtotal = Decimal("0")
            for item, qty, price in resolved_items:
                total = qty * price
                PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    item=item,
                    quantity_ordered=qty,
                    unit_price=price,
                    total_price=total,
                )
                subtotal += total
            po.subtotal = subtotal
            po.total_amount = subtotal
            po.save(update_fields=["subtotal", "total_amount"])

        return Response(PurchaseOrderSerializer(po).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="receive")
    def receive_items(self, request, pk=None):
        """Receive items against a purchase order, creating stock movements."""
        po = self.get_object()
        if po.status in (PurchaseOrder.Status.RECEIVED, PurchaseOrder.Status.CANCELLED):
            return Response({"error": f"Order is already {po.status}"}, status=400)

        items_data = request.data.get("items", [])
        if not items_data:
            return Response({"error": "items array required with {item_id, quantity_received}"}, status=400)

        with db_transaction.atomic():
            for entry in items_data:
                item_id = entry.get("item_id")
                qty = int(entry.get("quantity_received", 0))
                if qty <= 0:
                    continue
                try:
                    po_item = po.items.get(item_id=item_id)
                except PurchaseOrderItem.DoesNotExist:
                    return Response({"error": f"Item {item_id} not in this PO"}, status=400)

                po_item.quantity_received += qty
                po_item.save(update_fields=["quantity_received"])

                inv_item = po_item.item
                StockMovement.objects.create(
                    item=inv_item,
                    movement_type="purchase",
                    quantity=qty,
                    unit_price=po_item.unit_price,
                    total_amount=qty * po_item.unit_price,
                    reference_number=po.order_number,
                    reference_type="purchase_order",
                    notes=f"Received against PO {po.order_number}",
                    performed_by=request.user,
                )
                inv_item.current_stock += qty
                inv_item.save(update_fields=["current_stock"])

            # Update PO status
            all_received = all(pi.quantity_received >= pi.quantity_ordered for pi in po.items.all())
            any_received = any(pi.quantity_received > 0 for pi in po.items.all())
            if all_received:
                po.status = PurchaseOrder.Status.RECEIVED
            elif any_received:
                po.status = PurchaseOrder.Status.PARTIALLY_RECEIVED
            po.save(update_fields=["status"])

        return Response(PurchaseOrderSerializer(po).data)
