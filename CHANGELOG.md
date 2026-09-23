# Changelog

All notable changes to EduSphere SMS are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **Platform vs school dashboard routing** — `/admin` now renders the school
  dashboard whenever a super admin has a school selected, and the platform
  dashboard only in platform mode (previously it keyed off role alone, so a
  switched school still showed cross-school platform data).

- **Vite dev-server file watching** — `server.watch.usePolling` is enabled so
  edits made on the host are picked up inside the container. Without it,
  Docker's bind mount swallowed inotify events and the dev server kept serving
  a stale module graph (edits appeared "not applied" until a restart).

- **CORS fix for the school switcher** — `X-School-ID` (sent on every request
  while a super admin operates in a school context) was missing from
  `CORS_ALLOW_HEADERS`, so the browser's preflight failed and _every_ API call
  was blocked with a CORS policy error once a school was selected. The header
  is now explicitly allowed; preflight verified live (200 +
  `Access-Control-Allow-Headers: … x-school-id`), pinned by 2 tests.

- **WebSocket handshake fix** — the browser aborts the connection when the
  client offers `Sec-WebSocket-Protocol: Bearer, <token>` but the server
  echoes none back (RFC 6455). `JWTAuthMiddleware` now records the offered
  auth subprotocol in the scope and all consumers (notifications, chat,
  live attendance) echo it in `accept(subprotocol=...)`. Verified: WSCONNECT
  stays open, zero console errors in a real browser.

- **Super admin school switcher now works end-to-end** — selecting a school
  in the switcher actually swaps the data. The tenant context (and an
  in-memory tenant override on the resolved user, guarded by a `pre_save`
  hook so it can never be persisted) is now injected at JWT authentication
  time via `JWTAuthenticationWithTenant`, fixing the 403s/empty lists school
  pages showed for super admins. Frontend invalidates the whole react-query
  cache on switch. Tests: header-override is ignored for non-super roles,
  super-admin cross-tenant reads, persistence guard.

- **Two-mode super admin console** — super admins now land in a dedicated
  platform console (Platform Dashboard, Tenants → Schools/Revenue & Plans,
  Governance → Audit Logs) instead of the school-admin sidebar. Selecting a
  school in the switcher flips into school mode (full school nav, scoped to
  that school) with an "exit" affordance back to the platform. Backend:
  `GET /auth/platform/revenue/` (per-school tier/MRR/ARR + platform totals),
  super-admin cross-school audit-log access with `school_name` on rows.

- **Per-tier pricing on the Plan & Billing page** — `TIER_PRICING` registry
  (NPR per-student monthly + yearly rates, basic free, annual = 10× monthly)
  exposed through `GET /auth/plan/`; the page renders three pricing cards with
  the current tier highlighted and prices the upgrade/downgrade CTA directly
  ("Upgrade to Premium · Rs. 60.00/student/mo").

- **In-app Plan & Billing page** (`/admin/plan-billing`) — current tier card
  with plan badges, the tiered feature matrix (per-tier availability from the
  registry via `GET /auth/plan/`), and an upgrade/downgrade CTA for school
  admins through `POST /auth/plan/change-tier/` (validated, idempotent-reject,
  audit-logged). Non-admins see a read-only view. 5 backend + 6 frontend tests;
  verified live in both directions.

- **Plan gating UI** — plan badges in the admin header (from `/auth/me/`
  `plan_features`), `PlanGate`/`UpgradePrompt` components, and locking on all
  gated surfaces: ledger summary/trend, at-risk/funnel/forecast analytics,
  finance-ops card, and live transport tracking tabs. Center pages now honor
  `?tab=` deep links (previously silently ignored). Fail-open until plan data
  loads. 9 jest tests; verified live in both premium and standard states.

- **Subscription plan gating** (`core/plan_features.py` + `IsPremiumFeature`):
  `School.subscription_tier` (basic/standard/premium) now enforces tiered
  features — premium unlocks the double-entry ledger depth (summary/trend),
  advanced analytics (at-risk, funnel, forecast), live transport tracking
  (bus tracking, stop ETAs, geofences), and finance overview; standard keeps
  the finance overview plus the full core SIS. `/auth/me/` now returns
  `plan_features` (plan, unlocked feature keys, is_premium) so the UI can
  badge gated surfaces. 11 tests pin registry semantics, enforcement, and
  discovery.

