"""Classify each viewset's perform_create (CRLF-safe, plain substring)."""

MODULES = ["reporting", "conferences", "auth", "fees"]

for mod in MODULES:
    src = open(f"services/{mod}/views.py", encoding="utf-8").read()
    # normalize CRLF for analysis
    src = src.replace("\r\n", "\n")
    marks = []
    idx = 0
    while True:
        i = src.find("class ", idx)
        if i == -1:
            break
        j = src.find("ViewSet", i)
        if j == -1:
            break
        name = src[i + 6 : j]
        if not name.isidentifier():
            idx = i + 6
            continue
        nxt = src.find("\nclass ", i + 6)
        block = src[i : nxt if nxt != -1 else len(src)]
        has_pc = "def perform_create" in block
        sets_school = "save(school=" in block
        sets_user = "save(user=" in block or 'validated_data.get("user")' in block
        print(f"{mod}/{name}: pc={has_pc} school={sets_school} user={sets_user}")
        idx = i + 6
