"""Dump counseling model choice fields for FE select options."""

from django.db import models as djm
from services.counseling import models as cm

SKIP = {"id", "school", "created_at", "updated_at"}
for name in dir(cm):
    obj = getattr(cm, name)
    if not (isinstance(obj, type) and issubclass(obj, djm.Model)):
        continue
    choices = []
    for f in obj._meta.fields:
        if getattr(f, "choices", None) and f.name not in SKIP:
            choices.append((f.name, [c[0] for c in f.choices]))
    if choices:
        print(f"{name}: " + " | ".join(f"{k}={v}" for k, v in choices))
