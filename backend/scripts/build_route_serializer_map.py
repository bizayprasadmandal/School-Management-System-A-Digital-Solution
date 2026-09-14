"""Build authoritative route -> serializer_class map from urls.py + views.py."""

import json
import re
import sys

MODULES = sys.argv[1:] or ["reporting", "conferences", "auth", "fees"]
result = {}
for mod in MODULES:
    urlsrc = open(f"services/{mod}/urls.py", encoding="utf-8").read().replace("\r\n", "\n")
    viewsrc = open(f"services/{mod}/views.py", encoding="utf-8").read().replace("\r\n", "\n")
    # viewset name -> serializer name
    v2s = {}
    for m in re.finditer(r"class (\w+ViewSet)\([^)]*\):", viewsrc):
        name = m.group(1)
        nxt = viewsrc.find("\nclass ", m.start() + 1)
        block = viewsrc[m.start() : (nxt if nxt != -1 else len(viewsrc))]
        sm = re.search(r"serializer_class\s*=\s*(\w+)", block)
        v2s[name] = sm.group(1) if sm else None
    # route -> viewset
    mapping = {}
    for m in re.finditer(r"register\((?:r)?['\"]([^'\"]*)['\"]\s*,\s*(?:views\.)?(\w+ViewSet)", urlsrc):
        route, viewset = m.group(1), m.group(2)
        mapping[route.lstrip("^")] = v2s.get(viewset)
    result[mod] = mapping

map_name = sys.argv[1] if len(sys.argv) > 1 else "cluster"
with open(f"scripts/{map_name}_map.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=1)
for mod, mapping in result.items():
    print(mod, len(mapping), "routes;", sum(1 for v in mapping.values() if v is None), "unmapped")
