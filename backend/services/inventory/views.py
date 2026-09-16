"""Inventory / Store Management — Viewsets with school-scoped CRUD and stock actions."""

import json
import logging
from decimal import Decimal

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolAdminOrAccountant, IsSchoolMember, IsSchoolStaff
from django.db import transaction as db_transaction
from django.db.models import Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from services.fees.models import AccountingEntry, TransactionLog

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
from .serializers import (
    AssetTagSerializer,
    BarcodeSerializer,
    CategorySerializer,
    InventoryAlertSerializer,
    InventoryAnalyticsSerializer,
    InventoryBudgetSerializer,
    InventoryCatalogExtendedSerializer,
    InventoryCatalogItemSerializer,
    InventoryCatalogSerializer,
    InventoryCompositeItemSerializer,
    InventoryItemSerializer,
    InventoryLeaseAgreementExtendedSerializer,
    InventoryLeaseAgreementSerializer,
    InventoryPartsSerializer,
    InventoryPricingHistorySerializer,
    InventoryReportSerializer,
    InventorySettingsSerializer,
    InventorySubscriptionPlanSerializer,
    InventorySubscriptionSerializer,
    InventorySupplierPerformanceSerializer,
    InventoryTransferRouteSerializer,
    InvoicePaymentSerializer,
    InvoiceSerializer,
    PurchaseOrderItemSerializer,
    PurchaseOrderSerializer,
    PurchaseRequisitionItemSerializer,
    PurchaseRequisitionSerializer,
    ReturnRequestSerializer,
    StockAdjustmentSerializer,
    StockCountScheduleSerializer,
    StockLevelSerializer,
    StockMovementSerializer,
    StockTransferItemSerializer,
    StockTransferSerializer,
    SupplierRatingSerializer,
    SupplierSerializer,
    WarehouseLocationSerializer,
    WarehouseSerializer,
    WarehouseZoneSerializer,
    WarrantyClaimExtendedSerializer,
)

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        return (
            Category.objects.filter(school=self.request.user.school)
            .order_by("name")
            .annotate(item_count=Count("items"))
        )

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
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "sku", "description", "barcode"]
    filterset_fields = ["category", "supplier", "is_active"]
    ordering_fields = ["name", "current_stock", "unit_price"]
    ordering = ["name"]

    def get_queryset(self):
        return InventoryItem.objects.filter(school=self.request.user.school).select_related("category", "supplier")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        if self.action == "adjust_stock":
            return [IsAuthenticated(), IsSchoolStaff()]
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
        movement = serializer.save()
        # Keep the item's stock in sync with the recorded movement.
        # quantity is positive for inbound, negative for outbound.
        item = movement.item
        item.current_stock = max(0, item.current_stock + movement.quantity)
        item.save(update_fields=["current_stock"])


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
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "submit",
            "approve",
        ]:
            return [IsAuthenticated(), IsSchoolAdminOrAccountant()]
        if self.action == "receive_items":
            return [IsAuthenticated(), IsSchoolStaff()]
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Move a draft purchase order into the submitted (pending approval) state."""
        po = self.get_object()
        if po.status != PurchaseOrder.Status.DRAFT:
            return Response(
                {"error": f"Only draft orders can be submitted (current: {po.status})"},
                status=400,
            )
        if po.items.count() == 0:
            return Response({"error": "Cannot submit an order with no line items."}, status=400)
        po.status = PurchaseOrder.Status.SUBMITTED
        po.save(update_fields=["status"])
        return Response(PurchaseOrderSerializer(po).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve a submitted order: confirm it and post the commitment to accounting."""
        po = self.get_object()
        if po.status != PurchaseOrder.Status.SUBMITTED:
            return Response(
                {"error": f"Only submitted orders can be approved (current: {po.status})"},
                status=400,
            )

        with db_transaction.atomic():
            po.status = PurchaseOrder.Status.CONFIRMED
            po.save(update_fields=["status"])
            self._post_accounting_entries(po, request.user)

        return Response(PurchaseOrderSerializer(po).data)

    @staticmethod
    def _post_accounting_entries(po, user):
        """Post the PO commitment as debit (expense) / credit (payable) entries.

        Idempotent: keyed by reference_id=PO id, so a retried approval or a
        duplicate call never double-posts the books.
        """
        already = AccountingEntry.objects.filter(
            school=po.school,
            reference_type="purchase_order",
            reference_id=str(po.id),
        ).exists()
        if already:
            return
        AccountingEntry.objects.bulk_create(
            [
                AccountingEntry(
                    school=po.school,
                    entry_type=AccountingEntry.EntryType.DEBIT,
                    account_code="5000",
                    account_name="Inventory Purchases",
                    description=f"PO {po.order_number} approved",
                    amount=po.total_amount,
                    reference_type="purchase_order",
                    reference_id=str(po.id),
                    entry_date=timezone.localdate(),
                    created_by=user,
                    notes=f"Approved by {user.full_name or user.email}",
                ),
                AccountingEntry(
                    school=po.school,
                    entry_type=AccountingEntry.EntryType.CREDIT,
                    account_code="2000",
                    account_name="Accounts Payable",
                    description=f"PO {po.order_number} approved",
                    amount=po.total_amount,
                    reference_type="purchase_order",
                    reference_id=str(po.id),
                    entry_date=timezone.localdate(),
                    created_by=user,
                    notes=f"Approved by {user.full_name or user.email}",
                ),
            ]
        )
        TransactionLog.objects.get_or_create(
            transaction_id=f"PO-{po.id}-APPROVAL",
            defaults={
                "school": po.school,
                "transaction_type": TransactionLog.TransactionType.OTHER,
                "amount": po.total_amount,
                "reference_number": po.order_number,
                "status": "success",
                "description": f"Purchase order {po.order_number} approved and posted to accounting",
            },
        )

    def create(self, request, *args, **kwargs):
        # `items_data` is consumed by this view (line items), not a serializer
        # field, so strip it before validation to avoid an unknown-field error.
        data = request.data.copy()
        raw_items = data.pop("items_data", "[]")
        # Auto-generate a unique order number when the client omits one.
        if not data.get("order_number"):
            today = timezone.localdate()
            prefix = f"PO-{today:%Y%m%d}-"
            seq = PurchaseOrder.objects.filter(order_number__startswith=prefix).count() + 1
            data["order_number"] = f"{prefix}{seq:04d}"
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

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
            return Response(
                {"error": "items array required with {item_id, quantity_received}"},
                status=400,
            )

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

            # Update PO status. Use a fresh query: `po.items` may have been
            # prefetched before the loop, so the in-memory cache holds stale
            # quantity_received values.
            received_pairs = po.items.values_list("quantity_received", "quantity_ordered")
            all_received = all(r >= o for r, o in received_pairs)
            any_received = any(r > 0 for r, _ in received_pairs)
            if all_received:
                po.status = PurchaseOrder.Status.RECEIVED
            elif any_received:
                po.status = PurchaseOrder.Status.PARTIALLY_RECEIVED
            po.save(update_fields=["status"])

        return Response(PurchaseOrderSerializer(po).data)


