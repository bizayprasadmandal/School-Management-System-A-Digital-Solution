"""Dump sports serializer fields via Django introspection (run inside container)."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django  # noqa: E402

django.setup()

from services.sports import serializers as s  # noqa: E402

for name in dir(s):
    if name.endswith("Serializer") and not name.startswith("Meta"):
        cls = getattr(s, name)
        try:
            fields = cls()
            f = list(fields.fields.keys())
            print(name.replace("Serializer", "").lower(), "::", f)
        except Exception as e:  # noqa: BLE001
            print(name, ":: ERR", e)
