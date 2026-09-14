"""Build routes.json from the endpoint listing (run on host, reads docker output file)."""

import json
import re
import sys

MODULES = sys.argv[1:] or ["reporting", "conferences", "auth", "fees"]
routes = {m: [] for m in MODULES}
cur = None
for line in open("scripts/routes_dump.txt", encoding="utf-8"):
    m = re.match(r"== (\w+) \((\d+)\) ==", line.strip())
    if m:
        cur = m.group(1)
        continue
    m2 = re.search(rf"/({cur})/(\^?[\w-]+)/$", line.strip())
    if m2 and cur in MODULES:
        routes[cur].append(m2.group(2).lstrip("^"))

with open("scripts/cluster_routes.json", "w", encoding="utf-8") as f:
    json.dump(routes, f, indent=1)
print({k: len(v) for k, v in routes.items()})
