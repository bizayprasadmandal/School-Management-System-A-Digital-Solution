# EduSphere SMS — API Reference

## Base URL

| Environment | URL                                           |
| ----------- | --------------------------------------------- |
| Production  | `https://api.edusphere.school/api/v1`         |
| Staging     | `https://staging-api.edusphere.school/api/v1` |
| Local       | `http://localhost:8000/api/v1`                |

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
  "tracking_id": "APP-2026-001234",
  "status": "applied",
  "message": "Application submitted successfully. Use your tracking ID to check status."
}
```

### Check Application Status

```http
GET /admissions/public/status/APP-2026-001234/
```

**Response 200:**

```json
{
  "tracking_id": "APP-2026-001234",
  "status": "screening",
  "status_display": "Screening",
  "first_name": "Ram",
  "last_name": "Sharma",
  "email": "ram.sharma@email.com",
  "grade_applied_for": "Grade 8",
  "created_at": "2026-08-19T10:30:00Z"
}
```

### List Open Intakes

```http
GET /admissions/public/intakes/
```

**Response 200:**

```json
[
  {
    "id": 1,
    "name": "Fall 2026 Intake",
    "description": "Admissions open for Grade 1-10",
    "application_deadline": "2026-10-31"
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

| Client Type       | Limit                |
| ----------------- | -------------------- |
| Anonymous         | 50 requests / hour   |
| Authenticated     | 500 requests / hour  |
| Login (anonymous) | 10 requests / minute |
| 2FA verification  | 5 requests / minute  |

The `auth_login` and `auth_verify_2fa_login` rates are configurable via the
`AUTH_LOGIN_THROTTLE_RATE` and `AUTH_VERIFY_2FA_THROTTLE_RATE` environment
variables. All limits are defined in `backend/core/settings/base.py`.

Rate limit headers returned on every response:

```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 347
X-RateLimit-Reset: 1701388800
```

---

## Interactive API Docs

| Format         | URL                                        |
| -------------- | ------------------------------------------ |
| Swagger UI     | `https://api.edusphere.school/api/docs/`   |
| ReDoc          | `https://api.edusphere.school/api/redoc/`  |
| OpenAPI Schema | `https://api.edusphere.school/api/schema/` |
