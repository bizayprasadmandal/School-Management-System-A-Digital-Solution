# EduSphere SMS — API Reference

## Base URL

| Environment | URL                                           |
| ----------- | --------------------------------------------- |
| Production  | `https://api.edusphere.school/api/v1`         |
| Staging     | `https://staging-api.edusphere.school/api/v1` |
| Local       | `http://localhost:8000/api/v1`                |

There is no `/api/v2/` — the root URL configuration declares only `api/v1/`.
The version in the generated schema (`2.0.0`) is the product version, not a URL
segment.

### Module index

Every service module is mounted under its own prefix and carries a matching
tag in the generated schema. Prefixes that differ from the module name are
called out because they are easy to guess wrong:

| Prefix                    | Module (`backend/services/…`) | Tag              | Auth       |
| ------------------------- | ----------------------------- | ---------------- | ---------- |
| `/api/v1/auth/`           | `auth`                        | `auth`           | Partial    |
| `/api/v1/students/`       | `students`                    | `students`       | Yes        |
| `/api/v1/academics/`      | `academics`                   | `academics`      | Yes        |
| `/api/v1/attendance/`     | `attendance`                  | `attendance`     | Yes        |
| `/api/v1/gradebook/`      | `gradebook`                   | `gradebook`      | Yes        |
| `/api/v1/timetable/`      | `timetable`                   | `timetable`      | Yes        |
| `/api/v1/communication/`  | `communication`               | `communication`  | Yes        |
| `/api/v1/reporting/`      | `reporting`                   | `reporting`      | Yes        |
| `/api/v1/fees/`           | `fees`                        | `fees`           | Yes        |
| `/api/v1/admissions/`     | `admissions`                  | `admissions`     | Yes        |
| `/api/v1/hr/`             | `hr`                          | `hr`             | Yes        |
| `/api/v1/library/`        | `library`                     | `library`        | Yes        |
| `/api/v1/hostel/`         | `hostel`                      | `hostel`         | Yes        |
| `/api/v1/transport/`      | `transportation`              | `transport`      | Yes        |
| `/api/v1/cafeteria/`      | `cafeteria`                   | `cafeteria`      | Yes        |
| `/api/v1/inventory/`      | `inventory`                   | `inventory`      | Yes        |
| `/api/v1/sports/`         | `sports`                      | `sports`         | Yes        |
| `/api/v1/health/`         | `health_clinic`               | `health`         | Yes        |
| `/api/v1/behavior/`       | `behavior`                    | `behavior`       | Yes        |
| `/api/v1/counseling/`     | `counseling`                  | `counseling`     | Yes        |
| `/api/v1/conferences/`    | `conferences`                 | `conferences`    | Yes        |
| `/api/v1/alumni/`         | `alumni`                      | `alumni`         | Yes        |
| `/api/v1/infrastructure/` | `infrastructure`              | `infrastructure` | Yes        |
| `/api/v1/search/`         | `core/search`                 | `search`         | Yes        |
| `/health/live/`           | `core/health`                 | —                | **No**     |
| `/health/ready/`          | `core/health`                 | —                | **No**     |
| `/health/startup/`        | `core/health`                 | —                | **No**     |
| `/metrics`                | `django-prometheus`           | —                | Deployment |
| `/admin/`                 | Django admin                  | —                | Staff      |

## Authentication

All endpoints (except `/auth/login/` and `/auth/password-reset/`) require a Bearer JWT token:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Login

```http
POST /auth/login/
Content-Type: application/json

{
  "email": "admin@school.edu",
  "password": "Admin@1234"
}
```

**Response 200:**

```json
{
  "access": "<jwt_access_token>",
  "refresh": "<jwt_refresh_token>",
  "user": {
    "id": "uuid",
    "email": "admin@school.edu",
    "full_name": "Alex Administrator",
    "role": "school_admin",
    "school": { "id": "uuid", "name": "Demo Academy", "code": "DEMO" }
  }
}
```

### Refresh Token

```http
POST /auth/token/refresh/
Content-Type: application/json

{ "refresh": "<jwt_refresh_token>" }
```

---

## Pagination

All list endpoints return paginated responses:

```json
{
  "count": 245,
  "next": "https://api.edusphere.school/api/v1/students/?page=2",
  "previous": null,
  "total_pages": 10,
  "current_page": 1,
  "results": [...]
}
```

**Query parameters:** `?page=2&page_size=50`  
**Max page size:** 200

---

## Students

### List Students

```http
GET /students/
Authorization: Bearer <token>
```

**Query parameters:**

