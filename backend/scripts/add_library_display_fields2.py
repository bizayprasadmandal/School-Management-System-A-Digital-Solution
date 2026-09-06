"""Second display-field pass for library serializers."""

import re

path = "services/library/serializers.py"
src = open(path, encoding="utf-8").read()

MAP = {
    "InterLibraryLoanSerializer": [("requesting_student_name", "requesting_student.__str__")],
    "BookRepairSerializer": [("copy_label", "book_copy.__str__"), ("reported_by_name", "reported_by.get_full_name")],
    "BookDonationSerializer": [("received_by_name", "received_by.get_full_name")],
    "ReadingListSerializer": [("created_by_name", "created_by.get_full_name")],
    "LibraryEventSerializer": [("organizer_name", "organizer.get_full_name")],
    "InventoryManagementSerializer": [("conducted_by_name", "conducted_by.get_full_name")],
    "LibrarianProfileSerializer": [("user_name", "user.get_full_name")],
    "BookCopySerializer": [("book_title", "book.title")],
    "BookClubSerializer": [("advisor_name", "advisor.get_full_name"), ("current_book_title", "current_book.title")],
}

blocks = re.split(r"(?=^class \w+Serializer\()", src, flags=re.M)
changed = 0
for i, block in enumerate(blocks):
    m = re.match(r"^class (\w+Serializer)\(", block)
    if not m or m.group(1) not in MAP:
        continue
    name = m.group(1)
    decls = [f'    {d} = serializers.CharField(source="{s}", read_only=True)' for d, s in MAP[name] if d not in block]
    if not decls:
        continue
    fm = re.search(r"fields = \[(.*?)\]", block, re.S)
    existing = re.findall(r'"(\w+)"', fm.group(1))
    adds = [f'"{d}"' for d, _ in MAP[name] if d not in existing]
    new_fields = fm.group(0).replace("]", ", " + ", ".join(adds) + "]", 1)
    block_new = block.replace(fm.group(0), new_fields, 1)
    lines = block_new.split("\n")
    for li, ln in enumerate(lines):
        if ln.startswith("class "):
            insert_line = li + 1
            break
    block_new = "\n".join(lines[:insert_line]) + "\n" + "\n".join(decls) + "\n" + "\n".join(lines[insert_line:])
    blocks[i] = block_new
    changed += 1

src = "".join(blocks)
open(path, "w", encoding="utf-8", newline="\n").write(src)
print(f"display fields pass 2: {changed} serializers updated")
