"""Dump students serializer fields via Django introspection (manage.py shell)."""

from services.students import serializers as s  # noqa: E402

seen = set()
for name in dir(s):
    if name.endswith("Serializer") and not name.startswith("Meta") and name not in seen:
        seen.add(name)
        cls = getattr(s, name)
        try:
            fields = cls()
            f = list(fields.fields.keys())
            print(name.replace("Serializer", "").lower(), "::", f)
        except Exception as e:  # noqa: BLE001
            print(name, ":: ERR", e)
