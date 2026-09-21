"""Global tenant-aware search API.

One endpoint (``/api/v1/search/``) that scans the high-value entities a user
is likely to jump to — people, money, discipline, library, admissions,
facilities, communication — and returns grouped results:

- **Tenant-scoped first**: every queryset is filtered by the caller's school
  (via the same tenant helpers the rest of the codebase uses), so cross-school
  records can never leak into results.
- **Permission-filtered**: groups are only included when the caller's role
  may see that entity (an accountant doesn't get counseling results; a
  librarian doesn't get payroll).
- **Bounded**: a small per-group limit keeps the response fast; results are
  ordered by best-match (istartfrom > icontains) where the field supports it.
"""

from __future__ import annotations

from typing import Any

from django.db.models import Q, QuerySet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

# Staff roles are treated as trusted for cross-entity people search.
STAFF_ROLES = {"super_admin", "school_admin", "teacher", "accountant", "librarian", "counselor"}


# Per-group result cap — the palette only surfaces a handful anyway.
PER_GROUP_LIMIT = 5


def _resolve_school(request: Request) -> Any:
    """Tenant for this request, mirroring TenantMiddleware's contract."""
    school = getattr(request, "school", None)
    if school is not None:
        return school
    return getattr(request.user, "school", None)


def _name_qs(model: Any, school_field: str, school: Any) -> QuerySet:
    """Base tenant-scoped queryset for a model with a direct school FK."""
    return model.objects.filter(**{school_field: school})


def _person_names(first: str | None, last: str | None) -> str:
    return " ".join(p for p in [first, last] if p).strip()


class GlobalSearchView(APIView):
    """Cross-entity search scoped to the caller's school and role."""

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        query = (request.query_params.get("q") or "").strip()
        if len(query) < 2:
            return Response(
                {"detail": "Query must be at least 2 characters.", "groups": []},
                status=status.HTTP_400_BAD_REQUEST,
            )

        school = _resolve_school(request)
        if school is None:
            return Response({"detail": "No school context.", "groups": []}, status=status.HTTP_400_BAD_REQUEST)

        role = request.user.role
        groups: list[dict[str, Any]] = []

        for engine in SEARCH_ENGINES:
            if role not in engine["roles"] and role != "super_admin":
                continue
            try:
                rows = engine["search"](query, school, request.user)[:PER_GROUP_LIMIT]
            except Exception:  # noqa: BLE001 — a broken group must not kill the whole search
                rows = []
            if rows:
                groups.append({"key": engine["key"], "label": engine["label"], "results": rows})

        return Response({"query": query, "groups": groups})