- **Finance & Operations dashboard section** (`GET /api/v1/reporting/finance-ops/`):
  one aggregated round-trip for the admin dashboard — payroll committed this month
  (net, payslip count, drafts pending), fee collections this month, outstanding
  invoices, and operations health (open hostel maintenance, open complaints, stock
  alerts, fleet size). Rendered as two new cards on the admin dashboard with
  drill-down links to the finance/hostel/inventory/transport centers.

- **Wide API coverage for hostel/transport/inventory** (31 create-through-the-API
  tests + tenant isolation + 401): surfaced and fixed a `hostel-asset` 500
  (unique-but-blank `asset_tag` collided on empty string; now derives a
  collision-safe tag) and a `geofence-zone` 400 (serializer demanded writable
  `school` while the viewset never injected it).

- **Global tenant-aware search** (`GET /api/v1/search/`): one permission-filtered
  endpoint scanning nine high-value entities (students, staff, invoices, incidents,
  books, applications, vehicles, hostel rooms, announcements) with grouped results,
  per-role visibility (accountants see invoices but not incidents; students see
  announcements only), and strict school scoping. The Ctrl+K command palette now
  debounces (250 ms) queries ≥2 chars into it, merging remote record hits (title,
  subtitle, deep link) under local nav matches.

- **Public application portal** (`services/admissions`): unauthenticated `POST /admissions/public/apply/`, `GET /admissions/public/status/{tracking_id}/`, and `GET /admissions/public/intakes/` endpoints; entrance assessment model (`EntranceAssessment`) linked to applications; frontend pages (`/apply`, `/apply/status`) with form validation and status tracking.
- **Admissions state machine**: enforced valid transitions (applied → screening → interview → offer → enrolled → waitlisted → rejected → withdrawn); status-change emails sent to applicants on each transition.
- **Offer deadlines**: configurable `offer_deadline` on applications with Celery auto-expiry task; deadline-expired emails sent to applicants.
- **Guardian account on enrollment**: automatically creates a parent/guardian user account and sends welcome notification with temporary password when application is marked enrolled.
- **i18n (Nepal market)**: `i18next` + `react-i18next` setup with English and Nepali translation files; `LanguageSwitcher` component in admin header; `useTranslation` hooks wired into login page, sidebar, and common labels.
- **CRA → Vite migration**: replaced `react-scripts` with Vite 6 for dev server and production build; ~5x faster dev startup, ~20s builds; source code retains `process.env.REACT_APP_*` (mapped via Vite `define` for Jest compatibility); Dockerfile, entrypoint, CI workflows, and nginx config updated for Vite.
- **Grade-change audit trail** (`gradebook.GradeChangeLog`): immutable log of every
  grade create/update/delete (single, bulk, and CSV-import paths) with before/after
  values, actor, and timestamp. Read-only `GET /api/v1/gradebook/grades/history/`
  endpoint for school admins.
- **Analytics endpoints** (`reporting`): `at-risk-students/` (attendance + academic
  thresholds), `enrollment-funnel/` (admissions pipeline conversion), and
  `fee-forecast/` (90-day fee windows + trailing 3-month collection history).
- **Attendance CSV import** (`POST /api/v1/attendance/import-csv/`): upserts daily
  records by admission number with per-row error reporting.
- **Fee invoice CSV import** (`POST /api/v1/fees/invoices/import-csv/`): creates
  invoices resolved against existing fee structures, with per-row error reporting.
- **Database backup pipeline** (`infrastructure`): Celery task `create_database_backup`
  (pg_dump → gzip → local `SMS_BACKUP_DIR`, optional S3 mirror with
  `BACKUP_S3_BUCKET`, retention-pruned via `SMS_BACKUP_RETENTION_DAYS`), wired into
  docker-compose, Kubernetes (sms-backups-pvc volume), and Prometheus backup-alert
  rules; `verify_backup.sh` for restore validation.
- Product & project artifacts: `CHANGELOG.md`, `docs/PRD.md`, `docs/ROADMAP.md`.

### Security

- **Removed GraphQL** (Graphene-Django): eliminated unused `/graphql/` endpoint and dependency; removed `graphene_django` from `INSTALLED_APPS` and `requirements.txt`.
- **WebSocket authentication hardened**: notifications channel now requires `Sec-WebSocket-Protocol: jwt` header; unauthenticated connections rejected.
- **Admin IP allowlist**: configurable `ADMIN_IP_ALLOWLIST` env var to restrict Django admin access to trusted IPs.
- **Monitoring basic auth**: Alertmanager and Prometheus ingress endpoints protected with basic auth.
- **Password reset tokens are now stored as SHA-256 digests**; the plaintext is only
  sent in the reset email and never persisted. Tokens created before this change are
  unrecoverable by design.