| Param       | Type    | Description                        |
| ----------- | ------- | ---------------------------------- |
| `search`    | string  | Search by name or admission number |
| `gender`    | M\|F\|O | Filter by gender                   |
| `is_active` | boolean | Filter active/inactive             |
| `grade`     | integer | Filter by grade level              |
| `classroom` | integer | Filter by classroom                |
| `page`      | integer | Page number                        |
| `page_size` | integer | Results per page (max 200)         |

### Get Student

```http
GET /students/{id}/
```

### Create Student

```http
POST /students/
Content-Type: application/json

{
  "first_name": "Emma",
  "last_name": "Wilson",
  "email": "emma.wilson@school.edu",
  "password": "InitialPass@1234",
  "admission_number": "ADM-2024-0201",
  "date_of_birth": "2012-03-15",
  "gender": "F",
  "address": "789 Oak Street",
  "city": "Springfield",
  "state": "IL",
  "country": "USA",
  "admission_date": "2024-09-01",
  "classroom_id": 12
}
```

### Student Attendance Summary

```http
GET /students/{id}/attendance-summary/?academic_year=1
```

**Response:**

```json
{
  "total_days": 120,
  "present": 112,
  "absent": 5,
  "late": 3,
  "excused": 0,
  "attendance_percentage": 95.83
}
```

### Promote Students

```http
POST /students/promote/
Content-Type: application/json

{
  "student_ids": ["uuid1", "uuid2"],
  "target_classroom_id": 15,
  "academic_year_id": 2
}
```

---

## Attendance

### Bulk Record Attendance

```http
POST /attendance/bulk-record/
Content-Type: application/json

{
  "classroom_id": 5,
  "date": "2024-11-15",
  "records": [
    { "student_id": "uuid1", "status": "P", "remarks": "" },
    { "student_id": "uuid2", "status": "A", "remarks": "Called in sick" },
    { "student_id": "uuid3", "status": "L", "remarks": "Arrived 10 min late" }
  ]
}
```

**Status codes:** `P` = Present, `A` = Absent, `L` = Late, `E` = Excused, `H` = Half Day

### Classroom Summary

```http
GET /attendance/classroom-summary/?classroom_id=5&date=2024-11-15
```

**Response:**

```json
{
  "date": "2024-11-15",
  "total_students": 35,
  "recorded": 35,
  "not_recorded": 0,
  "breakdown": {
    "present": 31,
    "absent": 2,
    "late": 2,
    "excused": 0
  }
}
```

### Leave Requests

```http
POST /attendance/leaves/
Content-Type: application/json

{
  "student": "uuid",
  "leave_type": "sick",
  "from_date": "2024-11-20",
  "to_date": "2024-11-22",
  "reason": "Medical procedure"
}
```

```http
POST /attendance/leaves/{id}/approve/
{ "remarks": "Approved — medical certificate received" }
```

---

## Gradebook

### Submit Bulk Grades

```http
POST /gradebook/grades/bulk/
Content-Type: application/json

{
  "exam_schedule_id": 42,
  "grades": [
    { "student_id": "uuid1", "marks_obtained": 87.5, "is_absent": false, "remarks": "" },
    { "student_id": "uuid2", "marks_obtained": null, "is_absent": true, "remarks": "Absent" }
  ]
}
```

### Generate Report Cards

```http
POST /gradebook/exams/{id}/generate-report-cards/
```

**Response 202 (async):**

```json
{
  "detail": "Report card generation queued.",
  "task_id": "celery-task-uuid"
}
```

### Exam Leaderboard

```http
GET /gradebook/exams/{id}/leaderboard/?limit=10
```

---

## Communication

### Create Announcement

```http
POST /communication/announcements/
Content-Type: application/json

{
  "title": "Final Exam Schedule",
  "content": "The final examination schedule for Term 2 is now available...",
  "priority": "high",
  "audience": "all",
  "send_email": true,
  "send_push": true,
  "is_draft": false
}
```

**Priority values:** `low`, `normal`, `high`, `urgent`  
**Audience values:** `all`, `teachers`, `students`, `parents`, `staff`

### Unread Notification Count

```http
GET /communication/notifications/unread-count/
```

**Response:** `{ "count": 7 }`

### Mark All Notifications Read

```http
POST /communication/notifications/mark-all-read/
```

**Response:** `{ "marked_read": 7 }`

---

## Fees

### Generate Bulk Invoices

```http
POST /fees/invoices/bulk-generate/
Content-Type: application/json

{
  "fee_structure_id": 3,
  "academic_year_id": 1
}
```

### Record Payment