# ── Additional ViewSets (module expansion) ──


class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseOrderItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return PurchaseOrderItem.objects.filter(purchase_order__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class WarehouseViewSet(viewsets.ModelViewSet):
    serializer_class = WarehouseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return Warehouse.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class WarehouseZoneViewSet(viewsets.ModelViewSet):
    serializer_class = WarehouseZoneSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        return WarehouseZone.objects.filter(warehouse__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class WarehouseLocationViewSet(viewsets.ModelViewSet):
    serializer_class = WarehouseLocationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return WarehouseLocation.objects.filter(zone__warehouse__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class StockLevelViewSet(viewsets.ModelViewSet):
    serializer_class = StockLevelSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return StockLevel.objects.filter(item__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class StockAdjustmentViewSet(viewsets.ModelViewSet):
    serializer_class = StockAdjustmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return StockAdjustment.objects.filter(item__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(adjusted_by=self.request.user)


class StockCountScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = StockCountScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return StockCountSchedule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class StockTransferViewSet(viewsets.ModelViewSet):
    serializer_class = StockTransferSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return StockTransfer.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class StockTransferItemViewSet(viewsets.ModelViewSet):
    serializer_class = StockTransferItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return StockTransferItem.objects.filter(transfer__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class PurchaseRequisitionViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseRequisitionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return PurchaseRequisition.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class PurchaseRequisitionItemViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseRequisitionItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return PurchaseRequisitionItem.objects.filter(requisition__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return Invoice.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InvoicePaymentViewSet(viewsets.ModelViewSet):
    serializer_class = InvoicePaymentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return InvoicePayment.objects.filter(invoice__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ReturnRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ReturnRequestSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ReturnRequest.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class WarrantyClaimExtendedViewSet(viewsets.ModelViewSet):
    serializer_class = WarrantyClaimExtendedSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return WarrantyClaimExtended.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class BarcodeViewSet(viewsets.ModelViewSet):
    serializer_class = BarcodeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return Barcode.objects.filter(item__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class AssetTagViewSet(viewsets.ModelViewSet):
    serializer_class = AssetTagSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return AssetTag.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SupplierRatingViewSet(viewsets.ModelViewSet):
    serializer_class = SupplierRatingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return SupplierRating.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryAlertViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryAlertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryAlert.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryReportViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryReportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryReport.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryAnalyticsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryAnalytics.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventorySettingsViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySettingsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventorySettings.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventorySubscriptionPlanViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySubscriptionPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventorySubscriptionPlan.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventorySubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySubscriptionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventorySubscription.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryBudgetViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryBudgetSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryBudget.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryLeaseAgreementViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryLeaseAgreementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryLeaseAgreement.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventorySupplierPerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = InventorySupplierPerformanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventorySupplierPerformance.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryCatalogViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryCatalogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryCatalog.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryCatalogItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryCatalogItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return InventoryCatalogItem.objects.filter(catalog__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class InventoryPartsViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryPartsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryParts.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryCompositeItemViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryCompositeItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryCompositeItem.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryTransferRouteViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryTransferRouteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryTransferRoute.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryLeaseAgreementExtendedViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryLeaseAgreementExtendedSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryLeaseAgreementExtended.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryCatalogExtendedViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryCatalogExtendedSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryCatalogExtended.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class InventoryPricingHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = InventoryPricingHistorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return InventoryPricingHistory.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