- **2FA login no longer mints and discards JWTs**: `LoginView` returns only the 2FA
  challenge; the token is minted by `verify-2fa`.
- **Role-based action allowlists** across gradebook, HR, attendance, students,
  inventory, conferences, communication, reporting, and fees (admin/teacher/staff
  gates; e.g. attendance CSV import is admin-only, teachers can bulk-submit grades).
- **Tenant isolation hardening**: an authenticated non-super-admin can never be
  redirected to another tenant via the `X-School-ID` header; reporting scopes to the
  authenticated user's school.

### Fixed

- **Authenticated request throttle starved the whole admin UI** — `user` was
  capped at 500 requests/hour, but the SPA fires 10-25 calls per page view plus
  background polling (unread-count every 30s), so a normal session ran out and
  _every_ endpoint answered 429 for the rest of the hour (pages rendered empty
  and looked "disconnected"). Raised to a per-user 6000/hour default, overridable
  with `USER_THROTTLE_RATE`; documented in `.env.example`.

- **`User` was missing `get_full_name()`** — `AbstractBaseUser` does not provide
  it (only `AbstractUser` does). ~160 serializer fields use
  `source="…get_full_name"`, and since DRF silently skips a read-only field whose
  attribute is missing, every "…name" column (communication 38, timetable 35,
  attendance 35, cafeteria 27, health 17, library 13, …) rendered **blank**; the
  6 sites that _called_ it raised `AttributeError` and 500'd their endpoints
  (free-reduced, online-order, meal-pre-order, meal-subscription). Both
  `get_full_name()` and `get_short_name()` now exist on the model.

- **Seven serializers declared a field that a botched edit had glued into the
  previous entry** (`"voted_at" "poll_title",`), so DRF raised
  `AssertionError: The field … was declared but has not been included in the
'fields' option` and the endpoint 500'd (communication `poll-vote`,
  `conference-attendee`, `read-receipt`, `typing-indicator`, `message-reaction`;
  timetable `class-group-enrollment`, `exam-seating`). Added
  `scripts/check_serializers.py`, which instantiates all 932 serializer classes
  so this class of error can't reach an endpoint again (currently 0 problems).

- **Five more endpoints returned 500** and left their pages blank:
  `hr/hr-dashboard/metrics/` (`get_or_create` blew up once a school had more
  than one metrics row — the latest snapshot is now selected explicitly),
  `hr/performance-reviews/` (prefetched a non-existent `goals` relation),
  `hr/training-programs/` (annotated over a model _property_ of the same name),
  `attendance/records/dashboard/` (`grade__academic_year__is_current` — `Grade`
  has no academic-year FK; classrooms are now scoped through their active
  enrollments), `fees/dashboard/realtime/` and `fees/invoices/aging-report/`
  (`student__classroom` — the student→classroom link is `Enrollment`; the aging
  report also built a `Greatest(DateField, 0)` expression Django rejects).
  Verified with `scripts/sweep_api_endpoints.py`: all **1104 parameterless
  routes** now answer without a single 5xx.

- **HR Center shipped a dead duplicate tab** — `hr-dashboard` pointed at a list
  endpoint that does not exist (the viewset only exposes
  `hr-dashboard/metrics/`), so "H R Dashboard Metrics" always rendered a 404; the
  real entry (`hr-dashboard-metrics`) is kept.

- **Docker**: the sms redis no longer binds host port 6379 (owned by the
  bus-ticket-booking stack); it is exposed on **6380** instead — both projects
  can now run side by side.

- Teacher grade listing now resolves via the real `TeacherAssignment` relation
  (`subject__assignments__teacher` / invigilator) instead of the non-existent
  `exam_schedule__assignment` lookup — the old query raised on every teacher grade
  request.
- Attendance streak test was timezone-dependent (`date.today()` vs
  `timezone.now().date()`); now deterministic on any machine timezone.
- **Counseling create endpoints returned 500** when `send_reminder` /
  `notify_counselor` flags were passed (write-only fields leaked into
  `Model.save()`); serializers now pop them before saving.