```http
POST /fees/payments/
Content-Type: application/json

{
  "invoice": "invoice-uuid",
  "amount": "500.00",
  "payment_method": "cash"
}
```

**Payment methods:** `cash`, `bank_transfer`, `card`, `cheque`, `online`, `mobile`

---

## Reporting

### Dashboard Statistics

```http
GET /reporting/dashboard-stats/
```

### Export Students CSV

```http
GET /reporting/export/students-csv/
```

Returns a `text/csv` file download.

### Export Attendance PDF

```http
GET /reporting/export/attendance-pdf/?classroom_id=5&from_date=2024-11-01&to_date=2024-11-30
```

Returns a `application/pdf` file download.

---

## Public Application Portal

No authentication required. Endpoints for prospective students to apply and track status.

### Submit Application

```http
POST /admissions/public/apply/
Content-Type: application/json

{
  "first_name": "Ram",
  "last_name": "Sharma",
  "email": "ram.sharma@email.com",
  "phone": "+977-9841234567",
  "date_of_birth": "2012-05-15",
  "gender": "M",
  "grade_applied_for": "Grade 8",
  "previous_school": "Buddha Academy",
  "address": "Kathmandu, Nepal",
  "guardian_name": "Hari Sharma",
  "guardian_phone": "+977-9841234568",
  "guardian_email": "hari.sharma@email.com",
  "relationship": "father",
  "notes": ""
}
```

**Response 201:**

```json
{
  "application_number": "APP-202609-4F2A9C",
  "status": "submitted",
  "submitted_at": "2026-09-25T10:30:00Z",
  "intake_name": "Fall 2026 Intake",
  "message": "Application APP-202609-4F2A9C submitted successfully. Please save your application number to check the status later."
}
```

Application numbers are `APP-<YYYYMM>-<6 uppercase hex>` and unique in the whole
system. The public form submits straight to `submitted` — the status machine is
in `docs/LLD.md` §2.1.

### Check Application Status

```http
GET /admissions/public/status/APP-202609-4F2A9C/
```

No auth, but the application number is the only credential — it is a bearer
capability, so treat it as secret.

**Response 200:**

```json
{
  "application_number": "APP-202609-4F2A9C",
  "status": "under_review",
  "status_display": "Under Review",
  "first_name": "Ram",
  "last_name": "Sharma",
  "intake_name": "Fall 2026 Intake",
  "applying_for_grade": "Grade 8",
  "submitted_at": "2026-09-25T10:30:00Z",
  "offer_deadline": null,
  "timeline": []
}
```

### List Open Intakes

```http
GET /admissions/public/intakes/
```

**Response 200** (unpaginated list of open intakes):

```json
[
  {
    "id": "03daad60-4347-45af-9181-275bf802a1be",
    "name": "Fall 2026 Intake",
    "academic_year": "2026-2027",
    "application_start": "2026-05-16",
    "application_end": "2026-10-13",
    "enrollment_date": null,
    "status": "open",
    "status_display": "Open",
    "description": "Admissions open for Grade 1-10"
  }
]
```

---

## WebSocket Events

**Endpoint:** `wss://api.edusphere.school/ws/`

### Notifications Channel

`wss://api.edusphere.school/ws/notifications/?token=<jwt>`

**Server → Client events:**

| Type           | Payload                                                   |
| -------------- | --------------------------------------------------------- |
| `notification` | `{ type, notification: { id, title, body, created_at } }` |
| `unread_count` | `{ type, count: 7 }`                                      |

**Client → Server:**

| Type        | Payload                             |
| ----------- | ----------------------------------- |
| `mark_read` | `{ type, notification_id: "uuid" }` |

### Chat Channel

`wss://api.edusphere.school/ws/chat/{recipient_id}/?token=<jwt>`

| Direction | Type               | Payload                                                  |
| --------- | ------------------ | -------------------------------------------------------- |
| C→S       | `message`          | `{ type, content }`                                      |
| C→S       | `typing`           | `{ type, is_typing: true }`                              |
| C→S       | `read_receipt`     | `{ type, message_ids: ["uuid"] }`                        |
| S→C       | `chat_message`     | `{ type, message: { id, content, sender_id, sent_at } }` |
| S→C       | `typing_indicator` | `{ type, user_id, is_typing }`                           |
| S→C       | `read_receipt`     | `{ type, reader_id, message_ids, read_at }`              |

---

## Error Responses

```json
{
  "detail": "Not found.",
  "status_code": 404
}
```

```json
{
  "email": ["A user with this email already exists."],
  "status_code": 400
}
```

**HTTP status codes used:**

