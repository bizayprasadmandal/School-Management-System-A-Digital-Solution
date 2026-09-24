"""Seed every still-empty school-scoped model for the demo school.

The deep UI walk leaves ~150 tabs rendering "EMPTY (0 rows)" — not bugs, just
models nobody seeded (siblings, parking, lesson plans, portfolios, MFA methods,
login history, …). This script enumerates every model under ``services.*``,
keeps the ones that are empty for the demo school, topologically orders them by
FK dependencies, and creates a handful of plausible rows each by introspecting
the model's fields.

Rerunnable: unique suffixes keep it collision-free, and already-populated
models are skipped. Usage (inside the backend container):

    python scripts/seed_empty_models.py [school_name] [--dry-run]
"""

import os
import random
import sys
import uuid
from datetime import timedelta
from decimal import Decimal

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from django.apps import apps  # noqa: E402
from django.db import models as djm  # noqa: E402
from django.utils import timezone  # noqa: E402
from services.auth.models import School  # noqa: E402

WORDS = [
    "Alpha",
    "Bright",
    "Cedar",
    "Delta",
    "Everest",
    "Falcon",
    "Gemini",
    "Horizon",
    "Iris",
    "Jupiter",
    "Kepler",
    "Lumen",
    "Meridian",
    "Nova",
    "Orion",
    "Pulse",
    "Quartz",
    "Radiant",
    "Summit",
    "Titan",
    "Unity",
    "Voyager",
    "Zenith",
]
NOTES = [
    "Seeded demo entry generated for UI verification.",
    "Sample record created by the demo seeder.",
    "Placeholder row so the panel tab shows real data.",
    "Auto-generated demo content — safe to delete.",
]

MAX_DEPTH = 4
ROWS_PER_MODEL = 5
uniq_suffix = uuid.uuid4().hex[:6]
created_count = {}
failed = {}


def get_school(name):
    school = School.objects.filter(name__icontains=name).first()
    if school is None:
        school = School.objects.first()
    return school


_school_path_cache = {}


def school_path(model, seen=None):
    """Shortest FK chain (names, child→parent) from this model to School.

    Returns e.g. ['room', 'hostel', 'school'] for HostelAllocation. None when
    no route exists. Used to scope child models that lack a direct school FK.
    """
    if seen is None and model in _school_path_cache:
        return _school_path_cache[model]
    result = _school_path_uncached(model, seen)
    if seen is None:
        _school_path_cache[model] = result
    return result


def _school_path_uncached(model, seen=None):
    seen = seen or set()
    if model is School:
        return []
    if model in seen:
        return None
    best = None
    for f in model._meta.get_fields():
        if f.is_relation and (f.many_to_one or f.one_to_one):
            sub = school_path(f.related_model, seen | {model})
            if sub is not None and (best is None or len(sub) + 1 < len(best)):
                best = [f.name] + sub
    return best


def school_scope_kwargs(model, school):
    """Filter kwargs scoping the model to the school via its FK chain."""
    path = school_path(model)
    if not path or path[-1] != "school":
        return None
    # path names every FK hop, the last being the FK onto School itself
    return {"__".join(path): school}


def all_school_paths(model, seen=None):
    """Every FK path (names, child→School) from model, depth-capped, no cycles."""
    seen = seen or set()
    if model is School:
        return [[]]
    if model in seen or len(seen) >= MAX_DEPTH:
        return []
    paths = []
    for f in model._meta.get_fields():
        if f.is_relation and (f.many_to_one or f.one_to_one):
            for sub in all_school_paths(f.related_model, seen | {model}):
                paths.append([f.name] + sub)
    return paths


def is_empty(model, school):
    """True when NO row for this school exists via ANY FK path.

    Multi-FK models (e.g. WearableIntegration: student→school AND
    team→school) may have rows reachable through one path but zero through
    another — viewsets scope through different paths, so every path must
    have rows for the tab to show data.
    """
    if model._meta.proxy or model._meta.abstract or model._meta.auto_created:
        return False
    for path in all_school_paths(model):
        if not path:
            continue  # the model IS School — nothing to seed
        if not model._default_manager.filter(**{"__".join(path): school}).exists():
            return True
    return False


def school_fk_field(model):
    """Direct school FK — includes OneToOneField (per-school singleton configs)."""
    for field in model._meta.get_fields():
        if field.is_relation and (field.many_to_one or field.one_to_one) and field.related_model is School:
            return field
    return None


def uniques(model):
    names = set()
    for c in model._meta.constraints:
        fields = getattr(c, "fields", None)
        if fields and getattr(c, "unique", False):
            names.update(fields)
    for fields in model._meta.unique_together:
        names.update(fields)
    for f in model._meta.fields:
        if f.unique:
            names.add(f.name)
    return names