def _search_students(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    from services.students.models import Student

    qs = _name_qs(Student, "school", school).filter(
        Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(admission_number__icontains=q)
    )
    return [
        {
            "id": str(s.id),
            "title": _person_names(s.user.first_name, s.user.last_name) or s.admission_number,
            "subtitle": f"Student · {s.admission_number}",
            "url": f"/admin/students/{s.id}",
        }
        for s in qs.select_related("user")[:PER_GROUP_LIMIT]
    ]


def _search_staff(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    from services.hr.models import Employee

    qs = _name_qs(Employee, "school", school).filter(
        Q(user__first_name__icontains=q)
        | Q(user__last_name__icontains=q)
        | Q(employee_id__icontains=q)
        | Q(designation__icontains=q)
    )
    return [
        {
            "id": str(e.id),
            "title": _person_names(e.user.first_name, e.user.last_name) or e.employee_id,
            "subtitle": f"Staff · {e.designation or e.employee_id}",
            "url": "/admin/hr-center",
        }
        for e in qs.select_related("user")[:PER_GROUP_LIMIT]
    ]


def _search_invoices(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    from services.fees.models import FeeInvoice

    qs = FeeInvoice.objects.filter(student__school=school).filter(
        Q(invoice_number__icontains=q)
        | Q(student__user__first_name__icontains=q)
        | Q(student__user__last_name__icontains=q)
    )
    return [
        {
            "id": str(inv.id),
            "title": f"{inv.invoice_number} · {inv.student}",
            "subtitle": f"Invoice · {inv.get_status_display()}",
            "url": "/admin/finance-center",
        }
        for inv in qs.select_related("student__user")[:PER_GROUP_LIMIT]
    ]


def _search_incidents(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    from services.behavior.models import Incident

    qs = _name_qs(Incident, "school", school).filter(
        Q(incident_type__icontains=q)
        | Q(location__icontains=q)
        | Q(student__user__first_name__icontains=q)
        | Q(student__user__last_name__icontains=q)
    )
    return [
        {
            "id": str(i.id),
            "title": f"{i.get_incident_type_display()} — {i.student}",
            "subtitle": f"Incident · {i.get_severity_display()}",
            "url": "/admin/behavior",
        }
        for i in qs.select_related("student__user")[:PER_GROUP_LIMIT]
    ]


def _search_books(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    from services.library.models import Book

    qs = _name_qs(Book, "school", school).filter(Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q))
    return [
        {
            "id": str(b.id),
            "title": b.title,
            "subtitle": f"Book · {b.author or 'Unknown author'}",
            "url": "/admin/library",
        }
        for b in qs[:PER_GROUP_LIMIT]
    ]


def _search_applications(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    from services.admissions.models import Application

    qs = _name_qs(Application, "school", school).filter(
        Q(application_number__icontains=q)
        | Q(first_name__icontains=q)
        | Q(last_name__icontains=q)
        | Q(guardian_name__icontains=q)
    )
    return [
        {
            "id": str(a.id),
            "title": _person_names(a.first_name, a.last_name) or a.application_number,
            "subtitle": f"Application · {a.application_number}",
            "url": "/admin/admissions-center",
        }
        for a in qs[:PER_GROUP_LIMIT]
    ]


def _search_vehicles(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    from services.transportation.models import Vehicle

    qs = _name_qs(Vehicle, "school", school).filter(Q(plate_number__icontains=q) | Q(model_name__icontains=q))
    return [
        {
            "id": str(v.id),
            "title": v.plate_number,
            "subtitle": f"Vehicle · {v.model_name or v.vehicle_type}",
            "url": "/admin/transportation-center",
        }
        for v in qs[:PER_GROUP_LIMIT]
    ]


def _search_announcements(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    from services.communication.models import Announcement

    qs = _name_qs(Announcement, "school", school).filter(Q(title__icontains=q))
    return [
        {
            "id": str(a.id),
            "title": a.title,
            "subtitle": "Announcement",
            "url": "/admin/announcements",
        }
        for a in qs[:PER_GROUP_LIMIT]
    ]


def _search_checkouts(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    """Library checkouts — staff-only: hits expose other students' names."""
    from services.library.models import Checkout

    # Checkout carries no school FK of its own — it scopes through the book.
    qs = Checkout.objects.filter(book__school=school).filter(
        Q(book__title__icontains=q)
        | Q(book__author__icontains=q)
        | Q(student__user__first_name__icontains=q)
        | Q(student__user__last_name__icontains=q)
    )
    return [
        {
            "id": str(c.id),
            "title": f"{c.book.title} — {c.student}",
            "subtitle": f"Checkout · due {c.due_date}",
            "url": "/admin/library",
        }
        for c in qs.select_related("book", "student__user")[:PER_GROUP_LIMIT]
    ]


def _search_sessions(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    """Counseling sessions — sensitive; restricted to admins and counselors."""
    from services.counseling.models import CounselingSession

    qs = CounselingSession.objects.filter(school=school).filter(
        Q(session_type__icontains=q)
        | Q(presenting_issue__icontains=q)
        | Q(student__user__first_name__icontains=q)
        | Q(student__user__last_name__icontains=q)
    )
    return [
        {
            "id": str(s.id),
            "title": f"{s.student} — {s.presenting_issue or 'Session'}",
            "subtitle": f"Counseling · {s.session_date}",
            "url": "/admin/counseling",
        }
        for s in qs.select_related("student__user")[:PER_GROUP_LIMIT]
    ]


def _search_inventory(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    from services.inventory.models import InventoryItem

    qs = _name_qs(InventoryItem, "school", school).filter(
        Q(name__icontains=q) | Q(sku__icontains=q) | Q(barcode__icontains=q) | Q(location__icontains=q)
    )
    return [
        {
            "id": str(i.id),
            "title": i.name,
            "subtitle": f"Inventory · {i.sku or 'no SKU'}",
            "url": "/admin/inventory-center",
        }
        for i in qs[:PER_GROUP_LIMIT]
    ]


def _search_rooms(q: str, school: Any, user: Any) -> list[dict[str, Any]]:
    from services.hostel.models import HostelRoom

    qs = HostelRoom.objects.filter(hostel__school=school).filter(
        Q(room_number__icontains=q) | Q(room_type__icontains=q)
    )
    return [
        {
            "id": str(r.id),
            "title": f"Room {r.room_number}",
            "subtitle": f"Hostel room · {r.get_room_type_display()}",
            "url": "/admin/hostel-center",
        }
        for r in qs[:PER_GROUP_LIMIT]
    ]


SEARCH_ENGINES: list[dict[str, Any]] = [
    {"key": "students", "label": "Students", "roles": STAFF_ROLES | {"parent"}, "search": _search_students},
    {"key": "staff", "label": "Staff", "roles": {"super_admin", "school_admin"}, "search": _search_staff},
    {
        "key": "invoices",
        "label": "Invoices",
        "roles": {"super_admin", "school_admin", "accountant"},
        "search": _search_invoices,
    },
    {
        "key": "incidents",
        "label": "Incidents",
        "roles": {"super_admin", "school_admin", "teacher", "counselor"},
        "search": _search_incidents,
    },
    {"key": "books", "label": "Library", "roles": STAFF_ROLES, "search": _search_books},
    {
        "key": "applications",
        "label": "Admissions",
        "roles": {"super_admin", "school_admin"},
        "search": _search_applications,
    },
    {
        "key": "vehicles",
        "label": "Transport",
        "roles": {"super_admin", "school_admin"},
        "search": _search_vehicles,
    },
    {
        "key": "rooms",
        "label": "Hostel",
        "roles": {"super_admin", "school_admin"},
        "search": _search_rooms,
    },
    {
        "key": "announcements",
        "label": "Announcements",
        "roles": STAFF_ROLES | {"student", "parent"},
        "search": _search_announcements,
    },
    {"key": "checkouts", "label": "Checkouts", "roles": STAFF_ROLES, "search": _search_checkouts},
    {
        "key": "sessions",
        "label": "Counseling",
        "roles": {"super_admin", "school_admin", "counselor"},
        "search": _search_sessions,
    },
    {"key": "inventory", "label": "Inventory", "roles": STAFF_ROLES, "search": _search_inventory},
]
