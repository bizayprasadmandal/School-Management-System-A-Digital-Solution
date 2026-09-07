"""Fix counseling viewset filterset_fields / ordering_fields / ordering
against the REAL model fields (validated live via Django).

Run: docker exec -w /app sms_backend python manage.py shell -c "exec(open('scripts/fix_counseling_filters.py').read())"
"""

import ast
import re

from services.counseling import views as cv

VIEWS = "/app/services/counseling/views.py"
src = open(VIEWS, encoding="utf-8").read()

blocks = re.split(r"(?=^class \w+ViewSet)", src, flags=re.M)
out = []
fixed = 0
for b in blocks:
    m = re.match(r"^class (\w+ViewSet)", b)
    if not m:
        out.append(b)
        continue
    vs_name = m.group(1)
    vs = getattr(cv, vs_name, None)
    meta = getattr(getattr(vs, "serializer_class", None), "Meta", None)
    if meta is None:
        out.append(b)
        continue
    model = meta.model
    fields = {f.name for f in model._meta.get_fields()}

    new_b = b

    # --- filterset_fields ---
    fm = re.search(r"(    filterset_fields = )(\[[^\]]*\])", new_b)
    if fm:
        try:
            current = ast.literal_eval(fm.group(2))
        except Exception:
            current = []
        valid = [f for f in current if f in fields]
        if valid != current:
            new_b = new_b[: fm.start(2)] + repr(valid).replace("'", '"') + new_b[fm.end(2) :]
            fixed += 1
            print(f"{vs_name}: filterset {current} -> {valid}")

    # --- ordering_fields ---
    om = re.search(r"(    ordering_fields = )(\[[^\]]*\])", new_b)
    if om:
        try:
            current = ast.literal_eval(om.group(2))
        except Exception:
            current = []
        valid = [f for f in current if f in fields or f == "__all__"]
        if valid != current:
            new_b = new_b[: om.start(2)] + repr(valid).replace("'", '"') + new_b[om.end(2) :]
            fixed += 1
            print(f"{vs_name}: ordering_fields {current} -> {valid}")

    # --- ordering ---
    gm = re.search(r"(    ordering = )(\[[^\]]*\])", new_b)
    if gm:
        try:
            current = ast.literal_eval(gm.group(2))
        except Exception:
            current = []
        valid = []
        for f in current:
            base = f.lstrip("-")
            if base in fields:
                valid.append(f)
            elif "created_at" in fields:
                valid.append("-created_at")
            elif "timestamp" in fields:
                valid.append("-timestamp")
            # else drop
        if not valid:
            # fall back to pk ordering for stable pagination
            pk = model._meta.pk.name
            valid = [f"-{pk}"]
        if valid != current:
            new_b = new_b[: gm.start(2)] + repr(valid).replace("'", '"') + new_b[gm.end(2) :]
            fixed += 1
            print(f"{vs_name}: ordering {current} -> {valid}")

    out.append(new_b)

src = "".join(out)
open(VIEWS, "w", encoding="utf-8", newline="\n").write(src)
print(f"fixed {fixed} attribute blocks")
