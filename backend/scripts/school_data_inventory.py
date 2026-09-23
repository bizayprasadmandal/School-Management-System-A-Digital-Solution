"""Ground-truth data inventory for one school.

For every concrete model in the service apps that carries a direct ``school``
FK, print the row count for the given school. Used to tell a *UI* empty state
("the endpoint returns rows but the page shows nothing") apart from an
*unseeded* tab ("this school genuinely has no rows for that entity").

Run inside the backend container:

    python scripts/school_data_inventory.py "Green Valley School"
"""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from django.apps import apps  # noqa: E402
from services.auth.models import School  # noqa: E402

SKIP_APPS = {"admin", "auth", "contenttypes", "sessions", "token_blacklist", "axes"}


def global_report():
    """Totals across ALL schools — tells an unseeded entity from a tenant bug."""
    for app_config in sorted(apps.get_app_configs(), key=lambda a: a.label):
        if app_config.label in SKIP_APPS:
            continue
        empties = []
        for model in sorted(app_config.get_models(), key=lambda m: m.__name__):
            if "school" not in {f.name for f in model._meta.get_fields()}:
                continue
            try:
                total = model._default_manager.count()
            except Exception:  # noqa: BLE001
                continue
            if total == 0:
                empties.append(model.__name__)
        if empties:
            print(f"[{app_config.label}] {len(empties)} model(s) with ZERO rows in the whole DB:")
            print(f"    {', '.join(empties)}")


def main():
    if "--all-schools" in sys.argv:
        print("models with zero rows across ALL schools (unseeded, not a tenant bug)\n")
        global_report()
        return

    name = sys.argv[1] if len(sys.argv) > 1 else "Green Valley School"
    school = School.objects.filter(name__icontains=name).first()
    if not school:
        print(f"no school matching {name!r}")
        return
    print(f"school: {school.name} ({school.id})\n")

    total_rows = 0
    empty_models = []
    for app_config in sorted(apps.get_app_configs(), key=lambda a: a.label):
        if app_config.label in SKIP_APPS:
            continue
        rows = []
        for model in sorted(app_config.get_models(), key=lambda m: m.__name__):
            field_names = {f.name for f in model._meta.get_fields()}
            if "school" not in field_names:
                continue
            try:
                count = model._default_manager.filter(school=school).count()
            except Exception as exc:  # noqa: BLE001
                rows.append((model.__name__, f"ERR {str(exc)[:40]}"))
                continue
            rows.append((model.__name__, count))
            total_rows += count
            if count == 0:
                empty_models.append(f"{app_config.label}.{model.__name__}")
        if not rows:
            continue
        nonempty = [f"{n}={c}" for n, c in rows if c]
        empty = [n for n, c in rows if c == 0]
        print(f"[{app_config.label}] {len(nonempty)} non-empty / {len(empty)} empty")
        if nonempty:
            print(f"    {', '.join(nonempty)}")
        if empty:
            print(f"    EMPTY: {', '.join(empty)}")

    print(f"\ntotal school rows: {total_rows}")
    print(f"models with 0 rows: {len(empty_models)}")


if __name__ == "__main__":
    main()
