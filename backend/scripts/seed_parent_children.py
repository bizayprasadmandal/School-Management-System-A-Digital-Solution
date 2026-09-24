"""Guarantee every guardian-linked child has data per parent-portal category.

The parent SPA's module pages (health, cafeteria, library, sports, behavior,
counseling) read per-child rows from the ``<app>/…/children/`` endpoints,
which scope strictly to the children linked via ``StudentGuardian``. The
generic seeder scatters rows across *all* students, so any particular
guardian's child can easily have nothing in a category — parents then see
empty tabs.

This pass (rerunnable, per school) tops every guardian-linked child up to at
least one row in each of the twelve category models, reusing the generic
seeder's :func:`make_instance` for tenant-safe value generation and then
re-pointing the row's ``student`` FK at the target child (same school).

Usage (inside the backend container):
    python scripts/seed_parent_children.py [School Name]
"""

import os
import random
import sys

sys.path.insert(0, "/app")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django  # noqa: E402

django.setup()

from django.apps import apps  # noqa: E402
from django.db import IntegrityError  # noqa: E402
from seed_empty_models import make_instance  # noqa: E402
from services.auth.models import School  # noqa: E402

# model -> min rows every guardian-linked child should have
CATEGORY_MODELS = [
    ("health_clinic", "HealthRecord"),
    ("health_clinic", "NurseVisit"),
    ("health_clinic", "Immunization"),
    ("cafeteria", "MealPreOrder"),
    ("library", "Checkout"),
    ("library", "FineManagement"),
    ("sports", "TeamMember"),
    ("sports", "SportAchievement"),
    ("behavior", "Incident"),
    ("behavior", "BehaviorPoint"),
    ("counseling", "CounselingSession"),
    ("counseling", "StudentReferral"),
]


def get_school(name):
    try:
        return School.objects.get(name__iexact=name)
    except School.DoesNotExist:
        return School.objects.get(name__icontains=name)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    school = get_school(args[0]) if args else School.objects.first()
    print(f"school: {school.name}")

    StudentGuardian = apps.get_model("students", "StudentGuardian")
    children = list(
        StudentGuardian.objects.filter(student__school=school, guardian__user__school=school).values_list(
            "student_id", flat=True
        )
    )
    children = list(dict.fromkeys(children))  # dedupe, keep order
    print(f"guardian-linked children: {len(children)}")

    created_total = 0
    failed = {}
    for app, name in CATEGORY_MODELS:
        model = apps.get_model(app, name)
        have = set(model.objects.filter(student_id__in=children).values_list("student_id", flat=True))
        missing = [c for c in children if c not in have]
        created = 0
        for child in missing:
            for _ in range(random.randint(1, 2)):
                for attempt in range(3):
                    try:
                        obj = make_instance(model, school, 0, None)
                    except IntegrityError:
                        # random student pick hit a unique (per-student) row
                        continue
                    except Exception as exc:  # noqa: BLE001
                        if attempt == 2:
                            failed.setdefault(f"{app}.{name}", str(exc)[:160])
                        continue
                    try:
                        model.objects.filter(pk=obj.pk).update(student_id=child)
                        created += 1
                    except IntegrityError:
                        # child already has their (unique) row — drop the spare
                        obj.delete()
                    break
        created_total += created
        print(f"  {app}.{name}: +{created} (children covered: {len(children) - len(missing)}/{len(children)})")

    print(f"\ntotal rows created: {created_total}")
    if failed:
        print(f"{len(failed)} models had failures:")
        for label, err in failed.items():
            print(f"  {label}: {err}")


if __name__ == "__main__":
    main()
