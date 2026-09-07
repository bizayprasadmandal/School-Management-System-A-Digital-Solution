"""Dump sports model choice values (run via manage.py shell < script)."""

import importlib  # noqa: E402

from django.db import models  # noqa: E402

mod = importlib.import_module("services.sports.models")
for name in dir(mod):
    cls = getattr(mod, name)
    if isinstance(cls, type) and issubclass(cls, models.Model) and cls is not models.Model:
        for f in cls._meta.get_fields():
            choices = getattr(f, "choices", None)
            if choices and not hasattr(choices, "__call__"):
                print(f"{name}.{f.name} = {[c[0] for c in choices]}")
