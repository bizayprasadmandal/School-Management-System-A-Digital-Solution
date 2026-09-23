"""Instantiate every serializer in the service apps and report config errors.

DRF validates a serializer's field list lazily: ``"field_declared_but_missing_
from_fields"`` only explodes when ``.fields`` is first touched — i.e. on the
first API request. That makes a single bad ``fields`` entry a 500 for the whole
endpoint while looking harmless in review. Touching ``.fields`` on every
serializer class here surfaces them all up front.

Run inside the backend container:

    python scripts/check_serializers.py
"""

import importlib
import inspect
import os
import pkgutil
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from rest_framework import serializers  # noqa: E402


def serializer_modules():
    import services  # noqa: E402

    for mod in pkgutil.walk_packages(services.__path__, "services."):
        if mod.name.endswith(".serializers") or ".serializers" in mod.name:
            yield mod.name


def main():
    problems = []
    checked = 0
    for mod_name in sorted(set(serializer_modules())):
        try:
            module = importlib.import_module(mod_name)
        except Exception as exc:  # noqa: BLE001
            problems.append((mod_name, "IMPORT", str(exc)[:160]))
            continue
        for name, obj in vars(module).items():
            if not inspect.isclass(obj) or not issubclass(obj, serializers.BaseSerializer):
                continue
            if obj.__module__ != mod_name or inspect.isabstract(obj):
                continue
            checked += 1
            try:
                _ = obj().fields
            except Exception as exc:  # noqa: BLE001
                problems.append((f"{mod_name}.{name}", type(exc).__name__, str(exc)[:200]))

    print(f"checked {checked} serializer classes | problems: {len(problems)}\n")
    for where, kind, msg in problems:
        print(f"  {where}\n      {kind}: {msg}")
    print()
    return problems


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
