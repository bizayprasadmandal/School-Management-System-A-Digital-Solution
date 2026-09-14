"""Scan serializers for writable school/user fields that block creates."""

import re

MODULES = ["reporting", "conferences", "auth", "fees"]

for mod in MODULES:
    path = f"services/{mod}/serializers.py"
    src = open(path, encoding="utf-8").read()
    blocks = re.split(r"(?=^class \w+Serializer\()", src, flags=re.M)
    for b in blocks:
        m = re.match(r"class (\w+Serializer)\(", b)
        if not m:
            continue
        fm = re.search(r"fields = \[(.*?)\]", b, re.S)
        if not fm:
            continue
        fields = re.findall(r'"(\w+)"', fm.group(1))
        ro = re.search(r"read_only_fields = \[(.*?)\]", b, re.S)
        ro_fields = set(re.findall(r'"(\w+)"', ro.group(1))) if ro else set()
        for f in ("school", "user"):
            if f in fields and f not in ro_fields:
                print(f"{mod}/{m.group(1)}: writable {f}")
