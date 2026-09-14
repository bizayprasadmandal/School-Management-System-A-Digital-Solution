"""Fix inventory module viewsets/serializers:

1. Ten child-model viewsets filter on a nonexistent `school` FK
   (FieldError -> 500 on list). Scope through their parents instead:
     Barcode -> item__school
     InventoryCatalogItem -> catalog__school
     InvoicePayment -> invoice__school
     PurchaseOrderItem -> purchase_order__school
     PurchaseRequisitionItem -> requisition__school
     StockAdjustment -> item__school
     StockLevel -> item__school
     StockTransferItem -> transfer__school
     WarehouseLocation -> zone__warehouse__school
     WarehouseZone -> warehouse__school
2. Their perform_create passed school= to models without a school FK
   (TypeError on create). Remove it; set user-owned FKs where present.
3. Make `school` read-only in every serializer that exposes it, so
   clients cannot spoof tenant ownership.
"""

import re

VIEWS = "services/inventory/views.py"
SER = "services/inventory/serializers.py"

SCOPE_FIXES = {
    "Barcode": "item__school",
    "InventoryCatalogItem": "catalog__school",
    "InvoicePayment": "invoice__school",
    "PurchaseOrderItem": "purchase_order__school",
    "PurchaseRequisitionItem": "requisition__school",
    "StockAdjustment": "item__school",
    "StockLevel": "item__school",
    "StockTransferItem": "transfer__school",
    "WarehouseLocation": "zone__warehouse__school",
    "WarehouseZone": "warehouse__school",
}

# viewset -> (model, perform_create body lines)
PC_FIXES = {
    "Barcode": ("Barcode", "        serializer.save()\n"),
    "InventoryCatalogItem": ("InventoryCatalogItem", "        serializer.save()\n"),
    "InvoicePayment": (
        "InvoicePayment",
        "        serializer.save(created_by=self.request.user)\n",
    ),
    "PurchaseOrderItem": ("PurchaseOrderItem", "        serializer.save()\n"),
    "PurchaseRequisitionItem": (
        "PurchaseRequisitionItem",
        "        serializer.save()\n",
    ),
    "StockAdjustment": (
        "StockAdjustment",
        "        serializer.save(adjusted_by=self.request.user)\n",
    ),
    "StockLevel": ("StockLevel", "        serializer.save()\n"),
    "StockTransferItem": ("StockTransferItem", "        serializer.save()\n"),
    "WarehouseLocation": ("WarehouseLocation", "        serializer.save()\n"),
    "WarehouseZone": ("WarehouseZone", "        serializer.save()\n"),
}


def viewset_span(src, cls):
    start = src.index(f"class {cls}(")
    nxt = src.find("\nclass ", start + 1)
    return start, (nxt if nxt != -1 else len(src))


src = open(VIEWS, encoding="utf-8").read()
changed = 0

for model, path in SCOPE_FIXES.items():
    cls = f"{model}ViewSet"
    s, e = viewset_span(src, cls)
    seg = src[s:e]
    new_seg, n = re.subn(
        rf"{model}\.objects\.filter\(school=self\.request\.user\.school\)",
        f"{model}.objects.filter({path}=self.request.user.school)",
        seg,
    )
    if n:
        src = src[:s] + new_seg + src[e:]
        changed += n
        print(f"scope ok: {cls} -> {path}")
    else:
        print(f"scope SKIP (pattern not found): {cls}")

for key, (model, body) in PC_FIXES.items():
    cls = f"{key}ViewSet"
    s, e = viewset_span(src, cls)
    seg = src[s:e]
    new_seg, n = re.subn(
        r"    def perform_create\(self, serializer\):\n        serializer\.save\([^)]*\)\n",
        "    def perform_create(self, serializer):\n" + body,
        seg,
    )
    if n:
        src = src[:s] + new_seg + src[e:]
        print(f"perform_create ok: {cls}")
    else:
        print(f"perform_create SKIP: {cls}")

open(VIEWS, "w", encoding="utf-8").write(src)
print(f"views.py: {changed} scope fixes")

# ---- serializers: make school read-only wherever exposed ----
ser = open(SER, encoding="utf-8").read()
blocks = re.split(r"(?=^class \w+Serializer\(serializers\.ModelSerializer\))", ser, flags=re.M)
fixed = 0
for i, block in enumerate(blocks):
    m = re.match(r"^class (\w+)Serializer", block)
    if not m:
        continue
    if '"school"' not in block:
        continue
    if "read_only_fields" in block:
        new_block = block.replace("read_only_fields = [", 'read_only_fields = ["school", ', 1)
    else:
        # append read_only_fields at end of Meta class
        new_block = re.sub(
            r"(\n        read_only_fields = \[[^\]]*\])",
            lambda mm: mm.group(1),
            block,
            count=1,
        )
        if new_block == block:
            # no read_only_fields line; insert one before Meta's closing
            new_block = re.sub(
                r"(        fields = \[[^\]]*\]\n)",
                r"\1        read_only_fields = [\"school\"]\n",
                block,
                count=1,
            )
    if new_block != block:
        blocks[i] = new_block
        fixed += 1
        print(f"school read-only: {m.group(1)}")

open(SER, "w", encoding="utf-8").write("".join(blocks))
print(f"serializers.py: {fixed} school hardening")
