# Changelog

All notable changes to EduSphere SMS are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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
- Product & project artifacts: `CHANGELOG.md`, `docs/PRD.md`, `docs/ROADMAP.md`.

### Fixed

- Teacher grade listing now resolves via the real `TeacherAssignment` relation
  (`subject__assignments__teacher` / invigilator) instead of the non-existent
  `exam_schedule__assignment` lookup — the old query raised on every teacher grade
  request.
- Attendance streak test was timezone-dependent (`date.today()` vs
  `timezone.now().date()`); now deterministic on any machine timezone.

## [2.0.0] - 2026-08

### Added

- 24 modular Django services (students, attendance, gradebook, fees, academics,
  timetable, communication, reporting, HR, library, hostel, inventory, sports,
  transportation, health clinic, cafeteria, behavior, conferences, admissions,
  alumni, infrastructure, auth) with per-service migrations (68 files).
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
