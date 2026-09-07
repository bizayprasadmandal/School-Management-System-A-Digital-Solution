"""Add FK display fields to counseling serializers (safe version).

Inserts CharField declarations right after the class line and extends only
single-line `fields = [...]` lists. Skips `fields = "__all__"` serializers
(declared fields are automatically included there).
"""

import re

SERS = "services/counseling/serializers.py"

ser_src = open(SERS, encoding="utf-8").read()

DISPLAY_FIELDS = {
    "InterventionGoalSerializer": [("plan_title", "intervention_plan.title")],
    "ScreeningResponseSerializer": [("screening_title", "screening.screening_type")],
    "ProgressMilestoneSerializer": [("progress_domain", "progress.domain")],
    "CourseRecommendationSerializer": [("advising_type", "advising.advising_type")],
    "BullyingFollowUpSerializer": [("report_type", "report.report_type")],
    "CounselorCoverageSerializer": [
        ("absent_counselor_name", "absent_counselor.full_name"),
        ("covering_counselor_name", "covering_counselor.full_name"),
    ],
}

changed = []
for ser_name, fields in DISPLAY_FIELDS.items():
    anchor = f"class {ser_name}"
    if anchor not in ser_src:
        print("!! serializer not found:", ser_name)
        continue
    seg_start = ser_src.index(anchor)
    seg_end = ser_src.find("\nclass ", seg_start + 1)
    if seg_end == -1:
        seg_end = len(ser_src)
    seg = ser_src[seg_start:seg_end]

    decls = []
    for fname, fsource in fields:
        if re.search(rf"\b{fname}\s*=", seg):
            print("skip existing:", ser_name, fname)
            continue
        decls.append(f'    {fname} = serializers.CharField(source="{fsource}", read_only=True)')
    if not decls:
        continue

    cls_line_end = seg.index("\n") + 1
    new_seg = seg[:cls_line_end] + "\n".join(decls) + "\n" + seg[cls_line_end:]

    # extend a single-line fields list; leave __all__ alone
    fm = re.search(r"fields\s*=\s*\[([^\]]*)\]", new_seg)
    if fm and '"__all__"' not in fm.group(1) and "'" not in fm.group(1):
        fl = fm.group(1)
        add = [f'"{f[0]}"' for f in fields if f'"{f[0]}"' not in fl]
        if add:
            # ensure clean comma separation
            stripped = fl.rstrip().rstrip(",")
            new_fl = stripped + ",\n            " + ", ".join(add) + ","
            new_seg = new_seg[: fm.start(1)] + new_fl + new_seg[fm.end(1) :]

    ser_src = ser_src[:seg_start] + new_seg + ser_src[seg_end:]
    changed.append(ser_name)
    print("display:", ser_name, [f[0] for f in fields])

open(SERS, "w", encoding="utf-8", newline="\n").write(ser_src)
print(f"updated {len(changed)} serializers")
