"""Fix admissions module viewsets/serializers:

1. Twelve child-model viewsets filter on a nonexistent `school` FK
   (FieldError -> 500 on list). Scope through their parents instead:
     ApplicationTimelineEvent -> application__school
     EntranceAssessment       -> application__school
     OpenHouseRegistration    -> event__school
     ScholarshipApplication   -> application__school | scholarship__school
     AgreementSignature       -> application__school | agreement__school
     GradeLevelCapacity       -> intake__school
     AdmissionDecision        -> application__school
     SiblingRecord            -> application__school | sibling_group__school
     AdmissionDocumentChecklist     -> intake__school
     AdmissionDocumentVerification  -> application__school
     AdmissionFunnelSnapshot        -> intake__school
     AdmissionPredictionModel       -> intake__school
2. Their perform_create passed school= to models without a school FK
   (TypeError on create). Remove it; set user-owned FKs where present.
3. Make `school` read-only in every serializer that exposes it writable.
"""

import re

VIEWS = "services/admissions/views.py"
SER = "services/admissions/serializers.py"

# viewset class -> (model, scope filter expression)
SCOPE_FIXES = {
    "ApplicationTimelineEvent": (
        "ApplicationTimelineEvent",
        "application__school=school",
    ),
    "EntranceAssessment": ("EntranceAssessment", "application__school=school"),
    "OpenHouseRegistration": ("OpenHouseRegistration", "event__school=school"),
    "ScholarshipApplication": (
        "ScholarshipApplication",
        "Q(application__school=school) | Q(scholarship__school=school)",
    ),
    "AgreementSignature": (
        "AgreementSignature",
        "Q(application__school=school) | Q(agreement__school=school)",
    ),
    "GradeLevelCapacity": ("GradeLevelCapacity", "intake__school=school"),
    "AdmissionDecision": ("AdmissionDecision", "application__school=school"),
    "SiblingRecord": (
        "SiblingRecord",
        "Q(application__school=school) | Q(sibling_group__school=school)",
    ),
    "AdmissionDocumentChecklist": (
        "AdmissionDocumentChecklist",
        "intake__school=school",
    ),
    "AdmissionDocumentVerification": (
        "AdmissionDocumentVerification",
        "application__school=school",
    ),
    "AdmissionFunnelSnapshot": ("AdmissionFunnelSnapshot", "intake__school=school"),
    "AdmissionPredictionModel": ("AdmissionPredictionModel", "intake__school=school"),
}

# viewset class -> perform_create body
PC_FIXES = {
    "ApplicationTimelineEvent": "        serializer.save(created_by=self.request.user)\n",
    "EntranceAssessment": "        serializer.save()\n",
    "OpenHouseRegistration": "        serializer.save()\n",
    "ScholarshipApplication": "        serializer.save()\n",
    "AgreementSignature": "        serializer.save()\n",
    "GradeLevelCapacity": "        serializer.save()\n",
    "AdmissionDecision": "        serializer.save(decided_by=self.request.user)\n",
    "SiblingRecord": "        serializer.save()\n",
    "AdmissionDocumentChecklist": "        serializer.save()\n",
    "AdmissionDocumentVerification": "        serializer.save(verified_by=self.request.user)\n",
    "AdmissionFunnelSnapshot": "        serializer.save()\n",
    "AdmissionPredictionModel": "        serializer.save()\n",
}


def viewset_span(src, cls):
    start = src.index(f"class {cls}(")
    nxt = src.find("\nclass ", start + 1)
    return start, (nxt if nxt != -1 else len(src))


src = open(VIEWS, encoding="utf-8").read()

if "from django.db.models import Count, Q" not in src:
    src = src.replace(
        "from django.db.models import Count",
        "from django.db.models import Count, Q",
        1,
    )
    print("added Q import")
elif not re.search(r"^from django\.db\.models import .*Q", src, re.M):
    src = src.replace(
        "from django.db.models import Count",
        "from django.db.models import Count, Q",
        1,
    )
    print("added Q import (fallback)")

scope_fixed = pc_fixed = 0
for name, (model, scope) in SCOPE_FIXES.items():
    cls = f"{name}ViewSet"
    s, e = viewset_span(src, cls)
    seg = src[s:e]
    # build the actual filter expression with the request user school
    school_expr = scope.replace("=school", "=self.request.user.school")
    new_seg, n = re.subn(
        rf"{model}\.objects\.filter\(school=self\.request\.user\.school\)",
        f"{model}.objects.filter({school_expr})",
        seg,
        count=1,
    )
    if n:
        src = src[:s] + new_seg + src[e:]
        scope_fixed += 1
        print(f"scope ok: {cls} -> {scope}")
    else:
        print(f"scope SKIP (pattern not found): {cls}")

for name, body in PC_FIXES.items():
    cls = f"{name}ViewSet"
    s, e = viewset_span(src, cls)
    seg = src[s:e]
    PC_PATTERN = (
        r"    def perform_create\(self, serializer\):\n"
        r"        serializer\.save\(school=self\.request\.user\.school\)\n"
    )
    new_seg, n = re.subn(
        PC_PATTERN,
        "    def perform_create(self, serializer):\n" + body,
        seg,
        count=1,
    )
    if n:
        src = src[:s] + new_seg + src[e:]
        pc_fixed += 1
        print(f"perform_create ok: {cls}")
    else:
        print(f"perform_create SKIP: {cls}")

open(VIEWS, "w", encoding="utf-8").write(src)
print(f"views.py: {scope_fixed} scope fixes, {pc_fixed} perform_create fixes")

# ---- serializers: make school read-only wherever exposed writable ----
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
        if '"school"' not in re.search(r"read_only_fields = \[[^\]]*\]", block).group(0):
            new_block = block.replace("read_only_fields = [", 'read_only_fields = ["school", ', 1)
        else:
            new_block = block
    else:
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
