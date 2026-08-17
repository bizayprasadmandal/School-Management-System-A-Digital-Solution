"""Inventory / Store Management serializers."""

from rest_framework import serializers

from .models import Category, InventoryItem, PurchaseOrder, PurchaseOrderItem, StockMovement, Supplier


class CategorySerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "is_active", "item_count", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_item_count(self, obj):
        return getattr(obj, "item_count", obj.items.count())


class SupplierSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "contact_person",
            "email",
            "phone",
            "address",
            "tax_id",
            "payment_terms",
            "status",
            "status_display",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InventoryItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True, default=None)
    unit_display = serializers.CharField(source="get_unit_display", read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    stock_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            "id",
            "category",
            "category_name",
            "supplier",
            "supplier_name",
            "name",
            "sku",
            "description",
            "unit",
            "unit_display",
            "unit_price",
            "current_stock",
            "minimum_stock",
            "maximum_stock",
            "location",
            "barcode",
            "is_active",
            "is_low_stock",
            "stock_value",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "current_stock", "created_at", "updated_at"]

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
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_sku = serializers.CharField(source="item.sku", read_only=True)
    movement_type_display = serializers.CharField(source="get_movement_type_display", read_only=True)
    performed_by_name = serializers.CharField(source="performed_by.full_name", read_only=True, default=None)

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "item",
            "item_name",
            "item_sku",
            "movement_type",
            "movement_type_display",
            "quantity",
            "unit_price",
            "total_amount",
            "reference_number",
            "reference_type",
            "notes",
            "performed_by",
            "performed_by_name",
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


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_sku = serializers.CharField(source="item.sku", read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = [
            "id",
            "purchase_order",
            "item",
            "item_name",
            "item_sku",
            "quantity_ordered",
            "quantity_received",
            "unit_price",
            "total_price",
            "notes",
        ]
        read_only_fields = ["id"]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True, default=None)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    ordered_by_name = serializers.CharField(source="ordered_by.full_name", read_only=True, default=None)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "order_number",
            "supplier",
            "supplier_name",
            "order_date",
            "expected_date",
            "status",
            "status_display",
            "subtotal",
            "tax_amount",
            "shipping_cost",
            "total_amount",
            "notes",
            "ordered_by",
            "ordered_by_name",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "ordered_by", "created_at", "updated_at"]

    def validate_supplier(self, value):
        # Purchase orders must stay within the tenant — the supplier has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Supplier not found in your school.")
        return value
