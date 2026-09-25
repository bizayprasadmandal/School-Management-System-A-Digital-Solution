# Product & Project Roadmap — EduSphere SMS

Prioritization uses a simplified RICE score. "User" in the RICE column means the
schools/staff who touch the feature daily. Items needing the product owner's
decision or external credentials are marked **[OWNER]**.

Legend: 🔴 P0 (blocking) · 🟠 P1 (this quarter) · 🟡 P2 (next quarter)

> **Audit 2026-09-20** — every actionable item in Phases 1–3 is now implemented
> and verified against the code (endpoints, Celery schedules, and UI surfaces
> checked individually). Only owner-gated work remains. New candidate items are
> needed before this board is useful again.
>
> **Update 2026-09-25** — developer-experience and demo-fidelity work landed:
> generated API documentation (item 12), role-portal fixes for the parent,
> student and teacher surfaces, and per-school demo seeders. The docs set was
> re-audited against the code the same day (counts, endpoints, env vars, and
> credentials). Phase 4 candidates are listed at the bottom.

---

## Phase 1 — Make it deployable & legal (days 1–30)

| #   | Item                                                                                                                                                                                                    | RICE (R·I·C / E) | Owner         |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ------------- |
| 1   | **Resolve license** — README says _Proprietary_ on a public repo. Pick MIT/AGPL or go private. **[OWNER]**                                                                                              | 5·5·5/1 = 125    | Product owner |
| 2   | **Real deployment** — stand up the cluster (or a managed Postgres + container host for pilot scale), add `KUBE_CONFIG_PRODUCTION` + remaining `sms-secrets` values, un-skip the deploy job. **[OWNER]** | 5·5·5/2 = 62     | Dev + owner   |
| 3   | **Fix stale deploy docs** — `DEPLOYMENT.md` still claims only `auth_service` ships a hand-written migration; all 23 services ship migrations now. ✅ _done 2026-08_                                     | —                | —             |

## Phase 2 — Win one pilot school (days 31–60)

| #   | Item                                                                                                                                                                                                                                                                                                                      | RICE         | Notes                                                                                |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------ |
| 4   | **Data onboarding wizard** — CSV import shipped for **all five** record types, backend **and** UI: students (`/students/import-csv/`), classrooms (`/students/classrooms/import-csv/`), teachers (`/academics/teacher-profiles/import-csv/`), attendance (`/attendance/import-csv/`), fees (`/fees/invoices/import-csv/`) | 4·4·5/3 = 27 | ✅ Done — import UI is on Students / Classrooms / Teachers / Attendance / Fees pages |
| 5   | **Admissions CRM funnel** — enrollment funnel analytics ✅; follow-up pipeline ✅ (state machine, offer deadlines, guardian accounts); public application portal ✅                                                                                                                                                       | 4·4·4/4 = 16 | ✅ Done 2026-08                                                                      |
| 6   | **Pilot school onboarding** — recruit 1 school, load their real data, run 2 weeks live **[OWNER]**                                                                                                                                                                                                                        | 5·5·5/2 = 62 | Unblocks every other priority                                                        |

## Phase 3 — Deepen, don't widen (days 61–90)

