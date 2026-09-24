"""Parent portal — per-child data endpoints.

The parent SPA calls ``<app>/…/children/`` for each module so a guardian sees
their own children's data in one place (Health, Library, Cafeteria, Sports,
Behavior, Counseling). Every endpoint:

- scopes strictly to the children linked to the caller via ``Guardian``
  (``Student.objects.filter(guardians__user=user)`` — the same relationship
  the student-list view uses),
- is read-only and permission-gated to parent/guardian roles (admins may also
  call them for convenience, scoped to their own school),
- returns ``{count, results}`` matching the SPA's expectations.

This module is one shared mixin + per-app function-based views so the same
tenant-safety logic is not copy-pasted six times.
"""

from core.permissions import IsSchoolMember
from django.apps import apps
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


def get_parent_children(user):
    """Students linked to this guardian (or all school students for admins)."""
    Student = apps.get_model("students", "Student")
    if user.role in ("school_admin", "super_admin"):
        return Student.objects.filter(school=user.school)
    if user.role in ("parent", "guardian"):
        return Student.objects.filter(guardians__user=user, school=user.school)
    if user.role == "student":
        return Student.objects.filter(user=user)
    return Student.objects.none()


def children_response(data):
    return Response({"count": len(data), "results": data}, status=status.HTTP_200_OK)


def _field(model, *names):
    """Return the first existing field name, else None — tolerant to drift."""
    have = {f.name for f in model._meta.fields}
    for n in names:
        if n in have:
            return n
    return None


def make_children_view(model_label, select_related, out_fields):
    """Build a read-only /children/ view for one model.

    out_fields: list of (api_name, source_path or None-for-same). Display
    fallbacks ("—") are applied for missing values by the serializer layer.
    """

    @api_view(["GET"])
    @permission_classes([IsSchoolMember])
    def view(request):
        app, name = model_label.split(".")
        model = apps.get_model(app, name)
        children = get_parent_children(request.user)
        date_field = _field(model, "occurred_at", "session_date", "awarded_date", "created_at")
        qs = model.objects.filter(student__in=children).select_related(*select_related)
        if date_field:
            qs = qs.order_by("-" + date_field)
        rows = []
        for obj in qs[:200]:
            row = {}
            for api_name, source in out_fields:
                if source is None:
                    source = api_name
                val = obj
                for part in source.split("__"):
                    if val is None:
                        break
                    val = getattr(val, part, None)
                row[api_name] = val
            rows.append(row)
        return children_response(rows)

    view.__name__ = f"{model_label.split('.')[1].lower()}_children"
    return view


# ── health ───────────────────────────────────────────────────────────────────

health_records_children = make_children_view(
    "health_clinic.HealthRecord",
    ["student__user"],
    [
        ("id", None),
        ("student_name", "student__user__full_name"),
        ("blood_type", None),
        ("allergies", None),
        ("chronic_conditions", None),
    ],
)

health_visits_children = make_children_view(
    "health_clinic.NurseVisit",
    ["student__user"],
    [
        ("id", None),
        ("student_name", "student__user__full_name"),
        ("visit_type_display", "visit_type"),
        ("visit_date", None),
        ("diagnosis", None),
    ],
)

health_immunizations_children = make_children_view(
    "health_clinic.Immunization",
    ["student__user"],
    [
        ("id", None),
        ("student_name", "student__user__full_name"),
        ("vaccine_name", None),
        ("dose_number", None),
        ("date_administered", None),
        ("next_due_date", None),
    ],
)


# ── library ──────────────────────────────────────────────────────────────────

library_checkouts_children = make_children_view(
    "library.Checkout",
    ["student__user", "book"],
    [
        ("id", None),
        ("student_name", "student__user__full_name"),
        ("book_title", "book__title"),
        ("due_date", None),
        ("return_date", "returned_at"),
    ],
)

library_fines_children = make_children_view(
    "library.FineManagement",
    ["student__user", "book"],
    [
        ("id", None),
        ("checkout_book_title", "book__title"),
        ("amount", None),
        ("is_paid", "fine_paid"),
    ],
)


# ── cafeteria ────────────────────────────────────────────────────────────────

# MealPreOrder has no menu FK — menu_items holds what the child ordered.
cafeteria_bookings_children = make_children_view(
    "cafeteria.MealPreOrder",
    ["student__user"],
    [
        ("id", None),
        ("student_name", "student__user__full_name"),
        ("menu_name", "menu_items"),
        ("meal_type_display", "meal_type"),
        ("status_display", "status"),
        ("booking_date", "meal_date"),
    ],
)


# ── sports ───────────────────────────────────────────────────────────────────

sports_achievements_children = make_children_view(
    "sports.SportAchievement",
    ["student__user"],
    [
        ("id", None),
        ("student_name", "student__user__full_name"),
        ("title", None),
        ("position", None),
        ("level", None),
        ("awarded_date", None),
    ],
)


@api_view(["GET"])
@permission_classes([IsSchoolMember])
def sports_teams_children(request):
    """Teams the caller's children play on (Team has no student FK of its own)."""
    TeamMember = apps.get_model("sports", "TeamMember")
    children = get_parent_children(request.user)
    memberships = (
        TeamMember.objects.filter(student__in=children).select_related("team", "team__sport").order_by("-joined_date")
    )
    seen = {}
    for m in memberships:
        team = m.team
        if team.pk in seen:
            continue
        seen[team.pk] = {
            "id": str(team.pk),
            "sport_name": getattr(team.sport, "name", None),
            "name": team.name,
            "member_count": team.members.count(),
            "is_active": team.is_active,
        }
    return children_response(list(seen.values()))


# ── behavior ─────────────────────────────────────────────────────────────────

behavior_incidents_children = make_children_view(
    "behavior.Incident",
    ["student__user"],
    [
        ("id", None),
        ("student_name", "student__user__full_name"),
        ("incident_type_display", "incident_type"),
        ("description", None),
        ("severity", None),
        ("incident_date", "occurred_at"),
    ],
)

behavior_points_children = make_children_view(
    "behavior.BehaviorPoint",
    ["student__user"],
    [
        ("id", None),
        ("student_name", "student__user__full_name"),
        ("points", None),
        ("reason", None),
        ("awarded_date", "created_at"),
    ],
)


# ── counseling ───────────────────────────────────────────────────────────────

counseling_sessions_children = make_children_view(
    "counseling.CounselingSession",
    ["student__user", "counselor"],
    [
        ("id", None),
        ("student_name", "student__user__full_name"),
        ("counselor_name", "counselor__full_name"),
        ("session_type", None),
        ("session_date", None),
        ("session_summary", "session_summary"),
    ],
)

counseling_referrals_children = make_children_view(
    "counseling.StudentReferral",
    ["student__user"],
    [
        ("id", None),
        ("student_name", "student__user__full_name"),
        ("category", None),
        ("status", None),
        ("reason", None),
        ("created_at", None),
    ],
)
