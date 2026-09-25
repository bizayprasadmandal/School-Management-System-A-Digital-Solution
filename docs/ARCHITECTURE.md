# Architecture Decision Records — EduSphere SMS

## ADR-001: Multi-tenancy via School FK (not schema separation)

**Status:** Accepted  
**Context:** The system must serve multiple schools on one deployment.  
**Decision:** Use a `school` ForeignKey on every model + middleware tenant resolution.  
**Rationale:** Schema-per-tenant (PostgreSQL schemas) requires complex migration tooling.
Row-level isolation with indexed `school_id` + middleware enforcement is simpler,
performs well up to tens of thousands of records per school, and is audited at the
ORM queryset level. Super admins bypass this for cross-school reporting.  
**Consequences:** Every queryset must include `filter(school=request.user.school)`.
Enforced by `IsSchoolMember` permission + base queryset in every ViewSet.

---

## ADR-002: Django Monolith with Service Layer (not true microservices)

**Status:** Accepted  
**Context:** True microservices add operational overhead (service mesh, distributed tracing,
inter-service auth). The team is small.  
**Decision:** One Django process divided into service modules (`services/students/`,
`services/attendance/`, etc.) sharing one database and one deployable, scaled by
adding replicas behind an HPA.  
**Rationale:** Gives logical separation (23 modules, ~940 models, migrations and
routers per module) without the distributed-systems complexity. Services
communicate via Django ORM, not HTTP.  
**Consequences:** The whole backend ships or rolls back as one image — a module
cannot be deployed independently, only scaled horizontally. Can be migrated to
true microservices later by extracting service modules.

---

## ADR-003: Celery for all async work (not Django Signals for I/O)

**Status:** Accepted  
**Context:** Sending emails, push notifications, generating PDFs are slow I/O-bound operations.  
**Decision:** Django signals dispatch Celery tasks; Celery workers do the actual I/O.  
**Rationale:** Signals fire synchronously in the request cycle. Using them directly for
email/push would add 500ms+ to every attendance record save. Celery offloads this.  
**Consequences:** Redis is a required dependency. Tasks must be idempotent (use
`get_or_create` patterns). Failed tasks retry with exponential backoff.

---

## ADR-004: JWT over Session Auth for API

**Status:** Accepted  
**Context:** The system serves web, mobile, and third-party API consumers.  
**Decision:** `djangorestframework-simplejwt` with 60-minute access tokens and 7-day
rotating refresh tokens stored in memory (web) or SecureStore (mobile).  
**Rationale:** Sessions don't work well for mobile clients or cross-origin SPAs.
JWT is stateless, scales horizontally without sticky sessions.  
**Consequences:** Token blacklisting (on logout) requires Redis lookup.
Short access token lifetime reduces revocation window.

---

## ADR-005: WebSocket via Django Channels + Redis Channel Layer

**Status:** Accepted  
**Context:** Real-time chat, live attendance, and push notifications require persistent connections.  
**Decision:** Django Channels with `channels-redis` channel layer.  
**Rationale:** Integrates natively with Django ORM and auth. Redis pub/sub handles
message fan-out across multiple Gunicorn/Uvicorn workers.  
**Consequences:** Must use `UvicornWorker` (ASGI), not standard WSGI workers.
Redis becomes a critical dependency for WebSocket routing.

---

## ADR-006: React Query for frontend data fetching

**Status:** Accepted  
**Context:** Need caching, background refresh, optimistic updates, and pagination.  
**Decision:** TanStack React Query with a centralised query key factory.  
**Rationale:** Eliminates boilerplate Redux/Context data fetching patterns.
Automatic cache invalidation on mutations. Server-state vs UI-state separation is clean.  
**Consequences:** Learning curve for developers unfamiliar with React Query.
Cache invalidation logic must be co-located with mutations.

---

## ADR-007: ReportLab for PDF generation (not headless Chrome)

