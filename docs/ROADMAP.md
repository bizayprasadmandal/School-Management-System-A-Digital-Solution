# Product & Project Roadmap — EduSphere SMS

Prioritization uses a simplified RICE score. "User" in the RICE column means the
schools/staff who touch the feature daily. Items needing the product owner's
decision or external credentials are marked **[OWNER]**.

Legend: 🔴 P0 (blocking) · 🟠 P1 (this quarter) · 🟡 P2 (next quarter)

---

## Phase 1 — Make it deployable & legal (days 1–30)

| #   | Item                                                                                                                                                                                                    | RICE (R·I·C / E) | Owner         |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ------------- |
| 1   | **Resolve license** — README says _Proprietary_ on a public repo. Pick MIT/AGPL or go private. **[OWNER]**                                                                                              | 5·5·5/1 = 125    | Product owner |
| 2   | **Real deployment** — stand up the cluster (or a managed Postgres + container host for pilot scale), add `KUBE_CONFIG_PRODUCTION` + remaining `sms-secrets` values, un-skip the deploy job. **[OWNER]** | 5·5·5/2 = 62     | Dev + owner   |
| 3   | **Fix stale deploy docs** — `DEPLOYMENT.md` still claims only `auth_service` ships a hand-written migration; all 22 services ship migrations now. ✅ _done 2026-08 (see below)_                         | —                | —             |

## Phase 2 — Win one pilot school (days 31–60)

| #   | Item                                                                                                                                      | RICE         | Notes                               |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ----------------------------------- |
| 4   | **Data onboarding wizard** — attendance + fee CSV import shipped ✅; extend to classroom/teacher records and build the frontend wizard UI | 4·4·5/3 = 27 | Import endpoints live; UI next      |
| 5   | **Admissions CRM funnel** — enrollment funnel analytics ✅; add follow-up pipeline (inquiry → tour → offer) and per-application actions   | 4·4·4/4 = 16 | Backend funnel live; CRM depth next |
| 6   | **Pilot school onboarding** — recruit 1 school, load their real data, run 2 weeks live **[OWNER]**                                        | 5·5·5/2 = 62 | Unblocks every other priority       |

## Phase 3 — Deepen, don't widen (days 61–90)

| #   | Item                                                                                                                                                                              | RICE         | Notes                                         |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | --------------------------------------------- |
| 7   | **Parent notifications for attendance/fees** — templates already seed in `seed_demo_data`; wire fee-due reminders + absent-day alerts as standard event templates for all schools | 5·4·5/3 = 33 | NotificationService + templates already exist |
| 8   | **Grade-change approval workflow** — audit trail ✅; add "proposed → approved" state so admin review gates published grades                                                       | 3·4·3/4 = 9  | Builds directly on GradeChangeLog             |
| 9   | **Analytics dashboards UI** — expose at-risk/funnel/forecast ✅ in the admin UI with charts                                                                                       | 4·4·3/4 = 12 | Backend live; frontend next                   |
| 10  | **i18n (Nepali)** — string extraction + Nepali locale for the web app                                                                                                             | 4·4·3/5 = 10 | High value for the target market              |
| 11  | **Split Sentry projects** — separate backend / web / mobile DSNs with per-app alert rules **[OWNER]**                                                                             | 3·3·3/1 = 27 | Credentials from Sentry                       |

## Parked / Could-have

| Item                            | Why parked                                          |
| ------------------------------- | --------------------------------------------------- |
| QR/RFID attendance kiosk        | Needs hardware pilots; revisit after pilot #1       |
| Transport GPS tracking          | Not core to pilot school's daily ops                |
| WhatsApp notification channel   | Channel abstraction exists; add when a school asks  |
| Cafeteria POS / inventory depth | Unproven demand; keep minimal until a pilot uses it |

## Remove / trim

| Item                                           | Action                                                                                     |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Modules with no UI pages or test coverage      | Audit each of 24 services; park unused ones (cafeteria/inventory depth) rather than extend |
| Staged-but-unlinked accountant/librarian pages | Finish or remove before demo                                                               |
| Duplicate frontend mock fallbacks              | Replace with real `seed_operational_data` output                                           |

---

## How to run this roadmap

1. **Weekly cadence:** re-score the RICE columns; the board is intentionally small
   enough to hold in one screen.
2. **Definition of done:** each item ships with backend tests + e2e where a UI
   path exists; coverage gate must not drop.
3. **Progress today:** audit-trail, analytics, and import gaps from the Phase 1–3
   tables are **already implemented** in the unreleased change set (see
   `CHANGELOG.md`); the remaining work is UI, approvals, i18n, and deployment.
