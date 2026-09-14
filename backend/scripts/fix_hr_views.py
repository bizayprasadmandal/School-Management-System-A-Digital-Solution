"""Fix hr module: tenant scoping + create blockers.

1. Seven viewsets expose `objects.all()` (cross-tenant leak) -> add
   get_queryset scoping via direct school FK or parent path.
2. Five school-scoped viewsets lack perform_create -> add it.
3. Matching serializers expose writable `school` -> make read-only
   (AccountantProfile keeps `user` writable: admin assigns the user).
"""

import re

VIEWS = "services/hr/views.py"
SER = "services/hr/serializers.py"

# viewset -> (queryset filter, select_related)
SCOPING = {
    "AccountantProfileViewSet": ("school=self.request.user.school", None),
    "DataRetentionPolicyViewSet": ("school=self.request.user.school", None),
    "HRDashboardMetricsViewSet": ("school=self.request.user.school", None),
    "OnboardingChecklistViewSet": ("school=self.request.user.school", None),
    "OnboardingProgressViewSet": ("employee__school=self.request.user.school", '"employee", "task"'),
    "OnboardingTaskViewSet": ("checklist__school=self.request.user.school", '"checklist", "assigned_to"'),
    "PayslipViewLogViewSet": ("employee__school=self.request.user.school", '"employee", "payslip"'),
}

PERFORM = {
    "HRAuditLogViewSet": "serializer.save(school=self.request.user.school)",
    "AccountantProfileViewSet": "serializer.save(school=self.request.user.school)",
    "DataRetentionPolicyViewSet": "serializer.save(school=self.request.user.school)",
    "HRDashboardMetricsViewSet": "serializer.save(school=self.request.user.school)",
    "OnboardingChecklistViewSet": "serializer.save(school=self.request.user.school)",
}

# serializer -> read-only field to add (None -> use read_only_fields append)
RO_FIELDS = {
    "OnboardingChecklistSerializer": "school",
    "HRDashboardMetricsSerializer": "school",
    "HRAuditLogSerializer": "school",
    "AccountantProfileSerializer": "school",
    "DataRetentionPolicySerializer": "school",
}

src = open(VIEWS, encoding="utf-8").read()
blocks = re.split(r"(?=^class \w+ViewSet)", src, flags=re.M)
out = [blocks[0]]
fixed_qs = fixed_pc = 0
for b in blocks[1:]:
    m = re.match(r"^class (\w+ViewSet)", b)
    name = m.group(1) if m else ""
    if name in SCOPING and "def get_queryset" not in b:
        filt, sel = SCOPING[name]
        sel_line = f".select_related({sel})" if sel else ""
        inject = (
            f"\n    def get_queryset(self):\n"
            f"        return {name.replace('ViewSet', '')}.objects.filter({filt}){sel_line}\n\n"
        )
        # insert after the ordering line (end of attribute header)
        b = re.sub(r"(ordering = \[[^\]]*\]\n)", r"\1" + inject, b, count=1)
        fixed_qs += 1
    if name in PERFORM and "perform_create" not in b:
        b = b.rstrip("\n") + f"\n\n    def perform_create(self, serializer):\n        {PERFORM[name]}\n"
        fixed_pc += 1
    out.append(b)
src = "".join(out)
open(VIEWS, "w", encoding="utf-8", newline="\n").write(src)
print(f"viewsets: {fixed_qs} scoped, {fixed_pc} perform_create added")

ser = open(SER, encoding="utf-8").read()
blocks = re.split(r"(?=^class \w+Serializer)", ser, flags=re.M)
out = [blocks[0]]
fixed_ro = 0
for b in blocks[1:]:
    m = re.match(r"^class (\w+Serializer)", b)
    name = m.group(1) if m else ""
    if name in RO_FIELDS:
        field = RO_FIELDS[name]
        ro = re.search(r"read_only_fields = \[[^\]]*\]", b)
        if ro and f'"{field}"' not in ro.group(0):
            b = b.replace(ro.group(0), ro.group(0)[:-1] + f', "{field}"]', 1)
            fixed_ro += 1
        elif not ro:
            # append read_only_fields after the fields list
            fm = re.search(r"(fields = \[[^\]]*\]\n)", b, re.S)
            if fm:
                b = b.replace(fm.group(1), fm.group(1) + f'    read_only_fields = ["{field}"]\n', 1)
                fixed_ro += 1
            else:
                print("  !! no fields list in", name)
    out.append(b)
ser = "".join(out)
open(SER, "w", encoding="utf-8", newline="\n").write(ser)
print(f"serializers: {fixed_ro} made school read-only")