- **Communication `DeviceTokenView.destroy` raised `NameError`** (`DeviceToken` was
  never imported); the token is now resolved from the model and deactivated.
- **The suite could not run from a cold test database**: pytest-timeout counted
  setup time, so the ~500-migration `create_test_db` build exhausted the 120s
  per-test budget and every test errored at `django_db_setup`. `timeout_func_only`
  now times only the test body, leaving slow fixtures (and cold DB builds) alone.
- **Login-throttle tests asserted a limit that was not in force**: they inherited
  the e2e environment's `AUTH_LOGIN_THROTTLE_RATE=10000/minute` (set by
  docker-compose and the ci-full.yml e2e job) while asserting the documented
  10/minute behaviour. The rate is now pinned in those tests, so they pass in
  both the default and e2e-tuned environments.

### Changed

- **Frontend port standardized**: dev server uses Vite default port 5173 (was 3000/CRA); all docker-compose, nginx, CORS, CI, and e2e configs updated.
- **CI expanded to 8 jobs**: `docker-build` now depends on `frontend-test` + `security-scan`; `deploy-production` gated on `docker-build`.
- `AcademicYear.save()` demotes the previous current year inside a
  `select_for_update` lock so concurrent saves can't leave multiple current years.
- Health readiness is Celery-soft: worker downtime no longer pulls the HTTP service
  out of rotation; DB and cache remain hard checks.
- Celery beat schedule consolidated in `core/celery.py` (added
  `cleanup-expired-verification-tokens`, `notify-low-backup-codes`); removed the
  duplicate from settings and the dead `cache_school_analytics` task.
- **Roadmap re-audited (2026-09-20)**: Phases 1–3 verified item by item against
  the code — CSV onboarding covers all five record types in backend and UI,
  parent fee/attendance notifications are scheduled, the grade-change approval
  queue and analytics charts are live. `docs/ROADMAP.md` now reflects that state.

## [2.0.0] - 2026-08

### Added

- 24 modular Django services (students, attendance, gradebook, fees, academics,
  timetable, communication, reporting, HR, library, hostel, inventory, sports,
  transportation, health clinic, cafeteria, behavior, conferences, admissions,
  alumni, infrastructure, auth) with per-service migrations (50 files).
- Multi-tenant school isolation with dedicated tenant-isolation test suite.
- Auth: JWT, 2FA (TOTP + backup codes), email verification, generated secure
  passwords, rate limiting, account lockout.
- Payments: Stripe, Khalti, eSewa gateway configuration with per-school toggles,
  invoice lifecycle (draft/unpaid/partial/paid/overdue/waived), bulk invoice
  generation, PDF receipts.
- Communication: multi-channel notifications (in-app via WebSocket, email, SMS via
  Twilio/Vonage, push via Expo/FCM), announcements, direct messages, notification
  templates.
- Reporting: dashboard stats, attendance reports, fee reports, student/attendance
  PDF & CSV exports, cached dashboard.
- Gradebook: exams, schedules, bulk grade entry, CSV import/export, assessments,
  submissions, report cards with PDF generation + publish flow.
- Celery workers: bulk invoices, receipt PDFs, report card generation, notification
  dispatch; structured JSON logging with PII-redacted `task_failure` handling.
- Observability: Sentry (backend + web + mobile), Prometheus/Grafana, structured
  worker logging.

### Changed

- Django 4.2 → 5.2; DRF, django-filter, channels, drf-spectacular and related
  dependencies bumped for compatibility.
- CSP hardened: nonce-based script policy replacing `'unsafe-inline'`.

### DevOps

- CI/CD: 7 jobs (backend-test with coverage gate, frontend-test, mobile-test,
  e2e-test, security-scan/gitleaks, docker-build, deploy-production).
- Docker Compose (dev + prod), k8s manifests (12-doc bundle), Terraform, Nginx
  configs, load tests (k6), monitoring dashboards.
- Codecov coverage publishing (70.11% total, 68% gate).
- CI status + coverage badges in README.

## [1.0.0] - 2026-07

### Added

- Initial scaffold: core settings (base/dev/production), DRF + GraphQL + Channels
  API layers, auth service (User/School models, JWT), students service.
- Seed commands: `seed_demo_data`, `seed_operational_data`,
  `seed_additional_schools`, `seed_e2e_data`.
- Playwright e2e suite (role-based dashboards, 2FA login, email verification,
  admin modules).
