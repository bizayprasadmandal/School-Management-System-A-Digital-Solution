"""Dump model choice fields for reporting/conferences/auth/fees."""

import json
import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django

django.setup()

MODULES = sys.argv[1:] or ["reporting", "conferences", "auth", "fees"]
out = {}
for mod in MODULES:
    models_mod = __import__(f"services.{mod}.models", fromlist=["*"])
    mod_out = {}
    for name in dir(models_mod):
        obj = getattr(models_mod, name)
        if not (isinstance(obj, type) and hasattr(obj, "_meta") and getattr(obj._meta, "pk", None)):
            continue
        try:
            if obj._meta.abstract:
                continue
        except Exception:
            continue
        choices = {}
        for f in obj._meta.fields:
            if getattr(f, "choices", None):
                choices[f.name] = [c[0] for c in f.choices]
        if choices:
            mod_out[name] = choices
    out[mod] = mod_out

print(json.dumps(out, indent=1))
