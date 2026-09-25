# Demo Data Seeding & Tenant-Link Repair

How the demo database gets filled, how tenant consistency is kept, and how to
verify that every panel tab renders real rows.

> ⚠️ All of this applies to **demo/development data only**. The seeder writes
> clearly-labelled placeholder rows ("Seeded demo entry generated for UI
> verification") — never run it against a production database.

## The toolkit

| Script                                             | Purpose                                                                                                 |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `backend/scripts/seed_empty_models.py`             | Seeds every still-empty school-scoped model with plausible rows                                         |
| `backend/scripts/seed_parent_children.py`          | Tops every guardian-linked child up to ≥1 row per parent-portal category                                |
| `backend/scripts/seed_teacher_workspace.py`        | Gives up to 100 teachers/school an owned workspace (assignments, plans, attendance, payslips, messages) |
| `backend/scripts/repair_tenant_links.py`           | Deletes rows whose FK paths disagree about the tenant                                                   |
| `backend/scripts/diag_cross_tenant.py`             | Same check as the repair, **report-only** (no deletes)                                                  |
| `backend/scripts/check_hostel_tabs.py`             | Endpoint-level count check for one module (template for others)                                         |
| `backend/scripts/verify_all_logins.py`             | Logs in as every demo user to prove credentials still work                                              |
| `backend/scripts/reset_demo_passwords_fast.py`     | Re-applies the per-role demo passwords (see `DEMO_CREDENTIALS.md`)                                      |
| `frontend/web/scripts/walk_school_panel_tabs.mjs`  | Browser walk of every page + tab, flags EMPTY/error tabs                                                |
| `frontend/web/scripts/walk_teacher_per_school.mjs` | Browser walk of the 8 teacher pages for one school                                                      |
| `frontend/web/scripts/audit_role_portals.mjs`      | Walks the parent / student / teacher portals and reports failures                                       |

## Quick start (Docker stack running)

```bash
# Seed one school (name substring match)
docker exec sms_backend python scripts/seed_empty_models.py "Green Valley"

# Seed every school
docker exec sms_backend sh -c 'for s in "Green Valley" "EduSphere" \
  "Bright Future" "E2E Test" "Test School 0" "Test School 1"; do
  python scripts/seed_empty_models.py "$s"; done'

# Report cross-tenant rows (safe), then repair (deletes)
docker exec sms_backend python scripts/diag_cross_tenant.py
docker exec sms_backend python scripts/repair_tenant_links.py
```

The seeder is **rerunnable**: already-populated models are skipped, generated
values carry a unique run suffix, and each row retries a few times on unique
collisions. `--dry-run` lists what _would_ be seeded.

## Role-portal seeding

The generic seeder scatters rows across all students/teachers, so a _specific_
parent or teacher login usually lands on empty tabs. Two rerunnable passes fix
that per school:

```bash
# One row in each of the 12 parent-portal categories for every guardian-linked child
docker exec sms_backend python scripts/seed_parent_children.py "Green Valley School"

# Real teacher workspace: assignments, lesson plans, assessments, period attendance,
# Employee + payslips, direct messages, conference slots (up to MAX_TEACHERS = 100)
docker exec sms_backend python scripts/seed_teacher_workspace.py "Green Valley School"
```

Both take a school **name substring** and are safe to re-run (existing rows are
reused, not duplicated). Run them for every demo school:

```bash
docker exec sms_backend sh -c 'for s in "Green Valley" "EduSphere" "Bright Future" \
  "E2E Test" "Test School 0" "Test School 1"; do
  python scripts/seed_parent_children.py "$s";
  python scripts/seed_teacher_workspace.py "$s"; done'
```

The teacher pass attaches its rows to the school's **named** teachers
(`alice.morgan@…`, `sarah.mitchell@…`); the bulk filler accounts
(`demo.*@…-<runid>`) cannot log in — see `DEMO_CREDENTIALS.md`.

### Verifying a portal walk

```bash
cd frontend/web

# Form login — one school's teacher at a time (8 pages, PASS/FAIL per page)
MSYS_NO_PATHCONV=1 node scripts/walk_teacher_per_school.mjs alice.morgan@greenvalley.edu Teacher@1234

# Token injection — for accounts whose email the login form rejects
MSYS_NO_PATHCONV=1 node scripts/walk_teacher_per_school.mjs --token /tmp/jwt.txt
```

`walk_teacher_per_school.mjs` walks the 8 teacher pages, printing per-page HTTP
status, API row counts and a text sample. In `--token` mode it also fetches
`/auth/me/` and seeds `{tokens, user}` into the `sms-auth` localStorage key,
without which the route guards render blank pages. The dev server must be up on
`http://localhost:5173`.

## How the seeder decides what to seed

1. Enumerates every model under `services.*`.
2. A model is **empty** when _at least one FK path_ from the model to
   `auth_service.School` has zero rows for the target school. Multi-FK models
   (e.g. `WearableIntegration` is reachable via `student__school` **and**
   `team__school`) must have rows through _every_ path — viewsets scope
   through different paths, so a row count on the shortest path is not enough.
3. Models are seeded in FK-dependency order (parents first).
4. Row targets: **5** per model, **2** for policy/setting/config models, and
   **1** for OneToOne-per-school singleton configs.

### Value generation rules worth knowing

- **FK parents are strictly same-school.** If no same-school parent exists the
  seeder _creates_ one — it never falls back to another school's rows.
- **The school FK is always anchored**, even when nullable. School-less parent
  rows (e.g. a `User` with `school=NULL`) are invisible to tenant viewsets and
  used to be a major source of empty tabs.
- **Nullable FKs to tenant-scoped targets get filled**; only FKs to global
  (non-tenant) targets may stay NULL.
- **Visibility booleans are forced True** (`is_approved`, `is_active`,
  `is_published`, …) — viewsets filter these out when False, which left
  moderation-gated tabs permanently empty.
- Strings respect `max_length`, choices pick valid values, Decimals respect
  max_digits/decimal_places, and unique-constrained fields get a run-unique
  suffix (random IPs for `IPAddressField` where suffixing would break inet
  syntax).

## Tenant integrity invariants

Every `services.*` row must resolve to **one** school through _all_ of its FK
paths. `repair_tenant_links.py` resolves every FK path to `School` per model
and deletes rows whose paths disagree (deepest models first). The workflow is
convergent:

```
seed → repair (expect 0) → seed → repair (expect 0)
```

A non-zero repair count after a _fresh_ seed means the seeder introduced a
cross-tenant link — check FK fields with `default=` values pointing at
tenant-scoped targets (defaults bypass the strict pick).

> Historical note: an earlier version of the repair built lookups with
> `p[:-1]` (dropping the final hop onto School) and compared _parent PKs_
> instead of school ids, flagging every healthy multi-FK row. If a repair run
> ever reports suspiciously large deletions (~5 per model), suspect a
> path→lookup conversion bug and run `diag_cross_tenant.py` first.

## Verifying the result

### Endpoint check (fast)

Copy `backend/scripts/check_hostel_tabs.py` (run inside the container), swap
the endpoint list and URL prefix. It logs in as the demo super admin, sends
the `X-School-ID` header, and prints `count=` per endpoint — anything `200
count=0` with rows in the DB means the viewset scopes through a different FK
path than you checked.

### UI walk (thorough)

```bash
cd frontend/web
MSYS_NO_PATHCONV=1 WALK_PAGES="/admin/library,/admin/hostel-center" \
  node scripts/walk_school_panel_tabs.mjs
```

- `WALK_PAGES` filters pages (comma-separated). Without it, all 32 pages are
  walked (~800 tabs) — split into batches of 8–16 pages to stay under command
  timeouts; results flush to `scripts/tab_walk.json` after each page.
- `MSYS_NO_PATHCONV=1` is **required on Git Bash/Windows**: MSYS otherwise
  rewrites `/admin/...` in env vars into `C:/Program Files/Git/admin/...` and
  the filter silently matches nothing.
- Output flags per tab: `EMPTY (0 rows)`, API failures (≥400), and error
  banners. Console errors are listed at the end.

## When a tab legitimately shows empty

Some viewsets are **personal**, not school-scoped — they show only the logged-in
user's own rows, so an admin sees zero by design. Where the admin panel needs
the data, the viewset gets an admin fallback (all rows for the caller's school
when `role in ["school_admin", "super_admin"]`). Existing fallbacks:

- `timetable.TeacherTimetableViewSet`
- `timetable.TeacherPreferenceViewSet`
- `attendance.QRCodeSessionViewSet`
- `academics.AcademicNotificationViewSet`
- `library.BookRecommendationViewSet`

If a _new_ personal-scoped tab shows empty for admins, that's the pattern to
copy — not a seeding problem.

## Troubleshooting

| Symptom                                                           | Cause / fix                                                                                                                                                          |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `duplicate key value violates unique constraint` in seeder output | Benign retry on a singleton/unique row that already exists. Only a problem if the model ends with 0 rows.                                                            |
| Repair deletes rows on every run                                  | The seeder re-introduced cross-tenant links — usually a FK `default=` pointing at a tenant-scoped target. Fix the seeder, then seed → repair → seed.                 |
| Endpoint `200 count=0` but the DB has rows                        | Viewset scopes through a different FK path than the rows use. The multi-path `is_empty` handles detection; the viewset (or seeding of the other path) needs the fix. |
| Walk flags `EMPTY` but curl shows data                            | Logged-in role differs — see "personal viewsets" above.                                                                                                              |
| `WALK_PAGES` filter matches nothing on Git Bash                   | Missing `MSYS_NO_PATHCONV=1`.                                                                                                                                        |
