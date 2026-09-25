# Demo Login Credentials

All seeded users follow a **per-role password scheme**. Any email from the
roster patterns below (including the numbered `student0001@…`-style accounts)
logs in with that role's password.

> ⚠️ Demo data only — never reuse these passwords anywhere real.

**Last verified:** 2026-09-25 against the six seeded schools (Green Valley,
EduSphere Demo Academy, Bright Future, E2E Test School, Test School 0, Test
School 1). The canonical accounts in the tables below were checked with
`check_password()` and a live `POST /api/v1/auth/login/`.

## Canonical passwords by role

| Role                               | Password       | Notes                   |
| ---------------------------------- | -------------- | ----------------------- |
| school_admin / super_admin         | `Admin@1234`   | Full admin UI access    |
| teacher                            | `Teacher@1234` |                         |
| student                            | `Student@1234` |                         |
| parent                             | `Parent@1234`  |                         |
| counselor / librarian / accountant | `Admin@1234`   | Staff roles             |
| alumni                             | `Alumni@1234`  | GVS alumni portal users |

## Green Valley School (your main demo data — richest module coverage)

| Role      | Email                                                         | Password       |
| --------- | ------------------------------------------------------------- | -------------- |
| Admin     | `admin@greenvalley.edu`                                       | `Admin@1234`   |
| Teacher   | `alice.morgan@greenvalley.edu` (+5 more named teachers)       | `Teacher@1234` |
| Student   | `student0001@greenvalley.edu` … `student0060@greenvalley.edu` | `Student@1234` |
| Parent    | `parent0001@greenvalley.edu` … `parent0060@greenvalley.edu`   | `Parent@1234`  |
| Librarian | `librarian@greenvalley.edu`                                   | `Admin@1234`   |
| Alumni    | `alumni1.fowler@alumni.gvs.edu` (+51 more)                    | `Alumni@1234`  |

## EduSphere Demo Academy

| Role       | Email                                                                            | Password       |
| ---------- | -------------------------------------------------------------------------------- | -------------- |
| Admin      | `admin@demo.edusphere.school`                                                    | `Admin@1234`   |
| Teacher    | `sarah.mitchell@demo.edusphere.school`, `james.thompson@…`, `emily.chen@…` (+13) | `Teacher@1234` |
| Student    | `student001@demo.edusphere.school` … `student204@…`                              | `Student@1234` |
| Parent     | `parent001@demo.edusphere.school` … `parent200@…`                                | `Parent@1234`  |
| Counselor  | `counselor@demo.edusphere.school`                                                | `Admin@1234`   |
| Librarian  | `librarian@demo.edusphere.school`                                                | `Admin@1234`   |
| Accountant | `accountant@demo.edusphere.school`                                               | `Admin@1234`   |

## Bright Future Academy

| Role                   | Email                                                        | Password       |
| ---------------------- | ------------------------------------------------------------ | -------------- |
| Admin                  | `admin@brightfuture.edu`                                     | `Admin@1234`   |
| Teacher                | `alice.morgan@brightfuture.edu` (+5 named)                   | `Teacher@1234` |
| Student                | `student0001@brightfuture.edu` … `0060@…`                    | `Student@1234` |
| Parent                 | `parent0001@brightfuture.edu` … `0060@…`                     | `Parent@1234`  |
| Accountant / Librarian | `accountant@brightfuture.edu` / `librarian@brightfuture.edu` | `Admin@1234`   |

## E2E Test School (used by CI — do not repurpose)

| Role                       | Email                                                             | Password                                        |
| -------------------------- | ----------------------------------------------------------------- | ----------------------------------------------- |
| Admin                      | `admin@school.edu`                                                | `Admin@1234`                                    |
| Teacher / Student / Parent | `teacher@school.edu` / `student@school.edu` / `parent@school.edu` | `Teacher@1234` / `Student@1234` / `Parent@1234` |
| Counselor / Accountant     | `counselor@school.edu` / `accountant@school.edu`                  | `TestPass@1234`                                 |

## Personal / special accounts (do not reset)

| Email                                              | Password            | Note                                   |
| -------------------------------------------------- | ------------------- | -------------------------------------- |
| `bizaymndl@gmail.com`                              | (yours — unchanged) | super_admin, no school                 |
| `shree.tiwari@gmail.com`, `mamta.mandal@gmail.com` | (yours — unchanged) | personal student-role accounts         |
| `smoke@demo.edusphere.school`                      | `Admin@1234`        | super_admin @ GVS, used by smoke tests |

## Accounts that do _not_ log in

The generic seeders also create bulk filler users whose addresses are built by
appending a run suffix to the whole address, e.g.
`demo.497725@greenvalley.edu-497725230` or `demo.0a5a2d@greenvalley.edu-0a5a2d278`.
Those accounts are **not login-able** and should not be used in demos or walks:

- the address is malformed, so the browser login form's `.email()` validation
  refuses to submit it;
- the account's password is not one of the per-role passwords, so
  `POST /api/v1/auth/login/` answers `401 No active account found with the
given credentials`.

Current counts of such teacher accounts: Green Valley 30, Bright Future 20,
E2E 15, EduSphere 10, Test School 0 20, Test School 1 10. Use the named
accounts above, or run the workspace seeders (`scripts/seed_teacher_workspace.py`)
which attach data to the _named_ teachers. Making the filler emails valid is an
open follow-up.

Pages/scripts that need a session for such an account must inject a token:
`frontend/web/scripts/walk_teacher_per_school.mjs --token <file>` fetches
`/auth/me/` and seeds both `tokens` and `user` into the `sms-auth` localStorage
key, otherwise the route guards render blank pages.

## How the reset works

`backend/scripts/reset_demo_passwords_fast.py` hashes each role's password
once and bulk-updates via SQL. Exclusions are baked in: **E2E Test School** and
**Test School 0** in their entirety, plus personal gmail accounts and API test
artifacts (`api.test`, `formdata.test`, `verifytest`). Accounts in the excluded
schools keep whatever password their seeder/`verify_all_logins.py` gave them,
which is why Test School 0 teachers are not `Teacher@1234`. The per-role scheme
above is then verified end-to-end by `backend/scripts/verify_all_logins.py`.

```bash
# Re-apply the per-role passwords, then verify every account
docker exec sms_backend python scripts/reset_demo_passwords_fast.py
docker exec sms_backend python scripts/verify_all_logins.py
```
