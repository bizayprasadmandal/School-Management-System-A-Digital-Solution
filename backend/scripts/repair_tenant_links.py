"""Repair cross-tenant FK links created by earlier demo seeding.

The original generic seeder could link a child row to a parent from another
school (e.g. a Green Valley student's roommate assignment pointing at an
EduSphere room). Such rows are invisible per-tenant AND inconsistent.

For every services.* model, resolve *all* FK paths to ``auth_service.School``
(depth-capped) and delete rows whose paths disagree about the tenant. Deepest
models first so children are removed before the parents they dangle from.
Re-run ``seed_empty_models.py`` afterwards to refill the holes.
"""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from django.apps import apps  # noqa: E402
from services.auth.models import School  # noqa: E402

MAX_DEPTH = 4


def all_school_paths(model, seen=None):
    """Every FK-path (child→…→School) from model, depth-capped, no cycles."""
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
    models = []
    for app_conf in apps.get_app_configs():
        if app_conf.name.startswith("services."):
            models.extend(app_conf.get_models())

    total_deleted = 0
    checked = 0
    for model in models:
        paths = all_school_paths(model)
        # need ≥2 paths to be able to disagree (1 path = no cross-check)
        if len(paths) < 2:
            continue
        try:
            total = model._default_manager.count()
        except Exception:  # noqa: BLE001
            continue
        if total == 0 or total > 20000:
            continue
        checked += 1
        # lookups compare the school id reached via each FK path: path
        # ['school'] -> 'school_id'; ['room','hostel','school'] ->
        # 'room__hostel__school_id'. The FULL path (including the final FK
        # onto School) is required — dropping the last hop (p[:-1]) compares
        # parent pks instead of school ids and flags every healthy multi-FK
        # row, shredding tenant-consistent data on each run.
        try:
            lookups = ["__".join(p) + "_id" for p in paths if p]
            rows = model._default_manager.values_list("pk", *lookups)
        except Exception:  # noqa: BLE001
            continue
        bad_pks = []
        for row in rows:
            schools = set()
            for v in row[1:]:
                if v is not None:
                    schools.add(str(v))
            if len(schools) > 1:
                bad_pks.append(row[0])
        if bad_pks:
            n = len(bad_pks)
            model._default_manager.filter(pk__in=bad_pks).delete()
            total_deleted += n
            print(f"  repaired {model._meta.label}: deleted {n} cross-tenant rows")

    print(f"\nchecked {checked} multi-path models; deleted {total_deleted} rows total")


if __name__ == "__main__":
    main()