def value_for_field(field, model, school, i, depth, cache):
    """Build a plausible value for one concrete field."""
    internal = field.get_internal_type()
    name = field.name

    if isinstance(field, djm.AutoField):
        return None  # auto

    # relations ----------------------------------------------------------
    if field.is_relation and (field.many_to_one or field.one_to_one):
        if field.related_model is School:
            return school
        # null or default → leave alone — but ONLY when the target is a
        # global (non-tenant) lookup. A default like ``default=1`` on a
        # tenant-scoped FK points at *some* school's row → cross-tenant link.
        target_path = school_path(field.related_model)
        if field.null and not field.has_default():
            # nullable FK to a TENANT-SCOPED target: leaving it NULL hides the
            # row from every tenant viewset (e.g. WearableIntegration.team).
            # Fill it via the same-school pick/create logic below; only
            # global (non-tenant) targets may stay NULL.
            if target_path is None or depth >= MAX_DEPTH:
                return None
        if field.has_default() and target_path is None:
            return field.get_default()

        if field.one_to_one and depth < MAX_DEPTH:
            # OneToOne FKs must get a FRESH parent — reusing an existing row
            # collides with the unique constraint on tiny demo pools.
            return make_instance(field.related_model, school, depth + 1, cache)

        qs = field.related_model._default_manager.all()
        # STRICT tenant scoping: only same-school parents, ever. Reusing a
        # cross-tenant row is what previously linked Green Valley's rooms to
        # another school's hostels (empty tabs everywhere).
        rel_school_field = school_fk_field(field.related_model)
        if rel_school_field is not None:
            qs = qs.filter(**{rel_school_field.name: school})
        else:
            scope = school_scope_kwargs(field.related_model, school)
            if scope is not None:
                qs = qs.filter(**scope)
        obj = qs.order_by("?").first()
        if obj is not None:
            return obj
        # no same-school parent exists → create one (never fall back to
        # another school's rows)
        if depth < MAX_DEPTH:
            return make_instance(field.related_model, school, depth + 1, cache)
        return None  # give up; DB will complain and we record it

    # visibility booleans: rows with these False are filtered out by their
    # viewsets (moderation, activation), leaving tabs permanently empty.
    # Demo data must be visible, so force them True when generating.
    VISIBILITY_TRUE = {"is_approved", "is_active", "is_published", "is_visible", "is_public", "is_enabled"}

    has_default = field.has_default()

    # choices ------------------------------------------------------------
    choices = getattr(field, "choices", None)
    if choices:
        flat = [c[0] for c in choices if not isinstance(c[1], (list, tuple))]
        for c in choices:
            if isinstance(c[1], (list, tuple)):
                flat.extend(x[0] for x in c[1])
        if flat:
            return flat[i % len(flat)] if not has_default else field.get_default()

    if has_default and internal not in ("CharField", "TextField", "SlugField"):
        return field.get_default()

    # by internal type ----------------------------------------------------
    # string fields: always generate real content — defaults are often ""
    # which collides on unique constraints (e.g. slug fields)
    if internal in ("CharField", "TextField", "SlugField"):
        word = WORDS[(i + len(model.__name__)) % len(WORDS)]
        if any(k in name for k in ("email", "mail")):
            val = f"demo.{name.replace('email', '')}{uniq_suffix}@greenvalley.edu"
        elif "phone" in name or "mobile" in name:
            val = f"+97798{random.randint(10000000, 99999999)}"
        elif "url" in name or "link" in name:
            val = f"https://demo.greenvalley.edu/{name}/{uniq_suffix}"
        elif "code" in name or "slug" in name:
            val = f"{model.__name__[:8].upper()}-{name[:6].upper()}-{uniq_suffix}{i}"
        elif any(k in name for k in ("color", "hex")):
            val = "#4F46E5"
        elif "number" in name and "phone" not in name:
            val = f"{random.randint(1000, 999999)}"
        elif any(k in name for k in ("description", "notes", "comment", "summary", "content", "body", "text")):
            val = random.choice(NOTES)
        else:
            val = f"{word} {name.replace('_', ' ').title() or model.__name__} {uniq_suffix[:4]}{i}"
        max_len = getattr(field, "max_length", None)
        if max_len and max_len <= 12:
            # short enum-ish fields (semester, term, day, code, …): compact token
            val = f"{name[:5]}{i}"
        return val[:max_len] if max_len else val

    if internal in ("BooleanField", "NullBooleanField"):
        if name in VISIBILITY_TRUE:
            return True
        return i % 2 == 0

    if internal.endswith("IntegerField"):
        return random.randint(1, 100)

    if internal == "DecimalField":
        int_digits = max(1, field.max_digits - field.decimal_places)
        max_val = 10**int_digits - 1
        return Decimal(random.randint(1, max_val)).quantize(Decimal(10) ** -field.decimal_places)

    if internal == "FloatField":
        return round(random.uniform(1, 500), 2)

    if internal == "DateTimeField":
        return timezone.now() - timedelta(days=random.randint(0, 30))

    if internal == "DateField":
        return (timezone.now() - timedelta(days=random.randint(0, 30))).date()

    if internal == "TimeField":
        return timezone.now().time().replace(microsecond=0)

    if internal == "DurationField":
        return timedelta(minutes=random.randint(30, 120))

    if internal in ("JSONField",):
        return {"seeded": True, "note": "demo"}

    if internal == "UUIDField":
        return uuid.uuid4()

    if internal in ("IPAddressField", "GenericIPAddressField"):
        return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

    return None


