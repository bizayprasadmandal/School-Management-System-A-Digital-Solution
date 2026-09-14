"""Dump serializer fields + model choices for reporting/conferences/auth/fees."""

import json
import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django

django.setup()

from rest_framework import serializers  # noqa: E402

MODULES = sys.argv[1:] or ["reporting", "conferences", "auth", "fees"]
out = {}
for mod in MODULES:
    ser_mod = __import__(f"services.{mod}.serializers", fromlist=["*"])
    mod_out = {}
    for name in dir(ser_mod):
        cls = getattr(ser_mod, name)
        if not (isinstance(cls, type) and issubclass(cls, serializers.Serializer) and name.endswith("Serializer")):
            continue
        try:
            inst = cls()
            fields = list(inst.fields.keys())
        except Exception:
            continue
        mod_out[name] = fields
    out[mod] = mod_out

print(json.dumps(out, indent=1))