| #   | Item                                                                                                                             | RICE         | Notes                                                                                                                                                                                                          |
| --- | -------------------------------------------------------------------------------------------------------------------------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 7   | **Parent notifications for attendance/fees** — fee-due reminders + absent-day alerts as standard event templates for all schools | 5·4·5/3 = 33 | ✅ Done — `send_fee_reminders` runs daily 08:00 (`core/celery.py`), `notify_absent_guardians` (+ WhatsApp variant) on the attendance path, `attendance_absent` / `fee_due` templates seed via `seed_demo_data` |
| 8   | **Grade-change approval workflow** — proposed → approved state so admin review gates published grades                            | 3·4·3/4 = 9  | ✅ Done — `gradebook.GradeChangeProposal` (`Status.PROPOSED`, `proposed_by`/`proposed_at`) with an admin review queue and approve/reject actions                                                               |
| 9   | **Analytics dashboards UI** — at-risk / funnel / forecast exposed in the admin UI with charts                                    | 4·4·3/4 = 12 | ✅ Done — at-risk students (Attendance), admission funnel (Admissions Center), fee forecast + trend (Dashboard, Recharts)                                                                                      |
| 10  | **i18n (Nepali)** — string extraction + Nepali locale for the web app                                                            | 4·4·3/5 = 10 | ✅ Done 2026-08 (EN/NE + language switcher)                                                                                                                                                                    |
| 11  | **Split Sentry projects** — separate backend / web / mobile DSNs with per-app alert rules **[OWNER]**                            | 3·3·3/1 = 27 | Credentials from Sentry                                                                                                                                                                                        |
| 12  | **Generated API documentation** — OpenAPI 3 served from the code, Swagger UI + ReDoc, module tags, Authorize button              | 3·4·4/1 = 48 | ✅ Done 2026-09-25 — `/api/schema/`, `/api/docs/`, `/api/redoc/`, regression test in `backend/tests/test_api_schema.py`                                                                                        |
| 13  | **Role-portal completeness** — parent/student/teacher pages must point at real, self-scoped endpoints                            | 4·5·4/2 = 40 | ✅ Done 2026-09 — 12 guardian-scoped `/children/` endpoints, student self-scoping, teacher workspace seeder + per-school browser walk                                                                          |

## Phase 4 — candidates (not yet scored)

| Candidate                                                                          | Why it is on the list                                                                 |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Fix bulk-seeded `demo.*@…-<runid>` accounts (malformed address, unusable password) | 105 filler teacher accounts cannot log in; demos should not depend on token injection |
| Fully describe the 34 plain `APIView`s (`@extend_schema`)                          | Removes the remaining `spectacular --validate` warnings and makes login/2FA SDK-ready |
| Pilot-school onboarding support                                                    | Phase 2 item 6 is still owner-gated; tooling around it can start early                |
| Mobile parity for the surfaces shipped this quarter                                | The Expo app predates the portal and analytics work                                   |
| Operational hardening from the first school's usage                                | Whatever the first pilot actually breaks                                              |

## Parked / Could-have

| Item                            | Why parked                                          |
| ------------------------------- | --------------------------------------------------- |
| QR/RFID attendance kiosk        | Needs hardware pilots; revisit after pilot #1       |
| Transport GPS tracking          | Not core to pilot school's daily ops                |
| WhatsApp notification channel   | Channel abstraction exists; add when a school asks  |
| Cafeteria POS / inventory depth | Unproven demand; keep minimal until a pilot uses it |

## Remove / trim — audited 2026-09-20

| Item                                           | Verdict                                                                                                                          |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Modules with no UI pages or test coverage      | Audited — every service now has either an admin surface or a dedicated role surface                                              |
| Staged-but-unlinked accountant/librarian pages | None found — `ACCOUNTANT_NAV` / `LIBRARIAN_NAV` ship in `StudentLayout.tsx` with their own layouts and `RequireAuth` role guards |
| Duplicate frontend mock fallbacks              | None found — the only remaining "fallback" reference is a sort comment in `GradesPage.tsx`                                       |

---

## How to run this roadmap

1. **Weekly cadence:** re-score the RICE columns; the board is intentionally small
   enough to hold in one screen.
2. **Definition of done:** each item ships with backend tests + e2e where a UI
   path exists; coverage gate must not drop.
3. **Status:** the Phase 1–3 tables are complete as of the 2026-09-20 audit — the
   remaining work is deployment, licensing, and the Sentry split (all owner-gated),
   plus whatever reaches the next phase. Candidate themes for that phase: real
   pilot data onboarding support, mobile parity for the surfaces shipped this
   quarter, and operational hardening from the first school's usage.