def make_instance(model, school, depth=0, cache=None):
    """Create one instance, recursively creating missing FK parents."""
    kwargs = {}
    unique_fields = uniques(model)
    for field in model._meta.fields:
        if field.primary_key:
            continue
        val = value_for_field(field, model, school, len(created_count), depth, cache)
        if val is not None:
            kwargs[field.name] = val
    # tenant anchor: if the model has a direct school FK, ALWAYS set it —
    # even when nullable. Leaving it NULL (the nullable-FK branch above
    # returns None) creates school-less parents that tenant-scoped
    # viewsets can never see (e.g. ReportAccessControl → school-less User).
    sfk = school_fk_field(model)
    if sfk is not None:
        kwargs[sfk.name] = school
    # guarantee uniqueness on unique-constrained fields
    IP_TYPES = {"IPAddressField", "GenericIPAddressField"}
    for fname in unique_fields & set(kwargs):
        cur = kwargs[fname]
        f = model._meta.get_field(fname)
        if f.get_internal_type() in IP_TYPES:
            continue  # suffixing breaks inet syntax; random value suffices
        if isinstance(cur, str):
            ml = getattr(f, "max_length", None)
            suffix = f"-{uniq_suffix}{random.randint(100, 999)}"
            if not ml:
                kwargs[fname] = cur + suffix
            elif ml - len(suffix) >= 1:
                kwargs[fname] = cur[: ml - len(suffix)] + suffix
            else:
                # suffix doesn't fit the column — a short random token is the
                # only thing that both fits and stays unique
                kwargs[fname] = uuid.uuid4().hex[:ml]
        elif isinstance(cur, int):
            # integer uniques (version_number etc.): nudge off the default so
            # retries don't reproduce the same collision
            kwargs[fname] = cur + random.randint(1, 9)
    obj = model._default_manager.create(**kwargs)
    return obj


def seed_model(model, school):
    created = 0
    target = ROWS_PER_MODEL
    # singletons-ish models: policy/config models get 2
    if any(k in model.__name__.lower() for k in ("policy", "setting", "config")):
        target = 2
    # but OneToOne-per-school configs MUST stay at 1 — a second row for the
    # same school violates the unique school FK and aborts the whole model
    o2o_school = any(f.one_to_one and f.related_model is School for f in model._meta.fields if f.is_relation)
    if o2o_school:
        target = 1
    for i in range(target):
        # retry each row a few times — random FK picks can collide with
        # unique_together constraints; a retry regenerates all values
        for attempt in range(3):
            try:
                make_instance(model, school, 0, None)
                created += 1
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 2:
                    failed.setdefault(model._meta.label, str(exc)[:200])
    created_count[model._meta.label] = created


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    school_name = args[0] if args else "Green Valley"
    dry = "--dry-run" in sys.argv
    school = get_school(school_name)
    print(f"seeding school: {school}")

    all_models = []
    for app_conf in apps.get_app_configs():
        if not app_conf.name.startswith("services."):
            continue
        for m in app_conf.get_models():
            all_models.append(m)

    seedable = [m for m in all_models if is_empty(m, school)]
    print(f"{len(all_models)} service models, {len(seedable)} empty for this school")

    if dry:
        for m in seedable:
            print(" -", m._meta.label)
        return

    # order: models whose FK targets are already populated / none first
    def dependency_count(m):
        n = 0
        for f in m._meta.fields:
            if f.is_relation and f.many_to_one and f.related_model is not School:
                if f.related_model in seedable:
                    n += 1
        return n

    seedable.sort(key=dependency_count)

    for m in seedable:
        seed_model(m, school)

    ok = {k: v for k, v in created_count.items() if v}
    print(f"\nseeded rows into {len(ok)} models ({sum(ok.values())} rows total)")
    if failed:
        print(f"\n{len(failed)} models failed:")
        for label, err in sorted(failed.items()):
            print(f"  {label}: {err[:160]}")


if __name__ == "__main__":
    main()
