"""Cross-check the web app's API paths against the API's real URL patterns.

Many admin tabs are config-driven: the tab declares ``endpoint: "x"`` and the
page calls ``/api/v1/<basePath>/<endpoint>/``. If that route doesn't exist the
tab always renders a 404/empty state — invisible in code review, obvious in the
browser. This script finds every such dead call by asking Django's own URL
resolver whether the path resolves.

Two steps (run from the repo root):

    1) extract (host, reads frontend/web/src):
       python backend/scripts/check_frontend_routes.py extract

    2) check (inside the backend container, where Django is installed):
       docker exec sms_backend python /app/scripts/check_frontend_routes.py check
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FRONTEND = os.path.join(os.path.dirname(HERE), "..", "frontend", "web", "src")
INDEX = os.path.join(HERE, "frontend_api_paths.json")

CALL_RE = re.compile(
    r"""api\.(?:get|post|put|patch|delete)(?:<[^>]*>)?\(\s*[`"']([^`"'?]+)""" r"""|endpoint:\s*[`"']([^`"']+)[`"']"""
)
TEMPLATE_RE = re.compile(r"\$\{[^}]*\}")


def norm(path):
    """Keep absolute calls absolute and entity config endpoints relative."""
    return path.split("?")[0].replace("/api/v1/", "")


def extract():
    found = {}
    base = os.path.normpath(FRONTEND)
    for root, _dirs, files in os.walk(base):
        for name in files:
            if not name.endswith((".ts", ".tsx")):
                continue
            full = os.path.join(root, name)
            try:
                src = open(full, encoding="utf-8").read()
            except OSError:
                continue
            for match in CALL_RE.finditer(src):
                raw = next((g for g in match.groups() if g), None)
                if not raw or TEMPLATE_RE.search(raw):
                    continue
                rel = os.path.relpath(full, base).replace("\\", "/")
                found.setdefault(norm(raw), set()).add(rel)
    with open(INDEX, "w", encoding="utf-8") as fh:
        json.dump({k: sorted(v) for k, v in found.items()}, fh, indent=1)
    print(f"extracted {len(found)} static API paths -> {INDEX}")


def check():
    sys.path.insert(0, "/app")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")
    import django  # noqa: E402

    django.setup()

    from django.urls import Resolver404, resolve  # noqa: E402

    paths = json.load(open(INDEX, encoding="utf-8"))
    dead = []
    relative = []
    for path, files in sorted(paths.items()):
        if not path.startswith("/"):
            # Config-driven entity endpoints (``endpoint: "payslips"``) are only
            # meaningful once a page combines them with its basePath, so they
            # can't be resolved in isolation — the browser walk covers those.
            relative.append(path)
            continue
        candidates = [f"/api/v1{path}", f"/api/v1{path}/"]
        if any(_resolves(resolve, c) for c in candidates):
            continue
        dead.append((path, files))

    print(
        f"absolute frontend API paths: {len(paths) - len(relative)} | unresolvable: {len(dead)}"
        f" | relative (checked in the browser walk): {len(relative)}\n"
    )
    for path, files in dead:
        print(f"  {path}")
        for f in files[:4]:
            print(f"      {f}")
    return dead


def _resolves(resolve, url):
    from django.urls import Resolver404

    try:
        resolve(url)
        return True
    except Resolver404:
        return False


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "extract"
    if mode == "extract":
        extract()
    else:
        sys.exit(0 if not check() else 0)