**Status:** Accepted  
**Context:** Report cards, attendance PDFs, fee receipts.  
**Decision:** ReportLab programmatic PDF generation via Celery workers.  
**Rationale:** Headless Chrome (Puppeteer) requires significant memory (~150MB per instance)
and is fragile in containers. ReportLab generates PDFs programmatically with ~10MB memory.
Templates are Python code, not HTML, which fits better with backend service architecture.  
**Consequences:** PDF styling is code-based, not CSS. Design updates require code changes.

---

## ADR-008: Kubernetes HPA over manual scaling

**Status:** Accepted  
**Context:** School load is highly variable — spikes during exam results, start of term.  
**Decision:** HPA on CPU (70%) + memory (80%) for backend pods, independent HPA for Celery.  
**Rationale:** Predictable but unpredictable spike patterns (term start, results day) are
well-suited to reactive autoscaling. Manual scaling requires human intervention.  
**Consequences:** Cold-start latency when scaling up (~60s for new pod readiness).
PodDisruptionBudgets ensure at least 1 pod stays running during upgrades.

---

## ADR-009: OpenAPI schema generated from the code (drf-spectacular)

**Status:** Accepted (2026-09)  
**Context:** The API surface is ~4 400 URL patterns across 23 modules. A
hand-written reference drifts within days, and consumers (the React SPA, the Expo
app, partner integrations) need accurate request/response shapes.  
**Decision:** Serve `drf-spectacular`'s generated OpenAPI 3 document at
`/api/schema/`, with Swagger UI at `/api/docs/` and ReDoc at `/api/redoc/`. Two
project-specific pieces make the output usable: a `TaggedAutoSchema` that tags
each operation by the URL segment after `/api/v1/` (the default prefix splitting
collapsed all 2 200 operations into one `v1` tag), and an
`OpenApiAuthenticationExtension` that registers
`core.authentication.JWTAuthenticationWithTenant` as the `jwtAuth` HTTP bearer
scheme so Swagger's Authorize button works. Both are wired from `core/urls.py`,
which is the earliest import every entry point (ASGI app, `spectacular`
management command, test client) is guaranteed to hit.  
**Rationale:** The schema is derived from the same serializers the API uses, so
this class of drift is structurally impossible; `--validate` turns schema
problems into CI noise rather than production surprises.  
**Consequences:** Schema generation introspects every view, so viewsets whose
`get_queryset`/`get_permissions` assume an authenticated user must guard against
anonymous/non-request access — the failures are real bugs that also bite
`AnonymousUser` requests. Plain `APIView`s without a `serializer_class` are
documented as empty operations and reported as warnings (34 unique views today).
Schema generation is slow (~6 minutes for the full document), so the regression
suite generates it once per session (`backend/tests/test_api_schema.py`).

---

## ADR-010: Role portals are scoped views over shared module endpoints

**Status:** Accepted (2026-09)  
**Context:** The parent, student and teacher portals each needed read access to
module data (health, library, cafeteria, behavior, sports, counseling, …). The
cheap options were duplicate per-role endpoints, client-side filtering of
school-wide lists, or scoping the existing endpoints.  
**Decision:** Keep one endpoint per resource and scope it by the caller's role.
Guardians read `<module>/…/children/` routes (`backend/core/parent_portal.py`)
scoped to children linked via `StudentGuardian` and bounded by the caller's
school; students get self-scoped rows from the behavior, health, cafeteria and
hostel viewsets when `role == "student"`.  
**Rationale:** One query path per resource means one place to enforce tenant
(and now guardian) isolation, and no way for a portal page to silently fetch
another family's data. Duplicated endpoints would have doubled the isolation
surface — 12 new read endpoints instead of 12 new leak sites.  
**Consequences:** The literal `children` routes must be registered **before** the
module's DRF router, otherwise `children` is captured as a detail-route `pk`.
Viewsets that mix admin and self-service access need their scoping expressed in
the queryset (see `backend/tests/test_parent_portal_children.py` and the student
self-scoping tests).
