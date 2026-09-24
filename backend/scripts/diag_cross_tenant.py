"""Diagnose cross-tenant rows: which paths disagree, and row creation time.

Runs the same check as repair_tenant_links.py but prints, for up to 2 flagged
rows per model, every school-path value plus created_at when the model has
one — so we can tell fresh seeder output from pre-existing leftovers.
"""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from django.apps import apps  # noqa: E402
from django.db import models as djm  # noqa: E402
from services.auth.models import School  # noqa: E402

MAX_DEPTH = 4


def all_school_paths(model, seen=None):
    seen = seen or set()
    if model is School:
        return [[]]
    if model in seen or len(seen) >= MAX_DEPTH:
        return []
    paths = []
    for f in model._meta.get_fields():
        if f.is_relation and f.many_to_one:
            for sub in all_school_paths(f.related_model, seen | {model}):
                paths.append([f.name] + sub)
    return paths


def main():
    school_names = {str(pk): nm for pk, nm in School.objects.values_list("pk", "name")}
    shown = 0
    for app_conf in apps.get_app_configs():
        if not app_conf.name.startswith("services."):
            continue
        for model in app_conf.get_models():
            paths = all_school_paths(model)
            if len(paths) < 2:
                continue
            lookups = ["__".join(p) + "_id" for p in paths if p]
            try:
                total = model._default_manager.count()
            except Exception:  # noqa: BLE001
                continue
            if total == 0 or total > 20000:
                continue
            try:
                rows = model._default_manager.values_list("pk", *lookups)
            except Exception:  # noqa: BLE001
                continue
            has_created = any(f.name == "created_at" for f in model._meta.fields)
            if has_created:
                rows = model._default_manager.values_list("pk", "created_at", *lookups)
            n_flagged = 0
            for row in rows:
                vals = row[2:] if has_created else row[1:]
                schools = {str(v) for v in vals if v is not None}
                if len(schools) <= 1:
                    continue
                n_flagged += 1
                if n_flagged > 2:
                    continue
                if shown < 40:
                    shown += 1
                    created = row[1] if has_created else "?"
                    pretty = {v: school_names.get(str(v), str(v)) for v in vals if v is not None}
                    print(f"\n{model._meta.label}  pk={row[0]}  created={created}")
                    for p, v in zip(paths, vals):
                        if v is not None:
                            print(f"    {'__'.join(p) or 'self'} -> {pretty.get(v)}")
            if n_flagged > 2:
                print(f"{model._meta.label}: {n_flagged} flagged total (2 shown)")

    print("\n(flagged = ≥2 school-paths disagree; created timestamps tell us who)")


if __name__ == "__main__":
    main()
