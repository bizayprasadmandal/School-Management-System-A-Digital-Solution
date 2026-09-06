"""One-shot library module fixes:
1. Make `school` read-only in the serializers that expose it writable
   (viewsets set it server-side via perform_create).
2. Add perform_create to FineManagement and LibraryNotification viewsets.
3. Add FK display fields where missing for the UI cards.
"""

import re

path = "services/library/serializers.py"
src = open(path, encoding="utf-8").read()

# ─── 1. school read-only ─────────────────────────────────────────────────────
blocks = re.split(r"(?=^class \w+Serializer\()", src, flags=re.M)
changed = 0
for i, block in enumerate(blocks):
    m = re.match(r"^class (\w+Serializer)\(", block)
    if not m:
        continue
    fm = re.search(r"fields = \[(.*?)\]", block, re.S)
    fields = re.findall(r'"(\w+)"', fm.group(1)) if fm else []
    if "school" not in fields:
        continue
    if "read_only_fields" in block:
        # extend existing tuple/list
        rm = re.search(r"read_only_fields = (\[|\()(.*?)(\]|\))", block, re.S)
        ro_body = rm.group(2)
        if '"school"' in ro_body:
            continue
        new_body = ro_body.rstrip().rstrip(",") + (", " if ro_body.strip() else "") + '"school",'
        new_block = block.replace(rm.group(0), f"read_only_fields = ({new_body})")
        blocks[i] = new_block
        changed += 1
    else:
        # insert read_only_fields right after fields list
        insert_at = fm.end()
        new_block = block[:insert_at] + '\n    read_only_fields = ["school", "id", "created_at"]' + block[insert_at:]
        blocks[i] = new_block
        changed += 1

src = "".join(blocks)
open(path, "w", encoding="utf-8", newline="\n").write(src)
print(f"school read-only: {changed} serializers updated")

# ─── 2. perform_create for the two school-scoped viewsets lacking it ────────
vpath = "services/library/views.py"
vsrc = open(vpath, encoding="utf-8").read()

PC = "    def perform_create(self, serializer):\n" "        serializer.save(school=self.request.user.school)\n"

for model in ["FineManagement", "LibraryNotification"]:
    seg_start = vsrc.index(f"class {model}ViewSet")
    seg_end = vsrc.find("\nclass ", seg_start + 1)
    if seg_end == -1:
        seg_end = len(vsrc)
    seg = vsrc[seg_start:seg_end]
    if "def perform_create" in seg:
        print("skip (already has):", model)
        continue
    anchor = "    def get_queryset(self):"
    idx = seg.index(anchor)
    seg_new = seg[:idx] + PC + "\n" + seg[idx:]
    vsrc = vsrc[:seg_start] + seg_new + vsrc[seg_end:]
    print("perform_create added:", model)

open(vpath, "w", encoding="utf-8", newline="\n").write(vsrc)

# ─── 3. FK display fields for UI cards ──────────────────────────────────────
src = open(path, encoding="utf-8").read()

DISPLAY_MAP = {
    "CheckoutSerializer": [
        ("book", "book_title", "book.title"),
        ("student", "student_name", "student.__str__"),
        ("checked_out_by", "checked_out_by_name", "checked_out_by.get_full_name"),
    ],
    "BookReservationSerializer": [("book", "book_title", "book.title"), ("student", "student_name", "student.__str__")],
    "ReadingListItemSerializer": [
        ("reading_list", "reading_list_name", "reading_list.name"),
        ("book", "book_title", "book.title"),
    ],
    "InventoryAuditItemSerializer": [("audit", "audit_name", "audit.name"), ("book", "book_title", "book.title")],
    "BarcodeTrackingSerializer": [("book", "book_title", "book.title")],
    "FinePaymentSerializer": [
        ("fine", "fine_reference", "fine.__str__"),
        ("received_by", "received_by_name", "received_by.get_full_name"),
    ],
    "EventRegistrationSerializer": [
        ("event", "event_name", "event.name"),
        ("student", "student_name", "student.__str__"),
    ],
    "BookReviewSerializer": [("book", "book_title", "book.title"), ("student", "student_name", "student.__str__")],
    "BookRecommendationSerializer": [
        ("student", "student_name", "student.__str__"),
        ("book", "book_title", "book.title"),
    ],
    "BookConditionLogSerializer": [
        ("book_copy", "copy_label", "book_copy.__str__"),
        ("reported_by", "reported_by_name", "reported_by.get_full_name"),
    ],
    "BookClubMembershipSerializer": [
        ("book_club", "club_name", "book_club.name"),
        ("student", "student_name", "student.__str__"),
    ],
    "ReadingChallengeProgressSerializer": [
        ("challenge", "challenge_name", "challenge.name"),
        ("student", "student_name", "student.__str__"),
    ],
    "AcquisitionRequestSerializer": [
        ("requested_by", "requested_by_name", "requested_by.get_full_name"),
        ("approved_by", "approved_by_name", "approved_by.get_full_name"),
    ],
    "BookPurchaseSerializer": [("book", "book_title", "book.title")],
    "LibraryCardSerializer": [("student", "student_name", "student.__str__")],
    "StudentReadingLogSerializer": [("student", "student_name", "student.__str__")],
    "LibraryFeedbackSerializer": [
        ("student", "student_name", "student.__str__"),
        ("responded_by", "responded_by_name", "responded_by.get_full_name"),
    ],
    "FineManagementSerializer": [("student", "student_name", "student.__str__"), ("book", "book_title", "book.title")],
    "LibraryNotificationSerializer": [
        ("student", "student_name", "student.__str__"),
        ("book", "book_title", "book.title"),
    ],
}

changed_display = 0
blocks = re.split(r"(?=^class \w+Serializer\()", src, flags=re.M)
for i, block in enumerate(blocks):
    m = re.match(r"^class (\w+Serializer)\(", block)
    if not m or m.group(1) not in DISPLAY_MAP:
        continue
    name = m.group(1)
    decls = []
    for fk, disp, src_path in DISPLAY_MAP[name]:
        if disp in block:
            continue
        decls.append(f'    {disp} = serializers.CharField(source="{src_path}", read_only=True)')
    if not decls:
        continue
    fm = re.search(r"fields = \[(.*?)\]", block, re.S)
    body = fm.group(1)
    add_fields = []
    for fk, disp, _ in DISPLAY_MAP[name]:
        if disp in block and disp in fm.group(0):
            continue
        add_fields.append(f'"{disp}"')
        if fk not in re.findall(r'"(\w+)"', body):
            pass  # fk itself already in fields
    # append display names to fields list
    new_fields = fm.group(0).replace(
        "]",
        ", " + ", ".join(f'"{d}"' for _, d, _ in DISPLAY_MAP[name] if d not in re.findall(r'"(\w+)"', body)) + "]",
        1,
    )
    block_new = block.replace(fm.group(0), new_fields, 1)
    # insert decls after class docstring/first line
    lines = block_new.split("\n")
    # find first line after class decl
    for li, ln in enumerate(lines):
        if ln.startswith("class "):
            insert_line = li + 1
            break
    block_new = "\n".join(lines[:insert_line]) + "\n" + "\n".join(decls) + "\n" + "\n".join(lines[insert_line:])
    blocks[i] = block_new
    changed_display += 1

src = "".join(blocks)
open(path, "w", encoding="utf-8", newline="\n").write(src)
print(f"display fields: {changed_display} serializers updated")
