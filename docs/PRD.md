# Product Requirements Document — EduSphere SMS

> **Status:** Draft v0.1 — decision points are marked **[DECISION]** and are owned
> by the product owner. Sections are intentionally short: a PRD that needs a
> manual to read is a manual, not a PRD.

## 1. Problem

Private schools in South Asia (primary target: Nepal) run their operations on a
mix of registers, Excel sheets, and WhatsApp groups. Fee collection is manual,
attendance is paper, and parents learn about absences and results days late.
Off-the-shelf Western SIS platforms are expensive, don't support local payment
gateways (Khalti/eSewa), and are built around workflows that don't match local
school administration.

## 2. Vision

One multi-tenant platform that runs the daily operations of a school — students,
attendance, fees, grades, communication — from the principal's dashboard to the
parent's phone, in the local context, with payments that actually work locally.

## 3. Target segment **[DECISION]**

- **Primary:** private schools in Nepal, 100–1,500 students, single or small
  chains (2–10 schools) needing multi-school management.
- **Secondary:** regional schools in neighboring markets with similar payment
  ecosystems.
- **Explicitly out of scope for v1:** government district-level reporting engines,
  IB/curriculum-specific tooling.

## 4. Personas

| Persona                    | Core job                              | Pain today                    | Our answer                                          |
| -------------------------- | ------------------------------------- | ----------------------------- | --------------------------------------------------- |
| **School admin/principal** | Know school health; collect fees      | Spreadsheets, no visibility   | Dashboard stats, fee forecast, at-risk list         |
| **Teacher**                | Record attendance & grades quickly    | Paper registers, double entry | Bulk attendance, bulk grade entry, CSV import       |
| **Parent**                 | Know child is safe, learning, paid-up | No signal until report card   | Multi-channel notifications (in-app/email/SMS/push) |
| **Accountant**             | Track invoicing & collections         | Manual ledger                 | Invoices, payments, receipts PDF, forecast          |
| **Super admin (chain)**    | Manage multiple schools               | Fragmented systems            | Multi-tenant school switching                       |

## 5. Anchors (the 3 things we win on)

1. **Localized payments end-to-end** — Stripe + Khalti + eSewa with per-school
   toggles, invoice lifecycle, and PDF receipts. Western competitors cannot do
   this; local competitors don't do it this well.
2. **Multi-tenant isolation done properly** — one platform, strict per-school data
   isolation (proven by an isolation test suite), super-admin school switching.
3. **Operational speed** — bulk attendance, bulk grades, CSV imports, and
   background workers so a 1,000-student school's daily ops finish in minutes.

## 6. Feature scope (MoSCoW for v2.0)

**Must have (shipped):** students, attendance, grades/exams/report cards, fees &
payments, communication/notifications, HR/teachers, timetable, dashboard/reporting,
multi-tenancy, RBAC, 2FA, mobile app (read + basic write).

**Should have (next):** admissions CRM funnel, grade-change approval workflow,
at-risk analytics (shipped in unreleased), attendance/fee CSV import (shipped in
unreleased), data migration/import wizards for onboarding, i18n (Nepali).

**Could have:** QR/RFID attendance kiosk, transport GPS tracking, cafeteria POS,
WhatsApp channel, biometric verification.

**Won't have (v1):** government compliance engines, full LMS (quiz/lesson content),
financial accounting (ledger/AP/AR) beyond fee management.

## 7. KPIs & north-star metric **[DECISION]**

- **North star:** _weekly active schools_ — schools that record at least one
  attendance batch and one payment each week.
- Guardrails: daily attendance coverage % (records vs enrolled), fee collection
  rate, notification delivery success rate, p95 API latency.

## 8. Pricing **[DECISION — proposal]**

- Free tier: 1 school, up to 100 students.
- Standard: per-school/month, per-student tiering (or flat per school) —
  recommended entry price well under local competitor price points to win the
  first pilot schools, with onboarding (data import) included.
- Chain tier: multi-school discount + super-admin features.

## 9. Risks & mitigations

| Risk                                      | Mitigation                                                         |
| ----------------------------------------- | ------------------------------------------------------------------ |
| Schools won't onboard without data import | Import wizards are Should-have, scheduled before first pilot       |
| Western-style workflows don't fit         | Validate via pilot school before deepening modules                 |
| Payment gateway settlement/legal          | Per-school gateway config; keep cash/bank methods always available |
| Single-owner bus factor                   | Public repo + contribution docs + CI as safety net                 |

## 10. Out of scope for this document

Technical architecture (see `docs/ARCHITECTURE.md`), deployment (see
`docs/DEPLOYMENT.md`), API contracts (see `docs/API.md`).