| Code | Meaning                              |
| ---- | ------------------------------------ |
| 200  | Success                              |
| 201  | Created                              |
| 202  | Accepted (async task queued)         |
| 204  | No Content (delete)                  |
| 400  | Bad Request / Validation Error       |
| 401  | Unauthenticated                      |
| 403  | Forbidden (insufficient permissions) |
| 404  | Not Found                            |
| 429  | Rate Limited                         |
| 500  | Internal Server Error                |

---

## Rate Limits

| Throttle scope    | Limit                              | Env override                    |
| ----------------- | ---------------------------------- | ------------------------------- |
| Anonymous         | 50 requests / hour                 | —                               |
| Authenticated     | 6 000 requests / hour **per user** | `USER_THROTTLE_RATE`            |
| Login (anonymous) | 10 requests / minute               | `AUTH_LOGIN_THROTTLE_RATE`      |
| 2FA verification  | 5 requests / minute                | `AUTH_VERIFY_2FA_THROTTLE_RATE` |

All limits live in `backend/core/settings/base.py` (`DEFAULT_THROTTLE_RATES`).
The authenticated limit is high on purpose: the admin SPA fires 10–25 requests
per page view plus background polling, so the old 500/hour returned 429 to real
users mid-session and surfaced as empty pages. Lower it via
`USER_THROTTLE_RATE` if you need a tighter runaway-loop guard.

Throttled requests return **429** with a `Retry-After` header (seconds) and
`{"detail": "Request was throttled. Expected available in N seconds."}`. DRF does
not emit `X-RateLimit-*` headers, so don't build clients that depend on them.

---

## Parent & student self-service endpoints

Parents get a read-only, guardian-scoped view of several modules through
`<module>/…/children/` routes. Scoping is to the children linked to the caller
via `StudentGuardian`, further bounded by the caller's school, so a forged link
cannot cross tenants. Responses use the standard `{count, results}` envelope.

| Endpoint                              | Returns                              |
| ------------------------------------- | ------------------------------------ |
| `GET /health/records/children/`       | Children's health records            |
| `GET /health/visits/children/`        | Clinic visits                        |
| `GET /health/immunizations/children/` | Immunization records                 |
| `GET /library/checkouts/children/`    | Book checkouts and due dates         |
| `GET /library/fines/children/`        | Library fines                        |
| `GET /cafeteria/bookings/children/`   | Meal bookings / pre-orders           |
| `GET /sports/teams/children/`         | Teams the children play on           |
| `GET /sports/achievements/children/`  | Sports achievements                  |
| `GET /behavior/incidents/children/`   | Behavior incidents                   |
| `GET /behavior/points/children/`      | Behavior points ledger               |
| `GET /counseling/sessions/children/`  | Counseling sessions (summary fields) |
| `GET /counseling/referrals/children/` | Counseling referrals                 |

These routes are registered **before** each module's DRF router so the literal
`children` segment is not captured as a detail-route `pk`. Implementations live
in `backend/core/parent_portal.py`; regression coverage is in
`backend/tests/test_parent_portal_children.py`.

Students use the same underlying endpoints as admins, but the behavior, health,
cafeteria and hostel viewsets additionally self-scope to the caller's own rows
when `role == "student"` — a student querying them directly cannot read another
student's data.

---

## Interactive API Docs

| Format             | URL                                          |
| ------------------ | -------------------------------------------- |
| Swagger UI         | `https://api.edusphere.school/api/docs/`     |
| ReDoc              | `https://api.edusphere.school/api/redoc/`    |
| OpenAPI 3 document | `https://api.edusphere.school/api/schema/`   |
| JSON / YAML        | `…/api/schema/?format=json` · `?format=yaml` |

Swagger UI ships an **Authorize** button bound to the `jwtAuth` security scheme
(HTTP bearer, `bearerFormat: JWT`) — paste the `access` value from
`/auth/login/` into the token box and Swagger sends
`Authorization: Bearer <token>`. Operations are grouped by module tag, so the
sidebar mirrors the module index above.

The document is generated from the code by `drf-spectacular`; regenerate it
after changing views or serializers:

```bash
# inside the backend container
python manage.py spectacular --file /tmp/schema.yml
python manage.py spectacular --file /tmp/schema.yml --validate   # warnings only
```

Operations that are plain `APIView`s without a `serializer_class` (login,
logout, password-reset, 2FA, the public admissions portal, Zoom helpers) are
reported as "unable to guess serializer" during `--validate`. Those warnings are
expected and do not invalidate the document — add `@extend_schema` to such a
view if you want it fully described.
