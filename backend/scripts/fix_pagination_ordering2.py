"""Second pass: add order_by to viewsets whose get_queryset builds a `qs`
variable or uses multi-line parenthesized returns.

Patterns handled within each flagged viewset class segment:
  1. "return qs\n"                          -> "return qs.order_by(...)\n"
  2. "return qs.<chain>\n" (single line)    -> "return qs.<chain>.order_by(...)\n"
  3. "return (\n ... \n        )\n"         -> "return (\n ... \n        ).order_by(...)\n"
Only the first match inside get_queryset is rewritten.
"""

import re

# module -> [(viewset class, order_by args)]
FIXES = {
    "academics": [
        ("LessonPlanViewSet", ["-created_at"]),
        ("TeacherAssignmentViewSet", ["id"]),
    ],
    "gradebook": [
        ("AssessmentViewSet", ["-created_at"]),
        ("ExamViewSet", ["-start_date"]),
        ("GradeViewSet", ["-updated_at"]),
        ("ReportCardViewSet", ["id"]),
    ],
    "timetable": [("TimetableSlotViewSet", ["day_of_week", "period"])],
    "hr": [("TrainingProgramViewSet", ["-start_date"])],
    "sports": [("TeamViewSet", ["sport", "name"])],
    "transportation": [("RouteViewSet", ["name"])],
}


def order_expr(order):
    return f".order_by({', '.join(repr(o) for o in order)})"


total = 0
for mod, entries in FIXES.items():
    path = f"services/{mod}/views.py"
    src = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    changed = 0
    for cls, order in entries:
        start = src.index(f"class {cls}(")
        nxt = src.find("\nclass ", start + 1)
        seg = src[start:nxt]
        expr = order_expr(order)
        new_seg = seg

        m = re.search(r"(    def get_queryset\(self\):.*?)(\n    def |\Z)", seg, re.S)
        gq = m.group(1) if m else ""
        new_gq = gq

        if re.search(r"\n        return qs\n", gq):
            new_gq = re.sub(r"\n        return qs\n", f"\n        return qs{expr}\n", gq, count=1)
        elif re.search(r"\n        return qs\.\w", gq):
            new_gq = re.sub(
                r"\n        (return qs\.[^\n]+)\n",
                lambda mm: "\n        " + mm.group(1).rstrip() + expr + "\n",
                gq,
                count=1,
            )
        else:
            # multi-line parenthesized return: append after its closing paren
            m2 = re.search(r"\n        return \(\n(?:.*?\n)*?        \)\n", gq)
            if m2:
                block = m2.group(0)
                new_gq = gq.replace(block, block.rstrip("\n") + expr + "\n", 1)

        if new_gq != gq:
            new_seg = seg.replace(gq, new_gq, 1)
            src = src[:start] + new_seg + src[nxt:]
            changed += 1
            print(f"{mod}: {cls} -> order_by({', '.join(order)})")
        else:
            print(f"{mod}: SKIP {cls} (no pattern matched)")
    if changed:
        open(path, "w", encoding="utf-8", newline="\n").write(src)
        total += changed

print(f"TOTAL: {total} viewsets ordered")
