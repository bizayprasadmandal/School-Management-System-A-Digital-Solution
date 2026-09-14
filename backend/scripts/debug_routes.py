import re

for i, line in enumerate(open("scripts/routes_dump.txt", encoding="utf-8")):
    s = line.strip()
    m2 = re.search(r"/(\w+)/(\^?[\w-]+)/", s)
    if m2:
        print(i, repr(s[:40]), "->", m2.groups())
    if i > 8:
        break
