"""Static diagnosis of counseling viewsets: check filterset_fields,
ordering_fields, and ordering against each model's real fields.
Run via: docker exec sms_backend python manage.py shell -c "exec(open('scripts/diag_counseling.py').read())"
"""

import re

from services.counseling import views as cv

src = open("/app/services/counseling/views.py", encoding="utf-8").read()

blocks = re.split(r"(?=^class \w+ViewSet)", src, flags=re.M)
problems = []
for b in blocks:
    m = re.match(r"^class (\w+ViewSet)", b)
    if not m:
        continue
    vs_name = m.group(1)
    vs = getattr(cv, vs_name, None)
    if vs is None:
        continue
    model = getattr(getattr(vs, "serializer_class", None), "Meta", None)
    if model is None:
        continue
    model = model.model
    fields = {f.name for f in model._meta.get_fields()}
    bad_fs = [f for f in getattr(vs, "filterset_fields", []) if f not in fields]
    bad_of = [f for f in getattr(vs, "ordering_fields", []) if f not in fields and f != "__all__"]
    ordering = getattr(vs, "ordering", None)
    bad_order = [f for f in ordering if f not in fields] if ordering else []
    if bad_fs or bad_of or bad_order:
        problems.append((vs_name, model.__name__, bad_fs, bad_of, bad_order))

if not problems:
    print("ALL CLEAN")
for vs_name, model_name, bad_fs, bad_of, bad_order in problems:
    print(f"{vs_name} ({model_name}): filterset={bad_fs} ordering_fields={bad_of} ordering={bad_order}")
